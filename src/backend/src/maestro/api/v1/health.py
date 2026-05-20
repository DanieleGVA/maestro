"""Health check endpoint with database and Redis connectivity verification."""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from maestro.config import settings

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


async def _check_database() -> dict[str, Any]:
    """Verify PostgreSQL connectivity with a simple SELECT 1."""
    from maestro.db.engine import engine

    start = time.monotonic()
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {"status": "ok", "latency_ms": latency_ms}
    except Exception as exc:
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        logger.warning("Database health check failed: %s", exc)
        return {"status": "error", "latency_ms": latency_ms, "error": str(exc)}


async def _check_redis() -> dict[str, Any]:
    """Verify Redis connectivity with a PING command."""
    start = time.monotonic()
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.redis_url, decode_responses=True)
        try:
            pong = await client.ping()
            latency_ms = round((time.monotonic() - start) * 1000, 1)
            if pong:
                return {"status": "ok", "latency_ms": latency_ms}
            return {"status": "error", "latency_ms": latency_ms, "error": "PING returned False"}
        finally:
            await client.aclose()
    except ImportError:
        return {"status": "unavailable", "error": "redis package not installed"}
    except Exception as exc:
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        logger.warning("Redis health check failed: %s", exc)
        return {"status": "error", "latency_ms": latency_ms, "error": str(exc)}


@router.get("/health")
async def health() -> dict[str, Any]:
    """Comprehensive health check.

    Returns 200 with per-service status. The overall ``status`` is "ok" only
    when all dependencies are reachable; otherwise it is "degraded".
    """
    db = await _check_database()
    redis = await _check_redis()

    all_ok = db["status"] == "ok" and redis["status"] == "ok"

    return {
        "status": "ok" if all_ok else "degraded",
        "version": "0.1.0",
        "services": {
            "database": db,
            "redis": redis,
        },
    }


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    """Kubernetes liveness probe. Always returns 200 if the process is running."""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness() -> dict[str, Any]:
    """Kubernetes readiness probe. Returns 200 only if the database is reachable."""
    db = await _check_database()
    if db["status"] != "ok":
        from fastapi.responses import JSONResponse

        return JSONResponse(  # type: ignore[return-value]
            status_code=503,
            content={"status": "not_ready", "database": db},
        )
    return {"status": "ready", "database": db}
