"""Deterministic validation rules for mystery story structure."""

from typing import Tuple, List, Dict, Any
from auteur.mystery.core_templates import (
    HowdunitTemplate, ParanoiaTemplate, CozyTemplate
)


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class ValidationRule:
    """A single validation rule."""

    def __init__(self, rule_id: str, name: str, check_fn, error_msg: str):
        self.rule_id = rule_id
        self.name = name
        self.check_fn = check_fn  # Function that returns (passes: bool, message: str)
        self.error_msg = error_msg

    def check(self, template, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, str]:
        """Run this rule. Returns (passes, message)."""
        return self.check_fn(template, choices)


class RuleSet:
    """A collection of validation rules for a template."""

    def __init__(self, core_id: str):
        self.core_id = core_id
        self.rules: List[ValidationRule] = []
        self._build_rules()

    def _build_rules(self):
        """Build rule set based on core type."""
        if self.core_id == "howdunit":
            self._build_howdunit_rules()
        elif self.core_id == "paranoia":
            self._build_paranoia_rules()
        elif self.core_id == "cozy":
            self._build_cozy_rules()

    def _build_howdunit_rules(self):
        """Howdunit-specific validation rules."""

        # Rule 1: Want ≠ Change
        def check_want_not_equal_change(template, choices):
            """Ensure Want and Change differ (prevents static character arc)."""
            layer4 = choices.get(4, {})
            want = layer4.get("want")
            change = layer4.get("change")
            if want and change and want == change:
                return False, "Want and Change cannot be the same (no dramatic arc)"
            return True, ""

        self.rules.append(ValidationRule(
            "howdunit.core.want_not_equal_change",
            "Want must differ from Change",
            check_want_not_equal_change,
            "Want and Change cannot be identical in a dramatic arc"
        ))

        # Rule 2: Solution must be derivable
        def check_solution_derivable(template, choices):
            """Verify solution is fair and theoretically derivable by reader."""
            layer7 = choices.get(7, {})
            clue_dist = layer7.get("clue_distribution")
            layer8 = choices.get(8, {})
            solution_density = layer8.get("solution_density")

            # Tight solution requires good clue distribution
            if solution_density == "tight" and clue_dist == "late-heavy":
                return False, "Tight solutions require better clue distribution (not all clues come late)"
            return True, ""

        self.rules.append(ValidationRule(
            "howdunit.structure.solution_derivable",
            "Solution must be theoretically derivable",
            check_solution_derivable,
            "Howdunit solutions must be fair (reader can theoretically solve)"
        ))

        # Rule 3: Red herring coherence check
        def check_red_herring_coherence(template, choices):
            """Ensure red herrings are coherent with central solution and genre."""
            layer2 = choices.get(2, {})
            genre = layer2.get("genre_contract")
            layer7 = choices.get(7, {})
            clues = layer7.get("clue_distribution")

            # For puzzle-box, clues must be tightly distributed
            if genre == "puzzle-box" and clues == "late-heavy":
                return False, "Puzzle-box mysteries need earlier clue introduction"
            return True, ""

        self.rules.append(ValidationRule(
            "howdunit.structure.red_herring_coherence",
            "Red herrings must not contradict solution",
            check_red_herring_coherence,
            "Red herrings must be coherent with central solution"
        ))

    def _build_paranoia_rules(self):
        """Paranoia-specific validation rules."""

        # Rule 1: Want ≠ Change
        def check_want_not_equal_change(template, choices):
            """Ensure Want and Change differ (prevents static character arc)."""
            layer4 = choices.get(4, {})
            want = layer4.get("want")
            change = layer4.get("change")
            if want and change and want == change:
                return False, "Want and Change cannot be the same"
            return True, ""

        self.rules.append(ValidationRule(
            "paranoia.core.want_not_equal_change",
            "Want must differ from Change",
            check_want_not_equal_change,
            "Want and Change cannot be identical"
        ))

        # Rule 2: Narrator unreliability must be intentional
        def check_narrator_intentional(template, choices):
            """Verify unreliable narrator serves narrative purpose and is coherent."""
            layer5 = choices.get(5, {})
            reliability = layer5.get("narrator_reliability")
            layer8 = choices.get(8, {})
            truth_ambiguity = layer8.get("truth_ambiguity")

            # If narrator is unreliable AND truth_ambiguity is specified, they must be coherent
            if reliability in ["highly-unreliable", "moderately-unreliable"] and truth_ambiguity:
                # Fully revealed truth contradicts unreliable narrator
                if truth_ambiguity == "fully-revealed":
                    return False, "Unreliable narrator cannot have fully revealed truth"
            return True, ""

        self.rules.append(ValidationRule(
            "paranoia.structure.narrator_intentional",
            "Unreliable narrator must serve narrative purpose",
            check_narrator_intentional,
            "Narrator unreliability must be deliberate, not accidental"
        ))

        # Rule 3: Paranoia escalates logically
        def check_paranoia_escalates(template, choices):
            """Verify dread escalation matches gaslighting intensity."""
            layer6 = choices.get(6, {})
            gaslight = layer6.get("gaslighting_intensity")
            layer7 = choices.get(7, {})
            escalation = layer7.get("paranoia_escalation")

            # Intense gaslighting should pair with appropriate escalation
            if gaslight == "institutional" and escalation == "slow-build":
                return False, "Institutional gaslighting typically escalates rapidly, not slowly"
            return True, ""

        self.rules.append(ValidationRule(
            "paranoia.structure.paranoia_escalates",
            "Paranoia must escalate logically",
            check_paranoia_escalates,
            "Dread escalation must match narrative tension"
        ))

    def _build_cozy_rules(self):
        """Cozy-specific validation rules."""

        # Rule 1: Violence budget respected
        def check_violence_budget(template, choices):
            """Ensure violence stays within cozy constraints (none, off-page, minimal)."""
            layer7 = choices.get(7, {})
            violence = layer7.get("violence_budget")

            # Cozy should not have violence
            if violence and violence not in ["none", "off-page", "minimal"]:
                return False, f"Cozy mysteries should minimize violence, got: {violence}"
            return True, ""

        self.rules.append(ValidationRule(
            "cozy.tone.violence_budget",
            "Violence must stay within cozy constraints",
            check_violence_budget,
            "Cozy mysteries require off-page or minimal violence"
        ))

        # Rule 2: Tone consistency
        def check_tone_consistency(template, choices):
            """Verify tone remains warm, safe, and coherent throughout story."""
            layer5 = choices.get(5, {})
            humor = layer5.get("humor_level")
            layer9 = choices.get(9, {})
            warmth = layer9.get("warmth_confidence")

            # Dark humor should pair with restored coziness, not very cozy
            if humor == "dark-undertone" and warmth == "very-cozy":
                return False, "Dark humor undermines 'very cozy' tone"
            return True, ""

        self.rules.append(ValidationRule(
            "cozy.tone.consistency",
            "Tone must remain warm and safe",
            check_tone_consistency,
            "Cozy tone must be maintained throughout"
        ))

        # Rule 3: Community relationships matter
        def check_community_integrity(template, choices):
            """Verify community remains intact and relationships coherent after resolution."""
            layer6 = choices.get(6, {})
            relationships = layer6.get("relationship_focus")
            layer8 = choices.get(8, {})
            community_role = layer8.get("community_role")

            # Community-web relationships should involve community in solution
            if relationships == "community-web" and community_role == "protagonist-solves":
                return False, "Community-focused relationships should involve community in solution"
            return True, ""

        self.rules.append(ValidationRule(
            "cozy.structure.community_integrity",
            "Community must remain intact after resolution",
            check_community_integrity,
            "Cozy stories should not destroy community bonds"
        ))


def validate_choices(template, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
    """Validate choices using core-specific rules.

    Args:
        template: HowdunitTemplate, ParanoiaTemplate, or CozyTemplate instance
        choices: Dict mapping phase (int) to field choices dict

    Returns:
        (is_valid: bool, errors: List[str], warnings: List[str])
    """
    errors = []
    warnings = []

    # Get ruleset for this core
    ruleset = RuleSet(template.core_id)

    # Run all rules
    for rule in ruleset.rules:
        passes, message = rule.check(template, choices)
        if not passes and message:
            errors.append(message)

    return len(errors) == 0, errors, warnings
