"""ORM models for the Knowledge Graph (kg schema).

Shadow tables for AGE graph vertices/edges, plus supporting relational tables
for concept mapping, node embeddings, and coverage analysis.
Uses the dual-write pattern from HLD-002 Section 8.2.
"""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maestro.db.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> uuid.UUID:
    return uuid.uuid4()


# ---------------------------------------------------------------------------
# kg.node — Relational shadow of AGE MacroNode / MicroNode vertices
# ---------------------------------------------------------------------------

class KGNode(Base):
    """Relational shadow table for AGE graph vertices (HLD-002 Section 8.1)."""

    __tablename__ = "node"
    __table_args__ = (
        UniqueConstraint("course_id", "node_type", "label_it", name="uq_kg_node_course_type_label"),
        CheckConstraint(
            "(node_type = 'macro' AND macro_id IS NULL) OR "
            "(node_type = 'micro' AND macro_id IS NOT NULL)",
            name="ck_kg_node_macro_parent",
        ),
        CheckConstraint(
            "node_type IN ('macro', 'micro')",
            name="ck_kg_node_type",
        ),
        CheckConstraint(
            "difficulty IN ('base', 'intermedio', 'avanzato')",
            name="ck_kg_node_difficulty",
        ),
        CheckConstraint(
            "bloom_level IS NULL OR bloom_level IN "
            "('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')",
            name="ck_kg_node_bloom",
        ),
        CheckConstraint(
            "school_level IN ('secondaria_primo_grado', 'biennio_secondo_grado', "
            "'triennio_secondo_grado', 'post_diploma_its', 'formazione_professionale')",
            name="ck_kg_node_school_level",
        ),
        Index("idx_kg_nodes_course", "course_id", postgresql_where="is_active"),
        Index("idx_kg_nodes_macro", "macro_id", postgresql_where="node_type = 'micro'"),
        {"schema": "kg"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_uuid)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    node_type: Mapped[str] = mapped_column(String(10), nullable=False)
    macro_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("kg.node.id"),
        nullable=True,
    )
    label_it: Mapped[str] = mapped_column(Text, nullable=False)
    label_native: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    bloom_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    school_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    school_level: Mapped[str] = mapped_column(String(40), nullable=False)
    subject: Mapped[str] = mapped_column(Text, nullable=False, default="informatica")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    children: Mapped[list["KGNode"]] = relationship(
        "KGNode", back_populates="macro_parent", lazy="selectin"
    )
    macro_parent: Mapped["KGNode | None"] = relationship(
        "KGNode", back_populates="children", remote_side="KGNode.id", lazy="selectin"
    )


# ---------------------------------------------------------------------------
# kg.edge — Relational shadow of AGE PREREQUISITE / PARENT_OF / RELATED_TO
# ---------------------------------------------------------------------------

class KGEdge(Base):
    """Relational shadow table for AGE graph edges (HLD-002 Section 8.1)."""

    __tablename__ = "edge"
    __table_args__ = (
        UniqueConstraint(
            "source_node_id", "target_node_id", "edge_type",
            name="uq_kg_edge_src_tgt_type",
        ),
        CheckConstraint(
            "edge_type IN ('prerequisite', 'parent_of', 'related_to')",
            name="ck_kg_edge_type",
        ),
        CheckConstraint(
            "strength IS NULL OR strength IN ('required', 'recommended')",
            name="ck_kg_edge_strength",
        ),
        CheckConstraint(
            "source_node_id != target_node_id",
            name="ck_kg_edge_no_self",
        ),
        Index("idx_kg_edges_target", "target_node_id"),
        Index("idx_kg_edges_source", "source_node_id"),
        Index("idx_kg_edges_course", "course_id"),
        {"schema": "kg"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_uuid)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    edge_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kg.node.id"), nullable=False
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kg.node.id"), nullable=False
    )
    strength: Mapped[str | None] = mapped_column(String(20), nullable=True)
    relation_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


# ---------------------------------------------------------------------------
# kg.node_embedding — pgvector embeddings per KG node (HLD-002 Section 4.1)
# ---------------------------------------------------------------------------

class KGNodeEmbedding(Base):
    """Node embedding for concept-mapping similarity search."""

    __tablename__ = "node_embedding"
    __table_args__ = (
        CheckConstraint(
            "node_type IN ('macro', 'micro')",
            name="ck_kg_node_emb_type",
        ),
        {"schema": "kg"},
    )

    node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kg.node.id"), primary_key=True
    )
    node_type: Mapped[str] = mapped_column(String(10), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )


# ---------------------------------------------------------------------------
# kg.concept_node_link — Confirmed lesson-to-node mappings (HLD-002 Section 4.1)
# ---------------------------------------------------------------------------

class ConceptNodeLink(Base):
    """Confirmed mapping between a lesson chunk and a KG node."""

    __tablename__ = "concept_node_link"
    __table_args__ = (
        UniqueConstraint(
            "material_id", "chunk_id", "node_id",
            name="uq_kg_concept_link_mat_chunk_node",
        ),
        CheckConstraint(
            "node_type IN ('macro', 'micro')",
            name="ck_kg_concept_link_type",
        ),
        Index("idx_concept_links_node", "node_id"),
        Index("idx_concept_links_material", "material_id"),
        {"schema": "kg"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_uuid)
    material_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    chunk_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    node_type: Mapped[str] = mapped_column(String(10), nullable=False)
    start_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    auto_suggested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


# ---------------------------------------------------------------------------
# kg.error_node_mapping — Error-to-micronode mappings (HLD-002 Section 4.2)
# ---------------------------------------------------------------------------

class ErrorNodeMapping(Base):
    """Maps student quiz errors to the specific micro-node representing the gap."""

    __tablename__ = "error_node_mapping"
    __table_args__ = (
        UniqueConstraint(
            "verification_id", "question_id", "student_id", "node_id",
            name="uq_kg_error_mapping",
        ),
        Index("idx_error_mappings_student", "student_id"),
        Index("idx_error_mappings_node", "node_id"),
        Index("idx_error_mappings_verification", "verification_id"),
        {"schema": "kg"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_uuid)
    verification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    auto_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    teacher_confirmed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    error_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


# ---------------------------------------------------------------------------
# kg.course_granularity_override (HLD-002 Section 6.2)
# ---------------------------------------------------------------------------

class CourseGranularityOverride(Base):
    """Teacher-set granularity override per course."""

    __tablename__ = "course_granularity_override"
    __table_args__ = ({"schema": "kg"},)

    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    student_can_toggle_micro: Mapped[bool] = mapped_column(Boolean, nullable=False)
    overridden_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    overridden_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)


# ---------------------------------------------------------------------------
# content.lesson_chunk — Vector-indexed lesson chunks (HLD-002 Section 3.5)
# Lives in content schema but is used heavily by the KG ingestion pipeline.
# ---------------------------------------------------------------------------

class LessonChunk(Base):
    """Text chunk with pgvector embedding for semantic search."""

    __tablename__ = "lesson_chunk"
    __table_args__ = (
        UniqueConstraint("material_id", "chunk_index", name="uq_content_chunk_mat_idx"),
        Index("idx_lesson_chunks_course", "course_id"),
        {"schema": "content"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_uuid)
    material_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
    chunk_metadata: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


# ---------------------------------------------------------------------------
# content.lesson_material — Lesson files metadata (HLD-002 Section 8.1)
# ---------------------------------------------------------------------------

class LessonMaterial(Base):
    """Uploaded lesson file metadata."""

    __tablename__ = "lesson_material"
    __table_args__ = (
        CheckConstraint(
            "material_type IN ('lesson', 'textbook', 'exercise', 'notes', "
            "'code_example', 'article', 'external_link')",
            name="ck_content_material_type",
        ),
        CheckConstraint(
            "status IN ('uploaded', 'processing', 'transcribing', 'indexed', 'mapped', 'error')",
            name="ck_content_material_status",
        ),
        Index("idx_materials_course", "course_id"),
        Index("idx_materials_status", "status"),
        {"schema": "content"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_new_uuid)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    material_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_format: Mapped[str | None] = mapped_column(String(10), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="uploaded")
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    batch_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    extra_metadata: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
