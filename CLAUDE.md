# Selçuk Patoloji Rehberi — Claude Code çalışma notları

Bu depo, Selçuk Üniversitesi Tıp Fakültesi Tıbbi Patoloji AD için raporlama şablonları ve tanısal rehberden oluşan
statik bir web sitesidir. İçerik YAML'dadır; `build.py` doğrular ve `site/` klasörüne tek sayfalık uygulamayı üretir.
GitHub Actions `main`'e her push'ta derleyip GitHub Pages'e yayınlar.

## Komutlar

- `pip install pyyaml` (docx için isteğe bağlı: `pandoc`)
- `python build.py` → doğrulama + `dist/` (json, txt, docx) + `site/` (index.html, indir/)
- Yerel önizleme: `python -m http.server -d site 8000`

Derleme hata verirse commit atma; hatayı düzelt. Derleyicinin yakaladığı tipik hatalar: virgül / iki nokta içeren
etiketin tırnaksız yazılması, tanınmayan anahtar, ASCII olmayan `id`, metinde geçip alan listesinde olmayan `{token}`.

## Yapı

- `sablonlar/<id>.yaml` — her şablon (tanı, epikriz, makroskopi, isteğe bağlı mikroskopi ve `rehber:` paragrafları)
- `moduller/ortak.yaml`, `biyobelirtec.yaml`, `makro.yaml` — paylaşılan alanlar (`- modul: ortak.lvi`)
- `siniflama.yaml` — her şablonun organ sistemi ve grubu (N / NN / K / S / E); yeni şablon buraya da eklenmeli
- `katalog.yaml` — yol haritası; `site.yaml` — site adı
- `app/index.template.html` — arayüz (veri derlemede `/*__DATA__*/null` yerine gömülür)

## İçerik kuralları (bölüm standardı — değiştirmeden önce sor)

- Tanı satırı: `Tanı, lütfen epikrizi okuyunuz; alındığı yer, alınma şekli`. Çoklu materyal numaralı (`1-`, `2-`);
  "-" ile başlayan satır üstteki tanıya bağlı (rezeksiyon + lenf nodu birleşik yazımı).
- Sitolojide kategori parantez içinde: `Foliküler nodüler hastalık ile uyumlu (Bethesda kategori II — benign)`.
  Benign kategorilerde "lütfen epikrizi okuyunuz" yazılmaz.
- Dil: "Görüldü / Görülmedi / Belirlenemedi"; tanıda cümle düzeni (her kelime büyük harf değil).
- Makroskopi: mesafeler tek cümlede; lenf nodları "en büyüğü … cm, en küçüğü … cm çapında … adet".
- Kaset yazımı iki biçimde üretilir (uzun / kısa kod "3P3K"); metinde elle yazılmaz.
- Seviye: 0 gizli (tanı satırını besler), 1 çekirdek (ICCR core / CAP required), 2 standart, 3 geniş.
  Malignite riski (ROM) her zaman seviye 3.
- `id` yalnız küçük ASCII harf, rakam, alt çizgi.
- Kaynak protokollerden metin kopyalanmaz; alanlar Türkçe ve özgün yazılır, kaynak adı `kaynaklar:` altında verilir.
  Emin olunmayan sayısal değer (eşik, ROM) yazılmaz; "kurum tablosuna göre" kalıbı kullanılır.
- Hasta verisi, olgu fotoğrafı ya da kimlik bilgisi depoya hiçbir biçimde girmez.

## Gözden geçirme bekleyenler

- `anal-kanal`, `distal-pankreatektomi`, `karaciger-rezeksiyon`: kaynağı belirsiz; tıbbi içerik satır satır kontrol edilecek.
- Yaklaşık ROM değerleri (Milan, ISRSFC, Yokohama); akciğer TNM 8/9 baskı seçimi; FIGO 2023 endometrium alt evreleri;
  TUR-P örnekleme kuralı.
- Histoloji şablonlarına mikroskopi kalıbı eklenip eklenmeyeceği (karar bekliyor).

## Yol haritası

`ROADMAP.md`'ye bak. Yeni bölüm eklerken arayüzü büyütmeden önce içerik biçimini (YAML şeması) netleştir ve
derleyiciye doğrulamasını ekle.
