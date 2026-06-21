# Manual técnico y de usuario — V-0.22.2

CMS educativo interactivo para infantil y primaria. Esta versión es un **arreglo de configuración**
que hace funcionar el visor de fichas PDF en entorno de desarrollo y en dispositivos móviles
conectados a la red local de desarrollo. Sin cambios de esquema ni de contrato de la API.

## Novedades de V-0.22.2

### El visor PDF ya funciona en dev y desde móvil en LAN

**Problema:** la `pdf_url` devuelta por la API apuntaba a `http://localhost:8002/ficha/<hash>.pdf`
(el servidor sandbox). En entorno de desarrollo ese servidor normalmente no está arrancado, y
desde un móvil en red local `localhost` apunta al propio móvil (no al PC de desarrollo). Resultado:
PDF.js recibía un error de red y mostraba el mensaje de fallback.

**Solución:** nueva variable de entorno `PDF_BASE_URL`:
- En **dev** (valor por defecto `""`): la URL del PDF es relativa (`/ficha/<hash>.pdf`). Vite la
  proxea al backend principal, que ahora expone un endpoint `GET /ficha/{hash}.pdf` para servir la
  ficha desde el directorio `media/`. No hace falta el servidor sandbox en puerto 8002 para ver PDFs.
- En **producción** (docker-compose fija `PDF_BASE_URL=https://${SANDBOX_DOMAIN}`): la URL sigue
  siendo absoluta, apuntando al subdominio sandbox como antes. Sin ningún cambio de comportamiento.

### Detalles técnicos

- Nuevo endpoint `GET /ficha/{file_hash}.pdf` en `app.main` (app principal): sirve el PDF desde
  `media/<h2>/<hash>.pdf` con `Content-Disposition`, `Cache-Control: immutable` y
  `Access-Control-Allow-Origin: *`. En producción este endpoint nunca se llama.
- Proxy Vite: `"/ficha" → API_TARGET` añadido a `vite.config.ts`.
- `config.py`: nueva configuración `pdf_base_url: str = ""`.
- `docker-compose.yml`: `PDF_BASE_URL=https://${SANDBOX_DOMAIN}` añadido al servicio `api`.
- `PdfViewer.tsx`: `console.error` en el bloque `catch` para facilitar depuración futura.

## Despliegue

Sin migración ni reconstrucción del frontend necesaria. En producción Docker basta con:

```bash
# En el servidor, directorio del proyecto:
docker compose pull && docker compose up -d --build
```

El compose ya incluye `PDF_BASE_URL=https://${SANDBOX_DOMAIN}` que configura la URL absoluta
hacia el sandbox. Los contenidos existentes (PDFs subidos) siguen accesibles sin cambios.
