# Tarif ve Makale Sitesi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** cimenagapastirma.com için 8 tarif, 4 makale ve ana sayfadan oluşan statik, SEO ve AEO uyumlu bir site kurmak.

**Architecture:** İçerik `docs/content/**/*.json` dosyalarında tutulur. `docs/build.py` (yalnızca Python standart kütüphanesi) bu dosyalardan kök dizindeki statik HTML'i, JSON-LD'yi, sitemap.xml'i, robots.txt'i ve llms.txt'i üretir. Böylece schema ile görünür içerik aynı veriden çıkar ve birebir uyumlu kalır. `docs/check.py` yayın öncesi doğrulamayı yapar. Yayına giden dosyalarda JS yoktur.

**Tech Stack:** HTML, CSS, Python 3 (stdlib), WebSearch/WebFetch (araştırma ve görsel).

**Spec:** `docs/superpowers/specs/2026-10-11-tarif-sitesi-design.md`

## Global Constraints

- Klasör: `/ana/cimenaga/cimenagapastirma.com`. Dil: yalnızca Türkçe (`<html lang="tr">`).
- Statik, minimal HTML ve CSS. Efekt, animasyon, geçiş, hover efekti ve JS YOK.
- Hiçbir bilgi uydurulmaz. Doğrulanamayan sayısal bilgi (ör. saklama süresi) yazılmaz.
- `nutrition` (besin değeri) hiçbir yerde yazılmaz.
- Sucuğun üretimiyle ilgili iddia yazılmaz. Yalnızca yeme biçimleri anlatılır.
- Pastırma ve çemen bilgisi yalnızca cimenaga.com ve resmî kaynaklardan (TürkPatent vb.) alınır.
- Ürün bağlantıları yalnızca `https://cimenaga.com/urun/<slug>.html` biçiminde olur. Geçerli slug'lar: `kastamonu-pastirmasi`, `kastamonu-sucugu`, `kastamonu-pastirmali-ince-pide`.
- Görseller: Unsplash, Pexels ya da CC0 Wikimedia Commons. WebP, `width`, `height` ve dürüst `alt` ile. Görsel kaynakları sayfası YOK. Kaynaklar `docs/gorsel-kaynaklari.md` içinde tutulur.
- Bulunamayan görselde sayfa görselsiz kalır, `image` alanı schema'ya yazılmaz, kullanıcıya listelenir.
- Renk paleti ve serif başlıklar cimenaga.com ile aynı (`--ivory #faf6ee`, `--paper #fffdf8`, `--dark #1e1510`, `--ink #2b1f17`, `--muted #7a6a58`, `--line #e6dac3`, `--gold-d #8a6a2c`).
- Klasör git deposu değil. Plandaki "commit" adımlarının yerini `python3 docs/check.py` çalıştırmak alır.
- `docs/` yayına alınmaz. `robots.txt` içinde `Disallow: /docs/` bulunur.

## Review Focus

- Tarif adımı ya da malzemesi boş bırakıldığında ya da tek öğeli olduğunda sayfa ve schema bozulmamalı (`check.py` tarif başına en az 3 malzeme ve 2 adım ister).
- Başlıkta ve içerikte `&`, `<`, `"`, `'` gibi karakterler HTML ve JSON-LD içinde doğru kaçışlanmalı (`html.escape`, `json.dumps(ensure_ascii=False)`).
- Görseli olmayan tarif `image` alanı olmadan geçerli JSON-LD üretmeli ve kırık `<img>` bırakmamalı.
- Bir ürün slug'ı yanlış yazılırsa derleme hata vermeli (`PRODUCTS` sözlüğünde yoksa `KeyError`), sessizce kırık bağlantı üretmemeli.
- sitemap.xml'de olan ama dosyası olmayan ya da dosyası olup sitemap'te olmayan sayfa `check.py` tarafından yakalanmalı.


### Task 8: Görseller

**Files:**
- Create: `assets/img/*.webp`, `docs/gorsel-kaynaklari.md`
- Modify: `docs/content/**/*.json` (`image`, `image_alt`, `image_w`, `image_h`)

**Interfaces:**
- Consumes: 12 içerik dosyası.
- Produces: Görselli sayfalar ve kullanıcı için "görseli bulunamayanlar" listesi.

- [ ] **Step 1: Araçları kontrol et**

Run: `which cwebp magick convert; python3 -c "import PIL; print(PIL.__version__)"`
Expected: en az biri var. Yoksa kullanıcıya bildir.

- [ ] **Step 2: Her sayfa için görsel ara**

Unsplash, Pexels ve CC0 Wikimedia Commons'ta ara. Aranacaklar: pastırmalı yumurta, sucuklu yumurta, ince pide, tost, börek, patates, kuru fasulye, pastırma dilimleri, sarımsak, Kastamonu şehri. Lisans sayfasını WebFetch ile aç ve ücretsiz ticari kullanıma izin verdiğini doğrula. Sorun çıkan görseli kullanma. Dosyayı her biri kendi yeni boş klasörüne indir (örneğin scratchpad altında).

- [ ] **Step 3: Dönüştür ve yerleştir**

Genişlik en fazla 1200 px olacak şekilde WebP'ye çevir, `assets/img/<slug>.webp` olarak kaydet, gerçek `width` ve `height` değerlerini oku ve JSON'a yaz. `image_alt` görseli dürüstçe tanımlasın ("Tavada yumurtalı pastırma", pastırmanın Kastamonu olduğunu görselden anlaşılmıyorsa belirtme).

- [ ] **Step 4: Kaynak kaydı**

Her görsel için `docs/gorsel-kaynaklari.md` içine dosya adı, kaynak URL'si, fotoğrafçı ve lisans yaz. Bu bilgi sitede gösterilmez.

- [ ] **Step 5: Derle ve doğrula**

Run: `python3 docs/build.py && python3 docs/check.py`
Expected: `OK`.

- [ ] **Step 6: Görseli bulunamayan sayfaları listele.** Kullanıcıya göster.

