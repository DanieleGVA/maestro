"""KMM service layer -- high-level operations over the state machine.

All public functions receive an AsyncSession and operate within the caller's
transaction boundary. The caller decides commit/rollback.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.kmm.models import (
    MasteryState,
    StudentNodeState,
    TriggerType,
)
from maestro.kmm.state_machine import (
    IllegalTransitionError,
    StateTransitionLog,
    TransitionContext,
    execute_transition,
)


async def get_student_state(
    session: AsyncSession,
    student_id: str,
    node_id: str,
    course_id: str,
) -> StudentNodeState | None:
    """Return the current state record for a single (student, node, course)."""
    stmt = select(StudentNodeState).where(
        StudentNodeState.student_id == uuid.UUID(student_id),
        StudentNodeState.node_id == node_id,
        StudentNodeState.course_id == uuid.UUID(course_id),
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_student_map(
    session: AsyncSession,
    student_id: str,
    course_id: str,
) -> list[StudentNodeState]:
    """Return the full knowledge map for a student in a course."""
    stmt = (
        select(StudentNodeState)
        .where(
            StudentNodeState.student_id == uuid.UUID(student_id),
            StudentNodeState.course_id == uuid.UUID(course_id),
        )
        .order_by(StudentNodeState.node_id)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def initialize_student_map(
    session: AsyncSession,
    student_id: str,
    course_id: str,
    node_ids: list[str],
) -> int:
    """Create initial non_introdotto state for all given nodes.

    Returns the number of records created. Skips nodes that already have state.
    """
    student_uuid = uuid.UUID(student_id)
    course_uuid = uuid.UUID(course_id)

    # Find existing node_ids to avoid duplicates
    existing_stmt = select(StudentNodeState.node_id).where(
        StudentNodeState.student_id == student_uuid,
        StudentNodeState.course_id == course_uuid,
    )
    result = await session.execute(existing_stmt)
    existing_nodes = set(result.scalars().all())

    count = 0
    for nid in node_ids:
        if nid in existing_nodes:
            continue
        sns = StudentNodeState(
            student_id=student_uuid,
            node_id=nid,
            course_id=course_uuid,
            current_state=MasteryState.non_introdotto.value,
        )
        session.add(sns)
        count += 1

    if count > 0:
        await session.flush()

    return count


async def process_quiz_result(
    session: AsyncSession,
    student_id: str,
    node_id: str,
    course_id: str,
    score: int,
    response_time_ms: int | None = None,
) -> StateTransitionLog:
    """Process a quiz result and execute the appropriate transition.

    Logic (HLD-004 Section 3.3, interface-contracts IC-09):
      - score >= 80: quiz_superato -> da_consolidare (or consolidato if retention)
      - score 50-79: quiz_fallito -> stay in_recupero (retry)
      - score < 50:  quiz_fallito -> regress to lacuna (alert teacher)
    """
    sns = await get_student_state(session, student_id, node_id, course_id)
    if sns is None:
        from maestro.kmm.state_machine import StateNotFoundError

        raise StateNotFoundError(
            f"No state for student={student_id}, node={node_id}, course={course_id}"
        )

    current = sns.current_state

    if score >= 80:
        trigger = TriggerType.quiz_superato.value
        if current == MasteryState.in_recupero.value:
            target = MasteryState.da_consolidare.value
        elif current == MasteryState.da_consolidare.value:
            # Retention check passed
            target = MasteryState.consolidato.value
        else:
            target = MasteryState.da_consolidare.value
    else:
        trigger = TriggerType.quiz_fallito.value
        if score < 50:
            target = MasteryState.lacuna.value
        else:
            # 50-79: retry, stay in current state
            target = current

    ctx = TransitionContext(
        trigger_type=trigger,
        quiz_score=score,
        response_time_ms=response_time_ms,
    )

    return await execute_transition(
        session, student_id, node_id, course_id, target, ctx
    )


async def process_retention_check(
    session: AsyncSession,
    student_id: str,
    node_id: str,
    course_id: str,
    passed: bool,
    quiz_score: int | None = None,
    response_time_ms: int | None = None,
) -> StateTransitionLog:
    """Process a retention check result.

    MVP: single D+7 check. Pass -> consolidato. Fail -> lacuna.
    """
    if passed:
        trigger = TriggerType.retention_check_ok.value
        target = MasteryState.consolidato.value
    else:
        trigger = TriggerType.retention_check_fail.value
        target = MasteryState.lacuna.value

    ctx = TransitionContext(
        trigger_type=trigger,
        quiz_score=quiz_score,
        response_time_ms=response_time_ms,
    )

    return await execute_transition(
        session, student_id, node_id, course_id, target, ctx
    )


async def teacher_override(
    session: AsyncSession,
    teacher_id: str,
    student_id: str,
    node_id: str,
    course_id: str,
    target_state: str,
    motivation: str,
) -> StateTransitionLog:
    """Teacher manual override (F11.12).

    Motivation must be >= 20 characters (CLAUDE.md governance).
    The transition bypasses the legal transitions table but is fully audited.
    """
    if len(motivation.strip()) < 20:
        raise IllegalTransitionError(
            "any",
            target_state,
            "Override docente requires motivation >= 20 characters",
        )

    ctx = TransitionContext(
        trigger_type=TriggerType.override_docente.value,
        triggered_by=teacher_id,
        motivation=motivation,
    )

    return await execute_transition(
        session, student_id, node_id, course_id, target_state, ctx
    )
