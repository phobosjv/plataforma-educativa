import { expect, test } from "@playwright/test";

// Flujo crítico (CLAUDE.md §11): buscar en el catálogo público.
test("el buscador encuentra contenidos por texto (sin tildes)", async ({ page }) => {
  await page.goto("/");

  // El cuadro de búsqueda está en la portada. Buscar "articulo" (sin tilde) debe
  // encontrar "Artículo E2E" gracias a la normalización de acentos del índice FTS5.
  await page.getByRole("searchbox", { name: /Buscar en el catálogo/ }).fill("articulo");
  await page.getByRole("button", { name: /Buscar/ }).click();

  await expect(page.getByText(/Resultados de/)).toBeVisible();
  await expect(page.getByRole("link", { name: /Artículo E2E/ })).toBeVisible();
  // El ejercicio interactivo no contiene "articulo": no debe aparecer.
  await expect(page.getByRole("link", { name: /^Ejercicio E2E/ })).toHaveCount(0);
});

test("el buscador muestra un mensaje cuando no hay resultados", async ({ page }) => {
  await page.goto("/?q=dinosaurios");
  await expect(page.getByText(/No encontramos nada/)).toBeVisible();
});
