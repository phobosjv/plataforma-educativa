# Tests E2E (Playwright)

Cobertura de los flujos críticos exigidos por CLAUDE.md §11, ejecutados en un navegador real
contra la pila completa (API + sandbox + frontend) levantada automáticamente por Playwright.

## Qué cubren

| Spec | Flujo |
|---|---|
| `catalogo.spec.ts` | Navegación pública: curso → asignatura → ejercicio → ficha |
| `sandbox-seguridad.spec.ts` | **Aislamiento del sandbox** (§10): iframe `allow-scripts` sin `allow-same-origin`, origen sandbox distinto, y el JS del ejercicio **no alcanza el origen padre** |
| `ejercicio-pantalla-completa.spec.ts` | Maximizar el ejercicio y salir con Escape |
| `admin-login-crud.spec.ts` | Login de admin + crear y borrar (papelera) un artículo |

## Cómo se orquesta

`playwright.config.ts` levanta tres servidores en **puertos aislados** (no chocan con los de
desarrollo ni con sockets huérfanos en Windows):

- API en `:8101` (precedida de `scripts/seed_e2e.py`, que crea una **BD e2e fresca**)
- sandbox en `:8102`
- frontend (Vite) en `:5273`

Todo opera sobre una BD y una carpeta media **aisladas** (`backend/data/e2e.sqlite3`,
`backend/data/e2e-media`), con el scheduler de backups/purga desactivado. El seed crea un admin,
una taxonomía mínima, un ejercicio interactivo (con un HTML que intenta escapar del sandbox) y un
artículo.

## Ejecutar

```bash
cd frontend
npm install
npx playwright install chromium   # una vez: descarga el navegador
npm run test:e2e                  # ejecuta la suite (arranca y para los servidores solo)
npm run test:e2e:ui               # modo interactivo (UI)
```

Requisitos: el `python` del sistema con las dependencias del backend instaladas y `uvicorn`
disponible (los mismos que para `pytest`). El informe HTML queda en `frontend/playwright-report/`.
