/**
 * E2E tests: Teacher class list and class heatmap.
 *
 * Covers:
 * - Class list page: displays assigned classes
 * - Class heatmap: renders grid with state counts, legend
 * - Navigation from class list to heatmap
 * - Breadcrumb navigation
 * - Aggregate concept summary table
 *
 * Requirements: F11.14, SCR-DOC-06, SCR-DOC-08
 */

import { test, expect } from "@playwright/test";
import { setupTeacherApiMocks, injectTeacherAuth } from "../helpers/api-mock";

test.describe("Teacher Class List", () => {
  test.beforeEach(async ({ page }) => {
    await setupTeacherApiMocks(page);
    await injectTeacherAuth(page);
  });

  test("displays class list heading", async ({ page }) => {
    await page.goto("/classes");
    await expect(page.locator("h1")).toHaveText("Le tue classi");
  });

  test("shows class card with name and student count", async ({ page }) => {
    await page.goto("/classes");

    // MVP: single class "3A Informatica"
    await expect(page.getByRole("heading", { name: "3A Informatica" })).toBeVisible();
    await expect(page.getByText("25 studenti")).toBeVisible();
  });

  test("class card links to class detail with courseId param", async ({ page }) => {
    await page.goto("/classes");

    await page.getByRole("heading", { name: "3A Informatica" }).click();
    await expect(page).toHaveURL(/\/classes\/class-1\?courseId=course-1/);
  });
});

test.describe("Teacher Class Heatmap", () => {
  test.beforeEach(async ({ page }) => {
    await setupTeacherApiMocks(page);
    await injectTeacherAuth(page);
  });

  test("displays breadcrumb navigation", async ({ page }) => {
    await page.goto("/classes/class-1?courseId=course-1");

    const breadcrumb = page.locator('nav[aria-label="Breadcrumb"]');
    await expect(breadcrumb).toBeVisible();
    await expect(breadcrumb.getByText("Classi")).toBeVisible();
    await expect(breadcrumb.getByText("Heatmap classe")).toBeVisible();
  });

  test("breadcrumb Classi link navigates back to class list", async ({ page }) => {
    await page.goto("/classes/class-1?courseId=course-1");

    await page.locator('nav[aria-label="Breadcrumb"]').getByText("Classi").click();
    await expect(page).toHaveURL("/classes");
  });

  test("displays class heatmap heading", async ({ page }) => {
    await page.goto("/classes/class-1?courseId=course-1");
    await expect(page.locator("h1")).toHaveText("Padronanza della classe");
  });

  test("shows loading state while data loads", async ({ page }) => {
    await setupTeacherApiMocks(page, { delay: 2000 });
    await injectTeacherAuth(page);
    await page.goto("/classes/class-1?courseId=course-1");

    await expect(page.getByText("Caricamento in corso...")).toBeVisible();
  });

  test("renders heatmap legend", async ({ page }) => {
    await page.goto("/classes/class-1?courseId=course-1");

    // Wait for loading to finish
    await expect(page.getByText("Caricamento in corso...")).not.toBeVisible({ timeout: 10000 });

    // HeatmapLegend should be rendered -- it shows all 6 states
    // We verify the legend component is present
    await expect(page.getByText("Riepilogo per concetto")).toBeVisible();
  });

  test("renders aggregate concept summary table", async ({ page }) => {
    await page.goto("/classes/class-1?courseId=course-1");

    // Wait for data to load
    await expect(page.getByText("Caricamento in corso...")).not.toBeVisible({ timeout: 10000 });

    // The table should have an aria-label
    const table = page.locator('table[aria-label="Riepilogo padronanza per concetto"]');
    await expect(table).toBeVisible();

    // Table should have column headers for the 6 states + concept + total
    await expect(table.getByRole("columnheader", { name: "Concetto" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Non introdotto" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Introdotto" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Lacuna" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "In recupero" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Da consolidare" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Consolidato" })).toBeVisible();
    await expect(table.getByRole("columnheader", { name: "Totale" })).toBeVisible();

    // Table has a sr-only caption
    await expect(table.locator("caption")).toHaveClass(/sr-only/);
  });

  test("concept rows display node labels from KG", async ({ page }) => {
    await page.goto("/classes/class-1?courseId=course-1");
    await expect(page.getByText("Caricamento in corso...")).not.toBeVisible({ timeout: 10000 });

    // Check that macro node labels appear in the table
    await expect(page.getByRole("rowheader", { name: "Variabili e Tipi di Dato" })).toBeVisible();
    await expect(page.getByRole("rowheader", { name: "Strutture di Controllo" })).toBeVisible();
    await expect(page.getByRole("rowheader", { name: "Funzioni" })).toBeVisible();
  });
});
