# Changelog

Todos los cambios notables de este proyecto se documentan en este fichero.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/).
Versionado según [Semver](https://semver.org/lang/es/) con prefijo `V-`.

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
