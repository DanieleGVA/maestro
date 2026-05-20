"""Unit tests for the health check endpoint (api/v1/health.py)."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test the /healthz endpoint."""

    @pytest.fixture
    def client(self) -> TestClient:
        from maestro.main import app

        return TestClient(app)

    def test_health_returns_200(self, client: TestClient) -> None:
        resp = client.get("/healthz")
        assert resp.status_code == 200

    def test_health_body_structure(self, client: TestClient) -> None:
        resp = client.get("/healthz")
        data = resp.json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_health_includes_version(self, client: TestClient) -> None:
        resp = client.get("/healthz")
        data = resp.json()
        assert "version" in data
