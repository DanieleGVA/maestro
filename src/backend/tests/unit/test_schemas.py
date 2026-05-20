"""Unit tests for shared Pydantic schemas (common/schemas.py)."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from maestro.common.schemas import (
    ApiResponse,
    ErrorDetail,
    ErrorResponse,
    Meta,
    PaginatedResponse,
)


class TestMeta:
    def test_meta_with_request_id(self) -> None:
        m = Meta(request_id="req-1")
        assert m.request_id == "req-1"
        assert isinstance(m.timestamp, datetime)


class TestApiResponse:
    def test_wraps_data(self) -> None:
        resp = ApiResponse(
            data={"key": "value"},
            meta=Meta(request_id="req-1"),
        )
        assert resp.data == {"key": "value"}
        assert resp.meta.request_id == "req-1"


class TestErrorDetail:
    def test_basic(self) -> None:
        ed = ErrorDetail(code="NOT_FOUND", message="nope")
        assert ed.code == "NOT_FOUND"
        assert ed.message == "nope"
        assert ed.details is None

    def test_with_details(self) -> None:
        ed = ErrorDetail(code="ERR", message="msg", details={"x": 1})
        assert ed.details["x"] == 1


class TestErrorResponse:
    def test_wraps_error(self) -> None:
        resp = ErrorResponse(
            error=ErrorDetail(code="E", message="m"),
            meta=Meta(request_id="req-2"),
        )
        assert resp.error.code == "E"
        assert resp.meta.request_id == "req-2"


class TestPaginatedResponse:
    def test_pagination_fields(self) -> None:
        resp = PaginatedResponse(
            data=["a", "b"],
            meta=Meta(request_id="req-3"),
            total=100,
            page=1,
            page_size=10,
            total_pages=10,
        )
        assert resp.total == 100
        assert resp.page == 1
        assert resp.page_size == 10
        assert resp.total_pages == 10
        assert len(resp.data) == 2


class TestContentSchemas:
    """Test content-related Pydantic schemas."""

    def test_target_node_defaults(self) -> None:
        from maestro.content.schemas import TargetNode

        n = TargetNode(node_id="n1", current_state="lacuna")
        assert n.node_type == "micro"
        assert n.label_it == ""
        assert n.error_description is None

    def test_content_adaptation_profile_defaults(self) -> None:
        from maestro.content.schemas import ContentAdaptationProfile

        p = ContentAdaptationProfile()
        assert p.visuale == 0.2
        assert p.tone == "neutro"
        assert p.length == "sintesi"

    def test_content_adaptation_profile_validation(self) -> None:
        from maestro.content.schemas import ContentAdaptationProfile

        with pytest.raises(ValidationError):
            ContentAdaptationProfile(visuale=2.0)  # > 1.0

    def test_quiz_generate_request_defaults(self) -> None:
        from maestro.content.schemas import QuizGenerateRequest

        req = QuizGenerateRequest(
            student_pseudo_id="STU_x",
            course_id="course-1",
            node_id="n-1",
        )
        assert req.purpose == "closure"
        assert req.num_questions == 5
        assert req.current_state == "in_recupero"

    def test_quiz_submit_request_validation(self) -> None:
        from maestro.content.schemas import QuizSubmitRequest

        with pytest.raises(ValidationError):
            QuizSubmitRequest(student_id="s1", answers=[], total_time_ms=100)

    def test_student_create_request_validation(self) -> None:
        from maestro.api.v1.students import StudentCreateRequest

        req = StudentCreateRequest(
            school_id="school-1",
            name="Luca",
            surname="Rossi",
            school_year=3,
        )
        assert req.school_year == 3
        assert req.birth_year is None

    def test_student_create_request_year_bounds(self) -> None:
        from maestro.api.v1.students import StudentCreateRequest

        with pytest.raises(ValidationError):
            StudentCreateRequest(
                school_id="s1",
                name="L",
                surname="R",
                school_year=6,  # > 5
            )


class TestLLMModels:
    """Test LLM request/response Pydantic models."""

    def test_llm_request_defaults(self) -> None:
        from maestro.llm.models import LLMRequest

        req = LLMRequest(
            agent_name="test",
            prompt_template_id="t1",
            system_prompt="sys",
            context_block="ctx",
            task_block="task",
            correlation_id="c-1",
        )
        assert req.model_preference == "quality"
        assert req.max_tokens == 2000
        assert req.temperature == 0.7
        assert req.response_format == "json"

    def test_llm_request_temperature_bounds(self) -> None:
        from maestro.llm.models import LLMRequest

        with pytest.raises(ValidationError):
            LLMRequest(
                agent_name="test",
                prompt_template_id="t1",
                system_prompt="s",
                context_block="c",
                task_block="t",
                correlation_id="c-1",
                temperature=1.5,
            )

    def test_llm_response_fields(self) -> None:
        from maestro.llm.models import LLMResponse

        resp = LLMResponse(
            content="hello",
            model_id="claude",
            input_tokens=10,
            output_tokens=20,
            latency_ms=100,
            prompt_hash="abc",
        )
        assert resp.cache_hit is False
        assert resp.content == "hello"

    def test_llm_audit_entry(self) -> None:
        from maestro.llm.models import LLMAuditEntry

        entry = LLMAuditEntry(
            request_id="r1",
            agent_name="test",
            model_id="m1",
            prompt_hash="h1",
            input_tokens=10,
            output_tokens=20,
            latency_ms=100,
        )
        assert entry.cache_hit is False
        assert entry.created_at is None
