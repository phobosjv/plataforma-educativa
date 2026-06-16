# Manual Técnico y de Usuario — Plataforma Educativa V-0.10.1

**Fecha:** 2026-06-16  
**Versión:** V-0.10.1  
**Estado:** Desarrollo activo

---

## 0. Novedades de V-0.10.1

**Seguridad de las imágenes Docker.**

- **Backend** (`backend/Dockerfile`): base `python:3.12-slim` → **`python:3.12-slim-bookworm`**
  (release de Debian explícita) y **parches de seguridad del SO** en el build (`apt-get upgrade -y`),
  que aplican las correcciones de Debian publicadas después de la imagen base (el grueso de los
  hallazgos del escáner). Se actualizan `pip`/`setuptools`/`wheel` (versiones antiguas son un
  hallazgo recurrente). Limpieza de listas apt en la capa final.
- **Frontend** (`frontend/Dockerfile`): etapa final `nginx:alpine` con `apk upgrade --no-cache`.
- **Nueva guía** `docs/seguridad-imagenes.md`: cómo **escanear** las imágenes ya construidas (Trivy,
  `--ignore-unfixed`), fijar la base por **digest** y endurecimiento pendiente (usuario no-root,
  revisión de `python-jose`).
- **Sin cambios de código, API ni esquema:** 123 tests siguen en verde. Al desplegar no hace falta
  nada especial; el endurecimiento se aplica solo al reconstruir las imágenes.

### Versiones recientes
- **V-0.10.0** — Robustez: backups automáticos de la BD + purga programada de papelera + panel admin.
- **V-0.9.0** — Producción: HTTPS automático con Caddy (Let's Encrypt) + sandbox en subdominio.
---

## 1. Descripción del sistema

Plataforma web educativa tipo CMS para alojar y ejecutar **ejercicios interactivos** (HTML/CSS/JS autocontenidos) y **artículos de texto**, dirigidos a alumnado de infantil y primaria en España.

### Características principales
- Acceso público sin cuentas de alumno (sin registro de menores).
- Dos roles privilegiados: **admin** (configuración + contenidos) y **editor** (gestión de contenidos).
- Nombre, logotipo y paleta de colores configurables desde el panel de administración.
- Ejercicios ejecutados en iframe aislado con sandbox (sin acceso al origen padre).
- Artículos de texto con HTML sanitizado en servidor.
- Búsqueda full-text (FTS5) sobre contenidos publicados.
- Taxonomía configurable: ciclos, cursos y asignaturas.

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

### 2.2 Arquitectura del backend

```
backend/app/
├── contexts/
│   ├── identity/          # Usuarios y autenticación
│   │   ├── domain/        # Usuario, Rol, AuthService (puerto)
│   │   ├── application/   # LoginHandler, CrearUsuarioHandler, ListarUsuariosHandler
│   │   ├── infrastructure/# SqlAlchemyUsuarioRepository, ArgonAuthService, JWTAuthService
│   │   └── api/           # /api/v1/auth/, /api/v1/users/
│   ├── content/           # Contenidos educativos
│   │   ├── domain/        # Contenido, ContentVersion, HtmlStorage (puerto)
│   │   ├── application/   # CRUD handlers
│   │   ├── infrastructure/# SqlAlchemy repos, FileSystemHtmlStorage
│   │   └── api/           # /api/v1/contenidos/
│   ├── taxonomy/          # Ciclos, cursos, asignaturas
│   │   ├── domain/        # Ciclo, Curso, Asignatura y puertos
│   │   ├── application/   # CRUD handlers para las 3 entidades
│   │   ├── infrastructure/# Repositorios SQLAlchemy
│   │   └── api/           # /api/v1/taxonomy/
│   └── configuration/     # Apariencia del sitio
│       ├── domain/        # ConfiguracionSitio, PaletaPersonalizada
│       ├── application/   # Handlers para paletas
│       ├── infrastructure/# SqlAlchemyConfiguracionRepository
│       └── api/           # /api/v1/config/
├── shared/
│   ├── domain/base.py     # DomainError, NotFoundError, AuthorizationError
│   ├── infrastructure/    # database.py (SQLite WAL), unit_of_work.py
│   └── application/       # (reservado)
├── bootstrap.py           # Registro de modelos ORM
├── main.py                # App FastAPI, inclusión de routers
└── config.py              # Settings (Pydantic BaseSettings)
```

### 2.3 Regla de dependencia

```
infrastructure → application → domain
```

El dominio no importa FastAPI, SQLAlchemy ni Pydantic de request. Jamás.

### 2.4 Arquitectura del frontend

```
frontend/src/
├── app/
│   ├── App.tsx             # Router principal, QueryClientProvider
│   ├── auth/               # AuthContext, RequireAuth
│   └── config/             # palettes.ts, useConfig.ts
├── pages/
│   ├── CatalogoPage.tsx    # Listado público de contenidos
│   ├── ContenidoPage.tsx   # Visualización (iframe o texto)
│   ├── LoginPage.tsx       # Formulario de login
│   └── admin/
│       ├── DashboardPage.tsx
│       ├── ContenidosPage.tsx
│       ├── TaxonomiaPage.tsx
│       ├── UsuariosPage.tsx
│       └── ConfiguracionPage.tsx
├── shared/
│   ├── api/
│   │   ├── client.ts       # openapi-fetch (baseUrl relativo + proxy /api en dev)
│   │   └── schema.d.ts     # Tipos generados desde OpenAPI
│   └── ui/
│       ├── PublicLayout.tsx
│       └── AdminLayout.tsx
└── styles/
    └── tokens.css          # Design system (CSS custom properties)
```

---

## 3. API REST — Referencia de endpoints

Base URL: `http://localhost:8001/api/v1`

### 3.1 Autenticación

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/auth/token` | — | Login. Body: `username` + `password` (form). Devuelve JWT. |

**Respuesta de login:**
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer",
  "rol": "admin"
}
```

### 3.2 Usuarios (`/users/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/users/` | admin | Listar todos los usuarios |
| POST | `/users/` | admin | Crear usuario |

**Crear usuario (body JSON):**
```json
{
  "email": "editor@ejemplo.com",
  "password": "MiPassword123",
  "nombre": "Nombre Editor",
  "rol": "editor"
}
```

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
| GET | `/admin/contenidos/` | admin | Listar todos (incluye borradores y papelera) |

**Tipos de contenido:**
- `interactivo` — referencia a fichero HTML por SHA-256. Se sube con `POST /contenidos/{id}/html` y se sirve desde el origen sandbox; la respuesta incluye `sandbox_url`.
- `texto` — campo `body_html` sanitizado con nh3 (servidor) y DOMPurify (cliente).

### 3.4 Taxonomía (`/taxonomy/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/taxonomy/ciclos` | — | Listar ciclos |
| POST | `/taxonomy/ciclos` | admin | Crear ciclo |
| PUT | `/taxonomy/ciclos/{id}` | admin | Actualizar ciclo |
| DELETE | `/taxonomy/ciclos/{id}` | admin | Eliminar ciclo |
| GET | `/taxonomy/cursos` | — | Listar cursos (filtrar con `?ciclo_id=`) |
| POST | `/taxonomy/cursos` | admin | Crear curso |
| PUT | `/taxonomy/cursos/{id}` | admin | Actualizar curso |
| DELETE | `/taxonomy/cursos/{id}` | admin | Eliminar curso |
| GET | `/taxonomy/asignaturas` | — | Listar asignaturas |
| POST | `/taxonomy/asignaturas` | admin | Crear asignatura |
| PUT | `/taxonomy/asignaturas/{id}` | admin | Actualizar asignatura |
| DELETE | `/taxonomy/asignaturas/{id}` | admin | Eliminar asignatura |

### 3.5 Configuración (`/config/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/config/` | — | Obtener configuración (nombre, fuente, fondo, paleta activa + paletas) |
| PUT | `/config/general` | admin | Cambiar nombre del sitio y fuente de letra |
| PUT | `/config/paleta` | admin | Activar una paleta (predefinida o personalizada) |
| POST | `/config/paletas` | admin | Crear paleta personalizada |
| PUT | `/config/paletas/{id}` | admin | Actualizar paleta personalizada |
| DELETE | `/config/paletas/{id}` | admin | Eliminar paleta personalizada |

> **Nota de la V-0.5.0:** estos endpoints crean la fila singleton de configuración de forma
> idempotente (get-or-create con *flush*). La primera escritura sobre una base de datos sin
> configuración previa ya **no** produce error 500.

**Respuesta GET /config/:**
```json
{
  "nombre_sitio": "Plataforma Educativa",
  "paleta_activa": "cielo",
  "paletas_personalizadas": [
    {
      "id": "mi-paleta",
      "nombre": "Mi Paleta",
      "bg": "#f0f4ff",
      "surface": "#ffffff",
      "fg": "#1a1a2e",
      "primary": "#6366f1"
    }
  ]
}
```

**Paletas predefinidas disponibles:**

| ID | Nombre | Descripción |
|---|---|---|
| `cielo` | Cielo Azul | Tonos azules claros |
| `bosque` | Bosque Mágico | Tonos verdes naturales |
| `coral` | Coral Feliz | Tonos rosas y rojos suaves |
| `sol` | Sol Brillante | Tonos amarillos y naranjas |
| `lavanda` | Lavanda Soñadora | Tonos morados suaves |
| `estandar` | Estándar | Neutros, sin color fuerte |

### 3.6 Mantenimiento — Copias de seguridad (`/admin/backups`) *(solo admin)*

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/admin/backups` | admin | Listar las copias de seguridad existentes (recientes primero) |
| POST | `/admin/backups` | admin | Crear una copia de seguridad de la BD ahora (y rotar las antiguas) |

Cada copia es un fichero `app-YYYYMMDD-HHMMSS.sqlite3` autónomo en `BACKUP_DIR` (`./data/backups`).
La purga de la papelera es **automática** (tarea en segundo plano) y no se expone como endpoint.

### 3.7 Origen sandbox (servidor aparte)

Servido por `app/sandbox.py` (`:8002` en dev) o `nginx/sandbox.conf` (`sandbox.<dominio>` en prod).

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/ejercicio/{hash}` | — | Sirve el HTML del ejercicio con CSP estricta |
| GET | `/health` | — | Readiness del servidor sandbox |

Cabeceras de respuesta: `Content-Security-Policy` (estricta), `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Cache-Control: immutable`.

---

## 4. Modelo de datos

### 4.1 Tablas

#### `user`
| Columna | Tipo | Descripción |
|---|---|---|
| `id` | UUID (str) | PK |
| `email` | VARCHAR(255) UNIQUE | Email del usuario |
| `nombre` | VARCHAR(255) | Nombre visible |
| `hashed_password` | VARCHAR(255) | Hash Argon2id |
| `rol` | VARCHAR(50) | `admin` o `editor` |
| `activo` | BOOLEAN | Soft-disable |
| `creado_en` | DATETIME | Timestamp de creación |

#### `content`
| Columna | Tipo | Descripción |
|---|---|---|
| `id` | UUID (str) | PK |
| `titulo` | VARCHAR(500) | Título del contenido |
| `tipo` | VARCHAR(50) | `interactivo` o `texto` |
| `estado` | VARCHAR(50) | `borrador`, `publicado`, `archivado`, `papelera` |
| `ciclo_id` | UUID FK nullable | Ciclo educativo |
| `curso_id` | UUID FK nullable | Curso educativo |
| `asignatura_id` | UUID FK nullable | Asignatura |
| `html_hash` | VARCHAR(64) nullable | SHA-256 del HTML (interactivo) |
| `body_html` | TEXT nullable | HTML sanitizado (texto) |
| `creado_en` | DATETIME | |
| `actualizado_en` | DATETIME | |

#### `content_version`
| Columna | Tipo | Descripción |
|---|---|---|
| `id` | UUID (str) | PK |
| `contenido_id` | UUID FK | Contenido padre |
| `titulo` | VARCHAR(500) | Snapshot del título |
| `html_hash` | VARCHAR(64) nullable | Snapshot del hash |
| `body_html` | TEXT nullable | Snapshot del HTML |
| `creado_en` | DATETIME | Fecha de la versión |

#### `ciclo`
| Columna | Tipo | Descripción |
|---|---|---|
| `id` | UUID (str) | PK |
| `nombre` | VARCHAR(255) UNIQUE | Nombre del ciclo |
| `orden` | INTEGER | Orden de presentación |

#### `curso`
| Columna | Tipo | Descripción |
|---|---|---|
| `id` | UUID (str) | PK |
| `nombre` | VARCHAR(255) | Nombre del curso |
| `ciclo_id` | UUID FK | Ciclo al que pertenece |
| `orden` | INTEGER | Orden de presentación |

#### `asignatura`
| Columna | Tipo | Descripción |
|---|---|---|
| `id` | UUID (str) | PK |
| `nombre` | VARCHAR(255) UNIQUE | Nombre de la asignatura |
| `color` | VARCHAR(7) nullable | Color hex (#RRGGBB) |
| `orden` | INTEGER | Orden de presentación |

#### `site_config`
| Columna | Tipo | Descripción |
|---|---|---|
| `id` | VARCHAR(36) | PK (singleton fijo: `00000000-0000-0000-0000-000000000001`) |
| `nombre_sitio` | VARCHAR(255) | Nombre del sitio |
| `paleta_activa` | VARCHAR(100) | ID de la paleta activa |
| `paletas_json` | TEXT | JSON con paletas personalizadas |
| `fuente_activa` | VARCHAR(100) | ID de la fuente activa (default `sistema`) |
| `fondo_activo` | VARCHAR(100) | ID del fondo/estampado activo (default `ninguno`) |

---

## 5. Guía de instalación y despliegue

### 5.1 Requisitos previos

- Docker 24+ y Docker Compose v2
- (Desarrollo local) Python 3.12+, Node.js 20+

### 5.2 Arranque rápido con Docker (producción, Caddy + HTTPS)

Solo **Caddy** se expone a internet (80/443). `frontend`, `api` y `sandbox` son internos.

**Requisitos previos al `up`:**
1. **DNS:** registros **A** de `APP_DOMAIN` y `SANDBOX_DOMAIN` apuntando a la IP pública del servidor.
2. **Router:** redirigir **80** y **443** al servidor.

```bash
# 1. Copiar el proyecto al servidor y entrar en la carpeta
cd plataforma-educativa

# 2. Copiar y editar variables de entorno (.env en la RAÍZ)
cp .env.example .env
# Editar .env:
#   APP_DOMAIN=plataforma.tudominio.com
#   SANDBOX_DOMAIN=sandbox.tudominio.com
#   ACME_EMAIL=tu-email@tudominio.com
#   SECRET_KEY=...  (y admin)

# 3. Levantar (construye imágenes; Caddy pide los certificados de Let's Encrypt)
docker compose up -d --build
docker compose logs -f caddy   # seguir la emisión de certificados

# 4. Acceso
# Web: https://APP_DOMAIN     (solo por dominio + HTTPS, no por IP:puerto)
```

> **Importante:** `SANDBOX_BASE_URL`, `APP_ORIGINS` y `CORS_ALLOW_ORIGINS` se **derivan
> automáticamente** de `APP_DOMAIN`/`SANDBOX_DOMAIN` en `docker-compose.yml`; no hay que ponerlos en
> `.env`. El sandbox va en su **propio subdominio** (origen aislado, `CLAUDE.md §10`).

El entrypoint ejecuta automáticamente:
1. `alembic upgrade head` — aplica todas las migraciones.
2. Si no existe ningún usuario, crea el admin por defecto con las credenciales de `.env`.

### 5.3 Variables de entorno (backend/.env)

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/db.sqlite3` | URL de la base de datos |
| `SECRET_KEY` | *(requerido)* | Clave para firmar JWT (mín. 32 chars) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Expiración del token JWT |
| `DEFAULT_ADMIN_EMAIL` | `admin@plataforma.local` | Email del admin inicial |
| `DEFAULT_ADMIN_PASSWORD` | `CambiaMe1234` | Contraseña del admin inicial |
| `HTML_STORAGE_PATH` | `./data/html_files` | Directorio de ficheros HTML de ejercicios |
| `CORS_ORIGINS` | `http://localhost:5173` | Orígenes permitidos (separados por coma) |

> **Importante:** Cambiar `SECRET_KEY` y `DEFAULT_ADMIN_PASSWORD` antes del primer despliegue en producción.

### 5.4 Arranque en desarrollo local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Editar según necesidad
python -m alembic upgrade head
uvicorn app.main:app --reload --port 8001

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173 (el proxy /api reenvía al backend en :8001)
```

> **Nota (V-0.5.0):** en desarrollo, el frontend habla siempre con su mismo origen
> (`localhost:5173`) y Vite reenvía las peticiones `/api` al backend, de modo que no hay
> problemas de CORS. El puerto 5173 es fijo (`strictPort`).

### 5.5 Crear primer usuario administrador (manual)

Si se prefiere no usar el auto-seed del entrypoint:

```bash
cd backend
python scripts/seed_admin.py admin@midominio.com MiPassword123
```

---

## 6. Manual de uso

### 6.1 Acceso público

La portada del sitio (`/`) muestra el catálogo de contenidos publicados. Los visitantes pueden:
- Navegar por el catálogo.
- Abrir un ejercicio interactivo (se ejecuta en un iframe aislado).
- Leer artículos de texto.
- Buscar por título o contenido (próximamente).

No es necesario registrarse ni hacer login para acceder al catálogo.

### 6.2 Panel de administración — Acceso

1. Pulsar **"Acceder"** en la barra de navegación.
2. Introducir email y contraseña.
3. Tras el login, redirige automáticamente al **Panel Admin** (`/admin`).

### 6.3 Panel admin — Inicio

Muestra tarjetas de resumen con estadísticas del sitio:
- Número de contenidos publicados.
- Número de usuarios.
- Número de ciclos/cursos configurados.

### 6.4 Panel admin — Contenidos

Lista todos los contenidos con su estado (borrador, publicado, archivado, papelera).

**Acciones disponibles:**
- **+ Nuevo artículo** — abre el formulario de creación (ver abajo).
- **Editar** — abre el formulario con el contenido cargado.
- **Publicar** — pone el contenido en estado "publicado" (visible en catálogo).
- **Borrar** — mueve a la papelera (borrado lógico).
- **Restaurar** — recupera un contenido de la papelera.

**Crear o editar un artículo de texto:**
1. Pulsar **"+ Nuevo artículo"** (o **"Editar"** en una fila existente).
2. Rellenar **título** (obligatorio) y, opcionalmente, **descripción** y **etiquetas**
   (separadas por comas).
3. Al crear, asignar la **clasificación**: ciclo, curso y asignatura (opcional).
4. Escribir el **cuerpo** en el editor enriquecido (negrita, cursiva, encabezados, listas,
   cita, enlaces).
5. Pulsar **"Crear artículo"** / **"Guardar cambios"**. El HTML se sanea automáticamente por
   seguridad. El contenido queda en estado *borrador* hasta que se publica.

> Nota: por ahora el formulario cubre artículos de **texto**. Los contenidos **interactivos**
> (subida de HTML) llegarán con el subdominio sandbox.

### 6.5 Panel admin — Taxonomía

Gestión de ciclos, cursos y asignaturas educativas.

**Ciclos:**
- Añadir ciclo: escribir nombre en el campo inferior y pulsar "+ Añadir".
- Editar nombre: pulsar el lápiz ✏️ o hacer doble clic, editar, confirmar con Enter o ✓.
- Cancelar edición: pulsar Escape o ✕.
- Eliminar: pulsar el icono de papelera 🗑️ (pide confirmación).

**Cursos:** mismas acciones que ciclos.

**Asignaturas:** igual, más opción de seleccionar un color representativo con el selector de color.

### 6.6 Panel admin — Apariencia y ajustes

Gestión del nombre del sitio, la tipografía y la paleta de colores.

**Ajustes generales — Nombre del sitio:**
- Escribir el nombre en el campo "Nombre del sitio" (máx. 80 caracteres) y pulsar "Guardar cambios".
- Aparece al instante en la barra pública, el pie de página y el sidebar de administración.

**Ajustes generales — Fuente de letra:**
- Rejilla de fuentes, cada una previsualizada en su propia tipografía. Hacer clic en la deseada y
  pulsar "Guardar cambios" para aplicarla a todo el sitio.
- Catálogo: **Sistema** (sin descarga), **Nunito** y **Quicksand** (amigables), **Lexend**,
  **Atkinson Hyperlegible** y **Andika** (alta legibilidad / lectores principiantes).
- Las fuentes son *self-hosted*: las sirve la propia app, sin contactar con servidores externos,
  protegiendo la privacidad de los menores.

**Ajustes generales — Fondo / estampado:**
- Rejilla con **Ninguno** (fondo liso) y 6 temáticas: **Aula**, **Naturaleza**, **Espacio**,
  **Océano**, **Geométrico** y **Granja**. Cada opción muestra una vista previa del estampado.
- Al elegir una y pulsar "Guardar cambios", el estampado se aplica a todo el sitio.
- El estampado se **recolorea automáticamente con la paleta activa** y se muestra a baja opacidad,
  detrás del contenido, para no restar legibilidad. Los patrones son SVG *self-hosted*.

**Paletas predefinidas:**
- Hacer clic en cualquier swatch para activarla inmediatamente.
- La paleta activa muestra un badge "Activa" y un borde destacado.
- Los cambios se aplican en tiempo real en toda la interfaz.

**Paletas personalizadas:**
1. Pulsar el botón "+ Nueva paleta".
2. Introducir un nombre.
3. Elegir los 4 colores con el selector (Fondo, Superficie, Texto, Color principal).
4. Previsualizar el resultado en el rectángulo de muestra.
5. Pulsar "Guardar".

Para eliminar una paleta personalizada, pulsar el botón ✕ en su swatch (no disponible si es la paleta activa).

> **Novedad de la V-0.5.0:** si una operación de paleta falla (por ejemplo, intentar crear una
> paleta con un ID ya existente o eliminar la paleta activa), la página muestra un **mensaje de
> error claro** en la parte superior en lugar de no hacer nada.

### 6.7 Panel admin — Usuarios *(solo admin)*

Lista de usuarios del sistema.

**Crear usuario:**
1. Rellenar email, nombre, contraseña y rol (admin/editor).
2. Pulsar "Crear usuario".

---

## 7. Seguridad

### 7.1 Aislamiento del sandbox

Los ejercicios interactivos se sirven desde el subdominio `sandbox.<dominio>` con:
- `<iframe sandbox="allow-scripts">` — **sin** `allow-same-origin`.
- CSP estricta que impide acceso a cookies, localStorage y comunicación con el origen padre.

Esto garantiza que el JavaScript del ejercicio no puede leer datos del usuario ni interactuar con la aplicación.

### 7.2 Sanitización de HTML

- HTML de **artículos de texto**: sanitizado SIEMPRE en el servidor con **nh3** (whitelist de etiquetas seguras) y, como segunda capa, con **DOMPurify** en el cliente al renderizar.
- HTML de **ejercicios interactivos**: **no** sanitizado (debe ejecutar JS); por eso se aísla con sandbox.

### 7.3 Protección de datos de menores

- Sin cuentas de alumno ni cookies de seguimiento.
- Visitas registradas de forma anónima y agregada.
- Sin publicidad ni perfilado dirigido a menores (cumplimiento DSA art. 28).

### 7.4 Autenticación

- Contraseñas almacenadas con **Argon2id** (mínimo 8 caracteres).
- Sesiones via **JWT HS256** con expiración configurable (por defecto 60 minutos).
- Sin contraseñas ni tokens en logs.

---

## 8. Tests

```bash
cd backend
pytest -v
# → 123 tests, todos deben pasar
```

Tipos de tests:
- **Unitarios** (dominio + handlers): sin base de datos, mocks de repositorios.
- **Integración** (endpoints): SQLite en memoria con `StaticPool`, `TestClient` de FastAPI.

> **Nota (V-0.5.0):** el fichero `tests/integration/test_configuration_endpoints.py` incluye un
> caso de regresión para el error 500 al activar una paleta sin fila de configuración previa. Su
> fixture usa deliberadamente `autoflush=False` para igualar la sesión de producción; con
> `autoflush=True` el bug **no** se reproduciría y el test sería inútil.

Para generar el coverage:
```bash
pytest --cov=app --cov-report=html
# → htmlcov/index.html
```

---

## 9. Roadmap

### V-0.5.0 (próxima)
- Formulario completo de creación/edición de contenidos (tipos interactivo y texto).
- Subida de ficheros HTML para ejercicios interactivos.
- Editor de texto enriquecido (Tiptap o similar) para artículos.
- Sanitización en cliente con DOMPurify.

### V-0.5.0
- Buscador full-text (FTS5) en el catálogo público.
- Paginación en listas de contenidos.
- Soporte de etiquetas/tags en contenidos.

### V-1.0.0
- Despliegue en VPS con Docker + Nginx + HTTPS.
- E2E completos con Playwright.
- Configuración de nombre del sitio y logotipo desde el panel admin.
