"""Pydantic schemas for KMM API request/response models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class NodeStateResponse(BaseModel):
    """Single node state for API responses."""

    student_id: str
    node_id: str
    course_id: str
    current_state: str
    previous_state: str | None = None
    state_since: datetime
    attempt_count: int = 0
    last_quiz_score: int | None = None
    last_quiz_at: datetime | None = None
    next_retention_check: datetime | None = None
    retention_checks_passed: int = 0


class StudentMapResponse(BaseModel):
    """Full student knowledge map."""

    student_id: str
    course_id: str
    nodes: list[NodeStateResponse]


class TransitionLogResponse(BaseModel):
    """A single transition log entry."""

    id: int
    student_id: str
    node_id: str
    course_id: str
    previous_state: str
    new_state: str
    trigger_type: str
    triggered_by: str | None = None
    quiz_score: int | None = None
    motivation: str | None = None
    created_at: datetime


class MacroRollupResponse(BaseModel):
    """Macro-node rollup result."""

    macro_node_id: str
    worst_state: str
    total_micros: int
    micros_per_state: dict[str, int]


class ClassNodeSummaryResponse(BaseModel):
    """Per-node summary for class heatmap."""

    node_id: str
    counts_per_state: dict[str, int]
    total_students: int


class ClassHeatmapResponse(BaseModel):
    """Class-level heatmap."""

    course_id: str
    node_summaries: list[ClassNodeSummaryResponse]


class RetentionCheckResponse(BaseModel):
    """A due retention check."""

    id: int
    student_id: str
    node_id: str
    course_id: str
    check_number: int
    scheduled_at: datetime
    status: str


class StudentNodeBrief(BaseModel):
    """Minimal node state for a student in the class-students view."""

    node_id: str
    label: str
    current_state: str


class ClassStudentOut(BaseModel):
    """A student row in the class-students-with-mastery endpoint."""

    student_id: str
    display_name: str
    nodes: list[StudentNodeBrief]


class ClassStudentsResponse(BaseModel):
    """Per-student mastery data for a class."""

    course_id: str
    students: list[ClassStudentOut]
    total: int


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class TransitionRequest(BaseModel):
    """Teacher override transition request (F11.12)."""

    target_state: str = Field(
        ...,
        description="Target mastery state",
    )
    motivation: str = Field(
        ...,
        min_length=20,
        description="Motivation for override (minimum 20 characters, CLAUDE.md governance)",
    )
