"""Knowledge consistency validator for Layer 3 narrative realization.

The bounded V1 contract uses structured ``EntryState``/``ExitState`` knowledge
as the identity-bearing knowledge state. ``Outcome.knowledge_added`` and
``knowledge_questioned`` remain author-facing summaries, so they are not treated
as globally unique fact identifiers.

Within a chapter, a fact present in a same-POV scene's exit state must remain in
the next same-POV scene's entry state. Within a ready scene, entry knowledge must
remain in exit knowledge unless that exact fact is explicitly questioned.
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
        # Retained for compatibility with older callers; validation itself is
        # derived from ``self.scenes`` so results do not depend on call order.
        self._chapter_scenes: Dict[str, List[SceneOutline]] = {}

    def add_scene(self, scene: SceneOutline) -> None:
        """Register a scene for cross-scene validation."""
        self.scenes[scene.id] = scene

    def validate_scene(self, scene: SceneOutline) -> KnowledgeValidationResult:
        """Validate one scene against local and registered continuity rules."""
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
        """Require un-questioned entry facts to survive into the exit state.

        ``Outcome.knowledge_added`` is descriptive prose and is deliberately not
        matched to ``KnowledgeFact.what``. The current schema has no stable fact
        identifier that would make such a comparison deterministic.
        """
        if scene.entry_state is None or scene.exit_state is None:
            return []

        exit_keys = {_fact_key(fact.what) for fact in scene.exit_state.knowledge}
        questioned = {
            _fact_key(value)
            for value in (scene.outcome.knowledge_questioned if scene.outcome else [])
        }

        violations: List[KnowledgeViolation] = []
        for fact in scene.entry_state.knowledge:
            key = _fact_key(fact.what)
            if key in exit_keys or key in questioned:
                continue
            violations.append(
                KnowledgeViolation(
                    scene_id=scene.id,
                    violation_type=KnowledgeViolationType.INCONSISTENT_ENTRY_EXIT,
                    character_id=scene.pov_character_id,
                    fact_what=fact.what,
                    message=(
                        f"Entry knowledge disappears before {scene.id} exit state: "
                        f"{fact.what}"
                    ),
                    suggestion=(
                        "Carry the fact into exit_state.knowledge or explicitly list "
                        "the same fact in outcome.knowledge_questioned."
                    ),
                )
            )

        return violations

    def validate_no_retroactive_forgetting(
        self, scene: SceneOutline
    ) -> List[KnowledgeViolation]:
        """Reject loss of knowledge between adjacent same-POV scenes.

        Comparison is limited to the same chapter and the nearest preceding scene
        with the same POV. This keeps the check deterministic and avoids implying
        cross-character or cross-chapter knowledge ownership that the current
        schema cannot express.
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
                        f"Carry the fact into {scene.id}.entry_state.knowledge or "
                        "represent an explicit forgetting mechanism in a future "
                        "knowledge-model extension."
                    ),
                )
            )

        return violations

    def validate_pov_knowledge_vs_other_knowledge(
        self, scene: SceneOutline
    ) -> List[KnowledgeViolation]:
        """Return no findings where the current schema cannot prove ownership.

        Entry/exit states are scene-level and do not encode separate state for
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
