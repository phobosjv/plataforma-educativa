import { expect, test } from "@playwright/test";

// Catálogo público: la entrada "Aula Abierta" lleva a las asignaturas transversales y a
// sus ejercicios, fuera de la clasificación por ciclo/curso.
test("Aula Abierta lleva a una asignatura transversal y a su contenido", async ({ page }) => {
  await page.goto("/");

  // La tarjeta de Aula Abierta aparece en el inicio (hay contenido transversal sembrado).
  await page.getByRole("button", { name: /Aula Abierta/ }).click();

  // Pantalla de asignaturas transversales: elegir "Audición y Lenguaje".
  await expect(page.getByText("Elige una asignatura")).toBeVisible();
  await page.getByRole("button", { name: /Audición y Lenguaje/ }).click();

  // Sus ejercicios: abrir el contenido transversal.
  await page.getByRole("link", { name: /Ejercicio Aula Abierta/ }).click();
  await expect(page.getByRole("heading", { name: "Ejercicio Aula Abierta" })).toBeVisible();
});

// El contenido transversal NO aparece en el flujo normal de curso → asignatura.
test("el contenido transversal no se mezcla en el flujo de curso", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /3º E2E/ }).click();
  // En la elección de asignatura del curso no debe estar la transversal.
  await expect(page.getByText("¿Qué quieres aprender?")).toBeVisible();
  await expect(page.getByRole("button", { name: /Audición y Lenguaje/ })).toHaveCount(0);
});
