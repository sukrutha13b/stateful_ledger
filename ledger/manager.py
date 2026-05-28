"""ledger/manager.py — Ledger lifecycle operations.

All mutations to the Ledger go through functions in this module so that
higher layers never manipulate the dataclass directly.
"""
from dataclasses import asdict

from ledger.schema import (
    Ledger, Rule, Assumption, MissingInfo,
    InteractionTurn, VerifiedResponse, ContradictionFlag,
)


# ── Lifecycle ────────────────────────────────────────

def init_ledger() -> Ledger:
    """Create a fresh Ledger instance for a new session."""
    return Ledger()


# ── Snapshots ────────────────────────────────────────

def get_snapshot(ledger: Ledger, max_turns: int = 10) -> dict:
    """Return a serialisable dict of the ledger for prompt injection.

    Caps interaction_history to the last *max_turns* entries so the
    snapshot fits within the model's context window.
    """
    snapshot = asdict(ledger)
    snapshot["interaction_history"] = snapshot["interaction_history"][-max_turns:]
    return snapshot


def export_ledger(ledger: Ledger) -> dict:
    """Export the full ledger as a dict for JSON download."""
    return asdict(ledger)


def import_ledger(data: dict) -> Ledger:
    """Import a ledger from a parsed JSON dict, reconstructing nested dataclasses."""
    from ledger.schema import (
        Rubric, Rule, Assumption, MissingInfo, InteractionTurn,
        VerifiedResponse, Paragraph, Claim, ContradictionFlag, UserFeedback
    )
    
    # Extract basic fields
    session_id = data.get("session_id", "")
    goal_type = data.get("goal_type", "exploratory")
    rubric_confirmed = data.get("rubric_confirmed", False)
    trust_score = data.get("trust_score", 0.0)
    turn_count = data.get("turn_count", 0)
    
    # Reconstruct Rubric
    rubric_data = data.get("rubric", {})
    rubric = Rubric(
        criteria=rubric_data.get("criteria", []),
        is_edited_by_user=rubric_data.get("is_edited_by_user", False),
        version=rubric_data.get("version", 1)
    )
    
    # Reconstruct simple lists
    rules = [Rule(**r) for r in data.get("rules", [])]
    assumptions = [Assumption(**a) for a in data.get("assumptions", [])]
    missing_info = [MissingInfo(**m) for m in data.get("missing_info", [])]
    
    # Reconstruct Interaction History
    interaction_history = []
    for turn_data in data.get("interaction_history", []):
        # 1. Verified Response
        vr = None
        vr_data = turn_data.get("verified_response")
        if vr_data:
            paragraphs = []
            for p_data in vr_data.get("paragraphs", []):
                claims = [Claim(**c) for c in p_data.get("claims", [])]
                paragraphs.append(Paragraph(
                    index=p_data.get("index", 0),
                    text=p_data.get("text", ""),
                    claims=claims,
                    step_type=p_data.get("step_type")
                ))
            vr = VerifiedResponse(paragraphs=paragraphs)
        
        # 2. Contradiction Flags
        flags = [ContradictionFlag(**f) for f in turn_data.get("contradiction_flags", [])]
        
        # 3. User Feedback
        fb_data = turn_data.get("user_feedback", {})
        feedback = UserFeedback(
            accurate=fb_data.get("accurate", []),
            inaccurate=fb_data.get("inaccurate", []),
            uncertain=fb_data.get("uncertain", [])
        )
        
        turn = InteractionTurn(
            turn_index=turn_data.get("turn_index", 0),
            role=turn_data.get("role", "user"),
            raw_input=turn_data.get("raw_input", ""),
            verified_response=vr,
            contradiction_flags=flags,
            completeness_gaps=turn_data.get("completeness_gaps", []),
            user_feedback=feedback
        )
        interaction_history.append(turn)

    ledger = Ledger(
        session_id=session_id,
        goal_type=goal_type,
        rubric=rubric,
        rubric_confirmed=rubric_confirmed,
        rules=rules,
        assumptions=assumptions,
        missing_info=missing_info,
        interaction_history=interaction_history,
        trust_score=trust_score,
        turn_count=turn_count
    )
    
    # Fallback to new ID if empty
    if not ledger.session_id:
        from utils.id_gen import generate_id
        ledger.session_id = generate_id()
        
    return ledger


# ── Turn Management ──────────────────────────────────

def update_ledger(
    ledger: Ledger,
    user_input: str,
    verified_response: VerifiedResponse,
    new_assumptions: list[Assumption],
    new_missing_info: list[MissingInfo],
    contradiction_flags: list[ContradictionFlag],
    completeness_gaps: list[str],
) -> Ledger:
    """Append a new turn to the ledger after processing is complete.

    Returns the *mutated* ledger (same object, not a copy).
    """
    turn = InteractionTurn(
        turn_index=ledger.turn_count,
        role="assistant",
        raw_input=user_input,
        verified_response=verified_response,
        contradiction_flags=contradiction_flags,
        completeness_gaps=completeness_gaps,
    )
    ledger.interaction_history.append(turn)
    ledger.assumptions.extend(new_assumptions)
    ledger.missing_info.extend(new_missing_info)
    ledger.turn_count += 1
    return ledger


# ── Rule CRUD ────────────────────────────────────────

def add_rule(ledger: Ledger, text: str, source: str = "user") -> Rule:
    """Add a new rule to the ledger. Returns the created Rule."""
    rule = Rule(text=text, source=source, created_at=ledger.turn_count)
    ledger.rules.append(rule)
    return rule


def remove_rule(ledger: Ledger, rule_id: str) -> bool:
    """Remove a rule by ID. Returns True if found and removed."""
    for i, rule in enumerate(ledger.rules):
        if rule.id == rule_id:
            ledger.rules.pop(i)
            return True
    return False


def update_rule(ledger: Ledger, rule_id: str, new_text: str) -> bool:
    """Update a rule's text by ID. Returns True if found and updated."""
    for rule in ledger.rules:
        if rule.id == rule_id:
            rule.text = new_text
            return True
    return False


def get_active_rules(ledger: Ledger) -> list[Rule]:
    """Return only active rules."""
    return [r for r in ledger.rules if r.active]
