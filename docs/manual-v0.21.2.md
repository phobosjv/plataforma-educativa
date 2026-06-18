# Plataforma Educativa — Manual Técnico y de Usuario · V-0.21.2

> CMS educativo interactivo para infantil y primaria. Acceso público sin cuentas de alumno.
> Roles `admin` y `editor`. Arquitectura hexagonal. Fecha: 2026-06-18 · Licencia: MIT.

---

## Novedades de V-0.21.2 — Integridad referencial a nivel de base de datos

Endurecimiento: ahora **SQLite hace cumplir las claves foráneas (FK)**. Es una segunda capa, a
nivel de motor, sobre las guardas de dominio que ya existían.

- Cada conexión activa `PRAGMA foreign_keys=ON` (antes solo se activaba el modo WAL). Así pasan a
  aplicarse las FK ya declaradas: `curso.ciclo_id → ciclo` y `content_version.content_id → content`.
- La tabla `content` gana **FK a la taxonomía** (`ciclo_id`, `curso_id`, `asignatura_id`) con
  `ON DELETE RESTRICT`: la base de datos rechaza que un contenido apunte a una taxonomía que no
  existe, reforzando la guarda de dominio de los handlers de borrado.

La purga de contenido sigue borrando sus versiones mediante la cascada del ORM. Sin cambios de API.

---

## Parte I — Manual técnico

### 1. Cambios

| Área | Cambio |
|---|---|
| `shared/infrastructure/database.py` | El listener de conexión añade `PRAGMA foreign_keys=ON`. |
| `content` (modelo ORM) | `ciclo_id`/`curso_id`/`asignatura_id` declaran `ForeignKey(..., ondelete="RESTRICT")`. |
| Migración **017** | Recrea `content` para añadir las FK (batch SQLite); suelta y reconstruye el índice FTS5 alrededor. |

### 2. Por qué se recrea `content` y el índice FTS

SQLite no permite añadir una FK con `ALTER`: hay que **recrear la tabla** (patrón *batch* de
Alembic, que copia los datos). El índice de búsqueda `content_fts` es de *contenido externo* sobre
`content` y mapea por `rowid` (que cambia al recrear), por lo que la migración lo **suelta antes** y
lo **reconstruye después** (`rebuild`), dejando la búsqueda operativa.

La migración corre con las FK desactivadas (modo por defecto de la conexión de Alembic), así que la
recreación no tropieza con las referencias existentes.

### 3. Despliegue

```
cd plataforma-educativa
docker compose up -d --build
# El entrypoint corre alembic upgrade head: la migración 017 añade las FK y reconstruye el índice.
```

> Si una instalación tuviera referencias huérfanas previas, conviene revisarlas antes (en la BD de
> desarrollo se verificó que no había ninguna). Recomendado: hacer copia (o exportación completa)
> antes de actualizar, como en cualquier migración.

### 4. Tests

```
cd backend && python -m pytest tests/unit tests/integration -q   # 225 (3 nuevos)
cd frontend && npm run test:e2e                                  # 9 E2E
```

Nuevos (con un engine que activa las FK): no se puede borrar un curso referenciado por contenido; sí
se puede tras quitar el contenido; no se puede insertar contenido con un curso inexistente.

---

## Parte II — Manual de usuario

No hay cambios visibles: es una mejora interna de robustez. El comportamiento al borrar taxonomía es
el mismo que ya introdujo V-0.20.1 (la app avisa y no borra si hay elementos asociados); ahora además
la propia base de datos lo garantiza.

### Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.21.2) | Integridad referencial a nivel de BD (FK activas + FK de content a taxonomía). |
| Hecho (V-0.21.1) | Correcciones del contador de visitas. |
| Hecho (V-0.21.0) | Ejercicios tipo "Examen". |
