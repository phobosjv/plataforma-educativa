# Manual Técnico y de Usuario — Plataforma Educativa V-0.17.0

**Fecha:** 2026-06-17  
**Versión:** V-0.17.0  
**Estado:** Desarrollo activo

---

## 0. Novedades de V-0.17.0

**Historial de versiones y restauración de contenidos.**

- **Historial de versiones** en la edición de un contenido (panel admin): lista las versiones
  (número, título y fecha) con la más reciente marcada como «actual».
- **Restaurar una versión anterior**: devuelve el contenido al estado (título, descripción,
  etiquetas, cuerpo HTML o ejercicio) de esa versión. Restaurar **no destruye** el historial: crea
  una **versión nueva** con el estado restaurado (CLAUDE.md §7), así la operación es reversible.
- Endpoints: `GET /api/v1/contenidos/{id}/versiones` y
  `POST /api/v1/contenidos/{id}/versiones/{version_no}/restaurar` (editor/admin). La restauración se
  registra en la auditoría.
- Sin cambios de esquema: la tabla `content_version` ya existía y cada modificación crea una versión
  inmutable. 196 tests backend (4 nuevos) + 9 E2E en verde. API → `0.17.0`.

### Versiones recientes
- **V-0.16.0** — Donaciones, publicidad en márgenes y textos del catálogo configurables.
- **V-0.15.0** — Auditoría de acciones de gestión.

---

## 1. Descripción del sistema

Plataforma web educativa tipo CMS para alojar y ejecutar **ejercicios interactivos** (HTML/CSS/JS autocontenidos) y **artículos de texto**, dirigidos a alumnado de infantil y primaria en España. Acceso público sin cuentas de alumno. Roles **admin** y **editor**.

### Características principales
- Catálogo navegable + **buscador** full-text; **contador de visitas** anónimas.
- Nombre, logotipo, paleta, textos de portada, donaciones y publicidad configurables.
- **Auditoría** de acciones de gestión y **versionado con restauración** de contenidos.
- Ejercicios en iframe aislado con sandbox; artículos con HTML sanitizado en servidor.

---

## 2. Arquitectura

Monolito modular + arquitectura hexagonal. Regla de dependencia `infrastructure → application → domain`.

| Contexto | Responsabilidad |
|---|---|
| `identity` | Usuarios, login JWT, guardas de rol |
| `content` | CRUD, **versionado inmutable + restauración**, papelera, artículos + ejercicios, búsqueda FTS5 |
| `taxonomy` | Ciclos, cursos y asignaturas (transversal → «Aula Abierta») |
| `configuration` | Sitio: nombre, fuente, fondo, logo, paletas, textos, donaciones, publicidad |
| `media` | Subida de imágenes (artículos y logo) |
| `analytics` | Contador de visitas |
| `auditing` | Registro de acciones de gestión |

---

## 3. API REST — Versiones de contenido (V-0.17.0)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/contenidos/{id}/versiones` | editor+ | Historial de versiones (nº, título, tipo, autor, fecha) |
| POST | `/contenidos/{id}/versiones/{version_no}/restaurar` | editor+ | Restaura el contenido a esa versión (crea una versión nueva) |

**Modelo de una versión (`content_version`):** `version_no`, `metadata_snapshot` (título, descripción,
tipo, idioma, etiquetas), `body_html`/`hash_html`, `created_by`, `created_at`. Cada modificación de un
contenido (crear, editar, subir HTML, restaurar) añade una versión; las versiones son **inmutables**.

> El resto de endpoints (contenidos + `/buscar`, `/analytics/visitas`, `/auditoria`, `/config/*`,
> `/media/imagenes`, `/taxonomy/*`, `/admin/backups` + `/admin/export`, sandbox) se mantienen como en V-0.16.0.

---

## 4. Instalación y despliegue

### 4.1 Producción con Docker (Caddy + HTTPS)

```bash
cd plataforma-educativa
cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin
docker compose up -d --build
```

El entrypoint ejecuta `alembic upgrade head`. **Esta versión no añade migraciones** (la tabla
`content_version` ya existía).

### 4.2 Desarrollo local

```bash
cd backend && python -m alembic upgrade head
uvicorn app.main:app --reload --port 8001

cd frontend && npm install && npm run dev   # http://localhost:5173
```

---

## 5. Manual de uso

### 5.1 Historial de versiones y restauración *(novedad V-0.17.0)*

Al **editar** un contenido en el panel de administración, al final de la página aparece la sección
**«Historial de versiones»**:

1. Muestra cada versión guardada (número, título y fecha). La más reciente está marcada como **«actual»**.
2. Para volver a un estado anterior, pulsa **«Restaurar»** en la versión deseada.
3. El contenido recupera el título, la descripción, las etiquetas y el cuerpo (o el ejercicio) de esa
   versión. **No se pierde nada**: se crea una versión nueva con el estado restaurado, así que puedes
   deshacer la restauración volviendo a otra versión.

Cada vez que creas, editas, subes el HTML o restauras un contenido, se guarda automáticamente una
versión. La restauración queda además registrada en la **Auditoría**.

### 5.2 Resto del panel

Sin cambios respecto a V-0.16.0 (Contenidos, Taxonomía, Usuarios, Copias, Auditoría, Apariencia con
logo/fuente/fondo/paletas/textos/donaciones/publicidad).

---

## 6. Seguridad y privacidad

- **Sandbox / sanitización:** sin cambios (ejercicios aislados en iframe; HTML de artículos saneado).
- **Versionado:** las versiones son inmutables; restaurar nunca borra historial. Solo editor/admin
  pueden ver y restaurar versiones; la acción se audita.
- **Menores:** sin cuentas de alumno, sin cookies de seguimiento, visitas anónimas, sin perfilado.

---

## 7. Tests

```bash
cd backend && python -m pytest tests/unit tests/integration -q   # 196 tests
cd frontend && npm run test:e2e                                  # 9 flujos E2E
```

Los 4 tests nuevos cubren: listar versiones tras editar, restaurar una versión (revierte el estado y
crea una versión nueva, reflejada en la lectura pública), versión inexistente → 404 y la guarda de rol.

---

## 8. Roadmap

- **Hecho (V-0.17.0):** historial de versiones y restauración de contenidos.
- **Hecho (V-0.16.0):** donaciones, publicidad y textos del catálogo configurables.
- **Más adelante:** robustez (usuario no-root en el backend), revisión de dependencias; mostrar el
  autor (email) de cada versión; comparar versiones.
