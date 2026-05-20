"""Curriculum management: load curriculum structure, compute learning paths.

Provides operations for loading teacher-defined curriculum structures into the KG
and computing student learning paths that respect prerequisite ordering.
"""

from __future__ import annotations

import uuid
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.kg.graph_ops import (
    add_macro_node,
    add_micro_node,
    add_prerequisite_edge,
    get_course_edges,
    get_course_macro_nodes,
    get_node,
    get_subgraph,
)
from maestro.kg.models import KGEdge, KGNode


async def load_curriculum(
    session: AsyncSession,
    curriculum_data: dict,
    *,
    course_id: uuid.UUID,
    teacher_id: uuid.UUID,
) -> list[KGNode]:
    """Load a curriculum structure into the KG.

    Expected curriculum_data format:
    {
        "macro_nodes": [
            {
                "label_it": "Concetto di algoritmo",
                "difficulty": "base",
                "school_year": 3,
                "school_level": "triennio_secondo_grado",
                "description": "...",
                "sort_order": 1,
                "micro_nodes": [
                    {
                        "label_it": "Definizione di algoritmo",
                        "difficulty": "base",
                        "bloom_level": "remember",
                        "sort_order": 1
                    },
                    ...
                ]
            },
            ...
        ],
        "prerequisites": [
            {
                "source_label": "Concetto di algoritmo",
                "target_label": "Strutture di controllo",
                "strength": "required"
            },
            ...
        ]
    }
    """
    created_nodes: list[KGNode] = []
    label_to_id: dict[str, uuid.UUID] = {}

    # Create macro-nodes and their micro-children
    for macro_data in curriculum_data.get("macro_nodes", []):
        macro = await add_macro_node(
            session,
            course_id=course_id,
            label_it=macro_data["label_it"],
            difficulty=macro_data.get("difficulty", "base"),
            school_year=macro_data.get("school_year", 1),
            school_level=macro_data.get("school_level", "triennio_secondo_grado"),
            created_by=teacher_id,
            description=macro_data.get("description"),
            sort_order=macro_data.get("sort_order", 0),
        )
        created_nodes.append(macro)
        label_to_id[macro_data["label_it"]] = macro.id

        for micro_data in macro_data.get("micro_nodes", []):
            micro = await add_micro_node(
                session,
                macro_id=macro.id,
                course_id=course_id,
                label_it=micro_data["label_it"],
                difficulty=micro_data.get("difficulty", macro_data.get("difficulty", "base")),
                school_year=macro_data.get("school_year", 1),
                school_level=macro_data.get("school_level", "triennio_secondo_grado"),
                created_by=teacher_id,
                description=micro_data.get("description"),
                bloom_level=micro_data.get("bloom_level"),
                sort_order=micro_data.get("sort_order", 0),
            )
            created_nodes.append(micro)
            label_to_id[micro_data["label_it"]] = micro.id

    # Create prerequisite edges
    for prereq in curriculum_data.get("prerequisites", []):
        source_label = prereq["source_label"]
        target_label = prereq["target_label"]
        source_id = label_to_id.get(source_label)
        target_id = label_to_id.get(target_label)

        if source_id and target_id:
            await add_prerequisite_edge(
                session,
                source_id=source_id,
                target_id=target_id,
                course_id=course_id,
                strength=prereq.get("strength", "required"),
                created_by=teacher_id,
            )

    return created_nodes


async def get_learning_path(
    session: AsyncSession,
    course_id: uuid.UUID,
) -> list[KGNode]:
    """Compute a topologically sorted learning path for a course.

    Returns nodes in an order that respects all prerequisite constraints.
    Uses Kahn's algorithm on the prerequisite edges.
    """
    # Get all nodes and prerequisite edges for the course
    nodes_stmt = (
        select(KGNode)
        .where(
            KGNode.course_id == course_id,
            KGNode.is_active.is_(True),
        )
    )
    result = await session.execute(nodes_stmt)
    all_nodes = {n.id: n for n in result.scalars().all()}

    edges = await get_course_edges(session, course_id, edge_type="prerequisite")

    if not edges:
        # No prerequisites: return nodes ordered by type (macro first) then sort_order
        return sorted(
            all_nodes.values(),
            key=lambda n: (0 if n.node_type == "macro" else 1, n.sort_order),
        )

    # Kahn's algorithm for topological sort
    adj: dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    in_degree: dict[uuid.UUID, int] = {node_id: 0 for node_id in all_nodes}

    for edge in edges:
        if edge.source_node_id in all_nodes and edge.target_node_id in all_nodes:
            adj[edge.source_node_id].append(edge.target_node_id)
            in_degree[edge.target_node_id] = in_degree.get(edge.target_node_id, 0) + 1

    # Start with nodes that have no prerequisites
    queue = sorted(
        [nid for nid, deg in in_degree.items() if deg == 0],
        key=lambda nid: (
            0 if all_nodes[nid].node_type == "macro" else 1,
            all_nodes[nid].sort_order,
        ),
    )

    ordered: list[KGNode] = []
    while queue:
        node_id = queue.pop(0)
        if node_id in all_nodes:
            ordered.append(all_nodes[node_id])

        for neighbor in sorted(
            adj.get(node_id, []),
            key=lambda nid: all_nodes[nid].sort_order if nid in all_nodes else 0,
        ):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Append any remaining nodes not in the prerequisite graph
    ordered_ids = {n.id for n in ordered}
    for node in sorted(all_nodes.values(), key=lambda n: n.sort_order):
        if node.id not in ordered_ids:
            ordered.append(node)

    return ordered


async def get_node_detail(
    session: AsyncSession,
    node_id: uuid.UUID,
) -> dict:
    """Get detailed information about a node including prerequisites and dependents."""
    from maestro.kg.graph_ops import get_dependents, get_prerequisites

    node = await get_node(session, node_id)
    prerequisites = await get_prerequisites(session, node_id)
    dependents = await get_dependents(session, node_id)

    result: dict = {
        "node": node,
        "prerequisites": prerequisites,
        "dependents": dependents,
    }

    # If macro-node, include children
    if node.node_type == "macro":
        children = await get_subgraph(session, node_id)
        result["children"] = children

    # If micro-node, include parent info
    if node.node_type == "micro" and node.macro_id:
        parent = await get_node(session, node.macro_id)
        result["macro_parent"] = parent

    return result
