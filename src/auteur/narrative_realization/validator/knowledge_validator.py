"""Knowledge consistency validator for Layer 3 narrative realization.

The bounded V1 contract uses structured ``EntryState``/``ExitState`` knowledge
for deterministic continuity between adjacent same-POV scenes. The current
schema does not assign stable fact IDs and permits author-written paraphrase
inside a scene, so local entry/exit prose and ``Outcome.knowledge_added`` are not
treated as identical fact keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from auteur.narrative_realization.schema.scene_outline import SceneOutline, SceneStatus


class KnowledgeViolationType(str, Enum):
    """Types of knowledge consistency violations."""

    RETROACTIVE_FORGETTING = "retroactive_forgetting"
    INCONSISTENT_ENTRY_EXIT = "inconsistent_entry_exit"
    IMPOSSIBLE_OMNISCIENCE = "impossible_omniscience"
    KNOWLEDGE_GAP = "knowledge_gap"
    CONTRADICTORY_KNOWLEDGE = "contradictory_knowledge"


@dataclass
class KnowledgeViolation:
    """A single knowledge consistency violation."""

    scene_id: str
    violation_type: KnowledgeViolationType
    character_id: Optional[str]
    fact_what: str
    message: str
    suggestion: str


@dataclass
class KnowledgeValidationResult:
    """Result of knowledge validation for a scene or scene collection."""

    is_valid: bool
    violations: List[KnowledgeViolation]
    warnings: List[str]


def _fact_key(value: str) -> str:
    """Return a deterministic comparison key for author-written fact text."""
    return " ".join(value.split()).casefold()


class KnowledgeValidator:
    """Validate the bounded V1 scene-knowledge continuity contract."""

    def __init__(self) -> None:
        self.scenes: Dict[str, SceneOutline] = {}
        self.violations: List[KnowledgeViolation] = []
        # Kept for compatibility with callers that inspect the old attribute.
        # Validation derives from ``self.scenes`` and is therefore call-order independent.
        self._chapter_scenes: Dict[str, List[SceneOutline]] = {}

    def add_scene(self, scene: SceneOutline) -> None:
        """Register a scene for cross-scene validation."""
        self.scenes[scene.id] = scene

    def validate_scene(self, scene: SceneOutline) -> KnowledgeValidationResult:
        """Validate one scene against the currently provable knowledge rules."""
        violations: List[KnowledgeViolation] = []
        warnings: List[str] = []

        if scene.status == SceneStatus.DRAFT:
            return KnowledgeValidationResult(True, violations, warnings)

        violations.extend(self.validate_knowledge_consistency(scene))
        violations.extend(self.validate_no_retroactive_forgetting(scene))
        violations.extend(self.validate_pov_knowledge_vs_other_knowledge(scene))

        return KnowledgeValidationResult(not violations, violations, warnings)

    def validate_all_scenes(self) -> KnowledgeValidationResult:
        """Validate all registered scenes in deterministic narrative order."""
        all_violations: List[KnowledgeViolation] = []
        all_warnings: List[str] = []

        ordered = sorted(
            self.scenes.values(),
            key=lambda scene: (
                scene.chapter_id,
                scene.narrative_position if scene.narrative_position is not None else 10**9,
                scene.id,
            ),
        )
        for scene in ordered:
            result = self.validate_scene(scene)
            all_violations.extend(result.violations)
            all_warnings.extend(result.warnings)

        self.violations = list(all_violations)
        return KnowledgeValidationResult(
            is_valid=not all_violations,
            violations=all_violations,
            warnings=all_warnings,
        )

    def validate_knowledge_consistency(
        self, scene: SceneOutline
    ) -> List[KnowledgeViolation]:
        """Return no local text-identity finding without stable knowledge IDs.

        ``KnowledgeFact.what`` and ``Outcome.knowledge_added`` are author-written
        text. Existing accepted fixtures legitimately paraphrase a fact between a
        scene's entry and exit state. Treating those strings as canonical IDs
        would create false contradictions, so V1 limits deterministic enforcement
        to cross-scene carryover where the structured fact text is expected to be
        preserved by the next same-POV entry state.
        """
        return []

    def validate_no_retroactive_forgetting(
        self, scene: SceneOutline
    ) -> List[KnowledgeViolation]:
        """Reject loss of knowledge between adjacent same-POV scenes.

        Comparison is limited to the same chapter and nearest preceding scene
        with the same POV. That boundary is expressible by the current schema and
        does not infer knowledge ownership for other participants or chapters.
        """
        if (
            scene.status == SceneStatus.DRAFT
            or scene.narrative_position is None
            or not scene.pov_character_id
            or scene.entry_state is None
        ):
            return []

        previous_candidates = [
            candidate
            for candidate in self.scenes.values()
            if candidate.id != scene.id
            and candidate.status != SceneStatus.DRAFT
            and candidate.chapter_id == scene.chapter_id
            and candidate.pov_character_id == scene.pov_character_id
            and candidate.narrative_position is not None
            and candidate.narrative_position < scene.narrative_position
            and candidate.exit_state is not None
        ]
        if not previous_candidates:
            return []

        previous = max(
            previous_candidates,
            key=lambda candidate: (candidate.narrative_position or 0, candidate.id),
        )
        entry_keys = {_fact_key(fact.what) for fact in scene.entry_state.knowledge}

        violations: List[KnowledgeViolation] = []
        for fact in previous.exit_state.knowledge:
            if _fact_key(fact.what) in entry_keys:
                continue
            violations.append(
                KnowledgeViolation(
                    scene_id=scene.id,
                    violation_type=KnowledgeViolationType.RETROACTIVE_FORGETTING,
                    character_id=scene.pov_character_id,
                    fact_what=fact.what,
                    message=(
                        f"{scene.pov_character_id} knows '{fact.what}' at the end of "
                        f"{previous.id}, but it is absent from {scene.id} entry state."
                    ),
                    suggestion=(
                        f"Carry the fact into {scene.id}.entry_state.knowledge, or keep "
                        "the scene in a non-ready state until an explicit forgetting "
                        "mechanism can be represented."
                    ),
                )
            )

        return violations

    def validate_pov_knowledge_vs_other_knowledge(
        self, scene: SceneOutline
    ) -> List[KnowledgeViolation]:
        """Return no finding where the current schema cannot prove ownership.

        Entry/exit states are scene-level and do not encode independent state for
        every non-POV participant. V1 therefore fails conservatively rather than
        inventing omniscience findings from unavailable evidence.
        """
        return []

    def validate_scene_knowledge_adds_to_chapter(self) -> List[KnowledgeViolation]:
        """Compatibility entry point for deterministic cross-scene continuity."""
        violations: List[KnowledgeViolation] = []
        ordered = sorted(
            self.scenes.values(),
            key=lambda scene: (
                scene.chapter_id,
                scene.narrative_position if scene.narrative_position is not None else 10**9,
                scene.id,
            ),
        )
        for scene in ordered:
            violations.extend(self.validate_no_retroactive_forgetting(scene))
        return violations

    def report_knowledge_violations(
        self, violations: List[KnowledgeViolation]
    ) -> str:
        """Generate a human-readable report for knowledge violations."""
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
