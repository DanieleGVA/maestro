# HLD-001: Multi-Agent System Architecture

**Status**: Proposed
**Date**: 2026-05-18
**Author**: MSTR-04 (Agent Systems Architect)
**Reviewers required**: MSTR-02 (CTA), MSTR-03 (CPA), MSTR-20 (QA Sentinel)
**Related ADRs**: ADR-001 (Tech Stack), ADR-002 (Pedagogical Model)
**Task**: T2.1
**Blocked by**: T1.1 (v0.3 requirements), T1.2 (tech stack), T1.3 (pedagogical model)

---

## 1. Overview

### 1.1 Purpose

This document specifies the runtime multi-agent architecture of the MAESTRO product: the orchestrator pattern, per-agent specifications, communication protocols, LLM integration, safeguarding enforcement, error handling, and observability strategy. It is the primary input for MSTR-08 (Backend Engineer) during Phase 4 implementation.

### 1.2 Design Philosophy

MAESTRO's agent system is built on four principles:

1. **Durable execution with audit trail.** Every agent step is checkpointed by LangGraph. Every checkpoint is an audit record. This satisfies N7 (transparency) and F14.10 (audit trail) structurally, not as an afterthought.

2. **Consent gates before computation.** No agent operates on a student's data without the Identity & Consent Manager confirming that the required consents are active. This is enforced at the orchestrator level, not delegated to individual agents.

3. **Safeguarding as a mandatory pipeline stage.** Every content output passes through the Safeguarding Agent before reaching a student. This is not optional, not bypassable, and not dependent on the content type.

4. **Pseudonymisation at the LLM boundary.** No agent sends PII to an external LLM. The LLMGateway service strips PII before prompt construction and re-hydrates pseudonyms in responses. Native language (Art. 9) is never included in LLM prompts -- only language codes.

### 1.3 Tech Stack Context

Per ADR-001:
- **Orchestration**: LangGraph (Python) on FastAPI
- **LLM**: Claude API (primary) + GPT-4o-mini (secondary) via LLMGateway abstraction
- **Storage**: PostgreSQL 17 with Apache AGE (graph), pgvector (embeddings), partitioned tables (KMM transitions, audit log)
- **Auth**: Keycloak (SAML 2.0 + OIDC)
- **Caching**: Redis (deterministic cache, task queues, semantic cache coordination)
- **Observability**: OpenTelemetry + self-hosted Grafana stack

### 1.4 Scope

| Scope | Agents |
|---|---|
| **MVP** | Orchestrator, Curriculum Ingestion Agent, Student Profiler Agent, Diagnostic Agent, Identity & Consent Manager, Knowledge Map Manager, Content Orchestrator, Text Agent, Bilingual Composer, Safeguarding Agent, Feedback Loop Agent |
| **V1** | + Podcast Agent, Game Agent, Visual Agent (stub) |
| **V2** | + Dialog Agent, Visual Agent (full) |

---

## 2. Orchestration Pattern

### 2.1 Architecture Decision: Central Orchestrator via LangGraph StateGraph

**Decision**: Central orchestrator pattern implemented as a LangGraph `StateGraph`, not a peer-to-peer event bus.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| Central orchestrator (StateGraph) | Explicit flow control, durable checkpointing, audit-friendly, human-in-the-loop built-in | Single point of orchestration logic, potential bottleneck |
| Peer-to-peer with event bus | Loose coupling, independent scaling | Hard to enforce sequential consent checks, safeguarding pipeline not guaranteed, audit trail fragmented |
| Hierarchical (sub-orchestrators) | Separation of concerns | Over-engineering for MVP agent count |

**Rationale**: MAESTRO has hard sequencing requirements -- consent must precede processing, safeguarding must follow content generation, KMM transitions must be atomic. A central orchestrator makes these constraints explicit in the graph topology. LangGraph's `StateGraph` provides durable checkpointing, conditional edges, and human-in-the-loop interrupts, all of which map directly to MAESTRO's requirements.

### 2.2 LangGraph Implementation Model

```
StateGraph("maestro_orchestrator")
  |
  +--> [consent_gate]        # Identity & Consent Manager verifies consents
  |         |
  |    (conditional edge: consents valid?)
  |         |
  |    NO --+--> [consent_denied_handler]  --> END
  |         |
  |    YES -+--> [route_intent]            # Classify the incoming request
  |              |
  |         +----+----+----+----+----+
  |         |         |         |         |
  |    [ingest]  [diagnose] [recover] [profile] ...
  |         |         |         |         |
  |         +----+----+----+----+----+
  |              |
  |         [content_orchestrator]         # Coordinates content generation
  |              |
  |         [safeguarding_gate]            # MANDATORY before any student delivery
  |              |
  |         (conditional edge: safe?)
  |              |
  |         NO --+--> [safeguarding_block_handler] --> alert teacher
  |              |
  |         YES -+--> [deliver_to_student]
  |              |
  |         [feedback_loop]                # Update profile, KMM, KG
  |              |
  |         END (checkpoint persisted)
```

### 2.3 State Schema

The LangGraph state object carries the execution context across all nodes:

```python
from typing import TypedDict, Optional, Literal
from datetime import datetime

class MaestroState(TypedDict):
    # Request context
    request_id: str
    request_type: Literal[
        "lesson_upload", "verification_analysis", "gap_closure",
        "onboarding", "content_generation", "retention_check",
        "profile_update", "teacher_override", "course_setup"
    ]
    timestamp: datetime

    # Identity (resolved by consent_gate)
    student_pseudo_id: str          # Pseudonymised ID for LLM calls
    student_internal_id: str        # Internal DB ID, never sent to LLM
    course_id: str
    active_consents: list[str]      # ["a", "b", "c", "d", "e"] subset

    # KG context
    target_node_ids: list[str]      # Micro-node IDs being operated on
    kg_context: dict                # Relevant subgraph (prerequisites, siblings)

    # Content adaptation profile (ADR-002 validated)
    content_profile: dict           # 5-float vector + tone + length preference

    # Agent outputs (accumulated as graph executes)
    diagnostic_result: Optional[dict]
    generated_content: Optional[dict]
    safeguarding_verdict: Optional[dict]
    kmm_transitions: list[dict]
    feedback_actions: list[dict]

    # Audit
    agent_trace: list[dict]         # [{agent, action, timestamp, checkpoint_id}]
    llm_calls: list[dict]           # [{model, prompt_hash, token_count, latency_ms}]

    # Error handling
    errors: list[dict]
    fallback_activated: bool
```

### 2.4 Checkpointing and Durable Execution

LangGraph checkpoints are persisted to PostgreSQL via the `PostgresSaver` checkpointer. Every node execution produces a checkpoint containing:

- The full `MaestroState` at that point
- The node name and execution timestamp
- The LLM calls made (prompt hashes, model version, token counts)

This provides:
- **Audit trail** (N7, F14.10): every decision is traceable to a specific agent, timestamp, and model version
- **Resumability**: if the system fails mid-execution, the workflow resumes from the last checkpoint
- **Replayability**: for debugging and pedagogical review, any workflow can be replayed from any checkpoint

Checkpoint retention policy: 90 days for active students, 30 days post-erasure (pseudonymised).

### 2.5 Human-in-the-Loop Integration

LangGraph's `interrupt_before` and `interrupt_after` mechanisms are used for:

| Flow | Interrupt point | Human actor | Purpose |
|---|---|---|---|
| Lesson upload (F2.4) | After concept mapping | Teacher | Validate auto-extracted concept-to-KG mapping |
| Verification analysis (F4.2) | After error-to-concept mapping | Teacher | Confirm mappings with confidence <80% |
| Verification analysis (F4.4) | After transition preview | Teacher | Confirm state transitions before commit |
| Quiz generation (F11.8, OQ7) | After AI question generation | Teacher | First-use review of AI-generated questions |
| Teacher override (F11.12) | Before state change | Teacher | Provide motivation (min 20 chars) |
| Content review (F12.5) | After generation | Teacher | Optional edit before student delivery |

When an interrupt is triggered, the workflow pauses and persists state. The teacher receives a notification (F16). When the teacher responds via the dashboard, the workflow resumes from the interrupt checkpoint.

---

## 3. Agent Specifications

### 3.1 Orchestrator

| Attribute | Value |
|---|---|
| **Purpose** | Route incoming requests, enforce consent gates, sequence agent calls, enforce safeguarding pipeline, manage workflow state |
| **Trigger** | API request from FastAPI (REST or WebSocket) |
| **Inputs** | HTTP request payload, authenticated user context from Keycloak |
| **Outputs** | Completed workflow result, delivered to client via API response or WebSocket push |
| **LLM usage** | None. The orchestrator is deterministic graph logic, not LLM-powered. Intent classification uses a lightweight rules engine (request_type is explicit in the API contract, not inferred). |
| **State** | LangGraph StateGraph + PostgresSaver checkpoints |
| **Dependencies** | All other agents (calls them as graph nodes) |
| **Fallback** | If a non-critical agent fails, skip and deliver partial result with degradation notice. If a critical agent fails (Safeguarding, Identity & Consent), block delivery and alert teacher. |
| **MVP scope** | Full implementation |

### 3.2 Identity & Consent Manager

| Attribute | Value |
|---|---|
| **Purpose** | Manage student identity lifecycle (F14.1), verify consent status before any agent operates on student data (F14.3), provide audit log for all identity operations (F14.10) |
| **Trigger** | Called by Orchestrator at the start of every workflow (`consent_gate` node) |
| **Inputs** | `student_internal_id`, `request_type`, required consent categories for the request |
| **Outputs** | `ConsentVerification { student_pseudo_id, active_consents[], consent_valid: bool, missing_consents[] }` |
| **LLM usage** | None. Pure database lookups against the `consents` and `students` tables. |
| **State** | PostgreSQL tables: `students`, `consents`, `enrolments`, `audit_log` |
| **Dependencies** | Keycloak (authentication), PostgreSQL |
| **Fallback** | If database is unreachable, deny access (fail-closed). |
| **MVP scope** | Full lifecycle: creation, consent (administered), enrolment, activation, first-activation flow, erasure with certificate. Self-service consent (SPID/QR) deferred to V1. |

**Consent matrix by request type**:

| Request type | Required consents |
|---|---|
| Lesson upload | None (teacher operation) |
| Verification analysis | None (teacher triggers, system processes) |
| Content generation (text) | (a) if using profile adaptation; none for default content |
| Content generation (bilingual) | (a) + (b) |
| Gap closure cycle | (a) if profile-adapted |
| Onboarding quiz | (a) |
| Retention check | None (part of learning cycle, not profiling) |
| Family report | (c) |
| Cross-year history | (d) |
| Research analytics | (e) |

When consent is missing, the system operates in **degraded mode**: uniform content-adaptation profile (20% each dimension), no bilingual output, no behavioural tracking. The student still receives learning content -- just not personalised.

### 3.3 Knowledge Map Manager (KMM)

| Attribute | Value |
|---|---|
| **Purpose** | Central state authority for per-(student, node) mastery state. Owns the six-state machine (F11.3), all transitions (F11.4), retention check scheduling (F11.10), macro/micro rollup (F11.11), heatmap data (F11.14) |
| **Trigger** | Called by Orchestrator when a state transition is needed: post-diagnostic (F4.3), post-quiz (F11.9), retention check result, teacher override (F11.12), lesson introduction |
| **Inputs** | `KMMTransitionRequest { student_id, node_id, event_type, evidence_ref, source_agent, override_motivation? }` |
| **Outputs** | `KMMTransitionResult { node_id, prev_state, new_state, transition_id, scheduled_retention_checks[], macro_state_updates[] }` |
| **LLM usage** | None. Pure state-machine logic + database operations. |
| **State** | PostgreSQL tables: `kmm_states`, `kmm_transitions` (partitioned by month), `retention_schedule` |
| **Dependencies** | PostgreSQL, Apache AGE (for macro/micro hierarchy queries) |
| **Fallback** | If database is unreachable, queue transition in Redis and retry with exponential backoff. Never drop a transition event. |
| **MVP scope** | Full six-state machine, all canonical transitions, retention check at D+7 minimum, macro rollup (worst-state), teacher override with audit. Temporal heatmap deferred to V1. |

**State machine transition table** (canonical transitions per ADR-002):

```
non_introdotto  --[lesson_delivered]-->       introdotto
introdotto      --[error_mapping]-->          lacuna
introdotto      --[quiz_passed_80+]-->        da_consolidare  (skip if never tested as gap)
lacuna          --[start_recovery]-->         in_recupero
in_recupero     --[quiz_80+]-->              da_consolidare
in_recupero     --[quiz_50_79]-->            in_recupero      (varied path, attempt++)
in_recupero     --[quiz_lt_50]-->            lacuna           (alert teacher)
da_consolidare  --[retention_positive]-->     da_consolidare   (or consolidato if all checks pass)
da_consolidare  --[all_retention_positive]--> consolidato
da_consolidare  --[retention_negative]-->     lacuna
consolidato     --[error_mapping]-->          lacuna           (regression)
da_consolidare  --[error_mapping]-->          lacuna           (regression)
ANY             --[teacher_override]-->       ANY              (with motivation, audit logged)
```

**Retention scheduling** (MVP):
- When a node reaches `da_consolidare`, schedule a retention check at D+7
- Retention check result: pass -> `consolidato`; fail -> `lacuna`
- V1: expand to D+3, D+7, D+21 (with optional D+14 per ADR-002)

**Macro rollup** (per ADR-002):
- `macro_state = worst(child_micro_states)`
- UI displays both the worst-state color and a progress indicator ("7/10 consolidati")
- Rollup is computed on read (materialized view refreshed on transition), not stored redundantly

### 3.4 Curriculum Ingestion Agent

| Attribute | Value |
|---|---|
| **Purpose** | Process teacher-uploaded lessons and materials (F2), perform transcription (F2.2), extract concept mappings to KG nodes (F2.4), index materials in vector store (F2.10) |
| **Trigger** | Teacher uploads a lesson or material batch via dashboard API |
| **Inputs** | `LessonUpload { file_bytes, file_type, metadata: { difficulty, granularity, prerequisites }, course_id }` |
| **Outputs** | `IngestionResult { transcription_id?, concept_mappings: [{node_id, confidence, start_time?, end_time?}], vector_ids[], coverage_gaps[] }` |
| **LLM usage** | Yes. GPT-4o-mini for concept extraction from transcriptions (cost-optimized, F2.4). Claude for ambiguous mappings with confidence <80%. |
| **State** | PostgreSQL: `lessons`, `materials`, `concept_mappings`. pgvector: material embeddings. Object storage (Scaleway): raw files. |
| **Dependencies** | LLMGateway (for concept extraction), external transcription service (Whisper API or self-hosted), Apache AGE (KG node lookup) |
| **Fallback** | If transcription fails: accept manual transcript upload. If concept mapping fails: present all KG nodes for manual mapping by teacher. If vector indexing fails: retry async, content generation still works (uses KG relationships instead of semantic search). |
| **MVP scope** | Full: upload (PDF/DOCX/PPTX/MP3/MP4), transcription with timestamps, concept mapping with teacher validation, vector indexing. Batch upload supported. Coverage gap detection deferred to V1. |

**Processing pipeline**:

```
[File Upload] --> [Type Detection]
    |
    +--[Audio/Video]--> [Transcription Service] --> [Transcript]
    |                                                    |
    +--[Document]----> [Text Extraction] ---------------+
                                                         |
                                                    [Concept Extractor]  (LLMGateway)
                                                         |
                                                    [Mapping Confidence Check]
                                                         |
                                                    >=80%: auto-map
                                                    <80%: interrupt for teacher validation
                                                         |
                                                    [Vector Indexing]  (pgvector)
                                                         |
                                                    [KG Update]  (Apache AGE)
```

### 3.5 Student Profiler Agent

| Attribute | Value |
|---|---|
| **Purpose** | Manage the content-adaptation profile (F3, validated in ADR-002). Run onboarding quiz, compute 5-dimension profile vector, persist preferences. |
| **Trigger** | Student first activation (F14.6 -> onboarding), profile update request, V1: behavioural observation events |
| **Inputs** | Onboarding: `OnboardingQuizResponse { concept_responses: [{concept_id, modality_opened, time_spent_ms, completed}] }`. Update: `ProfileUpdate { dimension, new_value }` |
| **Outputs** | `ContentAdaptationProfile { visuale: float, audio: float, pratico: float, lettura: float, dialogo: float, tone: "confidenziale"|"neutro"|"formale", length: "sintesi"|"approfondimento" }` |
| **LLM usage** | None for MVP. The profile is computed from quiz interaction data using weighted scoring, not LLM inference. V1: LLM may assist in interpreting behavioural patterns. |
| **State** | PostgreSQL: `content_adaptation_profiles`, `onboarding_responses` |
| **Dependencies** | Identity & Consent Manager (requires consent (a) for profiling) |
| **Fallback** | If consent (a) denied: return uniform profile (20% each, neutral tone, medium length). If onboarding quiz abandoned mid-way: save partial responses, allow resumption, use partial data to compute initial profile. |
| **MVP scope** | Onboarding quiz (5-10 min, 3-5 concepts in 4 modalities), profile computation, manual override (F3.4), radar chart data. Behavioural evolution (F3.3) deferred to V1. |

**Terminology constraint** (per ADR-002): The profile is never called "learning style" in any interface. Dimensions use content-format labels: Visuale, Audio, Pratico, Lettura, Dialogo.

### 3.6 Diagnostic Agent

| Attribute | Value |
|---|---|
| **Purpose** | Analyze verification results, map errors to KG micro-nodes (F4.2), generate per-student diagnostic reports (F4.4), trigger KMM state transitions (F4.3) |
| **Trigger** | Teacher submits a graded verification via dashboard |
| **Inputs** | `VerificationSubmission { verification_id, questions: [{question_id, text, concept_node_ids, weight}], student_scores: [{student_id, question_id, score, student_code?}] }` |
| **Outputs** | `DiagnosticResult { per_student: [{student_id, errors: [{node_id, error_description, confidence}], transitions_preview: [{node_id, prev_state, proposed_state}]}], class_summary: {concept_distribution, avg_scores} }` |
| **LLM usage** | Yes. Claude for error-to-concept mapping when student code is provided (requires understanding of code semantics). GPT-4o-mini for straightforward score-to-concept mapping. All calls via LLMGateway with pseudonymised student IDs. |
| **State** | PostgreSQL: `verifications`, `verification_questions`, `student_scores`, `error_mappings` |
| **Dependencies** | LLMGateway, KMM (for current states and transition preview), Apache AGE (for concept hierarchy) |
| **Fallback** | If LLM fails: present raw scores to teacher with manual concept-mapping interface. If KMM is unreachable: queue transitions, generate report without transition preview. |
| **MVP scope** | Full: verification upload (manual + CSV import), error-to-concept mapping with confidence scoring, teacher validation of uncertain mappings (<80%), transition preview with teacher confirmation, class summary report. |

**Flow**:

```
[Verification Upload]
    |
[Question-Concept Mapping]  (teacher-defined in upload)
    |
[Per-Student Score Analysis]
    |
    +--[Code provided?]--YES--> [LLM Error Analysis]  (Claude via LLMGateway)
    |                                |
    +--[No code]---> [Score-Based Mapping]  (GPT-4o-mini or rules-based)
    |                                |
    +--------------------------------+
    |
[Confidence Scoring]
    |
    >=80% --> auto-map
    <80% --> interrupt: teacher validation
    |
[Transition Preview]  (query KMM for current states)
    |
[Teacher Confirmation Interrupt]
    |
[KMM Bulk Transition]  (atomic: all students in one transaction)
    |
[Generate Reports]  (teacher report + trigger content generation per student)
```

### 3.7 Content Orchestrator

| Attribute | Value |
|---|---|
| **Purpose** | Coordinate content generation across channels based on the content-adaptation profile. Enforce source priority (teacher lesson > textbook > external), minimum modality diversity (per ADR-002: at least 2 modality types per recovery mission), and bilingualism rules (F13). |
| **Trigger** | Called by Orchestrator when content generation is needed: post-diagnostic (F5), gap closure (F11.7), retention check prep |
| **Inputs** | `ContentRequest { student_pseudo_id, target_nodes: [{node_id, state, error_description?}], content_profile, bilingual: {active, language_code?}, attempt_number, source_priority_materials[] }` |
| **Outputs** | `ContentBundle { primary_content: {type, content}, secondary_content?: {type, content}, bilingual_content?: {type, content}, sources_used[] }` |
| **LLM usage** | None directly. Delegates to channel-specific agents (Text Agent, etc.) which use LLM. |
| **State** | PostgreSQL: `content_requests`, `content_bundles`, `content_delivery_log` |
| **Dependencies** | Text Agent, Bilingual Composer, Safeguarding Agent. V1: Podcast Agent, Game Agent. |
| **Fallback** | If preferred channel fails: fall back to text (always available). If all generation fails: serve cached content for the concept if available, or serve raw teacher lesson segment. |
| **MVP scope** | Text channel only (primary). Bilingual composition when consent (b) active. |

**Channel routing logic**:

```python
def route_content(profile: ContentAdaptationProfile, attempt: int) -> list[str]:
    """
    Returns ordered list of channels to generate.
    Minimum 2 channels for recovery missions (ADR-002 constraint).
    """
    # Sort channels by profile weight
    channels = sorted(
        [("text", profile.lettura), ("audio", profile.audio),
         ("visual", profile.visuale), ("exercise", profile.pratico),
         ("dialog", profile.dialogo)],
        key=lambda x: x[1], reverse=True
    )

    # Primary = highest weight
    result = [channels[0][0]]

    # If recovery mission (attempt >= 1), vary the channel on retry
    if attempt > 1:
        # Use the next-best channel that differs from previous attempt
        result = [channels[attempt % len(channels)][0]]

    # Ensure minimum diversity: add second channel if only one selected
    if len(result) < 2:
        for ch_name, _ in channels:
            if ch_name not in result:
                result.append(ch_name)
                break

    # MVP: only "text" is implemented. Filter to available channels.
    available = {"text"}  # V1: add "audio", "exercise", etc.
    return [ch for ch in result if ch in available] or ["text"]
```

### 3.8 Text Agent

| Attribute | Value |
|---|---|
| **Purpose** | Generate personalised review documents (F5) with the four-block structure: "Il tuo errore" -> "Perche' succede" -> "Come si fa giusto" -> "Ricordati". Adapt analogies, tone, and length to the content-adaptation profile. |
| **Trigger** | Called by Content Orchestrator |
| **Inputs** | `TextGenerationRequest { student_pseudo_id, target_nodes[], error_descriptions[], content_profile, source_materials[], course_language }` |
| **Outputs** | `TextDocument { blocks: [{concept_node_id, error_block, explanation_block, correction_block, remember_block}], analogies_used[], source_refs[], model_version, prompt_hash }` |
| **LLM usage** | Yes. Claude (primary) via LLMGateway. RAG over teacher lessons (priority) + course materials + vector store. Pseudonymised prompts only. |
| **State** | PostgreSQL: `generated_documents`. Object storage: rendered PDFs. |
| **Dependencies** | LLMGateway, pgvector (RAG retrieval), Apache AGE (concept context) |
| **Fallback** | If Claude is unavailable: try GPT-4o-mini with same prompt (quality may differ). If all LLMs fail: serve the teacher's lesson segment for the concept with a "generazione non disponibile" notice. |
| **MVP scope** | Full: four-block structure, profile-adapted analogies and tone, bilingual layout (via Bilingual Composer), teacher edit support (F5.7). |

**Prompt architecture** (pseudonymised example):

```
You are a tutor for an Italian high school IT student (STUDENT_0042).
The student has a gap in the concept: "Sessioni PHP - Gestione session_start()".

Content adaptation profile:
- Preferred format: in-depth reading
- Tone: confidenziale (tu, informal)
- Analogies: diversified (sports, cooking, gaming — vary across blocks)

Source material (teacher lesson, priority 1):
[RAG-retrieved segment from teacher's lesson on PHP sessions]

Source material (textbook, priority 2):
[RAG-retrieved segment from course textbook]

The student's error:
[Pseudonymised error description from diagnostic agent]

Generate a review document with exactly 4 blocks:
1. "IL TUO ERRORE" — show what went wrong in the student's code (yellow border)
2. "PERCHE' SUCCEDE" — explain why this error occurs, using an analogy
3. "COME SI FA GIUSTO" — show the correct code (green border) with explanation
4. "RICORDATI" — one memorable rule to retain

Constraints:
- NEVER reference the student's real name or personal details
- NEVER compare with other students
- Tone: encouraging, never punitive
- Language: Italian (official course language)
- If the concept involves code, show ERRATO/CORRETTO side by side
```

**Latency target**: <=60 seconds (N4). Achieved via:
- Streaming response from Claude (user sees progressive rendering)
- RAG retrieval pre-computed and cached per concept
- Semantic cache hit for common concepts (pgvector similarity >=0.95)

### 3.9 Bilingual Composer

| Attribute | Value |
|---|---|
| **Purpose** | Transform monolingual content into dual-language format (F13). Official course language in left column, student's native language in right column. Technical terms in both languages. |
| **Trigger** | Called by Content Orchestrator when bilingualism is active (consent (b) granted, language_code set) |
| **Inputs** | `BilingualRequest { content: TextDocument, source_language: str, target_language: str, glossary_id: str }` |
| **Outputs** | `BilingualDocument { blocks: [{left_column: str, right_column: str, technical_terms: [{official: str, native: str}]}] }` |
| **LLM usage** | Yes. Claude via LLMGateway. The prompt includes the controlled technical glossary (F13.18) to ensure consistent terminology. Native language is referenced by code only (e.g., `uk` for Ukrainian), never associated with a student identity in the prompt. |
| **State** | PostgreSQL: `bilingual_glossaries`, `bilingual_documents` |
| **Dependencies** | LLMGateway, glossary store |
| **Fallback** | If LLM fails for native language: deliver monolingual content with a notice "traduzione non disponibile al momento". If glossary is missing: use LLM's built-in translation (lower quality, flagged for review). |
| **MVP scope** | Two languages: Ukrainian (`uk`), Arabic (`ar`). Two-column text layout. Technical glossary per language. V1: +4 languages, podcast cross-language variant. |

**Privacy constraint**: The `BilingualRequest` never contains the student's identity. The LLMGateway receives only the content and a language code. The association between student and native language exists only in the Identity & Consent Manager's encrypted storage.

### 3.10 Safeguarding Agent

| Attribute | Value |
|---|---|
| **Purpose** | Validate every content output before student delivery (N3, CLAUDE.md non-negotiable). Detect: offensive language, age-inappropriate content, stereotypes, student comparisons, manipulative patterns, wellbeing concerns. |
| **Trigger** | Called by Orchestrator as a mandatory pipeline stage after content generation, before delivery |
| **Inputs** | `SafeguardingRequest { content, content_type, target_audience_age_range: [13, 19], context: { student_pseudo_id, concept_domain } }` |
| **Outputs** | `SafeguardingVerdict { safe: bool, issues: [{category, severity, description, location}], modified_content?: str, wellbeing_alert?: { type, recommended_action } }` |
| **LLM usage** | Yes. Claude via LLMGateway (safety-focused prompt, no student PII). For MVP, a single-pass review. V1: add rule-based pre-filter (keyword blocklist, regex patterns) before LLM pass to reduce latency and cost. |
| **State** | PostgreSQL: `safeguarding_verdicts`, `wellbeing_alerts` |
| **Dependencies** | LLMGateway |
| **Fallback** | If LLM is unavailable: apply rule-based filter only (keyword blocklist + regex). Content passes only if the rule-based filter finds zero issues. If both LLM and rule-based fail: block content delivery, notify teacher, serve teacher's original lesson material instead. Never deliver unreviewed content to a minor. |
| **MVP scope** | Full: every content output reviewed. Categories: offensive language, age-appropriateness, stereotype detection, student comparison detection, manipulative patterns (FOMO, scarcity), wellbeing pattern detection (repeated failure frustration). |

**Safeguarding categories and severity**:

| Category | Severity | Action |
|---|---|---|
| Offensive language | BLOCK | Remove content, regenerate |
| Age-inappropriate content | BLOCK | Remove content, regenerate |
| Stereotype (cultural, gender) | BLOCK | Remove content, regenerate |
| Student comparison | BLOCK | Remove content, regenerate |
| Manipulative pattern (FOMO, scarcity) | BLOCK | Remove content, regenerate |
| Punitive tone | WARN | Auto-correct tone, log for review |
| Wellbeing concern (frustration pattern) | ALERT | Deliver content, alert teacher + school referent |
| Minor factual concern | PASS_WITH_FLAG | Deliver content, flag for teacher review |

**Non-bypassable enforcement**: The Orchestrator graph has no edge that connects content generation to student delivery without passing through the `safeguarding_gate` node. This is a structural guarantee, not a policy.

### 3.11 Feedback Loop Agent

| Attribute | Value |
|---|---|
| **Purpose** | After content delivery, update the student's content-adaptation profile based on engagement, trigger KMM state transitions based on quiz/retention results, update KG coverage metrics |
| **Trigger** | Called by Orchestrator after content delivery and student interaction events |
| **Inputs** | `FeedbackEvent { student_id, event_type: "content_viewed"|"content_completed"|"quiz_submitted"|"retention_check_submitted"|"modality_switched", event_data }` |
| **Outputs** | `FeedbackActions { profile_updates?: dict, kmm_transitions?: [KMMTransitionRequest], kg_updates?: [CoverageUpdate], notifications?: [NotificationRequest] }` |
| **LLM usage** | None. Pure event processing and state updates. |
| **State** | PostgreSQL: `feedback_events`, `engagement_metrics` |
| **Dependencies** | KMM (for state transitions), Student Profiler (for profile updates, V1), Notification service (F16) |
| **Fallback** | If KMM is unreachable: queue transitions in Redis. If profile update fails: log and retry. Feedback events are never lost -- they are persisted to the events table before processing. |
| **MVP scope** | Quiz result processing (trigger KMM transitions), content delivery logging, basic engagement metrics. Behavioural profile updates deferred to V1. |

### 3.12 Podcast Agent (V1)

| Attribute | Value |
|---|---|
| **Purpose** | Generate two-voice podcast scripts (F6) and synthesize audio via TTS |
| **Trigger** | Called by Content Orchestrator when audio channel is selected |
| **Inputs** | `PodcastRequest { concept_nodes[], content_profile, voice_preferences, course_language }` |
| **Outputs** | `PodcastResult { script: { segments: [{speaker, text, timestamp}] }, audio_url, transcript_url, duration_seconds }` |
| **LLM usage** | Yes. Claude for script generation (two-voice dialogue: "esperto" and "curioso"). OpenAI TTS for audio synthesis (per ADR-001). |
| **State** | PostgreSQL: `podcast_scripts`. Object storage: audio files. |
| **Dependencies** | LLMGateway, TTS API, Safeguarding Agent (script reviewed before synthesis) |
| **Fallback** | If TTS fails: deliver script as readable text with a "audio non disponibile" notice. If script generation fails: fall back to Text Agent. |
| **MVP scope** | Stub only (returns "channel not available"). V1: full implementation. |

### 3.13 Game Agent (V1)

| Attribute | Value |
|---|---|
| **Purpose** | Manage gamification layer (F7): XP, badges, streaks, daily/weekly quests tied to gap closure |
| **Trigger** | Called by Orchestrator on student activity events, called by Content Orchestrator for quest generation |
| **Inputs** | `GamificationEvent { student_id, event_type, event_data }` or `QuestRequest { student_id, open_lacunae[] }` |
| **Outputs** | `GamificationUpdate { xp_earned, new_badges[], streak_status, active_quests[] }` |
| **LLM usage** | Minimal. GPT-4o-mini for quest description generation (creative text, not safety-critical). |
| **State** | PostgreSQL: `student_xp`, `badges`, `streaks`, `quests` |
| **Dependencies** | KMM (for gap status), Safeguarding Agent (quest descriptions reviewed) |
| **Fallback** | If gamification fails: learning flows continue without gamification. Gamification is opt-in and its failure never blocks content delivery. |
| **MVP scope** | Stub only. V1: full implementation with anti-patterns enforced (F7.7: no public leaderboards, no FOMO, opt-out preserved). |

### 3.14 Visual Agent (V1/V2)

| Attribute | Value |
|---|---|
| **Purpose** | Generate visual content: diagrams, flowcharts, concept maps, annotated code screenshots |
| **Trigger** | Called by Content Orchestrator when visual channel is selected |
| **Inputs** | `VisualRequest { concept_nodes[], content_type, accessibility_requirements }` |
| **Outputs** | `VisualResult { svg_content, alt_text, aria_description }` |
| **LLM usage** | Yes. Claude for generating diagram descriptions (Mermaid/D2 syntax), then rendered server-side. |
| **State** | PostgreSQL: `visual_content`. Object storage: rendered images. |
| **Dependencies** | LLMGateway, diagram rendering service |
| **Fallback** | If generation fails: fall back to Text Agent with structured explanation. |
| **MVP scope** | Stub only. V1: basic diagrams (Mermaid). V2: animations, interactive visuals. |

### 3.15 Dialog Agent (V2)

| Attribute | Value |
|---|---|
| **Purpose** | Conversational tutoring (F10.4): real-time Q&A about concepts, rubber-duck verification |
| **Trigger** | Student initiates a chat session from the concept detail view |
| **Inputs** | `DialogTurn { student_pseudo_id, message, concept_context, conversation_history[] }` |
| **Outputs** | `DialogResponse { message, suggested_resources[], concept_refs[] }` |
| **LLM usage** | Yes. Claude with streaming for <=3s P95 latency (N4). Context window: concept-scoped RAG + conversation history. |
| **State** | PostgreSQL: `dialog_sessions`, `dialog_turns` |
| **Dependencies** | LLMGateway, Safeguarding Agent (every response reviewed), KMM (concept context) |
| **Fallback** | If LLM is unavailable: display "tutoring non disponibile" with link to Text Agent content. |
| **MVP scope** | Not implemented. V2 feature. |

---

## 4. Agent Communication

### 4.1 Communication Model

Agents communicate through **LangGraph's shared state object** (`MaestroState`), not through direct message passing or an event bus. Each agent reads from and writes to designated fields in the state object. The Orchestrator controls sequencing through graph edges.

**Rationale**: This model provides:
- Deterministic execution order (no race conditions)
- Full state visibility at every checkpoint (audit)
- No need for a separate message broker (reduced infrastructure)
- Natural human-in-the-loop integration (interrupt pauses the graph, state is preserved)

### 4.2 Synchronous vs Asynchronous Flows

| Flow type | Communication model | Example |
|---|---|---|
| **Request-response** (student-facing) | Synchronous within the LangGraph execution | Content generation: student requests -> orchestrator -> agents -> safeguarding -> response |
| **Background processing** | Asynchronous via Redis task queue | Lesson transcription, vector indexing, batch content pre-generation |
| **Scheduled tasks** | Cron-triggered via Redis + LangGraph | Retention check notifications, overnight batch generation |
| **Teacher interrupts** | Async with checkpoint resume | Teacher validates concept mapping, confirms transitions |

### 4.3 Message Format (Internal)

Agents do not exchange messages directly. They write to typed fields in `MaestroState`. However, for **async background tasks** and **cross-workflow communication**, a standardised event format is used:

```python
class MaestroEvent(TypedDict):
    event_id: str               # UUID
    event_type: str             # e.g., "kmm.transition", "content.generated", "safeguarding.alert"
    timestamp: datetime
    source_agent: str           # e.g., "diagnostic_agent"
    target_agent: Optional[str] # None = broadcast
    payload: dict               # Event-specific data
    correlation_id: str         # Links to the originating request_id
    trace_id: str               # OpenTelemetry trace ID
```

Events are published to a Redis stream (`maestro:events`) for:
- Notification triggers (F16)
- Analytics pipeline
- Cross-workflow coordination (e.g., lesson upload triggers re-generation of affected content)

### 4.4 Agent State: Stateless with External Store

**Decision**: Agents are stateless functions. All state is external (PostgreSQL + Redis).

**Rationale**: This enables:
- Horizontal scaling (any worker can execute any agent node)
- Clean restart after failure (state survives process death)
- No session affinity required
- Simpler deployment (stateless containers)

The LangGraph `StateGraph` itself maintains execution state via `PostgresSaver`, but individual agent functions are pure: they receive state, perform computation, and return updated state.

---

## 5. Key Flows (Sequence Descriptions)

### 5.1 Lesson Upload Flow (F2)

```
Teacher -> [FastAPI: POST /api/v1/courses/{id}/lessons]
    |
    v
[Orchestrator: start "lesson_upload" workflow]
    |
    v
[consent_gate]  --> No student data involved, pass-through
    |
    v
[Curriculum Ingestion Agent]
    |
    +--[file_type detection]
    |
    +--[audio/video?] --> [Transcription Service (async)]
    |                         |
    |                    [Wait for transcription]
    |                         |
    +--[document?] ---------> [Text Extraction]
    |                              |
    +------------------------------+
    |
    v
[Concept Extraction]  (LLMGateway: GPT-4o-mini)
    |
    v
[Mapping Confidence Check]
    |
    >=80% for all concepts --> auto-map
    |
    <80% for any concept --> [INTERRUPT: teacher validation]
    |                              |
    |                    [Teacher validates via dashboard]
    |                              |
    +------------------------------+
    |
    v
[Vector Indexing]  (pgvector, async)
    |
    v
[KG Update]  (Apache AGE: link lesson to concept nodes)
    |
    v
[KMM: bulk transition introdotto]  (for enrolled students, if concepts newly covered)
    |
    v
[Notification: "Nuova lezione disponibile"]  (F16.3)
    |
    v
END (checkpoint persisted)
```

**Latency**: Transcription is async (background). Concept mapping completes in <30s for document-based lessons. The teacher interrupt for validation is async (hours/days).

### 5.2 Verification Analysis Flow (F4 -> F11 -> F5)

```
Teacher -> [FastAPI: POST /api/v1/verifications]
    |
    v
[Orchestrator: start "verification_analysis" workflow]
    |
    v
[consent_gate]  --> Teacher operation, pass-through for teacher actions.
                    Student processing requires no additional consent
                    (assessment is part of the educational relationship).
    |
    v
[Diagnostic Agent]
    |
    +--[Parse verification structure: questions, weights, concept mappings]
    |
    +--[Per-student score ingestion]
    |
    +--[Error-to-concept mapping]
    |      |
    |      +--[Code provided?] --> [Claude: analyze code errors] (LLMGateway)
    |      |
    |      +--[No code] --> [Score-based mapping] (rules + GPT-4o-mini)
    |      |
    |      +--[Confidence scoring]
    |             |
    |             <80% --> [INTERRUPT: teacher validates uncertain mappings]
    |             |
    +-------------+
    |
    v
[Transition Preview]
    |
    +--[Query KMM for current states of all affected (student, node) pairs]
    |
    +--[Compute proposed transitions: introdotto/da_consolidare/consolidato -> lacuna]
    |
    +--[INTERRUPT: teacher confirms transitions with preview]
    |       |
    |  [Teacher reviews per-student transition list]
    |  [Teacher can modify/reject individual transitions]
    |       |
    +-------+
    |
    v
[KMM: bulk atomic transition]
    |
    +--[For each student with new lacunae:]
    |      |
    |      v
    |  [Content Orchestrator: generate recovery content (F5)]
    |      |
    |      v
    |  [Text Agent: generate personalised document]  (LLMGateway: Claude)
    |      |
    |      v
    |  [Bilingual Composer: if consent (b) active]  (LLMGateway: Claude)
    |      |
    |      v
    |  [Safeguarding Agent: review]
    |      |
    |      SAFE --> [Store + notify student (F16.3)]
    |      |
    |      BLOCKED --> [Regenerate with modified prompt, re-review]
    |
    v
[Generate teacher report (F4.4)]
    |
    +--[Class summary: concept distribution, avg scores, most problematic concepts]
    |
    +--[Per-student: error list, transitions, link to generated content]
    |
    v
[Notification: teacher report ready (F16.1)]
    |
    v
END
```

**Latency**: The full flow for a class of 30 students takes approximately 3-5 minutes (dominated by per-student content generation at <=60s each, parallelised to 5-10 concurrent). Teacher interrupts are async.

### 5.3 Gap Closure Cycle (F11.6-F11.10)

```
Student -> [opens recovery mission from dashboard (F11.6)]
    |
    v
[Orchestrator: start "gap_closure" workflow]
    |
    v
[consent_gate]  --> Check consent (a) for profile-adapted content
    |
    v
[KMM: transition lacuna -> in_recupero]
    |
    v
[Content Orchestrator]
    |
    +--[Determine content channel based on profile + attempt number]
    |
    +--[Retrieve source materials (RAG): teacher lesson (P1) > textbook (P2) > external (P3)]
    |
    +--[Text Agent: generate recovery document (F11.7)]  (LLMGateway: Claude)
    |
    +--[Bilingual Composer: if applicable]
    |
    +--[Safeguarding Agent: review]
    |
    v
[Deliver content to student]
    |
    v
[Student studies content]
    |
    v
Student -> [requests mini-quiz (F11.8)]
    |
    v
[Quiz Generation]
    |
    +--[Check teacher question bank for micro-node]
    |      |
    |      Found --> use teacher questions (priority 1)
    |      |
    |      Not found --> [LLMGateway: generate quiz]  (Claude, RAG-anchored)
    |                         |
    |                    [Structural validation (automated)]
    |                         |
    |                    [First use?] --> [INTERRUPT: teacher review]
    |                         |
    |                    [Previously approved] --> use from vetted bank
    |
    v
[Deliver quiz to student (3-5 questions, official language only per F13.19)]
    |
    v
[Student submits quiz]
    |
    v
[Feedback Loop Agent: evaluate]
    |
    +--[Score >= 80%] --> [KMM: in_recupero -> da_consolidare]
    |                         |
    |                    [Schedule retention check at D+7]
    |                         |
    |                    [Show feedback: encouraging, green tone]
    |
    +--[Score 50-79%] --> [KMM: stay in_recupero, attempt++]
    |                         |
    |                    [Content Orchestrator: generate varied path]
    |                         |
    |                    [Show feedback: encouraging, "ci sei quasi"]
    |
    +--[Score < 50%]  --> [KMM: in_recupero -> lacuna]
    |                         |
    |                    [Alert teacher (F11.9)]
    |                         |
    |                    [Show feedback: encouraging (arancione, NEVER red)]
    |                         |
    |                    [Suggest: "Riprova con un altro approccio"]
    |
    v
[Per-question feedback: answer given, correct answer, explanation]
    |
    v
END
```

**Retention check sub-flow (D+7)**:

```
[Scheduled trigger: D+7 from da_consolidare timestamp]
    |
    v
[Notification to student: "Quick refresh disponibile" (gentle, never urgent)]
    |
    v
Student -> [opens retention check]
    |
    v
[Quiz Generation: Bloom's level Understand+Apply (per ADR-002)]
    |
    v
[Student submits]
    |
    v
[Score >= 80%] --> [KMM: da_consolidare -> consolidato]
    |
[Score < 80%]  --> [KMM: da_consolidare -> lacuna (regression)]
                        |
                   [Notification: encouraging tone, new recovery mission created]
```

### 5.4 Student Onboarding Flow (F14 -> F3)

```
Admin -> [creates student account (F14.2)]
    |
    v
[Identity & Consent Manager: create student record]
    |
    v
[Family -> consent flow (F14.3, administered in MVP)]
    |
    +--[5 consent cards: (a) profiling, (b) native language, (c) family comms,
    |                     (d) cross-year history, (e) research]
    |
    +--[Each toggle: title, explanation, base juridique, consequence if denied]
    |
    v
[Admin records consent decisions]
    |
    v
[Student receives credentials (one-time or SSO via Keycloak)]
    |
    v
Student -> [first activation (F14.6)]
    |
    v
[Terms acceptance (age-appropriate language)]
    |
    v
[consent_gate: check consent (a)]
    |
    +--[Consent (a) granted] --> [Student Profiler Agent: onboarding quiz]
    |                                  |
    |                             [3-5 concepts x 4 modalities, 5-10 min]
    |                                  |
    |                             [Compute 5-dimension profile vector]
    |                                  |
    |                             [Show radar chart with explanation:]
    |                             ["Questo grafico mostra come preferisci
    |                              ricevere i contenuti. Non e' un giudizio
    |                              sulle tue capacita'. Puoi cambiarlo
    |                              in qualsiasi momento."]
    |
    +--[Consent (a) denied] --> [Set uniform profile (20% each)]
    |                                  |
    |                             [Skip onboarding quiz]
    |
    v
[KMM: initialise all KG nodes to non_introdotto for the student's course]
    |
    v
[Redirect to student dashboard]
    |
    v
END
```

### 5.5 Content Generation Flow (F5 + F13 + N3)

```
[Content Orchestrator receives ContentRequest]
    |
    v
[Check bilingualism: consent (b) active AND language_code set?]
    |
    v
[RAG retrieval: source materials for target concepts]
    |
    +--[Teacher lessons (priority 1)]  --> pgvector similarity search, filtered by course_id + concept_node_ids
    |
    +--[Course textbook (priority 2)]  --> pgvector similarity search
    |
    +--[External materials (priority 3)] --> pgvector similarity search
    |
    v
[Text Agent: generate document]  (LLMGateway: Claude)
    |
    +--[Prompt includes: pseudonymised student context, content profile,
    |   source materials, error descriptions, tone/length preferences]
    |
    +--[Streaming response for progressive rendering]
    |
    v
[Bilingual?]
    |
    YES --> [Bilingual Composer: translate to dual-column format]
    |            |
    |       [Use controlled glossary (F13.18)]
    |            |
    |       [Technical terms in both languages]
    |
    NO ---> [Continue with monolingual content]
    |
    v
[Safeguarding Agent: mandatory review]
    |
    +--[SAFE]
    |     |
    |     v
    |  [Store content in PostgreSQL + object storage]
    |     |
    |     v
    |  [Deliver to student via API / push notification]
    |
    +--[BLOCKED]
    |     |
    |     v
    |  [Log issue, regenerate with modified prompt]
    |     |
    |     v
    |  [Safeguarding Agent: re-review (max 2 retries)]
    |     |
    |     v
    |  [Still blocked?] --> [Alert teacher, serve fallback content]
    |
    +--[ALERT (wellbeing)]
          |
          v
       [Deliver content (it's safe)]
          |
          v
       [Alert teacher + school referent via notification (F16)]
```

---

## 6. LLM Gateway & Pseudonymisation

### 6.1 LLMGateway Architecture

The `LLMGateway` is a Python service (not a separate microservice -- it is a module within the FastAPI application) that mediates all LLM API calls.

```
[Agent Node] --> [LLMGateway]
                      |
                 [Pseudonymiser]
                      |
                 [Model Router]
                      |
                 +----+----+
                 |         |
            [Claude]  [GPT-4o-mini]
                 |         |
                 +----+----+
                      |
                 [De-pseudonymiser]
                      |
                 [Audit Logger]
                      |
                 [Response Cache]
                      |
                 --> [Agent Node]
```

### 6.2 Pseudonymisation Rules

| Data type | Pseudonymisation | Example |
|---|---|---|
| Student name | `STUDENT_{hash_prefix_6}` | "Marco Rossi" -> `STUDENT_a3f2c1` |
| Teacher name | `TEACHER_{hash_prefix_6}` | "Prof. Bianchi" -> `TEACHER_7b4e2d` |
| School name | `SCHOOL_{id}` | "ITET Pantanelli" -> `SCHOOL_001` |
| Native language | Language code only | "ucraino" -> `uk` (never associated with student identity in prompt) |
| Student code (from verification) | Variable names preserved, comments stripped of names | Unchanged except PII in comments |
| Email/phone | Never included | Stripped at boundary |
| Class/section | `CLASS_{id}` | "5AI" -> `CLASS_001` |

**Session-scoped mapping table**: The pseudonymisation mapping is held in memory during request processing and is never persisted to disk or sent to any external service. After the LLM response is de-pseudonymised, the mapping is discarded.

### 6.3 Model Routing

| Task | Primary model | Secondary model | Routing criteria |
|---|---|---|---|
| Recovery document generation (F5) | Claude | GPT-4o-mini (fallback) | Quality-critical, pedagogical content |
| Quiz generation (F11.8) | Claude | GPT-4o-mini (fallback) | Quality-critical, educational assessment |
| Concept extraction from lessons (F2.4) | GPT-4o-mini | Claude (for ambiguous cases) | Cost-optimized, structured extraction |
| Error-to-concept mapping (F4.2) | GPT-4o-mini | Claude (for code analysis) | Cost-optimized for score-based; Claude for code semantics |
| Bilingual translation (F13) | Claude | -- | Quality-critical, nuanced translation |
| Safeguarding review (N3) | Claude | Rule-based (fallback) | Safety-critical, requires nuanced judgment |
| Podcast script (F6, V1) | Claude | -- | Creative content |
| Quest descriptions (F7, V1) | GPT-4o-mini | -- | Low-stakes creative text |

### 6.4 Caching Strategy

Three layers (per ADR-001):

1. **Deterministic cache** (Redis): Exact prompt hash match. TTL: 24 hours. Covers repeated concept extractions for the same lesson.

2. **Semantic cache** (pgvector): Cosine similarity >= 0.95 on the prompt embedding. TTL: 7 days. Covers similar recovery documents for the same concept across students (after pseudonymisation, prompts for the same concept differ only in error descriptions and profile parameters).

3. **Pre-generated batch cache** (overnight): Top 20 most common `lacuna` micro-nodes per class are pre-generated during off-peak hours. Stored in PostgreSQL. Cache invalidated when teacher uploads new lesson content for the concept.

### 6.5 Audit Logging

Every LLM call is logged to the `llm_audit_log` table:

```sql
CREATE TABLE llm_audit_log (
    id              BIGSERIAL PRIMARY KEY,
    request_id      UUID NOT NULL,          -- correlation to workflow
    agent_name      TEXT NOT NULL,           -- which agent made the call
    model_id        TEXT NOT NULL,           -- "claude-sonnet-4-20250514", "gpt-4o-mini-2024-07-18"
    prompt_hash     TEXT NOT NULL,           -- SHA-256 of the pseudonymised prompt
    input_tokens    INTEGER NOT NULL,
    output_tokens   INTEGER NOT NULL,
    latency_ms      INTEGER NOT NULL,
    cache_hit       BOOLEAN NOT NULL DEFAULT FALSE,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (timestamp);
```

The actual prompt text is NOT stored (it may contain concept-specific content that is copyrighted by the teacher). Only the hash is stored for reproducibility verification.

---

## 7. Safeguarding Integration

### 7.1 Placement in the Pipeline

The Safeguarding Agent is placed at two points in every content delivery path:

1. **Post-generation gate** (mandatory, blocking): After content is generated by any content agent (Text, Podcast, Visual, Game, Dialog) and before delivery to the student.

2. **Quiz review** (mandatory, blocking): After quiz questions are generated and before delivery to the student. This ensures AI-generated questions do not contain offensive content, trick questions, or anxiety-inducing language (per ADR-002 anti-patterns).

```
[Any Content Agent] --> [Safeguarding Agent] --> [Student Delivery]
                              ^
                              |
                        NEVER bypassed
```

### 7.2 Blocking vs Non-Blocking

| Verdict | Behavior | Student impact |
|---|---|---|
| SAFE | Content delivered immediately | None |
| BLOCKED | Content withheld, regenerated (max 2 retries), teacher alerted if retries exhausted | Delay. If retries fail, student receives teacher's original material with explanation. |
| ALERT (wellbeing) | Content delivered (it is safe), teacher and school referent alerted | None visible to student. Teacher receives notification with context. |

### 7.3 Wellbeing Detection Patterns

The Safeguarding Agent monitors for:

| Pattern | Detection method | Action |
|---|---|---|
| Repeated regression (3+ on same concept in 30 days) | KMM transition history query | Alert teacher, suggest channel change |
| Extended inactivity after lacuna detection (>7 days) | Engagement metrics | Gentle notification to student, alert teacher |
| Frustration language in chat (V2) | LLM classification | Alert teacher, offer support resources |
| Late-night usage (after 21:00 for under-16) | Timestamp check | Notification: "Fai una pausa, ci rivediamo domani" |
| Quiz abandonment pattern (3+ abandoned quizzes) | Engagement metrics | Alert teacher, suggest simpler assessment |

### 7.4 Content Moderation Rules

Per N3, F7.7, and ADR-002 tone requirements:

- No offensive language (including subtle put-downs in "confidenziale" tone)
- No student comparisons (even implied: "most students get this right")
- No stereotypes (cultural, gender, regional Nord/Sud, socio-economic)
- No manipulative patterns (FOMO: "altri stanno avanzando!", scarcity: "ultima possibilita'!")
- No punitive framing (never "hai sbagliato", prefer "questo concetto ha bisogno di un altro giro")
- No timer references in quiz context
- No red UI elements for negative results (arancione only)
- Age-appropriate vocabulary (no sarcasm, no irony that could be misread)

---

## 8. Error Handling & Resilience

### 8.1 Agent Failure Classification

| Failure type | Examples | Recovery strategy |
|---|---|---|
| **Critical (blocks delivery)** | Safeguarding Agent down, Identity & Consent Manager down, PostgreSQL down | Halt workflow, return error to client, alert ops. Never deliver content without safeguarding. Never process student data without consent verification. |
| **Degraded (partial delivery)** | LLM provider down, TTS down, vector store slow | Fall back to secondary model or cached content. Deliver what is available with degradation notice. |
| **Non-critical (log and continue)** | Analytics write fails, notification delivery fails, gamification update fails | Log error, retry async, continue primary workflow. |

### 8.2 Retry Policies

| Component | Retry strategy | Max retries | Backoff |
|---|---|---|---|
| LLM API (Claude) | Retry with exponential backoff, then failover to GPT-4o-mini | 3 | 1s, 2s, 4s |
| LLM API (GPT-4o-mini) | Retry with exponential backoff | 3 | 1s, 2s, 4s |
| PostgreSQL | Connection pool retry | 5 | 500ms, 1s, 2s, 4s, 8s |
| Redis | Retry, then bypass cache | 2 | 500ms, 1s |
| Transcription service | Retry async | 3 | 30s, 60s, 120s |
| TTS (V1) | Retry, then serve text-only | 2 | 1s, 2s |

### 8.3 Circuit Breaker

A circuit breaker wraps each external dependency (LLM APIs, Transcription, TTS):

- **Closed** (normal): requests flow through
- **Open** (failure threshold exceeded): requests immediately fail-fast to fallback for 60 seconds
- **Half-open**: after 60 seconds, allow one probe request. If it succeeds, close the circuit.

Failure threshold: 5 consecutive failures or >50% failure rate in a 30-second window.

### 8.4 Graceful Degradation Matrix

| Scenario | Student-facing impact | Teacher-facing impact |
|---|---|---|
| Claude API down | Content generated by GPT-4o-mini (potentially lower quality). If both down, cached content served. | Dashboard shows "generazione con modello alternativo" badge. |
| PostgreSQL down | System unavailable. Error page with retry suggestion. | Same. |
| Redis down | No caching. Slower responses, higher LLM costs. No degradation in functionality. | No visible impact. |
| Transcription service down | Lesson upload accepted but transcription pending. Manual transcript upload offered. | Upload succeeds, transcription queued. |
| Safeguarding Agent LLM down | Rule-based filter only. Higher bar for passing (zero tolerance). Delays possible. | Alerted that safeguarding is in degraded mode. |
| Vector store (pgvector) slow | RAG retrieval slower, content generation may exceed 60s. | Latency warning in monitoring. |

---

## 9. Observability

### 9.1 Distributed Tracing

Every workflow execution is a single OpenTelemetry trace. Each agent node is a span within the trace. LLM calls are child spans of their agent span.

```
Trace: maestro.workflow.verification_analysis
  |
  +-- Span: consent_gate (2ms)
  |
  +-- Span: diagnostic_agent (4200ms)
  |     |
  |     +-- Span: llm.call.gpt-4o-mini (1800ms)
  |     |     attributes: { model: "gpt-4o-mini", tokens_in: 2400, tokens_out: 800 }
  |     |
  |     +-- Span: llm.call.claude (2100ms)
  |           attributes: { model: "claude-sonnet-4", tokens_in: 8000, tokens_out: 3200 }
  |
  +-- Span: kmm_transition (15ms)
  |
  +-- Span: text_agent (42000ms)
  |     |
  |     +-- Span: rag.retrieval (350ms)
  |     |
  |     +-- Span: llm.call.claude (41000ms)
  |
  +-- Span: safeguarding_agent (3200ms)
  |     |
  |     +-- Span: llm.call.claude (3000ms)
  |
  +-- Span: delivery (80ms)
```

### 9.2 Metrics

Key metrics exported to Grafana via OpenTelemetry:

| Metric | Type | Alert threshold |
|---|---|---|
| `maestro.workflow.duration_ms` (by request_type) | Histogram | F5: >60s, F11.7: >30s, F11.8: >15s |
| `maestro.llm.call_duration_ms` (by model, agent) | Histogram | Claude: >30s, GPT-4o-mini: >10s |
| `maestro.llm.tokens_total` (by model, agent) | Counter | Daily cost exceeds budget threshold |
| `maestro.llm.cache_hit_ratio` | Gauge | <30% (indicates cache inefficiency) |
| `maestro.safeguarding.block_rate` | Gauge | >5% (indicates generation quality issue) |
| `maestro.safeguarding.wellbeing_alerts` | Counter | >3 per day per class (escalate to CPA) |
| `maestro.kmm.transitions_total` (by transition_type) | Counter | -- |
| `maestro.kmm.regression_rate` | Gauge | >15% (per ADR-002 KPI target) |
| `maestro.consent.denial_rate` (by consent_type) | Gauge | >50% for consent (a) (investigate UX) |
| `maestro.agent.error_rate` (by agent) | Gauge | >1% |
| `maestro.workflow.checkpoint_failures` | Counter | >0 (critical) |

### 9.3 Audit Log Integration

The audit log serves dual purposes:

1. **GDPR compliance** (F14.10): every operation on student data is logged with actor, timestamp, previous value, new value.

2. **Pedagogical transparency** (N7): every content generation, state transition, and safeguarding verdict is logged with the agent that produced it, the model version, and the prompt hash.

Audit log entries are:
- **Immutable**: append-only, UPDATE/DELETE denied by database trigger
- **Partitioned**: by month, for efficient retention management
- **Exportable**: CSV/JSON export via admin API
- **Pseudonymised post-erasure**: when a student exercises right to erasure (F14.9), audit entries are pseudonymised (name -> hash) but not deleted

### 9.4 Grafana Dashboards

| Dashboard | Audience | Key panels |
|---|---|---|
| **System Health** | DevOps | Workflow success/failure rates, agent error rates, infra metrics |
| **LLM Operations** | AI/ML Engineer | Token consumption by model/agent, cost projection, cache hit rates, latency percentiles |
| **Safeguarding** | CPA + Safeguarding Specialist | Block rate by category, wellbeing alerts, false positive rate |
| **Learning Outcomes** | CPA + Teacher | Transition volumes, regression rates, gap closure times, consolidation rates |
| **Privacy & Compliance** | Privacy Engineer | Consent rates, erasure requests, audit log volumes, pseudonymisation coverage |

---

## 10. MVP vs V1/V2 Scope

### 10.1 Agent Implementation Phases

| Agent | MVP | V1 | V2 |
|---|---|---|---|
| Orchestrator | Full | Expand for new channels | Expand for dialog |
| Identity & Consent Manager | Full (administered consent) | Self-service consent (SPID/QR) | Multi-course enrollment |
| Knowledge Map Manager | Full (D+7 retention) | D+3, D+7, D+21 + optional D+14 | FSRS adaptive scheduling |
| Curriculum Ingestion Agent | Full | Coverage gap detection (F2.12) | Auto-update from curriculum changes |
| Student Profiler Agent | Onboarding quiz + manual override | Behavioural adaptation (F3.3) | -- |
| Diagnostic Agent | Full | -- | -- |
| Content Orchestrator | Text channel only | + Podcast, Game, Visual (basic) | + Dialog, Visual (full) |
| Text Agent | Full | -- | -- |
| Bilingual Composer | 2 languages (uk, ar) | + 4 languages | + 6 languages (12 total) |
| Safeguarding Agent | Full (LLM-based) | + Rule-based pre-filter | + Wellbeing ML model |
| Feedback Loop Agent | Quiz processing, delivery logging | + Behavioural tracking | + Predictive analytics |
| Podcast Agent | Stub | Full | Cross-language variant |
| Game Agent | Stub | Full (XP, badges, streaks, quests) | Cooperative mode |
| Visual Agent | Stub | Basic (Mermaid diagrams) | Animations, interactive |
| Dialog Agent | Not implemented | Not implemented | Full (conversational tutoring) |

### 10.2 MVP Infrastructure

For MVP (1 school, ~30 students, 1 teacher):

- All agents run in a single FastAPI process on one Hetzner Cloud CCX33 server
- LangGraph StateGraph executes all agent nodes in-process
- Async tasks (transcription, batch generation) use Redis queues processed by Celery workers on the same server
- PostgreSQL (with AGE + pgvector) on the same server or a managed instance

No microservices, no Kubernetes, no service mesh. This is a monolith with clear internal boundaries (agent modules) that can be decomposed when scale demands it.

### 10.3 V1 Scaling Path

When V1 introduces 3 schools and 6 classes (~180 students):

- Separate the FastAPI/LangGraph application from PostgreSQL onto dedicated servers
- Add a second application server for redundancy (load-balanced)
- Move Celery workers to a dedicated server for background processing
- Consider Qdrant migration if vector count exceeds 5M

### 10.4 V2 Scaling Path

For multi-school deployment (>1000 students):

- Containerize with Docker, orchestrate with Kubernetes (Scaleway Kapsule)
- Agent nodes can be distributed across processes if needed
- Dialog Agent (real-time chat) may require WebSocket scaling (dedicated connection servers)
- PostgreSQL read replicas for dashboard queries

---

## Appendix A: Agent Dependency Graph

```
                        [FastAPI]
                            |
                     [Orchestrator]
                            |
              +-------------+-------------+
              |                           |
    [Identity & Consent         [Route Intent]
     Manager]                        |
              |           +----------+---------+----------+
              |           |          |         |          |
              |     [Curriculum  [Diagnostic [Student  [Gap Closure
              |      Ingestion]   Agent]     Profiler]  / Retention]
              |           |          |         |          |
              |           |          +----+----+          |
              |           |               |               |
              |           |          [KMM: state transitions]
              |           |               |
              |           +-------+-------+
              |                   |
              |          [Content Orchestrator]
              |                   |
              |     +------+------+------+------+
              |     |      |      |      |      |
              |  [Text] [Podcast [Visual [Game  [Dialog
              |  Agent]  Agent]  Agent]  Agent]  Agent]
              |     |      |      |      |      |
              |     +------+------+------+------+
              |                   |
              |          [Bilingual Composer]
              |                   |
              |          [Safeguarding Agent]  <-- MANDATORY, NON-BYPASSABLE
              |                   |
              |          [Student Delivery]
              |                   |
              |          [Feedback Loop Agent]
              |                   |
              |          [KMM: state updates]
              |                   |
              |          [Student Profiler: engagement data (V1)]
              |
              +-- gates every flow at entry
```

## Appendix B: Latency Budget Breakdown

| Flow | Target (N4) | Budget allocation |
|---|---|---|
| **Recovery document (F5)** | <=60s | RAG retrieval: 2s, LLM generation (Claude streaming): 45s, Bilingual: 8s, Safeguarding: 5s |
| **Remediation path (F11.7)** | <=30s | Material selection: 2s, LLM generation: 20s, Safeguarding: 5s, delivery: 3s |
| **Mini-quiz generation (F11.8)** | <=15s | Question bank lookup: 1s, LLM generation (if needed): 10s, Safeguarding: 3s, delivery: 1s |
| **Chat response (V2)** | <=3s P95 | RAG: 500ms, LLM streaming (Claude): 2s, Safeguarding (lightweight): 500ms |

Streaming is used for all student-facing LLM outputs. The student sees progressive rendering while the full response is being generated. The latency targets measure time to first meaningful chunk, not time to completion (except for quizzes, which are delivered as a complete unit).

## Appendix C: Consent-Degradation Matrix

| Consent denied | Affected features | Degraded behavior |
|---|---|---|
| (a) Profiling | F3 profile, personalised content ranking | Uniform profile (20% each dimension), no onboarding quiz, no behavioural tracking. Content is still generated but not personalised to channel preference. |
| (b) Native language | F13 bilingual content | Monolingual content only (official course language). Student can still set UI language (N9) without consent (b). |
| (c) Family comms | F11.16 family report, family notifications | No monthly report. No family notifications. Teacher can still view student progress. |
| (d) Cross-year history | Year-to-year KMM continuity | KMM reset at year boundary. Prior year data deleted. Each year starts fresh. |
| (e) Research | Aggregated analytics | Student's data excluded from all aggregate analytics and research datasets. |
| All denied | Core learning cycle | System operates in fully anonymous mode: uniform profile, monolingual, no family reports, no history, no research inclusion. The core cycle (lesson -> verification -> gap -> recovery -> quiz -> retention) still functions. |

---

*Document version: 1.0. Task T2.1 of the MAESTRO delivery DAG. Subject to review by MSTR-02 (CTA), MSTR-03 (CPA), and MSTR-20 (QA Sentinel) before ratification.*
