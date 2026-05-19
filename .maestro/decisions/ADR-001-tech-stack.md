# ADR-001: MAESTRO Tech Stack

**Status**: Proposed
**Date**: 2026-05-18
**Author**: MSTR-02 (Chief Technical Architect)
**Approved by**: Pending CPA co-sign on pedagogically-touching interfaces, pending QA Sentinel review
**Task**: T1.2 (Tech Stack Revalidation)

---

## Context

MAESTRO is a multi-agent personalised learning companion for minor IT students (13-19) in Italian high schools. The v0.2/v0.3 requirements document (section 5) provides a reference technology stack, explicitly marked as "input for revalidation, not decisions." This ADR evaluates each component against the following non-negotiable constraints:

1. **EU data residency** (GDPR, minors, Art. 8/9) -- no data leaves EU; no CLOUD Act exposure
2. **No PII to external LLMs** -- pseudonymisation at the boundary (N1)
3. **Performance** -- review doc <=60s, remediation <=30s, quiz <=15s, chat <=3s P95 (N4)
4. **WCAG 2.1 AA** conformance (N5)
5. **Cost sensitivity** -- Italian public school budget, risk R9 (LLM cost escalation)
6. **MVP simplicity** -- 1 school, 1 class, 1 teacher; no premature engineering
7. **V1/V2 extensibility** -- no decisions that force rewrites for 6-language, 12-language, multi-school expansion

Each decision below references specific functional (F) and non-functional (N) requirement IDs from the v0.3 requirements document.

---

## Decisions

### 1. LLM Provider

**Decision**: **Claude API (Anthropic)** as primary, with **OpenAI GPT-4o-mini** as cost-optimised secondary for batch/low-complexity tasks. Architecture designed for provider-agnostic switching via abstraction layer.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| Claude API only | Best instruction-following, 200K context, strong Italian, safety training | Single-vendor lock-in, EU data processing agreement required |
| OpenAI GPT-4o only | Broad ecosystem, competitive pricing | Weaker on long-context instruction-following vs Claude; similar EU concerns |
| Self-hosted open-source (Qwen 3.6, Mistral Medium 3.5) | Full data sovereignty, no PII boundary concern | 70-95% cheaper per token but requires GPU infrastructure, lower quality on Italian pedagogical content, higher ops burden |
| Hybrid: proprietary primary + open-source fallback | Cost savings on simple tasks | Operational complexity of managing two inference stacks |

**Rationale**: Claude's instruction-following superiority is critical for MAESTRO's pedagogically-sensitive content generation (F5, F8, F11.7). The pseudonymisation boundary (N1) mitigates the PII-to-external-LLM risk regardless of provider. For MVP, self-hosting LLMs adds GPU infrastructure cost and ops burden disproportionate to a 1-class deployment. GPT-4o-mini handles lower-stakes tasks (F2.4 concept mapping suggestions, F4.2 error-to-concept mapping) at ~10x lower cost.

**Architecture requirement**: All LLM calls go through a `LLMGateway` service that:
- Pseudonymises all PII before prompt construction (student name -> `STUDENT_0042`)
- Routes requests to Claude or GPT-4o-mini based on task complexity
- Logs prompt hashes + model version for audit trail (N7, F14.10)
- Supports swapping providers without downstream code changes

**Consequences**:
- (+) Best available quality for Italian-language pedagogical content
- (+) Pseudonymisation boundary satisfies N1 regardless of provider geography
- (+) Cost optimisation via tiered routing (R9 mitigation)
- (-) Dependency on two external API providers
- (-) Must negotiate EU data processing agreements with both Anthropic and OpenAI
- (-) V1/V2: if self-hosted open-source models reach parity, migration path is clean via LLMGateway

**EU compliance**: Both Anthropic and OpenAI offer EU data processing agreements. With pseudonymisation at the boundary, no PII reaches external systems. Prompt content contains only pseudonymised student IDs, concept names from the KG, and sanitised error descriptions. This architecture is GDPR-compliant even with US-headquartered providers.

**Requirements addressed**: F5 (text generation), F6 (podcast scripts), F8 (language adaptation), F11.7 (remediation paths), F11.8 (quiz generation), N1 (privacy), N4 (performance), R9 (cost)

---

### 2. Vector Database

**Decision**: **pgvector** (PostgreSQL extension) for MVP. Evaluate migration to **Qdrant** self-hosted if vector count exceeds 5M or filtered-search latency degrades.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| pgvector on PostgreSQL | Zero new infrastructure (reuses state store PG), single backup/monitoring stack, EU-resident by definition, HNSW indexing, 470+ QPS at 99% recall on 50M vectors | Not optimised for pure vector workloads at extreme scale |
| Qdrant (self-hosted) | Best filtered-search performance (1840 QPS on 1M vectors), Rust-based, single binary deployment | New infrastructure component to manage, separate backup strategy |
| Weaviate | Strong multi-tenancy | Java-based, resource-heavy for self-hosting, overkill for MVP scale |
| Pinecone (managed) | Zero ops | US-headquartered, no self-hosted option, CLOUD Act exposure, vendor lock-in |

**Rationale**: MVP scope is 1 school, 1 class, ~30 students, 1 course. The vector corpus consists of lesson transcriptions, teaching materials, and concept embeddings -- likely under 500K vectors. pgvector handles this with margin to spare, and critically, it eliminates an entire infrastructure component. The teaching materials (F2.10) and learning profile vectors (F3.2) live in the same database as the KMM state store, simplifying joins for "find materials relevant to this student's specific gaps" queries.

**Migration trigger**: If V1 (3 schools, 6 classes) pushes vector count past 5M and filtered-search P95 exceeds 200ms, migrate to self-hosted Qdrant on the same EU infrastructure.

**Consequences**:
- (+) Zero additional infrastructure for MVP
- (+) Single backup, single monitoring, single ops runbook
- (+) EU residency guaranteed (same PG instance)
- (+) Clean extension point: pgvector -> Qdrant migration is a data-plane change, not an application rewrite
- (-) Performance ceiling lower than dedicated vector DBs at scale
- (-) Missing advanced features (multi-vector, sparse-dense hybrid) that Qdrant provides

**Requirements addressed**: F2.10 (material indexing), F3.2 (learning profile vectors), F5 (RAG for text generation), N1 (EU residency), R9 (cost -- no additional service)

---

### 3. Knowledge Graph Store

**Decision**: **Apache AGE** (PostgreSQL extension) for MVP. Evaluate migration to **Neo4j Community Edition** (self-hosted) if graph complexity or traversal performance requires it.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| Apache AGE (PG extension) | Cypher query support inside PostgreSQL, no new infrastructure, inherits PG backup/HA, Azure-managed option available, joins KG data with relational KMM data in single query | Less mature than Neo4j, community smaller, fewer graph algorithms built-in |
| Neo4j Community Edition (self-hosted) | Most mature graph DB, rich algorithm library (GDS), strong Cypher, excellent visualisation tools | Separate infrastructure, AGPL license (copyleft), separate backup/monitoring, adds ops burden for MVP |
| ArangoDB | Multi-model (doc + graph + KV), fast benchmarks | BSL 1.1 license (100GB cap on free tier), non-standard query language (AQL), not Cypher-compatible |
| FalkorDB | Redis-based, fast for small graphs | Immature ecosystem, limited tooling |

**Rationale**: The MAESTRO curriculum graph for MVP is small: one course (e.g., "Informatica triennio"), ~50-100 macro-nodes, ~300-500 micro-nodes (F1.7), with prerequisite edges forming a DAG (F1.2). Apache AGE handles this scale trivially. The decisive advantage is **co-location with the KMM state store**: queries like "find all micro-nodes in `lacuna` state for student X that are prerequisites of concept Y" become a single SQL+Cypher query rather than a cross-database join.

Apache AGE reached Apache Top-Level Project status in 2022, is included in Azure Database for PostgreSQL as a managed extension, and supports PostgreSQL 11-18 as of 2025. For MAESTRO's DAG-structured curriculum graph with shallow traversals (typically 2-4 hops for prerequisite chains), AGE is sufficient.

**Migration trigger**: If V1/V2 introduces graph algorithms (community detection, centrality analysis for "most impactful concepts") or the graph exceeds 10K nodes, evaluate Neo4j Community Edition.

**Consequences**:
- (+) Single database engine for the entire MAESTRO data layer (KMM + KG + vectors)
- (+) Transactional consistency: KG updates and KMM state transitions in the same ACID transaction
- (+) Dramatically simpler infrastructure for MVP
- (-) Fewer built-in graph algorithms than Neo4j GDS
- (-) Smaller community, less tooling for graph visualisation during development
- (-) V1/V2: if graph analytics become a core feature, Neo4j migration is needed

**Requirements addressed**: F1.1-F1.10 (curriculum KG), F2.4 (lesson-to-concept mapping), F11.1 (knowledge map), F11.4 (state transitions referencing KG nodes), F11.11 (macro/micro aggregation)

---

### 4. State Store (KMM + F14 + Audit)

**Decision**: **PostgreSQL 17** as the single relational database, with **partitioned tables and BRIN indexes** for time-series KMM transition history. No TimescaleDB for MVP.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| PostgreSQL 17 with partitioned tables | Native partitioning by time, BRIN indexes for time-range queries, zero additional extensions, battle-tested | Manual partition management (automate via pg_partman) |
| PostgreSQL + TimescaleDB | Purpose-built time-series on PG, hypertable auto-partitioning, compression | Additional extension, licensing (community vs enterprise), adds complexity for MVP-scale data |
| PostgreSQL + separate ClickHouse for analytics | Best OLAP performance | Two database engines to manage, overkill for MVP |

**Rationale**: The KMM stores per-(student, node) state with transition history (F11.5). For MVP (30 students, ~500 nodes, ~6 transitions per node per semester), this is ~90K transition records per semester. PostgreSQL with time-based partitioning handles this without breaking a sweat. TimescaleDB's hypertables add value at millions of rows per day -- not MAESTRO's write pattern.

The audit log (F14.10) is append-only, write-once. PostgreSQL with a trigger-based immutability pattern (deny UPDATE/DELETE on audit tables) satisfies the tamper-evidence requirement.

**Data model highlights**:
- `kmm_states` table: (student_id, node_id, current_state, last_transition_at)
- `kmm_transitions` table: (id, student_id, node_id, prev_state, new_state, cause, evidence_ref, timestamp) -- partitioned by month
- `audit_log` table: (id, actor_id, action, entity_type, entity_id, prev_value, new_value, timestamp) -- append-only, partitioned by month
- `consents` table: (student_id, consent_type, granted, granted_by, granted_at, revoked_at) -- 5 rows per student per F14.3

**Consequences**:
- (+) Single database engine -- PostgreSQL serves KMM, KG (AGE), vectors (pgvector), audit, and relational data
- (+) ACID transactions across all data domains
- (+) Mature ecosystem: pg_partman for auto-partitioning, pgaudit for access logging
- (+) EU residency trivially enforced (single PG instance in EU region)
- (-) If heatmap analytics (F11.13, F11.14) require sub-second aggregations over millions of rows, TimescaleDB or a CQRS read model may be needed in V1
- (-) Manual partition management (mitigated by pg_partman)

**V1/V2 path**: Add TimescaleDB extension if time-series query patterns warrant it. The migration is additive (convert existing partitioned tables to hypertables) -- no schema rewrite.

**Requirements addressed**: F11 (entire state machine), F14 (identity/consent/enrolment), F14.10 (audit log), N1 (EU residency), N2 (DR RPO<=24h via pg_basebackup + WAL archiving)

---

### 5. Backend Orchestration Framework

**Decision**: **LangGraph** (Python) for multi-agent orchestration, with **FastAPI** as the HTTP/WebSocket API layer.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| LangGraph | Graph-based agent orchestration with durable state, human-in-the-loop checkpoints, audit-trail-friendly (every state transition is a checkpoint), 34% enterprise adoption share (Gartner Q1 2026), Python ecosystem | LangChain dependency (though decoupling), Python GIL limits single-process throughput |
| CrewAI | Lower learning curve, role-based agent teams | Less precise execution flow control, weaker durable state, less enterprise adoption |
| AutoGen (Microsoft) | Multi-party conversations | Shifted to maintenance mode in favour of Microsoft Agent Framework; risky for long-term dependency |
| Custom orchestration (no framework) | Full control, no dependency | Reimplements state management, checkpointing, retry logic; high engineering cost |

**Rationale**: LangGraph's graph-based execution model maps directly to MAESTRO's agent architecture (section 5 of v0.3): the Orchestrator coordinates Curriculum Ingestion, Student Profiler, Diagnostic, Content Orchestrator, KMM, and Safeguarding agents as nodes in a directed graph. LangGraph's durable checkpointing is critical for MAESTRO's audit requirements -- every agent step is checkpointed and replayable, which maps directly to N7 (transparency) and F14.10 (audit trail).

FastAPI provides the HTTP layer for teacher dashboard, student mobile app, and admin interfaces. It handles authentication, rate limiting, and request routing, delegating agent-workflow invocations to LangGraph.

**Architecture**:
```
Mobile App / Dashboard
        |
    FastAPI (REST + WebSocket)
        |
    LangGraph Orchestrator
        |
    +---+---+---+---+---+
    |   |   |   |   |   |
   CI  SP  DA  IC  KMM  CO -> Safeguarding -> Student
```
(CI=Curriculum Ingestion, SP=Student Profiler, DA=Diagnostic Agent, IC=Identity/Consent, KMM=Knowledge Map Manager, CO=Content Orchestrator)

**Consequences**:
- (+) Durable state + checkpointing = audit trail for every agent decision
- (+) Human-in-the-loop built-in (teacher override flows per F11.12)
- (+) Mature Python ecosystem for LLM tooling, NLP, data processing
- (+) Enterprise adoption trajectory reduces long-term risk
- (-) Python's GIL limits per-process throughput (mitigated by async + horizontal scaling)
- (-) LangChain dependency introduces transitive dependency surface
- (-) V1/V2: if agent count grows significantly, may need to distribute across processes

**Requirements addressed**: F11 (state machine orchestration), F14 (identity flows), N4 (performance -- async execution), N7 (transparency via checkpoints), F4 (diagnostic workflow), F5 (content generation workflow)

---

### 6. Frontend Framework

**Decision**: **React Native** (with Expo) for student mobile app; **Next.js** (React) for teacher dashboard web application.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| React Native + Expo | Native platform components (accessibility wins), VoiceOver/TalkBack/Switch Control work automatically, JavaScript/TypeScript ecosystem, Expo simplifies builds/OTA updates, offline support via Expo SQLite | Slightly lower UI consistency across platforms than Flutter |
| Flutter | Consistent pixel-perfect UI, fast development, 46% market share | Custom rendering engine bypasses native accessibility APIs (higher WCAG testing burden), Dart ecosystem smaller than JS/TS, accessibility requires more manual work |
| Native (Swift + Kotlin) | Best accessibility, best performance | Double codebase, double maintenance, disproportionate for MVP |
| PWA | No app store, single codebase | Limited offline, no push notifications on iOS, no native feel |

**Rationale**: WCAG 2.1 AA conformance (N5) is non-negotiable and MVP-priority. React Native renders using native platform components (UIKit on iOS, Android Views on Android), so built-in accessibility features -- VoiceOver, TalkBack, dynamic text sizing, Switch Control -- work automatically for standard components. This is a structural advantage over Flutter, which uses its own rendering engine and requires manual accessibility implementation.

The teacher dashboard is a web application (not mobile-first), so Next.js (React) is the natural choice: same component library, same design system tokens, shared TypeScript types with the mobile app. Server-side rendering supports the data-heavy heatmap views (F11.14, F12.1).

**Shared infrastructure**:
- TypeScript monorepo (pnpm workspaces)
- Shared design system package implementing F9 (accessibility tokens, colour palette, font stack)
- Shared API client (generated from OpenAPI spec)

**Consequences**:
- (+) Native accessibility APIs reduce WCAG compliance burden
- (+) VoiceOver/TalkBack work out-of-the-box for standard components
- (+) React ecosystem: largest component library selection, strong TypeScript support
- (+) Expo simplifies CI/CD, OTA updates, and offline storage (N8)
- (+) Shared codebase between mobile and web (design system, API types)
- (-) Bridge-based architecture can introduce latency for complex animations (mitigated: MAESTRO is data-display-heavy, not animation-heavy)
- (-) Requires React Native + React expertise (single skill set, but dual platform knowledge)

**Requirements addressed**: F9 (accessibility/design system), F11.1 (knowledge map visualisation), F12 (teacher dashboard), N5 (WCAG 2.1 AA), N8 (offline), N9 (UI internationalisation)

---

### 7. TTS Provider

**Decision**: **OpenAI TTS API** for MVP (V1 feature -- podcast is not MVP scope). Evaluate **ElevenLabs** for V1 if voice quality/variety requirements demand it.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| OpenAI TTS | $15/1M chars, 11 high-quality voices, simple API, adequate multilingual support | Fewer voice options, less expressive than ElevenLabs |
| ElevenLabs | Best quality (4.14 MOS), 3000+ voices, 74 languages, 75ms latency (Flash), voice cloning | Expensive ($99-$330/mo for production volumes), cost scales with usage |
| Azure Neural TTS | 140+ languages, 500+ voices, $15-30/1M chars, EU region available | More complex API, lower quality than ElevenLabs |
| Self-hosted (Coqui/VITS) | Full data sovereignty, zero per-character cost | Quality gap, limited multilingual, requires GPU hosting |

**Rationale**: Podcast generation (F6) is a V1 feature, not MVP. For MVP, no TTS is needed. When V1 introduces podcasts, OpenAI TTS at $15/1M characters provides adequate quality at predictable cost. The two-voice podcast format (F6.1) needs only 2 distinct voices per language, well within OpenAI's 11-voice library.

If V1 user testing reveals that voice quality/expressiveness is critical for student engagement (especially for the "curioso" vs "esperto" dialogue format per F6.3), upgrade to ElevenLabs. The TTS call is already abstracted behind the Content Orchestrator, so switching providers is a configuration change.

**MVP scope note**: Text-to-speech for accessibility (screen readers) is handled by the OS, not by the application's TTS provider. F9.6 (WCAG) and F6 (podcast) use different TTS pathways.

**Consequences**:
- (+) Zero TTS cost in MVP (podcast is V1)
- (+) Predictable pricing when V1 launches ($15/1M chars)
- (+) Simple integration (single API call)
- (-) Limited voice variety (11 voices) -- may not satisfy F6.2 "library of voices"
- (-) Voice quality adequate but not best-in-class
- (-) V1: if ElevenLabs is needed, cost increases significantly

**Requirements addressed**: F6 (V1 -- podcast), F13.11 (V1 -- cross-language podcast), R9 (cost control)

---

### 8. Cloud Infrastructure & EU Residency

**Decision**: **Hetzner Cloud** (primary compute + managed PostgreSQL) + **Scaleway Object Storage** (S3-compatible, for lesson materials and backups). Both are EU-native providers with no CLOUD Act exposure.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| Hetzner Cloud | 14.3x value vs AWS, EU-only (Germany/Finland), no US parent, no CLOUD Act, excellent price/performance | Minimal managed services, requires more self-management |
| Scaleway | Deep managed service stack (managed K8s, managed DBs, GPU, serverless), EU-native (France), no CLOUD Act | 3-4x more expensive than Hetzner for equivalent compute |
| OVHcloud | Broad service catalogue | Canadian subsidiary with demonstrated CLOUD Act-adjacent legal exposure |
| AWS eu-west-1 | Most mature, broadest services | US-headquartered, CLOUD Act exposure, 14x more expensive than Hetzner |
| Azure (EU region) | Managed PG, managed K8s | US-headquartered, CLOUD Act exposure |

**Rationale**: EU data residency is non-negotiable (CLAUDE.md, N1). Hetzner is a German company with data centres in Falkenstein, Nuremberg, and Helsinki -- no US parent company, no CLOUD Act jurisdiction. For MVP (1 school, 30 students, 1 teacher), Hetzner's compute pricing is unbeatable: a dedicated server with 64GB RAM runs ~EUR 50/month vs ~EUR 700 for equivalent AWS.

Scaleway complements Hetzner for S3-compatible object storage (lesson uploads per F2.1 -- up to 500MB video files) and as a future GPU provider for V1/V2 if self-hosted LLM inference becomes desirable.

**MVP infrastructure**:
- 1x Hetzner Cloud CCX33 (8 vCPU, 32GB RAM, ~EUR 55/mo) -- runs FastAPI + LangGraph + PostgreSQL (with AGE + pgvector)
- 1x Hetzner Cloud CX22 (2 vCPU, 4GB RAM, ~EUR 5/mo) -- runs Redis (caching, task queues) + monitoring
- Scaleway Object Storage (~EUR 0.01/GB/mo) -- lesson materials, backups, generated content
- Total estimated infrastructure cost: **~EUR 80-120/month for MVP**

**V1/V2 path**: Migrate to Hetzner Cloud dedicated servers or Scaleway managed Kubernetes (Kapsule) when multi-school deployment requires horizontal scaling. The application is containerised from day 1 (Docker), making the migration straightforward.

**Consequences**:
- (+) Full EU sovereignty -- no CLOUD Act exposure, no data transit outside EU
- (+) Order-of-magnitude cost savings vs hyperscalers (critical for R9 / public school budget)
- (+) Simple infrastructure for MVP (2 servers + object storage)
- (-) Less managed services than hyperscalers -- team must manage PG, backups, monitoring
- (-) No managed Kubernetes for MVP (not needed at this scale)
- (-) V1/V2: scaling requires more infrastructure engineering effort

**DR compliance (N2)**: RPO <=24h via PostgreSQL WAL archiving to Scaleway Object Storage (continuous archiving, point-in-time recovery). RTO <=4h via automated server provisioning + WAL replay. Tested quarterly.

**Requirements addressed**: N1 (EU residency), N2 (DR: RPO<=24h, RTO<=4h), R9 (cost), N4 (99.5% availability via Hetzner's 99.9% SLA)

---

### 9. Authentication (SSO + MFA)

**Decision**: **Keycloak** (self-hosted) for identity and access management, supporting SAML 2.0, OpenID Connect, TOTP, and WebAuthn.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| Keycloak (self-hosted) | Open source (Apache 2.0), SAML 2.0 + OIDC + LDAP, built-in TOTP + WebAuthn/Passkeys, mature (Red Hat backed), runs on single VPS, EU-resident by deployment | Requires self-management, Java-based (higher memory footprint) |
| Authentik | Modern UI, Python-based, lighter | Less mature than Keycloak, smaller enterprise track record |
| Auth0 (managed) | Zero ops, rich feature set | US-headquartered (Okta), CLOUD Act exposure, cost at scale |
| Zitadel | Go-based, lightweight, open source | Newer, less proven in education/SAML-heavy environments |

**Rationale**: Italian schools use SAML 2.0-based identity providers (registro elettronico integration). Keycloak is the most battle-tested open-source solution for SAML 2.0 federation, and it's the only option with proven compatibility across the fragmented Italian school IdP landscape. Built-in TOTP and WebAuthn/Passkey support satisfy N2 (MFA for admin). Self-hosting on Hetzner ensures EU residency for all authentication data.

**Configuration for MAESTRO**:
- Realm: `maestro`
- Client: `maestro-student-app` (OIDC, PKCE flow for mobile)
- Client: `maestro-teacher-dashboard` (OIDC, authorization code flow)
- Client: `maestro-admin` (OIDC + MFA required)
- Identity Provider: configurable per school (SAML 2.0 federation to school IdP)
- Role mapping: `student`, `teacher`, `coordinator`, `admin`, `family`
- MFA: Required for `admin` role (TOTP or WebAuthn per N2); optional for others

**Consequences**:
- (+) Full SAML 2.0 + OIDC support covers all school IdP scenarios
- (+) Built-in MFA (TOTP + WebAuthn) satisfies N2
- (+) EU-resident by deployment (on Hetzner)
- (+) Passkey support future-proofs authentication UX
- (+) Free and open source -- no per-user licensing cost
- (-) Java-based: ~512MB-1GB RAM footprint (acceptable on dedicated infrastructure)
- (-) Requires operational maintenance (upgrades, certificate rotation)
- (-) UI customisation requires Keycloak theming knowledge

**Requirements addressed**: N2 (SSO SAML 2.0 / OIDC, MFA for admin), F14.6 (first activation credentials), F14.1 (account lifecycle)

---

### 10. Observability & Monitoring

**Decision**: **OpenTelemetry** (instrumentation) + self-hosted **Grafana stack** (Grafana + Loki + Tempo + Mimir) for dashboards, logs, traces, and metrics.

**Alternatives considered**:

| Option | Pros | Cons |
|---|---|---|
| OpenTelemetry + Grafana stack (self-hosted) | Open source, vendor-neutral telemetry, full stack (metrics/logs/traces), self-hosted for EU residency, ~EUR 20/mo | Requires setup and maintenance |
| Datadog | Best-in-class UX, easy setup | US-headquartered, expensive ($15-23/host/mo + per-GB), data leaves EU without explicit configuration |
| Grafana Cloud | Managed Grafana stack, free tier for small teams | Data processed by Grafana Labs (US HQ, though EU storage available) |
| Prometheus + ELK stack | Mature components | Higher operational complexity, ELK is resource-hungry |

**Rationale**: Self-hosted Grafana stack on Hetzner ensures all observability data (which may include pseudonymised student activity patterns) stays within EU jurisdiction. OpenTelemetry is the CNCF standard for instrumentation -- it provides vendor-neutral SDKs for Python (LangGraph/FastAPI) and TypeScript (React Native/Next.js). Grafana Alloy (OpenTelemetry Collector distribution) simplifies collection and routing.

**Key dashboards for MAESTRO**:
- **LLM cost tracking**: token consumption per agent, per student, per day (R9 mitigation)
- **Generation latency P95**: per content type vs N4 targets (60s/30s/15s/3s)
- **Agent workflow health**: LangGraph checkpoint success/failure rates
- **Safeguarding intervention rate**: per category (N3)
- **Error rates**: per API endpoint, per service
- **Infrastructure**: CPU, memory, disk, PG connection pool, WAL lag

**Consequences**:
- (+) Full EU data sovereignty for observability data
- (+) OpenTelemetry instrumentation is vendor-neutral -- migrate to managed service if needed
- (+) Cost: ~EUR 20/mo on Hetzner (runs on the monitoring server)
- (+) LLM-specific observability (token tracking, latency per model) built-in
- (-) Requires initial setup effort (Grafana Alloy + Loki + Tempo + Mimir)
- (-) Self-managed: upgrades, retention policy management, storage scaling

**Requirements addressed**: N4 (performance monitoring), R9 (cost monitoring), N7 (transparency -- agent decision audit), N2 (99.5% availability monitoring)

---

## Cross-Cutting Concerns

### Pseudonymisation Strategy

All interactions with external LLM providers pass through the `LLMGateway` service, which:

1. **Replaces PII with pseudonyms** before prompt construction:
   - Student name -> `STUDENT_{internal_hash_prefix}`
   - Teacher name -> `TEACHER_{internal_hash_prefix}`
   - School name -> `SCHOOL_001`
   - Native language (Art. 9) -> **never included in LLM prompts**; bilingual content generation uses language code only (e.g., `uk` for Ukrainian), never the student's identity
2. **Maintains a session-scoped mapping table** (in-memory, never persisted to disk or sent externally)
3. **Re-hydrates pseudonyms** in LLM responses before delivering to the student
4. **Logs pseudonymised prompts** to the audit trail (N7, F14.10) -- the audit stores the pseudonymised version, not the original PII

This satisfies N1 (no PII to external LLMs) and ensures GDPR Art. 9 compliance for native language data.

### Caching Strategy (R9 Cost Mitigation)

LLM API calls are the dominant cost driver (R9). MAESTRO implements multi-layer caching:

1. **Semantic cache** (pgvector similarity search): Before calling the LLM, check if a semantically similar request has been answered. Threshold: cosine similarity >= 0.95. Covers: F5 text generation for common concepts, F11.8 quiz generation for frequently-tested micro-nodes.
2. **Deterministic cache** (Redis): Exact-match cache for identical prompts. Covers: F2.4 concept mapping (same lesson -> same concepts), F4.2 error mapping.
3. **Batch generation** (overnight): Pre-generate remediation content for the top 20 most common `lacuna` micro-nodes per class. Runs during off-peak hours (N4: 99.5% availability is school-hours only).
4. **Tiered model routing**: Route simple tasks (concept extraction, quiz formatting) to GPT-4o-mini (~$0.15/1M input tokens) instead of Claude (~$5/1M input tokens).

**Estimated cost savings**: 60-70% reduction vs naive "call Claude for everything" approach.

### Offline Support (N8)

The React Native + Expo stack supports offline via:

1. **Expo SQLite**: Local cache of already-viewed content (remediation docs, completed quizzes, knowledge map snapshot)
2. **Expo FileSystem**: Downloaded lesson materials and generated PDFs
3. **Action queue**: Student actions performed offline (quiz answers, content views) are queued and synced when connectivity returns
4. **Connectivity indicator**: Banner component per N8 specification

Offline support is read-only for generated content; new content generation requires connectivity (LLM API calls).

---

## Decision Rationale Summary

### The "PostgreSQL-centric" Architecture

The single most consequential decision in this ADR is consolidating three traditionally separate database engines (relational, graph, vector) into **a single PostgreSQL instance** with extensions (AGE for graph, pgvector for vectors). This is not a compromise -- it is a deliberate architectural choice optimised for:

1. **MVP simplicity**: One database to provision, back up, monitor, and secure. For a 1-school pilot, this eliminates two-thirds of the data infrastructure complexity.
2. **Transactional coherence**: A student's KMM state transition (relational), the KG prerequisite it references (graph), and the vector embedding of the generated content (vector) can all participate in a single ACID transaction.
3. **EU residency**: One database instance in one EU data centre. No cross-service data replication to manage.
4. **Cost**: A single PostgreSQL instance on Hetzner costs ~EUR 20/month. Neo4j + Pinecone + PostgreSQL would cost ~EUR 200+/month with three times the operational burden.
5. **Clean extension points**: pgvector -> Qdrant, AGE -> Neo4j, and partitioned tables -> TimescaleDB are all additive migrations, not rewrites. The application code uses repository abstractions that insulate it from the underlying storage engine.

### Stack Coherence

The chosen stack forms a coherent unit:

- **Language**: Python (backend/agents) + TypeScript (frontend) -- two languages, not five
- **Database**: PostgreSQL (one engine, three extensions) -- AGE, pgvector, pg_partman
- **Infrastructure**: Hetzner (EU compute) + Scaleway (EU object storage) -- two EU-native providers
- **Auth**: Keycloak (self-hosted, SAML + OIDC + MFA)
- **Observability**: OpenTelemetry + Grafana stack (self-hosted)
- **LLM**: Claude (primary) + GPT-4o-mini (secondary) via LLMGateway abstraction
- **Frontend**: React (shared component library) -- React Native for mobile, Next.js for web

**Total estimated MVP infrastructure cost**: EUR 80-120/month (excluding LLM API usage).
**Total estimated MVP LLM API cost**: EUR 200-400/month (with caching and tiered routing).
**Total estimated MVP monthly cost**: EUR 300-520/month -- viable for Italian public school budget.

---

## Impact on V1/V2 Horizon

| Component | MVP Choice | V1 Trigger | V2 Trigger | Migration Effort |
|---|---|---|---|---|
| Vector DB | pgvector | >5M vectors or P95 >200ms | Multi-tenant isolation | Medium (data migration to Qdrant) |
| Graph DB | Apache AGE | Graph algorithms needed | >10K nodes, deep traversals | Medium (schema migration to Neo4j) |
| State store | PG partitioned tables | Sub-second aggregation on >1M rows | Real-time analytics | Low (add TimescaleDB extension) |
| LLM | Claude + GPT-4o-mini | Open-source parity + cost pressure | Self-hosted GPU fleet | Low (LLMGateway swap) |
| TTS | None (V1) | Podcast feature launch | Voice library expansion | Low (API integration) |
| Infra | Hetzner single-server | Multi-school, >100 concurrent | >1000 concurrent | Medium (containerise -> K8s on Scaleway) |
| Frontend | React Native + Next.js | N/A | N/A | N/A (stable choice) |
| Auth | Keycloak | N/A | N/A | N/A (stable choice) |
| Monitoring | Self-hosted Grafana | Team prefers managed | N/A | Low (switch to Grafana Cloud) |

No decision in this ADR forces a rewrite for V1 or V2. Every migration path is additive or swap-based.

---

## Appendix: Full Stack Summary

| Layer | Technology | License | EU Residency | Cost (MVP/month) |
|---|---|---|---|---|
| LLM (primary) | Claude API (Anthropic) | Commercial API | Pseudonymised at boundary | ~EUR 150-300 |
| LLM (secondary) | GPT-4o-mini (OpenAI) | Commercial API | Pseudonymised at boundary | ~EUR 50-100 |
| Vector DB | pgvector (PG extension) | PostgreSQL License | Yes (Hetzner) | Included in PG |
| Knowledge Graph | Apache AGE (PG extension) | Apache 2.0 | Yes (Hetzner) | Included in PG |
| State Store | PostgreSQL 17 | PostgreSQL License | Yes (Hetzner) | ~EUR 20 |
| Backend Framework | LangGraph + FastAPI | MIT / MIT | Yes (Hetzner) | Included in compute |
| Mobile App | React Native + Expo | MIT | N/A (client-side) | N/A |
| Web Dashboard | Next.js (React) | MIT | Yes (Hetzner) | Included in compute |
| Auth | Keycloak | Apache 2.0 | Yes (Hetzner) | Included in compute |
| Object Storage | Scaleway Object Storage | Commercial | Yes (France) | ~EUR 5-10 |
| Compute | Hetzner Cloud | Commercial | Yes (Germany/Finland) | ~EUR 60 |
| TTS | OpenAI TTS (V1 only) | Commercial API | Pseudonymised | EUR 0 (MVP) |
| Monitoring | Grafana + Loki + Tempo + Mimir | AGPL 3.0 | Yes (Hetzner) | ~EUR 20 |
| Caching | Redis (self-hosted) | BSD-3 / SSPL | Yes (Hetzner) | Included in compute |

**Total MVP monthly estimate**: EUR 300-520 (infrastructure + LLM API)
