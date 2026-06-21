import { expect, test, type Page } from "@playwright/test";

async function abrirFichaPdf(page: Page): Promise<{ id: string; pdf_url: string }> {
  const res = await page.request.get("/api/v1/contenidos/");
  const lista: Array<{ id: string; tipo: string; pdf_url: string }> = await res.json();
  const ficha = lista.find((c) => c.tipo === "pdf");
  expect(ficha).toBeTruthy();
  await page.goto(`/contenido/${ficha!.id}`);
  return ficha!;
}

// Ficha PDF (V-0.22.0): el visor embebido apunta al origen sandbox, hay botón de descarga
// y se puede maximizar igual que un ejercicio.
test("la ficha PDF se ve embebida, se descarga y se maximiza", async ({ page }) => {
  const ficha = await abrirFichaPdf(page);

  await expect(page.getByRole("heading", { name: "Ficha PDF E2E" })).toBeVisible();

  // El iframe del visor apunta al sandbox /ficha/<hash>.pdf (origen aislado).
  const iframe = page.locator("iframe.cms-exercise-frame");
  await expect(iframe).toBeVisible();
  const src = await iframe.getAttribute("src");
  expect(src).toContain("/ficha/");
  expect(src).toContain(".pdf");
  expect(src).toBe(ficha.pdf_url);

  // Botón de descarga (fuerza attachment vía ?descargar=1 en el sandbox).
  const descarga = page.getByRole("link", { name: /Descargar/ });
  await expect(descarga).toBeVisible();
  expect(await descarga.getAttribute("href")).toContain("descargar=1");

  // Maximizar: barra superior visible, y salir con Escape.
  await page.getByRole("button", { name: "Maximizar ficha" }).click();
  const maximizado = page.locator(".cms-exercise-wrap--max");
  await expect(maximizado).toBeVisible();
  await expect(page.getByRole("button", { name: /Minimizar/ })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(maximizado).toHaveCount(0);
});
