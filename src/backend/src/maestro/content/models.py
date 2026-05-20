"""ORM models for the content schema: GeneratedContent, Quiz, QuizQuestion, QuizResponse."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maestro.db.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GeneratedContent(Base):
    """Generated content metadata + inline payload (content.generated_content)."""

    __tablename__ = "generated_content"
    __table_args__ = (
        CheckConstraint(
            "content_type IN ('recovery_document', 'remediation_path', 'quiz', "
            "'podcast_script', 'visual_diagram', 'quest_description')",
            name="ck_content_type",
        ),
        CheckConstraint(
            "status IN ('active', 'archived', 'blocked')",
            name="ck_content_status",
        ),
        {"schema": "content"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    student_pseudo_id: Mapped[str] = mapped_column(String(100), nullable=False)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    node_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_template_id: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_template_version: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_hash: Mapped[str] = mapped_column(Text, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    sources_used: Mapped[dict | None] = mapped_column(JSONB)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    teacher_reviewed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    modified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )


class Quiz(Base):
    """Quiz entity (content.quiz)."""

    __tablename__ = "quiz"
    __table_args__ = (
        CheckConstraint(
            "purpose IN ('closure', 'retention')",
            name="ck_quiz_purpose",
        ),
        CheckConstraint(
            "status IN ('active', 'completed', 'expired')",
            name="ck_quiz_status",
        ),
        {"schema": "content"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    student_pseudo_id: Mapped[str] = mapped_column(String(100), nullable=False)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    node_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    purpose: Mapped[str] = mapped_column(String(20), nullable=False)
    difficulty_level: Mapped[str] = mapped_column(String(50), nullable=False)
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_hash: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    questions: Mapped[list["QuizQuestion"]] = relationship(back_populates="quiz")
    responses: Mapped[list["QuizResponse"]] = relationship(back_populates="quiz")


class QuizQuestion(Base):
    """Individual quiz question (content.quiz_question)."""

    __tablename__ = "quiz_question"
    __table_args__ = (
        CheckConstraint(
            "question_type IN ('multiple_choice', 'true_false', 'fill_blank')",
            name="ck_question_type",
        ),
        {"schema": "content"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content.quiz.id"),
        nullable=False,
    )
    question_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict | None] = mapped_column(JSONB)  # For multiple choice
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    bloom_level: Mapped[str | None] = mapped_column(String(20))
    source_refs: Mapped[dict | None] = mapped_column(JSONB)
    from_teacher_bank: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")


class QuizResponse(Base):
    """Student quiz submission (content.quiz_response)."""

    __tablename__ = "quiz_response"
    __table_args__ = {"schema": "content"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content.quiz.id"),
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    answers: Mapped[dict] = mapped_column(JSONB, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    quiz: Mapped["Quiz"] = relationship(back_populates="responses")
