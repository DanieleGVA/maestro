"""Unit tests for Quiz Engine.

Tests quiz generation and response evaluation logic.
"""

import pytest

from maestro.content.quiz_engine import BLOOM_BY_STATE, BLOOM_INSTRUCTIONS, QuizEngine


class TestBloomMapping:
    """Tests for Bloom's taxonomy mapping per student state."""

    def test_introdotto_maps_to_remember_understand(self) -> None:
        assert BLOOM_BY_STATE["introdotto"] == "remember_understand"

    def test_in_recupero_maps_to_remember_understand(self) -> None:
        assert BLOOM_BY_STATE["in_recupero"] == "remember_understand"

    def test_da_consolidare_maps_to_apply_analyze(self) -> None:
        assert BLOOM_BY_STATE["da_consolidare"] == "apply_analyze"

    def test_consolidato_maps_to_evaluate_create(self) -> None:
        assert BLOOM_BY_STATE["consolidato"] == "evaluate_create"

    def test_all_bloom_levels_have_instructions(self) -> None:
        for state, bloom_key in BLOOM_BY_STATE.items():
            assert bloom_key in BLOOM_INSTRUCTIONS, (
                f"State '{state}' maps to '{bloom_key}' which has no instruction"
            )


class TestQuizEvaluation:
    """Tests for the quiz answer evaluation logic."""

    def setup_method(self) -> None:
        # QuizEngine requires a gateway, but evaluate_response is synchronous
        # and doesn't use it. Use None with a type: ignore for testing.
        self.engine = QuizEngine(None)  # type: ignore[arg-type]

    def test_all_correct(self) -> None:
        questions = [
            {"id": "q1", "correct_answer": "A", "question_text": "Q1"},
            {"id": "q2", "correct_answer": "B", "question_text": "Q2"},
            {"id": "q3", "correct_answer": "C", "question_text": "Q3"},
        ]
        answers = [
            {"question_id": "q1", "selected": "A"},
            {"question_id": "q2", "selected": "B"},
            {"question_id": "q3", "selected": "C"},
        ]
        result = self.engine.evaluate_response(
            questions=questions, student_answers=answers
        )
        assert result["score"] == 100
        assert result["correct_count"] == 3
        assert result["total_questions"] == 3

    def test_all_wrong(self) -> None:
        questions = [
            {"id": "q1", "correct_answer": "A", "question_text": "Q1"},
            {"id": "q2", "correct_answer": "B", "question_text": "Q2"},
        ]
        answers = [
            {"question_id": "q1", "selected": "C"},
            {"question_id": "q2", "selected": "D"},
        ]
        result = self.engine.evaluate_response(
            questions=questions, student_answers=answers
        )
        assert result["score"] == 0
        assert result["correct_count"] == 0

    def test_partial_correct(self) -> None:
        questions = [
            {"id": "q1", "correct_answer": "A", "question_text": "Q1"},
            {"id": "q2", "correct_answer": "B", "question_text": "Q2"},
            {"id": "q3", "correct_answer": "C", "question_text": "Q3"},
            {"id": "q4", "correct_answer": "D", "question_text": "Q4"},
        ]
        answers = [
            {"question_id": "q1", "selected": "A"},  # correct
            {"question_id": "q2", "selected": "A"},  # wrong
            {"question_id": "q3", "selected": "C"},  # correct
            {"question_id": "q4", "selected": "A"},  # wrong
        ]
        result = self.engine.evaluate_response(
            questions=questions, student_answers=answers
        )
        assert result["score"] == 50
        assert result["correct_count"] == 2
        assert result["total_questions"] == 4

    def test_case_insensitive_answers(self) -> None:
        """Student answers should match case-insensitively."""
        questions = [
            {"id": "q1", "correct_answer": "A", "question_text": "Q1"},
        ]
        answers = [{"question_id": "q1", "selected": "a"}]
        result = self.engine.evaluate_response(
            questions=questions, student_answers=answers
        )
        assert result["correct_count"] == 1

    def test_missing_answer_counts_as_wrong(self) -> None:
        """Unanswered questions count as wrong."""
        questions = [
            {"id": "q1", "correct_answer": "A", "question_text": "Q1"},
            {"id": "q2", "correct_answer": "B", "question_text": "Q2"},
        ]
        answers = [
            {"question_id": "q1", "selected": "A"},
            # q2 not answered
        ]
        result = self.engine.evaluate_response(
            questions=questions, student_answers=answers
        )
        assert result["correct_count"] == 1
        assert result["total_questions"] == 2
        assert result["score"] == 50

    def test_per_question_results(self) -> None:
        questions = [
            {"id": "q1", "correct_answer": "B", "question_text": "Q1"},
        ]
        answers = [{"question_id": "q1", "selected": "A"}]
        result = self.engine.evaluate_response(
            questions=questions, student_answers=answers
        )
        pq = result["per_question"]
        assert len(pq) == 1
        assert pq[0]["is_correct"] is False
        assert pq[0]["correct_answer"] == "B"
        assert pq[0]["selected"] == "A"

    def test_empty_questions(self) -> None:
        result = self.engine.evaluate_response(questions=[], student_answers=[])
        assert result["score"] == 0
        assert result["total_questions"] == 0
        assert result["correct_count"] == 0

    def test_question_index_based_id(self) -> None:
        """Questions can use question_index as the identifier."""
        questions = [
            {"question_index": 0, "correct_answer": "A", "question_text": "Q1"},
            {"question_index": 1, "correct_answer": "B", "question_text": "Q2"},
        ]
        answers = [
            {"question_id": "0", "selected": "A"},
            {"question_id": "1", "selected": "B"},
        ]
        result = self.engine.evaluate_response(
            questions=questions, student_answers=answers
        )
        assert result["correct_count"] == 2
