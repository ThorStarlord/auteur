"""Tests for gentle femdom validation rules."""

import pytest
from auteur.gentlefemdom.validation import (
    ValidationRule,
    RuleSet,
    SensualDominanceRuleSet,
    TenderSurrenderRuleSet,
    RomanticAuthorityRuleSet,
)


class TestValidationRule:
    """Tests for ValidationRule base class."""

    def test_validation_rule_instantiation(self):
        """Test that ValidationRule can be instantiated."""
        rule = ValidationRule(
            name="test_rule",
            description="A test rule",
            check_fn=lambda x: True,
        )
        assert rule.name == "test_rule"
        assert rule.description == "A test rule"

    def test_validation_rule_apply_passing(self):
        """Test applying a passing validation rule."""
        rule = ValidationRule(
            name="always_pass",
            description="Always passes",
            check_fn=lambda x: True,
        )
        result = rule.apply({"test": "data"})
        assert result["passed"] is True
        assert result["rule_name"] == "always_pass"

    def test_validation_rule_apply_failing(self):
        """Test applying a failing validation rule."""
        rule = ValidationRule(
            name="always_fail",
            description="Always fails",
            check_fn=lambda x: False,
            error_message="This always fails",
        )
        result = rule.apply({"test": "data"})
        assert result["passed"] is False
        assert result["error"] == "This always fails"


class TestSensualDominanceRuleSet:
    """Tests for SensualDominance validation rules."""

    def test_consent_enthusiastic_rule_exists(self):
        """Test that consent_enthusiastic rule exists."""
        ruleset = SensualDominanceRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "consent_enthusiastic" in rule_names

    def test_consent_enthusiastic_passes_with_valid_consent(self):
        """Test consent_enthusiastic passes when consent is clear and enthusiastic."""
        ruleset = SensualDominanceRuleSet()
        data = {
            "consent_status": "clear",
            "consent_tone": "enthusiastic",
            "negotiation_happened": True,
        }
        result = ruleset.validate(data)
        assert result["consent_enthusiastic"]["passed"] is True

    def test_consent_enthusiastic_fails_without_consent(self):
        """Test consent_enthusiastic fails without clear consent."""
        ruleset = SensualDominanceRuleSet()
        data = {
            "consent_status": "unclear",
            "consent_tone": "hesitant",
            "negotiation_happened": False,
        }
        result = ruleset.validate(data)
        assert result["consent_enthusiastic"]["passed"] is False

    def test_boundaries_explicit_rule_exists(self):
        """Test that boundaries_explicit rule exists."""
        ruleset = SensualDominanceRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "boundaries_explicit" in rule_names

    def test_boundaries_explicit_passes_with_stated_boundaries(self):
        """Test boundaries_explicit passes when boundaries are clearly stated."""
        ruleset = SensualDominanceRuleSet()
        data = {
            "boundaries_stated": True,
            "boundaries_respected": True,
            "hard_limits_defined": True,
            "soft_limits_defined": True,
        }
        result = ruleset.validate(data)
        assert result["boundaries_explicit"]["passed"] is True

    def test_boundaries_explicit_fails_without_boundaries(self):
        """Test boundaries_explicit fails when boundaries not stated."""
        ruleset = SensualDominanceRuleSet()
        data = {
            "boundaries_stated": False,
            "boundaries_respected": False,
            "hard_limits_defined": False,
            "soft_limits_defined": False,
        }
        result = ruleset.validate(data)
        assert result["boundaries_explicit"]["passed"] is False

    def test_playfulness_present_rule_exists(self):
        """Test that playfulness_present rule exists."""
        ruleset = SensualDominanceRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "playfulness_present" in rule_names

    def test_playfulness_present_passes_with_playful_tone(self):
        """Test playfulness_present passes with playful tone."""
        ruleset = SensualDominanceRuleSet()
        data = {
            "tone": "playful",
            "humor_present": True,
            "grim_atmosphere": False,
            "lightness_evident": True,
        }
        result = ruleset.validate(data)
        assert result["playfulness_present"]["passed"] is True

    def test_playfulness_present_fails_with_grim_tone(self):
        """Test playfulness_present fails with grim tone."""
        ruleset = SensualDominanceRuleSet()
        data = {
            "tone": "grim",
            "humor_present": False,
            "grim_atmosphere": True,
            "lightness_evident": False,
        }
        result = ruleset.validate(data)
        assert result["playfulness_present"]["passed"] is False

    def test_care_central_rule_exists(self):
        """Test that care_central rule exists."""
        ruleset = SensualDominanceRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "care_central" in rule_names

    def test_care_central_passes_when_care_evident(self):
        """Test care_central passes when dominant shows care."""
        ruleset = SensualDominanceRuleSet()
        data = {
            "care_shown": True,
            "attention_to_partner": True,
            "aftercare_present": True,
            "protective_instinct": True,
        }
        result = ruleset.validate(data)
        assert result["care_central"]["passed"] is True

    def test_care_central_fails_without_care(self):
        """Test care_central fails when care not evident."""
        ruleset = SensualDominanceRuleSet()
        data = {
            "care_shown": False,
            "attention_to_partner": False,
            "aftercare_present": False,
            "protective_instinct": False,
        }
        result = ruleset.validate(data)
        assert result["care_central"]["passed"] is False


class TestTenderSurrenderRuleSet:
    """Tests for TenderSurrender validation rules."""

    def test_surrender_voluntary_rule_exists(self):
        """Test that surrender_voluntary rule exists."""
        ruleset = TenderSurrenderRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "surrender_voluntary" in rule_names

    def test_surrender_voluntary_passes_when_uncoerced(self):
        """Test surrender_voluntary passes when surrender is voluntary."""
        ruleset = TenderSurrenderRuleSet()
        data = {
            "coercion_present": False,
            "manipulation_present": False,
            "free_choice": True,
            "can_withdraw": True,
        }
        result = ruleset.validate(data)
        assert result["surrender_voluntary"]["passed"] is True

    def test_surrender_voluntary_fails_when_coerced(self):
        """Test surrender_voluntary fails when coercion or manipulation present."""
        ruleset = TenderSurrenderRuleSet()
        data = {
            "coercion_present": True,
            "manipulation_present": True,
            "free_choice": False,
            "can_withdraw": False,
        }
        result = ruleset.validate(data)
        assert result["surrender_voluntary"]["passed"] is False

    def test_vulnerability_honored_rule_exists(self):
        """Test that vulnerability_honored rule exists."""
        ruleset = TenderSurrenderRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "vulnerability_honored" in rule_names

    def test_vulnerability_honored_passes_when_valued(self):
        """Test vulnerability_honored passes when vulnerability is valued."""
        ruleset = TenderSurrenderRuleSet()
        data = {
            "vulnerability_valued": True,
            "trust_reciprocated": True,
            "emotional_safety": True,
            "exposure_respected": True,
        }
        result = ruleset.validate(data)
        assert result["vulnerability_honored"]["passed"] is True

    def test_vulnerability_honored_fails_when_exploited(self):
        """Test vulnerability_honored fails when vulnerability is exploited."""
        ruleset = TenderSurrenderRuleSet()
        data = {
            "vulnerability_valued": False,
            "trust_reciprocated": False,
            "emotional_safety": False,
            "exposure_respected": False,
        }
        result = ruleset.validate(data)
        assert result["vulnerability_honored"]["passed"] is False

    def test_trust_earned_rule_exists(self):
        """Test that trust_earned rule exists."""
        ruleset = TenderSurrenderRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "trust_earned" in rule_names

    def test_trust_earned_passes_when_trustworthy(self):
        """Test trust_earned passes when dominant proves trustworthiness."""
        ruleset = TenderSurrenderRuleSet()
        data = {
            "consistency_shown": True,
            "promises_kept": True,
            "reliability_demonstrated": True,
            "track_record": "positive",
        }
        result = ruleset.validate(data)
        assert result["trust_earned"]["passed"] is True

    def test_trust_earned_fails_when_untrustworthy(self):
        """Test trust_earned fails when dominant doesn't prove trustworthiness."""
        ruleset = TenderSurrenderRuleSet()
        data = {
            "consistency_shown": False,
            "promises_kept": False,
            "reliability_demonstrated": False,
            "track_record": "negative",
        }
        result = ruleset.validate(data)
        assert result["trust_earned"]["passed"] is False

    def test_growth_emotional_rule_exists(self):
        """Test that growth_emotional rule exists."""
        ruleset = TenderSurrenderRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "growth_emotional" in rule_names

    def test_growth_emotional_passes_with_mutual_growth(self):
        """Test growth_emotional passes with emotional growth."""
        ruleset = TenderSurrenderRuleSet()
        data = {
            "emotional_development": True,
            "mutual_learning": True,
            "deepening_intimacy": True,
            "transformation_positive": True,
        }
        result = ruleset.validate(data)
        assert result["growth_emotional"]["passed"] is True

    def test_growth_emotional_fails_without_growth(self):
        """Test growth_emotional fails without emotional growth."""
        ruleset = TenderSurrenderRuleSet()
        data = {
            "emotional_development": False,
            "mutual_learning": False,
            "deepening_intimacy": False,
            "transformation_positive": False,
        }
        result = ruleset.validate(data)
        assert result["growth_emotional"]["passed"] is False


class TestRomanticAuthorityRuleSet:
    """Tests for RomanticAuthority validation rules."""

    def test_authority_rooted_in_care_rule_exists(self):
        """Test that authority_rooted_in_care rule exists."""
        ruleset = RomanticAuthorityRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "authority_rooted_in_care" in rule_names

    def test_authority_rooted_in_care_passes_when_care_based(self):
        """Test authority_rooted_in_care passes when leadership serves both."""
        ruleset = RomanticAuthorityRuleSet()
        data = {
            "leadership_serves_both": True,
            "care_motivates_decisions": True,
            "benevolent_authority": True,
            "mutual_benefit": True,
        }
        result = ruleset.validate(data)
        assert result["authority_rooted_in_care"]["passed"] is True

    def test_authority_rooted_in_care_fails_when_selfish(self):
        """Test authority_rooted_in_care fails when leadership is selfish."""
        ruleset = RomanticAuthorityRuleSet()
        data = {
            "leadership_serves_both": False,
            "care_motivates_decisions": False,
            "benevolent_authority": False,
            "mutual_benefit": False,
        }
        result = ruleset.validate(data)
        assert result["authority_rooted_in_care"]["passed"] is False

    def test_partner_cherished_rule_exists(self):
        """Test that partner_cherished rule exists."""
        ruleset = RomanticAuthorityRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "partner_cherished" in rule_names

    def test_partner_cherished_passes_when_valued(self):
        """Test partner_cherished passes when partner is genuinely valued."""
        ruleset = RomanticAuthorityRuleSet()
        data = {
            "partner_genuinely_valued": True,
            "appreciation_shown": True,
            "investment_evident": True,
            "priority_high": True,
        }
        result = ruleset.validate(data)
        assert result["partner_cherished"]["passed"] is True

    def test_partner_cherished_fails_when_not_valued(self):
        """Test partner_cherished fails when partner not valued."""
        ruleset = RomanticAuthorityRuleSet()
        data = {
            "partner_genuinely_valued": False,
            "appreciation_shown": False,
            "investment_evident": False,
            "priority_high": False,
        }
        result = ruleset.validate(data)
        assert result["partner_cherished"]["passed"] is False

    def test_respect_bidirectional_rule_exists(self):
        """Test that respect_bidirectional rule exists."""
        ruleset = RomanticAuthorityRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "respect_bidirectional" in rule_names

    def test_respect_bidirectional_passes_when_mutual(self):
        """Test respect_bidirectional passes when respect flows both ways."""
        ruleset = RomanticAuthorityRuleSet()
        data = {
            "dominant_respects_submissive": True,
            "submissive_respects_dominant": True,
            "mutual_dignity": True,
            "equal_humanity": True,
        }
        result = ruleset.validate(data)
        assert result["respect_bidirectional"]["passed"] is True

    def test_respect_bidirectional_fails_when_one_sided(self):
        """Test respect_bidirectional fails when respect is one-sided."""
        ruleset = RomanticAuthorityRuleSet()
        data = {
            "dominant_respects_submissive": False,
            "submissive_respects_dominant": False,
            "mutual_dignity": False,
            "equal_humanity": False,
        }
        result = ruleset.validate(data)
        assert result["respect_bidirectional"]["passed"] is False

    def test_interdependence_balanced_rule_exists(self):
        """Test that interdependence_balanced rule exists."""
        ruleset = RomanticAuthorityRuleSet()
        rule_names = [r.name for r in ruleset.rules]
        assert "interdependence_balanced" in rule_names

    def test_interdependence_balanced_passes_with_balance(self):
        """Test interdependence_balanced passes with healthy balance."""
        ruleset = RomanticAuthorityRuleSet()
        data = {
            "neither_fully_dependent": True,
            "autonomy_preserved": True,
            "interdependence_healthy": True,
            "power_not_absolute": True,
        }
        result = ruleset.validate(data)
        assert result["interdependence_balanced"]["passed"] is True

    def test_interdependence_balanced_fails_with_dependency(self):
        """Test interdependence_balanced fails with unhealthy dependency."""
        ruleset = RomanticAuthorityRuleSet()
        data = {
            "neither_fully_dependent": False,
            "autonomy_preserved": False,
            "interdependence_healthy": False,
            "power_not_absolute": False,
        }
        result = ruleset.validate(data)
        assert result["interdependence_balanced"]["passed"] is False


class TestRuleSetIntegration:
    """Tests for RuleSet integration and validation flow."""

    def test_ruleset_validate_returns_dict(self):
        """Test that validate returns a dict with all rule results."""
        ruleset = SensualDominanceRuleSet()
        data = {
            "consent_status": "clear",
            "consent_tone": "enthusiastic",
            "negotiation_happened": True,
            "boundaries_stated": True,
            "boundaries_respected": True,
            "hard_limits_defined": True,
            "soft_limits_defined": True,
            "tone": "playful",
            "humor_present": True,
            "grim_atmosphere": False,
            "lightness_evident": True,
            "care_shown": True,
            "attention_to_partner": True,
            "aftercare_present": True,
            "protective_instinct": True,
        }
        result = ruleset.validate(data)
        assert isinstance(result, dict)
        assert len(result) == 4  # 4 rules in SensualDominance

    def test_ruleset_all_rules_required(self):
        """Test that all rules in a RuleSet are required."""
        ruleset = TenderSurrenderRuleSet()
        # All rules should be in the result
        data = {
            "coercion_present": False,
            "manipulation_present": False,
            "free_choice": True,
            "can_withdraw": True,
            "vulnerability_valued": True,
            "trust_reciprocated": True,
            "emotional_safety": True,
            "exposure_respected": True,
            "consistency_shown": True,
            "promises_kept": True,
            "reliability_demonstrated": True,
            "track_record": "positive",
            "emotional_development": True,
            "mutual_learning": True,
            "deepening_intimacy": True,
            "transformation_positive": True,
        }
        result = ruleset.validate(data)
        expected_rules = ["surrender_voluntary", "vulnerability_honored", "trust_earned", "growth_emotional"]
        for rule_name in expected_rules:
            assert rule_name in result
