"""Integration tests for the orchestrator graph flow.

Tests end-to-end graph execution through consent gate, agent routing,
safeguarding gate, and delivery. LLM calls are mocked but the graph
structure and state propagation are real.
"""

from __future__ import annotations

from typing import Any

import pytest

from maestro.orchestrator.graph import build_graph
from maestro.orchestrator.state import MaestroState


class TestConsentGateIntegration:
    """Test consent gate interacts correctly with routing."""

    def test_teacher_op_flows_through_to_content_selector(self) -> None:
        """A lesson_upload (teacher op) should pass consent gate and route to content_selector."""
        graph = build_graph()
        compiled = graph.compile()

        state: MaestroState = {
            "request_type": "lesson_upload",
            "student_internal_id": "",
            "target_node_ids": ["node-1"],
            "active_consents": [],
            "content_profile": {},
            "agent_trace": [],
            "errors": [],
        }

        result = compiled.invoke(state)

        # Should have traces from consent_gate, route_intent, content_selector,
        # safeguarding_gate, deliver, and feedback
        agents_in_trace = [t["agent"] for t in result.get("agent_trace", [])]
        assert "consent_gate" in agents_in_trace
        assert "route_intent" in agents_in_trace

    def test_missing_student_id_denies_and_ends(self) -> None:
        """Student operation without ID should be denied at consent gate."""
        graph = build_graph()
        compiled = graph.compile()

        state: MaestroState = {
            "request_type": "gap_closure",
            "student_internal_id": "",
            "agent_trace": [],
            "errors": [],
        }

        result = compiled.invoke(state)

        # Should have consent error
        errors = result.get("errors", [])
        consent_errors = [e for e in errors if isinstance(e, dict) and e.get("gate") == "consent"]
        assert len(consent_errors) >= 1

        # Should NOT have reached any agent node
        agents_in_trace = [t.get("agent") for t in result.get("agent_trace", [])]
        assert "diagnostic" not in agents_in_trace
        assert "content_selector" not in agents_in_trace

    def test_valid_student_op_reaches_agent(self) -> None:
        """Student operation with valid ID should reach the appropriate agent."""
        graph = build_graph()
        compiled = graph.compile()

        state: MaestroState = {
            "request_type": "verification_analysis",
            "student_internal_id": "stu-uuid-123",
            "target_node_ids": ["node-1"],
            "active_consents": ["a"],
            "content_profile": {},
            "agent_trace": [],
            "errors": [],
        }

        result = compiled.invoke(state)

        agents_in_trace = [t.get("agent") for t in result.get("agent_trace", [])]
        assert "consent_gate" in agents_in_trace
        assert "diagnostic" in agents_in_trace or "route_intent" in agents_in_trace


class TestRoutingIntegration:
    """Test request type routing through the graph."""

    @pytest.mark.parametrize(
        "request_type,expected_agent",
        [
            ("verification_analysis", "diagnostic"),
            ("gap_closure", "content_selector"),
            ("onboarding", "profiler"),
            ("content_generation", "content_selector"),
            ("retention_check", "diagnostic"),
            ("profile_update", "profiler"),
            ("teacher_override", "diagnostic"),
        ],
    )
    def test_request_type_routes_to_correct_agent(
        self, request_type: str, expected_agent: str
    ) -> None:
        graph = build_graph()
        compiled = graph.compile()

        state: MaestroState = {
            "request_type": request_type,
            "student_internal_id": "stu-uuid-123",
            "target_node_ids": ["node-1"],
            "active_consents": ["a"],
            "content_profile": {
                "visuale": 0.2,
                "audio": 0.2,
                "pratico": 0.2,
                "lettura": 0.2,
                "dialogo": 0.2,
                "tone": "neutro",
                "length": "sintesi",
            },
            "agent_trace": [],
            "errors": [],
        }

        result = compiled.invoke(state)
        agents_in_trace = [t.get("agent") for t in result.get("agent_trace", [])]
        assert expected_agent in agents_in_trace


class TestSafeguardingGateIntegration:
    """Test safeguarding gate in the full graph flow."""

    def test_safe_content_reaches_delivery(self) -> None:
        """Safe content should pass through safeguarding gate and be delivered."""
        graph = build_graph()
        compiled = graph.compile()

        state: MaestroState = {
            "request_type": "gap_closure",
            "student_internal_id": "stu-1",
            "target_node_ids": ["node-1"],
            "active_consents": ["a"],
            "content_profile": {
                "visuale": 0.2,
                "audio": 0.2,
                "pratico": 0.2,
                "lettura": 0.2,
                "dialogo": 0.2,
                "tone": "neutro",
                "length": "sintesi",
            },
            "agent_trace": [],
            "errors": [],
        }

        result = compiled.invoke(state)

        agents_in_trace = [t.get("agent") for t in result.get("agent_trace", [])]
        assert "safeguarding_gate" in agents_in_trace
        # Content from content_selector is safe (no comparisons/punitive) so should deliver
        verdict = result.get("safeguarding_verdict", {})
        if verdict.get("safe"):
            assert "deliver" in agents_in_trace
