#!/usr/bin/env python3
"""İçerikten statik siteyi üretir. Kullanım: python3 docs/build.py"""
import html
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "docs" else HERE.parent / "cimenagapastirma.com"
CONTENT = HERE / "content"
SITE = "https://cimenagapastirma.com"
SHOP = "https://cimenaga.com"
PRODUCTS = {
    "kastamonu-pastirmasi": ("Kastamonu Pastırması", "Pastırmasını bizden alın"),
    "kastamonu-sucugu": ("Kastamonu Sucuğu", "Sucuğunu bizden alın"),
    "kastamonu-pastirmali-ince-pide": ("Kastamonu Pastırmalı İnce Pide (Pastırmalı Ekmek)", "Pastırmalı ince pideyi bizden alın"),
}
PRODIMG = {
    "kastamonu-pastirmasi": ("pastirma.webp", "Kastamonu pastırması"),
    "kastamonu-sucugu": ("sucuk.webp", "Kastamonu sucuğu"),
    "kastamonu-pastirmali-ince-pide": ("pide.webp", "Kastamonu pastırmalı ince pide (pastırmalı ekmek)"),
}
TRUST_BADGES = {
    "kastamonu-pastirmasi": [
        "🏛️ <b>Tescil No: 711</b> Mahreç İşareti",
        "⛰️ <b>Ilgaz Esintisi</b> Çimenağa'da ~60 Gün Olgunlaşma",
        "🧄 <b>Taşköprü Sarımsaklı</b> Çimen (Çemen)",
        "❄️ <b>Soğuk Zincir</b> Vakumlu Taze Kargo",
    ],
    "kastamonu-sucugu": [
        "🥩 <b>%100 Dana Eti</b> Fermente Sucuk",
        "🪵 <b>Geleneksel</b> Taşköprü Sarımsaklı Formül",
        "❄️ <b>Soğuk Zincir</b> Vakumlu Taze Kargo",
    ],
    "kastamonu-pastirmali-ince-pide": [
        "🥖 <b>Odun Fırınında</b> İnce Pide (Pastırmalı Ekmek)",
        "❄️ <b>Dondurulmuş</b> Gönderilir",
        "🥩 <b>Kastamonu Pastırmalı</b> İnce Hamur",
    ],
}
# Ana alan adı cimenaga.com; @id oradaki LocalBusiness kaydıyla aynı varlığı gösterir.
ORG = {"@type": "Organization", "@id": f"{SHOP}/#business", "name": "Çimenağa Pastırma & Sucuk",
       "url": SHOP + "/", "sameAs": [SHOP + "/", "https://www.instagram.com/cimenagapastirma/"]}
e = html.escape


def iso(minutes):
    h, m = divmod(minutes, 60)
    return "PT" + (f"{h}H" if h else "") + (f"{m}M" if m or not h else "")


def dur(minutes):
    h, m = divmod(minutes, 60)
    parts = ([f"{h} sa"] if h else []) + ([f"{m} dk"] if m or not h else [])
    return " ".join(parts)


LINK = re.compile(r"\[([^\]]+)\]\((/[^)\s]*|https://cimenaga\.com/[^)\s]*)\)")


def rich(text):
    """Paragraf metni: kaçış uygular, [metin](/yol veya https://cimenaga.com/...) biçimini bağlantıya çevirir."""
    return LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', e(text))


def plain(text):
    return LINK.sub(r"\1", text)


def table_html(t):
    head = "".join(f'<th scope="col">{e(h)}</th>' for h in t["head"])
    rows = "".join("<tr>" + f'<th scope="row">{e(r[0])}</th>' + "".join(f'<td data-label="{e(h, quote=True)}">{e(c)}</td>' for h, c in zip(t["head"][1:], r[1:])) + "</tr>" for r in t["rows"])
    note = f'<p class="tbl-note">{e(t["note"])}</p>' if t.get("note") else ""
    return (f'<div class="tbl"><table><caption>{e(t["caption"])}</caption><thead><tr>{head}</tr></thead>'
            f"<tbody>{rows}</tbody></table></div>{note}")


def table_md(t):
    out = [f"**{t['caption']}**", "", "| " + " | ".join(t["head"]) + " |", "|" + "---|" * len(t["head"])]
    out += ["| " + " | ".join(r) + " |" for r in t["rows"]]
    return out + ([t["note"]] if t.get("note") else [])


def yld(s):
    m = re.fullmatch(r"(\d+) kişilik", s)
    return [m.group(1), s] if m else s


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def url_of(rel):
    return SITE + "/" if rel == "index.html" else f"{SITE}/{rel}"


def ld_tag(d):
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def crumbs(items):
    """items: [(ad, mutlak_url)]; son öğe geçerli sayfadır."""
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}
    links = [f'<a href="{e(u.replace(SITE, "") or "/")}">{e(n)}</a>' for n, u in items[:-1]]
    return ld, '<nav class="crumbs" aria-label="Sayfa yolu">' + " › ".join(links + [e(items[-1][0])]) + "</nav>"


def img_size(rel, default=(1600, 900)):
    """Görsel boyutu: PIL varsa onunla, yoksa WebP başlığından (VP8/VP8L/VP8X); olmazsa varsayılan."""
    p = ROOT / rel
    if not p.is_file():
        return None
    try:
        from PIL import Image
        with Image.open(p) as im:
            return im.size
    except Exception:
        pass
    try:
        b = p.read_bytes()[:40]
        if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
            k = b[12:16]
            if k == b"VP8X":
                return (int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1)
            if k == b"VP8 ":
                return (int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF)
            if k == b"VP8L":
                v = int.from_bytes(b[21:25], "little")
                return ((v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1)
    except Exception:
        pass
    return default


def page(rel, title, desc, body, ld, image=None):
    otype = "article" if rel.startswith(("makaleler/", "tarifler/")) else "website"
    image = image or "hero.webp"
    og = f'\n<meta property="og:image" content="{SITE}/assets/img/{e(image)}">'
    gver = '\n<meta name="google-site-verification" content="googleef782f67a7468754">' if rel == "index.html" else ""
    scripts = "\n".join(ld_tag(d) for d in ld)
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc, quote=True)}">
<link rel="canonical" href="{url_of(rel)}">{gver}
<meta property="og:type" content="{otype}">
<meta property="og:site_name" content="Çimenağa Tarifler">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{e(title, quote=True)}">
<meta property="og:description" content="{e(desc, quote=True)}">
<meta property="og:url" content="{url_of(rel)}">{og}
<meta name="theme-color" content="#14284b">
<link rel="icon" href="/assets/img/icon.png?v=1">
<link rel="apple-touch-icon" href="/assets/img/icon.png?v=1">
<link rel="stylesheet" href="/assets/style.css">
{scripts}
</head>
<body>
<header><div class="wrap">
<a class="logo" href="{SHOP}/?ref=tarif_header"><img src="/assets/img/logo.png" alt="Çimenağa Pastırma" width="105" height="72"></a>
<nav aria-label="Ana menü"><a href="/#tarifler">Tarifler</a><a href="/#makaleler">Makaleler</a><a href="{SHOP}/urunlerimiz.html?ref=tarif_header">Ürünlerimiz</a><a class="shop" href="{SHOP}/?ref=tarif_header">Mağaza</a></nav>
</div></header>
<main>
{body}
</main>
<footer><div class="wrap">
<div><p><b>Çimenağa Pastırma &amp; Sucuk</b></p>
<p>1927'den beri Kastamonu</p></div>
<p class="fnav"><a href="/#tarifler">Tarifler</a> <a href="/#makaleler">Makaleler</a> <a href="/iade-ve-iptal-politikasi.html">İptal ve İade Koşulları</a> <a href="{SHOP}/?ref=tarif_footer">cimenaga.com</a> <a href="https://www.instagram.com/cimenagapastirma/" rel="me noopener">Instagram</a></p>
</div></footer>
</body>
</html>
"""


def figure(d, cls="cover"):
    """Kapak: görsel varsa img (aspect-ratio + cover), yoksa renk bandı yedeği."""
    if not d.get("image"):
        return f'<div class="{cls} ph" role="presentation"></div>'
    return (f'<figure class="{cls}"><img src="/assets/img/{e(d["image"])}" alt="{e(d["image_alt"], quote=True)}" '
            f'width="{d["image_w"]}" height="{d["image_h"]}"></figure>')


def thumb(d):
    if not d.get("image"):
        return '<div class="pic ph" role="presentation"></div>'
    return (f'<div class="pic"><img src="/assets/img/{e(d["image"])}" alt="{e(d["image_alt"], quote=True)}" '
            f'width="{d["image_w"]}" height="{d["image_h"]}" loading="lazy"></div>')


def cta(d, pfx="tarif"):
    if not d.get("products"):
        return ""
    out = []
    for s in d["products"]:
        name, label = PRODUCTS[s]  # bilinmeyen slug KeyError verir
        f, alt = PRODIMG[s]
        w, h = img_size(f"assets/img/{f}") or (900, 900)
        badges = "".join(f'<span class="badge-item">{b}</span>' for b in TRUST_BADGES.get(s, []))
        badges_html = f'<div class="trust-badges">{badges}</div>' if badges else ""
        out.append(f'<div class="buy"><img src="/assets/img/{f}" alt="{e(alt)}" width="{w}" height="{h}" loading="lazy">'
                   f'<div class="buy-txt"><p class="eyebrow">Çimenağa · 1927\'den beri</p><h2>{e(name)}</h2>'
                   f'{badges_html}'
                   f'<a class="btn" href="{SHOP}/urun/{s}.html?ref={pfx}&amp;kaynak={d["slug"]}&amp;konum=cta">{e(label)} <span aria-hidden="true">→</span></a></div></div>')
    return '<section class="cta"><div class="wrap">' + "".join(out) + "</div></section>" if out else ""


def sticky_bar(d, pfx="tarif"):
    if not d.get("products"):
        return ""
    p = d["products"][0]
    name = PRODUCTS[p][0]
    f, alt = PRODIMG[p]
    return f"""<aside class="sticky-bar" aria-label="Hızlı sipariş">
<div class="wrap sticky-wrap">
<div class="sticky-info">
<img src="/assets/img/{f}" alt="{e(alt)}" width="44" height="44" loading="lazy">
<div class="sticky-txt">
<p class="sticky-title">{e(name)}</p>
<p class="sticky-sub">1927'den beri · Çimenağa</p>
</div>
</div>
<a class="btn sticky-btn" href="{SHOP}/urun/{p}.html?ref={pfx}&amp;kaynak={d['slug']}&amp;konum=mobil_bar">Sipariş Ver <span aria-hidden="true">→</span></a>
</div>
</aside>"""


def format_ingredient_html(text, slug):
    text_lower = text.lower()
    if "pastırma" in text_lower:
        url = f"{SHOP}/urun/kastamonu-pastirmasi.html?ref=tarif&amp;kaynak={slug}&amp;konum=malzeme"
        idx = text_lower.find("pastırma")
        before = e(text[:idx])
        after = e(text[idx+len("pastırma"):])
        link = f'<a class="ing-buy" href="{url}" target="_blank" rel="noopener">Kastamonu pastırması <span class="ing-tag">Bizden alın →</span></a>'
        return before + link + after
    elif "sucuk" in text_lower:
        url = f"{SHOP}/urun/kastamonu-sucugu.html?ref=tarif&amp;kaynak={slug}&amp;konum=malzeme"
        idx = text_lower.find("sucuk")
        before = e(text[:idx])
        after = e(text[idx+len("sucuk"):])
        link = f'<a class="ing-buy" href="{url}" target="_blank" rel="noopener">Kastamonu sucuğu <span class="ing-tag">Bizden alın →</span></a>'
        return before + link + after
    return e(text)


def tips_html(d):
    if not d["tips"]:
        return ""
    return "<h2>İpuçları</h2>\n<ul class=\"tips\">\n" + "".join(f"<li>{e(x)}</li>" for x in d["tips"]) + "\n</ul>"



def card(prefix, d, label, meta=""):
    return (f'<li class="card"><a href="/{prefix}/{d["slug"]}.html">{thumb(d)}<div class="txt">'
            f'<p class="tag">{e(label)}</p><h3>{e(d["title"])}</h3>{meta}</div></a></li>')


def recipe_meta(d):
    return f'<p class="info"><span>{dur(d["prep_min"] + d["cook_min"])}</span><span>{e(d["yield"])}</span></p>'


def build_recipe(d):
    rel = f'tarifler/{d["slug"]}.html'
    total = d["prep_min"] + d["cook_min"]
    cat = d.get("category") or "Tarif"
    bc_ld, bc_html = crumbs([("Ana sayfa", SITE + "/"), (d["title"], url_of(rel))])
    recipe = {
        "@context": "https://schema.org", "@type": "Recipe", "name": d["title"],
        "description": d["description"], "author": ORG,
        "datePublished": d["published"], "dateModified": d["modified"],
        "prepTime": iso(d["prep_min"]), "cookTime": iso(d["cook_min"]), "totalTime": iso(total),
        "recipeYield": yld(d["yield"]), "recipeCategory": d["category"], "recipeCuisine": "Türk", "recipeIngredient": d["ingredients"],
        "recipeInstructions": [{"@type": "HowToStep", "text": s} for s in d["steps"]],
    }
    if d.get("image"):
        recipe["image"] = f'{SITE}/assets/img/{d["image"]}'
    ing_items = "".join(f"<li>{format_ingredient_html(i, d['slug'])}</li>" for i in d["ingredients"])
    body = f"""<div class="wrap">{bc_html}</div>
<article>
{figure(d)}
<div class="wrap">
<div class="lead">
<p class="tag">{e(cat)}</p>
<h1>{e(d["title"])}</h1>
<p class="answer">{e(d["answer"])}</p></div>
<ul class="meta"><li><small>Hazırlık</small>{dur(d["prep_min"])}</li><li><small>Pişirme</small>{dur(d["cook_min"])}</li><li><small>Toplam</small>{dur(total)}</li><li><small>Porsiyon</small>{e(d["yield"])}</li><li><small>Kategori</small>{e(cat)}</li></ul>
<div class="rgrid">
<section class="ing"><h2>Malzemeler</h2>
<ul id="malzemeler">
{ing_items}
</ul></section>
<div class="how"><h2>Yapılışı</h2>
<ol id="adimlar">
{"".join(f"<li>{e(s)}</li>" for s in d["steps"])}
</ol>
{tips_html(d)}</div>
</div>
</div>
</article>
{cta(d, "tarif")}
{sticky_bar(d, "tarif")}"""
    write(rel, page(rel, f'{d["title"]} | Çimenağa Tarifler', d["description"], body, [recipe, bc_ld], d.get("image")))
    return rel


def build_article(d, recipes, articles):
    rel = f'makaleler/{d["slug"]}.html'
    bc_ld, bc_html = crumbs([("Ana sayfa", SITE + "/"), (d["title"], url_of(rel))])
    art = {
        "@context": "https://schema.org", "@type": "Article", "headline": d["title"],
        "description": d["description"], "author": ORG, "publisher": ORG,
        "datePublished": d["published"], "dateModified": d["modified"],
        "mainEntityOfPage": url_of(rel),
    }
    if d.get("image"):
        art["image"] = f'{SITE}/assets/img/{d["image"]}'
    if d.get("sources"):
        art["citation"] = [x["url"] for x in d["sources"]]
    faq_items = [
        {"@type": "Question", "name": s["h2"], "acceptedAnswer": {"@type": "Answer", "text": " ".join(plain(p) for p in s["paras"])}}
        for s in d.get("sections", []) if s.get("h2", "").strip().endswith("?")
    ]
    ld = [art, bc_ld]
    if faq_items:
        ld.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items
        })
    secs = "".join(f'<h2>{e(s["h2"])}</h2>' + "".join(f"<p>{rich(p)}</p>" for p in s["paras"])
                   + (table_html(s["table"]) if s.get("table") else "") for s in d["sections"])
    if d.get("sources"):
        secs += '<h2>Kaynaklar</h2><ul class="sources">' + "".join(
            f'<li><a href="{e(x["url"], quote=True)}" rel="noopener">{e(x["name"])}</a></li>' for x in d["sources"]) + "</ul>"
    rel_html = ""
    if d["related"]:
        items = "".join(card("tarifler", recipes[s], recipes[s].get("category") or "Tarif", recipe_meta(recipes[s])) for s in d["related"])
        rel_html = f'<section class="related"><div class="wrap"><h2>İlgili Tarifler</h2><ul class="cards">{items}</ul></div></section>'
    if d.get("related_articles"):
        items = "".join(card("makaleler", articles[s], "Makale", f'<p class="desc">{e(articles[s]["description"])}</p>') for s in d["related_articles"])
        rel_html = f'<section class="related"><div class="wrap"><h2>İlgili Makaleler</h2><ul class="cards">{items}</ul></div></section>' + rel_html
    body = f"""<div class="wrap">{bc_html}</div>
<article>
{figure(d)}
<div class="wrap narrow">
<p class="tag">Makale</p>
<h1>{e(d["title"])}</h1>
<p class="answer">{e(d["answer"])}</p>
{secs}
</div>
</article>
{rel_html}
{cta(d, "makale")}
{sticky_bar(d, "makale")}"""
    title = d.get("seo_title", d["title"])
    if len(title) + len(" | Çimenağa Tarifler") <= 60:
        title += " | Çimenağa Tarifler"
    write(rel, page(rel, title, d["description"], body, ld, d.get("image")))
    return rel


def build_return_policy():
    rel = "iade-ve-iptal-politikasi.html"
    bc_ld, bc_html = crumbs([("Ana sayfa", SITE + "/"), ("İptal ve İade Koşulları", url_of(rel))])
    ld = [
        bc_ld,
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": "İptal ve İade Koşulları | Çimenağa",
            "description": "Çimenağa Pastırma iptal, iade ve kargo hasar telafi politikası. Gıda güvenliği, cayma hakkı istisnası ve kargo telafi süreçleri.",
            "url": url_of(rel),
            "publisher": ORG,
        },
    ]
    body = f"""<div class="wrap">{bc_html}</div>
<article>
<div class="wrap narrow">
<p class="tag">Politika</p>
<h1>İptal ve İade Koşulları</h1>
<p class="answer">Çimenağa Pastırma olarak 1927'den beri en büyük önceliğimiz, Kastamonu'nun geleneksel coğrafi işaretli lezzetlerini sofranıza en taze, hijyenik ve güvenli şekilde ulaştırmaktır. Çimenağa tarif ve içerik portalı üzerinden verilen yönlendirmeler ve resmî satış sitemiz <a href="{SHOP}/?ref=iade_politikasi">cimenaga.com</a> üzerinden oluşturulan siparişlerin iptal, iade ve kargo telafi süreçleri aşağıda şeffaf biçimde açıklanmıştır.</p>

<h2>1. Genel İade Politikası (Gıda Güvenliği ve Cayma Hakkı)</h2>
<p>Sitemizde tanıtılan ve <a href="{SHOP}/?ref=iade_politikasi">cimenaga.com</a> üzerinden satışı gerçekleştirilen Kastamonu pastırması, Kastamonu sucuğu ve dondurulmuş Kastamonu pastırmalı ince pide ürünleri; <b>çabuk bozulabilen, son tüketim tarihi bulunan, ısı ve soğuk zincir hassasiyeti taşıyan taze gıda maddeleridir.</b></p>
<p>6502 sayılı Tüketicinin Korunması Hakkında Kanun ve Mesafeli Sözleşmeler Yönetmeliği'nin 15. maddesinin 1. fıkrasının (c) bendi (<i>"Çabuk bozulabilen veya son kullanma tarihi geçebilecek malların teslimine ilişkin sözleşmeler"</i>) ile (ç) bendi (<i>"Tesliminden sonra ambalaj, bant, mühür, paket gibi koruyucu unsurları açılmış olan mallardan; iadesi sağlık ve hijyen açısından uygun olmayanların teslimine ilişkin sözleşmeler"</i>) gereğince, <b>taze gıda ürünlerinde keyfi cayma ve iade hakkı bulunmamaktadır. Gıda güvenliği ve halk sağlığı standartları gereği iade kabul edilmemektedir.</b></p>

<h2>2. Kargo Hasarı ve Ayıplı Ürün Telafisi (%100 Çimenağa Güvencesi)</h2>
<p>Ürünlerimiz vakumlu ambalajlarda, strafor ısı yalıtımlı özel kutularda ve soğuk zincir buz aküleri eşliğinde özenle sevk edilir. Ancak kargo taşınması sırasında meydana gelebilecek tüm hasarlar ve aksaklıklar <b>%100 Çimenağa garantisi altındadır; müşterilerimiz kesinlikle mağdur edilmez:</b></p>
<ul>
<li><b>Kapsamdaki Durumlar:</b> Kargo paketinin ezilmesi, yırtılması veya ıslanması; vakumlu ambalajın taşıma sırasında hava alması veya açılması; kargo gecikmesi sebebiyle ürünün tazeliğini yitirmesi; eksik veya yanlış ürün teslimatı.</li>
<li><b>Hasar Bildirimi:</b> Teslimat tarihinden itibaren <b>24 saat içinde</b>, hasarlı ürün ve ambalajın fotoğraflarını WhatsApp hattımıza (<a href="https://wa.me/905416967790">+90 541 696 77 90</a>) veya e-posta adresimize (<a href="mailto:cimenagapastirma@gmail.com">cimenagapastirma@gmail.com</a>) iletmeniz yeterlidir. Kargo teslimi sırasında tutanak tutturulması süreci hızlandırmakla birlikte zorunlu tutulmaz; fotoğraflı bildiriminiz derhal incelemeye alınır.</li>
<li><b>Telafi Seçenekleri (Müşteri Tercihine Bağlı):</b>
<ol>
<li><b>Koşulsuz Ücretsiz Yeniden Gönderim:</b> Hiçbir ek kargo veya ürün bedeli talep edilmeksizin aynı ürün derhal taze olarak hazırlanıp kargoya verilir.</li>
<li><b>Tam Para İadesi:</b> Ödenen toplam tutar (kargo bedeli dahil), hiçbir kesinti yapılmaksızın 1-3 iş günü içinde müşterinin ödeme yaptığı yöntemle (kredi kartı / banka hesabı) eksiksiz iade edilir.</li>
</ol>
</li>
</ul>

<h2>3. Sipariş İptali</h2>
<p>Verdiğiniz siparişi, <b>ürün henüz kargoya teslim edilmeden önce</b> WhatsApp hattımız üzerinden bildirerek hiçbir gerekçe göstermeksizin ve herhangi bir kesinti olmadan anında iptal edebilirsiniz. İptal edilen siparişlerin ücreti 1-3 iş günü içinde eksiksiz iade edilir. Kargoya verilmiş siparişlerde ise taze gıda transferi durdurulamayacağı için kargo aşamasında iptal yapılamaz.</p>

<h2>4. İade ve Değişim Kargo Masrafları</h2>
<p>Kargo hasarı, ayıplı ürün veya tarafımızdan kaynaklanan yanlış gönderimlerde yapılacak telafi veya değişim işlemlerinde <b>tüm kargo ücretleri Çimenağa tarafından karşılanır; müşterimize kesinlikle kargo maliyeti yansıtılmaz.</b></p>

<h2>5. Para İadesi Süresi</h2>
<p>Onaylanan iadeler, bankanızın işlem prosedürlerine bağlı olarak 1 ila 3 iş günü içerisinde hesabınıza veya kredi kartınıza yansıtılır.</p>

<h2>6. İletişim ve Destek Bilgileri</h2>
<p>Sipariş iptali, kargo hasar bildirimi ve her türlü sorunuz için bizimle doğrudan iletişime geçebilirsiniz:</p>
<p><b>Telefon &amp; WhatsApp:</b> <a href="tel:+905416967790">+90 541 696 77 90</a><br>
<b>E-posta:</b> <a href="mailto:cimenagapastirma@gmail.com">cimenagapastirma@gmail.com</a><br>
<b>Adres:</b> Hepkebirler Mh. Omuzlu Sk. No:1, Merkez, Kastamonu<br>
<b>Çalışma Saatleri:</b> Her gün 08:00 - 20:00<br>
<b>Resmî Mağaza Sayfası:</b> <a href="{SHOP}/iade-ve-iptal-politikasi.html">cimenaga.com İptal ve İade Koşulları</a></p>
</div>
</article>"""
    write(rel, page(rel, "İptal ve İade Koşulları | Çimenağa",
                    "Çimenağa Pastırma iptal, iade ve kargo hasar telafi politikası. Gıda güvenliği, cayma hakkı istisnası ve kargo telafi süreçleri.",
                    body, ld))
    return rel


def build_index(recipes, articles):
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "Çimenağa Tarifler",
           "url": SITE + "/", "inLanguage": "tr", "publisher": ORG}]
    rc = "".join(card("tarifler", d, d.get("category") or "Tarif", recipe_meta(d)) for d in recipes.values())
    ac = "".join(card("makaleler", d, "Makale", f'<p class="desc">{e(d["description"])}</p>') for d in articles.values())
    prods = "".join(
        f'<li class="card prod"><a href="{SHOP}/urun/{s}.html?ref=tarif_anasayfa_kart"><div class="pic"><img src="/assets/img/{PRODIMG[s][0]}" alt="{e(PRODIMG[s][1])}" '
        f'width="{(img_size("assets/img/" + PRODIMG[s][0]) or (900, 900))[0]}" height="{(img_size("assets/img/" + PRODIMG[s][0]) or (900, 900))[1]}" loading="lazy"></div>'
        f'<div class="txt"><h3>{e(PRODUCTS[s][0])}</h3><span class="more">Mağazaya git</span></div></a></li>'
        for s in PRODUCTS)
    body = f"""<section class="hero"><div class="wrap">
<p class="eyebrow">1927'den beri · Kastamonu</p>
<h1>Kastamonu Pastırması, Sucuğu ve Geleneksel Lezzet Tarifleri</h1>
<p class="answer">Kastamonu pastırması, fermente sucuğu, ata tohumu siyez bulguru ve Kastamonu çekme helvası gibi yöresel tatlarla hazırlanan tarifler ve gastronomi makaleleri. Çimenağa'nın hikâyesi 1927'den beri uzanır; ürünler <a href="{SHOP}/?ref=tarif_anasayfa_hero">cimenaga.com</a> adresindedir.</p>
<p class="actions"><a class="btn" href="#tarifler">Tarifleri Gör</a><a class="btn ghost" href="{SHOP}/?ref=tarif_anasayfa_hero">Mağazaya Git</a></p>
</div></section>
<section class="block dark shop"><div class="wrap">
<p class="eyebrow">Çimenağa</p>
<h2 class="head">Ürünlerimizi cimenaga.com'dan Satın Alabilirsiniz</h2>
<ul class="cards">{prods}</ul>
<p class="actions"><a class="btn" href="{SHOP}/urunlerimiz.html?ref=tarif_anasayfa_tumu">Tüm ürünleri gör <span aria-hidden="true">→</span></a></p>
</div></section>
<section class="block"><div class="wrap">
<p class="eyebrow">Mutfaktan</p>
<h2 id="tarifler" class="head">Tarifler</h2>
<ul class="cards">{rc}</ul>
</div></section>
<section class="block band"><div class="wrap">
<p class="eyebrow">Okumalık</p>
<h2 id="makaleler" class="head">Makaleler</h2>
<ul class="cards">{ac}</ul>
</div></section>"""
    write("index.html", page("index.html", "Kastamonu Pastırması, Sucuğu ve Yöresel Tarifler | Çimenağa Tarifler",
                             "Kastamonu pastırması, sucuğu, siyez bulguru ve yöresel lezzetlerle hazırlanan geleneksel tarifler ve gastronomi makaleleri.",
                             body, ld))


REDIRECTS = {
    "kastamonu-cemenli-pastirma": f"{SITE}/makaleler/kastamonu-pastirmasi-nedir.html",
    "Kastamonu-Pastirmali-Ekmek": f"{SITE}/tarifler/pastirmali-pide.html",
    "kastamonu-pastirmali-ekmek": f"{SITE}/tarifler/pastirmali-pide.html",
    "pastirma": f"{SITE}/#tarifler",
    "sucuk": f"{SITE}/tarifler/sucuklu-yumurta.html",
    "Sucuk": f"{SITE}/tarifler/sucuklu-yumurta.html",
    "Kastamonu-Sucugu": f"{SITE}/tarifler/sucuklu-yumurta.html",
    "kastamonu-sucugu": f"{SITE}/tarifler/sucuklu-yumurta.html",
    "Sucuk/Kastamonu-Sucugu": f"{SITE}/tarifler/sucuklu-yumurta.html",
    "taskopru-sarimsagi": f"{SITE}/makaleler/cemen-ve-taskopru-sarimsagi.html",
    "siyez-urunleri": f"{SITE}/tarifler/siyez-bulgur-pilavi.html",
    "helva-ve-tatlilar": f"{SITE}/tarifler/kastamonu-cekme-helvasi.html",
    "helva-ve-tatlilar/v175grantep-fistikli": f"{SITE}/tarifler/kastamonu-cekme-helvasi.html",
    "visne-receli": f"{SITE}/tarifler/visne-receli.html",
    "recel-bal": f"{SITE}/tarifler/visne-receli.html",
    "recel-bal/kureliden-bal-500gr": f"{SITE}/tarifler/visne-receli.html",
    "kureliden-bal-500gr": f"{SITE}/tarifler/visne-receli.html",
    "kureliden-bal-850gr": f"{SITE}/tarifler/visne-receli.html",
    "kahve": f"{SITE}/tarifler/dibek-kahvesi.html",
    "dovme-tasdibek-7karisimli-osmanli-kahve": f"{SITE}/tarifler/dibek-kahvesi.html",
    "dovme-tasdibek-7karisimli-osmanli-kahve2": f"{SITE}/tarifler/dibek-kahvesi.html",
    "dovme-tasdibek-damla-sakizli-kahve": f"{SITE}/tarifler/dibek-kahvesi.html",
    "hakkimizda": f"{SHOP}/hakkimizda.html",
}


def build_redirects():
    for src, dst in REDIRECTS.items():
        rel = f"{src}/index.html"
        html = f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>Yönlendiriliyorsunuz... | Çimenağa</title>
<meta http-equiv="refresh" content="0; url={dst}">
<link rel="canonical" href="{dst}">
<script>window.location.replace("{dst}");</script>
</head>
<body>
<p>Yönlendiriliyorsunuz... Lütfen bekleyin. <a href="{dst}">Otomatik yönlendirilmezseniz buraya tıklayın</a>.</p>
</body>
</html>
"""
        write(rel, html)


def build_404(recipes, articles):
    rel = "404.html"
    featured = ["pastirmali-pide", "sucuklu-yumurta", "siyez-bulgur-pilavi", "kastamonu-cekme-helvasi", "visne-receli", "dibek-kahvesi"]
    cards_html = "".join(
        card("tarifler", recipes[s], recipes[s].get("category") or "Tarif", recipe_meta(recipes[s]))
        for s in featured if s in recipes
    )

    redirect_map_json = json.dumps({
        "/kastamonu-cemenli-pastirma": f"{SITE}/makaleler/kastamonu-pastirmasi-nedir.html",
        "/kastamonu-pastirmali-ekmek": f"{SITE}/tarifler/pastirmali-pide.html",
        "/pastirma": f"{SITE}/#tarifler",
        "/sucuk": f"{SITE}/tarifler/sucuklu-yumurta.html",
        "/kastamonu-sucugu": f"{SITE}/tarifler/sucuklu-yumurta.html",
        "/sucuk/kastamonu-sucugu": f"{SITE}/tarifler/sucuklu-yumurta.html",
        "/taskopru-sarimsagi": f"{SITE}/makaleler/cemen-ve-taskopru-sarimsagi.html",
        "/siyez-urunleri": f"{SITE}/tarifler/siyez-bulgur-pilavi.html",
        "/helva-ve-tatlilar": f"{SITE}/tarifler/kastamonu-cekme-helvasi.html",
        "/helva-ve-tatlilar/v175grantep-fistikli": f"{SITE}/tarifler/kastamonu-cekme-helvasi.html",
        "/visne-receli": f"{SITE}/tarifler/visne-receli.html",
        "/recel-bal": f"{SITE}/tarifler/visne-receli.html",
        "/recel-bal/kureliden-bal-500gr": f"{SITE}/tarifler/visne-receli.html",
        "/kureliden-bal-500gr": f"{SITE}/tarifler/visne-receli.html",
        "/kureliden-bal-850gr": f"{SITE}/tarifler/visne-receli.html",
        "/kahve": f"{SITE}/tarifler/dibek-kahvesi.html",
        "/dovme-tasdibek-7karisimli-osmanli-kahve": f"{SITE}/tarifler/dibek-kahvesi.html",
        "/dovme-tasdibek-7karisimli-osmanli-kahve2": f"{SITE}/tarifler/dibek-kahvesi.html",
        "/dovme-tasdibek-damla-sakizli-kahve": f"{SITE}/tarifler/dibek-kahvesi.html",
        "/hakkimizda": f"{SHOP}/hakkimizda.html",
    }, ensure_ascii=False)

    html = f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sayfa Bulunamadı veya Taşındı | Çimenağa Tarifler</title>
<meta name="robots" content="noindex, follow">
<meta name="theme-color" content="#14284b">
<link rel="icon" href="/assets/img/icon.png?v=1">
<link rel="apple-touch-icon" href="/assets/img/icon.png?v=1">
<link rel="stylesheet" href="/assets/style.css">
<script>
(function() {{
  var path = window.location.pathname.replace(/\\/+$/, "");
  var search = window.location.search;
  var full = (path + search).toLowerCase();
  var map = {redirect_map_json};
  var target = map[path.toLowerCase()];

  if (!target) {{
    if (full.indexOf("pastirmali-ekmek") !== -1 || full.indexOf("pastirmali-pide") !== -1 || full.indexOf("product_id=40") !== -1) {{
      target = "/tarifler/pastirmali-pide.html";
    }} else if (full.indexOf("cemenli-pastirma") !== -1 || full.indexOf("product_id=37") !== -1) {{
      target = "/makaleler/kastamonu-pastirmasi-nedir.html";
    }} else if (full.indexOf("pastirma") !== -1) {{
      target = "/#tarifler";
    }} else if (full.indexOf("sucuk") !== -1 || full.indexOf("product_id=34") !== -1) {{
      target = "/tarifler/sucuklu-yumurta.html";
    }} else if (full.indexOf("sarimsak") !== -1 || full.indexOf("cemen") !== -1) {{
      target = "/makaleler/cemen-ve-taskopru-sarimsagi.html";
    }} else if (full.indexOf("siyez") !== -1) {{
      target = "/tarifler/siyez-bulgur-pilavi.html";
    }} else if (full.indexOf("helva") !== -1 || /product_id=5[7-9]|product_id=6[0-2]/.test(full) || full.indexOf("fistikli") !== -1) {{
      target = "/tarifler/kastamonu-cekme-helvasi.html";
    }} else if (full.indexOf("visne") !== -1 || full.indexOf("recel") !== -1 || full.indexOf("bal") !== -1) {{
      target = "/tarifler/visne-receli.html";
    }} else if (full.indexOf("kahve") !== -1 || full.indexOf("dibek") !== -1 || /product_id=(9|10|11|12)/.test(full)) {{
      target = "/tarifler/dibek-kahvesi.html";
    }} else if (full.indexOf("checkout") !== -1 || full.indexOf("account") !== -1 || full.indexOf("cart") !== -1) {{
      target = "{SHOP}/?ref=legacy_404";
    }} else if (full.indexOf("hakkimizda") !== -1 || full.indexOf("contact") !== -1) {{
      target = "{SHOP}/hakkimizda.html";
    }}
  }}

  if (target) {{
    window.location.replace(target);
  }}
}})();
</script>
</head>
<body>
<header><div class="wrap">
<a class="logo" href="{SHOP}/?ref=404_header"><img src="/assets/img/logo.png" alt="Çimenağa Pastırma" width="105" height="72"></a>
<nav aria-label="Ana menü"><a href="/#tarifler">Tarifler</a><a href="/#makaleler">Makaleler</a><a href="{SHOP}/urunlerimiz.html?ref=404_header">Ürünlerimiz</a><a class="shop" href="{SHOP}/?ref=404_header">Mağaza</a></nav>
</div></header>
<main>
<section class="hero"><div class="wrap">
<p class="eyebrow">404 · Sayfa Bulunamadı</p>
<h1>Sayfa Taşınmış veya Değişmiş Olabilir</h1>
<p class="answer">Aradığınız içerik Çimenağa'nın yenilenen geleneksel tarif ve gastronomi portalına taşınmış olabilir. Aşağıdaki popüler tariflerimize göz atabilir veya ana sayfaya dönebilirsiniz.</p>
<p class="actions"><a class="btn" href="/#tarifler">Tarifleri Gör</a><a class="btn ghost" href="{SHOP}/?ref=404_hero">Mağazaya Git</a></p>
</div></section>
<section class="block"><div class="wrap">
<p class="eyebrow">Mutfaktan</p>
<h2 class="head">Öne Çıkan Tarifler</h2>
<ul class="cards">{cards_html}</ul>
</div></section>
</main>
<footer><div class="wrap">
<div><p><b>Çimenağa Pastırma &amp; Sucuk</b></p>
<p>1927'den beri Kastamonu</p></div>
<p class="fnav"><a href="/#tarifler">Tarifler</a> <a href="/#makaleler">Makaleler</a> <a href="/iade-ve-iptal-politikasi.html">İptal ve İade Koşulları</a> <a href="{SHOP}/?ref=404_footer">cimenaga.com</a> <a href="https://www.instagram.com/cimenagapastirma/" rel="me noopener">Instagram</a></p>
</div></footer>
</body>
</html>
"""
    write(rel, html)


def load(sub):
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((CONTENT / sub).glob("*.json"))}


def main():
    recipes, articles = load("tarifler"), load("makaleler")
    rels = ["index.html"]
    mods = {}
    imgs = {"index.html": "hero.webp"}
    build_index(recipes, articles)
    r_pol = build_return_policy()
    rels.append(r_pol)
    mods[r_pol] = "2026-10-15"
    for d in recipes.values():
        r = build_recipe(d); rels.append(r); mods[r] = d["modified"]
        if d.get("image"):
            imgs[r] = d["image"]
    for d in articles.values():
        r = build_article(d, recipes, articles); rels.append(r); mods[r] = d["modified"]
        if d.get("image"):
            imgs[r] = d["image"]
    mods["index.html"] = max(mods.values())
    def sm_img(r):
        if r not in imgs:
            return ""
        return f"<image:image><image:loc>{SITE}/assets/img/{e(imgs[r])}</image:loc></image:image>"
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
          + "".join(f"<url><loc>{url_of(r)}</loc><lastmod>{mods[r]}</lastmod>{sm_img(r)}</url>\n" for r in rels) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /docs/\nSitemap: {SITE}/sitemap.xml\n")
    build_redirects()
    build_404(recipes, articles)

    # llms.txt
    lines = [
        "# Çimenağa Tarifler",
        "",
        "> Kastamonu pastırması ve sucuğuyla tarifler ve makaleler.",
        "> Kapsamlı tam metin ve bilgi kütüphanesi: " + SITE + "/llms-full.txt",
        "> Resmî Mağaza: " + SHOP + "/?ref=llms",
        "> İptal ve İade Koşulları: " + SITE + "/iade-ve-iptal-politikasi.html",
        "",
        "## Tarifler",
    ]
    lines += [f'- [{d["title"]}]({SITE}/tarifler/{d["slug"]}.html): {d["description"]}' for d in recipes.values()]
    lines += ["", "## Makaleler"]
    lines += [f'- [{d["title"]}]({SITE}/makaleler/{d["slug"]}.html): {d["description"]}' for d in articles.values()]
    write("llms.txt", "\n".join(lines) + "\n")

    # llms-full.txt
    full_lines = [
        "# Çimenağa Pastırma & Sucuk — Tam Bilgi ve Tarif Kütüphanesi",
        "",
        "> 1927'den beri Kastamonu Devrekani merkezli geleneksel pastırma, sucuk ve pastırmalı ince pide üretimi.",
        "> Resmî Mağaza: " + SHOP + "/?ref=llms_full",
        "> Tarif ve Bilgi Portalı: " + SITE + "/",
        "",
        "## Kurumsal Bilgiler ve Coğrafi İşaret Tescilleri",
        "- **Kuruluş:** 1927 (Kastamonu, Devrekani).",
        "- **Kastamonu Pastırması:** Türk Patent ve Marka Kurumu Mahreç İşareti Tescil No: 711 (Tescil: 29.03.2021). Sınır: Kastamonu ili.",
        "- **Taşköprü Sarımsağı:** Menşe Adı Tescil No: 135 (Tescil: 03.12.2009).",
        "- **Tosya Pirinci:** Menşe Adı Tescil No: 230 (Tescil: 08.11.2017).",
        "",
        "## İptal, İade ve Kargo Hasar Telafi Politikası",
        "- **Gıda Güvenliği ve Cayma Hakkı:** 6502 sayılı Tüketicinin Korunması Hakkında Kanun ve Mesafeli Sözleşmeler Yönetmeliği m.15/1-c gereğince taze pastırma, sucuk ve donuk pide gibi çabuk bozulabilen gıda ürünlerinde keyfi cayma ve iade hakkı bulunmamaktadır.",
        "- **Kargo Hasarı ve Telafi Güvencesi (%100 Çimenağa Güvencesi):** Taşıma sırasında ambalajın hava alması, bozulması veya gecikme durumunda teslimattan itibaren 24 saat içinde fotoğraflı bildirim ile derhal ücretsiz yeniden gönderim veya tam para iadesi yapılır.",
        "- **Kargo Masrafları:** Hasar telafi süreçlerinde tüm kargo masrafları Çimenağa tarafından karşılanır; müşteriye ek masraf yansıtılmaz.",
        f"- **Politika Sayfaları:** {SITE}/iade-ve-iptal-politikasi.html ve {SHOP}/iade-ve-iptal-politikasi.html",
        "",
        "## Kastamonu Pastırmasının Ayırt Edici Nitelikleri",
        "1. **Sayvanda Kurutma:** Ilgaz Dağı esintisini alan üstü kapalı çatılarda (sayvan) güneşte kurutulur. TürkPatent tescil belgesinde kurutma süresi 30 gün olarak tanımlanır; Çimenağa kendi uygulamasında daha lezzetli olması için pastırmayı daha uzun, yaklaşık 60 gün olgunlaştırır.",
        "2. **Taşköprü Sarımsaklı Çimen (Çemen):** Tescil belgesine göre çimen (çemen) bileşimi: %60 su, %30 çemen unu (buyotu), %8 Taşköprü sarımsağı, %1 kırmızı toz biber, %0,5 kimyon, %0,5 tuz.",
        "3. **Geleneksel İnce Dilimleme:** Keskin pastırma bıçağı ve satırla elde ortalama 0,75 mm tül inceliğinde dilimlenir.",
        "",
        "## Ürünler",
        f"- [Kastamonu Pastırması]({SHOP}/urun/kastamonu-pastirmasi.html?ref=llms_full): Coğrafi işaretli, el dilimi, Taşköprü sarımsaklı çimenle kaplı, 500 g ve katları (1 kg: 2.800 ₺).",
        f"- [Kastamonu Sucuğu]({SHOP}/urun/kastamonu-sucugu.html?ref=llms_full): Geleneksel fermente dana sucuğu, 500 g ve katları (1 kg: 2.000 ₺).",
        f"- [Kastamonu Pastırmalı İnce Pide]({SHOP}/urun/kastamonu-pastirmali-ince-pide.html?ref=llms_full): Birlikte çalışılan odun fırınında pişirilip dondurulmuş gönderilen yöresel pastırmalı ekmek (adet 350 ₺).",
        "",
        "## Tarifler (Tam Metin)",
    ]
    for d in recipes.values():
        total_time = d["prep_min"] + d["cook_min"]
        full_lines += [
            f"### {d['title']}",
            f"- **URL:** {SITE}/tarifler/{d['slug']}.html",
            f"- **Kategori:** {d.get('category', 'Tarif')}",
            f"- **Süre:** Hazırlık {d['prep_min']} dk, Pişirme {d['cook_min']} dk, Toplam {total_time} dk",
            f"- **Porsiyon:** {d['yield']}",
            f"- **Özet:** {d['answer']}",
            "- **Malzemeler:**",
        ]
        full_lines += [f"  - {ing}" for ing in d["ingredients"]]
        full_lines += ["- **Yapılışı:**"]
        full_lines += [f"  {idx+1}. {step}" for idx, step in enumerate(d["steps"])]
        if d.get("tips"):
            full_lines += ["- **İpuçları:**"]
            full_lines += [f"  - {tip}" for tip in d["tips"]]
        full_lines.append("")

    full_lines += ["## Makaleler (Tam Metin ve Soru-Cevaplar)"]
    for d in articles.values():
        full_lines += [
            f"### {d['title']}",
            f"- **URL:** {SITE}/makaleler/{d['slug']}.html",
            f"- **Özet:** {d['answer']}",
        ]
        for sec in d.get("sections", []):
            full_lines.append(f"#### {sec['h2']}")
            full_lines += [plain(p) for p in sec["paras"]]
            if sec.get("table"):
                full_lines += table_md(sec["table"])
        if d.get("sources"):
            full_lines += ["#### Kaynaklar"] + [f"- [{x['name']}]({x['url']})" for x in d["sources"]]
        full_lines.append("")

    write("llms-full.txt", "\n".join(full_lines) + "\n")
    print(f"{len(recipes)} tarif, {len(articles)} makale üretildi")


if __name__ == "__main__":
    main()
