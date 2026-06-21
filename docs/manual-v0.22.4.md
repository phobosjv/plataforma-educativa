# Manual técnico y de usuario — V-0.22.4

CMS educativo interactivo para infantil y primaria. Esta versión añade el indicador de versión
junto al nombre del sitio (para verificar el despliegue) y endurece el arreglo del worker de PDF.js.

## Novedades de V-0.22.4

### Versión de la app visible junto al nombre

Al lado del nombre del sitio ("Aprende y Juega"), tanto en la cabecera pública como en la barra
lateral del panel de administración, ahora se muestra la versión actual en texto pequeño y
atenuado (p. ej. `v0.22.4`).

La versión se **hornea en el bundle del frontend en build-time** (`frontend/src/version.ts`). Esto
la convierte en un **verificador de despliegue**: si tras actualizar el servidor NO ves el número
nuevo en la web, significa que la imagen del frontend no se reconstruyó y los assets antiguos
(incluido el worker de PDF.js) siguen sirviéndose.

### Por qué "seguía fallando" el PDF

El arreglo del MIME type de V-0.22.3 era correcto, pero `docker compose up -d` a secas **no recrea**
el contenedor del frontend si la imagen no cambió: nginx mantenía la configuración vieja cargada en
memoria y los assets horneados (el worker `.mjs`) eran los de antes. El despliegue correcto es:

```bash
docker compose up -d --build
```

Esto reconstruye la imagen (assets nuevos, incl. el badge de versión), recrea el contenedor y, en
la misma operación, recarga la configuración de nginx (que sirve los `.mjs` como `text/javascript`).

### Detalles técnicos

- `frontend/src/version.ts` exporta `APP_VERSION`, mostrado por `PublicLayout` y `AdminLayout` con
  la clase prefijada `.cms-version`.
- `nginx/frontend.conf`: `location ~* \.mjs$` → `text/javascript`; `location ~* \.wasm$` →
  `application/wasm` (por si PDF.js usa WebAssembly). Ambas con `try_files`.
- Dos fuentes de verdad de la versión, sincronizadas en cada release: `backend/app/version.py` y
  `frontend/src/version.ts` (CLAUDE.md §19).

## Despliegue

```bash
# En el servidor, directorio del proyecto:
docker compose up -d --build
```

Tras desplegar, abre la web: si junto al nombre ves `v0.22.4`, el frontend está actualizado y la
ficha PDF debe renderizar. Recarga con Ctrl+F5 para saltar la caché del navegador.
