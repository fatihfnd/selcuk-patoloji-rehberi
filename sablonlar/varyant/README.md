# Paylaşılan şablon sürümleri

Bir konu için bölümde kullanılan farklı şablon sürümleri (ör. hekime özgü, kısa rapor, konsültasyon) burada tutulur.

- Dosya adı: `<temel şablon id>--<ad>.yaml` (ör. `apendiks--ceyhan-hoca.yaml`); ad kısmında küçük ASCII harf, rakam, "-".
- En kolay yol: sitede şablon sayfasındaki listeden **“Yeni şablon oluştur”** → düzenle → **“GitHub'da paylaş”** ya da **“YAML indir”**.
- Dosya temel şablona göre yalnızca farkları içerir: `alanlar` (gizle / etiket / seviye / seçenekler), `sira`, `ekle` (x_ ile
  başlayan yeni alanlar), `tani`, `mikroskopi`, `varsayilanlar`.
- `python build.py` dosyayı doğrular; temel şablonda olmayan alan veya hatalı ad derlemeyi durdurur.
