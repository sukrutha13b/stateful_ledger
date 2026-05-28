from dataclasses import asdict
from ledger.schema import (
    Ledger, ContradictionFlag, VerifiedResponse
)
from engine.prompt_builder import build_contradiction_prompt
from engine.gemini_client import call_gemini
from utils.id_gen import generate_id


def run_contradiction_check(
    user_input: str,
    response: VerifiedResponse,
    ledger: Ledger,
) -> list[ContradictionFlag]:
    """
    Call #2: Check if the user's prompt or the response contradicts active ledger rules.
    Returns a list of ContradictionFlags.
    """
    active_rules = [asdict(r) for r in ledger.rules if r.active]
    if not active_rules:
        return []

    # Build full response text from paragraphs
    response_text = "\n\n".join(p.text for p in response.paragraphs)

    system_prompt, user_prompt = build_contradiction_prompt(
        rules=active_rules,
        user_input=user_input,
        response_text=response_text,
    )

    result = call_gemini(system_prompt, user_prompt)

    if "error" in result:
        return []  # Graceful degradation: skip contradiction check on API failure

    flags = []
    for v in result.get("violations", []):
        flag = ContradictionFlag(
            flag_id=generate_id(),
            conflict_text=v.get("conflict_text", ""),
            conflicting_rule_id=v.get("rule_id", ""),
            severity=v.get("severity", "tension"),
            conflict_message=(
                f"This conflicts with Rule '{v.get('rule_id', '?')}'. "
                f"You can update the rule, override for this response, "
                f"or keep both and I'll flag the tension."
            ),
        )
        flags.append(flag)

    return flags


def run_completeness_audit(
    response: VerifiedResponse,
    rubric_criteria: list[str],
) -> list[str]:
    """
    Check which rubric criteria are not addressed in the response.
    Uses keyword matching first, then falls back to semantic matching if needed.
    Returns list of unaddressed criteria.
    """
    gaps = []
    full_text = " ".join(p.text.lower() for p in response.paragraphs)

    for criterion in rubric_criteria:
        # Simple keyword-based check: split criterion into words, check if most appear
        keywords = [w.lower() for w in criterion.split() if len(w) > 3]
        if not keywords:
            continue

        match_count = sum(1 for kw in keywords if kw in full_text)
        coverage_ratio = match_count / len(keywords) if keywords else 0

        if coverage_ratio < 0.5:
            gaps.append(criterion)

    return gaps


def extract_assumptions_and_missing(
    raw_response: dict,
) -> tuple[list[str], list[str]]:
    """
    Extract assumptions and missing_info from the raw Gemini Call #1 response.
    Returns (assumptions_list, missing_info_list).
    """
    assumptions = raw_response.get("assumptions", [])
    missing_info = raw_response.get("missing_info", [])

    # Ensure they're lists of strings
    if not isinstance(assumptions, list):
        assumptions = []
    if not isinstance(missing_info, list):
        missing_info = []

    return (
        [str(a) for a in assumptions],
        [str(m) for m in missing_info],
    )
