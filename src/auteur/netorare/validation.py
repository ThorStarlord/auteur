"""Deterministic validation rules for netorare story structure."""

from typing import Tuple, List, Dict, Any
from auteur.netorare.core_templates import (
    HumiliationTemplate, HorrorTemplate, MysteryTemplate
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
        if self.core_id == "classic_humiliation":
            self._build_humiliation_rules()
        elif self.core_id == "horror":
            self._build_horror_rules()
        elif self.core_id == "mystery":
            self._build_mystery_rules()

    def _build_humiliation_rules(self):
        """Humiliation-specific rules."""

        # Rule 1: Want ≠ Change
        def check_want_not_equal_change(template, choices):
            layer4 = choices.get(4, {})
            want = layer4.get("want")
            change = layer4.get("change")
            if want and change and want == change:
                return False, "Want and Change cannot be the same"
            return True, ""

        self.rules.append(ValidationRule(
            "humiliation.core.want_not_equal_change",
            "Want must differ from Change",
            check_want_not_equal_change,
            "Want and Change cannot be identical in a dramatic arc"
        ))

        # Rule 2: Resistance must be compatible with want
        def check_resistance_compatible_with_want(template, choices):
            layer4 = choices.get(4, {})
            want = layer4.get("want")
            resistance = layer4.get("resistance")

            if not (want and resistance):
                return True, ""  # Not applicable if missing

            # Define incompatible pairings that should cause errors
            # These are cases where the resistance doesn't logically oppose the want
            incompatible_pairs = [
                ("want-prove-love", "resistance-inadequacy"),  # Inadequacy doesn't block proving love
                ("want-escape", "resistance-rival-superiority"),  # Superiority doesn't prevent escape
            ]

            is_incompatible = any(
                want == w and resistance == r for w, r in incompatible_pairs
            )

            if is_incompatible:
                return False, f"Resistance '{resistance}' does not logically block want '{want}'"
            return True, ""

        self.rules.append(ValidationRule(
            "humiliation.core.resistance_compatible",
            "Resistance must be compatible with want",
            check_resistance_compatible_with_want,
            "Resistance must logically oppose the MC's want"
        ))

        # Rule 3: Forbidden endpoint check (Layer 7)
        def check_forbidden_endpoints(template, choices):
            layer7 = choices.get(7, {})
            pacing = layer7.get("pacing")

            # For humiliation, certain pacings are forbidden
            forbidden = ["pacing-mc-wins", "pacing-dramatic-reversal"]
            if pacing in forbidden:
                return False, f"Pacing '{pacing}' is forbidden in humiliation core"
            return True, ""

        self.rules.append(ValidationRule(
            "humiliation.structure.no_mc_wins",
            "MC cannot win (forbidden for humiliation)",
            check_forbidden_endpoints,
            "Humiliation stories cannot end with MC triumphing over rival"
        ))

    def _build_horror_rules(self):
        """Horror-specific rules."""

        def check_want_not_equal_change(template, choices):
            layer4 = choices.get(4, {})
            want = layer4.get("want")
            change = layer4.get("change")
            if want and change and want == change:
                return False, "Want and Change cannot be the same"
            return True, ""

        self.rules.append(ValidationRule(
            "horror.core.want_not_equal_change",
            "Want must differ from Change",
            check_want_not_equal_change,
            "Want and Change cannot be identical"
        ))

        def check_resistance_inescapable(template, choices):
            layer4 = choices.get(4, {})
            want = layer4.get("want")
            change = layer4.get("change")

            # For horror, want is always to escape/prevent/restore
            # and resistance is required to exist and be inescapable
            if want or change:
                resistance = layer4.get("resistance")
                if not resistance:
                    return False, "Horror requires resistance (must be inescapable)"
                if resistance != "resistance-inescapable":
                    return False, "Horror resistance must be inescapability"
            return True, ""

        self.rules.append(ValidationRule(
            "horror.core.resistance_inescapable",
            "Resistance must be inescapable",
            check_resistance_inescapable,
            "Horror's central mechanism requires the situation to be ontologically inescapable"
        ))

        def check_forbidden_return_to_normal(template, choices):
            layer7 = choices.get(7, {})
            pacing = layer7.get("pacing")

            if pacing == "pacing-return-to-normal":
                return False, "Horror endings cannot return to normal"
            return True, ""

        self.rules.append(ValidationRule(
            "horror.structure.no_return_to_normal",
            "Cannot return to normal",
            check_forbidden_return_to_normal,
            "Horror must permanently transform reality"
        ))

    def _build_mystery_rules(self):
        """Mystery-specific rules."""

        def check_want_not_equal_change(template, choices):
            layer4 = choices.get(4, {})
            want = layer4.get("want")
            change = layer4.get("change")
            if want and change and want == change:
                return False, "Want and Change cannot be the same"
            return True, ""

        self.rules.append(ValidationRule(
            "mystery.core.want_not_equal_change",
            "Want must differ from Change",
            check_want_not_equal_change,
            "Want and Change cannot be identical"
        ))

        def check_no_innocent_observer(template, choices):
            layer4 = choices.get(4, {})
            change = layer4.get("change")

            # Mystery must end in complicity, not innocence
            if change == "change-innocent":
                return False, "Mystery cannot end with MC remaining innocent"
            return True, ""

        self.rules.append(ValidationRule(
            "mystery.core.no_innocent_ending",
            "MC cannot remain innocent",
            check_no_innocent_observer,
            "Discovery forces complicity; innocence is impossible"
        ))


def validate_choices(template, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
    """
    Validate a complete set of choices against a template.

    Args:
        template: HumiliationTemplate, HorrorTemplate, or MysteryTemplate
        choices: Dict mapping layer -> {field: value}

    Returns:
        (is_valid, errors, warnings)
    """
    ruleset = RuleSet(template.core_id)

    errors = []
    warnings = []

    for rule in ruleset.rules:
        passes, message = rule.check(template, choices)
        if not passes:
            errors.append(f"{rule.rule_id}: {message}")

    # Additional warnings for uncommon but valid choices
    if not errors:  # Only generate warnings if no errors
        layer4 = choices.get(4, {})
        want = layer4.get("want")
        resistance = layer4.get("resistance")

        # For humiliation: warn on uncommon want/resistance pairings
        # These are valid but unusual
        if template.core_id == "classic_humiliation":
            # Common pairings for humiliation
            common_pairs = [
                ("want-dignity", "resistance-inadequacy"),
                ("want-dignity", "resistance-rival-superiority"),
                ("want-prove-love", "resistance-no-one-believes"),
                ("want-expose", "resistance-no-one-believes"),
            ]

            if want and resistance:
                is_common = any(
                    want == w and resistance == r for w, r in common_pairs
                )

                if not is_common:
                    warnings.append(
                        f"This want/resistance pairing is uncommon. "
                        f"'{want}' usually pairs with different resistance types."
                    )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings
