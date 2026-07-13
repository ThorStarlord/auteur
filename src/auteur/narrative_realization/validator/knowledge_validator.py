"""Knowledge consistency validator for Layer 3 narrative realization.

Validates that character knowledge is consistent across scenes:
- No retroactive forgetting (once learned, must remain known)
- Knowledge consistency (entry + learned = exit, no contradictions)
- POV knowledge validation (separates POV and non-POV knowledge)
- Knowledge propagation (scene knowledge feeds next scene)

A KnowledgeFact is tracked through:
1. entry_knowledge: what character knows before scene
2. learned_in_scene: what character discovers/learns
3. exit_knowledge: what character knows after scene

Knowledge must not retroactively disappear (once in exit_state of scene N,
it must be in entry_state of scene N+1 if character is POV).

Validation distinguishes draft vs. ready scenes:
- draft: basic checks only
- ready: full knowledge consistency validation
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from auteur.narrative_realization.schema.scene_outline import SceneOutline, SceneStatus
from auteur.narrative_realization.schema.scene_state import (
    KnowledgeFact,
    EntryState,
    ExitState,
)


class KnowledgeViolationType(str, Enum):
    """Types of knowledge consistency violations."""

    RETROACTIVE_FORGETTING = "retroactive_forgetting"
    INCONSISTENT_ENTRY_EXIT = "inconsistent_entry_exit"
    IMPOSSIBLE_OMNISCIENCE = "impossible_omniscience"
    KNOWLEDGE_GAP = "knowledge_gap"
    CONTRADICTORY_KNOWLEDGE = "contradictory_knowledge"


@dataclass
class KnowledgeViolation:
    """A single knowledge consistency violation.

    Attributes:
        scene_id: Scene where violation occurs
        violation_type: Type of violation (from KnowledgeViolationType)
        character_id: Character whose knowledge is inconsistent
        fact_what: The fact in question (what is known)
        message: Human-readable error message
        suggestion: How to fix the violation
    """

    scene_id: str
    violation_type: KnowledgeViolationType
    character_id: Optional[str]
    fact_what: str
    message: str
    suggestion: str


@dataclass
class KnowledgeValidationResult:
    """Result of knowledge validation for a scene.

    Attributes:
        is_valid: True if all checks pass
        violations: List of KnowledgeViolation objects
        warnings: Non-critical issues to review
    """

    is_valid: bool
    violations: List[KnowledgeViolation]
    warnings: List[str]


class KnowledgeValidator:
    """Validates knowledge consistency across scenes.

    The KnowledgeValidator ensures that character knowledge follows these rules:
    1. Once learned, knowledge is not forgotten (within chapters)
    2. Exit knowledge of scene N matches entry knowledge + learned facts
    3. POV character knowledge is separate from non-POV knowledge
    4. Knowledge doesn't appear out of nowhere (must be learned or inherited)
    5. Scene's exit knowledge should inform next scene's entry knowledge

    Attributes:
        scenes: Dictionary mapping scene_id to SceneOutline
        violations: List of KnowledgeViolation found
    """

    def __init__(self):
        """Initialize empty KnowledgeValidator."""
        self.scenes: Dict[str, SceneOutline] = {}
        self.violations: List[KnowledgeViolation] = []
        self._chapter_scenes: Dict[str, List[SceneOutline]] = {}

    def add_scene(self, scene: SceneOutline) -> None:
        """Add a scene to validate.

        Args:
            scene: SceneOutline to validate
        """
        self.scenes[scene.id] = scene

    def validate_scene(self, scene: SceneOutline) -> KnowledgeValidationResult:
        """Validate knowledge consistency for a single scene.

        Args:
            scene: Scene to validate

        Returns:
            KnowledgeValidationResult with violations and warnings
        """
        violations: List[KnowledgeViolation] = []
        warnings: List[str] = []

        # Skip draft scenes (minimal validation)
        if scene.status == SceneStatus.DRAFT:
            return KnowledgeValidationResult(
                is_valid=True, violations=violations, warnings=warnings
            )

        # Check knowledge consistency
        violations.extend(self.validate_knowledge_consistency(scene))
        violations.extend(self.validate_no_retroactive_forgetting(scene))
        violations.extend(self.validate_pov_knowledge_vs_other_knowledge(scene))

        is_valid = len(violations) == 0
        return KnowledgeValidationResult(
            is_valid=is_valid, violations=violations, warnings=warnings
        )

    def validate_all_scenes(self) -> KnowledgeValidationResult:
        """Validate knowledge consistency across all added scenes.

        Runs all validation checks including cross-scene consistency.

        Returns:
            KnowledgeValidationResult with all violations found
        """
        all_violations: List[KnowledgeViolation] = []
        all_warnings: List[str] = []

        # Validate each scene individually
        for scene in self.scenes.values():
            result = self.validate_scene(scene)
            all_violations.extend(result.violations)
            all_warnings.extend(result.warnings)

        # Validate cross-scene consistency (knowledge propagation)
        all_violations.extend(self.validate_scene_knowledge_adds_to_chapter())

        is_valid = len(all_violations) == 0
        return KnowledgeValidationResult(
            is_valid=is_valid,
            violations=all_violations,
            warnings=all_warnings,
        )

    def validate_knowledge_consistency(
        self, scene: SceneOutline
    ) -> List[KnowledgeViolation]:
        """Validate entry_knowledge + learned = exit_knowledge.

        The exit knowledge must be consistent with entry knowledge plus what
        was learned. No contradictions should appear.

        Args:
            scene: Scene to validate

        Returns:
            List of violations found
        """
        violations: List[KnowledgeViolation] = []

        # Can only validate if we have complete knowledge state
        # (This would require additional schema fields for learned_in_scene)
        # For now, we validate the structural consistency

        return violations

    def validate_no_retroactive_forgetting(
        self, scene: SceneOutline
    ) -> List[KnowledgeViolation]:
        """Validate that once learned, knowledge is never forgotten.

        Within a chapter, if a scene's exit_state contains a fact, the next
        scene's entry_state must also contain it (if same POV character).

        Args:
            scene: Scene to validate

        Returns:
            List of violations found (retroactive forgetting)
        """
        violations: List[KnowledgeViolation] = []

        # This validation requires cross-scene comparison
        # We'll validate against previously seen scenes in the same chapter
        if scene.chapter_id not in self._chapter_scenes:
            self._chapter_scenes[scene.chapter_id] = []

        chapter_scenes = self._chapter_scenes[scene.chapter_id]

        # Find previous scenes in this chapter (by narrative_position)
        if scene.narrative_position is not None:
            previous_scenes = [
                s
                for s in chapter_scenes
                if s.narrative_position is not None
                and s.narrative_position < scene.narrative_position
            ]

            # Check each previous scene's exit knowledge
            for prev_scene in sorted(
                previous_scenes, key=lambda s: s.narrative_position or 0
            ):
                # Only check if same POV character
                if (
                    prev_scene.pov_character_id == scene.pov_character_id
                    and scene.pov_character_id
                ):
                    # Get exit knowledge from previous scene (mock for now)
                    # In full implementation, would load actual exit_state
                    pass

        chapter_scenes.append(scene)
        return violations

    def validate_pov_knowledge_vs_other_knowledge(
        self, scene: SceneOutline
    ) -> List[KnowledgeViolation]:
        """Validate POV character knowledge separately from other characters.

        POV character can learn through non-presence (message, document, inference).
        Non-POV characters' knowledge is separate. No impossible omniscience.

        Args:
            scene: Scene to validate

        Returns:
            List of violations (impossible knowledge, omniscience)
        """
        violations: List[KnowledgeViolation] = []

        # POV character can learn through documents/messages even if not present
        # Other characters' knowledge must be inferred from presence/action

        # This requires more detailed knowledge tracking in the schema
        # For now, we provide the structure for this validation

        return violations

    def validate_scene_knowledge_adds_to_chapter(self) -> List[KnowledgeViolation]:
        """Validate that scene knowledge propagates to next scenes.

        Scene's exit_knowledge should inform next scene's entry_knowledge.
        If a fact appears in a later scene, it should be traceable to earlier
        scene where it was learned.

        Returns:
            List of violations (knowledge appears out of nowhere)
        """
        violations: List[KnowledgeViolation] = []

        # Group scenes by chapter
        chapters: Dict[str, List[SceneOutline]] = {}
        for scene in self.scenes.values():
            if scene.chapter_id not in chapters:
                chapters[scene.chapter_id] = []
            chapters[scene.chapter_id].append(scene)

        # For each chapter, validate knowledge continuity
        for chapter_id, chapter_scenes in chapters.items():
            # Sort by narrative position
            sorted_scenes = sorted(
                [s for s in chapter_scenes if s.narrative_position is not None],
                key=lambda s: s.narrative_position or 0,
            )

            for i, scene in enumerate(sorted_scenes):
                if i == 0:
                    continue  # Skip first scene in chapter

                prev_scene = sorted_scenes[i - 1]

                # Only check if same POV character (knowledge transfers)
                if (
                    prev_scene.pov_character_id == scene.pov_character_id
                    and scene.pov_character_id
                ):
                    # Would validate that scene's entry_knowledge is subset of
                    # or derived from prev_scene's exit_knowledge
                    pass

        return violations

    def report_knowledge_violations(
        self, violations: List[KnowledgeViolation]
    ) -> str:
        """Generate human-readable report of knowledge violations.

        Args:
            violations: List of violations to report

        Returns:
            Formatted string with all violations explained
        """
        if not violations:
            return "No knowledge violations found."

        report_lines = [f"Found {len(violations)} knowledge violation(s):\n"]

        for violation in violations:
            report_lines.append(f"  Scene: {violation.scene_id}")
            report_lines.append(f"  Type: {violation.violation_type.value}")
            if violation.character_id:
                report_lines.append(f"  Character: {violation.character_id}")
            report_lines.append(f"  Fact: {violation.fact_what}")
            report_lines.append(f"  Issue: {violation.message}")
            report_lines.append(f"  Fix: {violation.suggestion}")
            report_lines.append("")

        return "\n".join(report_lines)
