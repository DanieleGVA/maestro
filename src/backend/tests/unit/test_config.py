"""Unit tests for application configuration (config.py)."""

import os
from unittest.mock import patch

import pytest


class TestSettings:
    """Verify Settings defaults and env override."""

    def test_default_database_url(self) -> None:
        from maestro.config import Settings

        s = Settings()
        assert "postgresql+asyncpg" in s.database_url
        assert "maestro" in s.database_url

    def test_default_redis_url(self) -> None:
        from maestro.config import Settings

        s = Settings()
        assert s.redis_url.startswith("redis://")

    def test_default_keycloak_realm(self) -> None:
        from maestro.config import Settings

        s = Settings()
        assert s.keycloak_realm == "maestro"

    def test_default_jwt_algorithm(self) -> None:
        from maestro.config import Settings

        s = Settings()
        assert s.jwt_algorithm == "RS256"

    def test_default_llm_max_retries(self) -> None:
        from maestro.config import Settings

        s = Settings()
        assert s.llm_max_retries == 3

    def test_default_debug_off(self) -> None:
        from maestro.config import Settings

        s = Settings()
        assert s.debug is False

    def test_default_cors_origins(self) -> None:
        from maestro.config import Settings

        s = Settings()
        assert "http://localhost:3000" in s.cors_origins

    def test_env_override(self) -> None:
        from maestro.config import Settings

        with patch.dict(os.environ, {"MAESTRO_DEBUG": "true"}):
            s = Settings()
            assert s.debug is True

    def test_db_pool_defaults(self) -> None:
        from maestro.config import Settings

        s = Settings()
        assert s.db_pool_size == 10
        assert s.db_max_overflow == 5

    def test_llm_models_have_defaults(self) -> None:
        from maestro.config import Settings

        s = Settings()
        assert "claude" in s.llm_primary_model
        assert "gpt" in s.llm_batch_model
