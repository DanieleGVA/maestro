"""Pydantic schemas for safeguarding API responses."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class WellbeingAlertOut(BaseModel):
    """Wellbeing alert response for teacher dashboard."""

    id: str
    student_id: str
    detected_phrase: str
    category: str
    urgency: Literal["low", "medium", "high", "critical"]
    context: str | None = None
    notified_teacher: bool
    notified_referent: bool
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SafeguardingVerdictOut(BaseModel):
    """Safeguarding verdict for audit trail."""

    id: str
    request_id: str
    content_type: str
    attempt_number: int
    verdict: Literal["safe", "blocked", "warn", "alert"]
    violations: dict | None = None
    check_method: str
    latency_ms: int
    fallback_served: bool
    created_at: datetime

    model_config = {"from_attributes": True}
