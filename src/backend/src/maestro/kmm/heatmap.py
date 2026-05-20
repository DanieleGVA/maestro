"""Heatmap aggregation for teacher dashboard.

Computes class-level and student-level heatmaps using the canonical
worst-state rollup rule (ADR-002 Section 4, ADR-005 Conflict 3).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from maestro.kmm.models import MasteryState, StudentNodeState
from maestro.kmm.state_machine import STATE_ORDER


@dataclass
class MacroRollup:
    """Rollup result for a single macro-node."""

    macro_node_id: str
    worst_state: str
    total_micros: int
    micros_per_state: dict[str, int] = field(default_factory=dict)


@dataclass
class StudentHeatmap:
    """Full knowledge map for one student with per-node state and macro rollups."""

    student_id: str
    course_id: str
    node_states: dict[str, str]  # node_id -> current_state
    macro_rollups: list[MacroRollup] = field(default_factory=list)


@dataclass
class ClassNodeSummary:
    """Per-node summary across a class: count of students in each state."""

    node_id: str
    counts_per_state: dict[str, int] = field(default_factory=dict)
    total_students: int = 0


@dataclass
class ClassHeatmap:
    """Class-level heatmap: for each node, how many students are in each state."""

    class_id: str
    course_id: str
    node_summaries: list[ClassNodeSummary] = field(default_factory=list)


def worst_state(states: list[str]) -> str:
    """Return the worst state from a list using canonical ordering (ADR-005)."""
    if not states:
        return MasteryState.non_introdotto.value
    return min(states, key=lambda s: STATE_ORDER.get(s, 2))


async def get_student_heatmap(
    session: AsyncSession,
    student_id: str,
    course_id: str,
    macro_structure: list[dict] | None = None,
) -> StudentHeatmap:
    """Build a student heatmap with optional macro rollups.

    Args:
        macro_structure: list of {"macro_node_id": str, "micro_node_ids": [str]}
            If provided, macro rollups are computed.
    """
    stmt = select(StudentNodeState).where(
        StudentNodeState.student_id == uuid.UUID(student_id),
        StudentNodeState.course_id == uuid.UUID(course_id),
    )
    result = await session.execute(stmt)
    rows = result.scalars().all()

    node_states = {row.node_id: row.current_state for row in rows}

    heatmap = StudentHeatmap(
        student_id=student_id,
        course_id=course_id,
        node_states=node_states,
    )

    if macro_structure:
        for macro in macro_structure:
            rollup = compute_macro_rollup_from_states(
                macro["macro_node_id"],
                macro["micro_node_ids"],
                node_states,
            )
            heatmap.macro_rollups.append(rollup)

    return heatmap


async def get_class_heatmap(
    session: AsyncSession,
    student_ids: list[str],
    course_id: str,
) -> ClassHeatmap:
    """Build a class-level heatmap: per-node student counts by state.

    Args:
        student_ids: list of student UUIDs in the class.
        course_id: course UUID.
    """
    student_uuids = [uuid.UUID(sid) for sid in student_ids]

    stmt = (
        select(
            StudentNodeState.node_id,
            StudentNodeState.current_state,
            func.count().label("cnt"),
        )
        .where(
            StudentNodeState.student_id.in_(student_uuids),
            StudentNodeState.course_id == uuid.UUID(course_id),
        )
        .group_by(StudentNodeState.node_id, StudentNodeState.current_state)
    )
    result = await session.execute(stmt)
    rows = result.all()

    # Aggregate into per-node summaries
    node_data: dict[str, dict[str, int]] = {}
    for row in rows:
        nid = row.node_id
        if nid not in node_data:
            node_data[nid] = {}
        node_data[nid][row.current_state] = row.cnt

    summaries = []
    for nid, counts in sorted(node_data.items()):
        total = sum(counts.values())
        summaries.append(
            ClassNodeSummary(node_id=nid, counts_per_state=counts, total_students=total)
        )

    return ClassHeatmap(
        class_id=",".join(student_ids[:5]),  # Simplified class identifier
        course_id=course_id,
        node_summaries=summaries,
    )


def compute_macro_rollup_from_states(
    macro_node_id: str,
    micro_node_ids: list[str],
    node_states: dict[str, str],
) -> MacroRollup:
    """Compute macro rollup from pre-fetched micro-node states.

    Uses worst-state rule (ADR-005 Conflict 3).
    """
    micro_states = [
        node_states.get(nid, MasteryState.non_introdotto.value)
        for nid in micro_node_ids
    ]

    counts: dict[str, int] = {}
    for s in micro_states:
        counts[s] = counts.get(s, 0) + 1

    return MacroRollup(
        macro_node_id=macro_node_id,
        worst_state=worst_state(micro_states),
        total_micros=len(micro_node_ids),
        micros_per_state=counts,
    )


async def get_macro_rollup(
    session: AsyncSession,
    student_id: str,
    course_id: str,
    macro_node_id: str,
    micro_node_ids: list[str],
) -> MacroRollup:
    """Compute macro rollup for a single macro-node from the database."""
    stmt = select(StudentNodeState).where(
        StudentNodeState.student_id == uuid.UUID(student_id),
        StudentNodeState.course_id == uuid.UUID(course_id),
        StudentNodeState.node_id.in_(micro_node_ids),
    )
    result = await session.execute(stmt)
    rows = result.scalars().all()

    node_states = {row.node_id: row.current_state for row in rows}
    return compute_macro_rollup_from_states(macro_node_id, micro_node_ids, node_states)
