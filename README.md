# Páginas por anuncio · Propiedades Mederos

Una página por propiedad y por grupo de Facebook, con tarjeta Open Graph (precio, foto con ▶️), video del reel, tarjeta de la asesora y botón a WhatsApp con mensaje prellenado. Se publica en https://mederos.moby.lat con AWS Amplify (cada push a `main` despliega).

## Cómo se actualiza
1. Editar `propiedades.json` (datos de cada propiedad, sus grupos, `pixel_id`, asesora).
2. Poner las imágenes de cada propiedad en `sitio/<ref>/` (`og.jpg` 1200×630 para la tarjeta, `foto-1.jpg`…).
3. Ejecutar `python3 generar.py` → crea `sitio/<ref>/<grupo>/index.html`.
4. Commit y push a `main`.

Dirección de cada anuncio: `https://mederos.moby.lat/<ref>/<grupo>/` (los UTM los agrega la página sola).

## Reporte de avance para el cliente
Copia pública del tablero de publicaciones, sin cuenta de Claude: `https://mederos.moby.lat/reporte/` (sin enlace desde el sitio y con `noindex`).

- `reporte/tablero.html`: la página del tablero (misma que el artifact de Claude).
- `reporte/envoltura.html`: estilos y un mini-entorno que carga los CSV de la carpeta.
- Para actualizar tras cada tanda:
  `python3 reporte/construir.py --publicaciones publicaciones-collage.csv --estadisticas estadisticas-real.csv`
  y luego commit y push a `main`. Solo se publican las columnas que usa la página.
