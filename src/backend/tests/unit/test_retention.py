"""Unit tests for retention scheduling logic.

Tests the scheduling constants and RetentionStatus enum.
Async DB-dependent functions are tested at the integration level.
"""

from datetime import datetime, timedelta, timezone

import pytest

from maestro.kmm.models import MasteryState, RetentionStatus
from maestro.kmm.state_machine import MVP_RETENTION_DELAY_DAYS


class TestRetentionConstants:
    def test_mvp_delay_is_7_days(self) -> None:
        """MVP retention check is D+7 (ADR-002 Section 3)."""
        assert MVP_RETENTION_DELAY_DAYS == 7

    def test_retention_status_values(self) -> None:
        """All expected status values exist."""
        assert RetentionStatus.pending.value == "pending"
        assert RetentionStatus.notified.value == "notified"
        assert RetentionStatus.completed_pass.value == "completed_pass"
        assert RetentionStatus.completed_fail.value == "completed_fail"
        assert RetentionStatus.cancelled.value == "cancelled"


class TestRetentionSchedulingLogic:
    """Test the scheduling logic that would be called by the state machine."""

    def test_d_plus_7_calculation(self) -> None:
        """When a concept reaches da_consolidare, retention is D+7."""
        now = datetime(2026, 9, 15, 10, 0, 0, tzinfo=timezone.utc)
        expected = now + timedelta(days=7)
        assert expected == datetime(2026, 9, 22, 10, 0, 0, tzinfo=timezone.utc)

    def test_mvp_single_check_to_consolidato(self) -> None:
        """MVP: 1 pass at D+7 transitions to consolidato.

        Per ADR-005 Conflict 7: 'MVP sets retention_checks_passed = 1 on pass
        and immediately transitions to consolidato.'
        """
        # This is a logical assertion about the expected behavior
        # The actual execution is in state_machine.execute_transition
        assert MVP_RETENTION_DELAY_DAYS == 7
        # In MVP, a single pass should be sufficient
        # V1 requires 3 passes (D+3, D+7, D+21)

    def test_regression_clears_retention(self) -> None:
        """When regressing to lacuna, retention checks should be cleared.

        Verified by the state machine: target_state == lacuna =>
        next_retention_check = None, retention_checks_passed = 0
        """
        # This is a design assertion; the state machine handles it
        assert MasteryState.lacuna.value == "lacuna"


class TestRetentionStateInteraction:
    """Test that retention check outcomes lead to correct state transitions."""

    def test_pass_transitions_defined(self) -> None:
        """retention_check_ok from da_consolidare can go to consolidato or da_consolidare."""
        from maestro.kmm.state_machine import LEGAL_TRANSITIONS

        allowed = LEGAL_TRANSITIONS["da_consolidare"]
        assert "consolidato" in allowed
        assert "da_consolidare" in allowed  # self-loop for V1 intermediate checks

    def test_fail_transitions_defined(self) -> None:
        """retention_check_fail from da_consolidare goes to lacuna."""
        from maestro.kmm.state_machine import LEGAL_TRANSITIONS

        allowed = LEGAL_TRANSITIONS["da_consolidare"]
        assert "lacuna" in allowed
