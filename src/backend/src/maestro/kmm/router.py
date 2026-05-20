"""FastAPI router for KMM endpoints.

Endpoints (mounted at /api/v1 by main.py):
  GET  /kmm/students/{id}/map           -- student knowledge map
  GET  /kmm/students/{id}/nodes/{nid}   -- single node state
  POST /kmm/students/{id}/nodes/{nid}/transition -- teacher override
  GET  /kmm/classes/{class_id}/heatmap  -- class heatmap
  GET  /kmm/students/{id}/retention/due -- due retention checks
"""

from __future__ import annotations

import uuid as _uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.auth.dependencies import get_current_user, get_db
from maestro.auth.keycloak import UserClaims
from maestro.auth.rbac import check_own_data_or_role
from maestro.common.exceptions import (
    NotFoundError,
    OverrideMotivationError,
    TransitionIllegalError,
)
from maestro.db.models.core import Enrolment
from maestro.kmm import schemas
from maestro.kmm.heatmap import get_class_heatmap
from maestro.kmm.retention import get_student_due_checks
from maestro.kmm.service import get_student_map, get_student_state, teacher_override
from maestro.kmm.state_machine import IllegalTransitionError, StateNotFoundError

router = APIRouter(prefix="/kmm", tags=["kmm"])


@router.get(
    "/students/{student_id}/map",
    response_model=schemas.StudentMapResponse,
)
async def read_student_map(
    student_id: str,
    course_id: str = Query(..., description="Course UUID"),
    user: UserClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> schemas.StudentMapResponse:
    """Return the full knowledge map for a student in a course."""
    check_own_data_or_role(user, student_id)
    nodes = await get_student_map(session, student_id, course_id)
    return schemas.StudentMapResponse(
        student_id=student_id,
        course_id=course_id,
        nodes=[
            schemas.NodeStateResponse(
                student_id=str(n.student_id),
                node_id=n.node_id,
                course_id=str(n.course_id),
                current_state=n.current_state,
                previous_state=n.previous_state,
                state_since=n.state_since,
                attempt_count=n.attempt_count,
                last_quiz_score=n.last_quiz_score,
                last_quiz_at=n.last_quiz_at,
                next_retention_check=n.next_retention_check,
                retention_checks_passed=n.retention_checks_passed,
            )
            for n in nodes
        ],
    )


@router.get(
    "/students/{student_id}/nodes/{node_id}",
    response_model=schemas.NodeStateResponse,
)
async def read_node_state(
    student_id: str,
    node_id: str,
    course_id: str = Query(..., description="Course UUID"),
    user: UserClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> schemas.NodeStateResponse:
    """Return state for a single (student, node, course)."""
    check_own_data_or_role(user, student_id)
    sns = await get_student_state(session, student_id, node_id, course_id)
    if sns is None:
        raise NotFoundError("node_state", f"{student_id}/{node_id}")
    return schemas.NodeStateResponse(
        student_id=str(sns.student_id),
        node_id=sns.node_id,
        course_id=str(sns.course_id),
        current_state=sns.current_state,
        previous_state=sns.previous_state,
        state_since=sns.state_since,
        attempt_count=sns.attempt_count,
        last_quiz_score=sns.last_quiz_score,
        last_quiz_at=sns.last_quiz_at,
        next_retention_check=sns.next_retention_check,
        retention_checks_passed=sns.retention_checks_passed,
    )


@router.post(
    "/students/{student_id}/nodes/{node_id}/transition",
    response_model=schemas.TransitionLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_teacher_override(
    student_id: str,
    node_id: str,
    body: schemas.TransitionRequest,
    course_id: str = Query(..., description="Course UUID"),
    user: UserClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> schemas.TransitionLogResponse:
    """Teacher override: manually set a node's mastery state (F11.12).

    Requires motivation >= 20 characters. Fully audited.
    """
    if user.role not in ("teacher", "admin"):
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(status_code=403, detail="Solo i docenti possono eseguire override")
    teacher_id = user.sub

    try:
        log = await teacher_override(
            session=session,
            teacher_id=teacher_id,
            student_id=student_id,
            node_id=node_id,
            course_id=course_id,
            target_state=body.target_state,
            motivation=body.motivation,
        )
        await session.commit()
    except IllegalTransitionError as exc:
        if "motivation" in exc.reason.lower():
            raise OverrideMotivationError() from exc
        raise TransitionIllegalError(
            node_id=node_id,
            current_state=exc.current_state,
            target_state=exc.target_state,
        ) from exc
    except StateNotFoundError:
        raise NotFoundError("node_state", f"{student_id}/{node_id}")

    return schemas.TransitionLogResponse(
        id=log.id,
        student_id=str(log.student_id),
        node_id=log.node_id,
        course_id=str(log.course_id),
        previous_state=log.previous_state,
        new_state=log.new_state,
        trigger_type=log.trigger_type,
        triggered_by=log.triggered_by,
        quiz_score=log.quiz_score,
        motivation=log.motivation,
        created_at=log.created_at,
    )


@router.get(
    "/classes/{class_id}/heatmap",
    response_model=schemas.ClassHeatmapResponse,
)
async def read_class_heatmap(
    class_id: str,
    course_id: str = Query(..., description="Course UUID"),
    user: UserClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> schemas.ClassHeatmapResponse:
    """Class-level heatmap: per-node student counts by state."""
    if user.role not in ("teacher", "admin"):
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(status_code=403, detail="Solo docenti e admin possono accedere alla heatmap")
    stmt = select(Enrolment.student_id).where(
        Enrolment.course_id == _uuid.UUID(course_id),
        Enrolment.status == "active",
    )
    result = await session.execute(stmt)
    student_ids = [str(sid) for sid in result.scalars().all()]

    heatmap = await get_class_heatmap(session, student_ids, course_id)
    return schemas.ClassHeatmapResponse(
        course_id=course_id,
        node_summaries=[
            schemas.ClassNodeSummaryResponse(
                node_id=ns.node_id,
                counts_per_state=ns.counts_per_state,
                total_students=ns.total_students,
            )
            for ns in heatmap.node_summaries
        ],
    )


@router.get(
    "/students/{student_id}/retention/due",
    response_model=list[schemas.RetentionCheckResponse],
)
async def read_due_retention_checks(
    student_id: str,
    course_id: str | None = Query(None, description="Optional course filter"),
    user: UserClaims = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[schemas.RetentionCheckResponse]:
    """Return retention checks that are due for a student."""
    check_own_data_or_role(user, student_id)
    checks = await get_student_due_checks(session, student_id, course_id)
    return [
        schemas.RetentionCheckResponse(
            id=c.id,
            student_id=str(c.student_id),
            node_id=c.node_id,
            course_id=str(c.course_id),
            check_number=c.check_number,
            scheduled_at=c.scheduled_at,
            status=c.status,
        )
        for c in checks
    ]
