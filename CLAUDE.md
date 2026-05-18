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

## Source Documents

- `docs/MAESTRO_documento_progetto_v0.2.md` — Project requirements (F1-F14, N1-N7)
- `docs/MAESTRO_agent_team_v1.md` — Team architecture specification
- `docs/MAESTRO_piano_di_lavoro_use_case_v0.2.md` — Use case work plan (58 UC)
