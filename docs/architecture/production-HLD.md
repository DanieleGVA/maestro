# MAESTRO -- Production High-Level Design

**Status**: Ratified
**Date**: 2026-05-18
**Version**: 1.0
**Author**: MSTR-02 (Chief Technical Architect)
**Co-signed**: MSTR-03 (CPA -- pedagogical interfaces), MSTR-20 (QA Sentinel)
**Task**: T2.5
**Input documents**: HLD-001 (Multi-Agent System), HLD-002 (Knowledge Graph), HLD-003 (Content Generation), HLD-004 (Data & Mastery State), ADR-001 through ADR-005

---

## 1. System Overview

MAESTRO is a personalised learning companion for Italian IT students (ages 13-19). It analyzes assessment results, identifies knowledge gaps, generates tailored recovery content, and tracks mastery across a structured curriculum -- all under strict GDPR compliance for minors.

### 1.1 Core Value Proposition

```
Teacher uploads  -->  System identifies  -->  Student receives
lesson + test        per-student gaps         personalised recovery
                                              content + quizzes
                                              + retention checks
```

### 1.2 Design Principles

1. **PostgreSQL-centric**: Single PG 17 instance with AGE (graph), pgvector (vectors), partitioned audit tables. No external databases.
2. **Consent-before-computation**: No agent operates on student data without verified consent. Structural enforcement via LangGraph graph topology.
3. **Safeguarding-before-delivery**: Every content output reviewed before reaching a minor. Non-bypassable graph constraint.
4. **Pseudonymisation at the LLM boundary**: No PII in external API calls. Session-scoped, in-memory mapping only.
5. **EU data residency**: All infrastructure in EU (Hetzner + Scaleway). No data leaves EU.
6. **MVP-first, V1/V2-ready**: Schema and interfaces designed for extension without rewrites.

---

## 2. Architecture Overview

### 2.1 Runtime Architecture

```
                    +-----------+       +------------+
                    | React     |       | Next.js    |
                    | Native +  |       | Teacher    |
                    | Expo      |       | Dashboard  |
                    | (Student) |       |            |
                    +-----+-----+       +-----+------+
                          |                   |
                          +-------+-----------+
                                  |
                          +-------v---------+
                          |    Keycloak     |
                          | (SAML 2.0/OIDC)|
                          +-------+---------+
                                  |
                          +-------v---------+
                          |  FastAPI + WS   |
                          |  (Python 3.12)  |
                          +-------+---------+
                                  |
                    +-------------v--------------+
                    |    LangGraph Orchestrator   |
                    |    (StateGraph + PG Saver)  |
                    +----+---+---+---+---+---+---+
                         |   |   |   |   |   |
              +----------+   |   |   |   |   +----------+
              |              |   |   |   |               |
         +----v---+    +----v-+ +v--v+ +v----+    +-----v-----+
         |Identity|    |Curric| |KMM | |Diag.|    |Safeguard. |
         |&Consent|    |Ingest| |    | |Agent|    |Agent      |
         +--------+    +------+ +----+ +-----+    +-----------+
                                  |
              +-------------------+-------------------+
              |                   |                   |
         +----v------+     +-----v-----+     +-------v-----+
         |Content    |     |Text Agent |     |Bilingual    |
         |Orchestr.  |     |           |     |Composer     |
         +-----------+     +-----------+     +-------------+
                                  |
                           +------v------+
                           |Feedback Loop|
                           +-------------+

         +--------------------------------------------------+
         |               PostgreSQL 17                       |
         |  +--------+ +-----+ +-------+ +-----+ +-------+ |
         |  | core   | | kmm | |content| | kg  | | audit | |
         |  +--------+ +-----+ +-------+ +-----+ +-------+ |
         |  +-------------+ +----------+ +----------------+ |
         |  | Apache AGE  | | pgvector | | pg_partman     | |
         |  +-------------+ +----------+ +----------------+ |
         +--------------------------------------------------+
              |                    |
         +----v----+         +----v----+
         |  Redis  |         |Scaleway |
         | (cache, |         |  S3     |
         |  queues)|         | (files) |
         +---------+         +---------+
```

### 2.2 Agent Inventory

| Agent | Phase | LLM | Purpose |
|---|---|---|---|
| Orchestrator | MVP | No | Route requests, enforce consent + safeguarding gates |
| Identity & Consent Manager | MVP | No | Student lifecycle, consent verification, pseudonymisation |
| Knowledge Map Manager (KMM) | MVP | No | Six-state machine, transitions, rollup, retention scheduling |
| Curriculum Ingestion Agent | MVP | Yes | Lesson upload, transcription, concept mapping, vector indexing |
| Student Profiler | MVP | No | 5-dimension content-adaptation profile |
| Diagnostic Agent | MVP | Yes | Error-to-concept mapping, transition preview |
| Content Orchestrator | MVP | No | Channel selection, source retrieval, pipeline coordination |
| Text Agent | MVP | Yes | Recovery documents (F5), remediation paths (F11.7) |
| Bilingual Composer | MVP | Yes | Dual-column translation (Ukrainian, Arabic) |
| Safeguarding Agent | MVP | Yes | Content review, wellbeing detection |
| Feedback Loop Agent | MVP | No | Quiz processing, KMM transitions, engagement metrics |
| Podcast Agent | V1 | Yes | Two-voice audio episodes |
| Game Agent | V1 | Minimal | XP, badges, quests (gamification) |
| Visual Agent | V1/V2 | Yes | Diagrams, code visualisations |
| Dialog Agent | V2 | Yes | Conversational tutoring |

---

## 3. Data Architecture

### 3.1 Database Schemas

Five PostgreSQL schemas provide logical separation and independent access control:

| Schema | Tables | Purpose |
|---|---|---|
| `core` | school, teacher, student, course, enrolment, consent, consent_history, notification, notification_preference | Identity, consent, enrollment |
| `kmm` | student_node_state, state_transition_log, retention_schedule, teacher_override | Mastery state, transitions, retention |
| `content` | generated_content, question_bank, bilingual_glossary, lesson_material, lesson_transcript, lesson_chunk, prompt_template | Content storage, quiz bank, RAG vectors |
| `kg` | node, edge, node_embedding, concept_node_link, error_node_mapping, course_granularity_override | KG shadow tables, embeddings, mappings |
| `audit` | audit_log, llm_audit_log, deletion_certificate | Immutable audit trail |

Plus Apache AGE graph `maestro_kg` with vertex labels `MacroNode`, `MicroNode` and edge labels `PREREQUISITE`, `PARENT_OF`, `RELATED_TO`.

### 3.2 Key Data Flows

**Write paths:**
- State transitions -> `kmm.student_node_state` + `kmm.state_transition_log` (append-only)
- Content generation -> `content.generated_content` + S3 (large files)
- Lesson upload -> `content.lesson_material` + `content.lesson_chunk` (pgvector) + AGE graph update
- Consent changes -> `core.consent` + `core.consent_history` (append-only)
- Every operation -> `audit.audit_log` (append-only)
- Every LLM call -> `audit.llm_audit_log` (append-only)

**Read paths:**
- Student knowledge map: `kmm.student_node_state` JOIN `kg.node` + AGE PARENT_OF traversal
- Class heatmap: `kmm.student_node_state` filtered by `course_id` + macro rollup
- Content retrieval: `content.generated_content` by `(student_id, node_id)`
- RAG: `content.lesson_chunk` pgvector similarity search filtered by `course_id`
- Prerequisite chain: AGE Cypher `PREREQUISITE*1..20` traversal

### 3.3 Partitioning Strategy

| Table | Strategy | Rationale |
|---|---|---|
| `kmm.state_transition_log` | Monthly RANGE on `created_at` | Time-series, append-only |
| `audit.audit_log` | Monthly RANGE on `created_at` | Time-series, append-only |
| `audit.llm_audit_log` | Monthly RANGE on `created_at` | Time-series, append-only |
| `content.lesson_chunk` | LIST on `course_id` | Course-scoped vector indexes |
| All others | None (MVP) | MVP data volume < 100K rows |

Partition management via `pg_partman` with `pg_cron` scheduled maintenance.

### 3.4 Immutability Enforcement

Append-only tables (`state_transition_log`, `audit_log`, `llm_audit_log`, `consent_history`, `teacher_override`, `deletion_certificate`) have BEFORE UPDATE/DELETE triggers that raise exceptions. The sole exception: right-to-erasure procedure temporarily disables triggers within a SECURITY DEFINER function.

---

## 4. Pedagogical Model

### 4.1 Six-State Mastery Machine

```
non_introdotto --[lesson]--> introdotto --[error]--> lacuna
                                                      |
                                                      v
                                                  in_recupero
                                                    / | \
                                        [<50%]     [50-79%]  [>=80%]
                                          |           |         |
                                        lacuna   in_recupero  da_consolidare
                                                                |
                                                         [retention checks]
                                                                |
                                                           consolidato
```

Canonical transitions defined in HLD-004 Section 3.3, validated by ADR-002.

### 4.2 State Ordering (Worst-to-Best, per ADR-005)

```
lacuna(0) < in_recupero(1) < non_introdotto(2) < introdotto(3) < da_consolidare(4) < consolidato(5)
```

Used for macro-node rollup: `macro_state = worst(child_micro_states)`.

### 4.3 Content-Adaptation Profile (ADR-002)

Five continuous dimensions (0-100 each), NOT "learning styles":

1. `preferenza_contenuto_visuale`
2. `preferenza_contenuto_audio`
3. `preferenza_esercizio_pratico`
4. `preferenza_lettura_approfondita`
5. `preferenza_interazione_dialogica`

Plus: `tone` (confidenziale / neutro / formale), `length` (sintesi / approfondimento).

Default (no consent or no quiz): 20% each, neutro, standard.

### 4.4 Retention Schedule

| Phase | Schedule | Passes for consolidato |
|---|---|---|
| MVP | D+7 (single check) | 1 |
| V1 | D+3, D+7, D+21 (+ optional D+14) | 3 |
| V2 | FSRS adaptive | Dynamic |

### 4.5 Quiz Quality Framework (5 layers)

1. **RAG constraint**: Questions anchored to source materials
2. **Structural validation**: 4 options, 1 correct, no duplicates, valid code
3. **Teacher review**: First-use questions require approval (MVP)
4. **Safeguarding check**: No anxiety language, no tricks, encouraging feedback
5. **Per-question feedback**: Always shown, always encouraging

---

## 5. Security Architecture

### 5.1 Authentication & Authorization

- **Provider**: Keycloak (self-hosted, SAML 2.0 + OIDC)
- **Roles**: student, teacher, coordinator, admin, system
- **Token**: JWT with role claims, validated at FastAPI middleware
- **Session**: Stateless JWT, no server-side sessions

### 5.2 Data Protection

| Layer | Mechanism |
|---|---|
| In transit | TLS 1.3 everywhere |
| At rest (PII) | pgcrypto `pgp_sym_encrypt` for name, surname, email |
| At rest (files) | Scaleway S3 server-side encryption |
| LLM boundary | Pseudonymisation (session-scoped, in-memory) |
| Audit trail | Immutable (trigger-enforced) |
| Native language | GDPR Art. 9; stored only with consent (b); referenced by ISO code only in prompts |

### 5.3 GDPR Compliance

| Requirement | Implementation |
|---|---|
| 5 granular consents (F14.3) | `core.consent` table, each independently revocable |
| Right to erasure (Art. 17) | Atomic stored procedure `core.execute_right_to_erasure` + deletion certificate |
| Data minimisation | Birth year (not DOB), IP hash (not raw IP), no unnecessary PII |
| Retention policies | Monthly partition management via pg_partman; configurable per data category |
| EU data residency | Hetzner (Germany) + Scaleway (France/Netherlands) |

### 5.4 Database Roles

| Role | Permissions |
|---|---|
| `maestro_app` | CRUD on `core`, `kmm`, `content`, `kg`. INSERT-only on `audit`. |
| `maestro_readonly` | SELECT on all schemas. Used by analytics/reporting. |
| `maestro_erasure` | EXECUTE on `core.execute_right_to_erasure`. No other write access. |

---

## 6. Deployment Architecture

### 6.1 Infrastructure (MVP)

| Component | Provider | Region | Spec |
|---|---|---|---|
| Application (FastAPI) | Hetzner Cloud | Falkenstein (DE) | 2x CPX31 (4 vCPU, 8 GB) |
| PostgreSQL 17 | Hetzner Cloud | Falkenstein (DE) | 1x CCX33 (8 vCPU, 32 GB, 240 GB NVMe) |
| Redis | Hetzner Cloud | Falkenstein (DE) | 1x CX22 (2 vCPU, 4 GB) |
| Object Storage | Scaleway | Paris (FR) / Amsterdam (NL) | S3-compatible |
| Keycloak | Hetzner Cloud | Falkenstein (DE) | 1x CX22 |
| Grafana + Tempo + Loki | Hetzner Cloud | Falkenstein (DE) | 1x CPX31 |

**Estimated monthly cost**: EUR 300-520 (per ADR-001).

### 6.2 Scalability Path

| Dimension | MVP | V1 | V2 |
|---|---|---|---|
| Schools | 1 | 3-5 | 10+ |
| Students | 30 | 150 | 500+ |
| App instances | 2 | 4 | 8+ (auto-scaling) |
| Database | Single instance | Single + read replica | Primary + read replicas |
| Redis | Single instance | Single | Sentinel cluster |

### 6.3 Observability

- **Tracing**: OpenTelemetry SDK -> Grafana Tempo
- **Metrics**: Prometheus metrics -> Grafana dashboards
- **Logs**: Structured JSON -> Grafana Loki
- **LLM dashboard**: Token usage, cost, latency per agent (from `audit.llm_audit_log`)
- **Alerting**: Grafana alerts for: LLM circuit breaker open, safeguarding block rate > 5%, DB connection pool exhaustion, queue depth > threshold

---

## 7. Key Flows

### 7.1 Lesson Upload (F2)

```
Teacher -> POST /api/v1/courses/{id}/lessons
  -> Orchestrator -> consent_gate (pass-through for teacher)
  -> Curriculum Ingestion Agent
    -> File storage (S3)
    -> Text extraction / Transcription (async for audio/video)
    -> Chunking + Embedding (pgvector)
    -> Concept mapping (LLM: GPT-4o-mini)
    -> [If confidence < 80%: INTERRUPT for teacher validation]
    -> KG update (AGE + shadow tables)
    -> KMM bulk init: enrolled students get 'introdotto' for new concepts
  -> Notification to students
```

### 7.2 Verification Analysis (F4 -> F11 -> F5)

```
Teacher -> POST /api/v1/courses/{id}/verifications
  -> Orchestrator -> consent_gate (pass-through)
  -> Diagnostic Agent
    -> Score ingestion
    -> Error-to-concept mapping (LLM: Claude for code, GPT-4o-mini for scores)
    -> [If confidence < 80%: INTERRUPT for teacher validation]
    -> Transition preview
    -> [INTERRUPT: teacher confirms transitions]
  -> KMM bulk transition (atomic)
  -> Per student with new lacunae:
    -> Content Orchestrator -> Text Agent -> Bilingual Composer -> Safeguarding
  -> Teacher report generated
  -> Notifications sent
```

### 7.3 Gap Closure Cycle (F11.6 -> F11.10)

```
Student -> starts recovery mission
  -> Orchestrator -> consent_gate -> check (a)
  -> KMM: lacuna -> in_recupero
  -> Content Orchestrator -> Text Agent -> [Bilingual] -> Safeguarding -> Deliver
  -> Student studies, requests quiz
  -> Quiz Engine: question bank -> [LLM generate if needed] -> [Teacher review] -> Safeguarding
  -> Student submits quiz
  -> Feedback Loop:
    >= 80%: in_recupero -> da_consolidare, schedule D+7 retention
    50-79%: stay in_recupero, attempt++, varied content
    < 50%:  in_recupero -> lacuna, alert teacher
  -> Per-question feedback shown
```

### 7.4 Retention Check (F11.10)

```
pg_cron trigger (hourly, school hours)
  -> Find due retention checks (next_retention_check <= now())
  -> Notification to student
  -> Student opens retention check
  -> Quiz at Bloom's Understand+Apply level
  -> Score >= 80%: da_consolidare -> consolidato (MVP, single check)
  -> Score < 80%:  da_consolidare -> lacuna (regression)
```

---

## 8. ADR Register

| ADR | Title | Status | Author | Key Decision |
|---|---|---|---|---|
| ADR-001 | Tech Stack | Ratified | MSTR-02 | PG-centric stack, Claude+GPT-4o-mini, React Native+Next.js |
| ADR-002 | Pedagogical Model | Ratified | MSTR-03 | 5-dim profile (not "learning styles"), 6-state machine, worst-state rollup |
| ADR-003 | Orchestrator Pattern | Ratified | MSTR-04 | Central LangGraph StateGraph with PG checkpointing |
| ADR-004 | Data Model | Ratified | MSTR-07 | App-level state machine, trigger-enforced audit, pgcrypto PII, atomic erasure |
| ADR-005 | Interface Resolution | Ratified | MSTR-02 | Schema naming, state ordering, table merges, llm_audit_log addition |

---

## 9. Open Items

| # | Item | Owner | Priority | Notes |
|---|---|---|---|---|
| 1 | HLD-002 shadow table DDL must be updated to use `kg` schema prefix | MSTR-05 | High | Before Phase 4 |
| 2 | HLD-004 `compute_macro_state` function must use ADR-005 state ordering | MSTR-07 | High | Before Phase 4 |
| 3 | `audit.llm_audit_log` DDL must be added to migration scripts | MSTR-07 | High | Before Phase 4 |
| 4 | `content.generated_content` amendments (node_type, embedding, content_inline) | MSTR-07 | High | Before Phase 4 |
| 5 | `content.question_bank` canonical schema must replace `content.quiz_question` | MSTR-07 | High | Before Phase 4 |
| 6 | DPIA for the data model (Phase 3, MSTR-16) | MSTR-16 | Medium | Depends on this HLD |
| 7 | Prompt template registry: file-based (MVP) vs DB-based (V1) decision | MSTR-06 | Low | MVP uses Python code |
| 8 | Glossary pre-population (Ukrainian + Arabic, ~300 terms each) | MSTR-18 | Medium | Before MVP pilot |
| 9 | Keycloak realm configuration for SAML 2.0 + student/teacher/admin roles | MSTR-12 | Medium | Phase 4 |
| 10 | Circuit breaker library selection (tenacity, pybreaker, or custom) | MSTR-08 | Low | Phase 4 |

---

## 10. Phase 2 Gate Checklist

Per CLAUDE.md Phase 2 gate requirements:

| Requirement | Status | Evidence |
|---|---|---|
| 4 architecture HLDs ratified | DONE | HLD-001, HLD-002, HLD-003, HLD-004 in `docs/architecture/` |
| Cross-component interface contracts in machine-readable format | DONE | `docs/architecture/interface-contracts.md` (typed schemas, SQL DDL, API signatures) |
| Production HLD signed off by CTA + CPA + QA Sentinel | DONE | This document. CTA: MSTR-02. CPA co-sign: MSTR-03. QA: MSTR-20. |
| Conflicts resolved via ADR | DONE | ADR-005 in `.maestro/decisions/ADR-005-interface-resolution.md` |

**Phase 2 gate: PASSED.**

---

## 11. Tech Stack Summary

| Component | Choice | ADR |
|---|---|---|
| LLM (primary) | Claude API | ADR-001 #1 |
| LLM (secondary) | GPT-4o-mini | ADR-001 #1 |
| Embedding | OpenAI text-embedding-3-small (1536d) | ADR-001 #1 |
| TTS (V1) | OpenAI TTS v1 | ADR-001 #7 |
| Vector DB | pgvector (in PostgreSQL) | ADR-001 #2 |
| Knowledge Graph | Apache AGE (in PostgreSQL) | ADR-001 #3 |
| State Store | PostgreSQL 17 | ADR-001 #4 |
| Backend Framework | FastAPI + LangGraph | ADR-001 #5 |
| Frontend (Student) | React Native + Expo | ADR-001 #6 |
| Frontend (Teacher) | Next.js | ADR-001 #6 |
| Auth | Keycloak (SAML 2.0 + OIDC) | ADR-001 #9 |
| Cache + Queue | Redis | ADR-001 #4 |
| Object Storage | Scaleway S3 | ADR-001 #8 |
| Observability | OpenTelemetry + Grafana | ADR-001 #10 |
| Infrastructure | Hetzner Cloud + Scaleway | ADR-001 #8 |

---

*Ratified by MSTR-02 (CTA). CPA co-sign: MSTR-03 (pedagogical model, safeguarding, bilingualism). QA Sentinel review: MSTR-20. Filed per CLAUDE.md governance rules.*
