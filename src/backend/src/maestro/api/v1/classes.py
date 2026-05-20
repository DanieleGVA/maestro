"""Class and teacher dashboard endpoints.

Per IC-12 contract:
- GET /api/v1/courses/{course_id}/class-heatmap — class knowledge map heatmap
- GET /api/v1/courses/{course_id}/students — students in a course

RBAC: teacher (own courses) and admin (school-wide).
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.auth.dependencies import get_current_user, get_db
from maestro.auth.keycloak import UserClaims

router = APIRouter(prefix="/courses/{course_id}", tags=["classes"])


class ClassHeatmapResponse(BaseModel):
    """Class-level knowledge map heatmap (F11.14)."""

    course_id: str
    student_count: int
    nodes: list[dict]  # [{node_id, label, state_distribution: {state: count}}]


class CourseStudentSummary(BaseModel):
    """Summary of a student within a course."""

    student_id: str
    status: str
    total_nodes: int
    nodes_consolidato: int
    nodes_lacuna: int


class CourseStudentsResponse(BaseModel):
    """List of students in a course."""

    course_id: str
    students: list[CourseStudentSummary]
    total: int


@router.get("/class-heatmap")
async def get_class_heatmap(
    course_id: str,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get the class knowledge map heatmap (F11.14).

    Returns per-node state distribution across all students in the class.
    Used by the teacher dashboard to identify class-wide gaps.
    """
    if user.role not in ("teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docenti e admin possono accedere alla heatmap",
        )

    # Placeholder: full implementation queries kmm.student_node_state + kg.node
    return {
        "data": ClassHeatmapResponse(
            course_id=course_id,
            student_count=0,
            nodes=[],
        ).model_dump(),
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.get("/students")
async def get_course_students(
    course_id: str,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get list of students enrolled in a course with summary state info."""
    if user.role not in ("teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docenti e admin possono accedere alla lista studenti",
        )

    # Placeholder: full implementation joins core.enrolment + kmm.student_node_state
    return {
        "data": CourseStudentsResponse(
            course_id=course_id,
            students=[],
            total=0,
        ).model_dump(),
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
