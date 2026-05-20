/**
 * API mock helper for MAESTRO E2E tests.
 *
 * Uses Playwright's route interception to mock backend API responses.
 * All mocked responses follow the IC-12 contract envelope: { data, meta }.
 */

import { Page, Route } from "@playwright/test";
import {
  TEACHER_TOKEN,
  MACRO_NODES,
  CLASS_HEATMAP,
  STUDENT_HEATMAP_ROWS,
  TEST_STUDENTS,
  LESSON_INGEST_RESPONSE,
  WELLBEING_ALERTS,
  buildStudentNodeStates,
  STUDENT_001_STATES,
  STUDENT_002_STATES,
} from "../fixtures/test-data";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface MockApiOptions {
  /** Override the default delay (ms) for API responses. 0 = no delay. */
  delay?: number;
  /** If true, fail the login request with 401. */
  failLogin?: boolean;
}

// ---------------------------------------------------------------------------
// API envelope helper
// ---------------------------------------------------------------------------

function envelope<T>(data: T): { data: T; meta: { request_id: string; timestamp: string } } {
  return {
    data,
    meta: {
      request_id: "test-request-" + Math.random().toString(36).slice(2),
      timestamp: new Date().toISOString(),
    },
  };
}

// ---------------------------------------------------------------------------
// Mock API setup
// ---------------------------------------------------------------------------

/**
 * Set up all API mocks for the teacher dashboard.
 * Call this in beforeEach or at the start of each test.
 */
export async function setupTeacherApiMocks(page: Page, options: MockApiOptions = {}) {
  const { delay = 0, failLogin = false } = options;

  // -- Auth: Keycloak token endpoint --
  await page.route("**/realms/*/protocol/openid-connect/token", async (route: Route) => {
    if (failLogin) {
      await maybeDelay(delay);
      return route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ error: "invalid_grant", error_description: "Invalid credentials" }),
      });
    }
    await maybeDelay(delay);
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: TEACHER_TOKEN,
        refresh_token: "test-refresh-token",
        expires_in: 3600,
        token_type: "Bearer",
      }),
    });
  });

  // -- Class heatmap --
  await page.route("**/api/v1/kmm/classes/*/heatmap*", async (route: Route) => {
    await maybeDelay(delay);
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(CLASS_HEATMAP),
    });
  });

  // -- Course KG nodes --
  await page.route("**/api/v1/kg/courses/*/nodes", async (route: Route) => {
    await maybeDelay(delay);
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(envelope(MACRO_NODES)),
    });
  });

  // -- Student map --
  await page.route("**/api/v1/kmm/students/*/map*", async (route: Route) => {
    const url = route.request().url();
    const studentId = url.match(/students\/([^/]+)/)?.[1] ?? "student-uuid-001";
    const stateMap = studentId === "student-uuid-002" ? STUDENT_002_STATES : STUDENT_001_STATES;
    await maybeDelay(delay);
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        student_id: studentId,
        course_id: "course-test-001",
        nodes: buildStudentNodeStates(studentId, stateMap),
      }),
    });
  });

  // -- Teacher override (state transition) --
  await page.route("**/api/v1/kmm/students/*/nodes/*/transition*", async (route: Route) => {
    if (route.request().method() !== "POST") return route.continue();
    const body = route.request().postDataJSON();
    await maybeDelay(delay);
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        student_id: "student-uuid-001",
        node_id: "macro-003",
        course_id: "course-test-001",
        previous_state: "in_recupero",
        new_state: body?.target_state ?? "da_consolidare",
        trigger_type: "teacher_override",
        triggered_by: "teacher-uuid-001",
        quiz_score: null,
        motivation: body?.motivation ?? "",
        created_at: new Date().toISOString(),
      }),
    });
  });

  // -- Lesson ingestion --
  await page.route("**/api/v1/kg/courses/*/lessons/ingest", async (route: Route) => {
    if (route.request().method() !== "POST") return route.continue();
    await maybeDelay(delay);
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(envelope(LESSON_INGEST_RESPONSE)),
    });
  });

  // -- Confirm/reject mapping --
  await page.route("**/api/v1/kg/mappings/*/confirm", async (route: Route) => {
    if (route.request().method() !== "POST") return route.continue();
    await maybeDelay(delay);
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(envelope({ status: "ok" })),
    });
  });

  // -- Course students --
  await page.route("**/api/v1/courses/*/students", async (route: Route) => {
    await maybeDelay(delay);
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(envelope({
        course_id: "course-test-001",
        students: TEST_STUDENTS.map((s) => ({
          student_id: s.id,
          status: "active",
          total_nodes: 5,
          nodes_consolidato: 2,
          nodes_lacuna: 1,
        })),
        total: TEST_STUDENTS.length,
      })),
    });
  });
}

/**
 * Inject a pre-built JWT into localStorage so the dashboard treats the
 * session as authenticated. Call BEFORE navigating to dashboard pages.
 */
export async function injectTeacherAuth(page: Page) {
  await page.addInitScript((token: string) => {
    localStorage.setItem("maestro_token", token);
    localStorage.setItem("maestro_refresh", "test-refresh-token");
  }, TEACHER_TOKEN);
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

async function maybeDelay(ms: number) {
  if (ms > 0) {
    await new Promise((resolve) => setTimeout(resolve, ms));
  }
}
