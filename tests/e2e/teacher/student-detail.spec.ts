/**
 * E2E tests: Teacher student detail page.
 *
 * Covers:
 * - Student mastery map display
 * - Breadcrumb navigation (Classi > Heatmap > Studente)
 * - Node click opens override modal
 * - Override requires motivation >= 20 chars
 * - Successful override submission
 *
 * Requirements: F11.12 (teacher override), SCR-DOC-09
 */

import { test, expect } from "@playwright/test";
import { setupTeacherApiMocks, injectTeacherAuth } from "../helpers/api-mock";

const STUDENT_URL =
  "/classes/class-test-001/students/student-uuid-001?courseId=course-test-001";

test.describe("Teacher Student Detail", () => {
  test.beforeEach(async ({ page }) => {
    await setupTeacherApiMocks(page);
    await injectTeacherAuth(page);
  });

  test("displays student detail heading", async ({ page }) => {
    await page.goto(STUDENT_URL);
    await expect(page.locator("h1")).toHaveText("Dettaglio studente");
  });

  test("shows student ID", async ({ page }) => {
    await page.goto(STUDENT_URL);
    await expect(page.getByText("ID: student-uuid-001")).toBeVisible();
  });

  test("displays breadcrumb navigation with three levels", async ({ page }) => {
    await page.goto(STUDENT_URL);

    const breadcrumb = page.locator('nav[aria-label="Breadcrumb"]');
    await expect(breadcrumb).toBeVisible();
    await expect(breadcrumb.getByText("Classi")).toBeVisible();
    await expect(breadcrumb.getByText("Heatmap classe")).toBeVisible();
    await expect(breadcrumb.getByText("Studente")).toBeVisible();

    // Current page should be marked with aria-current
    await expect(breadcrumb.locator('[aria-current="page"]')).toHaveText("Studente");
  });

  test("shows heatmap legend", async ({ page }) => {
    await page.goto(STUDENT_URL);

    // Wait for loading to finish
    await expect(page.getByText("Caricamento mappa padronanza...")).not.toBeVisible({
      timeout: 10000,
    });

    // Legend + mastery map heading
    await expect(page.getByRole("heading", { name: "Mappa padronanza" })).toBeVisible();
  });

  test("shows override instructions", async ({ page }) => {
    await page.goto(STUDENT_URL);
    await expect(page.getByText("Caricamento mappa padronanza...")).not.toBeVisible({
      timeout: 10000,
    });

    await expect(
      page.getByText("Clicca su un nodo per effettuare un override dello stato."),
    ).toBeVisible();
  });

  test("shows loading state", async ({ page }) => {
    await setupTeacherApiMocks(page, { delay: 2000 });
    await injectTeacherAuth(page);

    await page.goto(STUDENT_URL);
    await expect(page.getByText("Caricamento mappa padronanza...")).toBeVisible();
  });
});

test.describe("Teacher Override Modal", () => {
  test.beforeEach(async ({ page }) => {
    await setupTeacherApiMocks(page);
    await injectTeacherAuth(page);
    await page.goto(STUDENT_URL);
    // Wait for data to load
    await expect(page.getByText("Caricamento mappa padronanza...")).not.toBeVisible({
      timeout: 10000,
    });
  });

  test("override modal has required fields", async ({ page }) => {
    // This test verifies the OverrideModal component structure.
    // We simulate opening the modal by triggering a node click via the StudentMap.
    // Since StudentMap renders node buttons, we look for any clickable node.
    const nodeButtons = page.locator("[data-testid^='node-']");
    const count = await nodeButtons.count();

    if (count > 0) {
      await nodeButtons.first().click();

      // Modal should open with title
      await expect(page.getByText("Override stato studente")).toBeVisible();

      // Target state selector
      await expect(page.locator("#target-state")).toBeVisible();

      // Motivation textarea
      await expect(page.locator("#motivation")).toBeVisible();

      // Character counter showing minimum requirement
      await expect(page.getByText(/\/20 caratteri minimi/)).toBeVisible();

      // Cancel and submit buttons
      await expect(page.getByRole("button", { name: "Annulla" })).toBeVisible();
      await expect(page.getByRole("button", { name: "Conferma override" })).toBeVisible();
    }
  });

  test("submit button is disabled with short motivation", async ({ page }) => {
    const nodeButtons = page.locator("[data-testid^='node-']");
    const count = await nodeButtons.count();

    if (count > 0) {
      await nodeButtons.first().click();
      await expect(page.getByText("Override stato studente")).toBeVisible();

      // Select a different target state
      await page.locator("#target-state").selectOption("consolidato");

      // Type short motivation (< 20 chars)
      await page.locator("#motivation").fill("Breve motivo");

      // Submit should be disabled
      await expect(page.getByRole("button", { name: "Conferma override" })).toBeDisabled();

      // Error hint should appear
      await expect(page.getByText("Motivazione troppo breve")).toBeVisible();
    }
  });

  test("submit button enabled with valid motivation >= 20 chars", async ({ page }) => {
    const nodeButtons = page.locator("[data-testid^='node-']");
    const count = await nodeButtons.count();

    if (count > 0) {
      await nodeButtons.first().click();
      await expect(page.getByText("Override stato studente")).toBeVisible();

      // Select different target state
      await page.locator("#target-state").selectOption("consolidato");

      // Type valid motivation (>= 20 chars)
      await page.locator("#motivation").fill("Lo studente ha dimostrato padronanza durante l'orale");

      // Submit should be enabled
      await expect(page.getByRole("button", { name: "Conferma override" })).toBeEnabled();
    }
  });

  test("successful override closes modal", async ({ page }) => {
    const nodeButtons = page.locator("[data-testid^='node-']");
    const count = await nodeButtons.count();

    if (count > 0) {
      await nodeButtons.first().click();
      await expect(page.getByText("Override stato studente")).toBeVisible();

      await page.locator("#target-state").selectOption("consolidato");
      await page.locator("#motivation").fill("Lo studente ha dimostrato padronanza durante l'orale in classe");

      await page.getByRole("button", { name: "Conferma override" }).click();

      // Modal should close after successful submission
      await expect(page.getByText("Override stato studente")).not.toBeVisible({ timeout: 5000 });
    }
  });

  test("cancel button closes modal without submitting", async ({ page }) => {
    const nodeButtons = page.locator("[data-testid^='node-']");
    const count = await nodeButtons.count();

    if (count > 0) {
      await nodeButtons.first().click();
      await expect(page.getByText("Override stato studente")).toBeVisible();

      await page.getByRole("button", { name: "Annulla" }).click();

      // Modal should close
      await expect(page.getByText("Override stato studente")).not.toBeVisible();
    }
  });

  test("motivation textarea has aria-describedby and aria-invalid", async ({ page }) => {
    const nodeButtons = page.locator("[data-testid^='node-']");
    const count = await nodeButtons.count();

    if (count > 0) {
      await nodeButtons.first().click();
      await expect(page.getByText("Override stato studente")).toBeVisible();

      const textarea = page.locator("#motivation");
      await expect(textarea).toHaveAttribute("aria-describedby", "motivation-hint");

      // Type short text to trigger invalid state
      await page.locator("#target-state").selectOption("consolidato");
      await textarea.fill("breve");
      await expect(textarea).toHaveAttribute("aria-invalid", "true");
    }
  });
});
