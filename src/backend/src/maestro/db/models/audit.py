"""ORM models for the 'audit' schema: AuditLog, LLMAuditLog, DeletionCertificate.

All audit tables are append-only (write-once). PostgreSQL triggers deny UPDATE and DELETE.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from maestro.db.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base):
    """Universal audit log (audit.audit_log). Partitioned monthly by created_at.

    Immutability enforced by PostgreSQL triggers (trg_audit_no_update, trg_audit_no_delete).
    """

    __tablename__ = "audit_log"
    __table_args__ = {"schema": "audit"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    actor_id: Mapped[str] = mapped_column(Text, nullable=False)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(Text, nullable=False)
    previous_value: Mapped[dict | None] = mapped_column(JSONB)
    new_value: Mapped[dict | None] = mapped_column(JSONB)
    ip_address_hash: Mapped[str | None] = mapped_column(Text)
    user_agent_hash: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )


class LLMAuditLog(Base):
    """LLM call audit log (audit.llm_audit_log). Partitioned monthly.

    Every LLM call is logged with prompt hash (never prompt text), token counts,
    latency, and agent identification.
    """

    __tablename__ = "llm_audit_log"
    __table_args__ = {"schema": "audit"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(Text, nullable=False)
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_hash: Mapped[str] = mapped_column(Text, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )


class DeletionCertificate(Base):
    """Right-to-erasure certificates (audit.deletion_certificate). Immutable."""

    __tablename__ = "deletion_certificate"
    __table_args__ = {"schema": "audit"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id_hash: Mapped[str] = mapped_column(Text, nullable=False)
    executed_by: Mapped[str] = mapped_column(Text, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    tables_affected: Mapped[dict] = mapped_column(JSONB, nullable=False)
    rows_deleted: Mapped[int] = mapped_column(Integer, nullable=False)
    rows_pseudonymised: Mapped[int] = mapped_column(Integer, nullable=False)
