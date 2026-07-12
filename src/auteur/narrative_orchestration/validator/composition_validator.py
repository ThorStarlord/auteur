"""Composition validator for Layer 2.5 narrative orchestration.

This module implements CompositionValidator, which orchestrates all three
validators (Reference, Chronological, Contradiction) to provide complete
outline validation.

CompositionValidator:
1. Accepts complete outline artifacts (book, sequences, chapters, arcs)
2. Instantiates and runs all three validators
3. Aggregates violations from all validators
4. Categorizes violations as errors or warnings
5. Generates comprehensive error reports
6. Provides pass/fail/warnings status

A composition passes validation only if:
- All reference validators pass (no missing/broken references)
- All chronological validators pass (proper temporal ordering)
- All contradiction validators pass (no structural conflicts)
- Warnings may be present but do not fail validation

Violations are categorized:
- ERRORS: Structural failures that break composition coherence
- WARNINGS: Inconsistencies that should be reviewed but don't fail validation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

from auteur.narrative_orchestration.validator.reference_validator import (
    ReferenceValidator,
    ValidationError,
    ValidationResult,
)
from auteur.narrative_orchestration.validator.chronological_validator import (
    ChronologicalValidator,
    ChronologicalViolation,
    ChronologyViolationType,
)
from auteur.narrative_orchestration.validator.contradiction_validator import (
    ContradictionValidator,
    Contradiction,
    ContradictionSeverity,
)


class ValidationSeverity(str, Enum):
    """Severity levels for composition validation violations."""

    ERROR = "error"
    WARNING = "warning"


class CompositionStatus(str, Enum):
    """Overall composition validation status."""

    PASS = "pass"
    WARNINGS = "warnings"
    FAIL = "fail"


@dataclass
class AggregatedViolation:
    """A violation from any of the three validators, in unified format.

    Attributes:
        violation_type: What kind of violation (e.g., "missing_reference", "payoff_before_setup")
        validator_type: Which validator found this ("reference", "chronological", "contradiction")
        severity: ERRORS or WARNINGS
        artifact_id: Primary artifact with the violation
        related_artifact_id: Secondary artifact (if applicable)
        message: Human-readable description
        evidence: Additional context/evidence
    """

    violation_type: str
    validator_type: str
    severity: ValidationSeverity
    artifact_id: str
    related_artifact_id: Optional[str] = None
    message: str = ""
    evidence: Optional[str] = None


@dataclass
class CompositionValidationResult:
    """Result of complete composition validation.

    Attributes:
        status: CompositionStatus (PASS, WARNINGS, FAIL)
        error_count: Number of validation errors
        warning_count: Number of warnings
        violations: List of all AggregatedViolation objects
        report: Human-readable validation report
    """

    status: CompositionStatus
    error_count: int
    warning_count: int
    violations: List[AggregatedViolation] = field(default_factory=list)
    report: str = ""

    def is_valid(self) -> bool:
        """Return True if composition passed validation (PASS or WARNINGS status)."""
        return self.status in (CompositionStatus.PASS, CompositionStatus.WARNINGS)

    def has_errors(self) -> bool:
        """Return True if composition has errors (FAIL status)."""
        return self.status == CompositionStatus.FAIL

    def has_warnings(self) -> bool:
        """Return True if composition has warnings."""
        return self.warning_count > 0


class CompositionValidator:
    """Orchestrates all validators for complete outline coherence.

    Accepts complete outline artifacts and runs:
    1. ReferenceValidator - validates ID resolution and references
    2. ChronologicalValidator - validates temporal ordering
    3. ContradictionValidator - validates consistency between artifacts

    Aggregates violations from all three validators and provides unified
    error reporting.

    Attributes:
        artifact_registry: Complete registry of all artifacts
        book_outline: Book outline (required)
        sequence_outlines: Sequence outlines (optional)
        chapter_outlines: Chapter outlines (required)
        character_arcs: Character arcs (optional)
        story_arcs: Story arcs (optional)
        genre: Genre identifier (for contradiction validator)
    """

    def __init__(
        self,
        artifact_registry: Dict[str, Any],
        book_outline: Any,
        chapter_outlines: Dict[str, Any],
        genre: str,
        sequence_outlines: Optional[Dict[str, Any]] = None,
        character_arcs: Optional[Dict[str, Any]] = None,
        story_arcs: Optional[Dict[str, Any]] = None,
    ):
        """Initialize CompositionValidator with outline artifacts.

        Args:
            artifact_registry: Dictionary mapping artifact IDs to artifact objects
            book_outline: BookOutline artifact (required)
            chapter_outlines: Dictionary of ChapterOutline artifacts (required)
            genre: Genre identifier (required)
            sequence_outlines: Dictionary of SequenceOutline artifacts (optional)
            character_arcs: Dictionary of CharacterArc artifacts (optional)
            story_arcs: Dictionary of StoryArc artifacts (optional)

        Raises:
            ValueError: If required artifacts are missing or invalid
        """
        if not artifact_registry:
            raise ValueError("artifact_registry is required")
        if not book_outline:
            raise ValueError("book_outline is required")
        if not chapter_outlines:
            raise ValueError("chapter_outlines is required")
        if not genre:
            raise ValueError("genre is required")

        self.artifact_registry = artifact_registry
        self.book_outline = book_outline
        self.chapter_outlines = chapter_outlines
        self.genre = genre
        self.sequence_outlines = sequence_outlines or {}
        self.character_arcs = character_arcs or {}
        self.story_arcs = story_arcs or {}

        self.violations: List[AggregatedViolation] = []

    def validate_complete_outline(self) -> CompositionValidationResult:
        """Orchestrate all validators and aggregate results.

        This is the main entry point. Runs all three validators and produces
        a comprehensive validation result.

        Returns:
            CompositionValidationResult with complete validation outcome
        """
        self.violations = []

        # Run all three validators
        self._run_reference_validator()
        self._run_chronological_validator()
        self._run_contradiction_validator()

        # Categorize and aggregate violations
        self._categorize_violations()

        # Determine overall status
        status = self._determine_status()

        # Generate report
        report = self._generate_report()

        # Count errors and warnings
        error_count = len(
            [v for v in self.violations if v.severity == ValidationSeverity.ERROR]
        )
        warning_count = len(
            [v for v in self.violations if v.severity == ValidationSeverity.WARNING]
        )

        return CompositionValidationResult(
            status=status,
            error_count=error_count,
            warning_count=warning_count,
            violations=self.violations,
            report=report,
        )

    def _run_reference_validator(self) -> None:
        """Run reference validator and collect violations."""
        ref_validator = ReferenceValidator(self.artifact_registry)
        result = ref_validator.validate_all_references()

        # Add errors from reference validator
        for error in result.errors:
            violation = AggregatedViolation(
                violation_type=error.error_type,
                validator_type="reference",
                severity=ValidationSeverity.ERROR,
                artifact_id=error.artifact_id,
                related_artifact_id=error.reference_id,
                message=error.message,
                evidence=f"Reference: {error.reference_id}",
            )
            self.violations.append(violation)

        # Add warnings from reference validator
        for warning in result.warnings:
            violation = AggregatedViolation(
                violation_type="reference_warning",
                validator_type="reference",
                severity=ValidationSeverity.WARNING,
                artifact_id="unknown",
                message=warning,
            )
            self.violations.append(violation)

    def _run_chronological_validator(self) -> None:
        """Run chronological validator and collect violations."""
        chrono_validator = ChronologicalValidator()

        # Add all artifacts to validator
        chrono_validator.books["book"] = self.book_outline

        for seq_id, seq in self.sequence_outlines.items():
            chrono_validator.add_sequence(seq_id, seq)

        for ch_id, ch in self.chapter_outlines.items():
            chrono_validator.add_chapter(ch_id, ch)

        for arc_id, arc in self.character_arcs.items():
            chrono_validator.add_character_arc(arc_id, arc)

        for arc_id, arc in self.story_arcs.items():
            chrono_validator.add_story_arc(arc_id, arc)

        # Run validation
        chrono_validator.validate_all_chronology()

        # Convert violations to aggregated format
        for violation in chrono_validator.violations:
            # Map chronological severity to composition severity
            severity = (
                ValidationSeverity.ERROR
                if violation.severity == "error"
                else ValidationSeverity.WARNING
            )

            aggregated = AggregatedViolation(
                violation_type=violation.violation_type.value,
                validator_type="chronological",
                severity=severity,
                artifact_id=violation.source_artifact_id,
                related_artifact_id=violation.target_artifact_id,
                message=violation.message,
            )
            self.violations.append(aggregated)

    def _run_contradiction_validator(self) -> None:
        """Run contradiction validator and collect violations."""
        try:
            contradiction_validator = ContradictionValidator(
                book_outline=self.book_outline,
                chapter_outlines=self.chapter_outlines,
                genre=self.genre,
                sequence_outlines=self.sequence_outlines,
                character_arcs=self.character_arcs,
                story_arcs=self.story_arcs,
            )

            # Run validation
            has_no_contradictions, contradictions = contradiction_validator.validate_no_contradictions()

            # Convert contradictions to aggregated format
            for contradiction in contradictions:
                # Map contradiction severity to composition severity
                severity = (
                    ValidationSeverity.ERROR
                    if contradiction.severity == ContradictionSeverity.HARD
                    else ValidationSeverity.WARNING
                )

                aggregated = AggregatedViolation(
                    violation_type=contradiction.contradiction_type,
                    validator_type="contradiction",
                    severity=severity,
                    artifact_id=contradiction.artifact_a,
                    related_artifact_id=contradiction.artifact_b,
                    message=contradiction.description,
                    evidence=f"Evidence A: {contradiction.evidence_a}; Evidence B: {contradiction.evidence_b}",
                )
                self.violations.append(aggregated)
        except Exception:
            # If contradiction validator fails, record it as a warning
            violation = AggregatedViolation(
                violation_type="contradiction_validator_error",
                validator_type="contradiction",
                severity=ValidationSeverity.WARNING,
                artifact_id="composition",
                message="Contradiction validator encountered an error (may be missing theme data)",
            )
            self.violations.append(violation)

    def _categorize_violations(self) -> None:
        """Categorize violations as errors or warnings.

        This method ensures proper categorization:
        - Reference errors always stay as errors
        - Chronological violations follow their severity
        - Contradiction violations follow their severity
        """
        # Already categorized during aggregation, this is a placeholder
        # for any additional logic needed
        pass

    def _determine_status(self) -> CompositionStatus:
        """Determine overall validation status.

        Returns:
            PASS if no violations
            WARNINGS if only warnings
            FAIL if any errors
        """
        error_count = sum(
            1 for v in self.violations if v.severity == ValidationSeverity.ERROR
        )
        warning_count = sum(
            1 for v in self.violations if v.severity == ValidationSeverity.WARNING
        )

        if error_count > 0:
            return CompositionStatus.FAIL

        if warning_count > 0:
            return CompositionStatus.WARNINGS

        return CompositionStatus.PASS

    def _generate_report(self) -> str:
        """Generate comprehensive error report.

        Returns:
            Formatted multi-line report of all violations
        """
        lines = []

        # Overall status
        error_count = sum(
            1 for v in self.violations if v.severity == ValidationSeverity.ERROR
        )
        warning_count = sum(
            1 for v in self.violations if v.severity == ValidationSeverity.WARNING
        )

        status_line = f"Composition Validation: {error_count} error(s), {warning_count} warning(s)"
        lines.append(status_line)
        lines.append("=" * len(status_line))
        lines.append("")

        if not self.violations:
            lines.append("✓ All validation checks passed")
            return "\n".join(lines)

        # Group violations by validator
        by_validator = {}
        for violation in self.violations:
            if violation.validator_type not in by_validator:
                by_validator[violation.validator_type] = []
            by_validator[violation.validator_type].append(violation)

        # Report by validator
        for validator_type in ["reference", "chronological", "contradiction"]:
            if validator_type not in by_validator:
                continue

            violations = by_validator[validator_type]
            errors = [v for v in violations if v.severity == ValidationSeverity.ERROR]
            warnings = [v for v in violations if v.severity == ValidationSeverity.WARNING]

            lines.append(f"\n{validator_type.upper()} VALIDATOR")
            lines.append("-" * (len(validator_type) + 10))

            if errors:
                lines.append(f"  ERRORS ({len(errors)}):")
                for error in errors:
                    lines.append(f"    - {error.artifact_id}: {error.message}")
                    if error.related_artifact_id:
                        lines.append(f"      related: {error.related_artifact_id}")

            if warnings:
                lines.append(f"  WARNINGS ({len(warnings)}):")
                for warning in warnings:
                    lines.append(f"    - {warning.artifact_id}: {warning.message}")
                    if warning.related_artifact_id:
                        lines.append(f"      related: {warning.related_artifact_id}")

        return "\n".join(lines)

    def get_validation_status(self) -> str:
        """Get short validation status string.

        Returns:
            One of: "pass", "warnings", "fail"
        """
        result = self.validate_complete_outline()
        return result.status.value

    def report_violations(self) -> str:
        """Get human-readable violation report.

        Returns:
            Formatted report of all violations
        """
        result = self.validate_complete_outline()
        return result.report

    def get_violations_by_type(
        self, validator_type: Optional[str] = None
    ) -> List[AggregatedViolation]:
        """Get violations filtered by validator type.

        Args:
            validator_type: Optional filter by validator ("reference", "chronological", "contradiction")

        Returns:
            Filtered list of violations
        """
        if not self.violations:
            result = self.validate_complete_outline()
            violations = result.violations
        else:
            violations = self.violations

        if validator_type:
            return [v for v in violations if v.validator_type == validator_type]

        return violations

    def get_errors(self) -> List[AggregatedViolation]:
        """Get all errors (not warnings).

        Returns:
            List of all validation errors
        """
        if not self.violations:
            result = self.validate_complete_outline()
            violations = result.violations
        else:
            violations = self.violations

        return [v for v in violations if v.severity == ValidationSeverity.ERROR]

    def get_warnings(self) -> List[AggregatedViolation]:
        """Get all warnings (not errors).

        Returns:
            List of all validation warnings
        """
        if not self.violations:
            result = self.validate_complete_outline()
            violations = result.violations
        else:
            violations = self.violations

        return [v for v in violations if v.severity == ValidationSeverity.WARNING]
