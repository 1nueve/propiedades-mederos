#!/usr/bin/env python3
"""Genera sitio/<ref>/tarjeta.jpg (800x600) para la tarjeta del feed del home.
Uso: python3 tarjeta.py R5 sitio/r5/fotos/01.jpg"""
import sys
from pathlib import Path
from PIL import Image, ImageOps
ref, foto = sys.argv[1], sys.argv[2]
W, H = 800, 600
src = ImageOps.exif_transpose(Image.open(foto)).convert("RGB")
s = max(W / src.width, H / src.height)
im = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
x = (im.width - W) // 2; y = int((im.height - H) * 0.4)
out = Path(__file__).parent / "sitio" / ref.lower() / "tarjeta.jpg"
im.crop((x, y, x + W, y + H)).save(out, quality=82, optimize=True, progressive=True); print("OK", out)
