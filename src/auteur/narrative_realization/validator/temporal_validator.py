"""Temporal consistency validator for Layer 3 narrative realization.

Validates temporal relationships and positioning of scenes:
- Unique narrative_position within chapter (reading order)
- Valid temporal relations (parallel_with, follows_scene)
- Mutual parallel_with relationships (if A parallel B, then B parallel A)
- No circular temporal dependency chains
- Distinction between narrative_position (reading order) and story_time (world time)

A scene has two temporal dimensions:
1. narrative_position: How it's encountered by reader (always linear within chapter)
2. story_time: When it occurs in story world (can have simultaneous events)

Temporal relations track story-world simultaneity:
- parallel_with: Scenes that occur at same time but different POVs/locations
- follows_scene: Scene that must complete before this begins

Validation rules:
1. narrative_position unique within chapter
2. parallel_with relationships must be mutual
3. No circular parallel_with chains (A parallel B parallel C parallel A is invalid)
4. follows_scene must reference existing scene
5. Scene cannot follow/parallel itself
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum

from auteur.narrative_realization.schema.scene_outline import SceneOutline, SceneStatus


class TemporalViolationType(str, Enum):
    """Types of temporal relationship violations."""

    DUPLICATE_POSITION = "duplicate_position"
    NON_MUTUAL_PARALLEL = "non_mutual_parallel"
    CIRCULAR_PARALLEL = "circular_parallel"
    INVALID_FOLLOWS_REFERENCE = "invalid_follows_reference"
    SELF_REFERENCE = "self_reference"
    POSITION_AFTER_FOLLOWS = "position_after_follows"
    MISSING_POSITION = "missing_position"


@dataclass
class TemporalViolation:
    """A single temporal consistency violation.

    Attributes:
        scene_id: Scene with temporal issue
        violation_type: Type of violation (from TemporalViolationType)
        related_scene_id: Other scene involved (if applicable)
        message: Human-readable error message
        suggestion: How to fix the violation
    """

    scene_id: str
    violation_type: TemporalViolationType
    related_scene_id: Optional[str]
    message: str
    suggestion: str


@dataclass
class TemporalValidationResult:
    """Result of temporal validation.

    Attributes:
        is_valid: True if all temporal checks pass
        violations: List of TemporalViolation objects
        warnings: Non-critical issues to review
    """

    is_valid: bool
    violations: List[TemporalViolation]
    warnings: List[str]


class TemporalValidator:
    """Validates temporal consistency across scenes.

    The TemporalValidator ensures that:
    1. narrative_position values are unique within each chapter
    2. temporal_relation.parallel_with references are mutual
    3. No circular parallel_with chains exist
    4. follows_scene references point to existing scenes
    5. narrative_position is used for reading order (always linear)
    6. story_time is used for story-world simultaneity

    Attributes:
        scenes: Dictionary mapping scene_id to SceneOutline
        violations: List of TemporalViolation found
    """

    def __init__(self):
        """Initialize empty TemporalValidator."""
        self.scenes: Dict[str, SceneOutline] = {}
        self.violations: List[TemporalViolation] = []

    def add_scene(self, scene: SceneOutline) -> None:
        """Add a scene to validate.

        Args:
            scene: SceneOutline to validate
        """
        self.scenes[scene.id] = scene

    def validate_scene(self, scene: SceneOutline) -> TemporalValidationResult:
        """Validate temporal consistency for a single scene.

        Args:
            scene: Scene to validate

        Returns:
            TemporalValidationResult with violations and warnings
        """
        violations: List[TemporalViolation] = []
        warnings: List[str] = []

        # Skip draft scenes
        if scene.status == SceneStatus.DRAFT:
            return TemporalValidationResult(
                is_valid=True, violations=violations, warnings=warnings
            )

        # Validate individual scene constraints
        violations.extend(self.validate_self_reference(scene))
        violations.extend(self.validate_temporal_relations(scene))

        is_valid = len(violations) == 0
        return TemporalValidationResult(
            is_valid=is_valid, violations=violations, warnings=warnings
        )

    def validate_all_scenes(self) -> TemporalValidationResult:
        """Validate temporal consistency across all added scenes.

        Runs all temporal checks including cross-scene relationships.

        Returns:
            TemporalValidationResult with all violations found
        """
        all_violations: List[TemporalViolation] = []
        all_warnings: List[str] = []

        # Validate individual scenes
        for scene in self.scenes.values():
            result = self.validate_scene(scene)
            all_violations.extend(result.violations)
            all_warnings.extend(result.warnings)

        # Validate cross-scene constraints
        all_violations.extend(self.validate_unique_positions())
        all_violations.extend(self.validate_temporal_relations_mutual())
        all_violations.extend(self.validate_no_circular_parallels())

        is_valid = len(all_violations) == 0
        return TemporalValidationResult(
            is_valid=is_valid,
            violations=all_violations,
            warnings=all_warnings,
        )

    def validate_unique_positions(self) -> List[TemporalViolation]:
        """Validate narrative_position is unique within each chapter.

        narrative_position is reading order (always sequential).
        Two scenes cannot have same position within same chapter.

        Returns:
            List of violations (duplicate positions)
        """
        violations: List[TemporalViolation] = []

        # Group scenes by chapter
        chapters: Dict[str, List[SceneOutline]] = {}
        for scene in self.scenes.values():
            if scene.status == SceneStatus.DRAFT:
                continue  # Skip draft scenes
            if scene.chapter_id not in chapters:
                chapters[scene.chapter_id] = []
            chapters[scene.chapter_id].append(scene)

        # Check each chapter for duplicate positions
        for chapter_id, chapter_scenes in chapters.items():
            positions: Dict[int, List[str]] = {}
            for scene in chapter_scenes:
                if scene.narrative_position is not None:
                    pos = scene.narrative_position
                    if pos not in positions:
                        positions[pos] = []
                    positions[pos].append(scene.id)

            # Report duplicates
            for pos, scene_ids in positions.items():
                if len(scene_ids) > 1:
                    for scene_id in scene_ids:
                        violations.append(
                            TemporalViolation(
                                scene_id=scene_id,
                                violation_type=TemporalViolationType.DUPLICATE_POSITION,
                                related_scene_id=None,
                                message=f"Narrative position {pos} is shared with {len(scene_ids) - 1} other scene(s) in chapter {chapter_id}",
                                suggestion=f"Change narrative_position of one or more scenes to avoid duplicates within chapter",
                            )
                        )

        return violations

    def validate_temporal_relations(
        self, scene: SceneOutline
    ) -> List[TemporalViolation]:
        """Validate temporal relation references.

        - follows_scene must reference existing scene
        - No self-reference in parallel_with or follows_scene
        - All references must be valid scene IDs

        Args:
            scene: Scene to validate

        Returns:
            List of violations in temporal relations
        """
        violations: List[TemporalViolation] = []

        if not scene.temporal_relation:
            return violations

        tr = scene.temporal_relation

        # Check follows_scene reference
        if tr.follows_scene:
            if tr.follows_scene == scene.id:
                violations.append(
                    TemporalViolation(
                        scene_id=scene.id,
                        violation_type=TemporalViolationType.SELF_REFERENCE,
                        related_scene_id=None,
                        message=f"Scene cannot follow itself",
                        suggestion=f"Remove follows_scene: {tr.follows_scene}",
                    )
                )
            elif tr.follows_scene not in self.scenes:
                violations.append(
                    TemporalViolation(
                        scene_id=scene.id,
                        violation_type=TemporalViolationType.INVALID_FOLLOWS_REFERENCE,
                        related_scene_id=tr.follows_scene,
                        message=f"follows_scene references non-existent scene: {tr.follows_scene}",
                        suggestion=f"Verify {tr.follows_scene} exists or create it",
                    )
                )

        # Check parallel_with references
        for parallel_scene_id in tr.parallel_with:
            if parallel_scene_id == scene.id:
                violations.append(
                    TemporalViolation(
                        scene_id=scene.id,
                        violation_type=TemporalViolationType.SELF_REFERENCE,
                        related_scene_id=None,
                        message=f"Scene cannot be parallel with itself",
                        suggestion=f"Remove {parallel_scene_id} from parallel_with",
                    )
                )
            elif parallel_scene_id not in self.scenes:
                violations.append(
                    TemporalViolation(
                        scene_id=scene.id,
                        violation_type=TemporalViolationType.INVALID_FOLLOWS_REFERENCE,
                        related_scene_id=parallel_scene_id,
                        message=f"parallel_with references non-existent scene: {parallel_scene_id}",
                        suggestion=f"Verify {parallel_scene_id} exists or create it",
                    )
                )

        return violations

    def validate_temporal_relations_mutual(self) -> List[TemporalViolation]:
        """Validate parallel_with relationships are mutual.

        If scene A is parallel_with scene B, then scene B must be
        parallel_with scene A.

        Returns:
            List of violations (non-mutual parallels)
        """
        violations: List[TemporalViolation] = []

        for scene in self.scenes.values():
            if not scene.temporal_relation:
                continue

            for parallel_id in scene.temporal_relation.parallel_with:
                if parallel_id not in self.scenes:
                    continue  # Already caught by other validator

                parallel_scene = self.scenes[parallel_id]
                if not parallel_scene.temporal_relation:
                    violations.append(
                        TemporalViolation(
                            scene_id=scene.id,
                            violation_type=TemporalViolationType.NON_MUTUAL_PARALLEL,
                            related_scene_id=parallel_id,
                            message=f"{scene.id} is parallel_with {parallel_id}, but {parallel_id} does not reference {scene.id}",
                            suggestion=f"Add {scene.id} to {parallel_id}'s parallel_with list",
                        )
                    )
                elif scene.id not in parallel_scene.temporal_relation.parallel_with:
                    violations.append(
                        TemporalViolation(
                            scene_id=scene.id,
                            violation_type=TemporalViolationType.NON_MUTUAL_PARALLEL,
                            related_scene_id=parallel_id,
                            message=f"{scene.id} is parallel_with {parallel_id}, but {parallel_id} does not reference {scene.id}",
                            suggestion=f"Add {scene.id} to {parallel_id}'s parallel_with list",
                        )
                    )

        return violations

    def validate_no_circular_parallels(self) -> List[TemporalViolation]:
        """Validate no circular parallel_with chains.

        A→B→C→A circular chain is invalid (would create impossible simultaneity).

        Returns:
            List of violations (circular dependencies)
        """
        violations: List[TemporalViolation] = []

        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(scene_id: str, path: List[str]) -> Tuple[bool, List[str]]:
            """Detect cycle in parallel_with graph."""
            visited.add(scene_id)
            rec_stack.add(scene_id)
            path.append(scene_id)

            if scene_id not in self.scenes:
                return False, path

            scene = self.scenes[scene_id]
            if not scene.temporal_relation:
                rec_stack.remove(scene_id)
                return False, path

            for neighbor in scene.temporal_relation.parallel_with:
                if neighbor not in visited:
                    is_cycle, cycle_path = has_cycle(neighbor, path[:])
                    if is_cycle:
                        return True, cycle_path
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_path = path[path.index(neighbor) :] + [neighbor]
                    return True, cycle_path

            rec_stack.remove(scene_id)
            return False, path

        # Check each scene for cycles
        for scene_id in self.scenes:
            if scene_id not in visited:
                is_cycle, cycle_path = has_cycle(scene_id, [])
                if is_cycle:
                    # Report all scenes in cycle
                    cycle_str = " → ".join(cycle_path)
                    for scene_in_cycle in cycle_path[:-1]:  # Exclude last (duplicate)
                        violations.append(
                            TemporalViolation(
                                scene_id=scene_in_cycle,
                                violation_type=TemporalViolationType.CIRCULAR_PARALLEL,
                                related_scene_id=None,
                                message=f"Circular parallel_with chain detected: {cycle_str}",
                                suggestion=f"Remove one or more parallel_with references to break the cycle",
                            )
                        )

        return violations

    def validate_position_vs_time_distinction(self) -> List[TemporalViolation]:
        """Validate correct use of narrative_position vs story_time.

        narrative_position = reading order (always linear, no duplicates per chapter)
        story_time = when in story world (can be simultaneous)

        Returns:
            List of violations (confusion between position and time)
        """
        violations: List[TemporalViolation] = []

        # Check that position is always set for ready scenes
        for scene in self.scenes.values():
            if scene.status == SceneStatus.READY:
                if scene.narrative_position is None:
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

    def validate_chronological_consistency(self) -> List[TemporalViolation]:
        """Validate chronological consistency between position and follows_scene.

        If scene A follows scene B, A's narrative_position should be > B's
        within the same chapter (unless in parallel).

        Returns:
            List of violations in chronological ordering
        """
        violations: List[TemporalViolation] = []

        for scene in self.scenes.values():
            if not scene.temporal_relation or not scene.temporal_relation.follows_scene:
                continue

            if scene.narrative_position is None:
                continue

            follows_id = scene.temporal_relation.follows_scene
            if follows_id not in self.scenes:
                continue  # Already caught by other validator

            follows_scene = self.scenes[follows_id]
            if follows_scene.narrative_position is None:
                continue

            # Both in same chapter?
            if scene.chapter_id == follows_scene.chapter_id:
                # Scene should come after what it follows
                if scene.narrative_position <= follows_scene.narrative_position:
                    violations.append(
                        TemporalViolation(
                            scene_id=scene.id,
                            violation_type=TemporalViolationType.POSITION_AFTER_FOLLOWS,
                            related_scene_id=follows_id,
                            message=f"{scene.id} (position {scene.narrative_position}) follows {follows_id} (position {follows_scene.narrative_position}), but narrative position is not greater",
                            suggestion=f"Increase {scene.id}'s narrative_position to be greater than {follows_id}'s",
                        )
                    )

        return violations

    def report_temporal_violations(
        self, violations: List[TemporalViolation]
    ) -> str:
        """Generate human-readable report of temporal violations.

        Args:
            violations: List of violations to report

        Returns:
            Formatted string with all violations explained
        """
        if not violations:
            return "No temporal violations found."

        report_lines = [f"Found {len(violations)} temporal violation(s):\n"]

        for violation in violations:
            report_lines.append(f"  Scene: {violation.scene_id}")
            report_lines.append(f"  Type: {violation.violation_type.value}")
            if violation.related_scene_id:
                report_lines.append(f"  Related: {violation.related_scene_id}")
            report_lines.append(f"  Issue: {violation.message}")
            report_lines.append(f"  Fix: {violation.suggestion}")
            report_lines.append("")

        return "\n".join(report_lines)
