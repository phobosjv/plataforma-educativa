# Plataforma Educativa — Manual Técnico y de Usuario · V-0.19.0

> CMS educativo interactivo para infantil y primaria: ejercicios interactivos (HTML
> autocontenido, aislado en sandbox) y artículos de texto. Acceso público sin cuentas de
> alumno. Roles `admin` y `editor`. Arquitectura hexagonal (dominio puro → aplicación →
> infraestructura → API). Fecha: 2026-06-17 · Licencia: MIT.

---

## Novedades de V-0.19.0

Esta versión agrupa dos mejoras menores de contenido:

- **Iconos de red social en el cuerpo de los artículos.** Cuando un editor enlaza a un perfil
  de una red social conocida (Facebook, Instagram, X, YouTube, TikTok, WhatsApp, Telegram,
  LinkedIn) dentro de un artículo, el enlace aparece precedido por el **icono de marca** de la
  red. La detección es por dominio del enlace y el icono es el mismo SVG *self-hosted* del pie
  (fuente única en `frontend/src/app/config/redesSociales.tsx`, sin CDN externo, §10). Los
  enlaces externos siguen abriéndose en pestaña nueva con `rel=noopener noreferrer`.
- **Autor de cada versión en el historial.** El historial de versiones de un contenido muestra
  una columna **«Autor»** con el email del usuario que creó cada versión. El email se resuelve
  en la capa API a partir de `created_by` usando el caso de uso de `identity`, sin que el
  contexto de contenido dependa del de identidad.

Además se verificó que la taxonomía (ciclos/cursos/asignaturas) está **bien codificada en
UTF-8** en la base de datos; lo que parecía «doble codificación» era solo la consola de Windows
(cp1252). No hay datos corruptos ni se necesita migración.

---

## Parte I — Manual técnico

### 1. Descripción del sistema

CMS educativo para infantil y primaria. Ejercicios interactivos servidos aislados desde el
subdominio sandbox (`sandbox="allow-scripts"` sin `allow-same-origin`) y artículos de texto cuyo
HTML se sanea siempre (nh3 en servidor + DOMPurify en cliente). Monolito modular con arquitectura
hexagonal y contextos: `content`, `taxonomy`, `identity`, `media`, `auditing`, `analytics`,
`configuration`.

### 2. API afectada por esta versión

| Endpoint | Cambio |
|---|---|
| `GET /api/v1/contenidos/{id}/versiones` (editor/admin) | Cada versión incluye el nuevo campo `created_by_email` (string o null). |

El resto del contrato es idéntico a V-0.18.x. La resolución del email se hace listando los
usuarios privilegiados (pocos) y mapeando `id → email` en la capa de composición de la API.

### 3. Modelo de datos

Sin cambios de esquema en esta versión: **no hay migración Alembic nueva**. `created_by_email` se
deriva en lectura del `created_by` ya almacenado en `content_version`. El icono de cada red no se
guarda en base de datos; es un SVG del frontend asociado por el id de la red.

### 4. Instalación y despliegue

```
cd plataforma-educativa
cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY (>=32), admin
docker compose up -d --build
# El entrypoint corre alembic upgrade head. Esta versión no añade migraciones nuevas.
```

### 5. Seguridad y privacidad

- Iconos *self-hosted*: los SVG de redes van incluidos en la app, nunca de un CDN externo (no
  exponer la IP de un menor, §10).
- Enlaces salientes del cuerpo de artículos: abren en pestaña nueva con `rel=noopener noreferrer`;
  el HTML se sigue saneando siempre (nh3 + DOMPurify), solo esquemas `http/https/mailto`.
- Sandbox, sanitización asimétrica y tratamiento de menores: sin cambios.

### 6. Tests

| Suite | Cobertura |
|---|---|
| Backend | 205 tests (unit + integración) |
| Versionado | el historial expone `created_by_email` (autor de cada versión) |
| E2E (Playwright) | 9 flujos: catálogo, búsqueda, pantalla completa, login+CRUD, sandbox, Aula Abierta |

```
cd backend && python -m pytest tests/unit tests/integration -q   # 205
cd frontend && npm run test:e2e                                  # 9 E2E
```

---

## Parte II — Manual de usuario

### 7. Enlazar redes sociales en un artículo (editor)

1. En el editor de artículos, selecciona el texto (por ejemplo, el nombre de un autor citado).
2. Pulsa el botón de enlace (🔗) y pega la URL del perfil (puede ser de un tercero).
3. Al guardar y publicar, si la URL es de una red conocida, el enlace se mostrará en la web
   pública **con el icono de la red** delante; siempre abre en pestaña nueva de forma segura.

### 8. Ver el autor de cada versión (editor/admin)

En la edición de un contenido, la sección **«Historial de versiones»** muestra ahora la columna
**«Autor»** con el email de quien hizo cada versión, junto al título y la fecha. Restaurar una
versión sigue sin destruir el historial (crea una versión nueva).

### 9. Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.19.0) | Iconos de red en artículos + autor de cada versión. |
| Hecho (V-0.18.0) | Redes sociales en el pie + enlaces a terceros en artículos. |
| Pendiente (robustez) | Backend como usuario no-root en Docker (validar en servidor). |
