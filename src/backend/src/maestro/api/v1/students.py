"""Student API endpoints.

Per IC-12 contract (Section 14.4):
- GET /api/v1/students/{id} — student info
- GET /api/v1/students/{id}/state — student KMM state overview

RBAC: students access own data only. Teachers access class students. Admins access school.
"""

import re
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.auth.dependencies import get_current_user, get_db
from maestro.auth.keycloak import UserClaims
from maestro.auth.rbac import check_own_data_or_role

router = APIRouter(prefix="/students", tags=["students"])


# --- Schemas ---


class StudentResponse(BaseModel):
    """Public student info (no PII unless the caller is authorized)."""

    id: str
    school_id: str
    school_year: int
    status: str
    adaptation_profile: dict | None = None
    activated_at: str | None = None


class StudentCreateRequest(BaseModel):
    """Request schema for admin-only student creation (F14.2)."""

    school_id: str
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    school_year: int = Field(ge=1, le=5)
    birth_year: int | None = Field(default=None, ge=2006, le=2013)

    @field_validator("name", "surname")
    @classmethod
    def no_control_chars(cls, v: str) -> str:
        """Reject control characters in name fields."""
        if re.search(r"[\x00-\x1f\x7f]", v):
            raise ValueError("Caratteri di controllo non consentiti")
        return v.strip()

    @field_validator("email")
    @classmethod
    def valid_email(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Formato email non valido")
        return v.lower().strip()


class StudentCreatedResponse(BaseModel):
    """Response after student creation."""

    id: str
    status: str
    message: str


# --- Endpoints ---


@router.get("/{student_id}")
async def get_student(
    student_id: str,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get student information.

    Students can access only their own data. Teachers can access students
    in their class. Admins can access any student in their school.
    """
    check_own_data_or_role(user, student_id)

    from maestro.db.models.core import Student

    result = await db.execute(
        select(Student).where(Student.id == uuid.UUID(student_id))
    )
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Studente con id '{student_id}' non trovato",
        )

    return {
        "data": StudentResponse(
            id=str(student.id),
            school_id=str(student.school_id),
            school_year=student.school_year,
            status=student.status,
            adaptation_profile=student.adaptation_profile,
            activated_at=student.activated_at.isoformat() if student.activated_at else None,
        ).model_dump(),
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.get("/{student_id}/state")
async def get_student_state(
    student_id: str,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get student KMM state overview (mastery map).

    Returns the student's current mastery states across all enrolled courses.
    """
    check_own_data_or_role(user, student_id)

    # KMM state will be implemented by T4.4. Return placeholder for now.
    return {
        "data": {
            "student_id": student_id,
            "courses": [],
            "message": "KMM state endpoint — full implementation in T4.4",
        },
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_student(
    body: StudentCreateRequest,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create a new student account (F14.2). Admin only."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli admin possono creare studenti",
        )

    from sqlalchemy import text

    # Encrypt PII fields via pgcrypto before insertion
    new_id = uuid.uuid4()
    await db.execute(
        text("""
            INSERT INTO core.student
                (id, school_id, name_encrypted, surname_encrypted, email_encrypted,
                 school_year, birth_year, status, created_at)
            VALUES
                (:id, :school_id,
                 core.encrypt_pii(:name), core.encrypt_pii(:surname),
                 CASE WHEN :email IS NOT NULL THEN core.encrypt_pii(:email) ELSE NULL END,
                 :school_year, :birth_year, 'pending', :created_at)
        """),
        {
            "id": new_id,
            "school_id": uuid.UUID(body.school_id),
            "name": body.name,
            "surname": body.surname,
            "email": body.email,
            "school_year": body.school_year,
            "birth_year": body.birth_year,
            "created_at": datetime.now(timezone.utc),
        },
    )
    await db.commit()

    # Audit log
    from maestro.common.audit import log_audit_event

    await log_audit_event(
        db,
        actor_id=user.sub,
        actor_type="admin",
        action="student.create",
        entity_type="student",
        entity_id=str(new_id),
        new_value={"school_id": body.school_id, "school_year": body.school_year},
    )
    await db.commit()

    return {
        "data": StudentCreatedResponse(
            id=str(new_id),
            status="pending",
            message="Studente creato. Necessaria attivazione con credenziali Keycloak.",
        ).model_dump(),
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
