# Task 3 raporu

Durum: Tamamlandı. Çıktı: docs/kaynaklar.md (`grep -c http` = 23).

## Bulunan
- cimenaga.com: 4 dosyadan alıntılar dosya adıyla yazıldı.
- TürkPatent PDF'leri (pdftotext ile okundu): Kastamonu Pastırması no 711 mahreç işareti 29.03.2021; Taşköprü Sarımsağı no 135 menşe adı 03.12.2009; Tosya Pirinci no 230 menşe adı 08.11.2017.
- 8 tarif için 2 bağımsız kaynak (Yemek.com + Nefis Yemek Tarifleri veya Lezzet), ortak malzeme, süre aralıkları, çelişkiler.

## Bulunamadı
- Taşköprü sarımsağının AB tescili için resmî kayıt/tarih (yalnızca haberler).
- "Sarımsak üretiminin yaklaşık %90'ı Taşköprü'den" iddiasının kaynağı.
- Pastırma saklama/dilimleme/dondurma için resmî veya akademik sayısal süre-sıcaklık: yok; yazılmayacak. Yemek.com'daki süreler (7-10 gün, 5-7 gün) güvenilir kaynak değil, kullanılmayacak.
- Resmî kültür-turizm tarif sayfası kullanılmadı.

## Siteyle çelişen bilgi
1. Taşköprü sarımsağı: site 2010, TürkPatent 03.12.2009 (başvuru 28.05.2009). Site düzeltilmeli.
2. Tosya pirinci: sitedeki "Ilgaz Dağları'ndan gelen kar suyu" ve "mineral zengini topraklar" resmî belgede bulunamadı (belge: Devrez Çayı'na dağlardan eriyen kar suyu). 2017 doğru.
3. Taşköprü AB tescili ve %90 oranı doğrulanamadı.

## Notlar
- Tarif sayfalarının özetleri WebFetch ile alındı; ölçüler özetten, tam doğrulama sayfalardan yapılabilir.
- Pastırmalı ince pide, sucuklu patates, börek için iki kaynak farklı yöntem anlatıyor; yalnızca ortak olanlar yazıldı, çelişkiler işaretlendi.
