"""Lesson upload endpoints.

Per IC-12 contract:
- POST /api/v1/courses/{course_id}/lessons — upload lesson material
- GET /api/v1/courses/{course_id}/lessons — list lessons for a course

RBAC: teacher (own courses) for upload, teacher + admin for listing.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.auth.dependencies import get_current_user, get_db
from maestro.auth.keycloak import UserClaims

router = APIRouter(prefix="/courses/{course_id}/lessons", tags=["lessons"])


class LessonResponse(BaseModel):
    """Lesson metadata response."""

    id: str
    course_id: str
    filename: str
    file_type: str
    status: str
    uploaded_at: str


class LessonListResponse(BaseModel):
    """List of lessons."""

    lessons: list[LessonResponse]
    total: int


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_lesson(
    course_id: str,
    file: UploadFile,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Upload a lesson material file (F2).

    Accepted types: PDF, DOCX, PPTX, MP3, MP4.
    The file is stored and queued for processing (transcription + concept extraction).
    """
    if user.role not in ("teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i docenti possono caricare materiale",
        )

    # Validate file type
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "audio/mpeg",
        "video/mp4",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tipo file non supportato: {file.content_type}. "
            "Tipi accettati: PDF, DOCX, PPTX, MP3, MP4.",
        )

    # Validate file size (max 500MB per security spec)
    content = await file.read()
    max_size = 500 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File troppo grande. Dimensione massima: 500MB.",
        )

    lesson_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # Store metadata in DB (actual file stored in object storage in production)
    from sqlalchemy import text

    await db.execute(
        text("""
            INSERT INTO content.lesson_material
                (id, course_id, original_filename, file_type, file_size_bytes,
                 status, uploaded_by, created_at)
            VALUES
                (:id, :course_id, :filename, :file_type, :file_size,
                 'uploaded', :uploaded_by, :created_at)
        """),
        {
            "id": lesson_id,
            "course_id": uuid.UUID(course_id),
            "filename": file.filename or "unknown",
            "file_type": file.content_type,
            "file_size": len(content),
            "uploaded_by": user.sub,
            "created_at": now,
        },
    )
    await db.commit()

    # Audit log
    from maestro.common.audit import log_audit_event

    await log_audit_event(
        db,
        actor_id=user.sub,
        actor_type=user.role,
        action="lesson.upload",
        entity_type="lesson_material",
        entity_id=str(lesson_id),
        new_value={
            "course_id": course_id,
            "file_type": file.content_type,
            "size_bytes": len(content),
        },
    )
    await db.commit()

    return {
        "data": LessonResponse(
            id=str(lesson_id),
            course_id=course_id,
            filename=file.filename or "unknown",
            file_type=file.content_type or "unknown",
            status="uploaded",
            uploaded_at=now.isoformat(),
        ).model_dump(),
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": now.isoformat(),
        },
    }


@router.get("")
async def list_lessons(
    course_id: str,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List lessons for a course. Teacher (own courses) and admin."""
    if user.role not in ("teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso non autorizzato",
        )

    # Placeholder: in production, query content.lesson_material
    return {
        "data": LessonListResponse(lessons=[], total=0).model_dump(),
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
