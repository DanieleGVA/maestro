"""ORM models for the 'kmm' schema.

Tables:
  - student_node_state: current mastery state per (student, node, course)
  - state_transition_log: append-only transition history
  - retention_schedule: scheduled retention checks
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from maestro.db.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MasteryState(str, enum.Enum):
    """Canonical six-state mastery model (ADR-002, CLAUDE.md)."""

    non_introdotto = "non_introdotto"
    introdotto = "introdotto"
    lacuna = "lacuna"
    in_recupero = "in_recupero"
    da_consolidare = "da_consolidare"
    consolidato = "consolidato"


class TriggerType(str, enum.Enum):
    """Trigger types for state transitions (HLD-004 Section 3.2)."""

    verifica_errore = "verifica_errore"
    avvio_recupero = "avvio_recupero"
    quiz_superato = "quiz_superato"
    quiz_fallito = "quiz_fallito"
    retention_check_ok = "retention_check_ok"
    retention_check_fail = "retention_check_fail"
    regressione = "regressione"
    override_docente = "override_docente"
    lezione_completata = "lezione_completata"
    inizializzazione = "inizializzazione"


class RetentionStatus(str, enum.Enum):
    """Status for retention schedule entries (HLD-004 Section 3.4)."""

    pending = "pending"
    notified = "notified"
    completed_pass = "completed_pass"
    completed_fail = "completed_fail"
    cancelled = "cancelled"


class StudentNodeState(Base):
    """Current mastery state per (student, node, course) triple.

    Schema: kmm.student_node_state
    Primary key: composite (student_id, node_id, course_id).
    """

    __tablename__ = "student_node_state"
    __table_args__ = (
        CheckConstraint(
            "current_state IN ("
            "'non_introdotto', 'introdotto', 'lacuna', "
            "'in_recupero', 'da_consolidare', 'consolidato')",
            name="ck_sns_current_state",
        ),
        Index("idx_sns_student_course", "student_id", "course_id"),
        Index("idx_sns_course_state", "course_id", "current_state"),
        Index(
            "idx_sns_next_retention",
            "next_retention_check",
            postgresql_where="next_retention_check IS NOT NULL",
        ),
        {"schema": "kmm"},
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.student.id", ondelete="CASCADE"),
        primary_key=True,
    )
    node_id: Mapped[str] = mapped_column(Text, primary_key=True)
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.course.id", ondelete="RESTRICT"),
        primary_key=True,
    )

    current_state: Mapped[str] = mapped_column(
        String(20),
        default=MasteryState.non_introdotto.value,
        nullable=False,
    )
    previous_state: Mapped[str | None] = mapped_column(String(20))
    state_since: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    attempt_count: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    last_quiz_score: Mapped[int | None] = mapped_column(SmallInteger)
    last_quiz_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Retention scheduling
    next_retention_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retention_checks_passed: Mapped[int] = mapped_column(
        SmallInteger, default=0, nullable=False
    )

    # FSRS parameters (V1+, nullable for MVP per ADR-004 Decision 6)
    fsrs_stability: Mapped[float | None] = mapped_column()
    fsrs_difficulty: Mapped[float | None] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )


class StateTransitionLog(Base):
    """Immutable log of every state transition (kmm.state_transition_log).

    Append-only: PostgreSQL triggers deny UPDATE and DELETE.
    """

    __tablename__ = "state_transition_log"
    __table_args__ = (
        CheckConstraint(
            "trigger_type IN ("
            "'verifica_errore', 'avvio_recupero', 'quiz_superato', "
            "'quiz_fallito', 'retention_check_ok', 'retention_check_fail', "
            "'regressione', 'override_docente', 'lezione_completata', "
            "'inizializzazione')",
            name="ck_stl_trigger_type",
        ),
        Index("idx_stl_student_node", "student_id", "node_id", "course_id"),
        Index("idx_stl_course", "course_id"),
        {"schema": "kmm"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    node_id: Mapped[str] = mapped_column(Text, nullable=False)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    previous_state: Mapped[str] = mapped_column(String(20), nullable=False)
    new_state: Mapped[str] = mapped_column(String(20), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(30), nullable=False)
    triggered_by: Mapped[str | None] = mapped_column(Text)
    trigger_ref: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    quiz_score: Mapped[int | None] = mapped_column(SmallInteger)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    motivation: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )


class RetentionSchedule(Base):
    """Scheduled retention checks (kmm.retention_schedule).

    MVP: single D+7 check. V1: D+3, D+7, D+21.
    """

    __tablename__ = "retention_schedule"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'notified', 'completed_pass', "
            "'completed_fail', 'cancelled')",
            name="ck_rs_status",
        ),
        Index(
            "idx_rs_pending",
            "scheduled_at",
            postgresql_where="status = 'pending'",
        ),
        Index("idx_rs_student", "student_id", "node_id", "course_id"),
        {"schema": "kmm"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.student.id", ondelete="CASCADE"),
        nullable=False,
    )
    node_id: Mapped[str] = mapped_column(Text, nullable=False)
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.course.id", ondelete="RESTRICT"),
        nullable=False,
    )
    check_number: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default=RetentionStatus.pending.value, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    quiz_score: Mapped[int | None] = mapped_column(SmallInteger)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    concept_difficulty_estimate: Mapped[float | None] = mapped_column()
