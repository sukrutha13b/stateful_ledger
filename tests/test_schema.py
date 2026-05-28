"""tests/test_schema.py — Unit tests for ledger/schema.py (Phase 2)."""
from dataclasses import asdict

import pytest

from ledger.schema import (
    Ledger, Rule, Assumption, MissingInfo,
    Claim, Paragraph, VerifiedResponse,
    ContradictionFlag, UserFeedback, InteractionTurn, Rubric,
)


class TestLedgerCreationDefaults:
    """Verify all default values are sensible out of the box."""

    def test_session_id_is_set(self):
        ledger = Ledger()
        assert ledger.session_id  # non-empty string

    def test_goal_type_default(self):
        assert Ledger().goal_type == "exploratory"

    def test_turn_count_starts_at_zero(self):
        assert Ledger().turn_count == 0

    def test_trust_score_starts_at_zero(self):
        assert Ledger().trust_score == 0.0

    def test_lists_start_empty(self):
        ledger = Ledger()
        assert ledger.rules == []
        assert ledger.assumptions == []
        assert ledger.missing_info == []
        assert ledger.interaction_history == []

    def test_rubric_default(self):
        ledger = Ledger()
        assert isinstance(ledger.rubric, Rubric)
        assert ledger.rubric.criteria == []
        assert ledger.rubric.version == 1
        assert ledger.rubric.is_edited_by_user is False


class TestRuleHasUniqueId:
    """Two Rule() instances must have different IDs."""

    def test_unique_ids(self):
        r1 = Rule()
        r2 = Rule()
        assert r1.id != r2.id

    def test_id_is_8_chars(self):
        r = Rule()
        assert len(r.id) == 8


class TestClaimClassificationValues:
    """Classification must be one of the three valid values."""

    def test_default_is_unverified(self):
        c = Claim()
        assert c.classification == "unverified"

    def test_can_set_grounded(self):
        c = Claim(classification="grounded")
        assert c.classification == "grounded"

    def test_can_set_contested(self):
        c = Claim(classification="contested")
        assert c.classification == "contested"


class TestVerifiedResponseStructure:
    """VerifiedResponse holds Paragraphs with Claims."""

    def test_empty_by_default(self):
        vr = VerifiedResponse()
        assert vr.paragraphs == []

    def test_nested_structure(self):
        claim = Claim(text="Test claim", classification="grounded")
        para = Paragraph(index=0, text="Test paragraph", claims=[claim])
        vr = VerifiedResponse(paragraphs=[para])
        assert len(vr.paragraphs) == 1
        assert vr.paragraphs[0].claims[0].text == "Test claim"
        assert vr.paragraphs[0].step_type is None


class TestContradictionFlagDefaults:
    """Resolution starts as None, resolved_at starts as None."""

    def test_resolution_starts_none(self):
        cf = ContradictionFlag()
        assert cf.resolution is None

    def test_resolved_at_starts_none(self):
        cf = ContradictionFlag()
        assert cf.resolved_at is None

    def test_severity_default(self):
        cf = ContradictionFlag()
        assert cf.severity == "tension"


class TestLedgerSerialisationRoundtrip:
    """asdict(Ledger()) produces a valid dict and contains all expected keys."""

    def test_asdict_produces_dict(self):
        d = asdict(Ledger())
        assert isinstance(d, dict)

    def test_all_keys_present(self):
        d = asdict(Ledger())
        expected_keys = {
            "session_id", "goal_type", "rubric", "rubric_confirmed",
            "rules", "assumptions", "missing_info",
            "interaction_history", "trust_score", "turn_count",
        }
        assert expected_keys == set(d.keys())

    def test_nested_claim_round_trip(self):
        """Build a full structure, serialise, verify key paths exist."""
        claim = Claim(text="X", classification="grounded", tag="established")
        para = Paragraph(index=0, text="P", claims=[claim])
        vr = VerifiedResponse(paragraphs=[para])
        turn = InteractionTurn(
            turn_index=0, role="assistant", raw_input="Q",
            verified_response=vr,
        )
        ledger = Ledger(interaction_history=[turn])
        d = asdict(ledger)
        nested_claim = d["interaction_history"][0]["verified_response"]["paragraphs"][0]["claims"][0]
        assert nested_claim["text"] == "X"
        assert nested_claim["classification"] == "grounded"
