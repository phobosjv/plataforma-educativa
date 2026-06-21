# Manual técnico y de usuario — V-0.22.0

CMS educativo interactivo para infantil y primaria. Esta versión añade un **tercer tipo de
contenido**: la **ficha PDF imprimible**, junto a los artículos de texto y los ejercicios
interactivos.

## Novedades de V-0.22.0

### Ficha PDF imprimible
Pensada para que el alumnado de infantil y primaria practique la **escritura**: abren la ficha,
la imprimen y escriben a mano sobre el papel.

- En la ficha pública el PDF se muestra **embebido** (visor del navegador), con botón
  **Maximizar** (a pantalla completa, igual que los ejercicios) y botón **Descargar / Imprimir**.
- El editor crea la ficha con tipo «Ficha PDF» y sube el documento desde la edición. El fichero es
  **content-addressed por SHA-256**, inmutable, y cada subida queda **versionada** (restaurar una
  versión recupera su PDF).
- El PDF se sirve **aislado desde el subdominio sandbox** (`/ficha/<hash>.pdf`), nunca desde el
  origen de la app (CLAUDE.md §10). No se sanea (es binario): el aislamiento lo da el origen
  distinto. La descarga fuerza `attachment` con un nombre amigable derivado del título.

## Modelo de datos

`content.tipo` admite ahora `interactivo`, `texto` y `pdf`. La columna nueva `content.hash_pdf`
(y `content_version.hash_pdf`) referencia el documento PDF por hash, igual que `hash_html` lo hace
con los ejercicios interactivos. Migración Alembic **018** (ADD COLUMN; no toca el índice FTS5).

## API

- `POST /api/v1/contenidos/` con `tipo: "pdf"` crea la ficha (aún sin fichero).
- `POST /api/v1/contenidos/{id}/pdf` (editor/admin, multipart) sube el documento PDF: máx. 20 MB,
  se valida la firma `%PDF-`. Crea una versión nueva.
- La respuesta de contenido incorpora `hash_pdf`, `pdf_url` (visor) y `pdf_descarga_url` (descarga
  con `?descargar=1`). El sandbox sirve `/ficha/<hash>.pdf` con `Content-Type: application/pdf`.

## Seguridad

- El PDF se sirve desde `sandbox.<dominio>`, aislado del origen de la app, con la misma CSP estricta
  que los ejercicios. No se renderiza nunca en el origen de la app.
- El nombre de descarga se filtra (solo caracteres seguros) para evitar inyección en la cabecera
  `Content-Disposition`.
- La ficha es contenido infantil: la página de contenido no muestra publicidad (como los
  ejercicios), solo el catálogo.

## Manual de uso (editor/admin)

1. En **Contenidos**, pulsa **+ Ficha PDF**.
2. Rellena título, descripción y clasificación (ciclo/curso/asignatura), y crea la ficha.
3. En la edición, sube el documento PDF en **«Fichero PDF de la ficha»**.
4. Pulsa **Publicar**. (No se puede publicar una ficha sin su PDF.)
5. En la web pública, la ficha se ve embebida; el alumnado puede **maximizarla** y **descargarla**
   para imprimirla.
