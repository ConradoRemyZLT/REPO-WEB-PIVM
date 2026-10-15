#!/usr/bin/env python3
"""
Genera el sitio estático del Parque Industrial Vaca Muerta.

    python3 build.py

Lee content.json (textos ES/EN y datos), html/base.html (esqueleto) y
fotos/manifest.json (anchos disponibles de cada foto) y escribe:

    index.html · empresas/ · inversores/ · 404.html
    robots.txt · sitemap.xml · iconos/favicon.svg

No usa dependencias externas. Todo texto nuevo va en content.json en pares es/en.
"""
import json, html, math, re, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
C = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "fotos" / "manifest.json").read_text(encoding="utf-8"))
BASE = (ROOT / "html" / "base.html").read_text(encoding="utf-8")
LOGO_SVG = (ROOT / "logos" / "pivm-logo.svg").read_text(encoding="utf-8")
SITE = C["site"]
VERSION = time.strftime("%Y%m%d%H%M")

esc = lambda s: html.escape(str(s), quote=True)


# ----------------------------------------------------------------- helpers
def t(o, tag=None):
    """Texto bilingüe -> spans .l-es/.l-en (o texto plano si es igual)."""
    if isinstance(o, str):
        return esc(o)
    es, en = o.get("es", ""), o.get("en", "")
    if es == en:
        return esc(es)
    return f'<span class="l-es">{esc(es)}</span><span class="l-en">{esc(en)}</span>'


def tk(o, k):
    """Par de claves sueltas: o['es'|'en'] o o[k+'_es'|k+'_en']."""
    return t({"es": o.get(f"{k}_es", o.get("es")), "en": o.get(f"{k}_en", o.get("en"))})


def pair(es, en):
    return t({"es": es, "en": en})


def attr_i18n(attr, o):
    """Atributo traducible (alt, aria-label, placeholder)."""
    es, en = (o, o) if isinstance(o, str) else (o["es"], o["en"])
    return (f'{attr}="{esc(es)}" data-es-{attr}="{esc(es)}" data-en-{attr}="{esc(en)}" '
            f'data-i18n-attr="{attr}"')


def img(rel, key, alt, sizes="100vw", cls="", eager=False, extra=""):
    m = MANIFEST[key]
    ws = m["w"]
    srcset = ", ".join(f"{rel}{key}-{w}.webp {w}w" for w in ws)
    mid = ws[min(1, len(ws) - 1)]
    h = round(mid / m["ratio"])
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{rel}{key}-{mid}.webp" srcset="{srcset}" sizes="{sizes}" width="{mid}" height="{h}" '
            f'{attr_i18n("alt", alt)} {load} {extra}>')


ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
EXT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17L17 7M17 7H8M17 7v9"/></svg>'
DOWN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v12m0 0l-4-4m4 4l4-4M5 21h14"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M5 12.5l4.5 4.5L19 7"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>'
PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'
MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>'
WA = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.2-.3-.2-.6-.4zM12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2z"/></svg>'
PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>'
SOC = {
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zM9.5 9.5h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.2c0-1.3 0-2.9-1.8-2.9s-2 1.4-2 2.8V21h-4z"/></svg>',
    "youtube": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12c0 1.6.2 3.2.5 4.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1c.3-1.6.5-3.2.5-4.8s-.2-3.2-.5-4.8zM9.8 15V9l5.7 3z"/></svg>',
}


def bars(pos, cls=""):
    return f'<div class="bars {pos} {cls}" aria-hidden="true"><i></i><i></i><i></i></div>'


def eyebrow(o, center=False):
    return f'<div class="eyebrow{" center" if center else ""}" data-reveal="up">{t(o)}</div>'


def logo(cls="", label=True):
    svg = LOGO_SVG
    if not label:
        svg = svg.replace('role="img"', 'aria-hidden="true"')
    return svg.replace("<svg ", f'<svg class="{cls}" ', 1) if cls else svg


def wa_link(text_cls, inner, extra=""):
    m = SITE["whatsapp_msg"]
    return (f'<a class="{text_cls}" href="https://wa.me/{SITE["phone_e164"]}" target="_blank" rel="noopener" '
            f'data-wa="{SITE["phone_e164"]}" data-es-msg="{esc(m["es"])}" data-en-msg="{esc(m["en"])}" {extra}>{inner}</a>')


def brochure_btn(rel, cls="btn btn-cream", short=False):
    b = SITE["brochure"]
    lab_es = "Brochure" if short else "Descargar brochure"
    lab_en = "Brochure" if short else f"Download brochure {b['en_note']}"
    return (f'<a class="{cls}" href="{rel}{b["es"]}" download>{DOWN}{pair(lab_es, lab_en)}</a>')


# ----------------------------------------------------------------- header / footer
def header(rel, page):
    links = []
    mlinks = []
    for n in C["nav"]:
        href = n["href"] if n["href"].startswith("#") else rel + n["href"]
        if n["href"].startswith("index.html#") and page == "home":
            href = n["href"][len("index.html"):]
        cur = ' aria-current="page"' if n["page"] and n["page"] == page and page != "home" else ""
        links.append(f'<a href="{href}"{cur}>{t(n)}</a>')
        mlinks.append(f'<a class="mlink" href="{href}"{cur}>{t(n)}{ARROW}</a>')
    lang = ('<div class="lang" role="group" aria-label="Idioma / Language">'
            '<button type="button" data-lang-btn="es" aria-pressed="true">ES</button>'
            '<button type="button" data-lang-btn="en" aria-pressed="false">EN</button></div>')
    home = rel or "./"
    return f'''<header class="hdr" id="hdr">
  <a class="hlogo" href="{home}" aria-label="Parque Industrial Vaca Muerta — inicio">{logo(label=False)}</a>
  <nav class="menu" aria-label="Principal">{"".join(links)}</nav>
  <div class="htools">{lang}{brochure_btn(rel, "btn btn-cream hbro", short=True)}
    <button class="mbtn" type="button" aria-label="Menú" aria-expanded="false" aria-controls="mov"><span></span></button>
  </div>
</header>
<div class="mov" id="mov">{"".join(mlinks)}
  <div class="mfoot">{lang}{brochure_btn(rel)}{wa_link("btn btn-wa", WA + pair("Escribinos por WhatsApp", "Message us on WhatsApp"))}</div>
</div>'''


def footer(rel):
    soc = "".join(f'<a href="{s["url"]}" target="_blank" rel="noopener" aria-label="{s["label"]}">{SOC[s["id"]]}</a>' for s in SITE["social"])
    nav = "".join(f'<a href="{(n["href"] if n["href"].startswith("#") else rel + n["href"])}">{t(n)}</a>' for n in C["nav"])
    return f'''<footer class="foot">
  <div class="wrap">
    <div class="fgrid">
      <div class="fcol"><a class="flogo" href="{rel or "./"}" aria-label="Parque Industrial Vaca Muerta">{logo(label=False)}</a>
        <div class="fdev"><span>{pair("Desarrolla", "Developed by")}</span><a href="https://somoszlt.com/" target="_blank" rel="noopener"><img src="{rel}logos/zlt-blanco.png" alt="ZLT" width="80" height="36" loading="lazy"></a></div>
      </div>
      <div class="fcol"><b>{pair("Sitio", "Site")}</b>{nav}</div>
      <div class="fcol"><b>{pair("Contacto", "Contact")}</b>
        {wa_link("", esc(SITE["phone_display"]))}
        <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>
        <a href="{SITE["maps_url"]}" target="_blank" rel="noopener">{t(SITE["address"])}</a>
      </div>
      <div class="fcol"><b>{pair("Seguinos", "Follow us")}</b><span>@somoszlt</span><div class="socials">{soc}</div>
        <div style="margin-top:22px">{brochure_btn(rel, "btn btn-line")}</div></div>
    </div>
    <div class="flegal"><p>{t(SITE["legal"])}</p><span>© {SITE["year"]} Parque Industrial Vaca Muerta · ZLT</span></div>
  </div>
</footer>
{wa_link("wa-float", WA, 'aria-label="WhatsApp"')}
<a class="to-top" href="#top" {attr_i18n("aria-label", {"es": "Volver arriba", "en": "Back to top"})}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg></a>'''


# ----------------------------------------------------------------- bloques comunes
def stats_band():
    items = []
    for i, s in enumerate(C["stats"]):
        pre = f'<span class="pre">{t(s["pre"])}</span>' if s.get("pre") else '<span class="pre"></span>'
        num_es, num_en = s["num"], s.get("num_en", s["num"])
        num = (f'<span class="l-es" data-count="{num_es}">{num_es}</span><span class="l-en">{num_en}</span>'
               if num_es != num_en else f'<span data-count="{num_es}">{num_es}</span>')
        unit = f'<small>{s["unit"]}</small>' if s["unit"] else ""
        items.append(f'<div class="stat" data-reveal="up" style="--d:{i*0.07:.2f}s">{pre}<div class="snum">{num}{unit}</div><div class="slab">{t(s)}</div></div>')
    seals = "".join(f'<span class="seal">{CHECK}{t(s)}</span>' for s in C["seals"])
    return f'''<section class="stats-band" aria-label="Datos clave">
  <div class="wrap"><div class="stats">{"".join(items)}</div><div class="seals" data-reveal="up">{seals}</div></div>
</section>'''


def services_grid(rel, intro, bg_key="fotos/parque/aerea-lotes", cta_href=None):
    cards = "".join(
        f'<div class="svc" data-reveal="up" style="--d:{(i%4)*0.06:.2f}s"><div class="ico" style="-webkit-mask-image:url({rel}iconos/{s["icon"]}.png);mask-image:url({rel}iconos/{s["icon"]}.png)" aria-hidden="true"></div>'
        f'<b>{t(s)}</b><p>{tk(s, "d")}</p></div>' for i, s in enumerate(C["services"]))
    cta = f'<a class="link-arrow" href="{cta_href}">{t(intro["cta"])}{ARROW}</a>' if cta_href else ""
    return f'''<section class="sec navy svc-sec" id="infraestructura">
  <div class="bg">{img(rel, bg_key, {"es": "", "en": ""})}</div>
  <div class="wrap">
    <div class="sec-head"><div>{eyebrow(intro["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(intro["title"])}</h2></div>{cta}</div>
    <div class="svcs">{cards}</div>
  </div>
</section>'''


def map_svg():
    """Mapa esquemático (proyección equirectangular) — posiciones relativas reales."""
    W, H = 600, 612
    pts = [(d["lat"], d["lon"]) for d in C["distances"]] + [(C["anelo"]["lat"], C["anelo"]["lon"])]
    lat0 = sum(p[0] for p in pts) / len(pts)
    k = math.cos(math.radians(lat0))
    xs = [p[1] * k for p in pts]; ys = [-p[0] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    pad = 110
    s = min((W - 2 * pad) / (maxx - minx), (H - 2 * pad) / (maxy - miny))
    ox = (W - (maxx - minx) * s) / 2; oy = (H - (maxy - miny) * s) / 2
    P = lambda lat, lon: (ox + (lon * k - minx) * s, oy + (-lat - miny) * s)
    ax, ay = P(C["anelo"]["lat"], C["anelo"]["lon"])
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(0, W + 1, 50)) + \
           "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(0, H + 1, 50))
    roads, cities = [], []
    for d in C["distances"]:
        x, y = P(d["lat"], d["lon"])
        roads.append(f'<path class="m-road" d="M{ax:.1f} {ay:.1f} L{x:.1f} {y:.1f}"/>')
        # etiqueta: a la derecha salvo que no entre
        anchor, tx = ("end", x - 14) if x > W - 170 else ("start", x + 14)
        cities.append(f'<g class="m-city"><circle cx="{x:.1f}" cy="{y:.1f}" r="7"/>'
                      f'<text x="{tx:.1f}" y="{y-2:.1f}" text-anchor="{anchor}">{esc(d["city"])}</text>'
                      f'<text class="km" x="{tx:.1f}" y="{y+16:.1f}" text-anchor="{anchor}">{d["km"]} KM</text></g>')
    pin = (f'<g class="m-pin"><circle class="halo2" cx="{ax:.1f}" cy="{ay:.1f}" r="58"/><circle class="halo" cx="{ax:.1f}" cy="{ay:.1f}" r="30"/>'
           f'<rect x="{ax-9:.1f}" y="{ay-9:.1f}" width="18" height="18"/>'
           f'<text x="{ax+22:.1f}" y="{ay-6:.1f}">PIVM · AÑELO</text>'
           f'<text class="sub" x="{ax+22:.1f}" y="{ay+12:.1f}">RUTA 17 · KM 5</text></g>')
    north = (f'<g transform="translate({W-52},52)"><circle class="m-north" r="18"/><path d="M0 -12 L5 4 L0 1 L-5 4Z" fill="rgba(245,222,177,.75)"/>'
             f'<text class="m-label" x="0" y="34" text-anchor="middle">N</text></g>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Mapa esquemático: Añelo y distancias a Neuquén, Cutral Có y Rincón de los Sauces">'
            f'<g class="m-grid">{grid}</g>{"".join(roads)}{"".join(cities)}{pin}{north}'
            f'<text class="m-label" x="32" y="48">NEUQUÉN · PATAGONIA ARGENTINA</text>'
            f'<text class="m-note" x="32" y="{H-26}">Esquema ilustrativo · distancias por ruta</text></svg>')



# ---------------------------------------------------------------- masterplan interactivo
LOTES = json.loads((ROOT / "lotes.json").read_text(encoding="utf-8"))


def lot_type(m2):
    if m2 == 1350: return "t1350"
    if 2160 <= m2 <= 2170: return "t2166"
    if 2560 <= m2 <= 2570: return "t2566"
    if 3150 <= m2 <= 3165: return "t3155"
    if 4000 <= m2 <= 5000: return "t4000"
    if m2 > 20000: return "tmacro"
    return "totras"


def masterplan_map(rel, cap, alt):
    """Masterplan con los lotes coloreados por tipología y ficha al pasar el mouse.
    Datos: lotes.json (superficie, frente y fondo de las listas de precios, sin precios)."""
    M = C["masterplan"]
    types = {x["id"]: x for x in M["types"]}
    counts = {}
    polys = []
    for l in LOTES["lotes"]:
        ty = lot_type(l["m2"]); counts[ty] = counts.get(ty, 0) + 1
        pts = " ".join(f"{x:g},{y:g}" for x, y in l["poly"])
        polys.append(f'<polygon class="lt {ty}" points="{pts}" data-n="{l["lote"]}" data-m2="{l["m2"]}" data-f="{l["frente"]}" data-d="{l["fondo"]}" data-t="{ty}"/>')
    css_vars = "".join(f".{k}{{--c:{v['color']}}}" for k, v in types.items())
    legend = "".join(
        f'<button type="button" class="mp-key" data-type="{k}"><i style="background:{v["color"]}"></i>'
        f'<span><b>{t(v)}</b><small>{pair(v["d_es"], v["d_en"])} · {counts.get(k, 0)} {pair("lotes" if counts.get(k, 0) != 1 else "lote", "lots" if counts.get(k, 0) != 1 else "lot")}</small></span></button>'
        for k, v in types.items())
    i18n = {lg: {k: M[k][lg] for k in ("lot", "area", "dims", "front", "depth", "fos", "fot", "upto")} for lg in ("es", "en")}
    i18n["es"]["types"] = {k: v["es"] for k, v in types.items()}
    i18n["en"]["types"] = {k: v["en"] for k, v in types.items()}
    i18n["fos"] = LOTES["fos"]; i18n["fot"] = LOTES["fot"]
    W, H = LOTES["ancho"], LOTES["alto"]
    return f'''<figure class="mp wide mp-int" data-reveal="up" data-mp="{esc(json.dumps(i18n, ensure_ascii=False))}">
  <style>{css_vars}</style>
  <div class="mp-stage"><div class="mp-canvas">{img(rel, LOTES["imagen"], alt, sizes="(max-width:1240px) 100vw, 1240px")}
    <svg class="mp-svg" viewBox="0 0 {W} {H}" preserveAspectRatio="none" role="img" aria-label="{esc(alt["es"])}">{"".join(polys)}</svg>
    <div class="mp-tip" role="status" aria-live="polite" hidden></div></div></div>
  <div class="mp-legend"><div class="mp-lhead"><b>{t(M["legend_title"])}</b><span class="mp-hint"><span class="hov">{t(M["hint"])}</span><span class="tch">{t(M["hint_touch"])}</span></span></div>
    <div class="mp-keys">{legend}</div></div>
  <figcaption>{t(cap)} · {t(M["note"])}</figcaption>
</figure>'''

def location_section(rel, intro, cls="sand"):
    lis = "".join(
        f'<li><div><b>{esc(d["city"])}</b><span>{tk(d, "")}</span></div><span class="km">{d["km"]}<small>km</small></span></li>'
        for d in C["distances"])
    return f'''<section class="sec {cls}" id="ubicacion">
  {bars("r t", "soft")}
  <div class="wrap loc">
    <div class="map" data-reveal="scale">{map_svg()}</div>
    <div>{eyebrow(intro["eyebrow"])}<h2 class="h2" data-reveal="up">{t(intro["title"])}</h2>
      <p class="prose" data-reveal="up">{t(intro["text"])}</p>
      <ul class="dist" data-reveal="up">{lis}</ul>
      <div class="btns" data-reveal="up"><a class="btn btn-navy" href="{SITE["maps_url"]}" target="_blank" rel="noopener">{PIN}{t(intro["cta"])}</a></div>
    </div>
  </div>
</section>'''


def gallery(rel, items, autoplay=True, label="Galería"):
    n = len(items)
    slides = "".join(
        f'<figure class="gslide" role="group" aria-roledescription="slide" aria-label="{i+1} / {n}">'
        f'{img(rel, it["src"], it, sizes="(max-width:1240px) 100vw, 1240px")}<figcaption>{t(it)}</figcaption></figure>'
        for i, it in enumerate(items))
    dots = "".join(f'<button class="gdot" type="button" aria-label="Foto {i+1}"></button>' for i in range(n))
    return f'''<div class="gallery" data-gallery {"data-autoplay" if autoplay else ""} tabindex="0" aria-roledescription="carousel" aria-label="{label}" data-reveal="up">
  <div class="gviewport"><div class="gtrack">{slides}</div></div>
  <button class="garr gprev" type="button" aria-label="Anterior"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 6l-6 6 6 6"/></svg></button>
  <button class="garr gnext" type="button" aria-label="Siguiente"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 6l6 6-6 6"/></svg></button>
  <div class="gcount"><span class="gc-cur">1</span> / {n}</div>
  <div class="gdots">{dots}</div>
</div>'''


def tour360(rel):
    tr = SITE["tour360"]
    return f'''<div class="tour" data-reveal="up">
  <div class="tour-head"><span class="tour-lab">{pair("Recorrido 360°", "360° tour")}</span>
    <span class="small">{pair("Arrastrá para mirar alrededor", "Drag to look around")}</span></div>
  <div class="tour-box" data-tour="{tr["id"]}">
    {img(rel, "fotos/parque/aerea-horizonte", {"es": "", "en": ""}, sizes="(max-width:1240px) 100vw, 1240px")}
    <button class="tour-start" type="button" {attr_i18n("aria-label", tr)}>
      <span class="ts-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 6.5v11c-3 .9-6 1.4-9 1.4s-6-.5-9-1.4v-11c3 .9 6 1.4 9 1.4s6-.5 9-1.4z"/><path d="M7.5 14.5l3-4 2.5 3 1.8-2 1.7 3"/></svg></span>
      <span class="ts-txt">{t(tr)}</span>
      <span class="ts-go">{PLAY}{pair("Iniciar recorrido", "Start tour")}</span>
    </button>
  </div>
</div>'''


def video_cards(rel):
    out = []
    for key, fb in (("oficial", "fotos/parque/portico-frente"), ("avance", "fotos/parque/aerea-avenida")):
        v = SITE["videos"][key]
        fallback = f'{rel}{fb}-800.webp'
        out.append(f'''<div class="vcard" data-reveal="up"><div class="vframe">
  <img data-yt-thumb="{v["id"]}" data-fallback="{fallback}" src="{fallback}" alt="" loading="lazy">
  <button class="vplay" type="button" data-yt="{v["id"]}" {attr_i18n("aria-label", v)}><span>{PLAY}</span></button>
</div><div class="vtitle">{t(v)}</div></div>''')
    return f'<div class="vgrid">{"".join(out)}</div>'


def allies(rel, cls="paper"):
    items = []
    # proporción de cada logo: misma superficie visual aproximada
    from PIL import Image  # solo para medir; Pillow ya se usa en tools/
    for p in C["partners"]:
        im = Image.open(ROOT / "logos" / "acompanan" / f'{p["id"]}-navy.png')
        r = im.width / im.height
        area = 3400
        h = min(52, math.sqrt(area / r)); w = h * r
        if w > 150: w = 150; h = w / r
        items.append(f'<div class="mq-item"><img src="{rel}logos/acompanan/{p["id"]}-navy.png" alt="{esc(p["name"])}" '
                     f'style="--lw:{w:.0f}px;--lh:{h:.0f}px" width="{w:.0f}" height="{h:.0f}" loading="lazy"></div>')
    track = "".join(items)
    dup = track.replace('alt="', 'aria-hidden="true" alt="')
    return f'''<section class="sec tight {cls}" id="acompanan" aria-label="Desarrolla y acompañan">
  <div class="wrap allies">
    <div class="dev" data-reveal="up"><span class="lab">{pair("Desarrolla", "Developed by")}</span>
      <a href="https://somoszlt.com/" target="_blank" rel="noopener"><img src="{rel}logos/zlt-navy.png" alt="ZLT" width="98" height="44"></a></div>
    <div class="acc" data-reveal="up"><span class="acc-lab">{pair("Acompañan", "Partners")}</span>
      <div class="mq"><div class="mq-track">{track}{dup}</div></div></div>
  </div>
</section>'''


def contact(rel, preselect=""):
    ct = C["contact"]
    opts = "".join(f'<option value="{p["id"]}" data-modes="{" ".join(p["modes"])}" data-es-label="{esc(p["es"])}" data-en-label="{esc(p["en"])}" '
                   f'data-i18n-attr="label">{esc(p["es"])}</option>' for p in ct["profiles"])
    sw = ct["switch"]
    switch = (f'<div class="fswitch" role="radiogroup" {attr_i18n("aria-label", sw["aria"])}>'
              f'<input type="radio" name="soy" id="soy-empresa" value="empresa" checked><label for="soy-empresa">{t(sw["empresa"])}</label>'
              f'<input type="radio" name="soy" id="soy-inversor" value="inversor"><label for="soy-inversor">{t(sw["inversor"])}</label>'
              f'<span class="fs-thumb" aria-hidden="true"></span></div>')
    cfg = esc(json.dumps({"wa": SITE["phone_e164"], "mail": SITE["email"]}))
    ph = lambda es, en: attr_i18n("placeholder", {"es": es, "en": en})
    return f'''<section class="sec dark contact" id="contacto">
  {bars("l b", "bc soft")}
  <div class="wrap cgrid">
    <div>{eyebrow(ct["eyebrow"])}<h2 class="h2" data-reveal="up">{t(ct["title"])}</h2>
      <p class="lead" data-reveal="up">{t(ct["text"])}</p>
      <ul class="clist" data-reveal="up">
        <li>{wa_link("", f'<span class="ci">{WA}</span><span><b>{esc(SITE["phone_display"])}</b><small>WhatsApp</small></span>')}</li>
        <li><a href="tel:+{SITE["phone_e164"]}"><span class="ci">{PHONE}</span><span><b>{esc(SITE["phone_display"])}</b><small>{pair("Teléfono", "Phone")}</small></span></a></li>
        <li><a href="mailto:{SITE["email"]}"><span class="ci">{MAIL}</span><span><b>{SITE["email"]}</b><small>Email</small></span></a></li>
        <li><a href="{SITE["maps_url"]}" target="_blank" rel="noopener"><span class="ci">{PIN}</span><span><b>{t(SITE["address"])}</b><small>{pair("Cómo llegar", "Directions")}</small></span></a></li>
      </ul>
      <div class="btns" data-reveal="up">{brochure_btn(rel)}</div>
    </div>
    <form class="form" data-contact-form data-cfg="{cfg}" data-preselect="{preselect}" novalidate data-reveal="up">
      <h3>{pair("Dejanos tu consulta", "Send us your enquiry")}</h3>
      <p class="fsub">{pair("Elegí cómo enviarla: por WhatsApp o por mail.", "Choose how to send it: WhatsApp or email.")}</p>
      {switch}
      <div class="frow">
        <div class="field"><label for="f-nombre">{pair("Nombre y apellido *", "Full name *")}</label><input id="f-nombre" name="nombre" autocomplete="name" required>
          <span class="ferr">{pair("Completá tu nombre.", "Please enter your name.")}</span></div>
        <div class="field"><label for="f-empresa">{pair("Empresa", "Company")}</label><input id="f-empresa" name="empresa" autocomplete="organization"></div>
      </div>
      <div class="frow">
        <div class="field"><label for="f-tel">{pair("Celular *", "Mobile *")}</label><input id="f-tel" name="tel" type="tel" autocomplete="tel" required {ph("+54 9 …", "+54 9 …")}>
          <span class="ferr">{pair("Dejanos un número de contacto.", "Please leave a contact number.")}</span></div>
        <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email">
          <span class="ferr">{pair("Revisá el formato del mail.", "Please check the email format.")}</span></div>
      </div>
      <div class="field"><label for="f-perfil">{pair("¿Qué estás buscando?", "What are you looking for?")}</label><select id="f-perfil" name="perfil">{opts}</select></div>
      <div class="field"><label for="f-msg">{pair("Consulta", "Message")}</label><textarea id="f-msg" name="msg" {ph(sw["msg_empresa"]["es"], sw["msg_empresa"]["en"])} data-ph-empresa-es="{esc(sw["msg_empresa"]["es"])}" data-ph-empresa-en="{esc(sw["msg_empresa"]["en"])}" data-ph-inversor-es="{esc(sw["msg_inversor"]["es"])}" data-ph-inversor-en="{esc(sw["msg_inversor"]["en"])}"></textarea></div>
      <div class="fbtns">
        <button class="btn btn-wa" type="button" data-send="wa">{WA}{pair("Enviar por WhatsApp", "Send via WhatsApp")}</button>
        <button class="btn btn-navy" type="button" data-send="mail">{MAIL}{pair("Enviar por mail", "Send via email")}</button>
      </div>
      <p class="fnote">{pair("Al enviar se abre WhatsApp o tu correo con el mensaje armado. No guardamos tus datos en este sitio.", "Sending opens WhatsApp or your email app with the message ready. This site does not store your data.")}</p>
    </form>
  </div>
</section>'''


# ----------------------------------------------------------------- páginas
def page_home(rel):
    P = C["pages"]["home"]; h = P["hero"]; hv = SITE["hero_video"]
    hero = f'''<section class="hero" id="inicio">
  <div class="hero-media">
    <video data-hero-video autoplay muted loop playsinline preload="auto" poster="{rel}{hv["desktop_poster"]}"
      data-desktop="{rel}{hv["desktop"]}" data-mobile="{rel}{hv["mobile"]}"
      data-desktop-poster="{rel}{hv["desktop_poster"]}" data-mobile-poster="{rel}{hv["mobile_poster"]}" aria-hidden="true"></video>
  </div>
  <div class="hero-inner">
    <div class="hero-eyebrow" data-reveal="up" style="--d:.05s">{t(h["eyebrow"])}</div>
    <h1 class="hero-title" data-reveal="up" style="--d:.1s">{t(h["title"])}</h1>
    <div class="hero-foot">
      <div>
        <p class="hero-lead" data-reveal="up" style="--d:.16s">{t(h["lead"])}</p>
        <div class="btns" data-reveal="up" style="--d:.22s">
          <a class="btn btn-cream" href="{rel}empresas/">{t(h["cta1"])}{ARROW}</a>
          <a class="btn btn-line" href="{rel}inversores/">{t(h["cta2"])}{ARROW}</a>
        </div>
      </div>
      <div class="vctrl" data-reveal="up" style="--d:.3s">
        <button class="vbtn" type="button" data-v-sound {attr_i18n("aria-label", {"es": "Activar o silenciar sonido", "en": "Toggle sound"})}>
          <svg class="off" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 9h4l5-4v14l-5-4H4z"/><path d="M17 9l4 6M21 9l-4 6"/></svg>
          <svg class="on" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 9h4l5-4v14l-5-4H4z"/><path d="M17 8.5a5 5 0 0 1 0 7M19.5 6a8.5 8.5 0 0 1 0 12"/></svg></button>
        <button class="vbtn" type="button" data-v-play {attr_i18n("aria-label", {"es": "Pausar o reproducir video", "en": "Pause or play video"})}>
          <svg class="off" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          <svg class="on" viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg></button>
      </div>
    </div>
  </div>
  <span class="scrollcue" aria-hidden="true"></span>
</section>'''

    pth = P["paths"]
    def pcard(k, imgkey, href):
        c = pth[k]
        lis = "".join(f'<li>{pair(a, b)}</li>' for a, b in zip(c["bullets_es"], c["bullets_en"]))
        return f'''<a class="pcard" href="{href}" data-reveal="up">
  <div class="pc-img">{img(rel, imgkey, c["title"], sizes="(max-width:900px) 100vw, 50vw")}</div>
  <div class="pc-body"><span class="pc-tag">{t(c["tag"])}</span><h3 class="pc-title">{t(c["title"])}</h3>
    <p class="pc-text">{t(c["text"])}</p><ul class="checks">{lis}</ul>
    <span class="btn btn-cream">{t(c["cta"])}{ARROW}</span></div>
</a>'''
    paths = f'''<section class="sec light" id="caminos">
  {bars("r t")}
  <div class="wrap">
    {eyebrow(pth["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(pth["title"])}</h2>
    <div class="paths">{pcard("empresas", "fotos/parque/portico-calle", rel + "empresas/")}{pcard("inversores", "fotos/parque/aerea-lotes", rel + "inversores/")}</div>
  </div>
</section>'''

    pk = P["park"]
    drivers = "".join(f'<div class="driver" data-reveal="up" style="--d:{i*0.06:.2f}s"><b>{t(d)}</b><p>{tk(d, "d")}</p></div>' for i, d in enumerate(C["drivers"]))
    park = f'''<section class="sec paper" id="parque">
  <div class="wrap">
    <div class="split" style="align-items:end">
      <div>{eyebrow(pk["eyebrow"])}<h2 class="h2" data-reveal="up" style="margin-bottom:0">{t(pk["title"])}</h2></div>
      <div><p class="prose" data-reveal="up">{t(pk["text"])}</p>
        <div class="btns" data-reveal="up">{brochure_btn(rel, "btn btn-navy")}<a class="btn btn-ghost" href="{rel}empresas/#lotes">{pair("Ver lotes y normas", "See lots and zoning")}</a></div></div>
    </div>
    {masterplan_map(rel, pk["masterplan_cap"], {"es": "Masterplan del Parque Industrial Vaca Muerta con los 103 lotes por tipología", "en": "Parque Industrial Vaca Muerta masterplan with the 103 lots by type"})}
    <div class="drivers">{drivers}</div>
  </div>
</section>'''
    services = services_grid(rel, P["services"], cta_href=rel + "empresas/#ficha")
    location = location_section(rel, P["location"])

    gl = P["gallery"]
    gal = f'''<section class="sec paper" id="galeria">
  <div class="wrap">
    <div class="sec-head"><div>{eyebrow(gl["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(gl["title"])}</h2></div><p class="small" data-reveal="up">{t(gl["date"])}</p></div>
    {gallery(rel, C["gallery_parque"])}
    <div style="margin-top:clamp(40px,5vw,64px)">{tour360(rel)}</div>
    <div style="margin-top:clamp(40px,5vw,64px)">{video_cards(rel)}</div>
  </div>
</section>'''

    st = P["stage"]; it = st["intro"]
    stage = f'''<section class="sec navy" id="proxima-etapa">
  {bars("r b", "bc soft")}
  <div class="wrap stage">
    <div>
      <img class="sc-logo" src="{rel}logos/service-center-crema.png" alt="PIVM Service Center" width="150" height="122" data-reveal="up">
      <div><span class="tag tag-opp" data-reveal="up">{t(st["eyebrow"])}</span></div>
      <h2 class="h2" data-reveal="up" style="font-size:clamp(30px,3.6vw,50px)">{t(st["title"])}</h2>
      <p class="lead" data-reveal="up">{t(st["text"])}</p>
      <div class="btns" data-reveal="up"><a class="btn btn-cream" href="#contacto" data-preselect="service-center">{t(st["cta"])}{ARROW}</a></div>
    </div>
    <div class="stage-img" data-reveal="scale">{img(rel, "fotos/service-center/aerea", {"es": "Render del PIVM Service Center en el frente del parque", "en": "Render of PIVM Service Center at the park frontage"}, sizes="(max-width:900px) 100vw, 55vw")}</div>
  </div>
</section>'''
    parts = "".join(f'''<article class="part" data-reveal="up" style="--d:{i*0.08:.2f}s"><div class="pi">{img(rel, p["img"], p, sizes="(max-width:900px) 100vw, 50vw")}</div>
  <div class="pb"><h3>{t(p)}</h3><p>{tk(p, "d")}</p><ul class="checks">{"".join(f"<li>{pair(a,b)}</li>" for a,b in zip(p["facts_es"], p["facts_en"]))}</ul></div></article>''' for i, p in enumerate(st["parts"]))
    rb = st["rubros"]
    def rcol(k, cls):
        r = rb[k]
        return f'<div class="rub {cls}" data-reveal="up"><h3>{t(r["title"])}</h3><span class="sub">{t(r["sub"])}</span><ul>{"".join(f"<li>{pair(a,b)}</li>" for a,b in zip(r["items_es"], r["items_en"]))}</ul><p>{t(r["text"])}</p></div>'
    stage += f'''<section class="sec paper" id="service-center">
  <div class="wrap">
    <div class="sec-head"><div>{eyebrow(it["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(it["title"])}</h2></div><p class="lead" data-reveal="up">{t(it["text"])}</p></div>
    <div class="chips" style="margin:0 0 clamp(30px,4vw,48px)" data-reveal="up">
      <span class="chip">{pair("Bypass Ruta 7 – Ruta 17", "Route 7 – Route 17 bypass")}</span>
      <span class="chip">{pair("Ingreso al parque industrial", "Industrial park entrance")}</span>
      <span class="chip">{pair("6.000 m² de predio", "6,000 m² site")}</span>
      <span class="chip">{pair("A 1 km de Loma Campana", "1 km from Loma Campana")}</span>
    </div>
    <div class="parts">{parts}</div>
    <p class="small" style="margin-top:20px" data-reveal="up">{pair("Superficies y cantidades sujetas a proyecto definitivo.", "Areas and quantities subject to the final design.")}</p>
    <h3 class="h3" style="margin:clamp(50px,6vw,80px) 0 24px" data-reveal="up">{t(rb["title"])}</h3>
    <div class="rubros">{rcol("productos", "a")}{rcol("servicios", "b")}</div>
    <h3 class="h3" style="margin:clamp(50px,6vw,80px) 0 24px" data-reveal="up">{t(st["gallery"]["title"])}</h3>
    {gallery(rel, st["gallery"]["items"])}
  </div>
</section>'''

    pr = P["press"]
    press = f'''<section class="sec sand" id="prensa">
  <div class="wrap">
    <div class="sec-head"><div>{eyebrow(pr["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(pr["title"])}</h2></div></div>
    <div class="press-grid">{press_cards(sorted(C["press"], key=lambda x: x["date"], reverse=True)[:6])}</div>
  </div>
</section>'''
    return hero + stats_band() + paths + park + services + location + gal + stage + press + allies(rel) + contact(rel)


def fmt_date(s, lang):
    y, m, d = s.split("-")
    mes_es = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    mes_en = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{int(d)} {mes_es[int(m)-1]} {y}" if lang == "es" else f"{mes_en[int(m)-1]} {int(d)}, {y}"


WIX_MEDIA = "https://static.wixstatic.com/media/b9624d_"


def press_fig(p):
    """Foto de la nota. Se sirve desde el Wix de ZLT (la misma que usa ZLT-WEB-V2 en Novedades);
    si no carga, queda el fondo navy con las barritas de marca."""
    if not p.get("img"):
        return '<div class="pr-fig pr-empty" aria-hidden="true"></div>'
    mid, name = p["img"].split("|")
    u = lambda w, h, q: f"{WIX_MEDIA}{mid}/v1/fill/w_{w},h_{h},al_c,q_{q},enc_auto/{name}"
    alt = esc(f'{p["outlet"]} — {p["title"][:90]}')
    return (f'<div class="pr-fig"><img src="{u(760,428,82)}" srcset="{u(760,428,82)} 760w, {u(1140,642,78)} 1140w" '
            f'sizes="(max-width:600px) 92vw, (max-width:900px) 46vw, 31vw" width="760" height="428" loading="lazy" decoding="async" '
            f'referrerpolicy="no-referrer" alt="{alt}" onerror="this.remove()"></div>')


def press_cards(items):
    return "".join(
        f'<a class="pr" href="{esc(p["url"])}" target="_blank" rel="noopener" data-reveal="up" style="--d:{i*0.06:.2f}s">'
        f'{press_fig(p)}<div class="pr-body"><div class="meta"><b>{esc(p["outlet"])}</b><time datetime="{p["date"]}">{pair(fmt_date(p["date"],"es"), fmt_date(p["date"],"en"))}</time></div>'
        f'<h3>{esc(p["title"])}</h3><span class="go">{pair("Leer nota", "Read article")}{EXT}</span></div></a>'
        for i, p in enumerate(items))


def page_hero(rel, h, imgkey, alt, status=None):
    tag = f'<span class="tag tag-func" data-reveal="up">{t(status)}</span>' if status else ""
    cta = f'<div class="btns" data-reveal="up" style="--d:.22s"><a class="btn btn-cream" href="#contacto">{t(h["cta1"])}{ARROW}</a>{brochure_btn(rel, "btn btn-line")}</div>' if h.get("cta1") else ""
    return f'''<section class="phero">
  <div class="ph-img">{img(rel, imgkey, alt, eager=True)}</div>
  <div class="hero-inner">{tag}
    <div class="hero-eyebrow" data-reveal="up">{t(h["eyebrow"])}</div>
    <h1 class="hero-title" data-reveal="up" style="--d:.08s">{t(h["title"])}</h1>
    <p class="hero-lead" data-reveal="up" style="--d:.14s">{t(h["lead"])}</p>{cta}
  </div>
</section>'''


def page_empresas(rel):
    P = C["pages"]["empresas"]
    hero = page_hero(rel, P["hero"], "fotos/parque/portico-frente",
                     {"es": "Pórtico de acceso del Parque Industrial Vaca Muerta", "en": "Access gateway of Parque Industrial Vaca Muerta"},
                     status=C["pages"]["home"]["hero"]["status"])
    w = P["why"]
    why = f'''<section class="sec light" id="por-que">
  {bars("r t")}
  <div class="wrap">{eyebrow(w["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(w["title"])}</h2>
    <div class="cards3">{"".join(f'<div class="ncard" data-reveal="up" style="--d:{i*0.07:.2f}s"><span class="n">{c["n"]}</span><h3>{t(c)}</h3><p>{tk(c, "d")}</p></div>' for i, c in enumerate(w["items"]))}</div>
  </div>
</section>'''
    tc = P["tech"]
    def tnum(x):
        ne, nn = x["num"], x.get("num_en", x["num"])
        ue, un = x["unit"], x.get("unit_en", x["unit"])
        u = f'<small>{pair(ue, un)}</small>' if ue else ""
        return f'{pair(ne, nn)}{u}'
    cells = "".join(f'<div class="tcell" data-reveal="up" style="--d:{(i%3)*0.06:.2f}s"><div class="tnum">{tnum(x)}</div><p>{t(x)}</p></div>' for i, x in enumerate(C["tech"]))
    svl = "".join(f'<div class="svc-li" data-reveal="up"><span class="ico"><i style="-webkit-mask-image:url({rel}iconos/{s["icon"]}.png);mask-image:url({rel}iconos/{s["icon"]}.png)"></i></span>{t(s)}</div>' for s in C["services"])
    tech = f'''<section class="sec paper" id="ficha">
  <div class="wrap">{eyebrow(tc["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(tc["title"])}</h2>
    <div class="tech">{cells}</div>
    <div class="svc-list">{svl}</div>
  </div>
</section>'''
    lt = P["lots"]
    urban = "".join(f'<div class="ucard" data-reveal="up" style="--d:{i*0.06:.2f}s"><b>{t(u)}</b><ul>{"".join(f"<li>{pair(a,b)}</li>" for a,b in zip(u["items_es"], u["items_en"]))}</ul></div>' for i, u in enumerate(C["urban"]))
    lots = f'''<section class="sec sand" id="lotes">
  <div class="wrap">
    <div class="split" style="align-items:end">
      <div>{eyebrow(lt["eyebrow"])}<h2 class="h2" data-reveal="up" style="margin-bottom:0">{t(lt["title"])}</h2></div>
      <div><p class="prose" data-reveal="up">{t(lt["text"])}</p>
        <div class="btns" data-reveal="up"><a class="btn btn-navy" href="#contacto">{pair("Consultar disponibilidad", "Check availability")}{ARROW}</a></div></div>
    </div>
    {masterplan_map(rel, C["pages"]["home"]["park"]["masterplan_cap"], {"es": "Masterplan con los 103 lotes por tipología", "en": "Masterplan with the 103 lots by type"})}
    <h3 class="h3" style="margin-top:clamp(50px,6vw,80px)" data-reveal="up">{t(lt["urban_title"])}</h3>
    <div class="urban">{urban}</div>
  </div>
</section>'''
    sc = P["sectors"]
    sectors = f'''<section class="sec light" id="rubros">
  <div class="wrap">{eyebrow(sc["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(sc["title"])}</h2>
    <div class="chips" data-reveal="up">{"".join(f'<span class="chip">{pair(a,b)}</span>' for a,b in zip(sc["items_es"], sc["items_en"]))}</div>
    <p class="small" style="margin-top:22px" data-reveal="up">{pair("Usos permitidos: industriales, comercial minorista y mayorista con y sin depósito, y servicios.", "Permitted uses: industrial, retail and wholesale with or without storage, and services.")}</p>
  </div>
</section>'''
    tk_ = P["turnkey"]
    turnkey = f'''<section class="sec paper" id="naves">
  <div class="wrap"><div class="turnkey" data-reveal="up">
    <div class="tk-img">{img(rel, "fotos/renders/nave", {"es": "Render de nave industrial en el parque", "en": "Render of an industrial warehouse in the park"}, sizes="(max-width:900px) 100vw, 55vw")}</div>
    <div class="tk-body">{eyebrow(tk_["eyebrow"])}<h2 class="h2" style="font-size:clamp(28px,3.4vw,44px)">{t(tk_["title"])}</h2><p class="prose">{t(tk_["text"])}</p>
      <div class="btns"><a class="btn btn-cream" href="#contacto" data-preselect="nave">{t(tk_["cta"])}{ARROW}</a></div></div>
  </div></div>
</section>'''
    sp = P["steps"]
    steps = f'''<section class="sec light" id="como-empezar">
  <div class="wrap">{eyebrow(sp["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(sp["title"])}</h2>
    <div class="steps">{"".join(f'<div class="step" data-reveal="up" style="--d:{i*0.07:.2f}s"><h3>{t(s)}</h3><p>{tk(s, "d")}</p></div>' for i, s in enumerate(sp["items"]))}</div>
  </div>
</section>'''
    loc = location_section(rel, C["pages"]["home"]["location"], cls="paper")
    return hero + stats_band() + why + tech + lots + sectors + turnkey + steps + loc + allies(rel, "sand") + contact(rel, "empresa")


def page_inversores(rel):
    P = C["pages"]["inversores"]
    hero = page_hero(rel, P["hero"], "fotos/parque/aerea-avenida",
                     {"es": "Vista aérea del Parque Industrial Vaca Muerta", "en": "Aerial view of Parque Industrial Vaca Muerta"},
                     status=C["pages"]["home"]["hero"]["status"])
    pj = P["project"]
    tl = "".join(f'<div class="tl" data-reveal="up" style="--d:{i*0.08:.2f}s"><span class="d">{t(x["date"])}</span><h3>{t(x)}</h3><p>{tk(x, "d")}</p></div>' for i, x in enumerate(pj["timeline"]))
    project = f'''<section class="sec paper" id="proyecto">
  <div class="wrap">
    <div class="split">
      <div>{eyebrow(pj["eyebrow"])}<h2 class="h2" data-reveal="up">{t(pj["title"])}</h2><p class="prose" data-reveal="up">{t(pj["text"])}</p></div>
      <div class="stage-img" data-reveal="scale">{img(rel, "fotos/parque/portico-lateral", {"es": "Pórtico y cartel del parque", "en": "Park gateway and sign"}, sizes="(max-width:900px) 100vw, 55vw")}</div>
    </div>
    <div class="timeline">{tl}</div>
  </div>
</section>'''
    md = P["model"]
    model = f'''<section class="sec navy" id="modelo">
  {bars("r t", "bc soft")}
  <div class="wrap">{eyebrow(md["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(md["title"])}</h2>
    <div class="cards3">{"".join(f'<div class="ncard" data-reveal="up" style="--d:{i*0.07:.2f}s"><span class="n">{c["n"]}</span><h3>{t(c)}</h3><p>{tk(c, "d")}</p></div>' for i, c in enumerate(md["items"]))}</div>
    <p class="note" data-reveal="up">{t(md["note"])}</p>
    <div class="btns" data-reveal="up"><a class="btn btn-cream" href="#contacto">{t(P["hero"]["cta1"])}{ARROW}</a><a class="btn btn-line" href="{rel}empresas/#naves">{pair("Ver naves llave en mano", "See turnkey warehouses")}</a></div>
  </div>
</section>'''
    cx = P["context"]
    def dnum(x):
        return pair(x["num"], x.get("num_en", x["num"]))
    data = "".join(f'<div class="dcard" data-reveal="up" style="--d:{i*0.06:.2f}s"><div class="dnum">{dnum(x)}</div><span class="dunit">{t(x["unit"])}</span><p>{t(x)}</p></div>' for i, x in enumerate(cx["items"]))
    context = f'''<section class="sec dark" id="vaca-muerta">
  <div class="wrap">
    <div class="sec-head"><div>{eyebrow(cx["eyebrow"])}<h2 class="h2 wide" data-reveal="up">{t(cx["title"])}</h2></div><p class="lead" data-reveal="up">{t(cx["text"])}</p></div>
    <div class="data">{data}</div>
    <p class="small" style="margin-top:22px" data-reveal="up">{t(cx["source"])}</p>
  </div>
</section>'''
    drivers = "".join(f'<div class="driver" data-reveal="up" style="--d:{i*0.06:.2f}s"><b>{t(d)}</b><p>{tk(d, "d")}</p></div>' for i, d in enumerate(C["drivers"]))
    why = f'''<section class="sec light" id="por-que">
  {bars("r t")}
  <div class="wrap">{eyebrow({"es": "Key drivers", "en": "Key drivers"})}<h2 class="h2 wide" data-reveal="up">{pair("Por qué invertir en el parque", "Why invest in the park")}</h2>
    <div class="split" style="margin-top:20px"><figure class="mp" data-reveal="scale">{img(rel, "fotos/masterplan/entorno", {"es": "El parque en su entorno, junto a Añelo", "en": "The park in its setting, next to Añelo"}, sizes="(max-width:900px) 100vw, 50vw")}
      <figcaption>{pair("El parque en su entorno, junto a Añelo", "The park in its setting, next to Añelo")}</figcaption></figure>
      <div>{"".join(f'<div class="svc-li" style="margin:0 0 16px" data-reveal="up"><span class="ico"><i style="-webkit-mask-image:url({rel}iconos/{s["icon"]}.png);mask-image:url({rel}iconos/{s["icon"]}.png)"></i></span>{t(s)}</div>' for s in C["services"][:4])}
        <a class="link-arrow" href="{rel}empresas/#ficha" data-reveal="up">{pair("Ver ficha técnica completa", "See full technical specs")}{ARROW}</a></div></div>
    <div class="drivers">{drivers}</div>
  </div>
</section>'''
    z = P["zlt"]
    zlt = f'''<section class="sec sand" id="zlt">
  <div class="wrap"><div class="zltbox" data-reveal="up"><img src="{rel}logos/zlt-navy.png" alt="ZLT" width="160" height="72">
    <div>{eyebrow(z["eyebrow"])}<h2 class="h3" style="font-size:clamp(24px,2.6vw,34px);text-transform:uppercase;margin-bottom:14px">{t(z["title"])}</h2><p class="prose">{t(z["text"])}</p>
      <div class="btns"><a class="btn btn-ghost" href="{z["url"]}" target="_blank" rel="noopener">{t(z["cta"])}{EXT}</a></div></div></div></div>
</section>'''
    loc = location_section(rel, C["pages"]["home"]["location"], cls="paper")
    return hero + stats_band() + project + model + context + why + loc + zlt + allies(rel, "paper") + contact(rel, "inversor")


# ----------------------------------------------------------------- ensamblado
def jsonld():
    data = {
        "@context": "https://schema.org", "@type": "Place", "name": SITE["name"],
        "description": C["pages"]["home"]["description"]["es"], "url": SITE["url"],
        "telephone": "+" + SITE["phone_e164"], "email": SITE["email"],
        "address": {"@type": "PostalAddress", "streetAddress": "Ruta Provincial 17, km 5", "addressLocality": "Añelo",
                    "addressRegion": "Neuquén", "addressCountry": "AR"},
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def render(page, slug, body_fn):
    rel = "" if slug == "" else "../"
    meta = C["pages"][page]
    gilroy = ""
    if (ROOT / "fonts" / "gilroy-regular.woff2").exists():  # se activa solo si se cargan los archivos con licencia
        gilroy = f'<link rel="stylesheet" href="{rel}fonts/gilroy.css">'
    out = BASE
    rep = {
        "title_es": esc(meta["title"]["es"]), "title_en": esc(meta["title"]["en"]),
        "desc_es": esc(meta["description"]["es"]),
        "robots": "" if SITE["indexable"] else '<meta name="robots" content="noindex, nofollow">',
        "canonical": SITE["url"] + "/" + (slug + "/" if slug else ""),
        "og_image": SITE["url"] + "/iconos/web/og-pivm.jpg",
        "rel": rel, "v": VERSION, "gilroy": gilroy, "page": page,
        "jsonld": jsonld() if page == "home" else "",
        "header": header(rel, page), "main": body_fn(rel), "footer": footer(rel),
    }
    for k, v in rep.items():
        out = out.replace("{{" + k + "}}", v)
    assert "{{" not in out, re.findall(r"\{\{\w+\}\}", out)
    dest = ROOT / (slug + "/index.html" if slug else "index.html")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    print(f"  {dest.relative_to(ROOT)}  {len(out)/1024:.0f} KB")


def page_404():
    rel = "/"
    body = f'''<section class="nf"><div><div class="flogo" style="color:var(--cream);margin:0 auto 34px;width:180px">{logo(label=False)}</div>
<h1 class="hero-title" style="margin:0 auto;font-size:clamp(34px,5vw,60px)">{pair("Página no encontrada", "Page not found")}</h1>
<div class="btns" style="justify-content:center"><a class="btn btn-cream" href="/">{pair("Volver al inicio", "Back to home")}</a></div></div></section>'''
    out = BASE
    rep = {"title_es": "Página no encontrada · PIVM", "title_en": "Page not found · PIVM", "desc_es": "",
           "robots": '<meta name="robots" content="noindex">', "canonical": SITE["url"] + "/", "og_image": "",
           "rel": rel, "v": VERSION, "gilroy": "", "page": "404", "jsonld": "",
           "header": "", "main": body, "footer": ""}
    for k, v in rep.items():
        out = out.replace("{{" + k + "}}", v)
    (ROOT / "404.html").write_text(out, encoding="utf-8")


def extras():
    pages = ["", "empresas/", "inversores/"]
    if SITE["indexable"]:
        (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
    else:
        (ROOT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    urls = "".join(f"<url><loc>{SITE['url']}/{p}</loc></url>" for p in pages)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    # favicon: bloque del logo sobre navy
    (ROOT / "iconos" / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#2C3E50"/>'
        '<rect x="12" y="16" width="40" height="9" fill="#F5DEB1"/><rect x="12" y="29" width="26" height="9" fill="#F5DEB1"/>'
        '<rect x="12" y="42" width="34" height="9" fill="#F5DEB1"/></svg>')


if __name__ == "__main__":
    print("Generando sitio PIVM…")
    render("home", "", page_home)
    render("empresas", "empresas", page_empresas)
    render("inversores", "inversores", page_inversores)
    page_404(); extras()
    print("Listo.")
