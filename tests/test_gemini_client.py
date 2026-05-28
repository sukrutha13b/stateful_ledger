"""tests/test_gemini_client.py — Unit tests for engine/gemini_client.py (Phase 3).

All tests mock the Gemini API to avoid real network calls.
"""
import pytest
from unittest.mock import patch, MagicMock

# We must patch the module-level `client` object inside gemini_client,
# so we import the module itself rather than just the function.
import engine.gemini_client as gc
from engine.gemini_client import call_gemini


class TestCallGeminiSuccess:
    """Successful API calls return parsed dicts."""

    @patch.object(gc.client.models, "generate_content")
    def test_returns_parsed_dict(self, mock_gen):
        mock_response = MagicMock()
        mock_response.text = '{"result": "ok"}'
        mock_gen.return_value = mock_response

        result = call_gemini("system", "user")
        assert result == {"result": "ok"}
        mock_gen.assert_called_once()


class TestCallGeminiRetryOnError:
    """Retries on transient failures with exponential backoff."""

    @patch("engine.gemini_client.time.sleep")  # Don't actually sleep in tests
    @patch.object(gc.client.models, "generate_content")
    def test_retries_and_succeeds(self, mock_gen, mock_sleep):
        # First call raises, second succeeds
        mock_response = MagicMock()
        mock_response.text = '{"retried": true}'
        mock_gen.side_effect = [
            Exception("transient error"),
            mock_response,
        ]

        result = call_gemini("system", "user", max_retries=3)
        assert result == {"retried": True}
        assert mock_gen.call_count == 2
        mock_sleep.assert_called_once_with(1)  # 2^0 = 1


class TestCallGeminiAllRetriesFail:
    """All retries exhausted returns an error dict."""

    @patch("engine.gemini_client.time.sleep")
    @patch.object(gc.client.models, "generate_content")
    def test_returns_error_dict(self, mock_gen, mock_sleep):
        mock_gen.side_effect = Exception("persistent failure")

        result = call_gemini("system", "user", max_retries=3)
        assert "error" in result
        assert "persistent failure" in result["error"]
        assert result["raw_text"] == ""
        assert mock_gen.call_count == 3


class TestCallGeminiJsonParseFailure:
    """API returns non-JSON text → error with raw_text."""

    @patch.object(gc.client.models, "generate_content")
    def test_returns_error_with_raw_text(self, mock_gen):
        mock_response = MagicMock()
        mock_response.text = "This is not JSON at all"
        mock_gen.return_value = mock_response

        result = call_gemini("system", "user")
        assert result["error"] == "JSON parse failed"
        assert result["raw_text"] == "This is not JSON at all"


class TestCallGeminiSearchGrounding:
    """When use_search_grounding=True, config includes GoogleSearch tool."""

    @patch.object(gc.client.models, "generate_content")
    def test_search_grounding_flag(self, mock_gen):
        mock_response = MagicMock()
        mock_response.text = '{"grounded": true}'
        mock_gen.return_value = mock_response

        result = call_gemini("system", "user", use_search_grounding=True)
        assert result == {"grounded": True}

        # Inspect the config passed to generate_content
        call_kwargs = mock_gen.call_args
        config = call_kwargs.kwargs.get("config") or call_kwargs[1].get("config")
        assert config.tools is not None
        assert len(config.tools) == 1
