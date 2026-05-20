/**
 * Playwright configuration for MAESTRO teacher dashboard E2E tests.
 *
 * Target: Next.js 15 dashboard at src/dashboard/.
 * All tests run against a local dev server with mocked API endpoints.
 */

import { defineConfig, devices } from "@playwright/test";

const BASE_URL = process.env.DASHBOARD_URL ?? "http://localhost:3000";

export default defineConfig({
  testDir: "./teacher",
  outputDir: "./test-results",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["html", { outputFolder: "./playwright-report" }],
    ["json", { outputFile: "./test-results/results.json" }],
  ],

  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "on-first-retry",
    locale: "it-IT",
    timezoneId: "Europe/Rome",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
  ],

  webServer: {
    command: "npm run dev",
    cwd: "../../src/dashboard",
    url: BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
