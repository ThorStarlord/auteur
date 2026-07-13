"""Scene Builder for Layer 3 narrative realization.

Generates template scenes from chapter outlines, creating a default scene
structure that can be refined by the author.

Key Features:
- Accepts chapter outlines as input
- Creates one or more scenes per chapter
- Applies genre-specific defaults for scene structure
- Generates scenes with draft status ready for author completion
- Works identically across all genres (netorara, mystery, gentlefemdom)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum

from auteur.narrative_realization.schema.scene_outline import (
    SceneOutline,
    SceneStatus,
    TemporalRelation,
)
from auteur.narrative_realization.schema.scene_action import (
    Goal,
    Opposition,
)
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline


class SceneBuilder:
    """Builds template scenes from chapter outlines.

    The builder generates minimal but structurally complete scenes that authors
    can refine with specific actions, dialogue, and character details.

    Each scene generated has:
    - Unique scene ID (scene_{chapter:02d}_{position:02d})
    - Reference to parent chapter
    - Basic narrative position and temporal relations
    - Draft status (ready for author refinement)
    - Placeholder goal and opposition (derived from chapter)
    """

    # Default scenes per chapter (can be overridden)
    SCENES_PER_CHAPTER = 2

    # Genre-specific scene guidance
    SCENE_GUIDANCE = {
        "netorare": {
            "scene_1": "Setup: Establish the chapter's core situation and emotional tone",
            "scene_2": "Development: Progress the chapter's central tension or revelation",
            "scene_3": "Turning Point: Shift perspective or introduce new information",
        },
        "mystery": {
            "scene_1": "Investigation: Gather clues or interview suspects",
            "scene_2": "Discovery: Uncover contradictions or hidden motives",
            "scene_3": "Confrontation: Challenge assumptions or suspects",
        },
        "gentlefemdom": {
            "scene_1": "Negotiation: Explore needs, boundaries, or desires",
            "scene_2": "Expression: Show the dynamic in action through interaction",
            "scene_3": "Reflection: Process emotions and deepen understanding",
        },
    }

    def __init__(self, genre: str = "netorare"):
        """Initialize scene builder.

        Args:
            genre: Genre identifier (netorare, mystery, gentlefemdom)
        """
        self.genre = genre
        self.scenes_per_chapter = self.SCENES_PER_CHAPTER

    def build_scenes_from_chapter(
        self,
        chapter: ChapterOutline,
        story_id: str,
    ) -> List[SceneOutline]:
        """Build template scenes from a single chapter outline.

        Args:
            chapter: ChapterOutline to derive scenes from
            story_id: Story ID for scene references (not used in SceneOutline currently)

        Returns:
            List of SceneOutline objects with draft status
        """
        scenes = []

        # Create 1-2 scenes per chapter depending on chapter complexity
        num_scenes = self._determine_scene_count(chapter)

        for position in range(1, num_scenes + 1):
            scene = SceneOutline(
                id=self._generate_scene_id(chapter.chapter_number, position),
                chapter_id=f"chapter_{chapter.chapter_number:02d}",
                status=SceneStatus.DRAFT,
                # Draft status requires only id and chapter_id
                # Author to add pov_character_id, participants, goals, etc.
            )
            scenes.append(scene)

        return scenes

    def build_scenes_from_chapters(
        self,
        chapters: List[ChapterOutline],
        story_id: str,
    ) -> List[SceneOutline]:
        """Build template scenes from multiple chapter outlines.

        Args:
            chapters: List of ChapterOutline objects
            story_id: Story ID for scene references

        Returns:
            Flat list of all generated SceneOutline objects
        """
        all_scenes = []
        for chapter in chapters:
            chapter_scenes = self.build_scenes_from_chapter(chapter, story_id)
            all_scenes.extend(chapter_scenes)
        return all_scenes

    def _determine_scene_count(self, chapter: ChapterOutline) -> int:
        """Determine how many scenes a chapter should have.

        Currently uses a simple heuristic: most chapters get 2 scenes.
        Advanced versions could consider chapter length, phase, complexity.

        Args:
            chapter: ChapterOutline to analyze

        Returns:
            Number of scenes (typically 1-3)
        """
        # Midpoint chapters get 3 scenes; most others get 2
        if chapter.phase == 5:  # Midpoint
            return 3
        # Climax chapters get 3 scenes
        if chapter.phase == 8:  # Climax
            return 3
        # Default: 2 scenes
        return 2

    def _generate_scene_id(self, chapter_num: int, position: int) -> str:
        """Generate a unique scene ID.

        Format: scene_{chapter:02d}_{position:02d}

        Args:
            chapter_num: Chapter number (1-indexed)
            position: Scene position within chapter (1-indexed)

        Returns:
            Scene ID string
        """
        return f"scene_{chapter_num:02d}_{position:02d}"

    def _generate_scene_title(
        self,
        chapter: ChapterOutline,
        position: int,
    ) -> str:
        """Generate a descriptive scene title.

        Args:
            chapter: ChapterOutline this scene belongs to
            position: Scene position (1-indexed)

        Returns:
            Scene title string
        """
        # Use chapter title as basis
        chapter_title = chapter.title or f"Chapter {chapter.chapter_number}"

        # Add position indicator
        if position == 1:
            return f"{chapter_title} - Opening"
        elif position == 2:
            return f"{chapter_title} - Development"
        else:
            return f"{chapter_title} - Climax"
