"""Validation rules for gentle femdom templates: sensual dominance, tender surrender, romantic authority."""

from dataclasses import dataclass
from typing import Dict, Any, Callable, List, Optional


@dataclass
class ValidationRule:
    """A single validation rule that checks a condition in the data."""

    name: str
    description: str
    check_fn: Callable[[Dict[str, Any]], bool]
    error_message: Optional[str] = None

    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply this rule to the data and return the result."""
        passed = self.check_fn(data)
        result = {
            "rule_name": self.name,
            "passed": passed,
            "description": self.description,
        }
        if not passed and self.error_message:
            result["error"] = self.error_message
        return result


class RuleSet:
    """Base class for validation rule sets."""

    def __init__(self):
        """Initialize the rule set with rules."""
        self.rules: List[ValidationRule] = []

    def validate(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Validate data against all rules in this set."""
        results = {}
        for rule in self.rules:
            rule_result = rule.apply(data)
            rule_name = rule_result.pop("rule_name")
            results[rule_name] = rule_result
        return results


class SensualDominanceRuleSet(RuleSet):
    """Validation rules for Sensual Dominance emotional core."""

    def __init__(self):
        """Initialize SensualDominance validation rules."""
        super().__init__()
        self.rules = [
            ValidationRule(
                name="consent_enthusiastic",
                description="Dominance must be consensual and enthusiastic",
                check_fn=self._check_consent_enthusiastic,
                error_message="Consent must be clear, enthusiastic, and involve negotiation",
            ),
            ValidationRule(
                name="boundaries_explicit",
                description="Boundaries clearly stated and respected",
                check_fn=self._check_boundaries_explicit,
                error_message="Boundaries must be explicitly stated and respected",
            ),
            ValidationRule(
                name="playfulness_present",
                description="Tone is playful, not grim",
                check_fn=self._check_playfulness_present,
                error_message="The tone must be playful with humor and lightness, not grim",
            ),
            ValidationRule(
                name="care_central",
                description="Dominant's care for submissive evident",
                check_fn=self._check_care_central,
                error_message="Care must be central to the dominant's actions and attention",
            ),
        ]

    @staticmethod
    def _check_consent_enthusiastic(data: Dict[str, Any]) -> bool:
        """Check that consent is clear and enthusiastic."""
        return (
            data.get("consent_status") == "clear"
            and data.get("consent_tone") == "enthusiastic"
            and data.get("negotiation_happened") is True
        )

    @staticmethod
    def _check_boundaries_explicit(data: Dict[str, Any]) -> bool:
        """Check that boundaries are explicitly stated and respected."""
        return (
            data.get("boundaries_stated") is True
            and data.get("boundaries_respected") is True
            and data.get("hard_limits_defined") is True
            and data.get("soft_limits_defined") is True
        )

    @staticmethod
    def _check_playfulness_present(data: Dict[str, Any]) -> bool:
        """Check that tone is playful, not grim."""
        return (
            data.get("tone") == "playful"
            and data.get("humor_present") is True
            and data.get("grim_atmosphere") is False
            and data.get("lightness_evident") is True
        )

    @staticmethod
    def _check_care_central(data: Dict[str, Any]) -> bool:
        """Check that care is central to dominance."""
        return (
            data.get("care_shown") is True
            and data.get("attention_to_partner") is True
            and data.get("aftercare_present") is True
            and data.get("protective_instinct") is True
        )


class TenderSurrenderRuleSet(RuleSet):
    """Validation rules for Tender Surrender emotional core."""

    def __init__(self):
        """Initialize TenderSurrender validation rules."""
        super().__init__()
        self.rules = [
            ValidationRule(
                name="surrender_voluntary",
                description="Never coerced or manipulated",
                check_fn=self._check_surrender_voluntary,
                error_message="Surrender must be voluntary, free from coercion and manipulation",
            ),
            ValidationRule(
                name="vulnerability_honored",
                description="Vulnerability is valued",
                check_fn=self._check_vulnerability_honored,
                error_message="Vulnerability must be honored and valued, not exploited",
            ),
            ValidationRule(
                name="trust_earned",
                description="Dominant proves trustworthiness",
                check_fn=self._check_trust_earned,
                error_message="Trust must be earned through consistency, promises kept, and reliability",
            ),
            ValidationRule(
                name="growth_emotional",
                description="Emotional growth alongside surrender",
                check_fn=self._check_growth_emotional,
                error_message="There must be mutual emotional development and growth",
            ),
        ]

    @staticmethod
    def _check_surrender_voluntary(data: Dict[str, Any]) -> bool:
        """Check that surrender is voluntary and uncoerced."""
        return (
            data.get("coercion_present") is False
            and data.get("manipulation_present") is False
            and data.get("free_choice") is True
            and data.get("can_withdraw") is True
        )

    @staticmethod
    def _check_vulnerability_honored(data: Dict[str, Any]) -> bool:
        """Check that vulnerability is honored."""
        return (
            data.get("vulnerability_valued") is True
            and data.get("trust_reciprocated") is True
            and data.get("emotional_safety") is True
            and data.get("exposure_respected") is True
        )

    @staticmethod
    def _check_trust_earned(data: Dict[str, Any]) -> bool:
        """Check that trust is earned through demonstrated trustworthiness."""
        return (
            data.get("consistency_shown") is True
            and data.get("promises_kept") is True
            and data.get("reliability_demonstrated") is True
            and data.get("track_record") == "positive"
        )

    @staticmethod
    def _check_growth_emotional(data: Dict[str, Any]) -> bool:
        """Check that emotional growth is present."""
        return (
            data.get("emotional_development") is True
            and data.get("mutual_learning") is True
            and data.get("deepening_intimacy") is True
            and data.get("transformation_positive") is True
        )


class RomanticAuthorityRuleSet(RuleSet):
    """Validation rules for Romantic Authority emotional core."""

    def __init__(self):
        """Initialize RomanticAuthority validation rules."""
        super().__init__()
        self.rules = [
            ValidationRule(
                name="authority_rooted_in_care",
                description="Authority leadership serves both",
                check_fn=self._check_authority_rooted_in_care,
                error_message="Authority must be rooted in care that serves both partners",
            ),
            ValidationRule(
                name="partner_cherished",
                description="Partner genuinely valued",
                check_fn=self._check_partner_cherished,
                error_message="Partner must be genuinely valued and cherished",
            ),
            ValidationRule(
                name="respect_bidirectional",
                description="Respect flows both ways",
                check_fn=self._check_respect_bidirectional,
                error_message="Respect must flow bidirectionally with mutual dignity",
            ),
            ValidationRule(
                name="interdependence_balanced",
                description="Neither fully dependent",
                check_fn=self._check_interdependence_balanced,
                error_message="Interdependence must be balanced without unhealthy dependency",
            ),
        ]

    @staticmethod
    def _check_authority_rooted_in_care(data: Dict[str, Any]) -> bool:
        """Check that authority is rooted in care."""
        return (
            data.get("leadership_serves_both") is True
            and data.get("care_motivates_decisions") is True
            and data.get("benevolent_authority") is True
            and data.get("mutual_benefit") is True
        )

    @staticmethod
    def _check_partner_cherished(data: Dict[str, Any]) -> bool:
        """Check that partner is genuinely cherished."""
        return (
            data.get("partner_genuinely_valued") is True
            and data.get("appreciation_shown") is True
            and data.get("investment_evident") is True
            and data.get("priority_high") is True
        )

    @staticmethod
    def _check_respect_bidirectional(data: Dict[str, Any]) -> bool:
        """Check that respect is bidirectional."""
        return (
            data.get("dominant_respects_submissive") is True
            and data.get("submissive_respects_dominant") is True
            and data.get("mutual_dignity") is True
            and data.get("equal_humanity") is True
        )

    @staticmethod
    def _check_interdependence_balanced(data: Dict[str, Any]) -> bool:
        """Check that interdependence is balanced."""
        return (
            data.get("neither_fully_dependent") is True
            and data.get("autonomy_preserved") is True
            and data.get("interdependence_healthy") is True
            and data.get("power_not_absolute") is True
        )
