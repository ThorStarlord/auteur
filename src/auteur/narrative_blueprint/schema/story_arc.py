"""Story arc schema for tracking thematic/plot arcs spanning multiple phases.

This module defines the StoryArc overlay artifact and the ArcCheckpoint dataclass,
which together track how plot or thematic arcs (mystery, romance, political, revenge,
survival) progress through the 9 narrative phases.

Multiple story arcs can coexist in the same story (mystery + romance in same book).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal

from auteur.narrative_blueprint.schema.outline_types import (
    OverlayArtifact,
    ArcType,
    PhaseRange,
)


@dataclass
class ArcCheckpoint:
    """Represents a specific moment where a story arc progresses.

    A checkpoint captures a single instance within the narrative where a plot or
    thematic arc reaches a notable milestone.

    Attributes:
        phase: Which 9-phase does this checkpoint belong to? (1-9)
        moment: What happens at this checkpoint?
    """

    phase: int
    moment: str


class StoryArc(OverlayArtifact):
    """Story arc overlay artifact tracking thematic/plot arcs spanning multiple phases.

    A StoryArc describes how a narrative arc (mystery, romance, political, revenge,
    or survival) progresses through the 9-phase structure. Multiple story arcs can
    coexist in the same story, allowing complex narratives with intertwined plots
    and themes.

    Attributes:
        arc_name: Specific arc title (e.g., "The Library Secret", "First Contact")
        arc_category: Type of arc - one of: mystery, romance, political, revenge, survival
        phase_range: Which 9-phases does this arc span? (start, peak, end)
        checkpoints: Milestones within arc where the arc progresses (optional, defaults to empty)
    """

    def __init__(
        self,
        genre: str,
        story_id: str,
        name: str,
        description: str,
        created_at: datetime,
        modified_at: datetime,
        arc_name: str,
        arc_category: Literal["mystery", "romance", "political", "revenge", "survival"],
        phase_range: PhaseRange,
        checkpoints: List[ArcCheckpoint] = None,
        span_chapters: List[int] = None,
    ):
        """Initialize a StoryArc.

        Args:
            genre: Genre identifier
            story_id: Story identifier
            name: Display name
            description: Human-readable description
            created_at: Creation timestamp
            modified_at: Last modification timestamp
            arc_name: Specific arc title
            arc_category: Type of arc (mystery, romance, political, revenge, survival)
            phase_range: PhaseRange object defining which phases this arc spans
            checkpoints: List of ArcCheckpoint objects (optional, defaults to empty)
            span_chapters: List of chapter indices this arc spans (optional, defaults to empty)

        Raises:
            ValueError: If phase_range is invalid
        """
        # Call parent __init__ with arc_type set to STORY
        super().__init__(
            genre=genre,
            story_id=story_id,
            name=name,
            description=description,
            created_at=created_at,
            modified_at=modified_at,
            arc_type=ArcType.STORY,
            span_chapters=span_chapters if span_chapters is not None else [],
        )

        # Set arc-specific fields
        self.arc_name = arc_name
        self.arc_category = arc_category
        self.phase_range = phase_range
        self.checkpoints = checkpoints if checkpoints is not None else []

    def artifact_type(self) -> str:
        """Return the artifact type identifier.

        Returns:
            String "story_arc"
        """
        return "story_arc"
