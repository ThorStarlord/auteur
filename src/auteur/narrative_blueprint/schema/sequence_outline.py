"""SequenceOutline artifact for representing sequence-level narrative structure."""

from datetime import datetime
from typing import List, Optional, Tuple

from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact


class SequenceOutline(ContainerArtifact):
    """Concrete container artifact representing a sequence of chapters in a narrative.

    SequenceOutline groups chapters into meaningful sequences that accomplish
    a specific narrative objective. It represents a mid-level organizational
    structure between Book and Chapter.

    Attributes:
        sequence_number: Position in the book (1-indexed, must be > 0)
        objective: What this sequence accomplishes narratively
        chapter_range: Tuple of (start_chapter, end_chapter), 1-indexed inclusive
        key_scenes: List of major scene descriptions in this sequence (optional)

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
        sequence_number: int,
        objective: str,
        chapter_range: Tuple[int, int],
        key_scenes: Optional[List[str]] = None,
    ):
        """Initialize SequenceOutline.

        Args:
            genre: Genre identifier (e.g., "mystery", "netorare", "gentlefemdom")
            story_id: Story identifier for validation traceability
            name: Display name of the artifact
            description: Human-readable description
            created_at: Timestamp when artifact was created
            modified_at: Timestamp when artifact was last modified
            parent_id: Optional reference to parent container
            sequence_number: Position in book (must be > 0)
            objective: Narrative objective of this sequence
            chapter_range: Tuple of (start_chapter, end_chapter), both must be > 0, start <= end
            key_scenes: List of major scenes (optional, defaults to empty list)

        Raises:
            ValueError: If sequence_number <= 0 or chapter_range is invalid
        """
        # Validate sequence_number
        if sequence_number <= 0:
            raise ValueError("sequence_number must be > 0")

        # Validate chapter_range
        start_ch, end_ch = chapter_range
        if start_ch <= 0 or end_ch <= 0:
            raise ValueError("chapter_range start and end must be > 0")
        if start_ch > end_ch:
            raise ValueError("chapter_range start must be <= end")

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

        # Set SequenceOutline-specific attributes
        self.sequence_number = sequence_number
        self.objective = objective
        self.chapter_range = chapter_range
        self.key_scenes = key_scenes if key_scenes is not None else []

    def artifact_type(self) -> str:
        """Return the type of this artifact.

        Returns:
            "sequence_outline"
        """
        return "sequence_outline"
