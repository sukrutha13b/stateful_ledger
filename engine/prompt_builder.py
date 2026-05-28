"""engine/prompt_builder.py — Prompt templates for all Gemini API calls.

Each builder returns a ``(system_prompt, user_prompt)`` tuple that can be
passed directly to ``call_gemini()``.

Call #1a  — ``build_rubric_prompt``      → Goal-type + rubric inference
Call #1b  — ``build_main_prompt``        → Structured response generation
Call #2   — ``build_contradiction_prompt`` → Contradiction detection
Call #3   — ``build_classification_prompt`` → Claim classification (search-grounded)
"""
import json


# ══════════════════════════════════════════════════════
# Call #1a (Rubric): Infer goal type + rubric
# ══════════════════════════════════════════════════════

def build_rubric_prompt(user_input: str) -> tuple[str, str]:
    """Build system + user prompt for rubric generation (first turn only).

    Returns:
        ``(system_prompt, user_prompt)``
    """
    system_prompt = """You are a goal classification assistant for the Stateful Ledger system.
Analyze the user's first message and:
1. Infer the goal type: one of "analytical", "creative", "technical", "exploratory"
2. Generate 3-5 evaluation rubric criteria appropriate for this goal type.

Return ONLY valid JSON matching this schema:
{
    "goal_type": "analytical|creative|technical|exploratory",
    "rubric_criteria": ["criterion 1", "criterion 2", ...]
}
No markdown fences. No preamble."""

    user_prompt = f"User's first message:\n\n{user_input}"
    return system_prompt, user_prompt


# ══════════════════════════════════════════════════════
# Call #1b (Main): Structured response generation
# ══════════════════════════════════════════════════════

MAIN_RESPONSE_SCHEMA = """{
    "paragraphs": [
        {
            "index": 0,
            "text": "paragraph text",
            "claims": [
                {
                    "claim_id": "unique_id",
                    "text": "discrete factual claim",
                    "tag": "established|reasoned|inferred"
                }
            ],
            "step_type": "inference|assumption|established_fact"
        }
    ],
    "assumptions": ["assumption 1", "assumption 2"],
    "missing_info": ["info 1", "info 2"],
    "goal_type": "analytical|creative|technical|exploratory (FIRST TURN ONLY, omit otherwise)",
    "rubric_criteria": ["criterion 1", "criterion 2", "(FIRST TURN ONLY, omit otherwise)"]
}"""


def build_main_prompt(
    user_input: str,
    ledger_snapshot: dict,
    is_first_turn: bool = False,
) -> tuple[str, str]:
    """Build system + user prompt for main response generation (Call #1).

    Injects ledger context (rules, assumptions, goal type, rubric)
    into the system prompt so the model is aware of session state.
    On the first turn, also requests goal_type and rubric_criteria inline
    so a separate rubric call is not needed.

    Returns:
        ``(system_prompt, user_prompt)``
    """
    rules_text = json.dumps(
        [r["text"] for r in ledger_snapshot.get("rules", []) if r.get("active", True)],
        indent=2
    )
    assumptions_text = json.dumps(
        [a["text"] for a in ledger_snapshot.get("assumptions", [])],
        indent=2
    )
    goal_type = ledger_snapshot.get("goal_type", "exploratory")
    rubric_criteria = json.dumps(
        ledger_snapshot.get("rubric", {}).get("criteria", []),
        indent=2
    )

    first_turn_instruction = ""
    if is_first_turn:
        first_turn_instruction = """
6. Since this is the FIRST turn, also infer:
   - goal_type: one of \"analytical\", \"creative\", \"technical\", \"exploratory\"
   - rubric_criteria: 3-5 evaluation criteria appropriate for this goal type
   Include both fields in your JSON response.
"""

    system_prompt = f"""You are a precise reasoning assistant operating within a Stateful Ledger system.

ACTIVE LEDGER STATE:
Rules: {rules_text}
Assumptions established: {assumptions_text}
Goal type: {goal_type}
Rubric criteria: {rubric_criteria}

INSTRUCTIONS:
1. Generate a comprehensive response to the user's query.
2. For EACH paragraph, tag its reasoning type:
   - \"established_fact\": grounded in prior session context or verifiable data
   - \"assumption\": a premise taken without explicit grounding
   - \"inference\": derived logically from context but not directly stated
3. For each paragraph, extract discrete factual claims as a flat list.
   Tag each claim as \"established\", \"reasoned\", or \"inferred\".
4. List ALL assumptions you are making in this response.
5. List ALL information that was NOT available to you.{first_turn_instruction}

Return ONLY valid JSON matching this schema:
{MAIN_RESPONSE_SCHEMA}
No markdown fences. No preamble."""

    user_prompt = user_input
    return system_prompt, user_prompt


# ══════════════════════════════════════════════════════
# Call #2: Contradiction Check
# ══════════════════════════════════════════════════════

def build_contradiction_prompt(
    rules: list[dict],
    user_input: str,
    response_text: str,
) -> tuple[str, str]:
    """Build system + user prompt for contradiction detection (Call #2).

    Returns:
        ``(system_prompt, user_prompt)``
    """
    rules_json = json.dumps(
        [{"id": r["id"], "text": r["text"]} for r in rules if r.get("active", True)],
        indent=2
    )

    system_prompt = """You are a contradiction detection engine for the Stateful Ledger system.
Compare the user's prompt and the assistant's response against the established rules.
Identify any contradictions between the new content and the established rules.

Return ONLY valid JSON:
{
    "violations": [
        {
            "rule_id": "id of the violated rule",
            "conflict_text": "the specific text that conflicts",
            "severity": "direct|tension"
        }
    ]
}
If no contradictions exist, return: {"violations": []}
No markdown fences. No preamble."""

    user_prompt = f"""Active rules:
{rules_json}

User prompt:
{user_input}

Assistant response:
{response_text}"""

    return system_prompt, user_prompt


# ══════════════════════════════════════════════════════
# Call #3: Claim Classification with Search Grounding
# ══════════════════════════════════════════════════════

def build_classification_prompt(claims: list[dict]) -> tuple[str, str]:
    """Build system + user prompt for claim classification (Call #3).

    This call should use Google Search grounding (``use_search_grounding=True``).

    Returns:
        ``(system_prompt, user_prompt)``
    """
    system_prompt = """You are a claim verification engine. Classify each claim using Google Search grounding where available.

For each claim, return:
- classification: "grounded" | "contested" | "unverified"
- perspectives: [] (only if contested — 2 to 3 alternative framings, neutral phrasing)
- sources: [] (only if grounded — brief source descriptions)

Return ONLY valid JSON:
{
    "classified_claims": [
        {
            "claim_id": "id",
            "classification": "grounded|contested|unverified",
            "perspectives": [],
            "sources": []
        }
    ]
}
No markdown fences. No preamble."""

    claims_text = "\n".join(
        f"{i+1}. [ID: {c['claim_id']}] {c['text']}"
        for i, c in enumerate(claims)
    )

    user_prompt = f"Classify these claims:\n\n{claims_text}"
    return system_prompt, user_prompt
