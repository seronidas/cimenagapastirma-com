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

---

### Task 1: Doğrulama betiği (`check.py`)

**Files:**
- Create: `docs/check.py`

**Interfaces:**
- Produces: `python3 docs/check.py` komutu. Hata varsa çıkış kodu 1, her hata bir satır. Hata yoksa `OK` yazar.

- [ ] **Step 1: `docs/check.py` dosyasını yaz**

```python
#!/usr/bin/env python3
"""Yayın öncesi doğrulama. Kullanım: python3 docs/check.py"""
import json, pathlib, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOP = pathlib.Path("/ana/cimenaga/cimenaga.com")
SITE = "https://cimenagapastirma.com"
errors = []


def err(msg):
    errors.append(msg)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.title = ""
        self.meta = {}
        self.canonical = None
        self.links = []
        self.imgs = []
        self.ld = []
        self._in_ld = False
        self._in_title = False
        self._buf = ""
        self.ingredient_items = 0
        self._in_ing = False
        self.step_items = 0
        self._in_steps = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "meta" and a.get("name"):
            self.meta[a["name"]] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True
            self._buf = ""
        elif tag == "script":
            err("JS yasak: <script> bulundu")
        elif tag == "ul" and a.get("id") == "malzemeler":
            self._in_ing = True
        elif tag == "ol" and a.get("id") == "adimlar":
            self._in_steps = True
        elif tag == "li" and self._in_ing:
            self.ingredient_items += 1
        elif tag == "li" and self._in_steps:
            self.step_items += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_ld:
            self._in_ld = False
            self.ld.append(self._buf)
        elif tag == "ul":
            self._in_ing = False
        elif tag == "ol":
            self._in_steps = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ld:
            self._buf += data


def local_target(href):
    path = urlparse(href).path
    if path.endswith("/"):
        path += "index.html"
    return ROOT / path.lstrip("/")


pages = [p for p in ROOT.rglob("*.html") if "docs" not in p.relative_to(ROOT).parts]
if not pages:
    err("Hiç HTML sayfası yok")

for f in pages:
    rel = f.relative_to(ROOT)
    p = Page()
    p.feed(f.read_text(encoding="utf-8"))
    if p.h1 != 1:
        err(f"{rel}: h1 sayısı {p.h1}, 1 olmalı")
    if not p.title.strip():
        err(f"{rel}: title yok")
    if not p.meta.get("description"):
        err(f"{rel}: meta description yok")
    expected = SITE + ("/" if rel.name == "index.html" and len(rel.parts) == 1 else "/" + rel.as_posix())
    if p.canonical != expected:
        err(f"{rel}: canonical {p.canonical!r}, beklenen {expected!r}")
    for href in p.links:
        u = urlparse(href)
        if u.scheme in ("http", "https"):
            if u.netloc == "cimenaga.com" and u.path.startswith("/urun/"):
                if not (SHOP / u.path.lstrip("/")).is_file():
                    err(f"{rel}: ürün sayfası yok: {href}")
        elif href.startswith("/"):
            if not local_target(href).is_file():
                err(f"{rel}: kırık iç bağlantı {href}")
    for im in p.imgs:
        for k in ("alt", "width", "height", "src"):
            if not im.get(k):
                err(f"{rel}: img {k} eksik")
        src = im.get("src", "")
        if src.startswith("/") and not (ROOT / src.lstrip("/")).is_file():
            err(f"{rel}: görsel dosyası yok {src}")
    types = []
    for raw in p.ld:
        try:
            data = json.loads(raw)
        except ValueError as e:
            err(f"{rel}: JSON-LD geçersiz: {e}")
            continue
        for d in (data if isinstance(data, list) else [data]):
            types.append(d.get("@type"))
            if "nutrition" in d:
                err(f"{rel}: nutrition yasak")
            if d.get("@type") == "Recipe":
                if len(d.get("recipeIngredient", [])) < 3:
                    err(f"{rel}: en az 3 malzeme gerekir")
                if len(d.get("recipeInstructions", [])) < 2:
                    err(f"{rel}: en az 2 adım gerekir")
                if len(d.get("recipeIngredient", [])) != p.ingredient_items:
                    err(f"{rel}: schema malzeme sayısı görünür listeyle uyuşmuyor")
                if len(d.get("recipeInstructions", [])) != p.step_items:
                    err(f"{rel}: schema adım sayısı görünür listeyle uyuşmuyor")
    if rel.parts[0] == "tarifler" and "Recipe" not in types:
        err(f"{rel}: Recipe schema yok")
    if rel.parts[0] == "makaleler" and "Article" not in types:
        err(f"{rel}: Article schema yok")
    if rel.name != "index.html" or len(rel.parts) > 1:
        if "BreadcrumbList" not in types:
            err(f"{rel}: BreadcrumbList yok")

# sitemap <-> dosyalar
sm = ROOT / "sitemap.xml"
if not sm.is_file():
    err("sitemap.xml yok")
else:
    urls = set(re.findall(r"<loc>(.*?)</loc>", sm.read_text(encoding="utf-8")))
    on_disk = set()
    for f in pages:
        rel = f.relative_to(ROOT).as_posix()
        on_disk.add(SITE + "/" if rel == "index.html" else f"{SITE}/{rel}")
    for u in sorted(urls - on_disk):
        err(f"sitemap'te var, dosyası yok: {u}")
    for u in sorted(on_disk - urls):
        err(f"dosya var, sitemap'te yok: {u}")

robots = ROOT / "robots.txt"
if not robots.is_file():
    err("robots.txt yok")
else:
    t = robots.read_text(encoding="utf-8")
    if "Disallow: /docs/" not in t or f"Sitemap: {SITE}/sitemap.xml" not in t:
        err("robots.txt Disallow: /docs/ ve Sitemap satırlarını içermeli")
if not (ROOT / "llms.txt").is_file():
    err("llms.txt yok")

# sayım
n_t = len(list((ROOT / "tarifler").glob("*.html"))) if (ROOT / "tarifler").is_dir() else 0
n_m = len(list((ROOT / "makaleler").glob("*.html"))) if (ROOT / "makaleler").is_dir() else 0
if "--partial" not in sys.argv:
    if n_t != 8:
        err(f"8 tarif olmalı, {n_t} var")
    if n_m != 4:
        err(f"4 makale olmalı, {n_m} var")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("OK")
```

- [ ] **Step 2: Dosyayı oluştur ve çalıştır, başarısız olduğunu doğrula**

Step 1'deki kodu `docs/check.py` olarak kaydet, ardından çalıştır.
Run: `cd /ana/cimenaga/cimenagapastirma.com && python3 docs/check.py`
Expected: FAIL. "Hiç HTML sayfası yok", "sitemap.xml yok", "robots.txt yok", "llms.txt yok", "8 tarif olmalı, 0 var", "4 makale olmalı, 0 var" satırları görünür. Çıkış kodu 1.

---

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

---

### Task 3: Araştırma ve kaynak notları

**Files:**
- Create: `docs/kaynaklar.md`

**Interfaces:**
- Produces: Her makale ve tarif için doğrulanmış bilgi ve kaynak URL'leri. Task 4-7 yalnızca buradaki bilgilere dayanır.

- [ ] **Step 1: cimenaga.com'dan alıntıları çıkar**

`/ana/cimenaga/cimenaga.com/hikayemiz.html`, `urun/kastamonu-pastirmasi.html`, `kastamonu-cografi-isaretli-urunleri.html`, `hakkimizda.html` içinden pastırma, çemen, Taşköprü sarımsağı ve coğrafi işaret ile ilgili cümleleri `docs/kaynaklar.md` içine "cimenaga.com" başlığı altında, dosya adıyla birlikte kopyala.

- [ ] **Step 2: Resmî kaynaklarla doğrula**

WebSearch ile TürkPatent coğrafi işaret kayıtlarını ara: Kastamonu Pastırması (no 711, 2021, mahreç işareti), Taşköprü Sarımsağı (2010, AB tescili), Tosya Pirinci (2017). Her bilgi için en az bir resmî URL kaydet. Sitenle çelişen bir bilgi bulursan kullanıcıya bildir, sessizce seçme.

- [ ] **Step 3: Makale 3 için gerçek bilgi ara**

Pastırmanın dilimlenmesi ve saklanması (buzdolabı, kesilmiş/kesilmemiş, dondurma) için güvenilir kaynak ara (ör. Tarım ve Orman Bakanlığı, TÜRKOMP, akademik kaynak). Süre ve sıcaklık gibi sayısal değerleri yalnızca kaynakta açıkça yazıyorsa kaydet. Bulunamazsa "Bulunamadı, yazılmayacak" yaz.

- [ ] **Step 4: Her tarif için en az iki bağımsız kaynakta karşılaştır**

8 tarifin her biri için malzeme türleri, sıra ve pişirme süresi aralıklarını iki bağımsız tarif kaynağında (ör. Nefis Yemek Tarifleri, Yemek.com, resmî kültür turizm sayfaları) karşılaştır. Ortak olan aralıkları ve URL'leri `docs/kaynaklar.md` içine yaz. Birbirinden çok farklı olan değeri yazma.

- [ ] **Step 5: Kontrol**

Run: `grep -c "http" docs/kaynaklar.md`
Expected: en az 20 (8 tarif × 2 kaynak + resmî kaynaklar).

---

### Task 4: Tarifler 1-4

**Files:**
- Create/Modify: `docs/content/tarifler/pastirmali-yumurta.json`, `sucuklu-yumurta.json`, `pastirmali-ince-pide.json`, `sucuklu-pide.json`
- Generated: `tarifler/*.html`, `index.html`, `sitemap.xml`, `llms.txt`

**Interfaces:**
- Consumes: `docs/kaynaklar.md` (Task 3), JSON şeması (Task 2).
- Produces: 4 tarif sayfası.

Ürün eşleşmesi: `pastirmali-yumurta` → `["kastamonu-pastirmasi"]`; `sucuklu-yumurta` → `["kastamonu-sucugu"]`; `pastirmali-ince-pide` → `["kastamonu-pastirmasi", "kastamonu-pastirmali-ince-pide"]` (evde yapmak istemeyenler için hazır pide); `sucuklu-pide` → `["kastamonu-sucugu"]`.

- [ ] **Step 1: Her tarif için JSON yaz**

`answer` alanı tek paragraf ve doğrudan cevap olsun ("Pastırmalı yumurta yaklaşık X dakikada hazırlanır…"). Değerler yalnızca `docs/kaynaklar.md` içindeki ortak aralıklardan seçilir. `ingredients` en az 3, `steps` en az 2 öğe. Ölçüler Türkçe ve açık yazılır ("2 adet yumurta", "100 g pastırma"). Kastamonu pastırmasını anlatırken yalnızca doğrulanmış cümleleri kullan.

- [ ] **Step 2: Derle ve doğrula**

Run: `cd /ana/cimenaga/cimenagapastirma.com && python3 docs/build.py && python3 docs/check.py --partial`
Expected: "4 tarif, 0 makale üretildi" ve `OK`.

- [ ] **Step 3: Kullanıcıdan deneme onayı iste**

Dört tarifin sürelerini ve ölçülerini kullanıcıya liste halinde göster ve yayından önce denemesini ya da onaylamasını iste. Cevap gelene kadar bu 4 tarifi "onay bekliyor" olarak işaretle.

---

### Task 5: Tarifler 5-8

**Files:**
- Create: `docs/content/tarifler/pastirmali-tost.json`, `pastirmali-borek.json`, `sucuklu-patates.json`, `pastirmali-kuru-fasulye.json`

**Interfaces:**
- Consumes: Task 3 ve Task 2.
- Produces: 4 tarif sayfası daha (toplam 8).

Ürün eşleşmesi: `pastirmali-tost` → pastırma, `pastirmali-borek` → pastırma, `sucuklu-patates` → sucuk, `pastirmali-kuru-fasulye` → pastırma.

- [ ] **Step 1: Task 4, Step 1 kurallarıyla 4 JSON yaz**

- [ ] **Step 2: Derle ve doğrula**

Run: `python3 docs/build.py && python3 docs/check.py --partial`
Expected: "8 tarif, 0 makale üretildi" ve `OK`.

- [ ] **Step 3: Kullanıcıdan deneme onayı iste** (Task 4, Step 3 ile aynı biçimde)

---

### Task 6: Makaleler 1-2

**Files:**
- Create: `docs/content/makaleler/kastamonu-pastirmasi-nedir.json`, `cemen-ve-taskopru-sarimsagi.json`

**Interfaces:**
- Consumes: Task 3 (yalnızca doğrulanmış bilgiler).
- Produces: 2 makale sayfası.

İçerik sınırı: Makale 1 yalnızca sitedeki ve resmî kaynaklardaki bilgileri kullanır (kemiksiz sırt eti, kaya tuzu, ağırlık altında sıkıştırma, güneşte kurutma, çemen, Eylül-Nisan üretim, 2021 mahreç işareti, no 711, Devrekani 1927 hikâyesi). Makale 2: çemenin Taşköprü sarımsaklı olduğu, Taşköprü sarımsağının 2010 tescili ve AB tescili, Kastamonu sarımsağının yaklaşık yüzde 90'ının Taşköprü'den geldiği. Çemenin içeriği (baharat listesi vb.) kaynakta yoksa yazılmaz.

- [ ] **Step 1: İki JSON yaz.** `answer` ilk paragrafta kısa cevap versin. `related` alanında en az iki tarif slug'ı olsun. Her `h2` bir soru olabilir ("Kastamonu pastırması nasıl yapılır?").

- [ ] **Step 2: Derle ve doğrula**

Run: `python3 docs/build.py && python3 docs/check.py --partial`
Expected: `OK`.

- [ ] **Step 3: Her cümleyi Task 3 notlarıyla karşılaştır.** Notlarda karşılığı olmayan cümleyi sil.

---

### Task 7: Makaleler 3-4

**Files:**
- Create: `docs/content/makaleler/pastirma-nasil-dilimlenir-ve-saklanir.json`, `kastamonu-cografi-isaretli-lezzetleri.json`

**Interfaces:**
- Consumes: Task 3.
- Produces: 2 makale sayfası daha (toplam 4).

İçerik sınırı: Makale 3 yalnızca Task 3, Step 3'te kaynağı bulunan bilgileri içerir. Bulunamayan sayısal bilgi (saklama süresi vb.) yazılmaz. Dilimleme için sitedeki ifadeler ("ince dilimlenip tavada, yumurta ya da pideyle") kullanılabilir. Makale 4: sitedeki coğrafi işaretli ürün listesi (Taşköprü Sarımsağı, Kastamonu Pastırması, Tosya Pirinci ve "Tescilli Diğer Lezzetler"), listenin zamanla değişebileceği notuyla ve TürkPatent veri tabanına yönlendirmeyle.

- [ ] **Step 1: İki JSON yaz.**

- [ ] **Step 2: Derle ve tam doğrulamayı çalıştır**

Run: `python3 docs/build.py && python3 docs/check.py`
Expected: "8 tarif, 4 makale üretildi" ve `OK` (`--partial` olmadan).

---

### Task 8: Görseller

**Files:**
- Create: `assets/img/*.webp`, `docs/gorsel-kaynaklari.md`
- Modify: `docs/content/**/*.json` (`image`, `image_alt`, `image_w`, `image_h`)

**Interfaces:**
- Consumes: 12 içerik dosyası.
- Produces: Görselli sayfalar ve kullanıcı için "görseli bulunamayanlar" listesi.

- [ ] **Step 1: Araçları kontrol et**

Run: `which cwebp magick convert; python3 -c "import PIL; print(PIL.__version__)"`
Expected: en az biri var. Yoksa kullanıcıya bildir.

- [ ] **Step 2: Her sayfa için görsel ara**

Unsplash, Pexels ve CC0 Wikimedia Commons'ta ara. Aranacaklar: pastırmalı yumurta, sucuklu yumurta, ince pide, tost, börek, patates, kuru fasulye, pastırma dilimleri, sarımsak, Kastamonu şehri. Lisans sayfasını WebFetch ile aç ve ücretsiz ticari kullanıma izin verdiğini doğrula. Sorun çıkan görseli kullanma. Dosyayı her biri kendi yeni boş klasörüne indir (örneğin scratchpad altında).

- [ ] **Step 3: Dönüştür ve yerleştir**

Genişlik en fazla 1200 px olacak şekilde WebP'ye çevir, `assets/img/<slug>.webp` olarak kaydet, gerçek `width` ve `height` değerlerini oku ve JSON'a yaz. `image_alt` görseli dürüstçe tanımlasın ("Tavada yumurtalı pastırma", pastırmanın Kastamonu olduğunu görselden anlaşılmıyorsa belirtme).

- [ ] **Step 4: Kaynak kaydı**

Her görsel için `docs/gorsel-kaynaklari.md` içine dosya adı, kaynak URL'si, fotoğrafçı ve lisans yaz. Bu bilgi sitede gösterilmez.

- [ ] **Step 5: Derle ve doğrula**

Run: `python3 docs/build.py && python3 docs/check.py`
Expected: `OK`.

- [ ] **Step 6: Görseli bulunamayan sayfaları listele.** Kullanıcıya göster.

---

### Task 9: Son doğrulama

**Files:**
- Verify: tüm site

- [ ] **Step 1: Tam kontrol**

Run: `cd /ana/cimenaga/cimenagapastirma.com && python3 docs/build.py && python3 docs/check.py && for f in $(find . -name '*.html' -not -path './docs/*'); do python3 - "$f" <<'EOF'
import re, sys, json
t = open(sys.argv[1], encoding="utf-8").read()
for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    json.loads(m)
EOF
done; echo done`
Expected: `OK`, ardından `done`, hata yok.

- [ ] **Step 2: Yasaklı içerik taraması**

Run: `grep -rniE "nutrition|kalori" --include=*.html . | grep -v '^./docs/'; grep -rn "<script" --include=*.html . | grep -v '^./docs/' | grep -v 'application/ld+json'`
Expected: iki komut da çıktı vermez (besin değeri ve JSON-LD dışı script yok).

- [ ] **Step 3: Tarayıcıda görünüm**

Yerel sunucu başlat (`python3 -m http.server 8080 --directory /ana/cimenaga/cimenagapastirma.com`), ana sayfayı, bir tarifi ve bir makaleyi mobil ve masaüstü genişliğinde incele (chrome-devtools MCP bağlanamazsa kullanıcıya bildir ve sayfaları `curl` ile kontrol et).

- [ ] **Step 4: Kullanıcıya rapor**

Raporda şunlar olsun: kaç sayfa üretildi, onay bekleyen tarifler, görseli bulunamayan sayfalar, doğrulanamadığı için yazılmayan bilgiler ve alan adına yükleme için yapılacaklar.
