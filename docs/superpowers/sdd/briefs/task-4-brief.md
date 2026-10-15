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


### Task 4: Tarifler 1-4

**Files:**
- Create/Modify: `docs/content/tarifler/pastirmali-yumurta.json`, `sucuklu-yumurta.json`, `pastirmali-ince-pide.json`, `sucuklu-pide.json`
- Generated: `tarifler/*.html`, `index.html`, `sitemap.xml`, `llms.txt`

**Interfaces:**
- Consumes: `docs/kaynaklar.md` (Task 3), JSON şeması (Task 2).
- Produces: 4 tarif sayfası.

Ürün eşleşmesi: `pastirmali-yumurta` → `["kastamonu-pastirmasi"]`; `sucuklu-yumurta` → `["kastamonu-sucugu"]`; `pastirmali-ince-pide` → `["kastamonu-pastirmasi", "kastamonu-pastirmali-ince-pide"]` (evde yapmak istemeyenler için hazır pide); `sucuklu-pide` → `["kastamonu-sucugu"]`.

- [ ] **Step 1: Her tarif için JSON yaz**

`answer` alanı tek paragraf ve doğrudan cevap olsun ("Pastırmalı yumurta yaklaşık X dakikada hazırlanır…"). Değerler yalnızca `docs/kaynaklar.md` içindeki ortak aralıklardan seçilir. `ingredients` en az 3, `steps` en az 2 öğe. Ölçüler Türkçe ve açık yazılır ("2 adet yumurta", "100 g pastırma"). Kastamonu pastırmasını anlatırken yalnızca doğrulanmış cümleleri kullan.

- [ ] **Step 2: Derle ve doğrula**

Run: `cd /ana/cimenaga/cimenagapastirma.com && python3 docs/build.py && python3 docs/check.py --partial`
Expected: "4 tarif, 0 makale üretildi" ve `OK`.

- [ ] **Step 3: Kullanıcıdan deneme onayı iste**

Dört tarifin sürelerini ve ölçülerini kullanıcıya liste halinde göster ve yayından önce denemesini ya da onaylamasını iste. Cevap gelene kadar bu 4 tarifi "onay bekliyor" olarak işaretle.

