# Yeniden tasarım raporu
Durum: tamam. Değişen: assets/style.css, docs/build.py (page, figure, thumb, cta, card, build_recipe/article/index); kopyalanan: assets/img/{pastirma,sucuk,pide}.webp (900x900).
Test: build.py (8 tarif, 4 makale) + check.py OK; yerel sunucuda sayfalar ve CSS 200; JS/transition/hover yok.
Notlar: hero görseli CSS arka planı (inline style, hero.webp varsa), yoksa renk bandı; bu yüzden boyut okunmadı. Görselsiz kayıtlar gradient bandı gösterir. Tarayıcı aracı yok, görsel doğrulama yapılmadı. Şu an yalnızca sucuklu-pide görselli.
