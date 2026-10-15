# Düzeltme turu raporu
1. Important 1: yapıldı. Börek ve pidede ipucu yalnızca "orta tuzludur, sarımsağı belirgindir."
2. Important 2: yapıldı. Eylül–Nisan cümlesi "Çimenağa'nın hikâyemiz sayfasına göre" ile atfedildi.
3. Minor 1: yapıldı. Tost tips boş liste.
4. Minor 3: dokunulmadı. Kaynakta tepsi yağı zaten adımda ("yağlanmış fırın tepsisi"), mayalanma süresi kaynakta yok.
5. Minor 4: sucuklu-patates 2. adımdan "yumuşayana kadar" çıkarıldı; sucuklu-yumurta "isterseniz tereyağını"; kuru fasulye "Domatesleri ya da domates püresini". Dokunulmadı: pastirmali-borek (kaynakta doğrama yok), sucuklu-pide (kaynakta hamur bölme yok).
6. Minor 5: başlık "Pastırmanın tadı nasıldır?".
7. Minor 6: build_index cümlesi "Çimenağa'nın hikâyesi 1927'den beri uzanır; ürünler cimenaga.com adresindedir."
8. Minor 7: recipeCuisine "Türk", recipeCategory (JSON `category`), recipeYield ["N","N kişilik"] (N kişilik biçiminde; "8 adet" olduğu gibi).
9. Minor 8: og:type article (makaleler), og:site_name, twitter:card summary.
10. Minor 10: sitemap lastmod (index = en yeni modified).
11. Minor 13: kaynaklar.md slug pastirmali-pide.
12. Minor 14: .crumbs a padding/negatif margin.
Dosyalar: docs/build.py, docs/kaynaklar.md, assets/style.css, content/tarifler/*.json (8), content/makaleler/{kastamonu-pastirmasi-nedir,cemen-ve-taskopru-sarimsagi}.json, üretilen html/sitemap.
Test: build + check.py OK; nutrition/kaynaklarında grep boş.
