"""PostgreSQL-backed checkpointer for LangGraph durable execution.

Every node execution persists a checkpoint to PostgreSQL, providing audit trail,
resumability, and replayability per HLD-001 Section 2.4.
"""

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from maestro.config import settings


def _get_sync_database_url() -> str:
    """Convert the asyncpg URL to a psycopg-compatible URL for the checkpointer.

    LangGraph's PostgresSaver uses psycopg (sync driver) internally,
    so we need the standard postgresql:// scheme.
    """
    url = settings.database_url
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


async def create_checkpointer() -> AsyncPostgresSaver:
    """Create and set up the PostgreSQL checkpointer.

    This should be called during application startup (lifespan).
    The checkpointer creates its tables if they don't exist.
    """
    conn_string = _get_sync_database_url()
    checkpointer = AsyncPostgresSaver.from_conn_string(conn_string)
    await checkpointer.setup()
    return checkpointer
