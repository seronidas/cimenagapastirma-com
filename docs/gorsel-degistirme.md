# Görselleri kendi fotoğraflarınızla değiştirme

Sitedeki görseller şablon yer tutucusudur (kaynaklar: docs/gorsel-kaynaklari.md). Yayından önce şu adımları izleyin:

1. Fotoğrafı WebP olarak kaydedin (kalite ~80) ve `assets/img/` altına AYNI dosya adıyla koyun (eskisinin üzerine yazın).
2. İlgili JSON dosyasında (`docs/content/tarifler/<slug>.json` veya `docs/content/makaleler/<slug>.json`) `image_w` ve `image_h` değerlerini yeni dosyanın gerçek piksel ölçüleriyle, `image_alt` alanını fotoğrafta gerçekte görünenle (dürüstçe) güncelleyin.
3. Çalıştırın: `python3 docs/build.py && python3 docs/check.py`
4. Bittiğinde docs/gorsel-kaynaklari.md içindeki yer tutucu kayıtlarını silin/güncelleyin.

Anasayfa karşılama alanı artık görselsizdir (kompakt metin girişi); `hero.webp` kullanılmıyor. Anasayfadaki ürün kartları `assets/img/pastirma.webp`, `sucuk.webp`, `pide.webp` dosyalarını kullanır; aynı adla üzerine yazmanız yeterlidir.

| Sayfa | Dosya | Önerilen çözünürlük / oran |
|---|---|---|
| Ürün kartları (anasayfa ve tarif sonu) | assets/img/pastirma.webp, sucuk.webp, pide.webp | kare 1:1 (900x900) önerilir; kartta 4:3 kırpılır |
| Pastırmalı Yumurta | assets/img/pastirmali-yumurta.webp | 1200x900 (4:3) |
| Sucuklu Yumurta | assets/img/sucuklu-yumurta.webp | 1200x900 (4:3) |
| Pastırmalı Pide | assets/img/pastirmali-pide.webp | 1200x900 (4:3) |
| Sucuklu Pide | assets/img/sucuklu-pide.webp | 1200x900 (4:3) |
| Pastırmalı Börek | assets/img/pastirmali-borek.webp | 1200x900 (4:3) |
| Pastırmalı Tost | assets/img/pastirmali-tost.webp | 1200x900 (4:3) |
| Sucuklu Patates | assets/img/sucuklu-patates.webp | 1200x900 (4:3) |
| Pastırmalı Kuru Fasulye | assets/img/pastirmali-kuru-fasulye.webp | 1200x900 (4:3) |
| Makale: Kastamonu Pastırması Nedir? | assets/img/kastamonu-pastirmasi-nedir.webp | 1200x800 (3:2) veya 16:9 |
| Makale: Pastırma Nasıl Dilimlenir ve Saklanır? | assets/img/pastirma-nasil-dilimlenir-ve-saklanir.webp | 1200x800 (3:2) veya 16:9 |
| Makale: Çemen ve Taşköprü Sarımsağı | assets/img/cemen-ve-taskopru-sarimsagi.webp | 1200x800 (3:2) veya 16:9 |
| Makale: Kastamonu'nun Coğrafi İşaretli Lezzetleri | assets/img/kastamonu-cografi-isaretli-lezzetleri.webp | 1200x800 (3:2) veya 16:9 |

Not: Yatay (landscape) fotoğraf kullanın; kartlarda 4:3 / 16:9 kırpılır, önemli öğeyi ortada tutun.
