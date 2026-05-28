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


# ── CSS Overrides ──
def inject_css():
    st.markdown("""
    <style>
    /* ── Global Background ── */
    html, body, .stApp {
        background-color: #131314 !important;
        color: #E2E2E2 !important;
        font-family: 'Google Sans', 'Segoe UI', sans-serif !important;
    }

    /* ── Hide Streamlit default header/footer/menu ── */
    #MainMenu, header[data-testid="stHeader"], footer { display: none !important; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #1E1F20 !important;
        border-right: 1px solid #2A2B2D !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }

    /* Make the native Streamlit sidebar collapse arrow functional and visible */
    button[data-testid="collapsedControl"],
    button[data-testid="baseButton-headerNoPadding"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        color: #C4C7C5 !important;
        background: transparent !important;
        border: none !important;
    }

    /* ── Remove all SVG icons from sidebar nav items ── */
    section[data-testid="stSidebar"] svg,
    section[data-testid="stSidebar"] img.sidebar-icon,
    section[data-testid="stSidebar"] [data-testid="stImage"] {
        display: none !important;
    }

    /* ── Sidebar text styling ── */
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stRadio label {
        color: #C4C7C5 !important;
        font-size: 14px !important;
    }

    /* ── New Chat button ── */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: #2A2B2D !important;
        color: #E2E2E2 !important;
        border: 1px solid #3C3F41 !important;
        border-radius: 50px !important;
        width: 100% !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        margin-bottom: 8px !important;
        transition: background 0.2s ease;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #35363A !important;
    }

    /* ── Chat input bar — fix submit button position ── */
    div[data-testid="stChatInput"] {
        background-color: #1E1F20 !important;
        border: 1px solid #3C3F41 !important;
        border-radius: 50px !important;
        padding: 6px 12px !important;
        max-width: 760px !important;
        margin: 0 auto !important;
    }
    div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #E2E2E2 !important;
        font-size: 15px !important;
        border: none !important;
        outline: none !important;
        resize: none !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #6B6F72 !important;
    }
    /* Submit button — place inline to the right inside the pill */
    div[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
        background: linear-gradient(135deg, #8AB4F8, #C084FC) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 36px !important;
        height: 36px !important;
        padding: 6px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        align-self: center !important;
        margin-right: 4px !important;
        transition: opacity 0.2s;
    }
    div[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"]:hover {
        opacity: 0.85 !important;
    }
    div[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] svg {
        color: #131314 !important;
        fill: #131314 !important;
    }

    /* ── Chat messages ── */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 8px 0 !important;
    }
    div[data-testid="stChatMessage"] p {
        font-size: 15px !important;
        line-height: 1.65 !important;
        color: #E2E2E2 !important;
    }

    /* ── User bubble ── */
    div[data-testid="stChatMessage"][data-testid*="user"] {
        background-color: #1E1F20 !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 12px 16px !important;
        max-width: 80% !important;
        margin-left: auto !important;
    }

    /* ── Error / warning blocks ── */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        background-color: #2A1A1A !important;
        border-left: 3px solid #CF6679 !important;
        color: #E2E2E2 !important;
        font-size: 14px !important;
    }

    /* ── Expander ── */
    details {
        background-color: #1E1F20 !important;
        border: 1px solid #2A2B2D !important;
        border-radius: 12px !important;
    }

    /* ── Divider ── */
    hr { border-color: #2A2B2D !important; }

    /* ── Spinner ── */
    div[data-testid="stSpinner"] { color: #8AB4F8 !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #131314; }
    ::-webkit-scrollbar-thumb { background: #3C3F41; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)


inject_css()

# ── Session State Init ──
if "ledger" not in st.session_state:
    st.session_state["ledger"] = init_ledger()
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "pending_rubric" not in st.session_state:
    st.session_state["pending_rubric"] = None
# Track only actual user queries for recents
if "recent_queries" not in st.session_state:
    st.session_state["recent_queries"] = []


# ── Sidebar ──
with st.sidebar:
    render_gemini_sidebar()

    st.divider()
    st.markdown("**Recent**")

    # Show only actual user queries from this session
    if st.session_state["recent_queries"]:
        for i, q in enumerate(reversed(st.session_state["recent_queries"][-10:])):
            label = q[:40] + "…" if len(q) > 40 else q
            if st.button(label, key=f"recent_{i}"):
                pass  # Could restore query; extend as needed
    else:
        st.markdown(
            "<span style='color:#6B6F72; font-size:13px;'>No recent chats</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    ledger = st.session_state["ledger"]
    with st.expander("Session Ledger", expanded=False):
        render_ledger_panel(ledger)
        render_trust_indicator(ledger.trust_score)
        st.divider()
        render_import_export_buttons(ledger)
        st.divider()
        if st.button("Reset Session", key="reset_session"):
            st.session_state.clear()
            st.rerun()

    st.divider()
    st.markdown(
        "<div style='color:#6B6F72; font-size:12px;'>user@example.com</div>",
        unsafe_allow_html=True,
    )


# ── Main Area ──
ledger = st.session_state["ledger"]

if ledger.turn_count == 0:
    col_main = st.container()
    col_dash = None
    # Greeting
    st.markdown(
        """
        <div style='text-align:center; padding: 80px 0 40px 0;'>
            <h2 style='font-size:32px; font-weight:500; color:#E2E2E2;'>
                Where should we start?
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    col_main, col_dash = st.columns([2.5, 1], gap="large")

with col_main:
    render_chat_history(st.session_state["messages"], ledger)

if col_dash is not None:
    with col_dash:
        with st.expander("Ledger Snapshot", expanded=False):
            render_ledger_panel(ledger)
            render_trust_indicator(ledger.trust_score)


# ── Chat Input ──
user_input = st.chat_input("Ask anything...")

if st.session_state.get("auto_followup"):
    user_input = st.session_state.pop("auto_followup")

if user_input:
    # Record in recents (deduplicate)
    if user_input not in st.session_state["recent_queries"]:
        st.session_state["recent_queries"].append(user_input)

    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
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
                ledger.goal_type = "exploratory"
                ledger.rubric.criteria = ["Accuracy", "Completeness", "Clarity"]
                ledger.rubric_confirmed = True

    # ── MAIN GENERATION PIPELINE ──
    with st.chat_message("assistant"):
        with st.spinner("Generating and verifying response..."):
            snapshot = get_snapshot(ledger)
            sys_prompt, usr_prompt = build_main_prompt(user_input, snapshot)
            raw_response = call_gemini(sys_prompt, usr_prompt)

            if "error" in raw_response:
                err_msg = raw_response.get("error", "Unknown error")

                # ── API quota / billing guidance ──
                if "429" in str(err_msg) or "RESOURCE_EXHAUSTED" in str(err_msg) or "quota" in str(err_msg).lower():
                    st.error(
                        "**Gemini API quota exceeded.**\n\n"
                        "Your free-tier quota for `gemini-2.0-flash` is exhausted or the key has "
                        "a `limit: 0` on `generate_content_free_tier_requests`. "
                        "This is common with newly created keys that haven't been linked to a "
                        "billing-enabled GCP project.\n\n"
                        "**Fix options:**\n"
                        "1. Go to [Google AI Studio → API Keys](https://aistudio.google.com/app/apikey) "
                        "and confirm the key is active.\n"
                        "2. Enable billing on your GCP project at console.cloud.google.com.\n"
                        "3. Or switch to `gemini-1.5-flash` which has a separate free quota.\n\n"
                        "Check `engine/gemini_client.py` → `model` parameter to change the model."
                    )
                else:
                    st.error(f"Generation failed: {err_msg}")

                raw_text = raw_response.get("raw_text", "")
                if raw_text:
                    st.markdown(raw_text)
                    st.warning("⚠️ Verification unavailable for this turn.")

            else:
                verified_response = _parse_verified_response(raw_response)

                assumption_texts, missing_texts = extract_assumptions_and_missing(raw_response)
                new_assumptions = [
                    Assumption(text=a, turn_index=ledger.turn_count)
                    for a in assumption_texts
                ]
                new_missing = [
                    MissingInfo(text=m, turn_index=ledger.turn_count)
                    for m in missing_texts
                ]

                contradiction_flags = run_contradiction_check(
                    user_input, verified_response, ledger
                )

                verified_response = run_claim_classification(verified_response)
                verified_response = detect_overconfidence(verified_response)

                completeness_gaps = run_completeness_audit(
                    verified_response, ledger.rubric.criteria
                )

                update_ledger(
                    ledger, user_input, verified_response,
                    new_assumptions, new_missing,
                    contradiction_flags, completeness_gaps
                )

                with col_main:
                    direct_flags = [f for f in contradiction_flags if f.severity == "direct"]
                    tension_flags = [f for f in contradiction_flags if f.severity == "tension"]

                    for flag in direct_flags:
                        if flag.resolution is None:
                            render_contradiction_widget(flag, ledger, ledger.turn_count - 1)
                            st.stop()

                    for flag in tension_flags:
                        render_tension_notice(flag)

                    render_response_block(verified_response, ledger.turn_count - 1, ledger)
                    render_completeness_tracker(completeness_gaps, ledger.rubric.criteria)

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