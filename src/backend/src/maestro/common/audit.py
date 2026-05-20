"""Audit trail utility for write-once audit logging."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def log_audit_event(
    session: AsyncSession,
    *,
    actor_id: str,
    actor_type: str,
    action: str,
    entity_type: str,
    entity_id: str,
    previous_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
    ip_address_hash: str | None = None,
    user_agent_hash: str | None = None,
) -> None:
    """Insert an immutable audit log record.

    Uses raw SQL INSERT to write into the partitioned audit.audit_log table.
    The table has UPDATE/DELETE triggers that deny modification, so records
    are write-once by design.
    """
    await session.execute(
        text("""
            INSERT INTO audit.audit_log
                (actor_id, actor_type, action, entity_type, entity_id,
                 previous_value, new_value, ip_address_hash, user_agent_hash, created_at)
            VALUES
                (:actor_id, :actor_type, :action, :entity_type, :entity_id,
                 :previous_value, :new_value, :ip_address_hash, :user_agent_hash, :created_at)
        """),
        {
            "actor_id": actor_id,
            "actor_type": actor_type,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "previous_value": _to_jsonb(previous_value),
            "new_value": _to_jsonb(new_value),
            "ip_address_hash": ip_address_hash,
            "user_agent_hash": user_agent_hash,
            "created_at": datetime.now(timezone.utc),
        },
    )


def _to_jsonb(value: dict[str, Any] | None) -> str | None:
    """Serialize a dict to JSON string for JSONB insertion, or None."""
    if value is None:
        return None
    import json

    return json.dumps(value, default=str)
