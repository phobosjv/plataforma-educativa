# Plataforma Educativa — Manual Técnico y de Usuario · V-0.21.4

> CMS educativo interactivo para infantil y primaria. Acceso público sin cuentas de alumno.
> Roles `admin` y `editor`. Arquitectura hexagonal. Fecha: 2026-06-19 · Licencia: MIT.

---

## Novedades de V-0.21.4 — Tabla de contenidos: taxonomía, orden y paginación

Mejoras de usabilidad en la tabla de administración de contenidos (`/admin/contenidos`):

- **Tres columnas nuevas**: *Ciclo*, *Curso* y *Asignatura*, para ver de un vistazo a qué clasificación
  pertenece cada contenido. El contenido sin clasificar muestra «—».
- **Ordenación por columna**: pulsa cualquier cabecera para ordenar; vuelve a pulsar para invertir.
- **Paginación de 10 en 10**, con botones *Primero · Anterior · Siguiente · Último* y el indicador
  «Página X de Y».

Es un cambio **solo de interfaz**: no se ha tocado backend, API ni base de datos.

---

## Parte I — Manual técnico

### 1. Cambios

| Área | Cambio |
|---|---|
| `pages/admin/ContenidosPage.tsx` | Columnas Ciclo/Curso/Asignatura (nombres resueltos desde los IDs vía `/taxonomy/*`, caché compartida con el catálogo), ordenación por columna y paginación cliente de 10 filas. |
| `styles/tokens.css` | Estilos prefijados `cms-th-sortable` (cursor + flecha ▲/▼) y `cms-pagination` / `cms-pagination-info`. |

### 2. Detalles de implementación

- `ContenidoResponse` ya incluía `ciclo_id`, `curso_id` y `asignatura_id`; el frontend construye mapas
  `id → nombre` a partir de los endpoints de taxonomía (mismas `queryKey` que el catálogo, así se sirven
  de la caché de React Query). **No** se ha modificado el contrato de la API.
- La ordenación compara cadenas con `localeCompare('es', { sensitivity: 'base' })` (insensible a
  acentos/mayúsculas) y las visitas numéricamente; los valores vacíos (sin clasificar) van al final.
- La paginación es de cliente sobre la lista completa ya ordenada; cambiar el orden reinicia a la
  página 1 y la página actual se «recorta» si el total de filas disminuye (p. ej. al borrar).

### 3. Tests

```
cd backend && python -m pytest tests/unit tests/integration -q   # 225 (sin cambios)
cd frontend && npx tsc --noEmit                                  # type-check limpio
cd frontend && npm run test:e2e                                  # 9 E2E
```

Verificación adicional en navegador con Playwright: cabeceras y columnas correctas, orden por Ciclo y
Título, paginación 10 + 5 sobre 15 contenidos sembrados, botones de extremo deshabilitados, 0 errores
de consola.

---

## Parte II — Manual de usuario

### 4. Usar la tabla de contenidos (admin/editor)

- En **Contenidos** verás ahora, además de Título, Tipo, Estado y Visitas, las columnas **Ciclo**,
  **Curso** y **Asignatura** de cada elemento.
- **Para ordenar**, pulsa el título de una columna. Aparece ▲ (ascendente); pulsa de nuevo para ▼
  (descendente). Solo una columna ordena a la vez.
- Si hay más de 10 contenidos, la lista se **pagina**. Usa los botones inferiores:
  - **« Primero** y **Último »** para saltar al principio o al final.
  - **‹ Anterior** y **Siguiente ›** para avanzar de una en una.
  - El texto central indica la **página actual y el total** (p. ej. «Página 2 de 5»).

### 5. Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.21.4) | Tabla de contenidos: columnas de taxonomía, orden por columna y paginación. |
| Hecho (V-0.21.3) | Sección «Monetización y RRSS» separada de «Apariencia». |
| Hecho (V-0.21.2) | Integridad referencial a nivel de BD. |
