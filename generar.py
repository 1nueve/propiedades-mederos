#!/usr/bin/env python3
"""Genera una página por propiedad y por grupo: salida/<ref>/<grupo>/index.html
Uso: python3 generar.py   (lee propiedades.json; la imagen og.jpg de cada propiedad va en salida/<ref>/og.jpg)
"""
import json, html, os, urllib.parse as up
from pathlib import Path

BASE = Path(__file__).parent
cfg_all = json.loads((BASE / "propiedades.json").read_text(encoding="utf-8"))
cfg, props = cfg_all["config"], cfg_all["propiedades"]
tpl = (BASE / "plantilla.html").read_text(encoding="utf-8")
BLOQUE_VIDEO = (BASE / "bloque-video.html").read_text(encoding="utf-8")
BLOQUE_CARRUSEL = (BASE / "bloque-carrusel.html").read_text(encoding="utf-8")
dom = cfg["dominio"].rstrip("/")
a = cfg.get("asesora")
def tarjeta_asesora():
    if not a: return ""
    e = html.escape
    ini = "".join(w[0] for w in a["nombre"].split()[:2]).upper()
    foto = (f'<img src="../../{e(a["foto"])}" alt="{e(a["nombre"])}" width="72" height="72">' if a.get("foto")
            else f'<span class="ini" aria-hidden="true">{e(ini)}</span>')
    return (f'<section class="asesora">{foto}<div><b>{e(a["nombre"])}</b>'
            f'<span class="puesto">{e(a["puesto"])}</span><p>{e(a["bio"])}</p></div></section>')

def render(d):
    out = tpl
    for k, v in d.items():
        out = out.replace("{{" + k + "}}", str(v))
    assert "{{" not in out, "falta un dato en la plantilla"
    return out

total = 0
filas = []
for p in props:
    ref = p["id"].lower()
    renta = "renta" in p["operacion"].lower()
    precio = "${:,.0f}".format(p["precio"])
    og_title = f"{'Renta' if renta else 'Venta'} {precio}{'/mes' if renta else ''} · {p['tipo']} en {p['zona']}"
    if p.get("video"):
        og_desc = f"▶️ {p['titulo']}. {p['descripcion']}. Mira el video y pide informes por WhatsApp."
    else:
        og_desc = f"📷 {p['titulo']}. {p['descripcion']}. Mira las {len(p['carrusel'])} fotos y pide informes por WhatsApp."
    e = html.escape
    if p.get("video"):
        medio = (BLOQUE_VIDEO.replace("{{video_enc}}", up.quote(p["video"], safe=""))
                             .replace("{{video}}", e(p["video"])))
    else:
        fotos_c = p["carrusel"]
        imgs = "".join(f'<img src="../{e(f)}" alt="Foto {k+1} de {e(p["tipo"])} en {e(p["zona"])}"' + (' loading="lazy"' if k else "") + ">" for k, f in enumerate(fotos_c))
        medio = BLOQUE_CARRUSEL.replace("{{imgs}}", imgs).replace("{{n}}", str(len(fotos_c)))
    campaign = f"{p['id']}-{p['slug']}"
    for gslug, gnombre in p["grupos"].items():
        url = f"{dom}/{ref}/{gslug}/"
        msg = (f"Hola, vi en Facebook el anuncio de {p['tipo']} en {p['zona']} "
               f"(Ref. {p['id']}, grupo: {gnombre}). ¿Me das más información?\n{url}")
        wa = f"https://wa.me/{cfg['whatsapp']}?text={up.quote(msg)}"
        if p.get("wa_corto_base"):  # botón por short.io (cuenta el clic a WhatsApp)
            wa = f"{p['wa_corto_base'].rstrip('/')}/{gslug}"
        if cfg.get("shortio_dominio"):  # enlace corto que se publica en el grupo (cuenta el clic al anuncio)
            filas.append([url, f"{ref}/{gslug}", f"Anuncio {p['id']} · {gnombre}", f"anuncio,{p['id']}", f"{cfg['shortio_dominio']}/{ref}/{gslug}"])
        e = html.escape
        page = render({
            "og_title": e(og_title), "og_desc": e(og_desc), "url": e(url),
            "og_image": e(f"{dom}/{ref}/og.jpg"), "tipo": e(p["tipo"]), "zona": e(p["zona"]),
            "pixel_id": e(cfg["pixel_id"]), "ref": e(p["id"]), "grupo_nombre": e(gnombre).replace('"', "&quot;"),
            "grupo_slug": gslug, "utm_source": cfg["utm_source"], "utm_medium": p["utm_medium"],
            "utm_campaign": campaign, "wa_url": e(wa), "segundos": int(cfg["segundos_redireccion"]),
            "operacion": e(p["operacion"]), "precio_txt": precio,
            "precio_sufijo": " <small>/ mes</small>" if renta else "",
            "titulo": e(p["titulo"]), "medio": medio,
            "chips": "".join(f"<li>{e(c)}</li>" for c in p["datos"]),
            "texto": e(p["texto"]), "asesora": tarjeta_asesora(),
            "fotos": ('<div class="fotos">' + "".join(f'<img src="../{e(f["archivo"])}" alt="{e(f["alt"])}" loading="lazy">' for f in p.get("fotos", [])) + "</div>") if p.get("fotos") else "", "descripcion": e(p["descripcion"]),
        })
        dest = BASE / "sitio" / ref / gslug
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(page, encoding="utf-8")
        total += 1
    print(f"{p['id']}: {len(p['grupos'])} páginas  ->  {dom}/{ref}/<grupo>/")
print(f"Total: {total} páginas")
if filas:
    import csv
    with open(BASE / "shortio-anuncios.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["original_url", "path", "title", "tags", "enlace_corto"]); w.writerows(filas)
    print(f"shortio-anuncios.csv: {len(filas)} enlaces de anuncio")
