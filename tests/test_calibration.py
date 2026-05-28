import pytest
from unittest.mock import patch

from ledger.schema import Ledger, InteractionTurn, UserFeedback
from ui.calibration import _is_already_rated, _record_feedback

class TestCalibration:
    def test_is_already_rated_true(self):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="test",
                user_feedback=UserFeedback(accurate=[0], inaccurate=[1], uncertain=[2])
            )
        ])
        
        assert _is_already_rated(ledger, 0, 0) is True
        assert _is_already_rated(ledger, 0, 1) is True
        assert _is_already_rated(ledger, 0, 2) is True

    def test_is_already_rated_false(self):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="test",
                user_feedback=UserFeedback(accurate=[0])
            )
        ])
        
        assert _is_already_rated(ledger, 0, 1) is False
        assert _is_already_rated(ledger, 1, 0) is False  # Out of bounds turn

    @patch("ui.calibration.st")
    def test_record_feedback_accurate(self, mock_st):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="test",
                user_feedback=UserFeedback()
            )
        ])
        
        _record_feedback(ledger, 0, 1, "accurate")
        
        assert 1 in ledger.interaction_history[0].user_feedback.accurate
        mock_st.toast.assert_called_with("Marked as accurate")
        mock_st.rerun.assert_called_once()

    @patch("ui.calibration.st")
    def test_record_feedback_inaccurate(self, mock_st):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="test",
                user_feedback=UserFeedback()
            )
        ])
        
        _record_feedback(ledger, 0, 2, "inaccurate")
        
        assert 2 in ledger.interaction_history[0].user_feedback.inaccurate
        mock_st.toast.assert_called_with("Marked as inaccurate")
        mock_st.rerun.assert_called_once()

    @patch("ui.calibration.st")
    def test_record_feedback_recalculates_trust(self, mock_st):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="test",
                user_feedback=UserFeedback()
            )
        ])
        
        assert ledger.trust_score == 0.0
        
        _record_feedback(ledger, 0, 0, "accurate")
        
        assert ledger.trust_score == 1.0
