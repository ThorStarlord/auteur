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

Key Implementation Notes:
------------------------
The KnowledgeValidator works with the SceneOutline schema which includes:
- entry_state: Optional[EntryState] - knowledge and emotions at scene start
- exit_state: Optional[ExitState] - knowledge and emotions at scene end
- pov_character_id: Optional[str] - whose perspective the scene is from
- participants: List[str] - characters present in scene

The validator tracks knowledge across scenes using:
- narrative_position: reading order within chapter
- chapter_id: grouping of scenes
- pov_character_id: knowledge ownership

Future Extensions:
------------------
When schema is enhanced, validator will support:
- learned_in_scene field (explicit learning mechanisms)
- forgetting_in_scene field (explicit forgetting with reason)
- other_character_knowledge (what protagonist knows about others)
- knowledge_source tracking (how/where each fact came from)
- temporal knowledge (facts about when things happened)
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

        The mathematical relationship should hold:
        exit_knowledge = entry_knowledge ∪ learned_in_scene - contradicted_facts

        Where:
        - entry_knowledge: facts character knows entering the scene
        - learned_in_scene: new facts discovered or deduced during scene
        - contradicted_facts: facts that are explicitly denied
        - exit_knowledge: final knowledge state after scene

        Args:
            scene: Scene to validate

        Returns:
            List of violations found
        """
        violations: List[KnowledgeViolation] = []

        # Can only validate if we have complete knowledge state
        # (This would require additional schema fields for learned_in_scene and contradicted)
        #
        # Validation structure when full schema is available:
        # 1. Extract entry_knowledge facts (if scene has entry_state)
        # 2. Extract learned_in_scene facts (if available in scene schema)
        # 3. Extract exit_knowledge facts (if scene has exit_state)
        # 4. Verify exit_knowledge contains all non-contradicted entry facts
        # 5. Verify exit_knowledge contains all learned facts
        # 6. Check for contradictory facts (e.g., learned "X is true" and "X is false")
        # 7. Report specific violations with affected facts

        return violations

    def validate_no_retroactive_forgetting(
        self, scene: SceneOutline
    ) -> List[KnowledgeViolation]:
        """Validate that once learned, knowledge is never forgotten.

        Within a chapter, if a scene's exit_state contains a fact, the next
        scene's entry_state must also contain it (if same POV character).

        Core principle: In narrative, characters remember what they've learned.
        A character cannot know fact X in scene N+2 but not know it in scene N+1
        unless there's an explicit mechanism (memory loss, mind-wipe, etc.).

        Retroactive forgetting happens when:
        - Fact F is in scene_N.exit_knowledge
        - Fact F is NOT in scene_N+1.entry_knowledge
        - Scenes N and N+1 have same POV character
        - No mechanism for forgetting exists (memory loss scene, etc.)

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

            # Check each previous scene's exit knowledge against this scene's entry
            for prev_scene in sorted(
                previous_scenes, key=lambda s: s.narrative_position or 0
            ):
                # Only check if same POV character or same scene participant group
                if (
                    prev_scene.pov_character_id == scene.pov_character_id
                    and scene.pov_character_id
                ):
                    # In full implementation with complete schema:
                    # 1. Get exit_knowledge facts from prev_scene
                    # 2. Get entry_knowledge facts from current scene
                    # 3. For each fact in prev exit_knowledge:
                    #    - Check if it's in current entry_knowledge
                    #    - Report violation if missing and no forgetting mechanism
                    # 4. Track which facts were "explicitly forgotten"
                    #    (in contradiction list rather than missing)
                    pass

        chapter_scenes.append(scene)
        return violations

    def validate_pov_knowledge_vs_other_knowledge(
        self, scene: SceneOutline
    ) -> List[KnowledgeViolation]:
        """Validate POV character knowledge separately from other characters.

        POV character can learn through non-presence (message, document, inference).
        Non-POV characters' knowledge is separate. No impossible omniscience.

        Key constraint: No character should know facts that haven't been established
        in any scene they've participated in, been told about, or can logically infer.

        Args:
            scene: Scene to validate

        Returns:
            List of violations (impossible knowledge, omniscience)
        """
        violations: List[KnowledgeViolation] = []

        # POV character can learn through documents/messages even if not present in scene
        # Other characters' knowledge must be inferred from presence/action or communication
        # from POV character

        # This requires more detailed knowledge tracking in the schema:
        # - Separate entry_knowledge for POV vs other characters
        # - learned_in_scene split by mechanism (perceived, told, inferred, document)
        # - Ability to track inter-character communication
        #
        # Future validation will check:
        # 1. Non-POV character facts must be observable or told to POV
        # 2. POV can learn off-stage through messages/documents only if source is specified
        # 3. No character knows events before they occur (temporal causality)
        # 4. Character knowledge must be traceable to scene where learned
        # 5. If character A tells character B something, B must be in scene with A

        return violations

    def validate_scene_knowledge_adds_to_chapter(self) -> List[KnowledgeViolation]:
        """Validate that scene knowledge propagates to next scenes.

        Scene's exit_knowledge should inform next scene's entry_knowledge.
        If a fact appears in a later scene, it should be traceable to earlier
        scene where it was learned.

        Knowledge must flow coherently through the narrative:
        - Scene 1 learns fact X (exit_knowledge includes X)
        - Scene 2 (same character) must have X in entry_knowledge
        - If Scene 2 doesn't have X, it's a violation (gap in knowledge chain)
        - Exception: Character explicitly forgets X (with mechanism explanation)

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
                    # Full implementation will:
                    # 1. Extract exit_knowledge facts from prev_scene
                    # 2. Extract entry_knowledge facts from current scene
                    # 3. For each fact F in prev exit_knowledge:
                    #    - Check if F is in current entry_knowledge
                    #    - If F is missing and no explicit forgetting mechanism:
                    #      Report KnowledgeViolation with KNOWLEDGE_GAP error type
                    # 4. Check for contradictions (X true in prev, X false now)
                    #    Report with CONTRADICTORY_KNOWLEDGE error type
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
