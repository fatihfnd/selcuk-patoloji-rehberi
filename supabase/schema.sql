-- Selçuk Patoloji Rehberi — üyelik ve şablon sürümleri
-- Supabase > SQL Editor'de bir kez çalıştırın.

create table if not exists public.sablon_surumleri (
  id          uuid primary key default gen_random_uuid(),
  sahip       uuid not null default auth.uid() references auth.users(id) on delete cascade,
  sahip_ad    text,
  temel       text not null,
  ad          text not null check (char_length(ad) between 1 and 120),
  veri        jsonb not null,
  paylasim    text not null default 'kisisel' check (paylasim in ('kisisel', 'bolum')),
  olusturma   timestamptz not null default now(),
  guncelleme  timestamptz not null default now()
);

-- Bölümle paylaşma yetkisi olan kullanıcılar (yönetici panelden ekler)
create table if not exists public.bolum_uyeleri (
  uid   uuid primary key references auth.users(id) on delete cascade,
  not_  text
);

alter table public.sablon_surumleri enable row level security;
alter table public.bolum_uyeleri   enable row level security;

-- Herkes (girişsiz dahil) bölümde paylaşılanları görür; üye kendi kişisel şablonlarını görür
create policy "okuma" on public.sablon_surumleri for select
  using (paylasim = 'bolum' or auth.uid() = sahip);

-- Üye kendi adına ekler; 'bolum' paylaşımı yalnız bolum_uyeleri listesindekilere açık
create policy "ekleme" on public.sablon_surumleri for insert to authenticated
  with check (auth.uid() = sahip and (paylasim = 'kisisel' or exists (select 1 from public.bolum_uyeleri b where b.uid = auth.uid())));

create policy "guncelleme" on public.sablon_surumleri for update to authenticated
  using (auth.uid() = sahip)
  with check (auth.uid() = sahip and (paylasim = 'kisisel' or exists (select 1 from public.bolum_uyeleri b where b.uid = auth.uid())));

create policy "silme" on public.sablon_surumleri for delete to authenticated
  using (auth.uid() = sahip);

-- Kullanıcı yalnız kendi bölüm üyeliği satırını görebilir (arayüzde yetki kontrolü için)
create policy "kendi uyeligi" on public.bolum_uyeleri for select to authenticated
  using (uid = auth.uid());
