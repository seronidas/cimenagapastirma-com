# Son inceleme: cimenagapastirma.com

Tarih: 2026-10-11. İnceleyen bağımsızdı ve hiçbir dosyayı değiştirmedi; yalnızca bu rapor yazıldı.

## Nasıl doğrulandı

- `python3 docs/check.py` çalıştırıldı ve `OK` verdi.
- `docs/build.py`, scratchpad'deki bir kopyada yeniden çalıştırıldı. 13 HTML dosyası ile robots, sitemap ve llms dosyaları yayındaki dosyalarla bayt bayt aynı çıktı, yani yayındaki çıktı kaynakla uyumlu.
- 12 JSON dosyası ve üretilen sayfalar tek tek okundu. `kaynaklar.md` ile cimenaga.com'daki şu sayfalar karşılaştırıldı: hikayemiz, hakkimizda, kastamonu-cografi-isaretli-urunleri ve 3 ürün sayfası.
- Tarif kaynaklarından 8 sayfa yeniden açıldı (yemek.com ×6, lezzet ×2): pastırmalı pide, kuru fasulye, tost, pastırmalı yumurta, sucuklu pide, sucuklu yumurta, börek ve sucuklu patates. Ölçüler, süreler, kişi sayıları ve ipuçları kaynaklarla eşleşiyor.
- Kontrast WCAG formülüyle hesaplandı. Sucuklu pide görseli gözle incelendi; alt metni doğru.

## Critical

Yok.

**Yayın kapısı (kusur değil):** Spec'e göre tarifler kullanıcı denedikten ve onayladıktan sonra yayına girer. Bu onay hâlâ bekliyor (Ruling).

## Important

1. **Mantıksız tuz ipucu.**
   - Yer: `docs/content/tarifler/pastirmali-borek.json` ve `docs/content/tarifler/pastirmali-pide.json`, `tips[0]`.
   - Sorun: İpucu "tuzu en son tadarak ekleyin" diyor. Ancak börekte tuz hiç yok. Pidede de tuz 2. adımda hamura giriyor; harç çiğ olduğu için sonradan tadılamaz.
   - Öneri: Bu iki tarifte ipucunu yalnızca "Kastamonu pastırması orta tuzludur, sarımsağı belirgindir." olarak bırakın ya da tümüyle kaldırın.
2. **Yanlış atıf.**
   - Yer: `docs/content/makaleler/kastamonu-pastirmasi-nedir.json`, `sections[0].paras[0]`.
   - Sorun: Metin "Çimenağa'nın ürün sayfasına göre … Üretim genellikle Eylül'den Nisan'a kadar sürer." diyor. Eylül–Nisan bilgisi ürün sayfasında yok; `hikayemiz.html`'de ve TürkPatent belgesinde var.
   - Öneri: Atfı "Çimenağa'ya göre" yapın ya da bu cümleyi TürkPatent paragrafına taşıyın.
3. **7 tarif görselsiz.**
   - Yer: `tarifler/*.html` (sucuklu-pide dışındaki 7 tarif).
   - Sorun: Google Recipe zengin sonucu için `image` zorunludur. Bu 7 tarifin zengin sonuç alma şansı yok; spec bunu biliyor. Schema yine de geçerli: kırık `img` yok ve `image` alanı yazılmamış.
   - Öneri: Kullanıcı fotoğraf çektirmeli. Görseller 1:1, 4:3 ve 16:9 oranlarında, en az 1200 px genişlikte olmalı.
4. **`docs/` yayına çıkmamalı.**
   - Sorun: robots.txt'teki `Disallow: /docs/` yalnızca taramayı engeller, erişimi engellemez. `docs/` içinde iç notlar, ledger, `unused-img` ve `gorsel-kaynaklari.md` var. Spec bu klasörün "yayına alınmaz" olduğunu söylüyor.
   - Öneri: Sunucuya yükleme listesi şu olmalı: `index.html`, `tarifler/`, `makaleler/`, `assets/`, `robots.txt`, `sitemap.xml`, `llms.txt`.
5. **Siteler arası çelişki (cimenaga.com tarafı).**
   - Yer: `/ana/cimenaga/cimenaga.com/kastamonu-cografi-isaretli-urunleri.html`.
   - Sorun: Bu sayfada şu ifadeler var: Taşköprü sarımsağının "2010" tescili (resmî kayıtta 03.12.2009), "AB'de de tescilli", "yüzde 90" ve Tosya pirinci için "Ilgaz / mineral". Yeni site resmî kaydı izliyor; iki marka sitesi farklı şey söyleyecek. Yeni sitenin kendisinde hata yok (Ruling).
   - Öneri: cimenaga.com sayfası yayından önce ya da yayınla aynı anda düzeltilmeli.

## Minor

1. **Tost ipuçları.**
   - Yer: `pastirmali-tost.json`, `tips[0]` ve `tips[1]`.
   - Sorun: `tips[0]`'daki "aromasını daha iyi açığa çıkarır" gerekçesi kaynakta yok; kaynak yalnızca "peyniri eklemeden önce pastırmayı 1–2 dk ısıtın" diyor. `tips[1]` ise 3. adımı tekrar ediyor.
2. **"Çemensiz pastırma" notu atlanmış.**
   - Yer: `pastirmali-yumurta.json` ve `pastirmali-tost.json`.
   - Sorun: Kaynak tarifler açıkça çemensiz pastırma istiyor; tost kaynağına göre bu, baharat aromasını dengeliyor. Bizim tarifler çemenli ürüne yönlendiriyor. Yazılan bir şey yanlış değil, ama kaynaktan bilinçli bir sapma. İstenirse şu ipucu eklenebilir: "Kaynak tarif çemensiz pastırma kullanır; dilerseniz çemeni sıyırabilirsiniz." Bu cümle kaynakta var.
3. **Pastırmalı pide: eksik malzeme ve süre.**
   - Yer: `pastirmali-pide.json`.
   - Sorun: Tepsiyi yağlamak için gereken yağ malzemelerde yok; kaynakta da ölçüsüz. Mayalanma süresi de verilmemiş, bu yüzden "25 dakika hazırlık" mayalanmayı içermiyor.
   - Öneri: `answer` alanına "mayalanma hariç" ekleyin.
4. **Kaynaktan devralınan adım belirsizlikleri.** Kaynaklarla aynı, ama okuru şaşırtabilir:
   - `sucuklu-patates`: 2. adım "yumuşayana kadar" diyor, 3. adım "yumuşamaya başlayınca" diyor.
   - `pastirmali-borek`, `steps[0]`: Domates, biber ve pastırmanın doğranacağı söylenmiyor.
   - `sucuklu-pide`: Hamurun kaç parçaya bölüneceği yok.
   - `sucuklu-yumurta`, `steps[1]`: Tereyağı malzemelerde "isteğe bağlı", ama adımda koşulsuz eritiliyor.
   - `pastirmali-kuru-fasulye`, `steps[4]`: "Domatesleri" deniyor; püre seçeneğiyle uyuşmuyor.
5. **Başlık fazla vaat ediyor.**
   - Yer: `cemen-ve-taskopru-sarimsagi.json`, `sections[1].h2`.
   - Sorun: Başlık "Çemen pastırmanın tadını nasıl etkiler?" diye soruyor, ama paragraf çemen ile tat arasında bir neden-sonuç ilişkisi kurmuyor.
   - Öneri: Başlığı "Kastamonu pastırmasının tadı nasıldır?" yapın.
6. **Yanlış okunabilecek cümle.**
   - Yer: `docs/build.py`, `build_index`, kısa cevap paragrafı.
   - Sorun: "Ürünlerimiz 1927'den beri Kastamonu'dan, cimenaga.com üzerinden sipariş edilir." cümlesi, 1927'den beri online sipariş alınıyormuş gibi okunuyor.
   - Öneri: Cümleyi ikiye bölün.
7. **Recipe schema ayrıntıları.**
   - `recipeYield` şu an "4 kişilik". Google'ın sayıyı kesin okuması için `["4", "4 kişilik"]` biçimi önerilir.
   - Google'ın önerdiği `recipeCuisine` ("Türk"), `recipeCategory` ve `keywords` alanları yok.
8. **Open Graph eksikleri.**
   - Makalelerde `og:type` "website"; "article" olmalı.
   - 12 sayfada `og:image` yok; logo yedek olarak kullanılabilir.
   - `og:site_name` ve `twitter:card` yok.
9. **Ana sayfada BreadcrumbList yok.** Spec "tüm sayfalar" diyor; check.py ana sayfayı muaf tutuyor. Tek öğeli bir breadcrumb işe yaramaz; spec'e not düşmek yeterli.
10. **`sitemap.xml`'de `<lastmod>` yok.** `modified` alanından üretilebilir.
11. **İç bağlantılar ve tekrar eden içerik.**
    - `kastamonu-pastirmasi-nedir`, `sections[1].paras[1]` metin içinde "Çemen ve Taşköprü sarımsağı makalesi"ni anıyor, ama bağlantı vermiyor.
    - Tarif sayfalarından makalelere bağlantı yok.
    - Tescil ayrıntıları 3 makalede, çemen bileşimi 2 makalede aynen tekrar ediyor.
12. **Makale 3 (dilimleme ve saklama).**
    - Meta description zayıf: "sayısal süre içermeyen kısa notlar".
    - "Pastırma nasıl dilimlenir?" başlığı bir yöntem anlatmıyor. Bu Ruling gereği, ama başlık "Pastırma ne kalınlıkta dilimlenir?" yapılabilir.
13. **Eski slug.** `docs/kaynaklar.md` 84. ve 143. satırlarda hâlâ eski `pastirmali-ince-pide` slug'ını kullanıyor. Yalnızca belgeyi etkiliyor.
14. **Küçük dokunma hedefi.** `assets/style.css`'teki `.crumbs` bağlantısı 0.85rem; mobilde dokunma hedefi yaklaşık 23 px, yani küçük. CSS'in geri kalanı sorunsuz.

## Doğrulanan ve sorunsuz olanlar

- **Doğruluk.**
  - Makalelerdeki her olgu ya TürkPatent kaydına (`kaynaklar.md` tablosu ve belge notları) ya da cimenaga.com sayfalarına dayanıyor: no 711/135/230, tarihler, tescil ettirenler, %60/30/8/1/0,5/0,5 bileşimi, 3 gün, 30 gün, sayvan, 0,75 mm, Devrekani, 1927.
  - AB, %90, Ilgaz ve "mineral" ifadeleri sitede yok (grep).
  - Sucuk üretimiyle ilgili bir iddia yok.
  - Besin değeri ya da kalori yok.
  - Saklama için sayısal süre yok. Yemek.com önerileri "bir tarif sitesine göre" çerçevesinde verilmiş.
  - 8 tarifin ölçüleri, süreleri ve kişi sayıları tek kaynağıyla birebir uyuşuyor (WebFetch ile yeniden doğrulandı).
- **Spec uyumu.**
  - Sitede yalnızca `application/ld+json` script'i var.
  - CSS'te transition, animation ya da `:hover` yok.
  - `nutrition` alanı yok.
  - Ürün bağlantıları 3 gerçek `cimenaga.com/urun/*.html` dosyasına gidiyor.
  - Her sayfada canonical, `og:url`, BreadcrumbList, Recipe ya da Article ve `dateModified` var.
  - `img` öğelerinde `width`, `height` ve `alt` var: logo 210×144 dosya, 105×72 gösterim; pide görseli 1200×900.
  - robots.txt'te `Disallow: /docs/` ve Sitemap satırı var.
  - sitemap 13 URL içeriyor ve diskteki dosyalarla eşleşiyor.
- **SEO.**
  - 13 title'ın hepsi tekil ve 32–61 karakter arasında.
  - Meta description'lar 98–130 karakter; hiçbiri çok uzun ya da kısa değil.
  - Her sayfada tek H1 var ve ilk paragraf kısa cevap.
  - Makale H2'leri soru biçiminde.
  - Tarif sayfalarındaki `answer`, `description`, `meta` ve `yield` alanlarındaki süreler ve kişi sayıları birbiriyle tutarlı.
  - Malzemelerin hepsi adımlarda kullanılıyor.
- **Erişilebilirlik.**
  - Kontrast oranları:
    - muted/ivory: 4.83
    - gold-d/ivory: 4.66
    - sand/dark: 9.93
    - odak çizgisi, footer'da gold-d/dark: yaklaşık 3.6
  - `:focus-visible` tanımlı. Sayfa tek kolon, `flex-wrap` kullanıyor ve 20 px kenar boşluğu var; taşma riski görülmedi.

## Ledger'daki "minor (deferred)" maddeleri

| Madde | Durum | Yayından önce gerekli mi? |
|---|---|---|
| Task 4: Pide hamur ölçüleri miktarsız | 5b ile çözüldü; iki pidenin de tam ölçüleri var. Yalnızca tepsi yağı eksik (Minor 3). | Hayır, maddeyi kapatın |
| Task 4: sucuklu-yumurta ve sucuklu-pide ipuçları adımları tekrar ediyor | Çözüldü. İpuçları artık kaynağın püf noktaları (tava türü, servis, hamur kıvamı, yumurta) ve adım tekrarı değil. Benzer tekrar artık pastirmali-tost'ta (Minor 1). | Hayır |

**Yayından önce düzeltilmesi gerekenler:** Important 1 ve 2 (iki JSON alanı, ardından build ve check), Important 4 (yükleme listesi) ve kullanıcının tarif deneme onayı. Important 3 ile 5 kullanıcının vereceği kararlar.

## Genel hüküm

Site teknik olarak temiz. Doğruluk açısından da güçlü: uydurma ya da kaynaksız sayısal iddia bulunamadı. Yayına engel olan iki küçük metin hatası (tuz ipucu ve atıf) ile kullanıcının tarif deneme onayı. Bunlar giderilince yayına uygun.
