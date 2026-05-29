import json
from core.ledger import init_empty_ledger, update_ledger
from core.context_assembly import assemble_context
from gemini.client import GeminiClient
from schemas.audit_schemas import AuditResult, RubricBootstrapSchema
from gemini.prompts import AUDIT_SYSTEM_PROMPT, AUDIT_USER_PROMPT_TEMPLATE, RUBRIC_BOOTSTRAP_PROMPT

client = GeminiClient()
ledger = init_empty_ledger()

user_input = "When was ISRO founded?"

print("Stage 0")
prompt = f"{RUBRIC_BOOTSTRAP_PROMPT}\n\nQuery: {user_input}"
bootstrap = client.generate_structured(prompt, RubricBootstrapSchema)
if bootstrap:
    ledger["rubric"]["dimensions"] = [{"id": f"dim_{i}", "name": d.name, "description": d.description} for i, d in enumerate(bootstrap.evaluation_dimensions)]
    ledger["rules"] = [{"rule_id": f"rule_{i}", "text": r, "status": "active", "type": "auto", "source_turn": 1, "violation_count": 0} for i, r in enumerate(bootstrap.initial_boundary_rules)]
    ledger["rubric"]["auto_generated"] = True
    print("Bootstrap success!")
else:
    print("Bootstrap failed!")

ledger["total_turns"] += 1
turn_num = ledger["total_turns"]

print("Stage 1")
context = assemble_context(ledger, user_input)

print("Stage 2")
raw_response = client.generate(context, user_input)
print("Raw Response:", raw_response)

print("Stage 3")
audit_prompt = AUDIT_USER_PROMPT_TEMPLATE.format(
    raw_response_text=raw_response,
    active_rules=json.dumps([r for r in ledger["rules"] if r.get("status") == "active"]),
    active_assumptions=json.dumps([a for a in ledger["assumptions"] if a.get("status") == "active"]),
    rubric_dimensions=json.dumps(ledger["rubric"]["dimensions"])
)
audit_result = client.generate_structured(audit_prompt, AuditResult, system_instruction=AUDIT_SYSTEM_PROMPT)
if audit_result:
    print("Audit success!", audit_result.sentence_tags)
else:
    print("Audit failed!")
    
audit_dict = audit_result.model_dump() if audit_result else {}

print("Stage 4")
update_ledger(ledger, audit_dict, turn_num)
print("Ledger Rubric Dimensions:", ledger["rubric"]["dimensions"])
print("Ledger Rules:", ledger["rules"])
