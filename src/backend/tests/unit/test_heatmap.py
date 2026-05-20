"""Unit tests for heatmap aggregation (heatmap.py).

Tests the worst-state rollup logic using pure in-memory computation.
No database required.
"""

import pytest

from maestro.kmm.heatmap import compute_macro_rollup_from_states, worst_state
from maestro.kmm.models import MasteryState


class TestWorstState:
    """Test the worst_state helper against canonical ordering (ADR-005)."""

    def test_single_state(self) -> None:
        assert worst_state(["consolidato"]) == "consolidato"

    def test_lacuna_is_worst(self) -> None:
        all_states = [s.value for s in MasteryState]
        assert worst_state(all_states) == "lacuna"

    def test_empty_defaults_to_non_introdotto(self) -> None:
        assert worst_state([]) == "non_introdotto"

    def test_lacuna_beats_everything(self) -> None:
        states = ["consolidato", "da_consolidare", "introdotto", "lacuna"]
        assert worst_state(states) == "lacuna"

    def test_in_recupero_worse_than_non_introdotto(self) -> None:
        states = ["non_introdotto", "in_recupero"]
        assert worst_state(states) == "in_recupero"

    def test_non_introdotto_worse_than_introdotto(self) -> None:
        states = ["introdotto", "non_introdotto"]
        assert worst_state(states) == "non_introdotto"

    def test_da_consolidare_worse_than_consolidato(self) -> None:
        states = ["consolidato", "da_consolidare"]
        assert worst_state(states) == "da_consolidare"

    def test_all_consolidato(self) -> None:
        states = ["consolidato"] * 10
        assert worst_state(states) == "consolidato"


class TestMacroRollup:
    """Test compute_macro_rollup_from_states with various scenarios."""

    def test_all_consolidato(self) -> None:
        node_states = {
            "micro-1": "consolidato",
            "micro-2": "consolidato",
            "micro-3": "consolidato",
        }
        rollup = compute_macro_rollup_from_states(
            "macro-A", ["micro-1", "micro-2", "micro-3"], node_states
        )
        assert rollup.worst_state == "consolidato"
        assert rollup.total_micros == 3
        assert rollup.micros_per_state == {"consolidato": 3}

    def test_one_lacuna_among_consolidato(self) -> None:
        """ADR-002 Section 4: one lacuna out of 10 makes macro = lacuna."""
        micro_ids = [f"micro-{i}" for i in range(10)]
        node_states = {nid: "consolidato" for nid in micro_ids}
        node_states["micro-0"] = "lacuna"

        rollup = compute_macro_rollup_from_states("macro-A", micro_ids, node_states)
        assert rollup.worst_state == "lacuna"
        assert rollup.total_micros == 10
        assert rollup.micros_per_state["lacuna"] == 1
        assert rollup.micros_per_state["consolidato"] == 9

    def test_mixed_states(self) -> None:
        node_states = {
            "m1": "introdotto",
            "m2": "da_consolidare",
            "m3": "non_introdotto",
            "m4": "consolidato",
        }
        rollup = compute_macro_rollup_from_states(
            "macro-B", ["m1", "m2", "m3", "m4"], node_states
        )
        # non_introdotto (2) is worse than introdotto (3)
        assert rollup.worst_state == "non_introdotto"
        assert rollup.total_micros == 4

    def test_missing_node_defaults_to_non_introdotto(self) -> None:
        """If a micro-node has no state record, treat as non_introdotto."""
        node_states = {"m1": "consolidato"}
        rollup = compute_macro_rollup_from_states(
            "macro-C", ["m1", "m2"], node_states
        )
        assert rollup.worst_state == "non_introdotto"
        assert rollup.micros_per_state["non_introdotto"] == 1
        assert rollup.micros_per_state["consolidato"] == 1

    def test_in_recupero_worse_than_non_introdotto_in_rollup(self) -> None:
        node_states = {
            "m1": "non_introdotto",
            "m2": "in_recupero",
            "m3": "consolidato",
        }
        rollup = compute_macro_rollup_from_states(
            "macro-D", ["m1", "m2", "m3"], node_states
        )
        assert rollup.worst_state == "in_recupero"

    def test_empty_micro_list(self) -> None:
        rollup = compute_macro_rollup_from_states("macro-E", [], {})
        assert rollup.worst_state == "non_introdotto"
        assert rollup.total_micros == 0
        assert rollup.micros_per_state == {}

    def test_progress_indicator_counts(self) -> None:
        """Verify the '7/10 consolidati' progress indicator data (ADR-002 Section 4)."""
        micro_ids = [f"m{i}" for i in range(10)]
        node_states = {nid: "consolidato" for nid in micro_ids}
        node_states["m0"] = "lacuna"
        node_states["m1"] = "da_consolidare"
        node_states["m2"] = "in_recupero"

        rollup = compute_macro_rollup_from_states("macro-F", micro_ids, node_states)
        assert rollup.micros_per_state["consolidato"] == 7
        assert rollup.micros_per_state["lacuna"] == 1
        assert rollup.micros_per_state["da_consolidare"] == 1
        assert rollup.micros_per_state["in_recupero"] == 1
        assert rollup.worst_state == "lacuna"
