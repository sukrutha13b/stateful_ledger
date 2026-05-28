import pytest
from unittest.mock import patch, MagicMock

from ledger.schema import Ledger, Rule, VerifiedResponse, Paragraph, ContradictionFlag
from engine.layer1 import (
    run_contradiction_check,
    run_completeness_audit,
    extract_assumptions_and_missing,
)

class TestContradictionCheck:
    def test_contradiction_check_no_rules_returns_empty(self):
        ledger = Ledger()
        response = VerifiedResponse()
        flags = run_contradiction_check("input", response, ledger)
        assert len(flags) == 0

    @patch("engine.layer1.call_gemini")
    def test_contradiction_check_with_violation(self, mock_call_gemini):
        ledger = Ledger(rules=[Rule(id="rule_1", text="No swearing", active=True)])
        response = VerifiedResponse(paragraphs=[Paragraph(text="Damn it")])
        
        mock_call_gemini.return_value = {
            "violations": [
                {
                    "rule_id": "rule_1",
                    "conflict_text": "Damn it",
                    "severity": "direct"
                }
            ]
        }
        
        flags = run_contradiction_check("bad input", response, ledger)
        
        assert len(flags) == 1
        assert flags[0].conflicting_rule_id == "rule_1"
        assert flags[0].conflict_text == "Damn it"
        assert flags[0].severity == "direct"
        assert "conflicts with Rule 'rule_1'" in flags[0].conflict_message

    @patch("engine.layer1.call_gemini")
    def test_contradiction_check_api_failure_graceful(self, mock_call_gemini):
        ledger = Ledger(rules=[Rule(text="rule", active=True)])
        response = VerifiedResponse()
        
        mock_call_gemini.return_value = {"error": "API failed"}
        flags = run_contradiction_check("input", response, ledger)
        assert len(flags) == 0

    @patch("engine.layer1.call_gemini")
    def test_contradiction_flag_message_format(self, mock_call_gemini):
        ledger = Ledger(rules=[Rule(id="abc", text="rule", active=True)])
        response = VerifiedResponse()
        
        mock_call_gemini.return_value = {
            "violations": [{"rule_id": "abc"}]
        }
        flags = run_contradiction_check("input", response, ledger)
        assert "conflicts with Rule 'abc'" in flags[0].conflict_message


class TestCompletenessAudit:
    def test_completeness_audit_all_covered(self):
        response = VerifiedResponse(paragraphs=[Paragraph(text="This response is about quantum physics.")])
        criteria = ["quantum physics"]
        gaps = run_completeness_audit(response, criteria)
        assert len(gaps) == 0

    def test_completeness_audit_missing_criterion(self):
        response = VerifiedResponse(paragraphs=[Paragraph(text="This response is about apples.")])
        criteria = ["quantum physics"]
        gaps = run_completeness_audit(response, criteria)
        assert gaps == ["quantum physics"]

    def test_completeness_audit_empty_criteria(self):
        response = VerifiedResponse(paragraphs=[Paragraph(text="Hello")])
        gaps = run_completeness_audit(response, [])
        assert len(gaps) == 0

    def test_completeness_audit_partial_keyword_match(self):
        # The keywords from "advanced quantum computing details" are advanced, quantum, computing, details
        # The text has "quantum computing" (2 out of 4 keywords = 0.5 ratio)
        # Our function says < 0.5 is a gap, so 0.5 is NOT a gap. 
        # Let's make it 1 out of 4 keywords -> 0.25 ratio -> it will be a gap.
        response = VerifiedResponse(paragraphs=[Paragraph(text="This text mentions advanced mathematics.")])
        criteria = ["advanced quantum computing details"]
        gaps = run_completeness_audit(response, criteria)
        assert gaps == ["advanced quantum computing details"]


class TestExtractAssumptionsAndMissing:
    def test_extract_assumptions_valid(self):
        raw = {"assumptions": ["Assumed X"], "missing_info": ["Missing Y"]}
        assumptions, missing = extract_assumptions_and_missing(raw)
        assert assumptions == ["Assumed X"]
        assert missing == ["Missing Y"]

    def test_extract_assumptions_malformed(self):
        raw = {}
        assumptions, missing = extract_assumptions_and_missing(raw)
        assert assumptions == []
        assert missing == []

    def test_extract_assumptions_non_list(self):
        raw = {"assumptions": "not a list", "missing_info": {"key": "val"}}
        assumptions, missing = extract_assumptions_and_missing(raw)
        assert assumptions == []
        assert missing == []
