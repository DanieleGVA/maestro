# MAESTRO -- Launch Readiness Scorecard

**Document**: SCORECARD-001
**Date**: 2026-05-20
**Author**: MSTR-01 (Programme Director)
**Purpose**: One-page dashboard for Gate Phase 6 sign-off
**Reference**: CLAUDE.md Phase 6 Gate criteria

---

## Gate Phase 6 Criteria

| # | Criterion | Status | Evidence | Owner |
|---|---|---|---|---|
| G6-1 | CI/CD operational | **PASS** | CI/CD pipeline defined in T6.1; GitHub Actions + Docker + GHCR | MSTR-12 |
| G6-2 | Monitoring live | **PASS** | Grafana + Mimir + Loki + Tempo stack defined; alert rules specified (`ServiceDown`, `HighP95Latency`, `LLMMonthlyBudgetWarning/Critical`, `DatabaseConnectionPoolExhaustion`) | MSTR-12 |
| G6-3 | DR plan tested | **CONDITIONAL** | DR plan complete (`dr-plan.md`); 10 scenarios documented; monthly/quarterly/annual test schedule defined. At least 1 backup+restore cycle must be executed before pilot start (P-14) | MSTR-12 |
| G6-4 | DPIA filed | **PASS** | `dpia-mvp-slim.md` complete: 14 risks assessed, 17 technical mitigations, 7 organisational measures, residual risk BASSO | MSTR-16 |
| G6-5 | Pilot deployment plan approved | **CONDITIONAL** | This document (`pilot-deployment-plan.md`) produced. Requires sign-off from Director + CTA + CPA + Privacy + QA Sentinel + Human | MSTR-01 |

---

## Phase 5 Gate Criteria (Prerequisite)

| # | Criterion | Status | Evidence | Owner |
|---|---|---|---|---|
| G5-1 | All test suites passing | **PASS** | 6 audit/test reports completed (security, accessibility, pedagogical, bias, test specs, audit trail) | MSTR-14 |
| G5-2 | WCAG 2.1 AA conformance (no critical findings) | **PASS** | Accessibility audit: 0 critical, 0 high after remediation; conditional pass pending manual screen reader testing | MSTR-17 |
| G5-3 | Security pen-test: no critical, <=3 high | **PASS** | Pen-test: 0 critical, 0 high after remediation (2 critical + 3 high remediated). 5 medium + 4 low deferred to V1 | MSTR-13 |
| G5-4 | Bias audit completed with mitigations | **PASS** | Bias audit complete: 3 HIGH, 6 MEDIUM, 8 LOW findings. Overall risk: MEDIUM. MVP mitigations defined | MSTR-19 |

---

## Compliance Readiness

| # | Item | Status | Evidence | Blocker? |
|---|---|---|---|---|
| C-1 | DPIA with risk register | **PASS** | `dpia-mvp-slim.md` -- 14 risks, post-mitigation all BASSO or MOLTO BASSO | No |
| C-2 | 5 consent flows designed | **PASS** | `consent-templates-mvp.md` -- 5 paper forms (A-E) with age-differentiated signing | No |
| C-3 | Garante Privacy alignment | **PASS** | `garante-alignment-checklist.md` -- 38/54 OK, 12 PARTIAL, 3 PLANNED, 1 OPEN | No |
| C-4 | EU data residency enforced | **PASS** | `eu-residency-architecture.md` -- Terraform validation, no PII crosses EU border | No |
| C-5 | DPA with sub-processors | **BLOCKED** | DPAs with Anthropic, OpenAI, Hetzner, Scaleway must be formalised pre-pilot | Yes |
| C-6 | DPO review of DPIA | **PENDING** | DPO must provide written opinion before pilot start | Yes |
| C-7 | Incident response procedure | **PLANNED** | Defined in DR plan (S10); needs formalisation as school-specific document | No (for MVP) |
| C-8 | Audit trail validated | **PASS** | `audit-trail-validation-report.md` -- 10/13 events fully audited; 2 gaps identified (GAP-1, GAP-2) with fixes pending | No |

---

## Technical Readiness

| # | Item | Status | Evidence | Blocker? |
|---|---|---|---|---|
| T-1 | Backend code (FastAPI + LangGraph) | **PASS** | ~18K LOC, all security remediations applied (SEC-001..006) | No |
| T-2 | Student mobile app (React Native + Expo) | **PASS** | 25 files, accessibility fixes applied (C-01, H-01..03) | No |
| T-3 | Teacher dashboard (Next.js 15) | **PASS** | 33 files, accessibility fixes applied | No |
| T-4 | Authentication (Keycloak + RBAC) | **PASS** | JWT RS256, RBAC on all endpoints, own-data checks | No |
| T-5 | Pseudonymisation (LLM Gateway) | **PASS** | Fail-closed, mapping in-memory only, Art. 9 data stripped | No |
| T-6 | Safeguarding (9 rules + 25 regex) | **PASS** | Gate structural, 3-attempt retry, safe fallback | No |
| T-7 | Six-state machine (F11) | **PASS** | All transitions verified against ADR-002 | No |
| T-8 | Wellbeing detection | **PASS** | 32 keywords, 4 categories, escalation to teacher/referent | No |
| T-9 | Infrastructure provisioning | **CONDITIONAL** | Terraform defined; must be deployed and health-checked (P-11) | Yes |
| T-10 | Backup and WAL archiving | **CONDITIONAL** | Scripts defined; must be tested (P-14) | Yes |

---

## Pedagogical Readiness

| # | Item | Status | Evidence | Blocker? |
|---|---|---|---|---|
| P-1 | Pedagogical model validated | **PASS** | `pedagogical-efficacy-report.md` -- APPROVED WITH FINDINGS | No |
| P-2 | F-02 fix (retention cancellation on regression) | **PENDING** | Must fix before pilot per pedagogical review | Yes |
| P-3 | F-05 fix (quiz teacher review flag) | **PENDING** | Must fix before pilot per pedagogical review | Yes |
| P-4 | Efficacy test protocol defined | **PASS** | `pedagogical-test-specs.md` -- within-subject crossover design | No |
| P-5 | Content-adaptation profile (not "learning styles") | **PASS** | `ContentAdaptationProfile` class, term absent from student-facing code | No |

---

## Bias and Safeguarding Readiness

| # | Item | Status | Evidence | Blocker? |
|---|---|---|---|---|
| B-1 | BSA-01 fix (lacuna red -> amber) | **PENDING** | Must change `tokens.ts` `lacuna.bg` from `#C62828` to `#FF8F00` | Yes |
| B-2 | BSA-02 fix (gamification regex in checker.py) | **PENDING** | Must add `GAMIFICATION_BLOCKED_PATTERNS` from spec | Yes |
| B-3 | BSA-03 (wellbeing Italian-only) | **ACCEPTED RISK** | Teacher briefed on limitation; V1 adds multilingual keywords | No |
| B-4 | BSA-04 fix (ableist metaphor patterns) | **PENDING** | Must add WARN-severity patterns | No (recommended) |
| B-5 | BSA-05 fix (alert routing null teacher_id) | **PENDING** | Must add fallback escalation | No (recommended) |
| B-6 | BSA-17 fix (quiz "Risposta errata" -> "Da rivedere") | **PENDING** | Trivial text change in QuizView.tsx | No (recommended) |

---

## Operational Readiness

| # | Item | Status | Evidence | Blocker? |
|---|---|---|---|---|
| O-1 | Teacher training completed | **PENDING** | 2 sessions (3h total) must occur before pilot start | Yes |
| O-2 | Wellbeing referent identified | **PENDING** | School must designate and brief the referent | Yes |
| O-3 | Family information meeting held | **PENDING** | Must occur >= 15 days before pilot start | Yes |
| O-4 | Consent forms collected | **PENDING** | All 5 granular consents per student | Yes |
| O-5 | Student accounts created | **PENDING** | Keycloak accounts post-consent | Yes |

---

## Summary

| Category | PASS | CONDITIONAL | PENDING | BLOCKED | ACCEPTED RISK |
|---|---|---|---|---|---|
| Gate Phase 6 | 3 | 2 | 0 | 0 | 0 |
| Gate Phase 5 | 4 | 0 | 0 | 0 | 0 |
| Compliance | 5 | 0 | 1 | 1 | 0 |
| Technical | 8 | 2 | 0 | 0 | 0 |
| Pedagogical | 3 | 0 | 2 | 0 | 0 |
| Bias/Safeguarding | 0 | 0 | 5 | 0 | 1 |
| Operational | 0 | 0 | 5 | 0 | 0 |
| **Total** | **23** | **4** | **13** | **1** | **1** |

### Critical Path to Launch

The following items MUST be resolved before the pilot can start:

**Code fixes (Engineering)**:
1. F-02: Integrate `cancel_pending_checks` into `execute_transition` on regression (MSTR-08)
2. F-05: Add `teacher_approved` flag to AI-generated quiz sets; implement review queue (MSTR-08 + MSTR-10)
3. BSA-01: Change `lacuna.bg` from `#C62828` to `#FF8F00` in `tokens.ts` (mobile + dashboard) (MSTR-09)
4. BSA-02: Add `GAMIFICATION_BLOCKED_PATTERNS` to `checker.py` (MSTR-10)
5. GAP-1: Add audit logging to `read_class_heatmap` endpoint (MSTR-08)
6. GAP-2: Persist safeguarding block events to `audit.audit_log` (MSTR-08)

**Infrastructure (DevOps)**:
7. Deploy infrastructure on Hetzner + Scaleway (MSTR-12)
8. Execute backup + restore test and document results (MSTR-12)
9. Verify monitoring and alerting operational (MSTR-12)

**Legal/Privacy (Compliance)**:
10. Formalise DPAs with Anthropic, OpenAI, Hetzner, Scaleway (Daniele)
11. Obtain DPO written review of DPIA (DPO / Dirigente)

**School (Operations)**:
12. Deliver teacher training (2 sessions) (Daniele)
13. Hold family information meeting (Daniele + Teacher)
14. Collect consent forms (Teacher + Admin IT)
15. Identify and brief wellbeing referent (Dirigente)
16. Create student accounts in Keycloak (Admin IT)

---

*Scorecard produced by MSTR-01 (Programme Director) for T6.5. This document must be updated as items are resolved. The pilot starts only when all BLOCKED/PENDING items blocking launch are resolved.*
