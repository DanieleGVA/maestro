"""Unit tests for MaestroState and reducers (orchestrator/state.py)."""

from maestro.orchestrator.state import MaestroState, _merge_lists


class TestMergeLists:
    def test_appends_items(self) -> None:
        left = [1, 2]
        right = [3, 4]
        assert _merge_lists(left, right) == [1, 2, 3, 4]

    def test_empty_left(self) -> None:
        assert _merge_lists([], [1]) == [1]

    def test_empty_right(self) -> None:
        assert _merge_lists([1], []) == [1]

    def test_both_empty(self) -> None:
        assert _merge_lists([], []) == []


class TestMaestroState:
    def test_state_is_typed_dict(self) -> None:
        """MaestroState should be usable as a dict."""
        state: MaestroState = {
            "request_type": "gap_closure",
            "student_internal_id": "stu-1",
            "agent_trace": [],
            "errors": [],
        }
        assert state["request_type"] == "gap_closure"

    def test_state_total_false(self) -> None:
        """MaestroState uses total=False, so all fields are optional."""
        state: MaestroState = {}
        assert state.get("request_type") is None
