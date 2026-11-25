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
SLUG_SITIO = "ver"
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
    if p.get("precio_prefijo"):  # p. ej. "Desde"
        precio = f"{p['precio_prefijo']} {precio}"
    og_title = f"{'Renta' if renta else 'Venta'} {precio[0].lower() + precio[1:] if p.get('precio_prefijo') else precio}{'/mes' if renta else ''} · {p['tipo']} en {p['zona']}"
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
    # una página por grupo + la página "ver" que abre el feed del home
    for gslug, gnombre in list(p["grupos"].items()) + [(SLUG_SITIO, None)]:
        url = f"{dom}/{ref}/{gslug}/"
        if gnombre is None:  # página del sitio (desde el home)
            gnombre = "Sitio web"
            msg = (f"Hola, vi en moby.lat la {p['tipo'].lower()} en {p['zona']} "
                   f"(Ref. {p['id']}). ¿Me das más información?\n{url}")
            wa = f"https://wa.me/{cfg['whatsapp']}?text={up.quote(msg)}"
            if p.get("wa_corto_base") and cfg.get("wa_sitio_corto"):  # short.io <base>/ver, si ya se creó
                wa = f"{p['wa_corto_base'].rstrip('/')}/{SLUG_SITIO}"
        else:
            msg = (f"Hola, vi en Facebook el anuncio de {p['tipo']} en {p['zona']} "
                   f"(Ref. {p['id']}, grupo: {gnombre}). ¿Me das más información?\n{url}")
            wa = f"https://wa.me/{cfg['whatsapp']}?text={up.quote(msg)}"
            if p.get("wa_corto_base"):  # botón por short.io (cuenta el clic a WhatsApp)
                wa = f"{p['wa_corto_base'].rstrip('/')}/{gslug}"
        if cfg.get("shortio_dominio") and gslug != SLUG_SITIO:  # enlace corto que se publica en el grupo (cuenta el clic al anuncio)
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
    print(f"{p['id']}: {len(p['grupos'])} páginas + /{SLUG_SITIO}/  ->  {dom}/{ref}/<grupo>/")
print(f"Total: {total} páginas")
if filas:
    import csv
    with open(BASE / "shortio-anuncios.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["original_url", "path", "title", "tags", "enlace_corto"]); w.writerows(filas)
    print(f"shortio-anuncios.csv: {len(filas)} enlaces de anuncio")

# ---------- Home: feed con todas las propiedades disponibles ----------
def home():
    e = html.escape
    disp = [p for p in reversed(props) if p.get("disponible", True)]
    tarjetas = []
    for p in disp:
        ref = p["id"].lower()
        renta = "renta" in p["operacion"].lower()
        precio = "${:,.0f}".format(p["precio"])
        pre = f'<small>{e(p["precio_prefijo"])}</small> ' if p.get("precio_prefijo") else ""
        medio = "▶ Video" if p.get("video") else f'{len(p.get("carrusel", []))} fotos'
        dato = p["datos"][0] if p.get("datos") else ""
        tarjetas.append(
            f'<li data-op="{"renta" if renta else "venta"}"><a class="card" href="{ref}/{SLUG_SITIO}/">'
            f'<div class="ph"><img src="{ref}/tarjeta.jpg" alt="{e(p["tipo"])} en {e(p["zona"])}" loading="lazy" width="800" height="600">'
            f'<span class="op {"r" if renta else "v"}">{"Renta" if renta else "Venta"}</span><span class="md">{medio}</span></div>'
            f'<div class="bd"><p class="pr">{pre}{precio}{"<small> / mes</small>" if renta else ""}</p>'
            f'<h2>{e(p["tipo"])} en {e(p["zona"])}</h2><p class="dt">{e(dato)}</p><p class="rf">Ref. {e(p["id"])}</p></div></a></li>')
    n_v = sum(1 for p in disp if "renta" not in p["operacion"].lower())
    msg = "Hola, vi el sitio de Propiedades Mederos en moby.lat. ¿Me pueden ayudar a encontrar una propiedad?"
    wa = f"https://wa.me/{cfg['whatsapp']}?text={up.quote(msg)}"
    foto = f'<img src="{e(a["foto"])}" alt="" width="56" height="56">' if a and a.get("foto") else ""
    out = (BASE / "plantilla-home.html").read_text(encoding="utf-8")
    for k, v in {"tarjetas": "\n".join(tarjetas), "n": len(disp), "n_venta": n_v, "n_renta": len(disp) - n_v,
                 "wa": e(wa), "foto": foto, "asesora": e(a["nombre"]) if a else "", "puesto": e(a["puesto"]) if a else "",
                 "dominio": e(dom)}.items():
        out = out.replace("{{" + k + "}}", str(v))
    assert "{{" not in out
    (BASE / "sitio" / "index.html").write_text(out, encoding="utf-8")
    print(f"Home: {len(disp)} propiedades en el feed")
home()
