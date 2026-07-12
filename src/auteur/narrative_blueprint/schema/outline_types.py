"""Core outline types and enums for narrative blueprint artifacts.

This module defines the foundation type hierarchy for narrative outline artifacts.
All other outline schemas depend on these base classes and enums.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class ArcType(Enum):
    """Enumeration of narrative arc types."""

    CHARACTER = "character"
    STORY = "story"
    THEME = "theme"


@dataclass
class PhaseRange:
    """Represents a range of narrative phases (1-9).

    Attributes:
        start: Starting phase (1-9)
        peak: Peak phase (1-9), must be >= start
        end: Ending phase (1-9), must be >= peak
    """

    start: int
    peak: int
    end: int

    def __post_init__(self):
        """Validate phase range constraints."""
        # Validate individual phases are in range 1-9
        for phase, name in [(self.start, "start"), (self.peak, "peak"), (self.end, "end")]:
            if not 1 <= phase <= 9:
                raise ValueError(f"{name} phase must be between 1 and 9, got {phase}")

        # Validate ordering: start <= peak <= end
        if self.start > self.peak:
            raise ValueError(
                f"start phase ({self.start}) must be <= peak phase ({self.peak})"
            )
        if self.peak > self.end:
            raise ValueError(f"peak phase ({self.peak}) must be <= end phase ({self.end})")

    def includes_phase(self, phase: int) -> bool:
        """Check if a phase falls within this range.

        Args:
            phase: Phase to check (1-9)

        Returns:
            True if phase >= start and phase <= end, False otherwise
        """
        return self.start <= phase <= self.end


class OutlineArtifact(ABC):
    """Abstract base class for all outline artifacts.

    Outline artifacts represent narrative structures at different scales:
    - ContainerArtifacts: hierarchical containers (Series, Book, Chapter)
    - OverlayArtifacts: cross-cutting arcs (Character Arc, Story Arc, Theme Arc)

    All outline artifacts inherit genre and story_id for validation traceability.

    Attributes:
        genre: Genre identifier (e.g., "mystery", "netorare", "gentlefemdom")
        story_id: Story identifier for validation traceability
        name: Display name of the artifact
        description: Human-readable description
        created_at: Timestamp when artifact was created
        modified_at: Timestamp when artifact was last modified
    """

    def __init__(
        self,
        genre: str,
        story_id: str,
        name: str,
        description: str,
        created_at: datetime,
        modified_at: datetime,
    ):
        """Initialize OutlineArtifact.

        Args:
            genre: Genre identifier
            story_id: Story identifier
            name: Display name
            description: Human-readable description
            created_at: Creation timestamp
            modified_at: Last modification timestamp
        """
        self.genre = genre
        self.story_id = story_id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.modified_at = modified_at

    @abstractmethod
    def artifact_type(self) -> str:
        """Return the type of this artifact.

        Subclasses must implement this method to identify their artifact type.

        Returns:
            String identifier for the artifact type
        """
        pass


class ContainerArtifact(OutlineArtifact):
    """Abstract base class for hierarchical container artifacts.

    Represents containers in the outline hierarchy such as:
    - Series (collection of books)
    - Book (collection of chapters/sequences)
    - Sequence (grouping of scenes)
    - Chapter (collection of scenes)

    Containers can have parent containers for hierarchical composition.

    Attributes:
        parent_id: Optional reference to parent container
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
    ):
        """Initialize ContainerArtifact.

        Args:
            genre: Genre identifier
            story_id: Story identifier
            name: Display name
            description: Human-readable description
            created_at: Creation timestamp
            modified_at: Last modification timestamp
            parent_id: Optional parent container reference
        """
        super().__init__(
            genre=genre,
            story_id=story_id,
            name=name,
            description=description,
            created_at=created_at,
            modified_at=modified_at,
        )
        self.parent_id = parent_id


class OverlayArtifact(OutlineArtifact):
    """Abstract base class for cross-cutting arc artifacts.

    Represents narrative arcs that span multiple chapters or scenes:
    - Character Arc: development of a character
    - Story Arc: progression of the main plot
    - Theme Arc: development of thematic elements

    Overlays define which chapters they span, allowing them to be analyzed
    independently of the hierarchical container structure.

    Attributes:
        arc_type: Type of arc (CHARACTER, STORY, or THEME)
        span_chapters: List of chapter indices this arc spans
    """

    def __init__(
        self,
        genre: str,
        story_id: str,
        name: str,
        description: str,
        created_at: datetime,
        modified_at: datetime,
        arc_type: ArcType,
        span_chapters: List[int],
    ):
        """Initialize OverlayArtifact.

        Args:
            genre: Genre identifier
            story_id: Story identifier
            name: Display name
            description: Human-readable description
            created_at: Creation timestamp
            modified_at: Last modification timestamp
            arc_type: Type of arc (CHARACTER, STORY, or THEME)
            span_chapters: List of chapter indices this arc spans
        """
        super().__init__(
            genre=genre,
            story_id=story_id,
            name=name,
            description=description,
            created_at=created_at,
            modified_at=modified_at,
        )
        self.arc_type = arc_type
        self.span_chapters = span_chapters
