"""Tests for semantic coherence validation in gentle femdom identities.

These tests verify that generated identities match their template's emotional core,
catching silent semantic failures where structure is valid but meaning is wrong.
"""

import pytest
from auteur.gentlefemdom.semantic_validation import SemanticCoherenceRule
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.gentlefemdom.core_templates import get_template


class TestSemanticCoherenceRule:
    """Test suite for SemanticCoherenceRule."""

    def test_semantic_rule_accepts_matching_emotion(self):
        """Semantic rule accepts identity with emotion matching template's primary."""
        # Generate identity for sensual_dominance with valid choices
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident",
            },
        }

        identity = IdentityGenerator.from_choices("sensual_dominance", choices)
        template = get_template("sensual_dominance")

        rule = SemanticCoherenceRule()
        result = rule.validate(identity, template)

        assert result["passed"] is True

    def test_semantic_rule_rejects_mismatched_emotion(self):
        """Semantic rule rejects identity with emotion mismatched from template's primary."""
        # Generate valid identity
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident",
            },
        }

        identity = IdentityGenerator.from_choices("sensual_dominance", choices)

        # Manually corrupt the emotion to simulate a semantic failure
        identity.target_experience.primary = "dread"

        template = get_template("sensual_dominance")
        rule = SemanticCoherenceRule()
        result = rule.validate(identity, template)

        assert result["passed"] is False
        assert "emotion" in result.get("error", "").lower()

    def test_semantic_rule_explains_mismatch(self):
        """Error message clearly explains the mismatch with expected and actual emotions."""
        # Generate valid identity for tender_surrender
        choices = {
            4: {
                "want": "want-release-control",
                "resistance": "resistance-fear-vulnerability",
                "conflict": "conflict-self-protection-vs-desire",
                "stakes": "stakes-emotional-walls",
                "change": "change-defended-to-open",
            },
        }

        identity = IdentityGenerator.from_choices("tender_surrender", choices)

        # Corrupt emotion to trigger error
        identity.target_experience.primary = "dread"

        template = get_template("tender_surrender")
        rule = SemanticCoherenceRule()
        result = rule.validate(identity, template)

        assert result["passed"] is False
        error = result.get("error", "")
        assert "safe_vulnerability" in error  # Expected emotion for tender_surrender
        assert "dread" in error  # Actual (corrupted) emotion

    def test_semantic_rule_allows_author_override(self):
        """Author override bypasses semantic coherence check."""
        # Generate valid identity with mismatched emotion
        choices = {
            4: {
                "want": "want-establish-trust",
                "resistance": "resistance-partner-doubt",
                "conflict": "conflict-control-vs-consent",
                "stakes": "stakes-emotional-intimacy",
                "change": "change-tentative-to-confident",
            },
        }

        identity = IdentityGenerator.from_choices("sensual_dominance", choices)

        # Corrupt emotion
        identity.target_experience.primary = "dread"

        # Add author override
        identity.author_overrides = {"emotional_arc": True}

        template = get_template("sensual_dominance")
        rule = SemanticCoherenceRule()
        result = rule.validate(identity, template)

        # Despite mismatch, override allows it to pass
        assert result["passed"] is True
        assert result.get("reason") == "author_override"

    def test_all_three_cores_pass_semantic_validation(self):
        """All three gentle femdom cores produce semantically valid identities."""
        # Test sensual_dominance
        sensual_choices = {
            4: {
                "want": "want-explore-together",
                "resistance": "resistance-trust-gap",
                "conflict": "conflict-power-vs-care",
                "stakes": "stakes-vulnerability-safety",
                "change": "change-stranger-to-intimate",
            },
        }
        sensual_identity = IdentityGenerator.from_choices("sensual_dominance", sensual_choices)
        sensual_template = get_template("sensual_dominance")

        # Test tender_surrender
        tender_choices = {
            4: {
                "want": "want-experience-pleasure",
                "resistance": "resistance-doubt-worthiness",
                "conflict": "conflict-control-vs-release",
                "stakes": "stakes-identity-preservation",
                "change": "change-doubtful-to-trusting",
            },
        }
        tender_identity = IdentityGenerator.from_choices("tender_surrender", tender_choices)
        tender_template = get_template("tender_surrender")

        # Test romantic_authority
        romantic_choices = {
            4: {
                "want": "want-provide-protect",
                "resistance": "resistance-partner-independence",
                "conflict": "conflict-leadership-vs-partnership",
                "stakes": "stakes-relationship-balance",
                "change": "change-uncertain-to-confident",
            },
        }
        romantic_identity = IdentityGenerator.from_choices("romantic_authority", romantic_choices)
        romantic_template = get_template("romantic_authority")

        # Validate all three cores
        rule = SemanticCoherenceRule()

        sensual_result = rule.validate(sensual_identity, sensual_template)
        assert sensual_result["passed"] is True

        tender_result = rule.validate(tender_identity, tender_template)
        assert tender_result["passed"] is True

        romantic_result = rule.validate(romantic_identity, romantic_template)
        assert romantic_result["passed"] is True
