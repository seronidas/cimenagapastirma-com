#!/usr/bin/env python3
"""İçerikten statik siteyi üretir. Kullanım: python3 docs/build.py"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "docs" / "content"
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
        "⛰️ <b>Ilgaz Esintisi</b> 30 Gün Doğal Kurutma",
        "🧄 <b>Taşköprü Sarımsaklı</b> Çemen",
        "❄️ <b>Soğuk Zincir</b> Vakumlu Taze Kargo",
    ],
    "kastamonu-sucugu": [
        "🥩 <b>%100 Dana Eti</b> Fermente Sucuk",
        "🪵 <b>Geleneksel</b> Taşköprü Sarımsaklı Formül",
        "❄️ <b>Soğuk Zincir</b> Vakumlu Taze Kargo",
    ],
    "kastamonu-pastirmali-ince-pide": [
        "🥖 <b>Taş Fırın</b> İnce Pide (Pastırmalı Ekmek)",
        "❄️ <b>Dondurulmuş</b> Fırına Hazır",
        "🥩 <b>Bol Pastırma</b> ve Harç Dolgusu",
    ],
}
ORG = {"@type": "Organization", "name": "Çimenağa Pastırma & Sucuk", "url": SHOP}
e = html.escape


def iso(minutes):
    h, m = divmod(minutes, 60)
    return "PT" + (f"{h}H" if h else "") + (f"{m}M" if m or not h else "")


def dur(minutes):
    h, m = divmod(minutes, 60)
    parts = ([f"{h} sa"] if h else []) + ([f"{m} dk"] if m or not h else [])
    return " ".join(parts)


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
    otype = "article" if rel.startswith("makaleler/") else "website"
    og = f'\n<meta property="og:image" content="{SITE}/assets/img/{e(image)}">' if image else ""
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
<meta name="twitter:card" content="summary">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{e(title, quote=True)}">
<meta property="og:description" content="{e(desc, quote=True)}">
<meta property="og:url" content="{url_of(rel)}">{og}
<meta name="theme-color" content="#14284b">
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
<p class="fnav"><a href="/#tarifler">Tarifler</a> <a href="/#makaleler">Makaleler</a> <a href="{SHOP}/?ref=tarif_footer">cimenaga.com</a></p>
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
    return '<section class="cta"><div class="wrap">' + "".join(out) + "</div></section>"


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


def date_line(d):
    return f'<p class="date">Son güncelleme: <time datetime="{d["modified"]}">{d["modified"]}</time></p>'


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
{date_line(d)}
</div>
</article>
{cta(d, "tarif")}
{sticky_bar(d, "tarif")}"""
    write(rel, page(rel, f'{d["title"]} | Çimenağa Tarifler', d["description"], body, [recipe, bc_ld], d.get("image")))
    return rel


def build_article(d, recipes):
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
    faq_items = [
        {"@type": "Question", "name": s["h2"], "acceptedAnswer": {"@type": "Answer", "text": " ".join(s["paras"])}}
        for s in d.get("sections", []) if s.get("h2", "").strip().endswith("?")
    ]
    ld = [art, bc_ld]
    if faq_items:
        ld.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items
        })
    secs = "".join(f'<h2>{e(s["h2"])}</h2>' + "".join(f"<p>{e(p)}</p>" for p in s["paras"]) for s in d["sections"])
    rel_html = ""
    if d["related"]:
        items = "".join(card("tarifler", recipes[s], recipes[s].get("category") or "Tarif", recipe_meta(recipes[s])) for s in d["related"])
        rel_html = f'<section class="related"><div class="wrap"><h2>İlgili tarifler</h2><ul class="cards">{items}</ul></div></section>'
    body = f"""<div class="wrap">{bc_html}</div>
<article>
{figure(d)}
<div class="wrap narrow">
<p class="tag">Makale</p>
<h1>{e(d["title"])}</h1>
<p class="answer">{e(d["answer"])}</p>
{secs}
{date_line(d)}
</div>
</article>
{rel_html}
{cta(d, "makale")}
{sticky_bar(d, "makale")}"""
    write(rel, page(rel, f'{d["title"]} | Çimenağa Tarifler', d["description"], body, ld, d.get("image")))
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
<h1>Kastamonu Pastırması ve Sucuğu ile Tarifler</h1>
<p class="answer">Kastamonu pastırması ve sucuğuyla yapılan tarifler ve bu lezzetler hakkında makaleler. Çimenağa'nın hikâyesi 1927'den beri uzanır; ürünler <a href="{SHOP}/?ref=tarif_anasayfa_hero">cimenaga.com</a> adresindedir.</p>
<p class="actions"><a class="btn" href="#tarifler">Tarifleri Gör</a><a class="btn ghost" href="{SHOP}/?ref=tarif_anasayfa_hero">Mağazaya Git</a></p>
</div></section>
<section class="block dark shop"><div class="wrap">
<p class="eyebrow">Çimenağa</p>
<h2 class="head">Ürünlerimizi cimenaga.com'dan satın alabilirsiniz</h2>
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
    write("index.html", page("index.html", "Kastamonu Pastırması ve Sucuğu Tarifleri | Çimenağa Tarifler",
                             "Kastamonu pastırması ve sucuğuyla yapılan tarifler ve Kastamonu'nun lezzetleri hakkında makaleler.",
                             body, ld))


def load(sub):
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((CONTENT / sub).glob("*.json"))}


def main():
    recipes, articles = load("tarifler"), load("makaleler")
    rels = ["index.html"]
    mods = {}
    build_index(recipes, articles)
    for d in recipes.values():
        r = build_recipe(d); rels.append(r); mods[r] = d["modified"]
    for d in articles.values():
        r = build_article(d, recipes); rels.append(r); mods[r] = d["modified"]
    mods["index.html"] = max(mods.values())
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"<url><loc>{url_of(r)}</loc><lastmod>{mods[r]}</lastmod></url>\n" for r in rels) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /docs/\nSitemap: {SITE}/sitemap.xml\n")

    # llms.txt
    lines = [
        "# Çimenağa Tarifler",
        "",
        "> Kastamonu pastırması ve sucuğuyla tarifler ve makaleler.",
        "> Kapsamlı tam metin ve bilgi kütüphanesi: " + SITE + "/llms-full.txt",
        "> Resmî Mağaza: " + SHOP + "/?ref=llms",
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
        "## Kastamonu Pastırmasının Ayırt Edici Nitelikleri",
        "1. **Doğal Sayvan Kurutması:** Fırınlama veya suni sıcak hava kullanılmaz; Ilgaz Dağı esintisini alan üstü kapalı çatı katlarında (sayvan) güneşte ve rüzgarda 30 gün boyunca doğal kurutulur.",
        "2. **Taşköprü Sarımsaklı Çemen:** Tescil belgesine göre çemen bileşimi: %60 su, %30 çemen unu (buyotu), %8 Taşköprü sarımsağı, %1 kırmızı toz biber, %0,5 kimyon, %0,5 tuz.",
        "3. **Geleneksel İnce Dilimleme:** Keskin pastırma bıçağı ve satırla elde ortalama 0,75 mm tül inceliğinde dilimlenir.",
        "",
        "## Ürünler",
        f"- [Kastamonu Pastırması]({SHOP}/urun/kastamonu-pastirmasi.html?ref=llms_full): Coğrafi işaretli, el dilimi, Taşköprü sarımsaklı çemenle kaplı, 1 kg.",
        f"- [Kastamonu Sucuğu]({SHOP}/urun/kastamonu-sucugu.html?ref=llms_full): Geleneksel fermente dana sucuğu, 1 kg.",
        f"- [Kastamonu Pastırmalı İnce Pide]({SHOP}/urun/kastamonu-pastirmali-ince-pide.html?ref=llms_full): Taş fırında pişirilip dondurulmuş yöresel pastırmalı ekmek.",
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
            full_lines += [p for p in sec["paras"]]
        full_lines.append("")

    write("llms-full.txt", "\n".join(full_lines) + "\n")
    print(f"{len(recipes)} tarif, {len(articles)} makale üretildi")


if __name__ == "__main__":
    main()
