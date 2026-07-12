"""Reference system definition for Layer 2.5 narrative orchestration.

This module defines the reference types and validation for cross-artifact references.
References answer: "How do different artifacts point to each other?"

Reference types include:
- Arc references: how arcs reference chapters they span
- Beat references: how arc beats reference their chapters
- Setup/Payoff references: narrative cause-effect relationships
- Container references: book→sequence, sequence→chapter relationships

All references use a canonical ID format: {artifact_type}_{unique_id}
Examples: chapter_07, clara_distrust_deepens, book_001, sequence_03

References enable:
- Cross-checking that referenced IDs exist in the structure
- Chronological validation (payoffs after setups)
- Arc beat location mapping
- Hierarchical containment validation
"""

from enum import Enum
from typing import List, Optional, Dict, Callable, Any
from pydantic import BaseModel, Field, field_validator
import re


class ReferenceType(str, Enum):
    """Enumeration of reference types in Layer 2.5."""

    # Container hierarchy references
    BOOK_TO_SEQUENCE = "book_to_sequence"  # Book references its sequences
    SEQUENCE_TO_CHAPTER = "sequence_to_chapter"  # Sequence references its chapters
    CHAPTER_TO_PARENT = "chapter_to_parent"  # Chapter references parent sequence/book

    # Arc references
    ARC_TO_CHAPTER = "arc_to_chapter"  # Arc references chapters in its span
    ARC_BEAT_TO_CHAPTER = "arc_beat_to_chapter"  # Arc beat references its chapter

    # Narrative cause-effect
    SETUP_TO_PAYOFF = "setup_to_payoff"  # Setup event references its payoff
    PAYOFF_TO_SETUP = "payoff_to_setup"  # Payoff event references its setup

    # Derived references (computed, not authored)
    CHAPTER_TO_PHASE = "chapter_to_phase"  # Chapter references narrative phase


class ArtifactTypePrefix(str, Enum):
    """Canonical prefixes for artifact type IDs.

    IDs follow format: {prefix}_{unique_id}
    Examples: chapter_07, book_001, clara_arc_01
    """

    SERIES = "series"
    BOOK = "book"
    SEQUENCE = "sequence"
    CHAPTER = "chapter"
    CHARACTER_ARC = "character_arc"
    STORY_ARC = "story_arc"
    THEME_ARC = "theme_arc"
    BEAT = "beat"
    TURNING_POINT = "turning_point"
    ARC_CHECKPOINT = "arc_checkpoint"


class IdFormat:
    """Utility class for validating and parsing ID format."""

    # Pattern: {artifact_type}_{unique_id}
    # artifact_type must start with letter, can contain lowercase letters and underscores (e.g., character_arc)
    # unique_id must start with letter/number, can contain letters, numbers, underscores
    ID_PATTERN = re.compile(r"^[a-z]([a-z_]*[a-z])?_[a-z0-9]([a-z0-9_]*[a-z0-9])?$")

    @staticmethod
    def is_valid_id(artifact_id: str) -> bool:
        """Check if an ID follows the canonical format.

        Args:
            artifact_id: ID to validate

        Returns:
            True if ID matches {artifact_type}_{unique_id} format
        """
        return IdFormat.ID_PATTERN.match(artifact_id) is not None

    @staticmethod
    def split_id(artifact_id: str) -> tuple[str, str]:
        """Split an ID into type prefix and unique identifier.

        Args:
            artifact_id: ID in format {artifact_type}_{unique_id}

        Returns:
            Tuple of (artifact_type, unique_id)

        Raises:
            ValueError: If ID format is invalid
        """
        if not IdFormat.is_valid_id(artifact_id):
            raise ValueError(f"Invalid ID format: {artifact_id}")

        # Split on last underscore to handle artifact types with underscores
        parts = artifact_id.rsplit("_", 1)
        if len(parts) != 2:
            raise ValueError(f"Cannot parse ID: {artifact_id}")

        artifact_type, unique_id = parts
        return artifact_type, unique_id

    @staticmethod
    def make_id(artifact_type: str, unique_id: str) -> str:
        """Construct an ID from type and unique identifier.

        Args:
            artifact_type: Type prefix (e.g., "chapter", "character_arc")
            unique_id: Unique identifier (e.g., "07", "clara_distrust")

        Returns:
            Formatted ID string

        Raises:
            ValueError: If components are invalid
        """
        if not artifact_type or not unique_id:
            raise ValueError("artifact_type and unique_id must not be empty")

        if not re.match(r"^[a-z_]+$", artifact_type):
            raise ValueError(
                f"artifact_type must contain only lowercase letters and underscores: {artifact_type}"
            )

        if not re.match(r"^[a-z0-9_]+$", unique_id):
            raise ValueError(
                f"unique_id must contain only lowercase letters, numbers, and underscores: {unique_id}"
            )

        return f"{artifact_type}_{unique_id}"


class Reference(BaseModel):
    """Base model for narrative artifact references.

    A Reference captures a directed relationship from a source artifact to a target.
    It records what the reference is, allowing validation to check:
    - Does the target ID actually exist?
    - Is the reference type semantically valid?
    - Are chronological constraints respected (setup before payoff)?

    Attributes:
        source_id: The artifact making the reference (e.g., "chapter_07")
        target_id: The artifact being referenced (e.g., "chapter_03")
        reference_type: The kind of relationship (ReferenceType enum)
        optional: Whether this reference must resolve (True = may be null/unresolved)
        context: Optional human-readable context (why this reference exists)
    """

    source_id: str = Field(..., min_length=3, description="Source artifact ID")
    target_id: Optional[str] = Field(
        default=None, description="Target artifact ID (None if optional and unset)"
    )
    reference_type: ReferenceType = Field(
        ..., description="Type of reference relationship"
    )
    optional: bool = Field(
        default=False,
        description="Whether target_id must exist (False = required, True = optional)",
    )
    context: Optional[str] = Field(
        default=None, description="Human-readable context for this reference"
    )

    @field_validator("source_id")
    @classmethod
    def validate_source_id(cls, v: str) -> str:
        """Validate source_id follows canonical ID format."""
        if not IdFormat.is_valid_id(v):
            raise ValueError(
                f"source_id must follow format {{artifact_type}}_{{unique_id}}: {v}"
            )
        return v

    @field_validator("target_id")
    @classmethod
    def validate_target_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate target_id follows canonical ID format (if present)."""
        if v is not None and not IdFormat.is_valid_id(v):
            raise ValueError(
                f"target_id must follow format {{artifact_type}}_{{unique_id}}: {v}"
            )
        return v

    def is_resolved(self) -> bool:
        """Check if this reference has a target (is resolved).

        Returns:
            True if target_id is set, False if None
        """
        return self.target_id is not None

    def can_be_unresolved(self) -> bool:
        """Check if this reference is allowed to be unresolved.

        Returns:
            True if optional=True or target_id is not None
        """
        return self.optional or self.is_resolved()

    def validate_resolution(self) -> tuple[bool, Optional[str]]:
        """Validate that this reference's resolution status is valid.

        Returns:
            Tuple of (is_valid, error_message)
            is_valid is True if resolution status is OK, False if reference is required but unresolved
            error_message is None if valid, otherwise describes the problem
        """
        if not self.optional and not self.is_resolved():
            return (
                False,
                f"Required reference {self.source_id}→{self.reference_type.value} has no target",
            )
        return True, None


class ArcReference(Reference):
    """Reference from a narrative arc to chapters it spans.

    An ArcReference represents the relationship between an arc (character, story, or theme)
    and the chapters it encompasses. This is a required reference - arcs must reference
    at least the chapters where their beats/checkpoints occur.

    Example: "character_arc_clara" → ["chapter_02", "chapter_05", "chapter_12"]
    """

    reference_type: ReferenceType = Field(default=ReferenceType.ARC_TO_CHAPTER)

    @field_validator("optional")
    @classmethod
    def validate_optional(cls, v: bool) -> bool:
        """Arc references must be required (optional=False)."""
        if v is True:
            raise ValueError("Arc references must be required (optional must be False)")
        return v


class ChapterReference(Reference):
    """Reference from a chapter to its parent container (sequence or book).

    A ChapterReference represents the hierarchical containment relationship.
    Every chapter must reference its immediate parent container.

    Example: "chapter_03" → "sequence_02" or "book_001"
    """

    reference_type: ReferenceType = Field(default=ReferenceType.CHAPTER_TO_PARENT)

    @field_validator("optional")
    @classmethod
    def validate_optional(cls, v: bool) -> bool:
        """Chapter parent references must be required."""
        if v is True:
            raise ValueError(
                "Chapter parent references must be required (optional must be False)"
            )
        return v


class BeatReference(Reference):
    """Reference from an arc beat (turning point or checkpoint) to its chapter.

    A BeatReference represents where a specific beat occurs in the narrative.
    Arc beats (character arc turning points, story arc checkpoints) must reference
    their containing chapter to establish timeline.

    Example: "turning_point_clara_distrust" → "chapter_05"
    """

    reference_type: ReferenceType = Field(default=ReferenceType.ARC_BEAT_TO_CHAPTER)

    @field_validator("optional")
    @classmethod
    def validate_optional(cls, v: bool) -> bool:
        """Beat references must be required."""
        if v is True:
            raise ValueError("Beat references must be required (optional must be False)")
        return v


class PayoffReference(Reference):
    """Reference from a payoff event to its setup event.

    A PayoffReference establishes the narrative cause-effect relationship:
    where a setup event (plant, revelation, commitment) pays off later.
    Payoffs are required to reference their setup to enable chronological validation.

    Example: "chapter_15" (payoff) → "chapter_03" (setup)
    Constraint: payoff chapter must have higher number than setup chapter
    """

    reference_type: ReferenceType = Field(default=ReferenceType.PAYOFF_TO_SETUP)

    @field_validator("optional")
    @classmethod
    def validate_optional(cls, v: bool) -> bool:
        """Payoff references must be required."""
        if v is True:
            raise ValueError(
                "Payoff references must be required (optional must be False)"
            )
        return v


class SetupReference(Reference):
    """Reference from a setup event to its payoff event.

    A SetupReference establishes the forward reference: which setup event
    will have a payoff. This is typically optional to allow open-ended setups,
    but when provided enables thorough narrative validation.

    Example: "chapter_03" (setup) → "chapter_15" (payoff) (optional)
    Constraint: payoff chapter must have higher number than setup chapter
    """

    reference_type: ReferenceType = Field(default=ReferenceType.SETUP_TO_PAYOFF)
    # Setup references are optional by default
    optional: bool = Field(
        default=True, description="Setup→payoff references are typically optional"
    )


class ReferenceResolver:
    """Resolves and validates references against artifact registry.

    A ReferenceResolver knows how to:
    - Look up artifacts by ID
    - Resolve references (find the target of a reference)
    - Validate that references are semantically valid
    - Detect broken references

    The resolver is instantiated with a registry of artifacts, then used to
    validate references throughout the outline.
    """

    def __init__(self, artifact_registry: Dict[str, Any]):
        """Initialize resolver with an artifact registry.

        Args:
            artifact_registry: Dictionary mapping artifact IDs to artifact objects
                Example: {
                    "chapter_01": ChapterOutline(...),
                    "chapter_02": ChapterOutline(...),
                    "book_001": BookOutline(...),
                }
        """
        self.registry = artifact_registry

    def artifact_exists(self, artifact_id: str) -> bool:
        """Check if an artifact with given ID exists in the registry.

        Args:
            artifact_id: ID to look up

        Returns:
            True if artifact exists, False otherwise
        """
        return artifact_id in self.registry

    def get_artifact(self, artifact_id: str) -> Optional[Any]:
        """Retrieve an artifact from the registry.

        Args:
            artifact_id: ID to look up

        Returns:
            The artifact object, or None if not found
        """
        return self.registry.get(artifact_id)

    def resolve_reference(self, reference: Reference) -> tuple[bool, Optional[str]]:
        """Resolve and validate a single reference.

        Args:
            reference: Reference to validate

        Returns:
            Tuple of (is_valid, error_message)
            is_valid is True if reference is valid, False if broken
            error_message is None if valid, otherwise describes the problem
        """
        # If source doesn't exist, that's a problem with the source artifact, not this reference
        # But we can report it anyway
        if not self.artifact_exists(reference.source_id):
            return False, f"Source artifact not found: {reference.source_id}"

        # If reference is optional and unresolved, that's OK
        if reference.optional and reference.target_id is None:
            return True, None

        # If reference is required and unresolved, that's an error
        if reference.target_id is None:
            return False, f"Required reference has no target: {reference.source_id}"

        # If target doesn't exist, that's a broken reference
        if not self.artifact_exists(reference.target_id):
            return (
                False,
                f"Target artifact not found: {reference.source_id}→{reference.target_id}",
            )

        return True, None

    def resolve_references(
        self, references: List[Reference]
    ) -> tuple[bool, List[str]]:
        """Resolve and validate multiple references.

        Args:
            references: List of references to validate

        Returns:
            Tuple of (all_valid, error_messages)
            all_valid is True if all references are valid
            error_messages is list of error descriptions (empty if all valid)
        """
        errors = []
        for ref in references:
            is_valid, error_msg = self.resolve_reference(ref)
            if not is_valid:
                errors.append(error_msg)

        return len(errors) == 0, errors


class ReferenceGraph:
    """Tracks and analyzes the reference graph of a narrative outline.

    A ReferenceGraph maintains all references between artifacts and enables
    analysis such as:
    - Finding all artifacts referenced by a given artifact
    - Finding all artifacts that reference a given artifact
    - Detecting cycles in the reference graph
    - Visualizing the reference structure
    """

    def __init__(self):
        """Initialize an empty reference graph."""
        self.references: List[Reference] = []
        self._outgoing: Dict[str, List[Reference]] = {}  # source_id → references
        self._incoming: Dict[str, List[Reference]] = {}  # target_id → references

    def add_reference(self, reference: Reference) -> None:
        """Add a reference to the graph.

        Args:
            reference: Reference to add
        """
        self.references.append(reference)

        # Track outgoing references from source
        if reference.source_id not in self._outgoing:
            self._outgoing[reference.source_id] = []
        self._outgoing[reference.source_id].append(reference)

        # Track incoming references to target (if target exists)
        if reference.target_id:
            if reference.target_id not in self._incoming:
                self._incoming[reference.target_id] = []
            self._incoming[reference.target_id].append(reference)

    def get_outgoing(self, artifact_id: str) -> List[Reference]:
        """Get all references from a given artifact.

        Args:
            artifact_id: Artifact to query

        Returns:
            List of references where this artifact is the source
        """
        return self._outgoing.get(artifact_id, [])

    def get_incoming(self, artifact_id: str) -> List[Reference]:
        """Get all references to a given artifact.

        Args:
            artifact_id: Artifact to query

        Returns:
            List of references where this artifact is the target
        """
        return self._incoming.get(artifact_id, [])

    def get_references_by_type(self, ref_type: ReferenceType) -> List[Reference]:
        """Get all references of a given type.

        Args:
            ref_type: Type of reference to filter

        Returns:
            List of references matching the type
        """
        return [ref for ref in self.references if ref.reference_type == ref_type]
