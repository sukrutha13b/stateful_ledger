"""tests/test_edge_cases.py — Integration and edge case tests (Phase 11).

Tests for graceful degradation when the LLM or APIs fail to produce
expected outputs (e.g., malformed JSON, empty grounding, ambiguous prompts).
"""
import pytest
from unittest.mock import patch, MagicMock

from app import _parse_verified_response
from ledger.schema import Ledger, InteractionTurn, VerifiedResponse
from engine.layer2 import run_claim_classification


import engine.gemini_client as gc

class TestMalformedJSONGracefulDegradation:
    """If the LLM returns malformed JSON, the client handles it."""
    
    @patch.object(gc.client.models, "generate_content")
    def test_client_returns_error_dict(self, mock_gen):
        mock_response = MagicMock()
        mock_response.text = "This is just raw text, not JSON at all."
        mock_gen.return_value = mock_response
        
        from engine.gemini_client import call_gemini
        result = call_gemini("system", "user")
        
        assert "error" in result
        assert result["error"] == "JSON parse failed"
        assert result["raw_text"] == "This is just raw text, not JSON at all."
        
    def test_parse_verified_response_with_missing_keys(self):
        """Even if the JSON is valid but misses keys, it shouldn't crash."""
        raw = {"paragraphs": [{"text": "Hello"}]} # Missing claims and step_type and index
        vr = _parse_verified_response(raw)
        
        assert len(vr.paragraphs) == 1
        assert vr.paragraphs[0].text == "Hello"
        assert vr.paragraphs[0].index == 0
        assert vr.paragraphs[0].claims == []
        assert vr.paragraphs[0].step_type is None


class TestEmptyGroundingResults:
    """If grounding fails or returns empty, all claims default to unverified."""

    @patch("engine.layer2.call_gemini")
    def test_layer2_empty_grounding_defaults_unverified(self, mock_call):
        # Simulate an API error or empty result from the search grounding call
        mock_call.return_value = {"error": "Search failed"}
        
        from ledger.schema import Paragraph, Claim
        vr = VerifiedResponse(
            paragraphs=[
                Paragraph(
                    text="The capital of Moon is Cheese.",
                    claims=[Claim(text="Capital is Cheese")]
                )
            ]
        )
        
        result = run_claim_classification(vr)
        
        assert len(result.paragraphs[0].claims) == 1
        assert result.paragraphs[0].claims[0].classification == "unverified"

    @patch("engine.layer2.call_gemini")
    def test_layer2_partial_grounding(self, mock_call):
        # Simulate partial classification (one classified, one missing)
        mock_call.return_value = {
            "classified_claims": [
                {"claim_id": "c1", "classification": "grounded"}
            ]
        }
        
        from ledger.schema import Paragraph, Claim
        vr = VerifiedResponse(
            paragraphs=[
                Paragraph(
                    claims=[
                        Claim(claim_id="c1", text="Grounded claim"),
                        Claim(claim_id="c2", text="Ignored by LLM")
                    ]
                )
            ]
        )
        
        result = run_claim_classification(vr)
        
        # c1 should be grounded
        assert result.paragraphs[0].claims[0].classification == "grounded"
        # c2 should default to unverified
        assert result.paragraphs[0].claims[1].classification == "unverified"


class TestAmbiguousPrompts:
    """If a prompt is completely ambiguous, the rubric generator should fallback safely."""
    
    @patch.object(gc.client.models, "generate_content")
    def test_rubric_generator_fallback(self, mock_gen):
        mock_response = MagicMock()
        # If the model gets confused and returns empty or invalid JSON
        mock_response.text = '{"nonsense": true}'
        mock_gen.return_value = mock_response
        
        from engine.gemini_client import call_gemini
        from ui.rubric import process_rubric_response
        from ledger.manager import init_ledger
        
        api_result = call_gemini("sys", "user")
        ledger = init_ledger()
        
        # We simulate the fallback logic that happens in app.py
        if "error" not in api_result and "goal_type" not in api_result:
            api_result = {"error": "missing keys"}
            
        success = process_rubric_response(api_result, ledger)
        
        # It should return False because it failed to process valid goal_type
        assert success is False
