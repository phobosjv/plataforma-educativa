# Changelog

Todos los cambios notables de este proyecto se documentan en este fichero.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/).
Versionado según [Semver](https://semver.org/lang/es/) con prefijo `V-`.

---

## [V-0.21.1] - 2026-06-18

### Corregido (contador de visitas — hallazgos de la auditoría)
- **No se cuentan visitas de contenido inexistente.** El endpoint público de visitas acepta cualquier
  ID; al **volcar** el contador a la BD se descartan ahora los conteos de IDs que no corresponden a
  ningún contenido (UUID arbitrarios o contenido ya purgado), de modo que `content_views` no acumula
  **filas huérfanas** ni se infla el total mostrado en el panel.
- **No se pierde el lote si falla la persistencia.** Antes, el volcado vaciaba el buffer en memoria
  *antes* de confirmar la transacción: si el commit fallaba, ese lote se perdía. Ahora, si la
  persistencia falla, los conteos **vuelven al buffer** y se reintentan en el siguiente volcado.

### Detalles técnicos
- Nuevo puerto `ContenidosConocidos` (dominio de `analytics`) implementado por un adapter en `content`
  y cableado en la tarea de volcado: ANALYTICS no depende de CONTENIDO (regla de dependencia). El
  filtrado se hace una vez por lote (no por petición, §8). Sin cambios de esquema ni de contrato.
- 222 tests de backend (3 nuevos: descartar contenido desconocido, durabilidad del volcado, y un test
  de integración del filtrado) + 9 E2E en verde.

---

## [V-0.21.0] - 2026-06-18

### Añadido (ejercicios tipo "Examen")
- **Marca de "Examen" (simulacro) en los ejercicios interactivos.** Al crear/editar un contenido de
  tipo interactivo aparece un check **«Examen»** (no aplica a artículos de texto; el dominio rechaza
  marcar un texto como examen). En el **catálogo**, los ejercicios marcados como examen se muestran
  **al final** de cada lista (navegación por ciclo/curso/asignatura, Aula Abierta y «Ver todo») y con
  un **icono/badge distinto** que indica que es una simulación de examen. La fusión de varios
  ejercicios en uno la hace a mano el diseñador del examen; la app solo aporta la marca, el orden y el
  icono.

### Persistencia / migraciones
- `content` gana la columna `is_exam` (Boolean, default false). Migración Alembic **016**. Invariante de
  dominio: solo un interactivo puede marcarse como examen. Cliente OpenAPI regenerado (campo `es_examen`
  en `ContenidoResponse` y en los request de crear/actualizar).

### Notas
- 219 tests de backend (3 nuevos: crear interactivo examen, rechazo de texto-examen, marcar/desmarcar) +
  9 E2E en verde. Type-check de frontend limpio. API version → `0.21.0`.

---

## [V-0.20.1] - 2026-06-18

### Corregido (hallazgos de una auditoría de lógica)
- **Integridad referencial al borrar taxonomía.** SQLite no fuerza las claves foráneas, así que borrar
  un **ciclo** con cursos, o un **curso/asignatura** referenciado por contenidos, dejaba referencias
  colgando y hacía que ese contenido **desapareciera silenciosamente** de la navegación del catálogo.
  Ahora el borrado se **bloquea** con un `409 Conflict` y un mensaje claro ("…tiene N curso(s)/
  contenido(s) asociado(s)"). Se cuenta también el contenido en la papelera (puede restaurarse). La
  página de Taxonomía muestra el motivo del bloqueo (antes el borrado fallido no daba ninguna pista).
- **No se puede publicar un ejercicio interactivo sin su fichero HTML.** Antes podía publicarse un
  ejercicio "a medias" que en público mostraba una página vacía; ahora `publicar()` lo rechaza con un
  mensaje claro.
- **Importar ya no arrastra visitas del sitio anterior.** Tras una importación, el contador de visitas
  en memoria (con IDs del sitio antiguo) se descarta, para no volcarlo como filas huérfanas en el sitio
  recién importado.

### Detalles técnicos
- Nuevo puerto `ContenidoEnTaxonomia` (dominio de `taxonomy`) implementado por un adapter en `content`
  y cableado en el router: TAXONOMÍA no depende de CONTENIDO (se respeta la regla de dependencia).
- Sin cambios de esquema ni de contrato (los modelos de respuesta no cambian). 216 tests de backend
  (6 nuevos) + 9 E2E en verde. Type-check de frontend limpio.

---

## [V-0.20.0] - 2026-06-18

### Añadido (importar / restaurar el sitio)
- **Importación completa del sitio (admin).** Operación inversa de «Exportar todo»: el administrador
  sube el archivo `.tar.gz` de exportación (BD + media + `manifest.json`) y el sitio destino queda
  restaurado/migrado con ese contenido. Pensado para **poner en marcha una web en blanco** con el
  contenido de otra, o **recuperar tras un fallo total**. Endpoint `POST /api/v1/admin/import` (solo
  admin), con sección propia en «Copias de seguridad».
- **Confirmación y seguridad.** La importación es destructiva (reemplaza la BD y restaura la media), así
  que exige escribir `IMPORTAR` para confirmar y crea **automáticamente una copia de seguridad de la BD
  actual** antes de sobrescribir (rollback). Tras importar, la BD se lleva al esquema actual
  (`alembic upgrade head`), de modo que una exportación de una versión anterior queda **migrada**.

### Detalles técnicos / seguridad
- `ImportService` (infra) valida el `manifest` (formato) y la integridad SQLite del archivo, extrae de
  forma **segura** (sin path traversal: solo `data/`, `media/`, `manifest.json`; nunca enlaces), cierra
  las conexiones del pool (`engine.dispose()`) y sustituye el fichero de BD con un `os.replace` atómico
  (las conexiones abiertas conservan el inodo antiguo; las nuevas abren ya la BD importada).
- Cliente OpenAPI regenerado (nuevo endpoint). Sin cambios de esquema propios de esta versión (no hay
  migración nueva). 211 tests de backend (6 nuevos de importación) + 9 E2E en verde. Type-check limpio.

---

## [V-0.19.2] - 2026-06-17

### Cambiado (UI / visibilidad)
- **Pie de la web pública siempre visible sin scroll.** El pie (apoyo/donaciones, «{sitio} — contenidos
  para infantil y primaria» y los iconos de redes) se ancla al fondo del viewport mientras se navega y,
  al llegar al final del documento, queda en su sitio natural (no tapa el contenido). Fondo opaco y por
  debajo del ejercicio maximizado y de la barra de navegación.
- **Acciones de admin/editor siempre visibles.** La barra lateral del panel queda fija a la altura del
  viewport, de modo que «Ver la web» y «Cerrar sesión» (al fondo) están siempre accesibles sin bajar; si
  la lista de secciones no cupiera, esa zona hace scroll propio.

### Notas
- Cambio **solo de CSS** (`frontend/src/styles/tokens.css`), sin tocar componentes, API ni esquema.
  205 tests de backend + 9 E2E en verde. Type-check de frontend limpio.

---

## [V-0.19.1] - 2026-06-17

### Seguridad (endurecimiento de imágenes)
- **El backend ya no ejecuta la aplicación como `root`.** Principio de menor privilegio: si apareciera
  una RCE, el proceso comprometido no sería root dentro del contenedor (dificulta escalar/escapar).
  `backend/Dockerfile` instala `gosu` y crea el usuario `appuser` (UID/GID `10001`, configurables con
  los build-args `APP_UID`/`APP_GID`). El `entrypoint.sh` arranca como `root` **solo** para ajustar el
  propietario de los *bind mounts* (`chown` de `/app/data` y `/app/media`) y a continuación se reinvoca
  con `gosu appuser`: migraciones Alembic, seed del admin y `uvicorn` corren ya sin privilegios (patrón
  de la imagen oficial de postgres).

### Notas
- Cambio **solo de infraestructura** (Dockerfile + entrypoint + docs); sin cambios de código, API ni
  esquema. 205 tests de backend en verde. **Requiere validar en el servidor** (Docker no está en el
  entorno de desarrollo): ver pasos de verificación en `docs/seguridad-imagenes.md` §4.

---

## [V-0.19.0] - 2026-06-17

### Añadido (mejoras de contenido)
- **Iconos de red social en el cuerpo de los artículos.** Cuando un editor enlaza a un perfil de una
  red social conocida (Facebook, Instagram, X, YouTube, TikTok, WhatsApp, Telegram, LinkedIn) dentro de
  un artículo, el enlace se muestra precedido por el **icono de marca** de esa red. La detección es por
  dominio del enlace; el icono es el mismo SVG self-hosted del pie (fuente única en
  `redesSociales.tsx`). Los enlaces externos abren en pestaña nueva (`rel=noopener noreferrer`, §10).
- **Autor de cada versión en el historial.** El historial de versiones de un contenido muestra ahora una
  columna **«Autor»** con el email de quien creó cada versión. El email se resuelve en la capa API a
  partir de `created_by` vía el caso de uso de `identity` (sin acoplar el dominio de contenido).

### Corregido / aclarado
- **Taxonomía:** se verificó que los nombres de ciclos/cursos/asignaturas están correctamente
  codificados en UTF-8 en la base de datos; lo que parecía «doble codificación» era solo la consola de
  Windows (cp1252). No había datos corruptos, no se requiere migración de datos.

### Notas
- `VersionResponse` gana el campo opcional `created_by_email`; cliente OpenAPI regenerado. Sin cambios
  de esquema de base de datos (no hay migración nueva).
- 205 tests de backend + 9 E2E en verde. Type-check de frontend limpio. API version → `0.19.0`.

---

## [V-0.18.0] - 2026-06-17

### Añadido (redes sociales)
- **Redes sociales en el pie (config admin).** Desde Apariencia se configura una lista de enlaces a
  redes sociales (Facebook, Instagram, X, YouTube, TikTok, WhatsApp, Telegram, LinkedIn), cada uno con
  su **icono** (SVG self-hosted, sin CDN externo por privacidad de menores §10). Se muestran en el pie
  de la web pública. La URL debe ser web (`http(s)://`); cada red puede aparecer una sola vez.
- **Enlaces a terceros en el cuerpo de artículos (editor).** El editor de artículos ya permitía
  insertar enlaces; ahora los enlaces **abren en una pestaña nueva** (`target=_blank` + `rel=noopener
  noreferrer`), de modo que un editor puede enlazar perfiles de redes sociales de terceros (autores
  citados) sin sacar al menor del sitio. El HTML se sigue saneando siempre (nh3 + DOMPurify).

### Persistencia / migraciones
- `site_config` gana `redes_sociales_json` (lista de `{red, url}`). Migración Alembic `015`. Se guarda
  por el endpoint existente `PUT /config/general`. Cliente OpenAPI regenerado.

### Notas
- 205 tests de backend (4 nuevos de redes sociales) + 9 E2E en verde. Type-check de frontend limpio.
  API version → `0.18.0`.

---

## [V-0.17.1] - 2026-06-17

### Seguridad / cambiado (robustez)
- **Migrada la gestión de JWT de `python-jose` a `PyJWT`.** `python-jose` arrastra un historial de
  CVEs y mantenimiento irregular; `PyJWT` es la librería de referencia y mejor mantenida. El cambio
  está aislado en `auth_service.py` (codificación/decodificación HS256); **sin cambios de
  comportamiento, de API ni de esquema** — los tokens existentes siguen siendo válidos.
- Como beneficio colateral, `PyJWT` avisa si la `SECRET_KEY` es más corta de lo recomendado (< 32
  bytes), reforzando el aviso ya documentado de usar una clave larga en producción.

### Notas
- Dependencia `python-jose[cryptography]` → `pyjwt`. 201 tests de backend (5 nuevos del servicio de
  auth: round-trip, token inválido/expirado, secreto distinto, hash de contraseña) en verde. API
  version → `0.17.1`.

---

## [V-0.17.0] - 2026-06-17

### Añadido (historial de versiones y restauración de contenidos)
- **Historial de versiones** en la edición de un contenido (panel admin): lista las versiones
  (número, título y fecha) con la más reciente marcada como «actual».
- **Restaurar una versión anterior**: devuelve el contenido al estado (título, descripción,
  etiquetas, cuerpo HTML o ejercicio) de esa versión. Restaurar **no destruye** el historial: crea
  una **versión nueva** con el estado restaurado (CLAUDE.md §7), de modo que la operación es reversible.
- Endpoints: `GET /api/v1/contenidos/{id}/versiones` y
  `POST /api/v1/contenidos/{id}/versiones/{version_no}/restaurar` (ambos editor/admin). La
  restauración queda registrada en la auditoría.

### Notas
- Sin cambios de esquema (la tabla `content_version` ya existía; cada modificación crea una versión
  inmutable). 196 tests de backend (4 nuevos) + 9 E2E en verde. Type-check de frontend limpio.
  Cliente OpenAPI regenerado. API version → `0.17.0`.

---

## [V-0.16.0] - 2026-06-17

### Añadido (donaciones, publicidad y textos del catálogo configurables)
- **Enlaces de donación.** Desde Apariencia se configura una lista de enlaces (PayPal, Ko-fi, etc.,
  con etiqueta + URL). Se muestran como botones en el **pie de la web pública**. La URL debe ser web
  (`http(s)://`); se rechazan esquemas peligrosos.
- **Publicidad en los márgenes.** Anuncios (código HTML de la red de anuncios) en los márgenes
  izquierdo y derecho, **solo en las pantallas de navegación del catálogo** (zona de adultos, §10).
  **Nunca** durante un ejercicio/artículo (lo usa un menor) ni en el panel admin. Activable y con
  código independiente por lado. Se ocultan en pantallas estrechas.
- **Textos de la portada del catálogo configurables.** «¿En qué curso estás?» (título) y «Toca tu
  curso para ver las actividades» (subtítulo) se editan desde Apariencia; pensados para dirigirse a
  las familias cuando hay publicidad.

### Persistencia / migraciones
- `site_config` gana: `catalogo_titulo`, `catalogo_subtitulo`, `donaciones_json`, `publicidad_activa`,
  `publicidad_html_izquierda`, `publicidad_html_derecha`. Migración Alembic `014`.
- Todo se guarda por el endpoint existente `PUT /config/general` (contrato y cliente OpenAPI ampliados).

### Notas
- 192 tests de backend (6 nuevos) + 9 E2E en verde. Type-check de frontend limpio. API version → `0.16.0`.

---

## [V-0.15.0] - 2026-06-17

### Añadido (auditoría — contexto `auditing`)
- **Registro de auditoría** de todas las acciones de gestión (admin/editor): quién hizo qué, sobre qué
  objeto y cuándo. Cubre contenidos (crear/editar/publicar/borrar/restaurar/purgar/subir HTML),
  usuarios, taxonomía (ciclos/cursos/asignaturas) y configuración (ajustes y paletas).
- **Página «Auditoría»** en el panel de administración (solo admin): lista de acciones recientes con
  fecha, usuario (email + rol), acción y detalle.
- Endpoint `GET /api/v1/auditoria` (solo admin, paginado). El registro es **append-only** y se
  **conserva indefinidamente** (sin purga automática).

### Persistencia / migraciones
- Nueva tabla `audit_log` (índice por fecha). Migración Alembic `013`.
- El registro se escribe en la capa API tras cada acción con éxito, usando la sesión de la petición.
  Es **a prueba de fallos**: si la auditoría fallara, nunca tumba la acción real del usuario.

### Notas
- 186 tests de backend (10 nuevos de auditoría) + 9 E2E en verde. Type-check de frontend limpio.
  Cliente OpenAPI regenerado. API version → `0.15.0`.

---

## [V-0.14.0] - 2026-06-17

### Añadido (contador de visitas — contexto `analytics`)
- **Conteo de visitas anónimas** de los contenidos. Al abrir la ficha de un contenido se registra una
  visita; el panel de administración muestra las **visitas totales** (Inicio) y las **visitas por
  contenido** (lista de Contenidos).
- Arquitectura según CLAUDE.md §8: las visitas se **agregan en memoria** (buffer de proceso,
  thread-safe) y se **vuelcan por lotes** a la BD mediante la tarea de mantenimiento (por defecto cada
  5 min) y al apagar la app. **Nunca** hay una escritura en BD por petición. Visitas anónimas y
  agregadas, sin datos del visitante (§10).
- Endpoints: `POST /api/v1/analytics/visitas/{contenido_id}` (público; solo incrementa el buffer en
  memoria) y `GET /api/v1/analytics/visitas` (solo admin; total + desglose por contenido).

### Persistencia / migraciones
- Nueva tabla `content_views` (total por contenido, UPSERT acumulativo). Migración Alembic `012`.
- Nuevos ajustes: `analytics_enabled` y `analytics_flush_interval_seconds`. El planificador de
  mantenimiento admite ahora intervalos en segundos (además de las tareas horarias de backup/purga).

### Notas
- 176 tests de backend (12 nuevos de visitas) + 9 E2E en verde. Type-check de frontend limpio. Cliente
  OpenAPI regenerado. API version → `0.14.0`.

---

## [V-0.13.0] - 2026-06-17

### Añadido (buscador del catálogo, FTS5)
- **Búsqueda full-text en el catálogo público.** Cuadro de búsqueda en la portada que encuentra
  contenidos por **título, descripción y etiquetas**. Resultados ordenados por relevancia, con su
  propia pantalla (estado en la URL `?q=`) y mensaje cuando no hay coincidencias.
- **Tolerante para niños:** ignora acentos en ambos sentidos (buscar «espana» encuentra «España») y
  busca por **prefijo** (escribir «mapa» encuentra «mapas»). Varios términos combinan en AND.
- Nuevo endpoint público `GET /api/v1/contenidos/buscar?q=…` (sin autenticación, solo contenido
  publicado y no borrado, máx. 50 resultados).

### Persistencia / migraciones
- Tabla virtual **FTS5** `content_fts` (contenido externo sobre `content`, tokenizer
  `unicode61 remove_diacritics 2`) mantenida por **triggers** de alta/baja/modificación. Migración
  Alembic `011`. El DDL vive en `content/infrastructure/fts.py` (lo reusan migración, seed E2E y tests).
- La consulta neutraliza los operadores de FTS5 que escriba el usuario (sin errores de sintaxis).

### Notas
- 164 tests de backend (11 nuevos de búsqueda) + 9 E2E (2 nuevos del buscador) en verde. Type-check de
  frontend limpio. Cliente OpenAPI regenerado. API version → `0.13.0`.

---

## [V-0.12.0] - 2026-06-17

### Añadido (logo del sitio configurable)
- **Logo del sitio.** Desde Apariencia → Ajustes generales se puede **subir un logotipo** (PNG, JPG,
  GIF o WebP, máx. 5 MB) con vista previa y botón para quitarlo. La imagen se almacena en el propio
  origen (contexto MEDIA, direccionada por contenido) y se sirve con `X-Content-Type-Options: nosniff`.
- **Cabecera con logo + nombre.** El logo aparece junto al nombre del sitio en la cabecera pública y en
  la barra lateral del panel de administración. Si no hay logo, se muestra solo el nombre (igual que antes).

### Seguridad
- El campo `logo_url` solo admite referencias al **propio origen** (`/media/…`); se rechaza cualquier
  URL externa, evitando filtrar la IP de los menores a terceros (CLAUDE.md §10). SVG sigue rechazado.

### Cambiado / migraciones
- Alembic `010` (`site_config.logo_url`).
- Esquemas API: `ConfiguracionResponse` y ajustes generales con `logo_url`. Cliente OpenAPI regenerado.

### Notas
- 153 tests de backend (4 nuevos del logo) en verde. Type-check de frontend limpio. API version → `0.12.0`.

---

## [V-0.11.0] - 2026-06-16

### Añadido (asignaturas transversales / Aula Abierta)
- **Asignaturas transversales.** Una asignatura puede marcarse como **transversal** (check en
  Taxonomía): p. ej. Audición y Lenguaje o Pedagogía Terapéutica, que no dependen del curso. Su
  contenido se saca de la clasificación por ciclo/curso y se agrupa en **«Aula Abierta»**.
- **Catálogo público — Aula Abierta.** Tarjeta de acceso (en el inicio y dentro de un curso, solo si
  hay contenido transversal) que lleva a las asignaturas transversales y a sus ejercicios, agregados
  de cualquier curso. El contenido transversal **no** aparece en el flujo normal de curso/asignatura.
- **Etiqueta y emoji configurables** de «Aula Abierta» en Apariencia (default `🌟 Aula Abierta`), para
  que cada centro elija un término inclusivo.
- **Formulario de contenido**: al elegir una asignatura transversal se ocultan ciclo/curso (no
  aplican) y el desplegable separa las asignaturas normales de las transversales.

### Cambiado / migraciones
- Alembic `008` (`asignatura.is_transversal`) y `009` (`site_config.aula_abierta_label/emoji`).
- Esquemas API: `AsignaturaResponse`/requests con `transversal`; `ConfiguracionResponse`/ajustes
  generales con `aula_abierta_label`/`aula_abierta_emoji`. Cliente OpenAPI regenerado.

### Notas
- 149 tests de backend + 7 E2E (2 nuevos de Aula Abierta) en verde. API version → `0.11.0`.

---

## [V-0.10.4] - 2026-06-16

### Añadido (tests)
- **Suite E2E con Playwright** (CLAUDE.md §11), ejecutada en navegador real contra la pila completa
  (API + sandbox + frontend) que la propia configuración levanta en **puertos aislados** (8101/8102/
  5273) sobre una BD y media e2e desechables:
  - `catalogo.spec.ts` — navegación pública curso → asignatura → ejercicio → ficha.
  - `sandbox-seguridad.spec.ts` — **aislamiento del sandbox** (§10): iframe `allow-scripts` sin
    `allow-same-origin`, origen sandbox distinto, y el **JS del ejercicio no alcanza el origen padre**.
  - `ejercicio-pantalla-completa.spec.ts` — maximizar y salir con Escape.
  - `admin-login-crud.spec.ts` — login de admin + crear/borrar un artículo.
- `backend/scripts/seed_e2e.py` — siembra determinista (admin, taxonomía, ejercicio interactivo con
  HTML que intenta escapar del sandbox, y un artículo).
- Guía `docs/e2e.md` y scripts `npm run test:e2e` / `test:e2e:ui`.

### Notas
- Sin cambios de la aplicación: 144 tests de backend + 5 E2E en verde. API version → `0.10.4`.

---

## [V-0.10.3] - 2026-06-16

### Añadido
- **Exportación completa del sitio (BD + media) descargable.** Nuevo endpoint
  `POST /api/v1/admin/export` (solo `admin`) y botón **«Exportar todo (BD + media)»** en el panel.
  Genera un `.tar.gz` con `data/app.sqlite3` (copia en caliente), la carpeta `media/` entera y un
  `manifest.json`. Con ese archivo se puede **migrar el servidor** o **recuperar el sitio entero**
  ante un fallo total. No incluye el `.env` (secretos): se gestiona aparte.
- **Copia incremental automática de `media`.** En cada ciclo de backup, junto a la copia de la BD,
  se sincroniza un espejo de `media` en `./data/backups/media/` copiando solo los ficheros nuevos
  (son content-addressed e inmutables). Desactivable con `MEDIA_BACKUP_ENABLED=false`.

### Documentación
- Nueva guía `docs/copias-y-restauracion.md`: qué se guarda y dónde, copias automáticas,
  exportación y **procedimiento de restauración/migración** a otro servidor.

### Cambiado
- La versión de la app se centraliza en `app/version.py` (`__version__`), usada por FastAPI y por el
  `manifest.json` de la exportación (evita el drift de la versión, que llegó a quedar desactualizada).

### Notas
- Sin cambios de esquema → sin migración. 144 tests en verde (8 nuevos: espejo de media, servicio de
  exportación y endpoint). API version → `0.10.3`.

---

## [V-0.10.2] - 2026-06-16

### Añadido
- **Descarga de copias de seguridad desde el navegador.** Nuevo endpoint
  `GET /api/v1/admin/backups/{nombre}` (solo `admin`) que sirve el fichero de la copia como adjunto,
  y botón **«Descargar»** en cada fila del panel «Copias de seguridad». La descarga usa el cliente
  tipado con el token de sesión (`parseAs: blob`), de modo que el admin guarda la copia en su PC.

### Seguridad
- El nombre solicitado se valida en el servicio de backup (formato exacto
  `app-YYYYMMDD-HHMMSS.sqlite3` + comprobación de contención en el directorio de copias): se rechaza
  cualquier intento de *path traversal* (`../`, rutas absolutas, etc.) con 404.

### Notas
- Sin cambios de esquema → sin migración. 136 tests en verde (13 nuevos: validación de nombre y
  endpoints de descarga). API version → `0.10.2`.

---

## [V-0.10.1] - 2026-06-16

### Seguridad / Robustez (imágenes Docker)
- **Backend:** base `python:3.12-slim` → `python:3.12-slim-bookworm` (release de Debian explícita) y
  **parches de seguridad del SO** en el build (`apt-get upgrade -y`), que aplican las correcciones de
  Debian publicadas después de la imagen base (el grueso de los hallazgos del escáner). Se actualizan
  `pip`/`setuptools`/`wheel` (versiones antiguas son un hallazgo recurrente). Limpieza de listas apt
  en la capa final.
- **Frontend:** etapa final `nginx:alpine` con `apk upgrade --no-cache` (paridad de parches del SO).

### Documentación
- Nueva guía `docs/seguridad-imagenes.md`: cómo **escanear** las imágenes ya construidas (Trivy,
  `--ignore-unfixed`), fijar la base por **digest** y endurecimiento pendiente (usuario no-root,
  revisión de `python-jose`).

### Notas
- El escáner del IDE marca el **tag base** antes del `apt-get upgrade`; tras el build, las CVEs con
  parche quedan resueltas y las restantes suelen ser "sin fix" en Debian. Verificar en el servidor.
- Sin cambios de código, API ni esquema: 123 tests siguen en verde. El usuario NO necesita nada
  especial al desplegar; el endurecimiento se aplica solo al reconstruir las imágenes.

---

## [V-0.10.0] - 2026-06-16

### Añadido (robustez)
- **Copias de seguridad automáticas de la base de datos.** Tarea en segundo plano (en proceso, sin
  broker) que hace una **copia en caliente** del SQLite con la *online backup API* (consistente y
  segura con WAL, a diferencia de un simple copiado del fichero) y **rota** las antiguas conservando
  solo las más recientes. Configurable por `.env`.
- **Purga programada de la papelera.** El contenido que lleva en la papelera más de
  `TRASH_RETENTION_DAYS` (por defecto **30 días**) se elimina de forma **definitiva** automáticamente.
  El borrado sigue siendo lógico primero (CLAUDE.md §7); la purga solo actúa sobre lo ya borrado.
- **Panel admin «Copias de seguridad».** Nueva sección (solo `admin`) para ver las copias existentes
  (nombre, tamaño, fecha) y **crear una copia manual** bajo demanda.
- **Endpoints admin** `GET /api/v1/admin/backups` y `POST /api/v1/admin/backups` (guarda de rol admin).

### Cambiado
- `app.main` arranca/detiene las tareas de mantenimiento con el `lifespan` de FastAPI.
- Versión de la API: `0.8.0` → `0.10.0` (estaba desactualizada).
- `.env.example` documenta las variables nuevas de backup y purga.

### Notas
- Sin cambios de esquema → **sin migración Alembic**. La antigüedad en papelera se deduce de
  `updated_at` (un contenido borrado está congelado, así que marca cuándo entró a la papelera).
- 123 tests en verde (12 nuevos: servicio de backup, purga y endpoints admin).

---

## [V-0.9.0] - 2026-06-15

### Añadido (producción / HTTPS)
- **Proxy inverso Caddy con HTTPS automático (Let's Encrypt).** Nuevo servicio `caddy` y
  `caddy/Caddyfile`. Es el **único** servicio expuesto a internet (80/443); obtiene y **renueva los
  certificados solos** y aplica **HSTS** + cabeceras de seguridad en el origen de la app.
  - `https://${APP_DOMAIN}` → frontend (SPA + `/api` + `/media`).
  - `https://${SANDBOX_DOMAIN}` → sandbox (ejercicios), **origen aislado en su propio subdominio**
    (CLAUDE.md §10), todo sobre 443.

### Cambiado
- **`frontend`, `api` y `sandbox` pasan a ser internos** (ya no publican puertos). Solo Caddy
  escucha de cara a internet.
- `SANDBOX_BASE_URL`, `APP_ORIGINS` y `CORS_ALLOW_ORIGINS` se **derivan automáticamente** de
  `APP_DOMAIN`/`SANDBOX_DOMAIN` en `docker-compose.yml` (`https://…`).
- `.env.example` simplificado al modelo de dominios: `APP_DOMAIN`, `SANDBOX_DOMAIN`, `ACME_EMAIL`
  (+ secreto y admin). `ENVIRONMENT=production`.
- Volúmenes `caddy_data`/`caddy_config` para **persistir los certificados** (evitar el rate limit
  de Let's Encrypt).

### Notas de despliegue
- Requiere: registros **DNS A** de ambos dominios → IP del servidor, y **puertos 80/443**
  redirigidos. Luego `docker compose up -d --build`. El acceso pasa a ser solo por
  `https://${APP_DOMAIN}` (no por IP:puerto).

---

## [V-0.8.9] - 2026-06-15

### Cambiado (robustez / producción)
- **El frontend en Docker se sirve como build estático tras nginx**, en vez del servidor de
  desarrollo de Vite (`npm run dev`), que no es apto para producción.
  - `frontend/Dockerfile` ahora es **multi-stage**: etapa Node (`npm run build`) + etapa **nginx**
    que sirve `dist/`.
  - Nuevo `nginx/frontend.conf`: sirve la SPA con *fallback* a `index.html` (React Router), proxya
    `/api` y `/media` al servicio `api`, cachea los assets con hash (sin cachear errores) y sube
    `client_max_body_size` a **16 MB** (evita `413` al subir imágenes/HTML; el default de nginx es 1 MB).
  - `docker-compose.yml`: `frontend` pasa a `5173:80`, monta la config y deja de necesitar
    `VITE_API_TARGET`/`VITE_ALLOWED_HOSTS`.
- **`ALLOWED_HOSTS` ya no es necesario:** nginx sirve cualquier `Host`, así que el acceso por IP y
  por dominio funciona sin configurarlo. (El servidor de desarrollo de Vite para uso local sigue
  igual con `npm run dev`.)

### Notas de despliegue
- Aplicar con `docker compose up -d --build frontend`.

---

## [V-0.8.8] - 2026-06-15

### Añadido
- **Enlace "↗ Ver la web" en el panel de administración** (sidebar, sobre "Cerrar sesión") que
  lleva al catálogo público (`/`). Evita tener que borrar `/admin` de la URL a mano.

---

## [V-0.8.7] - 2026-06-15

### Corregido
- **El sandbox cacheaba las respuestas de error durante 1 año.** La CSP/headers del sandbox añadían
  `Cache-Control: public, max-age=31536000, immutable` con `always`, por lo que un **403/404** se
  cacheaba como inmutable: tras corregir el fichero, el navegador seguía mostrando el error sin
  reintentar. Ahora ese `Cache-Control` se aplica **sin `always`** (solo a respuestas 2xx/3xx), en
  `nginx/sandbox.conf.template` y `nginx/sandbox.conf`. (El sandbox Python ya solo lo ponía en el
  200, sin cambios.)
- Tras actualizar: `docker compose restart sandbox` (re-renderiza la plantilla). Y **vaciar la caché
  del navegador** para soltar un error ya cacheado (incógnito o recarga forzada).

---

## [V-0.8.6] - 2026-06-15

### Corregido
- **Ejercicios interactivos daban `403 Forbidden` (nginx del sandbox)** en el despliegue Docker. El
  HTML del ejercicio se guardaba con permisos `0o600` (herencia de `tempfile.mkstemp`), legible solo
  por el usuario de la API (root); el sandbox lo sirve como usuario `nginx`, que no podía leerlo.
  Ahora el fichero se guarda como `0o644` (es contenido público servido de forma aislada). En local
  no se reproducía porque el sandbox Python corría con el mismo usuario.
- **Remediación de ficheros ya subidos** (permisos antiguos): `chmod -R a+rX media/` en el host
  (o `docker compose exec api sh -c "chmod -R a+rX /app/media"`).

---

## [V-0.8.5] - 2026-06-15

### Corregido
- **Vite bloqueaba el acceso por dominio** (`Blocked request. This host ... is not allowed`). Vite
  permite las IP por defecto, pero exige declarar los dominios en `server.allowedHosts`.

### Añadido
- **`server.allowedHosts` configurable por entorno** en `vite.config.ts` mediante
  `VITE_ALLOWED_HOSTS` (lista de hosts separados por comas, o `true` para permitir cualquiera),
  propagada desde la variable `ALLOWED_HOSTS` del `.env` vía `docker-compose.yml`. Permite servir
  la web por **IP y dominio a la vez**.
- `.env.example`: nueva `ALLOWED_HOSTS` y guía de acceso dual (IP + dominio). `APP_ORIGINS` admite
  varios orígenes (separados por espacios) y `CORS_ALLOW_ORIGINS` varios (separados por comas).

---

## [V-0.8.4] - 2026-06-15

### Corregido
- **API en bucle de reinicio en Docker** (`ModuleNotFoundError: No module named 'app'` al ejecutar
  Alembic). El layout plano del backend no instala el paquete `app` en site-packages con
  `pip install .`, y el entrypoint usa el comando `alembic` (que no añade `/app` al `sys.path`).
  Solución: **`PYTHONPATH=/app`** en `backend/Dockerfile` (builds limpias) y en el servicio `api`
  del `docker-compose.yml` (permite aplicar el arreglo sin reconstruir la imagen).

### Cambiado
- **Mensajes de error de login más claros:** el formulario ahora distingue entre **credenciales
  incorrectas** (401), **servidor no disponible** (5xx, p. ej. la API caída o reiniciándose) y
  **fallo de conexión** (sin respuesta), en vez de mostrar siempre "Credenciales incorrectas".

---

## [V-0.8.3] - 2026-06-14

### Cambiado

#### Despliegue Docker para servidor de pruebas
- **Puertos publicados** del `docker-compose.yml`: **frontend 5173 · api 5070 · sandbox 5071**
  (antes 5173 · 8000 · 8080). Los puertos internos no cambian (api 8000, sandbox 80).
- El **frontend** (Vite) proxya `/api` y `/media` al servicio `api` por la red interna de Docker
  (`VITE_API_TARGET=http://api:8000`); el cliente usa rutas relativas, así que el navegador solo
  necesita el puerto 5173.
- **Sandbox por plantilla:** `nginx/sandbox.conf.template` con `frame-ancestors ${APP_ORIGINS}`,
  renderizada con envsubst (`NGINX_ENVSUBST_FILTER=APP_ORIGINS`). Permite configurar el origen del
  frontend sin editar la config de nginx.
- `restart: unless-stopped` en los tres servicios.

### Añadido
- **`.dockerignore`** en `frontend/` y `backend/`: evitan copiar `node_modules` del host (binarios
  nativos que romperían la imagen Linux) y hornear secretos (`.env`), la BD y cachés en la imagen.
- `.env.example` con los valores del servidor de pruebas (`SANDBOX_BASE_URL`, `APP_ORIGINS`,
  `CORS_ALLOW_ORIGINS` apuntando a `http://TU_SERVIDOR:<puerto>`) y el admin inicial.

---

## [V-0.8.2] - 2026-06-14

### Añadido

#### Path navegable en el ejercicio maximizado
- En la barra superior del ejercicio interactivo maximizado, cada tramo del **path** es ahora un
  **enlace** que lleva al catálogo filtrado por esa taxonomía:
  - **ciclo** (p. ej. *primaria*) → catálogo del ciclo (`/?ciclo=<id>`).
  - **curso** (p. ej. *3º*) → cursos/asignaturas de ese curso (`/?curso=<id>`).
  - **asignatura** (p. ej. *conocimiento del medio*) → ejercicios de esa asignatura y curso
    (`/?curso=<id>&asignatura=<id>`).
  - **título** → tramo actual (sin enlace).
- A la izquierda del path, separado por un divisor, se muestra el **título del sitio** como
  **enlace al inicio** (`/`).
- **Catálogo:** nuevo soporte de `?ciclo=<id>` que filtra la pantalla de inicio a los cursos de
  ese ciclo, con su miga de pan. (Navegación 100% en cliente, sin cambios de API.)

---

## [V-0.8.1] - 2026-06-14

### Añadido

#### Maximizar el contenedor de ejercicios interactivos
- Nuevo botón **"⤢ Maximizar"** en el contenedor de un ejercicio interactivo (esquina superior
  derecha). Al pulsarlo, el ejercicio pasa a ocupar **casi toda la pantalla** (`position: fixed`),
  dejando arriba una **barra fina** con:
  - El **path** del ejercicio construido desde las taxonomías
    (`ciclo / curso / asignatura / título`, p. ej. *primaria / 3º / conocimiento del medio / mapa españa*).
  - El botón **"⤡ Minimizar"** para volver a la vista normal.
- El **mismo iframe se reutiliza** en ambos modos: maximizar/minimizar **no recarga** el ejercicio
  (no se pierde el progreso del alumno).
- UX: se puede salir con la tecla **Escape** y el scroll del fondo se bloquea mientras está maximizado.

### Cambiado
- Las taxonomías del path se cargan con las mismas `queryKey` que el catálogo (`ciclos`/`cursos`/
  `asignaturas`), reutilizando la caché de React Query (sin peticiones extra en la navegación habitual).

### Seguridad
- Se mantiene el **aislamiento del sandbox** (CLAUDE.md §10) en ambos modos: `sandbox="allow-scripts"`
  sin `allow-same-origin` y servido desde el origen sandbox. Clases CSS todas prefijadas `cms-`.

---

## [V-0.8.0] - 2026-06-14

### Añadido

#### Estampados de fondo "desordenados" (configurables)
- Nueva opción **Disposición del estampado: Ordenada / Desordenada** en *Apariencia y ajustes*.
- En **Desordenada**, el patrón se **genera proceduralmente** a partir de los mismos iconos del tema:
  cada icono se coloca con **posición, rotación y escala variables**, y la selección garantiza que
  **dos iconos iguales nunca queden adyacentes** — ni dentro del tile ni al repetirse (vecindad
  **toroidal**; con respaldo determinista por backtracking si el azar no lo logra). Patrón estable
  (PRNG con semilla por tema) y servido como máscara CSS recoloreada con la paleta activa.
- **Backend:** campo `fondo_estilo` en el dominio `ConfiguracionSitio` (`ordenado`/`desordenado`),
  método `cambiar_estilo_fondo` con validación, migración Alembic **007**, expuesto en
  `GET /config/` y `PUT /config/general`. 3 tests nuevos.

#### Imágenes con formato en el editor de artículos
- El editor WYSIWYG permite **subir imágenes** (PNG/JPG/GIF/WebP, máx. 5 MB) y darles formato:
  **alineación** (izquierda/centro/derecha), **tamaño** (S/M/L/100%) y **pie de imagen** (figcaption).
- Se guardan como `<figure class="cms-fig …"><img><figcaption></figure>` (etiquetas/clases que el
  sanitizador nh3 ya permite); el HTML se sanea igual en servidor y cliente (CLAUDE.md §10).
- **Nuevo contexto `media`:** `POST /api/v1/media/imagenes` (multipart, editor/admin) almacena la
  imagen content-addressed (SHA-256) y devuelve su URL; **SVG rechazado** (vector XSS). Las imágenes
  (raster, seguras) se sirven desde el **origen de la app** con `X-Content-Type-Options: nosniff`
  (a diferencia de los ejercicios, que van aislados en el sandbox). 4 tests nuevos.

### Cambiado
- `body::before` usa `--cms-bg-size` (variable) para soportar tiles de distinto tamaño.
- Vite proxya `/media` al backend en desarrollo. Cliente OpenAPI del frontend regenerado.
- **Tests:** suite total **111**, todos en verde. API version `0.7.0` → `0.8.0`.

---

## [V-0.7.0] - 2026-06-14

### Añadido

#### Catálogo público navegable por taxonomías (pensado para niños)
- El catálogo deja de ser una lista plana y pasa a una **navegación guiada por pasos**:
  **¿En qué curso estás?** → **elige asignatura** → **ejercicios**. Diseñado para que alumnado de
  infantil/primaria llegue solo a su contenido.
- Tarjetas grandes y coloridas: cursos agrupados por **ciclo** (con nº de actividades y emoji 🎒),
  asignaturas con **su color** y la inicial en un círculo, y badges de tipo (🎮 interactivo / 📖 texto).
- **Migas de pan grandes y clicables** (🏠 Inicio › Curso › Asignatura) para retroceder. El estado va
  en la URL (`?curso=&asignatura=`), así funciona el botón "atrás" del navegador y es compartible.
- Nunca se llega a callejones vacíos: solo se muestran cursos/asignaturas **con actividades**. Botón
  **"Ver todo el catálogo"** como alternativa (incluye el contenido sin clasificar).

#### Eliminación definitiva desde la papelera
- Nuevo botón **"Eliminar definitivamente"** (con confirmación) en la papelera del panel. Borra el
  contenido y sus versiones de forma **irreversible** (solo **admin**).
- Backend: caso de uso `PurgarContenidoHandler` (solo purga lo que ya está en la papelera, CLAUDE.md §7)
  y endpoint `DELETE /api/v1/contenidos/{id}/purgar`. Las versiones se borran en cascada.

#### Crear ejercicios interactivos más visible
- En **Contenidos** ahora hay **dos botones**: "+ Artículo de texto" y "+ Ejercicio interactivo"
  (antes solo "+ Nuevo artículo", que ocultaba que se podían crear ejercicios). El formulario llega
  con el tipo preseleccionado (`?tipo=`).

### Cambiado
- `ContenidoResponse` (sin cambios de campos respecto a V-0.6.1); el catálogo usa `curso_id`,
  `asignatura_id` ya expuestos. Cliente OpenAPI del frontend regenerado (nuevo endpoint de purga).
- **Tests:** +3 de integración (purga desde papelera, purga de no-borrado → 400, purga requiere admin).
  Suite total: **104 tests**, todos en verde.
- API version `0.6.1` → `0.7.0` en `main.py`.

---

## [V-0.6.1] - 2026-06-14

### Añadido
- **Asignar y editar la clasificación (ciclo / curso / asignatura) de un contenido** desde el panel,
  tanto al **crear** como al **editar** (antes los selectores solo aparecían al crear). Se puede
  reclasificar y **desasignar** (dejar en blanco).
- `ContenidoResponse` ahora expone `ciclo_id`, `curso_id` y `asignatura_id` (antes eran write-only:
  se enviaban al crear pero el contrato nunca los devolvía, por lo que no se veían al editar).

### Corregido
- **La taxonomía no se persistía al editar:** `SqlAlchemyContenidoRepository.save()` no copiaba
  `ciclo_id/curso_id/asignatura_id` al modelo, así que un `PUT` con clasificación se reflejaba en la
  respuesta pero **no se guardaba** en la base de datos. Ahora se persiste correctamente.

### Cambiado
- `PUT /api/v1/contenidos/{id}` acepta `ciclo_id/curso_id/asignatura_id`. Semántica segura: solo se
  reasigna si el cliente envía esos campos (un `PUT` parcial que los omite no borra la clasificación;
  enviar `null` sí la desasigna), usando `model_fields_set`.
- **Tests:** +4 de integración (asignar al crear, reasignar con verificación de persistencia vía GET,
  conservar al no enviarla, desasignar con `null`). Suite total: **101 tests**, todos en verde.
- API version `0.6.0` → `0.6.1` en `main.py`; cliente OpenAPI del frontend regenerado.

---

## [V-0.6.0] - 2026-06-14

### Añadido

#### Ejercicios interactivos: subida de HTML + origen sandbox aislado
- Se cierra el circuito del tipo de contenido **`interactivo`** (hasta ahora solo existía `texto`):
  un editor/admin puede **crear un ejercicio interactivo y subir su fichero HTML autocontenido**.
- **Aislamiento de seguridad (CLAUDE.md §10 / AD-3):** el HTML del ejercicio **no se sanea** (debe
  ejecutar su JS) y se sirve desde un **origen sandbox distinto** al de la app, dentro de un iframe
  con `sandbox="allow-scripts"` **sin** `allow-same-origin`, con **CSP estricta**
  (`default-src 'none'; connect-src 'none'; frame-ancestors <orígenes de la app>; …`).
- **Servidor sandbox:** nueva app ASGI independiente `app/sandbox.py` (`GET /ejercicio/{hash}`) para
  desarrollo (`uvicorn app.sandbox:sandbox_app --port 8002`) y `nginx/sandbox.conf` para producción
  (`sandbox.<dominio>`), ambos con la **misma CSP** (a mantener sincronizada).
- **Backend:**
  - Invariante de dominio `Contenido.adjuntar_html_interactivo()` (solo tipo interactivo).
  - Caso de uso `SubirHtmlContenidoHandler` (almacena por hash SHA-256 content-addressed, sin sanear,
    y crea una **versión inmutable** nueva).
  - Endpoint `POST /api/v1/contenidos/{id}/html` (multipart, guarda de rol editor/admin, límite 2 MB).
  - `ContenidoResponse` expone `sandbox_url` (URL absoluta del ejercicio en el origen sandbox).
- **Frontend:** selector de tipo (texto/interactivo) al crear; sección de **subida del fichero HTML**
  al editar un interactivo, con previsualización; render público del ejercicio en iframe sandbox
  usando `sandbox_url`.
- **Tests:** +14 (dominio, handler de subida, endpoint de subida y seguridad del sandbox: CSP,
  hash inválido → 400, inexistente → 404). Suite total: **97 tests**, todos en verde.

### Cambiado
- `FileSystemHtmlStorage.url_for` ahora devuelve la ruta canónica `/ejercicio/{hash}` (unifica
  backend, servidor sandbox y frontend, que estaban desalineados).
- `docker-compose.yml`: el servicio `sandbox` monta `nginx/sandbox.conf`.
- Nuevas variables de entorno: `SANDBOX_BASE_URL`, `APP_ORIGINS` (ver `.env.example`).
- API version `0.5.0` → `0.6.0` en `main.py`; cliente OpenAPI del frontend regenerado.

---

## [V-0.5.0] - 2026-06-14

### Añadido

#### Fondos / estampados temáticos del sitio
- Nuevo ajuste para elegir un **fondo tipo estampado** desde el panel **Apariencia y ajustes**,
  con **6 temáticas** y la opción **Ninguno** (por defecto):
  - **Aula** (pizarra, lápiz, reloj, regla), **Naturaleza** (pino, hoja, seta, bellota),
    **Espacio** (cohete, planeta, estrella, luna), **Océano** (pez, concha, burbujas, estrella de
    mar), **Geométrico** (formas y lunares) y **Granja** (granero, trigo, valla, sol).
- Los estampados son **patrones SVG self-hosted** (`frontend/public/patterns/*.svg`) que se
  **recolorean con la paleta activa** mediante una máscara CSS, a baja opacidad y detrás del
  contenido, de modo que no afectan la legibilidad. Selector con previsualización en vivo.
- **Backend:** campo `fondo_activo` en el dominio, método `cambiar_fondo` con validación
  (`FONDOS_PERMITIDOS`), endpoint `PUT /api/v1/config/general` extendido y migración Alembic **006**.
- **Tests:** 3 de integración nuevos (fondo por defecto, guardado, fondo inválido → 400). Suite
  total: **83 tests**, todos en verde.

### Cambiado
- `GET /api/v1/config/` ahora incluye `fondo_activo`; cliente OpenAPI del frontend regenerado.
- API version `0.4.0` → `0.5.0` en `main.py`.

---

## [V-0.4.0] - 2026-06-14

### Añadido

#### Creación y edición de artículos de texto (panel admin)
- Formulario completo para **crear** y **editar** contenidos de tipo `texto` desde el panel:
  título, descripción, etiquetas, clasificación (ciclo/curso/asignatura) y cuerpo del artículo.
- **Editor WYSIWYG (Tiptap)** con barra de formato: negrita, cursiva, tachado, encabezados (H2/H3),
  listas, cita y enlaces.
- Rutas `/admin/contenidos/nuevo` y `/admin/contenidos/{id}/editar`; botones "+ Nuevo artículo" y
  "Editar" en la lista de contenidos.

#### Seguridad: sanitización del HTML de artículos (CLAUDE.md §10)
- **Sanitización en servidor** del `body_html` de los contenidos de tipo `texto`, SIEMPRE, antes de
  persistir. Nuevo puerto de dominio `HtmlSanitizer` e implementación `Nh3HtmlSanitizer` (librería
  `nh3`) con allowlist conservadora (sin `script`/`style`/`iframe`, sin atributos `on*`, sin
  esquemas `javascript:`). Se cablea en los casos de uso de crear y actualizar.
- **Sanitización en cliente** (segunda capa, sanitización asimétrica) del artículo en la vista
  pública con **DOMPurify**.
- 2 tests de integración de sanitización. Suite total: **80 tests**, todos en verde.

### Cambiado
- Dependencia backend nueva: `nh3` (sanitizador HTML). Dependencias frontend nuevas: `@tiptap/*` y
  `dompurify`.
- API version `0.3.0` → `0.4.0` en `main.py`.

### Notas
- Esta entrega cubre solo el tipo **texto**. Los contenidos **interactivos** (subida de HTML) se
  abordarán junto con el subdominio sandbox, requisito de seguridad para servirlos (§10).
- La clasificación (ciclo/curso/asignatura) se asigna al **crear**; el contrato actual de la API no
  la expone ni edita en actualización (mejora futura).

---

## [V-0.3.0] - 2026-06-14

### Añadido

#### Ajustes generales del sitio (nombre + tipografía)
- El **nombre del sitio** es editable desde el panel **Apariencia y ajustes** y se refleja en la
  barra pública, el pie de página y el sidebar de administración.
- **Selector de fuente de letra** con un catálogo curado para un portal infantil/primaria:
  - Amigables/redondeadas: **Nunito**, **Quicksand**.
  - Alta legibilidad / lectores principiantes: **Lexend**, **Atkinson Hyperlegible**, **Andika**.
  - **Sistema** (pila nativa, sin descarga) como opción por defecto.
- La fuente se aplica en tiempo real a todo el sitio (variable CSS `--cms-font`).
- **Fuentes self-hosted** (subset latino, pesos 400/700) servidas por la propia app, **no desde un
  CDN externo**: no se expone la IP de los menores a terceros (RGPD/DSA, CLAUDE.md §10). Los `.woff2`
  viven en `frontend/public/fonts/` y los descarga `frontend/scripts/download_fonts.py`.

#### Backend
- Dominio `ConfiguracionSitio`: campo `fuente_activa`, métodos `cambiar_nombre` y `cambiar_fuente`
  con validación (nombre no vacío ≤ 80 caracteres; fuente ∈ `FUENTES_PERMITIDAS`).
- Caso de uso `ActualizarAjustesGeneralesHandler` y endpoint `PUT /api/v1/config/general` (solo admin).
- Migración Alembic **005**: columna `fuente_activa` en `site_config` (default `sistema`).

#### Tests
- 4 tests de integración nuevos (guardado, guarda de admin, fuente no permitida → 400,
  nombre vacío → 400). Suite total: **78 tests**, todos en verde.

### Cambiado
- `GET /api/v1/config/` ahora incluye `fuente_activa`; cliente OpenAPI del frontend regenerado.
- API version `0.2.1` → `0.3.0` en `main.py`.

---

## [V-0.2.1] - 2026-06-14

### Corregido
- **Error 500 al aplicar o guardar paletas de color** (contexto `configuration`). Cuando la fila
  singleton `site_config` aún no existía, el flujo `get()` + `save()` insertaba **dos** filas con
  la misma clave primaria, provocando `IntegrityError: UNIQUE constraint failed: site_config.id`.
  La causa de fondo es que `SessionLocal` usa `autoflush=False`, por lo que `session.get()` no
  encontraba el modelo recién añadido (pendiente de flush) y `save()` creaba uno nuevo duplicado.
- Unificada la lógica de acceso al singleton en `SqlAlchemyConfiguracionRepository._get_or_create_model()`
  con `flush()` explícito: el modelo pasa a *persistent* y queda en el *identity map*, de modo que
  `get` y `save` dentro del mismo caso de uso operan sobre la **misma** instancia.

### Cambiado
- Frontend: las mutaciones de paletas (`useConfigMutations`) ahora **propagan** los errores de la API
  en lugar de tragárselos en silencio; `ConfiguracionPage` muestra un banner de error accesible (`role="alert"`).
- Frontend: el cliente de API usa `baseUrl` relativo y Vite reenvía `/api` al backend mediante proxy
  (`vite.config.ts`), eliminando los problemas de CORS en desarrollo. `strictPort` fija el puerto 5173.

### Añadido
- Tests de integración del contexto `configuration` (`tests/integration/test_configuration_endpoints.py`,
  7 tests). El fixture replica `autoflush=False` de producción para que el caso de regresión sea válido.
  Suite total: **74 tests**, todos en verde.

---

## [V-0.2.0] - 2026-06-13

### Añadido

#### Contexto `configuration` (apariencia del sitio)
- Dominio: agregado `ConfiguracionSitio` con patrón singleton (`SINGLETON_ID`), value object `PaletaPersonalizada`
- Métodos de dominio: `activar_paleta`, `agregar_paleta`, `actualizar_paleta`, `eliminar_paleta` (con invariante: no eliminar paleta activa)
- Puerto `ConfiguracionRepository` con get-or-create automático
- Casos de uso: `ObtenerConfiguracionHandler`, `ActivarPaletaHandler`, `AgregarPaletaHandler`, `ActualizarPaletaHandler`, `EliminarPaletaHandler`
- Repositorio `SqlAlchemyConfiguracionRepository` con patrón get-or-create
- Migración Alembic `004`: tabla `site_config` con `id`, `nombre_sitio`, `paleta_activa`, `paletas_json`
- API REST: `GET /api/v1/config/` (público), `PUT /api/v1/config/paleta`, `POST /api/v1/config/paletas`, `PUT /api/v1/config/paletas/{id}`, `DELETE /api/v1/config/paletas/{id}` (solo admin)
- Validación de colores hexadecimales con `Field(pattern=r"^#[0-9a-fA-F]{6}$")`

#### Frontend MVP completo (React + TypeScript)
- Sistema de diseño con CSS custom properties (`--cms-color-*`) y clases prefijadas `cms-`
- `PublicLayout` (nav pública) y `AdminLayout` (sidebar con Inicio, Contenidos, Taxonomía, Apariencia, Usuarios)
- Páginas públicas: `CatalogoPage`, `ContenidoPage` (iframe sandbox para ejercicios interactivos)
- Páginas admin: `DashboardPage`, `ContenidosPage`, `TaxonomiaPage`, `UsuariosPage`, `ConfiguracionPage`
- `AuthContext` con JWT (decodificación `atob`), `RequireAuth` con guarda de rol
- `useConfig` + `aplicarPaleta` — carga y aplica la paleta activa al arrancar la app
- 6 paletas predefinidas infantiles (Cielo Azul, Bosque Mágico, Coral Feliz, Sol Brillante, Lavanda Soñadora, Estándar)
- `ConfiguracionPage` — grid de swatches con preview, badge "Activa", formulario de paleta personalizada con color pickers y preview en vivo
- Cliente de API generado desde OpenAPI (`openapi-typescript` + `openapi-fetch`)
- Stack: React 18 + Vite 4 + TypeScript strict + TanStack Query v5 + React Router v6

#### Gestión de taxonomías (CRUD completo en frontend)
- `TaxonomiaPage` con secciones Ciclos, Cursos y Asignaturas
- `FilaEditable`: edición inline con Enter/Escape, confirmación de borrado
- Todas las mutaciones via `useMutation` + invalidación de caché

#### Scripts y despliegue
- `backend/scripts/seed_admin.py` — CLI para crear el primer usuario administrador
- `backend/entrypoint.sh` — ejecuta migraciones y crea admin por defecto si no existe ningún usuario
- `backend/Dockerfile` actualizado con `ENTRYPOINT` al script
- Variables de entorno `DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD` documentadas en `.env.example`

---

## [V-0.1.0] - 2026-06-13

### Añadido

#### Contexto `taxonomy` (ciclos, cursos, asignaturas)
- Dominio: agregados `Ciclo`, `Curso` y `Asignatura` con validación en `__post_init__` y método `actualizar()`
- Puertos `CicloRepository`, `CursoRepository`, `AsignaturaRepository` en dominio
- Casos de uso CRUD completos para las tres entidades (crear, actualizar, eliminar, listar, obtener)
- `CrearCursoHandler` valida la existencia del ciclo padre antes de persistir
- Repositorios SQLAlchemy con `list_by_ciclo()` en cursos
- Migración Alembic `003`: tablas `ciclo`, `curso` (FK → ciclo), `asignatura`
- API REST bajo `/api/v1/taxonomy/`: endpoints públicos (GET) y protegidos por `require_admin` (POST/PUT/DELETE)
- `GET /api/v1/taxonomy/cursos/?ciclo_id=...` para filtrar cursos por ciclo
- 23 tests nuevos (11 unitarios + 12 integración) — 67 tests en total, todos pasan

---

## [V-0.0.2] - 2026-06-13

### Corregido
- Eliminado `test_contenido.py` del esqueleto inicial (sustituido por `test_contenido_lifecycle.py`).
- Eliminado `shared/application/buses.py` del esqueleto (CommandBus/QueryBus no usado).
- Corregida versión de la API en `main.py`: `"0.1.0"` → `"0.0.1"`.
- Eliminados `data/` raíz y `.env` raíz creados accidentalmente al arrancar el servidor.

---

## [V-0.0.1] - 2026-06-13

### Añadido

#### Infraestructura compartida
- `shared/infrastructure/database.py` — motor SQLite WAL, `Base` ORM única, `get_db()` dependency
- `shared/infrastructure/unit_of_work.py` — Unit of Work para gestionar commit/rollback por caso de uso
- `shared/domain/base.py` — subclases de `DomainError`: `NotFoundError`, `AuthenticationError`, `AuthorizationError`

#### Contexto `identity` (autenticación y usuarios)
- Dominio: agregado `Usuario` con `Rol` (admin/editor), validación de email, métodos `crear`, `cambiar_password`, `desactivar`
- Puerto `AuthService` (protocolo) en dominio; implementado como `ArgonAuthService` (Argon2id + JWT HS256)
- Puerto `UsuarioRepository`; implementado como `SqlAlchemyUsuarioRepository`
- Casos de uso: `LoginHandler`, `CrearUsuarioHandler`, `ListarUsuariosHandler`
- API REST: `POST /api/v1/auth/token`, `GET /api/v1/users/`, `POST /api/v1/users/`
- Guardas de rol: `require_admin`, `require_editor_or_admin`

#### Contexto `content` (contenidos educativos)
- Dominio: `Contenido` extendido con ciclo de vida completo (`publicar`, `archivar`, `borrar`, `restaurar`)
- `ContentVersion` — snapshot inmutable creado en cada mutación
- Puerto `ContenidoRepository` completo (add, get, save, list_published, list_all, list_trash, delete_permanent)
- Puerto `ContentVersionRepository`; `HtmlStorage` (almacén content-addressed SHA-256)
- Casos de uso: crear, actualizar, publicar, archivar, borrar (soft), restaurar, listar, obtener
- `FileSystemHtmlStorage` — escrituras atómicas con `os.replace`
- API REST: catálogo público, CRUD editor+, panel admin

#### Persistencia
- Modelos ORM SQLAlchemy 2.0: `UsuarioModel`, `ContenidoModel`, `ContentVersionModel`
- Migraciones Alembic: `001_create_user_table`, `002_create_content_tables`
- `bootstrap.py` — registro de modelos ORM con `Base.metadata`

#### Tests
- 27 tests unitarios (dominio + handlers con mocks)
- 19 tests de integración (endpoints identity + content con SQLite en memoria + `StaticPool`)
- 46/46 tests pasan

#### Proceso de lanzamiento
- Sección §19 en `CLAUDE.md` — proceso de versión, manual PDF, zip y commit automatizados
