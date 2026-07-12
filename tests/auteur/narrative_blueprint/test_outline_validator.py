"""Tests for ContainerValidator - hierarchical outline consistency validator."""

import pytest
from datetime import datetime
from typing import List

from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.outline_types import ContainerArtifact


class TestContainerValidatorImports:
    """Test that ContainerValidator can be imported."""

    def test_import_container_validator(self):
        """Test that ContainerValidator can be imported."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        assert ContainerValidator is not None


class TestContainerValidatorBasics:
    """Test basic ContainerValidator functionality."""

    def test_validator_returns_tuple(self):
        """Test that validate_consistency returns a tuple."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        validator = ContainerValidator()
        result = validator.validate_consistency([])
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_outline_list_is_valid(self):
        """Test that empty outline list passes validation."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([])
        assert is_valid is True
        assert errors == []

    def test_valid_returns_true_empty_errors(self):
        """Test that valid outlines return (True, [])."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=10,
            structure="3-act",
            phases_summary=phases,
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book])
        assert is_valid is True
        assert errors == []

    def test_invalid_returns_false_with_errors(self):
        """Test that invalid outlines return (False, [...errors...])."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=5,
            structure="3-act",
            phases_summary=phases,
        )

        chapter = ChapterOutline(
            genre="mystery",
            story_id="story_001",
            name="Chapter",
            description="Chapter outline",
            created_at=now,
            modified_at=now,
            parent_id="book_001",
            chapter_number=10,  # Exceeds book estimate of 5
            phase=1,
            title="Chapter 10",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book, chapter])
        assert is_valid is False
        assert len(errors) > 0


class TestBookOutlineValidation:
    """Test book outline validation rules."""

    def test_book_outline_alone_is_valid(self):
        """Test that a single BookOutline passes validation."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=20,
            structure="3-act",
            phases_summary=phases,
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book])
        assert is_valid is True
        assert errors == []

    def test_multiple_books_is_valid(self):
        """Test that multiple BookOutlines are allowed (partial spec)."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book1 = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book 1",
            description="Book 1",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Book 1",
            chapter_estimate=10,
            structure="3-act",
            phases_summary=phases,
        )

        book2 = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book 2",
            description="Book 2",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Book 2",
            chapter_estimate=15,
            structure="3-act",
            phases_summary=phases,
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book1, book2])
        assert is_valid is True
        assert errors == []


class TestChapterValidation:
    """Test chapter outline validation rules."""

    def test_chapter_alone_is_valid(self):
        """Test that a single ChapterOutline passes validation."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()

        chapter = ChapterOutline(
            genre="mystery",
            story_id="story_001",
            name="Chapter",
            description="Chapter outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=1,
            phase=1,
            title="Chapter 1",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([chapter])
        assert is_valid is True
        assert errors == []

    def test_chapter_with_valid_phase_passes(self):
        """Test that chapters with phases 1-9 pass validation."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        validator = ContainerValidator()

        for phase in range(1, 10):
            chapter = ChapterOutline(
                genre="mystery",
                story_id="story_001",
                name=f"Chapter Phase {phase}",
                description="Chapter outline",
                created_at=now,
                modified_at=now,
                parent_id=None,
                chapter_number=phase,
                phase=phase,
                title=f"Chapter {phase}",
                goal="Goal",
                conflict="Conflict",
                turning_point="Turning point",
                emotional_beat="Beat",
            )

            is_valid, errors = validator.validate_consistency([chapter])
            assert is_valid is True, f"Phase {phase} should be valid"
            assert errors == [], f"Phase {phase} should have no errors"


class TestBookChapterConsistency:
    """Test consistency between BookOutline and ChapterOutline."""

    def test_chapter_within_book_estimate_passes(self):
        """Test that chapters within book's estimate pass validation."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=20,
            structure="3-act",
            phases_summary=phases,
        )

        chapters = []
        for i in range(1, 11):  # 10 chapters, estimate is 20
            chapter = ChapterOutline(
                genre="mystery",
                story_id="story_001",
                name=f"Chapter {i}",
                description=f"Chapter {i}",
                created_at=now,
                modified_at=now,
                parent_id=None,
                chapter_number=i,
                phase=(i % 9) + 1,
                title=f"Chapter {i}",
                goal="Goal",
                conflict="Conflict",
                turning_point="Turning point",
                emotional_beat="Beat",
            )
            chapters.append(chapter)

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book] + chapters)
        assert is_valid is True
        assert errors == []

    def test_chapter_exceeding_book_estimate_fails(self):
        """Test that chapters exceeding book's estimate fail validation."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=5,
            structure="3-act",
            phases_summary=phases,
        )

        chapter = ChapterOutline(
            genre="mystery",
            story_id="story_001",
            name="Chapter",
            description="Chapter outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=10,  # Exceeds estimate of 5
            phase=1,
            title="Chapter 10",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book, chapter])
        assert is_valid is False
        assert len(errors) > 0
        # Error message should mention the chapter exceeding the estimate
        assert any("exceed" in error.lower() or "chapter" in error.lower() for error in errors)

    def test_chapter_at_book_estimate_edge_passes(self):
        """Test that chapter at exact book estimate passes."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=10,
            structure="3-act",
            phases_summary=phases,
        )

        chapter = ChapterOutline(
            genre="mystery",
            story_id="story_001",
            name="Chapter",
            description="Chapter outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=10,  # Exactly at estimate
            phase=5,
            title="Chapter 10",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book, chapter])
        assert is_valid is True
        assert errors == []

    def test_multiple_chapters_exceeding_estimate_all_reported(self):
        """Test that multiple chapters exceeding estimate are all reported."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=5,
            structure="3-act",
            phases_summary=phases,
        )

        chapters = []
        for i in [10, 15, 20]:  # All exceed estimate of 5
            chapter = ChapterOutline(
                genre="mystery",
                story_id="story_001",
                name=f"Chapter {i}",
                description=f"Chapter {i}",
                created_at=now,
                modified_at=now,
                parent_id=None,
                chapter_number=i,
                phase=1,
                title=f"Chapter {i}",
                goal="Goal",
                conflict="Conflict",
                turning_point="Turning point",
                emotional_beat="Beat",
            )
            chapters.append(chapter)

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book] + chapters)
        assert is_valid is False
        assert len(errors) >= 3  # At least one error per chapter


class TestMixedGenreValidation:
    """Test validation across different genres."""

    @pytest.mark.parametrize("genre", ["mystery", "netorare", "gentlefemdom"])
    def test_validator_works_for_all_genres(self, genre):
        """Test that validator works identically for all 3 genres."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre=genre,
            story_id=f"story_{genre}",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=10,
            structure="3-act",
            phases_summary=phases,
        )

        chapter = ChapterOutline(
            genre=genre,
            story_id=f"story_{genre}",
            name="Chapter",
            description="Chapter outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=5,
            phase=5,
            title="Chapter 5",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book, chapter])
        assert is_valid is True
        assert errors == []


class TestValidatorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_validator_with_none_in_list_ignored(self):
        """Test that None values in outline list are handled gracefully."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=10,
            structure="3-act",
            phases_summary=phases,
        )

        # Validator should handle None gracefully (either ignore or report as error)
        validator = ContainerValidator()
        try:
            is_valid, errors = validator.validate_consistency([book, None])
            # If it doesn't raise, it should handle None gracefully
            assert isinstance(is_valid, bool)
            assert isinstance(errors, list)
        except TypeError:
            # It's acceptable to raise TypeError for None
            pass

    def test_book_estimate_of_1_with_chapter_1_passes(self):
        """Test minimal book with 1 chapter estimate and 1 chapter."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Minimal Book",
            chapter_estimate=1,
            structure="3-act",
            phases_summary=phases,
        )

        chapter = ChapterOutline(
            genre="mystery",
            story_id="story_001",
            name="Chapter",
            description="Chapter outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=1,
            phase=1,
            title="Only Chapter",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book, chapter])
        assert is_valid is True
        assert errors == []

    def test_book_estimate_of_1_with_chapter_2_fails(self):
        """Test minimal book with 1 chapter estimate but chapter 2 fails."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Minimal Book",
            chapter_estimate=1,
            structure="3-act",
            phases_summary=phases,
        )

        chapter = ChapterOutline(
            genre="mystery",
            story_id="story_001",
            name="Chapter",
            description="Chapter outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=2,  # Exceeds estimate of 1
            phase=1,
            title="Second Chapter",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book, chapter])
        assert is_valid is False
        assert len(errors) > 0


class TestValidatorRobustness:
    """Test validator robustness and error message quality."""

    def test_error_messages_are_descriptive(self):
        """Test that error messages clearly describe the problem."""
        from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator

        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        book = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book",
            description="Book outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=3,
            structure="3-act",
            phases_summary=phases,
        )

        chapter = ChapterOutline(
            genre="mystery",
            story_id="story_001",
            name="Chapter",
            description="Chapter outline",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=10,
            phase=1,
            title="Chapter 10",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([book, chapter])
        assert is_valid is False
        assert len(errors) > 0
        # Error message should mention chapter number and estimate
        error_text = " ".join(errors)
        assert "10" in error_text or "chapter" in error_text.lower()
        assert "3" in error_text or "estimate" in error_text.lower()
