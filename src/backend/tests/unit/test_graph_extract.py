"""Unit tests for _extract_text and additional graph helper functions."""

from maestro.orchestrator.graph import _extract_text


class TestExtractText:
    def test_flat_dict(self) -> None:
        content = {"text": "Hello", "code": "print()"}
        result = _extract_text(content)
        assert "Hello" in result
        assert "print()" in result

    def test_nested_dict(self) -> None:
        content = {"outer": {"inner": "deep value"}}
        result = _extract_text(content)
        assert "deep value" in result

    def test_list_of_strings(self) -> None:
        content = {"items": ["alpha", "beta"]}
        result = _extract_text(content)
        assert "alpha" in result
        assert "beta" in result

    def test_list_of_dicts(self) -> None:
        content = {"blocks": [{"text": "block1"}, {"text": "block2"}]}
        result = _extract_text(content)
        assert "block1" in result
        assert "block2" in result

    def test_deeply_nested(self) -> None:
        content = {
            "l1": {
                "l2": [
                    {"l3": {"text": "found"}}
                ]
            }
        }
        result = _extract_text(content)
        assert "found" in result

    def test_mixed_types_skips_non_string(self) -> None:
        content = {"num": 42, "flag": True, "text": "actual"}
        result = _extract_text(content)
        assert "actual" in result
        assert "42" not in result

    def test_empty_dict(self) -> None:
        assert _extract_text({}) == ""
