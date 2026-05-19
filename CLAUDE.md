# MAESTRO — Workspace Governance

**Project**: MAESTRO — Personalised Learning Companion for IT Students
**Namespace**: MSTR-
**Convention**: PROMETHEUS v3.0
**Version**: v1.0

---

## Authority Model

- **Programme Director** (MSTR-01): programme governance, schedule, final delivery
- **Chief Technical Architect** (MSTR-02): technical authority
- **Chief Pedagogical Architect** (MSTR-03): pedagogical & educational authority
- **QA Sentinel** (MSTR-20): veto power on deliverables
- **Verification Sidecar** (MSTR-21): evidence-based truth enforcement

CTA and CPA are **co-equal** on decisions touching the learning model.

---

## Non-Negotiable Rules

### Minor Safety

- Every student in MAESTRO is a minor (13-19). No agent generates content without Safeguarding review.
- Native language is GDPR Art. 9 sensitive data. Treat accordingly across all flows.
- No public student comparisons. No FOMO, scarcity, or addictive patterns in gamification.

### Evidence Before Completion

- Claiming "task done" without evidence is a Verification Sidecar block.
- **Code**: git diff present + CI passes.
- **Test**: actual test run output attached.
- **DPIA**: document with required sections present in `.maestro/dpia/`.
- **Pedagogical claim**: linked to model validation or empirical evidence.
- **Architecture**: ADR filed in `.maestro/decisions/` with alternatives considered + chosen option + consequences.

### Pedagogical Integrity

- "Learning styles" as fixed traits is contested (Pashler et al. 2009, Newton 2015). F3 must be framed as a *content-adaptation profile*, not a learner-typing claim, unless LSS validation explicitly justifies otherwise.
- F11 state changes from override must include teacher motivation in audit log.
- No public student comparisons. No FOMO, scarcity, or addictive patterns in gamification.
- The six-state machine (non_introdotto, introdotto, lacuna, in_recupero, da_consolidare, consolidato) is the canonical model. Changes require CPA + LSS + CTA joint ADR.

### Privacy

- No PII to external LLMs. Pseudonymise at the boundary.
- 5 granular consents (F14.3): each separately captured, separately revocable:
  - (a) profiling for learning style
  - (b) native language (Art. 9)
  - (c) family communications
  - (d) cross-year history
  - (e) aggregated research
- Right to erasure: full implementation, no soft-delete loopholes.
- EU data residency enforced on all infrastructure.
- Retention policies explicit for every data category.

### Code Quality

- Test coverage: >=80% unit on services with state, >=60% integration on critical paths.
- All security-sensitive code reviewed by MSTR-13 (Security Engineer).
- All UI reviewed by MSTR-17 (Accessibility & UX) for WCAG 2.1 AA conformance.
- No code merged without passing CI.

### Handoff Standard

- All cross-agent handoffs use JSON schema in `.maestro/schemas/handoff.json`.
- Required fields: `from`, `to`, `task_id`, `context`, `decisions`, `open_items`, `evidence_refs`.
- Handoffs are persisted to `.maestro/handoffs/` before any context compaction.

### ADR Standard

- Every architecture decision has an ADR in `.maestro/decisions/`.
- ADR format: title, status, context, decision, alternatives considered, consequences.
- ADRs are ratified by CTA (technical) or CPA (pedagogical) or both (cross-domain).

---

## Escalation Paths

| Level | Path | Trigger |
|---|---|---|
| 1 | Agent -> QA Sentinel or Verification Sidecar | Normal deliverable review |
| 2 | QA Sentinel -> CTA / CPA (per domain) | QA rejection or cross-track issue |
| 3 | CTA + CPA -> Programme Director | Unresolvable cross-track conflict |
| 4 | Director -> Human user (Daniele) | DPIA blocker, pedagogical model invalidation, budget decision |

Additional triggers:
- Cross-track architectural conflict CTA vs CPA cannot resolve -> Director
- DPIA blocker -> Director -> Human
- Pedagogical model invalidation by LSS -> CPA -> Director
- Three QA rejections on same deliverable -> mandatory cross-track meeting
- Security finding affecting production-readiness -> CTA + Security -> Director

---

## Persistence Layer

```
.maestro/
  decisions/      -> ADRs (architecture decisions) — NEVER compact
  handoffs/       -> inter-agent handoff documents (JSON) — NEVER compact
  qa_findings/    -> QA Sentinel findings register — NEVER compact
  dpia/           -> privacy & compliance work products — NEVER compact
  pedagogical/    -> pedagogical reviewer notes — NEVER compact
  tests/          -> test specifications and coverage records — NEVER compact
  tasks/          -> task DAG state — NEVER compact
  schemas/        -> JSON schemas for handoffs
```

Safe to compact: verbose intermediate reasoning, superseded drafts, exploratory searches that yielded no result.

---

## Phase Gates

### Gate Phase 1 (Foundation)
- v0.3 requirements doc complete with traceability to v0.2
- Tech stack ADRs covering all v0.2 S5 components
- Pedagogical model validation: F3, F11, retention intervals, rollup rule

### Gate Phase 2 (Architecture)
- 4 architecture HLDs ratified (Agent, KG, Content, Data)
- Cross-component interface contracts in machine-readable format
- Production HLD signed off by CTA + CPA + QA Sentinel

### Gate Phase 3 (Compliance & Safety)
- DPIA draft complete with risk register
- 5 consent flows designed with UX mockups
- Safeguarding policies + accessibility design system + security architecture

### Gate Phase 4 (Implementation)
- All T4.x tasks have code merged on main + passing CI
- Code coverage targets met
- F11 state machine verified against ADR

### Gate Phase 5 (Testing)
- All test suites passing
- WCAG 2.1 AA conformance (no critical findings)
- Security pen-test: no critical, <=3 high findings
- Bias audit completed with mitigations

### Gate Phase 6 (Deployment)
- CI/CD operational + monitoring live
- DR plan tested
- DPIA filed
- Pilot deployment plan approved by Director + CTA + CPA + Privacy + QA Sentinel + Human

---

## Team Roster Quick Reference

| ID | Name | Tier | Effort |
|---|---|---|---|
| MSTR-01 | Programme Director | Leadership | high |
| MSTR-02 | Chief Technical Architect | Leadership | max |
| MSTR-03 | Chief Pedagogical Architect | Leadership | max |
| MSTR-04 | Agent Systems Architect | Architecture | max |
| MSTR-05 | KG & Curriculum Architect | Architecture | high |
| MSTR-06 | Content & Multimodal Architect | Architecture | high |
| MSTR-07 | Data & Mastery State Architect | Architecture | high |
| MSTR-08 | Backend Engineer | Engineering | medium |
| MSTR-09 | Mobile & Frontend Engineer | Engineering | medium |
| MSTR-10 | AI/ML Engineer | Engineering | high |
| MSTR-11 | Data Engineer | Engineering | medium |
| MSTR-12 | DevOps & SRE | Engineering | medium |
| MSTR-13 | Security Engineer | Engineering | medium |
| MSTR-14 | Test Engineer | Engineering | medium |
| MSTR-15 | Learning Sciences Specialist | Domain | high |
| MSTR-16 | Privacy & Compliance Engineer | Domain | high |
| MSTR-17 | Accessibility & UX Specialist | Domain | medium |
| MSTR-18 | Localization & Bilingualism Lead | Domain | medium |
| MSTR-19 | Safeguarding & Ethics Specialist | Domain | high |
| MSTR-20 | QA Sentinel | Oversight | high |
| MSTR-21 | Verification Sidecar | Oversight | medium |
| MSTR-22 | Pedagogical Reviewer | Oversight | high |
| MSTR-23 | Infrastructure & Resource Manager | Infrastructure | medium |

---

## Current Project Status

**Last updated**: 2026-05-18
**Current phase**: Phase 2 COMPLETE — Phase 3 (Compliance & Safety) ready to start
**Task DAG**: `.maestro/tasks/task_dag.yaml` (T1.1–T2.5 completed, T3.1+ pending)

### Completed Phases

**Phase 1 — Foundation (COMPLETE)**
- T1.1: Requirements v0.3 synthesis → `docs/MAESTRO_requisiti_v0.3.md`
- T1.2: Tech stack revalidation → `.maestro/decisions/ADR-001-tech-stack.md`
- T1.3: Pedagogical model validation → `.maestro/decisions/ADR-002-pedagogical-model.md`

**Phase 2 — Architecture (COMPLETE)**
- T2.1: Multi-agent system HLD → `docs/architecture/HLD-001-multi-agent-system.md` + `.maestro/decisions/ADR-003-orchestrator-pattern.md`
- T2.2: KG & curriculum architecture → `docs/architecture/HLD-002-knowledge-graph.md`
- T2.3: Content generation architecture → `docs/architecture/HLD-003-content-generation.md`
- T2.4: Data & mastery state architecture → `docs/architecture/HLD-004-data-mastery-state.md` + `.maestro/decisions/ADR-004-data-model.md`
- T2.5: Interface contracts + production HLD → `docs/architecture/interface-contracts.md` + `docs/architecture/production-HLD.md` + `.maestro/decisions/ADR-005-interface-resolution.md`

### Key Architecture Decisions (ADR Summary)

| ADR | Decision | Rationale |
|---|---|---|
| ADR-001 | PostgreSQL-centric stack (pgvector + Apache AGE + relational in single PG17 instance) | Single backup, ACID across domains, EU residency, MVP cost EUR 300-520/mo |
| ADR-001 | Claude API primary + GPT-4o-mini batch, via LLMGateway abstraction | Pseudonymization at boundary, model routing, cost optimization |
| ADR-001 | LangGraph + FastAPI backend, React Native + Expo (student), Next.js (teacher) | Durable checkpointing for audit, native accessibility APIs |
| ADR-001 | Hetzner Cloud (DE/FI) + Scaleway (FR), Keycloak auth | EU-native, no CLOUD Act, SAML 2.0 + OIDC + MFA |
| ADR-002 | "Content-adaptation profile" not "learning styles"; 5-dim continuous vector | Pashler 2009, Newton 2015 — avoid contested fixed-trait claims |
| ADR-002 | 6-state machine validated (Bloom mastery learning, Guskey corrective instruction) | Quiz threshold >=80%, regression conservative but justified |
| ADR-002 | Retention: MVP fixed D+7, V1 D+3/D+7/D+21, V2 FSRS adaptive | FSRS columns present from day 1 for migration readiness |
| ADR-002 | Rollup: worst-state + UI progress indicator ("7/10 consolidati") | Pedagogically rigorous + encouraging UX |
| ADR-003 | Central LangGraph StateGraph orchestrator (not event bus) | Consent/safeguarding gates are structural, not policy-based |
| ADR-004 | 4 PostgreSQL schemas (core/kmm/content/audit), append-only audit | Application-level state machine, atomic right-to-erasure, pgcrypto encryption |
| ADR-005 | 7 cross-HLD conflicts resolved (state ordering, schema naming, table merges) | Canonical state ordering: lacuna < in_recupero < non_introdotto < introdotto < da_consolidare < consolidato |

### Open Questions Resolved

- **OQ7** (mini-quiz source): teacher-first + AI-generated with 5-layer quality framework (ADR-002)
- **OQ8** (rollup rule): worst-state validated with two-tier display enhancement (ADR-002)

### Open Questions Still Pending

- OQ1: LLM choice — decided Claude primary + GPT-4o-mini batch (ADR-001), but open-source fallback TBD
- OQ2: Release model (SaaS vs on-premise) — post-pilot decision
- OQ3: Pricing — escalate to Daniele
- OQ4: Data ownership governance — from DPIA (T3.1)
- OQ5: MIUR certification — from T3.1
- OQ6: Efficacy study design — from T5.5
- OQ11: DPO liaison — escalate to Daniele
- OQ12: Pilot school confirmation — escalate to Daniele
- OQ13-14: Linear vs Jira, Confluence vs Notion — TBD
- OQ15: Effort Router thresholds — validate after Phase 4

### Next Phase: Phase 3 — Compliance & Safety

Tasks ready to start (see task_dag.yaml for dependencies):
- T3.1: DPIA + consent design (MSTR-16) — blocked by T2.4 ✅
- T3.2: Safeguarding policies (MSTR-19) — blocked by T2.3 ✅
- T3.3: Accessibility design system (MSTR-17) — blocked by T2.5 ✅
- T3.4: Bilingual ops (MSTR-18) — blocked by T2.3, T2.5 ✅
- T3.5: Security architecture (MSTR-13) — blocked by T2.5, T3.1

---

## Source Documents

### Requirements & Design
- `docs/MAESTRO_documento_progetto_v0.2.md` — Original project requirements (F1-F14, N1-N7)
- `docs/MAESTRO_requisiti_v0.3.md` — Consolidated requirements v0.3 (F1-F17, N1-N9, 58 UC, 42 screens)
- `docs/MAESTRO_agent_team_v1.md` — Team architecture specification (23 agents, 32-task DAG)
- `docs/MAESTRO_use_cases_v1.md` — Full use case catalog (58 UC, Cockburn format)
- `docs/MAESTRO_schermate_v1.md` — Screen specifications (42 screens)
- `docs/use_cases/` — Use case work plan, suddiviso per attore

### Architecture (Phase 2 deliverables)
- `docs/architecture/production-HLD.md` — **START HERE** — Unified production HLD, system overview
- `docs/architecture/HLD-001-multi-agent-system.md` — 15 agents, orchestration, flows, safeguarding
- `docs/architecture/HLD-002-knowledge-graph.md` — KG schema, ingestion, concept mapping, DDL
- `docs/architecture/HLD-003-content-generation.md` — Text agent, prompts, bilingual, quiz, caching
- `docs/architecture/HLD-004-data-mastery-state.md` — KMM state store, F14 data model, complete DDL
- `docs/architecture/interface-contracts.md` — 14 typed contracts, REST API, event schemas

### Decisions
- `.maestro/decisions/ADR-001-tech-stack.md`
- `.maestro/decisions/ADR-002-pedagogical-model.md`
- `.maestro/decisions/ADR-003-orchestrator-pattern.md`
- `.maestro/decisions/ADR-004-data-model.md`
- `.maestro/decisions/ADR-005-interface-resolution.md`
