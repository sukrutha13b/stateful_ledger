"""ui/rubric.py — Streamlit rubric card for first-turn goal & criteria setup.

On the first user message, the system infers a goal type and generates
evaluation criteria. This module renders an editable form so the user
can review, tweak, and confirm the rubric before generation proceeds.
"""
import streamlit as st

from ledger.schema import Rubric


def render_rubric_card(rubric: Rubric, goal_type: str):
    """Render the rubric as an editable form at the top of the chat.

    Blocks generation until the user submits the form.  On submit the
    rubric is updated in ``st.session_state["ledger"]`` and
    ``rubric_confirmed`` is set to ``True``.
    """
    with st.form("rubric_form", clear_on_submit=False):
        st.subheader(f"📋 Session Rubric — [{goal_type.capitalize()}]")
        st.caption("This rubric will be used to evaluate response completeness.")

        updated_criteria = []
        for i, criterion in enumerate(rubric.criteria):
            val = st.text_input(
                f"Criterion {i+1}",
                value=criterion,
                key=f"rubric_criterion_{i}",
            )
            updated_criteria.append(val)

        # Add new criterion
        new_criterion = st.text_input(
            "Add new criterion (optional)",
            value="",
            key="rubric_new_criterion",
        )

        submitted = st.form_submit_button("✅ Confirm & Proceed")

        if submitted:
            if new_criterion.strip():
                updated_criteria.append(new_criterion.strip())
            rubric.criteria = [c for c in updated_criteria if c.strip()]
            rubric.is_edited_by_user = True
            rubric.version += 1
            st.session_state["ledger"].rubric = rubric
            st.session_state["ledger"].rubric_confirmed = True
            st.toast("Rubric confirmed ✅")
            st.rerun()


def process_rubric_response(api_result: dict, ledger) -> bool:
    """Apply a parsed rubric API response to the ledger.

    Args:
        api_result: Parsed JSON dict from ``call_gemini()`` with keys
            ``goal_type`` and ``rubric_criteria``.
        ledger: The active ``Ledger`` instance.

    Returns:
        ``True`` if the response was valid and applied, ``False`` otherwise.
    """
    if "error" in api_result:
        return False

    goal_type = api_result.get("goal_type", "")
    criteria = api_result.get("rubric_criteria")

    if not goal_type or criteria is None or not isinstance(criteria, list):
        return False

    valid_goals = {"analytical", "creative", "technical", "exploratory"}
    if goal_type not in valid_goals:
        goal_type = "exploratory"  # fallback

    ledger.goal_type = goal_type
    ledger.rubric.criteria = [str(c) for c in criteria if str(c).strip()]
    ledger.rubric_confirmed = False  # user must confirm
    return True


def is_rubric_confirmed(ledger) -> bool:
    """Check whether the rubric has been confirmed by the user.

    Used as a gate: generation is blocked until this returns ``True``.
    """
    return ledger.rubric_confirmed
