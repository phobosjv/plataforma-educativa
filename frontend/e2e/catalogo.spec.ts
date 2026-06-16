import { expect, test } from "@playwright/test";

// Navegación pública guiada: curso -> asignatura -> ejercicio -> ficha del contenido.
test("el catálogo navega de curso a asignatura y abre un ejercicio", async ({ page }) => {
  await page.goto("/");

  // Pantalla 1: elegir curso.
  await expect(page.getByText("¿En qué curso estás?")).toBeVisible();
  await page.getByRole("button", { name: /3º E2E/ }).click();

  // Pantalla 2: elegir asignatura.
  await expect(page.getByText("¿Qué quieres aprender?")).toBeVisible();
  await page.getByRole("button", { name: /Mates E2E/ }).click();

  // Pantalla 3: tarjetas de contenido; abrir el ejercicio interactivo.
  await page.getByRole("link", { name: /Ejercicio E2E/ }).click();

  // Ficha del contenido: título e iframe del ejercicio.
  await expect(page.getByRole("heading", { name: "Ejercicio E2E" })).toBeVisible();
  await expect(page.locator("iframe.cms-exercise-frame")).toBeVisible();
});
