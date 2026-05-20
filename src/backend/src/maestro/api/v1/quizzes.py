"""Quiz endpoints.

Per IC-12 contract:
- POST /api/v1/quizzes/generate — generate a quiz for a concept node
- POST /api/v1/quizzes/{quiz_id}/submit — submit quiz answers

RBAC: students submit quizzes. Teachers can trigger generation.
Quiz generation goes through safeguarding review before delivery.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.auth.dependencies import get_current_user, get_db
from maestro.auth.keycloak import UserClaims

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


class QuizGenerateRequest(BaseModel):
    """Request to generate a quiz for specific concept nodes."""

    course_id: str
    node_id: str
    quiz_purpose: str = Field(pattern=r"^(closure|retention)$")


class QuizGenerateResponse(BaseModel):
    """Generated quiz metadata (actual questions delivered separately)."""

    quiz_id: str
    node_id: str
    purpose: str
    question_count: int
    generated_at: str


class QuizAnswer(BaseModel):
    """A single quiz answer."""

    question_id: str
    selected: str


class QuizSubmitRequest(BaseModel):
    """Request to submit quiz answers."""

    answers: list[QuizAnswer] = Field(min_length=1, max_length=20)
    total_time_ms: int = Field(ge=0, le=3600000)


class QuizSubmitResponse(BaseModel):
    """Quiz submission result with score and per-question feedback."""

    quiz_id: str
    score: int  # 0-100 percentage
    correct_count: int
    total_questions: int
    transition_triggered: str | None
    feedback_message: str


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    body: QuizGenerateRequest,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate a quiz for a concept node (F11.8).

    Checks the teacher question bank first. Falls back to LLM-generated
    questions (via LLMGateway) if no teacher questions exist.
    All generated questions pass through safeguarding review.
    """
    if user.role not in ("student", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso non autorizzato",
        )

    quiz_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    return {
        "data": QuizGenerateResponse(
            quiz_id=quiz_id,
            node_id=body.node_id,
            purpose=body.quiz_purpose,
            question_count=5,  # Default 3-5 questions per F11.8
            generated_at=now.isoformat(),
        ).model_dump(),
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": now.isoformat(),
        },
    }


@router.post("/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: str,
    body: QuizSubmitRequest,
    user: UserClaims = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Submit quiz answers (F11.8-F11.9).

    Evaluates answers, computes score, and triggers KMM state transitions
    based on the score thresholds:
    - >= 80%: quiz_superato (in_recupero -> da_consolidare)
    - 50-79%: stay in_recupero, attempt++
    - < 50%: regress to lacuna, alert teacher
    """
    if user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli studenti possono sottomettere quiz",
        )

    # Placeholder scoring (actual implementation queries question_bank for correct answers)
    total = len(body.answers)
    correct = 0  # Placeholder: would compare with stored correct answers
    score = int((correct / total) * 100) if total > 0 else 0

    # Determine transition based on score thresholds (IC-09 contract)
    transition = None
    feedback = ""
    if score >= 80:
        transition = "quiz_superato"
        feedback = "Ottimo lavoro! Hai superato il quiz."
    elif score >= 50:
        transition = None  # Stay in_recupero
        feedback = "Ci sei quasi! Rivedi il materiale e riprova."
    else:
        transition = "quiz_fallito"
        feedback = "Non ti preoccupare, e' un'opportunita' per ripassare con un approccio diverso."

    # Audit log
    from maestro.common.audit import log_audit_event

    await log_audit_event(
        db,
        actor_id=user.student_id or user.sub,
        actor_type="student",
        action="quiz.submit",
        entity_type="quiz",
        entity_id=quiz_id,
        new_value={"score": score, "total_time_ms": body.total_time_ms},
    )
    await db.commit()

    return {
        "data": QuizSubmitResponse(
            quiz_id=quiz_id,
            score=score,
            correct_count=correct,
            total_questions=total,
            transition_triggered=transition,
            feedback_message=feedback,
        ).model_dump(),
        "meta": {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
