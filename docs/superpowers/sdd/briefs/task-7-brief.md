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


### Task 7: Makaleler 3-4

**Files:**
- Create: `docs/content/makaleler/pastirma-nasil-dilimlenir-ve-saklanir.json`, `kastamonu-cografi-isaretli-lezzetleri.json`

**Interfaces:**
- Consumes: Task 3.
- Produces: 2 makale sayfası daha (toplam 4).

İçerik sınırı: Makale 3 yalnızca Task 3, Step 3'te kaynağı bulunan bilgileri içerir. Bulunamayan sayısal bilgi (saklama süresi vb.) yazılmaz. Dilimleme için sitedeki ifadeler ("ince dilimlenip tavada, yumurta ya da pideyle") kullanılabilir. Makale 4: sitedeki coğrafi işaretli ürün listesi (Taşköprü Sarımsağı, Kastamonu Pastırması, Tosya Pirinci ve "Tescilli Diğer Lezzetler"), listenin zamanla değişebileceği notuyla ve TürkPatent veri tabanına yönlendirmeyle.

- [ ] **Step 1: İki JSON yaz.**

- [ ] **Step 2: Derle ve tam doğrulamayı çalıştır**

Run: `python3 docs/build.py && python3 docs/check.py`
Expected: "8 tarif, 4 makale üretildi" ve `OK` (`--partial` olmadan).

