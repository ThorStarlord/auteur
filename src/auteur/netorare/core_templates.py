"""Core templates: decision trees for humiliation, horror, mystery emotional cores."""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class TemplateOption:
    """A single option in a decision phase."""
    id: str
    label: str
    description: str = ""
    cascades_to: Optional[Dict[int, Any]] = None  # Which layers this affects

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        result = asdict(self)
        # Filter out None cascades_to for cleaner dicts
        if result.get("cascades_to") is None:
            del result["cascades_to"]
        if not result.get("description"):
            del result["description"]
        return result


class HumiliationTemplate:
    """Classic Humiliation netorare template."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "threads",
        6: "carriers",
        7: "representation",
        8: "modulation",
        9: "resonance"
    }

    def __init__(self):
        self.core_id = "classic_humiliation"
        self.primary_emotion = "humiliation"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            4: {  # Layer 4: Structural Forces
                "want": [
                    TemplateOption(
                        id="want-dignity",
                        label="Regain lost dignity / prove their worth",
                        description="MC wants to restore their self-image"
                    ),
                    TemplateOption(
                        id="want-prove-love",
                        label="Prove their love was genuine all along",
                        description="MC wants to validate the relationship"
                    ),
                    TemplateOption(
                        id="want-expose",
                        label="Expose the other person's deception",
                        description="MC wants to reveal the truth"
                    ),
                    TemplateOption(
                        id="want-escape",
                        label="Escape or flee the situation",
                        description="MC wants to get away"
                    ),
                ],
                "resistance": [
                    TemplateOption(
                        id="resistance-inadequacy",
                        label="Own inadequacy (real or perceived)",
                        description="MC's own failings block their want"
                    ),
                    TemplateOption(
                        id="resistance-rival-superiority",
                        label="Rival's genuine superiority",
                        description="The other person is genuinely better"
                    ),
                    TemplateOption(
                        id="resistance-no-one-believes",
                        label="No one will believe MC's version",
                        description="Social pressure blocks the want"
                    ),
                ],
                "change": [
                    TemplateOption(
                        id="change-accept",
                        label="Accept powerlessness / loss",
                        description="Tragic ending: MC accepts reality"
                    ),
                    TemplateOption(
                        id="change-reclaim",
                        label="Reclaim through reckoning (override)",
                        description="Cathartic ending: MC fights back (requires override)"
                    ),
                ],
            },
            5: {  # Layer 5: Threads
                "subplot": [
                    TemplateOption(
                        id="subplot-rival-perspective",
                        label="Rival's perspective (secondary POV)",
                        description="Show the rival's side of the story"
                    ),
                    TemplateOption(
                        id="subplot-witness",
                        label="Witness/confidant character",
                        description="External observer sees the humiliation"
                    ),
                    TemplateOption(
                        id="subplot-partner-motivation",
                        label="Partner's hidden motivation (revealed)",
                        description="Gradually reveal why the partner chose the rival"
                    ),
                    TemplateOption(
                        id="subplot-none",
                        label="No subplots (focus on main thread only)",
                        description="Keep story focused and tight"
                    ),
                ],
            },
            6: {  # Layer 6: Carriers
                "pov_structure": [
                    TemplateOption(
                        id="pov-limited-mc",
                        label="Limited to MC's perspective only",
                        description="Recommended: MC's shame-spiral view"
                    ),
                    TemplateOption(
                        id="pov-alternating",
                        label="Alternating MC + Rival (dual POV)",
                        description="Show both perspectives"
                    ),
                    TemplateOption(
                        id="pov-unreliable",
                        label="MC only, unreliable narrator",
                        description="MC's mind breaks down as story progresses"
                    ),
                ],
            },
            7: {  # Layer 7: Representation
                "pacing": [
                    TemplateOption(
                        id="pacing-accelerating",
                        label="Accelerating reveals (clue density increases)",
                        description="Discoveries compound near the end"
                    ),
                    TemplateOption(
                        id="pacing-slow-burn",
                        label="Slow burn (long suspicion, then acceleration)",
                        description="Long period of unease before revelation"
                    ),
                    TemplateOption(
                        id="pacing-delayed",
                        label="Delayed discovery (most withheld until Act 3)",
                        description="Final act explosion of information"
                    ),
                ],
            },
            8: {  # Layer 8: Modulation
                "tone": [
                    TemplateOption(
                        id="tone-suffocating",
                        label="Suffocating intimacy",
                        description="Claustrophobic, everything feels close and personal"
                    ),
                    TemplateOption(
                        id="tone-observation",
                        label="Social observation (watching from outside)",
                        description="Detached, witnessing rather than drowning"
                    ),
                    TemplateOption(
                        id="tone-fragmentation",
                        label="Psychological fragmentation",
                        description="MC's mind breaking apart"
                    ),
                ],
            },
            9: {  # Layer 9: Resonance
                "theme": [
                    TemplateOption(
                        id="theme-love-vs-adequacy",
                        label="The limits of love vs. adequacy",
                        description="Can love exist without being good enough?"
                    ),
                    TemplateOption(
                        id="theme-powerlessness",
                        label="Powerlessness in witnessing change",
                        description="The horror of watching what you cannot prevent"
                    ),
                    TemplateOption(
                        id="theme-self-deception",
                        label="The cost of self-deception",
                        description="What we tell ourselves about our relationships"
                    ),
                ],
            },
        }

    def get_option_label(self, phase: int, field_or_section: str, option_id: str) -> str:
        """Get human-readable label for an option.

        Args:
            phase: Phase number
            field_or_section: Field name within that phase (e.g., "want", "resistance")
            option_id: The option's ID (e.g., "want-dignity")

        Returns:
            Label string (e.g., "Regain lost dignity / prove their worth")

        Raises:
            KeyError: If the option_id is not found
        """
        raw_options = self.options.get(phase, {})

        # All netorare phases use nested dict structure
        if isinstance(raw_options, dict):
            field_options = raw_options.get(field_or_section, [])
            for opt in field_options:
                if isinstance(opt, TemplateOption) and opt.id == option_id:
                    return opt.label
            raise KeyError(f"Option {option_id} not found in phase {phase} field {field_or_section}")

        raise KeyError(f"No options found for phase {phase}")

    def get_options(self, phase: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all options for a given phase as dicts."""
        raw_options = self.options.get(phase, {})
        result = {}
        for key, option_list in raw_options.items():
            result[key] = [opt.to_dict() if isinstance(opt, TemplateOption) else opt for opt in option_list]
        return result

    def get_constraints(self, phase: int) -> List[str]:
        """Get validation constraints for a phase."""
        constraints = {
            4: [
                "want_not_equal_change",
                "resistance_blocks_want",
                "stakes_align_with_core",
            ],
            5: ["threads_support_want"],
            6: ["required_roles_present"],
            7: ["act_structure_matches_humiliation"],
            9: ["theme_resonates_with_layers"],
        }
        return constraints.get(phase, [])

    def validate_choices(self, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a complete set of choices against this template.

        Args:
            choices: Dict mapping phase -> {field: value}

        Returns:
            (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # For each phase with choices, validate
        for phase, phase_choices in choices.items():
            if phase not in self.phases:
                errors.append(f"Unknown phase {phase}")
                continue

            # Validate each field in the phase
            for field, value in phase_choices.items():
                options = self.get_options(phase)
                if field not in options:
                    errors.append(f"Unknown field {field} in phase {phase}")
                    continue

                # Check if the value is a valid option ID
                valid_ids = [opt["id"] for opt in options[field]]
                if value not in valid_ids:
                    errors.append(
                        f"Invalid value '{value}' for field '{field}' in phase {phase}. "
                        f"Valid options: {valid_ids}"
                    )

        is_valid = len(errors) == 0
        return is_valid, errors, warnings


class HorrorTemplate:
    """Horror netorare template (dread/body-horror/ontological)."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "threads",
        6: "carriers",
        7: "representation",
        8: "modulation",
        9: "resonance"
    }

    def __init__(self):
        self.core_id = "horror"
        self.primary_emotion = "dread"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            4: {
                "want": [
                    TemplateOption(
                        id="want-escape",
                        label="Escape / get away from the transgression",
                    ),
                    TemplateOption(
                        id="want-prevent",
                        label="Prevent the transformation from happening",
                    ),
                    TemplateOption(
                        id="want-understand",
                        label="Understand what is happening to reality",
                    ),
                    TemplateOption(
                        id="want-restore",
                        label="Restore things to how they were",
                    ),
                ],
                "resistance": [
                    TemplateOption(
                        id="resistance-inescapable",
                        label="The violation is inescapable",
                        description="Every attempt to escape reveals that reality has already changed",
                    ),
                ],
                "change": [
                    TemplateOption(
                        id="change-transform",
                        label="Transform into something new",
                        description="MC becomes part of the horror"
                    ),
                    TemplateOption(
                        id="change-accept-new-order",
                        label="Accept the new order of reality",
                        description="MC survives but reality is fundamentally changed"
                    ),
                ],
            },
            5: {
                "subplot": [
                    TemplateOption(
                        id="subplot-sanity",
                        label="Sanity fragmentation (MC's mind breaks)",
                    ),
                    TemplateOption(
                        id="subplot-partner-alien",
                        label="Partner's unknowability (becomes alien)",
                    ),
                    TemplateOption(
                        id="subplot-cosmic",
                        label="Cosmic scale (vast forces revealed)",
                    ),
                ],
            },
            6: {
                "pov_structure": [
                    TemplateOption(
                        id="pov-fragmenting",
                        label="Fragmenting perspective (sanity breaks)",
                        description="Recommended for horror"
                    ),
                    TemplateOption(
                        id="pov-inhuman",
                        label="Detached observation (MC becoming inhuman)",
                    ),
                ],
            },
            7: {
                "pacing": [
                    TemplateOption(
                        id="pacing-mounting",
                        label="Mounting dread (tension builds)",
                    ),
                    TemplateOption(
                        id="pacing-sudden",
                        label="Sudden vertigo (stable world breaks all at once)",
                    ),
                    TemplateOption(
                        id="pacing-gradual",
                        label="Slow wrongness (accumulates gradually)",
                    ),
                ],
            },
            8: {
                "tone": [
                    TemplateOption(
                        id="tone-wrongness",
                        label="Wrongness and violation",
                    ),
                    TemplateOption(
                        id="tone-cosmic",
                        label="Cosmic indifference",
                    ),
                    TemplateOption(
                        id="tone-body-horror",
                        label="Body horror intimacy",
                    ),
                ],
            },
            9: {
                "theme": [
                    TemplateOption(
                        id="theme-unknowable",
                        label="The horror of seeing loved ones become unknowable",
                    ),
                    TemplateOption(
                        id="theme-knowledge",
                        label="The price of knowledge",
                    ),
                    TemplateOption(
                        id="theme-corruption",
                        label="Bodily/existential corruption",
                    ),
                ],
            },
        }

    def get_options(self, phase: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all options for a given phase as dicts."""
        raw_options = self.options.get(phase, {})
        result = {}
        for key, option_list in raw_options.items():
            result[key] = [opt.to_dict() if isinstance(opt, TemplateOption) else opt for opt in option_list]
        return result

    def get_constraints(self, phase: int) -> List[str]:
        """Get validation constraints for a phase."""
        constraints = {
            4: ["want_not_equal_change", "resistance_is_inescapable"],
            5: ["threads_escalate_horror"],
            6: ["partner_becomes_alien"],
            7: ["act_structure_matches_horror"],
            9: ["theme_resonates_with_layers"],
        }
        return constraints.get(phase, [])

    def validate_choices(self, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a complete set of choices against this template.

        Args:
            choices: Dict mapping phase -> {field: value}

        Returns:
            (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # For each phase with choices, validate
        for phase, phase_choices in choices.items():
            if phase not in self.phases:
                errors.append(f"Unknown phase {phase}")
                continue

            # Validate each field in the phase
            for field, value in phase_choices.items():
                options = self.get_options(phase)
                if field not in options:
                    errors.append(f"Unknown field {field} in phase {phase}")
                    continue

                # Check if the value is a valid option ID
                valid_ids = [opt["id"] for opt in options[field]]
                if value not in valid_ids:
                    errors.append(
                        f"Invalid value '{value}' for field '{field}' in phase {phase}. "
                        f"Valid options: {valid_ids}"
                    )

        is_valid = len(errors) == 0
        return is_valid, errors, warnings

    def get_option_label(self, phase: int, field_or_section: str, option_id: str) -> str:
        """Get human-readable label for an option.

        Args:
            phase: Phase number
            field_or_section: Field name within that phase (e.g., "want", "resistance")
            option_id: The option's ID (e.g., "want-escape")

        Returns:
            Label string (e.g., "Escape / get away from the transgression")

        Raises:
            KeyError: If the option_id is not found
        """
        raw_options = self.options.get(phase, {})

        # All netorare phases use nested dict structure
        if isinstance(raw_options, dict):
            field_options = raw_options.get(field_or_section, [])
            for opt in field_options:
                if isinstance(opt, TemplateOption) and opt.id == option_id:
                    return opt.label
            raise KeyError(f"Option {option_id} not found in phase {phase} field {field_or_section}")

        raise KeyError(f"No options found for phase {phase}")


class MysteryTemplate:
    """Mystery netorare template (voyeurism/investigation)."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "threads",
        6: "carriers",
        7: "representation",
        8: "modulation",
        9: "resonance"
    }

    def __init__(self):
        self.core_id = "mystery"
        self.primary_emotion = "voyeurism"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            4: {
                "want": [
                    TemplateOption(
                        id="want-truth",
                        label="Understand the truth about the relationship",
                    ),
                    TemplateOption(
                        id="want-confirm",
                        label="Confirm suspicions without being seen",
                    ),
                    TemplateOption(
                        id="want-expose",
                        label="Expose what's been hidden",
                    ),
                    TemplateOption(
                        id="want-motives",
                        label="Figure out the other person's motivations",
                    ),
                ],
                "resistance": [
                    TemplateOption(
                        id="resistance-hidden-truth",
                        label="Truth remains hidden",
                        description="The truth is obscured or protected"
                    ),
                    TemplateOption(
                        id="resistance-misdirection",
                        label="False leads and misdirection",
                        description="Clues point in wrong directions"
                    ),
                    TemplateOption(
                        id="resistance-own-doubt",
                        label="Own doubt and uncertainty",
                        description="MC questions their own perceptions"
                    ),
                ],
                "change": [
                    TemplateOption(
                        id="change-witness",
                        label="Become unwilling witness (knew it, did nothing)",
                    ),
                    TemplateOption(
                        id="change-participant",
                        label="Become active participant (knew it, got involved)",
                    ),
                ],
            },
            5: {
                "subplot": [
                    TemplateOption(
                        id="subplot-red-herrings",
                        label="Red herrings (false leads, misdirection)",
                    ),
                    TemplateOption(
                        id="subplot-complicity",
                        label="Slow realization of own complicity",
                    ),
                    TemplateOption(
                        id="subplot-secondary",
                        label="Secondary investigation (parallel mystery)",
                    ),
                ],
            },
            6: {
                "pov_structure": [
                    TemplateOption(
                        id="pov-unreliable",
                        label="Gradually unreliable as knowledge reveals",
                        description="Recommended: detective becomes unreliable"
                    ),
                    TemplateOption(
                        id="pov-detective",
                        label="Detective prose style (analytical)",
                    ),
                ],
            },
            7: {
                "pacing": [
                    TemplateOption(
                        id="pacing-clue-density",
                        label="Clue density increases progressively",
                    ),
                    TemplateOption(
                        id="pacing-dump",
                        label="Information withheld then dumped",
                    ),
                    TemplateOption(
                        id="pacing-steady",
                        label="Steady accumulation with false explanations",
                    ),
                ],
            },
            8: {
                "tone": [
                    TemplateOption(
                        id="tone-voyeurism",
                        label="Voyeuristic unease",
                    ),
                    TemplateOption(
                        id="tone-noir",
                        label="Noir investigation",
                    ),
                    TemplateOption(
                        id="tone-puzzle",
                        label="Psychological puzzle-solving",
                    ),
                ],
            },
            9: {
                "theme": [
                    TemplateOption(
                        id="theme-innocence",
                        label="The impossibility of remaining innocent once you know",
                    ),
                    TemplateOption(
                        id="theme-complicity",
                        label="The complicity of observation",
                    ),
                    TemplateOption(
                        id="theme-watching",
                        label="Watching and being watched",
                    ),
                ],
            },
        }

    def get_options(self, phase: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all options for a given phase as dicts."""
        raw_options = self.options.get(phase, {})
        result = {}
        for key, option_list in raw_options.items():
            result[key] = [opt.to_dict() if isinstance(opt, TemplateOption) else opt for opt in option_list]
        return result

    def get_constraints(self, phase: int) -> List[str]:
        """Get validation constraints for a phase."""
        constraints = {
            4: ["want_not_equal_change", "resistance_hides_information"],
            5: ["threads_support_investigation"],
            6: ["required_roles_distinct"],
            7: ["act_structure_matches_mystery"],
            9: ["theme_resonates_with_layers"],
        }
        return constraints.get(phase, [])

    def validate_choices(self, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a complete set of choices against this template.

        Args:
            choices: Dict mapping phase -> {field: value}

        Returns:
            (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # For each phase with choices, validate
        for phase, phase_choices in choices.items():
            if phase not in self.phases:
                errors.append(f"Unknown phase {phase}")
                continue

            # Validate each field in the phase
            for field, value in phase_choices.items():
                options = self.get_options(phase)
                if field not in options:
                    errors.append(f"Unknown field {field} in phase {phase}")
                    continue

                # Check if the value is a valid option ID
                valid_ids = [opt["id"] for opt in options[field]]
                if value not in valid_ids:
                    errors.append(
                        f"Invalid value '{value}' for field '{field}' in phase {phase}. "
                        f"Valid options: {valid_ids}"
                    )

        is_valid = len(errors) == 0
        return is_valid, errors, warnings

    def get_option_label(self, phase: int, field_or_section: str, option_id: str) -> str:
        """Get human-readable label for an option.

        Args:
            phase: Phase number
            field_or_section: Field name within that phase (e.g., "want", "resistance")
            option_id: The option's ID (e.g., "want-truth")

        Returns:
            Label string (e.g., "Understand the truth about the relationship")

        Raises:
            KeyError: If the option_id is not found
        """
        raw_options = self.options.get(phase, {})

        # All netorare phases use nested dict structure
        if isinstance(raw_options, dict):
            field_options = raw_options.get(field_or_section, [])
            for opt in field_options:
                if isinstance(opt, TemplateOption) and opt.id == option_id:
                    return opt.label
            raise KeyError(f"Option {option_id} not found in phase {phase} field {field_or_section}")

        raise KeyError(f"No options found for phase {phase}")


def get_template(core_id: str):
    """Factory function to get the right template."""
    templates = {
        "classic_humiliation": HumiliationTemplate,
        "horror": HorrorTemplate,
        "mystery": MysteryTemplate,
    }
    template_class = templates.get(core_id)
    if not template_class:
        raise ValueError(f"Unknown core: {core_id}")
    return template_class()
