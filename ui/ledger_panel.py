import streamlit as st

def render_ledger_panel(col_ledger):
    with col_ledger:
        ledger = st.session_state.get("ledger", {})
        st.subheader(" LEDGER PANEL")
        
        # Rubric
        with st.expander(" EVALUATION RUBRIC", expanded=True):
            dims = ledger.get("rubric", {}).get("dimensions", [])
            if not dims:
                st.caption("No rubric generated yet.")
            for dim in dims:
                score = dim.get("last_coverage_score", 0)
                st.progress(score / 100.0, text=f"{dim['name']} [{score}%]")

        # Active Rules
        rules = ledger.get("rules", [])
        with st.expander(f" ACTIVE RULES ({len(rules)})"):
            for rule in rules:
                icon = "[PASS]" if rule.get("status") == "active" else ("[Warning]" if rule.get("violation_count", 0) > 0 else "[X]")
                st.markdown(f"{icon} **{rule.get('rule_id', '')}**: {rule.get('text', '')}")

        # Assumptions
        assumptions = [a for a in ledger.get("assumptions", []) if a.get("status") == "active"]
        with st.expander(f" ASSUMPTIONS ({len(assumptions)})"):
            for a in assumptions:
                colA, colB = st.columns([8, 1])
                colA.markdown(f"{a['assumption_id']}: {a['text']}")
                if colB.button("", key=f"inv_assump_{a['assumption_id']}"):
                    a["status"] = "invalidated"
                    st.rerun()

        # Missing Info
        missing = [m for m in ledger.get("missing_info_registry", []) if not m.get("resolved")]
        with st.expander(f" MISSING INFO ({len(missing)})"):
            for m in missing:
                icon = "(Red) HIGH" if m.get("severity") == "High" else "(Amber) MED"
                st.markdown(f"{icon}: {m.get('description', '')}")
                if st.button("Mark Resolved", key=f"res_miss_{m.get('item_id', '')}"):
                    m["resolved"] = True
                    st.rerun()

        # Contradictions
        pending = [c for c in ledger.get("contradiction_log", []) if c.get("resolution_status") == "pending"]
        with st.expander(f" CONTRADICTION LOG ({len(pending)} pending)", expanded=len(pending)>0):
            for c in pending:
                st.markdown(f"**{c.get('contradiction_id', '')}** (Turn {c.get('identified_at_turn', '')})")
                st.markdown(f"Description: {c.get('description', '')}")
