"""Student Profiler Agent — manages the content-adaptation profile.

Per HLD-001 Section 3.5 and ADR-002:
- Runs onboarding quiz to compute 5-dimension profile vector
- Provides manual override (F3.4)
- Returns uniform profile when consent (a) is denied

MVP: onboarding quiz + manual override. Behavioural evolution (F3.3) deferred to V1.

Terminology: the profile is NEVER called "learning style" in any interface.
Dimensions use content-format labels: Visuale, Audio, Pratico, Lettura, Dialogo.
"""

from datetime import datetime, timezone
from typing import Any

from maestro.agents.base import AgentNode
from maestro.orchestrator.state import MaestroState


class ProfilerAgent(AgentNode):
    """Manage the student's content-adaptation profile."""

    agent_name = "profiler_agent"

    def execute(self, state: MaestroState) -> dict[str, Any]:
        """Compute or return the content-adaptation profile."""
        request_type = state.get("request_type", "")
        consents = state.get("active_consents", [])

        if request_type == "onboarding":
            return self._handle_onboarding(state, consents)
        elif request_type == "profile_update":
            return self._handle_update(state, consents)

        # Default: return current or uniform profile
        return {
            "content_profile": state.get("content_profile") or _uniform_profile(),
        }

    def _handle_onboarding(
        self, state: MaestroState, consents: list[str]
    ) -> dict[str, Any]:
        """Handle student first activation: onboarding quiz or uniform profile."""
        if "a" not in consents:
            # Consent (a) denied: skip quiz, set uniform profile
            return {
                "content_profile": _uniform_profile(),
                "generated_content": {
                    "type": "onboarding_skipped",
                    "reason": "consent_a_denied",
                    "message": (
                        "Profilo uniforme impostato. "
                        "Puoi attivare la personalizzazione in qualsiasi momento."
                    ),
                },
            }

        # Consent (a) granted: initiate onboarding quiz
        # MVP: the quiz is delivered via the API; the actual profile computation
        # happens when quiz results are submitted. Here we prepare the initial state.
        return {
            "content_profile": _uniform_profile(),  # Start with uniform, refine after quiz
            "generated_content": {
                "type": "onboarding_quiz",
                "message": (
                    "Questo questionario ci aiuta a capire come preferisci "
                    "ricevere i contenuti. Non e' un giudizio sulle tue "
                    "capacita'. Puoi cambiarlo in qualsiasi momento."
                ),
            },
        }

    def _handle_update(
        self, state: MaestroState, consents: list[str]
    ) -> dict[str, Any]:
        """Handle manual profile override (F3.4)."""
        if "a" not in consents:
            return {
                "content_profile": _uniform_profile(),
                "errors": [
                    {
                        "agent": self.agent_name,
                        "reason": "consent_a_required_for_profile_update",
                    }
                ],
            }

        # The actual profile update values come from the API request,
        # stored in content_profile by the API layer before graph invocation
        current_profile = state.get("content_profile", _uniform_profile())
        return {
            "content_profile": current_profile,
        }


def _uniform_profile() -> dict[str, Any]:
    """Return the uniform content-adaptation profile (no personalization)."""
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
_agent = ProfilerAgent()


def run_profiler(state: MaestroState) -> dict[str, Any]:
    """Graph node entry point for the Profiler Agent."""
    return _agent(state)
