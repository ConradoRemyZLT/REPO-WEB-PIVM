# REPO WEB PIVM — Parque Industrial Vaca Muerta

Sitio estático multipágina, bilingüe (ES/EN), con la marca PIVM sobre la estructura de las webs de ZLT.
Se publica tal cual en GitHub Pages (o cualquier hosting estático). No necesita build para servirse: los HTML ya están generados.

## Páginas

| URL | Para quién | Contenido |
|---|---|---|
| `/` | General | Video hero (sept. 2026), datos clave, los dos caminos (empresas / inversores), masterplan, servicios, ubicación, galería + recorrido 360° (Kuula 7HcZL), próxima etapa (Service Center: zona comercial, estación con parador, rubros aptos, renders), prensa (últimas 6 notas, enlazan al medio), acompañan, contacto |
| `/empresas/` | Empresas que quieren operar | Por qué el parque, ficha técnica de servicios, lotes + indicadores urbanísticos, rubros, naves llave en mano, cómo empezar |
| `/inversores/` | Inversores | El proyecto + hitos, modelo (lote → nave → alquiler por cuenta propia), contexto Vaca Muerta, key drivers, ZLT |

## Cómo editar

1. **Textos y datos:** todo está en `content.json`, en pares `es` / `en`. No escribir textos en los HTML.
2. Regenerar: `python3 build.py`
3. Verificar: `python3 -m http.server 8765` y en otra terminal `python3 tools/check.py --shots`
   (1440 / 768 / 390 px: errores de JS, overflow, galerías, imágenes rotas, logo, balance de `<div>`).

## Carpetas

```
index.html, empresas/, inversores/, 404.html   ← generados por build.py
content.json      textos ES/EN y datos (fuente de verdad)
build.py          generador
html/base.html    esqueleto (head, metas, scripts)
css/site.css      sistema visual (tokens de marca PIVM al inicio)
js/site.js        idioma, menú, video, galerías, YouTube, formulario
fotos/            WebP en 3 anchos (srcset) + manifest.json
logos/            pivm-logo.svg (vector, toma el color por CSS), service center, ZLT, acompanan/
iconos/           iconografía oficial PIVM (manual de marca) + favicon
brochures/        Brochure_Digital_PIVM_2026.pdf (vigente)
videos/           hero 16:9 y 9:16 (+ pósters)
fonts/            Urbanist (OFL) como respaldo de Gilroy
links/            planillas CSV: videos y 360°, contacto y redes, prensa, ubicación
tools/            process_media.py (procesa fotos/logos/video desde SharePoint) y check.py
```

## Decisiones

- **Tipografía:** se declara Gilroy (marca). Como no tiene licencia web, el sitio cae a **Urbanist** (OFL), la más cercana. Si se consigue licencia web de Gilroy: copiar `gilroy-regular.woff2` (y pesos) + un `fonts/gilroy.css` con los `@font-face` y `build.py` lo enlaza solo.
- **Paleta:** navy `#2C3E50`, crema `#F5DEB1` (Pantone 7506 C), gris `#646464`, blanco `#FDFDFD` — manual de marca 2026. Los verdes/azules de estado (“Listo para operar”, “Próxima etapa”) son los del sistema ZLT.
- **Recurso gráfico:** las “barritas” en escalera del brochure (`.bars`) y el bloque del logo como marcador de eyebrows.
- **Formulario:** sin backend. Arma el mensaje y lo abre en WhatsApp (+54 9 3413 16-5100) o en el mail (vmindustria_info@somoszlt.com).
- **Indexación:** `"indexable": false` en `content.json` → `noindex` + `robots.txt` que bloquea. Cambiar a `true` el día de la mudanza del dominio (hoy vacamuertaindustria.com está en Wix).
- **Video hero:** el último editado (01-ZLT Parque Industrial, sept. 2026), 16:9 en escritorio y 9:16 en celular, muteado con botón de sonido. Se mantienen los fps de origen.
- **Mapa:** esquema propio en SVG (posiciones reales, distancias por ruta del brochure) + botón “Cómo llegar” a Google Maps. Sin tiles de terceros con licencia.
- **Estructura pensada para durar:** el Service Center es una sección de la home (`#proxima-etapa`), no una página: cuando se termine esa etapa se reescribe o se quita la sección sin romper URLs. No hay página de prensa; la home muestra las últimas 6 notas (lista completa en `links/notas-de-prensa.csv`).
- **Fotos de prensa:** cada nota usa la misma foto que ZLT-WEB-V2 (Novedades), servida desde el Wix de ZLT (`static.wixstatic.com`, campo `img` de cada nota en `content.json`: `mediaId|nombre`). Si una no carga, la tarjeta muestra el fondo navy con el logo. Si algún día se da de baja el Wix de ZLT, hay que bajar esas fotos a `fotos/prensa/`.
- **Masterplan interactivo:** los 103 lotes se pintan por tipología (1.350 · 2.166 · 2.566 · 3.155 · más de 4.000 m² · macrolote · otras medidas) y al pasar el mouse (o tocar, en celular) muestran lote, superficie, medidas, FOS y FOT (índice y m²). Los datos están en `lotes.json` (superficie, frente y fondo de la lista de precios del 16/12/2025, **sin precios**; el campo `fuente` indica el origen de cada lote). Los polígonos se trazaron sobre la imagen del masterplan (1919 px): si cambia esa imagen, hay que rehacerlos.
- **Formulario:** deslizante "Soy empresa / Soy inversor" que filtra las opciones de "¿Qué estás buscando?" y cambia el texto de ayuda; en /inversores/ arranca en inversor.
- **PIVM es venta de lotes** (escriturables, con posesión inmediata), con cotización opcional de nave llave en mano. No hay renta administrada; la comercialización de la nave es del inversor. No se publican cifras de lotes entregados.

## Pendientes / a confirmar

- Logo del Service Center en alta (hoy se usa el de la web de presentaciones, 204 px).
- Brochure en inglés actualizado (el EN de marzo 2026 tiene datos viejos; en EN se ofrece el PDF en español).
- Brochure del Service Center: el de dic-2025 tiene el teléfono viejo → desactivado en `content.json` (`brochure_service_center.enabled`).
- Service Center: cifras tomadas del brochure que usa ZLT-WEB-V2 (6.000 m² de predio, 3.000 m² cubiertos, 9 locales de 240 m² + 6 de 120 m², 60 cocheras). Ese brochure tiene el teléfono viejo (341 261-8540), por eso no se ofrece para descargar.
- Rango de lotes: brochure dice 1.350–4.350 m²; la lista de precios tiene lotes menores (1.139 m²) y el 93 de 26.733 m².

- Lotes vendidos que no figuran en la última lista (4, 5, 6, 7, 23, 32, 52, 70, 76, 83, 94, 102, 103): sus medidas salen de la lista del 08/09/2025 (con la numeración anterior) o de la tipología de su fila. Confirmar con la mensura si se quiere exactitud.

## Publicación

`.github/workflows/pages.yml` publica en GitHub Pages en cada push a `main` (mismo esquema que ZLT-WEB-V2, sin login: es una web pública). Si se quiere el mismo login de la V2 para la etapa de prueba, copiar `gate.js` de ese repo y agregar el `<script>` en `html/base.html`.
