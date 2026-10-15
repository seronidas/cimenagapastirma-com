# Task 2 raporu

Durum: DONE

Yapılanlar: assets/img/logo.png kopyalandı; assets/style.css ve docs/build.py brief'teki koda birebir yazıldı; docs/content/tarifler/pastirmali-yumurta.json taslağı yazıldı (nutrition yok, yalnızca genel bilgi, ürün slug'ı kastamonu-pastirmasi).

Komutlar ve çıktılar
- Step 5: `python3 docs/build.py && python3 docs/check.py --partial` -> "1 tarif, 0 makale üretildi", "OK"
- Step 6: products=["yanlis"] ile build -> `KeyError: 'yanlis'`; geri alındı, build -> "1 tarif, 0 makale üretildi"
- Step 7: title = `Pastırma & "Çemen" <test>` ile build + `check.py --partial` -> OK; `grep -c '&amp;' tarifler/pastirmali-yumurta.html` -> 4; başlık geri alındı, yeniden build + check -> OK. JSON'da title "Pastırmalı Yumurta", products ["kastamonu-pastirmasi"] doğrulandı.

Not: Build, kökte index.html, tarifler/, sitemap.xml, robots.txt, llms.txt üretti (beklenen çıktılar).
