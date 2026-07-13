"""Scene Inspector for Layer 3 narrative realization.

Provides inspection and reporting on scene structure, coverage, and status.

Key Features:
- Display complete scene sequence for chapters
- Show POV characters and participants
- Report arc beat realization coverage
- Identify missing or incomplete scenes
- Show validation status and coverage metrics
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set
from auteur.narrative_realization.schema.scene_outline import (
    SceneOutline,
    SceneStatus,
)


class SceneInspector:
    """Inspector for scene coverage and status reporting.

    Provides human-readable reports on:
    - Scene sequence and hierarchy
    - POV character coverage
    - Participant involvement
    - Arc beat realization status
    - Validation readiness (draft vs. ready)
    """

    def __init__(self):
        """Initialize scene inspector."""
        self.scenes: Dict[str, SceneOutline] = {}
        self.chapters: Dict[str, List[SceneOutline]] = {}

    def add_scene(self, scene: SceneOutline) -> None:
        """Add a scene to the inspector.

        Args:
            scene: SceneOutline to analyze
        """
        self.scenes[scene.id] = scene

        # Index by chapter
        if scene.chapter_id not in self.chapters:
            self.chapters[scene.chapter_id] = []
        self.chapters[scene.chapter_id].append(scene)

    def add_scenes(self, scenes: List[SceneOutline]) -> None:
        """Add multiple scenes to the inspector.

        Args:
            scenes: List of SceneOutline objects
        """
        for scene in scenes:
            self.add_scene(scene)

    def show_scene_tree(self) -> str:
        """Display complete scene tree organized by chapter.

        Returns:
            Formatted string showing chapter → scenes hierarchy
        """
        if not self.chapters:
            return "No scenes found"

        lines = []
        lines.append("Scene Tree")
        lines.append("=" * 70)

        for chapter_id in sorted(self.chapters.keys()):
            chapter_scenes = self.chapters[chapter_id]
            lines.append(f"\n{chapter_id.upper()}")
            lines.append("-" * 70)

            for scene in sorted(chapter_scenes, key=lambda s: s.narrative_position or 0):
                status_marker = self._status_marker(scene.status)
                lines.append(
                    f"  {status_marker} {scene.id}"
                )

                # Show POV character if set
                if scene.pov_character_id:
                    lines.append(f"     POV: {scene.pov_character_id}")

                # Show participants
                if scene.participants:
                    participants_str = ", ".join(scene.participants[:3])
                    if len(scene.participants) > 3:
                        participants_str += f" (+{len(scene.participants) - 3} more)"
                    lines.append(f"     With: {participants_str}")

                # Show temporal relations if present
                if scene.temporal_relation:
                    if scene.temporal_relation.follows_scene:
                        lines.append(
                            f"     Follows: {scene.temporal_relation.follows_scene}"
                        )
                    if scene.temporal_relation.parallel_with:
                        parallel_str = ", ".join(scene.temporal_relation.parallel_with)
                        lines.append(f"     Parallel: {parallel_str}")

        return "\n".join(lines)

    def show_pov_coverage(self) -> str:
        """Display POV character coverage across scenes.

        Returns:
            Report of which characters have POV scenes
        """
        pov_characters: Dict[Optional[str], int] = {}
        for scene in self.scenes.values():
            pov = scene.pov_character_id or "UNKNOWN"
            pov_characters[pov] = pov_characters.get(pov, 0) + 1

        if not pov_characters:
            return "No POV information available"

        lines = []
        lines.append("POV Character Coverage")
        lines.append("=" * 70)

        for pov in sorted(pov_characters.keys()):
            count = pov_characters[pov]
            lines.append(f"  {pov}: {count} scene{'s' if count != 1 else ''}")

        lines.append("")
        lines.append(f"Total: {len(self.scenes)} scenes across {len(pov_characters)} POV(s)")

        return "\n".join(lines)

    def show_participant_coverage(self) -> str:
        """Display which characters appear in scenes.

        Returns:
            Report of character participation
        """
        participant_count: Dict[str, int] = {}
        for scene in self.scenes.values():
            for participant in scene.participants:
                participant_count[participant] = participant_count.get(participant, 0) + 1

        if not participant_count:
            return "No participants recorded"

        lines = []
        lines.append("Character Participation")
        lines.append("=" * 70)

        for char in sorted(participant_count.keys(), key=lambda c: participant_count[c], reverse=True):
            count = participant_count[char]
            lines.append(f"  {char}: {count} appearance{'s' if count != 1 else ''}")

        lines.append("")
        lines.append(f"Total: {len(participant_count)} characters across {len(self.scenes)} scenes")

        return "\n".join(lines)

    def show_arc_beat_coverage(self) -> str:
        """Display arc beat realization coverage.

        Returns:
            Report of which arc beats have been realized in scenes
        """
        arc_beats: Dict[str, int] = {}
        scenes_with_arcs = 0

        for scene in self.scenes.values():
            if scene.arc_beat_realizations:
                scenes_with_arcs += 1
                for arc_beat in scene.arc_beat_realizations:
                    beat_id = arc_beat.arc_beat_id if hasattr(arc_beat, 'arc_beat_id') else str(arc_beat)
                    arc_beats[beat_id] = arc_beats.get(beat_id, 0) + 1

        if not arc_beats:
            return "No arc beat realizations recorded"

        lines = []
        lines.append("Arc Beat Realization Coverage")
        lines.append("=" * 70)

        for beat in sorted(arc_beats.keys()):
            count = arc_beats[beat]
            lines.append(f"  {beat}: realized in {count} scene{'s' if count != 1 else ''}")

        lines.append("")
        lines.append(
            f"Total: {len(arc_beats)} arc beats realized in {scenes_with_arcs} scenes"
        )

        return "\n".join(lines)

    def show_status_summary(self) -> str:
        """Display scene status distribution.

        Returns:
            Report showing count of draft/incomplete/ready scenes
        """
        status_counts = {
            SceneStatus.DRAFT: 0,
            SceneStatus.INCOMPLETE: 0,
            SceneStatus.READY: 0,
        }

        for scene in self.scenes.values():
            if scene.status in status_counts:
                status_counts[scene.status] += 1

        lines = []
        lines.append("Scene Status Summary")
        lines.append("=" * 70)

        for status in [SceneStatus.DRAFT, SceneStatus.INCOMPLETE, SceneStatus.READY]:
            count = status_counts[status]
            lines.append(f"  {status.value.upper()}: {count} scene{'s' if count != 1 else ''}")

        lines.append("")
        lines.append(f"Total: {len(self.scenes)} scenes")

        # Calculate readiness percentage
        ready_count = status_counts[SceneStatus.READY]
        if len(self.scenes) > 0:
            readiness = (ready_count / len(self.scenes)) * 100
            lines.append(f"Readiness: {readiness:.1f}%")

        return "\n".join(lines)

    def show_completeness(self) -> str:
        """Display scene completeness metrics.

        Reports which scenes have core fields filled in.

        Returns:
            Report of completeness indicators
        """
        completeness_metrics = {
            "has_pov": 0,
            "has_participants": 0,
            "has_goal": 0,
            "has_opposition": 0,
            "has_entry_state": 0,
            "has_exit_state": 0,
            "fully_complete": 0,
        }

        for scene in self.scenes.values():
            if scene.pov_character_id:
                completeness_metrics["has_pov"] += 1
            if scene.participants:
                completeness_metrics["has_participants"] += 1
            if scene.goal and scene.goal.objective:
                completeness_metrics["has_goal"] += 1
            if scene.opposition and scene.opposition.pressure:
                completeness_metrics["has_opposition"] += 1
            if scene.entry_state:
                completeness_metrics["has_entry_state"] += 1
            if scene.exit_state:
                completeness_metrics["has_exit_state"] += 1

            # Count fully complete if all core fields are set
            if (
                scene.pov_character_id
                and scene.participants
                and scene.goal
                and scene.opposition
                and scene.entry_state
                and scene.exit_state
            ):
                completeness_metrics["fully_complete"] += 1

        lines = []
        lines.append("Scene Completeness Metrics")
        lines.append("=" * 70)

        total = len(self.scenes)
        for metric in [
            "has_pov",
            "has_participants",
            "has_goal",
            "has_opposition",
            "has_entry_state",
            "has_exit_state",
        ]:
            count = completeness_metrics[metric]
            pct = (count / total * 100) if total > 0 else 0
            metric_name = metric.replace("_", " ").title()
            lines.append(f"  {metric_name}: {count}/{total} ({pct:.1f}%)")

        lines.append("")
        fully_complete = completeness_metrics["fully_complete"]
        fully_pct = (fully_complete / total * 100) if total > 0 else 0
        lines.append(
            f"Fully Complete: {fully_complete}/{total} ({fully_pct:.1f}%)"
        )

        return "\n".join(lines)

    def _status_marker(self, status: SceneStatus) -> str:
        """Get a visual marker for scene status.

        Args:
            status: SceneStatus value

        Returns:
            Short status marker string
        """
        markers = {
            SceneStatus.DRAFT: "[D]",
            SceneStatus.INCOMPLETE: "[I]",
            SceneStatus.READY: "[R]",
        }
        return markers.get(status, "[?]")
