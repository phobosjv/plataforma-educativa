# Manual técnico y de usuario — V-0.22.3

CMS educativo interactivo para infantil y primaria. Esta versión corrige el MIME type del worker de
PDF.js en producción, que impedía ver las fichas PDF. Sin cambios de esquema ni de contrato.

## Novedades de V-0.22.3

### El worker de PDF.js ya carga en producción

**Problema:** el nginx del frontend servía el fichero del worker de PDF.js
(`assets/pdf.worker.min-*.mjs`) con el MIME type `application/octet-stream`, porque el `mime.types`
de nginx no incluye la extensión `.mjs`. Los navegadores aplican comprobación estricta de tipo a los
*module scripts* y rechazan cualquiera que no sea JavaScript, así que el worker no arrancaba y la
ficha PDF quedaba en blanco con el mensaje "No se ha podido mostrar el PDF aquí".

**Solución:** `nginx/frontend.conf` añade una `location ~* \.mjs$` que sirve los ficheros `.mjs`
como `text/javascript`.

### Detalles técnicos

- La `location` regex tiene prioridad sobre el prefijo `/assets/`, así que captura el worker.
- Mantiene la cabecera `Cache-Control: immutable` (los assets de Vite llevan hash en el nombre).
- En desarrollo no aplica: el servidor de Vite ya sirve los `.mjs` con el MIME correcto.

## Despliegue

`nginx/frontend.conf` se monta como volumen en el contenedor `frontend`, así que **no hace falta
reconstruir** la imagen:

```bash
# En el servidor, directorio del proyecto:
docker compose up -d
# (o, para forzar el reinicio del frontend)
docker compose restart frontend
```

Tras el reinicio, recarga la ficha PDF en el navegador (Ctrl+F5 para saltar la caché).
