#!/usr/bin/env python3
"""
Arma versiones de vista previa autocontenidas (un HTML por página, con todo
adentro: CSS, JS, tipografía, fotos y video) para mirar la web sin servidor.
Salida: preview/PIVM-WEB-<pagina>.html  (no se publica; está en .gitignore)

    python3 tools/make_preview.py
"""
import base64, re, mimetypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "preview"; OUT.mkdir(exist_ok=True)
PAGES = {"": "home", "empresas/": "empresas", "inversores/": "inversores"}
cache = {}

def data_uri(path: Path):
    if path not in cache:
        mt = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix == ".webp": mt = "image/webp"
        if path.suffix == ".woff2": mt = "font/woff2"
        if path.suffix == ".svg": mt = "image/svg+xml"
        cache[path] = f"data:{mt};base64," + base64.b64encode(path.read_bytes()).decode()
    return cache[path]

def resolve(base: Path, url: str):
    url = url.split("?")[0].split("#")[0]
    p = (base / url).resolve()
    return p if p.is_file() and ROOT in p.parents else None

def build(slug, name):
    page = ROOT / (slug + "index.html")
    base = page.parent
    h = page.read_text(encoding="utf-8")
    # CSS (con sus fuentes) y JS en línea
    css_path = ROOT / "css" / "site.css"
    css = css_path.read_text(encoding="utf-8")
    css = re.sub(r"url\((\.\./fonts/[^)]+)\)", lambda m: f"url({data_uri(resolve(css_path.parent, m.group(1)))})", css)
    h = re.sub(r'<link rel="stylesheet" href="[^"]*css/site\.css[^"]*">', lambda m: f"<style>{css}</style>", h)
    js = (ROOT / "js" / "site.js").read_text(encoding="utf-8")
    h = re.sub(r'<script src="[^"]*js/site\.js[^"]*" defer></script>', lambda m: f"<script>{js}</script>", h)
    h = re.sub(r'<link rel="(preload|manifest)"[^>]*>', "", h)
    # srcset fuera: queda una sola imagen (la mediana) para no repetir peso
    h = re.sub(r'\s(srcset|sizes)="[^"]*"', "", h)
    # video: van las dos versiones (16:9 escritorio, 9:16 celular), como en la web
    # links entre páginas -> archivos de vista previa
    def link(m):
        url = m.group(2)
        for s, n in PAGES.items():
            target = (ROOT / s).resolve()
            u = url.split("#")[0]
            frag = ("#" + url.split("#")[1]) if "#" in url else ""
            if u and (base / u).resolve() in (target, target / "index.html"):
                return f'{m.group(1)}="PIVM-WEB-{n}.html{frag}"'
        return m.group(0)
    h = re.sub(r'(href)="((?:\.\./|\./|[a-z\-]+/|index\.html)[^"]*)"', link, h)
    # recursos locales -> data URI
    def inline(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith(("http", "data:", "mailto:", "tel:", "#")): return m.group(0)
        p = resolve(base, url)
        return f'{attr}="{data_uri(p)}"' if p else m.group(0)
    h = re.sub(r'(src|poster|data-desktop|data-desktop-poster|data-mobile|data-mobile-poster|data-fallback|href)="([^"]+\.(?:webp|png|jpg|svg|ico|mp4))"', inline, h)
    h = re.sub(r'url\(([^)"\']+\.png)\)', lambda m: f"url({data_uri(resolve(base, m.group(1)))})" if resolve(base, m.group(1)) else m.group(0), h)
    # brochure: se busca junto al HTML de vista previa
    h = re.sub(r'href="(?:\.\./)?brochures/([^"]+\.pdf)"', r'href="\1"', h)
    out = OUT / f"PIVM-WEB-{name}.html"
    out.write_text(h, encoding="utf-8")
    print(f"  {out.name}  {out.stat().st_size/1e6:.1f} MB")

if __name__ == "__main__":
    for s, n in PAGES.items(): build(s, n)
