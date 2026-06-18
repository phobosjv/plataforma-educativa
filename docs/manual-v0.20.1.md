# Plataforma Educativa — Manual Técnico y de Usuario · V-0.20.1

> CMS educativo interactivo para infantil y primaria. Acceso público sin cuentas de alumno.
> Roles `admin` y `editor`. Arquitectura hexagonal. Fecha: 2026-06-18 · Licencia: MIT.

---

## Novedades de V-0.20.1 — Correcciones (auditoría de lógica)

Release de corrección con tres arreglos surgidos de un análisis en profundidad de la lógica de
la aplicación:

1. **Integridad referencial al borrar taxonomía.** SQLite no fuerza las claves foráneas, de modo
   que borrar un **ciclo** que tenía cursos, o un **curso/asignatura** referenciado por contenidos,
   dejaba referencias "colgando" y hacía que ese contenido **desapareciera silenciosamente** de la
   navegación del catálogo (aunque siguiera publicado). Ahora el borrado se **bloquea** con un
   `409 Conflict` y un mensaje claro, contando también el contenido en la papelera (puede
   restaurarse). La página de Taxonomía del panel muestra el motivo del bloqueo.
2. **No se puede publicar un ejercicio interactivo sin su fichero HTML.** Antes se podía publicar un
   ejercicio "a medias" que en público mostraba una página vacía; ahora `publicar()` lo rechaza.
3. **Importar ya no arrastra visitas del sitio anterior.** Tras una importación, el contador de
   visitas en memoria (con IDs del sitio antiguo) se descarta, para no volcarlo como filas huérfanas
   en el sitio recién importado.

Sin cambios de esquema ni de contrato de la API.

---

## Parte I — Manual técnico

### 1. Cambios

| Área | Cambio |
|---|---|
| `taxonomy` (dominio/aplicación) | Nuevo puerto `ContenidoEnTaxonomia`; los handlers `Eliminar*` comprueban dependencias y lanzan `DomainError`. |
| `content` (infraestructura) | Adapter `SqlAlchemyContenidoEnTaxonomia` (cuenta contenidos por curso/asignatura, incluida la papelera). |
| `taxonomy` (API) | Los endpoints de borrado devuelven `409 Conflict` con el motivo. |
| `content` (dominio) | `Contenido.publicar()` exige `hash_html` en los interactivos. |
| `maintenance` (API) | El endpoint de importación vacía el buffer de visitas en memoria tras importar. |
| Frontend `TaxonomiaPage` | Las acciones de borrado muestran el error del backend (antes se silenciaba). |

### 2. Regla de dependencia

El puerto `ContenidoEnTaxonomia` se declara en el dominio de `taxonomy`; su implementación vive en
la infraestructura de `content` y se inyecta en el router (capa de composición). Así `taxonomy` no
importa `content`: la dependencia apunta hacia adentro, como exige la arquitectura.

### 3. Tests

```
cd backend && python -m pytest tests/unit tests/integration -q   # 216 (6 nuevos)
cd frontend && npm run test:e2e                                  # 9 E2E
```

Nuevos: borrar ciclo con cursos / curso con contenido / asignatura con contenido (409) y borrado
limpio (204); publicar interactivo sin HTML (400); el buffer de visitas se vacía tras importar.

---

## Parte II — Manual de usuario

### 4. Borrado de taxonomía

Si intentas borrar un ciclo, curso o asignatura que todavía tiene elementos asociados (cursos o
contenidos), el panel te avisará y **no** lo borrará, para no dejar contenido "huérfano" fuera de la
navegación. Reasigna o elimina primero esos elementos.

### 5. Publicar ejercicios

Un ejercicio interactivo solo puede publicarse **después** de subir su fichero HTML. Si lo intentas
antes, verás un aviso.

### 6. Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.20.1) | Correcciones: integridad de taxonomía, publicar interactivo, buffer de visitas en import. |
| Hecho (V-0.20.0) | Importar / restaurar el sitio (BD + media) desde una exportación. |
| Hecho (V-0.19.1) | Backend sin privilegios (no-root) en Docker. |
