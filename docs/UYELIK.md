# Üyelik kurulumu (Supabase, ücretsiz katman)

Site üyeliksiz çalışır. Üyelik açılınca: e-posta bağlantısıyla giriş (şifresiz), kişisel şablonların hesapta saklanması,
yetkili üyelerin şablonu tek tıkla bölümle paylaşması (depo / deploy gerekmez).

1. https://supabase.com → ücretsiz hesap → **New project** (bölge: Frankfurt / eu-central-1).
2. **SQL Editor** → `supabase/schema.sql` içeriğini yapıştır → Run.
3. **Authentication → URL Configuration**: Site URL = `https://fatihfnd.github.io/selcuk-patoloji-rehberi/`,
   Redirect URLs'e aynı adresi ekle.
4. (İsteğe bağlı) **Authentication → Providers → Email**: yalnız kurum adresleriyle kayıt istenirse bir e-posta alan adı
   kısıtı / davetli kayıt ayarlanabilir.
5. **Project Settings → API**: `Project URL` ve `anon public` anahtarını `site.yaml`'daki `supabase_url` ve
   `supabase_anon_key` satırlarına yaz (başlarındaki `#` kaldırılır). Anon anahtar tarayıcıda görünmek için tasarlanmıştır;
   `service_role` anahtarını asla depoya koyma.
6. Siteye bir kez giriş yap. Sonra **Table Editor → bolum_uyeleri** tablosuna kendi `uid`'ini (Authentication → Users'ta görünür)
   ve paylaşım yetkisi vereceğin hekimlerinkini ekle.
7. Değişiklikleri commit + push → site güncellenir.

Veritabanında yalnız e-posta adresi ve şablon içerikleri tutulur; hasta verisi girilmez.
