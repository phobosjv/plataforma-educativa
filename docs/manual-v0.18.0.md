# Manual Técnico y de Usuario — Plataforma Educativa V-0.18.0

**Fecha:** 2026-06-17  
**Versión:** V-0.18.0  
**Estado:** Desarrollo activo

---

## 0. Novedades de V-0.18.0

**Redes sociales (pie configurable + enlaces en artículos).**

- **Redes sociales en el pie (config admin).** Desde Apariencia se configura una lista de enlaces a
  redes sociales (Facebook, Instagram, X, YouTube, TikTok, WhatsApp, Telegram, LinkedIn), cada uno con
  su **icono** (SVG self-hosted, sin CDN externo por privacidad de menores §10). Aparecen en el pie de
  la web pública. La URL debe ser web (`http(s)://`); cada red, una sola vez.
- **Enlaces a terceros en el cuerpo de artículos (editor).** El editor ya permitía insertar enlaces;
  ahora **abren en pestaña nueva** (`target=_blank` + `rel=noopener noreferrer`), de modo que un editor
  puede enlazar perfiles de redes sociales de terceros (autores citados) sin sacar al menor del sitio.
  El HTML se sigue saneando siempre (nh3 en servidor + DOMPurify en cliente).
- `site_config` gana `redes_sociales_json`; migración Alembic `015`. 205 tests backend (4 nuevos) + 9
  E2E en verde. API → `0.18.0`.

### Versiones recientes
- **V-0.17.1** — Robustez: migración de JWT a PyJWT.
- **V-0.17.0** — Historial de versiones y restauración de contenidos.

---

## 1. Descripción del sistema

CMS educativo para infantil y primaria: ejercicios interactivos (sandbox) y artículos de texto.
Acceso público sin cuentas de alumno. Roles **admin** y **editor**. Arquitectura hexagonal, regla de
dependencia `infrastructure → application → domain`.

Funcionalidad principal: catálogo navegable + buscador, contador de visitas, auditoría, versionado con
restauración, configuración del sitio (nombre, logo, paleta, fondo, textos, donaciones, **redes
sociales**, publicidad), monetización ligera (donaciones + publicidad solo en zonas de adultos).

---

## 2. API REST — Configuración (`/config/`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/config/` | — | Configuración del sitio (incluye `redes_sociales`) |
| PUT | `/config/general` | admin | Actualiza todos los ajustes generales del sitio |

**Campo nuevo de `GET /config/` (V-0.18.0):**
```json
{
  "redes_sociales": [
    { "red": "instagram", "url": "https://instagram.com/micole" },
    { "red": "youtube",   "url": "https://youtube.com/@micole" }
  ]
}
```

Redes soportadas (`red`): `facebook`, `instagram`, `x`, `youtube`, `tiktok`, `whatsapp`, `telegram`,
`linkedin`. El dominio valida que la red esté soportada, que no se repita y que la URL sea `http(s)://`.

> El resto de endpoints se mantienen como en V-0.17.x.

---

## 3. Modelo de datos — `site_config` (campo nuevo)

| Columna | Tipo | Descripción |
|---|---|---|
| `redes_sociales_json` | TEXT | Lista JSON de `{red, url}` (enlaces del pie público) |

El icono de cada red **no** se guarda en BD: es un SVG self-hosted del frontend (catálogo
`app/config/redesSociales.tsx`), asociado por el `id` de la red.

---

## 4. Instalación y despliegue

```bash
cd plataforma-educativa
cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY (>=32), admin
docker compose up -d --build
# El entrypoint corre alembic upgrade head (la migración 015 añade redes_sociales_json).
```

Desarrollo local: `cd backend && python -m alembic upgrade head && uvicorn app.main:app --reload --port 8001`
y `cd frontend && npm install && npm run dev`.

---

## 5. Manual de uso

### 5.1 Apariencia — Redes sociales *(novedad)*

En **Apariencia → Ajustes generales**, sección **«Redes sociales»**:

1. Pulsa **«+ Añadir red social»**.
2. Elige la red en el desplegable (verás su icono) e introduce la **URL** de tu perfil (debe empezar
   por `https://`).
3. Pulsa **«Guardar cambios»**. Los iconos aparecen en el **pie de la web pública**, enlazando a tus
   perfiles (se abren en una pestaña nueva).
4. Usa **«Quitar»** para eliminar una red. Cada red puede añadirse una sola vez.

### 5.2 Artículos — enlaces a terceros *(novedad)*

En el editor de artículos, selecciona un texto (p. ej. el nombre de un autor) y pulsa el botón de
**enlace (🔗)**; pega la URL (puede ser un perfil de redes sociales de un tercero). Al publicarse, el
enlace **abre en una pestaña nueva** de forma segura, sin sacar al visitante del sitio. El HTML del
artículo se sanea siempre por seguridad.

### 5.3 Resto del panel

Sin cambios respecto a V-0.17.x (Contenidos con versionado, Taxonomía, Usuarios, Copias, Auditoría,
Apariencia con logo/fuente/fondo/paletas/textos/donaciones/publicidad).

---

## 6. Seguridad y privacidad

- **Iconos self-hosted:** los iconos de redes son SVG incluidos en la app; **no** se cargan de un CDN
  externo, para no exponer la IP de los menores a terceros (§10).
- **Enlaces salientes:** abren en pestaña nueva con `rel="noopener noreferrer"` (nh3 lo refuerza en el
  servidor). Solo esquemas `http`/`https`/`mailto`; nunca `javascript:`.
- **Sandbox / sanitización / menores:** sin cambios (ejercicios aislados; HTML de artículos saneado;
  sin cuentas de alumno, sin cookies de seguimiento, visitas anónimas, sin perfilado).

---

## 7. Tests

```bash
cd backend && python -m pytest tests/unit tests/integration -q   # 205 tests
cd frontend && npm run test:e2e                                  # 9 flujos E2E
```

Los 4 tests nuevos cubren: valor por defecto y actualización de redes sociales, rechazo de una red no
soportada y rechazo de una URL no web.

---

## 8. Roadmap

- **Hecho (V-0.18.0):** redes sociales en el pie + enlaces a terceros en artículos.
- **Hecho (V-0.17.1):** robustez (PyJWT). **(V-0.17.0):** versionado/restauración.
- **Pendiente de robustez:** ejecutar el backend como usuario no-root en Docker (`gosu` + `chown`;
  requiere validación en el servidor). Mejoras: iconos de red en el cuerpo del artículo (hoy van como
  enlace de texto por la sanitización).
