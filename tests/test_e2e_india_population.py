"""tests/test_e2e_india_population.py
End-to-end smoke test for the two-part prompt:
  Turn 1: "what is india population?"
  Turn 2: "what was it in 2020?"

Runs the full pipeline (rubric → main generation → contradiction check →
claim classification → completeness audit) against the live Gemini API and
prints a structured report.  No mocking — this is a true integration test.

Run with:
    cd "d:\\Projects\\Graduation Project 2\\stateful_ledger"
    python -m pytest tests/test_e2e_india_population.py -v -s
"""
import json
import pprint
import time
import pytest

# Project imports (resolved relative to workspace root)
from ledger.manager import init_ledger, get_snapshot, update_ledger
from ledger.schema import Assumption, MissingInfo, VerifiedResponse, Paragraph, Claim
from engine.gemini_client import call_gemini
from engine.prompt_builder import build_rubric_prompt, build_main_prompt
from engine.layer1 import (
    run_contradiction_check,
    run_completeness_audit,
    extract_assumptions_and_missing,
)
from engine.layer2 import run_claim_classification, detect_overconfidence
from utils.id_gen import generate_id


# ── Helper: mirror app._parse_verified_response without importing Streamlit ──
def parse_verified_response(raw: dict) -> VerifiedResponse:
    paragraphs = []
    for p_data in raw.get("paragraphs", []):
        claims = [
            Claim(
                claim_id=c.get("claim_id", generate_id()),
                text=c.get("text", ""),
                tag=c.get("tag", "inferred"),
            )
            for c in p_data.get("claims", [])
        ]
        para = Paragraph(
            index=p_data.get("index", 0),
            text=p_data.get("text", ""),
            claims=claims,
            step_type=p_data.get("step_type"),
        )
        paragraphs.append(para)
    return VerifiedResponse(paragraphs=paragraphs)


# ── Helper: run a single turn through the pipeline ──
def run_turn(user_input: str, ledger, max_retries: int = 5) -> dict:
    """
    Returns a result dict with all pipeline artefacts for inspection.
    Raises AssertionError on critical failures.
    """
    snapshot = get_snapshot(ledger)
    sys_prompt, usr_prompt = build_main_prompt(user_input, snapshot)

    # Call #1 — Main generation
    raw_response = call_gemini(sys_prompt, usr_prompt, max_retries=max_retries)
    assert "error" not in raw_response, (
        f"Call #1 failed: {raw_response.get('error')} | raw: {raw_response.get('raw_text', '')[:300]}"
    )

    verified_response = parse_verified_response(raw_response)
    assumption_texts, missing_texts = extract_assumptions_and_missing(raw_response)

    new_assumptions = [
        Assumption(text=a, turn_index=ledger.turn_count) for a in assumption_texts
    ]
    new_missing = [
        MissingInfo(text=m, turn_index=ledger.turn_count) for m in missing_texts
    ]

    # Call #2 — Contradiction check
    contradiction_flags = run_contradiction_check(user_input, verified_response, ledger)

    # Call #3 — Claim classification (search-grounded)
    verified_response = run_claim_classification(verified_response)
    verified_response = detect_overconfidence(verified_response)

    # Completeness audit
    completeness_gaps = run_completeness_audit(
        verified_response, ledger.rubric.criteria
    )

    # Update ledger
    update_ledger(
        ledger, user_input, verified_response,
        new_assumptions, new_missing,
        contradiction_flags, completeness_gaps,
    )

    return {
        "user_input": user_input,
        "raw_response": raw_response,
        "verified_response": verified_response,
        "assumptions": assumption_texts,
        "missing_info": missing_texts,
        "contradiction_flags": contradiction_flags,
        "completeness_gaps": completeness_gaps,
        "trust_score": ledger.trust_score,
        "turn_count": ledger.turn_count,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestIndiaPopulationE2E:
    """Full end-to-end tests for the two-part India population prompt."""

    @pytest.fixture(autouse=True)
    def setup_ledger(self):
        """Fresh ledger for every test — no shared state.
        
        A 7-second inter-test cooldown keeps us well under gemini-2.5-flash-lite's
        10 RPM free-tier limit (each turn makes ~3 API calls).
        """
        self.ledger = init_ledger()
        yield
        time.sleep(7)  # rate-limit cooldown between tests

    # ── Turn 0: Rubric generation ─────────────────────────────────────────────

    def test_rubric_generation(self):
        """Rubric should be generated for the first user prompt."""
        user_input = "what is india population? what was it in 2020?"
        sys_prompt, usr_prompt = build_rubric_prompt(user_input)
        result = call_gemini(sys_prompt, usr_prompt)

        print("\n[RUBRIC RESULT]")
        pprint.pprint(result)

        assert "error" not in result, f"Rubric call failed: {result}"
        assert "goal_type" in result, "Missing 'goal_type' in rubric response"
        assert "rubric_criteria" in result, "Missing 'rubric_criteria' in rubric response"
        assert isinstance(result["rubric_criteria"], list), "'rubric_criteria' must be a list"
        assert len(result["rubric_criteria"]) >= 1, "At least one rubric criterion expected"

        # Seed the ledger rubric so subsequent turns have context
        self.ledger.goal_type = result.get("goal_type", "exploratory")
        self.ledger.rubric.criteria = result.get("rubric_criteria", [])
        self.ledger.rubric_confirmed = True

    # ── Turn 1: "what is india population?" ──────────────────────────────────

    def test_turn1_response_structure(self):
        """Turn 1 — response must have at least one paragraph with claims."""
        self._seed_rubric()
        result = run_turn("what is india population? what was it in 2020?", self.ledger)

        print("\n[TURN 1 RESULT]")
        self._print_result(result)

        vr: VerifiedResponse = result["verified_response"]
        assert len(vr.paragraphs) >= 1, "Expected at least one paragraph"

        # At least one paragraph must mention 'india' or 'population' or a number
        full_text = " ".join(p.text.lower() for p in vr.paragraphs)
        assert any(kw in full_text for kw in ["india", "population", "billion", "million"]), (
            f"Response doesn't appear to address India population. Got:\n{full_text[:500]}"
        )

    def test_turn1_claims_present(self):
        """Turn 1 — at least one factual claim must be extracted."""
        self._seed_rubric()
        result = run_turn("what is india population? what was it in 2020?", self.ledger)
        vr: VerifiedResponse = result["verified_response"]
        all_claims = [c for p in vr.paragraphs for c in p.claims]

        print(f"\n[TURN 1] Total claims extracted: {len(all_claims)}")
        for c in all_claims:
            print(f"  • [{c.tag}] {c.text[:100]}")

        assert len(all_claims) >= 1, "Expected at least one claim to be extracted"

    def test_turn1_trust_score_updated(self):
        """Turn 1 — trust score must be between 0 and 1 after update."""
        self._seed_rubric()
        result = run_turn("what is india population? what was it in 2020?", self.ledger)

        print(f"\n[TURN 1] Trust score: {result['trust_score']}")
        assert 0.0 <= result["trust_score"] <= 1.0, (
            f"Trust score out of range: {result['trust_score']}"
        )

    def test_turn1_no_critical_contradictions(self):
        """Turn 1 — an empty ledger should produce zero contradiction flags."""
        self._seed_rubric()
        result = run_turn("what is india population? what was it in 2020?", self.ledger)
        direct_flags = [f for f in result["contradiction_flags"] if f.severity == "direct"]

        print(f"\n[TURN 1] Contradiction flags: {len(result['contradiction_flags'])}")
        assert len(direct_flags) == 0, (
            f"Unexpected direct contradictions on first turn: {direct_flags}"
        )

    # ── Turn 2: "what was it in 2020?" (follow-up referencing context) ────────

    def test_turn2_context_carryover(self):
        """Turn 2 — ledger context from turn 1 must carry over."""
        self._seed_rubric()

        # Run turn 1 first to populate ledger
        run_turn("what is india population? what was it in 2020?", self.ledger)

        # Now ask the follow-up
        result = run_turn("what was the population specifically in 2020?", self.ledger)

        print("\n[TURN 2 RESULT]")
        self._print_result(result)

        assert result["turn_count"] == 2, (
            f"Expected turn_count=2, got {result['turn_count']}"
        )

        full_text = " ".join(p.text.lower() for p in result["verified_response"].paragraphs)
        assert any(kw in full_text for kw in ["2020", "billion", "million", "population"]), (
            f"Turn 2 response doesn't reference 2020 or population data. Got:\n{full_text[:500]}"
        )

    def test_two_turn_full_pipeline(self):
        """Full two-turn smoke test — everything must succeed without errors."""
        self._seed_rubric()

        print("\n" + "=" * 60)
        print("FULL E2E: India Population — 2-Turn Conversation")
        print("=" * 60)

        # Turn 1
        r1 = run_turn("what is india population? what was it in 2020?", self.ledger)
        print("\n── Turn 1 ──")
        self._print_result(r1)

        # Turn 2
        r2 = run_turn("what was the population specifically in 2020?", self.ledger)
        print("\n── Turn 2 ──")
        self._print_result(r2)

        # Assertions
        assert r1["turn_count"] == 1
        assert r2["turn_count"] == 2
        assert len(r1["verified_response"].paragraphs) >= 1
        assert len(r2["verified_response"].paragraphs) >= 1

        print("\n✅ Full two-turn pipeline completed successfully.")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _seed_rubric(self):
        """Seed a default rubric so tests can skip the rubric API call."""
        self.ledger.goal_type = "analytical"
        self.ledger.rubric.criteria = [
            "Factual accuracy",
            "Completeness of data",
            "Clarity of explanation",
            "Historical context (2020 data)",
        ]
        self.ledger.rubric_confirmed = True

    @staticmethod
    def _print_result(result: dict):
        print(f"  User: {result['user_input']}")
        print(f"  Turn: {result['turn_count']}")
        print(f"  Trust score: {result['trust_score']:.2f}")
        print(f"  Paragraphs: {len(result['verified_response'].paragraphs)}")
        all_claims = [c for p in result["verified_response"].paragraphs for c in p.claims]
        print(f"  Claims: {len(all_claims)}")
        print(f"  Assumptions: {result['assumptions']}")
        print(f"  Missing info: {result['missing_info']}")
        print(f"  Contradiction flags: {len(result['contradiction_flags'])}")
        print(f"  Completeness gaps: {result['completeness_gaps']}")
        print("\n  Response text:")
        for p in result["verified_response"].paragraphs:
            print(f"    [{p.step_type}] {p.text[:200]}")
