"""Tests for Structure reference validator.

Tests cover:
- Valid references that pass all checks
- Missing chapter references that fail validation
- Broken parent references
- Orphaned artifacts detection
- Chronological ordering violations for setup→payoff
- Cross-artifact reference integrity
- Error message clarity and completeness
- Arc reference validation
- Chapter parent validation
- Setup→payoff chain validation
- Comprehensive validation orchestration
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

import pytest

from auteur.narrative_orchestration.validator.reference_validator import (
    ReferenceValidator,
    ValidationError,
    ValidationResult,
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
        **kwargs,
    ):
        super().__init__(
            artifact_id,
            chapter_number=chapter_number,
            parent_id=parent_id,
            phase=phase,
            title=title,
            **kwargs,
        )


class MockSequence(MockOutlineArtifact):
    """Mock sequence outline artifact."""

    def __init__(
        self,
        artifact_id: str,
        parent_id: Optional[str] = None,
        chapters: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(
            artifact_id,
            parent_id=parent_id,
            chapters=chapters or [],
            **kwargs,
        )


class MockBook(MockOutlineArtifact):
    """Mock book outline artifact."""

    def __init__(
        self,
        artifact_id: str,
        sequences: Optional[List[str]] = None,
        chapters: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(
            artifact_id,
            sequences=sequences or [],
            chapters=chapters or [],
            **kwargs,
        )


class MockCharacterArc(MockOutlineArtifact):
    """Mock character arc artifact."""

    def __init__(
        self,
        artifact_id: str,
        span_chapters: Optional[List[int]] = None,
        turning_points: Optional[List[Any]] = None,
        **kwargs,
    ):
        super().__init__(
            artifact_id,
            span_chapters=span_chapters or [],
            turning_points=turning_points or [],
            **kwargs,
        )


class MockStoryArc(MockOutlineArtifact):
    """Mock story arc artifact."""

    def __init__(
        self,
        artifact_id: str,
        span_chapters: Optional[List[int]] = None,
        checkpoints: Optional[List[Any]] = None,
        **kwargs,
    ):
        super().__init__(
            artifact_id,
            span_chapters=span_chapters or [],
            checkpoints=checkpoints or [],
            **kwargs,
        )


class MockTurningPoint:
    """Mock turning point for character arcs."""

    def __init__(self, chapter: int, moment: str, belief_shift: str):
        self.chapter = chapter
        self.moment = moment
        self.belief_shift = belief_shift


class MockArcCheckpoint:
    """Mock arc checkpoint for story arcs."""

    def __init__(self, phase: int, moment: str, chapter: Optional[int] = None):
        self.phase = phase
        self.moment = moment
        self.chapter = chapter


# Tests

class TestReferenceValidatorBasics:
    """Test basic validator initialization and setup."""

    def test_validator_initialization(self):
        """Test creating a reference validator with registry."""
        registry = {"chapter_01": MockChapter("chapter_01", 1)}
        validator = ReferenceValidator(registry)

        assert validator.registry == registry
        assert validator.resolver is not None
        assert validator.graph is not None
        assert len(validator.errors) == 0

    def test_validate_all_references_empty_registry(self):
        """Test validation with empty registry."""
        validator = ReferenceValidator({})
        result = validator.validate_all_references()

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_all_references_single_chapter(self):
        """Test validation with single valid chapter."""
        registry = {
            "book_001": MockBook("book_001"),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="book_001")
        }
        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is True
        assert len(result.errors) == 0


class TestValidateArcReferences:
    """Test arc reference validation."""

    def test_arc_references_valid_chapters(self):
        """Test arc with valid chapter references."""
        registry = {
            "book_001": MockBook("book_001"),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="book_001"),
            "chapter_02": MockChapter("chapter_02", 2, parent_id="book_001"),
            "chapter_05": MockChapter("chapter_05", 5, parent_id="book_001"),
            "character_arc_clara": MockCharacterArc(
                "character_arc_clara", span_chapters=[1, 2, 5]
            ),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is True

    def test_arc_references_missing_chapter(self):
        """Test arc referencing non-existent chapter."""
        registry = {
            "book_001": MockBook("book_001"),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="book_001"),
            "character_arc_clara": MockCharacterArc(
                "character_arc_clara", span_chapters=[1, 99]
            ),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is False
        # There will be errors for both the missing chapter 99 and the orphaned arc
        assert any(e.error_type == "missing_chapter_reference" for e in result.errors)
        assert any(e.artifact_id == "character_arc_clara" for e in result.errors)

    def test_story_arc_with_checkpoints(self):
        """Test story arc with checkpoint chapter references."""
        registry = {
            "book_001": MockBook("book_001"),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="book_001"),
            "chapter_05": MockChapter("chapter_05", 5, parent_id="book_001"),
            "story_arc_mystery": MockStoryArc(
                "story_arc_mystery",
                span_chapters=[1, 5],
                checkpoints=[
                    MockArcCheckpoint(phase=2, moment="clue found", chapter=1),
                    MockArcCheckpoint(phase=7, moment="mystery solved", chapter=5),
                ],
            ),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is True

    def test_story_arc_checkpoint_missing_chapter(self):
        """Test story arc checkpoint referencing missing chapter."""
        registry = {
            "book_001": MockBook("book_001"),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="book_001"),
            "story_arc_mystery": MockStoryArc(
                "story_arc_mystery",
                span_chapters=[1],
                checkpoints=[
                    MockArcCheckpoint(phase=2, moment="clue found", chapter=1),
                    MockArcCheckpoint(phase=7, moment="mystery solved", chapter=99),
                ],
            ),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is False
        assert any(e.error_type == "missing_checkpoint_chapter_reference" for e in result.errors)

    def test_character_arc_with_turning_points(self):
        """Test character arc with turning point chapter references."""
        registry = {
            "book_001": MockBook("book_001"),
            "chapter_02": MockChapter("chapter_02", 2, parent_id="book_001"),
            "chapter_05": MockChapter("chapter_05", 5, parent_id="book_001"),
            "character_arc_clara": MockCharacterArc(
                "character_arc_clara",
                span_chapters=[2, 5],
                turning_points=[
                    MockTurningPoint(chapter=2, moment="doubt", belief_shift="trust erodes"),
                    MockTurningPoint(chapter=5, moment="betrayal", belief_shift="broken"),
                ],
            ),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is True

    def test_character_arc_turning_point_missing_chapter(self):
        """Test character arc turning point referencing missing chapter."""
        registry = {
            "book_001": MockBook("book_001"),
            "chapter_02": MockChapter("chapter_02", 2, parent_id="book_001"),
            "character_arc_clara": MockCharacterArc(
                "character_arc_clara",
                span_chapters=[2],
                turning_points=[
                    MockTurningPoint(chapter=2, moment="doubt", belief_shift="trust erodes"),
                    MockTurningPoint(chapter=99, moment="betrayal", belief_shift="broken"),
                ],
            ),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is False
        assert any(e.error_type == "missing_beat_chapter_reference" for e in result.errors)


class TestValidateChapterReferences:
    """Test chapter reference validation."""

    def test_chapter_with_valid_parent(self):
        """Test chapter with valid parent sequence."""
        registry = {
            "book_001": MockBook("book_001"),
            "sequence_01": MockSequence("sequence_01", parent_id="book_001"),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="sequence_01"),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is True

    def test_chapter_with_valid_book_parent(self):
        """Test chapter with book as direct parent."""
        registry = {
            "book_001": MockBook("book_001"),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="book_001"),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is True

    def test_chapter_missing_parent_id(self):
        """Test chapter with no parent_id."""
        registry = {
            "chapter_01": MockChapter("chapter_01", 1, parent_id=None),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].error_type == "missing_parent_reference"

    def test_chapter_references_nonexistent_parent(self):
        """Test chapter referencing non-existent parent."""
        registry = {
            "chapter_01": MockChapter("chapter_01", 1, parent_id="sequence_99"),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is False
        assert result.errors[0].error_type == "missing_parent_artifact"
        assert result.errors[0].reference_id == "sequence_99"

    def test_chapter_parent_cannot_be_another_chapter(self):
        """Test that chapter parent cannot be another chapter."""
        registry = {
            "chapter_00": MockChapter("chapter_00", 0, parent_id="book_001"),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="chapter_00"),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is False
        assert any(e.error_type == "invalid_parent_type" for e in result.errors)


class TestValidateChronologicalOrdering:
    """Test setup→payoff chronological validation."""

    def test_valid_setup_payoff_ordering(self):
        """Test valid setup before payoff."""
        registry = {
            "chapter_03": MockChapter("chapter_03", 3, parent_id="book_001", setup_payoff_reference="chapter_15"),
            "chapter_15": MockChapter("chapter_15", 15, parent_id="book_001"),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        # Should be valid
        assert not any(e.error_type == "invalid_chronological_order" for e in result.errors)

    def test_invalid_setup_payoff_ordering_payoff_before_setup(self):
        """Test invalid: payoff before setup."""
        registry = {
            "chapter_15": MockChapter("chapter_15", 15, parent_id="book_001", setup_payoff_reference="chapter_03"),
            "chapter_03": MockChapter("chapter_03", 3, parent_id="book_001"),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        # Should have chronological error
        assert any(e.error_type == "invalid_chronological_order" for e in result.errors)

    def test_setup_payoff_same_chapter_invalid(self):
        """Test setup and payoff in same chapter (invalid)."""
        registry = {
            "chapter_05": MockChapter("chapter_05", 5, parent_id="book_001", setup_payoff_reference="chapter_05"),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        # Should have chronological error (setup and payoff must be different)
        assert any(e.error_type == "invalid_chronological_order" for e in result.errors)


class TestOrphanedArtifactsDetection:
    """Test detection of orphaned artifacts."""

    def test_orphaned_chapter_no_parent(self):
        """Test detection of orphaned chapter."""
        registry = {
            "chapter_05": MockChapter("chapter_05", 5, parent_id=None),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        # Chapter should be detected as orphaned in warnings/errors
        assert any("orphaned" in str(w).lower() or "no parent" in str(w).lower() for w in result.warnings)

    def test_orphaned_sequence_no_parent(self):
        """Test detection of orphaned sequence."""
        registry = {
            "sequence_01": MockSequence("sequence_01", parent_id=None),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        # Sequence should be detected as orphaned
        assert any("orphaned" in str(w).lower() or "no parent" in str(w).lower() for w in result.warnings)

    def test_orphaned_arc_no_references(self):
        """Test detection of orphaned arc."""
        registry = {
            "character_arc_clara": MockCharacterArc("character_arc_clara", span_chapters=[]),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        # Arc should be detected as orphaned
        assert any("orphaned" in str(w).lower() for w in result.warnings)


class TestErrorReporting:
    """Test error reporting and messages."""

    def test_validation_error_structure(self):
        """Test ValidationError has required fields."""
        error = ValidationError(
            artifact_id="chapter_01",
            reference_id="book_99",
            error_type="missing_parent_artifact",
            message="Parent book_99 not found",
        )

        assert error.artifact_id == "chapter_01"
        assert error.reference_id == "book_99"
        assert error.error_type == "missing_parent_artifact"
        assert "book_99" in error.message

    def test_validation_result_structure(self):
        """Test ValidationResult aggregates errors and warnings."""
        errors = [
            ValidationError("ch_01", "seq_99", "missing_parent_artifact", "Parent not found"),
        ]
        warnings = ["Orphaned artifact: arc_001"]

        result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1

    def test_report_validation_status_valid(self):
        """Test status report for valid validation."""
        registry = {
            "chapter_01": MockChapter("chapter_01", 1, parent_id="book_001"),
            "book_001": MockBook("book_001"),
        }

        validator = ReferenceValidator(registry)
        report = validator.report_validation_status()

        assert "valid" in report.lower()
        assert "✓" in report or "error" not in report.lower()

    def test_report_validation_status_with_errors(self):
        """Test status report includes error details."""
        registry = {
            "chapter_01": MockChapter("chapter_01", 1, parent_id="sequence_99"),
        }

        validator = ReferenceValidator(registry)
        report = validator.report_validation_status()

        assert "error" in report.lower() or "✗" in report
        assert "chapter_01" in report
        assert "sequence_99" in report


class TestComplexScenarios:
    """Test complex validation scenarios."""

    def test_complete_valid_outline(self):
        """Test complete valid outline with multiple levels."""
        registry = {
            "book_001": MockBook("book_001", sequences=["sequence_01"]),
            "sequence_01": MockSequence("sequence_01", parent_id="book_001", chapters=["chapter_01", "chapter_02"]),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="sequence_01"),
            "chapter_02": MockChapter("chapter_02", 2, parent_id="sequence_01"),
            "character_arc_protagonist": MockCharacterArc(
                "character_arc_protagonist", span_chapters=[1, 2]
            ),
            "story_arc_main": MockStoryArc("story_arc_main", span_chapters=[1, 2]),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_multiple_errors_collected(self):
        """Test validator collects multiple errors."""
        registry = {
            "book_001": MockBook("book_001"),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="sequence_99"),
            "chapter_02": MockChapter("chapter_02", 2, parent_id=None),
            "character_arc_clara": MockCharacterArc("character_arc_clara", span_chapters=[99]),
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is False
        # Errors: chapter_01 missing parent, chapter_02 missing parent, arc missing chapter
        assert len(result.errors) >= 2

    def test_mixed_book_and_sequence_parents(self):
        """Test chapters with different parent types."""
        registry = {
            "book_001": MockBook("book_001"),
            "sequence_01": MockSequence("sequence_01", parent_id="book_001"),
            "chapter_01": MockChapter("chapter_01", 1, parent_id="book_001"),  # Direct to book
            "chapter_02": MockChapter("chapter_02", 2, parent_id="sequence_01"),  # Through sequence
        }

        validator = ReferenceValidator(registry)
        result = validator.validate_all_references()

        assert result.is_valid is True
