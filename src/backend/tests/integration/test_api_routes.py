"""Integration tests for API routes.

Tests request/response validation, authentication gating, and error handling
across the FastAPI application. Uses TestClient with mocked dependencies.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from maestro.auth.keycloak import UserClaims
from maestro.main import app


def _mock_student_user() -> UserClaims:
    return UserClaims(
        sub="stu-uuid-1",
        role="student",
        school_id="school-1",
        student_id="stu-uuid-1",
        class_id="class-1",
    )


def _mock_teacher_user() -> UserClaims:
    return UserClaims(
        sub="teacher-uuid-1",
        role="teacher",
        school_id="school-1",
        class_id="class-1",
    )


def _mock_admin_user() -> UserClaims:
    return UserClaims(sub="admin-uuid-1", role="admin", school_id="school-1")


class TestSessionEndpoints:
    """Test session-related API routes."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_start_session_student_succeeds(self, client: TestClient) -> None:
        with (
            patch("maestro.auth.dependencies.get_current_user", return_value=_mock_student_user()),
            patch("maestro.auth.dependencies.get_db", return_value=AsyncMock()),
        ):
            resp = client.post(
                "/api/v1/sessions/start",
                json={"course_id": "course-1"},
            )
            assert resp.status_code == 201
            data = resp.json()
            assert "data" in data
            assert data["data"]["student_id"] == "stu-uuid-1"

    def test_start_session_teacher_forbidden(self, client: TestClient) -> None:
        with (
            patch("maestro.auth.dependencies.get_current_user", return_value=_mock_teacher_user()),
            patch("maestro.auth.dependencies.get_db", return_value=AsyncMock()),
        ):
            resp = client.post(
                "/api/v1/sessions/start",
                json={"course_id": "course-1"},
            )
            assert resp.status_code == 403

    def test_end_session_student_succeeds(self, client: TestClient) -> None:
        with (
            patch("maestro.auth.dependencies.get_current_user", return_value=_mock_student_user()),
            patch("maestro.auth.dependencies.get_db", return_value=AsyncMock()),
        ):
            resp = client.post(
                "/api/v1/sessions/end",
                json={"session_id": "sess-1"},
            )
            assert resp.status_code == 200
            assert resp.json()["data"]["ended"] is True


class TestHealthEndpointIntegration:
    """Test health endpoint returns correct structure."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_health_is_unauthenticated(self, client: TestClient) -> None:
        """Health endpoint should NOT require authentication."""
        resp = client.get("/healthz")
        assert resp.status_code == 200

    def test_health_response_structure(self, client: TestClient) -> None:
        resp = client.get("/healthz")
        data = resp.json()
        assert "status" in data
        assert "version" in data


class TestRequestValidation:
    """Test that invalid requests are properly rejected."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_session_start_missing_course_id(self, client: TestClient) -> None:
        with (
            patch("maestro.auth.dependencies.get_current_user", return_value=_mock_student_user()),
            patch("maestro.auth.dependencies.get_db", return_value=AsyncMock()),
        ):
            resp = client.post("/api/v1/sessions/start", json={})
            assert resp.status_code == 422  # Validation error

    def test_session_activity_invalid_type(self, client: TestClient) -> None:
        with (
            patch("maestro.auth.dependencies.get_current_user", return_value=_mock_student_user()),
            patch("maestro.auth.dependencies.get_db", return_value=AsyncMock()),
        ):
            resp = client.post(
                "/api/v1/sessions/activity",
                json={
                    "session_id": "sess-1",
                    "activity_type": "INVALID_TYPE",  # Should fail regex
                },
            )
            assert resp.status_code == 422
