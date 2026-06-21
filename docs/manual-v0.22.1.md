# Manual técnico y de usuario — V-0.22.1

CMS educativo interactivo para infantil y primaria. Esta versión es un **arreglo de compatibilidad**
del visor de fichas PDF en móviles. Sin cambios de esquema ni de contrato de la API.

## Novedades de V-0.22.1

### El PDF ahora se ve en móvil (visor PDF.js)
- **Problema:** muchos navegadores móviles (iOS Safari, Android Chrome) no renderizan un PDF
  embebido dentro de un `<iframe>` y lo dejaban en blanco (la descarga sí funcionaba).
- **Solución:** la ficha PDF se renderiza con **PDF.js** dentro de un `<div>` (un `<canvas>` por
  página). Funciona en prácticamente todos los navegadores, incluidos los móviles. Se mantienen los
  botones **Maximizar** y **Descargar / Imprimir**.

### Detalles técnicos
- El servidor sandbox añade `Access-Control-Allow-Origin: *` a las respuestas de `/ficha/*.pdf`: el
  visor PDF.js corre en el origen de la app y lee el fichero por fetch cross-origin. El PDF es
  contenido público (sin auth ni cookies), así que abrir su lectura es seguro.
- PDF.js se sirve **self-hosted** (bundle de Vite, sin CDN — CLAUDE.md §10), con su build *legacy*
  (transpilado para navegadores antiguos) y **cargado bajo demanda** (solo se descarga al abrir una
  ficha PDF; no penaliza el catálogo ni el resto de páginas).

## Despliegue
Sin migración. Basta con actualizar el código (frontend reconstruido + nueva cabecera CORS en el
sandbox) con el procedimiento de actualización habitual.
