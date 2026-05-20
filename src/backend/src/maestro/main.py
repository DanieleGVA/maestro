"""FastAPI application entry point.

Registers all API routers, configures CORS, OTEL instrumentation,
and custom error handlers for MAESTRO exceptions.
"""

import logging
import os
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
from maestro.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown events."""
    from maestro.db.engine import engine
    from maestro.db.init_db import init_db

    # --- Startup ---
    logger.info("MAESTRO API starting up...")

    # 1. Initialise database (extensions, schemas, migrations)
    try:
        await init_db()
        logger.info("Database initialisation succeeded")
    except Exception:
        logger.exception("Database initialisation failed — service may be degraded")

    # 2. Optionally seed demo data (dev/staging only)
    seed_demo = os.environ.get("MAESTRO_SEED_DEMO", "false").lower() in ("true", "1", "yes")
    if seed_demo:
        try:
            from maestro.db.engine import async_session_factory
            from maestro.db.seed import seed_demo_data

            async with async_session_factory() as session:
                await seed_demo_data(session)
            logger.info("Demo data seeded successfully")
        except Exception:
            logger.exception("Demo data seeding failed — continuing without seed data")

    logger.info("MAESTRO API ready to serve requests")

    yield

    # --- Shutdown ---
    logger.info("MAESTRO API shutting down...")
    await engine.dispose()
    logger.info("Database engine disposed")


app = FastAPI(
    title="MAESTRO API",
    version="0.1.0",
    description="Personalised Learning Companion for IT Students",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Add security response headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# ---------------------------------------------------------------------------
# OpenTelemetry instrumentation
# ---------------------------------------------------------------------------

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app)
except Exception:
    # OTEL instrumentation is optional; don't fail startup if unavailable
    pass


# ---------------------------------------------------------------------------
# Error handlers for custom exceptions
# ---------------------------------------------------------------------------

_ERROR_STATUS_MAP = {
    NotFoundError: 404,
    ForbiddenError: 403,
    ConsentRequiredError: 403,
    TransitionIllegalError: 422,
    SafeguardingBlockedError: 422,
    OverrideMotivationError: 422,
    LLMUnavailableError: 503,
}


@app.exception_handler(MaestroError)
async def maestro_error_handler(request: Request, exc: MaestroError) -> JSONResponse:
    """Handle all MAESTRO custom exceptions with the IC-12 error envelope."""
    status_code = _ERROR_STATUS_MAP.get(type(exc), 500)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.detail,
            },
            "meta": {
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        },
    )


# ---------------------------------------------------------------------------
# Register API routers
# ---------------------------------------------------------------------------

from maestro.api.v1.health import router as health_router
from maestro.api.v1.students import router as students_router
from maestro.api.v1.lessons import router as lessons_router
from maestro.api.v1.sessions import router as sessions_router
from maestro.api.v1.quizzes import router as quizzes_router
from maestro.api.v1.classes import router as classes_router
from maestro.kg.router import router as kg_router
from maestro.kmm.router import router as kmm_router
from maestro.content.router import router as content_router

app.include_router(health_router)
app.include_router(students_router, prefix="/api/v1")
app.include_router(lessons_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(quizzes_router, prefix="/api/v1")
app.include_router(classes_router, prefix="/api/v1")
app.include_router(kg_router)
app.include_router(kmm_router, prefix="/api/v1")
app.include_router(content_router)
