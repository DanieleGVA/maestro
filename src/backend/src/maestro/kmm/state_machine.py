"""Six-state mastery machine -- application-level enforcement (ADR-004 Decision 1).

Legal transitions are validated here. Override docente bypasses the table
but requires motivation >= 20 chars and full audit logging.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.kmm.models import (
    MasteryState,
    RetentionSchedule,
    RetentionStatus,
    StateTransitionLog,
    StudentNodeState,
    TriggerType,
)

# ---------------------------------------------------------------------------
# Canonical state ordering (ADR-005 Conflict 3)
# Lower value = worse state for rollup purposes
# ---------------------------------------------------------------------------
STATE_ORDER: dict[str, int] = {
    MasteryState.lacuna.value: 0,
    MasteryState.in_recupero.value: 1,
    MasteryState.non_introdotto.value: 2,
    MasteryState.introdotto.value: 3,
    MasteryState.da_consolidare.value: 4,
    MasteryState.consolidato.value: 5,
}

# ---------------------------------------------------------------------------
# Legal transitions (HLD-004 Section 3.3, interface-contracts IC-04)
# ---------------------------------------------------------------------------
LEGAL_TRANSITIONS: dict[str, set[str]] = {
    MasteryState.non_introdotto.value: {MasteryState.introdotto.value},
    MasteryState.introdotto.value: {MasteryState.lacuna.value},
    MasteryState.lacuna.value: {MasteryState.in_recupero.value},
    MasteryState.in_recupero.value: {
        MasteryState.da_consolidare.value,
        MasteryState.in_recupero.value,
        MasteryState.lacuna.value,
    },
    MasteryState.da_consolidare.value: {
        MasteryState.consolidato.value,
        MasteryState.da_consolidare.value,
        MasteryState.lacuna.value,
    },
    MasteryState.consolidato.value: {MasteryState.lacuna.value},
}

# MVP retention delay (ADR-002 Section 3)
MVP_RETENTION_DELAY_DAYS = 7


@dataclass
class TransitionContext:
    """Context for a state transition request."""

    trigger_type: str
    triggered_by: str | None = None
    quiz_score: int | None = None
    response_time_ms: int | None = None
    motivation: str | None = None  # Required for override_docente (>= 20 chars)


class IllegalTransitionError(Exception):
    """Raised when a state transition is not permitted."""

    def __init__(self, current_state: str, target_state: str, reason: str) -> None:
        self.current_state = current_state
        self.target_state = target_state
        self.reason = reason
        super().__init__(
            f"Illegal transition {current_state} -> {target_state}: {reason}"
        )


class StateNotFoundError(Exception):
    """Raised when a student-node state record does not exist."""


def validate_transition(
    current_state: str,
    target_state: str,
    trigger_type: str,
    context: TransitionContext,
) -> bool:
    """Validate whether a transition is legal.

    Returns True if legal, raises IllegalTransitionError otherwise.
    """
    # Override docente bypasses the transition table
    if trigger_type == TriggerType.override_docente.value:
        if not context.motivation or len(context.motivation.strip()) < 20:
            raise IllegalTransitionError(
                current_state,
                target_state,
                "Override docente requires motivation >= 20 characters",
            )
        return True

    # Check the legal transitions table
    allowed = LEGAL_TRANSITIONS.get(current_state, set())
    if target_state not in allowed:
        raise IllegalTransitionError(
            current_state,
            target_state,
            f"Transition not in legal table. Allowed from {current_state}: {allowed}",
        )

    # Context-specific validation
    if trigger_type == TriggerType.quiz_superato.value:
        if context.quiz_score is None or context.quiz_score < 80:
            raise IllegalTransitionError(
                current_state,
                target_state,
                f"quiz_superato requires score >= 80, got {context.quiz_score}",
            )

    if trigger_type == TriggerType.quiz_fallito.value:
        if context.quiz_score is not None and context.quiz_score >= 80:
            raise IllegalTransitionError(
                current_state,
                target_state,
                f"quiz_fallito requires score < 80, got {context.quiz_score}",
            )

    return True


async def execute_transition(
    session: AsyncSession,
    student_id: str,
    node_id: str,
    course_id: str,
    target_state: str,
    context: TransitionContext,
) -> StateTransitionLog:
    """Execute a validated state transition in a single transaction.

    1. Load current state
    2. Validate transition
    3. Update StudentNodeState
    4. Create StateTransitionLog record
    5. If transitioning to da_consolidare: schedule retention check (D+7)
    6. Return the log entry

    The caller is responsible for committing or rolling back the session.
    """
    import uuid as _uuid

    # 1. Load current state
    stmt = select(StudentNodeState).where(
        StudentNodeState.student_id == _uuid.UUID(student_id)
        if isinstance(student_id, str)
        else StudentNodeState.student_id == student_id,
        StudentNodeState.node_id == node_id,
        StudentNodeState.course_id == _uuid.UUID(course_id)
        if isinstance(course_id, str)
        else StudentNodeState.course_id == course_id,
    )
    result = await session.execute(stmt)
    sns = result.scalar_one_or_none()

    if sns is None:
        raise StateNotFoundError(
            f"No state record for student={student_id}, node={node_id}, course={course_id}"
        )

    current_state = sns.current_state

    # 2. Validate
    validate_transition(current_state, target_state, context.trigger_type, context)

    now = datetime.now(timezone.utc)

    # 3. Update StudentNodeState
    sns.previous_state = current_state
    sns.current_state = target_state
    sns.state_since = now
    sns.updated_at = now

    if context.quiz_score is not None:
        sns.last_quiz_score = context.quiz_score
        sns.last_quiz_at = now
        sns.attempt_count += 1

    # Reset retention on regression to lacuna
    if target_state == MasteryState.lacuna.value:
        sns.next_retention_check = None
        sns.retention_checks_passed = 0
        sns.attempt_count = 0

    # 4. Create transition log
    student_uuid = (
        _uuid.UUID(student_id) if isinstance(student_id, str) else student_id
    )
    course_uuid = (
        _uuid.UUID(course_id) if isinstance(course_id, str) else course_id
    )

    log_entry = StateTransitionLog(
        student_id=student_uuid,
        node_id=node_id,
        course_id=course_uuid,
        previous_state=current_state,
        new_state=target_state,
        trigger_type=context.trigger_type,
        triggered_by=context.triggered_by,
        quiz_score=context.quiz_score,
        response_time_ms=context.response_time_ms,
        motivation=context.motivation,
        created_at=now,
    )
    session.add(log_entry)

    # 5. If target is da_consolidare: schedule D+7 retention check
    if target_state == MasteryState.da_consolidare.value:
        # Only schedule if this is a fresh transition (not a self-loop from retention pass)
        if current_state != MasteryState.da_consolidare.value:
            retention_at = now + timedelta(days=MVP_RETENTION_DELAY_DAYS)
            sns.next_retention_check = retention_at
            sns.retention_checks_passed = 0

            schedule = RetentionSchedule(
                student_id=student_uuid,
                node_id=node_id,
                course_id=course_uuid,
                check_number=1,
                scheduled_at=retention_at,
                status=RetentionStatus.pending.value,
            )
            session.add(schedule)
        else:
            # Self-loop (retention pass but not yet consolidato): increment counter
            sns.retention_checks_passed += 1

    # If target is consolidato: clear retention scheduling
    if target_state == MasteryState.consolidato.value:
        sns.next_retention_check = None

    await session.flush()

    return log_entry
