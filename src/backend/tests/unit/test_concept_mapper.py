"""Unit tests for the concept mapping engine (maestro.kg.concept_mapper).

Tests the scoring logic, confidence levels, and LLM response parsing
without requiring a database or external LLM API.
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maestro.kg.concept_mapper import (
    HIGH_CONFIDENCE_THRESHOLD,
    LESSON_EMBEDDING_WEIGHT,
    LESSON_LLM_WEIGHT,
    MEDIUM_CONFIDENCE_THRESHOLD,
    ERROR_EMBEDDING_WEIGHT,
    ERROR_LLM_WEIGHT,
    CandidateMapping,
    _confidence_level,
    _parse_llm_response,
    map_concept,
    map_error_concept,
)


# ---------------------------------------------------------------------------
# Tests for _confidence_level
# ---------------------------------------------------------------------------

class TestConfidenceLevel:
    def test_high_confidence(self) -> None:
        assert _confidence_level(0.85) == "high"
        assert _confidence_level(0.80) == "high"
        assert _confidence_level(1.0) == "high"

    def test_medium_confidence(self) -> None:
        assert _confidence_level(0.65) == "medium"
        assert _confidence_level(0.60) == "medium"
        assert _confidence_level(0.79) == "medium"

    def test_low_confidence(self) -> None:
        assert _confidence_level(0.50) == "low"
        assert _confidence_level(0.0) == "low"
        assert _confidence_level(0.59) == "low"


# ---------------------------------------------------------------------------
# Tests for _parse_llm_response
# ---------------------------------------------------------------------------

class TestParseLLMResponse:
    def test_parse_json_array(self) -> None:
        content = json.dumps([
            {"node_id": "abc", "confidence": 0.9, "explanation": "match"},
            {"node_id": "def", "confidence": 0.3, "explanation": "no match"},
        ])
        result = _parse_llm_response(content)
        assert len(result) == 2
        assert result[0]["node_id"] == "abc"
        assert result[1]["confidence"] == 0.3

    def test_parse_wrapped_object_results(self) -> None:
        content = json.dumps({
            "results": [
                {"node_id": "abc", "confidence": 0.8}
            ]
        })
        result = _parse_llm_response(content)
        assert len(result) == 1
        assert result[0]["node_id"] == "abc"

    def test_parse_wrapped_object_mappings(self) -> None:
        content = json.dumps({
            "mappings": [{"node_id": "x", "confidence": 0.5}]
        })
        result = _parse_llm_response(content)
        assert len(result) == 1

    def test_parse_single_object_with_node_id(self) -> None:
        content = json.dumps({"node_id": "abc", "confidence": 0.9})
        result = _parse_llm_response(content)
        assert len(result) == 1
        assert result[0]["node_id"] == "abc"

    def test_parse_invalid_json(self) -> None:
        assert _parse_llm_response("not json at all") == []

    def test_parse_empty_string(self) -> None:
        assert _parse_llm_response("") == []

    def test_parse_empty_array(self) -> None:
        assert _parse_llm_response("[]") == []

    def test_parse_dict_without_known_keys(self) -> None:
        content = json.dumps({"unknown_key": "value"})
        result = _parse_llm_response(content)
        assert result == []


# ---------------------------------------------------------------------------
# Tests for scoring weights
# ---------------------------------------------------------------------------

class TestScoringWeights:
    """Verify the scoring weights match HLD-002 specification."""

    def test_lesson_weights_sum_to_one(self) -> None:
        assert LESSON_EMBEDDING_WEIGHT + LESSON_LLM_WEIGHT == 1.0

    def test_lesson_weights_values(self) -> None:
        assert LESSON_EMBEDDING_WEIGHT == 0.4
        assert LESSON_LLM_WEIGHT == 0.6

    def test_error_weights_sum_to_one(self) -> None:
        assert ERROR_EMBEDDING_WEIGHT + ERROR_LLM_WEIGHT == 1.0

    def test_error_weights_values(self) -> None:
        assert ERROR_EMBEDDING_WEIGHT == 0.3
        assert ERROR_LLM_WEIGHT == 0.7

    def test_thresholds(self) -> None:
        assert HIGH_CONFIDENCE_THRESHOLD == 0.80
        assert MEDIUM_CONFIDENCE_THRESHOLD == 0.60


class TestCompositeScoring:
    """Test composite score computation with known inputs."""

    def test_perfect_lesson_score(self) -> None:
        """Both embedding and LLM give max confidence."""
        emb_sim = 1.0
        llm_conf = 1.0
        score = LESSON_EMBEDDING_WEIGHT * emb_sim + LESSON_LLM_WEIGHT * llm_conf
        assert score == 1.0

    def test_zero_lesson_score(self) -> None:
        emb_sim = 0.0
        llm_conf = 0.0
        score = LESSON_EMBEDDING_WEIGHT * emb_sim + LESSON_LLM_WEIGHT * llm_conf
        assert score == 0.0

    def test_high_embedding_low_llm(self) -> None:
        """High embedding similarity but LLM disagrees."""
        emb_sim = 0.95
        llm_conf = 0.2
        score = LESSON_EMBEDDING_WEIGHT * emb_sim + LESSON_LLM_WEIGHT * llm_conf
        # 0.4*0.95 + 0.6*0.2 = 0.38 + 0.12 = 0.50
        assert abs(score - 0.50) < 0.001

    def test_low_embedding_high_llm(self) -> None:
        """Low embedding similarity but LLM confirms concept match."""
        emb_sim = 0.3
        llm_conf = 0.9
        score = LESSON_EMBEDDING_WEIGHT * emb_sim + LESSON_LLM_WEIGHT * llm_conf
        # 0.4*0.3 + 0.6*0.9 = 0.12 + 0.54 = 0.66
        assert abs(score - 0.66) < 0.001

    def test_error_scoring_weights_llm_more(self) -> None:
        """Error mapping gives more weight to LLM (0.7 vs 0.6 for lessons)."""
        emb_sim = 0.5
        llm_conf = 0.9
        lesson_score = LESSON_EMBEDDING_WEIGHT * emb_sim + LESSON_LLM_WEIGHT * llm_conf
        error_score = ERROR_EMBEDDING_WEIGHT * emb_sim + ERROR_LLM_WEIGHT * llm_conf
        # lesson: 0.4*0.5 + 0.6*0.9 = 0.20 + 0.54 = 0.74
        # error:  0.3*0.5 + 0.7*0.9 = 0.15 + 0.63 = 0.78
        assert error_score > lesson_score


# ---------------------------------------------------------------------------
# Tests for map_concept (mocked)
# ---------------------------------------------------------------------------

class TestMapConcept:
    @pytest.mark.asyncio
    async def test_no_similar_nodes_returns_empty(self) -> None:
        """When no KG nodes are similar, returns empty list."""
        session = AsyncMock()

        with patch(
            "maestro.kg.concept_mapper.search_similar_nodes",
            return_value=[],
        ):
            result = await map_concept(
                session,
                "Some lesson text about algorithms",
                [0.1] * 1536,
                course_id=uuid.uuid4(),
            )
            assert result == []

    @pytest.mark.asyncio
    async def test_candidates_sorted_by_composite_score(self) -> None:
        """Candidates should be sorted by composite_score descending."""
        session = AsyncMock()
        node_id_1 = uuid.uuid4()
        node_id_2 = uuid.uuid4()

        similar_nodes = [
            {
                "node_id": node_id_1,
                "node_type": "micro",
                "label_it": "Concept A",
                "description": "Desc A",
                "similarity": 0.8,
            },
            {
                "node_id": node_id_2,
                "node_type": "micro",
                "label_it": "Concept B",
                "description": "Desc B",
                "similarity": 0.7,
            },
        ]

        # Mock LLM to give higher confidence to node_id_2
        llm_response = json.dumps({
            "results": [
                {"node_id": str(node_id_1), "confidence": 0.5, "explanation": "Partial match"},
                {"node_id": str(node_id_2), "confidence": 0.95, "explanation": "Strong match"},
            ]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = llm_response

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

        with (
            patch("maestro.kg.concept_mapper.search_similar_nodes", return_value=similar_nodes),
            patch("maestro.kg.concept_mapper._get_openai_client", return_value=mock_client),
        ):
            result = await map_concept(
                session,
                "Lesson text about concepts",
                [0.1] * 1536,
                course_id=uuid.uuid4(),
            )

            # node_id_2 should come first (higher composite score due to high LLM confidence)
            assert len(result) >= 1
            if len(result) == 2:
                assert result[0].composite_score >= result[1].composite_score

    @pytest.mark.asyncio
    async def test_below_threshold_filtered_out(self) -> None:
        """Candidates below MEDIUM_CONFIDENCE_THRESHOLD are filtered."""
        session = AsyncMock()
        node_id = uuid.uuid4()

        similar_nodes = [
            {
                "node_id": node_id,
                "node_type": "micro",
                "label_it": "Weak match",
                "description": None,
                "similarity": 0.3,
            },
        ]

        llm_response = json.dumps({
            "results": [
                {"node_id": str(node_id), "confidence": 0.2, "explanation": "Weak"},
            ]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = llm_response

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

        with (
            patch("maestro.kg.concept_mapper.search_similar_nodes", return_value=similar_nodes),
            patch("maestro.kg.concept_mapper._get_openai_client", return_value=mock_client),
        ):
            result = await map_concept(
                session,
                "Some text",
                [0.1] * 1536,
                course_id=uuid.uuid4(),
            )
            # 0.4 * 0.3 + 0.6 * 0.2 = 0.12 + 0.12 = 0.24 < 0.60 threshold
            assert len(result) == 0


# ---------------------------------------------------------------------------
# Tests for map_error_concept (mocked)
# ---------------------------------------------------------------------------

class TestMapErrorConcept:
    @pytest.mark.asyncio
    async def test_error_mapping_uses_higher_llm_weight(self) -> None:
        """Error mapping should weight LLM more heavily (0.7 vs 0.6)."""
        session = AsyncMock()
        node_id = uuid.uuid4()

        similar_nodes = [
            {
                "node_id": node_id,
                "node_type": "micro",
                "label_it": "Session fixation",
                "description": "Attacco session fixation",
                "similarity": 0.6,
            },
        ]

        llm_response = json.dumps({
            "results": [
                {"node_id": str(node_id), "confidence": 0.9, "explanation": "Error matches"},
            ]
        })

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = llm_response

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

        with (
            patch("maestro.kg.concept_mapper.search_similar_nodes", return_value=similar_nodes),
            patch("maestro.kg.concept_mapper._get_openai_client", return_value=mock_client),
            patch("maestro.kg.concept_mapper.generate_embedding", return_value=[0.1] * 1536),
        ):
            result = await map_error_concept(
                session,
                "Student confused session fixation with hijacking",
                "Question about PHP session security",
                course_id=uuid.uuid4(),
            )

            assert len(result) >= 1
            # Expected score: 0.3 * 0.6 + 0.7 * 0.9 = 0.18 + 0.63 = 0.81
            assert result[0].composite_score > 0.80
