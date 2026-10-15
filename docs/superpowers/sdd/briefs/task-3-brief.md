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


### Task 3: Araştırma ve kaynak notları

**Files:**
- Create: `docs/kaynaklar.md`

**Interfaces:**
- Produces: Her makale ve tarif için doğrulanmış bilgi ve kaynak URL'leri. Task 4-7 yalnızca buradaki bilgilere dayanır.

- [ ] **Step 1: cimenaga.com'dan alıntıları çıkar**

`/ana/cimenaga/cimenaga.com/hikayemiz.html`, `urun/kastamonu-pastirmasi.html`, `kastamonu-cografi-isaretli-urunleri.html`, `hakkimizda.html` içinden pastırma, çemen, Taşköprü sarımsağı ve coğrafi işaret ile ilgili cümleleri `docs/kaynaklar.md` içine "cimenaga.com" başlığı altında, dosya adıyla birlikte kopyala.

- [ ] **Step 2: Resmî kaynaklarla doğrula**

WebSearch ile TürkPatent coğrafi işaret kayıtlarını ara: Kastamonu Pastırması (no 711, 2021, mahreç işareti), Taşköprü Sarımsağı (2010, AB tescili), Tosya Pirinci (2017). Her bilgi için en az bir resmî URL kaydet. Sitenle çelişen bir bilgi bulursan kullanıcıya bildir, sessizce seçme.

- [ ] **Step 3: Makale 3 için gerçek bilgi ara**

Pastırmanın dilimlenmesi ve saklanması (buzdolabı, kesilmiş/kesilmemiş, dondurma) için güvenilir kaynak ara (ör. Tarım ve Orman Bakanlığı, TÜRKOMP, akademik kaynak). Süre ve sıcaklık gibi sayısal değerleri yalnızca kaynakta açıkça yazıyorsa kaydet. Bulunamazsa "Bulunamadı, yazılmayacak" yaz.

- [ ] **Step 4: Her tarif için en az iki bağımsız kaynakta karşılaştır**

8 tarifin her biri için malzeme türleri, sıra ve pişirme süresi aralıklarını iki bağımsız tarif kaynağında (ör. Nefis Yemek Tarifleri, Yemek.com, resmî kültür turizm sayfaları) karşılaştır. Ortak olan aralıkları ve URL'leri `docs/kaynaklar.md` içine yaz. Birbirinden çok farklı olan değeri yazma.

- [ ] **Step 5: Kontrol**

Run: `grep -c "http" docs/kaynaklar.md`
Expected: en az 20 (8 tarif × 2 kaynak + resmî kaynaklar).

