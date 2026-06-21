import { expect, test, type Page } from "@playwright/test";

async function abrirFichaPdf(page: Page): Promise<{ id: string; pdf_url: string }> {
  const res = await page.request.get("/api/v1/contenidos/");
  const lista: Array<{ id: string; tipo: string; pdf_url: string }> = await res.json();
  const ficha = lista.find((c) => c.tipo === "pdf");
  expect(ficha).toBeTruthy();
  await page.goto(`/contenido/${ficha!.id}`);
  return ficha!;
}

// Ficha PDF (V-0.22.x): el PDF se renderiza con PDF.js dentro de un <div>/canvas (compatible con
// móviles donde el iframe nativo no carga), hay botón de descarga y se puede maximizar.
test("la ficha PDF se renderiza con PDF.js, se descarga y se maximiza", async ({ page }) => {
  await abrirFichaPdf(page);

  await expect(page.getByRole("heading", { name: "Ficha PDF E2E" })).toBeVisible();

  // El visor PDF.js pinta cada página en un <canvas> dentro del contenedor (no es un iframe).
  await expect(page.locator(".cms-pdf-viewer")).toBeVisible();
  await expect(page.locator("canvas.cms-pdf-page").first()).toBeVisible({ timeout: 15000 });

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
