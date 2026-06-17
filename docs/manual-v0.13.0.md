# Manual Técnico y de Usuario — Plataforma Educativa V-0.13.0

**Fecha:** 2026-06-17  
**Versión:** V-0.13.0  
**Estado:** Desarrollo activo

---

## 0. Novedades de V-0.13.0

**Buscador del catálogo (full-text, FTS5).**

- **Cuadro de búsqueda** en la portada del catálogo que encuentra contenidos por **título,
  descripción y etiquetas**. Resultados ordenados por relevancia, con su propia pantalla
  (estado en la URL `?q=`) y un mensaje claro cuando no hay coincidencias.
- **Pensado para niños:** ignora acentos en ambos sentidos (buscar «espana» encuentra «España»),
  busca por **prefijo** (escribir «mapa» encuentra «mapas») y combina varios términos en AND.
- Nuevo endpoint público `GET /api/v1/contenidos/buscar?q=…` (sin autenticación; solo contenido
  publicado y no borrado; máximo 50 resultados).
- **Persistencia:** tabla virtual **FTS5** `content_fts` (contenido externo sobre `content`,
  tokenizer `unicode61 remove_diacritics 2`) mantenida por **triggers** de alta/baja/modificación.
  Migración Alembic `011`. El DDL se centraliza en `content/infrastructure/fts.py`.
- 164 tests backend (11 nuevos) + 9 E2E (2 nuevos del buscador) en verde. API → `0.13.0`.

### Versiones recientes
- **V-0.12.0** — Logo del sitio configurable.
- **V-0.11.0** — Asignaturas transversales / «Aula Abierta».

---

## 1. Descripción del sistema

Plataforma web educativa tipo CMS para alojar y ejecutar **ejercicios interactivos** (HTML/CSS/JS autocontenidos) y **artículos de texto**, dirigidos a alumnado de infantil y primaria en España.

### Características principales
- Acceso público sin cuentas de alumno (sin registro de menores).
- Dos roles privilegiados: **admin** (configuración + contenidos) y **editor** (gestión de contenidos).
- Nombre, **logotipo** y paleta de colores configurables desde el panel de administración.
- **Buscador del catálogo** (full-text) por título, descripción y etiquetas.
- Ejercicios ejecutados en iframe aislado con sandbox (sin acceso al origen padre).
- Artículos de texto con HTML sanitizado en servidor.
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
| `content` | CRUD, versionado inmutable, papelera, artículos + ejercicios, **búsqueda FTS5** |
| `taxonomy` | Ciclos, cursos y asignaturas (con flag transversal → «Aula Abierta») |
| `configuration` | Configuración del sitio: nombre, fuente, fondo, logo, paleta y paletas |
| `media` | Subida de imágenes (artículos y logo): raster, content-addressed, servidas con nosniff |

---

## 3. API REST — Referencia de endpoints

Base URL: `http://localhost:8001/api/v1`

### 3.1 Contenidos (`/contenidos/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/contenidos/` | — | Listar contenidos publicados (catálogo público) |
| GET | `/contenidos/buscar?q=` | — | **(V-0.13.0)** Buscar por título/descripción/etiquetas (FTS5). Máx. 50, por relevancia |
| GET | `/contenidos/{id}` | — | Obtener contenido por ID |
| POST | `/contenidos/` | editor+ | Crear contenido (el `body_html` de tipo `texto` se sanea) |
| PUT | `/contenidos/{id}` | editor+ | Actualizar contenido (re-sanea el `body_html` de `texto`) |
| POST | `/contenidos/{id}/html` | editor+ | Subir el HTML de un ejercicio interactivo (multipart) |
| POST | `/contenidos/{id}/publicar` | editor+ | Publicar |
| DELETE | `/contenidos/{id}` | editor+ | Borrado lógico (papelera) |
| POST | `/contenidos/{id}/restaurar` | editor+ | Restaurar desde papelera |
| DELETE | `/contenidos/{id}/purgar` | admin | Eliminar definitivamente (desde papelera) |
| GET | `/admin/contenidos/` | admin | Listar todos (incluye borradores y papelera) |

> El endpoint `/contenidos/buscar` se declara **antes** de `/contenidos/{id}` para que el segmento
> `buscar` no se interprete como un UUID. Una `q` vacía o sin términos útiles devuelve `[]`.

### 3.2 Media, Taxonomía, Configuración, Mantenimiento

Sin cambios respecto a V-0.12.0: `POST /media/imagenes` (subida raster para artículos y logo),
`/taxonomy/*` (CRUD de ciclos/cursos/asignaturas), `/config/*` (nombre, fuente, fondo, logo, Aula
Abierta, paletas) y `/admin/backups` + `/admin/export` (copias y exportación, solo admin).

### 3.3 Origen sandbox (servidor aparte)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/ejercicio/{hash}` | — | Sirve el HTML del ejercicio con CSP estricta |
| GET | `/health` | — | Readiness del servidor sandbox |

---

## 4. Modelo de datos

### Índice de búsqueda `content_fts` *(V-0.13.0)*

Tabla virtual **FTS5** de **contenido externo** sobre `content`:

```sql
CREATE VIRTUAL TABLE content_fts USING fts5(
  titulo, descripcion, tags_json,
  content='content', content_rowid='rowid',
  tokenize='unicode61 remove_diacritics 2'
);
```

- No duplica los datos: lee de `content` por `rowid`.
- Se mantiene con **triggers** `content_fts_ai` (insert), `content_fts_ad` (delete) y
  `content_fts_au` (update). El índice queda siempre sincronizado, sea cual sea la ruta de escritura.
- La consulta une `content_fts` con `content` para aplicar la visibilidad (publicado, no borrado) y
  ordenar por `rank`. El texto del usuario se convierte en una consulta segura (`"término"*` por cada
  palabra), que neutraliza los operadores de FTS5 y busca por prefijo en AND.

El resto de tablas (`user`, `content`, `content_version`, `ciclo`, `curso`, `asignatura`,
`site_config`) se mantienen como en V-0.12.0 (`site_config.logo_url` de la migración `010`).

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

El entrypoint ejecuta `alembic upgrade head`: la migración `011` crea la tabla `content_fts` y, con
el comando `'rebuild'`, **indexa el contenido ya existente** (sin pérdida ni pasos manuales).

### 5.2 Desarrollo local

```bash
cd backend && python -m alembic upgrade head
uvicorn app.main:app --reload --port 8001

cd frontend && npm install && npm run dev   # http://localhost:5173
```

---

## 6. Manual de uso

### 6.1 Buscar en el catálogo *(novedad V-0.13.0)*

En la portada (`/`) hay un **cuadro de búsqueda**:

1. Escribir una o varias palabras (p. ej. «mapa», «sumas», «comunidades»). No hace falta poner tildes.
2. Pulsar **«Buscar»** (o Enter).
3. Aparece la pantalla de **resultados**, ordenados por relevancia. Cada tarjeta abre su contenido.
4. Si no hay coincidencias, se muestra un mensaje para probar con otra palabra.
5. La búsqueda queda en la dirección (`?q=…`), así que se puede compartir o recargar.

La búsqueda mira en el **título, la descripción y las etiquetas** del contenido publicado. Busca por
**prefijo** (escribir «mapa» también encuentra «mapas») y, con varias palabras, exige que aparezcan
todas.

### 6.2 Resto del panel

Acceso público (catálogo navegable curso → asignatura), Contenidos (CRUD + papelera), Taxonomía,
Apariencia (nombre, **logo**, fuente, fondo, paletas, Aula Abierta) y Usuarios (solo admin) funcionan
igual que en V-0.12.0.

---

## 7. Seguridad

- **Aislamiento del sandbox:** ejercicios en `<iframe sandbox="allow-scripts">` (sin
  `allow-same-origin`) servidos desde `sandbox.<dominio>` con CSP estricta.
- **Sanitización asimétrica:** HTML de artículos saneado siempre (nh3 + DOMPurify); HTML de
  ejercicios no saneado (se aísla en sandbox).
- **Búsqueda:** la consulta FTS5 se construye entrecomillando cada término, de modo que lo que escriba
  el usuario no puede inyectar operadores ni provocar errores de sintaxis.
- **Protección de menores:** sin cuentas de alumno, sin cookies de seguimiento, sin perfilado (DSA art. 28).
- **Autenticación:** Argon2id + JWT HS256 con expiración.

---

## 8. Tests

```bash
cd backend
python -m pytest tests/unit tests/integration -q   # 164 tests

cd frontend
npm run test:e2e   # 9 flujos E2E (Playwright), incl. buscar y seguridad del sandbox
```

Los 11 tests nuevos de búsqueda cubren: prefijo, acentos en ambos sentidos, búsqueda por descripción
y etiqueta, AND de varios términos, exclusión de no publicados y de borrados, sincronización al editar
(trigger UPDATE), consulta vacía, sin coincidencias y robustez ante caracteres especiales.

---

## 9. Roadmap

- **Hecho (V-0.13.0):** buscador full-text (FTS5) del catálogo.
- **Hecho (V-0.12.0):** logo del sitio configurable.
- **Siguiente:** contador de visitas (contexto `analytics`).
- **Más adelante:** auditoría (`auditing`), UI de versionado/restauración de contenidos. Robustez:
  usuario no-root en el backend.
