import { defineConfig, devices } from "@playwright/test";
import path from "node:path";

// Puertos AISLADOS para E2E (distintos de los de desarrollo 8001/8002/5173) para no
// chocar con servidores de dev ni con sockets huérfanos en Windows.
const FRONT_URL = "http://localhost:5273";
const API_URL = "http://localhost:8101";
const SANDBOX_URL = "http://localhost:8102";

// La config se ejecuta desde frontend/ (npm run test:e2e); el backend está al lado.
const BACKEND = path.resolve(process.cwd(), "..", "backend");

// Entorno común de los procesos Python: BD y media e2e AISLADAS, scheduler desactivado,
// sandbox/orígenes apuntando a los puertos e2e.
const backendEnv: Record<string, string> = {
  DATABASE_URL: "sqlite:///./data/e2e.sqlite3",
  MEDIA_DIR: "./data/e2e-media",
  SECRET_KEY: "e2e-secret-key-not-for-prod-min-32-bytes-largo",
  ENVIRONMENT: "test",
  SANDBOX_BASE_URL: SANDBOX_URL,
  APP_ORIGINS: FRONT_URL,
  CORS_ALLOW_ORIGINS: FRONT_URL,
  BACKUP_ENABLED: "false",
  MEDIA_BACKUP_ENABLED: "false",
  TRASH_PURGE_ENABLED: "false",
  PYTHONUTF8: "1",
  PYTHONIOENCODING: "utf-8",
};

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1, // los tests comparten la BD e2e sembrada; en serie evita interferencias
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["html", { open: "never" }]],
  timeout: 30_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: FRONT_URL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      // El comando siembra una BD e2e fresca y luego arranca la API.
      command:
        "python scripts/seed_e2e.py && python -m uvicorn app.main:app --host 127.0.0.1 --port 8101",
      cwd: BACKEND,
      url: `${API_URL}/health`,
      env: backendEnv,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: "python -m uvicorn app.sandbox:sandbox_app --host 127.0.0.1 --port 8102",
      cwd: BACKEND,
      url: `${SANDBOX_URL}/health`,
      env: backendEnv,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: "npx vite --port 5273 --strictPort",
      cwd: process.cwd(),
      url: FRONT_URL,
      env: { VITE_API_TARGET: API_URL },
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
