# Üyelik kurulumu (Supabase, ücretsiz katman)

Site üyeliksiz çalışır. Üyelik açılınca: e-posta bağlantısıyla giriş (şifresiz), kişisel şablonların hesapta saklanması,
yetkili üyelerin şablonu tek tıkla bölümle paylaşması (depo / deploy gerekmez).

**Durum (30.09.2026):** kurulu. Proje `kqqcebkccgresaobjzcv` (Frankfurt), e-postalar bölümün ayrı Gmail hesabı
üzerinden gider (adres depoda tutulmaz; Supabase → SMTP Settings'te görünür). Aşağıdaki adımlar yeniden kurulum ya da yeni proje içindir.

1. https://supabase.com → ücretsiz hesap → **New project** (bölge: Frankfurt / eu-central-1).
2. **SQL Editor** → `supabase/schema.sql` içeriğini yapıştır → Run (bir kez; ikinci çalıştırma "already exists" verir).
3. **Authentication → URL Configuration**: Site URL = `https://fatihfnd.github.io/selcuk-patoloji-rehberi/`,
   Redirect URLs'e `https://fatihfnd.github.io/selcuk-patoloji-rehberi/**` ekle.
4. **Project Settings → API Keys**: `Project URL` ve **Publishable key**'i (`sb_publishable_...`; eski projelerde
   `anon public`, `eyJ...`) `site.yaml`'daki `supabase_url` ve `supabase_anon_key` satırlarına yaz. Bu anahtar tarayıcıda
   görünmek için tasarlanmıştır; **secret / `service_role` anahtarını asla depoya koyma.**
5. **E-posta (SMTP)** — Supabase'in hazır servisi yalnız proje ekibine ve saatte birkaç e-posta gönderir; hekimlere
   ulaşmak için özel SMTP gerekir. Gmail ile:
   - Gönderici hesapta iki adımlı doğrulama açık olmalı (telefon / Authenticator), sonra
     https://myaccount.google.com/apppasswords → "Supabase" adıyla 16 haneli uygulama şifresi.
   - **Authentication → Emails → SMTP Settings** → Enable Custom SMTP: host `smtp.gmail.com`, port `465`,
     kullanıcı adı ve gönderici = Gmail adresi, gönderici adı `Selçuk Patoloji Rehberi`, şifre = uygulama şifresi.
   - Uygulama şifresi yalnız Supabase paneline girilir; depoya, sohbete ya da e-postaya yazılmaz.
6. **Authentication → Emails → Templates**: *Confirm signup* (ilk giriş) ve *Magic Link* (sonraki girişler) Türkçe;
   gövdedeki `{{ .ConfirmationURL }}` korunur.
   - Konu: `Selçuk Patoloji Rehberi — üyeliğinizi onaylayın` / `Selçuk Patoloji Rehberi — giriş bağlantınız`
7. Siteye bir kez giriş yap, sonra SQL Editor'de kendine (ve yetki vereceğin hekimlere) bölümle paylaşma yetkisi ver:
   ```sql
   insert into public.bolum_uyeleri (uid, not_)
   select id, 'yönetici' from auth.users where email = 'ornek@gmail.com';
   ```
   Denetim (Supabase `insert` sonrasında satır sayısı göstermez):
   ```sql
   select u.email, u.last_sign_in_at, b.uid is not null as bolum_yetkisi
   from auth.users u left join public.bolum_uyeleri b on b.uid = u.id;
   ```
   Yetkiyi geri almak: `delete from public.bolum_uyeleri where uid = (select id from auth.users where email = '...');`
8. `site.yaml` değişikliğini commit + push → site güncellenir.

## Bilinmesi gerekenler

- İlk giriş e-postaları Gmail'de çoğunlukla **spam**'e düşer; hekimlere "Spam değil" işaretlemelerini söyle.
- Giriş bağlantılarının kopyası gönderici Gmail'in **Gönderilmiş** kutusunda kalır. Bağlantılar tek kullanımlıktır ama
  kullanılmamış bir bağlantıyla başkası adına giriş yapılabilir: gönderici hesabı yalnız yönetici kullanır, iki adımlı
  doğrulama açık kalır. İsteğe bağlı: **Authentication → Sign In / Providers → Email → Email OTP Expiration** kısaltılabilir.
- Kayıt açıktır: e-postası olan herkes üye olup yalnız kendine özel şablon kaydedebilir; bölümle paylaşma yalnız
  `bolum_uyeleri`'ndekilere açıktır. Yalnız davetle üyelik istenirse **Authentication → Sign In / Providers**'ta
  yeni kayıtlar kapatılır ve hekimler **Authentication → Users → Invite user** ile davet edilir.

Veritabanında yalnız e-posta adresi ve şablon içerikleri tutulur; hasta verisi girilmez.
