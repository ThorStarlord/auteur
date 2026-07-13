"""Ownership rules definition for Structure composition and orchestration.

This module defines the canonical ownership mapping for narrative artifacts.
Ownership answers: "Which artifact is the authoritative source for this structural fact?"

The ownership model distinguishes between:
- Authoring ownership: which artifact is explicitly authored/modified by the user
- Derivation: computed state that flows from other artifacts (not separately authored)
- References: one artifact references another (not ownership, tracked separately)

All ownership rules are genre-agnostic and apply identically across all story types.
"""

from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator


class ArtifactType(str, Enum):
    """Enumeration of narrative artifact types in Layer 2."""

    SERIES_OUTLINE = "series_outline"
    BOOK_OUTLINE = "book_outline"
    SEQUENCE_OUTLINE = "sequence_outline"
    CHAPTER_OUTLINE = "chapter_outline"
    CHARACTER_ARC = "character_arc"
    STORY_ARC = "story_arc"
    THEME_ARC = "theme_arc"


class StructuralFact(str, Enum):
    """Enumeration of structural facts that can be owned by an artifact."""

    # Container hierarchy facts
    BOOKS_IN_SERIES = "books_in_series"
    SEQUENCES_IN_BOOK = "sequences_in_book"
    CHAPTERS_IN_SEQUENCE = "chapters_in_sequence"
    CHAPTER_ORDERING = "chapter_ordering"

    # Artifact content facts
    CHAPTER_PURPOSE = "chapter_purpose"
    CHAPTER_SUMMARY = "chapter_summary"

    # Arc-specific facts
    CHARACTER_TRANSFORMATION = "character_transformation"
    PLOT_PROGRESSION = "plot_progression"
    ARC_BEAT_LOCATIONS = "arc_beat_locations"

    # Derived facts (computed, not authored)
    CHAPTER_COUNT = "chapter_count"
    SEQUENCE_COUNT = "sequence_count"
    ARC_SPAN_CHAPTERS = "arc_span_chapters"
    NARRATIVE_PHASE_ASSIGNMENT = "narrative_phase_assignment"


class OwnershipRule(BaseModel):
    """A single ownership rule mapping a structural fact to its authoritative source.

    An OwnershipRule declares which artifact type owns (is the authoritative source for)
    a particular structural fact about the narrative.

    Attributes:
        fact: The structural fact being owned (StructuralFact enum)
        owner: The artifact type that authoritatively declares this fact
        description: Human-readable explanation of why this artifact owns this fact
        is_derived: Whether this fact is computed (derived) rather than authored
            Derived facts flow from other artifacts, not separately modified by user
    """

    fact: StructuralFact
    owner: ArtifactType
    description: str = Field(
        ..., min_length=10, description="Explanation of ownership rationale"
    )
    is_derived: bool = Field(
        default=False, description="True if fact is computed, not authored"
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Ensure description is non-empty and substantive."""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()


class OwnershipMapping(BaseModel):
    """Complete ownership mapping for all structural facts in Layer 2.

    This is the canonical ownership declaration used for composition validation.
    It defines which artifact type owns each structural fact, enabling:
    - Reference validation (which IDs should resolve between artifacts)
    - Modification tracking (which artifact should be edited for each fact)
    - Derivation detection (which facts flow from other artifacts)

    Attributes:
        version: Schema version for backward compatibility
        rules: List of OwnershipRule objects
        description: Overview of the ownership model
        last_updated: ISO 8601 timestamp when rules were last updated
    """

    version: str = Field(
        default="1.0.0",
        description="Schema version for ownership rules (semantic versioning)",
    )
    rules: List[OwnershipRule] = Field(
        ..., min_length=8, description="List of ownership rules"
    )
    description: str = Field(
        default="Layer 2.5 canonical ownership mapping",
        description="Overview of the ownership model",
    )
    last_updated: str = Field(
        default="2026-07-12", description="ISO 8601 timestamp of last update"
    )

    @field_validator("rules")
    @classmethod
    def validate_rules(cls, v: List[OwnershipRule]) -> List[OwnershipRule]:
        """Validate that rules don't have duplicates and cover essential facts."""
        # Check for duplicate facts
        facts = [rule.fact for rule in v]
        if len(facts) != len(set(facts)):
            raise ValueError("Duplicate ownership rules found for same fact")

        # Verify at least the 8 core facts are defined
        core_facts = {
            StructuralFact.BOOKS_IN_SERIES,
            StructuralFact.SEQUENCES_IN_BOOK,
            StructuralFact.CHAPTERS_IN_SEQUENCE,
            StructuralFact.CHAPTER_PURPOSE,
            StructuralFact.CHARACTER_TRANSFORMATION,
            StructuralFact.PLOT_PROGRESSION,
            StructuralFact.ARC_BEAT_LOCATIONS,
            StructuralFact.ARC_SPAN_CHAPTERS,
        }

        defined_facts = set(facts)
        missing = core_facts - defined_facts
        if missing:
            raise ValueError(
                f"Missing ownership rules for core facts: {[f.value for f in missing]}"
            )

        return v

    def get_rule(self, fact: StructuralFact) -> Optional[OwnershipRule]:
        """Look up the ownership rule for a given structural fact.

        Args:
            fact: The structural fact to look up

        Returns:
            The OwnershipRule for this fact, or None if not found
        """
        for rule in self.rules:
            if rule.fact == fact:
                return rule
        return None

    def get_owner(self, fact: StructuralFact) -> Optional[ArtifactType]:
        """Look up the owner (artifact type) for a given structural fact.

        Args:
            fact: The structural fact to look up

        Returns:
            The ArtifactType that owns this fact, or None if not found
        """
        rule = self.get_rule(fact)
        return rule.owner if rule else None

    def get_rules_by_owner(self, owner: ArtifactType) -> List[OwnershipRule]:
        """Get all ownership rules for a particular artifact type.

        Args:
            owner: The artifact type to filter by

        Returns:
            List of OwnershipRule objects owned by this artifact type
        """
        return [rule for rule in self.rules if rule.owner == owner]

    def get_derived_facts(self) -> List[StructuralFact]:
        """Get all structural facts that are derived (computed, not authored).

        Returns:
            List of StructuralFact objects marked as is_derived=True
        """
        return [rule.fact for rule in self.rules if rule.is_derived]

    def get_authored_facts(self) -> List[StructuralFact]:
        """Get all structural facts that are explicitly authored (not derived).

        Returns:
            List of StructuralFact objects marked as is_derived=False
        """
        return [rule.fact for rule in self.rules if not rule.is_derived]
