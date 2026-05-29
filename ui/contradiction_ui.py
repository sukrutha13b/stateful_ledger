import streamlit as st

def render_contradiction_banner(ledger: dict, turn_number: int):
    """
    Renders contradiction banners for any pending contradictions associated with a turn.
    """
    pending = [c for c in ledger.get("contradiction_log", []) 
               if c.get("resolution_status") == "pending" and c.get("identified_at_turn") == turn_number]
               
    for c in pending:
        severity = c.get("severity", "Medium")
        color = "red" if severity == "High" else "orange"
        
        st.markdown(f"""
        <div style="background-color: rgba(249, 171, 0, 0.15); border: 1px solid {color}; padding: 10px; border-radius: 5px; margin-top: 10px; color: #E2E2E2;">
            <strong style="color: {color};">[Warning] INTERNAL TENSION DETECTED</strong><br>
            {c.get('description', '')}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Accept This Response Anyway", key=f"acc_{c['contradiction_id']}"):
                c["resolution_status"] = "user_accepted"
                c["resolution_action"] = "accepted"
                c["resolved_at_turn"] = ledger["total_turns"]
                st.rerun()
        with col2:
            override_reason = st.text_input("Override Reason:", key=f"inp_{c['contradiction_id']}")
            if st.button("Override the Rule", key=f"ovr_{c['contradiction_id']}"):
                c["resolution_status"] = "user_overridden"
                c["resolution_action"] = f"override: {override_reason}"
                c["resolved_at_turn"] = ledger["total_turns"]
                
                # Find the rule and override it
                for elem in c.get("conflicting_elements", []):
                    for rule in ledger.get("rules", []):
                        if rule.get("rule_id") == elem:
                            rule["status"] = "overridden"
                            rule["override_reason"] = override_reason
                            rule["override_at_turn"] = ledger["total_turns"]
                st.rerun()
        with col3:
            if st.button("Flag for Later Review", key=f"flg_{c['contradiction_id']}"):
                c["resolution_status"] = "flagged"
                c["resolution_action"] = "flagged"
                st.rerun()
