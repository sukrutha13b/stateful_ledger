"""tests/test_rubric.py — Unit tests for ui/rubric.py (Phase 5).

Tests cover the rubric processing logic and generation gate.
The Streamlit render function (render_rubric_card) is not tested here
because it requires a live Streamlit runtime; it will be validated
during Phase 9 (UI Assembly) via manual browser testing.
"""
import pytest

from ledger.schema import Ledger, Rubric
from ledger.manager import init_ledger
from ui.rubric import process_rubric_response, is_rubric_confirmed


class TestRubricPromptReturnsValidGoalType:
    """process_rubric_response stores goal_type correctly."""

    def test_stores_analytical(self):
        ledger = init_ledger()
        result = {"goal_type": "analytical", "rubric_criteria": ["Accuracy"]}
        assert process_rubric_response(result, ledger) is True
        assert ledger.goal_type == "analytical"

    def test_stores_creative(self):
        ledger = init_ledger()
        result = {"goal_type": "creative", "rubric_criteria": ["Originality"]}
        assert process_rubric_response(result, ledger) is True
        assert ledger.goal_type == "creative"

    def test_stores_technical(self):
        ledger = init_ledger()
        result = {"goal_type": "technical", "rubric_criteria": ["Correctness"]}
        assert process_rubric_response(result, ledger) is True
        assert ledger.goal_type == "technical"

    def test_stores_exploratory(self):
        ledger = init_ledger()
        result = {"goal_type": "exploratory", "rubric_criteria": ["Breadth"]}
        assert process_rubric_response(result, ledger) is True
        assert ledger.goal_type == "exploratory"

    def test_invalid_goal_type_falls_back_to_exploratory(self):
        ledger = init_ledger()
        result = {"goal_type": "unknown", "rubric_criteria": ["Something"]}
        assert process_rubric_response(result, ledger) is True
        assert ledger.goal_type == "exploratory"


class TestRubricPromptReturnsCriteria:
    """process_rubric_response stores all rubric criteria."""

    def test_stores_three_criteria(self):
        ledger = init_ledger()
        criteria = ["Accuracy", "Depth", "Clarity"]
        result = {"goal_type": "analytical", "rubric_criteria": criteria}
        process_rubric_response(result, ledger)
        assert ledger.rubric.criteria == criteria

    def test_stores_five_criteria(self):
        ledger = init_ledger()
        criteria = ["A", "B", "C", "D", "E"]
        result = {"goal_type": "technical", "rubric_criteria": criteria}
        process_rubric_response(result, ledger)
        assert len(ledger.rubric.criteria) == 5

    def test_filters_empty_criteria(self):
        ledger = init_ledger()
        result = {"goal_type": "creative", "rubric_criteria": ["Good", "", "  ", "Clear"]}
        process_rubric_response(result, ledger)
        assert ledger.rubric.criteria == ["Good", "Clear"]


class TestRubricEditUpdatesCriteria:
    """Simulated editing via direct rubric mutation (mirrors form submit)."""

    def test_edit_existing_criteria(self):
        rubric = Rubric(criteria=["Old A", "Old B"])
        # Simulate user editing
        rubric.criteria = ["New A", "New B"]
        rubric.is_edited_by_user = True
        rubric.version += 1
        assert rubric.criteria == ["New A", "New B"]
        assert rubric.is_edited_by_user is True
        assert rubric.version == 2


class TestRubricAddNewCriterion:
    """New criterion added appears in criteria list."""

    def test_add_new_criterion(self):
        rubric = Rubric(criteria=["Existing"])
        new = "Brand new criterion"
        rubric.criteria.append(new)
        assert "Brand new criterion" in rubric.criteria
        assert len(rubric.criteria) == 2


class TestRubricConfirmSetsFlag:
    """After confirm, rubric_confirmed is True."""

    def test_starts_unconfirmed(self):
        ledger = init_ledger()
        assert ledger.rubric_confirmed is False

    def test_process_sets_unconfirmed(self):
        """process_rubric_response sets rubric_confirmed = False (user must confirm)."""
        ledger = init_ledger()
        result = {"goal_type": "analytical", "rubric_criteria": ["X"]}
        process_rubric_response(result, ledger)
        assert ledger.rubric_confirmed is False

    def test_manual_confirm(self):
        """Simulating the form submit sets rubric_confirmed = True."""
        ledger = init_ledger()
        result = {"goal_type": "analytical", "rubric_criteria": ["X"]}
        process_rubric_response(result, ledger)
        # Simulate user clicking "Confirm & Proceed"
        ledger.rubric_confirmed = True
        assert is_rubric_confirmed(ledger) is True


class TestGenerationBlockedWithoutRubric:
    """Generation should be blocked when rubric is not confirmed."""

    def test_blocked_before_rubric(self):
        ledger = init_ledger()
        assert is_rubric_confirmed(ledger) is False

    def test_blocked_after_process_before_confirm(self):
        ledger = init_ledger()
        result = {"goal_type": "technical", "rubric_criteria": ["Speed", "Memory"]}
        process_rubric_response(result, ledger)
        assert is_rubric_confirmed(ledger) is False

    def test_allowed_after_confirm(self):
        ledger = init_ledger()
        ledger.rubric_confirmed = True
        assert is_rubric_confirmed(ledger) is True

    def test_api_error_returns_false(self):
        ledger = init_ledger()
        result = {"error": "API call failed", "raw_text": ""}
        assert process_rubric_response(result, ledger) is False

    def test_missing_criteria_returns_false(self):
        ledger = init_ledger()
        result = {"goal_type": "analytical"}  # missing rubric_criteria
        assert process_rubric_response(result, ledger) is False
