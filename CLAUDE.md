# pivm-web

Web nueva del Parque Industrial Vaca Muerta (ver `LEEME.txt` y `README.md`).
Sitio estático multipágina generado por `build.py` desde `content.json`.

## Reglas
- Todo texto nuevo va en `content.json`, en pares `es` / `en`. Después: `python3 build.py`.
- Nunca editar a mano `index.html`, `empresas/`, `inversores/`: los pisa el build.
- Verificar antes de entregar: `python3 -m http.server 8765` + `python3 tools/check.py --shots` (1440/768/390).
- Marca PIVM: navy #2C3E50, crema #F5DEB1, gris #646464, blanco #FDFDFD, Gilroy (respaldo Urbanist).
- Fotos: nunca deformar; WebP en 3 anchos vía `tools/process_media.py`. Logos: recolorear preservando alfa.
- PIVM es venta de lotes escriturables con posesión inmediata + cotización opcional de nave llave en mano.
  No hay renta administrada. No publicar cifras de lotes/naves entregados u operativos.
- Service Center = sección `#proxima-etapa` de la home (no página propia). Sin página de prensa.
- Contacto: +54 9 3413 16-5100 · vmindustria_info@somoszlt.com.
- Login temporal: `gate.js` (copia del de ZLT-WEB-V2, mismos usuarios). No modificarlo; si cambian los usuarios, copiarlo de nuevo.
- El sitio está en `noindex` hasta la mudanza (`site.indexable` en `content.json`).
