"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration. All secrets from env vars, never hardcoded."""

    model_config = {"env_prefix": "MAESTRO_"}

    # --- Database ---
    database_url: str = "postgresql+asyncpg://maestro_app:changeme@localhost:5432/maestro"
    db_pool_size: int = 10
    db_max_overflow: int = 5

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Auth (Keycloak) ---
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "maestro"
    keycloak_client_id: str = "maestro-api"
    jwt_algorithm: str = "RS256"

    # --- LLM ---
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_primary_model: str = "claude-sonnet-4-20250514"
    llm_batch_model: str = "gpt-4o-mini"
    llm_max_retries: int = 3

    # --- Encryption ---
    pii_encryption_key: str = ""  # pgcrypto symmetric key

    # --- App ---
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
