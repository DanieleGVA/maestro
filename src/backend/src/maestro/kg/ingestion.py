"""Lesson ingestion pipeline: upload -> chunking -> embedding -> concept mapping.

Implements the pipeline from HLD-002 Section 3:
1. Extract text from lesson (MVP: plain text, no PDF/audio parsing)
2. Split into semantic chunks
3. For each chunk: generate embedding, search similar KG nodes
4. Map chunks to KG nodes (concept mapping)
5. Flag unmapped concepts as candidates for teacher review
6. Return mappings for teacher confirmation

All concept mappings are suggestions until confirmed by the teacher
(teacher authority principle, HLD-002 Section 1.2).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.kg.concept_mapper import (
    HIGH_CONFIDENCE_THRESHOLD,
    CandidateMapping,
    map_concept,
)
from maestro.kg.embeddings import (
    generate_embedding,
    generate_embeddings_batch,
    store_chunk_embedding,
)
from maestro.kg.models import ConceptNodeLink, LessonMaterial


@dataclass
class LessonMetadata:
    """Metadata for a lesson being ingested."""

    course_id: uuid.UUID
    title: str
    material_type: str = "lesson"
    uploaded_by: uuid.UUID = field(default_factory=uuid.uuid4)
    batch_id: uuid.UUID | None = None


@dataclass
class IngestionResult:
    """Result of a lesson ingestion operation (per IC-10 contract)."""

    material_id: uuid.UUID
    concept_mappings: list[ConceptNodeLink]
    chunk_count: int
    candidates_for_review: list[CandidateMapping]
    unmapped_chunks: int


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

_MAX_CHUNK_TOKENS = 1500
_OVERLAP_TOKENS = 100
# Approximate tokens-per-character ratio for Italian text
_CHARS_PER_TOKEN = 4


def _split_into_chunks(text: str, max_chars: int | None = None) -> list[str]:
    """Split text into semantic chunks.

    MVP strategy (HLD-002 Section 3.4):
    - Primary split: by paragraph boundaries (double newline)
    - Secondary split: if a chunk exceeds max_chars, split at sentence boundaries
    - Overlap: ~100 tokens between adjacent chunks
    """
    if max_chars is None:
        max_chars = _MAX_CHUNK_TOKENS * _CHARS_PER_TOKEN

    # Split by paragraph
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_chars:
            current_chunk = f"{current_chunk}\n\n{para}".strip() if current_chunk else para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If paragraph itself exceeds limit, split by sentences
            if len(para) > max_chars:
                sentences = _split_sentences(para)
                sub_chunk = ""
                for sent in sentences:
                    if len(sub_chunk) + len(sent) + 1 <= max_chars:
                        sub_chunk = f"{sub_chunk} {sent}".strip() if sub_chunk else sent
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = sent
                if sub_chunk:
                    current_chunk = sub_chunk
                else:
                    current_chunk = ""
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    # Add overlap between adjacent chunks
    if len(chunks) > 1:
        overlap_chars = _OVERLAP_TOKENS * _CHARS_PER_TOKEN
        overlapped: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap_chars:] if len(chunks[i - 1]) > overlap_chars else ""
            overlapped.append(f"{prev_tail} {chunks[i]}".strip() if prev_tail else chunks[i])
        return overlapped

    return chunks


def _split_sentences(text: str) -> list[str]:
    """Simple sentence splitter for Italian text."""
    sentences: list[str] = []
    current = ""
    for char in text:
        current += char
        if char in ".!?" and len(current.strip()) > 10:
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return sentences


# ---------------------------------------------------------------------------
# Main ingestion pipeline
# ---------------------------------------------------------------------------

async def ingest_lesson(
    session: AsyncSession,
    lesson_content: str,
    metadata: LessonMetadata,
) -> IngestionResult:
    """Full lesson ingestion pipeline.

    Steps per HLD-002 Section 3.2:
    1. Create lesson_material record with status 'processing'
    2. Split content into chunks
    3. Generate embeddings for each chunk
    4. Store chunks with embeddings in content.lesson_chunk
    5. Run concept mapping for each chunk
    6. Store suggested mappings in kg.concept_node_link
    7. Update material status to 'mapped'
    8. Return results for teacher review
    """
    # 1. Create material record
    material = LessonMaterial(
        course_id=metadata.course_id,
        title=metadata.title,
        material_type=metadata.material_type,
        status="processing",
        uploaded_by=metadata.uploaded_by,
        batch_id=metadata.batch_id,
    )
    session.add(material)
    await session.flush()

    try:
        # 2. Chunk the content
        chunks = _split_into_chunks(lesson_content)
        if not chunks:
            material.status = "indexed"
            await session.flush()
            return IngestionResult(
                material_id=material.id,
                concept_mappings=[],
                chunk_count=0,
                candidates_for_review=[],
                unmapped_chunks=0,
            )

        # 3. Generate embeddings in batch
        embeddings = await generate_embeddings_batch(chunks)

        # 4. Store chunks with embeddings
        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            await store_chunk_embedding(
                session,
                material_id=material.id,
                course_id=metadata.course_id,
                chunk_index=i,
                content=chunk_text,
                embedding=embedding,
                metadata={"section_index": i},
            )

        # 5-6. Concept mapping for each chunk
        all_mappings: list[ConceptNodeLink] = []
        all_candidates: list[CandidateMapping] = []
        unmapped_count = 0

        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            candidates = await map_concept(
                session,
                chunk_text,
                embedding,
                course_id=metadata.course_id,
            )

            if not candidates:
                unmapped_count += 1
                continue

            for candidate in candidates:
                link = ConceptNodeLink(
                    material_id=material.id,
                    node_id=candidate.node_id,
                    node_type=candidate.node_type,
                    confidence_score=candidate.composite_score,
                    auto_suggested=True,
                )

                # High confidence: auto-suggest for easy teacher confirmation
                if candidate.composite_score >= HIGH_CONFIDENCE_THRESHOLD:
                    link.auto_suggested = True
                else:
                    all_candidates.append(candidate)

                session.add(link)
                all_mappings.append(link)

        await session.flush()

        # 7. Update material status
        material.status = "mapped"
        await session.flush()

        return IngestionResult(
            material_id=material.id,
            concept_mappings=all_mappings,
            chunk_count=len(chunks),
            candidates_for_review=all_candidates,
            unmapped_chunks=unmapped_count,
        )

    except Exception:
        # Mark material as error so teacher can see it failed
        material.status = "error"
        material.processing_error = "Errore durante l'elaborazione della lezione"
        await session.flush()
        raise


# ---------------------------------------------------------------------------
# Teacher confirmation
# ---------------------------------------------------------------------------

async def confirm_mapping(
    session: AsyncSession,
    mapping_id: uuid.UUID,
    teacher_id: uuid.UUID,
) -> ConceptNodeLink:
    """Teacher confirms a concept mapping suggestion."""
    link = await session.get(ConceptNodeLink, mapping_id)
    if link is None:
        from maestro.common.exceptions import NotFoundError
        raise NotFoundError("ConceptNodeLink", str(mapping_id))

    link.confirmed_by = teacher_id
    link.confirmed_at = datetime.now(timezone.utc)
    await session.flush()
    return link


async def reject_mapping(
    session: AsyncSession,
    mapping_id: uuid.UUID,
) -> None:
    """Teacher rejects a concept mapping suggestion (deletes it)."""
    link = await session.get(ConceptNodeLink, mapping_id)
    if link is None:
        from maestro.common.exceptions import NotFoundError
        raise NotFoundError("ConceptNodeLink", str(mapping_id))

    await session.delete(link)
    await session.flush()


async def get_material_mappings(
    session: AsyncSession,
    material_id: uuid.UUID,
) -> list[ConceptNodeLink]:
    """Get all concept mappings for a given material."""
    stmt = (
        select(ConceptNodeLink)
        .where(ConceptNodeLink.material_id == material_id)
        .order_by(ConceptNodeLink.confidence_score.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
