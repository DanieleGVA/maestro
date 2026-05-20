"""Pydantic models for LLM requests, responses, and audit entries."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    """Request to the LLM Gateway (IC-11)."""

    agent_name: str
    model_preference: Literal["quality", "cost_optimized"] = "quality"
    prompt_template_id: str
    prompt_template_version: int = 1
    system_prompt: str
    context_block: str
    task_block: str
    max_tokens: int = 2000
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    response_format: Literal["json", "text"] = "json"
    correlation_id: str


class LLMResponse(BaseModel):
    """Response from the LLM Gateway (IC-11)."""

    content: str
    model_id: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cache_hit: bool = False
    prompt_hash: str


class LLMAuditEntry(BaseModel):
    """Audit entry for a single LLM call (audit.llm_audit_log)."""

    request_id: str
    agent_name: str
    model_id: str
    prompt_hash: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cache_hit: bool = False
    created_at: datetime | None = None
