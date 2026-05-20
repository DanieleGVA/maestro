"""LLM Gateway: single entry point for all LLM calls.

Responsibilities:
1. Pseudonymise prompt (remove PII) before sending to external LLM
2. Verify no PII residual (fail-closed)
3. Route to appropriate model (quality vs cost_optimized)
4. Retry with exponential backoff (max 3 attempts)
5. De-pseudonymise response
6. Log every call to audit.llm_audit_log
"""

import asyncio
import hashlib
import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.common.exceptions import LLMUnavailableError
from maestro.config import settings
from maestro.llm.clients import AnthropicClient, OpenAIClient, RawLLMResponse
from maestro.llm.models import LLMRequest, LLMResponse
from maestro.llm.pseudonymizer import PseudonymMap, Pseudonymizer, PseudonymisationError

logger = logging.getLogger(__name__)

# Model routing table (IC-11, Section 13.3)
_MODEL_ROUTES: dict[str, dict[str, str]] = {
    "quality": {
        "primary": settings.llm_primary_model,     # Claude
        "fallback": settings.llm_batch_model,       # GPT-4o-mini
    },
    "cost_optimized": {
        "primary": settings.llm_batch_model,        # GPT-4o-mini
        "fallback": settings.llm_primary_model,     # Claude
    },
}

_ANTHROPIC_PREFIXES = ("claude",)
_OPENAI_PREFIXES = ("gpt", "o1", "o3")


class LLMGateway:
    """Unified gateway for all LLM interactions.

    Enforces pseudonymisation on every call. No PII crosses to external LLMs.
    """

    def __init__(self) -> None:
        self._anthropic = AnthropicClient()
        self._openai = OpenAIClient()
        self._pseudonymizer = Pseudonymizer()

    async def generate(
        self,
        request: LLMRequest,
        session: AsyncSession,
        *,
        student_context: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Generate LLM content with full pseudonymisation pipeline.

        Args:
            request: The LLM request with prompt blocks.
            session: DB session for audit logging.
            student_context: Dict with PII fields (name, surname, etc.)
                that must be pseudonymised before the LLM call.

        Returns:
            LLMResponse with de-pseudonymised content.

        Raises:
            PseudonymisationError: If PII residual detected (fail-closed).
            LLMUnavailableError: If all models are unavailable after retries.
        """
        # 1. Build pseudonym map
        pmap = PseudonymMap()
        known_pii: list[str] = []
        if student_context:
            pmap = self._pseudonymizer.build_map(
                student_name=student_context.get("name"),
                student_surname=student_context.get("surname"),
                teacher_name=student_context.get("teacher_name"),
                teacher_surname=student_context.get("teacher_surname"),
                school_name=student_context.get("school_name"),
                class_name=student_context.get("class_name"),
                email=student_context.get("email"),
                native_language=student_context.get("native_language"),
                birth_year=student_context.get("birth_year"),
                phone=student_context.get("phone"),
                registry_id=student_context.get("registry_id"),
            )
            known_pii = self._pseudonymizer.collect_known_pii(
                student_name=student_context.get("name"),
                student_surname=student_context.get("surname"),
                teacher_name=student_context.get("teacher_name"),
                teacher_surname=student_context.get("teacher_surname"),
                school_name=student_context.get("school_name"),
                email=student_context.get("email"),
                native_language=student_context.get("native_language"),
                birth_year=student_context.get("birth_year"),
                phone=student_context.get("phone"),
                registry_id=student_context.get("registry_id"),
            )

        # 2. Pseudonymise all prompt blocks
        safe_system = pmap.pseudonymise(request.system_prompt)
        safe_context = pmap.pseudonymise(request.context_block)
        safe_task = pmap.pseudonymise(request.task_block)

        # 3. Fail-closed: verify no PII residual
        combined = safe_system + safe_context + safe_task
        if not self._pseudonymizer.verify_no_pii_residual(
            combined, known_pii=known_pii
        ):
            logger.error(
                "PII residual detected after pseudonymisation. LLM call BLOCKED.",
                extra={"correlation_id": request.correlation_id},
            )
            raise PseudonymisationError(
                "PII residuo rilevato nel prompt dopo pseudonimizzazione. "
                "Chiamata LLM bloccata."
            )

        # 4. Compute prompt hash for audit (of pseudonymised prompt, never raw)
        prompt_hash = hashlib.sha256(combined.encode()).hexdigest()

        # 5. Route and call with retry + fallback
        user_message = f"{safe_context}\n\n{safe_task}"
        raw = await self._call_with_retry_and_fallback(
            system_prompt=safe_system,
            user_message=user_message,
            model_preference=request.model_preference,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        # 6. De-pseudonymise response
        real_content = pmap.depseudonymise(raw.content)

        # 7. Destroy the mapping
        pmap.clear()

        # 8. Audit log (prompt hash, never prompt text)
        await self._log_audit(
            session=session,
            request_id=request.correlation_id,
            agent_name=request.agent_name,
            model_id=raw.model_id,
            prompt_hash=prompt_hash,
            input_tokens=raw.input_tokens,
            output_tokens=raw.output_tokens,
            latency_ms=raw.latency_ms,
            cache_hit=False,
        )

        return LLMResponse(
            content=real_content,
            model_id=raw.model_id,
            input_tokens=raw.input_tokens,
            output_tokens=raw.output_tokens,
            latency_ms=raw.latency_ms,
            cache_hit=False,
            prompt_hash=prompt_hash,
        )

    async def _call_with_retry_and_fallback(
        self,
        *,
        system_prompt: str,
        user_message: str,
        model_preference: str,
        max_tokens: int,
        temperature: float,
    ) -> RawLLMResponse:
        """Call LLM with exponential backoff retry, then fallback to secondary model."""
        route = _MODEL_ROUTES.get(model_preference, _MODEL_ROUTES["quality"])
        models_to_try = [route["primary"], route["fallback"]]

        for model in models_to_try:
            client = self._get_client_for_model(model)
            for attempt in range(settings.llm_max_retries):
                try:
                    return await client.generate(
                        system_prompt=system_prompt,
                        user_message=user_message,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                except Exception:
                    if attempt < settings.llm_max_retries - 1:
                        wait = 2**attempt
                        logger.warning(
                            "LLM call failed (model=%s, attempt=%d), retrying in %ds",
                            model,
                            attempt + 1,
                            wait,
                        )
                        await asyncio.sleep(wait)
                    else:
                        logger.warning(
                            "LLM model %s exhausted retries, trying fallback",
                            model,
                        )

        raise LLMUnavailableError()

    def _get_client_for_model(self, model: str) -> AnthropicClient | OpenAIClient:
        model_lower = model.lower()
        if any(model_lower.startswith(p) for p in _ANTHROPIC_PREFIXES):
            return self._anthropic
        if any(model_lower.startswith(p) for p in _OPENAI_PREFIXES):
            return self._openai
        # Default to Anthropic for unknown models
        return self._anthropic

    async def _log_audit(
        self,
        *,
        session: AsyncSession,
        request_id: str,
        agent_name: str,
        model_id: str,
        prompt_hash: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        cache_hit: bool,
    ) -> None:
        """Write LLM call to audit.llm_audit_log (append-only)."""
        try:
            await session.execute(
                text("""
                    INSERT INTO audit.llm_audit_log
                        (request_id, agent_name, model_id, prompt_hash,
                         input_tokens, output_tokens, latency_ms, cache_hit)
                    VALUES
                        (:request_id::uuid, :agent_name, :model_id, :prompt_hash,
                         :input_tokens, :output_tokens, :latency_ms, :cache_hit)
                """),
                {
                    "request_id": request_id,
                    "agent_name": agent_name,
                    "model_id": model_id,
                    "prompt_hash": prompt_hash,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "latency_ms": latency_ms,
                    "cache_hit": cache_hit,
                },
            )
        except Exception:
            logger.exception("Failed to write LLM audit log entry")
