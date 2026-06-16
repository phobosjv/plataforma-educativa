import { expect, test, type Page } from "@playwright/test";

async function abrirEjercicio(page: Page): Promise<void> {
  const res = await page.request.get("/api/v1/contenidos/");
  const lista: Array<{ id: string; tipo: string }> = await res.json();
  const ejercicio = lista.find((c) => c.tipo === "interactivo");
  expect(ejercicio).toBeTruthy();
  await page.goto(`/contenido/${ejercicio!.id}`);
}

// Pantalla completa del ejercicio (V-0.8.1): maximizar, ver la barra, y salir con Escape.
test("el ejercicio se maximiza y se sale con Escape", async ({ page }) => {
  await abrirEjercicio(page);

  await page.getByRole("button", { name: "Maximizar ejercicio" }).click();

  const maximizado = page.locator(".cms-exercise-wrap--max");
  await expect(maximizado).toBeVisible();
  await expect(page.getByRole("button", { name: /Minimizar/ })).toBeVisible();

  // Escape minimiza: desaparece el contenedor maximizado y vuelve el botón de maximizar.
  await page.keyboard.press("Escape");
  await expect(maximizado).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Maximizar ejercicio" })).toBeVisible();
});
