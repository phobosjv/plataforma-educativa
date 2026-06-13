# Changelog

Todos los cambios notables de este proyecto se documentan en este fichero.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/).
Versionado según [Semver](https://semver.org/lang/es/) con prefijo `V-`.

---

## [V-0.1.0] - 2026-06-13

### Añadido

#### Contexto `taxonomy` (ciclos, cursos, asignaturas)
- Dominio: agregados `Ciclo`, `Curso` y `Asignatura` con validación en `__post_init__` y método `actualizar()`
- Puertos `CicloRepository`, `CursoRepository`, `AsignaturaRepository` en dominio
- Casos de uso CRUD completos para las tres entidades (crear, actualizar, eliminar, listar, obtener)
- `CrearCursoHandler` valida la existencia del ciclo padre antes de persistir
- Repositorios SQLAlchemy con `list_by_ciclo()` en cursos
- Migración Alembic `003`: tablas `ciclo`, `curso` (FK → ciclo), `asignatura`
- API REST bajo `/api/v1/taxonomy/`: endpoints públicos (GET) y protegidos por `require_admin` (POST/PUT/DELETE)
- `GET /api/v1/taxonomy/cursos/?ciclo_id=...` para filtrar cursos por ciclo
- 23 tests nuevos (11 unitarios + 12 integración) — 67 tests en total, todos pasan

---

## [V-0.0.2] - 2026-06-13

### Corregido
- Eliminado `test_contenido.py` del esqueleto inicial (sustituido por `test_contenido_lifecycle.py`).
- Eliminado `shared/application/buses.py` del esqueleto (CommandBus/QueryBus no usado).
- Corregida versión de la API en `main.py`: `"0.1.0"` → `"0.0.1"`.
- Eliminados `data/` raíz y `.env` raíz creados accidentalmente al arrancar el servidor.

---

## [V-0.0.1] - 2026-06-13

### Añadido

#### Infraestructura compartida
- `shared/infrastructure/database.py` — motor SQLite WAL, `Base` ORM única, `get_db()` dependency
- `shared/infrastructure/unit_of_work.py` — Unit of Work para gestionar commit/rollback por caso de uso
- `shared/domain/base.py` — subclases de `DomainError`: `NotFoundError`, `AuthenticationError`, `AuthorizationError`

#### Contexto `identity` (autenticación y usuarios)
- Dominio: agregado `Usuario` con `Rol` (admin/editor), validación de email, métodos `crear`, `cambiar_password`, `desactivar`
- Puerto `AuthService` (protocolo) en dominio; implementado como `ArgonAuthService` (Argon2id + JWT HS256)
- Puerto `UsuarioRepository`; implementado como `SqlAlchemyUsuarioRepository`
- Casos de uso: `LoginHandler`, `CrearUsuarioHandler`, `ListarUsuariosHandler`
- API REST: `POST /api/v1/auth/token`, `GET /api/v1/users/`, `POST /api/v1/users/`
- Guardas de rol: `require_admin`, `require_editor_or_admin`

#### Contexto `content` (contenidos educativos)
- Dominio: `Contenido` extendido con ciclo de vida completo (`publicar`, `archivar`, `borrar`, `restaurar`)
- `ContentVersion` — snapshot inmutable creado en cada mutación
- Puerto `ContenidoRepository` completo (add, get, save, list_published, list_all, list_trash, delete_permanent)
- Puerto `ContentVersionRepository`; `HtmlStorage` (almacén content-addressed SHA-256)
- Casos de uso: crear, actualizar, publicar, archivar, borrar (soft), restaurar, listar, obtener
- `FileSystemHtmlStorage` — escrituras atómicas con `os.replace`
- API REST: catálogo público, CRUD editor+, panel admin

#### Persistencia
- Modelos ORM SQLAlchemy 2.0: `UsuarioModel`, `ContenidoModel`, `ContentVersionModel`
- Migraciones Alembic: `001_create_user_table`, `002_create_content_tables`
- `bootstrap.py` — registro de modelos ORM con `Base.metadata`

#### Tests
- 27 tests unitarios (dominio + handlers con mocks)
- 19 tests de integración (endpoints identity + content con SQLite en memoria + `StaticPool`)
- 46/46 tests pasan

#### Proceso de lanzamiento
- Sección §19 en `CLAUDE.md` — proceso de versión, manual PDF, zip y commit automatizados
