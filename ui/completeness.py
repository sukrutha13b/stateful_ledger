import streamlit as st


def render_completeness_tracker(
    gaps: list[str],
    all_criteria: list[str],
):
    """
    Render a completeness check showing which rubric criteria were addressed.
    """
    with st.expander(" Completeness Check", expanded=bool(gaps)):
        for criterion in all_criteria:
            if criterion in gaps:
                st.markdown(f"[X] **{criterion}**: Not addressed")
            else:
                st.markdown(f"[PASS] **{criterion}**: Addressed")

        if gaps:
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button(" Request missing coverage", key="request_coverage"):
                    # Append auto-follow-up prompt
                    missing_text = ", ".join(gaps)
                    follow_up = f"Please address the following from the rubric that was not covered: {missing_text}"
                    st.session_state["auto_followup"] = follow_up
                    st.rerun()
            with col2:
                if st.button(" Mark as intentionally skipped", key="skip_coverage"):
                    st.toast("Marked as intentionally skipped.")
