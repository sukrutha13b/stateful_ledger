"""tests/test_e2e_isro.py
End-to-end test: ISRO founding year, members, and chairmen from inception.
"""
import pytest
import time
import json
import pprint

from core.ledger import init_empty_ledger, update_ledger
from core.context_assembly import assemble_context
from gemini.client import GeminiClient
from schemas.audit_schemas import AuditResult, RubricBootstrapSchema
from gemini.prompts import AUDIT_SYSTEM_PROMPT, AUDIT_USER_PROMPT_TEMPLATE, RUBRIC_BOOTSTRAP_PROMPT


def run_turn(user_input: str, ledger: dict, max_retries: int = 3) -> dict:
    client = GeminiClient()

    if ledger["total_turns"] == 0:
        # Stage 0: Rubric Bootstrap
        prompt = f"{RUBRIC_BOOTSTRAP_PROMPT}\n\nQuery: {user_input}"
        bootstrap = client.generate_structured(prompt, RubricBootstrapSchema)
        if bootstrap:
            ledger["rubric"]["dimensions"] = [
                {"id": f"dim_{i}", "name": d.name, "description": d.description}
                for i, d in enumerate(bootstrap.evaluation_dimensions)
            ]
            ledger["rules"] = [
                {"rule_id": f"rule_{i}", "text": r, "status": "active",
                 "type": "auto", "source_turn": 1, "violation_count": 0}
                for i, r in enumerate(bootstrap.initial_boundary_rules)
            ]
            ledger["rubric"]["auto_generated"] = True

    ledger["total_turns"] += 1
    turn_num = ledger["total_turns"]

    # Stage 1: Context Assembly
    context = assemble_context(ledger, user_input)

    # Stage 2: Generation Pass 1
    raw_response = client.generate(context, user_input)

    # Stage 3: Internal Audit Pass 2
    audit_prompt = AUDIT_USER_PROMPT_TEMPLATE.format(
        raw_response_text=raw_response,
        active_rules=json.dumps([r for r in ledger["rules"] if r.get("status") == "active"]),
        active_assumptions=json.dumps([a for a in ledger["assumptions"] if a.get("status") == "active"]),
        rubric_dimensions=json.dumps(ledger["rubric"]["dimensions"])
    )
    audit_result = client.generate_structured(audit_prompt, AuditResult, system_instruction=AUDIT_SYSTEM_PROMPT)
    audit_dict = audit_result.model_dump() if audit_result else {}

    # Stage 4: Update ledger
    update_ledger(ledger, audit_dict, turn_num)

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

    return {
        "user_input": user_input,
        "raw_response": raw_response,
        "audit_result": audit_dict,
        "turn_count": ledger["total_turns"]
    }


class TestISROE2E:
    @pytest.fixture(autouse=True)
    def setup_ledger(self):
        self.ledger = init_empty_ledger()
        yield
        time.sleep(5)

    def test_isro_founding_members_chairmen(self):
        """Test: mention founding year, members and chairmen of ISRO from inception."""
        query = "mention founding year, members and chairmen of ISRO from inception"

        print("\n" + "=" * 80)
        print("QUERY:", query)
        print("=" * 80)

        result = run_turn(query, self.ledger)

        # --- Show the answer ---
        print("\n" + "-" * 80)
        print("RAW RESPONSE (Answer):")
        print("-" * 80)
        print(result["raw_response"])

        # --- Show audit result ---
        print("\n" + "-" * 80)
        print("AUDIT RESULT:")
        print("-" * 80)
        pprint.pprint(result["audit_result"])

        # --- Show the full ledger ---
        print("\n" + "-" * 80)
        print("FULL LEDGER STATE:")
        print("-" * 80)
        pprint.pprint(self.ledger)

        # --- Basic assertions ---
        assert result["turn_count"] == 1
        assert len(self.ledger["rubric"]["dimensions"]) > 0, "Rubric dimensions should be generated"
        assert len(self.ledger["rules"]) > 0, "Boundary rules should be generated"

        response_lower = result["raw_response"].lower()
        assert "isro" in response_lower, "Response should mention ISRO"
        assert any(year in response_lower for year in ["1969", "1962"]), \
            "Response should mention ISRO founding year (1969 or INCOSPAR 1962)"

        print("\n" + "=" * 80)
        print(f"RULES GENERATED: {len(self.ledger['rules'])}")
        print(f"RUBRIC DIMENSIONS: {len(self.ledger['rubric']['dimensions'])}")
        print(f"ASSUMPTIONS: {len(self.ledger['assumptions'])}")
        print(f"MISSING INFO: {len(self.ledger['missing_info_registry'])}")
        print(f"CONTRADICTIONS: {len(self.ledger['contradiction_log'])}")
        print("=" * 80)
