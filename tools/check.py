#!/usr/bin/env python3
"""
Verificación obligatoria (sistema ZLT) con Playwright/Chromium a 1440, 768 y 390 px:
errores de JS, overflow horizontal, galerías íntegras, logos dentro de pantalla,
balance de <div> por sección y capturas por página (en tools/_capturas/).

    python3 -m http.server 8765 &   (desde la raíz del repo)
    python3 tools/check.py [--shots]
"""
import sys, re, json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8765/"
PAGES = ["", "empresas/", "inversores/"]
WIDTHS = [(1440, 900), (768, 1024), (390, 844)]
EXTERNAL_OK = ("ytimg.com", "youtube", "fonts.g", "wixstatic.com", ".mp4")  # sin red, o Chromium de prueba sin H.264
SHOTS = "--shots" in sys.argv
out = ROOT / "tools" / "_capturas"; out.mkdir(exist_ok=True)


def div_balance(html):
    bad = []
    for m in re.finditer(r'<section\b[^>]*?(?:id="([^"]*)")?[^>]*>(.*?)</section>', html, re.S):
        body = m.group(2)
        o, c = len(re.findall(r"<div\b", body)), len(re.findall(r"</div>", body))
        if o != c:
            bad.append((m.group(1) or "?", o, c))
    return bad


problems = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for page_path in PAGES:
        html = (ROOT / (page_path + "index.html")).read_text(encoding="utf-8")
        for s in div_balance(html):
            problems.append(f"{page_path or '/'}: <div> desbalanceado en sección {s}")
        for (w, h) in WIDTHS:
            ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(f"JS: {e}"))
            pg.on("console", lambda m: errs.append(f"console.{m.type}: {m.text}") if m.type == "error" and "Failed to load resource" not in m.text else None)
            pg.on("response", lambda r: errs.append(f"HTTP {r.status}: {r.url}") if r.status >= 400 else None)
            pg.on("requestfailed", lambda r: errs.append(f"falló: {r.url}") if not any(x in r.url for x in EXTERNAL_OK) else None)
            pg.goto(BASE + page_path, wait_until="networkidle")
            pg.add_style_tag(content="*{transition:none!important;animation:none!important}")
            pg.evaluate("document.querySelectorAll('[data-reveal]').forEach(e=>e.classList.add('revealed'))")
            # scroll completo para cargar lazy
            pg.evaluate("async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){scrollTo(0,y);await new Promise(r=>setTimeout(r,40))}scrollTo(0,0)}")
            pg.wait_for_timeout(400)
            r = pg.evaluate("""()=>{
              const W=document.documentElement.clientWidth, res={};
              res.overflow=document.documentElement.scrollWidth>W;
              res.wide=[...document.querySelectorAll('body *')].filter(e=>{const b=e.getBoundingClientRect();
                 return b.width>0 && (b.right>W+1||b.left<-1) && !e.closest('.mq,.gtrack,.hdr .menu,.mov,.skip,.sr-only,.bars,.wa-float')}).slice(0,6)
                 .map(e=>e.tagName+'.'+e.className+' '+Math.round(e.getBoundingClientRect().left)+'→'+Math.round(e.getBoundingClientRect().right));
              res.gal=[...document.querySelectorAll('[data-gallery]')].map(g=>({s:g.querySelectorAll('.gslide').length,d:g.querySelectorAll('.gdot').length,n:!!g.querySelector('.gnext')}));
              res.brokenImgs=[...document.images].filter(i=>i.complete && i.naturalWidth===0 && !i.src.includes('ytimg')).map(i=>i.src);
              res.logo=(()=>{const l=document.querySelector('.hlogo svg');if(!l)return null;const b=l.getBoundingClientRect();return [b.left,b.right,b.width,b.height]})();
              return res}""")
            tag = f"{page_path or '/'} @{w}"
            if r["overflow"]: problems.append(f"{tag}: overflow horizontal {r['wide']}")
            for g in r["gal"]:
                if g["s"] != g["d"] or not g["n"]: problems.append(f"{tag}: galería rota {g}")
            if r["brokenImgs"]: problems.append(f"{tag}: imágenes rotas {r['brokenImgs'][:4]}")
            if r["logo"] and (r["logo"][0] < 0 or r["logo"][1] > w): problems.append(f"{tag}: logo fuera de pantalla {r['logo']}")
            for e in errs: problems.append(f"{tag}: {e}")
            if SHOTS:
                name = (page_path.strip('/') or 'home') + f"_{w}"
                pg.screenshot(path=str(out / f"{name}.png"), full_page=True)
            ctx.close()
    b.close()

print("\n".join(problems) if problems else "OK — sin problemas")
