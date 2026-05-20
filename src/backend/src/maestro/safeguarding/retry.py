"""Safeguarding retry logic.

When content is blocked by the safeguarding checker, the system retries
with progressively more conservative prompts (max 2 retries, 3 total attempts).
After the third failure, fallback content is served from teacher materials.
"""

from dataclasses import dataclass, field

from maestro.safeguarding.checker import Violation


RETRY_PROMPT_MODIFICATIONS: dict[int, dict[str, object]] = {
    1: {
        # Attempt 2: add context about the specific violation
        "prefix": (
            "ATTENZIONE: il contenuto precedente e' stato bloccato per: "
            "{violation_descriptions}. "
            "Rigenera evitando SPECIFICAMENTE questi pattern. "
        ),
        "temperature_override": 0.3,
    },
    2: {
        # Attempt 3: ultra-conservative prompt
        "prefix": (
            "MODALITA' ULTRA-SICURA. Il contenuto precedente e' stato bloccato "
            "DUE VOLTE. Genera un contenuto ESTREMAMENTE NEUTRO e FATTUALE. "
            "Nessuna analogia, nessun riferimento culturale, nessun humor. "
            "Solo spiegazione tecnica diretta con tono neutro. "
            "Se in dubbio, ometti. "
        ),
        "temperature_override": 0.1,
    },
}

MAX_SAFEGUARDING_ATTEMPTS = 3

FALLBACK_MESSAGE_IT = (
    "Il contenuto personalizzato per questo argomento non e' disponibile "
    "al momento. Il tuo docente e' stato avvisato e ti fornira' il "
    "materiale di studio. Nel frattempo, puoi consultare gli appunti "
    "della lezione nella sezione 'Materiali'."
)


@dataclass
class RetryContext:
    """Tracks safeguarding retry state across attempts."""

    attempt_number: int = 1
    previous_violations: list[Violation] = field(default_factory=list)
    original_request_id: str = ""

    @property
    def can_retry(self) -> bool:
        return self.attempt_number < MAX_SAFEGUARDING_ATTEMPTS

    @property
    def temperature_override(self) -> float | None:
        mod = RETRY_PROMPT_MODIFICATIONS.get(self.attempt_number - 1)
        if mod:
            return float(mod["temperature_override"])  # type: ignore[arg-type]
        return None


def build_retry_prompt(original_prompt: str, retry_ctx: RetryContext) -> str:
    """Build a retry prompt with safeguarding reinforcement prefix.

    Adds violation-specific context so the model avoids the same patterns.
    """
    mod = RETRY_PROMPT_MODIFICATIONS.get(retry_ctx.attempt_number - 1)
    if not mod:
        return original_prompt

    prefix_template = str(mod.get("prefix", ""))
    violation_descriptions = "; ".join(
        v.description for v in retry_ctx.previous_violations
    )
    prefix = prefix_template.format(violation_descriptions=violation_descriptions)
    return prefix + original_prompt
