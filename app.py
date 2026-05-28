import streamlit as st
from dataclasses import asdict
from ledger.schema import (
    Ledger, Assumption, MissingInfo, VerifiedResponse, Paragraph, Claim
)
from ledger.manager import init_ledger, get_snapshot, update_ledger
from engine.gemini_client import call_gemini
from engine.prompt_builder import build_rubric_prompt, build_main_prompt
from engine.layer1 import (
    run_contradiction_check, run_completeness_audit,
    extract_assumptions_and_missing
)
from engine.layer2 import run_claim_classification, detect_overconfidence
from ui.sidebar import (
    render_ledger_panel, render_trust_indicator,
    render_reasoning_trace, render_import_export_buttons,
    render_gemini_sidebar
)
from ui.chat import render_chat_history, render_response_block
from ui.flags import render_contradiction_widget, render_tension_notice
from ui.completeness import render_completeness_tracker
from utils.id_gen import generate_id


# ── Page Config ──
st.set_page_config(
    page_title="Stateful Ledger",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Insert the Gemini Design CSS
from ui.theme import inject_gemini_css
inject_gemini_css()

# ── Session State Init ──
if "ledger" not in st.session_state:
    st.session_state["ledger"] = init_ledger()
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "pending_rubric" not in st.session_state:
    st.session_state["pending_rubric"] = None


# ── Sidebar ──
with st.sidebar:
    render_gemini_sidebar()


# ── Main Area Layout ──
ledger = st.session_state["ledger"]

if ledger.turn_count == 0:
    col_main = st.container()
    col_dash = None
else:
    col_main, col_dash = st.columns([2.5, 1], gap="large")

with col_main:
    # Render chat history
    render_chat_history(st.session_state["messages"], ledger)

if col_dash is not None:
    with col_dash:
        with st.expander("Session Ledger", expanded=False):
            render_ledger_panel(ledger)
            render_trust_indicator(ledger.trust_score)
            st.divider()
            render_import_export_buttons(ledger)

            st.divider()
            if st.button("Reset Session", key="reset_session_dash"):
                st.session_state.clear()
                st.rerun()

# ── Chat Input ──
user_input = st.chat_input("Ask anything...")

# Handle auto-followup from completeness tracker
if st.session_state.get("auto_followup"):
    user_input = st.session_state.pop("auto_followup")

if user_input:
    # Add user message to history
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="U"):
        st.markdown(user_input)

    # ── RUBRIC GENERATION (first turn only) ──
    if not ledger.rubric_confirmed and ledger.turn_count == 0:
        with st.spinner("Analyzing your goal..."):
            sys_prompt, usr_prompt = build_rubric_prompt(user_input)
            rubric_result = call_gemini(sys_prompt, usr_prompt)

            if "error" not in rubric_result:
                ledger.goal_type = rubric_result.get("goal_type", "exploratory")
                ledger.rubric.criteria = rubric_result.get("rubric_criteria", [])
                ledger.rubric_confirmed = True
            else:
                # Fallback: use exploratory with default rubric
                ledger.goal_type = "exploratory"
                ledger.rubric.criteria = ["Accuracy", "Completeness", "Clarity"]
                ledger.rubric_confirmed = True

    # ── MAIN GENERATION PIPELINE ──
    with st.chat_message("assistant", avatar="✦"):
        with st.spinner("Generating and verifying response..."):
            # Step 1: Build prompt with ledger context
            snapshot = get_snapshot(ledger)
            sys_prompt, usr_prompt = build_main_prompt(user_input, snapshot)

            # Step 2: Call #1 — Main generation
            raw_response = call_gemini(sys_prompt, usr_prompt)

            if "error" in raw_response:
                st.error(f"Generation failed: {raw_response.get('error', 'Unknown error')}")
                raw_text = raw_response.get("raw_text", "")
                if raw_text:
                    st.markdown(raw_text)
                    st.warning("⚠️ Verification unavailable for this turn.")
            else:
                # Parse into VerifiedResponse
                verified_response = _parse_verified_response(raw_response)

                # Extract assumptions and missing info
                assumption_texts, missing_texts = extract_assumptions_and_missing(raw_response)
                new_assumptions = [
                    Assumption(text=a, turn_index=ledger.turn_count)
                    for a in assumption_texts
                ]
                new_missing = [
                    MissingInfo(text=m, turn_index=ledger.turn_count)
                    for m in missing_texts
                ]

                # Step 3: Call #2 — Contradiction check
                contradiction_flags = run_contradiction_check(
                    user_input, verified_response, ledger
                )

                # Step 4: Call #3 — Claim classification
                verified_response = run_claim_classification(verified_response)
                verified_response = detect_overconfidence(verified_response)

                # Step 5: Completeness audit
                completeness_gaps = run_completeness_audit(
                    verified_response, ledger.rubric.criteria
                )

                # Step 6: Update ledger
                update_ledger(
                    ledger, user_input, verified_response,
                    new_assumptions, new_missing,
                    contradiction_flags, completeness_gaps
                )

                # ── RENDER ──

                with col_main:
                    # Handle contradictions
                    direct_flags = [f for f in contradiction_flags if f.severity == "direct"]
                    tension_flags = [f for f in contradiction_flags if f.severity == "tension"]

                    for flag in direct_flags:
                        if flag.resolution is None:
                            render_contradiction_widget(flag, ledger, ledger.turn_count - 1)
                            st.stop()

                    for flag in tension_flags:
                        render_tension_notice(flag)

                    # Render response
                    render_response_block(verified_response, ledger.turn_count - 1, ledger)

                    # Render completeness tracker
                    render_completeness_tracker(completeness_gaps, ledger.rubric.criteria)

                    # Add to messages for chat history
                    response_text = "\n\n".join(p.text for p in verified_response.paragraphs)
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": response_text,
                        "turn_index": ledger.turn_count - 1,
                    })
                    st.rerun()


def _parse_verified_response(raw: dict) -> VerifiedResponse:
    """Parse the raw Gemini response dict into a VerifiedResponse dataclass."""
    paragraphs = []
    for p_data in raw.get("paragraphs", []):
        claims = [
            Claim(
                claim_id=c.get("claim_id", generate_id()),
                text=c.get("text", ""),
                tag=c.get("tag", "inferred"),
            )
            for c in p_data.get("claims", [])
        ]
        para = Paragraph(
            index=p_data.get("index", 0),
            text=p_data.get("text", ""),
            claims=claims,
            step_type=p_data.get("step_type"),
        )
        paragraphs.append(para)
    return VerifiedResponse(paragraphs=paragraphs)
