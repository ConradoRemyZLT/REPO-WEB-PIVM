#!/usr/bin/env python3
"""
Procesa fotos, renders, logos, íconos y video para la web de PIVM.

Uso:
    SRC_ROOT="C:/Users/<usuario>/zt-soma.com/Parque Industrial Añelo - Documentos" \
    EXTRA_ROOT="./tools/_fuentes_extra" python3 tools/process_media.py [fotos|logos|iconos|video|todo]

Reglas (sistema ZLT):
  * Nunca deformar: si el encuadre no da, se recorta; jamás se estira.
  * exif_transpose antes de redimensionar, LANCZOS para escalar.
  * Fotos en WebP, tres anchos (srcset). Logos: se recolorean preservando el
    alfa, sin tocar la forma. PNG con alfa: nunca optimize=True.
  * Video: H.264 + AAC, faststart, sin cambiar fps de origen.
"""
import os, sys, json, subprocess, shutil
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(os.environ.get("SRC_ROOT", ""))
EXTRA = Path(os.environ.get("EXTRA_ROOT", ROOT / "tools" / "_fuentes_extra"))
CM = "Comunicación y Marketing"

# --------------------------------------------------------------------------
# Manifiesto: destino -> (origen, anchos, recorte opcional "x0,y0,x1,y1" en %)
# --------------------------------------------------------------------------
FOTOS_SEP26 = f"Ventas/Inmobiliarias/Fotos_y_Videos/Fotos_y_Videos_Avance_de_Obra/Septiembre_2026"
RENDERS = f"{CM}/Renders/Definitivos/Renders_01_09_25"
MASTER = f"{CM}/Renders/Render masterplan"

PHOTOS = {
    # Fotos reales — septiembre 2026 (obra finalizada)
    "fotos/parque/aerea-avenida":   (f"{FOTOS_SEP26}/ParqueIndustrialVM_010.jpg", [800, 1400, 2200]),
    "fotos/parque/aerea-lotes":     (f"{FOTOS_SEP26}/ParqueIndustrialVM_011.jpg", [800, 1400, 2200]),
    "fotos/parque/aerea-anelo":     (f"{FOTOS_SEP26}/ParqueIndustrialVM_005.jpg", [800, 1400, 2200]),
    "fotos/parque/aerea-portico":   (f"{FOTOS_SEP26}/ParqueIndustrialVM_014.jpg", [800, 1400, 2200]),
    "fotos/parque/aerea-horizonte": (f"{FOTOS_SEP26}/ParqueIndustrialVM_008.jpg", [800, 1400, 2200]),
    "fotos/parque/portico-frente":  (f"{FOTOS_SEP26}/ParqueIndustrialVM_033.jpg", [800, 1400, 2200]),
    "fotos/parque/portico-lateral": (f"{FOTOS_SEP26}/ParqueIndustrialVM_034.jpg", [800, 1400, 2200]),
    "fotos/parque/portico-calle":   (f"{FOTOS_SEP26}/ParqueIndustrialVM_069.jpg", [800, 1400, 2200]),
    # Renders definitivos (sept. 2025)
    "fotos/renders/aerea-parque":   (f"{RENDERS}/01.jpg", [800, 1400, 2000]),
    "fotos/renders/aerea-naves":    (f"{RENDERS}/03.jpg", [800, 1400, 2000]),
    "fotos/renders/calle-naves":    (f"{RENDERS}/06.jpg", [800, 1400, 2000]),
    "fotos/renders/ingreso-naves":  (f"{RENDERS}/07.jpg", [800, 1400, 2000]),
    "fotos/renders/avenida":        (f"{RENDERS}/08.jpg", [800, 1400, 2000]),
    "fotos/renders/nave":           (f"{RENDERS}/09.jpg", [800, 1400, 2000]),
    "fotos/renders/portico-noche":  (f"{RENDERS}/10-NOCTURNA2.jpg", [800, 1400, 2000]),
    # Masterplan
    "fotos/masterplan/masterplan":  (f"{MASTER}/Definitivos/Definitivo/Masterplan_Actualizado.jpg", [800, 1400, 1920]),
    "fotos/masterplan/entorno":     (f"{MASTER}/masterplan_pivm_en_entorno.jpg", [800, 1400, 1920]),
}

# Fotos que ya estaban procesadas en ZLT-WEB-PRESENTACIONES (1160 px de ancho):
# se reencodan sin agrandar.
EXTRA_PHOTOS = {
    "fotos/parque/portico-detalle-1": ("pivm-portico-1.webp", [800, 1160]),
    "fotos/parque/portico-detalle-2": ("pivm-portico-2.webp", [800, 1160]),
    "fotos/parque/letras-1":          ("pivm-letras-1.webp", [700, 1000]),
    "fotos/parque/letras-2":          ("pivm-letras-2.webp", [700, 1000]),
    "fotos/service-center/aerea":       ("sc-1.webp", [800, 1160]),
    "fotos/service-center/aerea-2":     ("sc-2.webp", [800, 1160]),
    "fotos/service-center/locales":     ("sc-3.webp", [800, 1160]),
    "fotos/service-center/explanada":   ("sc-4.webp", [800, 1160]),
    "fotos/service-center/estacion":    ("sc-5.webp", [800, 1160]),
    "fotos/service-center/boxes":       ("sc-6.webp", [800, 1160]),
}

NAVY = (44, 62, 80)       # #2C3E50
CREAM = (245, 222, 177)   # #F5DEB1
WHITE = (255, 255, 255)


def _open(p: Path) -> Image.Image:
    im = Image.open(p)
    im.draft("RGB", (4400, 4400))  # decodifica más rápido los JPG de 8K
    im = ImageOps.exif_transpose(im)
    return im.convert("RGB")


def save_variants(im: Image.Image, dest: str, widths, q=74):
    out = ROOT / dest
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = {"w": [], "ratio": round(im.width / im.height, 4)}
    for w in widths:
        if w > im.width:          # nunca agrandar
            w = im.width
        h = round(im.height * w / im.width)
        r = im.resize((w, h), Image.LANCZOS)
        r.save(f"{out}-{w}.webp", "WEBP", quality=q, method=6)
        meta["w"].append(w)
    meta["w"] = sorted(set(meta["w"]))
    return meta


def trim_white(im, pad=0, thr=246):
    """Recorta márgenes blancos (no deforma: es un recorte)."""
    from PIL import ImageChops
    g = im.convert("L").point(lambda v: 255 if v < thr else 0)
    bbox = g.getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def do_photos():
    manifest = {}
    for dest, (src, widths) in PHOTOS.items():
        p = SRC / src
        if not p.exists():
            print("  falta:", p); continue
        im = _open(p)
        if dest.endswith("masterplan/masterplan"):
            im = trim_white(im, pad=40)   # el render viene con mucho margen blanco
        manifest[dest] = save_variants(im, dest, widths)
        print("  ok", dest, manifest[dest])
    for dest, (src, widths) in EXTRA_PHOTOS.items():
        p = EXTRA / src
        if not p.exists():
            print("  falta:", p); continue
        im = _open(p)
        manifest[dest] = save_variants(im, dest, widths, q=80)
        print("  ok", dest, manifest[dest])
    prev = ROOT / "fotos" / "manifest.json"
    old = json.loads(prev.read_text()) if prev.exists() else {}
    old.update(manifest)
    prev.write_text(json.dumps(old, indent=1, ensure_ascii=False))


def recolor(im: Image.Image, dark, light=None):
    """Recolorea un logo monocromo preservando el alfa.
    Si light es None, todo el logo pasa a `dark`. Si no, se interpola por
    luminancia (para logos con texto calado en blanco, como el del Service Center)."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if light is None:
                px[x, y] = (*dark, a)
            else:
                t = (r * .299 + g * .587 + b * .114) / 255  # 0 = negro, 1 = blanco
                c = tuple(round(dark[i] * (1 - t) + light[i] * t) for i in range(3))
                px[x, y] = (*c, a)
    return im


def trim(im: Image.Image, pad=0):
    """Recorta solo el margen 100% transparente (no toca el diseño)."""
    bbox = im.getchannel("A").getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def do_logos():
    logos = ROOT / "logos"
    # ZLT (blanco en origen) -> navy y blanco
    z = Image.open(EXTRA / "zlt-blanco.webp")
    trim(recolor(z, NAVY)).save(logos / "zlt-navy.png")
    trim(recolor(z, WHITE)).save(logos / "zlt-blanco.png")
    # Service Center (#000 + texto calado en blanco)
    sc = Image.open(EXTRA / "sc-logo.webp")
    trim(recolor(sc, NAVY, WHITE)).save(logos / "service-center-navy.png")
    trim(recolor(sc, CREAM, NAVY)).save(logos / "service-center-crema.png")
    # Acompañan (blancos en origen) -> navy y blanco
    acc = ROOT / "logos" / "acompanan"
    for name in ["soldini-stock", "avalian", "las-taperitas", "grupo-flecha", "la-segunda", "mbc", "qala"]:
        im = Image.open(EXTRA / f"acc-{name}.webp")
        trim(recolor(im, NAVY)).save(acc / f"{name}-navy.png")
        trim(recolor(im, WHITE)).save(acc / f"{name}-blanco.png")
    print("  logos ok")


ICONOS = {  # iconografía oficial PIVM (manual de marca), blanca 500x500
    "agua": "27.png", "fibra": "28.png", "asfalto": "29.png", "alumbrado": "30.png",
    "electricidad": "31.png", "cloacas": "32.png", "seguridad": "33.png", "cordon": "34.png",
}


def do_iconos():
    src = SRC / CM / "Manual_de_Marca_PIVM" / "Iconografia_pivm_png"
    for name, f in ICONOS.items():
        im = Image.open(src / f).convert("RGBA")
        im = trim(im, pad=6)
        side = max(im.size)
        sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
        sq = sq.resize((192, 192), Image.LANCZOS)
        recolor(sq, WHITE).save(ROOT / "iconos" / f"{name}.png")
    print("  íconos ok")


def ffmpeg(*args):
    cmd = ["ffmpeg", "-v", "error", "-y", *args]
    print("  $", " ".join(cmd[:12]), "…")
    subprocess.run(cmd, check=True)


def do_video():
    base = SRC / CM / "Fotos_y_Videos_Avance_De_Obra/2026/09 Septiembte Fotos y Videos Parque Industrial Vaca Muerta"
    h = base / "01-ZLT Parque Industrial 16-9.mp4"
    v = base / "01-ZLT Parque Industrial 9-16.mp4"
    out = ROOT / "videos"
    # 16:9 escritorio — 1920x1080 (HD), sin tocar fps
    ffmpeg("-i", str(h), "-vf", "scale=1920:-2:flags=lanczos", "-c:v", "libx264", "-preset", "slow",
           "-crf", "25", "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "112k",
           "-movflags", "+faststart", str(out / "pivm-hero-16x9.mp4"))
    # 9:16 móvil — 1080x1920 (HD)
    ffmpeg("-i", str(v), "-vf", "scale=1080:-2:flags=lanczos", "-c:v", "libx264", "-preset", "slow",
           "-crf", "26", "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "112k",
           "-movflags", "+faststart", str(out / "pivm-hero-9x16.mp4"))
    # pósters (primer cuadro visible mientras carga)
    ffmpeg("-ss", "0.4", "-i", str(h), "-frames:v", "1", "-q:v", "3", str(out / "pivm-hero-16x9.jpg"))
    ffmpeg("-ss", "0.4", "-i", str(v), "-frames:v", "1", "-q:v", "3", str(out / "pivm-hero-9x16.jpg"))
    print("  video ok")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "todo"
    if what in ("fotos", "todo"): do_photos()
    if what in ("logos", "todo"): do_logos()
    if what in ("iconos", "todo"): do_iconos()
    if what in ("video", "todo"): do_video()
