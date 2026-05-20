"""Unit tests for the LLM Gateway (llm/gateway.py).

Tests pseudonymisation pipeline, retry/fallback logic, and model routing.
All external LLM calls are mocked.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maestro.common.exceptions import LLMUnavailableError
from maestro.llm.clients import RawLLMResponse
from maestro.llm.gateway import LLMGateway, _ANTHROPIC_PREFIXES, _OPENAI_PREFIXES
from maestro.llm.models import LLMRequest
from maestro.llm.pseudonymizer import PseudonymisationError


def _make_request(**overrides: object) -> LLMRequest:
    defaults = {
        "agent_name": "test_agent",
        "prompt_template_id": "test_v1",
        "system_prompt": "System prompt",
        "context_block": "Context block",
        "task_block": "Task block",
        "correlation_id": "corr-1",
    }
    defaults.update(overrides)
    return LLMRequest(**defaults)


class TestModelRouting:
    def test_anthropic_prefix_detection(self) -> None:
        gw = LLMGateway.__new__(LLMGateway)
        gw._anthropic = MagicMock()
        gw._openai = MagicMock()
        client = gw._get_client_for_model("claude-sonnet-4-20250514")
        assert client is gw._anthropic

    def test_openai_prefix_detection(self) -> None:
        gw = LLMGateway.__new__(LLMGateway)
        gw._anthropic = MagicMock()
        gw._openai = MagicMock()
        client = gw._get_client_for_model("gpt-4o-mini")
        assert client is gw._openai

    def test_o1_routes_to_openai(self) -> None:
        gw = LLMGateway.__new__(LLMGateway)
        gw._anthropic = MagicMock()
        gw._openai = MagicMock()
        client = gw._get_client_for_model("o1-mini")
        assert client is gw._openai

    def test_unknown_model_defaults_to_anthropic(self) -> None:
        gw = LLMGateway.__new__(LLMGateway)
        gw._anthropic = MagicMock()
        gw._openai = MagicMock()
        client = gw._get_client_for_model("some-unknown-model")
        assert client is gw._anthropic


class TestRetryAndFallback:
    @pytest.mark.asyncio
    async def test_first_attempt_succeeds(self) -> None:
        """Normal case: first call succeeds."""
        gw = LLMGateway.__new__(LLMGateway)
        mock_client = AsyncMock()
        expected = RawLLMResponse(
            content="OK", model_id="test", input_tokens=10, output_tokens=20, latency_ms=100
        )
        mock_client.generate = AsyncMock(return_value=expected)
        gw._anthropic = mock_client
        gw._openai = mock_client

        result = await gw._call_with_retry_and_fallback(
            system_prompt="sys",
            user_message="msg",
            model_preference="quality",
            max_tokens=100,
            temperature=0.7,
        )
        assert result.content == "OK"

    @pytest.mark.asyncio
    async def test_all_retries_exhausted_raises(self) -> None:
        """When all models and retries fail, LLMUnavailableError is raised."""
        gw = LLMGateway.__new__(LLMGateway)
        mock_client = AsyncMock()
        mock_client.generate = AsyncMock(side_effect=RuntimeError("API error"))
        gw._anthropic = mock_client
        gw._openai = mock_client

        with (
            patch(
                "maestro.llm.gateway._MODEL_ROUTES",
                {
                    "quality": {"primary": "claude-test", "fallback": "gpt-test"},
                    "cost_optimized": {"primary": "gpt-test", "fallback": "claude-test"},
                },
            ),
            patch("maestro.llm.gateway.settings") as mock_settings,
            patch("asyncio.sleep", new_callable=AsyncMock),
            pytest.raises(LLMUnavailableError),
        ):
            mock_settings.llm_max_retries = 1
            await gw._call_with_retry_and_fallback(
                system_prompt="sys",
                user_message="msg",
                model_preference="quality",
                max_tokens=100,
                temperature=0.7,
            )


class TestPseudonymisationPipeline:
    @pytest.mark.asyncio
    async def test_pii_residual_blocks_call(self) -> None:
        """If PII residual detected, should raise PseudonymisationError."""
        gw = LLMGateway.__new__(LLMGateway)
        gw._pseudonymizer = MagicMock()
        gw._pseudonymizer.build_map.return_value = MagicMock()
        gw._pseudonymizer.build_map.return_value.pseudonymise = lambda t: t  # no-op
        gw._pseudonymizer.collect_known_pii.return_value = ["Mario"]
        gw._pseudonymizer.verify_no_pii_residual.return_value = False

        request = _make_request(
            system_prompt="Mario e' uno studente",
            context_block="",
            task_block="",
        )
        session = AsyncMock()

        with pytest.raises(PseudonymisationError):
            await gw.generate(
                request,
                session,
                student_context={"name": "Mario"},
            )

    @pytest.mark.asyncio
    async def test_no_student_context_skips_pseudonymisation(self) -> None:
        """Without student_context, pseudonymisation should be minimal."""
        gw = LLMGateway.__new__(LLMGateway)
        gw._pseudonymizer = MagicMock()
        from maestro.llm.pseudonymizer import PseudonymMap

        empty_map = PseudonymMap()
        gw._pseudonymizer.build_map.return_value = empty_map
        gw._pseudonymizer.verify_no_pii_residual.return_value = True

        raw = RawLLMResponse(
            content="Response", model_id="test", input_tokens=10, output_tokens=20, latency_ms=100
        )
        gw._call_with_retry_and_fallback = AsyncMock(return_value=raw)
        gw._log_audit = AsyncMock()

        request = _make_request()
        session = AsyncMock()

        result = await gw.generate(request, session)
        assert result.content == "Response"


class TestAuditLog:
    @pytest.mark.asyncio
    async def test_audit_log_failure_does_not_crash(self) -> None:
        """Audit log failure should be caught and not propagate."""
        gw = LLMGateway.__new__(LLMGateway)
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=RuntimeError("DB error"))

        # Should not raise
        await gw._log_audit(
            session=session,
            request_id="r1",
            agent_name="test",
            model_id="m1",
            prompt_hash="h1",
            input_tokens=10,
            output_tokens=20,
            latency_ms=100,
            cache_hit=False,
        )
