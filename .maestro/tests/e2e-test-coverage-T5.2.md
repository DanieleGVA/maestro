# T5.2 E2E Acceptance Test Coverage Record

**Task**: T5.2 -- E2E Acceptance Tests
**Author**: MSTR-14 (Test Engineer)
**Date**: 2026-05-20
**Status**: COMPLETE

---

## Summary

E2E acceptance tests created for all MVP user journeys covering both teacher
dashboard (Playwright) and student mobile app (test specifications for Detox).

## Test File Inventory

### Infrastructure

| File | Purpose |
|---|---|
| `tests/e2e/playwright.config.ts` | Playwright config (Chromium, Firefox, WebKit) |
| `tests/e2e/fixtures/test-data.ts` | Shared test data (pseudonymised, no real PII) |
| `tests/e2e/fixtures/types.ts` | Shared type definitions (6-state machine) |
| `tests/e2e/helpers/api-mock.ts` | API route interception for mocked backend |

### Teacher Dashboard (Playwright -- executable)

| File | Tests | Journey |
|---|---|---|
| `tests/e2e/teacher/login.spec.ts` | 9 | Login: form, success, failure, keyboard, a11y |
| `tests/e2e/teacher/dashboard-home.spec.ts` | 7 | Dashboard home: cards, links, welcome |
| `tests/e2e/teacher/classes.spec.ts` | 9 | Class list + heatmap: table, legend, breadcrumb |
| `tests/e2e/teacher/student-detail.spec.ts` | 11 | Student detail + override modal (F11.12) |
| `tests/e2e/teacher/lesson-upload.spec.ts` | 12 | Lesson upload + concept mapping review (F2) |
| `tests/e2e/teacher/alerts.spec.ts` | 4 | Wellbeing alerts (F11.15) |

**Total teacher tests**: 52

### Student Mobile (Specifications -- Detox target)

| File | Specs | Journey |
|---|---|---|
| `tests/e2e/student/login.spec.ts` | 7 | Login: form, auth, keyboard, a11y |
| `tests/e2e/student/home-dashboard.spec.ts` | 7 | Home: summary, missions, links |
| `tests/e2e/student/mastery-map.spec.ts` | 6 | Mastery map: nodes, states, navigation |
| `tests/e2e/student/node-detail.spec.ts` | 9 | Node detail: all 6 states, CTA, back nav |
| `tests/e2e/student/quiz.spec.ts` | 10 | Quiz: questions, submit, results, no timer |
| `tests/e2e/student/missions.spec.ts` | 7 | Missions: list, filter, nav, encouraging tone |
| `tests/e2e/student/profile.spec.ts` | 7 | Profile: font slider, privacy, logout |

**Total student specs**: 53

## Requirements Traceability

| Requirement | Test Coverage |
|---|---|
| F2 (lesson upload) | lesson-upload.spec.ts |
| F8 (encouraging tone) | node-detail, quiz, missions, home specs |
| F9.4 (font size) | profile.spec.ts |
| F11 (mastery map) | mastery-map, node-detail, classes specs |
| F11.3 (rollup state) | mastery-map.spec.ts |
| F11.8 (quiz) | quiz.spec.ts |
| F11.9 (scoring) | quiz.spec.ts |
| F11.12 (teacher override) | student-detail.spec.ts |
| F11.14 (class heatmap) | classes.spec.ts |
| F11.15 (wellbeing alerts) | alerts.spec.ts |
| F14 (authentication) | login.spec.ts (both) |
| N2 (accessibility) | All tests verify a11y attributes |
| WCAG 2.1 AA | Focus indicators, labels, roles, contrast |
| WCAG 2.2.1 (no timer) | quiz.spec.ts TC-ST-QUIZ-08 |

## Safeguarding Checks in Tests

- No PII in test data (pseudonymised student IDs)
- Encouraging tone verified for lacuna/in_recupero states
- No FOMO/urgency language in retention check display
- No public student comparisons
- Wellbeing alerts use pseudo-IDs
- Override requires motivation >= 20 chars (audit trail)

## Canonical State Machine Coverage

All 6 states verified in tests:
- `non_introdotto` -- mastery-map, node-detail
- `introdotto` -- mastery-map, classes heatmap
- `lacuna` -- node-detail, missions, home dashboard
- `in_recupero` -- node-detail, missions, quiz
- `da_consolidare` -- node-detail (retention check, no FOMO)
- `consolidato` -- node-detail (positive feedback)

## Test Data

- All test fixtures in `tests/e2e/fixtures/test-data.ts`
- JWT tokens built with `buildTestJwt()` helper (test-only, not production keys)
- Mock API uses Playwright route interception (no real backend needed)
- Student data pseudonymised (STU-001 through STU-005)
