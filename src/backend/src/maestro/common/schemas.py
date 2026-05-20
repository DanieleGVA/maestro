"""Shared Pydantic schemas for MAESTRO API."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Meta(BaseModel):
    """Standard response metadata."""

    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ApiResponse(BaseModel, Generic[T]):
    """Standard API success envelope per IC-12 contract."""

    data: T
    meta: Meta


class ErrorDetail(BaseModel):
    """Error detail following IC-12 error response contract."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Standard API error envelope."""

    error: ErrorDetail
    meta: Meta


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response envelope."""

    data: list[T]
    meta: Meta
    total: int
    page: int
    page_size: int
    total_pages: int
