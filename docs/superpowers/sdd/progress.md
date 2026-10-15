# SDD ledger — plan: docs/superpowers/plans/2026-10-11-tarif-sitesi.md

Ruling: Klasör git deposu değil; git/worktree/review-package betikleri kullanılmayacak. Brief'ler plandan sed ile çıkarılır, inceleme dosyaları doğrudan okuyarak yapılır, "commit" yerine `python3 docs/check.py` kullanılır — plan zaten bunu söylüyor — git init yapmak kullanıcının klasöründe istenmeyen değişiklik olurdu.
Ruling: Görsel ve tarif içeriği görevlerinde kullanıcı onayı gerektiren noktalar (Task 4/5 deneme onayı) son raporda toplanır, yürütme durmaz — "onay bekliyor" olarak işaretlenir; yayına alma kararı kullanıcıdadır.

## Pre-flight tablo
| Satır | Bulgu |
| T1 check.py ↔ T2 build.py | check.py `ul#malzemeler`, `ol#adimlar`, canonical, `<script>` kuralları; build.py bunları üretiyor. Uyumlu. |
| T2 ↔ T4-T7 | JSON şeması T2'de tanımlı, içerik görevleri aynı alanları kullanıyor. Uyumlu. |
| T2 ↔ T8 | image/image_alt/image_w/image_h alanları build.py'de destekli. Uyumlu. |
| T1 | `--partial` bayrağı T2-T7'de kullanılıyor, T9'da yok. Tutarlı. |
| T2 | Plan: figure() `image_alt` zorunlu, image varsa. Tutarlı. |
| T3 | Tek bağımsız görev, docs/kaynaklar.md üretir; T4-T7 tüketir. Tutarlı. |
| T6/T7 ↔ related | related slug'ları T4/T5'te var olmalı; T4/T5 önce çalışıyor. Tutarlı. |
Sonuç: çelişki yok.
Ruling: Task 1 incelemesi mekanik yapıldı (kod plandaki bloğa birebir eşit + check.py beklenen 6 hatayla çıkış 1) — git yok, kod plandan aktarma — yanlışsa Task 2 testleri yakalar.
Note: Plan Task 1 Step 1 kod bloğunun kapanış fence'i eksikti, düzeltildi.
Task 1: complete (review clean)
Task 2: complete (review clean: kod plana birebir eşit, build+check OK, taslak tarif Task 4'te doğrulanacak)
Ruling: Taşköprü sarımsağı tescil yılı: sitemizde resmî TürkPatent kaydı esas alınır (tescil 03.12.2009, no 135); cimenaga.com "2010" diyor — çelişki son raporda kullanıcıya bildirilir, cimenaga.com düzeltmesi önerilir — yanlışsa tek yıl değişir.
Ruling: "AB'de de tescilli" ve "sarımsağın yaklaşık %90'ı Taşköprü'den" iddiaları resmî kaynakla doğrulanamadığı için YAZILMAZ; Tosya pirinci anlatımı yalnızca resmî belgeye dayanır (Ilgaz/mineral ifadeleri yok) — kullanıcı isterse kaynak gösterip eklenir.
Ruling: Makale 3 saklama/dilimleme yalnızca niteliksel; sayısal süre/sıcaklık/dondurma bilgisi YOK; Yemek.com önerileri yazılırsa "bir tarif sitesine göre" çerçevesinde; dilim kalınlığı yalnızca TürkPatent ürün tanımı olarak — içerik kısa kalır ama uydurma riski sıfır.
Task 3: complete (review: kaynaklar.md okundu, çelişkiler ayrı işaretli)
Task 4: minor (deferred): pastırmalı/sucuklu pide hamur ölçüleri kaynaklar arası çelişkili olduğu için miktarsız (un, maya, su, pastırma) — kullanıcıdan kendi hamur ölçüsü istenecek (pideyi kendileri yapıyor).
Task 4: minor (deferred): sucuklu-yumurta ve sucuklu-pide ipuçlarının bir kısmı adımları tekrar ediyor — son incelemede sadeleştirilecek.
Ruling: Task 4 tarifleri kaynaklardan ortak değerlerle kabul edildi; miktarsız malzeme uydurmadan kalır — yanlışsa kullanıcı ölçü verir, JSON'da tek satır değişir.
Task 4: complete (review: 4 JSON okundu, build+check OK; kullanıcı deneme onayı bekliyor)
Task 5: complete (review: 4 JSON okundu, build+check OK) — ancak 8 tarif yayın kalitesinde değil: miktarsız malzemeler, "Tarif kaynaklarında…" meta ipuçları.
Ruling: Ek görev 5b (plan dışı): her tarif için TEK bir gerçek kaynağın bütün ölçüleri ve yöntemi alınır (karışık değil), kendi cümlelerimizle yazılır, miktarlar tamamlanır, meta ipuçları kaldırılır; kaynak URL'si docs/kaynaklar.md'ye "kullanılan kaynak" olarak yazılır. Dayanak: spec "tarif miktarları klasik tariflere dayanır, kullanıcı denemesi/onayı şart" diyor — yanlışsa kullanıcı denemesinde ölçüler düzeltilir.
Ruling: sucuklu-patates'in kaynaksız 2 ipucu silindi; build.py ipucu yoksa "İpuçları" başlığını basmıyor (tips_html) — plan kodundan küçük sapma — yanlışsa tek fonksiyon.
Ruling: "pastirmali-ince-pide" tarifi kaynağı sıradan pastırmalı pide olduğundan "pastirmali-pide" / "Pastırmalı Pide" olarak yeniden adlandırıldı (ince pide ürününüz ayrı; CTA'da hazır ürün olarak duruyor) — kullanıcı kendi ince pide hamur tarifini verirse ayrı bir "ince pide" tarifi eklenebilir.
Task 5b: complete (review: JSON'lar okundu, 2 düzeltme controller tarafından, build+check OK)
Ruling: Makale 4'e "diğer tescilli lezzetler" isimleri cimenaga.com/kastamonu-cografi-isaretli-urunleri.html'den "Çimenağa'ya göre" atfıyla eklendi (resmî kayıtla ayrıca doğrulanmadı) — yanlışsa tek paragraf.
Task 6: complete; Task 7: complete (review: 4 makale okundu, yasaklı ifade grep'i temiz, build+check tam OK). Not: Makale 3 kısa ve "bulamadık" dilinde; saklama tavsiyesi niteliksel.
Ruling: Task 8: kuru fasulye görseli (kuşbaşı etli, pastırmasız) yanıltıcı olacağından siteden çıkarıldı, docs/unused-img/'e taşındı — 7 tarif görselsiz, yalnız sucuklu-pide görselli — kullanıcı fotoğraf çektirecek (zaten planlıydı).
Task 8: complete (review: görseller gözle incelendi, lisans kaydı okundu)
Task 9 / final review: complete (fix round 1 uygulandı; scoped re-review controller tarafından build+check+örnek okuma ile yapıldı — git yok). Yapılmayanlar: kaynakta dayanağı olmayan adım ayrıntıları.
Ruling: Şablon aşaması: yer tutucu görseller (bacon'lı yumurta, dilimli salam/jambon vb.) alt metinleri dürüst olacak şekilde kullanıldı; kullanıcı kendi fotoğraflarıyla değiştirecek — yayından önce değiştirilmezse yanlış ürün görseli kalır.
