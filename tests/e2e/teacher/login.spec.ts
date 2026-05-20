/**
 * E2E tests: Teacher login flow.
 *
 * Covers:
 * - SCR-DOC-01: teacher login page
 * - Valid credentials -> redirect to dashboard home
 * - Invalid credentials -> error message displayed
 * - Keyboard accessibility (Tab order, Enter submit)
 * - Form validation (empty fields)
 *
 * Requirements: F14 (authentication), WCAG 2.1 AA
 */

import { test, expect } from "@playwright/test";
import { setupTeacherApiMocks, injectTeacherAuth } from "../helpers/api-mock";
import { TEACHER_CREDENTIALS } from "../fixtures/test-data";

test.describe("Teacher Login", () => {
  test.beforeEach(async ({ page }) => {
    await setupTeacherApiMocks(page);
  });

  test("displays login form with correct elements", async ({ page }) => {
    await page.goto("/login");

    // Page heading
    await expect(page.locator("h1")).toHaveText("MAESTRO");

    // Subtitle
    await expect(page.getByText("Accedi alla Dashboard Docente")).toBeVisible();

    // Username field with label
    const usernameLabel = page.locator('label[for="username"]');
    await expect(usernameLabel).toHaveText("Nome utente");
    await expect(page.locator("#username")).toBeVisible();

    // Password field with label
    const passwordLabel = page.locator('label[for="password"]');
    await expect(passwordLabel).toHaveText("Password");
    await expect(page.locator("#password")).toBeVisible();

    // Submit button
    await expect(page.getByRole("button", { name: "Accedi" })).toBeVisible();

    // Show/hide password toggle
    await expect(page.getByText("Mostra password")).toBeVisible();
  });

  test("successful login redirects to dashboard home", async ({ page }) => {
    await page.goto("/login");

    // Fill credentials
    await page.locator("#username").fill(TEACHER_CREDENTIALS.username);
    await page.locator("#password").fill(TEACHER_CREDENTIALS.password);

    // Submit
    await page.getByRole("button", { name: "Accedi" }).click();

    // Should redirect to dashboard home
    await expect(page).toHaveURL("/");
    await expect(page.locator("h1")).toHaveText("Dashboard");
  });

  test("invalid credentials show error message", async ({ page }) => {
    await setupTeacherApiMocks(page, { failLogin: true });
    await page.goto("/login");

    await page.locator("#username").fill("wrong-user");
    await page.locator("#password").fill("wrong-password");
    await page.getByRole("button", { name: "Accedi" }).click();

    // Error message should appear with role="alert"
    const errorAlert = page.locator('[role="alert"]');
    await expect(errorAlert).toBeVisible();
    await expect(errorAlert).toHaveText("Credenziali non valide. Riprova.");
  });

  test("submit button is disabled during loading", async ({ page }) => {
    await setupTeacherApiMocks(page, { delay: 2000 });
    await page.goto("/login");

    await page.locator("#username").fill(TEACHER_CREDENTIALS.username);
    await page.locator("#password").fill(TEACHER_CREDENTIALS.password);
    await page.getByRole("button", { name: "Accedi" }).click();

    // Button text changes to loading state
    await expect(page.getByRole("button", { name: "Accesso in corso..." })).toBeVisible();
    await expect(page.getByRole("button", { name: "Accesso in corso..." })).toBeDisabled();
  });

  test("password visibility toggle works", async ({ page }) => {
    await page.goto("/login");

    const passwordInput = page.locator("#password");
    await passwordInput.fill("test-password");

    // Initially password is hidden
    await expect(passwordInput).toHaveAttribute("type", "password");

    // Click show password
    await page.getByText("Mostra password").click();
    await expect(passwordInput).toHaveAttribute("type", "text");
    await expect(page.getByText("Nascondi password")).toBeVisible();

    // Click hide password
    await page.getByText("Nascondi password").click();
    await expect(passwordInput).toHaveAttribute("type", "password");
  });

  test("form submits with Enter key", async ({ page }) => {
    await page.goto("/login");

    await page.locator("#username").fill(TEACHER_CREDENTIALS.username);
    await page.locator("#password").fill(TEACHER_CREDENTIALS.password);
    await page.locator("#password").press("Enter");

    // Should redirect after successful login
    await expect(page).toHaveURL("/");
  });

  test("keyboard tab order follows expected sequence", async ({ page }) => {
    await page.goto("/login");

    // Tab to username
    await page.keyboard.press("Tab");
    await expect(page.locator("#username")).toBeFocused();

    // Tab to password
    await page.keyboard.press("Tab");
    await expect(page.locator("#password")).toBeFocused();
  });

  test("empty fields prevent submission", async ({ page }) => {
    await page.goto("/login");

    // Both fields have required attribute
    const usernameInput = page.locator("#username");
    const passwordInput = page.locator("#password");
    await expect(usernameInput).toHaveAttribute("required", "");
    await expect(passwordInput).toHaveAttribute("required", "");
  });

  test("autocomplete attributes are set correctly", async ({ page }) => {
    await page.goto("/login");

    await expect(page.locator("#username")).toHaveAttribute("autocomplete", "username");
    await expect(page.locator("#password")).toHaveAttribute("autocomplete", "current-password");
  });
});
