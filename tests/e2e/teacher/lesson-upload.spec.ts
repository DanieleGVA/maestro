/**
 * E2E tests: Teacher lesson upload and concept mapping review.
 *
 * Covers:
 * - Lesson upload form: title, content, material type
 * - Upload submission triggers concept extraction
 * - Concept mapping review: confirm/reject candidates
 * - Breadcrumb navigation
 * - Error handling on upload failure
 *
 * Requirements: F2 (lesson upload), SCR-DOC-10, SCR-DOC-11
 */

import { test, expect } from "@playwright/test";
import { setupTeacherApiMocks, injectTeacherAuth } from "../helpers/api-mock";
import { LESSON_INGEST_REQUEST } from "../fixtures/test-data";

test.describe("Lessons List Page", () => {
  test.beforeEach(async ({ page }) => {
    await setupTeacherApiMocks(page);
    await injectTeacherAuth(page);
  });

  test("displays lessons heading", async ({ page }) => {
    await page.goto("/lessons");
    await expect(page.locator("h1")).toHaveText("Lezioni");
  });

  test("shows upload button linking to upload page", async ({ page }) => {
    await page.goto("/lessons");

    const uploadLink = page.getByRole("link", { name: "Carica nuova lezione" });
    await expect(uploadLink).toBeVisible();
    await uploadLink.click();
    await expect(page).toHaveURL("/lessons/upload");
  });

  test("displays explanation text", async ({ page }) => {
    await page.goto("/lessons");
    await expect(
      page.getByText(/lezioni caricate verranno elaborate automaticamente/),
    ).toBeVisible();
  });
});

test.describe("Lesson Upload Form", () => {
  test.beforeEach(async ({ page }) => {
    await setupTeacherApiMocks(page);
    await injectTeacherAuth(page);
  });

  test("displays upload form with breadcrumb", async ({ page }) => {
    await page.goto("/lessons/upload");

    // Breadcrumb
    const breadcrumb = page.locator('nav[aria-label="Breadcrumb"]');
    await expect(breadcrumb).toBeVisible();
    await expect(breadcrumb.getByText("Lezioni")).toBeVisible();
    await expect(breadcrumb.getByText("Carica nuova lezione")).toBeVisible();

    // Heading
    await expect(page.locator("h1")).toHaveText("Carica nuova lezione");
  });

  test("form has title, material type, and content fields", async ({ page }) => {
    await page.goto("/lessons/upload");

    // Title
    await expect(page.locator('label[for="lesson-title"]')).toHaveText("Titolo della lezione");
    await expect(page.locator("#lesson-title")).toBeVisible();

    // Material type
    await expect(page.locator('label[for="material-type"]')).toHaveText("Tipo di materiale");
    const materialSelect = page.locator("#material-type");
    await expect(materialSelect).toBeVisible();

    // Verify material type options
    const options = materialSelect.locator("option");
    await expect(options).toHaveCount(3);
    await expect(options.nth(0)).toHaveText("Lezione");
    await expect(options.nth(1)).toHaveText("Libro di testo");
    await expect(options.nth(2)).toHaveText("Esercizio");

    // Content
    await expect(page.locator('label[for="lesson-content"]')).toHaveText("Contenuto della lezione");
    await expect(page.locator("#lesson-content")).toBeVisible();

    // Character counter
    await expect(page.getByText("0 caratteri")).toBeVisible();

    // Submit button
    await expect(page.getByRole("button", { name: "Carica lezione" })).toBeVisible();
  });

  test("submit button is disabled when fields are empty", async ({ page }) => {
    await page.goto("/lessons/upload");

    await expect(page.getByRole("button", { name: "Carica lezione" })).toBeDisabled();
  });

  test("submit button enables when both title and content are filled", async ({ page }) => {
    await page.goto("/lessons/upload");

    await page.locator("#lesson-title").fill(LESSON_INGEST_REQUEST.title);
    await page.locator("#lesson-content").fill(LESSON_INGEST_REQUEST.content);

    await expect(page.getByRole("button", { name: "Carica lezione" })).toBeEnabled();
  });

  test("character counter updates as content is typed", async ({ page }) => {
    await page.goto("/lessons/upload");

    await page.locator("#lesson-content").fill("Testo di prova");
    await expect(page.getByText("14 caratteri")).toBeVisible();
  });

  test("successful upload shows concept mapping review", async ({ page }) => {
    await page.goto("/lessons/upload");

    await page.locator("#lesson-title").fill(LESSON_INGEST_REQUEST.title);
    await page.locator("#lesson-content").fill(LESSON_INGEST_REQUEST.content);
    await page.getByRole("button", { name: "Carica lezione" }).click();

    // Success alert
    await expect(
      page.getByText("Lezione caricata con successo. Revisiona i concetti estratti di seguito."),
    ).toBeVisible();

    // Concept mapping review heading
    await expect(page.getByText("Concetti estratti dalla lezione")).toBeVisible();

    // Candidate mappings should be visible
    await expect(page.getByText("Variabili e Tipi di Dato")).toBeVisible();
    await expect(page.getByText("Assegnazione variabili")).toBeVisible();

    // Confidence scores should be shown
    await expect(page.getByText(/Confidence: 90%/)).toBeVisible();
    await expect(page.getByText(/Confidence: 81%/)).toBeVisible();
  });

  test("loading state shown during upload", async ({ page }) => {
    await setupTeacherApiMocks(page, { delay: 2000 });
    await injectTeacherAuth(page);
    await page.goto("/lessons/upload");

    await page.locator("#lesson-title").fill(LESSON_INGEST_REQUEST.title);
    await page.locator("#lesson-content").fill(LESSON_INGEST_REQUEST.content);
    await page.getByRole("button", { name: "Carica lezione" }).click();

    await expect(page.getByRole("button", { name: "Elaborazione in corso..." })).toBeVisible();
    await expect(page.getByRole("button", { name: "Elaborazione in corso..." })).toBeDisabled();
  });
});

test.describe("Concept Mapping Review", () => {
  test.beforeEach(async ({ page }) => {
    await setupTeacherApiMocks(page);
    await injectTeacherAuth(page);

    // Navigate to upload and submit to get to review state
    await page.goto("/lessons/upload");
    await page.locator("#lesson-title").fill(LESSON_INGEST_REQUEST.title);
    await page.locator("#lesson-content").fill(LESSON_INGEST_REQUEST.content);
    await page.getByRole("button", { name: "Carica lezione" }).click();
    await expect(page.getByText("Concetti estratti dalla lezione")).toBeVisible();
  });

  test("each candidate has confirm and reject buttons with aria-labels", async ({ page }) => {
    const confirmBtn = page.getByRole("button", {
      name: "Conferma mapping per Variabili e Tipi di Dato",
    });
    await expect(confirmBtn).toBeVisible();

    const rejectBtn = page.getByRole("button", {
      name: "Rifiuta mapping per Variabili e Tipi di Dato",
    });
    await expect(rejectBtn).toBeVisible();
  });

  test("confirming a candidate removes it from the list", async ({ page }) => {
    // Confirm first candidate
    await page
      .getByRole("button", { name: "Conferma mapping per Variabili e Tipi di Dato" })
      .click();

    // Should be removed from list
    await expect(
      page.getByRole("button", { name: "Conferma mapping per Variabili e Tipi di Dato" }),
    ).not.toBeVisible();

    // Second candidate should still be visible
    await expect(page.getByText("Assegnazione variabili")).toBeVisible();
  });

  test("rejecting a candidate removes it from the list", async ({ page }) => {
    await page
      .getByRole("button", { name: "Rifiuta mapping per Assegnazione variabili" })
      .click();

    await expect(
      page.getByRole("button", { name: "Rifiuta mapping per Assegnazione variabili" }),
    ).not.toBeVisible();

    // First candidate should still be visible
    await expect(page.getByText("Variabili e Tipi di Dato")).toBeVisible();
  });

  test("shows empty state when all candidates are reviewed", async ({ page }) => {
    // Confirm first
    await page
      .getByRole("button", { name: "Conferma mapping per Variabili e Tipi di Dato" })
      .click();

    // Reject second
    await page
      .getByRole("button", { name: "Rifiuta mapping per Assegnazione variabili" })
      .click();

    // Empty state
    await expect(page.getByText("Nessun mapping da revisionare.")).toBeVisible();
  });

  test("candidate shows node type and LLM explanation", async ({ page }) => {
    await expect(page.getByText(/Tipo: macro/)).toBeVisible();
    await expect(
      page.getByText("Il testo tratta esplicitamente di variabili Python"),
    ).toBeVisible();
  });
});
