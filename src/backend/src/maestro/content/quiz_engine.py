"""Quiz Generation Engine.

Generates mini-quizzes (F11.8) and retention checks (F11.10).
Uses Bloom's taxonomy targeting per student state (ADR-002):
  - introdotto: Remember/Understand
  - da_consolidare: Apply/Analyze
  - consolidato: Evaluate/Create

Teacher-authored questions (question bank) have priority over AI-generated ones.
"""

import json
import logging
import uuid
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from maestro.llm.gateway import LLMGateway
from maestro.llm.models import LLMRequest, LLMResponse
from maestro.safeguarding.checker import (
    SYSTEM_PROMPT_SAFEGUARDING,
    safeguarding_check,
)
from maestro.safeguarding.retry import FALLBACK_MESSAGE_IT

logger = logging.getLogger(__name__)


# Bloom's taxonomy mapping per state (from ADR-002 + HLD-003 Section 5.1)
BLOOM_BY_STATE: dict[str, str] = {
    "introdotto": "remember_understand",
    "in_recupero": "remember_understand",
    "da_consolidare": "apply_analyze",
    "consolidato": "evaluate_create",
}

BLOOM_INSTRUCTIONS: dict[str, str] = {
    "remember_understand": (
        "Generate questions that test RECALL and BASIC COMPREHENSION. "
        "Questions should verify the student can define concepts and explain "
        "them in their own words."
    ),
    "apply_analyze": (
        "Generate questions that test APPLICATION and ANALYSIS. "
        "Questions should require the student to apply the concept in a new "
        "context or analyze a scenario."
    ),
    "evaluate_create": (
        "Generate questions that test EVALUATION and CREATION. "
        "Questions should require the student to compare approaches, "
        "justify decisions, or design solutions."
    ),
}

QUIZ_SYSTEM_PROMPT = """\
You are generating a mini-quiz for an Italian high school IT student.
The quiz assesses understanding of a specific concept.

ABSOLUTE RULES:
1. Questions MUST be answerable using ONLY the provided source materials \
   and common IT knowledge for the target concept. No trick questions.
2. Questions MUST target the specific micro-node: {node_label}.
3. Distractors MUST be plausible but clearly wrong -- no ambiguous wording.
4. Language: Italian. Clear, age-appropriate (13-19 years old).
5. NEVER reference the student's name or compare with other students.
6. Each question has exactly 4 options (A, B, C, D) with exactly 1 correct answer.

OUTPUT FORMAT: Return valid JSON. No preamble.

{safeguarding_rules}
"""

QUIZ_TASK = """\
Generate a quiz with {num_questions} multiple-choice questions for:
  Concept: {node_label} (node_id: {node_id})
  Bloom's level target: {bloom_instruction}
  Purpose: {purpose}

Return JSON:
{{
  "questions": [
    {{
      "question_text": "string",
      "options": {{
        "A": "string",
        "B": "string",
        "C": "string",
        "D": "string"
      }},
      "correct_answer": "A|B|C|D",
      "explanation": "string (brief explanation of correct answer)",
      "bloom_level": "remember|understand|apply|analyze|evaluate|create"
    }}
  ]
}}
"""


class QuizEngine:
    """Generates and evaluates quizzes with Bloom's taxonomy targeting."""

    def __init__(self, gateway: LLMGateway) -> None:
        self._gateway = gateway

    async def generate_quiz(
        self,
        *,
        node_id: str,
        node_label: str,
        current_state: str,
        purpose: Literal["closure", "retention"],
        num_questions: int = 5,
        session: AsyncSession,
        student_context: dict | None = None,
    ) -> dict:
        """Generate a quiz for a concept node.

        Uses Bloom's taxonomy level appropriate for the student's current state.
        Returns quiz data dict or fallback message.
        """
        bloom_key = BLOOM_BY_STATE.get(current_state, "remember_understand")
        bloom_instruction = BLOOM_INSTRUCTIONS.get(bloom_key, "")

        system = QUIZ_SYSTEM_PROMPT.format(
            node_label=node_label,
            safeguarding_rules=SYSTEM_PROMPT_SAFEGUARDING,
        )
        task = QUIZ_TASK.format(
            num_questions=num_questions,
            node_label=node_label,
            node_id=node_id,
            bloom_instruction=bloom_instruction,
            purpose=purpose,
        )

        request = LLMRequest(
            agent_name="quiz_engine",
            model_preference="quality",
            prompt_template_id="quiz_generation_v1",
            prompt_template_version=1,
            system_prompt=system,
            context_block="",
            task_block=task,
            max_tokens=3000,
            temperature=0.5,
            response_format="json",
            correlation_id=str(uuid.uuid4()),
        )

        response: LLMResponse = await self._gateway.generate(
            request, session, student_context=student_context
        )

        # Safeguarding check on quiz content
        check = safeguarding_check(response.content)
        if not check.passed:
            logger.warning(
                "Safeguarding blocked quiz content for node %s", node_id
            )
            return {"fallback": True, "message": FALLBACK_MESSAGE_IT}

        try:
            quiz_data = json.loads(response.content)
        except json.JSONDecodeError:
            logger.error("Quiz LLM returned invalid JSON for node %s", node_id)
            return {"fallback": True, "message": FALLBACK_MESSAGE_IT}

        quiz_data["metadata"] = {
            "model_id": response.model_id,
            "prompt_hash": response.prompt_hash,
            "bloom_level": bloom_key,
            "purpose": purpose,
        }
        return quiz_data

    def evaluate_response(
        self,
        *,
        questions: list[dict],
        student_answers: list[dict],
    ) -> dict:
        """Evaluate student answers against quiz questions.

        Args:
            questions: List of quiz questions with correct_answer field.
            student_answers: List of {question_id: str, selected: str}.

        Returns:
            QuizResult dict with score, per-question results.
        """
        answer_map = {str(a["question_id"]): a["selected"] for a in student_answers}
        total = len(questions)
        correct = 0
        per_question: list[dict] = []

        for q in questions:
            q_id = str(q.get("id", q.get("question_index", "")))
            selected = answer_map.get(q_id, "")
            is_correct = selected.upper() == q.get("correct_answer", "").upper()
            if is_correct:
                correct += 1
            per_question.append({
                "question_id": q_id,
                "selected": selected,
                "correct_answer": q.get("correct_answer", ""),
                "is_correct": is_correct,
            })

        score = int((correct / total) * 100) if total > 0 else 0

        return {
            "score": score,
            "total_questions": total,
            "correct_count": correct,
            "per_question": per_question,
        }
