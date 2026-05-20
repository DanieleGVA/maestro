"""Base interface for MAESTRO agent nodes.

Every agent is a pure function: it receives MaestroState and returns a dict
with only the keys it modifies. LangGraph merges the returned dict into the state.

This module provides the AgentNode base class with standard audit logging.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from maestro.orchestrator.state import MaestroState


class AgentNode(ABC):
    """Base class for MAESTRO agent nodes.

    Subclasses implement `execute()` which contains the agent logic.
    The `__call__` method wraps execution with audit trace logging.
    """

    agent_name: str = "unnamed_agent"

    def __call__(self, state: MaestroState) -> dict[str, Any]:
        """Invoke the agent, wrapping execution with audit trace."""
        start = datetime.now(timezone.utc)
        try:
            result = self.execute(state)
        except Exception as exc:
            return {
                "errors": [
                    {
                        "agent": self.agent_name,
                        "error": str(exc),
                        "timestamp": start.isoformat(),
                    }
                ],
                "agent_trace": [
                    {
                        "agent": self.agent_name,
                        "action": "error",
                        "timestamp": start.isoformat(),
                        "error": str(exc),
                    }
                ],
            }

        end = datetime.now(timezone.utc)
        trace_entry = {
            "agent": self.agent_name,
            "action": "execute",
            "timestamp": start.isoformat(),
            "duration_ms": int((end - start).total_seconds() * 1000),
        }

        # Ensure agent_trace is always appended
        if "agent_trace" not in result:
            result["agent_trace"] = []
        result["agent_trace"].append(trace_entry)

        return result

    @abstractmethod
    def execute(self, state: MaestroState) -> dict[str, Any]:
        """Execute agent logic. Return dict with ONLY the state keys to update."""
        ...
