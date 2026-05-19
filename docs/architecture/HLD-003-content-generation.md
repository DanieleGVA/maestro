# HLD-003: Content Generation & Multimodal Architecture

**Status**: Proposed
**Date**: 2026-05-18
**Author**: MSTR-06 (Content Generation & Multimodal Architect)
**Reviewers required**: MSTR-02 (CTA), MSTR-03 (CPA), MSTR-10 (AI/ML Engineer), MSTR-20 (QA Sentinel)
**Related ADRs**: ADR-001 (Tech Stack), ADR-002 (Pedagogical Model)
**Related HLDs**: HLD-001 (Multi-Agent System), HLD-002 (Knowledge Graph), HLD-004 (Data & Mastery State)
**Task**: T2.3

---

## 1. Overview

### 1.1 Purpose

This document specifies the content generation architecture of MAESTRO: how the system produces personalised learning content across five channels (text, podcast, visual, game, dialog), how prompts are structured and managed, how the Bilingual Composer and Safeguarding Agent integrate into every generation pipeline, and how caching and batch pre-generation control costs.

### 1.2 Design Philosophy

1. **Text-first, multi-channel future.** The Text Agent is the only fully implemented content generator in MVP. Podcast, Visual, Game, and Dialog agents are V1/V2 and are specified here as interface contracts and design-only documents. This avoids premature engineering while ensuring no MVP decision blocks future channels.

2. **Prompt as a versioned artefact.** Every prompt template has an ID, a version, and a schema. Prompts are never constructed as ad-hoc string concatenations. This enables audit (N7), reproducibility, cost tracking, and progressive improvement.

3. **RAG with authorial priority.** Content generation is always grounded in source materials retrieved from the vector store (HLD-002 `lesson_chunks`). Teacher-authored content takes priority over textbook content, which takes priority over external sources (F2.5). The LLM generates *around* retrieved material, not from general knowledge.

4. **Safeguarding is structural, not optional.** Every content output -- text, quiz, podcast script, visual description -- passes through the Safeguarding Agent before reaching a student. This is enforced by the LangGraph graph topology (HLD-001, Section 3.10), not by developer discipline.

5. **Pseudonymisation at the boundary.** Prompts never contain PII. The LLMGateway (HLD-001, Section 6) strips student names, teacher names, school names, and class identifiers before prompt construction. Native language is referenced by ISO code only (`uk`, `ar`), never associated with a student identity in any prompt.

### 1.3 Channel Strategy

| Channel | Agent | Phase | Generates |
|---|---|---|---|
| **Text** | Text Agent | MVP | Recovery documents (F5), remediation paths (F11.7), quiz feedback |
| **Quiz** | Quiz Generation Engine | MVP | Mini-quizzes (F11.8), retention checks (F11.10) |
| **Podcast** | Podcast Agent | V1 | Two-voice audio episodes (F6), transcripts |
| **Game** | Game Agent | V1 | Quests, badge descriptions, XP events (F7) |
| **Visual** | Visual Agent | V1/V2 | Diagrams, annotated code visualisations (F10) |
| **Dialog** | Dialog Agent | V2 | Conversational tutoring, rubber-duck exercises (F10.4) |

### 1.4 Integration Context

The Content Orchestrator sits between the main Orchestrator (HLD-001) and the channel-specific agents. It receives a `ContentRequest` from the Orchestrator, determines which channels to activate based on the student's content-adaptation profile (ADR-002), retrieves source materials via RAG (HLD-002), dispatches to channel agents, and passes the output through the Bilingual Composer (if applicable) and the Safeguarding Agent before delivery.

```
[Main Orchestrator (HLD-001)]
        |
        v
[Content Orchestrator]
        |
   +----+----+----+----+----+
   |    |    |    |    |    |
  Text Quiz Podcast Visual Game Dialog
   |    |    |    |    |    |
   +----+----+----+----+----+
        |
        v
[Bilingual Composer]  (if consent (b) active)
        |
        v
[Safeguarding Agent]  (MANDATORY, NON-BYPASSABLE)
        |
        v
[Student Delivery / Teacher Review]
```

---

## 2. Content Orchestrator

### 2.1 Channel Selection Logic

The Content Orchestrator decides which channels to activate for a given content request. The logic uses the student's content-adaptation profile (a 5-float vector validated in ADR-002) as soft weights, not hard filters.

#### Selection Algorithm

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class ContentAdaptationProfile:
    visuale: float       # 0.0-1.0
    audio: float         # 0.0-1.0
    pratico: float       # 0.0-1.0
    lettura: float       # 0.0-1.0
    dialogo: float       # 0.0-1.0
    tone: Literal["confidenziale", "neutro", "formale"]
    length: Literal["sintesi", "approfondimento"]

CHANNEL_MAP = {
    "text":     "lettura",
    "audio":    "audio",
    "visual":   "visuale",
    "exercise": "pratico",
    "dialog":   "dialogo",
}

AVAILABLE_CHANNELS = {
    "mvp": {"text", "quiz"},
    "v1":  {"text", "quiz", "audio", "exercise", "visual"},
    "v2":  {"text", "quiz", "audio", "exercise", "visual", "dialog"},
}

def select_channels(
    profile: ContentAdaptationProfile,
    request_type: str,
    attempt_number: int,
    phase: str = "mvp",
) -> list[str]:
    """
    Returns ordered list of channels to generate.
    Enforces minimum diversity: >= 2 types for recovery missions (ADR-002).
    """
    available = AVAILABLE_CHANNELS[phase]

    # Quiz is always included for closure/retention requests
    if request_type in ("gap_closure", "retention_check"):
        result_set = {"quiz"}
    else:
        result_set = set()

    # Rank content channels by profile weight
    ranked = sorted(
        [(ch, getattr(profile, CHANNEL_MAP[ch]))
         for ch in ("text", "audio", "visual", "exercise", "dialog")
         if ch in available],
        key=lambda x: x[1],
        reverse=True,
    )

    if attempt_number <= 1:
        # First attempt: use the highest-weighted channel
        result_set.add(ranked[0][0])
    else:
        # Retry: rotate to next-best channel to provide variety (F11.7)
        idx = (attempt_number - 1) % len(ranked)
        result_set.add(ranked[idx][0])

    # Minimum diversity: recovery missions need >= 2 content types (ADR-002)
    if request_type == "gap_closure" and len(result_set) < 2:
        for ch_name, _ in ranked:
            if ch_name not in result_set:
                result_set.add(ch_name)
                break

    # MVP fallback: if no available channel matched, always fall back to text
    if not result_set.intersection(available):
        result_set = {"text"}

    return sorted(result_set)
```

#### Authorial Priority Enforcement (F2.5)

Before dispatching to any channel agent, the Content Orchestrator retrieves source materials using the RAG surface defined in HLD-002:

```python
async def retrieve_sources(
    course_id: str,
    node_ids: list[str],
    query_embedding: list[float],
    top_k: int = 10,
) -> list[SourceMaterial]:
    """
    Retrieve source materials with authorial priority:
      Priority 1: Teacher lessons (material_type = 'lesson')
      Priority 2: Textbook (material_type = 'textbook')
      Priority 3: Exercises / notes (material_type in ('exercise', 'notes'))
      Priority 4: External sources (material_type in ('external_link', 'article'))
    """
    # Query pgvector for semantically similar chunks,
    # filtered to confirmed concept-node links
    all_chunks = await vector_search(
        course_id=course_id,
        node_ids=node_ids,
        query_embedding=query_embedding,
        similarity_threshold=0.70,
        limit=top_k * 3,  # over-fetch to allow priority filtering
    )

    # Group by priority tier
    tiers = {1: [], 2: [], 3: [], 4: []}
    for chunk in all_chunks:
        if chunk.material_type == "lesson":
            tiers[1].append(chunk)
        elif chunk.material_type == "textbook":
            tiers[2].append(chunk)
        elif chunk.material_type in ("exercise", "notes", "code_example"):
            tiers[3].append(chunk)
        else:
            tiers[4].append(chunk)

    # Build final list: fill from highest priority first
    result = []
    for tier in (1, 2, 3, 4):
        for chunk in tiers[tier]:
            result.append(chunk)
            if len(result) >= top_k:
                return result

    return result
```

Each source material injected into a prompt carries a `source_tier` label so the LLM knows which source to prefer when information conflicts.

### 2.2 Content Request Schema

The Content Orchestrator receives this from the main Orchestrator:

```python
class ContentRequest:
    request_id: str                    # UUID, correlation ID
    request_type: Literal[
        "review_document",             # Post-verification review (F5)
        "gap_closure",                 # Recovery mission content (F11.7)
        "quiz_generation",             # Mini-quiz (F11.8)
        "retention_check",             # Retention check quiz (F11.10)
    ]
    student_pseudo_id: str             # Pseudonymised student ID
    course_id: str
    course_language: str               # e.g. "it"
    target_nodes: list[TargetNode]     # [{node_id, node_type, state, error_description?}]
    content_profile: ContentAdaptationProfile
    bilingual: BilingualConfig         # {active: bool, language_code?: str}
    attempt_number: int                # 1 = first attempt, 2+ = retry with varied approach
    teacher_question_bank_ids: list[str]  # Pre-approved quiz questions for these nodes
    source_materials: list[SourceMaterial]  # RAG-retrieved, priority-ordered
```

### 2.3 Content Response Schema

All channel agents return a standardised envelope:

```python
class ContentResponse:
    request_id: str
    channel: str                       # "text", "quiz", "audio", etc.
    content: ContentPayload            # Channel-specific structured content
    metadata: ContentMetadata

class ContentMetadata:
    model_id: str                      # e.g. "claude-opus-4-20250514"
    prompt_template_id: str            # e.g. "text_review_v3"
    prompt_template_version: int
    prompt_hash: str                   # SHA-256 of the rendered prompt
    input_tokens: int
    output_tokens: int
    latency_ms: int
    sources_used: list[SourceRef]      # [{material_id, chunk_id, tier}]
    cache_hit: bool
    generated_at: str                  # ISO-8601 timestamp
```

This envelope enables:
- **Audit trail** (N7): every piece of content is traceable to a prompt version and model
- **Cost tracking** (R9): per-generation token counts feed the Grafana LLM Operations dashboard
- **Reproducibility**: same prompt hash + same model version = verifiable output

---

## 3. Text Agent (MVP)

### 3.1 Prompt Architecture

The Text Agent uses a three-layer prompt structure:

```
SYSTEM PROMPT (static, versioned)
  |
  +-- Role definition
  +-- Output format constraints
  +-- Safeguarding pre-instructions
  +-- Tone and style instructions
  |
CONTEXT BLOCK (dynamic, per-request)
  |
  +-- Content-adaptation profile summary
  +-- Source materials (RAG-retrieved, priority-labelled)
  +-- KG context (concept hierarchy, prerequisites)
  |
TASK BLOCK (dynamic, per-request)
  |
  +-- Specific generation instruction
  +-- Error descriptions (for review documents)
  +-- Bloom's level target (for quizzes)
  +-- Language / bilingual instructions
```

#### System Prompt (shared across all Text Agent calls)

```
prompt_template_id: "text_system_v1"
version: 1

---

You are a learning tutor for Italian high school IT students. You generate
personalised study materials that help students understand concepts they
struggled with.

ABSOLUTE RULES — NEVER VIOLATE:
1. NEVER reference the student's real name or any personal details.
   You only know them as {student_pseudo_id}.
2. NEVER compare this student with other students, class averages, or
   rankings. Every reference is to the student's own journey.
3. NEVER use punitive, shaming, or discouraging language. Errors are
   opportunities. Use framing like "questo concetto ha bisogno di un
   altro giro" instead of "hai sbagliato."
4. NEVER include trick questions, sarcasm, irony that could be misread,
   or age-inappropriate content. Your audience is 13-19 years old.
5. NEVER fabricate information. If the source materials do not cover a
   point, say so explicitly rather than inventing an explanation.
6. ALWAYS ground your explanations in the provided source materials.
   Prioritise Teacher Lesson sources (TIER 1) over textbook (TIER 2)
   over external sources (TIER 3).
7. When showing code, ALWAYS include both the ERRONEOUS version (marked
   with [ERRATO]) and the CORRECT version (marked with [CORRETTO]).
8. Content must be in {course_language} unless bilingual mode instructions
   say otherwise.

OUTPUT FORMAT: You MUST return valid JSON matching the schema provided in
the task block. No markdown outside the JSON structure. No preamble.
```

### 3.2 Prompt Templates

#### 3.2.1 Review Document (F5, post-verification)

```
prompt_template_id: "text_review_document_v1"
version: 1
trigger: request_type == "review_document"
model_routing: claude (primary), gpt-4o-mini (fallback)

---

CONTEXT:
Student {student_pseudo_id} has gaps in the following concepts after a
verification.

Content adaptation profile:
- Tone: {profile.tone}
- Length: {profile.length} ({length_description})
- Analogy interests: {analogy_interests}

Source materials (ordered by authorial priority):
{for source in sources}
  [TIER {source.tier}] ({source.material_type}):
  ---
  {source.content}
  ---
{endfor}

KG context — prerequisite chain for this concept:
{prerequisite_summary}

TASK:
For EACH of the following concept gaps, generate a review block with
exactly 4 sections:

{for node in target_nodes}
Concept: {node.label_it} (ID: {node.node_id})
Student's error: {node.error_description}
{endfor}

Each block MUST have:
1. "il_tuo_errore" — Show what went wrong. If code is involved, show the
   erroneous code with [ERRATO] marker. Use a relatable analogy from
   {analogy_domain_1} or {analogy_domain_2} (VARY the domain across
   blocks — do not reuse the same analogy source for every block).
2. "perche_succede" — Explain WHY this error occurs. Root cause, not
   just symptoms. Ground in source materials.
3. "come_si_fa_giusto" — Show the correct approach. If code is involved,
   show corrected code with [CORRETTO] marker. Step-by-step if length
   mode is "approfondimento".
4. "ricordati" — One memorable rule or mnemonic. Brief. Sticky.

LENGTH GUIDANCE:
- "sintesi": 2-3 concepts per document, concise explanations (150-250
  words per block)
- "approfondimento": 6-8 concepts, detailed step-by-step (400-600 words
  per block)

TONE: {tone_instruction}

Return JSON:
{
  "blocks": [
    {
      "concept_node_id": "string",
      "concept_label": "string",
      "il_tuo_errore": {
        "text": "string (markdown)",
        "code_errato": "string | null",
        "analogy_domain": "string"
      },
      "perche_succede": {
        "text": "string (markdown)",
        "source_refs": ["material_id:chunk_id", ...]
      },
      "come_si_fa_giusto": {
        "text": "string (markdown)",
        "code_corretto": "string | null",
        "source_refs": ["material_id:chunk_id", ...]
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

**Tone instructions** (injected based on `profile.tone`):

| Tone | `{tone_instruction}` value |
|---|---|
| `confidenziale` | "Usa il 'tu'. Frasi brevi, tono leggero, qualche battuta. Come un compagno di classe piu' esperto che ti aiuta. Esempio: 'Allora, qui il problema e' che hai dimenticato di...' " |
| `neutro` | "Usa il 'tu'. Tono calmo e chiaro, senza battute ma senza formalita'. Esempio: 'In questo caso, l'errore si verifica perche'...' " |
| `formale` | "Usa il 'Lei'. Frasi articolate, terminologia precisa. Esempio: 'L'errore riscontrato nel codice e' riconducibile a...' " |

**Analogy domain selection** (from student profile interests):

The profile stores a list of interest domains (e.g., `["sport_calcio", "gaming", "cucina"]`). The prompt injects two domains and instructs the LLM to vary across blocks. If no interests are set, the system uses a default rotation: `["vita_quotidiana", "tecnologia", "scuola"]`.

#### 3.2.2 Remediation Path (F11.7, gap closure content)

```
prompt_template_id: "text_remediation_path_v1"
version: 1
trigger: request_type == "gap_closure"
model_routing: claude (primary), gpt-4o-mini (fallback)

---

CONTEXT:
Student {student_pseudo_id} is working on closing a gap in:
  Concept: {node.label_it}
  Current state: in_recupero
  Attempt: {attempt_number} ({"primo tentativo" if 1 else "tentativo " + str(attempt_number) + " — varia l'approccio"})

Content adaptation profile:
- Tone: {profile.tone}
- Length: {profile.length}
- Analogy interests: {analogy_interests}

Source materials (ordered by authorial priority):
{for source in sources}
  [TIER {source.tier}] ({source.material_type}):
  ---
  {source.content}
  ---
{endfor}

Prerequisite concepts (the student should already know these):
{for prereq in prerequisites}
  - {prereq.label_it}: state = {prereq.state}
{endfor}

{if attempt_number > 1}
IMPORTANT: This is retry attempt {attempt_number}. The student did not
pass the quiz on the previous attempt. You MUST use a DIFFERENT
explanatory approach than a standard textbook explanation:
- Try a different analogy domain
- Use a more concrete, hands-on example
- Break the concept into smaller sub-steps
- If the concept involves code, show a minimal working example first,
  then build complexity
{endif}

TASK:
Generate a focused remediation document for this single concept.

Structure:
1. "aggancio" — Connect to what the student already knows (reference
   prerequisite concepts). Brief, motivating opener.
2. "spiegazione" — Core explanation grounded in source materials.
   Use analogy from {analogy_domain}. If code, show working example.
3. "esempio_pratico" — A concrete, runnable example. If the concept is
   code-related, the example must be syntactically valid and complete
   enough to execute.
4. "verifica_veloce" — A single self-check question (not graded) to
   help the student confirm understanding before attempting the quiz.
5. "prossimo_passo" — Encouraging closing. "Quando ti senti pronto,
   prova il quiz!"

Return JSON:
{
  "concept_node_id": "string",
  "concept_label": "string",
  "aggancio": { "text": "string (markdown)" },
  "spiegazione": {
    "text": "string (markdown)",
    "source_refs": ["material_id:chunk_id", ...]
  },
  "esempio_pratico": {
    "text": "string (markdown)",
    "code": "string | null",
    "language": "string | null"
  },
  "verifica_veloce": {
    "question": "string",
    "hint": "string"
  },
  "prossimo_passo": { "text": "string" }
}
```

### 3.3 Tone & Length Adaptation

Tone and length are injected into every prompt via the context block. The implementation is parametric, not template-branching: there is one prompt template per content type, with tone/length as variables.

| Dimension | Values | Prompt effect |
|---|---|---|
| **Tone** | `confidenziale` | "tu", short sentences, occasional humour, peer-like register |
| | `neutro` | "tu", calm, clear, no humour, no formality |
| | `formale` | "Lei", precise, articulated, technical register |
| **Length** | `sintesi` | 2-3 concepts, 150-250 words per block, high-level explanations |
| | `approfondimento` | 6-8 concepts, 400-600 words per block, step-by-step detail |

The tone is always subject to the safeguarding constraint: even in `confidenziale` mode, no put-downs, no offensive language, no sarcasm that could be misread by a 13-year-old.

### 3.4 Code Highlighting Strategy

The Text Agent returns code blocks with semantic markers that the frontend renders:

```json
{
  "il_tuo_errore": {
    "code_errato": "<?php\nsession_start();\n// Missing session_regenerate_id()\n$_SESSION['user'] = $user;",
    "text": "..."
  },
  "come_si_fa_giusto": {
    "code_corretto": "<?php\nsession_start();\nsession_regenerate_id(true);\n$_SESSION['user'] = $user;",
    "text": "..."
  }
}
```

**Frontend rendering contract:**

| JSON field | Frontend rendering |
|---|---|
| `code_errato` | Yellow border (`#FDD835`), label "ERRATO" (text, not just colour for accessibility F9.3) |
| `code_corretto` | Green border (`#43A047`), label "CORRETTO" |
| Code language | Syntax-highlighted using a code highlighter. Language inferred from context or explicitly tagged in the `language` field. |
| Side-by-side | Desktop: two-column layout (errato left, corretto right). Mobile: stacked (errato above, corretto below). |

Accessibility: labels "ERRATO" and "CORRETTO" are always present as text, never conveyed by colour alone (F9.3, WCAG 2.1 AA).

### 3.5 Output Format

The Text Agent returns structured JSON. This is parsed by the frontend into the visual layout defined in SCR-ST-08. The JSON structure for each content type is defined in the prompt templates above (sections 3.2.1 and 3.2.2).

**Storage**: Generated text documents are stored in the `content.generated_content` table (HLD-004) with:
- `content_type = 'recovery_document'` or `'remediation_path'`
- `content` = the full JSON payload
- `embedding` = vector embedding of the content (for semantic cache, ADR-001)
- `version` = incremented on regeneration (F15.3)

**Teacher modification (F5.7)**: When a teacher modifies a generated document (F12.5), the system:
1. Stores the original as `status = 'archived'`
2. Creates a new version with the teacher's edits and `modified_by = teacher_id`
3. Sets the `teacher_reviewed = true` flag, which triggers the "Rivisto dal Prof." badge in the frontend

---

## 4. Bilingual Composer

### 4.1 Architecture

The Bilingual Composer operates as a **post-generation translation/adaptation pipeline**, not a parallel generation system. The rationale:

- **Single source of truth**: Content is generated in the official course language, ensuring pedagogical consistency. The bilingual version is derived from it.
- **Efficiency**: Parallel generation in two languages would double LLM costs and risk semantic divergence between columns.
- **Quality control**: The official-language version is the authoritative text. The native-language column is additive (F13.8: bilingualism never replaces the official language).

```
[Text Agent generates in course_language]
        |
        v
[Bilingual Composer]
        |
        +-- Load controlled glossary for target language
        |
        +-- LLM translation with glossary constraints
        |
        +-- Structure into dual-column format
        |
        v
[BilingualDocument]
```

#### Bilingual Composer Prompt

```
prompt_template_id: "bilingual_compose_v1"
version: 1
model_routing: claude (primary) — translation quality is critical

---

SYSTEM:
You are a bilingual educational content adapter. You translate Italian
educational content to {target_language_name} ({target_language_code})
for a high school student studying IT.

RULES:
1. Preserve the EXACT meaning of the original. Do not add, remove, or
   reinterpret.
2. Technical terms MUST follow the controlled glossary below. If a term
   is in the glossary, use EXACTLY the glossary translation. If not,
   transliterate/translate using standard CS terminology in the target
   language, and flag it for glossary review.
3. Code blocks are NOT translated — they remain in the programming
   language. Only the explanatory text around code is translated.
4. Analogies: adapt culturally where appropriate, but NEVER use
   national stereotypes, religious references, or politically
   sensitive examples. If the original analogy does not translate
   well, provide a culturally neutral alternative.
5. NEVER associate this content with any student identity. You are
   translating content for language code {target_language_code}.
6. If the content references Italian cultural context (e.g., "come
   ordinare una pizza"), you MAY keep the Italian reference AND add a
   parallel reference from the target culture, but NEVER remove the
   Italian reference (the student must learn to navigate Italian
   cultural context).

GLOSSARY ({target_language_code}):
{for term in glossary}
  {term.italian} -> {term.translated} ({term.context_note})
{endfor}

CONTENT TO TRANSLATE:
{original_content_json}

Return JSON with the same structure as the input, but each text field
becomes an object with "ufficiale" (original) and "nativa" (translated):

{
  "blocks": [
    {
      "concept_node_id": "...",
      "il_tuo_errore": {
        "text": {
          "ufficiale": "original Italian text",
          "nativa": "translated text"
        },
        "code_errato": "unchanged",
        "technical_terms": [
          {"ufficiale": "sessione", "nativa": "сесія"}
        ]
      },
      ...
    }
  ]
}
```

### 4.2 Technical Glossary Management

Each supported language has a controlled glossary of IT technical terms stored in PostgreSQL:

```sql
-- Glossary table (in content schema)
CREATE TABLE content.bilingual_glossary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    language_code TEXT NOT NULL,        -- 'uk', 'ar', etc.
    term_it TEXT NOT NULL,              -- Italian term
    term_translated TEXT NOT NULL,      -- Translated term
    context_note TEXT,                  -- Usage context for disambig
    domain TEXT DEFAULT 'informatica',  -- Subject domain
    verified BOOLEAN NOT NULL DEFAULT false,  -- Reviewed by native speaker
    verified_by TEXT,                   -- Reviewer identifier
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (language_code, term_it, domain)
);

CREATE INDEX idx_glossary_lang ON content.bilingual_glossary (language_code);
```

**MVP glossary scope**: Italian-Ukrainian and Italian-Arabic glossaries for core IT concepts (variables, loops, functions, sessions, databases, authentication). Approximately 200-300 terms per language. Pre-populated by MSTR-18 (Localization & Bilingualism Lead) before MVP launch.

**Glossary injection**: The Bilingual Composer loads the full glossary for the target language before each generation call. For MVP scale (~300 terms), this fits comfortably in the prompt context. For V1 (6 languages), a filtered glossary (only terms relevant to the current concept domain) is injected.

### 4.3 Cultural Localisation

Analogies are the most culturally sensitive element. The Bilingual Composer handles them with explicit constraints:

| Rule | Implementation |
|---|---|
| No national stereotypes (F13.16) | Prompt instruction: "NEVER use national stereotypes, religious references, or politically sensitive examples" |
| Dual-context analogies (F13.15) | When adapting an Italian analogy, keep the Italian reference AND add a culturally neutral or target-culture parallel |
| No removal of Italian context | The student lives in Italy and must navigate Italian culture; removing Italian references is counter-productive |
| Flagging for review | If the LLM adapts an analogy, it must tag it as `"culturally_adapted": true` in the output for quality review (F13.17) |

**Localised analogy validation pipeline** (V1):

1. LLM generates adapted analogy
2. If `culturally_adapted: true`, the analogy is queued for native-speaker review
3. Approved analogies enter a validated analogy bank per language
4. Future generations for the same concept can reuse validated analogies

### 4.4 Output Format

The Bilingual Composer outputs a dual-column structure:

```json
{
  "layout": "dual_column",
  "columns": {
    "left": {
      "language": "it",
      "label": "Italiano"
    },
    "right": {
      "language": "uk",
      "label": "Українська"
    }
  },
  "blocks": [
    {
      "concept_node_id": "...",
      "sections": {
        "il_tuo_errore": {
          "left": "Il tuo codice non chiama session_regenerate_id()...",
          "right": "Твій код не викликає session_regenerate_id()...",
          "technical_terms": [
            {"left": "sessione", "right": "сесія"},
            {"left": "rigenerazione ID", "right": "регенерація ID"}
          ]
        }
      }
    }
  ],
  "glossary_used": ["sessione", "variabile", "funzione"],
  "culturally_adapted_flags": [
    {"block_index": 0, "section": "perche_succede", "adapted": true}
  ]
}
```

**Frontend rendering**: Left column occupies 50% width on desktop; right column 50%. On mobile, columns stack (official first, native below), with a toggle to show/hide native column. Technical terms are visually distinguished (bold, with tooltip showing both translations).

**Constraint (F13.8)**: The official-language column is ALWAYS visible. The native column is additive and dismissible. The student cannot hide the official column.

---

## 5. Quiz Generation Engine

### 5.1 Question Generation

The Quiz Generation Engine follows the five-layer quality framework established in ADR-002, Section 5.

#### Source Priority

1. **Teacher question bank** (Priority 1): Questions pre-authored by the teacher for specific micro-nodes. Stored in `content.teacher_question_bank`.
2. **Vetted AI-generated questions** (Priority 2): Previously generated questions that have been teacher-reviewed and approved.
3. **Fresh AI-generated questions** (Priority 3): New questions generated on-demand. These require first-use teacher review (MVP) or statistical validation (V2).

#### Bloom's Taxonomy Targeting (per ADR-002)

| Quiz purpose | Student state | Bloom's level | Prompt instruction |
|---|---|---|---|
| Closure quiz (1st attempt) | `in_recupero` | Remember + Understand | "Generate questions that test recall and basic comprehension." |
| Closure quiz (2nd+ attempt) | `in_recupero` (retry) | Understand + Apply | "Generate questions that test comprehension and ability to apply the concept." |
| Retention D+3 (V1) | `da_consolidare` | Remember + Understand | "Generate recall-focused questions to verify retention." |
| Retention D+7 | `da_consolidare` | Understand + Apply | "Generate questions testing application of the concept in a new context." |
| Retention D+21 (V1) | `da_consolidare` | Apply + Analyze | "Generate questions requiring the student to apply and reason about the concept." |

#### Quiz Generation Prompt

```
prompt_template_id: "quiz_generation_v1"
version: 1
model_routing: claude (primary) — assessment quality is critical

---

SYSTEM:
You are generating a mini-quiz for an Italian high school IT student.
The quiz assesses understanding of a specific concept.

ABSOLUTE RULES:
1. Questions MUST be answerable using ONLY the provided source materials.
   No general knowledge questions. Every question is RAG-anchored.
2. Questions MUST target the specific micro-node: {node.label_it}.
   Do NOT test adjacent concepts.
3. Distractors MUST be plausible but clearly wrong — no trick questions,
   no ambiguous wording. Each distractor must be wrong for a specific,
   statable reason.
4. Language level: {language_level_instruction}
5. The quiz is in {course_language} ONLY (F13.19 — no bilingual quizzes).
6. No cultural references, humor, or colloquialisms in questions.
   Assessment is formal even when learning tone is playful.
7. No timer references. No anxiety-inducing language.
8. Code in questions must be syntactically valid and complete enough to
   evaluate. Use the language/framework relevant to the course.

CONTEXT:
Concept: {node.label_it} (micro-node ID: {node.node_id})
Target Bloom's level: {bloom_level}
Course language: {course_language}

Source materials (for anchoring questions):
{for source in sources}
  [{source.material_type}]:
  ---
  {source.content}
  ---
{endfor}

TASK:
Generate {question_count} multiple-choice questions.

Each question:
- 1 stem (clear, self-contained)
- 4 options (A, B, C, D) — exactly one correct
- 1 correct_answer (letter)
- 1 explanation (shown after answering, encouraging tone)
- 1 bloom_level (the actual Bloom's level this question tests)
- 1 distractor_rationale for each wrong option (for teacher review,
  not shown to student)

Return JSON:
{
  "quiz": {
    "concept_node_id": "string",
    "concept_label": "string",
    "target_bloom_level": "string",
    "questions": [
      {
        "question_id": "string (UUID)",
        "stem": "string",
        "options": {
          "A": "string",
          "B": "string",
          "C": "string",
          "D": "string"
        },
        "correct_answer": "A|B|C|D",
        "explanation_correct": "string (encouraging, shown when correct)",
        "explanation_incorrect": "string (encouraging, shown when wrong)",
        "bloom_level": "remember|understand|apply|analyze",
        "distractor_rationales": {
          "A": "string|null (null if correct)",
          "B": "string|null",
          "C": "string|null",
          "D": "string|null"
        },
        "source_refs": ["material_id:chunk_id"]
      }
    ]
  }
}
```

### 5.2 Quality Validation Pipeline

The five-layer quality framework from ADR-002:

```
[Quiz Generation (LLM)]
        |
        v
Layer 1: RAG CONSTRAINT CHECK
  - Every question stem must reference content from source_materials
  - Reject questions with no source_refs
        |
        v
Layer 2: STRUCTURAL VALIDATION (automated)
  - Exactly 4 options per question
  - Exactly 1 correct answer
  - No duplicate or near-duplicate options (Levenshtein distance > 0.3)
  - Correct answer is unambiguous
  - Stem is self-contained (no "as mentioned above" references)
  - Code snippets are syntactically valid (basic lint check)
        |
        v
Layer 3: TEACHER REVIEW (human-in-the-loop, MVP)
  - First-use questions are presented to the teacher
  - Teacher sees: stem, options, correct answer, explanations,
    distractor rationales, source references
  - Actions per question: "Approva" / "Modifica" / "Scarta"
  - Approved questions enter the vetted bank for reuse without
    per-use approval
  - V1: previously approved questions skip this layer
  - V2: statistical validation replaces per-question review for
    questions with sufficient response data
        |
        v
Layer 4: SAFEGUARDING CHECK
  - Standard Safeguarding Agent review (Section 8)
  - Additional quiz-specific checks:
    - No anxiety-inducing language
    - No trick questions (confirmed via distractor_rationales)
    - No cultural/personal references
    - Feedback text is encouraging regardless of correctness
        |
        v
Layer 5: PER-QUESTION FEEDBACK (post-delivery)
  - After student answers, show:
    - Their answer
    - The correct answer
    - explanation_correct or explanation_incorrect
  - Tone: always encouraging
  - Incorrect: "Non e' la risposta giusta, ma ci sei vicino. Ecco
    cosa succede..."
  - Correct: "Esatto! Questo concetto e'..."
```

**Anti-patterns enforced** (per ADR-002):

| Anti-pattern | Enforcement |
|---|---|
| Timer pressure | No countdown. `time_spent_ms` recorded silently for analytics, never shown during quiz. |
| Negative scoring | Score = correct / total. No deduction for wrong answers. |
| Red screen on failure | Quiz results use arancione (#FB8C00) for incomplete mastery, never red. Green (#43A047) for success. |
| Public leaderboard | Quiz results are private. No class-level quiz aggregation visible to students. |
| Trick questions | Prompt prohibits them. Structural validation checks distractor_rationales for "trick" patterns. |
| Repeated identical questions | No-repeat-within-3-sessions constraint. Question bank must contain >= 3x quiz size per micro-node. |

### 5.3 Output Format

```json
{
  "quiz_id": "uuid",
  "concept_node_id": "uuid",
  "concept_label": "Sessioni PHP - session_start()",
  "bloom_level_target": "understand",
  "question_count": 4,
  "questions": [
    {
      "question_id": "uuid",
      "stem": "Quale funzione PHP deve essere chiamata prima di accedere a qualsiasi variabile di sessione?",
      "options": {
        "A": "session_start()",
        "B": "session_begin()",
        "C": "start_session()",
        "D": "ini_set('session')"
      },
      "correct_answer": "A",
      "explanation_correct": "Esatto! session_start() inizializza la sessione e rende disponibile l'array $_SESSION.",
      "explanation_incorrect": "La risposta corretta e' session_start(). Questa funzione inizializza la sessione PHP e rende disponibile l'array $_SESSION. Le altre opzioni non sono funzioni PHP valide per questo scopo.",
      "bloom_level": "remember",
      "source_refs": ["mat-uuid:chunk-uuid"]
    }
  ],
  "metadata": {
    "generated_by": "quiz_generation_v1",
    "model_id": "claude-opus-4-20250514",
    "vetted": false,
    "first_use": true
  }
}
```

**Storage**: Quizzes are stored in `content.generated_content` with `content_type = 'quiz'`. Individual questions are also indexed in `content.question_bank` for reuse:

```sql
CREATE TABLE content.question_bank (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES core.courses(id),
    node_id UUID NOT NULL,                -- micro-node ID
    bloom_level TEXT NOT NULL,
    stem TEXT NOT NULL,
    options JSONB NOT NULL,               -- {"A": "...", "B": "...", ...}
    correct_answer TEXT NOT NULL,
    explanation_correct TEXT NOT NULL,
    explanation_incorrect TEXT NOT NULL,
    source_refs JSONB,
    source_type TEXT NOT NULL CHECK (source_type IN (
        'teacher_authored', 'ai_generated_vetted', 'ai_generated_unvetted'
    )),
    teacher_approved BOOLEAN NOT NULL DEFAULT false,
    approved_by UUID REFERENCES core.users(id),
    approved_at TIMESTAMPTZ,
    times_used INT NOT NULL DEFAULT 0,
    times_correct INT NOT NULL DEFAULT 0,  -- for V2 psychometric analysis
    discrimination_index NUMERIC(4,3),      -- V2: item discrimination
    difficulty_index NUMERIC(4,3),          -- V2: item difficulty
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    retired_at TIMESTAMPTZ                  -- NULL = active
);

CREATE INDEX idx_qbank_node ON content.question_bank (node_id)
    WHERE retired_at IS NULL;
CREATE INDEX idx_qbank_course ON content.question_bank (course_id);
CREATE INDEX idx_qbank_bloom ON content.question_bank (node_id, bloom_level)
    WHERE retired_at IS NULL AND teacher_approved = true;
```

---

## 6. Podcast Agent (V1 -- Design Only)

### 6.1 Script Generation

The Podcast Agent generates a two-voice dialogue between an "esperto" (expert) and a "curioso" (curious) speaker (F6.1, F6.3). The script is designed for 4-8 minutes of spoken content per concept.

#### Script Prompt Architecture

```
prompt_template_id: "podcast_script_v1"
version: 1
model_routing: claude — creative + pedagogically accurate

---

SYSTEM:
You write dialogue scripts for an educational podcast aimed at Italian
high school students (13-19). The podcast has two speakers:
- ESPERTO: Knowledgeable, clear, uses analogies. Not condescending.
- CURIOSO: Asks the questions the student would ask. Occasionally
  confused, always curious. Represents the student's perspective.

The dialogue must feel natural, not scripted. Use spoken Italian
conventions (contractions, filler words like "allora", "ecco",
"cioe'"). But NEVER use offensive, age-inappropriate, or
anxiety-inducing language.

CONTEXT:
Concept: {node.label_it}
Source materials: {sources}
Student profile tone: {profile.tone}
Target duration: {duration_minutes} minutes (~{word_count} words)

TASK:
Generate a podcast script as a sequence of dialogue turns.

Structure:
1. HOOK (30s): CURIOSO raises the problem/question
2. SETUP (60s): ESPERTO sets the context
3. DEEP DIVE (3-5 min): Back-and-forth exploring the concept
4. ANALOGY (60s): ESPERTO uses a memorable analogy
5. RECAP (30s): CURIOSO summarises in their own words
6. TAKEAWAY (15s): ESPERTO gives one memorable rule

Return JSON:
{
  "title": "string",
  "concept_node_id": "string",
  "estimated_duration_seconds": int,
  "segments": [
    {
      "speaker": "esperto|curioso",
      "text": "string",
      "phase": "hook|setup|deep_dive|analogy|recap|takeaway",
      "timestamp_hint_seconds": int
    }
  ]
}
```

#### Variant Modes (F6.6, F6.7)

| Mode | Modification |
|---|---|
| **Dialogue** (default, F6.1) | Two speakers: esperto + curioso |
| **Monologue** (F6.6) | Single speaker (esperto), narrated as a lecture. Script prompt adjusted to remove curioso turns. |
| **Debate** (F6.7, V2) | Two speakers with deliberate disagreement. Student judges who is correct. Higher-order thinking exercise. |

### 6.2 TTS Pipeline

Per ADR-001 decision 7, MVP uses no TTS (podcast is V1). V1 uses OpenAI TTS API.

```
[Script JSON]
        |
        v
[Safeguarding Agent: review script]
        |
        v
[TTS Renderer]
        |
        +-- For each segment:
        |     +-- Select voice_id based on speaker + student preference
        |     +-- Call OpenAI TTS API with segment text
        |     +-- Receive audio chunk (MP3)
        |
        +-- Concatenate audio chunks with 0.3s silence between speakers
        |
        +-- Add intro/outro jingle (configurable per course)
        |
        v
[Final audio file (MP3)] --> Scaleway Object Storage
        |
        v
[Transcript] --> stored alongside audio for accessibility (F6.5)
```

**Voice selection** (F6.2): The student selects from a voice library. V1 library:

| Voice pair | Style |
|---|---|
| "Compagni di classe" | Young male + young female, casual |
| "Divulgatori" | Adult male + adult female, professional |
| "Duo comico" | Male + male, humorous delivery |

Voice preferences are stored in the content-adaptation profile.

**Speed control** (F6.8): The audio player supports 0.75x to 2x playback speed. This is a frontend feature; the audio is generated at normal speed.

### 6.3 Cross-Language Variant (F13.11)

For bilingual students (consent (b) active), the podcast supports a cross-language variant:

**Option A — One voice per language**: ESPERTO speaks in the official language. CURIOSO speaks in the native language. This creates a natural code-switching pattern that supports bilingual comprehension.

**Option B — Dual-track**: Two separate audio files, one per language, with synchronised timestamps. Student can switch between tracks.

Decision deferred to V1 implementation based on user testing. The script generation pipeline supports both by producing parallel scripts.

---

## 7. Visual/Game/Dialog Agents (V1/V2 -- Stub Specifications)

### 7.1 Visual Agent (V1/V2)

**Interface contract:**

```python
class VisualRequest:
    concept_node_ids: list[str]
    content_type: Literal["flowchart", "concept_map", "code_annotation", "sequence_diagram"]
    accessibility: dict  # {high_contrast: bool, font_size: str}
    bilingual: BilingualConfig

class VisualResponse:
    svg_content: str           # SVG markup for frontend rendering
    alt_text: str              # WCAG: text alternative (F9.6)
    aria_description: str      # WCAG: detailed description for screen readers
    bilingual_labels: dict     # {node_id: {official: str, native: str}} (F13.14)
    source_format: str         # "mermaid" or "d2"
```

**V1 implementation**: Claude generates Mermaid diagram syntax from concept context. Server-side Mermaid renderer produces SVG. Labels are bilingual when F13.14 applies.

**V2 implementation**: Interactive diagrams, animations, step-by-step code walkthroughs.

### 7.2 Game Agent (V1)

**Interface contract:**

```python
class QuestRequest:
    student_id: str            # Internal (not pseudo) — game state is internal
    open_lacunae: list[str]    # Node IDs in lacuna or in_recupero state
    active_quests: list[str]   # Currently active quest IDs
    gamification_enabled: bool # False if student opted out (F7.8)

class QuestResponse:
    daily_quests: list[Quest]
    weekly_quests: list[Quest]
    xp_update: int
    new_badges: list[Badge]
    streak_status: StreakStatus

class Quest:
    id: str
    title: str                 # LLM-generated, safeguarding-reviewed
    description: str
    target_node_ids: list[str]
    xp_reward: int
    deadline_type: Literal["daily", "weekly"]
```

**Anti-patterns enforced (F7.7, F7.8):**

| Anti-pattern | Technical enforcement |
|---|---|
| Public leaderboard | No API endpoint exposes student XP/rank to other students. |
| FOMO / scarcity | Quest descriptions never use urgency language. No "ultima possibilita'!" or countdown timers. |
| Addictive mechanics | No variable-ratio reward schedules. XP is deterministic (fixed per action). No gacha mechanics. |
| Opt-out penalty | When `gamification_enabled = false`, all game endpoints return empty results. Core learning cycle (F11) is unaffected. Progress data is preserved. |
| Student comparison | Game Agent has no access to other students' game state. |

### 7.3 Dialog Agent (V2)

**Interface contract:**

```python
class DialogTurn:
    student_pseudo_id: str
    message: str
    concept_context: list[str]  # Current concept node IDs
    conversation_history: list[dict]  # Previous turns

class DialogResponse:
    message: str
    suggested_resources: list[str]  # Content IDs
    concept_refs: list[str]         # KG node IDs referenced
    metacognitive_prompt: str | None  # "Prova a spiegare con parole tue..."
```

**Metacognitive mode (F10.4)**: The Dialog Agent can operate in "rubber duck" mode where it asks the student to explain a concept, then validates the explanation against the KG and source materials. This is a V2 feature requiring streaming LLM responses with <= 3s P95 latency (N4).

---

## 8. Safeguarding Integration

### 8.1 Content Validation Pipeline

The Safeguarding Agent (fully specified in HLD-001, Section 3.10) is invoked at two points in every content generation flow:

1. **Post-generation, pre-delivery** (all channels): Every piece of content passes through safeguarding before reaching a student. This is a blocking gate -- content is held until cleared.

2. **Post-quiz-generation, pre-delivery**: Quiz questions receive an additional safeguarding check that includes quiz-specific rules (no anxiety language, no trick questions, no timer references).

```
[Content Generated]
        |
        v
[Safeguarding Agent]
        |
  SAFE? --YES--> [Deliver to student / store]
        |
  NO ---+
        |
  [Regenerate with modified prompt]
        |
  [Safeguarding Agent: re-review]
        |
  SAFE? --YES--> [Deliver]
        |
  NO ---+
        |
  [Second retry: regenerate with strict prompt]
        |
  [Safeguarding Agent: final review]
        |
  SAFE? --YES--> [Deliver]
        |
  NO ---+
        |
  [Block delivery, alert teacher, serve fallback content]
```

**Maximum retries**: 2 regeneration attempts. If content fails safeguarding after 2 retries, the system:
- Blocks delivery to the student
- Alerts the teacher (F16)
- Serves the teacher's original lesson material for the concept as fallback
- Logs the failure for review by MSTR-19 (Safeguarding & Ethics Specialist)

### 8.2 Rules Engine

The Safeguarding Agent checks every content output against these categories:

| Category | Detection method | Action | Severity |
|---|---|---|---|
| Offensive language | LLM classification + keyword blocklist | Block, regenerate | BLOCK |
| Age-inappropriate content | LLM classification | Block, regenerate | BLOCK |
| Student comparisons | Pattern matching ("altri studenti", "la maggior parte", class statistics) + LLM | Block, regenerate | BLOCK |
| Cultural/gender stereotypes | LLM classification | Block, regenerate | BLOCK |
| Manipulative patterns (FOMO, scarcity) | Pattern matching ("ultima occasione", "non perdere", "fretta") + LLM | Block, regenerate | BLOCK |
| Punitive tone | LLM classification | Auto-correct, log | WARN |
| Trick questions (quiz-specific) | Distractor rationale analysis | Block, regenerate | BLOCK |
| Timer/pressure language (quiz) | Pattern matching + LLM | Block, regenerate | BLOCK |
| Factual concern | LLM confidence scoring | Deliver, flag for teacher review | PASS_WITH_FLAG |
| Wellbeing signal | Pattern detection (repeated failure, frustration) | Deliver content, alert teacher + referent | ALERT |

#### Safeguarding Prompt

```
prompt_template_id: "safeguarding_review_v1"
version: 1
model_routing: claude — safety-critical, requires nuanced judgment

---

SYSTEM:
You are a content safety reviewer for educational materials delivered to
minors (13-19 years old) in Italian high schools.

Review the following content and check for EVERY category below. Return
a structured verdict.

CATEGORIES:
1. OFFENSIVE_LANGUAGE: Any insulting, demeaning, or profane language,
   including subtle put-downs disguised as humor.
2. AGE_INAPPROPRIATE: Content not suitable for 13-19 audience (sexual,
   violent, substance-related, etc.).
3. STUDENT_COMPARISON: Any reference to other students, class averages,
   rankings, or implied comparison ("most students get this right").
4. STEREOTYPE: Cultural, gender, regional (Nord/Sud), socio-economic
   stereotypes.
5. MANIPULATIVE_PATTERN: FOMO ("others are advancing!"), scarcity
   ("last chance!"), urgency pressure, guilt-tripping.
6. PUNITIVE_TONE: Shaming, blaming, discouraging framing. Look for
   "hai sbagliato" instead of "questo concetto ha bisogno di un altro
   giro."
7. FACTUAL_CONCERN: Technical inaccuracy, unsupported claim, or
   hallucinated information not grounded in source materials.
8. WELLBEING_SIGNAL: Content that might inadvertently discourage a
   struggling student.

CONTENT TO REVIEW:
{content_json}

CONTENT TYPE: {content_type}

Return JSON:
{
  "safe": true|false,
  "issues": [
    {
      "category": "OFFENSIVE_LANGUAGE|AGE_INAPPROPRIATE|...",
      "severity": "BLOCK|WARN|ALERT|PASS_WITH_FLAG",
      "description": "string",
      "location": "string (reference to specific text)"
    }
  ],
  "wellbeing_alert": {
    "detected": true|false,
    "type": "frustration_pattern|repeated_regression|null",
    "recommended_action": "string|null"
  }
}
```

### 8.3 Wellbeing Signals

The Safeguarding Agent monitors patterns across content generation requests (not just individual outputs) for wellbeing concerns:

| Pattern | Detection | Trigger | Action |
|---|---|---|---|
| Repeated regression | KMM query: 3+ regressions on same concept in 30 days | `regression_count >= 3` | Alert teacher, suggest channel change |
| Extended inactivity after lacuna | Engagement metrics: no activity for >7 days after lacuna detected | `days_since_lacuna > 7 AND activity_count = 0` | Gentle notification to student, alert teacher |
| Quiz abandonment | 3+ quizzes started but not completed | `abandoned_quiz_count >= 3` | Alert teacher, suggest simpler assessment path |
| Late-night usage | Timestamp check: activity after 21:00 for under-16 | `student_age < 16 AND hour >= 21` | "Fai una pausa, ci rivediamo domani!" |

These are implemented as scheduled checks (not real-time) that run as part of the Feedback Loop Agent (HLD-001, Section 3.11). Results are surfaced as wellbeing alerts in the teacher notification centre (F16.1).

---

## 9. Caching Strategy

### 9.1 What's Cached

| Cache layer | What | Storage | TTL | Hit rate estimate |
|---|---|---|---|---|
| **Deterministic cache** | Exact prompt hash -> LLM response | Redis | 24 hours | ~10% (same prompt rare due to personalisation) |
| **Semantic cache** | Prompt embedding similarity >= 0.95 -> cached response | pgvector | 7 days | ~30-40% (same concept, similar profiles cluster) |
| **Pre-generated batch cache** | Top-N common lacuna concepts -> pre-generated content | PostgreSQL (`content.generated_content`) | Until KG/material update | ~15-20% (covers most common gaps) |
| **Glossary cache** | Bilingual glossary per language | Redis | 1 hour (or invalidated on update) | ~99% (glossary changes rarely) |
| **RAG retrieval cache** | Concept -> top-K source materials | Redis | 24 hours (or invalidated on material upload) | ~50-60% (same concepts queried repeatedly) |

**Estimated overall cache hit rate**: 40-50% of LLM calls avoided through caching. At EUR 200-400/month MVP LLM budget (ADR-001), this saves EUR 80-200/month.

### 9.2 Cache Invalidation

| Event | Invalidation scope |
|---|---|
| Teacher uploads new lesson for a concept | Invalidate: semantic cache entries for that concept, RAG cache for that concept, batch cache for that concept |
| Teacher modifies the KG (node edit) | Invalidate: all caches referencing that node_id |
| Teacher modifies a generated document (F15.3) | Invalidate: the specific cached content for that student+concept |
| Student profile changes (tone, length, interests) | Invalidate: semantic cache entries for that student (they may still hit on concept-level cache) |
| Glossary update | Invalidate: bilingual content cache for that language, glossary Redis cache |

**Implementation**: Cache invalidation is event-driven via the Redis event stream (`maestro:events`). When an event with type `material.uploaded`, `kg.node.updated`, or `glossary.updated` is published, the cache invalidation handler processes it.

### 9.3 Batch Pre-generation

Overnight batch generation reduces latency and cost for predictable content:

**What is pre-generated:**

1. Recovery documents for the top 20 most common `lacuna` micro-nodes per class (based on KMM state data)
2. Remediation paths for the top 10 most common `in_recupero` nodes
3. Quiz questions for nodes that have fewer than 3x quiz-size questions in the vetted bank

**Schedule**: Runs between 02:00-06:00 CET (off-peak, school hours are 08:00-16:00 per N4).

**Cost control**: The batch job has a configurable token budget per night (default: 500K tokens, approximately EUR 2.50 on Claude). If the budget is exhausted, remaining pre-generations are deferred to the next night.

**Process:**

```
[Nightly CRON trigger at 02:00 CET]
        |
        v
[Query KMM: top-N lacuna/in_recupero nodes per class]
        |
        v
[For each node, check if valid pre-generated content exists]
        |
  EXISTS and VALID --> skip
        |
  MISSING or INVALIDATED --> [Generate with default profile (neutral tone, synthesis length)]
        |
        v
[Safeguarding review (batch mode)]
        |
        v
[Store in content.generated_content with cache_type = 'batch']
        |
        v
[Log generation to llm_audit_log]
```

**Note**: Batch-generated content uses a neutral default profile (neutral tone, synthesis length, no bilingual). When a student requests content, the system first checks if personalisation is needed (different tone/length/bilingualism). If the student's profile matches the batch defaults, the cached content is served immediately. If not, the system generates personalised content but uses the batch content as a "warm" context window (the RAG retrieval is already cached).

---

## 10. Performance Budget

Latency targets from N4:

| Content type | N4 target | Budget allocation | Caching benefit |
|---|---|---|---|
| **Review document (F5)** | <= 60s | RAG retrieval: 2s, LLM generation (Claude streaming): 40s, Bilingual: 10s, Safeguarding: 5s, delivery: 3s | Semantic/batch cache: ~35% of requests served in <5s |
| **Remediation path (F11.7)** | <= 30s | RAG retrieval: 2s, LLM generation: 18s, Safeguarding: 5s, delivery: 3s, buffer: 2s | Batch cache: ~20% served in <3s |
| **Quiz generation (F11.8)** | <= 15s | Question bank lookup: 1s, LLM generation (if needed): 8s, Structural validation: 1s, Safeguarding: 3s, delivery: 1s, buffer: 1s | Teacher bank / vetted bank: ~40% served in <3s |
| **Chat response (V2)** | <= 3s P95 | RAG: 500ms, LLM streaming: 2s, Safeguarding (lightweight): 500ms | Concept context cached |

**Streaming**: For text content (review documents, remediation paths), the Text Agent uses streaming LLM responses. The student sees progressive rendering in the frontend while the full response is being generated. The N4 target measures time to first meaningful content chunk, not time to completion.

**Quiz delivery**: Quizzes are delivered as a complete unit (not streamed) because the student should see all questions at once. The 15s target measures full generation time.

**Bilingual overhead**: The Bilingual Composer adds approximately 8-12 seconds to any text generation (a second LLM call for translation). This is within the 60s budget for review documents but tight for the 30s remediation path budget. Mitigation: bilingual content is pre-translated for batch-cached content; for real-time generation, the bilingual pass uses prompt-level caching (the glossary and translation instructions are identical across calls, reducing input token count).

---

## 11. Content Lifecycle (F15)

### 11.1 Content States

Every piece of generated content follows this lifecycle:

```
[generated] --> [delivered] --> [active]
                                  |
                            +-----+-----+
                            |           |
                      [archived]  [regenerated]
                                        |
                                        v
                                   [new version active,
                                    old version archived]
```

| State | Description |
|---|---|
| `generated` | Content has been created by an agent but not yet delivered to the student (may be awaiting safeguarding or teacher review) |
| `delivered` | Content has been sent to the student (notification sent, accessible in dashboard) |
| `active` | Content is visible and accessible to the student |
| `archived` | Content hidden from student view. Preserved for audit. Triggered by teacher action (F15.4) or regeneration. |
| `regenerated` | A new version has replaced this content. Previous version is archived. |

### 11.2 Versioning

When content is regenerated (F15.3):

1. The current version's status is set to `archived`, with `archived_at` and `archived_by` timestamps
2. A new record is created with `version = prev_version + 1`
3. The new version references the previous version ID for audit trail
4. The student sees only the latest active version

### 11.3 Audit Trail

Every content operation is logged in `audit.audit_log`:

| Operation | Actor | Logged data |
|---|---|---|
| Content generated | System (agent name) | content_id, prompt_template_id, model_id, prompt_hash, token_count |
| Content delivered | System | content_id, student_id, delivery_timestamp |
| Content viewed | Student | content_id, view_duration_ms |
| Content modified | Teacher | content_id, prev_content_hash, new_content_hash, teacher_id |
| Content archived | Teacher | content_id, reason, teacher_id |
| Content regenerated | Teacher/System | old_content_id, new_content_id, trigger_reason |

**Teacher modification badge (F5.7)**: When a teacher modifies content, the `teacher_reviewed` flag is set to `true` on the content record. The frontend renders the "Rivisto dal Prof." badge. The original and modified versions are both preserved.

**Copyright attribution (F2.13)**: Each piece of generated content tracks `sources_used` (list of material IDs and chunk IDs). When the teacher's own lessons are the primary source, the content carries an implicit attribution. The teacher can always see which of their materials were used via the explainability panel (N7).

---

## 12. Prompt Template Registry

### 12.1 Registry Structure

All prompt templates are managed as versioned artefacts:

```python
class PromptTemplate:
    id: str              # e.g., "text_review_document"
    version: int         # Monotonically increasing
    channel: str         # "text", "quiz", "bilingual", "safeguarding", etc.
    model_target: str    # "claude", "gpt-4o-mini", "any"
    template: str        # The template string with {placeholders}
    input_schema: dict   # JSON Schema for required template variables
    output_schema: dict  # JSON Schema for expected LLM output
    created_at: str
    created_by: str      # Agent ID or human
    deprecated_at: str | None
    notes: str           # Changelog for this version
```

### 12.2 Storage

```sql
CREATE TABLE content.prompt_templates (
    id TEXT NOT NULL,
    version INT NOT NULL,
    channel TEXT NOT NULL,
    model_target TEXT NOT NULL,
    template TEXT NOT NULL,
    input_schema JSONB NOT NULL,
    output_schema JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by TEXT NOT NULL,
    deprecated_at TIMESTAMPTZ,
    notes TEXT,

    PRIMARY KEY (id, version)
);

CREATE INDEX idx_prompt_templates_active
    ON content.prompt_templates (id, channel)
    WHERE deprecated_at IS NULL;
```

### 12.3 Version Management

- **New version**: When a prompt is updated, a new row with `version + 1` is inserted. The old version is NOT deprecated automatically -- both coexist until the old one is explicitly deprecated.
- **Active version**: The highest non-deprecated version for a given `id` is the active version.
- **Rollback**: If a new prompt version produces worse results (detected via safeguarding block rate or teacher feedback), the new version is deprecated and the previous version becomes active again.
- **Audit**: Every generated content references the `(prompt_template_id, prompt_template_version)` used. This enables tracing any quality issue back to the specific prompt version.

### 12.4 Cost Tracking

Every LLM call logs token consumption tagged with the prompt template ID:

```sql
-- Query: cost per prompt template per day
SELECT
    pt.id AS template_id,
    pt.version,
    DATE(lal.timestamp) AS day,
    COUNT(*) AS call_count,
    SUM(lal.input_tokens) AS total_input_tokens,
    SUM(lal.output_tokens) AS total_output_tokens,
    SUM(CASE
        WHEN lal.model_id LIKE 'claude%'
        THEN (lal.input_tokens * 15.0 / 1000000) + (lal.output_tokens * 75.0 / 1000000)
        WHEN lal.model_id LIKE 'gpt-4o-mini%'
        THEN (lal.input_tokens * 0.15 / 1000000) + (lal.output_tokens * 0.60 / 1000000)
    END) AS estimated_cost_usd
FROM audit.llm_audit_log lal
JOIN content.prompt_templates pt
    ON lal.prompt_template_id = pt.id
    AND lal.prompt_template_version = pt.version
GROUP BY pt.id, pt.version, DATE(lal.timestamp)
ORDER BY estimated_cost_usd DESC;
```

This feeds the "LLM Operations" Grafana dashboard (HLD-001, Section 9.4) for R9 cost monitoring.

---

## 13. MVP Scope vs V1/V2

| Component | MVP | V1 | V2 |
|---|---|---|---|
| **Text Agent** | Full: review documents, remediation paths, four-block structure, profile-adapted tone/length/analogies | -- | -- |
| **Quiz Engine** | Full: generation with Bloom's targeting, 5-layer quality framework, teacher review | Statistical validation (psychometric analysis) | Adaptive difficulty |
| **Bilingual Composer** | 2 languages (uk, ar), dual-column text, controlled glossary | +4 languages, podcast cross-language, diagram labels | +6 languages (12 total), chatbot bilingual |
| **Content Orchestrator** | Text + Quiz channels, authorial priority, profile routing | + Podcast, Visual, Game channels | + Dialog channel |
| **Podcast Agent** | Stub (returns "channel not available") | Full: two-voice scripts, TTS, transcript, speed control | Debate variant (F6.7) |
| **Visual Agent** | Stub | Basic: Mermaid diagrams, SVG, bilingual labels | Interactive animations |
| **Game Agent** | Stub | Full: XP, badges, streaks, quests, anti-patterns enforced | Cooperative mode (F7.6) |
| **Dialog Agent** | Not implemented | Not implemented | Full: conversational tutoring, rubber duck |
| **Safeguarding** | Full: LLM-based review, all categories, non-bypassable | + Rule-based pre-filter for latency/cost | + Wellbeing ML model |
| **Prompt Registry** | Full: versioned templates, audit trail | + A/B testing support | + Automated prompt optimisation |
| **Caching** | Deterministic + semantic + batch pre-generation | + Per-student content personalisation cache | + Predictive pre-generation |
| **Content Lifecycle** | Basic: generate, deliver, archive. Teacher modify/regenerate. | Full F15: content management UI, filtering, batch operations | -- |

---

## Appendix A: Prompt Template Inventory (MVP)

| Template ID | Channel | Purpose | Model |
|---|---|---|---|
| `text_system_v1` | text | System prompt for all text generation | claude |
| `text_review_document_v1` | text | Post-verification review document (F5) | claude |
| `text_remediation_path_v1` | text | Gap closure content (F11.7) | claude |
| `quiz_generation_v1` | quiz | Mini-quiz generation (F11.8, F11.10) | claude |
| `bilingual_compose_v1` | bilingual | Translation/adaptation to native language | claude |
| `safeguarding_review_v1` | safeguarding | Content safety review | claude |
| `concept_extraction_v1` | ingestion | Extract KG concepts from lesson content | gpt-4o-mini |
| `error_analysis_v1` | diagnostic | Analyze student code errors | claude |
| `error_mapping_v1` | diagnostic | Map errors to micro-nodes | gpt-4o-mini |

## Appendix B: Content Output Schema Reference

### Review Document (F5)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["blocks", "summary"],
  "properties": {
    "blocks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["concept_node_id", "concept_label", "il_tuo_errore", "perche_succede", "come_si_fa_giusto", "ricordati"],
        "properties": {
          "concept_node_id": {"type": "string", "format": "uuid"},
          "concept_label": {"type": "string"},
          "il_tuo_errore": {
            "type": "object",
            "required": ["text"],
            "properties": {
              "text": {"type": "string"},
              "code_errato": {"type": ["string", "null"]},
              "analogy_domain": {"type": "string"}
            }
          },
          "perche_succede": {
            "type": "object",
            "required": ["text"],
            "properties": {
              "text": {"type": "string"},
              "source_refs": {"type": "array", "items": {"type": "string"}}
            }
          },
          "come_si_fa_giusto": {
            "type": "object",
            "required": ["text"],
            "properties": {
              "text": {"type": "string"},
              "code_corretto": {"type": ["string", "null"]},
              "source_refs": {"type": "array", "items": {"type": "string"}}
            }
          },
          "ricordati": {
            "type": "object",
            "required": ["text"],
            "properties": {
              "text": {"type": "string", "maxLength": 500},
              "mnemonic": {"type": ["string", "null"]}
            }
          }
        }
      }
    },
    "summary": {"type": "string"}
  }
}
```

### Quiz

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["quiz"],
  "properties": {
    "quiz": {
      "type": "object",
      "required": ["concept_node_id", "concept_label", "target_bloom_level", "questions"],
      "properties": {
        "concept_node_id": {"type": "string", "format": "uuid"},
        "concept_label": {"type": "string"},
        "target_bloom_level": {"type": "string", "enum": ["remember", "understand", "apply", "analyze"]},
        "questions": {
          "type": "array",
          "minItems": 3,
          "maxItems": 5,
          "items": {
            "type": "object",
            "required": ["question_id", "stem", "options", "correct_answer", "explanation_correct", "explanation_incorrect", "bloom_level"],
            "properties": {
              "question_id": {"type": "string", "format": "uuid"},
              "stem": {"type": "string"},
              "options": {
                "type": "object",
                "required": ["A", "B", "C", "D"],
                "properties": {
                  "A": {"type": "string"},
                  "B": {"type": "string"},
                  "C": {"type": "string"},
                  "D": {"type": "string"}
                }
              },
              "correct_answer": {"type": "string", "enum": ["A", "B", "C", "D"]},
              "explanation_correct": {"type": "string"},
              "explanation_incorrect": {"type": "string"},
              "bloom_level": {"type": "string", "enum": ["remember", "understand", "apply", "analyze"]},
              "distractor_rationales": {"type": "object"},
              "source_refs": {"type": "array", "items": {"type": "string"}}
            }
          }
        }
      }
    }
  }
}
```

## Appendix C: Cross-HLD Interface Dependencies

| This HLD consumes | From HLD | Interface |
|---|---|---|
| `ContentRequest` dispatched by Orchestrator | HLD-001, Section 3.7 | `MaestroState.generated_content` field |
| RAG retrieval over `lesson_chunks` | HLD-002, Section 3.5 | pgvector similarity search with authorial priority |
| `concept_node_links` for source material lookup | HLD-002, Section 4.1 | SQL join on `node_id` |
| `kg_nodes` for concept hierarchy and labels | HLD-002, Section 8.1 | Relational query + AGE Cypher for prerequisites |
| `student_node_state` for current mastery state | HLD-004, Section 3.1 | SQL query via KMM service |
| `content.generated_content` table | HLD-004, Section defined in this HLD | Shared schema definition |
| LLMGateway pseudonymisation | HLD-001, Section 6 | All LLM calls routed through LLMGateway |
| Safeguarding Agent verdict | HLD-001, Section 3.10 | `SafeguardingVerdict` response schema |
| Content-adaptation profile | HLD-001, Section 3.5 / ADR-002 | 5-float vector + tone + length |
| Consent status | HLD-001, Section 3.2 | `ConsentVerification` response (consent (b) for bilingual) |

---

*Document version: 1.0. Task T2.3 of the MAESTRO delivery DAG. Subject to review by MSTR-02 (CTA), MSTR-03 (CPA), MSTR-10 (AI/ML Engineer), and MSTR-20 (QA Sentinel) before ratification.*
