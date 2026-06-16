import { expect, test, type Page } from "@playwright/test";

// Localiza el primer contenido interactivo publicado y abre su ficha.
async function abrirEjercicio(page: Page): Promise<void> {
  const res = await page.request.get("/api/v1/contenidos/");
  expect(res.ok()).toBeTruthy();
  const lista: Array<{ id: string; tipo: string }> = await res.json();
  const ejercicio = lista.find((c) => c.tipo === "interactivo");
  expect(ejercicio, "debe existir un ejercicio interactivo sembrado").toBeTruthy();
  await page.goto(`/contenido/${ejercicio!.id}`);
}

// Test de seguridad del sandbox (CLAUDE.md §10/§11): el ejercicio se sirve aislado y su
// JavaScript NO puede alcanzar el origen padre.
test("el ejercicio se sirve aislado en un iframe sandbox", async ({ page }) => {
  await abrirEjercicio(page);
  const iframe = page.locator("iframe.cms-exercise-frame");
  await expect(iframe).toBeVisible();

  // 1. Estructural: sandbox=allow-scripts SIN allow-same-origin, y origen sandbox distinto.
  await expect(iframe).toHaveAttribute("sandbox", "allow-scripts");
  await expect(iframe).toHaveAttribute("src", /^http:\/\/localhost:8102\/ejercicio\/[0-9a-f]{64}$/);
});

test("el JavaScript del ejercicio no alcanza el origen padre", async ({ page }) => {
  await abrirEjercicio(page);

  // El HTML del ejercicio intenta leer window.parent.document; al estar aislado (sin
  // allow-same-origin) lanza SecurityError y marca data-sandbox="aislado".
  const cuerpo = page.frameLocator("iframe.cms-exercise-frame").locator("body");
  await expect(cuerpo).toHaveAttribute("data-sandbox", "aislado");
  await expect(
    page.frameLocator("iframe.cms-exercise-frame").locator("#resultado-sandbox"),
  ).toHaveText("aislado");
});
