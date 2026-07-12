"""Tests for ChapterOutline artifact."""

import pytest
from datetime import datetime
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline


class TestChapterOutlineCreation:
    """Test basic ChapterOutline creation and initialization."""

    def test_chapter_outline_creation_with_all_fields(self):
        """Test successful creation with all required fields."""
        now = datetime.now()
        arc_progressions = {
            "character_arc": "Growing confidence",
            "plot_arc": "Mystery deepens",
        }

        outline = ChapterOutline(
            genre="mystery",
            story_id="story_001",
            name="Chapter 1 Outline",
            description="First chapter of the mystery",
            created_at=now,
            modified_at=now,
            parent_id="book_001",
            chapter_number=1,
            phase=1,
            title="The Discovery",
            goal="Introduce the protagonist and their world",
            conflict="An unexpected body is found",
            turning_point="The detective realizes they're involved",
            emotional_beat="hope → intrigue → uncertainty",
            arc_progressions=arc_progressions,
        )

        assert outline.genre == "mystery"
        assert outline.story_id == "story_001"
        assert outline.name == "Chapter 1 Outline"
        assert outline.description == "First chapter of the mystery"
        assert outline.created_at == now
        assert outline.modified_at == now
        assert outline.parent_id == "book_001"
        assert outline.chapter_number == 1
        assert outline.phase == 1
        assert outline.title == "The Discovery"
        assert outline.goal == "Introduce the protagonist and their world"
        assert outline.conflict == "An unexpected body is found"
        assert outline.turning_point == "The detective realizes they're involved"
        assert outline.emotional_beat == "hope → intrigue → uncertainty"
        assert outline.arc_progressions == arc_progressions

    def test_chapter_outline_artifact_type(self):
        """Test that artifact_type() returns 'chapter_outline'."""
        now = datetime.now()

        outline = ChapterOutline(
            genre="netorare",
            story_id="story_002",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=1,
            phase=5,
            title="Midpoint Chapter",
            goal="Test goal",
            conflict="Test conflict",
            turning_point="Test turning point",
            emotional_beat="Test beat",
        )

        assert outline.artifact_type() == "chapter_outline"

    def test_chapter_outline_with_optional_arc_progressions_empty(self):
        """Test creation without arc_progressions (defaults to empty dict)."""
        now = datetime.now()

        outline = ChapterOutline(
            genre="gentlefemdom",
            story_id="story_003",
            name="Simple Chapter",
            description="Chapter without arc progressions",
            created_at=now,
            modified_at=now,
            parent_id="book_001",
            chapter_number=2,
            phase=2,
            title="Chapter Two",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        assert outline.arc_progressions == {}

    def test_chapter_outline_with_multiple_arc_progressions(self):
        """Test creation with multiple arc progression entries."""
        now = datetime.now()
        arc_progressions = {
            "character_arc": "Confidence grows",
            "plot_arc": "Stakes increase",
            "theme_arc": "Truth emerges",
            "subplot_arc": "Relationship develops",
        }

        outline = ChapterOutline(
            genre="mystery",
            story_id="story_004",
            name="Complex Chapter",
            description="Chapter with many arcs",
            created_at=now,
            modified_at=now,
            parent_id="book_001",
            chapter_number=5,
            phase=5,
            title="Midpoint",
            goal="Everything changes",
            conflict="Multiple conflicts converge",
            turning_point="The revelation",
            emotional_beat="despair → hope",
            arc_progressions=arc_progressions,
        )

        assert len(outline.arc_progressions) == 4
        assert outline.arc_progressions["character_arc"] == "Confidence grows"
        assert outline.arc_progressions["theme_arc"] == "Truth emerges"

    def test_chapter_outline_with_none_parent_id(self):
        """Test creation with None parent_id."""
        now = datetime.now()

        outline = ChapterOutline(
            genre="mystery",
            story_id="story_005",
            name="Standalone Chapter",
            description="A standalone chapter",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=1,
            phase=1,
            title="Standalone",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        assert outline.parent_id is None


class TestChapterOutlineValidation:
    """Test ChapterOutline validation logic."""

    def test_phase_must_be_1_to_9_inclusive(self):
        """Test that phase must be between 1 and 9 inclusive."""
        now = datetime.now()

        # Phase 1 is valid
        outline = ChapterOutline(
            genre="mystery",
            story_id="story_006",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=1,
            phase=1,
            title="Test",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )
        assert outline.phase == 1

        # Phase 9 is valid
        outline = ChapterOutline(
            genre="mystery",
            story_id="story_006b",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=1,
            phase=9,
            title="Test",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )
        assert outline.phase == 9

    def test_phase_zero_is_rejected(self):
        """Test that phase 0 is rejected."""
        now = datetime.now()

        with pytest.raises(ValueError, match="phase must be between 1 and 9"):
            ChapterOutline(
                genre="mystery",
                story_id="story_007",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                chapter_number=1,
                phase=0,
                title="Test",
                goal="Goal",
                conflict="Conflict",
                turning_point="Turning point",
                emotional_beat="Beat",
            )

    def test_phase_10_is_rejected(self):
        """Test that phase 10 is rejected."""
        now = datetime.now()

        with pytest.raises(ValueError, match="phase must be between 1 and 9"):
            ChapterOutline(
                genre="mystery",
                story_id="story_008",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                chapter_number=1,
                phase=10,
                title="Test",
                goal="Goal",
                conflict="Conflict",
                turning_point="Turning point",
                emotional_beat="Beat",
            )

    def test_phase_negative_is_rejected(self):
        """Test that negative phase is rejected."""
        now = datetime.now()

        with pytest.raises(ValueError, match="phase must be between 1 and 9"):
            ChapterOutline(
                genre="mystery",
                story_id="story_009",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                chapter_number=1,
                phase=-1,
                title="Test",
                goal="Goal",
                conflict="Conflict",
                turning_point="Turning point",
                emotional_beat="Beat",
            )

    def test_chapter_number_must_be_greater_than_zero(self):
        """Test that chapter_number must be > 0."""
        now = datetime.now()

        # Chapter 1 is valid
        outline = ChapterOutline(
            genre="mystery",
            story_id="story_010",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=1,
            phase=1,
            title="Test",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )
        assert outline.chapter_number == 1

    def test_chapter_number_zero_is_rejected(self):
        """Test that chapter_number of 0 is rejected."""
        now = datetime.now()

        with pytest.raises(ValueError, match="chapter_number must be > 0"):
            ChapterOutline(
                genre="mystery",
                story_id="story_011",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                chapter_number=0,
                phase=1,
                title="Test",
                goal="Goal",
                conflict="Conflict",
                turning_point="Turning point",
                emotional_beat="Beat",
            )

    def test_chapter_number_negative_is_rejected(self):
        """Test that negative chapter_number is rejected."""
        now = datetime.now()

        with pytest.raises(ValueError, match="chapter_number must be > 0"):
            ChapterOutline(
                genre="mystery",
                story_id="story_012",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                chapter_number=-5,
                phase=1,
                title="Test",
                goal="Goal",
                conflict="Conflict",
                turning_point="Turning point",
                emotional_beat="Beat",
            )


class TestChapterOutlineGenreConsistency:
    """Test that ChapterOutline works identically across all genres."""

    @pytest.mark.parametrize("genre", ["mystery", "netorare", "gentlefemdom"])
    def test_chapter_outline_works_for_all_genres(self, genre):
        """Test that ChapterOutline class works for all 3 genres without special-casing."""
        now = datetime.now()

        outline = ChapterOutline(
            genre=genre,
            story_id=f"story_{genre}",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=3,
            phase=3,
            title=f"Chapter for {genre}",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        assert outline.genre == genre
        assert outline.artifact_type() == "chapter_outline"
        assert outline.chapter_number == 3
        assert outline.phase == 3


class TestChapterOutlineEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_chapter_outline_with_large_chapter_number(self):
        """Test with a very large chapter number."""
        now = datetime.now()

        outline = ChapterOutline(
            genre="mystery",
            story_id="story_013",
            name="Epic Chapter",
            description="Late chapter in epic book",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=500,
            phase=9,
            title="Final Conflict",
            goal="Resolve everything",
            conflict="Ultimate challenge",
            turning_point="The final truth",
            emotional_beat="despair → triumph",
        )

        assert outline.chapter_number == 500

    def test_chapter_outline_with_empty_string_fields(self):
        """Test that empty string fields are accepted (no content validation)."""
        now = datetime.now()

        outline = ChapterOutline(
            genre="mystery",
            story_id="story_014",
            name="",
            description="",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=1,
            phase=1,
            title="",
            goal="",
            conflict="",
            turning_point="",
            emotional_beat="",
        )

        assert outline.title == ""
        assert outline.goal == ""

    def test_chapter_outline_with_long_descriptive_text(self):
        """Test with long descriptive text in narrative fields."""
        now = datetime.now()
        long_text = (
            "This is a very long description of the chapter's purpose and meaning. "
            "It contains detailed information about what happens and why it matters. "
            * 5
        )

        outline = ChapterOutline(
            genre="mystery",
            story_id="story_015",
            name="Detailed Chapter",
            description="Chapter with detailed descriptions",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=10,
            phase=5,
            title="Complex Chapter",
            goal=long_text,
            conflict=long_text,
            turning_point=long_text,
            emotional_beat=long_text,
        )

        assert len(outline.goal) > 500

    def test_chapter_number_and_phase_are_accessible(self):
        """Test that chapter_number and phase attributes are directly accessible."""
        now = datetime.now()

        outline = ChapterOutline(
            genre="mystery",
            story_id="story_016",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            chapter_number=7,
            phase=6,
            title="Test",
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        # Directly access and verify
        assert hasattr(outline, "chapter_number")
        assert hasattr(outline, "phase")
        assert outline.chapter_number == 7
        assert outline.phase == 6
