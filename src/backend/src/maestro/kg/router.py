"""KG API router — REST endpoints for Knowledge Graph operations.

Registered on /api/v1/kg per HLD-002 Section 9.
All endpoints require authentication (not enforced in MVP scaffold).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.common.exceptions import MaestroError, NotFoundError
from maestro.common.schemas import ApiResponse, Meta
from maestro.db.engine import get_db
from maestro.kg.concept_mapper import CandidateMapping
from maestro.kg.schemas import (
    CandidateMappingResponse,
    ConceptLinkResponse,
    CurriculumLoadRequest,
    EdgeCreate,
    EdgeResponse,
    IngestionResultResponse,
    LessonIngestRequest,
    MacroNodeCreate,
    MappingConfirmRequest,
    MicroNodeCreate,
    NodeDetailResponse,
    NodeResponse,
    NodeUpdate,
    SearchResultResponse,
    SemanticSearchRequest,
)

router = APIRouter(prefix="/api/v1/kg", tags=["knowledge-graph"])


def _meta() -> Meta:
    return Meta(request_id=str(uuid.uuid4()), timestamp=datetime.now(timezone.utc))


def _to_node_response(node) -> NodeResponse:  # type: ignore[no-untyped-def]
    return NodeResponse.model_validate(node)


# ---------------------------------------------------------------------------
# Lesson ingestion
# ---------------------------------------------------------------------------

@router.post(
    "/courses/{course_id}/lessons/ingest",
    response_model=ApiResponse[IngestionResultResponse],
)
async def ingest_lesson(
    course_id: uuid.UUID,
    body: LessonIngestRequest,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[IngestionResultResponse]:
    """Ingest a lesson: chunking, embedding, concept mapping."""
    from maestro.kg.ingestion import LessonMetadata, ingest_lesson as do_ingest

    # MVP: teacher_id is hardcoded; will come from JWT in production
    teacher_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    metadata = LessonMetadata(
        course_id=course_id,
        title=body.title,
        material_type=body.material_type,
        uploaded_by=teacher_id,
    )

    result = await do_ingest(session, body.content, metadata)
    await session.commit()

    candidates = [
        CandidateMappingResponse(
            node_id=c.node_id,
            node_type=c.node_type,
            label_it=c.label_it,
            description=c.description,
            embedding_similarity=c.embedding_similarity,
            llm_confidence=c.llm_confidence,
            composite_score=c.composite_score,
            confidence_level=c.confidence_level,
            llm_explanation=c.llm_explanation,
        )
        for c in result.candidates_for_review
    ]

    return ApiResponse(
        data=IngestionResultResponse(
            material_id=result.material_id,
            chunk_count=result.chunk_count,
            mapping_count=len(result.concept_mappings),
            candidates_for_review=candidates,
            unmapped_chunks=result.unmapped_chunks,
        ),
        meta=_meta(),
    )


# ---------------------------------------------------------------------------
# Mapping confirmation
# ---------------------------------------------------------------------------

@router.post(
    "/mappings/{mapping_id}/confirm",
    response_model=ApiResponse[ConceptLinkResponse],
)
async def confirm_or_reject_mapping(
    mapping_id: uuid.UUID,
    body: MappingConfirmRequest,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[ConceptLinkResponse]:
    """Confirm or reject a concept mapping suggestion."""
    from maestro.kg.ingestion import confirm_mapping, reject_mapping

    teacher_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    try:
        if body.action == "confirm":
            link = await confirm_mapping(session, mapping_id, teacher_id)
            await session.commit()
            return ApiResponse(
                data=ConceptLinkResponse.model_validate(link),
                meta=_meta(),
            )
        else:
            await reject_mapping(session, mapping_id)
            await session.commit()
            # Return a minimal response for deletion
            return ApiResponse(
                data=ConceptLinkResponse(
                    id=mapping_id,
                    material_id=uuid.UUID(int=0),
                    node_id=uuid.UUID(int=0),
                    node_type="micro",
                    auto_suggested=True,
                    created_at=datetime.now(timezone.utc),
                ),
                meta=_meta(),
            )
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Mapping non trovato")


# ---------------------------------------------------------------------------
# Node CRUD
# ---------------------------------------------------------------------------

@router.get(
    "/courses/{course_id}/nodes",
    response_model=ApiResponse[list[NodeResponse]],
)
async def list_nodes(
    course_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[list[NodeResponse]]:
    """List all active nodes for a course."""
    from maestro.kg.graph_ops import get_course_nodes

    nodes = await get_course_nodes(session, course_id)
    return ApiResponse(
        data=[_to_node_response(n) for n in nodes],
        meta=_meta(),
    )


@router.get(
    "/nodes/{node_id}",
    response_model=ApiResponse[NodeDetailResponse],
)
async def get_node_detail(
    node_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[NodeDetailResponse]:
    """Get node detail with prerequisites and dependents."""
    from maestro.kg.curriculum import get_node_detail as do_get_detail

    try:
        detail = await do_get_detail(session, node_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Nodo non trovato")

    return ApiResponse(
        data=NodeDetailResponse(
            node=_to_node_response(detail["node"]),
            prerequisites=[_to_node_response(n) for n in detail.get("prerequisites", [])],
            dependents=[_to_node_response(n) for n in detail.get("dependents", [])],
            children=[_to_node_response(n) for n in detail["children"]]
            if "children" in detail
            else None,
            macro_parent=_to_node_response(detail["macro_parent"])
            if detail.get("macro_parent")
            else None,
        ),
        meta=_meta(),
    )


@router.post(
    "/courses/{course_id}/nodes",
    response_model=ApiResponse[NodeResponse],
    status_code=201,
)
async def create_node(
    course_id: uuid.UUID,
    body: MacroNodeCreate | MicroNodeCreate,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[NodeResponse]:
    """Create a macro or micro node."""
    from maestro.kg.graph_ops import add_macro_node, add_micro_node

    teacher_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    try:
        if isinstance(body, MicroNodeCreate):
            node = await add_micro_node(
                session,
                macro_id=body.macro_id,
                course_id=course_id,
                label_it=body.label_it,
                difficulty=body.difficulty,
                school_year=1,  # Inherited from course in production
                school_level="triennio_secondo_grado",
                created_by=teacher_id,
                description=body.description,
                label_native=body.label_native,
                bloom_level=body.bloom_level,
                sort_order=body.sort_order,
            )
        else:
            node = await add_macro_node(
                session,
                course_id=course_id,
                label_it=body.label_it,
                difficulty=body.difficulty,
                school_year=body.school_year,
                school_level=body.school_level,
                created_by=teacher_id,
                description=body.description,
                label_native=body.label_native,
                subject=body.subject,
                sort_order=body.sort_order,
            )
        await session.commit()
    except MaestroError as e:
        raise HTTPException(status_code=422, detail=e.message)

    return ApiResponse(data=_to_node_response(node), meta=_meta())


@router.put(
    "/nodes/{node_id}",
    response_model=ApiResponse[NodeResponse],
)
async def update_node(
    node_id: uuid.UUID,
    body: NodeUpdate,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[NodeResponse]:
    """Update editable fields of a KG node."""
    from maestro.kg.graph_ops import update_node as do_update

    teacher_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    try:
        node = await do_update(
            session,
            node_id=node_id,
            updated_by=teacher_id,
            **body.model_dump(exclude_none=True),
        )
        await session.commit()
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Nodo non trovato")
    except MaestroError as e:
        raise HTTPException(status_code=422, detail=e.message)

    return ApiResponse(data=_to_node_response(node), meta=_meta())


@router.delete(
    "/nodes/{node_id}",
    response_model=ApiResponse[NodeResponse],
)
async def deactivate_node(
    node_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[NodeResponse]:
    """Deactivate a node (soft-delete per C4 constraint)."""
    from maestro.kg.graph_ops import deactivate_node as do_deactivate

    teacher_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    try:
        node = await do_deactivate(session, node_id=node_id, deactivated_by=teacher_id)
        await session.commit()
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Nodo non trovato")

    return ApiResponse(data=_to_node_response(node), meta=_meta())


# ---------------------------------------------------------------------------
# Edge CRUD
# ---------------------------------------------------------------------------

@router.post(
    "/courses/{course_id}/edges",
    response_model=ApiResponse[EdgeResponse],
    status_code=201,
)
async def create_edge(
    course_id: uuid.UUID,
    body: EdgeCreate,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[EdgeResponse]:
    """Create an edge (DAG validation for prerequisites)."""
    from maestro.kg.graph_ops import add_prerequisite_edge

    teacher_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    try:
        edge = await add_prerequisite_edge(
            session,
            source_id=body.source_node_id,
            target_id=body.target_node_id,
            course_id=course_id,
            strength=body.strength,
            created_by=teacher_id,
        )
        await session.commit()
    except MaestroError as e:
        status = 422 if e.code == "DAG_CYCLE_DETECTED" else 400
        raise HTTPException(status_code=status, detail=e.message)

    return ApiResponse(data=EdgeResponse.model_validate(edge), meta=_meta())


@router.delete(
    "/edges/{edge_id}",
)
async def remove_edge(
    edge_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    """Remove a prerequisite edge."""
    from maestro.kg.graph_ops import remove_prerequisite_edge

    teacher_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    try:
        await remove_prerequisite_edge(session, edge_id=edge_id, removed_by=teacher_id)
        await session.commit()
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Edge non trovato")

    return ApiResponse(data={"deleted": True}, meta=_meta())


# ---------------------------------------------------------------------------
# Prerequisites
# ---------------------------------------------------------------------------

@router.get(
    "/nodes/{node_id}/prerequisites",
    response_model=ApiResponse[list[NodeResponse]],
)
async def get_prerequisites(
    node_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[list[NodeResponse]]:
    """Get prerequisite nodes for a given node."""
    from maestro.kg.graph_ops import get_prerequisites as do_get_prereqs

    nodes = await do_get_prereqs(session, node_id)
    return ApiResponse(data=[_to_node_response(n) for n in nodes], meta=_meta())


# ---------------------------------------------------------------------------
# Curriculum
# ---------------------------------------------------------------------------

@router.get(
    "/courses/{course_id}/curriculum",
    response_model=ApiResponse[list[NodeResponse]],
)
async def get_curriculum(
    course_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[list[NodeResponse]]:
    """Get complete curriculum as a topologically sorted learning path."""
    from maestro.kg.curriculum import get_learning_path

    nodes = await get_learning_path(session, course_id)
    return ApiResponse(data=[_to_node_response(n) for n in nodes], meta=_meta())


@router.post(
    "/courses/{course_id}/curriculum/load",
    response_model=ApiResponse[list[NodeResponse]],
    status_code=201,
)
async def load_curriculum(
    course_id: uuid.UUID,
    body: CurriculumLoadRequest,
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[list[NodeResponse]]:
    """Load a full curriculum structure into the KG."""
    from maestro.kg.curriculum import load_curriculum as do_load

    teacher_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    try:
        nodes = await do_load(
            session,
            body.model_dump(),
            course_id=course_id,
            teacher_id=teacher_id,
        )
        await session.commit()
    except MaestroError as e:
        raise HTTPException(status_code=422, detail=e.message)

    return ApiResponse(data=[_to_node_response(n) for n in nodes], meta=_meta())


# ---------------------------------------------------------------------------
# Semantic search
# ---------------------------------------------------------------------------

@router.get(
    "/courses/{course_id}/search",
    response_model=ApiResponse[list[SearchResultResponse]],
)
async def semantic_search(
    course_id: uuid.UUID,
    q: str = Query(..., min_length=2),
    top_k: int = Query(5, ge=1, le=50),
    session: AsyncSession = Depends(get_db),
) -> ApiResponse[list[SearchResultResponse]]:
    """Semantic search over KG nodes for a course."""
    from maestro.kg.embeddings import generate_embedding, search_similar_nodes

    embedding = await generate_embedding(q)
    results = await search_similar_nodes(
        session,
        embedding,
        top_k=top_k,
        course_id=course_id,
    )

    return ApiResponse(
        data=[
            SearchResultResponse(
                node_id=r["node_id"],
                node_type=r["node_type"],
                label_it=r["label_it"],
                description=r.get("description"),
                similarity=r["similarity"],
            )
            for r in results
        ],
        meta=_meta(),
    )
