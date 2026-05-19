# ADR-003: Data Model Architecture Decisions

**Status**: Proposed
**Date**: 2026-05-18
**Author**: MSTR-07 (Data & Mastery State Architect)
**Reviewers required**: MSTR-02 (CTA), MSTR-05 (KG Architect), MSTR-11 (Data Engineer), MSTR-16 (Privacy & Compliance)
**Task**: T2.4 (Data & mastery state architecture)
**Related**: ADR-001 (Tech Stack), ADR-002 (Pedagogical Model), HLD-004 (Data & Mastery State Architecture)

---

## Context

MAESTRO requires a data layer that supports: (1) per-(student, node) mastery state tracking with full transition history, (2) GDPR-compliant identity and consent management for minors, (3) an immutable audit trail, and (4) a right-to-erasure procedure. All within a single PostgreSQL 17 instance per ADR-001.

This ADR records the key design decisions made in HLD-004 that have architectural consequences.

---

## Decision 1: Application-Level State Machine Enforcement

### Decision

State transition validation is enforced in the Python application layer (FastAPI service), not in PostgreSQL triggers or stored procedures.

### Alternatives Considered

| Option | Pros | Cons |
|---|---|---|
| **A. Application-level** (chosen) | Full decision context (quiz scores, consent, teacher identity) available; easy to unit test; flexible to evolve; logs complete decision rationale | No database-level protection against invalid transitions from direct SQL |
| **B. PL/pgSQL trigger** | Database enforces invariant regardless of caller | Complex triggers that need to query quiz results, consent tables, teacher identity; hard to test; tightly couples logic to schema |
| **C. CHECK constraint on transitions** | Simplest database enforcement | Cannot encode conditional transitions (e.g., quiz_superato requires score >= 80%); static rules only |
| **D. Hybrid (app validates, DB checks basic constraints)** | Defense in depth | Dual maintenance of transition rules; risk of inconsistency |

### Rationale

The MAESTRO state machine has context-dependent transitions: `in_recupero -> da_consolidare` requires a quiz score >= 80%; `override_docente` requires a teacher role and motivation >= 20 characters; consent status affects what data can be stored. This context is not available in a single-row trigger without expensive cross-table lookups. The application layer has the full request context (authenticated user, quiz result, consent check) and can produce a rich audit entry with the decision rationale.

The database still provides structural safety via CHECK constraints on the `current_state` enum values and the `trigger_type` enum. Only the transition logic (which state can follow which) is application-enforced.

### Consequences

- (+) State machine logic is testable with pure Python unit tests
- (+) Full decision context logged in transition records
- (+) Transition rules can evolve without DDL migrations
- (-) Direct SQL access could bypass transition validation -- mitigated by database role restrictions (`maestro_app` role, no direct admin access in production)
- (-) Requires discipline: all state changes must go through the service layer

---

## Decision 2: Append-Only Audit with Trigger-Enforced Immutability

### Decision

The `audit.audit_log` and `kmm.state_transition_log` tables are append-only. UPDATE and DELETE are blocked by BEFORE triggers that raise exceptions. The single exception is the right-to-erasure procedure, which temporarily disables triggers.

### Alternatives Considered

| Option | Pros | Cons |
|---|---|---|
| **A. Trigger-enforced immutability** (chosen) | Simple, effective, auditable; clear exception path for erasure | Requires SUPERUSER or trigger manipulation for erasure |
| **B. Row-level security (RLS)** | PostgreSQL-native access control | More complex; still needs exception for erasure; does not prevent privileged users |
| **C. Separate audit database** | Physical isolation | Operational complexity; two databases to manage; cross-database transactions impossible |
| **D. Blockchain/hash-chain** | Tamper-evident | Massive over-engineering for MVP; PostgreSQL is trusted infrastructure |

### Rationale

Trigger-based immutability is the simplest mechanism that satisfies the tamper-evidence requirement (N7, F14.10). The trigger function is 3 lines of PL/pgSQL. The erasure exception is controlled via a SECURITY DEFINER function that only the `maestro_erasure` role can execute, and the erasure itself is logged.

### Consequences

- (+) Simple implementation, easy to verify
- (+) Works on all partition children automatically
- (-) Right-to-erasure requires temporarily disabling triggers -- mitigated by running inside a SECURITY DEFINER function with full logging
- (-) Does not prevent a DBA with SUPERUSER from modifying data -- acceptable; DBA access is logged at the infrastructure level (pgaudit)

---

## Decision 3: PII Encryption with pgcrypto

### Decision

Student and teacher PII (name, surname, email) is encrypted at rest using `pgcrypto` `pgp_sym_encrypt/pgp_sym_decrypt` with an application-managed symmetric key.

### Alternatives Considered

| Option | Pros | Cons |
|---|---|---|
| **A. pgcrypto symmetric encryption** (chosen) | PostgreSQL-native; no external dependency; key managed by application; queryable with decrypt in WHERE clause if needed | Key management is application responsibility; decryption in SQL exposes key to query logs |
| **B. Application-level encryption** (encrypt before INSERT) | Database never sees plaintext; key never touches PG | Cannot query by name in SQL; all lookups must use IDs; index on encrypted values useless |
| **C. PostgreSQL TDE (full-disk)** | Transparent; no code changes | Protects against disk theft only, not against SQL access; not standard in PG 17 community edition |
| **D. Vault/KMS integration** | Enterprise key management | Additional infrastructure; latency on every decrypt; overkill for MVP |

### Rationale

For MVP (1 school, 30 students), `pgcrypto` provides adequate encryption at rest without introducing external key management infrastructure. The encryption key is stored in an environment variable (`app.encryption_key`) set via PostgreSQL `ALTER SYSTEM SET` or injected at connection time, never in the database itself.

Student lookups primarily use `student.id` (UUID), not name. The encrypted name/surname fields are only decrypted for display purposes, which happens at the application layer. This limits the exposure of plaintext PII.

### Consequences

- (+) Zero additional infrastructure for encryption
- (+) Native PostgreSQL integration
- (-) Key rotation requires re-encrypting all PII rows -- acceptable at MVP scale
- (-) V1/V2: evaluate migration to application-level encryption or Vault if scale warrants

---

## Decision 4: Partitioning Strategy

### Decision

`state_transition_log` and `audit_log` are partitioned by month (RANGE on `created_at`). `student_node_state` is not partitioned for MVP.

### Alternatives Considered

| Option | Pros | Cons |
|---|---|---|
| **A. Monthly RANGE on created_at** (chosen) | Natural for time-series data; partition pruning on date range queries; easy to drop old partitions for retention enforcement | Requires partition management (pg_partman) |
| **B. Hash partitioning by student_id** | Even distribution | No time-based pruning; cannot drop old data by partition |
| **C. No partitioning** | Simplest | BRIN indexes less effective on very large unpartitioned tables; no partition-level operations |
| **D. List partitioning by course_id** | Course isolation | Uneven partition sizes; does not help with time-range queries |

### Rationale

The transition log and audit log are append-only, time-ordered data -- the canonical use case for monthly range partitioning. BRIN indexes on `created_at` combined with monthly partitions enable efficient time-range scans. pg_partman automates partition creation and retention-based deletion.

`student_node_state` is a "current state" table, not a time-series. At MVP scale (15K rows), partitioning adds complexity without benefit. V1 trigger: if row count exceeds 500K (3+ schools), consider HASH partitioning by `course_id` for course-scoped query isolation.

### Consequences

- (+) Efficient time-range queries on transition history and audit
- (+) Partition-level operations for data retention enforcement
- (+) pg_partman automates maintenance
- (-) Partition management is an operational concern (mitigated by pg_cron + pg_partman)

---

## Decision 5: Right-to-Erasure as Atomic Stored Procedure

### Decision

Right to erasure (Art. 17 GDPR) is implemented as a single PostgreSQL stored procedure (`core.execute_right_to_erasure`) that runs in a single transaction, deleting identifiable data and pseudonymizing audit trails.

### Alternatives Considered

| Option | Pros | Cons |
|---|---|---|
| **A. Stored procedure (single transaction)** (chosen) | Atomic; either all data is deleted or none; audit trail of the erasure preserved | Complex procedure; requires elevated privileges; long-running transaction for large datasets |
| **B. Application-level multi-step deletion** | Simpler per-step logic | Not atomic; partial deletion on failure; complex retry/rollback logic |
| **C. Soft delete (mark as deleted)** | Simple | Violates GDPR -- data is still present; explicitly prohibited by CLAUDE.md |
| **D. Async deletion pipeline** | Non-blocking | Not atomic; audit trail harder to maintain; compliance gap during processing |

### Rationale

GDPR Art. 17 for minors requires complete, verifiable deletion. An atomic transaction ensures that either all identifiable data is removed (and a deletion certificate generated) or the operation fails entirely and can be retried. The stored procedure approach also simplifies the compliance narrative: "one function call, one transaction, one certificate."

The procedure handles:
1. PII deletion (name, email, birth year, school registry ref, native language, adaptation profile)
2. KMM state deletion
3. Retention schedule deletion
4. Generated content deletion (DB records; S3 cleanup is async post-transaction)
5. Audit trail pseudonymization (student UUID -> SHA-256 hash)
6. Deletion certificate generation
7. Consent record deletion
8. Enrolment deletion

External resource cleanup (S3 files, Keycloak user) happens in the application layer after the transaction commits, with retry logic for failures.

### Consequences

- (+) Atomic, verifiable, certificate-generating
- (+) Single point of implementation for all deletion logic
- (+) Audit trail preserved in pseudonymized form
- (-) Long transaction for students with extensive history -- mitigated by MVP scale
- (-) S3 and Keycloak cleanup is eventual (not transactional) -- acceptable; retried until success

---

## Decision 6: FSRS Data Collection from Day 1

### Decision

The schema includes FSRS-related columns (`fsrs_stability`, `fsrs_difficulty` on `student_node_state`; `response_time_ms`, `concept_difficulty_estimate` on `retention_schedule` and `state_transition_log`) from MVP, even though the FSRS algorithm is not active until V2.

### Alternatives Considered

| Option | Pros | Cons |
|---|---|---|
| **A. Schema present from day 1, columns nullable** (chosen) | No migration needed when FSRS activates; data collected passively from MVP onward | Slightly wider tables; nullable columns add minor storage overhead |
| **B. Add columns in V2 migration** | Cleaner MVP schema | Loses MVP and V1 data for FSRS parameter estimation; migration on production tables with data |
| **C. Separate FSRS table** | Clean separation of concerns | Extra join; data duplication; more complex FSRS integration |

### Rationale

Per ADR-002 (section 3, recommended algorithm by phase), V2 FSRS requires accumulated review data from V1 (and ideally MVP). Adding nullable columns from day 1 costs almost nothing (NULLs in PostgreSQL are stored as a single bit in the null bitmap) but preserves the option to bootstrap FSRS with real student data when the time comes.

The `response_time_ms` field on quiz-related records captures how long students take to answer, which is a key input to FSRS's difficulty estimation. Collecting this from MVP onward provides a richer training dataset.

### Consequences

- (+) No migration needed when FSRS activates
- (+) MVP and V1 data available for FSRS parameter estimation
- (+) Response time data enables better per-student scheduling
- (-) Slightly wider rows (negligible storage impact)
- (-) Application code must populate these fields even if FSRS is not active

---

## Summary

| # | Decision | Key driver |
|---|---|---|
| 1 | Application-level state machine | Context-dependent transitions, testability |
| 2 | Trigger-enforced append-only audit | Tamper evidence, simplicity |
| 3 | pgcrypto for PII encryption | Zero additional infrastructure |
| 4 | Monthly RANGE partitioning on time-series tables | Time-range query efficiency |
| 5 | Atomic stored procedure for right-to-erasure | GDPR Art. 17 compliance, atomicity |
| 6 | FSRS data collection from day 1 | Future algorithm bootstrapping |
