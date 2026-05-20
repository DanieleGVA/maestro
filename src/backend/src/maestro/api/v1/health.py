"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Basic health check. Returns 200 if the service is running."""
    return {"status": "ok"}
