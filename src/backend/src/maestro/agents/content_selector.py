"""Content Selection Agent — selects appropriate content for the student's mastery state.

Per HLD-001 Section 3.7: coordinates content generation across channels based on
the content-adaptation profile. Enforces source priority (teacher > textbook > external)
and minimum modality diversity.

MVP: text channel only. Profile-adapted content when consent (a) is active,
otherwise uniform profile (20% each dimension).
"""

from datetime import datetime, timezone
from typing import Any

from maestro.agents.base import AgentNode
from maestro.orchestrator.state import MaestroState


class ContentSelectorAgent(AgentNode):
    """Select and coordinate content generation for a student."""

    agent_name = "content_selector_agent"

    def execute(self, state: MaestroState) -> dict[str, Any]:
        """Determine which content to generate based on state and profile."""
        request_type = state.get("request_type", "")
        target_nodes = state.get("target_node_ids", [])
        consents = state.get("active_consents", [])
        profile = state.get("content_profile", {})

        # Determine if we can use profile adaptation
        use_profile = "a" in consents and bool(profile)

        # Select content channel (MVP: always text)
        channel = "text"

        # Resolve profile: adapted or uniform
        effective_profile = profile if use_profile else _uniform_profile()

        generated_content = {
            "channel": channel,
            "request_type": request_type,
            "target_nodes": target_nodes,
            "profile_used": effective_profile,
            "profile_adapted": use_profile,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content_payload": {
                "type": "placeholder",
                "message": (
                    "Content generation placeholder. "
                    "Actual LLM-generated content is produced by the Text Agent "
                    "via the LLMGateway (not implemented in this agent)."
                ),
            },
        }

        return {
            "generated_content": generated_content,
        }


def _uniform_profile() -> dict[str, Any]:
    """Return the uniform content adaptation profile (consent (a) denied)."""
    return {
        "visuale": 0.2,
        "audio": 0.2,
        "pratico": 0.2,
        "lettura": 0.2,
        "dialogo": 0.2,
        "tone": "neutro",
        "length": "medio",
    }


# Module-level function for graph node integration
_agent = ContentSelectorAgent()


def run_content_selector(state: MaestroState) -> dict[str, Any]:
    """Graph node entry point for the Content Selection Agent."""
    return _agent(state)
