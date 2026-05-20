"""Database initialisation utility.

Runs Alembic migrations programmatically, creates required PostgreSQL
extensions and schemas. Fully idempotent: safe to call on every startup.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from maestro.db.engine import engine

logger = logging.getLogger(__name__)

# Resolve paths relative to the backend root (where alembic.ini lives)
_BACKEND_ROOT = Path(__file__).resolve().parents[4]  # src/backend/
_ALEMBIC_INI = _BACKEND_ROOT / "alembic.ini"


def _get_alembic_config() -> Config:
    """Build an Alembic Config pointing at our alembic.ini."""
    cfg = Config(str(_ALEMBIC_INI))
    # Override script_location to an absolute path so Alembic finds versions/
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    return cfg


async def _ensure_extensions(eng: AsyncEngine) -> None:
    """Create required PostgreSQL extensions if they do not exist."""
    extensions = ["pgcrypto", "vector"]
    async with eng.begin() as conn:
        for ext in extensions:
            await conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS {ext}"))
            logger.info("PostgreSQL extension '%s' ensured", ext)


async def _ensure_schemas(eng: AsyncEngine) -> None:
    """Create the application schemas if they do not exist."""
    schemas = ["core", "kmm", "content", "audit", "kg"]
    async with eng.begin() as conn:
        for schema in schemas:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            logger.info("PostgreSQL schema '%s' ensured", schema)


def _run_alembic_upgrade() -> None:
    """Run ``alembic upgrade head`` synchronously.

    Alembic's command API is synchronous. The async engine in env.py
    handles the actual connection internally via asyncio.run().
    """
    cfg = _get_alembic_config()

    # Ensure the database URL is propagated from settings
    from maestro.config import settings

    cfg.set_main_option("sqlalchemy.url", settings.database_url)

    logger.info("Running Alembic migrations (upgrade head)...")
    command.upgrade(cfg, "head")
    logger.info("Alembic migrations completed")


async def init_db() -> None:
    """Initialise the database: extensions, schemas, and migrations.

    This function is idempotent and should be called during application
    startup (FastAPI lifespan).
    """
    logger.info("Initialising database...")

    # Step 1: Ensure extensions exist (requires superuser or CREATE on db)
    try:
        await _ensure_extensions(engine)
    except Exception:
        logger.warning(
            "Could not create PostgreSQL extensions (may need superuser privileges). "
            "Continuing — extensions may already exist."
        )

    # Step 2: Ensure schemas exist
    try:
        await _ensure_schemas(engine)
    except Exception:
        logger.warning(
            "Could not create schemas (may need CREATE ON DATABASE privilege). "
            "Continuing — schemas may already exist."
        )

    # Step 3: Run Alembic migrations
    _run_alembic_upgrade()

    logger.info("Database initialisation complete")
