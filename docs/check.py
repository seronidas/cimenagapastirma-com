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
