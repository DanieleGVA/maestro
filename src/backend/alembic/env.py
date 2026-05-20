"""Alembic environment configuration for MAESTRO.

Imports all ORM models so that Base.metadata contains every table,
then runs migrations using the async engine from settings.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from maestro.config import settings

# Import Base and ALL models so that metadata is fully populated
from maestro.db.models import Base
import maestro.db.models.core  # noqa: F401 — School, Teacher, Student, Course, Enrolment
import maestro.db.models.audit  # noqa: F401 — AuditLog, LLMAuditLog, DeletionCertificate
import maestro.kmm.models  # noqa: F401 — StudentNodeState, StateTransitionLog, RetentionSchedule
import maestro.content.models  # noqa: F401 — GeneratedContent, Quiz, QuizQuestion, QuizResponse
import maestro.kg.models  # noqa: F401 — KGNode, KGEdge, KGNodeEmbedding, ConceptNodeLink, etc.

# Alembic Config object — provides access to values in alembic.ini
config = context.config

# Set the SQLAlchemy URL from our application settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging (if present)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL script output without connecting to the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations inside an existing connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations using an async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with an async engine."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
