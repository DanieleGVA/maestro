# ADR-003: Orchestrator Pattern

**Status**: Proposed
**Date**: 2026-05-18
**Author**: MSTR-04 (Agent Systems Architect)
**Reviewers required**: MSTR-02 (CTA), MSTR-03 (CPA), MSTR-20 (QA Sentinel)
**Related**: HLD-001 (Multi-Agent System Architecture), ADR-001 (Tech Stack)

---

## Context

MAESTRO's runtime agent system requires an orchestration pattern that coordinates 15 product agents (11 in MVP) with the following hard constraints:

1. **Consent-before-computation**: No agent may operate on student data without verified consent (CLAUDE.md, F14.3). This requires a sequential gate at the start of every workflow.
2. **Safeguarding-before-delivery**: Every content output must pass through the Safeguarding Agent before reaching a student (CLAUDE.md, N3). This requires a sequential gate at the end of every content workflow.
3. **Audit trail**: Every agent decision must be traceable to a specific agent, timestamp, and model version (N7, F14.10).
4. **Human-in-the-loop**: Teacher validation is required at multiple points: concept mapping (F2.4), transition confirmation (F4.4), quiz review (OQ7), override motivation (F11.12).
5. **Durable execution**: Long-running workflows (lesson upload with transcription, class-wide verification analysis) must survive process restarts.

These constraints create strong sequencing requirements that must be enforced architecturally, not by convention.

---

## Decision

**Central orchestrator implemented as a LangGraph StateGraph** with PostgreSQL-backed checkpointing.

The orchestrator is a single `StateGraph` instance that defines all agent-to-agent flows as nodes and edges. Agents do not communicate with each other directly -- they read from and write to a shared state object (`MaestroState`) that flows through the graph. The orchestrator controls execution order through the graph topology.

Key properties:
- **Deterministic**: The graph topology statically defines which agents can execute in which order. No runtime discovery, no dynamic routing.
- **Checkpointed**: Every node execution persists a checkpoint to PostgreSQL via `PostgresSaver`. This provides audit trail and resumability.
- **Interruptible**: `interrupt_before` and `interrupt_after` mechanisms pause the graph at teacher validation points. The workflow resumes when the teacher responds.
- **Stateless agents**: Individual agent nodes are pure functions. All state lives in `MaestroState` and the database.

---

## Alternatives Considered

### A. Peer-to-Peer with Shared Event Bus

Agents communicate via a message broker (e.g., Redis Streams, RabbitMQ). Each agent subscribes to relevant event types and publishes its outputs.

**Pros**:
- Loose coupling between agents
- Independent scaling of each agent
- Natural fit for event-driven architectures

**Cons**:
- Hard to enforce sequential consent gate (race condition: agent processes event before consent is verified)
- Hard to guarantee safeguarding pipeline (content could be delivered without passing through safeguarding if an agent publishes directly)
- Audit trail is fragmented across broker logs -- requires log correlation
- Human-in-the-loop interrupts require complex state management outside the broker
- Operational complexity: message broker infrastructure, dead-letter queues, event schema evolution

**Rejected because**: The consent and safeguarding constraints require guaranteed sequential gates. An event bus makes these guarantees hard to enforce and easy to accidentally bypass.

### B. Hierarchical Sub-Orchestrators

A top-level orchestrator delegates to sub-orchestrators (e.g., "content sub-orchestrator", "assessment sub-orchestrator"), each managing a subset of agents.

**Pros**:
- Separation of concerns at the orchestration level
- Sub-orchestrators can evolve independently
- Natural grouping of related agents

**Cons**:
- Adds indirection without solving the core sequencing problem
- Cross-sub-orchestrator flows (e.g., diagnostic -> content generation -> safeguarding) still need a top-level coordinator
- Over-engineering for the current agent count (11 MVP agents)
- Increases debugging complexity (which sub-orchestrator handled what?)

**Rejected because**: MAESTRO's MVP has 11 agents. A single StateGraph with clear node grouping provides sufficient separation of concerns without the overhead of nested orchestrators. Revisit if V2 agent count exceeds 20.

### C. Custom Orchestration (No Framework)

Build a bespoke orchestrator using Python async primitives, without LangGraph.

**Pros**:
- Full control over execution model
- No framework dependency
- Can be precisely tailored to MAESTRO's needs

**Cons**:
- Must reimplement: durable checkpointing, state management, human-in-the-loop interrupts, graph visualization, retry logic
- High engineering cost for MVP timeline
- No community ecosystem for tooling, debugging, visualization

**Rejected because**: LangGraph provides durable checkpointing, interrupt mechanisms, and graph-based execution out of the box. Reimplementing these would consume engineering time disproportionate to the benefit.

---

## Consequences

### Positive

- **Consent and safeguarding guarantees are structural**: The graph topology makes it impossible to bypass consent gates or safeguarding review. This is enforced by the absence of edges, not by agent-level discipline.
- **Audit trail is automatic**: LangGraph checkpoints capture every state transition. Combined with the `llm_audit_log` table, every decision is fully traceable.
- **Human-in-the-loop is native**: Teacher validation points map directly to LangGraph interrupts. No custom state management needed.
- **Resumability**: If the system crashes during a verification analysis for 30 students, it resumes from the last checkpoint, not from scratch.
- **Debuggability**: LangGraph provides graph visualization and step-through debugging, making it possible to replay any workflow.

### Negative

- **Single orchestrator complexity**: As agent count grows in V1/V2, the StateGraph may become large. Mitigated by using subgraphs (LangGraph supports nested graphs) for logical grouping.
- **LangGraph dependency**: Tight coupling to LangGraph's execution model. Mitigated by keeping agent nodes as pure functions that can be extracted if the framework changes.
- **Python GIL**: The orchestrator runs in a single Python process. For MVP (1 school, 30 students), this is sufficient. V1 scaling uses multiple worker processes with shared PostgreSQL checkpointer.
- **Sequential bottleneck**: Some flows that could theoretically run in parallel (e.g., generating content for 30 students) are serialized by the graph. Mitigated by launching parallel LangGraph invocations for per-student subflows.

### Migration Path

If V2 reveals that the central orchestrator is a bottleneck:
1. Extract sub-orchestrators as separate LangGraph StateGraphs
2. Coordinate via PostgreSQL-based event table (replacing in-process state sharing with database-mediated handoffs)
3. Keep the consent gate and safeguarding gate as cross-cutting middleware, not embedded in sub-orchestrators

---

*ADR filed per CLAUDE.md governance rules. Ratification required by MSTR-02 (CTA). Cross-domain review by MSTR-03 (CPA) for safeguarding enforcement implications.*
