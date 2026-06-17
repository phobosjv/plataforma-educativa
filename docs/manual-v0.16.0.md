# Manual Técnico y de Usuario — Plataforma Educativa V-0.16.0

**Fecha:** 2026-06-17  
**Versión:** V-0.16.0  
**Estado:** Desarrollo activo

---

## 0. Novedades de V-0.16.0

**Donaciones, publicidad y textos del catálogo configurables.**

- **Enlaces de donación.** Desde Apariencia se configura una lista de enlaces (PayPal, Ko-fi, etc.,
  con etiqueta + URL); se muestran como botones en el **pie de la web pública**. La URL debe ser web
  (`http(s)://`); se rechazan esquemas peligrosos (`javascript:`, …).
- **Publicidad en los márgenes.** Anuncios (código HTML de la red de anuncios, pegado por el admin) en
  los márgenes izquierdo y derecho, **solo en las pantallas de navegación del catálogo** (zona de
  adultos, §10). **Nunca** durante un ejercicio/artículo (lo usa un menor) ni en el panel admin.
  Activable, con código independiente por lado, y se ocultan en pantallas estrechas.
- **Textos de la portada del catálogo configurables.** «¿En qué curso estás?» (título) y «Toca tu
  curso para ver las actividades» (subtítulo) se editan desde Apariencia, pensados para dirigirse a
  las familias cuando hay publicidad.
- `site_config` gana 6 columnas; migración Alembic `014`. Todo se guarda por `PUT /config/general`.
- 192 tests backend (6 nuevos) + 9 E2E en verde. API → `0.16.0`.

### Versiones recientes
- **V-0.15.0** — Auditoría de acciones de gestión (contexto `auditing`).
- **V-0.14.0** — Contador de visitas (contexto `analytics`).

---

## 1. Descripción del sistema

Plataforma web educativa tipo CMS para alojar y ejecutar **ejercicios interactivos** (HTML/CSS/JS autocontenidos) y **artículos de texto**, dirigidos a alumnado de infantil y primaria en España.

### Características principales
- Acceso público sin cuentas de alumno. Roles **admin** y **editor**.
- Nombre, **logotipo**, paleta, **textos de portada**, **donaciones** y **publicidad** configurables.
- **Buscador** del catálogo (full-text). **Contador de visitas** anónimas. **Auditoría** de gestión.
- Ejercicios en iframe aislado con sandbox; artículos con HTML sanitizado en servidor.
- Taxonomía configurable: ciclos, cursos y asignaturas (transversales / «Aula Abierta»).
- **Monetización ligera:** donaciones (pie público) y publicidad **solo en zonas de adultos** (§10).

---

## 2. Arquitectura

### 2.1 Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic |
| Base de datos | SQLite en modo WAL (búsqueda con FTS5) |
| Autenticación | Argon2id (contraseñas), JWT HS256 (sesiones) |
| Frontend | React 18, TypeScript strict, Vite 4 |

### 2.2 Regla de dependencia

```
infrastructure → application → domain
```

### 2.3 Contextos acotados

| Contexto | Responsabilidad |
|---|---|
| `identity` | Usuarios, login JWT, guardas de rol |
| `content` | CRUD, versionado, papelera, artículos + ejercicios, búsqueda FTS5 |
| `taxonomy` | Ciclos, cursos y asignaturas (transversal → «Aula Abierta») |
| `configuration` | Sitio: nombre, fuente, fondo, logo, paletas, **textos catálogo, donaciones, publicidad** |
| `media` | Subida de imágenes (artículos y logo) |
| `analytics` | Contador de visitas |
| `auditing` | Registro de acciones de gestión |

---

## 3. API REST — Configuración (`/config/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/config/` | — | Configuración del sitio (incluye textos, donaciones y publicidad) |
| PUT | `/config/general` | admin | Actualiza ajustes generales (todos los campos del sitio) |
| PUT | `/config/paleta` | admin | Activar paleta |
| POST/PUT/DELETE | `/config/paletas[/{id}]` | admin | CRUD de paletas personalizadas |

**Campos nuevos de `GET /config/` (V-0.16.0):**
```json
{
  "catalogo_titulo": "¿En qué curso estás?",
  "catalogo_subtitulo": "Toca tu curso para ver las actividades",
  "donaciones": [{ "etiqueta": "PayPal", "url": "https://paypal.me/micole" }],
  "publicidad_activa": false,
  "publicidad_html_izquierda": "",
  "publicidad_html_derecha": ""
}
```

> El resto de endpoints (contenidos + `/buscar`, `/analytics/visitas`, `/auditoria`, `/media/imagenes`,
> `/taxonomy/*`, `/admin/backups` + `/admin/export`, sandbox) se mantienen como en V-0.15.0.

---

## 4. Modelo de datos — `site_config` (campos nuevos)

| Columna | Tipo | Descripción |
|---|---|---|
| `catalogo_titulo` | VARCHAR(120) | Título de la portada del catálogo |
| `catalogo_subtitulo` | VARCHAR(120) | Subtítulo de la portada del catálogo |
| `donaciones_json` | TEXT | Lista JSON de `{etiqueta, url}` |
| `publicidad_activa` | BOOLEAN | Si se muestra la publicidad en navegación |
| `publicidad_html_izquierda` | TEXT | Código del anuncio del margen izquierdo |
| `publicidad_html_derecha` | TEXT | Código del anuncio del margen derecho |

El resto de tablas se mantienen como en V-0.15.0.

---

## 5. Instalación y despliegue

### 5.1 Producción con Docker (Caddy + HTTPS)

```bash
cd plataforma-educativa
cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin
docker compose up -d --build
# El entrypoint corre alembic upgrade head (la migración 014 añade los campos nuevos).
```

### 5.2 Desarrollo local

```bash
cd backend && python -m alembic upgrade head
uvicorn app.main:app --reload --port 8001

cd frontend && npm install && npm run dev   # http://localhost:5173
```

---

## 6. Manual de uso

### 6.1 Apariencia — Textos de la portada *(novedad)*

En **Apariencia → Ajustes generales**, sección «Textos de la portada del catálogo»: edita el **título**
y el **subtítulo** de la pantalla inicial. Si activas la publicidad, conviene redactarlos dirigidos a
las familias (es donde se ven los anuncios).

### 6.2 Apariencia — Enlaces de donación *(novedad)*

En la sección «Enlaces de donación»: pulsa **«+ Añadir enlace de donación»**, escribe la **etiqueta**
(p. ej. «PayPal») y la **URL** (debe empezar por `https://`). Pulsa **«Guardar cambios»**. Los enlaces
aparecen como botones en el **pie de la web pública**. Usa «Quitar» para eliminar un enlace.

### 6.3 Apariencia — Publicidad en los márgenes *(novedad)*

En la sección «Publicidad en los márgenes»: marca **«Mostrar publicidad…»** y pega el **código HTML**
de tu red de anuncios en los recuadros de margen izquierdo y/o derecho. Los anuncios:
- se muestran **solo en las pantallas de navegación del catálogo** (elegir curso/asignatura/ejercicio);
- **no** se muestran durante un ejercicio o artículo (lo usa un menor), ni en el panel de administración;
- se ocultan automáticamente en pantallas estrechas (móvil) para no tapar el contenido.

> Cumple CLAUDE.md §10: publicidad solo en zonas de adultos, sin perfilado (DSA art. 28).

### 6.4 Resto del panel

Sin cambios respecto a V-0.15.0 (Contenidos, Taxonomía, Usuarios, Copias, Auditoría, paletas, logo,
fuente, fondo, Aula Abierta).

---

## 7. Seguridad y privacidad

- **Sandbox / sanitización:** sin cambios (ejercicios aislados; HTML de artículos saneado).
- **Donaciones:** las URLs deben ser `http(s)://`; el dominio rechaza otros esquemas (evita
  `javascript:` en un enlace).
- **Publicidad:** el código lo introduce el **admin** (de confianza) y se muestra **solo en zonas de
  adultos** (pantallas de navegación), nunca durante la interacción del menor con un ejercicio.
- **Menores:** sin cuentas de alumno, sin cookies de seguimiento, visitas anónimas, sin perfilado.

---

## 8. Tests

```bash
cd backend && python -m pytest tests/unit tests/integration -q   # 192 tests
cd frontend && npm run test:e2e                                  # 9 flujos E2E
```

Los 6 tests nuevos cubren: valores por defecto y actualización de los textos del catálogo (con título
vacío → error), donaciones (alta y rechazo de URL no web) y publicidad (activar + código por lado).

---

## 9. Roadmap

- **Hecho (V-0.16.0):** donaciones, publicidad en márgenes y textos del catálogo configurables.
- **Hecho (V-0.15.0):** auditoría de acciones de gestión.
- **Siguiente:** UI de versionado/restauración de contenidos.
- **Más adelante:** robustez (usuario no-root en el backend), revisión de dependencias.
