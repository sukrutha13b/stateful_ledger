import streamlit as st
from ledger.schema import ContradictionFlag, Ledger


def render_contradiction_widget(flag: ContradictionFlag, ledger: Ledger, turn_index: int):
    """
    Render a contradiction warning box with three resolution buttons.
    For "direct" severity, this should block further rendering (call st.stop() after).
    """
    # Find the conflicting rule text
    rule_text = ""
    for rule in ledger.rules:
        if rule.id == flag.conflicting_rule_id:
            rule_text = rule.text
            break

    st.warning(f"""
    ⚠️ **CONTRADICTION DETECTED**

    This response conflicts with Rule: *"{rule_text}"*

    Conflict: *"{flag.conflict_text}"*
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📝 Update the Rule", key=f"update_rule_{flag.flag_id}"):
            flag.resolution = "update_rule"
            flag.resolved_at = turn_index
            st.session_state[f"editing_rule_{flag.conflicting_rule_id}"] = True
            st.rerun()

    with col2:
        if st.button("⏭️ Override for this response", key=f"override_{flag.flag_id}"):
            flag.resolution = "override_once"
            flag.resolved_at = turn_index
            st.toast("Override applied for this response.")
            st.rerun()

    with col3:
        if st.button("🔀 Flag the Tension", key=f"tension_{flag.flag_id}"):
            flag.resolution = "flag_tension"
            flag.resolved_at = turn_index
            st.toast("Tension flagged — both positions will coexist.")
            st.rerun()


def render_tension_notice(flag: ContradictionFlag):
    """Render a subtle tension notice prepended to the response."""
    st.info(f"""
    🔀 **Tension Notice**: This response has a noted tension with an established rule.
    *"{flag.conflict_text}"*
    This tension has been acknowledged and both positions coexist.
    """)
