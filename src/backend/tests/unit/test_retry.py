"""Unit tests for safeguarding retry logic (safeguarding/retry.py)."""

import pytest

from maestro.safeguarding.checker import Violation, ViolationCategory, ViolationSeverity
from maestro.safeguarding.retry import (
    FALLBACK_MESSAGE_IT,
    MAX_SAFEGUARDING_ATTEMPTS,
    RETRY_PROMPT_MODIFICATIONS,
    RetryContext,
    build_retry_prompt,
)


class TestRetryConstants:
    def test_max_attempts_is_3(self) -> None:
        assert MAX_SAFEGUARDING_ATTEMPTS == 3

    def test_fallback_message_in_italian(self) -> None:
        assert "docente" in FALLBACK_MESSAGE_IT
        assert "materiale" in FALLBACK_MESSAGE_IT.lower()

    def test_retry_modifications_exist(self) -> None:
        assert 1 in RETRY_PROMPT_MODIFICATIONS
        assert 2 in RETRY_PROMPT_MODIFICATIONS

    def test_attempt_2_lowers_temperature(self) -> None:
        mod = RETRY_PROMPT_MODIFICATIONS[1]
        assert mod["temperature_override"] == 0.3

    def test_attempt_3_ultra_conservative(self) -> None:
        mod = RETRY_PROMPT_MODIFICATIONS[2]
        assert mod["temperature_override"] == 0.1
        assert "ULTRA-SICURA" in str(mod["prefix"])


class TestRetryContext:
    def test_can_retry_at_attempt_1(self) -> None:
        ctx = RetryContext(attempt_number=1)
        assert ctx.can_retry is True

    def test_can_retry_at_attempt_2(self) -> None:
        ctx = RetryContext(attempt_number=2)
        assert ctx.can_retry is True

    def test_cannot_retry_at_attempt_3(self) -> None:
        ctx = RetryContext(attempt_number=3)
        assert ctx.can_retry is False

    def test_temperature_override_attempt_1(self) -> None:
        ctx = RetryContext(attempt_number=1)
        assert ctx.temperature_override is None  # First attempt, no override

    def test_temperature_override_attempt_2(self) -> None:
        ctx = RetryContext(attempt_number=2)
        assert ctx.temperature_override == 0.3

    def test_temperature_override_attempt_3(self) -> None:
        ctx = RetryContext(attempt_number=3)
        assert ctx.temperature_override == 0.1


class TestBuildRetryPrompt:
    def _make_violation(self, desc: str = "test violation") -> Violation:
        return Violation(
            category=ViolationCategory.PUNITIVE_TONE,
            severity=ViolationSeverity.BLOCK,
            pattern="test",
            matched_text="test text",
            description=desc,
        )

    def test_attempt_1_returns_original(self) -> None:
        """First attempt has no modification (index 0 not in RETRY_PROMPT_MODIFICATIONS)."""
        ctx = RetryContext(attempt_number=1)
        original = "Generate content."
        result = build_retry_prompt(original, ctx)
        assert result == original

    def test_attempt_2_adds_violation_context(self) -> None:
        ctx = RetryContext(
            attempt_number=2,
            previous_violations=[self._make_violation("punitive tone detected")],
        )
        original = "Generate content."
        result = build_retry_prompt(original, ctx)
        assert "ATTENZIONE" in result
        assert "punitive tone detected" in result
        assert result.endswith(original)

    def test_attempt_3_ultra_safe_prefix(self) -> None:
        ctx = RetryContext(
            attempt_number=3,
            previous_violations=[
                self._make_violation("comparison"),
                self._make_violation("fomo"),
            ],
        )
        original = "Generate content."
        result = build_retry_prompt(original, ctx)
        assert "ULTRA-SICURA" in result
        assert "FATTUALE" in result

    def test_multiple_violations_joined(self) -> None:
        ctx = RetryContext(
            attempt_number=2,
            previous_violations=[
                self._make_violation("issue A"),
                self._make_violation("issue B"),
            ],
        )
        result = build_retry_prompt("prompt", ctx)
        assert "issue A" in result
        assert "issue B" in result
