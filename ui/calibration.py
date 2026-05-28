import streamlit as st
from ledger.schema import Ledger
from ledger.trust import calculate_trust_score


def render_calibration_buttons(
    turn_index: int,
    para_index: int,
    ledger: Ledger,
):
    """
    Render three compact feedback buttons below each paragraph.
    Updates ledger.interaction_history[turn].user_feedback on click.
    """
    col1, col2, col3 = st.columns(3)

    already_rated = _is_already_rated(ledger, turn_index, para_index)

    if already_rated:
        st.caption("✓ Rated")
        return

    with col1:
        if st.button("✅ Accurate", key=f"accurate_{turn_index}_{para_index}"):
            _record_feedback(ledger, turn_index, para_index, "accurate")

    with col2:
        if st.button("❌ Inaccurate", key=f"inaccurate_{turn_index}_{para_index}"):
            _record_feedback(ledger, turn_index, para_index, "inaccurate")

    with col3:
        if st.button("❓ Uncertain", key=f"uncertain_{turn_index}_{para_index}"):
            _record_feedback(ledger, turn_index, para_index, "uncertain")


def _is_already_rated(ledger: Ledger, turn_index: int, para_index: int) -> bool:
    """Check if a paragraph has already been rated."""
    if turn_index >= len(ledger.interaction_history):
        return False
    fb = ledger.interaction_history[turn_index].user_feedback
    return para_index in fb.accurate or para_index in fb.inaccurate or para_index in fb.uncertain


def _record_feedback(
    ledger: Ledger,
    turn_index: int,
    para_index: int,
    feedback_type: str,
):
    """Record user feedback and recalculate trust score."""
    if turn_index >= len(ledger.interaction_history):
        return

    fb = ledger.interaction_history[turn_index].user_feedback
    getattr(fb, feedback_type).append(para_index)

    # Recalculate trust score
    ledger.trust_score = calculate_trust_score(ledger)

    st.toast(f"Marked as {feedback_type}")
    st.rerun()
