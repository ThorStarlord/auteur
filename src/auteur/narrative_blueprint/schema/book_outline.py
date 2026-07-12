"""BookOutline artifact for representing book-level narrative structure."""

from datetime import datetime
from typing import Dict, Literal, Optional

from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact


class BookOutline(ContainerArtifact):
    """Concrete container artifact representing the entire book's narrative structure.

    BookOutline decomposes a complete book into 9 narrative phases, forming the
    highest-level story structure before chapter-level breakdown.

    Attributes:
        title: The book's title
        chapter_estimate: Expected number of chapters (must be > 0)
        structure: Story structure template ("3-act" or "4-act")
        phases_summary: One-line summary for each 9-phase (keys 1-9)

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
        title: str,
        chapter_estimate: int,
        structure: Literal["3-act", "4-act"],
        phases_summary: Dict[int, str],
    ):
        """Initialize BookOutline.

        Args:
            genre: Genre identifier (e.g., "mystery", "netorare", "gentlefemdom")
            story_id: Story identifier for validation traceability
            name: Display name of the artifact
            description: Human-readable description
            created_at: Timestamp when artifact was created
            modified_at: Timestamp when artifact was last modified
            parent_id: Optional reference to parent container
            title: The book's title
            chapter_estimate: Expected number of chapters (must be > 0)
            structure: Story structure template ("3-act" or "4-act")
            phases_summary: Dictionary with keys 1-9, one-line summary per phase

        Raises:
            ValueError: If chapter_estimate <= 0 or phases_summary validation fails
        """
        # Validate chapter_estimate
        if chapter_estimate <= 0:
            raise ValueError("chapter_estimate must be > 0")

        # Validate phases_summary
        if len(phases_summary) != 9:
            raise ValueError("phases_summary must have exactly 9 phases")

        # Verify keys are exactly 1 through 9
        expected_keys = set(range(1, 10))
        actual_keys = set(phases_summary.keys())
        if actual_keys != expected_keys:
            raise ValueError("phases_summary must have keys 1 through 9")

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

        # Set BookOutline-specific attributes
        self.title = title
        self.chapter_estimate = chapter_estimate
        self.structure = structure
        self.phases_summary = phases_summary

    def artifact_type(self) -> str:
        """Return the type of this artifact.

        Returns:
            "book_outline"
        """
        return "book_outline"
