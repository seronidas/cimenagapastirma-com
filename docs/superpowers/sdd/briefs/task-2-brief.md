# Tarif ve Makale Sitesi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** cimenagapastirma.com için 8 tarif, 4 makale ve ana sayfadan oluşan statik, SEO ve AEO uyumlu bir site kurmak.

**Architecture:** İçerik `docs/content/**/*.json` dosyalarında tutulur. `docs/build.py` (yalnızca Python standart kütüphanesi) bu dosyalardan kök dizindeki statik HTML'i, JSON-LD'yi, sitemap.xml'i, robots.txt'i ve llms.txt'i üretir. Böylece schema ile görünür içerik aynı veriden çıkar ve birebir uyumlu kalır. `docs/check.py` yayın öncesi doğrulamayı yapar. Yayına giden dosyalarda JS yoktur.

**Tech Stack:** HTML, CSS, Python 3 (stdlib), WebSearch/WebFetch (araştırma ve görsel).

**Spec:** `docs/superpowers/specs/2026-10-11-tarif-sitesi-design.md`

## Global Constraints

- Klasör: `/ana/cimenaga/cimenagapastirma.com`. Dil: yalnızca Türkçe (`<html lang="tr">`).
- Statik, minimal HTML ve CSS. Efekt, animasyon, geçiş, hover efekti ve JS YOK.
- Hiçbir bilgi uydurulmaz. Doğrulanamayan sayısal bilgi (ör. saklama süresi) yazılmaz.
- `nutrition` (besin değeri) hiçbir yerde yazılmaz.
- Sucuğun üretimiyle ilgili iddia yazılmaz. Yalnızca yeme biçimleri anlatılır.
- Pastırma ve çemen bilgisi yalnızca cimenaga.com ve resmî kaynaklardan (TürkPatent vb.) alınır.
- Ürün bağlantıları yalnızca `https://cimenaga.com/urun/<slug>.html` biçiminde olur. Geçerli slug'lar: `kastamonu-pastirmasi`, `kastamonu-sucugu`, `kastamonu-pastirmali-ince-pide`.
- Görseller: Unsplash, Pexels ya da CC0 Wikimedia Commons. WebP, `width`, `height` ve dürüst `alt` ile. Görsel kaynakları sayfası YOK. Kaynaklar `docs/gorsel-kaynaklari.md` içinde tutulur.
- Bulunamayan görselde sayfa görselsiz kalır, `image` alanı schema'ya yazılmaz, kullanıcıya listelenir.
- Renk paleti ve serif başlıklar cimenaga.com ile aynı (`--ivory #faf6ee`, `--paper #fffdf8`, `--dark #1e1510`, `--ink #2b1f17`, `--muted #7a6a58`, `--line #e6dac3`, `--gold-d #8a6a2c`).
- Klasör git deposu değil. Plandaki "commit" adımlarının yerini `python3 docs/check.py` çalıştırmak alır.
- `docs/` yayına alınmaz. `robots.txt` içinde `Disallow: /docs/` bulunur.

## Review Focus

- Tarif adımı ya da malzemesi boş bırakıldığında ya da tek öğeli olduğunda sayfa ve schema bozulmamalı (`check.py` tarif başına en az 3 malzeme ve 2 adım ister).
- Başlıkta ve içerikte `&`, `<`, `"`, `'` gibi karakterler HTML ve JSON-LD içinde doğru kaçışlanmalı (`html.escape`, `json.dumps(ensure_ascii=False)`).
- Görseli olmayan tarif `image` alanı olmadan geçerli JSON-LD üretmeli ve kırık `<img>` bırakmamalı.
- Bir ürün slug'ı yanlış yazılırsa derleme hata vermeli (`PRODUCTS` sözlüğünde yoksa `KeyError`), sessizce kırık bağlantı üretmemeli.
- sitemap.xml'de olan ama dosyası olmayan ya da dosyası olup sitemap'te olmayan sayfa `check.py` tarafından yakalanmalı.


### Task 2: Üretici (`build.py`), CSS ve ana sayfa iskeleti

**Files:**
- Create: `docs/build.py`
- Create: `assets/style.css`
- Create: `assets/img/logo.png` (kopya: `/ana/cimenaga/cimenaga.com/assets/img/logo.png`)
- Create: `docs/content/tarifler/pastirmali-yumurta.json` (taslak; Task 4'te doğrulanıp son haline getirilir)

**Interfaces:**
- Consumes: `docs/check.py` (Task 1).
- Produces: `python3 docs/build.py` komutu. `docs/content/tarifler/<slug>.json` ve `docs/content/makaleler/<slug>.json` dosyalarını okur. `index.html`, `tarifler/<slug>.html`, `makaleler/<slug>.html`, `sitemap.xml`, `robots.txt`, `llms.txt` üretir.

Tarif JSON alanları (hepsi zorunlu, `image` hariç): `slug`, `title`, `description`, `answer`, `prep_min`, `cook_min`, `yield`, `ingredients` (liste), `steps` (liste), `tips` (liste), `products` (liste; slug'lar `PRODUCTS` içinde olmalı), `published`, `modified` (ISO tarih). İsteğe bağlı: `image` (dosya adı), `image_alt`, `image_w`, `image_h`.

Makale JSON alanları: `slug`, `title`, `description`, `answer`, `sections` (liste, her biri `{"h2": str, "paras": [str]}`), `related` (tarif slug listesi), `products`, `published`, `modified`, isteğe bağlı görsel alanları (tarifle aynı).

- [ ] **Step 1: Logoyu kopyala**

Run: `mkdir -p /ana/cimenaga/cimenagapastirma.com/assets/img && cp /ana/cimenaga/cimenaga.com/assets/img/logo.png /ana/cimenaga/cimenagapastirma.com/assets/img/logo.png`

- [ ] **Step 2: `assets/style.css` yaz**

```css
:root {
  --ivory: #faf6ee; --paper: #fffdf8; --dark: #1e1510; --ink: #2b1f17;
  --muted: #7a6a58; --line: #e6dac3; --gold-d: #8a6a2c; --sand: #cdbfa8;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
}
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; background: var(--ivory); color: var(--ink); font: 16px/1.7 system-ui, -apple-system, "Segoe UI", sans-serif; }
img { display: block; max-width: 100%; height: auto; }
a { color: var(--gold-d); }
:focus-visible { outline: 2px solid var(--gold-d); outline-offset: 3px; }
h1, h2, h3 { font-family: var(--serif); font-weight: 500; line-height: 1.2; margin: 0 0 .5em; }
h1 { font-size: clamp(2rem, 5vw, 2.8rem); }
h2 { font-size: 1.5rem; margin-top: 1.8em; }
.wrap { max-width: 760px; margin: 0 auto; padding: 0 20px; }
header { background: var(--paper); border-bottom: 1px solid var(--gold-d); }
header .wrap { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 24px; padding-top: 10px; padding-bottom: 10px; }
header img { width: 105px; height: 72px; }
header nav { display: flex; flex-wrap: wrap; gap: 0 20px; font-size: .85rem; font-weight: 600; }
header nav a { color: var(--ink); text-decoration: none; padding: 10px 0; }
main { padding: 32px 0 56px; }
.crumbs { font-size: .85rem; color: var(--muted); margin-bottom: 16px; }
.answer { font-size: 1.1rem; }
figure { margin: 24px 0; }
.meta { list-style: none; padding: 0; margin: 20px 0; display: flex; flex-wrap: wrap; gap: 8px 24px; border-block: 1px solid var(--line); padding-block: 12px; }
.cta { border: 1px solid var(--gold-d); background: var(--paper); padding: 16px 20px; margin: 32px 0; }
.cta a { font-weight: 600; }
.date { color: var(--muted); font-size: .85rem; }
.list { list-style: none; padding: 0; }
.list li { border-top: 1px solid var(--line); padding: 14px 0; }
.list a { font-family: var(--serif); font-size: 1.2rem; }
.list p { margin: 4px 0 0; color: var(--muted); }
footer { background: var(--dark); color: var(--sand); padding: 32px 0; font-size: .9rem; }
footer a { color: #fff; }
footer p { margin: 0 0 6px; }
```

- [ ] **Step 3: `docs/build.py` yaz**

```python
#!/usr/bin/env python3
"""İçerikten statik siteyi üretir. Kullanım: python3 docs/build.py"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "docs" / "content"
SITE = "https://cimenagapastirma.com"
SHOP = "https://cimenaga.com"
PRODUCTS = {
    "kastamonu-pastirmasi": ("Kastamonu Pastırması", "Pastırmasını bizden alın"),
    "kastamonu-sucugu": ("Kastamonu Sucuğu", "Sucuğunu bizden alın"),
    "kastamonu-pastirmali-ince-pide": ("Kastamonu Pastırmalı İnce Pide", "Pastırmalı ince pideyi bizden alın"),
}
ORG = {"@type": "Organization", "name": "Çimenağa Pastırma", "url": SHOP}
e = html.escape


def iso(minutes):
    h, m = divmod(minutes, 60)
    return "PT" + (f"{h}H" if h else "") + (f"{m}M" if m or not h else "")


def dur(minutes):
    h, m = divmod(minutes, 60)
    parts = ([f"{h} sa"] if h else []) + ([f"{m} dk"] if m or not h else [])
    return " ".join(parts)


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


def page(rel, title, desc, body, ld, image=None):
    og = f'\n<meta property="og:image" content="{SITE}/assets/img/{e(image)}">' if image else ""
    scripts = "\n".join(ld_tag(d) for d in ld)
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc, quote=True)}">
<link rel="canonical" href="{url_of(rel)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{e(title, quote=True)}">
<meta property="og:description" content="{e(desc, quote=True)}">
<meta property="og:url" content="{url_of(rel)}">{og}
<link rel="stylesheet" href="/assets/style.css">
{scripts}
</head>
<body>
<header><div class="wrap">
<a href="{SHOP}/"><img src="/assets/img/logo.png" alt="Çimenağa Pastırma" width="105" height="72"></a>
<nav><a href="/">Tarifler ve Makaleler</a><a href="{SHOP}/urunlerimiz.html">Ürünlerimiz</a></nav>
</div></header>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
<p><b>Çimenağa Pastırma</b> · 1927'den beri Kastamonu</p>
<p>Ürünlerimiz için <a href="{SHOP}/">cimenaga.com</a></p>
</div></footer>
</body>
</html>
"""


def figure(d):
    if not d.get("image"):
        return ""
    return (f'<figure><img src="/assets/img/{e(d["image"])}" alt="{e(d["image_alt"], quote=True)}" '
            f'width="{d["image_w"]}" height="{d["image_h"]}"></figure>')


def cta(d):
    out = []
    for s in d["products"]:
        name, label = PRODUCTS[s]  # bilinmeyen slug KeyError verir
        out.append(f'<a href="{SHOP}/urun/{s}.html">{e(label)}: {e(name)}</a>')
    return '<p class="cta">' + "<br>".join(out) + "</p>"


def date_line(d):
    return f'<p class="date">Son güncelleme: <time datetime="{d["modified"]}">{d["modified"]}</time></p>'


def build_recipe(d):
    rel = f'tarifler/{d["slug"]}.html'
    total = d["prep_min"] + d["cook_min"]
    bc_ld, bc_html = crumbs([("Ana sayfa", SITE + "/"), (d["title"], url_of(rel))])
    recipe = {
        "@context": "https://schema.org", "@type": "Recipe", "name": d["title"],
        "description": d["description"], "author": ORG,
        "datePublished": d["published"], "dateModified": d["modified"],
        "prepTime": iso(d["prep_min"]), "cookTime": iso(d["cook_min"]), "totalTime": iso(total),
        "recipeYield": d["yield"], "recipeIngredient": d["ingredients"],
        "recipeInstructions": [{"@type": "HowToStep", "text": s} for s in d["steps"]],
    }
    if d.get("image"):
        recipe["image"] = f'{SITE}/assets/img/{d["image"]}'
    body = f"""{bc_html}
<article>
<h1>{e(d["title"])}</h1>
<p class="answer">{e(d["answer"])}</p>
{figure(d)}
<ul class="meta"><li>Hazırlık: {dur(d["prep_min"])}</li><li>Pişirme: {dur(d["cook_min"])}</li><li>Toplam: {dur(total)}</li><li>{e(d["yield"])}</li></ul>
<h2>Malzemeler</h2>
<ul id="malzemeler">
{"".join(f"<li>{e(i)}</li>" for i in d["ingredients"])}
</ul>
<h2>Yapılışı</h2>
<ol id="adimlar">
{"".join(f"<li>{e(s)}</li>" for s in d["steps"])}
</ol>
<h2>İpuçları</h2>
<ul>
{"".join(f"<li>{e(t)}</li>" for t in d["tips"])}
</ul>
{cta(d)}
{date_line(d)}
</article>"""
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
    secs = "".join(f'<h2>{e(s["h2"])}</h2>' + "".join(f"<p>{e(p)}</p>" for p in s["paras"]) for s in d["sections"])
    rel_html = ""
    if d["related"]:
        items = "".join(f'<li><a href="/tarifler/{s}.html">{e(recipes[s]["title"])}</a></li>' for s in d["related"])
        rel_html = f'<h2>İlgili tarifler</h2><ul>{items}</ul>'
    body = f"""{bc_html}
<article>
<h1>{e(d["title"])}</h1>
<p class="answer">{e(d["answer"])}</p>
{figure(d)}
{secs}
{rel_html}
{cta(d)}
{date_line(d)}
</article>"""
    write(rel, page(rel, f'{d["title"]} | Çimenağa Tarifler', d["description"], body, [art, bc_ld], d.get("image")))
    return rel


def build_index(recipes, articles):
    def li(prefix, d):
        return f'<li><a href="/{prefix}/{d["slug"]}.html">{e(d["title"])}</a><p>{e(d["description"])}</p></li>'
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "Çimenağa Tarifler",
           "url": SITE + "/", "inLanguage": "tr", "publisher": ORG}]
    body = f"""<h1>Kastamonu Pastırması ve Sucuğu ile Tarifler</h1>
<p class="answer">Kastamonu pastırması ve sucuğuyla yapılan tarifler ve bu lezzetler hakkında makaleler. Ürünlerimiz 1927'den beri Kastamonu'dan, <a href="{SHOP}/">cimenaga.com</a> üzerinden sipariş edilir.</p>
<h2 id="tarifler">Tarifler</h2>
<ul class="list">{"".join(li("tarifler", d) for d in recipes.values())}</ul>
<h2 id="makaleler">Makaleler</h2>
<ul class="list">{"".join(li("makaleler", d) for d in articles.values())}</ul>"""
    write("index.html", page("index.html", "Kastamonu Pastırması ve Sucuğu Tarifleri | Çimenağa Tarifler",
                             "Kastamonu pastırması ve sucuğuyla yapılan tarifler ve Kastamonu'nun lezzetleri hakkında makaleler.",
                             body, ld))


def load(sub):
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((CONTENT / sub).glob("*.json"))}


def main():
    recipes, articles = load("tarifler"), load("makaleler")
    rels = ["index.html"]
    build_index(recipes, articles)
    rels += [build_recipe(d) for d in recipes.values()]
    rels += [build_article(d, recipes) for d in articles.values()]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"<url><loc>{url_of(r)}</loc></url>\n" for r in rels) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /docs/\nSitemap: {SITE}/sitemap.xml\n")
    lines = ["# Çimenağa Tarifler", "", "> Kastamonu pastırması ve sucuğuyla tarifler ve makaleler. Ürünler: " + SHOP + "/", "", "## Tarifler"]
    lines += [f'- [{d["title"]}]({SITE}/tarifler/{d["slug"]}.html): {d["description"]}' for d in recipes.values()]
    lines += ["", "## Makaleler"]
    lines += [f'- [{d["title"]}]({SITE}/makaleler/{d["slug"]}.html): {d["description"]}' for d in articles.values()]
    write("llms.txt", "\n".join(lines) + "\n")
    print(f"{len(recipes)} tarif, {len(articles)} makale üretildi")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Taslak tarifi yaz**

`docs/content/tarifler/pastirmali-yumurta.json` içine, Task 4'te doğrulanıp değiştirilecek bir taslak koy. Alanlar yukarıdaki listedeki gibi olmalı. Metin "TASLAK" kelimesi içermemeli ama Task 4 bitmeden yayına alınmaz.

- [ ] **Step 5: Üret ve doğrula**

Run: `cd /ana/cimenaga/cimenagapastirma.com && python3 docs/build.py && python3 docs/check.py --partial`
Expected: "1 tarif, 0 makale üretildi" ve ardından `OK`.

- [ ] **Step 6: Hata yolu testi (Review Focus: yanlış ürün slug'ı)**

`pastirmali-yumurta.json` içindeki `products` değerini geçici olarak `["yanlis"]` yap.
Run: `python3 docs/build.py`
Expected: `KeyError: 'yanlis'`. Sonra değeri geri al ve `python3 docs/build.py` yeniden çalıştır.

- [ ] **Step 7: Kaçış testi (Review Focus: özel karakterler)**

Geçici olarak `title` değerine `Pastırma & "Çemen" <test>` yaz, derle ve çalıştır:
`python3 docs/check.py --partial` → `OK`, `grep -c '&amp;' tarifler/pastirmali-yumurta.html` → 1 ya da daha fazla. Başlığı geri al.

