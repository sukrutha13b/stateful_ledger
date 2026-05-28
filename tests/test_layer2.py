import pytest
from unittest.mock import patch

from ledger.schema import VerifiedResponse, Paragraph, Claim
from engine.layer2 import run_claim_classification, detect_overconfidence

class TestLayer2:
    def test_claim_classification_empty_claims(self):
        response = VerifiedResponse(paragraphs=[Paragraph(text="Hello", claims=[])])
        updated = run_claim_classification(response)
        assert len(updated.paragraphs[0].claims) == 0

    @patch("engine.layer2.call_gemini")
    def test_claim_classification_all_grounded(self, mock_call_gemini):
        claim = Claim(claim_id="c1", text="Test")
        response = VerifiedResponse(paragraphs=[Paragraph(claims=[claim])])
        
        mock_call_gemini.return_value = {
            "classified_claims": [
                {"claim_id": "c1", "classification": "grounded", "sources": ["src"]}
            ]
        }
        
        updated = run_claim_classification(response)
        c = updated.paragraphs[0].claims[0]
        assert c.classification == "grounded"
        assert c.sources == ["src"]

    @patch("engine.layer2.call_gemini")
    def test_claim_classification_mixed(self, mock_call_gemini):
        claim1 = Claim(claim_id="c1", text="Grounded")
        claim2 = Claim(claim_id="c2", text="Contested")
        claim3 = Claim(claim_id="c3", text="Unverified")
        response = VerifiedResponse(paragraphs=[Paragraph(claims=[claim1, claim2, claim3])])
        
        mock_call_gemini.return_value = {
            "classified_claims": [
                {"claim_id": "c1", "classification": "grounded"},
                {"claim_id": "c2", "classification": "contested"},
                {"claim_id": "c3", "classification": "unverified"}
            ]
        }
        
        updated = run_claim_classification(response)
        assert updated.paragraphs[0].claims[0].classification == "grounded"
        assert updated.paragraphs[0].claims[1].classification == "contested"
        assert updated.paragraphs[0].claims[2].classification == "unverified"

    @patch("engine.layer2.call_gemini")
    def test_claim_classification_api_failure(self, mock_call_gemini):
        claim = Claim(claim_id="c1", text="Test")
        response = VerifiedResponse(paragraphs=[Paragraph(claims=[claim])])
        
        mock_call_gemini.return_value = {"error": "API Error"}
        
        updated = run_claim_classification(response)
        assert updated.paragraphs[0].claims[0].classification == "unverified"

    @patch("engine.layer2.call_gemini")
    def test_claim_classification_merges_perspectives(self, mock_call_gemini):
        claim = Claim(claim_id="c1", text="Test")
        response = VerifiedResponse(paragraphs=[Paragraph(claims=[claim])])
        
        mock_call_gemini.return_value = {
            "classified_claims": [
                {"claim_id": "c1", "classification": "contested", "perspectives": ["P1", "P2"]}
            ]
        }
        
        updated = run_claim_classification(response)
        assert updated.paragraphs[0].claims[0].perspectives == ["P1", "P2"]

    @patch("engine.layer2.call_gemini")
    def test_claim_classification_merges_sources(self, mock_call_gemini):
        claim = Claim(claim_id="c1", text="Test")
        response = VerifiedResponse(paragraphs=[Paragraph(claims=[claim])])
        
        mock_call_gemini.return_value = {
            "classified_claims": [
                {"claim_id": "c1", "classification": "grounded", "sources": ["S1"]}
            ]
        }
        
        updated = run_claim_classification(response)
        assert updated.paragraphs[0].claims[0].sources == ["S1"]

    @patch("engine.layer2.call_gemini")
    def test_claim_classification_unknown_id_ignored(self, mock_call_gemini):
        claim = Claim(claim_id="c1", text="Test", classification="unverified")
        response = VerifiedResponse(paragraphs=[Paragraph(claims=[claim])])
        
        # API returns an ID we don't have
        mock_call_gemini.return_value = {
            "classified_claims": [
                {"claim_id": "c_unknown", "classification": "grounded"}
            ]
        }
        
        updated = run_claim_classification(response)
        # Should stay as it was (unverified)
        assert updated.paragraphs[0].claims[0].classification == "unverified"

    def test_detect_overconfidence_flagged(self):
        claim = Claim(classification="contested")
        response = VerifiedResponse(paragraphs=[Paragraph(step_type="established_fact", claims=[claim])])
        updated = detect_overconfidence(response)
        assert updated.paragraphs[0].claims[0].overconfidence_flag is True

    def test_detect_overconfidence_not_flagged(self):
        claim = Claim(classification="contested")
        response = VerifiedResponse(paragraphs=[Paragraph(step_type="inference", claims=[claim])])
        updated = detect_overconfidence(response)
        assert updated.paragraphs[0].claims[0].overconfidence_flag is False

    def test_detect_overconfidence_grounded_not_flagged(self):
        claim = Claim(classification="grounded")
        response = VerifiedResponse(paragraphs=[Paragraph(step_type="established_fact", claims=[claim])])
        updated = detect_overconfidence(response)
        assert updated.paragraphs[0].claims[0].overconfidence_flag is False
