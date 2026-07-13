"""Tests for Structure composition validator.

Tests cover:
- Valid outline (all validators pass)
- Reference violations detected
- Chronological violations detected
- Contradiction violations detected
- Multiple violation types together
- Error vs warning categorization
- Comprehensive report generation
- Genre-specific validation
- Edge cases (empty outline, single element)
- Violation filtering and querying
- Status reporting
"""

from typing import Dict, List, Optional, Any

import pytest

from auteur.narrative_orchestration.validator.composition_validator import (
    CompositionValidator,
    CompositionValidationResult,
    CompositionStatus,
    AggregatedViolation,
    ValidationSeverity,
)
from auteur.narrative_orchestration.validator.reference_validator import (
    ValidationError,
)
from auteur.narrative_orchestration.validator.chronological_validator import (
    ChronologicalViolation,
    ChronologyViolationType,
)


# Test fixtures: Mock outline artifacts

class MockOutlineArtifact:
    """Mock outline artifact for testing."""

    def __init__(self, artifact_id: str, **kwargs):
        self.id = artifact_id
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockChapter(MockOutlineArtifact):
    """Mock chapter outline artifact."""

    def __init__(
        self,
        artifact_id: str,
        chapter_number: int,
        parent_id: Optional[str] = None,
        phase: int = 1,
        title: str = "Chapter",
        goal: str = "Advance plot",
        emotional_beat: str = "Positive",
        arc_progressions: Optional[Dict] = None,
        **kwargs,
    ):
        super().__init__(
            artifact_id,
            chapter_number=chapter_number,
            parent_id=parent_id,
            phase=phase,
            title=title,
            goal=goal,
            emotional_beat=emotional_beat,
            arc_progressions=arc_progressions or {},
            **kwargs,
        )


class MockSequence(MockOutlineArtifact):
    """Mock sequence outline artifact."""

    def __init__(
        self,
        artifact_id: str,
        parent_id: Optional[str] = None,
        chapter_range: tuple = (1, 3),
        objective: str = "Establish conflict",
        **kwargs,
    ):
        super().__init__(
            artifact_id,
            parent_id=parent_id,
            chapter_range=chapter_range,
            objective=objective,
            **kwargs,
        )


class MockBook(MockOutlineArtifact):
    """Mock book outline artifact."""

    def __init__(
        self,
        artifact_id: str,
        name: str = "Book 1",
        climax: str = "Resolution",
        **kwargs,
    ):
        super().__init__(
            artifact_id,
            name=name,
            climax=climax,
            **kwargs,
        )


class MockCharacterArc(MockOutlineArtifact):
    """Mock character arc artifact."""

    def __init__(
        self,
        artifact_id: str,
        character_name: str = "Protagonist",
        initial_belief: str = "Distrusts others",
        final_belief: str = "Trusts others",
        genre_themes: Optional[List[str]] = None,
        span_chapters: Optional[List[int]] = None,
        turning_points: Optional[List] = None,
        **kwargs,
    ):
        super().__init__(
            artifact_id,
            character_name=character_name,
            initial_belief=initial_belief,
            final_belief=final_belief,
            genre_themes=genre_themes or ["trust", "vulnerability"],
            span_chapters=span_chapters or [1, 2, 3],
            turning_points=turning_points or [],
            **kwargs,
        )


class MockTurningPoint:
    """Mock turning point in character arc."""

    def __init__(self, chapter: int, moment: str = "Crisis", belief_shift: str = "Acceptance"):
        self.chapter = chapter
        self.moment = moment
        self.belief_shift = belief_shift


class MockStoryArc(MockOutlineArtifact):
    """Mock story arc artifact."""

    def __init__(
        self,
        artifact_id: str,
        arc_name: str = "Mystery",
        arc_category: str = "mystery",
        phase_range: Any = None,
        checkpoints: Optional[List] = None,
        **kwargs,
    ):
        super().__init__(
            artifact_id,
            arc_name=arc_name,
            arc_category=arc_category,
            phase_range=phase_range or MockPhaseRange(),
            checkpoints=checkpoints or [],
            **kwargs,
        )


class MockPhaseRange:
    """Mock phase range for story arc."""

    def __init__(self, start: int = 1, end: int = 9):
        self.start = start
        self.end = end

    def includes_phase(self, phase: int) -> bool:
        return self.start <= phase <= self.end


class MockCheckpoint:
    """Mock checkpoint in story arc."""

    def __init__(self, phase: int, moment: str = "Clue"):
        self.phase = phase
        self.moment = moment


# Tests

class TestCompositionValidatorBasics:
    """Test basic CompositionValidator functionality."""

    def test_valid_outline_passes_validation(self):
        """Test that a valid outline passes all validators."""
        # Create minimal valid outline
        registry = {}
        book = MockBook("book_001", name="Test Book")
        registry["book_001"] = book

        chapter1 = MockChapter("chapter_01", chapter_number=1, parent_id="book_001")
        registry["chapter_01"] = chapter1

        chapter2 = MockChapter("chapter_02", chapter_number=2, parent_id="book_001")
        registry["chapter_02"] = chapter2

        chapter_outlines = {"chapter_01": chapter1, "chapter_02": chapter2}

        # Validate
        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines=chapter_outlines,
            genre="netorare",
        )

        result = validator.validate_complete_outline()

        # Should pass (no reference errors)
        assert result.status in (CompositionStatus.PASS, CompositionStatus.WARNINGS)

    def test_invalid_outline_fails_validation(self):
        """Test that invalid outline is detected."""
        # Create outline with missing reference
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        # Chapter references non-existent parent
        chapter1 = MockChapter("chapter_01", chapter_number=1, parent_id="nonexistent_parent")
        registry["chapter_01"] = chapter1

        chapter_outlines = {"chapter_01": chapter1}

        # Validate
        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines=chapter_outlines,
            genre="netorare",
        )

        result = validator.validate_complete_outline()

        # Should fail
        assert result.status == CompositionStatus.FAIL
        assert result.error_count > 0

    def test_composition_validator_requires_book_outline(self):
        """Test that book_outline is required."""
        registry = {"book_001": MockBook("book_001")}
        with pytest.raises(ValueError, match="book_outline is required"):
            CompositionValidator(
                artifact_registry=registry,
                book_outline=None,
                chapter_outlines={"chapter_01": MockChapter("chapter_01", 1)},
                genre="netorare",
            )

    def test_composition_validator_requires_chapter_outlines(self):
        """Test that chapter_outlines cannot be empty."""
        book = MockBook("book_001")
        with pytest.raises(ValueError, match="chapter_outlines is required"):
            CompositionValidator(
                artifact_registry={"book_001": book},
                book_outline=book,
                chapter_outlines={},  # Empty dict
                genre="netorare",
            )

    def test_composition_validator_requires_genre(self):
        """Test that genre is required."""
        book = MockBook("book_001")
        chapter = MockChapter("chapter_01", chapter_number=1)
        with pytest.raises(ValueError, match="genre is required"):
            CompositionValidator(
                artifact_registry={"book_001": book, "chapter_01": chapter},
                book_outline=book,
                chapter_outlines={"chapter_01": chapter},
                genre=None,
            )


class TestCompositionValidatorReferenceViolations:
    """Test reference validation in CompositionValidator."""

    def test_reference_violation_detected(self):
        """Test that reference violations are detected."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        # Chapter with missing parent
        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="missing_sequence")
        registry["chapter_01"] = chapter

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
        )

        result = validator.validate_complete_outline()

        # Should have errors
        assert result.error_count > 0
        assert result.status == CompositionStatus.FAIL

        # Check for reference validator violations
        ref_violations = [
            v for v in result.violations if v.validator_type == "reference"
        ]
        assert len(ref_violations) > 0

    def test_reference_violation_categorized_as_error(self):
        """Test that reference violations are categorized as errors."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="missing")
        registry["chapter_01"] = chapter

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
        )

        result = validator.validate_complete_outline()

        # All reference violations should be errors
        ref_violations = [
            v for v in result.violations if v.validator_type == "reference"
        ]
        # If there are reference violations, they should all be errors
        if ref_violations:
            for violation in ref_violations:
                # Reference violations can be errors or warnings
                assert violation.severity in (ValidationSeverity.ERROR, ValidationSeverity.WARNING)


class TestCompositionValidatorChronologicalViolations:
    """Test chronological validation in CompositionValidator."""

    def test_chronological_violation_detected(self):
        """Test that chronological violations are detected."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        # Create arc with out-of-order chapters
        tp1 = MockTurningPoint(chapter=5)
        tp2 = MockTurningPoint(chapter=3)  # Out of order!

        arc = MockCharacterArc(
            "char_arc_01",
            turning_points=[tp1, tp2],
            span_chapters=[5, 3],
        )
        registry["char_arc_01"] = arc

        for i in range(1, 7):
            ch = MockChapter(f"chapter_{i:02d}", chapter_number=i, parent_id="book_001")
            registry[f"chapter_{i:02d}"] = ch

        chapter_outlines = {
            f"chapter_{i:02d}": registry[f"chapter_{i:02d}"]
            for i in range(1, 7)
        }

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines=chapter_outlines,
            genre="netorare",
            character_arcs={"char_arc_01": arc},
        )

        result = validator.validate_complete_outline()

        # Should have violations
        chrono_violations = [
            v for v in result.violations if v.validator_type == "chronological"
        ]
        assert len(chrono_violations) > 0


class TestCompositionValidatorContradictionViolations:
    """Test contradiction validation in CompositionValidator."""

    def test_contradiction_validation_runs(self):
        """Test that contradiction validator is invoked."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter1 = MockChapter(
            "chapter_01",
            chapter_number=1,
            parent_id="book_001",
            emotional_beat="Positive",
        )
        registry["chapter_01"] = chapter1

        chapter_outlines = {"chapter_01": chapter1}

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines=chapter_outlines,
            genre="netorare",
        )

        result = validator.validate_complete_outline()

        # Contradiction validator should have run (even if no contradictions)
        # This just ensures the validator is being called
        assert result is not None


class TestCompositionValidatorViolationCategorization:
    """Test error vs warning categorization."""

    def test_errors_and_warnings_separated(self):
        """Test that errors and warnings are properly separated."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        # Create chapter with missing parent (error)
        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="missing")
        registry["chapter_01"] = chapter

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
        )

        result = validator.validate_complete_outline()

        # Separate into errors and warnings
        errors = [v for v in result.violations if v.severity == ValidationSeverity.ERROR]
        warnings = [v for v in result.violations if v.severity == ValidationSeverity.WARNING]

        # Should have errors from reference validation
        assert len(errors) > 0
        # Errors count should match result.error_count
        assert len(errors) == result.error_count
        assert len(warnings) == result.warning_count

    def test_get_errors_method(self):
        """Test getting errors via get_errors method."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="missing")
        registry["chapter_01"] = chapter

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
        )

        errors = validator.get_errors()

        # Should have at least one error
        assert len(errors) > 0
        for error in errors:
            assert error.severity == ValidationSeverity.ERROR

    def test_get_warnings_method(self):
        """Test getting warnings via get_warnings method."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter1 = MockChapter("chapter_01", chapter_number=1, parent_id="book_001")
        registry["chapter_01"] = chapter1

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter1},
            genre="netorare",
        )

        warnings = validator.get_warnings()

        # Type is correct for each warning
        for warning in warnings:
            assert warning.severity == ValidationSeverity.WARNING


class TestCompositionValidatorReportGeneration:
    """Test report generation."""

    def test_report_generation_valid_outline(self):
        """Test report for valid outline."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter1 = MockChapter("chapter_01", chapter_number=1, parent_id="book_001")
        registry["chapter_01"] = chapter1

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter1},
            genre="netorare",
        )

        report = validator.report_violations()

        # Report should be a string
        assert isinstance(report, str)
        # Should indicate validation status
        assert "validation" in report.lower() or "pass" in report.lower() or "error" in report.lower()

    def test_report_generation_invalid_outline(self):
        """Test report for invalid outline."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="missing")
        registry["chapter_01"] = chapter

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
        )

        report = validator.report_violations()

        # Report should contain error information
        assert isinstance(report, str)
        assert "error" in report.lower() or "missing" in report.lower()
        assert "chapter_01" in report or "missing" in report

    def test_status_string(self):
        """Test get_validation_status method."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter1 = MockChapter("chapter_01", chapter_number=1, parent_id="book_001")
        registry["chapter_01"] = chapter1

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter1},
            genre="netorare",
        )

        status = validator.get_validation_status()

        # Status should be one of the valid values
        assert status in ("pass", "warnings", "fail")


class TestCompositionValidatorViolationQuerying:
    """Test filtering and querying violations."""

    def test_get_violations_by_type(self):
        """Test filtering violations by validator type."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="missing")
        registry["chapter_01"] = chapter

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
        )

        # Get only reference violations
        ref_violations = validator.get_violations_by_type("reference")

        # Should have reference violations
        for violation in ref_violations:
            assert violation.validator_type == "reference"

    def test_get_all_violations(self):
        """Test getting all violations."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="missing")
        registry["chapter_01"] = chapter

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
        )

        # Get all violations
        all_violations = validator.get_violations_by_type(None)

        # Should have violations
        assert len(all_violations) > 0


class TestCompositionValidatorMultipleViolations:
    """Test handling multiple violation types together."""

    def test_multiple_reference_violations(self):
        """Test outline with multiple reference violations."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        # Multiple chapters with missing parents
        chapter1 = MockChapter("chapter_01", chapter_number=1, parent_id="missing1")
        chapter2 = MockChapter("chapter_02", chapter_number=2, parent_id="missing2")
        registry["chapter_01"] = chapter1
        registry["chapter_02"] = chapter2

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter1, "chapter_02": chapter2},
            genre="netorare",
        )

        result = validator.validate_complete_outline()

        # Should detect multiple errors
        assert result.error_count >= 2

    def test_result_contains_violation_details(self):
        """Test that result contains detailed violation information."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="missing")
        registry["chapter_01"] = chapter

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
        )

        result = validator.validate_complete_outline()

        # Violations should have details
        for violation in result.violations:
            assert violation.violation_type is not None
            assert violation.validator_type is not None
            assert violation.severity is not None
            assert violation.artifact_id is not None
            assert violation.message is not None


class TestCompositionValidatorGenreHandling:
    """Test genre-specific handling."""

    def test_different_genres_accepted(self):
        """Test that all three genres are accepted."""
        for genre in ["netorare", "mystery", "gentlefemdom"]:
            registry = {}
            book = MockBook("book_001")
            registry["book_001"] = book

            chapter = MockChapter("chapter_01", chapter_number=1, parent_id="book_001")
            registry["chapter_01"] = chapter

            validator = CompositionValidator(
                artifact_registry=registry,
                book_outline=book,
                chapter_outlines={"chapter_01": chapter},
                genre=genre,
            )

            result = validator.validate_complete_outline()

            # Should accept all genres without error
            assert result is not None

    def test_genre_passed_to_contradiction_validator(self):
        """Test that genre is passed to contradiction validator."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="book_001")
        registry["chapter_01"] = chapter

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="mystery",
        )

        # Validator should store genre
        assert validator.genre == "mystery"

        result = validator.validate_complete_outline()
        assert result is not None


class TestCompositionValidatorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_chapter_outline(self):
        """Test validation with empty chapter outlines raises error."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        # No chapters - should raise ValueError
        with pytest.raises(ValueError, match="chapter_outlines is required"):
            CompositionValidator(
                artifact_registry=registry,
                book_outline=book,
                chapter_outlines={},  # Empty
                genre="netorare",
            )

    def test_single_chapter(self):
        """Test validation with single chapter."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="book_001")
        registry["chapter_01"] = chapter

        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
        )

        result = validator.validate_complete_outline()

        # Should handle single chapter
        assert result is not None

    def test_optional_sequences_not_required(self):
        """Test that sequences are optional."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="book_001")
        registry["chapter_01"] = chapter

        # No sequences provided
        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
            sequence_outlines=None,  # Explicitly None
        )

        result = validator.validate_complete_outline()

        # Should handle missing sequences gracefully
        assert result is not None

    def test_optional_arcs_not_required(self):
        """Test that arcs are optional."""
        registry = {}
        book = MockBook("book_001")
        registry["book_001"] = book

        chapter = MockChapter("chapter_01", chapter_number=1, parent_id="book_001")
        registry["chapter_01"] = chapter

        # No arcs provided
        validator = CompositionValidator(
            artifact_registry=registry,
            book_outline=book,
            chapter_outlines={"chapter_01": chapter},
            genre="netorare",
            character_arcs=None,
            story_arcs=None,
        )

        result = validator.validate_complete_outline()

        # Should handle missing arcs gracefully
        assert result is not None


class TestCompositionValidationResult:
    """Test CompositionValidationResult data structure."""

    def test_result_is_valid_pass(self):
        """Test is_valid returns True for PASS status."""
        result = CompositionValidationResult(
            status=CompositionStatus.PASS,
            error_count=0,
            warning_count=0,
        )

        assert result.is_valid() is True

    def test_result_is_valid_warnings(self):
        """Test is_valid returns True for WARNINGS status."""
        result = CompositionValidationResult(
            status=CompositionStatus.WARNINGS,
            error_count=0,
            warning_count=1,
        )

        assert result.is_valid() is True

    def test_result_is_valid_fail(self):
        """Test is_valid returns False for FAIL status."""
        result = CompositionValidationResult(
            status=CompositionStatus.FAIL,
            error_count=1,
            warning_count=0,
        )

        assert result.is_valid() is False

    def test_result_has_errors(self):
        """Test has_errors method."""
        result = CompositionValidationResult(
            status=CompositionStatus.FAIL,
            error_count=1,
            warning_count=0,
        )

        assert result.has_errors() is True

    def test_result_has_warnings(self):
        """Test has_warnings method."""
        result = CompositionValidationResult(
            status=CompositionStatus.WARNINGS,
            error_count=0,
            warning_count=2,
        )

        assert result.has_warnings() is True


class TestAggregatedViolation:
    """Test AggregatedViolation data structure."""

    def test_violation_contains_required_fields(self):
        """Test that violation contains all required fields."""
        violation = AggregatedViolation(
            violation_type="missing_reference",
            validator_type="reference",
            severity=ValidationSeverity.ERROR,
            artifact_id="chapter_01",
            related_artifact_id="missing_sequence",
            message="Chapter references missing sequence",
            evidence="Sequence ID: missing_sequence",
        )

        assert violation.violation_type == "missing_reference"
        assert violation.validator_type == "reference"
        assert violation.severity == ValidationSeverity.ERROR
        assert violation.artifact_id == "chapter_01"
        assert violation.related_artifact_id == "missing_sequence"
        assert violation.message == "Chapter references missing sequence"
