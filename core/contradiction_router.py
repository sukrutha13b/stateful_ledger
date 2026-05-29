def route_contradiction(contradiction: dict, ledger: dict):
    """
    Determines severity and actions for a contradiction if not pre-assigned.
    """
    # Simple routing logic: severity is pre-assigned
    severity = contradiction.get("severity", "Medium")
    
    if severity == "High":
        pass  # High-severity contradictions are tracked in contradiction_log
    
def flag_overconfidence(audit_result: dict, grounding_result: dict, turn_record: dict) -> dict | None:
    """
    Section 4.3: Overconfident AI Responses.
    Compares internal audit confidence with external grounding contested ratio.
    """
    import uuid
    from config import OVERCONFIDENCE_THRESHOLD, CONTESTED_RATIO_THRESHOLD
    
    internal_confidence = audit_result.get("overall_audit_confidence", 0)
    
    # Internal confidence flag logic (set during Pass 2 if high)
    if internal_confidence >= OVERCONFIDENCE_THRESHOLD:
        tags = audit_result.get("sentence_tags", [])
        if tags:
            reasoned_count = sum(1 for t in tags if t["tag"] == "Reasoned")
            if reasoned_count / len(tags) >= 0.8:
                turn_record["internal_confidence_flag"] = "High"
                
    # If grounding result is present, check for divergence
    if grounding_result and grounding_result.get("status") == "completed":
        claims = grounding_result.get("claims", [])
        if claims and turn_record.get("internal_confidence_flag") == "High":
            contested_count = sum(1 for c in claims if c.get("classification") == "Contested")
            contested_ratio = contested_count / len(claims)
            
            if contested_ratio >= CONTESTED_RATIO_THRESHOLD:
                # Returns a new contradiction
                return {
                    "contradiction_id": f"contra_{uuid.uuid4().hex[:8]}",
                    "description": f"This response scored {internal_confidence}/100 on internal logic but {int(contested_ratio*100)}% of claims are externally contested.",
                    "conflicting_elements": ["overconfidence_divergence"],
                    "identified_at_turn": turn_record["turn_number"],
                    "severity": "High",
                    "resolution_status": "pending",
                    "resolution_action": None,
                    "resolved_at_turn": None
                }
    return None
