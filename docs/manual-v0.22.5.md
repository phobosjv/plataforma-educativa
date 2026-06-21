# Manual técnico y de usuario — V-0.22.5

CMS educativo interactivo para infantil y primaria. Esta versión es el **arreglo definitivo** del
visor de fichas PDF: el worker de PDF.js ahora se emite como `.js`, eliminando la dependencia del
MIME type de nginx y la caché envenenada. Sin cambios de esquema ni de contrato.

## Novedades de V-0.22.5

### El worker de PDF.js se emite como `.js`

**Diagnóstico (gracias al badge de versión de V-0.22.4):** el badge confirmó que el frontend SÍ se
estaba desplegando (mostraba la versión nueva), pero el worker seguía dando
`application/octet-stream`. La causa real era doble:

1. **Caché envenenada:** el fichero del worker (`pdf.worker.min-bd888051.mjs`) conserva el **mismo
   nombre** entre versiones porque su contenido no cambia. La carpeta `/assets/` marca
   `Cache-Control: immutable` (1 año), así que el navegador (y posibles proxies) seguían sirviendo
   la respuesta vieja con el MIME incorrecto, aunque la config de nginx ya fuera correcta.
2. **Fragilidad del MIME de `.mjs`:** depender de que cada nginx mapee la extensión `.mjs` es poco
   robusto entre despliegues.

**Solución:** Vite ahora emite el worker con extensión **`.js`**
(`build.rollupOptions.output.assetFileNames`). La extensión `.js` está mapeada por defecto a
`application/javascript` en cualquier nginx, sin configuración especial. Y al cambiar la extensión,
cambia el nombre del fichero → la URL es nueva → **se rompe la caché** envenenada.

### Detalles técnicos

- `vite.config.ts`: `assetFileNames` renombra los assets `.mjs` a `.js` (solo afecta al worker de
  PDF.js; el resto de assets conservan su patrón `[name]-[hash][extname]`).
- En desarrollo no cambia nada perceptible: Vite ya servía bien los módulos.
- Se mantiene como red de seguridad el manejo de `.mjs`/`.wasm` en `nginx/frontend.conf`, pero ya no
  es imprescindible para que PDF.js funcione.

### Sobre servir el PDF desde el CMS (pregunta del usuario)

Mover el PDF al origen del CMS NO era necesario para este fallo: el error era del *worker* de PDF.js
(un asset del frontend), no del PDF (su URL del sandbox cargaba bien). Con PDF.js el PDF se descarga
y se dibuja en un `<canvas>` sin ejecutar el posible JavaScript embebido del PDF, así que servirlo
desde el CMS sería viable y más simple, pero es una optimización aparte y no se aborda aquí.

## Despliegue

```bash
# En el servidor, directorio del proyecto:
docker compose up -d --build
```

Tras desplegar: la versión junto al nombre debe ser **v0.22.5**, y en la consola el worker se pedirá
como `…/pdf.worker.min-*.js` (nombre nuevo). Recarga con Ctrl+F5.
