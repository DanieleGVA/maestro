"""Unit tests for the FastAPI application entry point (main.py).

Tests error handlers, security headers, and CORS configuration.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

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
from maestro.main import _ERROR_STATUS_MAP, app


class TestSecurityHeaders:
    """Test that security headers are set on all responses."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_nosniff(self, client: TestClient) -> None:
        resp = client.get("/healthz")
        assert resp.headers["X-Content-Type-Options"] == "nosniff"

    def test_frame_deny(self, client: TestClient) -> None:
        resp = client.get("/healthz")
        assert resp.headers["X-Frame-Options"] == "DENY"

    def test_referrer_policy(self, client: TestClient) -> None:
        resp = client.get("/healthz")
        assert "strict-origin" in resp.headers["Referrer-Policy"]

    def test_cache_control_no_store(self, client: TestClient) -> None:
        resp = client.get("/healthz")
        assert resp.headers["Cache-Control"] == "no-store"

    def test_hsts(self, client: TestClient) -> None:
        resp = client.get("/healthz")
        assert "max-age=" in resp.headers["Strict-Transport-Security"]

    def test_xss_protection_disabled(self, client: TestClient) -> None:
        """X-XSS-Protection should be 0 (legacy header, CSP preferred)."""
        resp = client.get("/healthz")
        assert resp.headers["X-XSS-Protection"] == "0"


class TestErrorStatusMapping:
    """Test the error type to HTTP status code mapping."""

    def test_not_found_maps_to_404(self) -> None:
        assert _ERROR_STATUS_MAP[NotFoundError] == 404

    def test_forbidden_maps_to_403(self) -> None:
        assert _ERROR_STATUS_MAP[ForbiddenError] == 403

    def test_consent_maps_to_403(self) -> None:
        assert _ERROR_STATUS_MAP[ConsentRequiredError] == 403

    def test_transition_maps_to_422(self) -> None:
        assert _ERROR_STATUS_MAP[TransitionIllegalError] == 422

    def test_safeguarding_maps_to_422(self) -> None:
        assert _ERROR_STATUS_MAP[SafeguardingBlockedError] == 422

    def test_override_maps_to_422(self) -> None:
        assert _ERROR_STATUS_MAP[OverrideMotivationError] == 422

    def test_llm_maps_to_503(self) -> None:
        assert _ERROR_STATUS_MAP[LLMUnavailableError] == 503


class TestCORSConfiguration:
    """Test CORS middleware is properly configured."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_preflight_request(self, client: TestClient) -> None:
        resp = client.options(
            "/healthz",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Should allow the origin from settings
        assert resp.status_code == 200

    def test_cors_allows_auth_header(self, client: TestClient) -> None:
        resp = client.options(
            "/healthz",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization",
            },
        )
        assert resp.status_code == 200
