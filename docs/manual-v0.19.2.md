# Plataforma Educativa — Manual Técnico y de Usuario · V-0.19.2

> CMS educativo interactivo para infantil y primaria. Acceso público sin cuentas de alumno.
> Roles `admin` y `editor`. Arquitectura hexagonal. Fecha: 2026-06-17 · Licencia: MIT.

---

## Novedades de V-0.19.2 — Mejoras de visibilidad (UI)

Dos ajustes de interfaz para que ciertos elementos estén **siempre accesibles sin hacer scroll**:

- **Pie de la web pública siempre visible.** El pie (apoyo/donaciones, «{nombre del sitio} —
  contenidos para infantil y primaria» y los iconos de redes sociales) se ancla al fondo del
  viewport mientras se navega y, al llegar al final del documento, queda en su posición natural
  (no tapa el contenido final). Tiene fondo opaco y queda por debajo del ejercicio maximizado y
  de la barra de navegación superior.
- **Acciones de admin/editor siempre visibles.** La barra lateral del panel se mantiene fija a la
  altura del viewport, de manera que los botones del fondo —«Ver la web» y «Cerrar sesión»— están
  siempre accesibles sin necesidad de bajar. Si la lista de secciones no cupiera en la pantalla,
  esa zona hace su propio scroll.

Cambio **solo de CSS**: no se han tocado componentes, API ni esquema. No hay migración.

---

## Parte I — Manual técnico

### 1. Ficheros afectados

| Fichero | Cambio |
|---|---|
| `frontend/src/styles/tokens.css` | `.cms-footer` → `position: sticky; bottom: 0` + fondo opaco + `z-index: 50`. `.cms-sidebar` → `position: sticky; top: 0; height: 100vh; overflow-y: auto`. |

### 2. Notas de diseño

- El pie usa `position: sticky` (no `fixed`): permanece anclado al fondo del viewport mientras hay
  contenido por debajo y, al final, ocupa su espacio natural, de modo que **no oculta** el último
  contenido. Capas (z-index): barra de navegación `100`, pie `50`, rieles de publicidad `5`,
  ejercicio maximizado `1000` (el pie nunca asoma sobre un ejercicio a pantalla completa).
- La barra lateral del panel es `sticky` a `100vh` con `overflow-y: auto`: con el número habitual de
  secciones todo cabe y las acciones quedan ancladas abajo; si creciera, la propia barra scrollea.

### 3. Tests

Cambio solo de CSS; la suite no se ve afectada y sigue en verde.

```
cd backend && python -m pytest tests/unit tests/integration -q   # 205
cd frontend && npm run test:e2e                                  # 9 E2E
```

---

## Parte II — Manual de usuario

### 4. Para visitantes

El pie con las opciones de apoyo al proyecto y las redes sociales se ve siempre, sin tener que
desplazarse hasta el final de la página.

### 5. Para administradores y editores

En el panel, los botones **«Ver la web»** y **«Cerrar sesión»** están siempre a la vista en la parte
inferior de la barra lateral, aunque la página de trabajo sea larga.

### 6. Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.19.2) | Pie público y acciones de admin/editor siempre visibles. |
| Hecho (V-0.19.1) | Backend sin privilegios (usuario no-root) en Docker. |
| Hecho (V-0.19.0) | Iconos de red en artículos + autor de cada versión. |
