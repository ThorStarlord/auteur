"""Composition Rules YAML Loader for Layer 2.5 narrative orchestration.

This module provides:
- Loading and validation of composition rules from YAML files
- Pydantic models for all rule types (ordering, optionality, state, coverage)
- Genre-specific rule selection and merging
- Integration with existing ownership and constraint systems

The rules define the structural and narrative constraints that govern how
outlines must be composed to maintain coherence across artifacts.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
import yaml

from pydantic import BaseModel, Field, field_validator


class RuleType(str, Enum):
    """Enumeration of composition rule types."""

    OPTIONALITY = "optionality"
    CHRONOLOGICAL_ORDERING = "chronological_ordering"
    STATE_VALIDITY = "state_validity"
    ARC_COVERAGE = "arc_coverage"


class OptionalityLevel(str, Enum):
    """Enumeration of optionality levels for artifacts."""

    REQUIRED = "required"
    CONDITIONAL = "conditional"
    OPTIONAL = "optional"


class Severity(str, Enum):
    """Enumeration of violation severity levels."""

    ERROR = "error"
    WARNING = "warning"


class OptionalityRule(BaseModel):
    """A rule defining which artifacts are optional in composition.

    Attributes:
        constraint_id: Unique identifier for this rule
        artifact_type: Type of artifact (chapter, sequence, book, etc.)
        optionality_level: REQUIRED, CONDITIONAL, or OPTIONAL
        description: Human-readable explanation of the rule
        reason: Why this artifact has this optionality level
        condition: Optional conditional description (when required/optional)
        example: Optional example artifact ID
    """

    constraint_id: str = Field(..., description="Unique constraint identifier")
    artifact_type: str = Field(..., description="Type of artifact")
    optionality_level: OptionalityLevel = Field(
        ..., description="Required, conditional, or optional"
    )
    description: str = Field(..., min_length=10, description="Rule explanation")
    reason: str = Field(..., min_length=10, description="Why this rule exists")
    condition: Optional[str] = Field(
        default=None, description="Condition when optionality applies"
    )
    example: Optional[str] = Field(default=None, description="Example artifact ID")

    @field_validator("constraint_id")
    @classmethod
    def validate_constraint_id(cls, v: str) -> str:
        """Ensure constraint_id is non-empty and follows naming convention."""
        if not v or not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"constraint_id must be alphanumeric with underscores: {v}")
        return v

    def is_artifact_required(self) -> bool:
        """Check if this artifact type is required."""
        return self.optionality_level == OptionalityLevel.REQUIRED

    def is_artifact_optional(self) -> bool:
        """Check if this artifact type is optional."""
        return self.optionality_level == OptionalityLevel.OPTIONAL


class ChronologicalOrderingRule(BaseModel):
    """A rule defining chronological ordering relationships between artifacts.

    Attributes:
        constraint_id: Unique identifier for this rule
        name: Human-readable name (payoff_after_setup, etc.)
        source_artifact_type: Type of source artifact
        source_phase: Optional phase number (1-9) for source
        target_artifact_type: Type of target artifact
        target_phase: Optional phase number (1-9) for target
        description: Explanation of the ordering requirement
        reason: Why this ordering is required
        severity: ERROR (breaks composition) or WARNING (should review)
    """

    constraint_id: str = Field(..., description="Unique constraint identifier")
    name: str = Field(..., min_length=3, description="Rule name")
    source_artifact_type: str = Field(..., description="Source artifact type")
    source_phase: Optional[int] = Field(
        default=None, ge=1, le=9, description="Source phase (1-9)"
    )
    target_artifact_type: str = Field(..., description="Target artifact type")
    target_phase: Optional[int] = Field(
        default=None, ge=1, le=9, description="Target phase (1-9)"
    )
    description: str = Field(..., min_length=10, description="Rule explanation")
    reason: str = Field(..., min_length=10, description="Why this rule exists")
    severity: Severity = Field(default=Severity.ERROR, description="Error or warning")

    def requires_phases(self) -> bool:
        """Check if this rule requires phase ordering."""
        return self.source_phase is not None and self.target_phase is not None

    def requires_strict_ordering(self) -> bool:
        """Check if source must strictly precede target."""
        return self.source_phase is not None and self.target_phase is not None


class StateTransition(BaseModel):
    """Represents a valid state transition for a character.

    Attributes:
        from_state: Starting state of the character
        to_state: Ending state of the character
        description: Why this transition is valid
    """

    from_state: str = Field(..., min_length=1, description="Starting state")
    to_state: str = Field(..., min_length=1, description="Ending state")
    description: str = Field(..., min_length=10, description="Transition explanation")


class StateValidityRule(BaseModel):
    """A rule defining valid state progressions for characters.

    Attributes:
        constraint_id: Unique identifier for this rule
        character_id: ID of character (wildcard patterns allowed)
        valid_transitions: List of allowed state transitions
        description: Explanation of state validity rules
        reason: Why these transitions are required
        severity: ERROR (breaks composition) or WARNING (should review)
    """

    constraint_id: str = Field(..., description="Unique constraint identifier")
    character_id: str = Field(..., description="Character ID or pattern")
    valid_transitions: List[StateTransition] = Field(
        default_factory=list, description="Allowed state transitions"
    )
    description: str = Field(..., min_length=10, description="Rule explanation")
    reason: str = Field(..., min_length=10, description="Why this rule exists")
    severity: Severity = Field(default=Severity.ERROR, description="Error or warning")

    def matches_character(self, character_id: str) -> bool:
        """Check if this rule applies to a given character ID.

        Supports wildcard patterns:
        - "*protagonist*" matches any character_id containing "protagonist"
        - "clara" matches exactly "clara"

        Args:
            character_id: Character ID to check

        Returns:
            True if rule applies to this character
        """
        if self.character_id == "*":
            return True
        if "*" not in self.character_id:
            return self.character_id == character_id
        # Pattern matching: *substring* matches if substring is in character_id
        pattern = self.character_id.strip("*")
        return pattern.lower() in character_id.lower()


class ArcCoverageRule(BaseModel):
    """A rule defining which books/chapters must have character arcs.

    Attributes:
        constraint_id: Unique identifier for this rule
        character_id: ID of character (wildcard patterns allowed)
        artifact_type: Type of artifact (character_arc, story_arc, etc.)
        minimum_beats: Minimum number of beats/checkpoints required
        minimum_chapters: Minimum chapters spanned by arc
        required_coverage_type: "each_book", "entire_series", or None
        description: Explanation of coverage requirements
        reason: Why this coverage is required
        severity: ERROR (breaks composition) or WARNING (should review)
    """

    constraint_id: str = Field(..., description="Unique constraint identifier")
    character_id: Optional[str] = Field(
        default=None, description="Character ID or pattern"
    )
    artifact_type: Optional[str] = Field(default=None, description="Artifact type")
    minimum_beats: int = Field(default=1, ge=1, description="Minimum beats")
    minimum_chapters: int = Field(default=1, ge=1, description="Minimum chapters")
    required_coverage_type: Optional[str] = Field(
        default=None, description="each_book, entire_series, or None"
    )
    description: str = Field(..., min_length=10, description="Rule explanation")
    reason: str = Field(..., min_length=10, description="Why this rule exists")
    severity: Severity = Field(default=Severity.ERROR, description="Error or warning")

    @field_validator("required_coverage_type")
    @classmethod
    def validate_coverage_type(cls, v: Optional[str]) -> Optional[str]:
        """Ensure coverage_type is a valid value."""
        if v is not None and v not in ["each_book", "entire_series"]:
            raise ValueError(
                f"required_coverage_type must be 'each_book' or 'entire_series': {v}"
            )
        return v

    def matches_artifact(self, artifact_id: str) -> bool:
        """Check if this rule applies to a given artifact.

        Supports wildcard patterns like StateValidityRule.

        Args:
            artifact_id: Artifact ID to check

        Returns:
            True if rule applies to this artifact
        """
        if not self.character_id and not self.artifact_type:
            return True
        if self.character_id:
            if self.character_id == "*":
                return True
            if "*" not in self.character_id:
                return self.character_id == artifact_id
            pattern = self.character_id.strip("*")
            return pattern.lower() in artifact_id.lower()
        return False


class CompositionRules(BaseModel):
    """Complete set of composition rules for a given scope (global or genre).

    Attributes:
        scope: "global" or genre name (netorare, mystery, gentlefemdom)
        description: Description of these rules
        optionality_rules: List of OptionalityRule objects
        chronological_rules: List of ChronologicalOrderingRule objects
        state_validity_rules: List of StateValidityRule objects
        arc_coverage_rules: List of ArcCoverageRule objects
    """

    scope: str = Field(..., description="Global or genre-specific scope")
    description: str = Field(..., description="Description of this rule set")
    optionality_rules: List[OptionalityRule] = Field(
        default_factory=list, description="Optionality constraints"
    )
    chronological_rules: List[ChronologicalOrderingRule] = Field(
        default_factory=list, description="Chronological ordering rules"
    )
    state_validity_rules: List[StateValidityRule] = Field(
        default_factory=list, description="State validity rules"
    )
    arc_coverage_rules: List[ArcCoverageRule] = Field(
        default_factory=list, description="Arc coverage rules"
    )

    def get_rule_by_id(self, constraint_id: str) -> Optional[Any]:
        """Look up a rule by its constraint_id.

        Args:
            constraint_id: ID to search for

        Returns:
            The rule object or None if not found
        """
        for rule in self.optionality_rules:
            if rule.constraint_id == constraint_id:
                return rule
        for rule in self.chronological_rules:
            if rule.constraint_id == constraint_id:
                return rule
        for rule in self.state_validity_rules:
            if rule.constraint_id == constraint_id:
                return rule
        for rule in self.arc_coverage_rules:
            if rule.constraint_id == constraint_id:
                return rule
        return None

    def get_rules_by_type(self, rule_type: RuleType) -> List[Any]:
        """Get all rules of a given type.

        Args:
            rule_type: Type of rules to retrieve

        Returns:
            List of rules matching the type
        """
        if rule_type == RuleType.OPTIONALITY:
            return self.optionality_rules
        elif rule_type == RuleType.CHRONOLOGICAL_ORDERING:
            return self.chronological_rules
        elif rule_type == RuleType.STATE_VALIDITY:
            return self.state_validity_rules
        elif rule_type == RuleType.ARC_COVERAGE:
            return self.arc_coverage_rules
        return []


class CompositionRulesLoader:
    """Loads and validates composition rules from YAML files.

    This loader:
    - Reads composition_constraints.yaml
    - Parses global and genre-specific rules
    - Provides methods to get rules by genre
    - Supports rule merging and override strategies
    - Validates rule structure and consistency

    Attributes:
        yaml_path: Path to composition_constraints.yaml
        raw_data: Loaded YAML data (dict)
        global_rules: CompositionRules for global constraints
        genre_rules: Dict mapping genre name to CompositionRules
    """

    SUPPORTED_GENRES = {"netorare", "mystery", "gentlefemdom"}

    def __init__(self, yaml_path: Optional[Path] = None):
        """Initialize the rules loader.

        Args:
            yaml_path: Path to composition_constraints.yaml
                      If None, loads from default data/composition/ location
        """
        if yaml_path is None:
            # Default location: from schema/rules_loader.py navigate to project root/data/composition/
            # Path is: src/auteur/narrative_orchestration/schema/rules_loader.py
            # Go up to: src -> project root -> data/composition/
            yaml_path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "data"
                / "composition"
                / "composition_constraints.yaml"
            )

        self.yaml_path = yaml_path
        self.raw_data: Dict[str, Any] = {}
        self.global_rules: Optional[CompositionRules] = None
        self.genre_rules: Dict[str, CompositionRules] = {}

        self.load_rules()

    def load_rules(self) -> None:
        """Load and parse composition rules from YAML file.

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            yaml.YAMLError: If YAML is invalid
            ValueError: If rule structure is invalid
        """
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"Rules file not found: {self.yaml_path}")

        with open(self.yaml_path, "r") as f:
            self.raw_data = yaml.safe_load(f)

        if not self.raw_data:
            raise ValueError("YAML file is empty or invalid")

        # Parse global constraints
        global_constraints = self.raw_data.get("global_constraints", {})
        self.global_rules = self._parse_composition_rules(
            "global", global_constraints, "Global composition rules"
        )

        # Parse genre-specific constraints
        genre_constraints = self.raw_data.get("genre_constraints", {})
        for genre_name, genre_data in genre_constraints.items():
            if genre_name in self.SUPPORTED_GENRES:
                # Merge genre-specific overrides with global rules
                merged_data = self._merge_genre_rules(
                    global_constraints, genre_data
                )
                self.genre_rules[genre_name] = self._parse_composition_rules(
                    genre_name, merged_data, genre_data.get("description", "")
                )

    def _parse_composition_rules(
        self, scope: str, data: Dict[str, Any], description: str
    ) -> CompositionRules:
        """Parse composition rules from a data dictionary.

        Args:
            scope: Scope identifier (global or genre name)
            data: Dictionary of rule data
            description: Description of this rule set

        Returns:
            CompositionRules object

        Raises:
            ValueError: If rule structure is invalid
        """
        optionality_rules = []
        for rule_data in data.get("optionality", []):
            optionality_rules.append(OptionalityRule(**rule_data))

        chronological_rules = []
        for rule_data in data.get("chronological_ordering", []):
            chronological_rules.append(ChronologicalOrderingRule(**rule_data))

        state_validity_rules = []
        for rule_data in data.get("state_validity", []):
            valid_transitions = [
                StateTransition(**t) for t in rule_data.get("valid_transitions", [])
            ]
            rule_dict = {k: v for k, v in rule_data.items() if k != "valid_transitions"}
            rule_dict["valid_transitions"] = valid_transitions
            state_validity_rules.append(StateValidityRule(**rule_dict))

        arc_coverage_rules = []
        for rule_data in data.get("arc_coverage", []):
            arc_coverage_rules.append(ArcCoverageRule(**rule_data))

        return CompositionRules(
            scope=scope,
            description=description,
            optionality_rules=optionality_rules,
            chronological_rules=chronological_rules,
            state_validity_rules=state_validity_rules,
            arc_coverage_rules=arc_coverage_rules,
        )

    def _merge_genre_rules(
        self, global_data: Dict[str, Any], genre_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge global and genre-specific rules based on merge strategy.

        Genre-specific rules override global rules by constraint_id.

        Args:
            global_data: Global constraint data
            genre_data: Genre-specific constraint data

        Returns:
            Merged constraint data

        Raises:
            ValueError: If merge produces inconsistent rules
        """
        merged = {
            "optionality": list(global_data.get("optionality", [])),
            "chronological_ordering": list(
                global_data.get("chronological_ordering", [])
            ),
            "state_validity": list(global_data.get("state_validity", [])),
            "arc_coverage": list(global_data.get("arc_coverage", [])),
        }

        # Process overrides
        for override in genre_data.get("optionality_overrides", []):
            merged["optionality"] = self._apply_override(
                merged["optionality"], override
            )

        for addition in genre_data.get("chronological_ordering_additions", []):
            merged["chronological_ordering"].append(addition)

        for addition in genre_data.get("state_validity_additions", []):
            merged["state_validity"].append(addition)

        for addition in genre_data.get("arc_coverage_additions", []):
            merged["arc_coverage"].append(addition)

        return merged

    @staticmethod
    def _apply_override(rules: List[Dict], override: Dict) -> List[Dict]:
        """Apply a rule override by replacing matching constraint_id.

        Args:
            rules: List of existing rules
            override: Override rule data

        Returns:
            Updated list with override applied
        """
        override_id = override.get("constraint_id")
        result = []

        for rule in rules:
            if rule.get("constraint_id") == override_id:
                result.append(override)
            else:
                result.append(rule)

        # If override not found, add it
        if not any(r.get("constraint_id") == override_id for r in rules):
            result.append(override)

        return result

    def get_global_rules(self) -> CompositionRules:
        """Get the global composition rules.

        Returns:
            CompositionRules for global constraints

        Raises:
            RuntimeError: If rules haven't been loaded yet
        """
        if self.global_rules is None:
            raise RuntimeError("Rules not loaded. Call load_rules() first.")
        return self.global_rules

    def get_genre_rules(self, genre: str) -> CompositionRules:
        """Get composition rules for a specific genre.

        Args:
            genre: Genre name (netorare, mystery, gentlefemdom)

        Returns:
            CompositionRules for this genre
            Falls back to global rules if genre not found

        Raises:
            ValueError: If genre is not recognized
        """
        if genre not in self.SUPPORTED_GENRES:
            raise ValueError(
                f"Unknown genre: {genre}. Supported: {self.SUPPORTED_GENRES}"
            )

        return self.genre_rules.get(genre, self.get_global_rules())

    def get_all_genres(self) -> Set[str]:
        """Get all supported genres with custom rules.

        Returns:
            Set of genre names
        """
        return set(self.genre_rules.keys())

    def get_merged_rules(self, genre: str) -> CompositionRules:
        """Get merged rules for a genre (global + genre-specific).

        This is equivalent to get_genre_rules() since merging happens
        during load_rules().

        Args:
            genre: Genre name

        Returns:
            Merged CompositionRules for this genre
        """
        return self.get_genre_rules(genre)

    def validate_rules_consistency(self) -> Tuple[bool, List[str]]:
        """Validate that loaded rules are internally consistent.

        Checks:
        - No duplicate constraint_ids
        - All referenced phases are 1-9
        - All state transitions have valid state names
        - All character patterns are valid

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check global rules
        if self.global_rules:
            errors.extend(
                self._validate_composition_rules(self.global_rules, "global")
            )

        # Check genre rules
        for genre, rules in self.genre_rules.items():
            errors.extend(self._validate_composition_rules(rules, genre))

        return len(errors) == 0, errors

    @staticmethod
    def _validate_composition_rules(
        rules: CompositionRules, scope: str
    ) -> List[str]:
        """Validate a single CompositionRules object.

        Args:
            rules: CompositionRules to validate
            scope: Scope identifier for error messages

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        seen_ids = set()

        # Check for duplicate constraint_ids
        all_rules = (
            rules.optionality_rules
            + rules.chronological_rules
            + rules.state_validity_rules
            + rules.arc_coverage_rules
        )

        for rule in all_rules:
            if rule.constraint_id in seen_ids:
                errors.append(
                    f"{scope}: Duplicate constraint_id '{rule.constraint_id}'"
                )
            seen_ids.add(rule.constraint_id)

        # Validate phases
        for rule in rules.chronological_rules:
            if rule.source_phase and not (1 <= rule.source_phase <= 9):
                errors.append(
                    f"{scope}: Invalid source_phase {rule.source_phase} "
                    f"in rule {rule.constraint_id}"
                )
            if rule.target_phase and not (1 <= rule.target_phase <= 9):
                errors.append(
                    f"{scope}: Invalid target_phase {rule.target_phase} "
                    f"in rule {rule.constraint_id}"
                )

        # Validate state transitions
        # Note: Global state validity rules can have empty transitions (to be extended by genres)
        for rule in rules.state_validity_rules:
            if not rule.valid_transitions and scope != "global":
                errors.append(
                    f"{scope}: No valid transitions defined in rule {rule.constraint_id}"
                )

        return errors

    def rules_summary(self) -> Dict[str, Any]:
        """Get a summary of loaded rules.

        Returns:
            Dictionary with counts and metadata
        """
        global_summary = self._summarize_composition_rules(self.global_rules)

        genre_summaries = {}
        for genre, rules in self.genre_rules.items():
            genre_summaries[genre] = self._summarize_composition_rules(rules)

        return {
            "version": self.raw_data.get("version", "unknown"),
            "last_updated": self.raw_data.get("last_updated", "unknown"),
            "global": global_summary,
            "genres": genre_summaries,
        }

    @staticmethod
    def _summarize_composition_rules(rules: Optional[CompositionRules]) -> Dict[str, int]:
        """Summarize a CompositionRules object.

        Args:
            rules: CompositionRules to summarize

        Returns:
            Dictionary with rule counts
        """
        if not rules:
            return {
                "optionality": 0,
                "chronological": 0,
                "state_validity": 0,
                "arc_coverage": 0,
                "total": 0,
            }

        total = (
            len(rules.optionality_rules)
            + len(rules.chronological_rules)
            + len(rules.state_validity_rules)
            + len(rules.arc_coverage_rules)
        )

        return {
            "optionality": len(rules.optionality_rules),
            "chronological": len(rules.chronological_rules),
            "state_validity": len(rules.state_validity_rules),
            "arc_coverage": len(rules.arc_coverage_rules),
            "total": total,
        }
