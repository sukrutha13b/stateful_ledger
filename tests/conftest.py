"""tests/conftest.py — Shared pytest fixtures for the entire test suite.

NOTE: Fixtures that require Phase 2+ modules (ledger.schema, ledger.manager) are
defined here but will only be importable once those modules are implemented.
Phase 1 tests (test_config.py) do not use any of these fixtures.
"""
import pytest


# ── Phase 2+ fixtures (imported lazily to avoid breaking Phase 1 tests) ──

@pytest.fixture
def empty_ledger():
    """Return a fresh, empty Ledger instance. Requires Phase 2."""
    from ledger.schema import Ledger  # noqa: F401 — deferred import
    from ledger.manager import init_ledger
    return init_ledger()


@pytest.fixture
def ledger_with_rules(empty_ledger):
    """Return a Ledger pre-populated with two rules. Requires Phase 2."""
    from ledger.schema import Rule
    empty_ledger.rules = [
        Rule(text="Rule A", source="user", created_at=0),
        Rule(text="Rule B", source="inferred", created_at=1, active=False),
    ]
    return empty_ledger


@pytest.fixture
def sample_claim():
    """Return a sample Claim. Requires Phase 2."""
    from ledger.schema import Claim
    return Claim(
        text="The sky is blue.",
        classification="grounded",
        tag="established",
        sources=["https://example.com"],
    )


@pytest.fixture
def sample_verified_response(sample_claim):
    """Return a sample VerifiedResponse. Requires Phase 2."""
    from ledger.schema import VerifiedResponse, Paragraph
    return VerifiedResponse(
        paragraphs=[
            Paragraph(index=0, text="The sky is blue.", claims=[sample_claim])
        ]
    )


@pytest.fixture
def sample_contradiction():
    """Return a sample ContradictionFlag. Requires Phase 2."""
    from ledger.schema import ContradictionFlag
    return ContradictionFlag(
        conflict_text="Claim A contradicts Rule X",
        conflicting_rule_id="rule-001",
        conflict_message="Direct logical contradiction detected.",
        severity="direct",
    )


@pytest.fixture
def mock_gemini_json_response() -> str:
    """A well-formed JSON string simulating a Gemini API response."""
    return """{
        "paragraphs": [
            {
                "index": 0,
                "text": "The model responded with a fact.",
                "step_type": "established_fact",
                "claims": [
                    {
                        "text": "The model responded with a fact.",
                        "classification": "grounded",
                        "tag": "established",
                        "sources": ["https://source.example.com"],
                        "perspectives": [],
                        "ledger_rules_used": [],
                        "overconfidence_flag": false
                    }
                ]
            }
        ]
    }"""
