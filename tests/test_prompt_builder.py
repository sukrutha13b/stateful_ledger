"""tests/test_prompt_builder.py - Unit tests for engine/prompt_builder.py (Phase 4)."""
import json

import pytest

from engine.prompt_builder import (
    build_rubric_prompt,
    build_main_prompt,
    build_contradiction_prompt,
    build_classification_prompt,
    MAIN_RESPONSE_SCHEMA,
)


# ------------------------------------------------------
# Rubric Prompt (Call #1a)
# ------------------------------------------------------

class TestBuildRubricPrompt:
    """build_rubric_prompt produces valid system + user prompts."""

    def test_contains_all_goal_types(self):
        system, _ = build_rubric_prompt("Tell me about quantum computing")
        for goal in ["analytical", "creative", "technical", "exploratory"]:
            assert goal in system

    def test_includes_user_input(self):
        _, user = build_rubric_prompt("Explain photosynthesis")
        assert "Explain photosynthesis" in user

    def test_returns_tuple_of_two_strings(self):
        result = build_rubric_prompt("Hello")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(s, str) for s in result)

    def test_system_requests_json(self):
        system, _ = build_rubric_prompt("test")
        assert "JSON" in system
        assert "goal_type" in system
        assert "rubric_criteria" in system


# ------------------------------------------------------
# Main Prompt (Call #1b)
# ------------------------------------------------------

class TestBuildMainPrompt:
    """build_main_prompt injects ledger state correctly."""

    @pytest.fixture
    def snapshot_with_rules(self):
        return {
            "rules": [
                {"text": "Always cite sources", "active": True},
                {"text": "Inactive rule", "active": False},
            ],
            "assumptions": [{"text": "User prefers formal tone"}],
            "goal_type": "analytical",
            "rubric": {"criteria": ["Accuracy", "Depth"]},
        }

    def test_injects_active_rules(self, snapshot_with_rules):
        system, _ = build_main_prompt("query", snapshot_with_rules)
        assert "Always cite sources" in system
        # Inactive rule should be filtered out
        assert "Inactive rule" not in system

    def test_injects_assumptions(self, snapshot_with_rules):
        system, _ = build_main_prompt("query", snapshot_with_rules)
        assert "User prefers formal tone" in system

    def test_injects_rubric_criteria(self, snapshot_with_rules):
        system, _ = build_main_prompt("query", snapshot_with_rules)
        assert "Accuracy" in system
        assert "Depth" in system

    def test_injects_goal_type(self, snapshot_with_rules):
        system, _ = build_main_prompt("query", snapshot_with_rules)
        assert "analytical" in system

    def test_includes_schema(self):
        system, _ = build_main_prompt("query", {})
        assert "paragraphs" in system
        assert "claims" in system
        assert "step_type" in system

    def test_user_prompt_is_raw_input(self):
        _, user = build_main_prompt("What is gravity?", {})
        assert user == "What is gravity?"

    def test_empty_ledger_snapshot(self):
        """Empty snapshot should still produce valid prompts."""
        system, user = build_main_prompt("Hello", {})
        assert "Rules:" in system
        assert "exploratory" in system  # default goal type
        assert user == "Hello"


# ------------------------------------------------------
# Contradiction Prompt (Call #2)
# ------------------------------------------------------

class TestBuildContradictionPrompt:
    """build_contradiction_prompt embeds rules and response."""

    @pytest.fixture
    def sample_rules(self):
        return [
            {"id": "r1", "text": "Always be concise", "active": True},
            {"id": "r2", "text": "Skip this one", "active": False},
        ]

    def test_includes_active_rules(self, sample_rules):
        _, user = build_contradiction_prompt(sample_rules, "input", "response")
        assert "Always be concise" in user
        assert "Skip this one" not in user

    def test_includes_response_text(self, sample_rules):
        _, user = build_contradiction_prompt(sample_rules, "input", "The sky is green.")
        assert "The sky is green." in user

    def test_includes_user_input(self, sample_rules):
        _, user = build_contradiction_prompt(sample_rules, "My question here", "response")
        assert "My question here" in user

    def test_system_requests_violations_json(self, sample_rules):
        system, _ = build_contradiction_prompt(sample_rules, "i", "r")
        assert "violations" in system
        assert "rule_id" in system
        assert "severity" in system


# ------------------------------------------------------
# Classification Prompt (Call #3)
# ------------------------------------------------------

class TestBuildClassificationPrompt:
    """build_classification_prompt numbers claims with IDs."""

    @pytest.fixture
    def sample_claims(self):
        return [
            {"claim_id": "c1", "text": "Water boils at 100C"},
            {"claim_id": "c2", "text": "The moon is made of cheese"},
        ]

    def test_numbers_claims(self, sample_claims):
        _, user = build_classification_prompt(sample_claims)
        assert "1. [ID: c1]" in user
        assert "2. [ID: c2]" in user

    def test_includes_claim_text(self, sample_claims):
        _, user = build_classification_prompt(sample_claims)
        assert "Water boils at 100C" in user
        assert "The moon is made of cheese" in user

    def test_empty_claims_produces_valid_prompt(self):
        system, user = build_classification_prompt([])
        assert "Classify these claims" in user
        assert "classified_claims" in system

    def test_system_requests_classification_json(self, sample_claims):
        system, _ = build_classification_prompt(sample_claims)
        assert "grounded" in system
        assert "contested" in system
        assert "unverified" in system
        assert "perspectives" in system
        assert "sources" in system
