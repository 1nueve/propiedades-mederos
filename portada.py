#!/usr/bin/env python3
"""Genera sitio/<ref>/og.jpg (1200x630) para la tarjeta de Facebook.
Uso: python3 portada.py R5 sitio/r5/fotos/01.jpg   (requiere Pillow y la fuente Inter)"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
BASE = Path(__file__).parent
ref, foto = sys.argv[1], sys.argv[2]
p = next(x for x in json.loads((BASE / "propiedades.json").read_text(encoding="utf-8"))["propiedades"] if x["id"] == ref)
F = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
def font(w, s): return ImageFont.truetype(F % w, s)
W, H = 1200, 630
src = Image.open(foto).convert("RGB")
s = max(W / src.width, H / src.height)
im = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
x = (im.width - W) // 2; y = int((im.height - H) * 0.4)
im = im.crop((x, y, x + W, y + H)).filter(ImageFilter.UnsharpMask(2, 50, 2))
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
for i in range(760):
    d.line([(i, 0), (i, H)], fill=(10, 30, 50, int(225 * (1 - i / 760) ** 1.2)))
im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB"); d = ImageDraw.Draw(im)
renta = "renta" in p["operacion"].lower()
precio = "${:,.0f}".format(p["precio"]) + ("/mes" if renta else "")
d.text((60, 60), "PROPIEDADES MEDEROS", font=font("SemiBold", 28), fill="#d6e6f3")
d.text((60, 130), "Renta" if renta else "Venta", font=font("SemiBold", 40), fill="white")
d.text((60, 180), precio, font=font("ExtraBold", 86 if len(precio) < 13 else 72), fill="white")
d.text((60, 295), p["tipo"] + " en", font=font("Medium", 36), fill="white")
d.text((60, 340), p["zona"], font=font("Bold", 40), fill="white")
y = 410
for linea in p.get("datos", [])[:2]:
    d.text((60, y), linea, font=font("Regular", 28), fill="#d6e6f3"); y += 40
if p.get("video"):
    cx, cy, r = 1030, 470, 95
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 235))
    im = Image.alpha_composite(im.convert("RGBA"), sh).convert("RGB"); d = ImageDraw.Draw(im)
    d.polygon([(cx - 30, cy - 48), (cx - 30, cy + 48), (cx + 52, cy)], fill="#123b5c")
else:
    n = len(p.get("carrusel", []))
    etiqueta = f"{n} fotos  ›"
    f = font("Bold", 34); w = d.textlength(etiqueta, font=f)
    d.rounded_rectangle([W - 60 - w - 40, H - 120, W - 60, H - 60], radius=30, fill="white")
    d.text((W - 60 - w - 20, H - 111), etiqueta, font=f, fill="#123b5c")
out = BASE / "sitio" / ref.lower() / "og.jpg"
im.save(out, quality=88); print("OK", out)
