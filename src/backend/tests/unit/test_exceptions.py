"""Unit tests for custom exceptions (common/exceptions.py)."""

import pytest

from maestro.common.exceptions import (
    ConsentRequiredError,
    ForbiddenError,
    LLMUnavailableError,
    MaestroError,
    NotFoundError,
    OverrideMotivationError,
    SafeguardingBlockedError,
    TransitionIllegalError,
)


class TestMaestroError:
    def test_base_error(self) -> None:
        err = MaestroError("test", code="TEST_CODE", detail={"key": "val"})
        assert err.message == "test"
        assert err.code == "TEST_CODE"
        assert err.detail == {"key": "val"}
        assert str(err) == "test"

    def test_default_code(self) -> None:
        err = MaestroError("msg")
        assert err.code == "INTERNAL_ERROR"
        assert err.detail is None


class TestNotFoundError:
    def test_message_includes_entity(self) -> None:
        err = NotFoundError("student", "abc-123")
        assert "student" in err.message
        assert "abc-123" in err.message
        assert err.code == "STUDENT_NOT_FOUND"
        assert err.detail["entity_type"] == "student"
        assert err.detail["entity_id"] == "abc-123"


class TestForbiddenError:
    def test_default_message(self) -> None:
        err = ForbiddenError()
        assert err.code == "FORBIDDEN"
        assert "non autorizzato" in err.message.lower()

    def test_custom_message(self) -> None:
        err = ForbiddenError("custom msg")
        assert err.message == "custom msg"


class TestConsentRequiredError:
    def test_lists_missing_consents(self) -> None:
        err = ConsentRequiredError(["a", "b"])
        assert err.code == "CONSENT_MISSING"
        assert "a" in err.message
        assert "b" in err.message
        assert err.detail["missing_consents"] == ["a", "b"]


class TestTransitionIllegalError:
    def test_includes_transition_details(self) -> None:
        err = TransitionIllegalError("node-1", "lacuna", "consolidato")
        assert "node-1" in err.message
        assert "lacuna" in err.message
        assert "consolidato" in err.message
        assert err.code == "TRANSITION_ILLEGAL"
        assert err.detail["node_id"] == "node-1"


class TestSafeguardingBlockedError:
    def test_includes_violations(self) -> None:
        err = SafeguardingBlockedError(["comparison", "punitive"])
        assert err.code == "SAFEGUARDING_BLOCKED"
        assert err.detail["violations"] == ["comparison", "punitive"]


class TestOverrideMotivationError:
    def test_message(self) -> None:
        err = OverrideMotivationError()
        assert err.code == "OVERRIDE_MOTIVATION_SHORT"
        assert "20" in err.message


class TestLLMUnavailableError:
    def test_message(self) -> None:
        err = LLMUnavailableError()
        assert err.code == "LLM_UNAVAILABLE"
