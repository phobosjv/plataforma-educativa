# Manual Técnico y de Usuario — Plataforma Educativa V-0.14.0

**Fecha:** 2026-06-17  
**Versión:** V-0.14.0  
**Estado:** Desarrollo activo

---

## 0. Novedades de V-0.14.0

**Contador de visitas (contexto `analytics`).**

- **Conteo de visitas anónimas** de los contenidos. Al abrir la ficha de un contenido se registra una
  visita. El panel de administración muestra las **visitas totales** (Inicio) y las **visitas por
  contenido** (lista de Contenidos).
- **Diseño (CLAUDE.md §8):** las visitas se **agregan en memoria** (buffer de proceso, seguro para
  concurrencia) y se **vuelcan por lotes** a la BD mediante la tarea de mantenimiento (por defecto cada
  5 minutos) y al apagar la app. **Nunca** hay una escritura en BD por petición.
- **Privacidad (§10):** visitas anónimas y agregadas; solo se guarda un total por contenido, sin
  ningún dato del visitante.
- Endpoints: `POST /api/v1/analytics/visitas/{id}` (público; solo incrementa el buffer en memoria) y
  `GET /api/v1/analytics/visitas` (solo admin; total + desglose por contenido).
- Nueva tabla `content_views` (UPSERT acumulativo). Migración Alembic `012`.
- 176 tests backend (12 nuevos) + 9 E2E en verde. API → `0.14.0`.

### Versiones recientes
- **V-0.13.0** — Buscador del catálogo (full-text, FTS5).
- **V-0.12.0** — Logo del sitio configurable.

---

## 1. Descripción del sistema

Plataforma web educativa tipo CMS para alojar y ejecutar **ejercicios interactivos** (HTML/CSS/JS autocontenidos) y **artículos de texto**, dirigidos a alumnado de infantil y primaria en España.

### Características principales
- Acceso público sin cuentas de alumno (sin registro de menores).
- Dos roles privilegiados: **admin** (configuración + contenidos) y **editor** (gestión de contenidos).
- Nombre, **logotipo** y paleta de colores configurables desde el panel de administración.
- **Buscador del catálogo** (full-text) por título, descripción y etiquetas.
- **Contador de visitas** anónimas y agregadas por contenido.
- Ejercicios ejecutados en iframe aislado con sandbox; artículos con HTML sanitizado en servidor.
- Taxonomía configurable: ciclos, cursos y asignaturas (con asignaturas transversales / «Aula Abierta»).

---

## 2. Arquitectura

### 2.1 Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic |
| Base de datos | SQLite en modo WAL (búsqueda con FTS5) |
| Autenticación | Argon2id (contraseñas), JWT HS256 (sesiones) |
| Frontend | React 18, TypeScript strict, Vite 4 |
| Cliente API | openapi-typescript + openapi-fetch |
| Estado servidor | TanStack Query v5 |

### 2.2 Regla de dependencia

```
infrastructure → application → domain
```

El dominio no importa FastAPI, SQLAlchemy ni Pydantic de request. Jamás.

### 2.3 Contextos acotados

| Contexto | Responsabilidad |
|---|---|
| `identity` | Usuarios (admin/editor), login JWT, guardas de rol |
| `content` | CRUD, versionado, papelera, artículos + ejercicios, búsqueda FTS5 |
| `taxonomy` | Ciclos, cursos y asignaturas (con flag transversal → «Aula Abierta») |
| `configuration` | Configuración del sitio: nombre, fuente, fondo, logo, paleta y paletas |
| `media` | Subida de imágenes (artículos y logo): raster, content-addressed, nosniff |
| `analytics` | **Contador de visitas:** buffer en memoria + volcado por lotes a `content_views` |

---

## 3. API REST — Referencia de endpoints

Base URL: `http://localhost:8001/api/v1`

### 3.1 Analytics — visitas (`/analytics/`) *(V-0.14.0)*

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/analytics/visitas/{id}` | — | Registra una visita anónima (solo incrementa el buffer en memoria; no escribe en BD) |
| GET | `/analytics/visitas` | admin | Total de visitas + desglose por contenido (lo ya volcado a la BD) |

**Respuesta GET /analytics/visitas:**
```json
{ "total": 128, "por_contenido": { "<id>": 90, "<id>": 38 } }
```

### 3.2 Contenidos (`/contenidos/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/contenidos/` | — | Listar contenidos publicados (catálogo público) |
| GET | `/contenidos/buscar?q=` | — | Buscar por título/descripción/etiquetas (FTS5). Máx. 50, por relevancia |
| GET | `/contenidos/{id}` | — | Obtener contenido por ID |
| POST | `/contenidos/` | editor+ | Crear contenido (el `body_html` de tipo `texto` se sanea) |
| PUT | `/contenidos/{id}` | editor+ | Actualizar contenido (re-sanea el `body_html` de `texto`) |
| POST | `/contenidos/{id}/html` | editor+ | Subir el HTML de un ejercicio interactivo (multipart) |
| POST | `/contenidos/{id}/publicar` | editor+ | Publicar |
| DELETE | `/contenidos/{id}` | editor+ | Borrado lógico (papelera) |
| POST | `/contenidos/{id}/restaurar` | editor+ | Restaurar desde papelera |
| DELETE | `/contenidos/{id}/purgar` | admin | Eliminar definitivamente (desde papelera) |
| GET | `/admin/contenidos/` | admin | Listar todos (incluye borradores y papelera) |

### 3.3 Resto

Sin cambios respecto a V-0.13.0: `/media/imagenes`, `/taxonomy/*`, `/config/*`, `/admin/backups` +
`/admin/export`, y el origen sandbox (`/ejercicio/{hash}`, `/health`).

---

## 4. Modelo de datos

### Tabla `content_views` *(V-0.14.0)*

| Columna | Tipo | Descripción |
|---|---|---|
| `content_id` | VARCHAR | PK. ID del contenido visitado (no FK: si se purga, la fila queda huérfana, inocua) |
| `total` | INTEGER | Total acumulado de visitas |
| `updated_at` | DATETIME | Último volcado que la modificó |

El volcado usa `INSERT ... ON CONFLICT(content_id) DO UPDATE SET total = total + n`: crea la fila la
primera vez y **acumula** en los volcados sucesivos. El resto de tablas se mantienen como en V-0.13.0
(incluida la tabla virtual FTS5 `content_fts`).

---

## 5. Guía de instalación y despliegue

### 5.1 Producción con Docker (Caddy + HTTPS)

```bash
cd plataforma-educativa
cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin
docker compose up -d --build
docker compose logs -f caddy
# Web: https://APP_DOMAIN
```

El entrypoint ejecuta `alembic upgrade head` (la migración `012` crea `content_views`). Ajustes
opcionales del contador en `.env`: `ANALYTICS_ENABLED` (default `true`) y
`ANALYTICS_FLUSH_INTERVAL_SECONDS` (default `300`).

### 5.2 Desarrollo local

```bash
cd backend && python -m alembic upgrade head
uvicorn app.main:app --reload --port 8001

cd frontend && npm install && npm run dev   # http://localhost:5173
```

---

## 6. Manual de uso

### 6.1 Contador de visitas *(novedad V-0.14.0)*

- Cada vez que un visitante abre la ficha de un contenido (ejercicio o artículo), se cuenta **una
  visita**. No se registra ningún dato de la persona: es un simple contador anónimo.
- En el panel de administración:
  - **Inicio:** tarjeta «Visitas totales» con la suma de todas las visitas.
  - **Contenidos:** columna «Visitas» con el total de cada contenido.
- Los números se actualizan por lotes (no al instante): el sistema acumula las visitas y las guarda
  cada pocos minutos, para no sobrecargar la base de datos. Tras un repunte de visitas, el panel puede
  tardar un momento en reflejarlas.

### 6.2 Resto del panel

Acceso público (catálogo navegable + buscador), Contenidos (CRUD + papelera), Taxonomía, Apariencia
(nombre, logo, fuente, fondo, paletas, Aula Abierta) y Usuarios (solo admin) funcionan igual que en
V-0.13.0.

---

## 7. Seguridad y privacidad

- **Aislamiento del sandbox:** ejercicios en `<iframe sandbox="allow-scripts">` (sin
  `allow-same-origin`), servidos desde `sandbox.<dominio>` con CSP estricta.
- **Sanitización asimétrica:** HTML de artículos saneado siempre (nh3 + DOMPurify); el de ejercicios
  no se sanea (se aísla en sandbox).
- **Visitas:** anónimas y agregadas; solo un total por contenido, sin IP ni identificadores. La lectura
  del desglose es solo para admin. Sin cookies de seguimiento ni perfilado (DSA art. 28).
- **Autenticación:** Argon2id + JWT HS256 con expiración.

---

## 8. Tests

```bash
cd backend
python -m pytest tests/unit tests/integration -q   # 176 tests

cd frontend
npm run test:e2e   # 9 flujos E2E (Playwright)
```

Los 12 tests nuevos del contador cubren: acumulación y drenaje del buffer, volcado por lotes (con
acumulación entre volcados), consulta del total/desglose, el beacon público sin escritura en BD, la
guarda de admin en la lectura y la validación del id.

---

## 9. Roadmap

- **Hecho (V-0.14.0):** contador de visitas (contexto `analytics`).
- **Hecho (V-0.13.0):** buscador full-text (FTS5) del catálogo.
- **Siguiente:** auditoría (contexto `auditing`) de acciones de admin/editor.
- **Más adelante:** UI de versionado/restauración de contenidos. Robustez: usuario no-root en el backend.
