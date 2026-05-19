# ADR-005: Cross-HLD Interface Resolution

**Status**: Ratified
**Date**: 2026-05-18
**Author**: MSTR-02 (Chief Technical Architect)
**Reviewers**: MSTR-03 (CPA, co-sign on pedagogically-touching items), MSTR-20 (QA Sentinel)
**Task**: T2.5 (Cross-component interface contracts + HLD ratification)
**Related**: HLD-001, HLD-002, HLD-003, HLD-004, ADR-001 through ADR-004

---

## Context

During HLD ratification, the CTA identified seven classes of inconsistency across the four independently-authored HLDs. These must be resolved before implementation to ensure a single authoritative schema and avoid integration-time ambiguity. This ADR records each conflict, the resolution, and the rationale.

---

## Conflict 1: Table Naming Convention

### Observation

HLD-004 uses PostgreSQL schema-qualified names (`core.student`, `kmm.student_node_state`, `content.generated_content`, `audit.audit_log`). HLD-002 uses bare names without schema qualification (`courses`, `students`, `users`, `lesson_materials`, `lesson_chunks`, `generated_content`). HLD-001 uses yet another set of names (`kmm_states`, `kmm_transitions`, `consents`, `students`).

### Resolution

**HLD-004's schema-qualified naming is canonical.** HLD-004 provides the complete DDL with four PostgreSQL schemas (`core`, `kmm`, `content`, `audit`). All other HLDs' table references are informal shorthand and MUST be mapped to HLD-004 names during implementation.

**Canonical mapping:**

| HLD-001 / HLD-002 reference | Canonical (HLD-004) |
|---|---|
| `students` | `core.student` |
| `users` | Does not exist. See Conflict 2 |
| `courses` | `core.course` |
| `consents` | `core.consent` |
| `kmm_states` | `kmm.student_node_state` |
| `kmm_transitions` | `kmm.state_transition_log` |
| `retention_schedule` | `kmm.retention_schedule` |
| `lesson_materials` | HLD-002 table, to be placed in `content` schema: `content.lesson_material` |
| `lesson_chunks` | HLD-002 table, to be placed in `content` schema: `content.lesson_chunk` |
| `lesson_transcripts` | HLD-002 table, to be placed in `content` schema: `content.lesson_transcript` |
| `kg_nodes` | HLD-002 shadow table, to be placed in `kg` schema: `kg.node` |
| `kg_edges` | HLD-002 shadow table, to be placed in `kg` schema: `kg.edge` |
| `kg_node_embeddings` | HLD-002 table, to be placed in `kg` schema: `kg.node_embedding` |
| `concept_node_links` | HLD-002 table, to be placed in `kg` schema: `kg.concept_node_link` |
| `error_node_mappings` | HLD-002 table, to be placed in `kg` schema: `kg.error_node_mapping` |
| `generated_content` (HLD-002) | `content.generated_content` (HLD-004 canonical) |
| `course_granularity_overrides` | HLD-002 table, to be placed in `kg` schema: `kg.course_granularity_override` |
| `llm_audit_log` (HLD-001) | To be placed in `audit` schema: `audit.llm_audit_log` |

**New schema introduced**: `kg` -- for KG shadow tables, embeddings, concept links, and error mappings. This separates KG-specific relational data from generic content storage.

### Rationale

Schema-qualified names provide logical separation, independent permissions per schema, and avoid naming collisions. HLD-004 already defined four schemas; we add a fifth (`kg`) for the KG subsystem's relational tables, which are distinct from the content generation tables.

### Consequences

- (+) Unambiguous table references across all code
- (+) Schema-level GRANT/REVOKE for least-privilege database roles
- (-) All HLD-002 table references must be updated to use the `kg` or `content` schema prefix during implementation

---

## Conflict 2: `users` Table vs Separate `student`/`teacher` Tables

### Observation

HLD-002 references a `users` table (e.g., `MacroNode.created_by UUID FK -> users.id`, `lesson_materials.uploaded_by UUID FK -> users.id`, `concept_node_links.confirmed_by UUID REFERENCES users(id)`). HLD-004 defines separate `core.student` and `core.teacher` tables with no unified `users` table.

### Resolution

**No `users` table.** `core.student` and `core.teacher` are the canonical identity tables per HLD-004. Foreign keys that reference "users" in HLD-002 refer to teachers (the KG is a teacher-authored artefact). Implementation MUST use `core.teacher(id)` as the FK target.

For columns where the referencing entity could be either a student or teacher (e.g., audit log `actor_id`), HLD-004 already handles this by using `TEXT` for `actor_id` with a separate `actor_type` discriminator. This pattern is correct.

### Rationale

Students and teachers have fundamentally different schemas (students have PII encryption, adaptation profiles, consent; teachers have roles). A unified `users` table would either duplicate these concerns or require nullable columns for both. The HLD-004 separation is cleaner.

### Consequences

- (+) Clear identity model, no polymorphic confusion
- (-) Queries that need "any user" (e.g., KG node `created_by`) must know the referencing entity is a teacher. This is acceptable since only teachers author KG content.
- (-) If V2 adds student-authored content (e.g., collaborative notes), a view or polymorphic pattern may be needed

---

## Conflict 3: State Ordering for Worst-State Rollup

### Observation

**HLD-002 Section 6.4** defines state ordering as: `lacuna < in_recupero < non_introdotto < introdotto < da_consolidare < consolidato` (worst to best).

**HLD-004 Section 3.5** defines state ordering as: `non_introdotto(0) < introdotto(1) < lacuna(2) < in_recupero(3) < da_consolidare(4) < consolidato(5)`.

These are semantically different. Under HLD-002's ordering, `lacuna` is the worst state and `non_introdotto` is better than `in_recupero`. Under HLD-004's ordering, `non_introdotto` is the worst and `lacuna` is mid-range.

### Resolution

**HLD-002's ordering is semantically correct and is adopted as canonical.**

The canonical worst-to-best ordering for rollup computation:

```
lacuna(0) < in_recupero(1) < non_introdotto(2) < introdotto(3) < da_consolidare(4) < consolidato(5)
```

**Rationale**: The rollup serves a motivational purpose (ADR-002 Section 4). From a student's perspective:
- `lacuna` (a known gap) is the most concerning state -- it requires action
- `in_recupero` (actively recovering) is slightly better -- work is in progress
- `non_introdotto` (not yet introduced) is neutral -- the student cannot have a gap in something not yet taught
- `introdotto` (introduced, no gaps found) is positive
- `da_consolidare` / `consolidato` are the best

A macro-node with one child in `lacuna` and nine in `consolidato` should show the `lacuna` color, not the `non_introdotto` color. This matches HLD-002's ordering.

**HLD-004's `compute_macro_state` function and Python `STATE_ORDER` dictionary MUST be updated** to use the corrected ordering.

### Consequences

- (+) Rollup semantics match pedagogical intent
- (-) HLD-004 DDL pseudocode must be corrected before implementation
- (!) CPA co-sign obtained: this ordering aligns with ADR-002 Section 4

---

## Conflict 4: `generated_content` Table Schema Mismatch

### Observation

HLD-002 Section 4.3 defines `generated_content` with columns: `id, student_id, node_id, node_type, content_type, content (JSONB), embedding (vector), version, status, created_at, archived_at, archived_by`. FK references `students(id)` and `users(id)`.

HLD-004 Section 7.1 defines `content.generated_content` with different columns: `id, student_id, course_id, node_id, content_type, content_ref (TEXT -- S3 path), version, replaces_id, status, created_by_agent, llm_model, prompt_hash, reviewed_by_teacher, reviewed_at, teacher_modified, language, bilingual, bilingual_language, created_at, modified_at`. FK references `core.student(id)` and `core.course(id)`.

Key differences: HLD-002 stores content inline as JSONB + embedding vector. HLD-004 stores a `content_ref` (S3 path) with metadata. HLD-004 adds `course_id`, provenance tracking, teacher review fields, and bilingual metadata.

### Resolution

**HLD-004's `content.generated_content` is canonical** with the following amendments:

1. **Add `node_type TEXT`** (from HLD-002) to distinguish macro vs micro node references
2. **Add `embedding vector(1536)`** (from HLD-002) for semantic cache support per ADR-001
3. **Add `content_inline JSONB`** -- for MVP, store small content (text, quiz JSON) inline in addition to the S3 reference. This avoids an S3 round-trip for every content read. The `content_ref` remains for large content (audio, PDF).
4. **Keep all HLD-004 columns** for provenance, review, and bilingual tracking

### Rationale

HLD-004's schema is more complete (provenance, review workflow, bilingual metadata). HLD-002's inline JSONB storage and embedding vector are valuable additions for performance and caching. Merging both is the correct approach.

### Consequences

- (+) Single canonical table with full metadata
- (+) Semantic cache via embedding column
- (+) Inline content avoids S3 round-trip for small payloads
- (-) Slightly wider table; acceptable given MVP scale

---

## Conflict 5: Question Bank Table Name and Schema

### Observation

HLD-003 Section 5.3 defines `content.question_bank` with columns including `stem, options (JSONB as {"A": "...", ...}), correct_answer, explanation_correct, explanation_incorrect, source_refs, source_type, teacher_approved, approved_by, times_used, times_correct, discrimination_index, difficulty_index`.

HLD-004 Section 7.2 defines `content.quiz_question` with columns including `question_text, question_type, options (JSONB as [{text, is_correct}]), correct_answer, explanation, bloom_level, difficulty, source, created_by, reviewed_by, times_used, times_correct, discrimination_index`.

Key differences: different table names, different options format (key-value vs array-of-objects), single vs split explanation, different source/review column names.

### Resolution

**Canonical table name: `content.question_bank`** (HLD-003's name). The quiz engine is a content concern, and "question bank" is the domain term used throughout requirements and ADR-002.

**Canonical schema merges both:**

| Column | Source | Notes |
|---|---|---|
| `id, course_id, node_id` | Both | Same |
| `stem` | HLD-003 | Rename HLD-004's `question_text` to `stem` |
| `question_type` | HLD-004 | HLD-003 assumes MCQ only; HLD-004 adds `fill_in, code_completion, true_false` |
| `options` | HLD-003 format | `{"A": "...", "B": "...", ...}` -- matches quiz generation prompt output format |
| `correct_answer` | Both | Letter for MCQ, text for others |
| `explanation_correct` | HLD-003 | Split explanations (correct/incorrect) per ADR-002 quiz feedback spec |
| `explanation_incorrect` | HLD-003 | See above |
| `distractor_rationales` | HLD-003 | JSONB, for teacher review |
| `bloom_level` | Both | Same |
| `difficulty` | HLD-004 | `easy/medium/hard` -- useful for V2 adaptive selection |
| `source_type` | HLD-003 | `teacher_authored, ai_generated_vetted, ai_generated_unvetted` |
| `source_refs` | HLD-003 | JSONB linking to source materials |
| `teacher_approved, approved_by, approved_at` | HLD-003 | Review workflow |
| `times_used, times_correct` | Both | Same |
| `discrimination_index, difficulty_index` | HLD-003 | V2 psychometrics |
| `language` | HLD-004 | ISO 639-1 |
| `status` | HLD-004 | `active, pending_review, retired, flagged` |
| `created_by, created_at, retired_at` | Merged | Both |

### Rationale

HLD-003's schema is more aligned with the quiz generation prompt output format (key-value options, split explanations). HLD-004 adds question types beyond MCQ and difficulty/language metadata. The merged schema supports both.

### Consequences

- (+) Single canonical quiz table
- (+) Options format matches LLM output format (no transformation needed)
- (-) HLD-004's `content.quiz_question` name is retired; all references must use `content.question_bank`

---

## Conflict 6: `llm_audit_log` Table Missing from HLD-004

### Observation

HLD-001 Section 6.5 defines an `llm_audit_log` table for logging every LLM API call (agent name, model ID, prompt hash, token counts, latency, cache hit). This table is not defined in HLD-004, which provides the complete database DDL.

### Resolution

**Add `audit.llm_audit_log` to the canonical DDL.** HLD-001's definition is adopted with the following placement:

- Schema: `audit` (it is an audit table)
- Partitioning: `PARTITION BY RANGE (timestamp)` -- monthly, same as `audit.audit_log`
- Immutability: same `deny_modify` triggers as other audit tables
- FK: `request_id` correlates to the LangGraph workflow `request_id`

### Rationale

LLM call tracing is a requirement (N7 audit trail, cost tracking). HLD-001 correctly identified this need; HLD-004 omitted it because it falls at the boundary between agent infrastructure and data model.

### Consequences

- (+) Complete audit trail for LLM usage
- (+) Cost tracking (input/output tokens) feeds Grafana dashboards
- (-) Additional table to manage; mitigated by identical partitioning/immutability as other audit tables

---

## Conflict 7: HLD-001 Retention Scheduling Simplification

### Observation

HLD-001 Section 3.3 states: "Retention check result: pass -> `consolidato`" for MVP (single D+7 check). HLD-004 Section 3.4 states: "Pass: Increment `retention_checks_passed`. If `= 1` (MVP D+7 only check) -> transition to `consolidato`." Additionally, HLD-004 defines `retention_checks_passed SMALLINT NOT NULL DEFAULT 0` with comment "0-3 needed for consolidato".

### Resolution

**For MVP, a single retention pass at D+7 transitions to `consolidato`.** The `retention_checks_passed` column and the "3 checks needed" comment in HLD-004 apply to V1 (D+3, D+7, D+21 schedule per ADR-002). Both HLDs are consistent on the MVP behavior; the column is schema-ready for V1 per ADR-004 Decision 6 (FSRS data collection from day 1).

No code change needed. Implementation note: MVP sets `retention_checks_passed = 1` on pass and immediately transitions to `consolidato`. V1 implementation checks against the target count from the retention schedule.

### Consequences

- (+) Schema is V1-ready
- (+) MVP behavior is clear and simple

---

## Summary

| # | Conflict | Resolution |
|---|---|---|
| 1 | Table naming | HLD-004 schema-qualified names canonical; add `kg` schema for HLD-002 tables |
| 2 | `users` table | Does not exist; use `core.teacher` for KG-authoring FKs |
| 3 | State ordering | HLD-002 ordering adopted: `lacuna(0) < in_recupero(1) < non_introdotto(2) < introdotto(3) < da_consolidare(4) < consolidato(5)` |
| 4 | `generated_content` schema | HLD-004 canonical + HLD-002 additions (`node_type`, `embedding`, `content_inline`) |
| 5 | Question bank | `content.question_bank` canonical name; merged schema from HLD-003 and HLD-004 |
| 6 | `llm_audit_log` missing | Add to HLD-004 DDL as `audit.llm_audit_log` |
| 7 | Retention scheduling | Consistent; MVP = 1 pass -> consolidato; V1 = 3 passes |

---

*Ratified by MSTR-02 (CTA). CPA co-sign on Conflict 3 (state ordering -- pedagogically-touching). Filed per CLAUDE.md governance rules.*
