"""Core templates: decision trees for sensual dominance, tender surrender, romantic authority emotional cores."""

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


class SensualDominanceTemplate:
    """Sensual Dominance template: playful control and intimate power exchange."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "boundary_clarity",
        6: "tone_playfulness",
        7: "care_expression",
        8: "power_balance",
        9: "connection_confidence"
    }

    def __init__(self):
        self.core_id = "sensual_dominance"
        self.primary_emotion = "playful_control"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            1: [
                TemplateOption(
                    id="sensual_dominance",
                    label="Sensual Dominance",
                    description="Playful control and intimate power exchange"
                )
            ],
            2: [
                TemplateOption(id="dom_leadership", label="Dominant leadership through charm"),
                TemplateOption(id="playful_power", label="Playful power dynamics"),
                TemplateOption(id="intimate_control", label="Intimate control with consent"),
                TemplateOption(id="confident_direction", label="Confident direction of partnership"),
            ],
            3: [
                TemplateOption(id="intimate_pair", label="Intimate pair dynamic"),
                TemplateOption(id="expanding_circle", label="Expanding circle of trust"),
                TemplateOption(id="community_dynamic", label="Community within safe bounds"),
            ],
            4: {
                "want": [
                    TemplateOption(
                        id="want-establish-trust",
                        label="Establish trust through demonstrated leadership",
                        description="Dominant seeks to earn submissive's faith"
                    ),
                    TemplateOption(
                        id="want-create-safety",
                        label="Create safe space for vulnerability",
                        description="Dominant wants to enable partner's openness"
                    ),
                    TemplateOption(
                        id="want-explore-together",
                        label="Explore power exchange together",
                        description="Mutual discovery of pleasure and connection"
                    ),
                    TemplateOption(
                        id="want-deepen-intimacy",
                        label="Deepen intimate connection through power play",
                        description="Use power dynamics to strengthen bonds"
                    ),
                ],
                "resistance": [
                    TemplateOption(
                        id="resistance-partner-doubt",
                        label="Partner's doubt about surrendering",
                        description="Submissive fears loss of autonomy"
                    ),
                    TemplateOption(
                        id="resistance-trust-gap",
                        label="Gap in existing trust",
                        description="Relationship not yet deep enough"
                    ),
                    TemplateOption(
                        id="resistance-vulnerability-fear",
                        label="Submissive's fear of vulnerability",
                        description="Past experiences create protective walls"
                    ),
                    TemplateOption(
                        id="resistance-boundary-negotiations",
                        label="Ongoing boundary negotiations",
                        description="Finding balance between control and agency"
                    ),
                ],
                "conflict": [
                    TemplateOption(
                        id="conflict-control-vs-consent",
                        label="Control vs. enthusiastic consent",
                        description="Balancing direction with genuine agreement"
                    ),
                    TemplateOption(
                        id="conflict-power-vs-care",
                        label="Display of power vs. demonstration of care",
                        description="Dominance must never appear cruel"
                    ),
                    TemplateOption(
                        id="conflict-structure-vs-flexibility",
                        label="Structure vs. flexibility",
                        description="Maintaining order while allowing individual expression"
                    ),
                ],
                "stakes": [
                    TemplateOption(
                        id="stakes-emotional-intimacy",
                        label="Emotional intimacy and trust",
                        description="Relationship depth at risk"
                    ),
                    TemplateOption(
                        id="stakes-vulnerability-safety",
                        label="Vulnerability requires safety",
                        description="Submissive's security depends on dominant's care"
                    ),
                    TemplateOption(
                        id="stakes-connection-depth",
                        label="Depth of connection and understanding",
                        description="Either partners grow together or drift apart"
                    ),
                ],
                "change": [
                    TemplateOption(
                        id="change-tentative-to-confident",
                        label="From tentative to confidently empowered",
                        description="Both partners gain certainty in their roles"
                    ),
                    TemplateOption(
                        id="change-stranger-to-intimate",
                        label="From stranger to intimate partner",
                        description="Deep mutual knowledge achieved"
                    ),
                    TemplateOption(
                        id="change-separate-to-synergistic",
                        label="From separate selves to synergistic whole",
                        description="Power exchange creates union without loss of self"
                    ),
                ],
            },
            5: [
                TemplateOption(id="boundaries-explicit", label="Boundaries explicitly stated and honored"),
                TemplateOption(id="boundaries-tested", label="Boundaries gently tested and refined"),
                TemplateOption(id="boundaries-woven", label="Boundaries woven into dynamic naturally"),
            ],
            6: [
                TemplateOption(id="playfulness-central", label="Playfulness central to dynamic"),
                TemplateOption(id="playfulness-frequent", label="Playfulness frequent, humor present"),
                TemplateOption(id="playfulness-balanced", label="Playfulness balanced with intensity"),
            ],
            7: [
                TemplateOption(id="care-constant", label="Dominant's care constantly demonstrated"),
                TemplateOption(id="care-expressed", label="Care expressed through attentiveness"),
                TemplateOption(id="care-integrated", label="Care integral to every interaction"),
            ],
            8: [
                TemplateOption(id="power-dynamic", label="Power dynamic clearly established"),
                TemplateOption(id="power-balanced", label="Power exchange remains balanced"),
                TemplateOption(id="power-mutual", label="Power ultimately serves mutual pleasure"),
            ],
            9: [
                TemplateOption(id="connection-deepened", label="Connection visibly deepened"),
                TemplateOption(id="connection-secure", label="Security in power exchange achieved"),
                TemplateOption(id="connection-transcendent", label="Transcendent intimacy through trust"),
            ],
        }

    def get_option_label(self, phase: int, field_or_section: str, option_id: str) -> str:
        """Get human-readable label for an option.

        Args:
            phase: Phase number
            field_or_section: Field name within that phase (e.g., "want", "resistance")
            option_id: The option's ID (e.g., "want-establish-trust")

        Returns:
            Label string (e.g., "Establish trust through demonstrated leadership")

        Raises:
            KeyError: If the option_id is not found
        """
        raw_options = self.options.get(phase, {})

        # Handle Layer 4 (structural forces) which has nested dict
        if isinstance(raw_options, dict) and phase == 4:
            field_options = raw_options.get(field_or_section, [])
            for opt in field_options:
                if isinstance(opt, TemplateOption) and opt.id == option_id:
                    return opt.label
            raise KeyError(f"Option {option_id} not found in phase {phase} field {field_or_section}")

        # For other phases, search through the list
        if isinstance(raw_options, list):
            for opt in raw_options:
                if isinstance(opt, TemplateOption) and opt.id == option_id:
                    return opt.label
            raise KeyError(f"Option {option_id} not found in phase {phase}")

        raise KeyError(f"No options found for phase {phase}")

    def get_options(self, phase: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all options for a given phase as dicts."""
        raw_options = self.options.get(phase, {})

        # Handle Layer 4 (structural forces) which has nested dict
        if isinstance(raw_options, dict) and phase == 4:
            result = {}
            for key, option_list in raw_options.items():
                result[key] = [opt.to_dict() if isinstance(opt, TemplateOption) else opt for opt in option_list]
            return result

        # Handle other phases which are lists
        if isinstance(raw_options, list):
            return {"options": [opt.to_dict() if isinstance(opt, TemplateOption) else opt for opt in raw_options]}

        return {}

    def get_constraints(self, phase: int) -> List[str]:
        """Get validation constraints for a phase."""
        constraints = {
            4: [
                "want_not_equal_change",
                "resistance_creates_dynamic",
                "stakes_align_with_consent",
            ],
            5: ["boundaries_explicit"],
            6: ["playfulness_present"],
            7: ["care_demonstrated"],
            8: ["power_balanced"],
            9: ["connection_deepened"],
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


class TenderSurrenderTemplate:
    """Tender Surrender template: safe vulnerability and willing release of control."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "vulnerability_journey",
        6: "trust_building",
        7: "release_rhythm",
        8: "emotional_tone",
        9: "transformation_culmination"
    }

    def __init__(self):
        self.core_id = "tender_surrender"
        self.primary_emotion = "safe_vulnerability"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            1: [
                TemplateOption(
                    id="tender_surrender",
                    label="Tender Surrender",
                    description="Safe vulnerability and willing release"
                )
            ],
            2: [
                TemplateOption(id="voluntary-release", label="Voluntary release of control"),
                TemplateOption(id="discovery-trust", label="Discovery through trusting"),
                TemplateOption(id="opening-journey", label="Journey of gradual opening"),
                TemplateOption(id="safe-falling", label="Safe falling into arms of partner"),
            ],
            3: [
                TemplateOption(id="intimate-dyad", label="Intimate dyad focus"),
                TemplateOption(id="expanding-trust", label="Expanding circle of trust"),
                TemplateOption(id="chosen-witnesses", label="Selected trusted witnesses"),
            ],
            4: {
                "want": [
                    TemplateOption(
                        id="want-release-control",
                        label="Release burden of decision-making",
                        description="Submissive seeks freedom through surrender"
                    ),
                    TemplateOption(
                        id="want-experience-pleasure",
                        label="Experience pleasure through vulnerability",
                        description="Discover joy in being cared for"
                    ),
                    TemplateOption(
                        id="want-be-seen",
                        label="Be fully seen and accepted",
                        description="Validation of true self through partner's eyes"
                    ),
                    TemplateOption(
                        id="want-trust-transformation",
                        label="Transform through trusted surrender",
                        description="Emotional growth via safe vulnerability"
                    ),
                ],
                "resistance": [
                    TemplateOption(
                        id="resistance-fear-vulnerability",
                        label="Fear of vulnerability and exposure",
                        description="Concern about being seen fully"
                    ),
                    TemplateOption(
                        id="resistance-doubt-worthiness",
                        label="Doubt about worthiness to receive",
                        description="Internal belief that submissive doesn't deserve care"
                    ),
                    TemplateOption(
                        id="resistance-past-trauma",
                        label="Past experiences of betrayal or harm",
                        description="Old wounds prevent trust"
                    ),
                    TemplateOption(
                        id="resistance-identity-fear",
                        label="Fear of losing identity in surrender",
                        description="Concern that submission means erasure"
                    ),
                ],
                "conflict": [
                    TemplateOption(
                        id="conflict-self-protection-vs-desire",
                        label="Self-protection vs. desire to trust",
                        description="Walls maintained for safety clash with longing"
                    ),
                    TemplateOption(
                        id="conflict-control-vs-release",
                        label="Maintaining control vs. letting go",
                        description="Habitual vigilance vs. willingness to be vulnerable"
                    ),
                    TemplateOption(
                        id="conflict-independence-vs-interdependence",
                        label="Independence vs. interdependence",
                        description="Solo survival vs. chosen dependence"
                    ),
                ],
                "stakes": [
                    TemplateOption(
                        id="stakes-emotional-walls",
                        label="Emotional walls and protective barriers",
                        description="Risk letting defenses down"
                    ),
                    TemplateOption(
                        id="stakes-identity-preservation",
                        label="Preservation of authentic self",
                        description="Must not lose essence through submission"
                    ),
                    TemplateOption(
                        id="stakes-sense-of-safety",
                        label="Fundamental sense of safety and security",
                        description="Trust broken could shatter more than before"
                    ),
                ],
                "change": [
                    TemplateOption(
                        id="change-defended-to-open",
                        label="From defended to open",
                        description="Walls gradually soften"
                    ),
                    TemplateOption(
                        id="change-doubtful-to-trusting",
                        label="From doubtful to trusting",
                        description="Belief in partner's care grows"
                    ),
                    TemplateOption(
                        id="change-fragmented-to-whole",
                        label="From fragmented to whole",
                        description="Integration of vulnerability as strength"
                    ),
                ],
            },
            5: [
                TemplateOption(id="journey-internal", label="Internal journey of opening"),
                TemplateOption(id="journey-relational", label="Relational unfolding together"),
                TemplateOption(id="journey-transformative", label="Transformative surrender process"),
            ],
            6: [
                TemplateOption(id="trust-demonstrated", label="Trust demonstrated through consistent care"),
                TemplateOption(id="trust-earned", label="Trust earned through patient presence"),
                TemplateOption(id="trust-reciprocal", label="Trust becomes reciprocal and mutual"),
            ],
            7: [
                TemplateOption(id="rhythm-gradual", label="Gradual building of surrender"),
                TemplateOption(id="rhythm-crescendo", label="Crescendo toward release"),
                TemplateOption(id="rhythm-settling", label="Settling into safe submission"),
            ],
            8: [
                TemplateOption(id="tone-tender", label="Tender and affectionate throughout"),
                TemplateOption(id="tone-safe", label="Safe and protective space"),
                TemplateOption(id="tone-liberating", label="Liberating freedom in vulnerability"),
            ],
            9: [
                TemplateOption(id="transformation-profound", label="Profound transformation achieved"),
                TemplateOption(id="transformation-healing", label="Healing through safe release"),
                TemplateOption(id="transformation-blissful", label="Blissful peace in surrender"),
            ],
        }

    def get_option_label(self, phase: int, field_or_section: str, option_id: str) -> str:
        """Get human-readable label for an option.

        Args:
            phase: Phase number
            field_or_section: Field name within that phase (e.g., "want", "resistance")
            option_id: The option's ID (e.g., "want-release-control")

        Returns:
            Label string (e.g., "Release burden of decision-making")

        Raises:
            KeyError: If the option_id is not found
        """
        raw_options = self.options.get(phase, {})

        # Handle Layer 4 (structural forces) which has nested dict
        if isinstance(raw_options, dict) and phase == 4:
            field_options = raw_options.get(field_or_section, [])
            for opt in field_options:
                if isinstance(opt, TemplateOption) and opt.id == option_id:
                    return opt.label
            raise KeyError(f"Option {option_id} not found in phase {phase} field {field_or_section}")

        # For other phases, search through the list
        if isinstance(raw_options, list):
            for opt in raw_options:
                if isinstance(opt, TemplateOption) and opt.id == option_id:
                    return opt.label
            raise KeyError(f"Option {option_id} not found in phase {phase}")

        raise KeyError(f"No options found for phase {phase}")

    def get_options(self, phase: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all options for a given phase as dicts."""
        raw_options = self.options.get(phase, {})

        # Handle Layer 4 (structural forces) which has nested dict
        if isinstance(raw_options, dict) and phase == 4:
            result = {}
            for key, option_list in raw_options.items():
                result[key] = [opt.to_dict() if isinstance(opt, TemplateOption) else opt for opt in option_list]
            return result

        # Handle other phases which are lists
        if isinstance(raw_options, list):
            return {"options": [opt.to_dict() if isinstance(opt, TemplateOption) else opt for opt in raw_options]}

        return {}

    def get_constraints(self, phase: int) -> List[str]:
        """Get validation constraints for a phase."""
        constraints = {
            4: [
                "want_not_equal_change",
                "resistance_blocks_trust",
                "stakes_require_vulnerability",
            ],
            5: ["journey_internal"],
            6: ["trust_earned"],
            7: ["rhythm_gradual"],
            8: ["tone_tender"],
            9: ["transformation_achieved"],
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


class RomanticAuthorityTemplate:
    """Romantic Authority template: cherished leadership and interdependent partnership."""

    phases = {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "leadership_style",
        6: "care_expression",
        7: "partnership_rhythm",
        8: "respect_dynamic",
        9: "interdependence_deepening"
    }

    def __init__(self):
        self.core_id = "romantic_authority"
        self.primary_emotion = "cherished_leadership"
        self._initialize_options()

    def _initialize_options(self):
        """Define all decision options for this template."""
        self.options = {
            1: [
                TemplateOption(
                    id="romantic_authority",
                    label="Romantic Authority",
                    description="Cherished leadership and interdependent partnership"
                )
            ],
            2: [
                TemplateOption(id="strong-protector", label="Strong protector and provider"),
                TemplateOption(id="confident-leader", label="Confident leadership with tenderness"),
                TemplateOption(id="caring-authority", label="Caring authority figure"),
                TemplateOption(id="romantic-direction", label="Romantic direction of shared life"),
            ],
            3: [
                TemplateOption(id="committed-pair", label="Committed intimate pair"),
                TemplateOption(id="family-unit", label="Partnership expanding to family"),
                TemplateOption(id="social-recognition", label="Socially recognized partnership"),
            ],
            4: {
                "want": [
                    TemplateOption(
                        id="want-provide-protect",
                        label="Provide for and protect beloved",
                        description="Leader seeks to care for partner"
                    ),
                    TemplateOption(
                        id="want-make-decisions",
                        label="Make decisions that serve both partners",
                        description="Exercise leadership for mutual good"
                    ),
                    TemplateOption(
                        id="want-lead-confidently",
                        label="Lead with confidence and purpose",
                        description="Demonstrate worthy stewardship"
                    ),
                    TemplateOption(
                        id="want-cherish-partner",
                        label="Cherish and celebrate the beloved",
                        description="Make partner feel valued and chosen"
                    ),
                ],
                "resistance": [
                    TemplateOption(
                        id="resistance-partner-independence",
                        label="Partner's independence and autonomy",
                        description="Submissive partner retains own will"
                    ),
                    TemplateOption(
                        id="resistance-prove-worthiness",
                        label="Need to prove worthiness of leadership",
                        description="Must earn the right to lead"
                    ),
                    TemplateOption(
                        id="resistance-competing-wills",
                        label="Competing wills about direction",
                        description="Partners don't always want same things"
                    ),
                    TemplateOption(
                        id="resistance-equality-tension",
                        label="Tension between equality and hierarchy",
                        description="Both partners believe in equal worth despite roles"
                    ),
                ],
                "conflict": [
                    TemplateOption(
                        id="conflict-leadership-vs-partnership",
                        label="Leadership vs. partnership equality",
                        description="Balancing hierarchy with mutual respect"
                    ),
                    TemplateOption(
                        id="conflict-direction-vs-choice",
                        label="Leader's direction vs. partner's choice",
                        description="Dominance must honor partner agency"
                    ),
                    TemplateOption(
                        id="conflict-authority-vs-care",
                        label="Authority structures vs. caring connection",
                        description="Power must serve love, not ego"
                    ),
                ],
                "stakes": [
                    TemplateOption(
                        id="stakes-relationship-balance",
                        label="Relationship balance and health",
                        description="Partnership survives or crumbles"
                    ),
                    TemplateOption(
                        id="stakes-both-fulfillment",
                        label="Fulfillment for both partners",
                        description="Role structure must serve both"
                    ),
                    TemplateOption(
                        id="stakes-mutual-respect",
                        label="Maintenance of mutual respect",
                        description="Authority cannot breed resentment"
                    ),
                ],
                "change": [
                    TemplateOption(
                        id="change-uncertain-to-confident",
                        label="From uncertain to confident in roles",
                        description="Clear understanding of partnership structure"
                    ),
                    TemplateOption(
                        id="change-separate-to-interdependent",
                        label="From separate to interdependent",
                        description="United while maintaining individuality"
                    ),
                    TemplateOption(
                        id="change-tested-to-secure",
                        label="From tested to secure in love",
                        description="Authority proven worthy of trust"
                    ),
                ],
            },
            5: [
                TemplateOption(id="leadership-protective", label="Protective leadership style"),
                TemplateOption(id="leadership-decisive", label="Decisive and confident direction"),
                TemplateOption(id="leadership-nurturing", label="Nurturing leadership approach"),
            ],
            6: [
                TemplateOption(id="care-constant", label="Constant demonstration of care"),
                TemplateOption(id="care-protective", label="Protective and attentive care"),
                TemplateOption(id="care-celebratory", label="Celebratory expression of love"),
            ],
            7: [
                TemplateOption(id="rhythm-steady", label="Steady rhythm of partnership"),
                TemplateOption(id="rhythm-deepening", label="Deepening partnership over time"),
                TemplateOption(id="rhythm-graceful", label="Graceful dance of leadership and trust"),
            ],
            8: [
                TemplateOption(id="respect-earned", label="Respect earned through demonstrated care"),
                TemplateOption(id="respect-reciprocal", label="Respect flowing both directions"),
                TemplateOption(id="respect-foundational", label="Respect foundational to authority"),
            ],
            9: [
                TemplateOption(id="interdependence-secure", label="Secure interdependence achieved"),
                TemplateOption(id="interdependence-romantic", label="Romantic interdependence"),
                TemplateOption(id="interdependence-blessed", label="Blessed union through trust"),
            ],
        }

    def get_option_label(self, phase: int, field_or_section: str, option_id: str) -> str:
        """Get human-readable label for an option.

        Args:
            phase: Phase number
            field_or_section: Field name within that phase (e.g., "want", "resistance")
            option_id: The option's ID (e.g., "want-provide-protect")

        Returns:
            Label string (e.g., "Provide for and protect beloved")

        Raises:
            KeyError: If the option_id is not found
        """
        raw_options = self.options.get(phase, {})

        # Handle Layer 4 (structural forces) which has nested dict
        if isinstance(raw_options, dict) and phase == 4:
            field_options = raw_options.get(field_or_section, [])
            for opt in field_options:
                if isinstance(opt, TemplateOption) and opt.id == option_id:
                    return opt.label
            raise KeyError(f"Option {option_id} not found in phase {phase} field {field_or_section}")

        # For other phases, search through the list
        if isinstance(raw_options, list):
            for opt in raw_options:
                if isinstance(opt, TemplateOption) and opt.id == option_id:
                    return opt.label
            raise KeyError(f"Option {option_id} not found in phase {phase}")

        raise KeyError(f"No options found for phase {phase}")

    def get_options(self, phase: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all options for a given phase as dicts."""
        raw_options = self.options.get(phase, {})

        # Handle Layer 4 (structural forces) which has nested dict
        if isinstance(raw_options, dict) and phase == 4:
            result = {}
            for key, option_list in raw_options.items():
                result[key] = [opt.to_dict() if isinstance(opt, TemplateOption) else opt for opt in option_list]
            return result

        # Handle other phases which are lists
        if isinstance(raw_options, list):
            return {"options": [opt.to_dict() if isinstance(opt, TemplateOption) else opt for opt in raw_options]}

        return {}

    def get_constraints(self, phase: int) -> List[str]:
        """Get validation constraints for a phase."""
        constraints = {
            4: [
                "want_not_equal_change",
                "resistance_respects_autonomy",
                "stakes_serve_both_partners",
            ],
            5: ["leadership_caring"],
            6: ["care_constant"],
            7: ["rhythm_steady"],
            8: ["respect_bidirectional"],
            9: ["interdependence_secure"],
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


def get_template(core_id: str):
    """Factory function to get the right template."""
    templates = {
        "sensual_dominance": SensualDominanceTemplate,
        "tender_surrender": TenderSurrenderTemplate,
        "romantic_authority": RomanticAuthorityTemplate,
    }
    template_class = templates.get(core_id)
    if not template_class:
        raise ValueError(f"Unknown core: {core_id}")
    return template_class()
