"""Teacher-facing endpoints.

GET /api/v1/teachers/me/courses -- courses for the authenticated teacher
"""

import uuid as _uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.auth.dependencies import get_current_user, get_db
from maestro.auth.keycloak import UserClaims
from maestro.db.models.core import Course, Enrolment, Teacher

router = APIRouter(prefix="/teachers", tags=["teachers"])


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class TeacherCourseOut(BaseModel):
    """A course assigned to the teacher."""

    id: str
    name: str
    academic_year: str
    student_count: int


class TeacherCoursesResponse(BaseModel):
    """List of teacher courses."""

    courses: list[TeacherCourseOut]
    total: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/me/courses", response_model=TeacherCoursesResponse)
async def get_my_courses(
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TeacherCoursesResponse:
    """Return the courses for the currently authenticated teacher.

    The teacher is identified by matching the JWT ``sub`` claim against
    ``core.teacher.keycloak_user_id``.  If no teacher record is linked yet
    (typical for fresh Keycloak setups), it falls back to the first active
    teacher in the school -- acceptable for MVP demo only.
    """
    if user.role not in ("teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docenti e admin possono accedere a questo endpoint",
        )

    # Step 1: resolve JWT sub -> internal teacher_id
    teacher_row = await db.execute(
        select(Teacher.id).where(Teacher.keycloak_user_id == user.sub)
    )
    teacher_id = teacher_row.scalar_one_or_none()

    # Fallback for MVP: if keycloak_user_id is not linked, try to find
    # any active teacher in the school.  This covers the demo seed scenario
    # where Keycloak users are created separately from DB records.
    if teacher_id is None:
        fallback_row = await db.execute(
            select(Teacher.id)
            .where(Teacher.status == "active")
            .limit(1)
        )
        teacher_id = fallback_row.scalar_one_or_none()

    if teacher_id is None:
        return TeacherCoursesResponse(courses=[], total=0)

    # Step 2: fetch courses with enrolled-student counts
    stmt = (
        select(
            Course.id,
            Course.name,
            Course.academic_year,
            func.count(Enrolment.id).label("student_count"),
        )
        .outerjoin(Enrolment, (Enrolment.course_id == Course.id) & (Enrolment.status == "active"))
        .where(Course.teacher_id == teacher_id, Course.status != "archived")
        .group_by(Course.id, Course.name, Course.academic_year)
        .order_by(Course.academic_year.desc(), Course.name)
    )

    result = await db.execute(stmt)
    rows = result.all()

    courses = [
        TeacherCourseOut(
            id=str(row.id),
            name=row.name,
            academic_year=row.academic_year,
            student_count=row.student_count,
        )
        for row in rows
    ]

    return TeacherCoursesResponse(courses=courses, total=len(courses))
