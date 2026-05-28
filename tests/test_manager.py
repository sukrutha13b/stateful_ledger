"""tests/test_manager.py — Unit tests for ledger/manager.py (Phase 2)."""
from dataclasses import asdict

import pytest

from ledger.schema import (
    Ledger, Rule, Assumption, MissingInfo,
    VerifiedResponse, Paragraph, Claim, ContradictionFlag,
)
from ledger.manager import (
    init_ledger, get_snapshot, update_ledger,
    add_rule, remove_rule, update_rule, get_active_rules, export_ledger, import_ledger,
)


class TestInitLedger:
    """init_ledger returns a fresh, valid instance."""

    def test_returns_ledger(self):
        ledger = init_ledger()
        assert isinstance(ledger, Ledger)

    def test_session_id_is_set(self):
        ledger = init_ledger()
        assert ledger.session_id
        assert len(ledger.session_id) == 8

    def test_turn_count_starts_at_zero(self):
        assert init_ledger().turn_count == 0


class TestGetSnapshot:
    """get_snapshot returns a capped, serialisable dict."""

    def test_returns_dict(self):
        ledger = init_ledger()
        snapshot = get_snapshot(ledger)
        assert isinstance(snapshot, dict)

    def test_caps_history_to_max_turns(self):
        ledger = init_ledger()
        # Simulate 15 turns
        from ledger.schema import InteractionTurn
        for i in range(15):
            ledger.interaction_history.append(
                InteractionTurn(turn_index=i, role="assistant", raw_input=f"Q{i}")
            )
        snapshot = get_snapshot(ledger, max_turns=10)
        assert len(snapshot["interaction_history"]) == 10
        # Should keep the *last* 10
        assert snapshot["interaction_history"][0]["turn_index"] == 5

    def test_fewer_turns_than_cap(self):
        ledger = init_ledger()
        from ledger.schema import InteractionTurn
        ledger.interaction_history.append(
            InteractionTurn(turn_index=0, role="user", raw_input="Hello")
        )
        snapshot = get_snapshot(ledger, max_turns=10)
        assert len(snapshot["interaction_history"]) == 1


class TestUpdateLedger:
    """update_ledger appends a turn and merges assumptions/missing_info."""

    def _make_verified_response(self):
        return VerifiedResponse(
            paragraphs=[
                Paragraph(index=0, text="Resp", claims=[
                    Claim(text="C1", classification="grounded")
                ])
            ]
        )

    def test_appends_turn(self):
        ledger = init_ledger()
        vr = self._make_verified_response()
        update_ledger(ledger, "user query", vr, [], [], [], [])
        assert len(ledger.interaction_history) == 1
        assert ledger.turn_count == 1

    def test_turn_index_increments(self):
        ledger = init_ledger()
        vr = self._make_verified_response()
        update_ledger(ledger, "q1", vr, [], [], [], [])
        update_ledger(ledger, "q2", vr, [], [], [], [])
        assert ledger.turn_count == 2
        assert ledger.interaction_history[1].turn_index == 1

    def test_appends_assumptions(self):
        ledger = init_ledger()
        vr = self._make_verified_response()
        assumptions = [
            Assumption(text="Assumed X"),
            Assumption(text="Assumed Y"),
        ]
        update_ledger(ledger, "q", vr, assumptions, [], [], [])
        assert len(ledger.assumptions) == 2

    def test_appends_missing_info(self):
        ledger = init_ledger()
        vr = self._make_verified_response()
        missing = [MissingInfo(text="Need Z")]
        update_ledger(ledger, "q", vr, [], missing, [], [])
        assert len(ledger.missing_info) == 1

    def test_stores_contradiction_flags(self):
        ledger = init_ledger()
        vr = self._make_verified_response()
        flags = [ContradictionFlag(conflict_text="A vs B", severity="direct")]
        update_ledger(ledger, "q", vr, [], [], flags, [])
        assert ledger.interaction_history[0].contradiction_flags[0].severity == "direct"

    def test_stores_completeness_gaps(self):
        ledger = init_ledger()
        vr = self._make_verified_response()
        gaps = ["Missing context about X"]
        update_ledger(ledger, "q", vr, [], [], [], gaps)
        assert ledger.interaction_history[0].completeness_gaps == gaps


class TestAddRule:
    """add_rule creates and appends a Rule."""

    def test_assigns_id_and_appends(self):
        ledger = init_ledger()
        rule = add_rule(ledger, "Always cite sources")
        assert rule.id
        assert len(ledger.rules) == 1
        assert ledger.rules[0].text == "Always cite sources"

    def test_source_defaults_to_user(self):
        ledger = init_ledger()
        rule = add_rule(ledger, "Be concise")
        assert rule.source == "user"

    def test_inferred_source(self):
        ledger = init_ledger()
        rule = add_rule(ledger, "Prefers formal tone", source="inferred")
        assert rule.source == "inferred"


class TestRemoveRule:
    """remove_rule removes by ID, returns bool."""

    def test_removes_existing_rule(self):
        ledger = init_ledger()
        rule = add_rule(ledger, "Temp rule")
        assert remove_rule(ledger, rule.id) is True
        assert len(ledger.rules) == 0

    def test_returns_false_for_nonexistent(self):
        ledger = init_ledger()
        assert remove_rule(ledger, "no-such-id") is False


class TestUpdateRule:
    """update_rule modifies text by ID, returns bool."""

    def test_updates_existing_rule(self):
        ledger = init_ledger()
        rule = add_rule(ledger, "Old text")
        assert update_rule(ledger, rule.id, "New text") is True
        assert ledger.rules[0].text == "New text"

    def test_returns_false_for_nonexistent(self):
        ledger = init_ledger()
        assert update_rule(ledger, "no-such-id", "text") is False


class TestGetActiveRules:
    """get_active_rules filters out inactive rules."""

    def test_filters_inactive(self, ledger_with_rules):
        active = get_active_rules(ledger_with_rules)
        assert len(active) == 1
        assert active[0].text == "Rule A"

    def test_empty_ledger(self):
        ledger = init_ledger()
        assert get_active_rules(ledger) == []


class TestExportLedger:
    """export_ledger returns a complete dict."""

    def test_is_complete_dict(self):
        ledger = init_ledger()
        add_rule(ledger, "R1")
        export = export_ledger(ledger)
        assert isinstance(export, dict)
        assert len(export["rules"]) == 1
        assert "session_id" in export
        assert "trust_score" in export
        assert "turn_count" in export


class TestImportLedger:
    """import_ledger reconstructs a Ledger dataclass from export dictionary."""

    def test_imports_full_ledger(self):
        ledger = init_ledger()
        add_rule(ledger, "Rule 1")
        export_data = export_ledger(ledger)
        
        imported = import_ledger(export_data)
        assert imported.session_id == ledger.session_id
        assert len(imported.rules) == 1
        assert imported.rules[0].text == "Rule 1"
        assert imported.trust_score == ledger.trust_score

