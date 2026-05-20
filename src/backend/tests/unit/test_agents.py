"""Unit tests for agent base class and agent implementations."""

from datetime import datetime, timezone
from typing import Any

import pytest

from maestro.agents.base import AgentNode
from maestro.agents.content_selector import ContentSelectorAgent, run_content_selector
from maestro.agents.diagnostic import DiagnosticAgent, run_diagnostic
from maestro.agents.profiler import ProfilerAgent, run_profiler
from maestro.orchestrator.state import MaestroState


# ---------------------------------------------------------------------------
# Tests: AgentNode base class
# ---------------------------------------------------------------------------


class TestAgentNodeBase:
    """Tests for the AgentNode base class."""

    def test_agent_adds_trace_entry(self):
        """Calling an agent should add an agent_trace entry to the result."""

        class TestAgent(AgentNode):
            agent_name = "test_agent"

            def execute(self, state: MaestroState) -> dict[str, Any]:
                return {"diagnostic_result": {"test": True}}

        agent = TestAgent()
        result = agent({"agent_trace": [], "errors": []})

        assert "agent_trace" in result
        traces = result["agent_trace"]
        assert len(traces) >= 1
        assert traces[-1]["agent"] == "test_agent"
        assert "duration_ms" in traces[-1]

    def test_agent_handles_exception(self):
        """Agent exceptions should be caught and recorded in errors + trace."""

        class FailingAgent(AgentNode):
            agent_name = "failing_agent"

            def execute(self, state: MaestroState) -> dict[str, Any]:
                raise ValueError("Test failure")

        agent = FailingAgent()
        result = agent({"agent_trace": [], "errors": []})

        assert "errors" in result
        assert len(result["errors"]) == 1
        assert "Test failure" in result["errors"][0]["error"]
        assert result["agent_trace"][0]["agent"] == "failing_agent"
        assert result["agent_trace"][0]["action"] == "error"


# ---------------------------------------------------------------------------
# Tests: DiagnosticAgent
# ---------------------------------------------------------------------------


class TestDiagnosticAgent:
    """Tests for the Diagnostic Agent."""

    def test_verification_analysis(self):
        """Diagnostic agent should produce transition previews for verification analysis."""
        state: MaestroState = {
            "request_type": "verification_analysis",
            "target_node_ids": ["node-1", "node-2"],
            "agent_trace": [],
            "errors": [],
        }
        result = run_diagnostic(state)

        assert "diagnostic_result" in result
        diag = result["diagnostic_result"]
        assert diag["status"] == "analysed"
        assert len(diag["transitions_preview"]) == 2

    def test_retention_check(self):
        """Diagnostic agent should handle retention check requests."""
        state: MaestroState = {
            "request_type": "retention_check",
            "target_node_ids": ["node-3"],
            "agent_trace": [],
            "errors": [],
        }
        result = run_diagnostic(state)
        assert result["diagnostic_result"]["status"] == "retention_check_processed"

    def test_teacher_override(self):
        """Diagnostic agent should handle teacher override requests."""
        state: MaestroState = {
            "request_type": "teacher_override",
            "target_node_ids": ["node-4"],
            "agent_trace": [],
            "errors": [],
        }
        result = run_diagnostic(state)
        assert result["diagnostic_result"]["status"] == "override_processed"

    def test_unknown_request_type(self):
        """Diagnostic agent should handle unknown request types gracefully."""
        state: MaestroState = {
            "request_type": "unknown",
            "target_node_ids": [],
            "agent_trace": [],
            "errors": [],
        }
        result = run_diagnostic(state)
        assert result["diagnostic_result"]["status"] == "no_op"


# ---------------------------------------------------------------------------
# Tests: ContentSelectorAgent
# ---------------------------------------------------------------------------


class TestContentSelectorAgent:
    """Tests for the Content Selection Agent."""

    def test_selects_text_channel(self):
        """MVP: content selector should always use text channel."""
        state: MaestroState = {
            "request_type": "gap_closure",
            "target_node_ids": ["node-1"],
            "active_consents": ["a"],
            "content_profile": {
                "visuale": 0.3,
                "audio": 0.1,
                "pratico": 0.2,
                "lettura": 0.3,
                "dialogo": 0.1,
                "tone": "confidenziale",
                "length": "approfondimento",
            },
            "agent_trace": [],
            "errors": [],
        }
        result = run_content_selector(state)

        content = result["generated_content"]
        assert content["channel"] == "text"
        assert content["profile_adapted"] is True

    def test_uniform_profile_without_consent(self):
        """Without consent (a), content selector should use uniform profile."""
        state: MaestroState = {
            "request_type": "content_generation",
            "target_node_ids": ["node-1"],
            "active_consents": [],
            "content_profile": {},
            "agent_trace": [],
            "errors": [],
        }
        result = run_content_selector(state)

        content = result["generated_content"]
        assert content["profile_adapted"] is False
        profile = content["profile_used"]
        assert profile["visuale"] == 0.2
        assert profile["tone"] == "neutro"


# ---------------------------------------------------------------------------
# Tests: ProfilerAgent
# ---------------------------------------------------------------------------


class TestProfilerAgent:
    """Tests for the Profiler Agent."""

    def test_onboarding_with_consent(self):
        """Onboarding with consent (a) should prepare the onboarding quiz."""
        state: MaestroState = {
            "request_type": "onboarding",
            "active_consents": ["a"],
            "content_profile": {},
            "agent_trace": [],
            "errors": [],
        }
        result = run_profiler(state)

        assert "content_profile" in result
        assert "generated_content" in result
        assert result["generated_content"]["type"] == "onboarding_quiz"

    def test_onboarding_without_consent(self):
        """Onboarding without consent (a) should skip quiz and set uniform profile."""
        state: MaestroState = {
            "request_type": "onboarding",
            "active_consents": [],
            "content_profile": {},
            "agent_trace": [],
            "errors": [],
        }
        result = run_profiler(state)

        assert result["content_profile"]["visuale"] == 0.2
        assert result["generated_content"]["type"] == "onboarding_skipped"

    def test_profile_update_requires_consent(self):
        """Profile update without consent (a) should produce an error."""
        state: MaestroState = {
            "request_type": "profile_update",
            "active_consents": [],
            "content_profile": {},
            "agent_trace": [],
            "errors": [],
        }
        result = run_profiler(state)

        assert result["content_profile"]["visuale"] == 0.2
        errors = result.get("errors", [])
        assert any("consent_a_required" in str(e) for e in errors)

    def test_default_returns_existing_profile(self):
        """For non-onboarding/update, profiler should return existing profile."""
        existing_profile = {
            "visuale": 0.4,
            "audio": 0.1,
            "pratico": 0.1,
            "lettura": 0.3,
            "dialogo": 0.1,
            "tone": "confidenziale",
            "length": "sintesi",
        }
        state: MaestroState = {
            "request_type": "content_generation",
            "active_consents": ["a"],
            "content_profile": existing_profile,
            "agent_trace": [],
            "errors": [],
        }
        result = run_profiler(state)

        assert result["content_profile"] == existing_profile
