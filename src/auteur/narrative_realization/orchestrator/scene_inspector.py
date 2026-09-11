"""Scene inspection and coverage reporting for Layer 3 narrative realization."""

from __future__ import annotations

from typing import Dict, List, Optional

from auteur.narrative_realization.schema.scene_outline import SceneOutline, SceneStatus


class SceneInspector:
    """Provide read-only human-facing reports over a set of SceneOutline objects."""

    def __init__(self) -> None:
        self.scenes: Dict[str, SceneOutline] = {}
        self.chapters: Dict[str, List[SceneOutline]] = {}

    def add_scene(self, scene: SceneOutline) -> None:
        self.scenes[scene.id] = scene
        self.chapters.setdefault(scene.chapter_id, []).append(scene)

    def add_scenes(self, scenes: List[SceneOutline]) -> None:
        for scene in scenes:
            self.add_scene(scene)

    def show_scene_tree(self) -> str:
        if not self.chapters:
            return "No scenes found"

        lines = ["Scene Tree", "=" * 70]
        for chapter_id in sorted(self.chapters):
            lines.extend([f"\n{chapter_id.upper()}", "-" * 70])
            for scene in sorted(
                self.chapters[chapter_id], key=lambda item: item.narrative_position or 0
            ):
                lines.append(f"  {self._status_marker(scene.status)} {scene.id}")
                if scene.pov_character_id:
                    lines.append(f"     POV: {scene.pov_character_id}")
                if scene.participants:
                    participants = ", ".join(scene.participants[:3])
                    if len(scene.participants) > 3:
                        participants += f" (+{len(scene.participants) - 3} more)"
                    lines.append(f"     With: {participants}")
                if scene.temporal_relation:
                    if scene.temporal_relation.follows_scene:
                        lines.append(f"     Follows: {scene.temporal_relation.follows_scene}")
                    if scene.temporal_relation.parallel_with:
                        lines.append(
                            "     Parallel: "
                            + ", ".join(scene.temporal_relation.parallel_with)
                        )
        return "\n".join(lines)

    def show_pov_coverage(self) -> str:
        pov_characters: Dict[Optional[str], int] = {}
        for scene in self.scenes.values():
            pov = scene.pov_character_id or "UNKNOWN"
            pov_characters[pov] = pov_characters.get(pov, 0) + 1

        if not pov_characters:
            return "No POV information available"

        lines = ["POV Character Coverage", "=" * 70]
        for pov in sorted(pov_characters):
            count = pov_characters[pov]
            lines.append(f"  {pov}: {count} scene{'s' if count != 1 else ''}")
        lines.extend(
            [
                "",
                f"Total: {len(self.scenes)} scenes across {len(pov_characters)} POV(s)",
            ]
        )
        return "\n".join(lines)

    def show_participant_coverage(self) -> str:
        participant_count: Dict[str, int] = {}
        for scene in self.scenes.values():
            for participant in scene.participants:
                participant_count[participant] = participant_count.get(participant, 0) + 1

        if not participant_count:
            return "No participants recorded"

        lines = ["Character Participation", "=" * 70]
        for participant in sorted(
            participant_count, key=lambda item: participant_count[item], reverse=True
        ):
            count = participant_count[participant]
            lines.append(
                f"  {participant}: {count} appearance{'s' if count != 1 else ''}"
            )
        lines.extend(
            [
                "",
                f"Total: {len(participant_count)} characters across {len(self.scenes)} scenes",
            ]
        )
        return "\n".join(lines)

    def show_arc_beat_coverage(self) -> str:
        """Report canonical SceneOutline ``realizes_arc_beats`` coverage."""
        arc_beats: Dict[str, int] = {}
        scenes_with_arcs = 0

        for scene in self.scenes.values():
            if not scene.realizes_arc_beats:
                continue
            scenes_with_arcs += 1
            for realization in scene.realizes_arc_beats:
                arc_beats[realization.beat_id] = arc_beats.get(realization.beat_id, 0) + 1

        if not arc_beats:
            return "No arc beat realizations recorded"

        lines = ["Arc Beat Realization Coverage", "=" * 70]
        for beat_id in sorted(arc_beats):
            count = arc_beats[beat_id]
            lines.append(
                f"  {beat_id}: realized in {count} scene{'s' if count != 1 else ''}"
            )
        lines.extend(
            [
                "",
                f"Total: {len(arc_beats)} arc beats realized in {scenes_with_arcs} scenes",
            ]
        )
        return "\n".join(lines)

    def show_status_summary(self) -> str:
        counts = {
            SceneStatus.DRAFT: 0,
            SceneStatus.INCOMPLETE: 0,
            SceneStatus.READY: 0,
        }
        for scene in self.scenes.values():
            if scene.status in counts:
                counts[scene.status] += 1

        lines = ["Scene Status Summary", "=" * 70]
        for status in (SceneStatus.DRAFT, SceneStatus.INCOMPLETE, SceneStatus.READY):
            count = counts[status]
            lines.append(
                f"  {status.value.upper()}: {count} scene{'s' if count != 1 else ''}"
            )
        lines.extend(["", f"Total: {len(self.scenes)} scenes"])
        if self.scenes:
            readiness = counts[SceneStatus.READY] / len(self.scenes) * 100
            lines.append(f"Readiness: {readiness:.1f}%")
        return "\n".join(lines)

    def show_completeness(self) -> str:
        metrics = {
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
                metrics["has_pov"] += 1
            if scene.participants:
                metrics["has_participants"] += 1
            if scene.goal and scene.goal.objective:
                metrics["has_goal"] += 1
            if scene.opposition and scene.opposition.pressure:
                metrics["has_opposition"] += 1
            if scene.entry_state:
                metrics["has_entry_state"] += 1
            if scene.exit_state:
                metrics["has_exit_state"] += 1
            if (
                scene.pov_character_id
                and scene.participants
                and scene.goal
                and scene.opposition
                and scene.entry_state is not None
                and scene.exit_state is not None
            ):
                metrics["fully_complete"] += 1

        total = len(self.scenes)
        lines = ["Scene Completeness Metrics", "=" * 70]
        for metric in (
            "has_pov",
            "has_participants",
            "has_goal",
            "has_opposition",
            "has_entry_state",
            "has_exit_state",
        ):
            count = metrics[metric]
            pct = count / total * 100 if total else 0
            lines.append(f"  {metric.replace('_', ' ').title()}: {count}/{total} ({pct:.1f}%)")

        fully_complete = metrics["fully_complete"]
        fully_pct = fully_complete / total * 100 if total else 0
        lines.extend(["", f"Fully Complete: {fully_complete}/{total} ({fully_pct:.1f}%)"])
        return "\n".join(lines)

    def _status_marker(self, status: SceneStatus) -> str:
        return {
            SceneStatus.DRAFT: "[D]",
            SceneStatus.INCOMPLETE: "[I]",
            SceneStatus.READY: "[R]",
        }.get(status, "[?]")
