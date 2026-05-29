import streamlit as st

def render_ledger_panel(col_ledger):
    with col_ledger:
        ledger = st.session_state.get("ledger", {})
        # Header with Title and Collapse Arrow
        col_title, col_close = st.columns([8, 2])
        col_title.subheader(" LEDGER PANEL")
        if col_close.button("→", help="Hide Ledger Panel"):
            st.session_state["show_ledger"] = False
            st.rerun()
            
        # Rubric
        with st.expander(" EVALUATION RUBRIC", expanded=True):
            dims = ledger.get("rubric", {}).get("dimensions", [])
            
            # Edit toggle
            edit_rubric_key = "edit_rubric"
            if edit_rubric_key not in st.session_state:
                st.session_state[edit_rubric_key] = False
                
            if dims:
                if st.button("✏️ Edit Rubric" if not st.session_state[edit_rubric_key] else "👁 View Rubric", key="btn_edit_rubric"):
                    st.session_state[edit_rubric_key] = not st.session_state[edit_rubric_key]
                    st.rerun()
                
            if st.session_state.get(edit_rubric_key, False):
                for i, dim in enumerate(dims):
                    dim["name"] = st.text_input(f"Dimension {i+1} Name", value=dim.get("name", ""), key=f"rub_name_{i}")
                    dim["description"] = st.text_area(f"Dimension {i+1} Description", value=dim.get("description", ""), key=f"rub_desc_{i}")
                    if st.button(f"Delete Dimension {i+1}", key=f"del_rub_{i}"):
                        dims.pop(i)
                        st.rerun()
                
                st.write("---")
                st.markdown("**Add New Dimension**")
                new_dim_name = st.text_input("New Dimension Name", key="new_dim_name")
                new_dim_desc = st.text_area("New Dimension Description", key="new_dim_desc")
                if st.button("Add Dimension"):
                    if new_dim_name:
                        dims.append({"id": f"dim_{len(dims)}", "name": new_dim_name, "description": new_dim_desc, "last_coverage_score": 0})
                        st.rerun()
            else:
                if not dims:
                    st.caption("No rubric generated yet.")
                for dim in dims:
                    score = dim.get("last_coverage_score", 0)
                    st.progress(score / 100.0, text=f"{dim['name']} [{score}%]")

        # Active Rules
        rules = ledger.get("rules", [])
        with st.expander(f" ACTIVE RULES ({len(rules)})"):
            edit_rules_key = "edit_rules"
            if edit_rules_key not in st.session_state:
                st.session_state[edit_rules_key] = False
                
            if rules:
                if st.button("✏️ Edit Rules" if not st.session_state[edit_rules_key] else "👁 View Rules", key="btn_edit_rules"):
                    st.session_state[edit_rules_key] = not st.session_state[edit_rules_key]
                    st.rerun()
                    
            if st.session_state.get(edit_rules_key, False):
                for i, rule in enumerate(rules):
                    rule["text"] = st.text_input(f"Rule {rule.get('rule_id')} Text", value=rule.get("text", ""), key=f"rule_text_{i}")
                    rule["status"] = st.selectbox(f"Rule {rule.get('rule_id')} Status", ["active", "inactive", "overridden"], index=["active", "inactive", "overridden"].index(rule.get("status", "active")), key=f"rule_status_{i}")
                    if st.button(f"Delete Rule {rule.get('rule_id')}", key=f"del_rule_{i}"):
                        rules.pop(i)
                        st.rerun()
                
                st.write("---")
                st.markdown("**Add New Rule**")
                new_rule_text = st.text_input("New Rule Text", key="new_rule_text")
                if st.button("Add Rule"):
                    if new_rule_text:
                        rules.append({
                            "rule_id": f"rule_{len(rules)}",
                            "text": new_rule_text,
                            "status": "active",
                            "type": "manual",
                            "source_turn": ledger.get("total_turns", 0),
                            "violation_count": 0
                        })
                        st.rerun()
            else:
                for rule in rules:
                    icon = "[PASS]" if rule.get("status") == "active" else ("[Warning]" if rule.get("violation_count", 0) > 0 else "[X]")
                    st.markdown(f"{icon} **{rule.get('rule_id', '')}**: {rule.get('text', '')}")

        # Assumptions
        assumptions = ledger.get("assumptions", [])
        active_assumptions = [a for a in assumptions if a.get("status") == "active"]
        with st.expander(f" ASSUMPTIONS ({len(active_assumptions)})"):
            edit_assump_key = "edit_assumptions"
            if edit_assump_key not in st.session_state:
                st.session_state[edit_assump_key] = False
                
            if assumptions:
                if st.button("✏️ Edit Assumptions" if not st.session_state[edit_assump_key] else "👁 View Assumptions", key="btn_edit_assump"):
                    st.session_state[edit_assump_key] = not st.session_state[edit_assump_key]
                    st.rerun()
                    
            if st.session_state.get(edit_assump_key, False):
                for i, a in enumerate(assumptions):
                    a["text"] = st.text_input(f"Assumption {a.get('assumption_id')} Text", value=a.get("text", ""), key=f"assump_text_{i}")
                    a["status"] = st.selectbox(f"Assumption {a.get('assumption_id')} Status", ["active", "invalidated"], index=["active", "invalidated"].index(a.get("status", "active")), key=f"assump_status_{i}")
                    if st.button(f"Delete Assumption {a.get('assumption_id')}", key=f"del_assump_{i}"):
                        assumptions.pop(i)
                        st.rerun()
                
                st.write("---")
                st.markdown("**Add New Assumption**")
                new_assump_text = st.text_input("New Assumption Text", key="new_assump_text")
                if st.button("Add Assumption"):
                    if new_assump_text:
                        assumptions.append({
                            "assumption_id": f"assump_{len(assumptions)}",
                            "text": new_assump_text,
                            "status": "active"
                        })
                        st.rerun()
            else:
                for a in active_assumptions:
                    colA, colB = st.columns([8, 2])
                    colA.markdown(f"**{a['assumption_id']}**: {a['text']}")
                    if colB.button("Invalidate", key=f"inv_assump_{a['assumption_id']}"):
                        a["status"] = "invalidated"
                        st.rerun()

        # Missing Info
        missing = ledger.get("missing_info_registry", [])
        active_missing = [m for m in missing if not m.get("resolved")]
        with st.expander(f" MISSING INFO ({len(active_missing)})"):
            edit_missing_key = "edit_missing"
            if edit_missing_key not in st.session_state:
                st.session_state[edit_missing_key] = False
                
            if missing:
                if st.button("✏️ Edit Missing Info" if not st.session_state[edit_missing_key] else "👁 View Missing Info", key="btn_edit_missing"):
                    st.session_state[edit_missing_key] = not st.session_state[edit_missing_key]
                    st.rerun()
                    
            if st.session_state.get(edit_missing_key, False):
                for i, m in enumerate(missing):
                    m["description"] = st.text_input(f"Item {m.get('item_id')} Description", value=m.get("description", ""), key=f"miss_desc_{i}")
                    m["severity"] = st.selectbox(f"Item {m.get('item_id')} Severity", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(m.get("severity", "Medium")), key=f"miss_sev_{i}")
                    m["resolved"] = st.checkbox(f"Resolved", value=m.get("resolved", False), key=f"miss_res_{i}")
                    if st.button(f"Delete Item {m.get('item_id')}", key=f"del_miss_{i}"):
                        missing.pop(i)
                        st.rerun()
                
                st.write("---")
                st.markdown("**Add Missing Info**")
                new_miss_desc = st.text_input("New Missing Info Description", key="new_miss_desc")
                new_miss_sev = st.selectbox("New Severity", ["High", "Medium", "Low"], key="new_miss_sev")
                if st.button("Add Missing Info"):
                    if new_miss_desc:
                        missing.append({
                            "item_id": f"miss_{len(missing)}",
                            "description": new_miss_desc,
                            "severity": new_miss_sev,
                            "resolved": False
                        })
                        st.rerun()
            else:
                for m in active_missing:
                    icon = "🔴 HIGH" if m.get("severity") == "High" else "🟡 MED"
                    st.markdown(f"{icon}: {m.get('description', '')}")
                    if st.button("Mark Resolved", key=f"res_miss_{m.get('item_id', '')}"):
                        m["resolved"] = True
                        st.rerun()

        # Contradictions
        contradictions = ledger.get("contradiction_log", [])
        pending = [c for c in contradictions if c.get("resolution_status") == "pending"]
        with st.expander(f" CONTRADICTION LOG ({len(pending)} pending)", expanded=len(pending)>0):
            edit_contra_key = "edit_contradictions"
            if edit_contra_key not in st.session_state:
                st.session_state[edit_contra_key] = False
                
            if contradictions:
                if st.button("✏️ Edit Contradictions" if not st.session_state[edit_contra_key] else "👁 View Contradictions", key="btn_edit_contra"):
                    st.session_state[edit_contra_key] = not st.session_state[edit_contra_key]
                    st.rerun()
                    
            if st.session_state.get(edit_contra_key, False):
                for i, c in enumerate(contradictions):
                    c["description"] = st.text_area(f"Contradiction {c.get('contradiction_id')} Description", value=c.get("description", ""), key=f"contra_desc_{i}")
                    c["resolution_status"] = st.selectbox(f"Contradiction {c.get('contradiction_id')} Status", ["pending", "resolved", "flagged"], index=["pending", "resolved", "flagged"].index(c.get("resolution_status", "pending")), key=f"contra_res_{i}")
                    if st.button(f"Delete Contradiction {c.get('contradiction_id')}", key=f"del_contra_{i}"):
                        contradictions.pop(i)
                        st.rerun()
                
                st.write("---")
                st.markdown("**Add Contradiction**")
                new_contra_desc = st.text_area("New Contradiction Description", key="new_contra_desc")
                if st.button("Add Contradiction"):
                    if new_contra_desc:
                        contradictions.append({
                            "contradiction_id": f"contra_{len(contradictions)}",
                            "description": new_contra_desc,
                            "resolution_status": "pending",
                            "identified_at_turn": ledger.get("total_turns", 0)
                        })
                        st.rerun()
            else:
                for c in pending:
                    st.markdown(f"**{c.get('contradiction_id', '')}** (Turn {c.get('identified_at_turn', '')})")
                    st.markdown(f"Description: {c.get('description', '')}")
