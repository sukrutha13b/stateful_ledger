import json
import streamlit as st
from ledger.schema import Ledger, InteractionTurn
from ledger.manager import add_rule, remove_rule, update_rule

def render_gemini_sidebar():
    """Render the exact Gemini left navigation sidebar."""
    
    # 1. Header: Collapse Menu & Logo
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 20px; cursor: pointer; color: var(--text-secondary);">☰</span>
                <span style="font-weight: 500; font-size: 16px; letter-spacing: 0.2px; color: var(--text-primary);">Gemini</span>
            </div>
            <span style="font-size: 11px; background: var(--surface-high); padding: 2px 8px; border-radius: var(--radius-pill); color: var(--accent-blue); font-weight: 500;">Advanced</span>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. New Chat Button
    if st.button("➕ New chat", key="new_chat_gemini", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # 3. Global Links & Recent Chats
    st.markdown("""
        <div style="display: flex; flex-direction: column; gap: 0.25rem; margin-bottom: 1.5rem; margin-top: 1.5rem;">
            <div style="cursor: pointer; padding: 0.5rem 0.75rem; border-radius: var(--radius-card); display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 16px;">🔍</span>
                <span style="font-size: var(--font-label); color: var(--text-primary); font-weight: 500;">Search chats</span>
            </div>
            <div style="cursor: pointer; padding: 0.5rem 0.75rem; border-radius: var(--radius-card); display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 16px;">🎥</span>
                <span style="font-size: var(--font-label); color: var(--text-primary); font-weight: 500;">Videos</span>
            </div>
            <div style="cursor: pointer; padding: 0.5rem 0.75rem; border-radius: var(--radius-card); display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 16px;">📚</span>
                <span style="font-size: var(--font-label); color: var(--text-primary); font-weight: 500;">Library</span>
            </div>
            <div style="cursor: pointer; padding: 0.5rem 0.75rem; border-radius: var(--radius-card); display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 16px;">📓</span>
                <span style="font-size: var(--font-label); color: var(--text-primary); font-weight: 500;">Notebooks</span>
            </div>
        </div>

        <div style="flex: 1; display: flex; flex-direction: column; overflow-y: auto;">
            <div style="font-size: 11px; font-weight: 500; color: var(--text-secondary); margin-bottom: 0.5rem; padding-left: 0.75rem; letter-spacing: 0.5px;">Recent</div>
            <div style="display: flex; flex-direction: column; gap: 0.15rem;">
                <div style="cursor: pointer; padding: 0.4rem 0.75rem; border-radius: var(--radius-card); background-color: var(--surface-high); display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 14px;">💬</span>
                    <span style="font-size: 13px; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Microservices comparison</span>
                </div>
                <div style="cursor: pointer; padding: 0.4rem 0.75rem; border-radius: var(--radius-card); display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 14px;">💬</span>
                    <span style="font-size: 13px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Python GIL multi-threading</span>
                </div>
                <div style="cursor: pointer; padding: 0.4rem 0.75rem; border-radius: var(--radius-card); display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 14px;">💬</span>
                    <span style="font-size: 13px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Stateful ledger MVP guidelines</span>
                </div>
            </div>
        </div>

        <hr style="border: none; border-top: 1px solid var(--surface-high); margin: 0.75rem 0 0.5rem 0; opacity: 0.5;">

        <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0.75rem; border-radius: var(--radius-card); margin-top: auto; cursor: pointer;">
            <div style="width: 28px; height: 28px; font-size: 12px; background-color: var(--accent-green); color: white; border-radius: 50%; display: grid; place-content: center; font-weight: 700; flex-shrink: 0;">U</div>
            <div style="display: flex; flex-direction: column;">
                <span style="font-size: 13px; font-weight: 500; color: var(--text-primary);">User Account</span>
                <span style="font-size: 11px; color: var(--text-secondary);">user@example.com</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_ledger_panel(ledger: Ledger):
    """Render the full sidebar ledger panel with edit controls."""

    # ── Rules Section ──
    st.subheader(f"📋 Rules ({len([r for r in ledger.rules if r.active])})")
    for rule in ledger.rules:
        if not rule.active:
            continue

        edit_key = f"editing_rule_{rule.id}"
        col1, col2, col3 = st.columns([6, 1, 1])

        with col1:
            if st.session_state.get(edit_key, False):
                new_text = st.text_input(
                    "Edit rule",
                    value=rule.text,
                    key=f"rule_text_{rule.id}",
                    label_visibility="collapsed",
                )
                if st.button("Save", key=f"save_rule_{rule.id}"):
                    update_rule(ledger, rule.id, new_text)
                    st.session_state[edit_key] = False
                    st.toast("Rule updated.")
                    st.rerun()
            else:
                st.markdown(f"・ {rule.text}")

        with col2:
            if st.button("✏️", key=f"edit_btn_{rule.id}"):
                st.session_state[edit_key] = True
                st.rerun()

        with col3:
            if st.button("✕", key=f"del_btn_{rule.id}"):
                remove_rule(ledger, rule.id)
                st.toast("Rule removed.")
                st.rerun()

    # Add Rule button
    if st.button("+ Add Rule", key="add_rule_btn"):
        st.session_state["adding_rule"] = True
        st.rerun()

    if st.session_state.get("adding_rule", False):
        new_rule_text = st.text_input("New rule:", key="new_rule_text")
        if st.button("Save New Rule", key="save_new_rule"):
            if new_rule_text.strip():
                add_rule(ledger, new_rule_text.strip())
                st.session_state["adding_rule"] = False
                st.toast("Rule added.")
                st.rerun()

    st.divider()

    # ── Assumptions Section ──
    st.subheader(f"🤔 Assumptions ({len(ledger.assumptions)})")
    for assumption in ledger.assumptions:
        status = ""
        if assumption.user_confirmed is True:
            status = "✅"
        elif assumption.user_confirmed is False:
            status = "❌"
        else:
            status = "❓"
        st.markdown(f"・ {status} {assumption.text}")

    st.divider()

    # ── Missing Info Section ──
    st.subheader(f"❓ Missing Info ({len(ledger.missing_info)})")
    for info in ledger.missing_info:
        st.markdown(f"・ {info.text}")


def render_trust_indicator(trust_score: float):
    """Render the trust score progress bar with qualitative label."""
    st.divider()
    st.subheader("📊 Trust Indicator")

    # Qualitative label
    if trust_score >= 0.75:
        label = "High reliability"
        colour = "🟢"
    elif trust_score >= 0.4:
        label = "Moderate — verify contested claims externally"
        colour = "🟡"
    else:
        label = "Low — verify all claims externally"
        colour = "🔴"

    st.progress(trust_score, text=f"{colour} {trust_score:.0%} — {label}")

    # Stats
    total_rated = sum(
        len(t.user_feedback.accurate) + len(t.user_feedback.inaccurate) + len(t.user_feedback.uncertain)
        for t in st.session_state["ledger"].interaction_history
    )
    st.caption(f"Based on {total_rated} rated sections.")


def render_reasoning_trace(turn: InteractionTurn, ledger: Ledger):
    """Render the reasoning trace panel for the current turn."""
    with st.expander("🔍 Reasoning Trace"):
        # Rules used
        if turn.verified_response:
            rules_used = set()
            for para in turn.verified_response.paragraphs:
                for claim in para.claims:
                    rules_used.update(claim.ledger_rules_used)

            if rules_used:
                st.markdown("**Ledger rules that influenced this response:**")
                for rule_id in rules_used:
                    rule_text = next(
                        (r.text for r in ledger.rules if r.id == rule_id), rule_id
                    )
                    st.markdown(f"・ {rule_text}")

        # Completeness gaps
        if turn.completeness_gaps:
            st.markdown("**Coverage gaps:**")
            for gap in turn.completeness_gaps:
                st.markdown(f"・ ❌ {gap}")

        # Missing info for this turn
        turn_missing = [
            m for m in ledger.missing_info
            if m.turn_index == turn.turn_index
        ]
        if turn_missing:
            st.markdown("**Information unavailable at generation time:**")
            for m in turn_missing:
                st.markdown(f"・ {m.text}")


def render_import_export_buttons(ledger: Ledger):
    """Render buttons to Export and Import the Ledger."""
    from ledger.manager import export_ledger, import_ledger
    
    st.subheader("💾 Session Persistence")
    
    # Export
    ledger_json = json.dumps(export_ledger(ledger), indent=2, default=str)
    st.download_button(
        label="📥 Export Ledger",
        data=ledger_json,
        file_name="ledger_export.json",
        mime="application/json",
        use_container_width=True,
    )
    
    # Import
    uploaded_file = st.file_uploader("📤 Import Ledger", type=["json"], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            new_ledger = import_ledger(data)
            
            if st.button("Confirm Import", type="primary", use_container_width=True):
                st.session_state["ledger"] = new_ledger
                
                # Rebuild chat history from imported ledger
                messages = []
                for turn in new_ledger.interaction_history:
                    messages.append({"role": "user", "content": turn.raw_input})
                    if turn.verified_response:
                        response_text = "\n\n".join(p.text for p in turn.verified_response.paragraphs)
                        messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "turn_index": turn.turn_index
                        })
                st.session_state["messages"] = messages
                
                st.toast("Ledger imported successfully!")
                st.rerun()
        except Exception as e:
            st.error(f"Failed to import: {str(e)}")
