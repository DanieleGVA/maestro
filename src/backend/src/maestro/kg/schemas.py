"""Pydantic schemas for KG API request/response validation.

Follows the IC-12 response envelope contract from interface-contracts.md.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Node schemas
# ---------------------------------------------------------------------------

class MacroNodeCreate(BaseModel):
    """Request body for creating a macro-node."""

    label_it: str = Field(..., max_length=200)
    label_native: str | None = None
    description: str | None = None
    difficulty: Literal["base", "intermedio", "avanzato"]
    school_year: int = Field(..., ge=1, le=5)
    school_level: Literal[
        "secondaria_primo_grado",
        "biennio_secondo_grado",
        "triennio_secondo_grado",
        "post_diploma_its",
        "formazione_professionale",
    ]
    subject: str = "informatica"
    sort_order: int = 0


class MicroNodeCreate(BaseModel):
    """Request body for creating a micro-node."""

    macro_id: uuid.UUID
    label_it: str = Field(..., max_length=300)
    label_native: str | None = None
    description: str | None = None
    difficulty: Literal["base", "intermedio", "avanzato"]
    bloom_level: Literal[
        "remember", "understand", "apply", "analyze", "evaluate", "create"
    ] | None = None
    sort_order: int = 0


class NodeUpdate(BaseModel):
    """Request body for updating a node."""

    label_it: str | None = Field(None, max_length=300)
    label_native: str | None = None
    description: str | None = None
    difficulty: Literal["base", "intermedio", "avanzato"] | None = None
    bloom_level: Literal[
        "remember", "understand", "apply", "analyze", "evaluate", "create"
    ] | None = None
    sort_order: int | None = None
    subject: str | None = None


class NodeResponse(BaseModel):
    """Response representation of a KG node."""

    id: uuid.UUID
    course_id: uuid.UUID
    node_type: str
    macro_id: uuid.UUID | None = None
    label_it: str
    label_native: str | None = None
    description: str | None = None
    difficulty: str
    bloom_level: str | None = None
    school_year: int
    school_level: str
    subject: str
    sort_order: int
    is_active: bool
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NodeDetailResponse(BaseModel):
    """Detailed node response with prerequisites and dependents."""

    node: NodeResponse
    prerequisites: list[NodeResponse] = []
    dependents: list[NodeResponse] = []
    children: list[NodeResponse] | None = None
    macro_parent: NodeResponse | None = None


# ---------------------------------------------------------------------------
# Edge schemas
# ---------------------------------------------------------------------------

class EdgeCreate(BaseModel):
    """Request body for creating an edge (with DAG validation for prerequisites)."""

    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    edge_type: Literal["prerequisite", "related_to"] = "prerequisite"
    strength: Literal["required", "recommended"] = "required"
    relation_type: str | None = None


class EdgeResponse(BaseModel):
    """Response representation of a KG edge."""

    id: uuid.UUID
    course_id: uuid.UUID
    edge_type: str
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    strength: str | None = None
    relation_type: str | None = None
    created_by: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Ingestion schemas
# ---------------------------------------------------------------------------

class LessonIngestRequest(BaseModel):
    """Request body for lesson ingestion."""

    content: str = Field(..., min_length=10)
    title: str = Field(..., max_length=500)
    material_type: Literal[
        "lesson", "textbook", "exercise", "notes", "code_example", "article"
    ] = "lesson"


class CandidateMappingResponse(BaseModel):
    """A concept mapping candidate for teacher review."""

    node_id: uuid.UUID
    node_type: str
    label_it: str
    description: str | None = None
    embedding_similarity: float
    llm_confidence: float
    composite_score: float
    confidence_level: str
    llm_explanation: str = ""


class IngestionResultResponse(BaseModel):
    """Result of a lesson ingestion operation."""

    material_id: uuid.UUID
    chunk_count: int
    mapping_count: int
    candidates_for_review: list[CandidateMappingResponse]
    unmapped_chunks: int


# ---------------------------------------------------------------------------
# Mapping confirmation schemas
# ---------------------------------------------------------------------------

class MappingConfirmRequest(BaseModel):
    """Request body for confirming/rejecting a concept mapping."""

    action: Literal["confirm", "reject"]


class ConceptLinkResponse(BaseModel):
    """Response representation of a confirmed concept-node link."""

    id: uuid.UUID
    material_id: uuid.UUID
    chunk_id: uuid.UUID | None = None
    node_id: uuid.UUID
    node_type: str
    confidence_score: float | None = None
    confirmed_by: uuid.UUID | None = None
    confirmed_at: datetime | None = None
    auto_suggested: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Search schemas
# ---------------------------------------------------------------------------

class SemanticSearchRequest(BaseModel):
    """Query for semantic search over KG nodes."""

    query: str = Field(..., min_length=2)
    top_k: int = Field(5, ge=1, le=50)


class SearchResultResponse(BaseModel):
    """A single semantic search result."""

    node_id: uuid.UUID
    node_type: str
    label_it: str
    description: str | None = None
    similarity: float


# ---------------------------------------------------------------------------
# Curriculum schemas
# ---------------------------------------------------------------------------

class CurriculumMicroNode(BaseModel):
    """Micro-node within a curriculum load."""

    label_it: str
    difficulty: str = "base"
    bloom_level: str | None = None
    description: str | None = None
    sort_order: int = 0


class CurriculumMacroNode(BaseModel):
    """Macro-node within a curriculum load."""

    label_it: str
    difficulty: str = "base"
    school_year: int = 1
    school_level: str = "triennio_secondo_grado"
    description: str | None = None
    sort_order: int = 0
    micro_nodes: list[CurriculumMicroNode] = []


class CurriculumPrerequisite(BaseModel):
    """Prerequisite edge within a curriculum load."""

    source_label: str
    target_label: str
    strength: Literal["required", "recommended"] = "required"


class CurriculumLoadRequest(BaseModel):
    """Request body for loading a full curriculum into the KG."""

    macro_nodes: list[CurriculumMacroNode]
    prerequisites: list[CurriculumPrerequisite] = []
