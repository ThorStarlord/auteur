"""Composition constraints for Layer 2.5 narrative orchestration.

This module defines constraint types that govern how artifacts in a narrative
composition must relate to each other. Constraints enforce domain rules about
optionality, chronological ordering, state validity, and arc coverage.

Constraint Types:
1. Optionality: Which artifacts are optional (e.g., sequences can be omitted)
2. Chronological Ordering: Payoff after setup, crisis before resolution
3. State Validity: Character state progression must be consistent
4. Arc Coverage: Which books/chapters must have character arcs
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field, field_validator


class ArtifactType(str, Enum):
    """Enumeration of artifact types in the narrative structure."""

    SERIES = "series"
    BOOK = "book"
    SEQUENCE = "sequence"
    CHAPTER = "chapter"
    CHARACTER_ARC = "character_arc"
    STORY_ARC = "story_arc"


class OptionalityLevel(str, Enum):
    """Enumeration of optionality levels for artifacts."""

    REQUIRED = "required"
    CONDITIONAL = "conditional"
    OPTIONAL = "optional"


class ConstraintViolation(BaseModel):
    """Represents a single constraint violation in a composition.

    Attributes:
        constraint_id: Unique identifier for the constraint
        constraint_type: Type of constraint (e.g., 'chronological_ordering')
        artifact_id: ID of the artifact violating the constraint
        message: Human-readable description of the violation
        severity: 'error' (breaks composition) or 'warning' (should be reviewed)
    """

    constraint_id: str
    constraint_type: str
    artifact_id: str
    message: str
    severity: str = Field(default="error", pattern="^(error|warning)$")


class ConstraintEvaluation(BaseModel):
    """Result of evaluating a single constraint against artifacts.

    Attributes:
        constraint_id: Unique identifier for the constraint
        is_satisfied: Whether the constraint is satisfied
        violations: List of ConstraintViolation objects if not satisfied
    """

    constraint_id: str
    is_satisfied: bool
    violations: List[ConstraintViolation] = Field(default_factory=list)


class OptionalityConstraint(BaseModel):
    """Constraint defining which artifacts are optional in composition.

    Attributes:
        constraint_id: Unique identifier for this constraint
        artifact_type: Type of artifact (e.g., SEQUENCE, CHAPTER)
        optionality_level: REQUIRED, CONDITIONAL, or OPTIONAL
        condition: Optional description of when this artifact is required
        example: Example artifact that follows this constraint
    """

    constraint_id: str
    artifact_type: ArtifactType
    optionality_level: OptionalityLevel
    condition: Optional[str] = None
    example: Optional[str] = None

    def evaluate(self, artifacts: List[Dict]) -> ConstraintEvaluation:
        """Evaluate this constraint against a list of artifacts.

        Args:
            artifacts: List of artifact dictionaries with 'type' and 'id' keys

        Returns:
            ConstraintEvaluation indicating if constraint is satisfied
        """
        violations = []
        relevant_artifacts = [a for a in artifacts if a.get("type") == self.artifact_type.value]

        if self.optionality_level == OptionalityLevel.REQUIRED:
            # Required artifacts must have at least one instance
            if not relevant_artifacts:
                violations.append(
                    ConstraintViolation(
                        constraint_id=self.constraint_id,
                        constraint_type="optionality",
                        artifact_id="",
                        message=f"Required artifact type {self.artifact_type.value} is missing",
                        severity="error",
                    )
                )

        return ConstraintEvaluation(
            constraint_id=self.constraint_id,
            is_satisfied=len(violations) == 0,
            violations=violations,
        )


class ChronologicalOrderingConstraint(BaseModel):
    """Constraint defining chronological ordering relationships between artifacts.

    Attributes:
        constraint_id: Unique identifier for this constraint
        name: Human-readable name (e.g., "payoff_after_setup")
        source_artifact: ID of source artifact (must occur before target)
        source_phase: Optional phase number for source (1-9)
        target_artifact: ID of target artifact (must occur after source)
        target_phase: Optional phase number for target (1-9)
        description: Explanation of the ordering requirement
    """

    constraint_id: str
    name: str
    source_artifact: str
    source_phase: Optional[int] = None
    target_artifact: str
    target_phase: Optional[int] = None
    description: str

    @field_validator("source_phase", "target_phase")
    @classmethod
    def validate_phase(cls, v):
        """Validate phase is in range 1-9."""
        if v is not None and not (1 <= v <= 9):
            raise ValueError(f"phase must be between 1 and 9, got {v}")
        return v

    def evaluate(
        self,
        artifacts: Dict[str, Dict],
        artifact_ordering: Dict[str, int],
    ) -> ConstraintEvaluation:
        """Evaluate this constraint against ordered artifacts.

        Args:
            artifacts: Dictionary mapping artifact_id to artifact data
            artifact_ordering: Dictionary mapping artifact_id to position/order

        Returns:
            ConstraintEvaluation indicating if ordering is valid
        """
        violations = []

        # Check if artifacts exist
        if self.source_artifact not in artifacts:
            violations.append(
                ConstraintViolation(
                    constraint_id=self.constraint_id,
                    constraint_type="chronological_ordering",
                    artifact_id=self.source_artifact,
                    message=f"Source artifact {self.source_artifact} not found",
                    severity="error",
                )
            )
            return ConstraintEvaluation(
                constraint_id=self.constraint_id,
                is_satisfied=False,
                violations=violations,
            )

        if self.target_artifact not in artifacts:
            violations.append(
                ConstraintViolation(
                    constraint_id=self.constraint_id,
                    constraint_type="chronological_ordering",
                    artifact_id=self.target_artifact,
                    message=f"Target artifact {self.target_artifact} not found",
                    severity="error",
                )
            )
            return ConstraintEvaluation(
                constraint_id=self.constraint_id,
                is_satisfied=False,
                violations=violations,
            )

        # Check ordering
        if (
            self.source_artifact in artifact_ordering
            and self.target_artifact in artifact_ordering
        ):
            source_order = artifact_ordering[self.source_artifact]
            target_order = artifact_ordering[self.target_artifact]

            # If phases are specified, check phase ordering
            if self.source_phase is not None and self.target_phase is not None:
                source_phase = artifacts[self.source_artifact].get("phase", self.source_phase)
                target_phase = artifacts[self.target_artifact].get("phase", self.target_phase)

                if source_phase >= target_phase:
                    violations.append(
                        ConstraintViolation(
                            constraint_id=self.constraint_id,
                            constraint_type="chronological_ordering",
                            artifact_id=self.source_artifact,
                            message=(
                                f"Chronological violation: {self.source_artifact} "
                                f"(phase {source_phase}) must occur before {self.target_artifact} "
                                f"(phase {target_phase}). {self.description}"
                            ),
                            severity="error",
                        )
                    )
            else:
                # Check basic ordering
                if source_order >= target_order:
                    violations.append(
                        ConstraintViolation(
                            constraint_id=self.constraint_id,
                            constraint_type="chronological_ordering",
                            artifact_id=self.source_artifact,
                            message=(
                                f"Chronological violation: {self.source_artifact} "
                                f"must occur before {self.target_artifact}. {self.description}"
                            ),
                            severity="error",
                        )
                    )

        return ConstraintEvaluation(
            constraint_id=self.constraint_id,
            is_satisfied=len(violations) == 0,
            violations=violations,
        )


class StateTransition(BaseModel):
    """Represents a valid state transition for a character.

    Attributes:
        from_state: Starting state of the character
        to_state: Ending state of the character
        description: Why this transition is valid
    """

    from_state: str
    to_state: str
    description: str


class StateValidityConstraint(BaseModel):
    """Constraint defining valid state progressions for characters.

    Attributes:
        constraint_id: Unique identifier for this constraint
        character_id: ID of the character
        valid_transitions: List of valid state transitions
        genre: Genre for which this constraint applies (optional)
        description: Explanation of state validity rules
    """

    constraint_id: str
    character_id: str
    valid_transitions: List[StateTransition] = Field(default_factory=list)
    genre: Optional[str] = None
    description: str

    def evaluate(self, character_states: Dict[str, List[str]]) -> ConstraintEvaluation:
        """Evaluate this constraint against character state progressions.

        Args:
            character_states: Dictionary mapping character_id to list of states in order

        Returns:
            ConstraintEvaluation indicating if state progressions are valid
        """
        violations = []

        if self.character_id not in character_states:
            return ConstraintEvaluation(
                constraint_id=self.constraint_id,
                is_satisfied=True,
                violations=[],
            )

        states = character_states[self.character_id]
        if len(states) < 2:
            # Single state or empty is always valid
            return ConstraintEvaluation(
                constraint_id=self.constraint_id,
                is_satisfied=True,
                violations=[],
            )

        # Check each transition
        for i in range(len(states) - 1):
            from_state = states[i]
            to_state = states[i + 1]

            # Check if this transition is valid
            valid = any(
                t.from_state == from_state and t.to_state == to_state
                for t in self.valid_transitions
            )

            if not valid:
                violations.append(
                    ConstraintViolation(
                        constraint_id=self.constraint_id,
                        constraint_type="state_validity",
                        artifact_id=self.character_id,
                        message=(
                            f"Invalid state transition for {self.character_id}: "
                            f"{from_state} → {to_state} is not allowed. {self.description}"
                        ),
                        severity="error",
                    )
                )

        return ConstraintEvaluation(
            constraint_id=self.constraint_id,
            is_satisfied=len(violations) == 0,
            violations=violations,
        )


class ArcCoverageConstraint(BaseModel):
    """Constraint defining which books/chapters must have character arcs.

    Attributes:
        constraint_id: Unique identifier for this constraint
        character_id: ID of the character
        required_coverage: Set of book/chapter IDs where arc must have beats
        minimum_beats: Minimum number of turning points required
        genre: Genre for which this constraint applies (optional)
        description: Explanation of arc coverage requirements
    """

    constraint_id: str
    character_id: str
    required_coverage: Set[str] = Field(default_factory=set)
    minimum_beats: int = Field(default=1, ge=1)
    genre: Optional[str] = None
    description: str

    def evaluate(
        self, character_arcs: Dict[str, Dict]
    ) -> ConstraintEvaluation:
        """Evaluate this constraint against character arc definitions.

        Args:
            character_arcs: Dictionary mapping character_id to arc data with 'beats' and 'chapters'

        Returns:
            ConstraintEvaluation indicating if arc coverage is sufficient
        """
        violations = []

        if self.character_id not in character_arcs:
            violations.append(
                ConstraintViolation(
                    constraint_id=self.constraint_id,
                    constraint_type="arc_coverage",
                    artifact_id=self.character_id,
                    message=f"Character arc for {self.character_id} not found",
                    severity="error",
                )
            )
            return ConstraintEvaluation(
                constraint_id=self.constraint_id,
                is_satisfied=False,
                violations=violations,
            )

        arc = character_arcs[self.character_id]
        beats = arc.get("beats", [])
        beat_chapters = arc.get("chapters", [])

        # Check minimum beats
        if len(beats) < self.minimum_beats:
            violations.append(
                ConstraintViolation(
                    constraint_id=self.constraint_id,
                    constraint_type="arc_coverage",
                    artifact_id=self.character_id,
                    message=(
                        f"Character arc for {self.character_id} has only {len(beats)} beats, "
                        f"but minimum {self.minimum_beats} required. {self.description}"
                    ),
                    severity="error",
                )
            )

        # Check coverage in required books/chapters
        if self.required_coverage:
            covered = set(beat_chapters) & self.required_coverage
            uncovered = self.required_coverage - covered

            if uncovered:
                violations.append(
                    ConstraintViolation(
                        constraint_id=self.constraint_id,
                        constraint_type="arc_coverage",
                        artifact_id=self.character_id,
                        message=(
                            f"Character arc for {self.character_id} does not have beats in "
                            f"required chapters: {', '.join(sorted(uncovered))}. {self.description}"
                        ),
                        severity="error",
                    )
                )

        return ConstraintEvaluation(
            constraint_id=self.constraint_id,
            is_satisfied=len(violations) == 0,
            violations=violations,
        )


class CompositionConstraintSet(BaseModel):
    """A complete set of composition constraints for a narrative.

    Attributes:
        genre: Genre these constraints apply to
        optionality_constraints: List of optionality constraints
        chronological_constraints: List of chronological ordering constraints
        state_validity_constraints: List of state validity constraints
        arc_coverage_constraints: List of arc coverage constraints
    """

    genre: str
    optionality_constraints: List[OptionalityConstraint] = Field(default_factory=list)
    chronological_constraints: List[ChronologicalOrderingConstraint] = Field(
        default_factory=list
    )
    state_validity_constraints: List[StateValidityConstraint] = Field(default_factory=list)
    arc_coverage_constraints: List[ArcCoverageConstraint] = Field(default_factory=list)

    def add_optionality_constraint(self, constraint: OptionalityConstraint) -> None:
        """Add an optionality constraint to this set.

        Args:
            constraint: OptionalityConstraint to add
        """
        self.optionality_constraints.append(constraint)

    def add_chronological_constraint(self, constraint: ChronologicalOrderingConstraint) -> None:
        """Add a chronological ordering constraint to this set.

        Args:
            constraint: ChronologicalOrderingConstraint to add
        """
        self.chronological_constraints.append(constraint)

    def add_state_validity_constraint(self, constraint: StateValidityConstraint) -> None:
        """Add a state validity constraint to this set.

        Args:
            constraint: StateValidityConstraint to add
        """
        self.state_validity_constraints.append(constraint)

    def add_arc_coverage_constraint(self, constraint: ArcCoverageConstraint) -> None:
        """Add an arc coverage constraint to this set.

        Args:
            constraint: ArcCoverageConstraint to add
        """
        self.arc_coverage_constraints.append(constraint)

    def evaluate_all(
        self,
        artifacts: List[Dict],
        artifact_ordering: Dict[str, int],
        character_states: Dict[str, List[str]],
        character_arcs: Dict[str, Dict],
    ) -> Tuple[bool, List[ConstraintEvaluation]]:
        """Evaluate all constraints in this set.

        Args:
            artifacts: List of artifact dictionaries
            artifact_ordering: Dictionary mapping artifact_id to position
            character_states: Dictionary mapping character_id to state progression
            character_arcs: Dictionary mapping character_id to arc data

        Returns:
            Tuple of (all_satisfied, list of evaluations)
        """
        evaluations = []

        # Evaluate optionality constraints
        for constraint in self.optionality_constraints:
            evaluations.append(constraint.evaluate(artifacts))

        # Evaluate chronological constraints
        artifacts_dict = {a.get("id"): a for a in artifacts if "id" in a}
        for constraint in self.chronological_constraints:
            evaluations.append(constraint.evaluate(artifacts_dict, artifact_ordering))

        # Evaluate state validity constraints
        for constraint in self.state_validity_constraints:
            evaluations.append(constraint.evaluate(character_states))

        # Evaluate arc coverage constraints
        for constraint in self.arc_coverage_constraints:
            evaluations.append(constraint.evaluate(character_arcs))

        all_satisfied = all(e.is_satisfied for e in evaluations)
        return all_satisfied, evaluations


def create_netorare_constraints() -> CompositionConstraintSet:
    """Create composition constraints specific to netorare genre.

    Returns:
        CompositionConstraintSet configured for netorare
    """
    constraint_set = CompositionConstraintSet(genre="netorare")

    # Sequences are optional in netorare
    constraint_set.add_optionality_constraint(
        OptionalityConstraint(
            constraint_id="netorare_sequence_optional",
            artifact_type=ArtifactType.SEQUENCE,
            optionality_level=OptionalityLevel.OPTIONAL,
            condition="Sequences can be omitted if book uses direct chapter structure",
            example="netorare_book_1",
        )
    )

    # Chapters are required
    constraint_set.add_optionality_constraint(
        OptionalityConstraint(
            constraint_id="netorare_chapter_required",
            artifact_type=ArtifactType.CHAPTER,
            optionality_level=OptionalityLevel.REQUIRED,
            condition="Every book must have at least one chapter",
            example="netorare_chapter_1",
        )
    )

    # Protagonist humiliation must build gradually (setup before peak before resolution)
    constraint_set.add_chronological_constraint(
        ChronologicalOrderingConstraint(
            constraint_id="netorare_humiliation_progression",
            name="humiliation_setup_before_peak",
            source_artifact="protagonist_humiliation_setup",
            source_phase=2,
            target_artifact="protagonist_humiliation_peak",
            target_phase=5,
            description="Humiliation setup must occur before peak humiliation",
        )
    )

    # Character arcs must have coverage in multiple chapters (minimum 3)
    constraint_set.add_arc_coverage_constraint(
        ArcCoverageConstraint(
            constraint_id="netorare_protagonist_arc_coverage",
            character_id="protagonist",
            minimum_beats=3,
            genre="netorare",
            description="Protagonist must have transformation beats in at least 3 chapters",
        )
    )

    return constraint_set


def create_mystery_constraints() -> CompositionConstraintSet:
    """Create composition constraints specific to mystery genre.

    Returns:
        CompositionConstraintSet configured for mystery
    """
    constraint_set = CompositionConstraintSet(genre="mystery")

    # Sequences are optional in mystery
    constraint_set.add_optionality_constraint(
        OptionalityConstraint(
            constraint_id="mystery_sequence_optional",
            artifact_type=ArtifactType.SEQUENCE,
            optionality_level=OptionalityLevel.OPTIONAL,
            condition="Sequences can organize chapters thematically",
            example="mystery_investigation_sequence",
        )
    )

    # Chapters are required
    constraint_set.add_optionality_constraint(
        OptionalityConstraint(
            constraint_id="mystery_chapter_required",
            artifact_type=ArtifactType.CHAPTER,
            optionality_level=OptionalityLevel.REQUIRED,
            condition="Every mystery must have investigative chapters",
            example="mystery_chapter_investigation",
        )
    )

    # Clues must be revealed after investigation (chronological ordering)
    constraint_set.add_chronological_constraint(
        ChronologicalOrderingConstraint(
            constraint_id="mystery_clue_revelation_order",
            name="investigation_before_revelation",
            source_artifact="investigation_phase",
            source_phase=3,
            target_artifact="revelation_phase",
            target_phase=7,
            description="Investigation must occur before final revelation",
        )
    )

    # Detective arc must span entire story
    constraint_set.add_arc_coverage_constraint(
        ArcCoverageConstraint(
            constraint_id="mystery_detective_arc_coverage",
            character_id="detective",
            minimum_beats=4,
            genre="mystery",
            description="Detective must have logical deduction beats throughout story",
        )
    )

    return constraint_set


def create_gentlefemdom_constraints() -> CompositionConstraintSet:
    """Create composition constraints specific to gentle femdom genre.

    Returns:
        CompositionConstraintSet configured for gentle femdom
    """
    constraint_set = CompositionConstraintSet(genre="gentlefemdom")

    # Sequences can organize relationship progression
    constraint_set.add_optionality_constraint(
        OptionalityConstraint(
            constraint_id="gentlefemdom_sequence_optional",
            artifact_type=ArtifactType.SEQUENCE,
            optionality_level=OptionalityLevel.OPTIONAL,
            condition="Sequences can mark relationship development stages",
            example="gentlefemdom_relationship_sequence",
        )
    )

    # Chapters are required for intimate moments
    constraint_set.add_optionality_constraint(
        OptionalityConstraint(
            constraint_id="gentlefemdom_chapter_required",
            artifact_type=ArtifactType.CHAPTER,
            optionality_level=OptionalityLevel.REQUIRED,
            condition="Emotional and intimate beats must occur in chapters",
            example="gentlefemdom_chapter_intimacy",
        )
    )

    # Trust-building must precede surrender (state validity)
    constraint_set.add_chronological_constraint(
        ChronologicalOrderingConstraint(
            constraint_id="gentlefemdom_trust_before_surrender",
            name="trust_establishment_phase",
            source_artifact="trust_building_phase",
            source_phase=2,
            target_artifact="surrender_phase",
            target_phase=6,
            description="Trust must be established before vulnerability and surrender",
        )
    )

    # Dominant partner must guide submissive through emotional journey
    constraint_set.add_arc_coverage_constraint(
        ArcCoverageConstraint(
            constraint_id="gentlefemdom_submissive_arc_coverage",
            character_id="submissive_partner",
            minimum_beats=4,
            genre="gentlefemdom",
            description="Submissive must show emotional growth through vulnerability beats",
        )
    )

    return constraint_set


def get_constraints_for_genre(genre: str) -> CompositionConstraintSet:
    """Get the composition constraint set for a given genre.

    Args:
        genre: Genre identifier (netorare, mystery, gentlefemdom)

    Returns:
        CompositionConstraintSet for that genre

    Raises:
        ValueError: If genre is not recognized
    """
    if genre.lower() == "netorare":
        return create_netorare_constraints()
    elif genre.lower() == "mystery":
        return create_mystery_constraints()
    elif genre.lower() == "gentlefemdom":
        return create_gentlefemdom_constraints()
    else:
        raise ValueError(f"Unknown genre: {genre}")
