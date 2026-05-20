"""Unit tests for the TextAgent content generation (content/text_agent.py).

Tests the generation with safeguarding retry loop and fallback logic.
All LLM calls are mocked.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maestro.content.text_agent import (
    LENGTH_DESCRIPTIONS,
    TONE_INSTRUCTIONS,
    TextAgent,
)
from maestro.llm.models import LLMResponse
from maestro.safeguarding.retry import FALLBACK_MESSAGE_IT, MAX_SAFEGUARDING_ATTEMPTS


class TestToneInstructions:
    def test_confidenziale_uses_tu(self) -> None:
        assert "'tu'" in TONE_INSTRUCTIONS["confidenziale"]

    def test_formale_uses_lei(self) -> None:
        assert "'Lei'" in TONE_INSTRUCTIONS["formale"]

    def test_neutro_exists(self) -> None:
        assert "neutro" in TONE_INSTRUCTIONS

    def test_all_tones_present(self) -> None:
        for tone in ("confidenziale", "neutro", "formale"):
            assert tone in TONE_INSTRUCTIONS


class TestLengthDescriptions:
    def test_sintesi_shorter(self) -> None:
        assert "150-250" in LENGTH_DESCRIPTIONS["sintesi"]

    def test_approfondimento_longer(self) -> None:
        assert "400-600" in LENGTH_DESCRIPTIONS["approfondimento"]


class TestTextAgentGeneration:
    @pytest.fixture
    def mock_gateway(self) -> AsyncMock:
        gateway = AsyncMock()
        return gateway

    @pytest.fixture
    def agent(self, mock_gateway: AsyncMock) -> TextAgent:
        return TextAgent(mock_gateway)

    @pytest.mark.asyncio
    async def test_generate_explanation_success(
        self, agent: TextAgent, mock_gateway: AsyncMock, mock_db_session: AsyncMock
    ) -> None:
        """Safe content should be returned as parsed JSON."""
        safe_content = json.dumps({
            "blocks": [
                {
                    "concept_node_id": "n1",
                    "concept_label": "Session Fixation",
                    "il_tuo_errore": {"text": "Errore spiegato"},
                    "perche_succede": {"text": "Causa"},
                    "come_si_fa_giusto": {"text": "Soluzione"},
                    "ricordati": {"text": "Ricorda!"},
                }
            ],
            "summary": "Buon lavoro!",
        })
        mock_gateway.generate = AsyncMock(
            return_value=LLMResponse(
                content=safe_content,
                model_id="test",
                input_tokens=100,
                output_tokens=200,
                latency_ms=500,
                prompt_hash="abc",
            )
        )

        from maestro.content.schemas import ContentAdaptationProfile, TargetNode

        result = await agent.generate_explanation(
            nodes=[
                TargetNode(
                    node_id="n1",
                    current_state="lacuna",
                    label_it="Session Fixation",
                )
            ],
            student_pseudo_id="STUDENTE_test",
            profile=ContentAdaptationProfile(tone="confidenziale", length="sintesi"),
            course_language="it",
            session=mock_db_session,
        )

        assert "blocks" in result
        assert result["summary"] == "Buon lavoro!"

    @pytest.mark.asyncio
    async def test_generate_explanation_fallback_on_all_blocked(
        self, agent: TextAgent, mock_gateway: AsyncMock, mock_db_session: AsyncMock
    ) -> None:
        """After MAX_SAFEGUARDING_ATTEMPTS blocked responses, serve fallback."""
        blocked_content = "Sei scarso in programmazione. Non sarai mai capace."
        mock_gateway.generate = AsyncMock(
            return_value=LLMResponse(
                content=blocked_content,
                model_id="test",
                input_tokens=100,
                output_tokens=200,
                latency_ms=500,
                prompt_hash="abc",
            )
        )

        from maestro.content.schemas import ContentAdaptationProfile, TargetNode

        result = await agent.generate_explanation(
            nodes=[
                TargetNode(
                    node_id="n1",
                    current_state="lacuna",
                    label_it="Test",
                )
            ],
            student_pseudo_id="STUDENTE_test",
            profile=ContentAdaptationProfile(),
            course_language="it",
            session=mock_db_session,
        )

        assert result["fallback"] is True
        assert result["message"] == FALLBACK_MESSAGE_IT
        assert mock_gateway.generate.call_count == MAX_SAFEGUARDING_ATTEMPTS

    @pytest.mark.asyncio
    async def test_generate_explanation_invalid_json_returns_raw(
        self, agent: TextAgent, mock_gateway: AsyncMock, mock_db_session: AsyncMock
    ) -> None:
        """If LLM returns invalid JSON, return raw_text wrapper."""
        mock_gateway.generate = AsyncMock(
            return_value=LLMResponse(
                content="This is not JSON but is safe content",
                model_id="test",
                input_tokens=100,
                output_tokens=50,
                latency_ms=200,
                prompt_hash="abc",
            )
        )

        from maestro.content.schemas import ContentAdaptationProfile, TargetNode

        result = await agent.generate_explanation(
            nodes=[
                TargetNode(node_id="n1", current_state="lacuna", label_it="Test")
            ],
            student_pseudo_id="STUDENTE_test",
            profile=ContentAdaptationProfile(),
            course_language="it",
            session=mock_db_session,
        )

        assert "raw_text" in result

    @pytest.mark.asyncio
    async def test_generate_recovery_mission_retry_note(
        self, agent: TextAgent, mock_gateway: AsyncMock, mock_db_session: AsyncMock
    ) -> None:
        """Retry attempts > 1 should include a retry note in the prompt."""
        safe_content = json.dumps({
            "concept_node_id": "n1",
            "concept_label": "Test",
            "aggancio": {"text": "Hook"},
            "spiegazione": {"text": "Explain"},
            "esempio_pratico": {"text": "Example"},
            "verifica_veloce": {"question": "Q?", "hint": "H"},
            "prossimo_passo": {"text": "Next"},
        })
        mock_gateway.generate = AsyncMock(
            return_value=LLMResponse(
                content=safe_content,
                model_id="test",
                input_tokens=100,
                output_tokens=200,
                latency_ms=500,
                prompt_hash="abc",
            )
        )

        from maestro.content.schemas import ContentAdaptationProfile, TargetNode

        result = await agent.generate_recovery_mission(
            node=TargetNode(node_id="n1", current_state="in_recupero", label_it="Test"),
            student_pseudo_id="STUDENTE_test",
            profile=ContentAdaptationProfile(),
            attempt_number=3,
            session=mock_db_session,
        )

        assert "concept_node_id" in result
        # Check that the gateway was called with a prompt containing retry info
        call_args = mock_gateway.generate.call_args
        request = call_args[0][0]
        assert "retry" in request.task_block.lower() or "attempt" in request.task_block.lower()
