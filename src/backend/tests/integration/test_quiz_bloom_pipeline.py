"""Integration tests for the Quiz Engine + Bloom's taxonomy pipeline.

Verifies that quiz generation correctly targets Bloom's levels based on
student state and that evaluation logic integrates with scoring thresholds.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from maestro.content.quiz_engine import (
    BLOOM_BY_STATE,
    BLOOM_INSTRUCTIONS,
    QuizEngine,
)
from maestro.llm.models import LLMResponse
from maestro.safeguarding.retry import FALLBACK_MESSAGE_IT


class TestBloomStateMapping:
    """Test Bloom's taxonomy mapping to student mastery states."""

    def test_introdotto_maps_to_remember(self) -> None:
        assert BLOOM_BY_STATE["introdotto"] == "remember_understand"

    def test_in_recupero_maps_to_remember(self) -> None:
        assert BLOOM_BY_STATE["in_recupero"] == "remember_understand"

    def test_da_consolidare_maps_to_apply(self) -> None:
        assert BLOOM_BY_STATE["da_consolidare"] == "apply_analyze"

    def test_consolidato_maps_to_evaluate(self) -> None:
        assert BLOOM_BY_STATE["consolidato"] == "evaluate_create"

    def test_all_bloom_levels_have_instructions(self) -> None:
        for bloom_key in BLOOM_BY_STATE.values():
            assert bloom_key in BLOOM_INSTRUCTIONS

    def test_unknown_state_defaults_to_remember(self) -> None:
        """States not in the map should default to remember_understand."""
        assert BLOOM_BY_STATE.get("unknown", "remember_understand") == "remember_understand"


class TestQuizGenerationIntegration:
    """Test quiz generation with mocked LLM."""

    @pytest.fixture
    def mock_gateway(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def engine(self, mock_gateway: AsyncMock) -> QuizEngine:
        return QuizEngine(mock_gateway)

    @pytest.mark.asyncio
    async def test_valid_quiz_generation(
        self, engine: QuizEngine, mock_gateway: AsyncMock, mock_db_session: AsyncMock
    ) -> None:
        """Valid JSON quiz should be returned with metadata."""
        quiz_data = json.dumps({
            "questions": [
                {
                    "question_text": "Cos'e' una variabile?",
                    "options": {"A": "Un contenitore", "B": "Un ciclo", "C": "Un tipo", "D": "Un errore"},
                    "correct_answer": "A",
                    "explanation": "Una variabile e' un contenitore di dati.",
                    "bloom_level": "remember",
                }
            ]
        })
        mock_gateway.generate = AsyncMock(
            return_value=LLMResponse(
                content=quiz_data, model_id="test", input_tokens=100,
                output_tokens=200, latency_ms=300, prompt_hash="h1",
            )
        )

        result = await engine.generate_quiz(
            node_id="n1",
            node_label="Variabili",
            current_state="introdotto",
            purpose="closure",
            session=mock_db_session,
        )

        assert "questions" in result
        assert "metadata" in result
        assert result["metadata"]["bloom_level"] == "remember_understand"

    @pytest.mark.asyncio
    async def test_safeguarding_blocked_quiz(
        self, engine: QuizEngine, mock_gateway: AsyncMock, mock_db_session: AsyncMock
    ) -> None:
        """Quiz with safeguarding violations should return fallback."""
        blocked_content = "Sei peggio dei tuoi compagni in questo argomento."
        mock_gateway.generate = AsyncMock(
            return_value=LLMResponse(
                content=blocked_content, model_id="test", input_tokens=100,
                output_tokens=50, latency_ms=200, prompt_hash="h1",
            )
        )

        result = await engine.generate_quiz(
            node_id="n1",
            node_label="Test",
            current_state="in_recupero",
            purpose="closure",
            session=mock_db_session,
        )

        assert result["fallback"] is True
        assert result["message"] == FALLBACK_MESSAGE_IT


class TestQuizEvaluationIntegration:
    """Test quiz evaluation and scoring."""

    def test_perfect_score(self) -> None:
        engine = QuizEngine.__new__(QuizEngine)
        questions = [
            {"id": "1", "correct_answer": "A"},
            {"id": "2", "correct_answer": "B"},
            {"id": "3", "correct_answer": "C"},
        ]
        answers = [
            {"question_id": "1", "selected": "A"},
            {"question_id": "2", "selected": "B"},
            {"question_id": "3", "selected": "C"},
        ]

        result = engine.evaluate_response(questions=questions, student_answers=answers)
        assert result["score"] == 100
        assert result["correct_count"] == 3

    def test_zero_score(self) -> None:
        engine = QuizEngine.__new__(QuizEngine)
        questions = [
            {"id": "1", "correct_answer": "A"},
            {"id": "2", "correct_answer": "B"},
        ]
        answers = [
            {"question_id": "1", "selected": "C"},
            {"question_id": "2", "selected": "D"},
        ]

        result = engine.evaluate_response(questions=questions, student_answers=answers)
        assert result["score"] == 0
        assert result["correct_count"] == 0

    def test_threshold_80_percent(self) -> None:
        """4/5 correct = 80%, which meets the quiz_superato threshold."""
        engine = QuizEngine.__new__(QuizEngine)
        questions = [{"id": str(i), "correct_answer": "A"} for i in range(5)]
        answers = [
            {"question_id": "0", "selected": "A"},
            {"question_id": "1", "selected": "A"},
            {"question_id": "2", "selected": "A"},
            {"question_id": "3", "selected": "A"},
            {"question_id": "4", "selected": "B"},  # wrong
        ]

        result = engine.evaluate_response(questions=questions, student_answers=answers)
        assert result["score"] == 80
        assert result["score"] >= 80  # meets threshold

    def test_below_50_threshold(self) -> None:
        """2/5 correct = 40%, which triggers regression to lacuna."""
        engine = QuizEngine.__new__(QuizEngine)
        questions = [{"id": str(i), "correct_answer": "A"} for i in range(5)]
        answers = [
            {"question_id": "0", "selected": "A"},
            {"question_id": "1", "selected": "A"},
            {"question_id": "2", "selected": "B"},
            {"question_id": "3", "selected": "B"},
            {"question_id": "4", "selected": "B"},
        ]

        result = engine.evaluate_response(questions=questions, student_answers=answers)
        assert result["score"] == 40
        assert result["score"] < 50

    def test_case_insensitive_answers(self) -> None:
        """Answer matching should be case-insensitive."""
        engine = QuizEngine.__new__(QuizEngine)
        questions = [{"id": "1", "correct_answer": "A"}]
        answers = [{"question_id": "1", "selected": "a"}]

        result = engine.evaluate_response(questions=questions, student_answers=answers)
        assert result["score"] == 100
