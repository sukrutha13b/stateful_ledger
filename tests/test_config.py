"""tests/test_config.py - Phase 1: Verify all config constants are valid."""
import pytest
import config


class TestConfigConstantsDefined:
    """Assert all constants are non-None and have correct types."""

    def test_gemini_api_key_is_str(self):
        assert isinstance(config.GEMINI_API_KEY, str)

    def test_model_name_is_str(self):
        assert isinstance(config.MODEL_NAME, str)
        assert len(config.MODEL_NAME) > 0

    def test_max_output_tokens_is_positive_int(self):
        assert isinstance(config.MAX_OUTPUT_TOKENS, int)
        assert config.MAX_OUTPUT_TOKENS > 0

    def test_max_history_turns_is_positive_int(self):
        assert isinstance(config.MAX_HISTORY_TURNS_IN_PROMPT, int)
        assert config.MAX_HISTORY_TURNS_IN_PROMPT > 0


class TestGoalTypes:
    """Assert expected goal types are present."""

    def test_goal_types_is_list(self):
        assert isinstance(config.GOAL_TYPES, list)

    def test_goal_types_non_empty(self):
        assert len(config.GOAL_TYPES) > 0

    def test_expected_goal_types_present(self):
        expected = {"analytical", "creative", "technical", "exploratory"}
        assert expected.issubset(set(config.GOAL_TYPES))

    def test_goal_types_are_strings(self):
        for g in config.GOAL_TYPES:
            assert isinstance(g, str)


class TestTrustWeights:
    """Assert trust weight values are within [0.0, 1.0]."""

    def test_trust_weights_is_dict(self):
        assert isinstance(config.TRUST_WEIGHTS, dict)

    def test_trust_weights_keys_present(self):
        assert "accurate" in config.TRUST_WEIGHTS
        assert "uncertain" in config.TRUST_WEIGHTS
        assert "inaccurate" in config.TRUST_WEIGHTS

    def test_trust_weights_in_range(self):
        for key, value in config.TRUST_WEIGHTS.items():
            assert 0.0 <= value <= 1.0, f"Weight for '{key}' out of range: {value}"

    def test_trust_weights_accurate_is_highest(self):
        """'accurate' should have the highest weight (1.0)."""
        assert config.TRUST_WEIGHTS["accurate"] == 1.0

    def test_trust_weights_inaccurate_is_zero(self):
        assert config.TRUST_WEIGHTS["inaccurate"] == 0.0


class TestClaimClassifications:
    """Assert claim classification constants are correct."""

    def test_claim_classifications_is_list(self):
        assert isinstance(config.CLAIM_CLASSIFICATIONS, list)

    def test_expected_classifications_present(self):
        expected = {"grounded", "contested", "unverified"}
        assert expected == set(config.CLAIM_CLASSIFICATIONS)


class TestStepTypes:
    """Assert step type and claim tag constants are correct."""

    def test_step_types_is_list(self):
        assert isinstance(config.STEP_TYPES, list)

    def test_expected_step_types_present(self):
        expected = {"inference", "assumption", "established_fact"}
        assert expected == set(config.STEP_TYPES)

    def test_claim_tags_is_list(self):
        assert isinstance(config.CLAIM_TAGS, list)

    def test_expected_claim_tags_present(self):
        expected = {"established", "reasoned", "inferred"}
        assert expected == set(config.CLAIM_TAGS)
