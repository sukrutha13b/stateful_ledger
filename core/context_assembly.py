import json

def assemble_context(ledger: dict, user_prompt: str) -> str:
    """Builds a structured string injected as the system prompt for Pass 1. No AI call."""
    
    active_rules = [r for r in ledger.get("rules", []) if r.get("status") == "active"]
    active_assumptions = [a for a in ledger.get("assumptions", []) if a.get("status") == "active"]
    missing_info = [m for m in ledger.get("missing_info_registry", []) if not m.get("resolved")]
    rubric_dims = ledger.get("rubric", {}).get("dimensions", [])
    
    pending_contradictions = [c for c in ledger.get("contradiction_log", []) if c.get("resolution_status") == "pending"]

    # History construction (last N turns)
    # Using 10 as N or from config
    try:
        from config import MAX_HISTORY_TURNS_IN_PROMPT
        history_limit = MAX_HISTORY_TURNS_IN_PROMPT
    except ImportError:
        history_limit = 10
        
    history = ledger.get("turn_history", [])[-history_limit:]
    history_text = ""
    for t in history:
        history_text += f"USER (Turn {t['turn_number']}): {t['user_prompt']}\n"
        history_text += f"AI (Turn {t['turn_number']}): {t['raw_response']}\n\n"

    system_context = []
    system_context.append("-- [SYSTEM CONTEXT BLOCK] --------------------")
    
    system_context.append(" ACTIVE RULES:")
    if active_rules:
        for r in active_rules:
            system_context.append(f"  - {r['rule_id']}: {r['text']}")
    else:
        system_context.append("  (None)")
        
    system_context.append(" ACTIVE ASSUMPTIONS:")
    if active_assumptions:
        for a in active_assumptions:
            system_context.append(f"  - {a['assumption_id']}: {a['text']}")
    else:
        system_context.append("  (None)")

    system_context.append(" KNOWN MISSING INFO:")
    if missing_info:
        for m in missing_info:
            system_context.append(f"  - {m['item_id']}: {m['description']}")
    else:
        system_context.append("  (None)")

    system_context.append(" EVALUATION RUBRIC:")
    if rubric_dims:
        for dim in rubric_dims:
            system_context.append(f"  - {dim['name']}: {dim.get('description', '')}")
    else:
        system_context.append("  (None)")

    system_context.append(" CONTRADICTION LOG:")
    if pending_contradictions:
        for c in pending_contradictions:
            system_context.append(f"  - {c['contradiction_id']} (Turn {c['identified_at_turn']}): {c['description']}")
    else:
        system_context.append("  (None)")

    system_context.append("------------------------------------------------")
    
    context_str = "\n".join(system_context)
    
    if pending_contradictions:
        latest_turn = pending_contradictions[-1]['identified_at_turn']
        context_str += f"\n\n[DIRECTIVE] There is an unresolved contradiction from Turn {latest_turn}. Do not resolve it autonomously. Surface it explicitly in your response."

    if history_text:
        context_str += f"\n\n=== CHAT HISTORY ===\n{history_text}"

    return context_str
