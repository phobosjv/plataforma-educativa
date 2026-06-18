# Plataforma Educativa — Manual Técnico y de Usuario · V-0.21.1

> CMS educativo interactivo para infantil y primaria. Acceso público sin cuentas de alumno.
> Roles `admin` y `editor`. Arquitectura hexagonal. Fecha: 2026-06-18 · Licencia: MIT.

---

## Novedades de V-0.21.1 — Correcciones del contador de visitas

Release de corrección con dos arreglos del contador de visitas (hallazgos de la auditoría de
lógica):

1. **No se cuentan visitas de contenido inexistente.** El endpoint público de visitas acepta
   cualquier ID (no puede consultar la BD en cada petición, §8). Al **volcar** el contador por
   lotes se descartan ahora los conteos cuyos IDs no corresponden a ningún contenido (UUID
   arbitrarios recibidos por el endpoint, o contenido ya purgado). Así `content_views` no acumula
   **filas huérfanas** ni se infla el total mostrado en el panel.
2. **No se pierde el lote si falla la persistencia.** Antes, el volcado vaciaba el buffer en
   memoria *antes* de confirmar la transacción: si el commit fallaba, ese lote se perdía. Ahora,
   si la persistencia falla, los conteos **vuelven al buffer** y se reintentan en el siguiente
   volcado.

Sin cambios de esquema ni de contrato de la API.

---

## Parte I — Manual técnico

### 1. Cambios

| Área | Cambio |
|---|---|
| `analytics` (dominio) | Nuevo puerto `ContenidosConocidos` (`filtrar_existentes`). |
| `content` (infraestructura) | Adapter `SqlAlchemyContenidosConocidos` (filtra IDs a los existentes). |
| `analytics` (aplicación) | `VolcarVisitasHandler` descarta IDs desconocidos y, si falla el commit, devuelve los conteos al buffer. |
| `shared` (scheduler) | La tarea de volcado inyecta el adapter de contenido. |

### 2. Regla de dependencia

El puerto `ContenidosConocidos` se declara en el dominio de `analytics`; su implementación vive en
la infraestructura de `content` y se inyecta en la tarea de volcado (capa de composición). Así
`analytics` no importa `content`: la dependencia apunta hacia adentro. El filtrado se ejecuta una
vez por lote (no por petición), coherente con CLAUDE.md §8.

### 3. Tests

```
cd backend && python -m pytest tests/unit tests/integration -q   # 222 (3 nuevos)
cd frontend && npm run test:e2e                                  # 9 E2E
```

Nuevos: el volcado descarta el contenido desconocido; si la persistencia falla, el lote vuelve al
buffer (durabilidad); test de integración del filtrado (real vs. fantasma).

---

## Parte II — Manual de usuario

No hay cambios visibles para administradores, editores ni visitantes: es una corrección interna
del contador de visitas (el total del panel ya no puede inflarse con visitas a contenido que no
existe).

### Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.21.1) | Correcciones del contador de visitas (no contar inexistentes, durabilidad). |
| Hecho (V-0.21.0) | Ejercicios tipo "Examen". |
| Hecho (V-0.20.1) | Correcciones de auditoría (taxonomía, publicar, buffer en import). |
