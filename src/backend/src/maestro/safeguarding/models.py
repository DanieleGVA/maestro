"""ORM models for the safeguarding schema."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from maestro.db.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WellbeingAlert(Base):
    """Wellbeing alert record (safeguarding.wellbeing_alerts).

    Created when student input matches wellbeing keywords.
    The system does NOT provide psychological support -- it facilitates
    contact with the school referent (teacher or psychologist).
    """

    __tablename__ = "wellbeing_alerts"
    __table_args__ = (
        CheckConstraint(
            "category IN ('frustration', 'hopelessness', 'isolation', 'self_harm_risk')",
            name="ck_wellbeing_category",
        ),
        CheckConstraint(
            "urgency IN ('low', 'medium', 'high', 'critical')",
            name="ck_wellbeing_urgency",
        ),
        {"schema": "safeguarding"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    detected_phrase: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    urgency: Mapped[str] = mapped_column(String(10), nullable=False)
    context: Mapped[str | None] = mapped_column(Text)
    notified_teacher: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notified_referent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    acknowledged_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )


class SafeguardingVerdict(Base):
    """Safeguarding verdict record (safeguarding.safeguarding_verdicts).

    Logs every safeguarding check result for audit and post-mortem analysis.
    """

    __tablename__ = "safeguarding_verdicts"
    __table_args__ = (
        CheckConstraint(
            "verdict IN ('safe', 'blocked', 'warn', 'alert')",
            name="ck_verdict_type",
        ),
        {"schema": "safeguarding"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    verdict: Mapped[str] = mapped_column(String(10), nullable=False)
    violations: Mapped[dict | None] = mapped_column(JSONB)
    check_method: Mapped[str] = mapped_column(String(20), nullable=False)
    model_id: Mapped[str | None] = mapped_column(Text)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    fallback_served: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
