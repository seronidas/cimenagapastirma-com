# cimenagapastirma.com Tarif ve Makale Sitesi: Tasarım

Tarih: 2026-10-11

## Amaç
cimenaga.com'u destekleyen, SEO ve AEO uyumlu, statik bir tarif ve makale sitesi.
Her tarif sayfası, kullanılan ürün için `https://cimenaga.com/urun/...` sayfasına bağlanır.

## Kısıtlar (kullanıcıdan)
- Klasör: `/ana/cimenaga/cimenagapastirma.com`, dil yalnızca Türkçe.
- Statik, minimal HTML ve CSS. Efekt, animasyon ve JS yok (menü gerektirirse gerekmeyecek biçimde tasarlanır).
- Hiçbir bilgi uydurulmaz. Her şey gerçek ve doğru olmalı.
- Görseller internetten, telifsiz kaynaktan. Bulunamazsa sayfa görselsiz kalır ve kullanıcıya listelenir.
- Görsel kaynakları sayfası YOK.
- Recipe schema, sitemap.xml, robots.txt zorunlu. SEO ve AEO uyumlu.

## Dosya yapısı
```
index.html
tarifler/<slug>.html        (8)
makaleler/<slug>.html       (4)
assets/style.css
assets/img/*.webp
robots.txt
sitemap.xml
llms.txt
docs/                       (yayına alınmaz; robots.txt'te Disallow)
```
`index.html` tarifleri ve makaleleri iki listede gösterir, ayrı liste sayfası yoktur.

## İçerik
Tarifler: pastırmalı yumurta, sucuklu yumurta, pastırmalı ince pide, sucuklu pide, pastırmalı tost, pastırmalı börek, sucuklu patates, pastırmalı kuru fasulye.

Makaleler:
1. Kastamonu pastırması nedir, nasıl yapılır
2. Çemen ve Taşköprü sarımsağı
3. Pastırma nasıl dilimlenir ve saklanır
4. Kastamonu'nun coğrafi işaretli lezzetleri

## Sayfa şablonları
**Tarif:** H1, ilk paragrafta kısa cevap, süre ve porsiyon, malzemeler, adımlar, ipuçları, ürün bağlantısı ("Pastırmasını bizden alın" → cimenaga.com/urun/...), güncelleme tarihi. Başlıklar soru kalıbında olabilir.
**Makale:** H1, kısa cevap paragrafı, H2 bölümleri, ilgili tarif bağlantıları, ürün bağlantısı, güncelleme tarihi.
**Ortak:** canonical, meta description, Open Graph, BreadcrumbList, Organization (Çimenağa Pastırma), header ve footer. Footer'da cimenaga.com bağlantısı.

## Yapılandırılmış veri
- Tarif: `Recipe` (name, image, description, prepTime, cookTime, totalTime, recipeYield, recipeIngredient, recipeInstructions HowToStep, datePublished, author=Organization). `nutrition` YAZILMAZ.
- Makale: `Article` (headline, datePublished, dateModified, author, publisher).
- Tüm sayfalar: `BreadcrumbList`.
- `FAQPage` yalnızca sayfada görünür soru-cevap varsa.
- Schema, görünür içerikle birebir aynı olmalıdır.
- Görseli bulunamayan tarifte `image` alanı yazılmaz. Recipe zengin sonucu için görsel gerekeceği not edilir.

## Doğruluk kuralları
- Pastırma ve çemen bilgisi yalnızca cimenaga.com ve resmî kaynaklardan (ör. TürkPatent) alınır. Dayanak bir dipnot ya da içerik notunda kaydedilir.
- Sucuğun üretimiyle ilgili iddia yazılmaz. Yalnızca yeme biçimleri anlatılır.
- Tarif miktar ve süreleri klasik, yaygın tariflere dayanır. Yayından önce kullanıcıdan deneme ve onay istenir.
- Doğrulanamayan sayısal bilgi (ör. saklama süresi) yazılmaz.
- Besin değeri yazılmaz.

## Görseller
- Kaynak: Unsplash, Pexels ve CC0 Wikimedia Commons (atıf gerektirenler tercih edilmez).
- Her görselin kaynağı ve lisansı `docs/gorsel-kaynaklari.md` içinde tutulur. Site yayınında görünmez.
- WebP, boyutları belirtilmiş, `alt` metni görseli dürüstçe tanımlar. Genel stok fotoğraf "Kastamonu pastırması" diye etiketlenmez.
- Bulunamayan görseller kullanıcıya listelenir.

## Tasarım
cimenaga.com'daki renk paleti (`--ivory`, `--gold-d`, `--dark` vb.) ve serif başlıklar kullanılır. Geçiş, animasyon ve hover efekti yoktur. Mobil öncelikli, tek kolon.

## Test ve doğrulama
- Tüm iç bağlantılar çalışmalı. sitemap.xml'deki her URL'nin dosyası olmalı.
- JSON-LD sözdizimi geçerli olmalı (`python -m json.tool`).
- Tüm `cimenaga.com/urun/` bağlantıları gerçek dosyalarla eşleşmeli.
- Her görselin `width`, `height` ve `alt` değeri olmalı.
- Tarayıcıda mobil ve masaüstü görünümü kontrol edilir.

## Kapsam dışı
Sepet, çok dilli sürüm, yorum ve arama, analitik, besin değeri.
