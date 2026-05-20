"""Unit tests for audit trail utility (common/audit.py)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, call

import pytest

from maestro.common.audit import _to_jsonb, log_audit_event


class TestToJsonb:
    def test_none_returns_none(self) -> None:
        assert _to_jsonb(None) is None

    def test_dict_returns_json_string(self) -> None:
        result = _to_jsonb({"key": "value"})
        assert json.loads(result) == {"key": "value"}

    def test_serializes_non_json_types(self) -> None:
        """datetime and other types should be serialized via str."""
        from datetime import datetime

        result = _to_jsonb({"ts": datetime(2026, 1, 1)})
        parsed = json.loads(result)
        assert "2026" in parsed["ts"]


class TestLogAuditEvent:
    @pytest.mark.asyncio
    async def test_inserts_audit_record(self) -> None:
        session = AsyncMock()
        session.execute = AsyncMock()

        await log_audit_event(
            session,
            actor_id="user-1",
            actor_type="admin",
            action="student.create",
            entity_type="student",
            entity_id="stu-1",
            new_value={"school_year": 3},
        )

        session.execute.assert_called_once()
        call_args = session.execute.call_args
        params = call_args[0][1]
        assert params["actor_id"] == "user-1"
        assert params["action"] == "student.create"
        assert params["entity_id"] == "stu-1"

    @pytest.mark.asyncio
    async def test_none_values_for_optional_fields(self) -> None:
        session = AsyncMock()
        session.execute = AsyncMock()

        await log_audit_event(
            session,
            actor_id="u1",
            actor_type="system",
            action="test",
            entity_type="test",
            entity_id="t1",
        )

        params = session.execute.call_args[0][1]
        assert params["previous_value"] is None
        assert params["ip_address_hash"] is None
