"""Concept-mapping engine: maps text chunks to KG nodes.

Uses a two-step pipeline per HLD-002 Section 4.1:
1. Embedding similarity (pgvector cosine distance)
2. LLM classification (GPT-4o-mini for cost optimisation)

Weighting per HLD-002:
- Lesson mapping:  0.4 embedding + 0.6 LLM
- Error mapping:   0.3 embedding + 0.7 LLM
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.config import settings
from maestro.kg.embeddings import generate_embedding, search_similar_nodes

# Confidence thresholds per HLD-002 Section 4.1
HIGH_CONFIDENCE_THRESHOLD = 0.80
MEDIUM_CONFIDENCE_THRESHOLD = 0.60

# Scoring weights
LESSON_EMBEDDING_WEIGHT = 0.4
LESSON_LLM_WEIGHT = 0.6
ERROR_EMBEDDING_WEIGHT = 0.3
ERROR_LLM_WEIGHT = 0.7


@dataclass
class CandidateMapping:
    """A candidate concept mapping with confidence scoring."""

    node_id: uuid.UUID
    node_type: str
    label_it: str
    description: str | None
    embedding_similarity: float
    llm_confidence: float
    composite_score: float
    confidence_level: str  # "high", "medium", "low"
    llm_explanation: str = ""


@dataclass
class MappingResult:
    """Result of a concept mapping operation."""

    chunk_text: str
    candidates: list[CandidateMapping] = field(default_factory=list)
    unmapped: bool = False
    suggested_concept: str | None = None


_openai_client: AsyncOpenAI | None = None


def _get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _openai_client


async def map_concept(
    session: AsyncSession,
    text_chunk: str,
    embedding: list[float],
    *,
    course_id: uuid.UUID,
    top_k: int = 5,
) -> list[CandidateMapping]:
    """Map a lesson text chunk to KG nodes (HLD-002 Section 4.1).

    Uses embedding similarity (weight 0.4) + LLM classification (weight 0.6).
    Returns candidates ordered by composite score descending.
    """
    # Step 1: Find candidate nodes by embedding similarity
    similar_nodes = await search_similar_nodes(
        session,
        embedding,
        top_k=top_k,
        similarity_threshold=0.40,  # Lower threshold to capture more candidates for LLM
        course_id=course_id,
    )

    if not similar_nodes:
        return []

    # Step 2: LLM classification for each candidate
    candidates = await _llm_classify_candidates(
        text_chunk=text_chunk,
        candidate_nodes=similar_nodes,
        embedding_weight=LESSON_EMBEDDING_WEIGHT,
        llm_weight=LESSON_LLM_WEIGHT,
    )

    # Filter below medium threshold and sort by composite score
    candidates = [c for c in candidates if c.composite_score >= MEDIUM_CONFIDENCE_THRESHOLD]
    candidates.sort(key=lambda c: c.composite_score, reverse=True)

    return candidates


async def map_error_concept(
    session: AsyncSession,
    error_text: str,
    quiz_context: str,
    *,
    course_id: uuid.UUID,
    target_macro_ids: list[uuid.UUID] | None = None,
    top_k: int = 5,
) -> list[CandidateMapping]:
    """Map a student quiz error to micro-nodes (HLD-002 Section 4.2).

    Uses embedding similarity (weight 0.3) + LLM classification (weight 0.7).
    The higher LLM weight reflects that error analysis requires semantic understanding.
    """
    combined_text = f"Errore studente: {error_text}\nContesto quiz: {quiz_context}"
    embedding = await generate_embedding(combined_text)

    similar_nodes = await search_similar_nodes(
        session,
        embedding,
        top_k=top_k,
        similarity_threshold=0.30,  # Even lower for errors -- cast wider net
        course_id=course_id,
    )

    if not similar_nodes:
        return []

    # For error mapping, prefer micro-nodes within the target macro
    if target_macro_ids:
        target_ids = {str(m) for m in target_macro_ids}
        # Keep candidates that are micro-nodes under target macros, plus any direct hits
        similar_nodes = [
            n for n in similar_nodes
            if n["node_type"] == "micro" or str(n["node_id"]) in target_ids
        ]

    candidates = await _llm_classify_error_candidates(
        error_text=error_text,
        quiz_context=quiz_context,
        candidate_nodes=similar_nodes,
        embedding_weight=ERROR_EMBEDDING_WEIGHT,
        llm_weight=ERROR_LLM_WEIGHT,
    )

    candidates.sort(key=lambda c: c.composite_score, reverse=True)
    return candidates


async def _llm_classify_candidates(
    *,
    text_chunk: str,
    candidate_nodes: list[dict],
    embedding_weight: float,
    llm_weight: float,
) -> list[CandidateMapping]:
    """Ask the LLM to classify each (chunk, node) pair."""
    if not candidate_nodes:
        return []

    nodes_desc = "\n".join(
        f"- ID: {n['node_id']}, Label: {n['label_it']}, "
        f"Tipo: {n['node_type']}, Descrizione: {n.get('description', 'N/A')}"
        for n in candidate_nodes
    )

    prompt = (
        "Sei un assistente che mappa segmenti di lezioni a concetti di un curriculum "
        "di informatica. Per ogni concetto candidato, valuta se il testo della lezione "
        "insegna effettivamente quel concetto.\n\n"
        f"TESTO DELLA LEZIONE:\n{text_chunk[:2000]}\n\n"
        f"CONCETTI CANDIDATI:\n{nodes_desc}\n\n"
        "Per ogni concetto, rispondi con un JSON array dove ogni elemento ha:\n"
        '- "node_id": l\'ID del concetto\n'
        '- "confidence": un numero da 0.0 a 1.0 che indica quanto sei sicuro '
        "che il testo insegni questo concetto\n"
        '- "explanation": breve spiegazione in italiano\n\n'
        "Rispondi SOLO con il JSON array, senza altro testo."
    )

    client = _get_openai_client()
    response = await client.chat.completions.create(
        model=settings.llm_batch_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1000,
        response_format={"type": "json_object"},
    )

    llm_results = _parse_llm_response(response.choices[0].message.content or "")

    # Build candidate mappings with composite scores
    candidates: list[CandidateMapping] = []
    node_map = {str(n["node_id"]): n for n in candidate_nodes}

    for llm_result in llm_results:
        node_id_str = str(llm_result.get("node_id", ""))
        node = node_map.get(node_id_str)
        if node is None:
            continue

        emb_sim = node["similarity"]
        llm_conf = max(0.0, min(1.0, float(llm_result.get("confidence", 0.0))))
        composite = embedding_weight * emb_sim + llm_weight * llm_conf

        candidates.append(CandidateMapping(
            node_id=uuid.UUID(node_id_str),
            node_type=node["node_type"],
            label_it=node["label_it"],
            description=node.get("description"),
            embedding_similarity=emb_sim,
            llm_confidence=llm_conf,
            composite_score=round(composite, 3),
            confidence_level=_confidence_level(composite),
            llm_explanation=str(llm_result.get("explanation", "")),
        ))

    return candidates


async def _llm_classify_error_candidates(
    *,
    error_text: str,
    quiz_context: str,
    candidate_nodes: list[dict],
    embedding_weight: float,
    llm_weight: float,
) -> list[CandidateMapping]:
    """Ask the LLM to classify which micro-node an error maps to."""
    if not candidate_nodes:
        return []

    nodes_desc = "\n".join(
        f"- ID: {n['node_id']}, Label: {n['label_it']}, "
        f"Tipo: {n['node_type']}, Descrizione: {n.get('description', 'N/A')}"
        for n in candidate_nodes
    )

    prompt = (
        "Sei un assistente che analizza errori di studenti in verifiche di informatica. "
        "Devi identificare quale concetto specifico (micro-nodo) lo studente non ha compreso.\n\n"
        f"ERRORE DELLO STUDENTE:\n{error_text[:1000]}\n\n"
        f"CONTESTO DELLA DOMANDA:\n{quiz_context[:1000]}\n\n"
        f"CONCETTI CANDIDATI:\n{nodes_desc}\n\n"
        "Per ogni concetto, rispondi con un JSON array dove ogni elemento ha:\n"
        '- "node_id": l\'ID del concetto\n'
        '- "confidence": un numero da 0.0 a 1.0 che indica quanto sei sicuro '
        "che l'errore riveli una lacuna in questo concetto\n"
        '- "explanation": breve analisi dell\'errore in italiano\n\n'
        "Rispondi SOLO con il JSON array, senza altro testo."
    )

    client = _get_openai_client()
    response = await client.chat.completions.create(
        model=settings.llm_batch_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1000,
        response_format={"type": "json_object"},
    )

    llm_results = _parse_llm_response(response.choices[0].message.content or "")

    candidates: list[CandidateMapping] = []
    node_map = {str(n["node_id"]): n for n in candidate_nodes}

    for llm_result in llm_results:
        node_id_str = str(llm_result.get("node_id", ""))
        node = node_map.get(node_id_str)
        if node is None:
            continue

        emb_sim = node["similarity"]
        llm_conf = max(0.0, min(1.0, float(llm_result.get("confidence", 0.0))))
        composite = embedding_weight * emb_sim + llm_weight * llm_conf

        candidates.append(CandidateMapping(
            node_id=uuid.UUID(node_id_str),
            node_type=node["node_type"],
            label_it=node["label_it"],
            description=node.get("description"),
            embedding_similarity=emb_sim,
            llm_confidence=llm_conf,
            composite_score=round(composite, 3),
            confidence_level=_confidence_level(composite),
            llm_explanation=str(llm_result.get("explanation", "")),
        ))

    return candidates


def _parse_llm_response(content: str) -> list[dict]:
    """Parse the LLM JSON response, handling various formats."""
    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return parsed
        # Handle {"results": [...]} or {"mappings": [...]} wrapper
        if isinstance(parsed, dict):
            for key in ("results", "mappings", "candidates", "items"):
                if key in parsed and isinstance(parsed[key], list):
                    return parsed[key]
            # Single result wrapped in dict
            if "node_id" in parsed:
                return [parsed]
        return []
    except (json.JSONDecodeError, TypeError):
        return []


def _confidence_level(score: float) -> str:
    """Determine confidence level per HLD-002 thresholds."""
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "high"
    if score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "medium"
    return "low"
