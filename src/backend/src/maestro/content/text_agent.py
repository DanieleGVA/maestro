"""Text Agent: generates personalised text content for students.

Produces:
- Review documents (F5): post-verification review with error analysis
- Remediation missions (F11.7): gap closure content

Uses three-layer prompt architecture (system/context/task) from HLD-003 Section 3.1.
Safeguarding system prompt is injected in EVERY call -- this is non-optional.
"""

import json
import logging
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from maestro.content.schemas import ContentAdaptationProfile, TargetNode
from maestro.llm.gateway import LLMGateway
from maestro.llm.models import LLMRequest, LLMResponse
from maestro.safeguarding.checker import (
    SYSTEM_PROMPT_SAFEGUARDING,
    SafeguardingResult,
    safeguarding_check,
)
from maestro.safeguarding.retry import (
    FALLBACK_MESSAGE_IT,
    MAX_SAFEGUARDING_ATTEMPTS,
    RetryContext,
    build_retry_prompt,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates from HLD-003 Section 3.2
# ---------------------------------------------------------------------------
TEXT_SYSTEM_PROMPT = """\
You are a learning tutor for Italian high school IT students. You generate \
personalised study materials that help students understand concepts they \
struggled with.

ABSOLUTE RULES -- NEVER VIOLATE:
1. NEVER reference the student's real name or any personal details.
   You only know them as {student_pseudo_id}.
2. NEVER compare this student with other students, class averages, or \
   rankings. Every reference is to the student's own journey.
3. NEVER use punitive, shaming, or discouraging language. Errors are \
   opportunities. Use framing like "questo concetto ha bisogno di un \
   altro giro" instead of "hai sbagliato."
4. NEVER include trick questions, sarcasm, irony that could be misread, \
   or age-inappropriate content. Your audience is 13-19 years old.
5. NEVER fabricate information. If the source materials do not cover a \
   point, say so explicitly rather than inventing an explanation.
6. ALWAYS ground your explanations in the provided source materials. \
   Prioritise Teacher Lesson sources (TIER 1) over textbook (TIER 2) \
   over external sources (TIER 3).
7. When showing code, ALWAYS include both the ERRONEOUS version (marked \
   with [ERRATO]) and the CORRECT version (marked with [CORRETTO]).
8. Content must be in {course_language} unless bilingual mode instructions \
   say otherwise.

OUTPUT FORMAT: You MUST return valid JSON matching the schema provided in \
the task block. No markdown outside the JSON structure. No preamble.

{safeguarding_rules}
"""

TONE_INSTRUCTIONS = {
    "confidenziale": (
        "Usa il 'tu'. Frasi brevi, tono leggero, qualche battuta. "
        "Come un compagno di classe piu' esperto che ti aiuta."
    ),
    "neutro": (
        "Usa il 'tu'. Tono calmo e chiaro, senza battute ma senza formalita'."
    ),
    "formale": (
        "Usa il 'Lei'. Frasi articolate, terminologia precisa."
    ),
}

LENGTH_DESCRIPTIONS = {
    "sintesi": "2-3 concetti per documento, spiegazioni concise (150-250 parole per blocco)",
    "approfondimento": "6-8 concetti, spiegazioni dettagliate passo-passo (400-600 parole per blocco)",
}

REVIEW_DOCUMENT_TASK = """\
CONTEXT:
Student {student_pseudo_id} has gaps in the following concepts after a verification.

Content adaptation profile:
- Tone: {tone}
- Length: {length} ({length_description})

TASK:
For EACH of the following concept gaps, generate a review block with exactly 4 sections:

{node_descriptions}

Each block MUST have:
1. "il_tuo_errore" -- Show what went wrong. Use a relatable analogy.
2. "perche_succede" -- Explain WHY this error occurs. Root cause, not just symptoms.
3. "come_si_fa_giusto" -- Show the correct approach. Step-by-step if length mode is \
"approfondimento".
4. "ricordati" -- One memorable rule or mnemonic. Brief. Sticky.

TONE: {tone_instruction}

Return JSON:
{{
  "blocks": [
    {{
      "concept_node_id": "string",
      "concept_label": "string",
      "il_tuo_errore": {{
        "text": "string (markdown)",
        "code_errato": "string | null",
        "analogy_domain": "string"
      }},
      "perche_succede": {{
        "text": "string (markdown)",
        "source_refs": []
      }},
      "come_si_fa_giusto": {{
        "text": "string (markdown)",
        "code_corretto": "string | null",
        "source_refs": []
      }},
      "ricordati": {{
        "text": "string (max 100 words)",
        "mnemonic": "string | null"
      }}
    }}
  ],
  "summary": "string (2-3 sentence encouraging summary)"
}}
"""

REMEDIATION_PATH_TASK = """\
CONTEXT:
Student {student_pseudo_id} is working on closing a gap in:
  Concept: {node_label}
  Current state: in_recupero
  Attempt: {attempt_number}

Content adaptation profile:
- Tone: {tone}
- Length: {length}

{retry_note}

TASK:
Generate a focused remediation document for this single concept.

Structure:
1. "aggancio" -- Connect to what the student already knows. Brief, motivating opener.
2. "spiegazione" -- Core explanation. Use a relatable analogy. If code, show working example.
3. "esempio_pratico" -- A concrete, runnable example. If the concept is code-related, \
the example must be syntactically valid and complete enough to execute.
4. "verifica_veloce" -- A single self-check question (not graded).
5. "prossimo_passo" -- Encouraging closing. "Quando ti senti pronto, prova il quiz!"

Return JSON:
{{
  "concept_node_id": "string",
  "concept_label": "string",
  "aggancio": {{ "text": "string (markdown)" }},
  "spiegazione": {{
    "text": "string (markdown)",
    "source_refs": []
  }},
  "esempio_pratico": {{
    "text": "string (markdown)",
    "code": "string | null",
    "language": "string | null"
  }},
  "verifica_veloce": {{
    "question": "string",
    "hint": "string"
  }},
  "prossimo_passo": {{ "text": "string" }}
}}
"""


class TextAgent:
    """Generates personalised text content with safeguarding checks."""

    def __init__(self, gateway: LLMGateway) -> None:
        self._gateway = gateway

    async def generate_explanation(
        self,
        *,
        nodes: list[TargetNode],
        student_pseudo_id: str,
        profile: ContentAdaptationProfile,
        course_language: str,
        session: AsyncSession,
        student_context: dict | None = None,
    ) -> dict:
        """Generate a review document (F5) for post-verification review.

        Returns the content dict or fallback message if safeguarding blocks all attempts.
        """
        node_descriptions = "\n".join(
            f"Concept: {n.label_it} (ID: {n.node_id})\n"
            f"Student's error: {n.error_description or 'N/A'}"
            for n in nodes
        )

        system = TEXT_SYSTEM_PROMPT.format(
            student_pseudo_id=student_pseudo_id,
            course_language=course_language,
            safeguarding_rules=SYSTEM_PROMPT_SAFEGUARDING,
        )
        task = REVIEW_DOCUMENT_TASK.format(
            student_pseudo_id=student_pseudo_id,
            tone=profile.tone,
            length=profile.length,
            length_description=LENGTH_DESCRIPTIONS.get(profile.length, ""),
            node_descriptions=node_descriptions,
            tone_instruction=TONE_INSTRUCTIONS.get(profile.tone, ""),
        )

        return await self._generate_with_safeguarding(
            system_prompt=system,
            task_block=task,
            prompt_template_id="text_review_document_v1",
            session=session,
            student_context=student_context,
        )

    async def generate_recovery_mission(
        self,
        *,
        node: TargetNode,
        student_pseudo_id: str,
        profile: ContentAdaptationProfile,
        attempt_number: int,
        session: AsyncSession,
        student_context: dict | None = None,
    ) -> dict:
        """Generate a remediation path (F11.7) for gap closure.

        Returns the content dict or fallback message if safeguarding blocks all attempts.
        """
        retry_note = ""
        if attempt_number > 1:
            retry_note = (
                f"IMPORTANT: This is retry attempt {attempt_number}. The student did not "
                "pass the quiz on the previous attempt. You MUST use a DIFFERENT "
                "explanatory approach: different analogy domain, more concrete examples, "
                "smaller sub-steps."
            )

        system = TEXT_SYSTEM_PROMPT.format(
            student_pseudo_id=student_pseudo_id,
            course_language="it",
            safeguarding_rules=SYSTEM_PROMPT_SAFEGUARDING,
        )
        task = REMEDIATION_PATH_TASK.format(
            student_pseudo_id=student_pseudo_id,
            node_label=node.label_it,
            attempt_number=attempt_number,
            tone=profile.tone,
            length=profile.length,
            retry_note=retry_note,
        )

        return await self._generate_with_safeguarding(
            system_prompt=system,
            task_block=task,
            prompt_template_id="text_remediation_path_v1",
            session=session,
            student_context=student_context,
        )

    async def _generate_with_safeguarding(
        self,
        *,
        system_prompt: str,
        task_block: str,
        prompt_template_id: str,
        session: AsyncSession,
        student_context: dict | None = None,
    ) -> dict:
        """Generate content with safeguarding retry loop.

        Attempts up to MAX_SAFEGUARDING_ATTEMPTS times. On each failure,
        modifies the prompt to be more conservative. After exhausting retries,
        returns a fallback message.
        """
        retry_ctx = RetryContext(
            attempt_number=1,
            original_request_id=str(uuid.uuid4()),
        )
        current_task = task_block

        for attempt in range(1, MAX_SAFEGUARDING_ATTEMPTS + 1):
            retry_ctx.attempt_number = attempt

            request = LLMRequest(
                agent_name="text_agent",
                model_preference="quality",
                prompt_template_id=prompt_template_id,
                prompt_template_version=1,
                system_prompt=system_prompt,
                context_block="",
                task_block=current_task,
                max_tokens=4000,
                temperature=retry_ctx.temperature_override or 0.7,
                response_format="json",
                correlation_id=retry_ctx.original_request_id,
            )

            start = time.monotonic()
            response: LLMResponse = await self._gateway.generate(
                request, session, student_context=student_context
            )
            latency = int((time.monotonic() - start) * 1000)

            # Safeguarding post-generation check
            check: SafeguardingResult = safeguarding_check(response.content)

            if check.passed:
                try:
                    return json.loads(response.content)
                except json.JSONDecodeError:
                    # If the LLM returned invalid JSON, treat as content
                    return {"raw_text": response.content}

            # Blocked -- prepare for retry
            logger.warning(
                "Safeguarding blocked content (attempt %d/%d, violations=%d)",
                attempt,
                MAX_SAFEGUARDING_ATTEMPTS,
                len(check.violations),
            )
            retry_ctx.previous_violations = check.violations

            if retry_ctx.can_retry:
                current_task = build_retry_prompt(task_block, retry_ctx)

        # All attempts exhausted -- serve fallback
        logger.error(
            "Safeguarding blocked content after %d attempts. Serving fallback.",
            MAX_SAFEGUARDING_ATTEMPTS,
        )
        return {"fallback": True, "message": FALLBACK_MESSAGE_IT}
