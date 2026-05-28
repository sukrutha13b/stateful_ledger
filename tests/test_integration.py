import pytest
from app import _parse_verified_response
from ledger.schema import VerifiedResponse

class TestIntegration:
    def test_parse_verified_response_valid(self):
        raw = {
            "paragraphs": [
                {
                    "index": 0,
                    "text": "First para",
                    "step_type": "established_fact",
                    "claims": [
                        {"claim_id": "c1", "text": "Claim 1", "tag": "established"}
                    ]
                }
            ]
        }
        resp = _parse_verified_response(raw)
        assert len(resp.paragraphs) == 1
        assert resp.paragraphs[0].text == "First para"
        assert resp.paragraphs[0].step_type == "established_fact"
        assert len(resp.paragraphs[0].claims) == 1
        assert resp.paragraphs[0].claims[0].claim_id == "c1"
        assert resp.paragraphs[0].claims[0].text == "Claim 1"

    def test_parse_verified_response_empty(self):
        resp = _parse_verified_response({})
        assert len(resp.paragraphs) == 0

    def test_parse_verified_response_missing_claims(self):
        raw = {
            "paragraphs": [
                {
                    "index": 0,
                    "text": "First para"
                }
            ]
        }
        resp = _parse_verified_response(raw)
        assert len(resp.paragraphs) == 1
        assert len(resp.paragraphs[0].claims) == 0
