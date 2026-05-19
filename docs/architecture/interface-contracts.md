# MAESTRO -- Cross-Component Interface Contracts

**Status**: Ratified
**Date**: 2026-05-18
**Author**: MSTR-02 (Chief Technical Architect)
**Reviewers**: MSTR-03 (CPA), MSTR-04 (Agent Architect), MSTR-05 (KG Architect), MSTR-06 (Content Architect), MSTR-07 (Data Architect), MSTR-20 (QA Sentinel)
**Task**: T2.5
**Related**: ADR-005 (Interface Resolution), HLD-001 through HLD-004

---

## 1. Purpose

This document defines every cross-component interface in MAESTRO -- the data structures, protocols, and contracts that two or more HLD components share. Each contract is concrete enough for implementation: typed schemas, endpoint signatures, event payloads.

All table names use the canonical schema-qualified names per ADR-005.

---

## 2. Component Boundaries

```
                         +-----------------------+
                         |   FastAPI REST/WS     |
                         |   (External API)      |
                         +----------+------------+
                                    |
                         +----------v------------+
                         |     Orchestrator      |
                         |   (LangGraph Graph)   |
                         +----------+------------+
                                    |
        +----------+--------+------+------+--------+----------+
        |          |        |             |        |          |
   +----v---+ +---v----+ +-v----------+ +v------+ +v-------+ +v---------+
   |Identity| |  KMM   | |Curriculum  | |Diag.  | |Content | |Safeguard.|
   |&Consent| |        | |Ingestion   | |Agent  | |Orch.   | |Agent     |
   +--------+ +----+---+ +-----+------+ +---+---+ +---+----+ +----------+
                   |            |             |        |
              +----v---+   +---v-----+       |   +----v----+
              |  AGE   |   |pgvector |       |   |Text Agt.|
              |  Graph |   |Embeddings|      |   |Bilingual|
              +--------+   +---------+       |   +---------+
                                             |
                                        +----v----+
                                        | Feedback|
                                        |  Loop   |
                                        +---------+
```

The contracts below are organised by the interface boundary between producer and consumer.

---

## 3. Contract IC-01: Orchestrator <-> All Agents (State Protocol)

**Source**: HLD-001 Section 2.3, Section 4.1
**Protocol**: LangGraph shared state (`MaestroState` TypedDict)
**Direction**: Bidirectional (orchestrator passes state to agent; agent returns updated state)

### 3.1 MaestroState Schema

```python
from typing import TypedDict, Optional, Literal
from datetime import datetime

class MaestroState(TypedDict):
    # --- Request context (set by Orchestrator) ---
    request_id: str                    # UUID, correlation ID for all tracing
    request_type: Literal[
        "lesson_upload", "verification_analysis", "gap_closure",
        "onboarding", "content_generation", "retention_check",
        "profile_update", "teacher_override", "course_setup"
    ]
    timestamp: datetime

    # --- Identity (resolved by consent_gate node) ---
    student_pseudo_id: str             # Pseudonymised ID for LLM calls
    student_internal_id: str           # Internal DB UUID, NEVER sent to LLM
    course_id: str
    active_consents: list[str]         # Subset of ["a", "b", "c", "d", "e"]

    # --- KG context (populated by KG queries) ---
    target_node_ids: list[str]         # Micro-node IDs being operated on
    kg_context: dict                   # {prerequisites: [...], siblings: [...], macro_parent: ...}

    # --- Content adaptation profile (ADR-002) ---
    content_profile: dict              # {visuale, audio, pratico, lettura, dialogo, tone, length}

    # --- Agent outputs (accumulated during graph execution) ---
    diagnostic_result: Optional[dict]
    generated_content: Optional[dict]
    safeguarding_verdict: Optional[dict]
    kmm_transitions: list[dict]        # [{node_id, prev_state, new_state, trigger_type}]
    feedback_actions: list[dict]

    # --- Audit ---
    agent_trace: list[dict]            # [{agent, action, timestamp, checkpoint_id}]
    llm_calls: list[dict]              # [{model, prompt_hash, token_count, latency_ms}]

    # --- Error handling ---
    errors: list[dict]
    fallback_activated: bool
```

### 3.2 Agent Node Contract

Every agent is a pure function with this signature:

```python
def agent_node(state: MaestroState) -> dict:
    """
    Receives full state, returns a dict with ONLY the keys it modifies.
    LangGraph merges the returned dict into the state.
    """
    # Example: KMM agent
    return {
        "kmm_transitions": [...],
        "agent_trace": state["agent_trace"] + [{"agent": "kmm", ...}],
    }
```

### 3.3 Invariants

- Agents MUST NOT modify keys they do not own (see ownership table below)
- Agents MUST append to `agent_trace` on every invocation
- Agents that call LLMs MUST append to `llm_calls`
- `student_internal_id` MUST NEVER appear in any LLM prompt or external API call

### 3.4 State Key Ownership

| Key | Owner (writes) | Readers |
|---|---|---|
| `request_id`, `request_type`, `timestamp` | Orchestrator | All |
| `student_pseudo_id`, `student_internal_id`, `active_consents` | Identity & Consent Manager | All |
| `course_id` | Orchestrator | All |
| `target_node_ids`, `kg_context` | Diagnostic Agent, Curriculum Ingestion | Content Orchestrator, KMM, Text Agent |
| `content_profile` | Student Profiler | Content Orchestrator, Text Agent, Bilingual Composer |
| `diagnostic_result` | Diagnostic Agent | Orchestrator, KMM, Content Orchestrator |
| `generated_content` | Content Orchestrator | Safeguarding Agent, Feedback Loop |
| `safeguarding_verdict` | Safeguarding Agent | Orchestrator |
| `kmm_transitions` | KMM | Feedback Loop, Orchestrator |
| `feedback_actions` | Feedback Loop | Orchestrator |
| `agent_trace`, `llm_calls` | All agents (append-only) | Audit system |
| `errors`, `fallback_activated` | Any agent (on error) | Orchestrator |

---

## 4. Contract IC-02: Identity & Consent Manager <-> All Components

**Source**: HLD-001 Section 3.2, HLD-004 Section 4
**Protocol**: Internal Python function call (within LangGraph graph)
**Direction**: Request/Response

### 4.1 Consent Verification Request

```python
class ConsentVerificationRequest:
    student_internal_id: str           # UUID
    request_type: str                  # Maps to consent matrix
    required_consents: list[str]       # ["a", "b"] etc.
```

### 4.2 Consent Verification Response

```python
class ConsentVerification:
    student_pseudo_id: str             # Pseudonymised ID for downstream use
    active_consents: list[str]         # Currently active consent types
    consent_valid: bool                # True if all required consents are active
    missing_consents: list[str]        # Consents required but not granted
    degraded_mode: bool                # True if operating without optional consents
```

### 4.3 Consent Matrix (canonical)

| Request type | Required consents | Degraded behavior if missing |
|---|---|---|
| `lesson_upload` | None | N/A (teacher operation) |
| `verification_analysis` | None | N/A (teacher triggers) |
| `content_generation` (text) | (a) if profile-adapted | Uniform profile (20% each) |
| `content_generation` (bilingual) | (a) + (b) | Monolingual output |
| `gap_closure` | (a) if profile-adapted | Uniform profile |
| `onboarding` | (a) | Skip quiz, uniform profile |
| `retention_check` | None | N/A |
| `family_report` | (c) | Report not generated |
| `cross_year_history` | (d) | History not carried over |
| `research_analytics` | (e) | Student excluded from aggregates |

### 4.4 Database Tables

- `core.student` -- identity + PII (encrypted)
- `core.consent` -- 5 granular consent rows per student
- `core.consent_history` -- append-only consent change log

---

## 5. Contract IC-03: KG Service <-> KMM

**Source**: HLD-002 Sections 2, 7.2; HLD-004 Section 3.5
**Protocol**: Internal Python service calls
**Direction**: Bidirectional

### 5.1 KG -> KMM: Node Structure for Rollup

The KMM needs the macro-micro hierarchy to compute rollup state.

```python
class MacroMicroStructure:
    macro_node_id: str                 # UUID
    macro_label_it: str
    micro_node_ids: list[str]          # UUIDs of active child micro-nodes

async def get_macro_structure(course_id: str) -> list[MacroMicroStructure]:
    """Returns all macro nodes with their active micro children for a course."""
```

### 5.2 KG -> KMM: New Node Cascade

When a new node is added to the KG, all enrolled students need a `non_introdotto` state record.

```python
class NodeAddedEvent:
    node_id: str
    node_type: Literal["macro", "micro"]
    course_id: str
    macro_parent_id: Optional[str]     # Set for micro nodes

async def initialize_states_for_node(event: NodeAddedEvent) -> int:
    """
    Creates kmm.student_node_state records for all enrolled students.
    Returns count of records created.
    Called within the same transaction as node creation (HLD-002 dual-write).
    """
```

### 5.3 KMM -> KG: Rollup Computation

```python
# Canonical state ordering per ADR-005, Conflict 3
STATE_ORDER = {
    'lacuna': 0,
    'in_recupero': 1,
    'non_introdotto': 2,
    'introdotto': 3,
    'da_consolidare': 4,
    'consolidato': 5,
}

class MacroRollupResult:
    macro_node_id: str
    worst_state: str                   # Worst state among active micro children
    total_micros: int
    micros_per_state: dict[str, int]   # {"consolidato": 7, "lacuna": 1, ...}

async def compute_macro_rollup(
    student_id: str,
    course_id: str,
    structure: list[MacroMicroStructure],
) -> list[MacroRollupResult]:
    """
    Computes macro state for each macro node.
    Uses STATE_ORDER (ADR-005) for worst-state determination.
    """
```

### 5.4 Database Boundary

- KG reads: `kg.node`, `kg.edge` (shadow tables), Apache AGE graph
- KMM reads/writes: `kmm.student_node_state`, `kmm.state_transition_log`
- Shared FK: `node_id` (TEXT, stable UUID from AGE)

---

## 6. Contract IC-04: Diagnostic Agent <-> KMM

**Source**: HLD-001 Section 3.6; HLD-004 Section 3.3
**Protocol**: Internal Python service calls (within LangGraph graph)
**Direction**: Diagnostic -> KMM

### 6.1 KMM Transition Request

```python
class KMMTransitionRequest:
    student_id: str                    # Internal UUID
    node_id: str                       # Micro-node UUID
    course_id: str
    trigger_type: Literal[
        "verifica_errore", "avvio_recupero", "quiz_superato",
        "quiz_fallito", "retention_check_ok", "retention_check_fail",
        "regressione", "override_docente", "lezione_completata",
        "inizializzazione"
    ]
    evidence_ref: Optional[str]        # S3 path or UUID of triggering entity
    quiz_score: Optional[int]          # 0-100, for quiz-related triggers
    response_time_ms: Optional[int]    # For FSRS data collection (V1+)
    override_motivation: Optional[str] # Min 20 chars, for override_docente only
```

### 6.2 KMM Transition Result

```python
class KMMTransitionResult:
    node_id: str
    previous_state: str
    new_state: str
    transition_id: int                 # ID in state_transition_log
    retention_check_scheduled: Optional[str]  # ISO-8601 if da_consolidare
    macro_rollup_changed: bool         # True if parent macro state changed
```

### 6.3 Bulk Transition (Verification Flow)

```python
async def bulk_transition(
    transitions: list[KMMTransitionRequest],
) -> list[KMMTransitionResult]:
    """
    Atomic: all transitions in a single database transaction.
    If any transition is invalid, the entire batch is rejected.
    """
```

### 6.4 Legal Transitions (Application-Level Enforcement)

```python
LEGAL_TRANSITIONS = {
    'non_introdotto': {'introdotto'},
    'introdotto':     {'lacuna'},
    'lacuna':         {'in_recupero'},
    'in_recupero':    {'da_consolidare', 'in_recupero', 'lacuna'},
    'da_consolidare': {'consolidato', 'da_consolidare', 'lacuna'},
    'consolidato':    {'lacuna'},
}
# override_docente bypasses this table; requires motivation + audit
```

---

## 7. Contract IC-05: KMM <-> Content Orchestrator

**Source**: HLD-001 Section 3.7; HLD-003 Section 2
**Protocol**: Internal (within LangGraph graph, via `MaestroState`)
**Direction**: KMM transitions trigger content generation

### 7.1 Content Trigger Conditions

| KMM event | Content action |
|---|---|
| `introdotto -> lacuna` (verifica_errore) | Generate review document (F5) |
| `lacuna -> in_recupero` (avvio_recupero) | Generate remediation content (F11.7) |
| `in_recupero -> in_recupero` (quiz_fallito, 50-79%) | Generate varied remediation (different approach) |
| `da_consolidare` (retention check due) | Generate retention check quiz |
| None (teacher request) | Generate ad-hoc content |

### 7.2 ContentRequest Schema

```python
class TargetNode:
    node_id: str
    node_type: Literal["macro", "micro"]
    current_state: str
    error_description: Optional[str]   # From diagnostic agent

class BilingualConfig:
    active: bool                       # True if consent (b) granted and language set
    language_code: Optional[str]       # ISO 639-1: "uk", "ar", etc.

class ContentRequest:
    request_id: str                    # UUID, correlation ID
    request_type: Literal[
        "review_document", "gap_closure", "quiz_generation", "retention_check"
    ]
    student_pseudo_id: str             # Pseudonymised
    course_id: str
    course_language: str               # "it" for MVP
    target_nodes: list[TargetNode]
    content_profile: ContentAdaptationProfile
    bilingual: BilingualConfig
    attempt_number: int                # 1 = first, 2+ = retry with variation
    teacher_question_bank_ids: list[str]  # Pre-approved quiz IDs for these nodes
    source_materials: list[SourceMaterial]  # RAG-retrieved, priority-ordered
```

### 7.3 ContentResponse Schema

```python
class ContentMetadata:
    model_id: str                      # e.g., "claude-opus-4-20250514"
    prompt_template_id: str
    prompt_template_version: int
    prompt_hash: str                   # SHA-256
    input_tokens: int
    output_tokens: int
    latency_ms: int
    sources_used: list[SourceRef]      # [{material_id, chunk_id, tier}]
    cache_hit: bool
    generated_at: str                  # ISO-8601

class ContentResponse:
    request_id: str
    channel: str                       # "text", "quiz", "audio", etc.
    content: dict                      # Channel-specific payload (JSON)
    metadata: ContentMetadata
```

---

## 8. Contract IC-06: Content Orchestrator <-> Text Agent

**Source**: HLD-003 Section 3; HLD-001 Section 3.8
**Protocol**: Internal Python function call
**Direction**: Content Orchestrator -> Text Agent -> Content Orchestrator

### 8.1 Text Generation Input

The Text Agent receives the full `ContentRequest` plus resolved source materials. The prompt is constructed using the three-layer architecture (system/context/task) defined in HLD-003 Section 3.1.

### 8.2 Text Output: Review Document (F5)

```json
{
  "blocks": [
    {
      "concept_node_id": "uuid",
      "concept_label": "string",
      "il_tuo_errore": {
        "text": "markdown string",
        "code_errato": "string | null",
        "analogy_domain": "string"
      },
      "perche_succede": {
        "text": "markdown string",
        "source_refs": ["material_id:chunk_id"]
      },
      "come_si_fa_giusto": {
        "text": "markdown string",
        "code_corretto": "string | null",
        "source_refs": ["material_id:chunk_id"]
      },
      "ricordati": {
        "text": "string (max 100 words)",
        "mnemonic": "string | null"
      }
    }
  ],
  "summary": "string (2-3 sentence encouraging summary)"
}
```

### 8.3 Text Output: Remediation Path (F11.7)

```json
{
  "concept_node_id": "uuid",
  "concept_label": "string",
  "aggancio": { "text": "markdown" },
  "spiegazione": { "text": "markdown", "source_refs": ["..."] },
  "esempio_pratico": { "text": "markdown", "code": "string | null", "language": "string | null" },
  "verifica_veloce": { "question": "string", "hint": "string" },
  "prossimo_passo": { "text": "string" }
}
```

### 8.4 Frontend Rendering Contract

| JSON field | Frontend rendering |
|---|---|
| `code_errato` | Yellow border (#FDD835), label "ERRATO" |
| `code_corretto` | Green border (#43A047), label "CORRETTO" |
| Code blocks | Syntax-highlighted; desktop: side-by-side; mobile: stacked |
| Labels "ERRATO"/"CORRETTO" | Always text, never color-only (WCAG 2.1 AA, F9.3) |

---

## 9. Contract IC-07: Content Orchestrator <-> Bilingual Composer

**Source**: HLD-003 Section 4; HLD-001 Section 3.9
**Protocol**: Internal Python function call
**Direction**: Content Orchestrator -> Bilingual Composer -> Content Orchestrator
**Precondition**: Consent (b) active AND `bilingual.language_code` set

### 9.1 Input

```python
class BilingualRequest:
    content: dict                      # Original content JSON (review doc or remediation)
    source_language: str               # "it" (course language)
    target_language: str               # "uk", "ar"
    glossary: list[GlossaryTerm]       # From content.bilingual_glossary
```

### 9.2 Output

```json
{
  "layout": "dual_column",
  "columns": {
    "left": { "language": "it", "label": "Italiano" },
    "right": { "language": "uk", "label": "..." }
  },
  "blocks": [
    {
      "concept_node_id": "...",
      "sections": {
        "il_tuo_errore": {
          "left": "original Italian text",
          "right": "translated text",
          "technical_terms": [
            {"left": "sessione", "right": "..."}
          ]
        }
      }
    }
  ],
  "glossary_used": ["sessione", "variabile"],
  "culturally_adapted_flags": [
    {"block_index": 0, "section": "perche_succede", "adapted": true}
  ]
}
```

### 9.3 Invariants

- Code blocks are NEVER translated
- Official language column is ALWAYS visible (F13.8)
- Technical terms follow controlled glossary from `content.bilingual_glossary`
- Native language referenced by ISO code only in LLM prompts, never associated with student identity

---

## 10. Contract IC-08: Content Pipeline <-> Safeguarding Agent

**Source**: HLD-001 Section 3.10, Section 7; HLD-003 Section 5.2 (Layer 4)
**Protocol**: Internal Python function call (mandatory graph node)
**Direction**: Any content agent -> Safeguarding Agent -> Orchestrator
**Structural guarantee**: No graph edge connects content generation to student delivery without passing through `safeguarding_gate`

### 10.1 Safeguarding Request

```python
class SafeguardingRequest:
    content: dict                      # Content JSON payload
    content_type: Literal[
        "review_document", "remediation_path", "quiz",
        "podcast_script", "visual_diagram", "quest_description",
        "dialog_response"
    ]
    target_audience_age_range: tuple[int, int]  # (13, 19)
    context: dict                      # {student_pseudo_id, concept_domain}
```

### 10.2 Safeguarding Verdict

```python
class SafeguardingIssue:
    category: Literal[
        "offensive_language", "age_inappropriate", "stereotype",
        "student_comparison", "manipulative_pattern", "punitive_tone",
        "wellbeing_concern", "factual_concern"
    ]
    severity: Literal["BLOCK", "WARN", "ALERT", "PASS_WITH_FLAG"]
    description: str
    location: str                      # JSON path to problematic content

class SafeguardingVerdict:
    safe: bool
    issues: list[SafeguardingIssue]
    modified_content: Optional[dict]   # Auto-corrected content (for WARN)
    wellbeing_alert: Optional[dict]    # {type, recommended_action}
```

### 10.3 Flow Control

| Verdict | Action |
|---|---|
| `safe = True`, no issues | Deliver to student |
| `safe = False`, BLOCK issues | Regenerate with modified prompt (max 2 retries). If retries exhausted: alert teacher, serve fallback. |
| `safe = True`, ALERT issues | Deliver content. Alert teacher + school referent. |
| `safe = True`, PASS_WITH_FLAG | Deliver content. Queue for teacher review. |

---

## 11. Contract IC-09: Quiz Engine <-> KMM (Feedback Loop)

**Source**: HLD-003 Section 5; HLD-001 Section 3.11; HLD-004 Section 3.3
**Protocol**: Internal (within LangGraph graph)
**Direction**: Student quiz submission -> Feedback Loop -> KMM transition

### 11.1 Quiz Result

```python
class QuizResult:
    student_id: str                    # Internal UUID
    course_id: str
    node_id: str                       # Micro-node
    quiz_id: str
    score: int                         # 0-100 (percentage correct)
    total_questions: int
    correct_count: int
    response_time_ms: int              # Total time (for FSRS, V1+)
    per_question: list[QuestionResult] # [{question_id, selected, correct, time_ms}]
```

### 11.2 Transition Logic (Application Layer)

```python
def determine_transition(
    current_state: str,
    quiz_result: QuizResult,
    quiz_purpose: Literal["closure", "retention"],
) -> KMMTransitionRequest:
    if quiz_purpose == "closure":
        if quiz_result.score >= 80:
            return KMMTransitionRequest(trigger_type="quiz_superato", ...)
        elif quiz_result.score >= 50:
            return KMMTransitionRequest(trigger_type="quiz_fallito", ...)
            # Stay in_recupero, attempt++
        else:
            return KMMTransitionRequest(trigger_type="quiz_fallito", ...)
            # Regress to lacuna, alert teacher

    elif quiz_purpose == "retention":
        if quiz_result.score >= 80:
            return KMMTransitionRequest(trigger_type="retention_check_ok", ...)
        else:
            return KMMTransitionRequest(trigger_type="retention_check_fail", ...)
            # Regress to lacuna
```

---

## 12. Contract IC-10: Curriculum Ingestion <-> KG + Vector Store

**Source**: HLD-002 Sections 3, 4; HLD-001 Section 3.4
**Protocol**: Internal Python service calls
**Direction**: Curriculum Ingestion Agent -> KG Service + pgvector

### 12.1 Ingestion Pipeline Output

```python
class IngestionResult:
    material_id: str                   # UUID in content.lesson_material
    transcription_id: Optional[str]    # UUID in content.lesson_transcript (audio/video)
    concept_mappings: list[ConceptMapping]
    vector_ids: list[str]              # UUIDs of indexed chunks in content.lesson_chunk
    coverage_gaps: list[str]           # Node IDs with insufficient coverage

class ConceptMapping:
    chunk_id: str
    node_id: str
    node_type: Literal["macro", "micro"]
    confidence_score: float            # 0.0-1.0 composite
    auto_suggested: bool               # True if >= 0.80 confidence
    start_ms: Optional[int]            # For audio/video
    end_ms: Optional[int]
```

### 12.2 Vector Storage Contract

Chunks stored in `content.lesson_chunk` (canonical name per ADR-005):

| Column | Type | Source |
|---|---|---|
| `id` | UUID | Generated |
| `material_id` | UUID FK | `content.lesson_material` |
| `course_id` | UUID FK | `core.course` |
| `chunk_index` | INT | Sequential within material |
| `content` | TEXT | Extracted text |
| `embedding` | vector(1536) | OpenAI text-embedding-3-small |
| `metadata` | JSONB | {page, slide, start_ms, end_ms, speaker_id, section_heading} |

### 12.3 Retrieval Interface

```python
class SourceMaterial:
    material_id: str
    chunk_id: str
    content: str
    material_type: str                 # "lesson", "textbook", "exercise", etc.
    tier: int                          # 1=teacher, 2=textbook, 3=exercise, 4=external
    similarity: float                  # Cosine similarity score
    metadata: dict

async def retrieve_sources(
    course_id: str,
    node_ids: list[str],
    query_embedding: list[float],
    top_k: int = 10,
    similarity_threshold: float = 0.70,
) -> list[SourceMaterial]:
    """
    Returns source materials ordered by authorial priority (tier),
    then by similarity within tier.
    """
```

---

## 13. Contract IC-11: LLM Gateway <-> All LLM-Using Agents

**Source**: HLD-001 Section 6; HLD-004 Section 8
**Protocol**: Internal Python module call
**Direction**: Agent -> LLMGateway -> External LLM API -> Agent

### 13.1 LLM Call Request

```python
class LLMRequest:
    agent_name: str                    # Calling agent identifier
    model_preference: Literal["quality", "cost_optimized"]
    prompt_template_id: str            # e.g., "text_review_document_v1"
    prompt_template_version: int
    system_prompt: str
    context_block: str
    task_block: str
    max_tokens: int
    temperature: float                 # 0.0-1.0
    response_format: Literal["json", "text"]
    correlation_id: str                # request_id from MaestroState
```

### 13.2 LLM Call Response

```python
class LLMResponse:
    content: str                       # LLM output (de-pseudonymised)
    model_id: str                      # Actual model used
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cache_hit: bool
    prompt_hash: str                   # SHA-256 of pseudonymised prompt
```

### 13.3 Model Routing Table

| `model_preference` | Primary | Fallback | Use cases |
|---|---|---|---|
| `quality` | Claude | GPT-4o-mini | Content generation, quiz, bilingual, safeguarding |
| `cost_optimized` | GPT-4o-mini | Claude | Concept extraction, score-based mapping, quest text |

### 13.4 Pseudonymisation Contract

| Data type | Pseudonym format | Reversible |
|---|---|---|
| Student name | `STUDENT_{hash_6}` | Yes (session-scoped) |
| Teacher name | `TEACHER_{hash_6}` | Yes (session-scoped) |
| School name | `SCHOOL_{id}` | Yes (session-scoped) |
| Native language | ISO 639-1 code only | N/A (not PII in prompt) |
| Email, phone, birth year | Stripped entirely | N/A |

Session-scoped mapping: in-memory only, never persisted, destroyed after LLM call completes.

### 13.5 Audit Log Entry

Every LLM call produces a record in `audit.llm_audit_log`:

```sql
-- Canonical DDL (added per ADR-005 Conflict 6)
CREATE TABLE audit.llm_audit_log (
    id              BIGINT GENERATED ALWAYS AS IDENTITY,
    request_id      UUID        NOT NULL,
    agent_name      TEXT        NOT NULL,
    model_id        TEXT        NOT NULL,
    prompt_hash     TEXT        NOT NULL,
    input_tokens    INTEGER     NOT NULL,
    output_tokens   INTEGER     NOT NULL,
    latency_ms      INTEGER     NOT NULL,
    cache_hit       BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT pk_llm_audit PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE INDEX idx_llm_audit_request ON audit.llm_audit_log (request_id);
CREATE INDEX idx_llm_audit_created_brin ON audit.llm_audit_log
    USING BRIN (created_at) WITH (pages_per_range = 32);

CREATE TRIGGER trg_llm_audit_no_update
    BEFORE UPDATE ON audit.llm_audit_log
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();
CREATE TRIGGER trg_llm_audit_no_delete
    BEFORE DELETE ON audit.llm_audit_log
    FOR EACH ROW EXECUTE FUNCTION audit.deny_modify();
```

---

## 14. Contract IC-12: Frontend <-> Backend (External API)

**Source**: HLD-001 Section 5 (flows); HLD-002 Section 9 (KG API); HLD-004 (data model)
**Protocol**: REST (JSON over HTTPS) + WebSocket (real-time updates)
**Auth**: Keycloak JWT (Bearer token)

### 14.1 API Versioning

All endpoints under `/api/v1/`. Version increment on breaking changes only.

### 14.2 Response Envelope

```json
{
  "data": { "..." },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO-8601"
  }
}
```

### 14.3 Error Response

```json
{
  "error": {
    "code": "MACHINE_READABLE_CODE",
    "message": "Human-readable message in Italian",
    "details": { "..." }
  },
  "meta": { "..." }
}
```

### 14.4 Key Endpoint Groups

**Student API:**

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/students/{id}/knowledge-map` | Student's full KMM state (macro + micro) |
| `GET` | `/api/v1/students/{id}/missions` | Active recovery missions |
| `POST` | `/api/v1/students/{id}/missions/{nodeId}/start` | Start gap closure cycle |
| `GET` | `/api/v1/students/{id}/content/{contentId}` | Retrieve generated content |
| `POST` | `/api/v1/students/{id}/quizzes/{quizId}/submit` | Submit quiz answers |
| `GET` | `/api/v1/students/{id}/retention-checks` | Due retention checks |
| `GET` | `/api/v1/students/{id}/notifications` | Student notifications |
| `GET` | `/api/v1/students/{id}/profile` | Content-adaptation profile |
| `PUT` | `/api/v1/students/{id}/profile` | Manual profile override (F3.4) |

**Teacher API:**

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/courses/{id}/class-heatmap` | Class knowledge map heatmap (F11.14) |
| `POST` | `/api/v1/courses/{id}/verifications` | Submit graded verification |
| `GET` | `/api/v1/courses/{id}/verifications/{id}/transitions` | Transition preview |
| `POST` | `/api/v1/courses/{id}/verifications/{id}/transitions/confirm` | Confirm transitions |
| `POST` | `/api/v1/courses/{id}/overrides` | Teacher override (F11.12) |
| `GET` | `/api/v1/courses/{id}/overrides` | Override history |
| `POST` | `/api/v1/courses/{id}/lessons` | Upload lesson material |
| `GET` | `/api/v1/courses/{id}/coverage` | Curriculum coverage report |
| `GET` | `/api/v1/courses/{id}/materials/{id}/mappings` | Concept mappings for review |
| `POST` | `/api/v1/courses/{id}/materials/{id}/mappings` | Confirm/reject mappings |

**KG API (from HLD-002 Section 9):**

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/courses/{id}/kg/nodes` | All active nodes |
| `GET` | `/api/v1/courses/{id}/kg/nodes/macro` | Macro nodes only |
| `POST` | `/api/v1/courses/{id}/kg/nodes` | Create node |
| `PUT` | `/api/v1/courses/{id}/kg/nodes/{id}` | Update node |
| `DELETE` | `/api/v1/courses/{id}/kg/nodes/{id}` | Deactivate node |
| `POST` | `/api/v1/courses/{id}/kg/edges` | Create edge (DAG validated) |
| `DELETE` | `/api/v1/courses/{id}/kg/edges/{id}` | Remove edge |
| `POST` | `/api/v1/courses/{id}/retrieve` | Semantic search (internal) |

**Admin API:**

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/students` | Create student account (F14.2) |
| `POST` | `/api/v1/students/{id}/consent` | Record consent (F14.3) |
| `POST` | `/api/v1/students/{id}/enrol` | Enrol in course |
| `POST` | `/api/v1/students/{id}/erasure` | Right to erasure (F14.9) |

### 14.5 WebSocket Events

Connection: `wss://api.maestro.example/ws?token={jwt}`

| Event | Direction | Payload |
|---|---|---|
| `content.ready` | Server -> Client | `{content_id, content_type, node_id}` |
| `notification.new` | Server -> Client | `{notification_id, type, title}` |
| `transition.preview` | Server -> Client | `{verification_id, transitions: [...]}` |
| `processing.status` | Server -> Client | `{task_id, status, progress_pct}` |

---

## 15. Contract IC-13: Async Event Bus (Redis Streams)

**Source**: HLD-001 Section 4.3
**Protocol**: Redis Streams (`maestro:events`)
**Direction**: Publisher -> Redis Stream -> Subscriber(s)

### 15.1 Event Schema

```python
class MaestroEvent:
    event_id: str                      # UUID
    event_type: str                    # e.g., "kmm.transition", "content.generated"
    timestamp: str                     # ISO-8601
    source_agent: str
    target_agent: Optional[str]        # None = broadcast
    payload: dict
    correlation_id: str                # Links to originating request_id
    trace_id: str                      # OpenTelemetry trace ID
```

### 15.2 Event Types

| Event type | Publisher | Subscribers | Purpose |
|---|---|---|---|
| `kmm.transition` | KMM | Notification service, Analytics | State change occurred |
| `content.generated` | Content Orchestrator | Notification service | New content ready |
| `content.safeguarding_blocked` | Safeguarding Agent | Teacher notification | Content blocked |
| `ingestion.complete` | Curriculum Ingestion | Content regeneration service | New material indexed |
| `quiz.submitted` | Feedback Loop | Analytics | Quiz result |
| `wellbeing.alert` | Safeguarding Agent | Teacher notification, School referent | Wellbeing concern |

---

## 16. Contract IC-14: Database Schema Registry

This section provides the complete, authoritative list of tables across all schemas after ADR-005 conflict resolution.

### 16.1 Schema: `core`

| Table | Owner HLD | Purpose |
|---|---|---|
| `core.school` | HLD-004 | School entities |
| `core.teacher` | HLD-004 | Teacher identity (PII encrypted) |
| `core.student` | HLD-004 | Student identity (PII encrypted) |
| `core.course` | HLD-004 | Course definitions |
| `core.enrolment` | HLD-004 | Student-course enrollment |
| `core.consent` | HLD-004 | 5 granular consents per student |
| `core.consent_history` | HLD-004 | Append-only consent change log |
| `core.notification` | HLD-004 | Notifications for all recipient types |
| `core.notification_preference` | HLD-004 | Teacher notification preferences |

### 16.2 Schema: `kmm`

| Table | Owner HLD | Purpose |
|---|---|---|
| `kmm.student_node_state` | HLD-004 | Current mastery state per (student, node, course) |
| `kmm.state_transition_log` | HLD-004 | Append-only transition history (partitioned monthly) |
| `kmm.retention_schedule` | HLD-004 | Scheduled retention checks (V1, schema present from MVP) |
| `kmm.teacher_override` | HLD-004 | Override records with motivation |

### 16.3 Schema: `content`

| Table | Owner HLD | Purpose |
|---|---|---|
| `content.generated_content` | HLD-004 + HLD-002 amendments | Generated content metadata + inline payload |
| `content.question_bank` | HLD-003 (canonical name per ADR-005) | Quiz question repository |
| `content.bilingual_glossary` | HLD-003 | Technical term translations per language |
| `content.lesson_material` | HLD-002 | Uploaded lesson files metadata |
| `content.lesson_transcript` | HLD-002 | Audio/video transcripts |
| `content.lesson_chunk` | HLD-002 | Text chunks with embeddings (pgvector) |
| `content.prompt_template` | HLD-003 | Versioned prompt templates (V1; MVP uses code) |

### 16.4 Schema: `kg`

| Table | Owner HLD | Purpose |
|---|---|---|
| `kg.node` | HLD-002 | Relational shadow of AGE vertices |
| `kg.edge` | HLD-002 | Relational shadow of AGE edges |
| `kg.node_embedding` | HLD-002 | Node embeddings for concept mapping |
| `kg.concept_node_link` | HLD-002 | Confirmed lesson-to-node mappings |
| `kg.error_node_mapping` | HLD-002 | Error-to-micronode mappings from diagnostics |
| `kg.course_granularity_override` | HLD-002 | Teacher granularity overrides per course |

### 16.5 Schema: `audit`

| Table | Owner HLD | Purpose |
|---|---|---|
| `audit.audit_log` | HLD-004 | Universal audit log (partitioned monthly) |
| `audit.llm_audit_log` | HLD-001 (added per ADR-005) | LLM call audit (partitioned monthly) |
| `audit.deletion_certificate` | HLD-004 | Right-to-erasure certificates |

### 16.6 Apache AGE Graph: `maestro_kg`

| Vertex Label | Edge Label | Source HLD |
|---|---|---|
| `MacroNode` | `PREREQUISITE`, `PARENT_OF`, `RELATED_TO` | HLD-002 |
| `MicroNode` | `PREREQUISITE`, `PARENT_OF`, `RELATED_TO` | HLD-002 |

---

## 17. Cross-Cutting Concerns

### 17.1 Tracing

Every request gets an OpenTelemetry trace ID at the API boundary. This trace ID propagates through:
- LangGraph state (`MaestroState.agent_trace`)
- LLM audit log (`correlation_id`)
- Redis events (`trace_id`)
- Database operations (PostgreSQL `application_name` set to `maestro:{trace_id}`)

### 17.2 Error Codes

Standardised error codes across all components:

| Code | HTTP Status | Meaning |
|---|---|---|
| `CONSENT_MISSING` | 403 | Required consent not granted |
| `CONSENT_REVOKED` | 403 | Consent was revoked |
| `STUDENT_NOT_FOUND` | 404 | Student ID not found or deleted |
| `NODE_NOT_FOUND` | 404 | KG node ID not found or inactive |
| `DAG_CYCLE_DETECTED` | 422 | Prerequisite edge would create cycle |
| `TRANSITION_ILLEGAL` | 422 | KMM state transition not permitted |
| `SAFEGUARDING_BLOCKED` | 422 | Content blocked by safeguarding |
| `OVERRIDE_MOTIVATION_SHORT` | 422 | Override motivation < 20 characters |
| `LLM_UNAVAILABLE` | 503 | All LLM providers down |
| `GENERATION_FAILED` | 502 | Content generation failed after retries |

---

*Ratified by MSTR-02 (CTA). Cross-domain review by MSTR-03 (CPA) on contracts IC-03 (rollup ordering), IC-05 (content triggers), IC-08 (safeguarding). Filed per CLAUDE.md governance rules.*
