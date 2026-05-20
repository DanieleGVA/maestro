"""MaestroState: the shared state object that flows through the LangGraph StateGraph.

This is the canonical state schema per HLD-001 Section 2.3 and IC-01 contract.
Every agent node reads from and writes to this state. Agents return dicts with
ONLY the keys they modify; LangGraph merges them into the state.
"""

from datetime import datetime
from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph import add_messages


def _merge_lists(left: list[Any], right: list[Any]) -> list[Any]:
    """Reducer that appends right items to left (used for append-only fields)."""
    return left + right


class MaestroState(TypedDict, total=False):
    """Shared execution state for all LangGraph nodes.

    Fields marked with Annotated[..., _merge_lists] use LangGraph reducers
    so that each agent can append items without overwriting previous entries.
    """

    # --- Request context (set by Orchestrator at graph start) ---
    request_id: str
    request_type: Literal[
        "lesson_upload",
        "verification_analysis",
        "gap_closure",
        "onboarding",
        "content_generation",
        "retention_check",
        "profile_update",
        "teacher_override",
        "course_setup",
    ]
    timestamp: str  # ISO-8601

    # --- Identity (resolved by consent_gate node) ---
    student_pseudo_id: str
    student_internal_id: str  # NEVER sent to LLM
    course_id: str
    active_consents: list[str]  # Subset of ["a", "b", "c", "d", "e"]

    # --- KG context ---
    target_node_ids: list[str]
    kg_context: dict[str, Any]

    # --- Content adaptation profile (ADR-002) ---
    content_profile: dict[str, Any]

    # --- Agent outputs (accumulated during graph execution) ---
    diagnostic_result: dict[str, Any] | None
    generated_content: dict[str, Any] | None
    safeguarding_verdict: dict[str, Any] | None
    kmm_transitions: Annotated[list[dict[str, Any]], _merge_lists]
    feedback_actions: Annotated[list[dict[str, Any]], _merge_lists]

    # --- Audit (append-only) ---
    agent_trace: Annotated[list[dict[str, Any]], _merge_lists]
    llm_calls: Annotated[list[dict[str, Any]], _merge_lists]

    # --- Error handling ---
    errors: Annotated[list[dict[str, Any]], _merge_lists]
    fallback_activated: bool
