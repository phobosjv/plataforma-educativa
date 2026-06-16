import { expect, test } from "@playwright/test";

const ADMIN_EMAIL = "admin@e2e.local";
const ADMIN_PASSWORD = "E2eTest1234";
const TITULO = "Artículo CRUD E2E";

// Login + CRUD: el admin entra, crea un artículo de texto y lo envía a la papelera.
test("login de admin y ciclo crear/borrar de un artículo", async ({ page }) => {
  // Login.
  await page.goto("/login");
  await page.getByLabel("Email").fill(ADMIN_EMAIL);
  await page.getByLabel("Contraseña").fill(ADMIN_PASSWORD);
  await page.getByRole("button", { name: "Acceder" }).click();
  await expect(page).toHaveURL(/\/admin$/);

  // Crear un artículo de texto.
  await page.goto("/admin/contenidos");
  await page.getByRole("link", { name: "+ Artículo de texto" }).click();
  await page.getByLabel("Título").fill(TITULO);
  await page.getByRole("button", { name: "Crear artículo" }).click();

  // Vuelve a la lista; el artículo aparece como borrador.
  await expect(page).toHaveURL(/\/admin\/contenidos$/);
  const fila = page.getByRole("row", { name: new RegExp(TITULO) });
  await expect(fila).toBeVisible();
  await expect(fila.getByText("borrador")).toBeVisible();

  // Borrar (a la papelera): dos pasos, con confirmación.
  await fila.getByRole("button", { name: "Borrar" }).click();
  await fila.getByRole("button", { name: "Confirmar borrado" }).click();

  // La fila sigue (la lista admin incluye la papelera) pero ahora en estado "papelera".
  await expect(fila.getByText("papelera")).toBeVisible();
});
