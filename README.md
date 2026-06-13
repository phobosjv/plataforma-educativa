# Plataforma Educativa (CMS de ejercicios — infantil y primaria)

CMS para alojar y ejecutar **ejercicios interactivos** (HTML/CSS/JS autocontenidos) y
**artículos de texto**, dirigidos a alumnado de infantil y primaria. Acceso público sin cuentas
de alumno; gestión mediante roles `admin` y `editor`.

- **Backend:** FastAPI + SQLite (WAL) + Alembic — arquitectura hexagonal modular.
- **Frontend:** React + Vite.
- **Despliegue:** Docker sobre VPS único.

## Documentación
- `CLAUDE.md` — reglas operativas y contexto para IA y equipo (fuente de verdad).
- `docs/ARCHITECTURE.md` — arquitectura de referencia.
- `docs/analisis/analisis-proyecto.pdf` — análisis completo del proyecto (con gráficos).
- `docs/analisis/analisis-proyecto.md` — misma versión en Markdown (para consulta por IA).

## Arranque rápido (desarrollo)
```bash
cp .env.example .env        # ajusta los valores
docker compose up --build   # api:8000 · sandbox:8080 · frontend:5173
```

## Estructura
```
backend/app/contexts/<contexto>/{domain,application,infrastructure,api}
backend/app/shared/{domain,application,infrastructure}
frontend/src/{app,pages,features,shared,styles}
```
Contextos: content · taxonomy · identity · media · auditing · analytics · configuration.

## Seguridad (resumen)
Los ejercicios se sirven **siempre** desde un subdominio aislado (`sandbox.*`) en iframe con CSP.
El HTML de artículos se sanitiza; el de ejercicios no (por eso va aislado). Ver `CLAUDE.md` §10.

## Licencia
Por definir (proyecto open-source).
