"""Knowledge consistency validation for Layer 3 narrative realization.

The current SceneOutline schema can prove two deterministic continuity facts:

* facts present on scene entry may not silently disappear from scene exit; and
* facts present at the prior same-POV scene exit must be present on the next
  same-POV scene entry.

Richer semantics such as explicit learning mechanisms, intentional forgetting,
or contradiction resolution require schema that does not yet exist and are not
inferred here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from auteur.narrative_realization.schema.scene_outline import SceneOutline, SceneStatus


class KnowledgeViolationType(str, Enum):
    RETROACTIVE_FORGETTING = "retroactive_forgetting"
    INCONSISTENT_ENTRY_EXIT = "inconsistent_entry_exit"
    IMPOSSIBLE_OMNISCIENCE = "impossible_omniscience"
    KNOWLEDGE_GAP = "knowledge_gap"
    CONTRADICTORY_KNOWLEDGE = "contradictory_knowledge"


@dataclass
class KnowledgeViolation:
    scene_id: str
    violation_type: KnowledgeViolationType
    character_id: Optional[str]
    fact_what: str
    message: str
    suggestion: str


@dataclass
class KnowledgeValidationResult:
    is_valid: bool
    violations: list[KnowledgeViolation]
    warnings: list[str]


class KnowledgeValidator:
    """Validate the deterministic knowledge continuity represented by scenes."""

    def __init__(self) -> None:
        self.scenes: dict[str, SceneOutline] = {}
        self.violations: list[KnowledgeViolation] = []
        # Retained for compatibility with callers that may inspect the old
        # implementation detail. Validation itself is deliberately stateless.
        self._chapter_scenes: dict[str, list[SceneOutline]] = {}

    def add_scene(self, scene: SceneOutline) -> None:
        self.scenes[scene.id] = scene

    def validate_scene(self, scene: SceneOutline) -> KnowledgeValidationResult:
        if scene.status == SceneStatus.DRAFT:
            return KnowledgeValidationResult(True, [], [])

        violations = [
            *self.validate_knowledge_consistency(scene),
            *self.validate_no_retroactive_forgetting(scene),
            *self.validate_pov_knowledge_vs_other_knowledge(scene),
        ]
        return KnowledgeValidationResult(not violations, violations, [])

    def validate_all_scenes(self) -> KnowledgeValidationResult:
        """Validate each scene once, then validate cross-scene POV continuity."""
        violations: list[KnowledgeViolation] = []
        warnings: list[str] = []

        for scene in self.scenes.values():
            if scene.status == SceneStatus.DRAFT:
                continue
            violations.extend(self.validate_knowledge_consistency(scene))
            violations.extend(self.validate_pov_knowledge_vs_other_knowledge(scene))

        violations.extend(self.validate_scene_knowledge_adds_to_chapter())
        return KnowledgeValidationResult(not violations, violations, warnings)

    @staticmethod
    def _fact_names(scene_state: object | None) -> set[str]:
        if scene_state is None:
            return set()
        knowledge = getattr(scene_state, "knowledge", [])
        return {fact.what for fact in knowledge}

    def validate_knowledge_consistency(
        self, scene: SceneOutline
    ) -> list[KnowledgeViolation]:
        """Ensure entry facts do not silently disappear from scene exit.

        The current schema does not encode an explicit forgetting mechanism, so
        disappearance is objectively inconsistent. Newly learned facts are not
        inferred because their acquisition mechanism is not represented yet.
        """
        if scene.entry_state is None or scene.exit_state is None:
            return []

        exit_facts = self._fact_names(scene.exit_state)
        violations: list[KnowledgeViolation] = []
        for fact in scene.entry_state.knowledge:
            if fact.what in exit_facts:
                continue
            violations.append(
                KnowledgeViolation(
                    scene_id=scene.id,
                    violation_type=KnowledgeViolationType.INCONSISTENT_ENTRY_EXIT,
                    character_id=scene.pov_character_id,
                    fact_what=fact.what,
                    message=(
                        f"Knowledge present on entry disappears from {scene.id}'s "
                        "exit state without a representable forgetting mechanism"
                    ),
                    suggestion="Preserve the fact in exit_state or revise the scene state",
                )
            )
        return violations

    def _previous_same_pov_scene(self, scene: SceneOutline) -> SceneOutline | None:
        if scene.narrative_position is None or not scene.pov_character_id:
            return None

        candidates = [
            candidate
            for candidate in self.scenes.values()
            if candidate.id != scene.id
            and candidate.chapter_id == scene.chapter_id
            and candidate.pov_character_id == scene.pov_character_id
            and candidate.narrative_position is not None
            and candidate.narrative_position < scene.narrative_position
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda candidate: candidate.narrative_position or 0)

    def validate_no_retroactive_forgetting(
        self, scene: SceneOutline
    ) -> list[KnowledgeViolation]:
        """Require prior same-POV exit facts on the next same-POV scene entry."""
        previous = self._previous_same_pov_scene(scene)
        if previous is None or previous.exit_state is None or scene.entry_state is None:
            return []

        entry_facts = self._fact_names(scene.entry_state)
        violations: list[KnowledgeViolation] = []
        for fact in previous.exit_state.knowledge:
            if fact.what in entry_facts:
                continue
            violations.append(
                KnowledgeViolation(
                    scene_id=scene.id,
                    violation_type=KnowledgeViolationType.RETROACTIVE_FORGETTING,
                    character_id=scene.pov_character_id,
                    fact_what=fact.what,
                    message=(
                        f"{scene.pov_character_id} knew this fact at {previous.id} exit "
                        f"but it is absent from {scene.id} entry"
                    ),
                    suggestion="Carry the fact into entry_state or revise the prior scene state",
                )
            )
        return violations

    def validate_pov_knowledge_vs_other_knowledge(
        self, scene: SceneOutline
    ) -> list[KnowledgeViolation]:
        """Do not infer per-character omniscience from data the schema lacks.

        EntryState/ExitState currently belong to the scene POV state. They do not
        encode independent non-POV knowledge ledgers or communication events, so
        stronger omniscience claims would be speculative.
        """
        return []

    def validate_scene_knowledge_adds_to_chapter(self) -> list[KnowledgeViolation]:
        """Validate same-POV continuity for all registered non-draft scenes."""
        violations: list[KnowledgeViolation] = []
        ordered = sorted(
            self.scenes.values(),
            key=lambda scene: (
                scene.chapter_id,
                scene.narrative_position if scene.narrative_position is not None else -1,
                scene.id,
            ),
        )
        for scene in ordered:
            if scene.status != SceneStatus.DRAFT:
                violations.extend(self.validate_no_retroactive_forgetting(scene))
        return violations

    def report_knowledge_violations(
        self, violations: list[KnowledgeViolation]
    ) -> str:
        if not violations:
            return "No knowledge violations found."

        lines = [f"Found {len(violations)} knowledge violation(s):\n"]
        for violation in violations:
            lines.append(f"  Scene: {violation.scene_id}")
            lines.append(f"  Type: {violation.violation_type.value}")
            if violation.character_id:
                lines.append(f"  Character: {violation.character_id}")
            lines.append(f"  Fact: {violation.fact_what}")
            lines.append(f"  Issue: {violation.message}")
            lines.append(f"  Fix: {violation.suggestion}")
            lines.append("")
        return "\n".join(lines)
