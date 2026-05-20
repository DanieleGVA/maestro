"""Integration tests for the safeguarding + content generation pipeline.

Verifies that content flows through safeguarding checks before reaching students,
and that the retry/fallback mechanism works correctly end-to-end.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maestro.content.text_agent import TextAgent
from maestro.content.schemas import ContentAdaptationProfile, TargetNode
from maestro.llm.models import LLMResponse
from maestro.safeguarding.checker import safeguarding_check
from maestro.safeguarding.retry import FALLBACK_MESSAGE_IT, MAX_SAFEGUARDING_ATTEMPTS


class TestSafeguardingContentPipeline:
    """Test safeguarding checks on realistic content."""

    def test_safe_educational_content_passes(self) -> None:
        """Good educational content should pass safeguarding."""
        content = (
            "Questo concetto ha bisogno di un altro giro. "
            "Pensa a una variabile come a un'etichetta su un barattolo: "
            "il nome non cambia, ma puoi mettere cose diverse. "
            "Quando ti senti pronto, prova il quiz!"
        )
        result = safeguarding_check(content)
        assert result.passed is True
        assert result.content == content

    def test_student_comparison_blocks(self) -> None:
        """Content comparing students must be blocked."""
        content = (
            "Mentre i tuoi compagni sono avanti, tu hai bisogno di "
            "recuperare. Sei peggio della media della classe."
        )
        result = safeguarding_check(content)
        assert result.passed is False
        assert result.content is None

    def test_mixed_content_with_one_violation_blocks(self) -> None:
        """Even mostly-safe content with one violation should be blocked."""
        content = (
            "La session fixation e' un attacco dove l'attaccante imposta "
            "un session ID prima dell'autenticazione. Sei scarso in questo "
            "argomento, ma possiamo rimediare."
        )
        result = safeguarding_check(content)
        assert result.passed is False

    def test_technical_php_code_not_blocked(self) -> None:
        """Technical code should not trigger false positives."""
        content = (
            "La funzione session_start() inizializza una sessione PHP. "
            "Il codice corretto chiama session_regenerate_id(true). "
            "Ecco il codice [CORRETTO]: session_start(); "
            "session_regenerate_id(true);"
        )
        result = safeguarding_check(content)
        assert result.passed is True


class TestRetryPipelineIntegration:
    """Test the full retry pipeline: generation -> check -> retry -> fallback."""

    @pytest.mark.asyncio
    async def test_first_attempt_blocked_second_succeeds(self) -> None:
        """If first attempt is blocked but second is clean, content is delivered."""
        gateway = AsyncMock()
        agent = TextAgent(gateway)

        blocked_content = "Sei scarso in programmazione."
        safe_content = json.dumps({
            "blocks": [{"concept_node_id": "n1", "text": "Ecco il concetto."}],
            "summary": "Buon lavoro!"
        })

        # First call returns blocked content, second returns safe
        gateway.generate = AsyncMock(
            side_effect=[
                LLMResponse(
                    content=blocked_content, model_id="m1", input_tokens=100,
                    output_tokens=50, latency_ms=200, prompt_hash="h1",
                ),
                LLMResponse(
                    content=safe_content, model_id="m1", input_tokens=100,
                    output_tokens=50, latency_ms=200, prompt_hash="h2",
                ),
            ]
        )

        session = AsyncMock()
        result = await agent.generate_explanation(
            nodes=[TargetNode(node_id="n1", current_state="lacuna", label_it="Test")],
            student_pseudo_id="STUDENTE_x",
            profile=ContentAdaptationProfile(),
            course_language="it",
            session=session,
        )

        assert "fallback" not in result
        assert "blocks" in result
        assert gateway.generate.call_count == 2

    @pytest.mark.asyncio
    async def test_all_attempts_blocked_serves_fallback(self) -> None:
        """After MAX_SAFEGUARDING_ATTEMPTS blocked, fallback is served."""
        gateway = AsyncMock()
        agent = TextAgent(gateway)

        blocked_content = "Sei un caso perso, non sarai mai capace."
        gateway.generate = AsyncMock(
            return_value=LLMResponse(
                content=blocked_content, model_id="m1", input_tokens=100,
                output_tokens=50, latency_ms=200, prompt_hash="h1",
            )
        )

        session = AsyncMock()
        result = await agent.generate_explanation(
            nodes=[TargetNode(node_id="n1", current_state="lacuna", label_it="Test")],
            student_pseudo_id="STUDENTE_x",
            profile=ContentAdaptationProfile(),
            course_language="it",
            session=session,
        )

        assert result["fallback"] is True
        assert result["message"] == FALLBACK_MESSAGE_IT
        assert gateway.generate.call_count == MAX_SAFEGUARDING_ATTEMPTS


class TestWellbeingToSafeguardingIntegration:
    """Test that wellbeing checks work alongside content safeguarding."""

    def test_wellbeing_check_on_student_input(self) -> None:
        """Wellbeing keywords should be detected in student input."""
        from maestro.safeguarding.checker import wellbeing_check

        matches = wellbeing_check("Non ce la faccio piu', voglio smettere")
        assert len(matches) >= 2

        # Critical/high urgency should come first
        assert matches[0].urgency in ("critical", "high")

    def test_safeguarding_and_wellbeing_independent(self) -> None:
        """Safeguarding checks content; wellbeing checks student input. They're independent."""
        from maestro.safeguarding.checker import safeguarding_check, wellbeing_check

        # This is LLM-generated content -- safeguarding check
        content = "Pensa a una variabile come a un contenitore."
        sg_result = safeguarding_check(content)
        assert sg_result.passed is True

        # This is student input -- wellbeing check
        student_input = "Non ci riesco, e' troppo difficile"
        wb_matches = wellbeing_check(student_input)
        assert len(wb_matches) >= 1
