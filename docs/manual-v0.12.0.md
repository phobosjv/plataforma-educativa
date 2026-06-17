# Manual Técnico y de Usuario — Plataforma Educativa V-0.12.0

**Fecha:** 2026-06-17  
**Versión:** V-0.12.0  
**Estado:** Desarrollo activo

---

## 0. Novedades de V-0.12.0

**Logo del sitio configurable.**

- Desde **Apariencia → Ajustes generales** se puede **subir un logotipo** (PNG, JPG, GIF o WebP, máx.
  5 MB), con vista previa y botón para quitarlo. Se recomienda un PNG con fondo transparente.
- El logo aparece **junto al nombre del sitio** en la cabecera pública y en la barra lateral del
  panel de administración. Si no hay logo, se muestra solo el nombre (comportamiento anterior).
- La imagen se almacena en el **propio origen** (contexto `media`, direccionada por contenido SHA-256)
  y se sirve con `X-Content-Type-Options: nosniff`. El campo `logo_url` **solo** admite referencias a
  `/media/…`: se rechaza cualquier URL externa, evitando filtrar la IP de los menores a terceros
  (CLAUDE.md §10). SVG sigue rechazado (vector XSS).
- **Migración** Alembic `010` (`site_config.logo_url`). 153 tests backend (4 nuevos del logo) en
  verde. API → `0.12.0`.

### Versiones recientes
- **V-0.11.0** — Asignaturas transversales / «Aula Abierta».
- **V-0.10.4** — Suite E2E con Playwright (incluye test de seguridad del sandbox).
- **V-0.10.3** — Exportación completa BD+media + copia incremental de media.

---

## 1. Descripción del sistema

Plataforma web educativa tipo CMS para alojar y ejecutar **ejercicios interactivos** (HTML/CSS/JS autocontenidos) y **artículos de texto**, dirigidos a alumnado de infantil y primaria en España.

### Características principales
- Acceso público sin cuentas de alumno (sin registro de menores).
- Dos roles privilegiados: **admin** (configuración + contenidos) y **editor** (gestión de contenidos).
- Nombre, **logotipo** y paleta de colores configurables desde el panel de administración.
- Ejercicios ejecutados en iframe aislado con sandbox (sin acceso al origen padre).
- Artículos de texto con HTML sanitizado en servidor.
- Taxonomía configurable: ciclos, cursos y asignaturas (con asignaturas transversales / «Aula Abierta»).

---

## 2. Arquitectura

### 2.1 Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic |
| Base de datos | SQLite en modo WAL |
| Autenticación | Argon2id (contraseñas), JWT HS256 (sesiones) |
| Frontend | React 18, TypeScript strict, Vite 4 |
| Cliente API | openapi-typescript + openapi-fetch |
| Estado servidor | TanStack Query v5 |
| Enrutamiento | React Router v6 |

### 2.2 Regla de dependencia

```
infrastructure → application → domain
```

El dominio no importa FastAPI, SQLAlchemy ni Pydantic de request. Jamás. La comunicación entre
contextos es solo vía casos de uso de aplicación o eventos de dominio.

### 2.3 Contextos acotados

| Contexto | Responsabilidad |
|---|---|
| `identity` | Usuarios (admin/editor), login JWT, guardas de rol |
| `content` | CRUD, versionado inmutable, papelera, artículos de texto + ejercicios HTML |
| `taxonomy` | Ciclos, cursos y asignaturas (con flag transversal → «Aula Abierta») |
| `configuration` | Configuración del sitio: nombre, fuente, fondo, **logo**, paleta y paletas |
| `media` | Subida de imágenes (artículos y logo): raster, content-addressed, servidas con nosniff |

---

## 3. API REST — Referencia de endpoints

Base URL: `http://localhost:8001/api/v1`

### 3.1 Autenticación

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/auth/token` | — | Login. Body: `username` + `password` (form). Devuelve JWT. |

### 3.2 Usuarios (`/users/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/users/` | admin | Listar todos los usuarios |
| POST | `/users/` | admin | Crear usuario |

### 3.3 Contenidos (`/contenidos/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/contenidos/` | — | Listar contenidos publicados (catálogo público) |
| GET | `/contenidos/{id}` | — | Obtener contenido por ID |
| POST | `/contenidos/` | editor+ | Crear contenido (el `body_html` de tipo `texto` se sanea) |
| PUT | `/contenidos/{id}` | editor+ | Actualizar contenido (re-sanea el `body_html` de `texto`) |
| POST | `/contenidos/{id}/html` | editor+ | Subir el HTML de un ejercicio interactivo (multipart) |
| POST | `/contenidos/{id}/publicar` | editor+ | Publicar |
| DELETE | `/contenidos/{id}` | editor+ | Borrado lógico (papelera) |
| POST | `/contenidos/{id}/restaurar` | editor+ | Restaurar desde papelera |
| DELETE | `/contenidos/{id}/purgar` | admin | Eliminar definitivamente (desde papelera) |
| GET | `/admin/contenidos/` | admin | Listar todos (incluye borradores y papelera) |

### 3.4 Media (`/media/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/media/imagenes` | editor+ | Subir imagen (multipart, raster: PNG/JPG/GIF/WebP, máx. 5 MB). Devuelve `{ "url": "/media/images/<sha256>.<ext>" }`. Se usa para imágenes de artículos **y para el logo del sitio**. |

### 3.5 Taxonomía (`/taxonomy/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/taxonomy/ciclos` | — | Listar ciclos |
| POST/PUT/DELETE | `/taxonomy/ciclos[/{id}]` | admin | CRUD de ciclos |
| GET | `/taxonomy/cursos` | — | Listar cursos (filtrar con `?ciclo_id=`) |
| POST/PUT/DELETE | `/taxonomy/cursos[/{id}]` | admin | CRUD de cursos |
| GET | `/taxonomy/asignaturas` | — | Listar asignaturas (incluye flag `transversal`) |
| POST/PUT/DELETE | `/taxonomy/asignaturas[/{id}]` | admin | CRUD de asignaturas |

### 3.6 Configuración (`/config/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/config/` | — | Obtener configuración (nombre, fuente, fondo, **logo**, Aula Abierta, paleta + paletas) |
| PUT | `/config/general` | admin | Cambiar nombre, fuente, fondo, **logo** y etiqueta/emoji de Aula Abierta |
| PUT | `/config/paleta` | admin | Activar una paleta (predefinida o personalizada) |
| POST | `/config/paletas` | admin | Crear paleta personalizada |
| PUT | `/config/paletas/{id}` | admin | Actualizar paleta personalizada |
| DELETE | `/config/paletas/{id}` | admin | Eliminar paleta personalizada |

**Respuesta GET /config/ (extracto):**
```json
{
  "nombre_sitio": "Plataforma Educativa",
  "fuente_activa": "sistema",
  "fondo_activo": "ninguno",
  "fondo_estilo": "ordenado",
  "logo_url": "/media/images/<sha256>.png",
  "aula_abierta_label": "Aula Abierta",
  "aula_abierta_emoji": "🌟",
  "paleta_activa": "cielo",
  "paletas_personalizadas": []
}
```

> El campo `logo_url` solo acepta referencias al propio origen (`/media/…`) o cadena vacía. Una URL
> externa se rechaza con `400`.

### 3.7 Mantenimiento — Copias de seguridad (`/admin/backups`) *(solo admin)*

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/admin/backups` | admin | Listar las copias de seguridad existentes |
| POST | `/admin/backups` | admin | Crear una copia de seguridad de la BD ahora (y rotar las antiguas) |
| GET | `/admin/backups/{nombre}` | admin | Descargar el fichero de una copia (adjunto) |
| POST | `/admin/export` | admin | Exportación completa BD+media (`.tar.gz`, adjunto) |

### 3.8 Origen sandbox (servidor aparte)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/ejercicio/{hash}` | — | Sirve el HTML del ejercicio con CSP estricta |
| GET | `/health` | — | Readiness del servidor sandbox |

---

## 4. Modelo de datos

### `site_config` (singleton)

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | VARCHAR(36) | PK (singleton fijo: `00000000-0000-0000-0000-000000000001`) |
| `nombre_sitio` | VARCHAR(255) | Nombre del sitio |
| `paleta_activa` | VARCHAR(100) | ID de la paleta activa |
| `paletas_json` | TEXT | JSON con paletas personalizadas |
| `fuente_activa` | VARCHAR(100) | ID de la fuente activa (default `sistema`) |
| `fondo_activo` | VARCHAR(100) | ID del fondo/estampado activo (default `ninguno`) |
| `fondo_estilo` | VARCHAR(100) | Disposición del estampado (default `ordenado`) |
| `logo_url` | VARCHAR(500) | **(V-0.12.0)** URL del logo en el propio origen (`/media/…`) o vacío |
| `aula_abierta_label` | VARCHAR(40) | Etiqueta de «Aula Abierta» (default `Aula Abierta`) |
| `aula_abierta_emoji` | VARCHAR(16) | Emoji de «Aula Abierta» (default `🌟`) |

Las tablas `user`, `content`, `content_version`, `ciclo`, `curso` y `asignatura` se mantienen sin
cambios respecto a V-0.11.0 (`asignatura.is_transversal` introducido en la migración `008`).

---

## 5. Guía de instalación y despliegue

### 5.1 Producción con Docker (Caddy + HTTPS)

Solo **Caddy** se expone a internet (80/443). `frontend`, `api` y `sandbox` son internos.

```bash
cd plataforma-educativa
cp .env.example .env
# Editar .env: APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin
docker compose up -d --build
docker compose logs -f caddy   # seguir la emisión de certificados
# Web: https://APP_DOMAIN
```

El entrypoint ejecuta `alembic upgrade head` (aplica la migración `010` en caliente) y crea el admin
inicial si no hay usuarios.

### 5.2 Desarrollo local

```bash
# Backend
cd backend && python -m alembic upgrade head
uvicorn app.main:app --reload --port 8001

# Frontend (otra terminal)
cd frontend && npm install && npm run dev   # http://localhost:5173
```

---

## 6. Manual de uso

### 6.1 Apariencia y ajustes — Logo del sitio *(novedad V-0.12.0)*

En **Apariencia → Ajustes generales**, sección **«Logo del sitio»** (justo bajo el nombre):

1. Pulsar **«Subir logo»** y elegir una imagen (PNG, JPG, GIF o WebP, máx. 5 MB). Se recomienda un
   PNG con fondo transparente.
2. Se muestra una **vista previa** del logo.
3. Pulsar **«Guardar cambios»** para aplicarlo. El logo aparece junto al nombre en la cabecera
   pública y en la barra lateral del panel admin.
4. Para retirarlo, pulsar **«Quitar»** y guardar; el sitio vuelve a mostrar solo el nombre.

> El logo se sube al propio servidor (no a un CDN externo) y se sirve de forma segura. Sin logo, la
> cabecera se ve igual que antes.

### 6.2 Resto de ajustes

El resto de la sección Apariencia (nombre del sitio, fuente de letra, fondo/estampado, «Aula Abierta»,
paletas predefinidas y personalizadas) funciona igual que en versiones anteriores.

### 6.3 Acceso público, contenidos, taxonomía y usuarios

Sin cambios respecto a V-0.11.0 (catálogo público navegable, panel de contenidos con CRUD y papelera,
taxonomía configurable, gestión de usuarios para admin).

---

## 7. Seguridad

- **Aislamiento del sandbox:** ejercicios en `<iframe sandbox="allow-scripts">` (sin
  `allow-same-origin`) servidos desde `sandbox.<dominio>` con CSP estricta.
- **Sanitización asimétrica:** HTML de artículos saneado siempre (nh3 + DOMPurify); HTML de
  ejercicios no saneado (se aísla en sandbox).
- **Logo / imágenes:** subidas raster (sin SVG), content-addressed, servidas con `nosniff`. El
  `logo_url` solo referencia el propio origen.
- **Protección de menores:** sin cuentas de alumno, sin cookies de seguimiento, sin perfilado (DSA art. 28).
- **Autenticación:** Argon2id + JWT HS256 con expiración.

---

## 8. Tests

```bash
cd backend
python -m pytest tests/unit tests/integration -q
# → 153 tests, todos deben pasar
```

Los 4 tests nuevos de V-0.12.0 cubren: valor por defecto de `logo_url` (vacío), actualización del
logo, retirada con cadena vacía y rechazo de una URL externa.

---

## 9. Roadmap

- **Hecho (V-0.12.0):** logo del sitio configurable.
- **Hecho (V-0.11.0):** asignaturas transversales / «Aula Abierta».
- **Siguiente:** buscador full-text (FTS5) en el catálogo público.
- **Más adelante:** contador de visitas (analytics), auditoría, UI de versionado/restauración de
  contenidos. Robustez: usuario no-root en el backend.
