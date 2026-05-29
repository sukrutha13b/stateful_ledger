import uuid
from datetime import datetime, timezone
from schemas.ledger_schemas import LedgerSchema

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def init_empty_ledger() -> LedgerSchema:
    """Returns the pure JSON-serializable dict for the initial ledger state."""
    return {
        "ledger_id": str(uuid.uuid4()),
        "session_created_at": _now_iso(),
        "total_turns": 0,
        "rubric": {
            "auto_generated": False,
            "generated_at_turn": 1,
            "dimensions": []
        },
        "rules": [],
        "assumptions": [],
        "missing_info_registry": [],
        "contradiction_log": [],
        "turn_history": []
    }


def update_ledger(ledger: dict, audit_result: dict, turn_number: int):
    """
    Update ledger state based on the structured audit result from Pass 2.
    No AI calls, pure Python logic.
    """
    if not audit_result:
        return
        
    import uuid

    # 1. Evaluate each rule_check result
    for rule_check in audit_result.get("rule_checks", []):
        for rule in ledger["rules"]:
            if rule["rule_id"] == rule_check["rule_id"]:
                if rule_check["status"] == "Violated":
                    # Create contradiction
                    contradiction = {
                        "contradiction_id": f"contra_{uuid.uuid4().hex[:8]}",
                        "description": f"Violation of rule: {rule['text']}. Evidence: {rule_check['evidence']}",
                        "conflicting_elements": [rule["rule_id"], f"turn_{turn_number}"],
                        "identified_at_turn": turn_number,
                        "severity": "Medium", # Will be assigned by router if needed, fallback to Medium
                        "resolution_status": "pending",
                        "resolution_action": None,
                        "resolved_at_turn": None
                    }
                    ledger["contradiction_log"].append(contradiction)
                    rule["violation_count"] = rule.get("violation_count", 0) + 1
                elif rule_check["status"] == "Satisfied":
                    rule["last_evaluated_at"] = _now_iso()

    # 2. Update rubric coverage scores
    for r_score in audit_result.get("rubric_scores", []):
        for dim in ledger["rubric"]["dimensions"]:
            if dim["name"] == r_score["dimension_name"] or dim["id"] == r_score["dimension_id"]:
                dim["last_coverage_score"] = r_score["coverage_score"]
                dim.setdefault("coverage_history", []).append(r_score["coverage_score"])
    
    # 3. New missing info items
    from utils.deduplication import deduplicate_missing_info
    new_missing = []
    for m in audit_result.get("new_missing_info", []):
        new_missing.append({
            "item_id": f"missing_{uuid.uuid4().hex[:8]}",
            "description": m["description"],
            "identified_at_turn": turn_number,
            "severity": m["severity"],
            "resolved": False,
            "resolved_at_turn": None,
            "resolution_note": None
        })
    # Deduplicate against existing missing info
    if new_missing:
        deduplicated = deduplicate_missing_info(ledger["missing_info_registry"], new_missing)
        ledger["missing_info_registry"].extend(deduplicated)

    # 4. New Assumptions
    for asm in audit_result.get("new_assumptions", []):
        ledger["assumptions"].append({
            "assumption_id": f"assump_{uuid.uuid4().hex[:8]}",
            "text": asm["text"],
            "source_turn": turn_number,
            "confidence": asm["confidence"],
            "status": "active",
            "invalidated_at_turn": None,
            "invalidation_reason": None
        })
        
    # 5. New Contradictions from the audit output directly
    for contra in audit_result.get("new_contradictions", []):
        ledger["contradiction_log"].append({
            "contradiction_id": f"contra_{uuid.uuid4().hex[:8]}",
            "description": contra["description"],
            "conflicting_elements": contra["conflicting_elements"],
            "identified_at_turn": turn_number,
            "severity": contra["severity"],
            "resolution_status": "pending",
            "resolution_action": None,
            "resolved_at_turn": None
        })

