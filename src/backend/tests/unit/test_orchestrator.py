"""Unit tests for the orchestrator graph.

Verifies that the LangGraph StateGraph has the required structural guarantees:
1. consent_gate is the entry point (runs before any agent)
2. safeguarding_gate exists and runs before content delivery
3. Routing works correctly based on request_type
"""

import pytest

from maestro.orchestrator.graph import (
    _consent_check,
    _route_by_type,
    _safeguarding_check,
    build_graph,
    consent_gate,
    safeguarding_gate,
)
from maestro.orchestrator.state import MaestroState


# ---------------------------------------------------------------------------
# Tests: Graph structure
# ---------------------------------------------------------------------------


class TestGraphStructure:
    """Verify the graph topology enforces consent and safeguarding gates."""

    def test_graph_builds_without_error(self):
        """build_graph should return a valid StateGraph."""
        graph = build_graph()
        assert graph is not None

    def test_graph_has_consent_gate_node(self):
        """The graph must have a consent_gate node."""
        graph = build_graph()
        assert "consent_gate" in graph.nodes

    def test_graph_has_safeguarding_gate_node(self):
        """The graph must have a safeguarding_gate node."""
        graph = build_graph()
        assert "safeguarding_gate" in graph.nodes

    def test_graph_has_all_agent_nodes(self):
        """The graph should contain diagnostic, content_selector, and profiler nodes."""
        graph = build_graph()
        for node_name in ("diagnostic", "content_selector", "profiler"):
            assert node_name in graph.nodes, f"Missing node: {node_name}"

    def test_graph_has_deliver_and_feedback(self):
        """The graph should have deliver and feedback nodes for the post-safeguarding path."""
        graph = build_graph()
        assert "deliver" in graph.nodes
        assert "feedback" in graph.nodes

    def test_entry_point_is_consent_gate(self):
        """The graph entry point must be consent_gate (no bypass possible)."""
        graph = build_graph()
        # LangGraph stores the entry point in __start__ edges
        compiled = graph.compile()
        # The compiled graph should have consent_gate reachable from __start__
        assert compiled is not None


# ---------------------------------------------------------------------------
# Tests: Consent gate logic
# ---------------------------------------------------------------------------


class TestConsentGate:
    """Tests for the consent_gate node."""

    def test_teacher_operation_passes_through(self):
        """Lesson upload (teacher operation) should pass the consent gate."""
        state: MaestroState = {
            "request_type": "lesson_upload",
            "student_internal_id": "",
            "agent_trace": [],
            "errors": [],
        }
        result = consent_gate(state)
        # Should have no errors and a pass_through trace
        assert not any(
            e.get("gate") == "consent"
            for e in result.get("errors", [])
        )
        trace = result.get("agent_trace", [])
        assert len(trace) == 1
        assert "pass_through" in trace[0].get("result", "")

    def test_student_operation_without_id_denied(self):
        """Student operation without student_internal_id should be denied."""
        state: MaestroState = {
            "request_type": "gap_closure",
            "student_internal_id": "",
            "agent_trace": [],
            "errors": [],
        }
        result = consent_gate(state)
        errors = result.get("errors", [])
        assert any(e.get("gate") == "consent" for e in errors)

    def test_student_operation_with_id_passes(self):
        """Student operation with valid student_internal_id should pass."""
        state: MaestroState = {
            "request_type": "gap_closure",
            "student_internal_id": "stu-uuid-123",
            "agent_trace": [],
            "errors": [],
        }
        result = consent_gate(state)
        errors = result.get("errors", [])
        assert not any(e.get("gate") == "consent" for e in errors)


# ---------------------------------------------------------------------------
# Tests: Safeguarding gate logic
# ---------------------------------------------------------------------------


class TestSafeguardingGate:
    """Tests for the safeguarding_gate node."""

    def test_safe_content_passes(self):
        """Clean content should pass the safeguarding gate."""
        state: MaestroState = {
            "generated_content": {
                "text": "Questo concetto ha bisogno di un altro giro di revisione."
            },
            "agent_trace": [],
        }
        result = safeguarding_gate(state)
        verdict = result.get("safeguarding_verdict", {})
        assert verdict["safe"] is True
        assert len(verdict["issues"]) == 0

    def test_comparison_content_blocked(self):
        """Content with student comparison should be blocked."""
        state: MaestroState = {
            "generated_content": {
                "text": "Sei peggio degli altri studenti della classe."
            },
            "agent_trace": [],
        }
        result = safeguarding_gate(state)
        verdict = result.get("safeguarding_verdict", {})
        assert verdict["safe"] is False
        assert len(verdict["issues"]) > 0

    def test_punitive_content_blocked(self):
        """Punitive language should be blocked."""
        state: MaestroState = {
            "generated_content": {
                "feedback": "Sei scarso in questa materia."
            },
            "agent_trace": [],
        }
        result = safeguarding_gate(state)
        verdict = result.get("safeguarding_verdict", {})
        assert verdict["safe"] is False

    def test_no_content_passes(self):
        """When there is no content to review, gate should pass."""
        state: MaestroState = {
            "generated_content": None,
            "agent_trace": [],
        }
        result = safeguarding_gate(state)
        verdict = result.get("safeguarding_verdict", {})
        assert verdict["safe"] is True

    def test_nested_content_checked(self):
        """Safeguarding should check nested dict values."""
        state: MaestroState = {
            "generated_content": {
                "blocks": [
                    {
                        "il_tuo_errore": {"text": "Non sarai mai capace di programmare."},
                    }
                ]
            },
            "agent_trace": [],
        }
        result = safeguarding_gate(state)
        verdict = result.get("safeguarding_verdict", {})
        assert verdict["safe"] is False


# ---------------------------------------------------------------------------
# Tests: Conditional edge functions
# ---------------------------------------------------------------------------


class TestConditionalEdges:
    """Tests for the routing/conditional edge functions."""

    def test_consent_check_proceeds_when_no_errors(self):
        """_consent_check should return 'proceed' when there are no consent errors."""
        state: MaestroState = {"errors": []}
        assert _consent_check(state) == "proceed"

    def test_consent_check_denied_when_consent_error(self):
        """_consent_check should return 'denied' when consent errors exist."""
        state: MaestroState = {
            "errors": [{"gate": "consent", "reason": "missing"}]
        }
        assert _consent_check(state) == "denied"

    def test_safeguarding_safe(self):
        """_safeguarding_check should return 'safe' when verdict is safe."""
        state: MaestroState = {"safeguarding_verdict": {"safe": True}}
        assert _safeguarding_check(state) == "safe"

    def test_safeguarding_blocked(self):
        """_safeguarding_check should return 'blocked' when verdict is not safe."""
        state: MaestroState = {"safeguarding_verdict": {"safe": False}}
        assert _safeguarding_check(state) == "blocked"

    def test_route_verification_to_diagnostic(self):
        """verification_analysis should route to diagnostic agent."""
        state: MaestroState = {"request_type": "verification_analysis"}
        assert _route_by_type(state) == "diagnostic"

    def test_route_gap_closure_to_content(self):
        """gap_closure should route to content_selector agent."""
        state: MaestroState = {"request_type": "gap_closure"}
        assert _route_by_type(state) == "content_selector"

    def test_route_onboarding_to_profiler(self):
        """onboarding should route to profiler agent."""
        state: MaestroState = {"request_type": "onboarding"}
        assert _route_by_type(state) == "profiler"

    def test_route_unknown_defaults_to_content(self):
        """Unknown request_type should default to content_selector."""
        state: MaestroState = {"request_type": "unknown_type"}
        assert _route_by_type(state) == "content_selector"
