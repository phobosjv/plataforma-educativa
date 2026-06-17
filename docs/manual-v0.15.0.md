# Manual Técnico y de Usuario — Plataforma Educativa V-0.15.0

**Fecha:** 2026-06-17  
**Versión:** V-0.15.0  
**Estado:** Desarrollo activo

---

## 0. Novedades de V-0.15.0

**Auditoría de acciones de gestión (contexto `auditing`).**

- **Registro de auditoría** de todas las acciones de admin/editor: quién hizo qué, sobre qué objeto y
  cuándo. Cubre **contenidos** (crear/editar/publicar/borrar/restaurar/purgar/subir HTML), **usuarios**,
  **taxonomía** (ciclos/cursos/asignaturas) y **configuración** (ajustes y paletas).
- **Página «Auditoría»** en el panel de administración (solo admin): lista de acciones recientes con
  fecha, usuario (email + rol), acción y detalle.
- Endpoint `GET /api/v1/auditoria` (solo admin, paginado). El registro es **append-only** y se
  **conserva indefinidamente** (sin purga automática).
- **Diseño:** la auditoría se escribe en la capa API tras cada acción con éxito, con la misma sesión de
  la petición; es **a prueba de fallos** (si fallara, nunca tumba la acción real del usuario).
- Nueva tabla `audit_log`. Migración Alembic `013`.
- 186 tests backend (10 nuevos) + 9 E2E en verde. API → `0.15.0`.

### Versiones recientes
- **V-0.14.0** — Contador de visitas (contexto `analytics`).
- **V-0.13.0** — Buscador del catálogo (full-text, FTS5).

---

## 1. Descripción del sistema

Plataforma web educativa tipo CMS para alojar y ejecutar **ejercicios interactivos** (HTML/CSS/JS autocontenidos) y **artículos de texto**, dirigidos a alumnado de infantil y primaria en España.

### Características principales
- Acceso público sin cuentas de alumno (sin registro de menores).
- Dos roles privilegiados: **admin** (configuración + contenidos) y **editor** (gestión de contenidos).
- Nombre, **logotipo** y paleta de colores configurables desde el panel de administración.
- **Buscador del catálogo** (full-text) por título, descripción y etiquetas.
- **Contador de visitas** anónimas y agregadas por contenido.
- **Auditoría** de todas las acciones de gestión (quién, qué, cuándo).
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
| `analytics` | Contador de visitas: buffer en memoria + volcado por lotes |
| `auditing` | **Registro de acciones de gestión (append-only) + consulta para admin** |

---

## 3. API REST — Referencia de endpoints

Base URL: `http://localhost:8001/api/v1`

### 3.1 Auditoría (`/auditoria`) *(V-0.15.0)*

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/auditoria?limite=&offset=` | admin | Acciones registradas, más recientes primero (paginado) |

**Respuesta:**
```json
{
  "total": 42,
  "entradas": [
    {
      "id": "<uuid>", "usuario_id": "<uuid>", "usuario_email": "editor@cole.es",
      "usuario_rol": "editor", "accion": "publicar", "entidad": "contenido",
      "entidad_id": "<uuid>", "detalle": "El mapa de España", "created_at": "..."
    }
  ]
}
```

### 3.2 Resto

Sin cambios respecto a V-0.14.0: contenidos (`/contenidos/*` incl. `/buscar`), `/analytics/visitas`,
`/media/imagenes`, `/taxonomy/*`, `/config/*`, `/admin/backups` + `/admin/export`, y el origen sandbox.

---

## 4. Modelo de datos

### Tabla `audit_log` *(V-0.15.0)*

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | VARCHAR | PK (UUID) |
| `usuario_id` | VARCHAR | ID del autor de la acción (nullable) |
| `usuario_email` | VARCHAR | Email del autor (copia, para trazabilidad histórica) |
| `usuario_rol` | VARCHAR | Rol del autor (`admin`/`editor`) |
| `accion` | VARCHAR | `crear`, `editar`, `publicar`, `borrar`, `restaurar`, `purgar`, `subir_html`, … |
| `entidad` | VARCHAR | `contenido`, `usuario`, `ciclo`, `curso`, `asignatura`, `configuracion` |
| `entidad_id` | VARCHAR | ID del objeto afectado (nullable) |
| `detalle` | VARCHAR | Texto libre (p. ej. el título o nombre) |
| `created_at` | DATETIME | Fecha de la acción (indexada) |

Append-only: no se edita ni se borra desde la aplicación. El resto de tablas se mantienen como en
V-0.14.0 (incluida `content_views` y la tabla virtual FTS5 `content_fts`).

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

El entrypoint ejecuta `alembic upgrade head` (la migración `013` crea `audit_log`).

### 5.2 Desarrollo local

```bash
cd backend && python -m alembic upgrade head
uvicorn app.main:app --reload --port 8001

cd frontend && npm install && npm run dev   # http://localhost:5173
```

---

## 6. Manual de uso

### 6.1 Auditoría *(novedad V-0.15.0)*

- En el panel de administración, sección **«Auditoría»** (solo admin), se ve el registro de las
  acciones de gestión más recientes: **fecha, usuario, acción y detalle**.
- Se registra automáticamente cada vez que un admin o editor crea, edita, publica, borra, restaura o
  elimina contenidos; crea usuarios; gestiona la taxonomía; o cambia la configuración.
- El registro **no se borra** con el tiempo: queda como historial permanente.
- Las acciones que fallan (por ejemplo, borrar algo que no existe) **no** generan entrada.

### 6.2 Resto del panel

Acceso público (catálogo navegable + buscador), Contenidos (CRUD + papelera + visitas), Taxonomía,
Apariencia (nombre, logo, fuente, fondo, paletas, Aula Abierta) y Usuarios (solo admin) funcionan
igual que en V-0.14.0.

---

## 7. Seguridad y privacidad

- **Aislamiento del sandbox:** ejercicios en `<iframe sandbox="allow-scripts">` (sin
  `allow-same-origin`), servidos desde `sandbox.<dominio>` con CSP estricta.
- **Sanitización asimétrica:** HTML de artículos saneado siempre (nh3 + DOMPurify); el de ejercicios
  no se sanea (se aísla en sandbox).
- **Auditoría:** el registro guarda el email/rol del autor de cada acción de gestión, para
  trazabilidad. Solo admin puede consultarlo. No registra acciones de visitantes anónimos.
- **Privacidad de menores:** sin cuentas de alumno, sin cookies de seguimiento, visitas anónimas, sin
  perfilado (DSA art. 28).
- **Autenticación:** Argon2id + JWT HS256 con expiración.

---

## 8. Tests

```bash
cd backend
python -m pytest tests/unit tests/integration -q   # 186 tests

cd frontend
npm run test:e2e   # 9 flujos E2E (Playwright)
```

Los 10 tests nuevos de auditoría cubren: el registro y la consulta (orden/paginación), que una acción
de gestión (contenido, taxonomía, configuración) deja entrada con el autor correcto, que las acciones
fallidas no se registran, y las guardas de admin del endpoint de consulta.

---

## 9. Roadmap

- **Hecho (V-0.15.0):** auditoría de acciones de gestión (contexto `auditing`).
- **Hecho (V-0.14.0):** contador de visitas (contexto `analytics`).
- **Siguiente:** enlaces de donación configurables; publicidad en márgenes (solo zona pública);
  frases del catálogo configurables desde admin.
- **Más adelante:** UI de versionado/restauración de contenidos. Robustez: usuario no-root en el backend.
