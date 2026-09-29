# Selçuk Patoloji Rehberi

Selçuk Üniversitesi Tıp Fakültesi Tıbbi Patoloji AD — raporlama şablonları ve tanısal rehber.
Yayın: GitHub Pages (`.github/workflows/deploy.yml`). Geliştirme notları: `CLAUDE.md`; plan: `ROADMAP.md`.

Tek kaynak (YAML) → çıktılar: editör/PatoLIS için `sablonlar.json`, Enlil'e yapıştırmalık düz metin
(tanı+epikriz kısa / standart / tam; makroskopi iki kaset yazımıyla), ilerleme için `Katalog.md`, elle kullanım için `Sablon_Arsivi.docx`. Derleme: `python3 build.py`.

## Uygulama

`site/index.html` — tek dosyalık, kurulum gerektirmeyen tarayıcı uygulaması (her `build.py` çalışmasında
şablonlardan yeniden üretilir; arayüz kodu `app/index.template.html`, gezinme sınıflaması `siniflama.yaml`).
Neoplastik / non-neoplastik / karma / sitoloji / ek test ve organ sistemi filtreleri; şablon sayfasında doldurulabilir
alanlar ve canlı rapor önizlemesi, boş şablon ve dolu rapor yazdırma; her şablonun ayrı rehber sayfası.
Şablona daha kapsamlı rehber metni eklemek için YAML'a `rehber:` altında paragraf listesi yazılır.

## Rapor biçimi

```
TANI:
1- Tanı, lütfen epikrizi okuyunuz; alındığı yer, alınma şekli
   - Metastatik lenf nodları (… adet), nonmetastatik lenf nodları (… adet); yer
2- Tanı; alındığı yer, alınma şekli

EPİKRİZ:
1-
- Alan: değer
   - Alt alan: değer
```

"- " ile başlayan tanı satırı üstteki numaraya bağlıdır (rezeksiyon + lenf nodu birleşik yazımı).
Epikriz numarası tanı numarasını izler; epikrizi olmayan tanılar atlanır.

## Seviyeler (genişlet / daralt)

| Seviye | Anlamı | Karşılık |
|---|---|---|
| 0 | gizli — yalnız tanı satırını besler (taraf vb.) | — |
| 1 | çekirdek | ICCR *core* / CAP *required* |
| 2 | standart | ICCR *non-core* içinde rutin raporlananlar |
| 3 | geniş | isteğe bağlı, araştırma, özel durum |

Seviye atamaları kaynak protokollerin yapısına göre yapılmıştır; kurum içi kullanıma göre
alan bazında değiştirilebilir (tek satır: `seviye:`).

## Alan anahtarları

`id` (şablon içinde tekil), `etiket`, `seviye`, `tip` (secim | coklu | metin | sayi | olcu | boş = başlık),
`secenekler`, `serbest` (listede yoksa serbest metin), `kalip` (düz metin çıktısında gösterilecek boşluklu kalıp),
`birim`, `kosul` (editörün değerlendireceği görünürlük koşulu), `not`, `alt` (iç içe alanlar), `gizli`.
Ortak bloklar: `- modul: ortak.lvi` / `- modul: biyobelirtec.mmr` — yanına yazılan anahtarlar modülü ezer.
Tekrarlı yapı (ör. prostat korları): `tekrar_blok`.

Derleyici tanınmayan anahtar, eksik zorunlu alan, boş seçenek listesi ve tekrarlanan id'de durur
(YAML'da virgül içeren etiketlerin tırnaksız yazılması bu kontrolle yakalanır).

## Mikroskopi bloğu (isteğe bağlı)

`mikroskopi:` altında düz metin kalıp satırları; rapor metninde TANI'dan önce "MİKROSKOPİ:" başlığıyla basılır.
Şimdilik sitoloji şablonlarında kullanılıyor.

## Makroskopi bloğu

```yaml
makroskopi:
  alanlar:        # dikte aracı ve editörün soracağı veri noktaları
    - {id: tumor_boyut, etiket: Tümör boyutu, tip: olcu, birim: cm, zorunlu: true}
  varyantlar:     # aynı organın farklı prosedürleri (mastektomi / lumpektomi, kolon / rektum …)
    - ad: Mastektomi
      metin: ["… {tumor_boyut} cm boyutlarında …"]   # {id} yer tutucuları alan listesine bağlı
      ornekleme:  # kaset listesi
        - {kod: T, aciklama: "tümör", parca: "…", kaset: "…", not: "örnekleme kuralı"}
      tekrar: {etiket: Her kap için, metin: "…"}     # prostat korları gibi çoğaltılan satır
  ek_materyaller: [makro.ln_istasyon, makro.donat]  # ayrı kapta gelenler
  yapilacaklar: [...]                               # grossing kontrol listesi (rapora girmez)
```

Kural: mesafeler tek cümlede, lenf nodları "en büyüğü / en küçüğü" kalıbında. Metinde geçen her `{id}`
alan listesinde olmalı; `zorunlu: true` alan en az bir varyant metninde geçmeli — derleyici ikisini de denetler.
Böylece bir alan listesi, hem editörde boş alan uyarısı hem dikte aracında "eksik veriyi sor" döngüsü için
tek kaynak olur. Kaset yazımı iki biçimde üretilir: `_makro.txt` ("T (tümör): 3 parça 3 kasette … takibe
alındı") ve `_makro_kisakod.txt` ("T (tümör): 3P3K").

## Yeni şablon eklemek

1. En yakın şablonu kopyala (`sablonlar/…yaml`), `id` ve `baslik` değiştir.
2. Ortak alanları modülden çağır; organa özgü olanları yaz.
3. `python3 build.py` → hata yoksa üç çıktı birden güncellenir.

## Eski şablonlarda güncellenmesi gereken noktalar

- **Böbrek:** Fuhrman yerine WHO/ISUP nükleer derece; papiller RCC tip 1/tip 2 ayrımı WHO 2022'de kaldırıldı;
  "multiloküler berrak hücreli RCC" → multiloküler kistik düşük malign potansiyelli renal neoplazm;
  berrak hücreli papiller RCC → berrak hücreli papiller renal hücreli *tümör*; moleküler tanımlı tipler eklendi;
  rabdoid özellik ve tümör dışı böbrek değerlendirmesi zorunlu alan.
- **Meme:** "medüller karsinom / atipik medüller" WHO 2019'da ayrı tip değil → NST, medüller paternli;
  "Cerb-B2" → HER2; HER2 0 içinde ultradüşük ayrımı ve HER2-düşük (1+, 2+/ISH−) kategorisi;
  ER %1–10 "düşük pozitif"; mitoz skoru alan çapı yerine mm² ile; nodal ITC/mikro/makro ayrı sayılır.
- **Kolorektal:** 4 basamaklı derece yerine WHO iki basamaklı (düşük/yüksek); tomurcuklanma Bd1–3 (0,785 mm²);
  intramural/ekstramural venöz invazyon ayrı.
- **Mide:** ≥16 lenf nodu notu; HER2 gastrik kriterleri; PD-L1 CPS, Claudin 18.2, MMR, EBV isteğe bağlı.
- **Prostat:** ISUP/GUPS intraduktal karsinom farkının belirtilmesi; pT2 alt evreleri AJCC 8'de yok;
  pozitif sınır uzunluğu ve sınırdaki patern.
- **Yazım:** "örmeklendi", "nükleer pleomorfizim", "İn situ" (büyük İ), "Lenfoma tutulumu" (lenf nodu tutulumu
  yerine) gibi eski şablonlarda kalan hatalar yeni şablonlarda düzeltildi.
- pMX / pM0 yazılmaz; yalnız kanıtlanmış pM1.
