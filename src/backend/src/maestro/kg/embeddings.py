"""Embedding generation and similarity search using OpenAI + pgvector.

MVP uses OpenAI text-embedding-3-small (1536 dimensions).
Content is pseudonymised before reaching the embedding API (no PII per CLAUDE.md).
"""

from __future__ import annotations

import uuid

from openai import AsyncOpenAI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.config import settings
from maestro.kg.models import KGNodeEmbedding, LessonChunk

# Module-level client, lazily initialized
_client: AsyncOpenAI | None = None

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def generate_embedding(text_content: str) -> list[float]:
    """Generate a 1536-dimensional embedding for the given text.

    Uses OpenAI text-embedding-3-small. The caller MUST ensure no PII
    is present in text_content (pseudonymisation boundary per N1).
    """
    client = _get_client()
    response = await client.embeddings.create(
        input=text_content,
        model=EMBEDDING_MODEL,
    )
    return response.data[0].embedding


async def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts (max ~2048 per call)."""
    if not texts:
        return []
    client = _get_client()
    response = await client.embeddings.create(
        input=texts,
        model=EMBEDDING_MODEL,
    )
    # OpenAI returns embeddings in the same order as input
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]


async def store_node_embedding(
    session: AsyncSession,
    *,
    node_id: uuid.UUID,
    node_type: str,
    embedding: list[float],
) -> KGNodeEmbedding:
    """Store or update the embedding for a KG node."""
    existing = await session.get(KGNodeEmbedding, node_id)
    if existing is not None:
        existing.embedding = embedding
        existing.node_type = node_type
        await session.flush()
        return existing

    node_emb = KGNodeEmbedding(
        node_id=node_id,
        node_type=node_type,
        embedding=embedding,
    )
    session.add(node_emb)
    await session.flush()
    return node_emb


async def store_chunk_embedding(
    session: AsyncSession,
    *,
    material_id: uuid.UUID,
    course_id: uuid.UUID,
    chunk_index: int,
    content: str,
    embedding: list[float],
    metadata: dict | None = None,
) -> LessonChunk:
    """Store a lesson chunk with its embedding in the content.lesson_chunk table."""
    chunk = LessonChunk(
        material_id=material_id,
        course_id=course_id,
        chunk_index=chunk_index,
        content=content,
        embedding=embedding,
        chunk_metadata=metadata or {},
    )
    session.add(chunk)
    await session.flush()
    return chunk


async def search_similar_nodes(
    session: AsyncSession,
    query_embedding: list[float],
    *,
    top_k: int = 5,
    similarity_threshold: float = 0.60,
    course_id: uuid.UUID | None = None,
) -> list[dict]:
    """Find KG nodes with the most similar embeddings.

    Returns dicts with node_id, node_type, similarity score.
    Uses pgvector cosine distance operator (<=>).
    """
    # Build the query with optional course filter
    where_clause = ""
    params: dict = {
        "query_embedding": str(query_embedding),
        "top_k": top_k,
        "threshold": similarity_threshold,
    }

    if course_id is not None:
        where_clause = "AND kn.course_id = :course_id"
        params["course_id"] = str(course_id)

    result = await session.execute(
        text(f"""
            SELECT
                ne.node_id,
                ne.node_type,
                kn.label_it,
                kn.description,
                1 - (ne.embedding <=> :query_embedding::vector) AS similarity
            FROM kg.node_embedding ne
            JOIN kg.node kn ON kn.id = ne.node_id
            WHERE kn.is_active = true
                AND 1 - (ne.embedding <=> :query_embedding::vector) > :threshold
                {where_clause}
            ORDER BY ne.embedding <=> :query_embedding::vector
            LIMIT :top_k
        """),
        params,
    )
    rows = result.all()
    return [
        {
            "node_id": row.node_id,
            "node_type": row.node_type,
            "label_it": row.label_it,
            "description": row.description,
            "similarity": float(row.similarity),
        }
        for row in rows
    ]


async def search_similar_chunks(
    session: AsyncSession,
    query_embedding: list[float],
    *,
    course_id: uuid.UUID,
    top_k: int = 10,
    similarity_threshold: float = 0.70,
) -> list[dict]:
    """Find lesson chunks most similar to the query embedding.

    Course-scoped per HLD-002 Section 3.5.
    """
    result = await session.execute(
        text("""
            SELECT
                lc.id,
                lc.material_id,
                lc.content,
                lc.metadata,
                lc.chunk_index,
                1 - (lc.embedding <=> :query_embedding::vector) AS similarity
            FROM content.lesson_chunk lc
            WHERE lc.course_id = :course_id
                AND 1 - (lc.embedding <=> :query_embedding::vector) > :threshold
            ORDER BY lc.embedding <=> :query_embedding::vector
            LIMIT :top_k
        """),
        {
            "query_embedding": str(query_embedding),
            "course_id": str(course_id),
            "threshold": similarity_threshold,
            "top_k": top_k,
        },
    )
    rows = result.all()
    return [
        {
            "chunk_id": row.id,
            "material_id": row.material_id,
            "content": row.content,
            "metadata": row.metadata,
            "chunk_index": row.chunk_index,
            "similarity": float(row.similarity),
        }
        for row in rows
    ]
