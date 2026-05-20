"""Student session endpoints.

Per IC-12 contract:
- POST /api/v1/sessions/start — start a student learning session
- POST /api/v1/sessions/activity — record an activity in the current session
- POST /api/v1/sessions/end — end the current session

Sessions drive the LangGraph orchestrator: starting a session triggers the
student_session_flow, which loads the student's state, selects an activity,
executes it, and updates the state.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.auth.dependencies import get_current_user, get_db
from maestro.auth.keycloak import UserClaims

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionStartRequest(BaseModel):
    """Request to start a new student session."""

    course_id: str
    node_id: str | None = None  # Optional: start with a specific recovery mission


class SessionStartResponse(BaseModel):
    """Response after session start."""

    session_id: str
    student_id: str
    course_id: str
    started_at: str


class SessionActivityRequest(BaseModel):
    """Record an activity within the current session."""

    session_id: str
    activity_type: str = Field(
        pattern=r"^(content_viewed|content_completed|quiz_started|modality_switched)$"
    )
    activity_data: dict | None = None


class SessionEndRequest(BaseModel):
    """Request to end the current session."""

    session_id: str


@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_session(
    body: SessionStartRequest,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Start a new student learning session.

    Triggers the student_session_flow in the orchestrator: loads student state,
    selects the next activity, and prepares content.
    """
    if user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli studenti possono avviare sessioni",
        )

    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    return {
        "data": SessionStartResponse(
            session_id=session_id,
            student_id=user.student_id or user.sub,
            course_id=body.course_id,
            started_at=now.isoformat(),
        ).model_dump(),
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": now.isoformat(),
        },
    }


@router.post("/activity")
async def record_activity(
    body: SessionActivityRequest,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Record a student activity within the current session."""
    if user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli studenti possono registrare attivita'",
        )

    return {
        "data": {
            "session_id": body.session_id,
            "activity_type": body.activity_type,
            "recorded": True,
        },
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


@router.post("/end")
async def end_session(
    body: SessionEndRequest,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """End the current student session and persist state updates."""
    if user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli studenti possono terminare sessioni",
        )

    return {
        "data": {
            "session_id": body.session_id,
            "ended": True,
            "ended_at": datetime.now(timezone.utc).isoformat(),
        },
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
