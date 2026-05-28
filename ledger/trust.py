from config import TRUST_WEIGHTS
from ledger.schema import Ledger


def calculate_trust_score(ledger: Ledger) -> float:
    """
    Calculate the session-level trust score as a weighted average
    across all user-rated paragraphs.

    Formula: (accurate * 1.0 + uncertain * 0.5 + inaccurate * 0.0) / total_rated

    Returns 0.0 if no paragraphs have been rated.
    This score is NEVER passed to the Gemini API — it's purely user-facing.
    """
    total_weighted = 0.0
    total_count = 0

    for turn in ledger.interaction_history:
        fb = turn.user_feedback
        accurate_count = len(fb.accurate)
        uncertain_count = len(fb.uncertain)
        inaccurate_count = len(fb.inaccurate)

        total_weighted += (
            accurate_count * TRUST_WEIGHTS["accurate"]
            + uncertain_count * TRUST_WEIGHTS["uncertain"]
            + inaccurate_count * TRUST_WEIGHTS["inaccurate"]
        )
        total_count += accurate_count + uncertain_count + inaccurate_count

    if total_count == 0:
        return 0.0

    return total_weighted / total_count
