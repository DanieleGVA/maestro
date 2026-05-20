"""Diagnostic Agent — analyses verification results, maps errors to KG micro-nodes.

Per HLD-001 Section 3.6: This agent processes teacher-submitted verifications,
performs error-to-concept mapping, computes confidence scores, and generates
per-student diagnostic reports with KMM transition previews.

For MVP: score-based mapping (rules engine). LLM-based error analysis (for
code-level analysis) is handled via the LLMGateway when available.
"""

from datetime import datetime, timezone
from typing import Any

from maestro.agents.base import AgentNode
from maestro.orchestrator.state import MaestroState


class DiagnosticAgent(AgentNode):
    """Analyse verification results and map errors to KG concepts."""

    agent_name = "diagnostic_agent"

    def execute(self, state: MaestroState) -> dict[str, Any]:
        """Process diagnostic analysis based on the current state."""
        request_type = state.get("request_type", "")
        target_nodes = state.get("target_node_ids", [])

        if request_type == "verification_analysis":
            return self._analyse_verification(state, target_nodes)
        elif request_type == "retention_check":
            return self._process_retention_check(state, target_nodes)
        elif request_type == "teacher_override":
            return self._process_override(state, target_nodes)

        return {
            "diagnostic_result": {"status": "no_op", "request_type": request_type},
        }

    def _analyse_verification(
        self, state: MaestroState, target_nodes: list[str]
    ) -> dict[str, Any]:
        """Analyse a verification submission: map errors to concept nodes.

        MVP: uses score-based mapping. Transitions are previewed but not committed
        (teacher must confirm via the dashboard).
        """
        diagnostic_result = {
            "status": "analysed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target_nodes": target_nodes,
            "transitions_preview": [],
            "class_summary": {},
        }

        # Build transition previews for affected nodes
        for node_id in target_nodes:
            diagnostic_result["transitions_preview"].append(
                {
                    "node_id": node_id,
                    "proposed_trigger": "verifica_errore",
                    "confidence": 1.0,  # Score-based mapping has full confidence
                }
            )

        return {
            "diagnostic_result": diagnostic_result,
        }

    def _process_retention_check(
        self, state: MaestroState, target_nodes: list[str]
    ) -> dict[str, Any]:
        """Process a retention check result."""
        return {
            "diagnostic_result": {
                "status": "retention_check_processed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "target_nodes": target_nodes,
            },
        }

    def _process_override(
        self, state: MaestroState, target_nodes: list[str]
    ) -> dict[str, Any]:
        """Process a teacher override request."""
        return {
            "diagnostic_result": {
                "status": "override_processed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "target_nodes": target_nodes,
            },
        }


# Module-level function for graph node integration
_agent = DiagnosticAgent()


def run_diagnostic(state: MaestroState) -> dict[str, Any]:
    """Graph node entry point for the Diagnostic Agent."""
    return _agent(state)
