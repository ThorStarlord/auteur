"""Temporal consistency validator for Layer 3 narrative realization.

The validator treats ``narrative_position`` as reader order and ``story_time``
as story-world time. Parallel relations are symmetric; ``follows_scene`` is a
directional dependency and may not contradict reader order inside a chapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from auteur.narrative_realization.schema.scene_outline import SceneOutline, SceneStatus


class TemporalViolationType(str, Enum):
    DUPLICATE_POSITION = "duplicate_position"
    NON_MUTUAL_PARALLEL = "non_mutual_parallel"
    CIRCULAR_PARALLEL = "circular_parallel"  # historical public value: follows-cycle
    INVALID_FOLLOWS_REFERENCE = "invalid_follows_reference"
    SELF_REFERENCE = "self_reference"
    POSITION_AFTER_FOLLOWS = "position_after_follows"
    MISSING_POSITION = "missing_position"


@dataclass
class TemporalViolation:
    scene_id: str
    violation_type: TemporalViolationType
    related_scene_id: Optional[str]
    message: str
    suggestion: str


@dataclass
class TemporalValidationResult:
    is_valid: bool
    violations: list[TemporalViolation]
    warnings: list[str]


class TemporalValidator:
    """Validate deterministic temporal invariants across SceneOutline objects."""

    def __init__(self) -> None:
        self.scenes: dict[str, SceneOutline] = {}
        self.violations: list[TemporalViolation] = []

    def add_scene(self, scene: SceneOutline) -> None:
        self.scenes[scene.id] = scene

    def validate_scene(self, scene: SceneOutline) -> TemporalValidationResult:
        if scene.status == SceneStatus.DRAFT:
            return TemporalValidationResult(True, [], [])

        violations = [
            *self.validate_self_reference(scene),
            *self.validate_temporal_relations(scene),
        ]
        return TemporalValidationResult(not violations, violations, [])

    def validate_all_scenes(self) -> TemporalValidationResult:
        """Run every cross-scene temporal check advertised by this validator."""
        violations: list[TemporalViolation] = []
        warnings: list[str] = []

        for scene in self.scenes.values():
            result = self.validate_scene(scene)
            violations.extend(result.violations)
            warnings.extend(result.warnings)

        violations.extend(self.validate_unique_positions())
        violations.extend(self.validate_temporal_relations_mutual())
        violations.extend(self.validate_no_circular_follows_chains())
        violations.extend(self.validate_position_vs_time_distinction())
        violations.extend(self.validate_chronological_consistency())

        return TemporalValidationResult(not violations, violations, warnings)

    def validate_unique_positions(self) -> list[TemporalViolation]:
        violations: list[TemporalViolation] = []
        chapters: dict[str, list[SceneOutline]] = {}
        for scene in self.scenes.values():
            if scene.status != SceneStatus.DRAFT:
                chapters.setdefault(scene.chapter_id, []).append(scene)

        for chapter_id, chapter_scenes in chapters.items():
            positions: dict[int, list[str]] = {}
            for scene in chapter_scenes:
                if scene.narrative_position is not None:
                    positions.setdefault(scene.narrative_position, []).append(scene.id)
            for position, scene_ids in positions.items():
                if len(scene_ids) <= 1:
                    continue
                for scene_id in scene_ids:
                    violations.append(
                        TemporalViolation(
                            scene_id=scene_id,
                            violation_type=TemporalViolationType.DUPLICATE_POSITION,
                            related_scene_id=None,
                            message=(
                                f"Narrative position {position} is shared with "
                                f"{len(scene_ids) - 1} other scene(s) in chapter {chapter_id}"
                            ),
                            suggestion=(
                                "Change narrative_position of one or more scenes to avoid "
                                "duplicates within chapter"
                            ),
                        )
                    )
        return violations

    def validate_self_reference(self, scene: SceneOutline) -> list[TemporalViolation]:
        """Retain a defensive check for deserialized/legacy scene objects."""
        if not scene.temporal_relation:
            return []

        violations: list[TemporalViolation] = []
        relation = scene.temporal_relation
        if relation.follows_scene == scene.id:
            violations.append(
                TemporalViolation(
                    scene_id=scene.id,
                    violation_type=TemporalViolationType.SELF_REFERENCE,
                    related_scene_id=None,
                    message="Scene cannot follow itself",
                    suggestion="Remove follows_scene or set it to another scene",
                )
            )
        if scene.id in relation.parallel_with:
            violations.append(
                TemporalViolation(
                    scene_id=scene.id,
                    violation_type=TemporalViolationType.SELF_REFERENCE,
                    related_scene_id=None,
                    message="Scene cannot be parallel with itself",
                    suggestion="Remove scene from its own parallel_with list",
                )
            )
        return violations

    def validate_temporal_relations(self, scene: SceneOutline) -> list[TemporalViolation]:
        if not scene.temporal_relation:
            return []

        violations: list[TemporalViolation] = []
        relation = scene.temporal_relation
        if relation.follows_scene:
            if relation.follows_scene == scene.id:
                violations.append(
                    TemporalViolation(
                        scene_id=scene.id,
                        violation_type=TemporalViolationType.SELF_REFERENCE,
                        related_scene_id=None,
                        message="Scene cannot follow itself",
                        suggestion=f"Remove follows_scene: {relation.follows_scene}",
                    )
                )
            elif relation.follows_scene not in self.scenes:
                violations.append(
                    TemporalViolation(
                        scene_id=scene.id,
                        violation_type=TemporalViolationType.INVALID_FOLLOWS_REFERENCE,
                        related_scene_id=relation.follows_scene,
                        message=(
                            "follows_scene references non-existent scene: "
                            f"{relation.follows_scene}"
                        ),
                        suggestion=f"Verify {relation.follows_scene} exists or create it",
                    )
                )

        for parallel_id in relation.parallel_with:
            if parallel_id == scene.id:
                violations.append(
                    TemporalViolation(
                        scene_id=scene.id,
                        violation_type=TemporalViolationType.SELF_REFERENCE,
                        related_scene_id=None,
                        message="Scene cannot be parallel with itself",
                        suggestion=f"Remove {parallel_id} from parallel_with",
                    )
                )
            elif parallel_id not in self.scenes:
                violations.append(
                    TemporalViolation(
                        scene_id=scene.id,
                        violation_type=TemporalViolationType.INVALID_FOLLOWS_REFERENCE,
                        related_scene_id=parallel_id,
                        message=f"parallel_with references non-existent scene: {parallel_id}",
                        suggestion=f"Verify {parallel_id} exists or create it",
                    )
                )
        return violations

    def validate_temporal_relations_mutual(self) -> list[TemporalViolation]:
        violations: list[TemporalViolation] = []
        for scene in self.scenes.values():
            if not scene.temporal_relation:
                continue
            for parallel_id in scene.temporal_relation.parallel_with:
                parallel_scene = self.scenes.get(parallel_id)
                if parallel_scene is None:
                    continue
                if (
                    parallel_scene.temporal_relation is None
                    or scene.id not in parallel_scene.temporal_relation.parallel_with
                ):
                    violations.append(
                        TemporalViolation(
                            scene_id=scene.id,
                            violation_type=TemporalViolationType.NON_MUTUAL_PARALLEL,
                            related_scene_id=parallel_id,
                            message=(
                                f"{scene.id} is parallel_with {parallel_id}, but "
                                f"{parallel_id} does not reference {scene.id}"
                            ),
                            suggestion=f"Add {scene.id} to {parallel_id}'s parallel_with list",
                        )
                    )
        return violations

    def validate_no_circular_follows_chains(self) -> list[TemporalViolation]:
        """Reject cycles in the directional ``follows_scene`` graph only."""
        violations: list[TemporalViolation] = []
        visited: set[str] = set()
        active: list[str] = []
        active_set: set[str] = set()
        reported_cycles: set[frozenset[str]] = set()

        def visit(scene_id: str) -> None:
            if scene_id in active_set:
                start = active.index(scene_id)
                cycle = active[start:] + [scene_id]
                cycle_nodes = frozenset(cycle[:-1])
                if cycle_nodes in reported_cycles:
                    return
                reported_cycles.add(cycle_nodes)
                cycle_text = " → ".join(cycle)
                for member in cycle[:-1]:
                    violations.append(
                        TemporalViolation(
                            scene_id=member,
                            violation_type=TemporalViolationType.CIRCULAR_PARALLEL,
                            related_scene_id=None,
                            message=f"Circular follows_scene chain detected: {cycle_text}",
                            suggestion=(
                                "Remove or change follows_scene reference to break the cycle"
                            ),
                        )
                    )
                return
            if scene_id in visited:
                return

            visited.add(scene_id)
            active.append(scene_id)
            active_set.add(scene_id)
            scene = self.scenes.get(scene_id)
            if scene and scene.temporal_relation and scene.temporal_relation.follows_scene:
                follows_id = scene.temporal_relation.follows_scene
                if follows_id in self.scenes:
                    visit(follows_id)
            active.pop()
            active_set.remove(scene_id)

        for scene_id in self.scenes:
            visit(scene_id)
        return violations

    def validate_position_vs_time_distinction(self) -> list[TemporalViolation]:
        violations: list[TemporalViolation] = []
        for scene in self.scenes.values():
            if scene.status == SceneStatus.READY and scene.narrative_position is None:
                violations.append(
                    TemporalViolation(
                        scene_id=scene.id,
                        violation_type=TemporalViolationType.MISSING_POSITION,
                        related_scene_id=None,
                        message="Ready scene is missing narrative_position (reading order)",
                        suggestion="Set narrative_position to unique value within chapter",
                    )
                )
        return violations

    def validate_chronological_consistency(self) -> list[TemporalViolation]:
        violations: list[TemporalViolation] = []
        for scene in self.scenes.values():
            relation = scene.temporal_relation
            if not relation or not relation.follows_scene or scene.narrative_position is None:
                continue
            predecessor = self.scenes.get(relation.follows_scene)
            if predecessor is None or predecessor.narrative_position is None:
                continue
            if (
                scene.chapter_id == predecessor.chapter_id
                and scene.narrative_position <= predecessor.narrative_position
            ):
                violations.append(
                    TemporalViolation(
                        scene_id=scene.id,
                        violation_type=TemporalViolationType.POSITION_AFTER_FOLLOWS,
                        related_scene_id=predecessor.id,
                        message=(
                            f"{scene.id} (position {scene.narrative_position}) follows "
                            f"{predecessor.id} (position {predecessor.narrative_position}), "
                            "but narrative position is not greater"
                        ),
                        suggestion=(
                            f"Increase {scene.id}'s narrative_position to be greater than "
                            f"{predecessor.id}'s"
                        ),
                    )
                )
        return violations

    def report_temporal_violations(self, violations: list[TemporalViolation]) -> str:
        if not violations:
            return "No temporal violations found."

        lines = [f"Found {len(violations)} temporal violation(s):\n"]
        for violation in violations:
            lines.append(f"  Scene: {violation.scene_id}")
            lines.append(f"  Type: {violation.violation_type.value}")
            if violation.related_scene_id:
                lines.append(f"  Related: {violation.related_scene_id}")
            lines.append(f"  Issue: {violation.message}")
            lines.append(f"  Fix: {violation.suggestion}")
            lines.append("")
        return "\n".join(lines)
