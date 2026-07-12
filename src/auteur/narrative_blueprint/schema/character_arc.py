"""Character arc schema for tracking character belief transformation across chapters.

This module defines the CharacterArc overlay artifact and the TurningPoint dataclass,
which together track how a character's beliefs and understanding evolve throughout
a narrative.

The CharacterArc introduces the first weak boundary: character arcs must reference
genre-appropriate themes, enforcing that character development respects the genre
contract established by the story identity layer.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List

from auteur.narrative_blueprint.schema.outline_types import (
    OverlayArtifact,
    ArcType,
)


@dataclass
class TurningPoint:
    """Represents a specific moment where a character's beliefs shift.

    A turning point captures a single instance within the narrative where a character's
    understanding, perspective, or emotional stance changes.

    Attributes:
        chapter: Chapter number where this turning point occurs (1-indexed)
        moment: Description of what happens at this turning point
        belief_shift: How the character's understanding or belief changes as a result
    """

    chapter: int
    moment: str
    belief_shift: str


class CharacterArc(OverlayArtifact):
    """Character arc overlay artifact tracking belief transformation across chapters.

    A CharacterArc describes how a character's beliefs, worldview, and emotional state
    evolve from the beginning to the end of a story. It spans multiple chapters and
    includes specific turning points where beliefs shift.

    This is the first weak boundary in the narrative schema: character arcs must
    reference genre-appropriate themes, enforcing that character development respects
    the genre contract. Task 8 (Arc Validator) will validate that themes match
    genre expectations.

    Attributes:
        character_name: Name of the character whose arc this is
        initial_belief: What the character believes at the start
        final_belief: What the character believes at the end
        turning_points: List of TurningPoint objects where beliefs shift
        genre_themes: Genre-relevant themes this arc explores
            (e.g., ["humiliation", "cuckoldry"] for netorare)
            Must be non-empty to enforce genre awareness
    """

    def __init__(
        self,
        genre: str,
        story_id: str,
        name: str,
        description: str,
        created_at: datetime,
        modified_at: datetime,
        span_chapters: List[int],
        character_name: str,
        initial_belief: str,
        final_belief: str,
        turning_points: List[TurningPoint] = None,
        genre_themes: List[str] = None,
    ):
        """Initialize a CharacterArc.

        Args:
            genre: Genre identifier
            story_id: Story identifier
            name: Display name
            description: Human-readable description
            created_at: Creation timestamp
            modified_at: Last modification timestamp
            span_chapters: List of chapter indices this arc spans
            character_name: Name of the character
            initial_belief: What the character believes at start
            final_belief: What the character believes at end
            turning_points: List of TurningPoint objects (optional, defaults to empty)
            genre_themes: Genre-relevant themes (required, must not be empty)

        Raises:
            ValueError: If genre_themes is empty
        """
        # Call parent __init__ with arc_type set to CHARACTER
        super().__init__(
            genre=genre,
            story_id=story_id,
            name=name,
            description=description,
            created_at=created_at,
            modified_at=modified_at,
            arc_type=ArcType.CHARACTER,
            span_chapters=span_chapters,
        )

        # Set arc-specific fields
        self.character_name = character_name
        self.initial_belief = initial_belief
        self.final_belief = final_belief
        self.turning_points = turning_points if turning_points is not None else []
        self.genre_themes = genre_themes if genre_themes is not None else []

        # WEAK BOUNDARY: genre_themes must not be empty
        # This enforces that character arcs respect genre constraints
        if not self.genre_themes:
            raise ValueError("genre_themes must not be empty")

    def artifact_type(self) -> str:
        """Return the artifact type identifier.

        Returns:
            String "character_arc"
        """
        return "character_arc"
