"""Retention check scheduler.

MVP: fixed D+7 after reaching da_consolidare.
V1: D+3, D+7, D+21 (configurable).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.kmm.models import RetentionSchedule, RetentionStatus


async def get_due_retention_checks(
    session: AsyncSession,
    as_of: datetime | None = None,
) -> list[RetentionSchedule]:
    """Return retention checks that are past their scheduled time and still pending."""
    now = as_of or datetime.now(timezone.utc)
    stmt = (
        select(RetentionSchedule)
        .where(
            RetentionSchedule.status == RetentionStatus.pending.value,
            RetentionSchedule.scheduled_at <= now,
        )
        .order_by(RetentionSchedule.scheduled_at)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_student_due_checks(
    session: AsyncSession,
    student_id: str,
    course_id: str | None = None,
    as_of: datetime | None = None,
) -> list[RetentionSchedule]:
    """Return due retention checks for a specific student."""
    now = as_of or datetime.now(timezone.utc)
    conditions = [
        RetentionSchedule.student_id == uuid.UUID(student_id),
        RetentionSchedule.status == RetentionStatus.pending.value,
        RetentionSchedule.scheduled_at <= now,
    ]
    if course_id:
        conditions.append(RetentionSchedule.course_id == uuid.UUID(course_id))

    stmt = (
        select(RetentionSchedule)
        .where(*conditions)
        .order_by(RetentionSchedule.scheduled_at)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def schedule_retention(
    session: AsyncSession,
    student_id: str,
    node_id: str,
    course_id: str,
    delay_days: int = 7,
    check_number: int = 1,
) -> RetentionSchedule:
    """Create a retention check schedule entry.

    MVP default: D+7. V1 will call this multiple times with different delays.
    """
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=delay_days)

    schedule = RetentionSchedule(
        student_id=uuid.UUID(student_id),
        node_id=node_id,
        course_id=uuid.UUID(course_id),
        check_number=check_number,
        scheduled_at=scheduled_at,
        status=RetentionStatus.pending.value,
    )
    session.add(schedule)
    await session.flush()
    return schedule


async def mark_retention_completed(
    session: AsyncSession,
    schedule_id: int,
    passed: bool,
    quiz_score: int | None = None,
    response_time_ms: int | None = None,
) -> RetentionSchedule:
    """Mark a retention check as completed (pass or fail)."""
    stmt = select(RetentionSchedule).where(RetentionSchedule.id == schedule_id)
    result = await session.execute(stmt)
    schedule = result.scalar_one_or_none()

    if schedule is None:
        raise ValueError(f"Retention schedule {schedule_id} not found")

    now = datetime.now(timezone.utc)
    schedule.status = (
        RetentionStatus.completed_pass.value
        if passed
        else RetentionStatus.completed_fail.value
    )
    schedule.completed_at = now
    schedule.quiz_score = quiz_score
    schedule.response_time_ms = response_time_ms

    await session.flush()
    return schedule


async def cancel_pending_checks(
    session: AsyncSession,
    student_id: str,
    node_id: str,
    course_id: str,
) -> int:
    """Cancel all pending retention checks for a (student, node, course).

    Used when a student regresses to lacuna -- pending retention checks become moot.
    """
    stmt = (
        update(RetentionSchedule)
        .where(
            RetentionSchedule.student_id == uuid.UUID(student_id),
            RetentionSchedule.node_id == node_id,
            RetentionSchedule.course_id == uuid.UUID(course_id),
            RetentionSchedule.status == RetentionStatus.pending.value,
        )
        .values(status=RetentionStatus.cancelled.value)
    )
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount  # type: ignore[return-value]
