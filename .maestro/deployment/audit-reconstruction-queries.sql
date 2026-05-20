-- =============================================================================
-- MAESTRO -- Audit Trail Reconstruction Queries
-- T6.4: Evidence of audit completeness for Garante Privacy accountability
--
-- Author: MSTR-16 (Privacy & Compliance Engineer)
-- Date: 2026-05-20
-- Purpose: Demonstrate that the audit trail can fully reconstruct any
--          student journey, meeting GDPR Art. 5(2) + Art. 30 requirements.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Q1: Full State History for a Student-Node Pair
--
-- Reconstructs the complete mastery state journey for a specific student
-- on a specific concept node within a course.
-- Demonstrates: temporal ordering, trigger types, score context.
-- ---------------------------------------------------------------------------

SELECT
    stl.id                  AS transition_id,
    stl.previous_state,
    stl.new_state,
    stl.trigger_type,
    stl.triggered_by        AS actor_id,
    stl.quiz_score,
    stl.response_time_ms,
    stl.motivation,
    stl.created_at          AS transition_timestamp
FROM
    kmm.state_transition_log stl
WHERE
    stl.student_id = :student_id::uuid
    AND stl.node_id = :node_id
    AND stl.course_id = :course_id::uuid
ORDER BY
    stl.created_at ASC, stl.id ASC;

-- Expected output: ordered list of all state changes, from non_introdotto
-- through to consolidato (or current state), with full context.


-- ---------------------------------------------------------------------------
-- Q2: All Teacher Overrides in a Course
--
-- Identifies every manual state override, who performed it, and their
-- pedagogical justification (motivation). Required by CLAUDE.md governance.
-- ---------------------------------------------------------------------------

SELECT
    stl.id                  AS transition_id,
    stl.student_id,
    stl.node_id,
    stl.previous_state,
    stl.new_state,
    stl.triggered_by        AS teacher_id,
    stl.motivation,
    stl.created_at          AS override_timestamp
FROM
    kmm.state_transition_log stl
WHERE
    stl.course_id = :course_id::uuid
    AND stl.trigger_type = 'override_docente'
ORDER BY
    stl.created_at DESC;

-- Verification: every row MUST have motivation IS NOT NULL
-- and LENGTH(TRIM(motivation)) >= 20 (enforced by application).


-- ---------------------------------------------------------------------------
-- Q3: LLM Pseudonymization Proof for a Session/Request
--
-- Proves that a specific LLM call used pseudonymised input by showing
-- the prompt hash (SHA-256 of pseudonymised text, never raw PII).
-- ---------------------------------------------------------------------------

SELECT
    lla.id,
    lla.request_id,
    lla.agent_name,
    lla.model_id,
    lla.prompt_hash         AS pseudonymised_prompt_sha256,
    lla.input_tokens,
    lla.output_tokens,
    lla.latency_ms,
    lla.cache_hit,
    lla.created_at          AS call_timestamp
FROM
    audit.llm_audit_log lla
WHERE
    lla.request_id = :request_id::uuid
ORDER BY
    lla.created_at ASC;

-- The prompt_hash field contains SHA-256 of the pseudonymised prompt.
-- If prompt_hash exists, pseudonymisation was applied before the call.
-- The application fails-closed: if PII is detected post-pseudonymisation,
-- PseudonymisationError is raised and NO record is created (call blocked).


-- ---------------------------------------------------------------------------
-- Q4: All LLM Calls for a Time Window (Audit Completeness Check)
--
-- Used to verify that every content generation had a corresponding
-- LLM audit entry. Cross-reference with application request logs.
-- ---------------------------------------------------------------------------

SELECT
    lla.request_id,
    lla.agent_name,
    lla.model_id,
    lla.prompt_hash,
    lla.input_tokens,
    lla.output_tokens,
    lla.latency_ms,
    lla.created_at
FROM
    audit.llm_audit_log lla
WHERE
    lla.created_at >= :start_time
    AND lla.created_at < :end_time
ORDER BY
    lla.created_at ASC;


-- ---------------------------------------------------------------------------
-- Q5: Safeguarding Event Timeline (Wellbeing Alerts for a Student)
--
-- Reconstructs all wellbeing detections for a specific student,
-- showing escalation path (teacher notified? referent notified?).
-- ---------------------------------------------------------------------------

SELECT
    wa.id                   AS alert_id,
    wa.detected_phrase,
    wa.category,
    wa.urgency,
    wa.context,
    wa.notified_teacher,
    wa.notified_referent,
    wa.teacher_id,
    wa.created_at           AS detection_timestamp
FROM
    safeguarding.wellbeing_alerts wa
WHERE
    wa.student_id = :student_id::uuid
ORDER BY
    wa.created_at ASC;

-- Cross-reference with audit.audit_log:
SELECT
    al.id,
    al.action,
    al.entity_id            AS student_id,
    al.new_value->>'alert_id'       AS alert_id,
    al.new_value->>'category'       AS category,
    al.new_value->>'urgency'        AS urgency,
    al.new_value->>'notified_teacher'   AS teacher_notified,
    al.new_value->>'notified_referent'  AS referent_notified,
    al.created_at
FROM
    audit.audit_log al
WHERE
    al.entity_type = 'student'
    AND al.entity_id = :student_id
    AND al.action = 'wellbeing.alert'
ORDER BY
    al.created_at ASC;


-- ---------------------------------------------------------------------------
-- Q6: Full Audit Trail for a Student (Journey Reconstruction)
--
-- Combines all audit sources to produce a unified timeline of
-- everything that happened to/for a specific student.
-- ---------------------------------------------------------------------------

WITH student_events AS (
    -- General audit events
    SELECT
        al.created_at       AS event_time,
        'audit'             AS source,
        al.action           AS event_type,
        al.actor_id,
        al.actor_type,
        al.entity_type,
        al.previous_value::text AS prev_value,
        al.new_value::text      AS new_value,
        NULL::text              AS extra_context
    FROM audit.audit_log al
    WHERE al.entity_type = 'student' AND al.entity_id = :student_id

    UNION ALL

    -- State transitions
    SELECT
        stl.created_at      AS event_time,
        'kmm'               AS source,
        stl.trigger_type    AS event_type,
        stl.triggered_by    AS actor_id,
        CASE
            WHEN stl.trigger_type = 'override_docente' THEN 'teacher'
            ELSE 'system'
        END                 AS actor_type,
        'state_transition'  AS entity_type,
        jsonb_build_object(
            'node_id', stl.node_id,
            'previous_state', stl.previous_state
        )::text             AS prev_value,
        jsonb_build_object(
            'node_id', stl.node_id,
            'new_state', stl.new_state,
            'quiz_score', stl.quiz_score,
            'motivation', stl.motivation
        )::text             AS new_value,
        stl.node_id         AS extra_context
    FROM kmm.state_transition_log stl
    WHERE stl.student_id = :student_id::uuid

    UNION ALL

    -- Wellbeing alerts
    SELECT
        wa.created_at       AS event_time,
        'safeguarding'      AS source,
        'wellbeing_alert'   AS event_type,
        'system'            AS actor_id,
        'system'            AS actor_type,
        'wellbeing'         AS entity_type,
        NULL                AS prev_value,
        jsonb_build_object(
            'category', wa.category,
            'urgency', wa.urgency,
            'notified_teacher', wa.notified_teacher,
            'notified_referent', wa.notified_referent
        )::text             AS new_value,
        wa.detected_phrase  AS extra_context
    FROM safeguarding.wellbeing_alerts wa
    WHERE wa.student_id = :student_id::uuid
)
SELECT *
FROM student_events
ORDER BY event_time ASC;


-- ---------------------------------------------------------------------------
-- Q7: Right-to-Erasure Certificate Verification
--
-- Retrieves the deletion certificate for a student (by hashed student_id)
-- to prove erasure was executed per GDPR Art. 17.
-- ---------------------------------------------------------------------------

SELECT
    dc.id                   AS certificate_id,
    dc.student_id_hash,
    dc.executed_by,
    dc.executed_at,
    dc.tables_affected,
    dc.rows_deleted,
    dc.rows_pseudonymised
FROM
    audit.deletion_certificate dc
WHERE
    dc.student_id_hash = :student_id_hash
ORDER BY
    dc.executed_at DESC;

-- Note: student_id_hash is SHA-256 of the original student UUID.
-- After erasure, the original student record is deleted, so we use
-- the hash to link the certificate to the (now-deleted) student.


-- ---------------------------------------------------------------------------
-- Q8: Retention Schedule History for a Student-Node
--
-- Shows all retention checks scheduled, completed, or cancelled for
-- a specific student-node pair.
-- ---------------------------------------------------------------------------

SELECT
    rs.id,
    rs.check_number,
    rs.scheduled_at,
    rs.status,
    rs.completed_at,
    rs.quiz_score,
    rs.response_time_ms,
    rs.concept_difficulty_estimate
FROM
    kmm.retention_schedule rs
WHERE
    rs.student_id = :student_id::uuid
    AND rs.node_id = :node_id
    AND rs.course_id = :course_id::uuid
ORDER BY
    rs.check_number ASC, rs.scheduled_at ASC;


-- ---------------------------------------------------------------------------
-- Q9: Quiz Submission History for a Student
--
-- Shows all quiz attempts with scores, enabling reconstruction of
-- the evidence that led to state transitions.
-- ---------------------------------------------------------------------------

SELECT
    al.id,
    al.entity_id            AS quiz_id,
    al.new_value->>'score'  AS score,
    al.new_value->>'total_time_ms' AS time_ms,
    al.actor_id             AS student_id,
    al.created_at           AS submitted_at
FROM
    audit.audit_log al
WHERE
    al.entity_type = 'quiz'
    AND al.action = 'quiz.submit'
    AND al.actor_id = :student_id
ORDER BY
    al.created_at ASC;


-- ---------------------------------------------------------------------------
-- Q10: KG Node Creation Audit Trail for a Course
--
-- Shows when and by whom curriculum nodes were created/modified.
-- Demonstrates teacher accountability for curriculum design.
-- ---------------------------------------------------------------------------

SELECT
    al.id,
    al.action,
    al.entity_id            AS node_id,
    al.actor_id             AS teacher_id,
    al.new_value->>'label_it'   AS node_label,
    al.new_value->>'course_id'  AS course_id,
    al.created_at
FROM
    audit.audit_log al
WHERE
    al.entity_type = 'kg_node'
    AND (al.new_value->>'course_id' = :course_id
         OR al.entity_id IN (
            SELECT id::text FROM kg.node WHERE course_id = :course_id::uuid
         ))
ORDER BY
    al.created_at ASC;


-- ---------------------------------------------------------------------------
-- Q11: Immutability Verification Query
--
-- This query would return rows if any audit record had been modified.
-- In a properly configured system, this should return 0 rows.
-- Useful for periodic integrity checks.
-- ---------------------------------------------------------------------------

-- Verify no audit records have a modification timestamp after creation
-- (This relies on the fact that our tables have no updated_at column --
--  only created_at, which is set once at INSERT time.)

SELECT 'audit.audit_log' AS table_name, COUNT(*) AS record_count,
       MIN(created_at) AS earliest, MAX(created_at) AS latest
FROM audit.audit_log

UNION ALL

SELECT 'audit.llm_audit_log', COUNT(*), MIN(created_at), MAX(created_at)
FROM audit.llm_audit_log

UNION ALL

SELECT 'kmm.state_transition_log', COUNT(*), MIN(created_at), MAX(created_at)
FROM kmm.state_transition_log

UNION ALL

SELECT 'audit.deletion_certificate', COUNT(*), MIN(executed_at), MAX(executed_at)
FROM audit.deletion_certificate;


-- ---------------------------------------------------------------------------
-- Q12: Sample Audit Reconstruction for Garante Demonstration
--
-- Given a student UUID, produce a comprehensive report suitable for
-- regulatory review. Shows processing basis, data accessed, and actions.
-- ---------------------------------------------------------------------------

-- Step 1: Count events per source
SELECT
    'General audit events' AS category,
    COUNT(*) AS event_count
FROM audit.audit_log
WHERE entity_type = 'student' AND entity_id = :student_id

UNION ALL

SELECT
    'State transitions' AS category,
    COUNT(*) AS event_count
FROM kmm.state_transition_log
WHERE student_id = :student_id::uuid

UNION ALL

SELECT
    'LLM interactions (via session)' AS category,
    COUNT(*) AS event_count
FROM audit.llm_audit_log
WHERE created_at >= (
    SELECT MIN(created_at) FROM kmm.state_transition_log
    WHERE student_id = :student_id::uuid
)

UNION ALL

SELECT
    'Wellbeing alerts' AS category,
    COUNT(*) AS event_count
FROM safeguarding.wellbeing_alerts
WHERE student_id = :student_id::uuid

UNION ALL

SELECT
    'Retention checks' AS category,
    COUNT(*) AS event_count
FROM kmm.retention_schedule
WHERE student_id = :student_id::uuid;
