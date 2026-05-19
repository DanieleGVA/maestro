# HLD-002: Knowledge Graph & Curriculum Architecture

**Status**: Proposed
**Date**: 2026-05-18
**Author**: MSTR-05 (KG & Curriculum Architect)
**Approved by**: Pending CTA (MSTR-02) + CPA (MSTR-03) + QA Sentinel (MSTR-20) review
**Task**: T2.2 (Knowledge graph & curriculum architecture)
**Depends on**: ADR-001 (Tech Stack), ADR-002 (Pedagogical Model)

---

## 1. Overview

### 1.1 Purpose

This document specifies the knowledge graph schema, curriculum ingestion pipeline, and concept-mapping engine for MAESTRO. The knowledge graph (KG) is the structural backbone of the system: it defines what students learn (the curriculum), how concepts relate (prerequisites), and at what granularity students and teachers interact with the material.

### 1.2 Design Philosophy

1. **Single database, three roles.** The KG lives in Apache AGE (PostgreSQL graph extension), alongside the KMM state store (relational tables) and the vector store (pgvector). All three participate in the same ACID transactions (ADR-001, decision 3).
2. **Macro for motivation, micro for diagnosis.** Students see macro-nodes (encouraging, manageable units); the diagnostic engine operates on micro-nodes (precise gap identification). The worst-state rollup rule (ADR-002, section 4) bridges the two.
3. **Teacher authority.** The KG is a teacher-authored artefact. Automated suggestions (concept extraction, prerequisite inference) are always validated by the teacher before taking effect.
4. **DAG invariant.** Prerequisite edges form a directed acyclic graph. This is enforced at write time -- no insert/update operation may introduce a cycle.
5. **Stable identifiers.** Node IDs are immutable UUIDs. The KMM state store, content links, and analytics all reference nodes by ID. Renaming or restructuring nodes does not break references.

### 1.3 Scope

| In scope (this HLD) | Out of scope |
|---|---|
| KG node and edge schema | KMM state machine (HLD-004, MSTR-07) |
| Apache AGE DDL and Cypher patterns | Content generation pipeline (HLD-003, MSTR-06) |
| Curriculum ingestion pipeline (F2-A, F2-B) | Agent orchestration (HLD-001, MSTR-04) |
| Concept-mapping engine (F2.4, F4.2) | Frontend visualisation (MSTR-09) |
| pgvector indexing for lesson materials | Authentication / consent flows (F14) |
| Coverage gap detection (F2.12) | Gamification layer (F7) |
| KG update and versioning | LLM prompt engineering |

---

## 2. KG Schema Design

### 2.1 Node Types

All nodes live in the Apache AGE graph `maestro_kg`. Node types are implemented as vertex labels.

#### MacroNode

Structural concepts visible to students and families. Represent a coherent topic unit (e.g., "Concetto di algoritmo", "Sessioni PHP").

| Attribute | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, immutable | Stable identifier referenced by KMM, content, analytics |
| `course_id` | UUID | FK -> `courses.id`, NOT NULL | Owning course |
| `label_it` | TEXT | NOT NULL, max 200 chars | Italian display name |
| `label_native` | TEXT | NULL | Optional native-language label (F13.12 glossary) |
| `description` | TEXT | NULL | Brief description for tooltip/explainability |
| `difficulty` | ENUM | {base, intermedio, avanzato}, NOT NULL | Difficulty level (F1.3) |
| `school_year` | SMALLINT | 1-5, NOT NULL | Target school year |
| `school_level` | ENUM | see below, NOT NULL | School level (F1.6) |
| `subject` | TEXT | NOT NULL, default 'informatica' | Subject area (extensible for V2 multi-subject) |
| `sort_order` | INT | NOT NULL, default 0 | Teacher-defined display ordering |
| `created_by` | UUID | FK -> `users.id`, NOT NULL | Teacher who created the node |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default now() | Last modification timestamp |
| `is_active` | BOOLEAN | NOT NULL, default true | Soft-deactivation (preserves references) |

**school_level ENUM values** (F1.6):
- `secondaria_primo_grado`
- `biennio_secondo_grado`
- `triennio_secondo_grado`
- `post_diploma_its`
- `formazione_professionale`

#### MicroNode

Fine-grained sub-concepts for diagnostic engine and teacher view. Each micro-node has exactly one macro parent.

| Attribute | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, immutable | Stable identifier |
| `macro_id` | UUID | FK -> MacroNode.id, NOT NULL | Parent macro-node |
| `course_id` | UUID | FK -> `courses.id`, NOT NULL | Denormalized for query efficiency |
| `label_it` | TEXT | NOT NULL, max 300 chars | Italian display name |
| `label_native` | TEXT | NULL | Optional native-language label |
| `description` | TEXT | NULL | Detailed description |
| `difficulty` | ENUM | {base, intermedio, avanzato}, NOT NULL | May differ from macro parent |
| `bloom_level` | ENUM | {remember, understand, apply, analyze, evaluate, create} | Target Bloom's level (ADR-002 section 5) |
| `sort_order` | INT | NOT NULL, default 0 | Display order within macro parent |
| `created_by` | UUID | FK -> `users.id`, NOT NULL | Creator |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default now() | |
| `is_active` | BOOLEAN | NOT NULL, default true | |

### 2.2 Edge Types

Edges are implemented as AGE edge labels.

#### PREREQUISITE

Directed edge: `source -[PREREQUISITE]-> target` means "to understand `target`, you need `source`."

| Attribute | Type | Description |
|---|---|---|
| `id` | UUID | Edge identifier |
| `strength` | ENUM {required, recommended} | `required`: hard prerequisite, blocks learning path. `recommended`: soft link, system suggests but does not block. |
| `created_by` | UUID | Teacher who defined the edge |
| `created_at` | TIMESTAMPTZ | |

PREREQUISITE edges may exist between:
- MacroNode -> MacroNode (structural prerequisites)
- MicroNode -> MicroNode (fine-grained prerequisites within or across macros)
- MicroNode -> MacroNode and MacroNode -> MicroNode (cross-granularity, less common but valid)

#### PARENT_OF

Containment edge: `MacroNode -[PARENT_OF]-> MicroNode`. Exactly one per micro-node.

| Attribute | Type | Description |
|---|---|---|
| `id` | UUID | Edge identifier |
| `created_at` | TIMESTAMPTZ | |

Constraint: Every MicroNode has exactly one incoming PARENT_OF edge. This is enforced at application level (AGE does not support cardinality constraints natively).

#### RELATED_TO

Soft associative link for content discovery. Bidirectional semantically (stored as directed, queried both ways).

| Attribute | Type | Description |
|---|---|---|
| `id` | UUID | Edge identifier |
| `relation_type` | TEXT | e.g., "applies_in", "extends", "contrasts_with" |
| `created_by` | UUID | |
| `created_at` | TIMESTAMPTZ | |

RELATED_TO edges are not part of the DAG constraint -- they may form cycles.

### 2.3 Constraints

#### C1: DAG Invariant on PREREQUISITE Edges

No cycle may exist in the PREREQUISITE edge set. This is validated:

1. **At write time**: Before inserting or updating a PREREQUISITE edge, the service executes a reachability query from `target` to `source`. If `source` is reachable from `target`, the edge would create a cycle and is rejected.

```cypher
-- Check: would adding source->target create a cycle?
-- If target can already reach source, then yes.
MATCH path = (t {id: $target_id})-[:PREREQUISITE*1..50]->(s {id: $source_id})
RETURN count(path) > 0 AS would_cycle
```

2. **Periodic batch validation**: A nightly job runs a topological sort on the full PREREQUISITE subgraph. If it fails, an alert is raised to the teacher and CTA.

#### C2: Single Macro Parent

Every MicroNode has exactly one incoming PARENT_OF edge. Enforced by the application layer: the `create_micro_node` operation atomically creates the node and the PARENT_OF edge.

#### C3: Uniqueness

- `(course_id, label_it)` is unique within MacroNodes.
- `(macro_id, label_it)` is unique within MicroNodes.
- These are enforced via unique indexes on the relational shadow tables (section 8).

#### C4: Referential Integrity on Deletion

Nodes cannot be hard-deleted if referenced by KMM state records. Instead, `is_active` is set to `false`. The node remains queryable for historical state but is hidden from active views.

### 2.4 Apache AGE Implementation

#### Graph Creation

```sql
-- Load the AGE extension
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- Create the graph
SELECT create_graph('maestro_kg');
```

#### Vertex Labels

```sql
SELECT create_vlabel('maestro_kg', 'MacroNode');
SELECT create_vlabel('maestro_kg', 'MicroNode');
```

#### Edge Labels

```sql
SELECT create_elabel('maestro_kg', 'PREREQUISITE');
SELECT create_elabel('maestro_kg', 'PARENT_OF');
SELECT create_elabel('maestro_kg', 'RELATED_TO');
```

#### Creating Nodes (Cypher via AGE)

```sql
-- Create a macro-node
SELECT * FROM cypher('maestro_kg', $$
  CREATE (n:MacroNode {
    id: 'a1b2c3d4-...',
    course_id: 'course-uuid-...',
    label_it: 'Concetto di algoritmo',
    difficulty: 'base',
    school_year: 3,
    school_level: 'triennio_secondo_grado',
    subject: 'informatica',
    sort_order: 1,
    created_by: 'teacher-uuid-...',
    created_at: '2026-05-18T10:00:00Z',
    updated_at: '2026-05-18T10:00:00Z',
    is_active: true
  })
  RETURN n
$$) AS (node agtype);

-- Create a micro-node
SELECT * FROM cypher('maestro_kg', $$
  CREATE (n:MicroNode {
    id: 'e5f6g7h8-...',
    macro_id: 'a1b2c3d4-...',
    course_id: 'course-uuid-...',
    label_it: 'Proprieta: finitezza',
    difficulty: 'base',
    bloom_level: 'understand',
    sort_order: 2,
    created_by: 'teacher-uuid-...',
    created_at: '2026-05-18T10:00:00Z',
    updated_at: '2026-05-18T10:00:00Z',
    is_active: true
  })
  RETURN n
$$) AS (node agtype);
```

#### Creating Edges

```sql
-- PARENT_OF edge
SELECT * FROM cypher('maestro_kg', $$
  MATCH (m:MacroNode {id: 'a1b2c3d4-...'}), (n:MicroNode {id: 'e5f6g7h8-...'})
  CREATE (m)-[:PARENT_OF {
    id: 'edge-uuid-...',
    created_at: '2026-05-18T10:00:00Z'
  }]->(n)
$$) AS (result agtype);

-- PREREQUISITE edge (after DAG validation passes)
SELECT * FROM cypher('maestro_kg', $$
  MATCH (a:MacroNode {id: 'var-uuid-...'}), (b:MacroNode {id: 'algo-uuid-...'})
  CREATE (a)-[:PREREQUISITE {
    id: 'edge-uuid-...',
    strength: 'required',
    created_by: 'teacher-uuid-...',
    created_at: '2026-05-18T10:00:00Z'
  }]->(b)
$$) AS (result agtype);
```

#### Key Query Patterns

```sql
-- Get all micro-nodes for a macro-node
SELECT * FROM cypher('maestro_kg', $$
  MATCH (m:MacroNode {id: $macro_id})-[:PARENT_OF]->(n:MicroNode)
  WHERE n.is_active = true
  RETURN n
  ORDER BY n.sort_order
$$) AS (node agtype);

-- Get prerequisites (1 hop) for a node
SELECT * FROM cypher('maestro_kg', $$
  MATCH (prereq)-[:PREREQUISITE]->(target {id: $node_id})
  WHERE prereq.is_active = true
  RETURN prereq
$$) AS (node agtype);

-- Get full prerequisite chain (variable depth, max 20 hops)
SELECT * FROM cypher('maestro_kg', $$
  MATCH path = (root)-[:PREREQUISITE*1..20]->(target {id: $node_id})
  WHERE root.is_active = true
  RETURN DISTINCT root, length(path) AS depth
  ORDER BY depth DESC
$$) AS (node agtype, depth agtype);

-- Get all macro-nodes for a course with their micro counts
SELECT * FROM cypher('maestro_kg', $$
  MATCH (m:MacroNode {course_id: $course_id, is_active: true})
  OPTIONAL MATCH (m)-[:PARENT_OF]->(n:MicroNode {is_active: true})
  RETURN m, count(n) AS micro_count
  ORDER BY m.sort_order
$$) AS (macro_node agtype, micro_count agtype);

-- Topological sort (DAG validation)
-- Performed at application level using Kahn's algorithm
-- on the full PREREQUISITE edge set for a course.
```

#### Indexes

AGE inherits PostgreSQL indexing. Create indexes on frequently queried properties:

```sql
-- These are created on the internal AGE tables
-- The exact syntax depends on AGE version; shown conceptually

-- Index on MacroNode.course_id for course-scoped queries
CREATE INDEX idx_macronode_course ON maestro_kg."MacroNode"
  USING btree ((properties->>'course_id'));

-- Index on MacroNode.id for point lookups
CREATE INDEX idx_macronode_id ON maestro_kg."MacroNode"
  USING btree ((properties->>'id'));

-- Index on MicroNode.macro_id for parent lookups
CREATE INDEX idx_micronode_macro ON maestro_kg."MicroNode"
  USING btree ((properties->>'macro_id'));

-- Index on MicroNode.id for point lookups
CREATE INDEX idx_micronode_id ON maestro_kg."MicroNode"
  USING btree ((properties->>'id'));
```

---

## 3. Curriculum Ingestion Pipeline

### 3.1 Architecture Overview

```
Teacher Upload (UI)
       |
       v
  +-----------+      +------------------+      +-----------------+
  | File Store|----->| Document Parser  |----->| Text Chunker    |
  | (Scaleway |      | (per format)     |      | (by concept     |
  |  S3)      |      |                  |      |  segment)       |
  +-----------+      +------------------+      +-----------------+
                                                       |
                                                       v
                                               +-----------------+
                                               | Embedding Gen   |
                                               | (pgvector)      |
                                               +-----------------+
                                                       |
       +-----------------------------------------------+
       |                       |                        |
       v                       v                        v
+--------------+    +------------------+    +------------------+
| Concept      |    | Vector Store     |    | Content Registry |
| Mapper (LLM) |    | (pgvector)       |    | (relational)     |
+--------------+    +------------------+    +------------------+
       |
       v
+------------------+
| Teacher          |
| Validation UI    |
+------------------+
       |
       v
+------------------+
| KG Link Records  |
| (relational)     |
+------------------+
```

### 3.2 Document Processing (F2-A, F2-B)

#### Supported Formats and Parsing

| Format | Parser | Output | Max Size |
|---|---|---|---|
| PDF | Apache Tika / PyMuPDF | Structured text + images | 50MB |
| DOCX | python-docx | Structured text + images | 50MB |
| PPTX | python-pptx | Slide text + speaker notes + images | 50MB |
| MP3 | Whisper (see 3.3) | Timestamped transcript | 500MB |
| MP4 | Whisper + ffmpeg | Timestamped transcript + keyframes | 500MB |
| WAV | Whisper (see 3.3) | Timestamped transcript | 500MB |

#### Processing Pipeline

1. **Upload**: File is stored in Scaleway Object Storage. A `lesson_materials` record is created with status `processing`.
2. **Format detection**: MIME type + extension validation.
3. **Text extraction**: Format-specific parser extracts raw text, preserving structure (headings, lists, code blocks).
4. **Metadata extraction**: Title, author, page count, duration (for audio/video).
5. **Chunking**: Text is split into semantic chunks (see 3.4).
6. **Embedding generation**: Each chunk is embedded and stored in pgvector.
7. **Concept mapping suggestion**: LLM identifies KG nodes relevant to each chunk (see section 4).
8. **Status update**: Material status set to `mapped` (pending teacher validation) or `indexed` (if no concept mapping needed).

#### Batch Upload (F2.7)

Teachers can upload an entire module folder. The system processes files sequentially within the batch, preserving the order for concept-mapping continuity. The batch is treated as a single logical unit in the teacher validation UI.

### 3.3 Audio/Video Processing (F2.2, F2.3)

#### Transcription

- **Engine**: OpenAI Whisper (large-v3) via self-hosted inference or API.
- **Output**: Word-level timestamps, language detection, segment boundaries.
- **Speaker diarization**: pyannote.audio for speaker identification. Maps speaker segments to teacher vs. student roles where identifiable.

#### Processing Flow

```
Audio/Video file
      |
      v
  ffmpeg (extract audio track if video)
      |
      v
  Whisper large-v3
      |
      +---> Raw transcript with word-level timestamps
      |
      v
  pyannote.audio (speaker diarization)
      |
      +---> Speaker-labeled segments with timestamps
      |
      v
  Merge: aligned transcript with speaker labels
      |
      v
  Store in lesson_transcripts table
      |
      v
  Teacher edit UI (F2.3): synchronized player + editable transcript
```

#### Editable Transcript (F2.3)

- Transcript stored as an array of segments: `{speaker_id, start_ms, end_ms, text}`.
- Teacher edits are tracked as diffs against the original ASR output.
- Player synchronization: clicking a transcript segment seeks to the corresponding timestamp; playback highlights the current segment.

### 3.4 Chunking Strategy

Content is chunked for two purposes: (a) vector indexing for RAG retrieval, and (b) concept mapping to KG nodes.

#### For Documents (PDF/DOCX/PPTX)

- **Primary split**: By structural boundaries (headings, sections, slide boundaries).
- **Secondary split**: If a section exceeds 1500 tokens, split at paragraph boundaries.
- **Overlap**: 100-token overlap between adjacent chunks for retrieval continuity.
- **Metadata per chunk**: source_file, page/slide number, section heading, chunk_index.

#### For Audio/Video Transcripts

- **Primary split**: By topic-shift detection (silence gaps > 3s, speaker changes, topic-model boundaries).
- **Secondary split**: Fixed 120-second windows if no natural boundary is detected.
- **Timestamp preservation**: Every chunk retains `start_ms` and `end_ms` for deep-linking (F2.4).
- **Metadata per chunk**: source_file, start_time, end_time, speaker_id.

### 3.5 Vector Indexing (F2.10)

#### Embedding Model

- **MVP**: OpenAI `text-embedding-3-small` (1536 dimensions). Pseudonymized content only -- no student PII reaches the embedding API.
- **V1**: Evaluate self-hosted `e5-mistral-7b-instruct` or `multilingual-e5-large` for full EU data sovereignty on content embeddings.

#### pgvector Storage

```sql
CREATE TABLE lesson_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID NOT NULL REFERENCES lesson_materials(id),
    course_id UUID NOT NULL REFERENCES courses(id),
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    -- metadata includes: page, slide, start_ms, end_ms, speaker_id, section_heading
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (material_id, chunk_index)
);

-- HNSW index for approximate nearest neighbor search
CREATE INDEX idx_lesson_chunks_embedding
    ON lesson_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Filter index for course-scoped searches
CREATE INDEX idx_lesson_chunks_course
    ON lesson_chunks (course_id);
```

#### Retrieval Pattern

For content generation (F5, F6, F11.7), the system retrieves relevant lesson material:

```sql
-- Find the top-K lesson chunks relevant to a concept
SELECT lc.id, lc.content, lc.metadata,
       1 - (lc.embedding <=> $query_embedding) AS similarity
FROM lesson_chunks lc
WHERE lc.course_id = $course_id
  AND 1 - (lc.embedding <=> $query_embedding) > 0.70
ORDER BY lc.embedding <=> $query_embedding
LIMIT 10;
```

The authorial priority rule (F2.5) is enforced by the Content Orchestrator (HLD-003), not by the vector query itself. The orchestrator queries teacher-authored chunks first, then textbook chunks, then external sources.

---

## 4. Concept-Mapping Engine

### 4.1 Lesson-to-Node Mapping (F2.4)

When a teacher uploads a lesson, the system automatically suggests which KG nodes are covered by each content segment.

#### Mapping Pipeline

```
Lesson chunks (from section 3)
       |
       v
  +-------------------+
  | Step 1: Embedding  |  Embed each chunk; find top-5 nearest KG nodes
  | Similarity         |  by comparing chunk embedding to node embeddings
  +-------------------+
       |
       v
  +-------------------+
  | Step 2: LLM        |  For each (chunk, candidate_node) pair,
  | Confirmation       |  ask GPT-4o-mini: "Does this text teach this concept?"
  +-------------------+
       |
       v
  +-------------------+
  | Step 3: Confidence  |  Combine embedding similarity (0-1) and LLM
  | Scoring            |  confidence (0-1) into a composite score
  +-------------------+
       |
       v
  +-------------------+
  | Step 4: Teacher     |  Present suggested mappings in split-view UI
  | Validation         |  Left: extracted segments. Right: KG nodes.
  +-------------------+
       |
       v
  concept_node_links table (confirmed mappings)
```

#### Node Embeddings

Each KG node has a precomputed embedding based on its label, description, and associated content:

```sql
CREATE TABLE kg_node_embeddings (
    node_id UUID PRIMARY KEY,
    node_type TEXT NOT NULL CHECK (node_type IN ('macro', 'micro')),
    embedding vector(1536) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_kg_node_embeddings
    ON kg_node_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

Node embeddings are recomputed when: (a) the node label/description changes, (b) new content is linked to the node, (c) triggered manually by the teacher.

#### Confidence Scoring

```
composite_score = 0.4 * embedding_similarity + 0.6 * llm_confidence
```

- `embedding_similarity`: cosine similarity between chunk embedding and node embedding (0.0-1.0).
- `llm_confidence`: LLM-reported confidence that the chunk teaches the concept (0.0-1.0). Extracted from a structured JSON response.

Thresholds:
- `composite_score >= 0.80`: Auto-suggested with high confidence (green indicator in UI).
- `0.60 <= composite_score < 0.80`: Suggested with medium confidence (yellow indicator).
- `composite_score < 0.60`: Not suggested unless explicitly searched by teacher.

All suggestions require teacher confirmation before becoming active links.

#### Teacher Validation UI (F2.4)

Split-view interface:
- **Left panel**: Lesson content organized by segment (for documents: sections/pages; for audio/video: timestamp ranges). Each segment shows its text/transcript.
- **Right panel**: KG tree (macro > micro) for the course. Suggested nodes are highlighted with confidence indicators.
- **Interaction**: Teacher drags a node to a segment to create a link, or clicks "confirm" on an auto-suggested link. Teacher can reject suggestions or add links not suggested by the system.
- **Time ranges** (audio/video): Each concept link includes `start_ms` and `end_ms` defining the lesson segment where the concept is taught. These enable deep-linking from study paths to specific lesson moments.

#### Confirmed Mapping Storage

```sql
CREATE TABLE concept_node_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID NOT NULL REFERENCES lesson_materials(id),
    chunk_id UUID REFERENCES lesson_chunks(id),
    node_id UUID NOT NULL,  -- MacroNode or MicroNode ID
    node_type TEXT NOT NULL CHECK (node_type IN ('macro', 'micro')),
    start_ms INT,  -- NULL for documents; populated for audio/video
    end_ms INT,
    confidence_score NUMERIC(4,3),  -- composite score at mapping time
    confirmed_by UUID REFERENCES users(id),  -- teacher who validated
    confirmed_at TIMESTAMPTZ,
    auto_suggested BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (material_id, chunk_id, node_id)
);

CREATE INDEX idx_concept_links_node ON concept_node_links (node_id);
CREATE INDEX idx_concept_links_material ON concept_node_links (material_id);
```

### 4.2 Error-to-Micronode Mapping (F4.2)

When a teacher uploads verification results (F4), the system maps each student error to the specific micro-node(s) representing the gap.

#### Mapping Pipeline

```
Verification question + student answer + correct answer
       |
       v
  +-------------------+
  | Step 1: Question   |  The question was already linked to KG nodes
  | Context           |  during verification setup (F4.1)
  +-------------------+
       |
       v
  +-------------------+
  | Step 2: Error      |  LLM analyzes the specific error:
  | Analysis (LLM)    |  "What misconception does this answer reveal?"
  +-------------------+
       |
       v
  +-------------------+
  | Step 3: Micro-node |  Map the misconception to candidate micro-nodes
  | Candidate Selection|  from the question's linked macro-node(s)
  +-------------------+
       |
       v
  +-------------------+
  | Step 4: Confidence  |  Score each (error, micro-node) pair
  | Scoring            |  using LLM analysis + embedding similarity
  +-------------------+
       |
       v
  Threshold application:
  >= 80%: auto-proposed to teacher
  < 80%: flagged as "uncertain" for teacher validation
```

#### Confidence Scoring for Errors

```
error_confidence = 0.3 * embedding_similarity(error_desc, node_desc)
                 + 0.7 * llm_classification_confidence
```

The LLM classification weight is higher here because error analysis requires semantic understanding that pure embedding similarity cannot capture (e.g., a session fixation error vs. a session expiry error both relate to "Sessioni PHP" but map to different micro-nodes).

#### Error Mapping Storage

```sql
CREATE TABLE error_node_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_id UUID NOT NULL REFERENCES verifications(id),
    question_id UUID NOT NULL REFERENCES verification_questions(id),
    student_id UUID NOT NULL REFERENCES students(id),
    node_id UUID NOT NULL,  -- always a MicroNode ID
    confidence_score NUMERIC(4,3) NOT NULL,
    auto_confirmed BOOLEAN NOT NULL DEFAULT false,  -- true if >= 0.80
    teacher_confirmed BOOLEAN,  -- NULL = pending, true = confirmed, false = rejected
    confirmed_by UUID REFERENCES users(id),
    error_description TEXT,  -- LLM-generated error analysis
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (verification_id, question_id, student_id, node_id)
);

CREATE INDEX idx_error_mappings_student ON error_node_mappings (student_id);
CREATE INDEX idx_error_mappings_node ON error_node_mappings (node_id);
CREATE INDEX idx_error_mappings_verification ON error_node_mappings (verification_id);
```

### 4.3 Content-to-Node Mapping

Generated content (recovery documents, quizzes, podcasts) is linked back to the KG nodes it addresses. This is a simpler mapping: the Content Orchestrator (HLD-003) generates content *for* a specific node, so the link is established at generation time, not inferred.

```sql
CREATE TABLE generated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id),
    node_id UUID NOT NULL,  -- target KG node
    node_type TEXT NOT NULL CHECK (node_type IN ('macro', 'micro')),
    content_type TEXT NOT NULL CHECK (content_type IN (
        'recovery_document', 'quiz', 'retention_check', 'podcast_script'
    )),
    content JSONB NOT NULL,  -- structured content payload
    embedding vector(1536),  -- for semantic cache (ADR-001)
    version INT NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN (
        'active', 'archived', 'regenerated'
    )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    archived_at TIMESTAMPTZ,
    archived_by UUID REFERENCES users(id)
);

CREATE INDEX idx_generated_content_student_node
    ON generated_content (student_id, node_id)
    WHERE status = 'active';
```

---

## 5. Coverage Analysis

### 5.1 Gap Detection (F2.12)

The coverage analysis engine identifies KG nodes that lack sufficient learning materials. Per F2.11, the target is at least 3 sources per concept (lesson + manual + exercise).

#### Coverage Computation

```sql
-- Coverage view: count distinct materials per node
CREATE OR REPLACE VIEW node_coverage AS
SELECT
    cnl.node_id,
    cnl.node_type,
    COUNT(DISTINCT cnl.material_id) AS total_sources,
    COUNT(DISTINCT cnl.material_id) FILTER (
        WHERE lm.material_type = 'lesson'
    ) AS lesson_sources,
    COUNT(DISTINCT cnl.material_id) FILTER (
        WHERE lm.material_type = 'textbook'
    ) AS textbook_sources,
    COUNT(DISTINCT cnl.material_id) FILTER (
        WHERE lm.material_type = 'exercise'
    ) AS exercise_sources,
    COUNT(DISTINCT cnl.material_id) FILTER (
        WHERE lm.material_type = 'external'
    ) AS external_sources,
    CASE
        WHEN COUNT(DISTINCT cnl.material_id) >= 3 THEN 'adequate'
        WHEN COUNT(DISTINCT cnl.material_id) >= 1 THEN 'partial'
        ELSE 'uncovered'
    END AS coverage_status
FROM concept_node_links cnl
JOIN lesson_materials lm ON cnl.material_id = lm.id
WHERE cnl.confirmed_at IS NOT NULL  -- only teacher-confirmed links
GROUP BY cnl.node_id, cnl.node_type;
```

#### Alert Generation

A scheduled job (daily) checks for nodes with `coverage_status != 'adequate'` and generates alerts for the teacher via the notification system (F16):

- **Uncovered** (0 sources): Priority HIGH. "Il concetto '{label}' non ha materiale associato."
- **Partial** (1-2 sources): Priority MEDIUM. "Il concetto '{label}' ha {n} fonti su 3 minime raccomandate."

Alerts are deduplicated: a node only generates one active alert at a time. The alert is auto-resolved when coverage reaches 3.

### 5.2 Coverage Metrics

Exposed to the teacher dashboard (F12.7):

| Metric | Computation |
|---|---|
| Overall coverage % | (nodes with >= 3 sources) / (total active nodes) * 100 |
| Per-macro coverage | For each macro: min(coverage of children micro-nodes) |
| Source diversity score | (distinct material_types per node) / 3 (lesson, textbook, exercise) |
| Uncovered nodes list | Nodes with 0 confirmed links |

---

## 6. Granularity Adaptation (F1.8, F1.9)

### 6.1 Default Rules by School Level

| School Level | Student Default View | Teacher View | Student Can Toggle? |
|---|---|---|---|
| `secondaria_primo_grado` | Macro only | Macro + Micro | No (unless teacher overrides) |
| `biennio_secondo_grado` | Macro only | Macro + Micro | No (unless teacher overrides) |
| `triennio_secondo_grado` | Macro (can switch to Micro) | Macro + Micro | Yes (segmented control) |
| `post_diploma_its` | Macro (can switch to Micro) | Macro + Micro | Yes |
| `formazione_professionale` | Macro only | Macro + Micro | No (unless teacher overrides) |

### 6.2 Teacher Override (F1.9)

Teachers can override the default granularity setting per course:

```sql
CREATE TABLE course_granularity_overrides (
    course_id UUID PRIMARY KEY REFERENCES courses(id),
    student_can_toggle_micro BOOLEAN NOT NULL,
    overridden_by UUID NOT NULL REFERENCES users(id),
    overridden_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    reason TEXT  -- optional teacher note
);
```

### 6.3 Query Patterns

```sql
-- Macro-only view (student in biennio)
SELECT * FROM cypher('maestro_kg', $$
  MATCH (m:MacroNode {course_id: $course_id, is_active: true})
  RETURN m
  ORDER BY m.sort_order
$$) AS (node agtype);

-- Macro + Micro view (teacher, or triennio student with toggle)
SELECT * FROM cypher('maestro_kg', $$
  MATCH (m:MacroNode {course_id: $course_id, is_active: true})
  OPTIONAL MATCH (m)-[:PARENT_OF]->(n:MicroNode {is_active: true})
  RETURN m, collect(n) AS micros
  ORDER BY m.sort_order
$$) AS (macro_node agtype, micros agtype);
```

### 6.4 Rollup for Macro View (ADR-002 Section 4)

When displaying the macro-only view, macro-node state is computed by the worst-state rollup rule:

```
macro_state = worst(micro_states for all active children)
```

State ordering (worst to best): `lacuna` < `in_recupero` < `non_introdotto` < `introdotto` < `da_consolidare` < `consolidato`.

The UI displays the macro color (worst-state) plus a progress indicator: "7/10 concetti consolidati" (two-tier display from ADR-002).

The rollup computation is performed by the KMM service (HLD-004, MSTR-07). The KG service provides the macro-micro structure; the KMM service provides the state data.

---

## 7. KG Update Operations

### 7.1 Teacher Edits (F1.4)

The KG supports live updates without system restart. All edits are performed via the KG API and take effect immediately.

#### Supported Operations

| Operation | Description | Side Effects |
|---|---|---|
| Add MacroNode | Create a new macro concept | New node visible in all student maps. All students get `non_introdotto` state for new micro-children. |
| Add MicroNode | Add sub-concept to a macro | Students enrolled in the course get `non_introdotto` for the new micro-node. Macro rollup is recomputed. |
| Edit node | Change label, description, difficulty, bloom_level | No state impact. Updated immediately in all views. |
| Deactivate node | Set `is_active = false` | Node hidden from active views. Existing KMM state preserved for history. Coverage alerts suppressed. |
| Reactivate node | Set `is_active = true` | Node reappears. KMM state is restored (last known state). |
| Add PREREQUISITE edge | Define a prerequisite relationship | DAG validation runs first. If valid, edge is created. Learning paths may be reordered. |
| Remove PREREQUISITE edge | Remove prerequisite | Edge deleted. Learning paths simplified. |
| Reorder nodes | Change `sort_order` | Visual reordering only, no state impact. |

### 7.2 Cascade Effects on Student Maps

When the KG structure changes, student maps must be synchronized:

#### New Node Added

```
For each student enrolled in the course:
  - Create KMM state record: (student_id, new_node_id, 'non_introdotto')
  - Log transition: cause = 'kg_structure_change'
```

This is implemented as a database trigger or application-level event handler, executing within the same transaction as the node creation.

#### Node Deactivated

```
For each student enrolled in the course:
  - KMM state record is NOT deleted (preserves history)
  - State is excluded from rollup computation
  - State is excluded from coverage analysis
  - State is excluded from active map views
```

#### Prerequisite Added

```
For each student enrolled in the course:
  - If student has target node in 'in_recupero' or later state
    AND prereq node in 'non_introdotto' or 'lacuna':
    Alert teacher: "Student X may need to study {prereq} before continuing {target}"
```

### 7.3 Versioning Strategy

The KG does not use full graph versioning (snapshotting the entire graph at each change). Instead:

1. **Node-level audit**: Every node creation, edit, and deactivation is logged in the `audit_log` table (ADR-001, section 4) with `prev_value` and `new_value` as JSONB.
2. **Edge-level audit**: Every edge creation and deletion is logged similarly.
3. **Timestamp-based reconstruction**: The audit log supports reconstructing the KG state at any point in time by replaying changes forward from the initial state.

This approach is sufficient for MVP (small graph, infrequent structural changes). If V2 introduces automated KG evolution (e.g., LLM-suggested new nodes based on curriculum changes), a more formal versioning system (event sourcing on the graph) should be evaluated.

---

## 8. Data Model (SQL + AGE)

### 8.1 Relational Tables (PostgreSQL)

These tables complement the AGE graph. Some data is stored in both relational tables and graph vertices to support different query patterns.

```sql
-- ============================================================
-- COURSES
-- ============================================================
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    school_year SMALLINT NOT NULL CHECK (school_year BETWEEN 1 AND 5),
    school_level TEXT NOT NULL CHECK (school_level IN (
        'secondaria_primo_grado',
        'biennio_secondo_grado',
        'triennio_secondo_grado',
        'post_diploma_its',
        'formazione_professionale'
    )),
    subject TEXT NOT NULL DEFAULT 'informatica',
    official_language TEXT NOT NULL DEFAULT 'it',
    teacher_id UUID NOT NULL REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'setup' CHECK (status IN (
        'setup', 'active', 'archived'
    )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- KG NODE REGISTRY (relational shadow of AGE vertices)
-- Provides fast relational joins that AGE Cypher cannot do
-- ============================================================
CREATE TABLE kg_nodes (
    id UUID PRIMARY KEY,
    course_id UUID NOT NULL REFERENCES courses(id),
    node_type TEXT NOT NULL CHECK (node_type IN ('macro', 'micro')),
    macro_id UUID REFERENCES kg_nodes(id),  -- NULL for macro, set for micro
    label_it TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('base', 'intermedio', 'avanzato')),
    bloom_level TEXT CHECK (bloom_level IN (
        'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'
    )),
    school_year SMALLINT NOT NULL,
    school_level TEXT NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Uniqueness within scope
    UNIQUE (course_id, node_type, label_it),
    -- Every micro must have a macro parent
    CHECK (
        (node_type = 'macro' AND macro_id IS NULL) OR
        (node_type = 'micro' AND macro_id IS NOT NULL)
    )
);

CREATE INDEX idx_kg_nodes_course ON kg_nodes (course_id) WHERE is_active;
CREATE INDEX idx_kg_nodes_macro ON kg_nodes (macro_id) WHERE node_type = 'micro';

-- ============================================================
-- KG EDGE REGISTRY (relational shadow of AGE edges)
-- ============================================================
CREATE TABLE kg_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id),
    edge_type TEXT NOT NULL CHECK (edge_type IN (
        'prerequisite', 'parent_of', 'related_to'
    )),
    source_node_id UUID NOT NULL REFERENCES kg_nodes(id),
    target_node_id UUID NOT NULL REFERENCES kg_nodes(id),
    strength TEXT CHECK (strength IN ('required', 'recommended')),
    relation_type TEXT,  -- for RELATED_TO edges
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (source_node_id, target_node_id, edge_type),
    CHECK (source_node_id != target_node_id)
);

CREATE INDEX idx_kg_edges_target ON kg_edges (target_node_id);
CREATE INDEX idx_kg_edges_source ON kg_edges (source_node_id);
CREATE INDEX idx_kg_edges_course ON kg_edges (course_id);

-- ============================================================
-- LESSON MATERIALS
-- ============================================================
CREATE TABLE lesson_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id),
    title TEXT NOT NULL,
    material_type TEXT NOT NULL CHECK (material_type IN (
        'lesson', 'textbook', 'exercise', 'notes', 'code_example',
        'article', 'external_link'
    )),
    file_format TEXT,  -- 'pdf', 'docx', 'pptx', 'mp3', 'mp4', 'wav', 'url'
    file_size_bytes BIGINT,
    storage_key TEXT,  -- S3 object key
    storage_url TEXT,  -- presigned URL (generated on access)
    duration_ms INT,  -- for audio/video
    page_count INT,  -- for documents
    status TEXT NOT NULL DEFAULT 'uploaded' CHECK (status IN (
        'uploaded', 'processing', 'transcribing', 'indexed', 'mapped', 'error'
    )),
    processing_error TEXT,
    uploaded_by UUID NOT NULL REFERENCES users(id),
    batch_id UUID,  -- groups files uploaded together (F2.7)
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_materials_course ON lesson_materials (course_id);
CREATE INDEX idx_materials_batch ON lesson_materials (batch_id) WHERE batch_id IS NOT NULL;
CREATE INDEX idx_materials_status ON lesson_materials (status);

-- ============================================================
-- LESSON TRANSCRIPTS (F2.2, F2.3)
-- ============================================================
CREATE TABLE lesson_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID NOT NULL REFERENCES lesson_materials(id) UNIQUE,
    language TEXT NOT NULL DEFAULT 'it',
    segments JSONB NOT NULL,
    -- segments: [{speaker_id, start_ms, end_ms, text, is_edited}, ...]
    original_segments JSONB,  -- preserved ASR output before teacher edits
    asr_model TEXT,  -- e.g., 'whisper-large-v3'
    asr_confidence NUMERIC(4,3),
    edited_by UUID REFERENCES users(id),
    edited_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- LESSON CHUNKS (for vector indexing) - defined in section 3.5
-- ============================================================
-- (lesson_chunks table already defined above)

-- ============================================================
-- KG NODE EMBEDDINGS - defined in section 4.1
-- ============================================================
-- (kg_node_embeddings table already defined above)

-- ============================================================
-- CONCEPT NODE LINKS - defined in section 4.1
-- ============================================================
-- (concept_node_links table already defined above)

-- ============================================================
-- ERROR NODE MAPPINGS - defined in section 4.2
-- ============================================================
-- (error_node_mappings table already defined above)

-- ============================================================
-- GENERATED CONTENT - defined in section 4.3
-- ============================================================
-- (generated_content table already defined above)

-- ============================================================
-- COURSE GRANULARITY OVERRIDES - defined in section 6.2
-- ============================================================
-- (course_granularity_overrides table already defined above)
```

### 8.2 Dual-Write Pattern (Relational + AGE)

The KG data exists in two forms:
1. **Apache AGE graph**: For graph traversals (prerequisite chains, path finding, DAG validation).
2. **Relational shadow tables** (`kg_nodes`, `kg_edges`): For JOIN-heavy queries with KMM state, coverage analysis, and standard CRUD operations.

All writes go through the KG service, which updates both representations within a single PostgreSQL transaction:

```python
async def create_macro_node(self, node: MacroNodeCreate) -> MacroNode:
    async with self.db.transaction():
        # 1. Insert into relational shadow table
        row = await self.db.execute(
            "INSERT INTO kg_nodes (...) VALUES (...) RETURNING *",
            node.dict()
        )

        # 2. Create vertex in AGE graph
        await self.db.execute("""
            SELECT * FROM cypher('maestro_kg', $$
                CREATE (n:MacroNode {id: $id, ...})
            $$) AS (node agtype)
        """, {"id": str(row.id), ...})

        # 3. Initialize KMM states for enrolled students
        await self.kmm_service.initialize_states_for_node(row.id, row.course_id)

        return MacroNode.from_row(row)
```

This dual-write adds some complexity but provides the best query performance for both graph and relational access patterns. The relational table is the source of truth; the AGE graph is reconstructible from it.

### 8.3 Partitioning Strategy

For MVP scale (~500 nodes, ~30 students), partitioning is not needed for KG tables. However, the following tables are partitioned from day one for growth:

- `lesson_chunks`: Partitioned by `course_id` (list partitioning). Each course gets its own partition, keeping vector indexes smaller and course-scoped queries fast.
- `error_node_mappings`: Partitioned by `created_at` (monthly range partitioning) via pg_partman.
- `generated_content`: Partitioned by `created_at` (monthly range partitioning).

---

## 9. API Contract (Draft)

The KG service exposes a REST API consumed by other MAESTRO components. All endpoints require authentication via Keycloak JWT.

### 9.1 KG Structure Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/courses/{courseId}/kg/nodes` | List all active nodes (macro + micro) | teacher, student |
| `GET` | `/api/v1/courses/{courseId}/kg/nodes/macro` | List macro nodes only | teacher, student |
| `GET` | `/api/v1/courses/{courseId}/kg/nodes/{nodeId}` | Get node detail with children | teacher, student |
| `POST` | `/api/v1/courses/{courseId}/kg/nodes` | Create a node | teacher |
| `PUT` | `/api/v1/courses/{courseId}/kg/nodes/{nodeId}` | Update a node | teacher |
| `DELETE` | `/api/v1/courses/{courseId}/kg/nodes/{nodeId}` | Deactivate a node | teacher |
| `GET` | `/api/v1/courses/{courseId}/kg/edges` | List all edges | teacher |
| `POST` | `/api/v1/courses/{courseId}/kg/edges` | Create an edge (with DAG validation) | teacher |
| `DELETE` | `/api/v1/courses/{courseId}/kg/edges/{edgeId}` | Remove an edge | teacher |
| `GET` | `/api/v1/courses/{courseId}/kg/prerequisites/{nodeId}` | Get prerequisite chain for a node | teacher, student, system |
| `POST` | `/api/v1/courses/{courseId}/kg/validate-dag` | Run full DAG validation | teacher, admin |

### 9.2 Ingestion Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/courses/{courseId}/materials` | Upload lesson material | teacher |
| `POST` | `/api/v1/courses/{courseId}/materials/batch` | Batch upload | teacher |
| `GET` | `/api/v1/courses/{courseId}/materials` | List materials with status | teacher |
| `GET` | `/api/v1/courses/{courseId}/materials/{materialId}` | Get material detail | teacher |
| `GET` | `/api/v1/courses/{courseId}/materials/{materialId}/transcript` | Get transcript | teacher |
| `PUT` | `/api/v1/courses/{courseId}/materials/{materialId}/transcript` | Edit transcript | teacher |
| `GET` | `/api/v1/courses/{courseId}/materials/{materialId}/mappings` | Get concept mappings | teacher |
| `POST` | `/api/v1/courses/{courseId}/materials/{materialId}/mappings` | Confirm/reject mappings | teacher |

### 9.3 Concept Mapping Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/courses/{courseId}/mappings/suggest` | Get mapping suggestions for content | system |
| `POST` | `/api/v1/courses/{courseId}/mappings/error` | Map student errors to micro-nodes | system |
| `GET` | `/api/v1/courses/{courseId}/coverage` | Get coverage analysis | teacher |
| `GET` | `/api/v1/courses/{courseId}/coverage/gaps` | Get uncovered/partial nodes | teacher |

### 9.4 Retrieval Endpoints (Internal)

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/courses/{courseId}/retrieve` | Semantic search over lesson chunks | system |
| `GET` | `/api/v1/nodes/{nodeId}/materials` | Get materials linked to a node | system, teacher |
| `GET` | `/api/v1/nodes/{nodeId}/deep-link` | Get specific lesson segment for a node | system, student |

### 9.5 Response Formats

All responses follow the pattern:

```json
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO-8601"
  }
}
```

Error responses:

```json
{
  "error": {
    "code": "DAG_CYCLE_DETECTED",
    "message": "Adding this prerequisite would create a cycle: A -> B -> C -> A",
    "details": { "cycle_path": ["A", "B", "C", "A"] }
  },
  "meta": { ... }
}
```

---

## 10. MVP Scope vs V1/V2

### 10.1 MVP (1 school, 1 class, 1 course)

| Component | MVP Scope |
|---|---|
| **KG schema** | Full macro/micro node structure with all attributes. PREREQUISITE + PARENT_OF edges. |
| **DAG validation** | Real-time at write time + nightly batch. |
| **Document ingestion** | PDF, DOCX, PPTX parsing. Text extraction + chunking + embedding. |
| **Audio/video ingestion** | Whisper transcription + basic diarization. Editable transcript. |
| **Concept mapping** | Auto-suggestion via embedding + LLM. Teacher validation UI (split view). |
| **Error-to-micro mapping** | LLM-based mapping with confidence scoring. >= 80% auto-proposed, < 80% flagged. |
| **Vector indexing** | pgvector with HNSW. Course-scoped retrieval. |
| **Coverage analysis** | Basic gap detection (nodes with < 3 sources). Teacher alerts. |
| **Granularity** | Default rules by school level. Teacher override. |
| **KG updates** | Full CRUD on nodes and edges, live (no restart). |
| **RELATED_TO edges** | Not in MVP. |

### 10.2 V1 (3 schools, multi-class)

| Component | V1 Addition |
|---|---|
| **Coverage gap detection** | Full F2.12 with priority-ranked alerts and dashboard integration. |
| **RELATED_TO edges** | Soft links for content discovery and cross-concept suggestions. |
| **KG templates** | Pre-built KG templates per curriculum (MIUR Informatica triennio, etc.). Teachers can fork and customize. |
| **Batch concept mapping** | Process an entire module's materials in one validation session. |
| **Override mass mapping** | Teacher confirms/overrides error-to-micro mappings for entire class at once. |
| **Node embeddings refresh** | Automatic recomputation when linked content changes. |

### 10.3 V2 (multi-school, multi-subject)

| Component | V2 Addition |
|---|---|
| **Multi-subject KGs** | Same student may have KGs for multiple subjects (Informatica, Matematica). Cross-subject prerequisite edges. |
| **KG federation** | Schools can share KG templates. A "national" KG template endorsed by MIUR. |
| **Automated KG evolution** | LLM suggests new nodes based on curriculum updates. Teacher approves. |
| **Graph algorithms** | Community detection for concept clusters, centrality analysis for "gateway concepts." Migration to Neo4j if needed (ADR-001). |
| **Advanced analytics** | Per-node difficulty calibration based on cohort data. FSRS integration for node difficulty estimates. |

---

## Appendix A: Example KG Structure (F1.10)

```
Course: "Informatica 3AI" (triennio_secondo_grado, anno 3)

MacroNode: "Concetto di algoritmo" (base, anno 3)
  |-- MicroNode: "Definizione di algoritmo" (base, remember)
  |-- MicroNode: "Proprieta: finitezza" (base, understand)
  |-- MicroNode: "Proprieta: determinatezza" (base, understand)
  |-- MicroNode: "Proprieta: non ambiguita" (base, understand)
  |-- MicroNode: "Rappresentazione: pseudocodice" (base, apply)
  |-- MicroNode: "Rappresentazione: diagramma di flusso" (base, apply)

MacroNode: "Variabili e tipi di dato" (base, anno 3)
  |-- MicroNode: "Dichiarazione di variabile" (base, remember)
  |-- MicroNode: "Tipi primitivi: int, float, string, bool" (base, understand)
  |-- MicroNode: "Casting e conversione di tipo" (intermedio, apply)
  |-- MicroNode: "Scope e visibilita" (intermedio, understand)

MacroNode: "Strutture di controllo" (base, anno 3)
  |-- MicroNode: "If/else" (base, apply)
  |-- MicroNode: "Switch/case" (base, apply)
  |-- MicroNode: "Ciclo for" (base, apply)
  |-- MicroNode: "Ciclo while/do-while" (base, apply)
  |-- MicroNode: "Cicli annidati" (intermedio, apply)
  |-- MicroNode: "Break e continue" (intermedio, understand)

Prerequisite edges:
  "Concetto di algoritmo" --[PREREQUISITE, required]--> "Strutture di controllo"
  "Variabili e tipi di dato" --[PREREQUISITE, required]--> "Strutture di controllo"
  "Dichiarazione di variabile" --[PREREQUISITE, required]--> "Scope e visibilita"
  "If/else" --[PREREQUISITE, required]--> "Cicli annidati"
  "Ciclo for" --[PREREQUISITE, required]--> "Cicli annidati"

MacroNode: "Sessioni PHP" (avanzato, anno 5)
  |-- MicroNode: "Cos'e una sessione HTTP" (base, understand)
  |-- MicroNode: "session_start() e ciclo di vita" (intermedio, apply)
  |-- MicroNode: "Variabili di sessione: lettura e scrittura" (intermedio, apply)
  |-- MicroNode: "Session hijacking: rischio e prevenzione" (avanzato, analyze)
  |-- MicroNode: "Session fixation: rischio e mitigazione" (avanzato, analyze)
  |-- MicroNode: "Sessioni vs cookie: differenze e casi d'uso" (intermedio, analyze)
```

---

## Appendix B: Glossary

| Term | Definition |
|---|---|
| **MacroNode** | A structural concept unit visible to students and families (e.g., "Sessioni PHP"). |
| **MicroNode** | A fine-grained sub-concept used by the diagnostic engine (e.g., "Session hijacking: rischio e prevenzione"). |
| **PREREQUISITE** | A directed edge indicating that the source concept must be understood before the target. |
| **PARENT_OF** | A containment edge from MacroNode to MicroNode. |
| **DAG** | Directed Acyclic Graph. The PREREQUISITE edges must form a DAG (no cycles). |
| **KMM** | Knowledge Map Manager. The service that manages per-(student, node) mastery state. |
| **Worst-state rollup** | Macro state = worst state among all active micro children (ADR-002). |
| **Concept mapping** | The process of linking lesson content segments to KG nodes. |
| **Coverage** | The number and diversity of learning materials linked to a KG node. |
| **Deep-link** | A reference from a study path to a specific timestamp range in a lesson recording. |
