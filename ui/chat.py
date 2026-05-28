import streamlit as st
from ledger.schema import VerifiedResponse, Ledger
from ui.claims import render_paragraph_with_claims
from ui.calibration import render_calibration_buttons


def render_chat_history(messages: list[dict], ledger: Ledger):
    """Render all previous messages in the chat history."""
    for msg in messages:
        avatar = "U" if msg["role"] == "user" else "✦"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

            # For assistant messages, render calibration buttons
            if msg["role"] == "assistant" and "turn_index" in msg:
                turn_idx = msg["turn_index"]
                if turn_idx < len(ledger.interaction_history):
                    turn = ledger.interaction_history[turn_idx]
                    if turn.verified_response:
                        for para in turn.verified_response.paragraphs:
                            render_calibration_buttons(turn_idx, para.index, ledger)


def render_response_block(
    response: VerifiedResponse,
    turn_index: int,
    ledger: Ledger,
):
    """
    Render a full verified response block with:
    - Annotated paragraphs with claim badges
    - Step type tags
    - Per-paragraph calibration buttons
    """
    for para in response.paragraphs:
        render_paragraph_with_claims(para, turn_index)
        render_calibration_buttons(turn_index, para.index, ledger)
        st.divider()
