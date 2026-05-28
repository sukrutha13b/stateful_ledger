import pytest

from ledger.schema import Ledger, InteractionTurn, UserFeedback
from ledger.trust import calculate_trust_score

class TestTrustScore:
    def test_trust_score_no_ratings(self):
        ledger = Ledger()
        assert calculate_trust_score(ledger) == 0.0

    def test_trust_score_all_accurate(self):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="test",
                user_feedback=UserFeedback(accurate=[0, 1, 2, 3, 4])
            )
        ])
        assert calculate_trust_score(ledger) == 1.0

    def test_trust_score_all_inaccurate(self):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="test",
                user_feedback=UserFeedback(inaccurate=[0, 1, 2, 3, 4])
            )
        ])
        assert calculate_trust_score(ledger) == 0.0

    def test_trust_score_all_uncertain(self):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="test",
                user_feedback=UserFeedback(uncertain=[0, 1, 2, 3, 4])
            )
        ])
        assert calculate_trust_score(ledger) == 0.5

    def test_trust_score_mixed(self):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="test",
                user_feedback=UserFeedback(accurate=[0, 1, 2], inaccurate=[3, 4], uncertain=[5])
            )
        ])
        # 3 accurate (1.0), 2 inaccurate (0.0), 1 uncertain (0.5)
        # Total weight = 3*1.0 + 2*0.0 + 1*0.5 = 3.5
        # Total count = 6
        # Score = 3.5 / 6 = 0.5833333333333334
        assert abs(calculate_trust_score(ledger) - (3.5 / 6)) < 1e-6

    def test_trust_score_across_multiple_turns(self):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="t1",
                user_feedback=UserFeedback(accurate=[0, 1])
            ),
            InteractionTurn(
                turn_index=1,
                raw_input="t2",
                user_feedback=UserFeedback(inaccurate=[0])
            ),
            InteractionTurn(
                turn_index=2,
                raw_input="t3",
                user_feedback=UserFeedback(uncertain=[0])
            )
        ])
        # Total weight = 2*1.0 + 1*0.0 + 1*0.5 = 2.5
        # Total count = 4
        # Score = 2.5 / 4 = 0.625
        assert calculate_trust_score(ledger) == 0.625

    def test_trust_score_never_exceeds_1(self):
        ledger = Ledger(interaction_history=[
            InteractionTurn(
                turn_index=0,
                raw_input="test",
                user_feedback=UserFeedback(accurate=[i for i in range(100)])
            )
        ])
        assert calculate_trust_score(ledger) <= 1.0
