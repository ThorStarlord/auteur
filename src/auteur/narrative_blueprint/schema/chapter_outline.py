"""ChapterOutline artifact for representing chapter-level narrative decisions."""

from datetime import datetime
from typing import Dict, Optional

from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact


class ChapterOutline(ContainerArtifact):
    """Concrete container artifact representing a single chapter's narrative decisions.

    ChapterOutline decomposes a chapter into its key narrative elements and its
    position within the 9-phase structure. It records how this chapter advances
    the story, character, and thematic arcs.

    Attributes:
        chapter_number: Position in book (1-indexed, must be > 0)
        phase: Which 9-phase this chapter occupies (1-9 only)
        title: Chapter title
        goal: What narrative objective does this chapter accomplish?
        conflict: What opposition/challenge does protagonist face?
        turning_point: The moment that changes everything in this chapter
        emotional_beat: Emotional tone/progression (e.g., "hope → despair → acceptance")
        arc_progressions: How do story/character arcs advance? (optional, default empty dict)

    Inherited from ContainerArtifact:
        genre: Genre identifier
        story_id: Story identifier
        name: Display name
        description: Description
        created_at: Creation timestamp
        modified_at: Last modification timestamp
        parent_id: Optional parent container reference
    """

    def __init__(
        self,
        genre: str,
        story_id: str,
        name: str,
        description: str,
        created_at: datetime,
        modified_at: datetime,
        parent_id: Optional[str],
        chapter_number: int,
        phase: int,
        title: str,
        goal: str,
        conflict: str,
        turning_point: str,
        emotional_beat: str,
        arc_progressions: Optional[Dict[str, str]] = None,
    ):
        """Initialize ChapterOutline.

        Args:
            genre: Genre identifier (e.g., "mystery", "netorare", "gentlefemdom")
            story_id: Story identifier for validation traceability
            name: Display name of the artifact
            description: Human-readable description
            created_at: Timestamp when artifact was created
            modified_at: Timestamp when artifact was last modified
            parent_id: Optional reference to parent container
            chapter_number: Position in book (1-indexed, must be > 0)
            phase: Which 9-phase this chapter occupies (1-9 only)
            title: Chapter title
            goal: What narrative objective does this chapter accomplish?
            conflict: What opposition/challenge does protagonist face?
            turning_point: The moment that changes everything in this chapter
            emotional_beat: Emotional tone/progression
            arc_progressions: How do story/character arcs advance? (optional, default empty dict)

        Raises:
            ValueError: If chapter_number <= 0 or phase not in 1-9
        """
        # Validate chapter_number
        if chapter_number <= 0:
            raise ValueError("chapter_number must be > 0")

        # Validate phase
        if not 1 <= phase <= 9:
            raise ValueError("phase must be between 1 and 9")

        # Initialize parent
        super().__init__(
            genre=genre,
            story_id=story_id,
            name=name,
            description=description,
            created_at=created_at,
            modified_at=modified_at,
            parent_id=parent_id,
        )

        # Set ChapterOutline-specific attributes
        self.chapter_number = chapter_number
        self.phase = phase
        self.title = title
        self.goal = goal
        self.conflict = conflict
        self.turning_point = turning_point
        self.emotional_beat = emotional_beat
        self.arc_progressions = arc_progressions if arc_progressions is not None else {}

    def artifact_type(self) -> str:
        """Return the type of this artifact.

        Returns:
            "chapter_outline"
        """
        return "chapter_outline"
