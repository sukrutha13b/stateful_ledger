"""tests/test_json_parser.py - Unit tests for utils/json_parser.py (Phase 3)."""
import pytest

from utils.json_parser import safe_parse_json


class TestParseCleanJson:
    """Direct, well-formed JSON strings."""

    def test_simple_object(self):
        assert safe_parse_json('{"a": 1}') == {"a": 1}

    def test_simple_string_values(self):
        result = safe_parse_json('{"name": "Alice", "age": 30}')
        assert result == {"name": "Alice", "age": 30}


class TestParseJsonWithMarkdownFences:
    """JSON wrapped in ```json ... ``` fences."""

    def test_json_fence(self):
        text = '```json\n{"a": 1}\n```'
        assert safe_parse_json(text) == {"a": 1}

    def test_plain_fence(self):
        text = '```\n{"a": 1}\n```'
        assert safe_parse_json(text) == {"a": 1}

    def test_fence_with_whitespace(self):
        text = '```json  \n  {"key": "value"}  \n```  '
        assert safe_parse_json(text) == {"key": "value"}


class TestParseJsonWithPreamble:
    """JSON preceded by natural-language text."""

    def test_preamble_text(self):
        text = 'Here is the JSON:\n{"a": 1}'
        assert safe_parse_json(text) == {"a": 1}

    def test_preamble_and_postamble(self):
        text = 'Sure! Here you go:\n{"b": 2}\nHope that helps!'
        assert safe_parse_json(text) == {"b": 2}


class TestParseJsonArray:
    """Top-level JSON arrays."""

    def test_simple_array(self):
        assert safe_parse_json("[1, 2, 3]") == [1, 2, 3]

    def test_array_of_objects(self):
        text = '[{"id": 1}, {"id": 2}]'
        result = safe_parse_json(text)
        assert len(result) == 2
        assert result[0]["id"] == 1


class TestParseMalformedJson:
    """Completely unparseable input."""

    def test_plain_text_returns_none(self):
        assert safe_parse_json("not json at all") is None

    def test_truncated_json_returns_none(self):
        assert safe_parse_json('{"a": ') is None


class TestParseEmptyString:
    """Edge case: empty or whitespace-only input."""

    def test_empty_string_returns_none(self):
        assert safe_parse_json("") is None

    def test_whitespace_returns_none(self):
        assert safe_parse_json("   \n\t  ") is None


class TestParseNoneInput:
    """Edge case: None or non-string input."""

    def test_none_returns_none(self):
        assert safe_parse_json(None) is None

    def test_integer_returns_none(self):
        assert safe_parse_json(42) is None

    def test_list_returns_none(self):
        assert safe_parse_json([1, 2]) is None


class TestParseNestedJson:
    """Complex, deeply nested structures."""

    def test_nested_object(self):
        text = '{"paragraphs": [{"index": 0, "claims": [{"text": "X", "tag": "inferred"}]}]}'
        result = safe_parse_json(text)
        assert result["paragraphs"][0]["claims"][0]["text"] == "X"

    def test_nested_inside_markdown_fence(self):
        text = '```json\n{"outer": {"inner": [1, 2, 3]}}\n```'
        result = safe_parse_json(text)
        assert result["outer"]["inner"] == [1, 2, 3]
