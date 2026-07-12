"""SeriesOutline artifact for representing series-level narrative structure."""

from datetime import datetime
from typing import Dict, List, Optional

from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact


class SeriesOutline(ContainerArtifact):
    """Concrete container artifact representing the structure of a multi-book series.

    SeriesOutline tracks continuity, character arcs, and thematic progression
    across multiple books. It represents the highest level of narrative organization
    for a series.

    Attributes:
        series_name: Name of the series
        book_ids: List of story_ids for each book in order
        long_term_character_evolution: Dictionary mapping character names to their arcs
        thematic_progression: List of thematic progressions across books

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
        series_name: str,
        book_ids: List[str],
        long_term_character_evolution: Dict[str, str],
        thematic_progression: List[str],
    ):
        """Initialize SeriesOutline.

        Args:
            genre: Genre identifier (e.g., "mystery", "netorare", "gentlefemdom")
            story_id: Story identifier for validation traceability
            name: Display name of the artifact
            description: Human-readable description
            created_at: Timestamp when artifact was created
            modified_at: Timestamp when artifact was last modified
            parent_id: Optional reference to parent container
            series_name: Name of the series
            book_ids: List of story_ids for each book in order
            long_term_character_evolution: Dict mapping character names to their arcs
            thematic_progression: List of thematic progression descriptions

        Raises:
            ValueError: Never (all collections can be empty)
        """
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

        # Set SeriesOutline-specific attributes
        self.series_name = series_name
        self.book_ids = book_ids
        self.long_term_character_evolution = long_term_character_evolution
        self.thematic_progression = thematic_progression

    def artifact_type(self) -> str:
        """Return the type of this artifact.

        Returns:
            "series_outline"
        """
        return "series_outline"
