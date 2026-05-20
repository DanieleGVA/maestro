"""Unit tests for wellbeing alert management (safeguarding/alerts.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from maestro.safeguarding.alerts import create_wellbeing_alert
from maestro.safeguarding.checker import WellbeingKeyword


class TestCreateWellbeingAlert:
    @pytest.mark.asyncio
    async def test_empty_keywords_returns_empty(self) -> None:
        """No keywords should return empty string and not insert."""
        session = AsyncMock()
        result = await create_wellbeing_alert(
            session,
            student_id="stu-1",
            teacher_id="tea-1",
            trigger_text="test",
            matched_keywords=[],
        )
        assert result == ""
        session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_critical_keyword_notifies_referent(self) -> None:
        """Critical urgency should set notified_referent=True."""
        session = AsyncMock()
        session.execute = AsyncMock()

        kw = WellbeingKeyword(
            phrase="mi faccio del male",
            category="self_harm_risk",
            urgency="critical",
            action="alert_referent",
        )
        result = await create_wellbeing_alert(
            session,
            student_id="stu-1",
            teacher_id="tea-1",
            trigger_text="mi faccio del male",
            matched_keywords=[kw],
        )

        assert result  # non-empty UUID string
        # Should have executed 3 times: alert insert, notification insert, audit log
        assert session.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_medium_keyword_notifies_teacher(self) -> None:
        """Medium urgency should notify teacher but not referent."""
        session = AsyncMock()
        session.execute = AsyncMock()

        kw = WellbeingKeyword(
            phrase="non ce la faccio",
            category="frustration",
            urgency="medium",
            action="alert_teacher",
        )
        result = await create_wellbeing_alert(
            session,
            student_id="stu-1",
            teacher_id="tea-1",
            trigger_text="non ce la faccio",
            matched_keywords=[kw],
        )

        assert result  # non-empty UUID string
        # Alert + notification + audit = 3 calls
        assert session.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_low_urgency_no_notification(self) -> None:
        """Low urgency should not create teacher notification."""
        session = AsyncMock()
        session.execute = AsyncMock()

        kw = WellbeingKeyword(
            phrase="non ci riesco",
            category="frustration",
            urgency="low",
            action="log",
        )
        result = await create_wellbeing_alert(
            session,
            student_id="stu-1",
            teacher_id="tea-1",
            trigger_text="non ci riesco",
            matched_keywords=[kw],
        )

        assert result  # non-empty
        # Alert insert + audit log only, no notification
        assert session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_no_teacher_id_skips_notification(self) -> None:
        """Without teacher_id, notification should be skipped."""
        session = AsyncMock()
        session.execute = AsyncMock()

        kw = WellbeingKeyword(
            phrase="mi sento solo",
            category="isolation",
            urgency="high",
            action="alert_referent",
        )
        result = await create_wellbeing_alert(
            session,
            student_id="stu-1",
            teacher_id=None,
            trigger_text="mi sento solo",
            matched_keywords=[kw],
        )

        assert result
        # Alert insert + audit log, no notification (no teacher_id)
        assert session.execute.call_count == 2
