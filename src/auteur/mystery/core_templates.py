"""Core templates: decision trees for howdunit, paranoia, cozy emotional cores."""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class TemplateOption:
    """A single option in a decision phase."""
    id: str
    label: str
    description: str = ""
    cascades_to: Optional[Dict[int, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        result = asdict(self)
        if result.get("cascades_to") is None:
            del result["cascades_to"]
        if not result.get("description"):
            del result["description"]
        return result


class HowdunitTemplate:
    """Classic Detective Mystery (puzzle-solving) template."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "investigation_style",
        6: "pacing_rhythm",
        7: "clue_distribution",
        8: "solution_density",
        9: "fairness_confidence"
    }

    def __init__(self):
        self.core_id = "howdunit"
        self.primary_emotion = "puzzle-solving"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            1: [
                TemplateOption(
                    id="howdunit",
                    label="Classic Detective Mystery",
                    description="Intellectual satisfaction via puzzle-solving"
                )
            ],
            2: [  # Genre Contract
                TemplateOption(id="detective", label="Detective procedural"),
                TemplateOption(id="procedural", label="Police/investigation procedural"),
                TemplateOption(id="locked-room", label="Locked-room puzzle"),
                TemplateOption(id="puzzle-box", label="Intricate puzzle structure"),
            ],
            3: [  # Scope
                TemplateOption(id="focused", label="Single crime, contained"),
                TemplateOption(id="standard", label="Multi-faceted crime, wider cast"),
                TemplateOption(id="expanded", label="Serial crimes, city-scale investigation"),
            ],
            4: [  # Structural Forces (requires all fields)
                TemplateOption(id="want-solve-puzzle", label="Want: Solve the puzzle", description="Discover truth"),
                TemplateOption(id="want-identify-culprit", label="Want: Identify the culprit", description="Find the guilty party"),
                TemplateOption(id="want-restore-order", label="Want: Restore order", description="Resolve disruption"),
                TemplateOption(id="resistance-misleading-clues", label="Resistance: Misleading clues", description="False evidence misdirects"),
                TemplateOption(id="resistance-false-suspects", label="Resistance: False suspects", description="Red herrings point wrong way"),
                TemplateOption(id="resistance-hidden-motives", label="Resistance: Hidden motives", description="True reasons obscured"),
                TemplateOption(id="conflict-deduction-misdirection", label="Conflict: Deduction vs. misdirection", description="Reader vs. author puzzle"),
                TemplateOption(id="conflict-logic-chaos", label="Conflict: Logic vs. chaos", description="Pattern-seeking in confusion"),
                TemplateOption(id="stakes-justice", label="Stakes: Justice served", description="Culprit answer required"),
                TemplateOption(id="stakes-order-restored", label="Stakes: Order restored", description="Community resolution"),
                TemplateOption(id="change-clarity", label="Change: From confusion to clarity", description="Understanding achieved"),
                TemplateOption(id="change-certainty", label="Change: From suspicion to certainty", description="Truth confirmed"),
            ],
            5: [  # Investigation Style
                TemplateOption(id="logical", label="Logical deduction"),
                TemplateOption(id="intuitive", label="Intuitive investigation"),
                TemplateOption(id="procedural", label="By-the-book procedure"),
            ],
            6: [  # Pacing Rhythm
                TemplateOption(id="accelerating", label="Clues accelerate toward solution"),
                TemplateOption(id="rhythmic", label="Steady rhythm of discovery"),
                TemplateOption(id="zigzag", label="Forward progress with setbacks"),
            ],
            7: [  # Clue Distribution
                TemplateOption(id="early-heavy", label="Heavy clues early, light late"),
                TemplateOption(id="even", label="Even clue distribution"),
                TemplateOption(id="late-heavy", label="Light clues early, heavy late"),
            ],
            8: [  # Solution Density
                TemplateOption(id="tight", label="Solution barely derivable from clues"),
                TemplateOption(id="moderate", label="Solution is one of several reasonable readings"),
                TemplateOption(id="generous", label="Solution obvious once clues are gathered"),
            ],
            9: [  # Fairness Confidence
                TemplateOption(id="fair-high", label="High confidence reader could solve it"),
                TemplateOption(id="fair-medium", label="Medium confidence (possible on rereads)"),
                TemplateOption(id="fair-challenging", label="Challenging but fair puzzle"),
            ]
        }

    def get_options(self, phase: int) -> List[TemplateOption]:
        """Get available options for a phase."""
        return self.options.get(phase, [])

    def get_constraints(self, phase: int) -> str:
        """Get validation constraints for a phase."""
        if phase == 4:
            return "Must select one from each field: want, resistance, conflict, stakes, change"
        return ""

    def validate_choices(self, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
        """Validate choices for structural coherence. Returns (is_valid, errors, warnings)."""
        errors = []
        warnings = []

        for phase, phase_choices in choices.items():
            if phase not in self.phases:
                errors.append(f"Phase {phase} does not exist in Howdunit template (valid: 1-9)")
                continue

            for field, value in phase_choices.items():
                # Check that value exists in options for this phase
                valid_ids = [opt.id for opt in self.get_options(phase)]
                if value not in valid_ids:
                    errors.append(f"Phase {phase}: '{value}' is not a valid option. Valid options: {valid_ids}")

        return len(errors) == 0, errors, warnings

    def get_option_label(self, phase: int, field_or_section: str, option_id: str) -> str:
        """Get human-readable label for an option.

        Args:
            phase: Phase number
            field_or_section: Field name within that phase (ignored for mystery, as options are flat)
            option_id: The option's ID (e.g., "want-solve-puzzle")

        Returns:
            Label string (e.g., "Want: Solve the puzzle")

        Raises:
            KeyError: If the option_id is not found
        """
        phase_options = self.get_options(phase)
        for opt in phase_options:
            if isinstance(opt, TemplateOption) and opt.id == option_id:
                return opt.label
        raise KeyError(f"Option {option_id} not found in phase {phase}")


class ParanoiaTemplate:
    """Paranoia (psychological thriller) template."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "narrator_reliability",
        6: "gaslighting_intensity",
        7: "paranoia_escalation",
        8: "truth_ambiguity",
        9: "dread_confidence"
    }

    def __init__(self):
        self.core_id = "paranoia"
        self.primary_emotion = "dread"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            1: [
                TemplateOption(
                    id="paranoia",
                    label="Paranoia / Psychological Thriller",
                    description="Dread and uncertainty via unreliable reality"
                )
            ],
            2: [
                TemplateOption(id="gaslight", label="Gaslighting narrative"),
                TemplateOption(id="conspiracy", label="Hidden conspiracy"),
                TemplateOption(id="psychological-horror", label="Psychological horror premise"),
                TemplateOption(id="unreliable-narrator", label="Unreliable narrator study"),
            ],
            3: [
                TemplateOption(id="intimate", label="1-2 characters, internal focus"),
                TemplateOption(id="contained", label="Household or institution"),
                TemplateOption(id="sprawling", label="Conspiracy reaches wider"),
            ],
            4: [
                TemplateOption(id="want-understand-reality", label="Want: Understand what's real"),
                TemplateOption(id="want-escape-situation", label="Want: Escape the situation"),
                TemplateOption(id="want-prove-sanity", label="Want: Prove they're not crazy"),
                TemplateOption(id="resistance-unreliable-narrator", label="Resistance: Unreliable narrator"),
                TemplateOption(id="resistance-gaslighting", label="Resistance: Active gaslighting"),
                TemplateOption(id="resistance-hidden-truth", label="Resistance: Truth hidden from all"),
                TemplateOption(id="conflict-reality-perception", label="Conflict: Reality vs. Perception"),
                TemplateOption(id="conflict-trust-doubt", label="Conflict: Trust vs. Doubt"),
                TemplateOption(id="stakes-mental-stability", label="Stakes: Mental stability"),
                TemplateOption(id="stakes-safety", label="Stakes: Physical safety"),
                TemplateOption(id="stakes-identity", label="Stakes: Sense of identity"),
                TemplateOption(id="change-paranoia-peak", label="Change: Paranoia reaches peak"),
                TemplateOption(id="change-revelation", label="Change: Revelation of truth"),
            ],
            5: [
                TemplateOption(id="highly-unreliable", label="Narrator severely distorts reality"),
                TemplateOption(id="moderately-unreliable", label="Narrator's account has selective gaps"),
                TemplateOption(id="subtly-unreliable", label="Subtle inconsistencies suggest doubt"),
            ],
            6: [
                TemplateOption(id="psychological", label="Psychological manipulation"),
                TemplateOption(id="social", label="Social pressure and isolation"),
                TemplateOption(id="institutional", label="System-level deception"),
            ],
            7: [
                TemplateOption(id="slow-build", label="Paranoia builds slowly from doubt"),
                TemplateOption(id="rapid-spiral", label="Paranoia spirals rapidly"),
                TemplateOption(id="rhythmic-escalation", label="Rhythmic escalation of dread"),
            ],
            8: [
                TemplateOption(id="fully-revealed", label="Truth is fully revealed by end"),
                TemplateOption(id="ambiguous", label="Truth remains ambiguous"),
                TemplateOption(id="devastatingly-different", label="Reality is devastatingly different from perception"),
            ],
            9: [
                TemplateOption(id="high-dread", label="Maintains high dread throughout"),
                TemplateOption(id="managed-dread", label="Dread peaks then resolves"),
                TemplateOption(id="open-dread", label="Dread remains unresolved"),
            ]
        }

    def get_options(self, phase: int) -> List[TemplateOption]:
        """Get available options for a phase."""
        return self.options.get(phase, [])

    def get_constraints(self, phase: int) -> str:
        """Get validation constraints for a phase."""
        if phase == 4:
            return "Must select one from each field: want, resistance, conflict, stakes, change"
        return ""

    def validate_choices(self, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
        """Validate choices for structural coherence."""
        errors = []
        warnings = []

        for phase, phase_choices in choices.items():
            if phase not in self.phases:
                errors.append(f"Phase {phase} does not exist in Paranoia template (valid: 1-9)")
                continue

            for field, value in phase_choices.items():
                valid_ids = [opt.id for opt in self.get_options(phase)]
                if value not in valid_ids:
                    errors.append(f"Phase {phase}: '{value}' is not a valid option. Valid options: {valid_ids}")

        return len(errors) == 0, errors, warnings

    def get_option_label(self, phase: int, field_or_section: str, option_id: str) -> str:
        """Get human-readable label for an option.

        Args:
            phase: Phase number
            field_or_section: Field name within that phase (ignored for mystery, as options are flat)
            option_id: The option's ID (e.g., "want-understand-reality")

        Returns:
            Label string (e.g., "Want: Understand what's real")

        Raises:
            KeyError: If the option_id is not found
        """
        phase_options = self.get_options(phase)
        for opt in phase_options:
            if isinstance(opt, TemplateOption) and opt.id == option_id:
                return opt.label
        raise KeyError(f"Option {option_id} not found in phase {phase}")


class CozyTemplate:
    """Cozy Mystery (low-stakes, community-focused) template."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "humor_level",
        6: "relationship_focus",
        7: "violence_budget",
        8: "community_role",
        9: "warmth_confidence"
    }

    def __init__(self):
        self.core_id = "cozy"
        self.primary_emotion = "comfort"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            1: [
                TemplateOption(
                    id="cozy",
                    label="Cozy Mystery",
                    description="Comfort and closure in a warm, safe world"
                )
            ],
            2: [
                TemplateOption(id="village", label="Village/small-town cozy"),
                TemplateOption(id="bookshop", label="Bookshop or library cozy"),
                TemplateOption(id="domestic", label="Domestic/home cozy"),
                TemplateOption(id="culinary", label="Food/culinary cozy"),
            ],
            3: [
                TemplateOption(id="micro", label="Single household or shop"),
                TemplateOption(id="village", label="Village with interconnected residents"),
                TemplateOption(id="regional", label="Multiple small towns"),
            ],
            4: [
                TemplateOption(id="want-solve-community", label="Want: Solve in community context"),
                TemplateOption(id="want-find-truth", label="Want: Find the truth gently"),
                TemplateOption(id="want-restore-peace", label="Want: Restore community peace"),
                TemplateOption(id="resistance-scattered-clues", label="Resistance: Clues are scattered"),
                TemplateOption(id="resistance-community-dynamics", label="Resistance: Community politics block truth"),
                TemplateOption(id="resistance-reluctant-witnesses", label="Resistance: Witnesses reluctant to speak"),
                TemplateOption(id="conflict-investigation-daily-life", label="Conflict: Investigation vs. daily life"),
                TemplateOption(id="conflict-truth-bonds", label="Conflict: Finding truth vs. maintaining bonds"),
                TemplateOption(id="stakes-community-bonds", label="Stakes: Community relationships"),
                TemplateOption(id="stakes-personal-growth", label="Stakes: Personal transformation"),
                TemplateOption(id="stakes-closure", label="Stakes: Closure and peace"),
                TemplateOption(id="change-community-shift", label="Change: Community dynamics shift"),
                TemplateOption(id="change-mystery-resolved", label="Change: Mystery is solved"),
            ],
            5: [
                TemplateOption(id="light-humor", label="Light, warm humor throughout"),
                TemplateOption(id="occasional-humor", label="Occasional moments of levity"),
                TemplateOption(id="dark-undertone", label="Dark humor underneath warmth"),
            ],
            6: [
                TemplateOption(id="protagonist-centric", label="Focus on protagonist relationships"),
                TemplateOption(id="community-web", label="Complex web of community bonds"),
                TemplateOption(id="romance-subplot", label="Romantic subplot alongside investigation"),
            ],
            7: [
                TemplateOption(id="none", label="No violence (mystery is abstract)"),
                TemplateOption(id="off-page", label="Violence is off-page"),
                TemplateOption(id="minimal", label="Minimal, non-graphic violence"),
            ],
            8: [
                TemplateOption(id="community-central", label="Community bonds are central to resolution"),
                TemplateOption(id="community-involved", label="Community participates in solution"),
                TemplateOption(id="protagonist-solves", label="Protagonist solves mostly alone"),
            ],
            9: [
                TemplateOption(id="very-cozy", label="Very warm and safe throughout"),
                TemplateOption(id="cozy-with-tension", label="Cozy interrupted by investigation tension"),
                TemplateOption(id="restored-coziness", label="Coziness restored by resolution"),
            ]
        }

    def get_options(self, phase: int) -> List[TemplateOption]:
        """Get available options for a phase."""
        return self.options.get(phase, [])

    def get_constraints(self, phase: int) -> str:
        """Get validation constraints for a phase."""
        if phase == 4:
            return "Must select one from each field: want, resistance, conflict, stakes, change"
        return ""

    def validate_choices(self, choices: Dict[int, Dict[str, str]]) -> Tuple[bool, List[str], List[str]]:
        """Validate choices for structural coherence."""
        errors = []
        warnings = []

        for phase, phase_choices in choices.items():
            if phase not in self.phases:
                errors.append(f"Phase {phase} does not exist in Cozy template (valid: 1-9)")
                continue

            for field, value in phase_choices.items():
                valid_ids = [opt.id for opt in self.get_options(phase)]
                if value not in valid_ids:
                    errors.append(f"Phase {phase}: '{value}' is not a valid option. Valid options: {valid_ids}")

        return len(errors) == 0, errors, warnings

    def get_option_label(self, phase: int, field_or_section: str, option_id: str) -> str:
        """Get human-readable label for an option.

        Args:
            phase: Phase number
            field_or_section: Field name within that phase (ignored for mystery, as options are flat)
            option_id: The option's ID (e.g., "warm-amateur-sleuth")

        Returns:
            Label string (e.g., "Warm amateur sleuth as protagonist")

        Raises:
            KeyError: If the option_id is not found
        """
        phase_options = self.get_options(phase)
        for opt in phase_options:
            if isinstance(opt, TemplateOption) and opt.id == option_id:
                return opt.label
        raise KeyError(f"Option {option_id} not found in phase {phase}")


def get_template(core_id: str):
    """Factory function: return template instance for core_id."""
    if core_id == "howdunit":
        return HowdunitTemplate()
    elif core_id == "paranoia":
        return ParanoiaTemplate()
    elif core_id == "cozy":
        return CozyTemplate()
    else:
        raise ValueError(f"Unknown mystery core_id: {core_id}. Valid: howdunit, paranoia, cozy")
