# CLAUDE.md

> Archivo de contexto y reglas para asistentes de IA (Claude Code / extensión de VS Code) y
> para el equipo humano. Es la **fuente de verdad operativa** del proyecto. Si una decisión
> contradice este archivo, primero se actualiza este archivo (vía PR) y luego se implementa.
> Complementa a `docs/ARCHITECTURE.md`, que describe la arquitectura de referencia.

---

## 1. Contexto del proyecto

Plataforma web (escritorio y móvil) tipo **CMS educativo** para alojar y ejecutar **ejercicios
interactivos** (HTML/CSS/JS autocontenidos, ejecución en cliente) y **artículos de texto**,
dirigidos a alumnado de **infantil y primaria** en España.

- Acceso **público** sin cuentas de alumno.
- Dos roles privilegiados: **`admin`** (configuración del sitio + contenidos) y **`editor`**
  (crear, modificar y borrar contenidos).
- Nombre y logotipo del sitio son **configurables** desde administración.
- Proyecto personal/open-source con monetización ligera (anuncios/afiliación **solo en zonas de
  adultos** y donaciones) para sostener el VPS.

## 2. Objetivos

1. Publicar y ejecutar ejercicios educativos de forma **segura para menores**.
2. Permitir a editores **gestionar contenidos** (CRUD, versionado, papelera) con baja fricción.
3. Ofrecer a familias/alumnos **descubrir contenido** por catálogo y buscador.
4. **Sostenibilidad** económica sin comprometer la privacidad ni la legalidad (DSA/RGPD).
5. **Mantenibilidad** por una sola persona: simplicidad por encima de la sofisticación.

## 3. Principios arquitectónicos

- **Monolito modular + Arquitectura Hexagonal** (Ports & Adapters) + **Clean Architecture**.
- **DDD táctico ligero**: contextos acotados como módulos; lenguaje ubicuo en español.
- **Regla de dependencia**: `infrastructure -> application -> domain`. El **dominio no conoce
  FastAPI ni SQLAlchemy**. Jamás.
- **CQRS solo lógico** (separación lectura/escritura, sin segunda BD).
- **Eventos de dominio en proceso** para auditoría y conteo de visitas. Sin broker.
- **Twelve-Factor App**: config por entorno, procesos sin estado, logs a stdout.
- **Privacy & Security by Design**: minimización de datos, aislamiento del contenido no confiable.
- **Documentation as Code**: las decisiones viven en el repositorio.
- **No sobre-ingeniería**: sin microservicios, sin event sourcing, sin Kubernetes.

## 4. Estándares de código

### Backend (Python)
- Python 3.12+. `ruff` (lint) + `black` (formato) + `mypy` (tipado estricto en dominio/aplicación).
- Funciones puras y pequeñas; sin lógica de negocio en routers ni en repos.
- Errores de dominio como **excepciones de dominio** propias, mapeadas a HTTP en la capa API.
- Inyección de dependencias explícita (wiring en `bootstrap.py`), nada de imports globales ocultos.
- Nada de SQL ni `Session` de SQLAlchemy fuera de `infrastructure/`.

### Frontend (React)
- TypeScript estricto. `eslint` + `prettier`. Componentes funcionales + hooks.
- Cliente de API **generado desde el OpenAPI** del backend (no escribir tipos a mano).
- Sin estado global innecesario; preferir estado local y data-fetching declarativo.

## 5. Convenciones de nomenclatura

- **Lenguaje ubicuo del dominio en español**: `Contenido`, `Ciclo`, `Curso`, `Asignatura`,
  `Etiqueta`, `Version`, `Usuario`, `ConfiguracionSitio`. Términos técnicos/infra en inglés.
- **Python**: `snake_case` (módulos/funciones), `PascalCase` (clases), `UPPER_SNAKE` (constantes).
- **TypeScript/React**: `camelCase` (variables/funciones), `PascalCase` (componentes/tipos).
- **CSS del armazón (anti-colisión)**: **todas** las clases del CMS van **prefijadas**
  (`cms-…`, p. ej. `.cms-titulo`, `.cms-card`). No usar selectores de elemento desnudos
  (`h1 { }`); usar `.cms-h1` o equivalentes prefijados. Esto evita conflictos con los estilos
  propios del HTML de artículos. (Los ejercicios interactivos ya están aislados por iframe.)
- **Ramas Git**: `feat/…`, `fix/…`, `chore/…`, `docs/…`, `refactor/…`, `test/…`.
- **Tablas BD**: `snake_case` singular (`content`, `content_version`, `audit_log`).

## 6. Estructura de carpetas

Ver `docs/ARCHITECTURE.md` §6. Resumen:
- `backend/app/contexts/<contexto>/{domain,application,infrastructure,api}`
- `backend/app/shared/{domain,application,infrastructure}`
- `frontend/src/{app,pages,features,shared,styles}`
- Contextos: `content`, `taxonomy`, `identity`, `media`, `auditing`, `analytics`, `configuration`.

## 7. Reglas de dominio

- El **dominio es puro**: sin imports de FastAPI, SQLAlchemy, Pydantic de request, ni I/O.
- Los **agregados** protegen sus invariantes; no se permite construir un agregado en estado inválido.
- Los **puertos** (interfaces de repositorio/servicios) se declaran en `domain/`; los implementa
  `infrastructure/`.
- Comunicación entre contextos **solo** vía casos de uso de aplicación o **eventos de dominio**.
  Está prohibido importar un modelo de un contexto dentro de otro.
- Reglas concretas:
  - Un `Contenido` tiene `tipo ∈ {interactivo, texto}` y ese tipo determina su almacenamiento.
  - `interactivo` ⇒ referencia a `FicheroHtml` por hash. `texto` ⇒ `body_html` sanitizado.
  - Cada modificación crea una **versión inmutable** (`content_version`). Restaurar nunca destruye.
  - Borrar es **lógico** (papelera); la purga es una operación explícita y programada.
  - `ciclo`, `curso` y `asignatura` provienen de **catálogos configurables**, no son enums fijos.

## 8. Reglas de persistencia

- BD: **SQLite en modo WAL**. Toda escritura va por la **unit of work** del caso de uso.
- **Migraciones siempre con Alembic**; nunca alterar el esquema a mano. Un cambio de modelo ⇒
  una migración en el mismo PR.
- Repositorios: una interfaz (puerto) por agregado; implementación SQLAlchemy en `infrastructure/`.
- **Búsqueda** mediante FTS5 (`content_fts`), mantenida por triggers o desde el repositorio.
- **Ficheros HTML**: content-addressed (`sha256`), **inmutables**, nunca se sobrescriben.
- **Contador de visitas**: agregar en memoria y **volcar por lotes** (tarea en segundo plano);
  nunca una escritura por petición.

## 9. Reglas de API

- REST sobre FastAPI. Esquemas de entrada/salida con Pydantic en la capa `api/` (no en el dominio).
- Versionar la API bajo prefijo (`/api/v1`). Respuestas de error consistentes (problema + código).
- La **API es el contrato**: cualquier cambio de contrato se refleja en OpenAPI y regenera el
  cliente del frontend en el mismo PR.
- Endpoints públicos (lectura de catálogo, contenido, búsqueda) **sin autenticación**.
- Endpoints de gestión **siempre** tras guarda de rol (`admin`/`editor` según corresponda).
- Servir ejercicios **siempre** desde el subdominio sandbox, **nunca** desde el origen de la app.

## 10. Reglas de seguridad

- **Aislamiento obligatorio del sandbox**: ejercicios en iframe con `sandbox` (con `allow-scripts`,
  **sin** `allow-same-origin`) servidos desde `sandbox.<dominio>` con CSP estricta.
- **Nunca** renderizar HTML de ejercicio en el origen de la app.
- **Sanitización asimétrica**: sanitizar SIEMPRE el HTML de artículos (servidor + cliente).
  **No** sanitizar el HTML de ejercicios (debe ejecutar JS): por eso va aislado.
- Contraseñas con **Argon2id** (o bcrypt). Sesiones/JWT con expiración. Sin contraseñas en logs.
- **Secretos por variable de entorno**; prohibido commitearlos. `.env` fuera del control de versiones.
- Cabeceras de seguridad en el proxy: CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`.
- **Menores y datos**: sin cuentas de alumno, sin cookies de seguimiento, visitas anónimas y
  agregadas. Publicidad/afiliación **solo en zonas de adultos**; jamás publicidad perfilada (DSA art. 28).

## 11. Reglas de testing

- Todo caso de uso del dominio/aplicación lleva **test unitario**.
- Todo endpoint nuevo lleva **test de integración**.
- Cambios de contrato ⇒ verificación contra **OpenAPI** + regeneración del cliente.
- Flujos críticos cubiertos con **E2E** (Playwright): navegar, buscar, pantalla completa, login + CRUD.
- Mantener el **test de seguridad del sandbox** (el JS del ejercicio no alcanza el origen padre).
- Los tests no dependen de red ni de estado externo; SQLite temporal por test.

## 12. Reglas de documentación

- Toda decisión arquitectónica relevante se registra en `docs/ARCHITECTURE.md` (o un ADR).
- El código se autoexplica; los comentarios explican el **porqué**, no el **qué**.
- README con arranque local en < 5 minutos (Docker). Variables de entorno documentadas.
- Mantener este `CLAUDE.md` y `ARCHITECTURE.md` **sincronizados** con la realidad del código.

## 13. Reglas de Git

- **Trunk-based** con ramas de vida corta. `main` siempre desplegable.
- **Conventional Commits**: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.
- Commits pequeños y atómicos. Nada de "WIP" en `main`.
- Prohibido commitear secretos, `.env`, ni la base de datos.

## 14. Reglas de Pull Request

- Una PR = un objetivo. Descripción del **qué** y el **porqué**.
- CI en verde obligatorio (lint, types, tests, build, E2E de los flujos afectados).
- Incluye migración Alembic si cambia el modelo, y tests si cambia comportamiento.
- Auto-revisión con el **checklist de revisión** (§18) antes de pedir merge.

## 15. Reglas para generación automática de código (IA)

Al generar o modificar código, el asistente **debe**:
- Respetar la **regla de dependencia**: nunca importar framework/infra en `domain/`.
- Colocar el código en el **contexto** correcto y en la **capa** correcta.
- Definir/usar **puertos** en el dominio e implementarlos en infraestructura (no acoplar).
- Añadir **tests** (unitario y, si aplica, integración) en el mismo cambio.
- Crear **migración Alembic** ante cualquier cambio de esquema.
- **Nunca** sanitizar el HTML de ejercicios; **siempre** sanitizar el HTML de artículos.
- **Nunca** servir ejercicios desde el origen de la app; usar el subdominio sandbox.
- Usar **clases CSS prefijadas** (`cms-…`); no introducir selectores de elemento desnudos.
- No introducir dependencias pesadas (broker, microservicios, nuevas BD) sin un ADR aprobado.
- Ante ambigüedad de diseño, **preguntar** antes de asumir; no improvisar arquitectura.

## 16. Definición de Terminado (Definition of Done)

Una tarea está terminada cuando:
- [ ] Cumple el criterio de aceptación de la historia.
- [ ] Respeta capas, contextos y la regla de dependencia.
- [ ] Tiene tests (unitario/integración) y todos pasan; E2E afectados en verde.
- [ ] Incluye migración Alembic si cambió el modelo.
- [ ] Lint, formato y type-check en verde.
- [ ] OpenAPI y cliente del frontend regenerados si cambió el contrato.
- [ ] Documentación actualizada (`CLAUDE.md`/`ARCHITECTURE.md`/README según aplique).
- [ ] Sin secretos ni datos sensibles en el código ni en logs.

## 17. Checklist para nuevas funcionalidades

- [ ] ¿A qué **contexto** pertenece? ¿Necesita uno nuevo (requiere ADR)?
- [ ] Modelo de dominio: agregados, value objects, invariantes, eventos.
- [ ] Puertos necesarios y sus adapters de infraestructura.
- [ ] Casos de uso (comandos/consultas) y su wiring.
- [ ] Migración Alembic y, si aplica, índice/entrada FTS.
- [ ] Endpoints + esquemas + guardas de autorización.
- [ ] Impacto en seguridad (¿toca el sandbox? ¿HTML no confiable? ¿datos de menores?).
- [ ] Tests (unitario, integración, E2E si es flujo crítico).
- [ ] Frontend: feature, componentes prefijados, cliente regenerado.
- [ ] Documentación y entrada en el roadmap si cambia el alcance.

## 19. Proceso de lanzamiento de versión (obligatorio tras cada entrega)

Al terminar cada conjunto de cambios entregado al usuario, el asistente de IA **debe** ejecutar
automáticamente los siguientes pasos **en este orden**, sin esperar instrucciones adicionales:

### 19.1 Asignación de versión

Seguir semver estricto (`V-MAJOR.MINOR.PATCH`):

| Dígito | Cuándo avanza | Quién decide |
|--------|---------------|--------------|
| `PATCH` (tercero) | Bug fix o cambio menor sin nueva funcionalidad | Automático |
| `MINOR` (segundo) | Nueva funcionalidad compatible con versiones anteriores | **Preguntar** antes de avanzar |
| `MAJOR` (primero) | Cambio disruptivo (breaking change, rediseño) | Solo si se pide explícitamente |

La versión actual se lee de `CHANGELOG.md` (última entrada) o se inicializa en `V-1.0.0`.

### 19.2 Actualizar CHANGELOG.md

Fichero en la raíz del proyecto. Formato:

```
## [V-X.Y.Z] - YYYY-MM-DD

### Añadido
- ...

### Cambiado
- ...

### Corregido
- ...
```

### 19.3 Generar manual técnico y de usuario (PDF)

- Crear o actualizar `docs/manual-v{VERSION}.md` con el contenido completo.
- Convertir a PDF usando Python (`fpdf2` o `reportlab`; instalar si no está disponible).
- Guardar como `docs/manual-v{VERSION}.pdf`.
- El manual incluye: descripción del sistema, endpoints de la API, modelo de datos,
  guía de instalación/despliegue, y manual de uso para admin/editor.

### 19.4 Generar zip de distribución

- Crear `dist/plataforma-educativa-v{VERSION}.zip` con todo lo necesario para desplegar en VPS.
- Incluir: `docker-compose.yml`, `backend/`, `frontend/`, `nginx/` (si existe), `.env.example`.
- Excluir: `__pycache__/`, `*.pyc`, `node_modules/`, `dist/`, `.env`, `data/`, `media/`,
  `*.sqlite3`, `*.zip`, `.git/`.

### 19.5 Commit en Git

- Inicializar el repositorio si no existe (`git init`).
- Stage de todos los ficheros relevantes (excluir los del `.gitignore`).
- Mensaje de commit siguiendo Conventional Commits:
  `release: V-X.Y.Z — <resumen de una línea de los cambios principales>`.

---

## 18. Checklist para revisiones de código

- [ ] ¿El dominio sigue puro (sin framework/infra)?
- [ ] ¿Las dependencias apuntan hacia adentro?
- [ ] ¿La lógica de negocio está en aplicación/dominio y no en routers o repos?
- [ ] ¿Se respeta el aislamiento del sandbox y la sanitización asimétrica?
- [ ] ¿Hay migración para el cambio de esquema? ¿Es reversible?
- [ ] ¿El contador de visitas/escrituras de alta frecuencia van por lotes?
- [ ] ¿Tests adecuados y significativos (no solo cobertura cosmética)?
- [ ] ¿Nombres en lenguaje ubicuo? ¿Clases CSS prefijadas?
- [ ] ¿Secretos fuera del código? ¿Logs sin datos sensibles?
- [ ] ¿Complejidad justificada o hay una solución más simple?
