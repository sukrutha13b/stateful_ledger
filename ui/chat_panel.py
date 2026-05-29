import streamlit as st
from ui.renderers import render_tagged_response

def render_chat_panel(col_chat):
    with col_chat:
        ledger = st.session_state.get("ledger", {})
        turn_history = ledger.get("turn_history", [])
        
        # Header Row
        st.markdown(f"**STATEFUL LEDGER**")
        st.divider()
        
        if not turn_history:
            st.caption("Start a conversation. The Ledger will build itself.")
            return

        for turn in turn_history:
            # User Message
            with st.chat_message("user"):
                st.markdown(turn.get("user_prompt", ""))
                
            # Assistant Message
            with st.chat_message("assistant"):
                tags = turn.get("audit_result", {}).get("sentence_tags", [])
                
                # Check Layer 2 Grounding tags
                grounding_result = turn.get("grounding_result", {})
                
                html_response = render_tagged_response(tags, turn.get("raw_response", ""), grounding_result)
                st.markdown(html_response, unsafe_allow_html=True)
                
                st.caption("LEGEND:  Reasoned (green underline) ~ Inferred (orange dashed underline)")
                
                # Action Buttons
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(" Verify Facts", key=f"verify_{turn['turn_number']}"):
                        st.session_state[f"run_grounding_{turn['turn_number']}"] = True
                        st.rerun()
                with col2:
                    if st.button(" Looks Good", key=f"good_{turn['turn_number']}"):
                        st.rerun()
                        
                # If there's a contradiction banner to render
                from ui.contradiction_ui import render_contradiction_banner
                render_contradiction_banner(ledger, turn["turn_number"])
