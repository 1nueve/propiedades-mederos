# Páginas por anuncio · Propiedades Mederos

Una página por propiedad y por grupo de Facebook, con tarjeta Open Graph (precio, foto con ▶️), video del reel, tarjeta de la asesora y botón a WhatsApp con mensaje prellenado. Se publica en https://mederos.1nueve.com con AWS Amplify (cada push a `main` despliega).

## Cómo se actualiza
1. Editar `propiedades.json` (datos de cada propiedad, sus grupos, `pixel_id`, asesora).
2. Poner las imágenes de cada propiedad en `sitio/<ref>/` (`og.jpg` 1200×630 para la tarjeta, `foto-1.jpg`…).
3. Ejecutar `python3 generar.py` → crea `sitio/<ref>/<grupo>/index.html`.
4. Commit y push a `main`.

Dirección de cada anuncio: `https://mederos.1nueve.com/<ref>/<grupo>/` (los UTM los agrega la página sola).
