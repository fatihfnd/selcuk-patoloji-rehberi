#!/usr/bin/env python3
"""Şablon arşivi derleyici.

Kaynak : sablonlar/*.yaml + moduller/*.yaml
Çıktı  : dist/sablonlar.json          (editör / PatoLIS için çözülmüş tek dosya)
         dist/metin/<id>_<seviye>.txt (Enlil'e yapıştırmalık düz metin; kisa/standart/tam)
         dist/Sablon_Arsivi.md / .docx (elle kullanım için basılı arşiv)

Seviye: 0 = gizli (yalnız tanı satırını besler), 1 = çekirdek (ICCR core / CAP required),
        2 = standart, 3 = geniş (isteğe bağlı / araştırma).
"""
import copy, glob, json, os, re, shutil, subprocess, sys
import yaml

KOK = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(KOK, "dist")
SEVIYE_AD = {1: "kisa", 2: "standart", 3: "tam"}
TIPLER = {"secim", "coklu", "metin", "sayi", "olcu", None}
ANAHTARLAR = {"id", "etiket", "seviye", "tip", "secenekler", "serbest", "kalip", "birim", "kosul",
              "not", "alt", "gizli", "_kaynak_modul"}


def modulleri_yukle():
    mod = {}
    for f in glob.glob(os.path.join(KOK, "moduller", "*.yaml")):
        ad = os.path.splitext(os.path.basename(f))[0]
        for k, v in (yaml.safe_load(open(f, encoding="utf-8")) or {}).items():
            mod[f"{ad}.{k}"] = v
    return mod


def coz(alanlar, mod, yol):
    """modul: referanslarını açar, ezmeleri uygular, alt alanları özyinelemeli çözer."""
    cikti = []
    for a in alanlar or []:
        if "modul" in a:
            ref = a["modul"]
            if ref not in mod:
                sys.exit(f"HATA {yol}: bilinmeyen modül '{ref}'")
            yeni = copy.deepcopy(mod[ref])
            yeni.update({k: v for k, v in a.items() if k != "modul"})
            yeni["_kaynak_modul"] = ref
            a = yeni
        else:
            a = copy.deepcopy(a)
        if "alt" in a:
            a["alt"] = coz(a["alt"], mod, yol)
        cikti.append(a)
    return cikti


def dogrula(s, yol):
    idler = []

    def gez(alanlar):
        for a in alanlar:
            for zorunlu in ("id", "etiket", "seviye"):
                if zorunlu not in a:
                    sys.exit(f"HATA {yol}: '{a.get('etiket', a)}' alanında '{zorunlu}' eksik")
            if a.get("tip") not in TIPLER:
                sys.exit(f"HATA {yol}: {a['id']} geçersiz tip {a.get('tip')}")
            if a.get("tip") in ("secim", "coklu") and not a.get("secenekler"):
                sys.exit(f"HATA {yol}: {a['id']} seçenek listesi boş")
            fazla = set(a) - ANAHTARLAR
            if fazla:
                sys.exit(f"HATA {yol}: {a['id']} tanınmayan anahtar {fazla} (tırnak eksik olabilir)")
            if not re.fullmatch(r"[a-z0-9_]+", a["id"]):
                sys.exit(f"HATA {yol}: id yalnız küçük ASCII harf/rakam/alt çizgi olmalı: {a['id']}")
            idler.append(a["id"])
            gez(a.get("alt", []))

    gez(s["epikriz"])
    if "tekrar_blok" in s:
        gez(s["tekrar_blok"]["alanlar"])
    ciftler = {i for i in idler if idler.count(i) > 1}
    if ciftler:
        sys.exit(f"HATA {yol}: tekrarlanan id {ciftler}")


# ---------- makroskopi ----------
MAKRO_ANAHTAR = {"id", "etiket", "tip", "secenekler", "birim", "zorunlu", "not"}
TOKEN = re.compile(r"\{(\w+)\}")


def makro_dogrula(m, mod, yol):
    ids = {}
    for a in m["alanlar"]:
        fazla = set(a) - MAKRO_ANAHTAR
        if fazla or "id" not in a or "etiket" not in a:
            sys.exit(f"HATA {yol} makro: {a} (tanınmayan anahtar {fazla} / id-etiket eksik)")
        if a["id"] in ids:
            sys.exit(f"HATA {yol} makro: tekrarlanan id {a['id']}")
        if not re.fullmatch(r"[a-z0-9_]+", a["id"]):
            sys.exit(f"HATA {yol} makro: id yalnız küçük ASCII harf/rakam/alt çizgi olmalı: {a['id']}")
        ids[a["id"]] = a
    kullanilan = set()
    for v in m["varyantlar"]:
        metinler = list(v.get("metin", [])) + ([v["tekrar"]["metin"]] if "tekrar" in v else [])
        for t in metinler:
            for tok in TOKEN.findall(t):
                if tok not in ids:
                    sys.exit(f"HATA {yol} makro/{v['ad']}: '{{{tok}}}' alan listesinde yok")
                kullanilan.add(tok)
        for o in v.get("ornekleme", []):
            if "kod" not in o or "aciklama" not in o or set(o) - {"kod", "aciklama", "parca", "kaset", "not", "tek"}:
                sys.exit(f"HATA {yol} makro/{v['ad']}: örnekleme satırı hatalı {o}")
    kullanilmayan = [i for i, a in ids.items() if a.get("zorunlu") and i not in kullanilan]
    if kullanilmayan:
        sys.exit(f"HATA {yol} makro: zorunlu ama metinde geçmeyen alan {kullanilmayan}")
    for r in m.get("ek_materyaller", []):
        if r not in mod:
            sys.exit(f"HATA {yol} makro: bilinmeyen ek materyal '{r}'")
    return ids


def makro_token(ids):
    def f(mt):
        a = ids.get(mt.group(1), {})
        s = a.get("secenekler") or []
        if a.get("tip") == "secim" and 0 < len(s) <= 3 and all(len(x) <= 25 for x in s):
            return " / ".join(s)
        return "…"
    return f


def ornekleme_metni(orn, kisa):
    if len(orn) == 1 and orn[0].get("tek"):
        return f"{orn[0]['kod']}…P…K" if kisa else "Tümü … parça … kasette takibe alındı."
    parca = []
    for o in orn:
        p, k = o.get("parca", "…"), o.get("kaset", "…")
        parca.append(f"{o['kod']} ({o['aciklama']}): " + (f"{p}P{k}K" if kisa else f"{p} parça {k} kasette"))
    return ("" if kisa else "Alınan parçalar: ") + ", ".join(parca) + ("" if kisa else " takibe alındı.")


def makro_metni(s, mod, kisa=False):
    m = s["makroskopi"]
    ids = {a["id"]: a for a in m["alanlar"]}
    f = makro_token(ids)
    out = []
    for v in m["varyantlar"]:
        out.append(f"### {v['ad']}")
        out += [(lambda x: x[:1].upper() + x[1:])(TOKEN.sub(f, t)) for t in v.get("metin", [])]
        if "tekrar" in v:
            out.append(TOKEN.sub(f, v["tekrar"]["metin"]) + f"   [{v['tekrar']['etiket']}]")
        if v.get("ornekleme"):
            out.append(ornekleme_metni(v["ornekleme"], kisa))
        out.append("")
    for r in m.get("ek_materyaller", []):
        em = mod[r]
        g = makro_token({a["id"]: a for a in em["alanlar"]})
        t = TOKEN.sub(g, em["metin"])
        if kisa:
            t = t.replace("Tümü … parça … kasette takibe alındı.", "T…P…K")
        out += [f"### Ek materyal: {em['ad']}", t, ""]
    return "\n".join(out).rstrip() + "\n"


# ---------- düz metin üretimi ----------
def deger_metni(a):
    if a.get("kalip"):
        return a["kalip"]
    t = a.get("tip")
    if t in ("secim", "coklu"):
        s = a["secenekler"]
        birlesik = " / ".join(s)
        kisa_sec = all(len(x) <= 4 for x in s) and len(s) <= 10
        return birlesik if kisa_sec or (len(s) <= 6 and len(birlesik) <= 140) else "…"
    if t == "olcu":
        b = a.get("birim", "")
        return f"%…" if b == "%" else f"… {b}".strip()
    return "…" if t else ""


def satirlar(alanlar, seviye, girinti=0):
    out = []
    for a in alanlar:
        if a.get("gizli") or a["seviye"] == 0 or a["seviye"] > seviye:
            continue
        on = "   " * girinti + "- "
        d = deger_metni(a)
        out.append(f"{on}{a['etiket']}:" + (f" {d}" if d else ""))
        out += satirlar(a.get("alt", []), seviye, girinti + 1)
    return out


def tani_metni(s):
    alan = {}

    def topla(al):
        for a in al:
            alan[a["id"]] = a
            topla(a.get("alt", []))

    topla(s["epikriz"])
    out, no = [], 0
    for t in s["tani"]:
        def yerine(m):
            a = alan.get(m.group(1))
            if a and a.get("secenekler") and len(a["secenekler"]) <= 3:
                return " / ".join(x.lower() for x in a["secenekler"])
            return "…"

        t = re.sub(r"\{(\w+)\}", yerine, t)
        if t.startswith("-"):
            out.append("   " + t)
        elif s.get("tani_alternatif"):
            out.append(f"1- {t}")
        else:
            no += 1
            out.append(f"{no}- {t}")
    return out


def rapor_metni(s, seviye):
    mik = []
    if s.get("mikroskopi"):
        if not all(isinstance(x, str) for x in s["mikroskopi"]):
            sys.exit(f"HATA {s['id']}: mikroskopi yalnız metin satırlarından oluşmalı")
        mik = ["MİKROSKOPİ:"] + s["mikroskopi"] + [""]
    out = mik + [s.get("tani_etiket", "TANI") + ":" + ("  [seçeneklerden birini bırakın]" if s.get("tani_alternatif") else "")] + tani_metni(s) + ["", s.get("epikriz_etiket", "EPİKRİZ") + ":", "1-"]
    if "tekrar_blok" in s:
        tb = s["tekrar_blok"]
        out.append(f"- {tb['etiket'].replace('{kor_kodu}', '… (kor kodu)')}:  [{tb['aciklama']}]")
        out += satirlar(tb["alanlar"], seviye, 1)
    out += satirlar(s["epikriz"], seviye)
    return "\n".join(out)


# ---------- basılı arşiv (markdown → docx) ----------
def alan_tablosu(alanlar, derinlik=0):
    rows = []
    for a in alanlar:
        sec = "; ".join(a.get("secenekler", [])) or a.get("kalip", "")
        if a.get("serbest"):
            sec += " — (listede yoksa serbest metin)"
        notm = a.get("not", "") + (f" Koşul: {a['kosul']}." if a.get("kosul") else "")
        lvl = {0: "gizli", 1: "çekirdek", 2: "standart", 3: "geniş"}[a["seviye"]]
        rows.append(f"| {'↳ ' * derinlik}{a['etiket']} | {lvl} | {sec.replace('|', '/')} | {notm.strip()} |")
        rows += alan_tablosu(a.get("alt", []), derinlik + 1)
    return rows


def main():
    mod = modulleri_yukle()
    paket = []
    os.makedirs(os.path.join(DIST, "metin"), exist_ok=True)
    md = ["---", "title: Patoloji Tanı ve Epikriz Şablon Arşivi", "---", "",
          "Seviyeler: **çekirdek** (ICCR core / CAP required), **standart**, **geniş** (isteğe bağlı). "
          "Metin blokları 'standart' seviyede basılmıştır; kısa ve tam sürümler dist/metin klasöründedir.", ""]
    for f in sorted(glob.glob(os.path.join(KOK, "sablonlar", "*.yaml"))):
        s = yaml.safe_load(open(f, encoding="utf-8"))
        s["epikriz"] = coz(s["epikriz"], mod, f)
        if "tekrar_blok" in s:
            s["tekrar_blok"]["alanlar"] = coz(s["tekrar_blok"]["alanlar"], mod, f)
        dogrula(s, f)
        if "makroskopi" in s:
            makro_dogrula(s["makroskopi"], mod, f)
            for kisa, ek in ((False, "makro"), (True, "makro_kisakod")):
                open(os.path.join(DIST, "metin", f"{s['id']}_{ek}.txt"), "w", encoding="utf-8").write(makro_metni(s, mod, kisa))
            s["makroskopi"]["ek_materyaller_cozulmus"] = {r: mod[r] for r in s["makroskopi"].get("ek_materyaller", [])}
        paket.append(s)
        for lv, ad in SEVIYE_AD.items():
            with open(os.path.join(DIST, "metin", f"{s['id']}_{ad}.txt"), "w", encoding="utf-8") as g:
                g.write(rapor_metni(s, lv) + "\n")
        md += [f"# {s['baslik']}", "", "**Kaynaklar:** " + "; ".join(s["kaynaklar"]), ""]
        if s.get("not"):
            md += [f"*Not:* {s['not']}", ""]
        if "makroskopi" in s:
            m = s["makroskopi"]
            md += ["## " + s.get("makro_baslik", "Makroskopi"), "", "```", makro_metni(s, mod).replace("### ", "» "), "```", ""]
            for v in m["varyantlar"]:
                if v.get("ornekleme"):
                    md += [f"**Örnekleme — {v['ad']}**", "", "| Kod | Açıklama | Varsayılan | Not |", "|------|----------------|------|------------------------|"]
                    md += [f"| {o['kod']} | {o['aciklama']} | {o.get('parca','…')}P{o.get('kaset','…')}K | {o.get('not','')} |" for o in v["ornekleme"]]
                    md.append("")
            zor = [a["etiket"] for a in m["alanlar"] if a.get("zorunlu")]
            md += ["**Zorunlu makroskopik veriler:** " + "; ".join(zor), "", "**Yapılacaklar:**", ""]
            md += [f"- [ ] {y}" for y in m.get("yapilacaklar", [])] + [""]
            md += ["## " + s.get("epikriz_baslik", "Tanı ve epikriz"), ""]
        md += ["```", rapor_metni(s, 2), "```", "",
               "| Alan | Seviye | Seçenekler / kalıp | Not |", "|--------------|------|------------------------------|--------------|"]
        if "tekrar_blok" in s:
            md += alan_tablosu(s["tekrar_blok"]["alanlar"])
        md += alan_tablosu(s["epikriz"]) + [""]
    kat = yaml.safe_load(open(os.path.join(KOK, "katalog.yaml"), encoding="utf-8"))
    mevcut = {x["id"] for x in paket}
    km, top, tam = ["# Katalog ve ilerleme", ""], 0, 0
    for p in kat["paketler"]:
        km += [f"## {p['ad']}", ""]
        for sid, ad in p["sablonlar"]:
            top += 1; tam += sid in mevcut
            km.append(f"- [{'x' if sid in mevcut else ' '}] {ad} (`{sid}`)")
        km.append("")
    km.insert(1, f"\n{tam} / {top} şablon tamamlandı.\n")
    open(os.path.join(DIST, "Katalog.md"), "w", encoding="utf-8").write("\n".join(km))
    md += km
    # --- uygulama (tek HTML) ---
    sin = yaml.safe_load(open(os.path.join(KOK, "siniflama.yaml"), encoding="utf-8"))
    eksik = [x["id"] for x in paket if x["id"] not in sin["sablonlar"]]
    if eksik:
        sys.exit(f"HATA siniflama.yaml: sınıflanmamış şablon {eksik}")
    app_sablon = []
    for x in paket:
        y = {k: v for k, v in x.items() if k != "makroskopi"}
        if "makroskopi" in x:
            y["makroskopi"] = {k: v for k, v in x["makroskopi"].items() if k != "ek_materyaller_cozulmus"}
        y["_sistem"], y["_grup"] = sin["sablonlar"][x["id"]]
        app_sablon.append(y)
    veri = {"sablonlar": app_sablon, "makro_moduller": {k: v for k, v in mod.items() if k.startswith("makro.")},
            "siniflama": {"gruplar": sin["gruplar"], "sistemler": sin["sistemler"]},
            "site": yaml.safe_load(open(os.path.join(KOK, "site.yaml"), encoding="utf-8"))}
    js = json.dumps(veri, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = open(os.path.join(KOK, "app", "index.template.html"), encoding="utf-8").read().replace("/*__DATA__*/null", js)
    site = os.path.join(KOK, "site")
    os.makedirs(os.path.join(site, "indir"), exist_ok=True)
    open(os.path.join(site, "index.html"), "w", encoding="utf-8").write(html)
    open(os.path.join(site, ".nojekyll"), "w").close()
    json.dump({"surum": 1, "sablonlar": paket}, open(os.path.join(DIST, "sablonlar.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(os.path.join(DIST, "Sablon_Arsivi.md"), "w", encoding="utf-8").write("\n".join(md))
    if shutil.which("pandoc"):
        subprocess.run(["pandoc", os.path.join(DIST, "Sablon_Arsivi.md"), "-o",
                        os.path.join(DIST, "Sablon_Arsivi.docx"), "--toc"], check=True)
    else:
        print("uyarı: pandoc yok, docx üretilmedi")
    for ad in ("sablonlar.json", "Sablon_Arsivi.docx"):
        if os.path.exists(os.path.join(DIST, ad)):
            shutil.copy(os.path.join(DIST, ad), os.path.join(site, "indir", ad))
    print(f"{len(paket)} şablon derlendi.")


if __name__ == "__main__":
    main()
