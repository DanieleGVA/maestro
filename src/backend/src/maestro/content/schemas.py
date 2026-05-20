"""Pydantic schemas for content generation request/response."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------
class TargetNode(BaseModel):
    node_id: str
    node_type: Literal["macro", "micro"] = "micro"
    current_state: str
    label_it: str = ""
    error_description: str | None = None


class ContentAdaptationProfile(BaseModel):
    visuale: float = Field(default=0.2, ge=0.0, le=1.0)
    audio: float = Field(default=0.2, ge=0.0, le=1.0)
    pratico: float = Field(default=0.2, ge=0.0, le=1.0)
    lettura: float = Field(default=0.2, ge=0.0, le=1.0)
    dialogo: float = Field(default=0.2, ge=0.0, le=1.0)
    tone: Literal["confidenziale", "neutro", "formale"] = "neutro"
    length: Literal["sintesi", "approfondimento"] = "sintesi"


class ContentGenerateRequest(BaseModel):
    """POST /api/v1/content/generate"""

    request_type: Literal[
        "review_document", "gap_closure", "quiz_generation", "retention_check"
    ]
    student_pseudo_id: str
    course_id: str
    target_nodes: list[TargetNode]
    content_profile: ContentAdaptationProfile = ContentAdaptationProfile()
    attempt_number: int = Field(default=1, ge=1)


class QuizGenerateRequest(BaseModel):
    """POST /api/v1/content/quiz/generate"""

    student_pseudo_id: str
    course_id: str
    node_id: str
    node_label: str = ""
    purpose: Literal["closure", "retention"] = "closure"
    difficulty_level: str = "remember_understand"
    num_questions: int = Field(default=5, ge=1, le=20)
    current_state: str = "in_recupero"


class QuizSubmitRequest(BaseModel):
    """POST /api/v1/content/quiz/{id}/submit"""

    student_id: str
    answers: list[dict] = Field(min_length=1, max_length=20)
    total_time_ms: int = Field(ge=0, le=3600000)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class ContentMetadataOut(BaseModel):
    model_id: str
    prompt_template_id: str
    prompt_template_version: int
    prompt_hash: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cache_hit: bool
    generated_at: datetime


class ContentOut(BaseModel):
    id: str
    request_id: str
    content_type: str
    content: dict
    metadata: ContentMetadataOut
    model_config = {"from_attributes": True}


class QuizQuestionOut(BaseModel):
    id: str
    question_index: int
    question_type: str
    question_text: str
    options: dict | None = None
    bloom_level: str | None = None
    model_config = {"from_attributes": True}


class QuizOut(BaseModel):
    id: str
    node_id: str
    purpose: str
    difficulty_level: str
    questions: list[QuizQuestionOut]
    created_at: datetime
    model_config = {"from_attributes": True}


class QuizResultOut(BaseModel):
    quiz_id: str
    score: int
    total_questions: int
    correct_count: int
    per_question: list[dict]
