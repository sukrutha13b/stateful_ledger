import streamlit as st
import json

from core.ledger import init_empty_ledger, update_ledger
from core.context_assembly import assemble_context
from gemini.client import GeminiClient
from schemas.audit_schemas import AuditResult, RubricBootstrapSchema
from gemini.prompts import AUDIT_SYSTEM_PROMPT, AUDIT_USER_PROMPT_TEMPLATE, RUBRIC_BOOTSTRAP_PROMPT
from gemini.grounding_parser import parse_grounding_metadata
from core.contradiction_router import flag_overconfidence

from ui.styles import apply_styles
from ui.theme import inject_gemini_css
from ui.navigation_sidebar import render_navigation_sidebar
from ui.chat_panel import render_chat_panel
from ui.ledger_panel import render_ledger_panel

# -- Global Config --
st.set_page_config(
    page_title="Stateful Ledger",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_gemini_css()
apply_styles()


# -- Init State --
if "ledger" not in st.session_state:
    st.session_state["ledger"] = init_empty_ledger()

ledger = st.session_state["ledger"]

# -- Left Navigation Sidebar --
render_navigation_sidebar()

# -- Main Layout --
if "show_ledger" not in st.session_state:
    st.session_state["show_ledger"] = True

if st.session_state["show_ledger"]:
    col_chat, col_ledger = st.columns([65, 35], gap="large")
else:
    col_chat = st.container()
    col_ledger = None
# Grounding Trigger (Stage 6)
client = GeminiClient()
for turn in ledger.get("turn_history", []):
    t_num = turn["turn_number"]
    if st.session_state.get(f"run_grounding_{t_num}"):
        with col_chat:
            with st.spinner("Searching for grounding evidence..."):
                from gemini.prompts import GROUNDING_PROMPT_TEMPLATE
                
                claims_text = turn.get("raw_response", "")
                tags = turn.get("audit_result", {}).get("sentence_tags", [])
                if tags:
                    claims_text = "\n".join([f"- {t.get('text')}" for t in tags])
                
                prompt = GROUNDING_PROMPT_TEMPLATE.format(claims_list=claims_text)
                grounding_raw = client.run_grounding(prompt)
                
                parsed_claims = parse_grounding_metadata(grounding_raw)
                
                turn["grounding_result"] = {
                    "status": "completed",
                    "claims": [c.model_dump() for c in parsed_claims] if parsed_claims else []
                }
                
                contra = flag_overconfidence(turn.get("audit_result", {}), turn["grounding_result"], turn)
                if contra:
                    ledger["contradiction_log"].append(contra)
                
        st.session_state[f"run_grounding_{t_num}"] = False
        st.rerun()

# Render chat history panel
render_chat_panel(col_chat)

# Render ledger panel
if col_ledger:
    render_ledger_panel(col_ledger)

# -- User Input & Pipeline --
user_input = st.chat_input("Ask or clarify...")

if user_input:
    with col_chat:
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                # Stage 0
                if ledger["total_turns"] == 0 or not ledger.get("rubric", {}).get("dimensions"):
                    st.toast("Calibrating evaluation lens...")
                    prompt = f"{RUBRIC_BOOTSTRAP_PROMPT}\n\nQuery: {user_input}"
                    bootstrap = client.generate_structured(prompt, RubricBootstrapSchema)
                    if bootstrap:
                        ledger["rubric"]["dimensions"] = [{"id": f"dim_{i}", "name": d.name, "description": d.description} for i, d in enumerate(bootstrap.evaluation_dimensions)]
                        ledger["rules"] = [{"rule_id": f"rule_{i}", "text": r, "status": "active", "type": "auto", "source_turn": 1, "violation_count": 0} for i, r in enumerate(bootstrap.initial_boundary_rules)]
                        ledger["rubric"]["auto_generated"] = True
                
                ledger["total_turns"] += 1
                turn_num = ledger["total_turns"]
                
                # Stage 1
                context = assemble_context(ledger, user_input)
                
                # Stage 2
                raw_response = client.generate(context, user_input)
                
                # Stage 3
                audit_prompt = AUDIT_USER_PROMPT_TEMPLATE.format(
                    raw_response_text=raw_response,
                    active_rules=json.dumps([r for r in ledger["rules"] if r.get("status") == "active"]),
                    active_assumptions=json.dumps([a for a in ledger["assumptions"] if a.get("status") == "active"]),
                    rubric_dimensions=json.dumps(ledger["rubric"]["dimensions"])
                )
                audit_result = client.generate_structured(audit_prompt, AuditResult, system_instruction=AUDIT_SYSTEM_PROMPT)
                audit_dict = audit_result.model_dump() if audit_result else {}
                
                # Stage 4
                update_ledger(ledger, audit_dict, turn_num)
                
                # Stage 5 setup
                turn_record = {
                    "turn_id": f"turn_{turn_num}",
                    "turn_number": turn_num,
                    "timestamp": "",
                    "user_prompt": user_input,
                    "raw_response": raw_response,
                    "audit_result": audit_dict,
                    "grounding_result": {"status": "not_run", "claims": []},
                    "internal_confidence_flag": None
                }
                ledger["turn_history"].append(turn_record)
                
    st.rerun()
