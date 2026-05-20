"""Apache AGE graph operations with dual-write to relational shadow tables.

All public functions perform the dual-write pattern (HLD-002 Section 8.2):
AGE graph + relational shadow tables in the same PostgreSQL transaction.
The relational table is the source of truth; the AGE graph is reconstructible from it.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.common.audit import log_audit_event
from maestro.common.exceptions import MaestroError, NotFoundError
from maestro.kg.models import KGEdge, KGNode


class DAGCycleError(MaestroError):
    """Raised when adding a prerequisite edge would create a cycle."""

    def __init__(self, source_id: str, target_id: str, cycle_path: list[str] | None = None) -> None:
        super().__init__(
            message=(
                f"Aggiungere prerequisito {source_id} -> {target_id} "
                "creerebbe un ciclo nel DAG"
            ),
            code="DAG_CYCLE_DETECTED",
            detail={"source_id": source_id, "target_id": target_id, "cycle_path": cycle_path},
        )


# ---------------------------------------------------------------------------
# Graph initialization
# ---------------------------------------------------------------------------

async def create_graph(session: AsyncSession) -> None:
    """Initialize the maestro_kg Apache AGE graph and vertex/edge labels.

    Idempotent: safe to call multiple times.
    """
    await session.execute(text("CREATE EXTENSION IF NOT EXISTS age"))
    await session.execute(text("LOAD 'age'"))
    await session.execute(text("SET search_path = ag_catalog, \"$user\", public"))

    # Create graph (ignore if exists)
    result = await session.execute(
        text("SELECT count(*) FROM ag_catalog.ag_graph WHERE name = 'maestro_kg'")
    )
    if result.scalar() == 0:
        await session.execute(text("SELECT create_graph('maestro_kg')"))

    # Create vertex labels (idempotent via IF NOT EXISTS pattern)
    for label in ("MacroNode", "MicroNode"):
        count = await session.execute(
            text(
                "SELECT count(*) FROM ag_catalog.ag_label "
                "WHERE name = :label AND graph = ("
                "  SELECT graphid FROM ag_catalog.ag_graph WHERE name = 'maestro_kg'"
                ")"
            ),
            {"label": label},
        )
        if count.scalar() == 0:
            await session.execute(text(f"SELECT create_vlabel('maestro_kg', '{label}')"))

    # Create edge labels
    for label in ("PREREQUISITE", "PARENT_OF", "RELATED_TO"):
        count = await session.execute(
            text(
                "SELECT count(*) FROM ag_catalog.ag_label "
                "WHERE name = :label AND graph = ("
                "  SELECT graphid FROM ag_catalog.ag_graph WHERE name = 'maestro_kg'"
                ")"
            ),
            {"label": label},
        )
        if count.scalar() == 0:
            await session.execute(text(f"SELECT create_elabel('maestro_kg', '{label}')"))


# ---------------------------------------------------------------------------
# Macro-node CRUD
# ---------------------------------------------------------------------------

async def add_macro_node(
    session: AsyncSession,
    *,
    course_id: uuid.UUID,
    label_it: str,
    difficulty: str,
    school_year: int,
    school_level: str,
    created_by: uuid.UUID,
    description: str | None = None,
    label_native: str | None = None,
    subject: str = "informatica",
    sort_order: int = 0,
) -> KGNode:
    """Create a macro-node in both the relational shadow table and AGE graph."""
    node = KGNode(
        id=uuid.uuid4(),
        course_id=course_id,
        node_type="macro",
        macro_id=None,
        label_it=label_it,
        label_native=label_native,
        description=description,
        difficulty=difficulty,
        bloom_level=None,
        school_year=school_year,
        school_level=school_level,
        subject=subject,
        sort_order=sort_order,
        is_active=True,
        created_by=created_by,
    )
    session.add(node)
    await session.flush()

    # Write to AGE graph
    await _cypher_create_node(session, node, "MacroNode")

    await log_audit_event(
        session,
        actor_id=str(created_by),
        actor_type="teacher",
        action="create_macro_node",
        entity_type="kg_node",
        entity_id=str(node.id),
        new_value={"label_it": label_it, "course_id": str(course_id)},
    )
    return node


async def add_micro_node(
    session: AsyncSession,
    *,
    macro_id: uuid.UUID,
    course_id: uuid.UUID,
    label_it: str,
    difficulty: str,
    school_year: int,
    school_level: str,
    created_by: uuid.UUID,
    description: str | None = None,
    label_native: str | None = None,
    bloom_level: str | None = None,
    sort_order: int = 0,
) -> KGNode:
    """Create a micro-node and its PARENT_OF edge atomically (C2 constraint)."""
    # Verify macro parent exists
    macro = await session.get(KGNode, macro_id)
    if macro is None or macro.node_type != "macro":
        raise NotFoundError("MacroNode", str(macro_id))

    node = KGNode(
        id=uuid.uuid4(),
        course_id=course_id,
        node_type="micro",
        macro_id=macro_id,
        label_it=label_it,
        label_native=label_native,
        description=description,
        difficulty=difficulty,
        bloom_level=bloom_level,
        school_year=school_year,
        school_level=school_level,
        sort_order=sort_order,
        is_active=True,
        created_by=created_by,
    )
    session.add(node)
    await session.flush()

    # Write to AGE graph: vertex + PARENT_OF edge
    await _cypher_create_node(session, node, "MicroNode")
    await _cypher_create_edge(
        session,
        source_id=macro_id,
        source_label="MacroNode",
        target_id=node.id,
        target_label="MicroNode",
        edge_label="PARENT_OF",
        properties={"id": str(uuid.uuid4())},
    )

    # Relational shadow edge for PARENT_OF
    parent_edge = KGEdge(
        course_id=course_id,
        edge_type="parent_of",
        source_node_id=macro_id,
        target_node_id=node.id,
        created_by=created_by,
    )
    session.add(parent_edge)
    await session.flush()

    await log_audit_event(
        session,
        actor_id=str(created_by),
        actor_type="teacher",
        action="create_micro_node",
        entity_type="kg_node",
        entity_id=str(node.id),
        new_value={
            "label_it": label_it,
            "macro_id": str(macro_id),
            "course_id": str(course_id),
        },
    )
    return node


# ---------------------------------------------------------------------------
# Prerequisite edge management (with DAG validation)
# ---------------------------------------------------------------------------

async def add_prerequisite_edge(
    session: AsyncSession,
    *,
    source_id: uuid.UUID,
    target_id: uuid.UUID,
    course_id: uuid.UUID,
    strength: str = "required",
    created_by: uuid.UUID,
) -> KGEdge:
    """Add a PREREQUISITE edge after verifying the DAG invariant (C1).

    source -[PREREQUISITE]-> target means "to understand target, you need source".
    """
    # Validate both nodes exist
    source = await session.get(KGNode, source_id)
    if source is None:
        raise NotFoundError("KGNode", str(source_id))
    target = await session.get(KGNode, target_id)
    if target is None:
        raise NotFoundError("KGNode", str(target_id))

    # DAG cycle check: would target -> ... -> source path exist?
    if await _would_create_cycle(session, source_id=source_id, target_id=target_id):
        raise DAGCycleError(str(source_id), str(target_id))

    # Relational shadow
    edge = KGEdge(
        course_id=course_id,
        edge_type="prerequisite",
        source_node_id=source_id,
        target_node_id=target_id,
        strength=strength,
        created_by=created_by,
    )
    session.add(edge)
    await session.flush()

    # AGE graph
    await _cypher_create_edge(
        session,
        source_id=source_id,
        source_label=_age_label(source.node_type),
        target_id=target_id,
        target_label=_age_label(target.node_type),
        edge_label="PREREQUISITE",
        properties={
            "id": str(edge.id),
            "strength": strength,
            "created_by": str(created_by),
        },
    )

    await log_audit_event(
        session,
        actor_id=str(created_by),
        actor_type="teacher",
        action="add_prerequisite_edge",
        entity_type="kg_edge",
        entity_id=str(edge.id),
        new_value={
            "source_node_id": str(source_id),
            "target_node_id": str(target_id),
            "strength": strength,
        },
    )
    return edge


async def remove_prerequisite_edge(
    session: AsyncSession,
    *,
    edge_id: uuid.UUID,
    removed_by: uuid.UUID,
) -> None:
    """Remove a prerequisite edge from both AGE graph and relational table."""
    edge = await session.get(KGEdge, edge_id)
    if edge is None or edge.edge_type != "prerequisite":
        raise NotFoundError("KGEdge", str(edge_id))

    # Remove from AGE graph
    await session.execute(
        text(
            "SELECT * FROM cypher('maestro_kg', $$ "
            "MATCH (a)-[e:PREREQUISITE]->(b) "
            "WHERE e.id = $edge_id "
            "DELETE e "
            "$$, :params) AS (result agtype)"
        ),
        {"params": _age_params({"edge_id": str(edge_id)})},
    )

    prev_value = {
        "source_node_id": str(edge.source_node_id),
        "target_node_id": str(edge.target_node_id),
    }
    await session.delete(edge)
    await session.flush()

    await log_audit_event(
        session,
        actor_id=str(removed_by),
        actor_type="teacher",
        action="remove_prerequisite_edge",
        entity_type="kg_edge",
        entity_id=str(edge_id),
        previous_value=prev_value,
    )


# ---------------------------------------------------------------------------
# Query operations
# ---------------------------------------------------------------------------

async def get_prerequisites(session: AsyncSession, node_id: uuid.UUID) -> list[KGNode]:
    """Get direct prerequisite nodes (1 hop) for a given node."""
    stmt = (
        select(KGNode)
        .join(KGEdge, KGEdge.source_node_id == KGNode.id)
        .where(
            KGEdge.target_node_id == node_id,
            KGEdge.edge_type == "prerequisite",
            KGNode.is_active.is_(True),
        )
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_dependents(session: AsyncSession, node_id: uuid.UUID) -> list[KGNode]:
    """Get nodes that depend on this node (nodes where this node is a prerequisite)."""
    stmt = (
        select(KGNode)
        .join(KGEdge, KGEdge.target_node_id == KGNode.id)
        .where(
            KGEdge.source_node_id == node_id,
            KGEdge.edge_type == "prerequisite",
            KGNode.is_active.is_(True),
        )
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_subgraph(session: AsyncSession, macro_id: uuid.UUID) -> list[KGNode]:
    """Get all active micro-nodes belonging to a macro-node, ordered by sort_order."""
    stmt = (
        select(KGNode)
        .where(
            KGNode.macro_id == macro_id,
            KGNode.node_type == "micro",
            KGNode.is_active.is_(True),
        )
        .order_by(KGNode.sort_order)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_node(session: AsyncSession, node_id: uuid.UUID) -> KGNode:
    """Get a single node by ID, raising NotFoundError if absent."""
    node = await session.get(KGNode, node_id)
    if node is None:
        raise NotFoundError("KGNode", str(node_id))
    return node


async def get_course_nodes(
    session: AsyncSession,
    course_id: uuid.UUID,
    *,
    active_only: bool = True,
) -> list[KGNode]:
    """Get all nodes for a course, optionally filtering by active status."""
    stmt = select(KGNode).where(KGNode.course_id == course_id)
    if active_only:
        stmt = stmt.where(KGNode.is_active.is_(True))
    stmt = stmt.order_by(KGNode.node_type.desc(), KGNode.sort_order)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_course_macro_nodes(
    session: AsyncSession,
    course_id: uuid.UUID,
) -> list[KGNode]:
    """Get all active macro-nodes for a course."""
    stmt = (
        select(KGNode)
        .where(
            KGNode.course_id == course_id,
            KGNode.node_type == "macro",
            KGNode.is_active.is_(True),
        )
        .order_by(KGNode.sort_order)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_course_edges(
    session: AsyncSession,
    course_id: uuid.UUID,
    *,
    edge_type: str | None = None,
) -> list[KGEdge]:
    """Get all edges for a course, optionally filtering by type."""
    stmt = select(KGEdge).where(KGEdge.course_id == course_id)
    if edge_type is not None:
        stmt = stmt.where(KGEdge.edge_type == edge_type)
    result = await session.execute(stmt)
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Node update / deactivation
# ---------------------------------------------------------------------------

async def update_node(
    session: AsyncSession,
    *,
    node_id: uuid.UUID,
    updated_by: uuid.UUID,
    **fields: Any,
) -> KGNode:
    """Update editable fields of a KG node (label, description, difficulty, etc.)."""
    node = await session.get(KGNode, node_id)
    if node is None:
        raise NotFoundError("KGNode", str(node_id))

    allowed_fields = {
        "label_it", "label_native", "description", "difficulty",
        "bloom_level", "sort_order", "subject",
    }
    prev_values: dict[str, Any] = {}
    new_values: dict[str, Any] = {}
    for key, value in fields.items():
        if key in allowed_fields and value is not None:
            prev_values[key] = getattr(node, key)
            setattr(node, key, value)
            new_values[key] = value

    if new_values:
        node.updated_at = datetime.now(timezone.utc)
        await session.flush()

        # Update AGE vertex properties
        age_label = _age_label(node.node_type)
        set_clauses = ", ".join(f"n.{k} = ${k}" for k in new_values)
        await session.execute(
            text(
                f"SELECT * FROM cypher('maestro_kg', $$ "
                f"MATCH (n:{age_label} {{id: $node_id}}) "
                f"SET {set_clauses} "
                f"$$, :params) AS (result agtype)"
            ),
            {"params": _age_params({"node_id": str(node_id), **{k: str(v) for k, v in new_values.items()}})},
        )

        await log_audit_event(
            session,
            actor_id=str(updated_by),
            actor_type="teacher",
            action="update_node",
            entity_type="kg_node",
            entity_id=str(node_id),
            previous_value=prev_values,
            new_value=new_values,
        )
    return node


async def deactivate_node(
    session: AsyncSession,
    *,
    node_id: uuid.UUID,
    deactivated_by: uuid.UUID,
) -> KGNode:
    """Soft-deactivate a node (C4: preserves references, hides from active views)."""
    node = await session.get(KGNode, node_id)
    if node is None:
        raise NotFoundError("KGNode", str(node_id))

    node.is_active = False
    node.updated_at = datetime.now(timezone.utc)
    await session.flush()

    # Update AGE
    age_label = _age_label(node.node_type)
    await session.execute(
        text(
            f"SELECT * FROM cypher('maestro_kg', $$ "
            f"MATCH (n:{age_label} {{id: $node_id}}) "
            f"SET n.is_active = false "
            f"$$, :params) AS (result agtype)"
        ),
        {"params": _age_params({"node_id": str(node_id)})},
    )

    await log_audit_event(
        session,
        actor_id=str(deactivated_by),
        actor_type="teacher",
        action="deactivate_node",
        entity_type="kg_node",
        entity_id=str(node_id),
        previous_value={"is_active": True},
        new_value={"is_active": False},
    )
    return node


# ---------------------------------------------------------------------------
# DAG validation
# ---------------------------------------------------------------------------

async def validate_dag(session: AsyncSession, course_id: uuid.UUID) -> bool:
    """Run full DAG validation (topological sort) on prerequisite edges for a course.

    Uses Kahn's algorithm on the relational shadow table for reliability.
    Returns True if valid, raises DAGCycleError if a cycle is detected.
    """
    edges_stmt = select(KGEdge).where(
        KGEdge.course_id == course_id,
        KGEdge.edge_type == "prerequisite",
    )
    result = await session.execute(edges_stmt)
    edges = list(result.scalars().all())

    if not edges:
        return True

    # Build adjacency and in-degree
    adj: dict[uuid.UUID, list[uuid.UUID]] = {}
    in_degree: dict[uuid.UUID, int] = {}
    all_nodes: set[uuid.UUID] = set()

    for edge in edges:
        all_nodes.add(edge.source_node_id)
        all_nodes.add(edge.target_node_id)
        adj.setdefault(edge.source_node_id, []).append(edge.target_node_id)
        in_degree.setdefault(edge.target_node_id, 0)
        in_degree[edge.target_node_id] = in_degree.get(edge.target_node_id, 0) + 1
        in_degree.setdefault(edge.source_node_id, 0)

    # Kahn's algorithm
    queue = [n for n in all_nodes if in_degree.get(n, 0) == 0]
    visited = 0

    while queue:
        node = queue.pop(0)
        visited += 1
        for neighbor in adj.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited != len(all_nodes):
        raise DAGCycleError("unknown", "unknown")

    return True


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _would_create_cycle(
    session: AsyncSession,
    *,
    source_id: uuid.UUID,
    target_id: uuid.UUID,
) -> bool:
    """Check if adding source->target edge would create a cycle.

    A cycle would exist if target can already reach source via prerequisite edges.
    Uses BFS on relational shadow table for reliability.
    """
    if source_id == target_id:
        return True

    # BFS from target following prerequisite edges (source direction)
    visited: set[uuid.UUID] = set()
    queue = [target_id]

    while queue:
        current = queue.pop(0)
        if current == source_id:
            return True
        if current in visited:
            continue
        visited.add(current)

        stmt = select(KGEdge.source_node_id).where(
            KGEdge.target_node_id == current,
            KGEdge.edge_type == "prerequisite",
        )
        result = await session.execute(stmt)
        for (prereq_id,) in result.all():
            if prereq_id not in visited:
                queue.append(prereq_id)

    return False


async def _cypher_create_node(session: AsyncSession, node: KGNode, label: str) -> None:
    """Create a vertex in the AGE graph."""
    props = {
        "id": str(node.id),
        "course_id": str(node.course_id),
        "label_it": node.label_it,
        "difficulty": node.difficulty,
        "school_year": node.school_year,
        "school_level": node.school_level,
        "sort_order": node.sort_order,
        "is_active": True,
        "created_by": str(node.created_by),
    }
    if node.node_type == "micro" and node.macro_id:
        props["macro_id"] = str(node.macro_id)
    if node.bloom_level:
        props["bloom_level"] = node.bloom_level
    if node.description:
        props["description"] = node.description

    # Build Cypher property string
    prop_assignments = ", ".join(f"{k}: ${k}" for k in props)
    await session.execute(
        text(
            f"SELECT * FROM cypher('maestro_kg', $$ "
            f"CREATE (n:{label} {{{prop_assignments}}}) "
            f"RETURN n "
            f"$$, :params) AS (node agtype)"
        ),
        {"params": _age_params(props)},
    )


async def _cypher_create_edge(
    session: AsyncSession,
    *,
    source_id: uuid.UUID,
    source_label: str,
    target_id: uuid.UUID,
    target_label: str,
    edge_label: str,
    properties: dict[str, str] | None = None,
) -> None:
    """Create an edge in the AGE graph."""
    props = properties or {}
    prop_str = ""
    if props:
        prop_assignments = ", ".join(f"{k}: ${k}" for k in props)
        prop_str = f" {{{prop_assignments}}}"

    params = {
        "source_id": str(source_id),
        "target_id": str(target_id),
        **props,
    }

    await session.execute(
        text(
            f"SELECT * FROM cypher('maestro_kg', $$ "
            f"MATCH (a:{source_label} {{id: $source_id}}), "
            f"(b:{target_label} {{id: $target_id}}) "
            f"CREATE (a)-[:{edge_label}{prop_str}]->(b) "
            f"$$, :params) AS (result agtype)"
        ),
        {"params": _age_params(params)},
    )


def _age_label(node_type: str) -> str:
    """Convert node_type ('macro'/'micro') to AGE vertex label."""
    return "MacroNode" if node_type == "macro" else "MicroNode"


def _age_params(params: dict[str, Any]) -> str:
    """Format parameters as an agtype map for AGE Cypher queries.

    AGE expects parameters as a JSON-like agtype string.
    """
    import json
    return json.dumps(params)
