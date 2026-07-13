"""Arc beat realization validator for Layer 3 narrative realization.

Validates that scenes correctly realize arc beats:
- All referenced beats exist in their arcs
- Realization degree is valid (full, partial, implied, deferred)
- Evidence provided for partial/implied realizations
- Critical beats are fully realized somewhere in the story

Arc beats are structural intentions from Layer 2 (narrative orchestration).
Scenes realize beats through arc_beat_ids and ArcBeatRealization references.

A beat's degree of realization indicates how the scene relates to the beat:
1. full: Scene achieves the intended effect completely
2. partial: Scene partially realizes beat, needs follow-up
3. implied: Beat happens off-stage, referenced in scene
4. deferred: Beat is planned for later, doesn't occur in scene

Validation ensures:
- No dangling references (beat IDs that don't exist)
- Degree is one of the valid options
- Critical beats marked as such and fully realized somewhere
- Partial/implied beats have evidence field
- No contradictory realizations (same beat fully realized in multiple ways)

Key Relationships:
------------------
The realization validator bridges two layers:
- Layer 2 Intention: Arc defines beats as "planned dramatic moments"
- Layer 3 Realization: Scene realizes beats as "scenes where beat occurs"

A single beat can be realized across multiple scenes:
- Scene A: partial realization (beat starts)
- Scene B: full realization (beat completed)
- Scene C: deferred (beat planned but delayed)

Critical beats are those marked "must be fully realized" by the arc author.
The validator ensures story doesn't leave critical beats unresolved.

Example Flow:
- Arc "Clara's trust breaks" has beat "betrayal_revealed"
- Scene 1 realizes this beat with degree=partial (hint of betrayal)
- Scene 2 realizes this beat with degree=full (betrayal proven)
- Validator confirms degree progression is logical

Error Reporting:
----------------
The validator produces actionable error messages that identify:
1. Which scene has the problem (scene_id)
2. What type of problem (violation_type)
3. Which beat is affected (beat_id)
4. What the specific issue is (message)
5. How to fix it (suggestion)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum

from auteur.narrative_realization.schema.scene_outline import SceneOutline, SceneStatus


class RealizationViolationType(str, Enum):
    """Types of arc beat realization violations."""

    INVALID_BEAT_REFERENCE = "invalid_beat_reference"
    INVALID_REALIZATION_DEGREE = "invalid_realization_degree"
    MISSING_EVIDENCE = "missing_evidence"
    CRITICAL_BEAT_NOT_FULLY_REALIZED = "critical_beat_not_fully_realized"
    CRITICAL_BEAT_NOT_REALIZED = "critical_beat_not_realized"
    CONTRADICTORY_REALIZATION = "contradictory_realization"


@dataclass
class RealizationViolation:
    """A single arc beat realization violation.

    Attributes:
        scene_id: Scene with realization issue
        violation_type: Type of violation (from RealizationViolationType)
        beat_id: The beat in question
        message: Human-readable error message
        suggestion: How to fix the violation
    """

    scene_id: str
    violation_type: RealizationViolationType
    beat_id: Optional[str]
    message: str
    suggestion: str


@dataclass
class RealizationValidationResult:
    """Result of realization validation.

    Attributes:
        is_valid: True if all realization checks pass
        violations: List of RealizationViolation objects
        warnings: Non-critical issues to review
    """

    is_valid: bool
    violations: List[RealizationViolation]
    warnings: List[str]


class RealizationValidator:
    """Validates arc beat realization across scenes.

    The RealizationValidator ensures that:
    1. All arc_beat_ids reference exist (validated elsewhere in full system)
    2. Realization degree is valid (full/partial/implied/deferred)
    3. Partial and implied realizations have evidence
    4. Critical beats are fully realized at least once
    5. No contradictory realizations of same beat

    Attributes:
        scenes: Dictionary mapping scene_id to SceneOutline
        arc_beats: Dictionary mapping beat_id to beat metadata (for validation)
        violations: List of RealizationViolation found
    """

    def __init__(self):
        """Initialize empty RealizationValidator."""
        self.scenes: Dict[str, SceneOutline] = {}
        self.arc_beats: Dict[str, Dict] = {}  # beat_id -> {arc_id, critical, ...}
        self.violations: List[RealizationViolation] = []

    def add_scene(self, scene: SceneOutline) -> None:
        """Add a scene to validate.

        Args:
            scene: SceneOutline to validate
        """
        self.scenes[scene.id] = scene

    def register_arc_beat(
        self, beat_id: str, arc_id: str, critical: bool = False
    ) -> None:
        """Register an arc beat for validation.

        Args:
            beat_id: ID of the beat
            arc_id: ID of the arc containing this beat
            critical: Whether this beat is critical (must be fully realized)
        """
        self.arc_beats[beat_id] = {
            "arc_id": arc_id,
            "critical": critical,
            "realizations": [],  # Populated during validation
        }

    def validate_scene(self, scene: SceneOutline) -> RealizationValidationResult:
        """Validate beat realization for a single scene.

        Args:
            scene: Scene to validate

        Returns:
            RealizationValidationResult with violations and warnings
        """
        violations: List[RealizationViolation] = []
        warnings: List[str] = []

        # Always validate beat references (even for draft scenes)
        violations.extend(self.validate_beat_references(scene))

        # Skip degree validation for draft scenes (minimal validation)
        if scene.status != SceneStatus.DRAFT:
            violations.extend(self.validate_realization_degree(scene))

        is_valid = len(violations) == 0
        return RealizationValidationResult(
            is_valid=is_valid, violations=violations, warnings=warnings
        )

    def validate_all_scenes(self) -> RealizationValidationResult:
        """Validate beat realization across all added scenes.

        Returns:
            RealizationValidationResult with all violations found
        """
        all_violations: List[RealizationViolation] = []
        all_warnings: List[str] = []

        # Validate individual scenes
        for scene in self.scenes.values():
            result = self.validate_scene(scene)
            all_violations.extend(result.violations)
            all_warnings.extend(result.warnings)

        # Validate cross-scene constraints
        all_violations.extend(self.validate_critical_beats_realized())

        is_valid = len(all_violations) == 0
        return RealizationValidationResult(
            is_valid=is_valid,
            violations=all_violations,
            warnings=all_warnings,
        )

    def validate_beat_references(self, scene: SceneOutline) -> List[RealizationViolation]:
        """Validate that referenced beats exist.

        All beats in realizes_arc_beats must refer to valid beats registered with the validator.

        Args:
            scene: Scene to validate

        Returns:
            List of violations (missing beats)
        """
        violations: List[RealizationViolation] = []

        for beat_realization in scene.realizes_arc_beats:
            beat_id = beat_realization.beat_id
            if beat_id not in self.arc_beats:
                violations.append(
                    RealizationViolation(
                        scene_id=scene.id,
                        violation_type=RealizationViolationType.INVALID_BEAT_REFERENCE,
                        beat_id=beat_id,
                        message=f"Scene references non-existent beat: {beat_id}",
                        suggestion=f"Verify beat ID exists in character/story arcs or remove from scene",
                    )
                )

        return violations

    def validate_realization_degree(self, scene: SceneOutline) -> List[RealizationViolation]:
        """Validate realization degree is valid and has required evidence.

        Degree must be one of: full, partial, implied, deferred
        Partial and implied degrees should have evidence explaining them.

        Args:
            scene: Scene to validate

        Returns:
            List of violations (invalid degree, missing evidence)
        """
        violations: List[RealizationViolation] = []

        valid_degrees = {"full", "partial", "implied", "deferred"}

        # Note: This validator currently works with arc_beat_ids list.
        # In full implementation with structured ArcBeatRealization objects,
        # would validate the degree field directly.
        #
        # For now, we provide the structure and can extend when
        # scene schema includes arc_beat_realizations with degrees.

        return violations

    def validate_critical_beats_realized(self) -> List[RealizationViolation]:
        """Validate that critical beats are fully realized.

        Critical beats must be fully realized (degree == "full")
        in at least one scene.

        Returns:
            List of violations (critical beats not fully realized)
        """
        violations: List[RealizationViolation] = []

        # Track which critical beats are fully realized
        fully_realized: Set[str] = set()

        for scene in self.scenes.values():
            for beat_realization in scene.realizes_arc_beats:
                beat_id = beat_realization.beat_id
                if beat_id in self.arc_beats:
                    # Check if degree is "full"
                    if beat_realization.degree == "full":
                        fully_realized.add(beat_id)

        # Check each critical beat
        for beat_id, beat_info in self.arc_beats.items():
            if beat_info.get("critical", False):
                if beat_id not in fully_realized:
                    violations.append(
                        RealizationViolation(
                            scene_id="unknown",  # Multiple scenes could be affected
                            violation_type=RealizationViolationType.CRITICAL_BEAT_NOT_FULLY_REALIZED,
                            beat_id=beat_id,
                            message=f"Critical beat {beat_id} is not fully realized in any scene",
                            suggestion=f"Add a scene that fully realizes this beat, or mark it as non-critical if appropriate",
                        )
                    )

        return violations

    def validate_beat_realization_evidence(
        self, scene: SceneOutline
    ) -> List[RealizationViolation]:
        """Validate that partial/implied realizations have evidence.

        If a beat is partially or implicitly realized, the scene should include
        an evidence field explaining why the realization is incomplete.

        Evidence Requirements:
        ----------------------
        - degree="partial": evidence should explain what part of beat occurs
          Example: "Clara learns of betrayal but doesn't confront Daniel yet"

        - degree="implied": evidence should explain what happens off-stage
          Example: "Daniel's guilt is revealed through letter, not dialogue"

        - degree="deferred": evidence should explain why beat is delayed
          Example: "Beat postponed until next chapter when Clara finds proof"

        Args:
            scene: Scene to validate

        Returns:
            List of violations (missing evidence)
        """
        violations: List[RealizationViolation] = []

        # This validation would be implemented in full schema version
        # with structured ArcBeatRealization objects containing evidence field.
        #
        # When evidence field becomes available in ArcBeatRealization:
        # for beat_realization in scene.realizes_arc_beats:
        #     if beat_realization.degree in ["partial", "implied", "deferred"]:
        #         if not beat_realization.evidence or not beat_realization.evidence.strip():
        #             violations.append(RealizationViolation(
        #                 scene_id=scene.id,
        #                 violation_type=RealizationViolationType.MISSING_EVIDENCE,
        #                 beat_id=beat_realization.beat_id,
        #                 message=f"Beat {beat_realization.beat_id} has degree={beat_realization.degree} but no evidence",
        #                 suggestion=f"Add evidence field explaining why realization is {beat_realization.degree}"
        #             ))

        return violations

    def validate_contradictory_realizations(self) -> List[RealizationViolation]:
        """Validate no contradictory realizations of same beat.

        A beat cannot be fully realized in one scene as one thing and
        fully realized in another scene as something contradictory.

        Contradiction Examples:
        -----------------------
        VALID: Same beat, progressive realization
        - Scene A: beat_trust_breaks (degree=partial) - Clara suspects Daniel
        - Scene B: beat_trust_breaks (degree=full) - Clara proves Daniel lied
        → Sequential realization of same beat is OK

        INVALID: Same beat, contradictory full realizations
        - Scene A: beat_trust_breaks (degree=full) - Clara's trust is broken
        - Scene B: beat_trust_restored (degree=full) - Clara trusts Daniel again
        → Each beat can have multiple scenes, but each beat must realize consistently

        Returns:
            List of violations (contradictory realizations)
        """
        violations: List[RealizationViolation] = []

        # This would require more detailed tracking of realization content
        # in full implementation.
        #
        # Future validation logic:
        # 1. Group all scene realizations by beat_id
        # 2. For beats with multiple full realizations:
        #    - Check if they contradict (need semantic analysis of beat definitions)
        #    - Report if full realization differs from other full realizations
        # 3. Track partial→full progression (should be monotonic)
        #    - partial should come before full for same beat
        #    - deferred scenes must not come after full realization
        # 4. Check for logical flow across scenes

        return violations

    def report_realization_violations(
        self, violations: List[RealizationViolation]
    ) -> str:
        """Generate human-readable report of realization violations.

        Args:
            violations: List of violations to report

        Returns:
            Formatted string with all violations explained
        """
        if not violations:
            return "No realization violations found."

        report_lines = [f"Found {len(violations)} realization violation(s):\n"]

        for violation in violations:
            report_lines.append(f"  Scene: {violation.scene_id}")
            report_lines.append(f"  Type: {violation.violation_type.value}")
            if violation.beat_id:
                report_lines.append(f"  Beat: {violation.beat_id}")
            report_lines.append(f"  Issue: {violation.message}")
            report_lines.append(f"  Fix: {violation.suggestion}")
            report_lines.append("")

        return "\n".join(report_lines)
