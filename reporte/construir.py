#!/usr/bin/env python3
"""Arma el reporte público del cliente en sitio/<carpeta>/.

Uso:
  python3 reporte/construir.py [--publicaciones CSV] [--estadisticas CSV] [--fecha ISO]

- Siempre regenera sitio/<carpeta>/index.html a partir de reporte/tablero.html
  (la misma página del tablero de Claude) y reporte/envoltura.html.
- Si se pasan CSV, los copia a la carpeta (solo con las columnas que usa la página)
  y escribe actualizado.json con la fecha.
Luego: commit y push a main (Amplify despliega en ~3 min).
"""
import argparse, csv, json, pathlib, datetime, shutil

AQUI = pathlib.Path(__file__).resolve().parent
CARPETA = "reporte"  # la página lleva noindex
DESTINO = AQUI.parent / "sitio" / CARPETA

COLS_PUB = ["n", "fecha", "hora", "id", "propiedad", "tipo", "formato", "grupo",
            "tipo_grupo", "miembros", "estado", "enlace_post", "clics"]
COLS_EST = ["tipo", "nombre", "clics"]


def copiar(origen, destino, cols):
    with open(origen, newline="", encoding="utf-8-sig") as f:
        filas = list(csv.DictReader(f))
    faltan = [c for c in cols if filas and c not in filas[0]]
    if faltan:
        raise SystemExit(f"{origen}: faltan columnas {faltan}")
    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    print(f"{destino.name}: {len(filas)} filas")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--publicaciones")
    ap.add_argument("--estadisticas")
    ap.add_argument("--fecha", help="ISO 8601; por defecto ahora (UTC)")
    a = ap.parse_args()

    DESTINO.mkdir(parents=True, exist_ok=True)
    tablero = (AQUI / "tablero.html").read_text(encoding="utf-8")
    tablero = tablero.replace('<meta name="dash-one-writer">', "")
    html = (AQUI / "envoltura.html").read_text(encoding="utf-8").replace("<!--TABLERO-->", tablero)
    (DESTINO / "index.html").write_text(html, encoding="utf-8")
    shutil.copy(AQUI / "moby-wordmark.png", DESTINO / "moby-wordmark.png")

    cambio = False
    if a.publicaciones:
        copiar(a.publicaciones, DESTINO / "publicaciones.csv", COLS_PUB); cambio = True
    if a.estadisticas:
        copiar(a.estadisticas, DESTINO / "estadisticas.csv", COLS_EST); cambio = True
    if cambio or a.fecha:
        at = a.fecha or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        (DESTINO / "actualizado.json").write_text(json.dumps({"at": at}) + "\n", encoding="utf-8")
    print(f"Listo: sitio/{CARPETA}/  →  https://mederos.moby.lat/{CARPETA}/")


if __name__ == "__main__":
    main()
