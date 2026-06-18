# Plataforma Educativa — Manual Técnico y de Usuario · V-0.20.0

> CMS educativo interactivo para infantil y primaria. Acceso público sin cuentas de alumno.
> Roles `admin` y `editor`. Arquitectura hexagonal. Fecha: 2026-06-18 · Licencia: MIT.

---

## Novedades de V-0.20.0 — Importar / restaurar el sitio

Operación **inversa de «Exportar todo»**: el administrador sube el archivo `.tar.gz` de
exportación (base de datos + media + `manifest.json`) y el sitio destino queda **restaurado o
migrado** con ese contenido. Casos de uso: poner en marcha una **web en blanco** con el contenido
de otra (migración de servidor) o **recuperar tras un fallo total**.

Es una operación **destructiva** (reemplaza la base de datos y restaura la media), por eso:

- Exige escribir `IMPORTAR` para confirmar.
- Crea **automáticamente una copia de seguridad de la BD actual** antes de sobrescribir (rollback).
- Tras importar, la BD se lleva al esquema actual (`alembic upgrade head`): una exportación de una
  versión anterior queda **migrada** a la versión que corre el servidor de destino.
- La sesión del administrador puede dejar de ser válida (el usuario procede de la BD importada): se
  cierra sesión y se vuelve al login para entrar con las credenciales del sitio importado.

---

## Parte I — Manual técnico

### 1. API

| Endpoint | Descripción |
|---|---|
| `POST /api/v1/admin/import` (admin) | Sube el `.tar.gz` (`multipart`: `fichero` + `confirmacion=IMPORTAR`). Restaura BD + media. |
| `POST /api/v1/admin/export` (admin) | (existente) Genera y descarga el `.tar.gz` de exportación. |

Respuesta de import: `{ ok, num_ficheros_media, app_version_importada, backup_seguridad, detalle }`.

### 2. Cómo funciona (seguridad y robustez)

`ImportService` (capa de infraestructura, sin FastAPI ni dominio):

1. **Extracción segura** del `.tar.gz`: solo se aceptan entradas bajo `data/`, `media/` y el
   `manifest.json`; se rechazan rutas absolutas o con `..` (sin *path traversal*) y se ignoran
   enlaces simbólicos y dispositivos.
2. **Validación**: `manifest.formato` soportado e **integridad SQLite** del fichero de BD
   (`PRAGMA integrity_check`).
3. **Copia de seguridad** de la BD actual (rollback) antes de tocar nada.
4. **Cierre de conexiones** del pool (`engine.dispose()`).
5. **Restauración de media** (mezcla; los ficheros son content-addressed inmutables).
6. **Intercambio atómico** del fichero de BD con `os.replace` (rename): las conexiones aún abiertas
   conservan el inodo antiguo y las nuevas abren ya la BD importada, sin corromper nada. Se eliminan
   los `-wal`/`-shm` obsoletos.

Después, el endpoint ejecuta `alembic upgrade head` para migrar el esquema si la exportación era de
una versión anterior.

### 3. Modelo de datos

Sin cambios de esquema propios de esta versión: **no hay migración nueva**.

### 4. Tests

```
cd backend && python -m pytest tests/unit tests/integration -q   # 211 (6 nuevos de import)
cd frontend && npm run test:e2e                                  # 9 E2E
```

Cobertura de import: requiere admin (401/403), confirmación obligatoria, archivo inválido, manifest
no soportado y un **round-trip** export→import que verifica que la BD y la media quedan restauradas.

---

## Parte II — Manual de usuario

### 5. Migrar o restaurar el sitio (admin)

1. En el sitio de **origen**: «Copias de seguridad» → **Exportar todo (BD + media)**; guarda el
   `.tar.gz`.
2. En el sitio de **destino** (puede estar en blanco): «Copias de seguridad» → sección **«Importar /
   restaurar el sitio»**.
3. Selecciona el archivo `.tar.gz`, escribe **`IMPORTAR`** en el cuadro de confirmación y pulsa
   **«Importar y reemplazar el sitio»**.
4. Al terminar se cierra la sesión: vuelve a entrar con las **credenciales del sitio importado**. La
   web queda con el contenido, la configuración, los usuarios y la media del origen.

> Antes de sobrescribir se guarda una copia de seguridad de la base de datos actual, por si necesitas
> revertir.

### 6. Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.20.0) | Importar / restaurar el sitio (BD + media) desde una exportación. |
| Hecho (V-0.19.2) | Pie público y acciones de admin/editor siempre visibles. |
| Hecho (V-0.19.1) | Backend sin privilegios (no-root) en Docker. |
