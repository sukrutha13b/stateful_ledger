"""tests/test_e2e_isro_ad_sprint.py
End-to-end test: One-week sprint plan for creating an AD on ISRO's achievements.
Measures wall-clock time for the full pipeline and prints answer + ledger.
"""
import pytest
import time
import json
import pprint

from google.api_core.exceptions import ResourceExhausted

from core.ledger import init_empty_ledger, update_ledger
from core.context_assembly import assemble_context
from gemini.client import GeminiClient
from schemas.audit_schemas import AuditResult, RubricBootstrapSchema
from gemini.prompts import AUDIT_SYSTEM_PROMPT, AUDIT_USER_PROMPT_TEMPLATE, RUBRIC_BOOTSTRAP_PROMPT


# -- Retry helper ------------------------------------------------------------

import re as _re

_DAILY_QUOTA_IDS = {"GenerateRequestsPerDayPerProjectPerModel-FreeTier"}

def _parse_retry_seconds(exc: ResourceExhausted) -> float:
    """Extract the suggested retry delay (seconds) from a 429 error message."""
    msg = str(exc)
    m = _re.search(r"retry[_\s]delay\s*\{?\s*seconds:\s*(\d+)", msg)
    if m:
        return float(m.group(1)) + 2   # add 2s buffer
    m = _re.search(r"retry in ([\d.]+)s", msg, _re.IGNORECASE)
    if m:
        return float(m.group(1)) + 2
    return 30.0   # safe default


def _is_daily_quota(exc: ResourceExhausted) -> bool:
    """Return True when the daily free-tier quota is exhausted."""
    msg = str(exc)
    return any(qid in msg for qid in _DAILY_QUOTA_IDS)


def _with_retry(fn, max_retries=4):
    """Call fn(); on ResourceExhausted (429) wait the API-suggested delay and retry.
    If the daily quota is exhausted and all retries are spent, skip the test.
    """
    for attempt in range(max_retries):
        try:
            return fn()
        except ResourceExhausted as exc:
            is_daily = _is_daily_quota(exc)
            suggested = _parse_retry_seconds(exc)

            if attempt == max_retries - 1:
                if is_daily:
                    pytest.skip(
                        f"Gemini free-tier DAILY quota exhausted "
                        f"({max_retries} retries spent). "
                        f"Re-run after quota resets (typically midnight UTC). "
                        f"Original error: {exc}"
                    )
                raise  # non-daily quota: propagate as failure

            wait = max(suggested, 15)   # never wait less than 15s
            kind = "DAILY" if is_daily else "RPM"
            print(f"\n[RATE LIMIT {kind}] 429 hit - "
                  f"waiting {wait:.0f}s before retry "
                  f"(attempt {attempt + 1}/{max_retries})...")
            time.sleep(wait)


# -- Shared pipeline helper (mirrors test_e2e_isro.py) ------------------------

def run_turn(user_input: str, ledger: dict) -> dict:
    client = GeminiClient()

    if ledger["total_turns"] == 0:
        # Stage 0  Rubric Bootstrap
        prompt = f"{RUBRIC_BOOTSTRAP_PROMPT}\n\nQuery: {user_input}"
        bootstrap = _with_retry(lambda: client.generate_structured(prompt, RubricBootstrapSchema))
        if bootstrap:
            ledger["rubric"]["dimensions"] = [
                {"id": f"dim_{i}", "name": d.name, "description": d.description}
                for i, d in enumerate(bootstrap.evaluation_dimensions)
            ]
            ledger["rules"] = [
                {
                    "rule_id": f"rule_{i}", "text": r, "status": "active",
                    "type": "auto", "source_turn": 1, "violation_count": 0,
                }
                for i, r in enumerate(bootstrap.initial_boundary_rules)
            ]
            ledger["rubric"]["auto_generated"] = True

    ledger["total_turns"] += 1
    turn_num = ledger["total_turns"]

    # Stage 1  Context Assembly
    context = assemble_context(ledger, user_input)

    # Stage 2  Generation (Pass 1)
    raw_response = _with_retry(lambda: client.generate(context, user_input))

    # Stage 3  Internal Audit (Pass 2)
    audit_prompt = AUDIT_USER_PROMPT_TEMPLATE.format(
        raw_response_text=raw_response,
        active_rules=json.dumps([r for r in ledger["rules"] if r.get("status") == "active"]),
        active_assumptions=json.dumps([a for a in ledger["assumptions"] if a.get("status") == "active"]),
        rubric_dimensions=json.dumps(ledger["rubric"]["dimensions"]),
    )
    audit_result = _with_retry(
        lambda: client.generate_structured(audit_prompt, AuditResult, system_instruction=AUDIT_SYSTEM_PROMPT)
    )
    audit_dict = audit_result.model_dump() if audit_result else {}

    # Stage 4  Ledger Update
    update_ledger(ledger, audit_dict, turn_num)

    turn_record = {
        "turn_id": f"turn_{turn_num}",
        "turn_number": turn_num,
        "timestamp": "",
        "user_prompt": user_input,
        "raw_response": raw_response,
        "audit_result": audit_dict,
        "grounding_result": {"status": "not_run", "claims": []},
        "internal_confidence_flag": None,
    }
    ledger["turn_history"].append(turn_record)

    return {
        "user_input": user_input,
        "raw_response": raw_response,
        "audit_result": audit_dict,
        "turn_count": ledger["total_turns"],
    }


# -- Test class ----------------------------------------------------------------

class TestISROAdSprintPlan:
    """E2E test: one-week sprint plan to create an AD on ISRO's achievements."""

    @pytest.fixture(autouse=True)
    def setup_ledger(self):
        self.ledger = init_empty_ledger()
        yield
        time.sleep(5)   # polite cooldown between API-heavy tests

    def test_isro_ad_sprint_plan(self):
        """
        Query: Write a one-week sprint plan for creating an AD on ISRO's achievements.
        Keywords only, keep it small.
        """
        query = (
            "write a one week sprint plan for creating a AD on ISRO's achievments. "
            "mention what all key aspects to research and what all technical team is required "
            "to shoot the ad, and steps to release the ad, who all has to approve the add. "
            "keep just keywords and keep it small"
        )

        print("\n" + "=" * 80)
        print("QUERY:")
        print(query)
        print("=" * 80)

        # -- Timing ----------------------------------------------------------
        t_start = time.perf_counter()
        result = run_turn(query, self.ledger)
        t_end = time.perf_counter()
        elapsed = t_end - t_start
        # --------------------------------------------------------------------

        # -- Raw Answer ------------------------------------------------------
        print("\n" + "-" * 80)
        print("RAW RESPONSE (Answer):")
        print("-" * 80)
        print(result["raw_response"])

        # -- Audit Result ----------------------------------------------------
        print("\n" + "-" * 80)
        print("AUDIT RESULT:")
        print("-" * 80)
        pprint.pprint(result["audit_result"])

        # -- Full Ledger ------------------------------------------------------
        print("\n" + "-" * 80)
        print("FULL LEDGER STATE:")
        print("-" * 80)
        pprint.pprint(self.ledger)

        # -- Timing Summary --------------------------------------------------
        print("\n" + "=" * 80)
        print(f"[TIME] TOTAL GENERATION TIME : {elapsed:.2f} seconds")
        print(f"       RULES GENERATED        : {len(self.ledger['rules'])}")
        print(f"       RUBRIC DIMENSIONS      : {len(self.ledger['rubric']['dimensions'])}")
        print(f"       ASSUMPTIONS CAPTURED   : {len(self.ledger['assumptions'])}")
        print(f"       MISSING INFO ITEMS     : {len(self.ledger['missing_info_registry'])}")
        print(f"       CONTRADICTIONS FLAGGED : {len(self.ledger['contradiction_log'])}")
        print("=" * 80)

        # -- Assertions ------------------------------------------------------
        assert result["turn_count"] == 1, "Should complete in a single turn"
        assert len(self.ledger["rubric"]["dimensions"]) > 0, \
            "Rubric dimensions must be generated"
        assert len(self.ledger["rules"]) > 0, \
            "Boundary rules must be generated"

        response_lower = result["raw_response"].lower()
        assert "isro" in response_lower, \
            "Response must mention ISRO"

        # Sprint plan should reference days or the concept of a week
        assert any(kw in response_lower for kw in ["day", "week", "sprint", "phase"]), \
            "Response should contain sprint/week/day/phase terminology"

        # Should mention at least one of: team, crew, director, producer, cinematographer
        assert any(kw in response_lower for kw in [
            "team", "director", "producer", "cinematographer",
            "editor", "crew", "camera", "script",
        ]), "Response should mention technical team roles"

        # Should mention approval or release steps
        assert any(kw in response_lower for kw in [
            "approv", "release", "publish", "broadcast", "review",
        ]), "Response should cover approval / release steps"

        # Elapsed time must be reasonable (generous 3-minute ceiling)
        assert elapsed < 180, f"Generation took too long: {elapsed:.2f}s"
        print(f"\n[PASS] All assertions passed in {elapsed:.2f}s")
