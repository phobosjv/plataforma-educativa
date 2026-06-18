# Plataforma Educativa — Manual Técnico y de Usuario · V-0.21.0

> CMS educativo interactivo para infantil y primaria. Acceso público sin cuentas de alumno.
> Roles `admin` y `editor`. Arquitectura hexagonal. Fecha: 2026-06-18 · Licencia: MIT.

---

## Novedades de V-0.21.0 — Ejercicios tipo "Examen"

Los ejercicios interactivos pueden marcarse ahora como **«Examen» (simulacro)**:

- Al crear o editar un contenido de tipo **interactivo**, aparece un check **«Examen»**. No aplica a
  los artículos de texto (el dominio rechaza marcar un texto como examen).
- En el **catálogo**, los ejercicios marcados como examen se muestran **al final** de cada lista
  (navegación por ciclo/curso/asignatura, Aula Abierta y «Ver todo») y con un **icono/badge distinto**
  que indica que es una simulación de examen.
- Suelen ser ejercicios más largos, resultado de **fusionar varios ejercicios**: esa combinación la
  hace a mano el **diseñador** del examen; la aplicación solo aporta la marca, el orden y el icono.

---

## Parte I — Manual técnico

### 1. API

| Endpoint | Cambio |
|---|---|
| `POST /api/v1/contenidos/` | Acepta `es_examen` (bool, por defecto `false`). Solo válido en `tipo="interactivo"`. |
| `PUT /api/v1/contenidos/{id}` | Acepta `es_examen` (bool opcional) para marcar/desmarcar. |
| `GET /api/v1/contenidos/...` | `ContenidoResponse` incluye `es_examen`. |

Si se intenta marcar como examen un contenido de tipo `texto`, la API responde `400` (regla de
dominio: "solo un ejercicio interactivo puede marcarse como examen").

### 2. Modelo de datos

`content` gana la columna `is_exam` (Boolean, default `false`). **Migración Alembic 016**. El campo de
dominio es `Contenido.es_examen`; la invariante (solo interactivo) se valida en el agregado
(`__post_init__` y `marcar_examen`).

### 3. Catálogo (frontend)

`CatalogoPage` ordena cada lista de ejercicios con `examenesAlFinal()` (orden estable: los exámenes
quedan al final conservando el orden del resto) y la tarjeta muestra un badge `cms-badge-examen` con el
icono 📝. La búsqueda **no** se reordena (manda la relevancia).

### 4. Instalación / despliegue

```
cd plataforma-educativa
docker compose up -d --build
# El entrypoint corre alembic upgrade head: la migración 016 añade is_exam (default false).
```

### 5. Tests

```
cd backend && python -m pytest tests/unit tests/integration -q   # 219 (3 nuevos)
cd frontend && npm run test:e2e                                  # 9 E2E
```

Nuevos: crear interactivo marcado como examen; rechazo de marcar un texto como examen (400);
marcar/desmarcar por edición.

---

## Parte II — Manual de usuario

### 6. Marcar un ejercicio como examen (editor/admin)

1. Crea o edita un contenido de tipo **Ejercicio interactivo (HTML)**.
2. Marca el check **«Examen»**.
3. Sube el fichero HTML del examen (puede ser la fusión de varios ejercicios que prepares aparte) y
   publícalo.
4. En el catálogo, el examen aparecerá **al final** de su lista, con un distintivo 📝 que lo diferencia
   de los ejercicios normales.

### 7. Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.21.0) | Ejercicios tipo "Examen" (marca + orden al final + icono en el catálogo). |
| Hecho (V-0.20.1) | Correcciones de auditoría (integridad de taxonomía, publicar, buffer de visitas). |
| Hecho (V-0.20.0) | Importar / restaurar el sitio (BD + media). |
