/**
 * E2E tests: Teacher dashboard home page.
 *
 * Covers:
 * - Dashboard layout after login
 * - Welcome message with teacher name
 * - Navigation cards (classes, lessons, alerts)
 * - Links to sub-pages
 *
 * Requirements: SCR-DOC-02
 */

import { test, expect } from "@playwright/test";
import { setupTeacherApiMocks, injectTeacherAuth } from "../helpers/api-mock";

test.describe("Teacher Dashboard Home", () => {
  test.beforeEach(async ({ page }) => {
    await setupTeacherApiMocks(page);
    await injectTeacherAuth(page);
  });

  test("displays dashboard heading", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toHaveText("Dashboard");
  });

  test("shows welcome message with teacher username", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText(/Bentornato/)).toBeVisible();
  });

  test("displays three navigation cards", async ({ page }) => {
    await page.goto("/");

    // Classes card
    await expect(page.getByRole("heading", { name: "Le tue classi" })).toBeVisible();
    await expect(
      page.getByText("Visualizza la heatmap di padronanza e il dettaglio di ogni studente."),
    ).toBeVisible();

    // Lessons card
    await expect(page.getByRole("heading", { name: "Lezioni" })).toBeVisible();
    await expect(
      page.getByText("Carica nuove lezioni e revisiona i concept mapping suggeriti."),
    ).toBeVisible();

    // Alerts card
    await expect(page.getByRole("heading", { name: "Alert benessere" })).toBeVisible();
    await expect(
      page.getByText("Segnalazioni di benessere rilevate dal sistema."),
    ).toBeVisible();
  });

  test("classes card links to /classes", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("heading", { name: "Le tue classi" }).click();
    await expect(page).toHaveURL("/classes");
  });

  test("lessons card links to /lessons", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("heading", { name: "Lezioni" }).click();
    await expect(page).toHaveURL("/lessons");
  });

  test("alerts card links to /alerts", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("heading", { name: "Alert benessere" }).click();
    await expect(page).toHaveURL("/alerts");
  });

  test("navigation cards have visible focus indicators", async ({ page }) => {
    await page.goto("/");

    // Tab to first card and check focus-visible styles are defined
    const classesLink = page.getByRole("link", { name: /Le tue classi/ });
    await classesLink.focus();
    await expect(classesLink).toBeFocused();
    // The component uses focus-visible:outline classes
    await expect(classesLink).toHaveClass(/focus-visible/);
  });
});
