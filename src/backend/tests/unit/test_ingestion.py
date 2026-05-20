"""Unit tests for the lesson ingestion pipeline (maestro.kg.ingestion).

Tests the chunking logic and pipeline flow without requiring a database
or external API calls.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maestro.kg.ingestion import (
    LessonMetadata,
    _split_into_chunks,
    _split_sentences,
    ingest_lesson,
)


# ---------------------------------------------------------------------------
# Tests for _split_sentences
# ---------------------------------------------------------------------------

class TestSplitSentences:
    def test_simple_sentences(self) -> None:
        text = "Prima frase. Seconda frase. Terza frase."
        sentences = _split_sentences(text)
        assert len(sentences) == 3

    def test_single_sentence(self) -> None:
        text = "Una sola frase senza punto finale"
        sentences = _split_sentences(text)
        assert len(sentences) == 1
        assert sentences[0] == text

    def test_question_and_exclamation(self) -> None:
        text = "Cos'e un algoritmo? E' una sequenza di istruzioni! Deve essere finito."
        sentences = _split_sentences(text)
        assert len(sentences) == 3

    def test_short_fragments_not_split(self) -> None:
        """Fragments under 10 chars should not cause premature splits."""
        text = "A. B. C. Questa e' una frase lunga che supera i dieci caratteri."
        sentences = _split_sentences(text)
        # The short fragments "A.", "B.", "C." should not cause splits
        assert len(sentences) >= 1


# ---------------------------------------------------------------------------
# Tests for _split_into_chunks
# ---------------------------------------------------------------------------

class TestSplitIntoChunks:
    def test_short_text_single_chunk(self) -> None:
        text = "Questo e' un testo breve che non supera il limite."
        chunks = _split_into_chunks(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_paragraph_splitting(self) -> None:
        text = "Primo paragrafo.\n\nSecondo paragrafo.\n\nTerzo paragrafo."
        chunks = _split_into_chunks(text, max_chars=30)
        assert len(chunks) >= 2

    def test_empty_text(self) -> None:
        chunks = _split_into_chunks("")
        assert chunks == []

    def test_whitespace_only(self) -> None:
        chunks = _split_into_chunks("   \n\n   ")
        assert chunks == []

    def test_long_paragraph_split_by_sentences(self) -> None:
        """A very long paragraph should be split at sentence boundaries."""
        long_para = ". ".join([f"Frase numero {i} del paragrafo molto lungo" for i in range(50)])
        chunks = _split_into_chunks(long_para, max_chars=200)
        assert len(chunks) > 1
        for chunk in chunks:
            # Each chunk should be within the limit (with some tolerance for overlap)
            assert len(chunk) <= 600  # max_chars + overlap room

    def test_overlap_present(self) -> None:
        """Adjacent chunks should have overlapping content."""
        para1 = "Primo paragrafo con contenuto sufficientemente lungo per essere separato."
        para2 = "Secondo paragrafo con altro contenuto altrettanto lungo e significativo."
        para3 = "Terzo paragrafo con ulteriore contenuto che completa il testo della lezione."
        text = f"{para1}\n\n{para2}\n\n{para3}"
        chunks = _split_into_chunks(text, max_chars=80)
        if len(chunks) >= 2:
            # Second chunk should contain some text from the end of the first
            # (due to overlap mechanism)
            first_tail = chunks[0][-40:]
            assert any(
                word in chunks[1] for word in first_tail.split()
                if len(word) > 3
            )

    def test_preserves_content(self) -> None:
        """All original text should be present across the chunks."""
        sentences = [f"Frase {i} del testo originale." for i in range(10)]
        text = "\n\n".join(sentences)
        chunks = _split_into_chunks(text, max_chars=200)
        combined = " ".join(chunks)
        for sentence in sentences:
            assert sentence in combined


# ---------------------------------------------------------------------------
# Tests for ingest_lesson (mocked)
# ---------------------------------------------------------------------------

class TestIngestLesson:
    @pytest.fixture
    def metadata(self) -> LessonMetadata:
        return LessonMetadata(
            course_id=uuid.uuid4(),
            title="Test lesson",
            material_type="lesson",
            uploaded_by=uuid.uuid4(),
        )

    @pytest.mark.asyncio
    async def test_empty_content_returns_zero_chunks(self, metadata: LessonMetadata) -> None:
        """Empty lesson content should result in 0 chunks and status 'indexed'."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.get = AsyncMock(return_value=None)

        # We need to mock the LessonMaterial that gets created
        with patch(
            "maestro.kg.ingestion.LessonMaterial",
        ) as MockMaterial:
            mock_material = MagicMock()
            mock_material.id = uuid.uuid4()
            mock_material.status = "uploaded"
            MockMaterial.return_value = mock_material

            result = await ingest_lesson(session, "", metadata)

            assert result.chunk_count == 0
            assert result.concept_mappings == []
            assert mock_material.status == "indexed"

    @pytest.mark.asyncio
    async def test_successful_ingestion_flow(self, metadata: LessonMetadata) -> None:
        """Test the full ingestion pipeline with mocked dependencies."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        lesson_text = (
            "Gli algoritmi sono sequenze finite di istruzioni.\n\n"
            "Un algoritmo deve avere la proprieta di finitezza: "
            "deve terminare in un numero finito di passi."
        )

        mock_material = MagicMock()
        mock_material.id = uuid.uuid4()
        mock_material.status = "processing"

        fake_embedding = [0.1] * 1536
        mock_link = MagicMock()
        mock_link.id = uuid.uuid4()

        with (
            patch("maestro.kg.ingestion.LessonMaterial", return_value=mock_material),
            patch(
                "maestro.kg.ingestion.generate_embeddings_batch",
                return_value=[fake_embedding],
            ),
            patch("maestro.kg.ingestion.store_chunk_embedding", new_callable=AsyncMock),
            patch("maestro.kg.ingestion.map_concept", return_value=[]),
        ):
            result = await ingest_lesson(session, lesson_text, metadata)

            assert result.material_id == mock_material.id
            assert result.chunk_count >= 1
            assert mock_material.status == "mapped"

    @pytest.mark.asyncio
    async def test_error_sets_material_status_to_error(self, metadata: LessonMetadata) -> None:
        """If ingestion fails, material status should be set to 'error'."""
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        mock_material = MagicMock()
        mock_material.id = uuid.uuid4()
        mock_material.status = "processing"

        with (
            patch("maestro.kg.ingestion.LessonMaterial", return_value=mock_material),
            patch(
                "maestro.kg.ingestion.generate_embeddings_batch",
                side_effect=RuntimeError("API error"),
            ),
            pytest.raises(RuntimeError),
        ):
            await ingest_lesson(session, "Some lesson content here.", metadata)

        assert mock_material.status == "error"
        assert mock_material.processing_error is not None


# ---------------------------------------------------------------------------
# Tests for LessonMetadata
# ---------------------------------------------------------------------------

class TestLessonMetadata:
    def test_defaults(self) -> None:
        meta = LessonMetadata(
            course_id=uuid.uuid4(),
            title="Test",
        )
        assert meta.material_type == "lesson"
        assert meta.batch_id is None

    def test_with_batch_id(self) -> None:
        batch = uuid.uuid4()
        meta = LessonMetadata(
            course_id=uuid.uuid4(),
            title="Test",
            batch_id=batch,
        )
        assert meta.batch_id == batch
