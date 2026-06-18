# Plataforma Educativa — Manual Técnico y de Usuario · V-0.21.3

> CMS educativo interactivo para infantil y primaria. Acceso público sin cuentas de alumno.
> Roles `admin` y `editor`. Arquitectura hexagonal. Fecha: 2026-06-18 · Licencia: MIT.

---

## Novedades de V-0.21.3 — Sección «Monetización y RRSS»

Reorganización del panel de administración: los enlaces de **donación**, las **redes sociales** y la
**publicidad** se han movido de «Apariencia» a una **página propia**, *Monetización y RRSS*
(`/admin/monetizacion`).

- **Apariencia** queda con: nombre del sitio, logo, fuente, fondo (estampado y disposición), Aula
  Abierta y textos de la portada del catálogo.
- **Monetización y RRSS**: enlaces de donación, redes sociales y publicidad en los márgenes.

Es un cambio **solo de interfaz**: la funcionalidad es la misma, mejor organizada.

---

## Parte I — Manual técnico

### 1. Cambios

| Área | Cambio |
|---|---|
| `pages/admin/MonetizacionPage.tsx` | Nueva página con las secciones de donación, redes y publicidad. |
| `pages/admin/ConfiguracionPage.tsx` | «Apariencia» pierde esas tres secciones (quedan nombre/logo/fuente/fondo/Aula Abierta/textos). |
| `app/config/useConfig.ts` | Expone `ajustesActuales` (config actual como `AjustesGeneralesRequest`). |
| `app/App.tsx` + `shared/ui/AdminLayout.tsx` | Ruta `/admin/monetizacion` + enlace de navegación. |

### 2. Cómo se evita pisar ajustes

El endpoint `PUT /config/general` **reemplaza** toda la configuración. Para repartir los ajustes en
dos páginas sin que una borre los de la otra, cada formulario parte de `ajustesActuales` (la
configuración actual completa) y **solo sobrescribe su sección** antes de enviar. Así, guardar en
«Monetización y RRSS» conserva intactos los ajustes de «Apariencia» y viceversa. Sin cambios de API
ni de backend.

### 3. Tests

```
cd backend && python -m pytest tests/unit tests/integration -q   # 225 (sin cambios)
cd frontend && npm run test:e2e                                  # 9 E2E
```

---

## Parte II — Manual de usuario

### 4. Dónde está cada cosa ahora (admin)

- **Apariencia**: nombre del sitio, logo, fuente de letra, fondo/estampado, Aula Abierta y los textos
  de la portada del catálogo.
- **Monetización y RRSS** (nueva entrada del menú): botones de donación, iconos de redes sociales del
  pie y el código de publicidad de los márgenes.

Recuerda: la publicidad solo se muestra en las pantallas de navegación del catálogo, nunca durante un
ejercicio (que usa un menor) ni en el panel.

### 5. Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.21.3) | Sección «Monetización y RRSS» separada de «Apariencia». |
| Hecho (V-0.21.2) | Integridad referencial a nivel de BD. |
| Hecho (V-0.21.1) | Correcciones del contador de visitas. |
