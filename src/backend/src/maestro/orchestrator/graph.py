"""Main LangGraph StateGraph for the MAESTRO orchestrator.

This module defines the orchestration graph per HLD-001 Section 2.2 and ADR-003.
The graph enforces two structural guarantees:
  1. consent_gate runs BEFORE any agent operates on student data
  2. safeguarding_gate runs BEFORE any content reaches a student

These are enforced by the graph topology (absence of bypass edges),
not by agent-level discipline.
"""

from datetime import datetime, timezone
from typing import Any

from langgraph.graph import END, StateGraph

from maestro.orchestrator.state import MaestroState


# ---------------------------------------------------------------------------
# Gate nodes
# ---------------------------------------------------------------------------


def consent_gate(state: MaestroState) -> dict[str, Any]:
    """Verify that required consents are present for the request type.

    For MVP: verify that the student exists and is active. Full consent
    verification (5 granular categories) is deferred to V1.

    This node is the FIRST node in every flow. It populates identity fields
    in the state and sets active_consents.
    """
    request_type = state.get("request_type", "")
    student_id = state.get("student_internal_id", "")

    trace_entry = {
        "agent": "consent_gate",
        "action": "verify_consent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_type": request_type,
        "student_id": student_id,
    }

    # Teacher-only operations bypass student consent checks
    if request_type in ("lesson_upload", "course_setup"):
        return {
            "agent_trace": [trace_entry | {"result": "pass_through_teacher_op"}],
        }

    # MVP: student must have an internal ID set (means they exist and are active)
    if not student_id:
        return {
            "errors": [{"gate": "consent", "reason": "student_internal_id mancante"}],
            "agent_trace": [trace_entry | {"result": "denied_no_student"}],
        }

    return {
        "agent_trace": [trace_entry | {"result": "passed"}],
    }


def safeguarding_gate(state: MaestroState) -> dict[str, Any]:
    """Mandatory safeguarding check on all generated content before delivery.

    Runs the deterministic regex check (MVP). LLM-based safeguarding is V1.
    This node MUST execute between content generation and student delivery.
    """
    import re

    content = state.get("generated_content")
    trace_entry = {
        "agent": "safeguarding_gate",
        "action": "content_review",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if content is None:
        return {
            "safeguarding_verdict": {"safe": True, "issues": [], "reason": "no_content"},
            "agent_trace": [trace_entry | {"result": "no_content_to_review"}],
        }

    # Extract text content for review
    text_to_check = _extract_text(content)

    # MVP safeguarding: deterministic regex patterns (phase3-compliance-mvp.md)
    blocked_patterns = [
        r"(?i)(peggio|meglio) (di|degli altri|dei compagni|della classe)",
        r"(?i)(sei (scarso|incapace|lento|stupido))",
        r"(?i)(non (sei|sarai) (mai|capace))",
        r"(?i)(devi vergognarti|che figuraccia)",
        r"(?i)(tutti.*tranne te|solo tu)",
    ]

    violations: list[str] = []
    for pattern in blocked_patterns:
        if re.search(pattern, text_to_check):
            violations.append(pattern)

    safe = len(violations) == 0
    verdict = {
        "safe": safe,
        "issues": [
            {"category": "safeguarding_pattern", "severity": "BLOCK", "pattern": v}
            for v in violations
        ],
    }

    return {
        "safeguarding_verdict": verdict,
        "agent_trace": [
            trace_entry | {"result": "safe" if safe else "blocked", "violations": len(violations)}
        ],
    }


def _extract_text(content: dict[str, Any]) -> str:
    """Recursively extract all string values from a content dict for safeguarding review."""
    parts: list[str] = []
    for value in content.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, dict):
            parts.append(_extract_text(value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    parts.append(_extract_text(item))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------


def route_intent(state: MaestroState) -> dict[str, Any]:
    """Classify the incoming request and prepare routing.

    Per HLD-001: request_type is explicit in the API contract, not inferred.
    This node simply validates and records the routing decision.
    """
    request_type = state.get("request_type", "unknown")
    return {
        "agent_trace": [
            {
                "agent": "route_intent",
                "action": "classify",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_type": request_type,
            }
        ],
    }


# ---------------------------------------------------------------------------
# Stub nodes for agent integration
# ---------------------------------------------------------------------------


def diagnostic_node(state: MaestroState) -> dict[str, Any]:
    """Diagnostic Agent node — analyses verification results, maps errors to KG nodes."""
    from maestro.agents.diagnostic import run_diagnostic

    return run_diagnostic(state)


def content_selector_node(state: MaestroState) -> dict[str, Any]:
    """Content Selection Agent node — selects content for the student's state."""
    from maestro.agents.content_selector import run_content_selector

    return run_content_selector(state)


def profiler_node(state: MaestroState) -> dict[str, Any]:
    """Profiler Agent node — manages content adaptation profile."""
    from maestro.agents.profiler import run_profiler

    return run_profiler(state)


def deliver_node(state: MaestroState) -> dict[str, Any]:
    """Delivery node — sends content to the student after safeguarding approval."""
    verdict = state.get("safeguarding_verdict", {})
    if not verdict.get("safe", False):
        return {
            "errors": [{"gate": "delivery", "reason": "contenuto bloccato da safeguarding"}],
            "agent_trace": [
                {
                    "agent": "deliver",
                    "action": "blocked",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }
    return {
        "agent_trace": [
            {
                "agent": "deliver",
                "action": "delivered",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ],
    }


def feedback_node(state: MaestroState) -> dict[str, Any]:
    """Feedback Loop node — updates profile, KMM, KG after content delivery."""
    return {
        "agent_trace": [
            {
                "agent": "feedback_loop",
                "action": "process",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ],
    }


# ---------------------------------------------------------------------------
# Conditional edges
# ---------------------------------------------------------------------------


def _consent_check(state: MaestroState) -> str:
    """After consent_gate: route to intent or deny."""
    errors = state.get("errors", [])
    consent_errors = [e for e in errors if isinstance(e, dict) and e.get("gate") == "consent"]
    if consent_errors:
        return "denied"
    return "proceed"


def _safeguarding_check(state: MaestroState) -> str:
    """After safeguarding_gate: route to delivery or block."""
    verdict = state.get("safeguarding_verdict", {})
    if verdict.get("safe", False):
        return "safe"
    return "blocked"


def _route_by_type(state: MaestroState) -> str:
    """Route to the appropriate agent based on request_type."""
    request_type = state.get("request_type", "")
    routing_map = {
        "lesson_upload": "content_selector",
        "verification_analysis": "diagnostic",
        "gap_closure": "content_selector",
        "onboarding": "profiler",
        "content_generation": "content_selector",
        "retention_check": "diagnostic",
        "profile_update": "profiler",
        "teacher_override": "diagnostic",
        "course_setup": "content_selector",
    }
    return routing_map.get(request_type, "content_selector")


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def build_graph() -> StateGraph:
    """Build the MAESTRO orchestrator StateGraph.

    Graph topology (simplified):

        consent_gate -> route_intent -> [agent nodes] -> safeguarding_gate -> deliver -> feedback -> END
                |                                                   |
                +-> END (denied)                                    +-> END (blocked)

    This topology structurally guarantees:
    - No agent executes without consent verification
    - No content reaches students without safeguarding review
    """
    graph = StateGraph(MaestroState)

    # Add nodes
    graph.add_node("consent_gate", consent_gate)
    graph.add_node("route_intent", route_intent)
    graph.add_node("diagnostic", diagnostic_node)
    graph.add_node("content_selector", content_selector_node)
    graph.add_node("profiler", profiler_node)
    graph.add_node("safeguarding_gate", safeguarding_gate)
    graph.add_node("deliver", deliver_node)
    graph.add_node("feedback", feedback_node)

    # Entry point
    graph.set_entry_point("consent_gate")

    # consent_gate -> proceed or denied
    graph.add_conditional_edges(
        "consent_gate",
        _consent_check,
        {"proceed": "route_intent", "denied": END},
    )

    # route_intent -> agent based on request_type
    graph.add_conditional_edges(
        "route_intent",
        _route_by_type,
        {
            "diagnostic": "diagnostic",
            "content_selector": "content_selector",
            "profiler": "profiler",
        },
    )

    # All agents -> safeguarding_gate
    graph.add_edge("diagnostic", "safeguarding_gate")
    graph.add_edge("content_selector", "safeguarding_gate")
    graph.add_edge("profiler", "safeguarding_gate")

    # safeguarding_gate -> deliver or END (blocked)
    graph.add_conditional_edges(
        "safeguarding_gate",
        _safeguarding_check,
        {"safe": "deliver", "blocked": END},
    )

    # deliver -> feedback -> END
    graph.add_edge("deliver", "feedback")
    graph.add_edge("feedback", END)

    return graph
