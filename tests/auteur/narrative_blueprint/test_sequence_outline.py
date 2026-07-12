"""Tests for SequenceOutline artifact."""

import pytest
from datetime import datetime
from auteur.narrative_blueprint.schema.sequence_outline import SequenceOutline


class TestSequenceOutlineCreation:
    """Test basic SequenceOutline creation and initialization."""

    def test_sequence_outline_creation_with_all_fields(self):
        """Test successful creation with all required fields."""
        now = datetime.now()
        key_scenes = ["Discovery of clue", "Confrontation", "Resolution"]

        outline = SequenceOutline(
            genre="mystery",
            story_id="story_001",
            name="Sequence 1",
            description="First sequence of the narrative",
            created_at=now,
            modified_at=now,
            parent_id="book_001",
            sequence_number=1,
            objective="Introduce the mystery and main suspects",
            chapter_range=(1, 5),
            key_scenes=key_scenes,
        )

        assert outline.genre == "mystery"
        assert outline.story_id == "story_001"
        assert outline.name == "Sequence 1"
        assert outline.description == "First sequence of the narrative"
        assert outline.created_at == now
        assert outline.modified_at == now
        assert outline.parent_id == "book_001"
        assert outline.sequence_number == 1
        assert outline.objective == "Introduce the mystery and main suspects"
        assert outline.chapter_range == (1, 5)
        assert outline.key_scenes == key_scenes

    def test_sequence_outline_artifact_type(self):
        """Test that artifact_type() returns 'sequence_outline'."""
        now = datetime.now()

        outline = SequenceOutline(
            genre="netorare",
            story_id="story_002",
            name="Sequence",
            description="Test sequence",
            created_at=now,
            modified_at=now,
            parent_id=None,
            sequence_number=1,
            objective="Test objective",
            chapter_range=(1, 3),
        )

        assert outline.artifact_type() == "sequence_outline"

    def test_sequence_outline_with_empty_key_scenes(self):
        """Test creation with empty key_scenes list."""
        now = datetime.now()

        outline = SequenceOutline(
            genre="gentlefemdom",
            story_id="story_003",
            name="Sequence",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            sequence_number=2,
            objective="Test",
            chapter_range=(10, 15),
            key_scenes=[],
        )

        assert outline.key_scenes == []

    def test_sequence_outline_with_none_parent_id(self):
        """Test creation with None parent_id."""
        now = datetime.now()

        outline = SequenceOutline(
            genre="mystery",
            story_id="story_004",
            name="Standalone Sequence",
            description="A sequence without parent",
            created_at=now,
            modified_at=now,
            parent_id=None,
            sequence_number=1,
            objective="Objective",
            chapter_range=(1, 10),
        )

        assert outline.parent_id is None

    def test_sequence_outline_with_multiple_key_scenes(self):
        """Test creation with multiple key scenes."""
        now = datetime.now()
        scenes = [
            "Opening scene",
            "First major plot point",
            "Escalation",
            "Climactic moment",
            "Transition to resolution",
        ]

        outline = SequenceOutline(
            genre="mystery",
            story_id="story_005",
            name="Complex Sequence",
            description="Sequence with many scenes",
            created_at=now,
            modified_at=now,
            parent_id="book_001",
            sequence_number=3,
            objective="Build tension and reveal clues",
            chapter_range=(20, 30),
            key_scenes=scenes,
        )

        assert len(outline.key_scenes) == 5
        assert outline.key_scenes == scenes


class TestSequenceOutlineValidation:
    """Test SequenceOutline validation logic."""

    def test_sequence_number_must_be_positive(self):
        """Test that sequence_number must be > 0."""
        now = datetime.now()

        with pytest.raises(ValueError, match="sequence_number must be > 0"):
            SequenceOutline(
                genre="mystery",
                story_id="story_006",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                sequence_number=0,
                objective="Test",
                chapter_range=(1, 5),
            )

    def test_sequence_number_negative_is_rejected(self):
        """Test that negative sequence_number is rejected."""
        now = datetime.now()

        with pytest.raises(ValueError, match="sequence_number must be > 0"):
            SequenceOutline(
                genre="mystery",
                story_id="story_007",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                sequence_number=-1,
                objective="Test",
                chapter_range=(1, 5),
            )

    def test_chapter_range_start_must_be_positive(self):
        """Test that chapter_range start must be > 0."""
        now = datetime.now()

        with pytest.raises(ValueError, match="chapter_range start and end must be > 0"):
            SequenceOutline(
                genre="mystery",
                story_id="story_008",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                sequence_number=1,
                objective="Test",
                chapter_range=(0, 5),
            )

    def test_chapter_range_end_must_be_positive(self):
        """Test that chapter_range end must be > 0."""
        now = datetime.now()

        with pytest.raises(ValueError, match="chapter_range start and end must be > 0"):
            SequenceOutline(
                genre="mystery",
                story_id="story_009",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                sequence_number=1,
                objective="Test",
                chapter_range=(1, 0),
            )

    def test_chapter_range_start_must_be_less_than_or_equal_to_end(self):
        """Test that chapter_range start <= end."""
        now = datetime.now()

        with pytest.raises(ValueError, match="chapter_range start must be <= end"):
            SequenceOutline(
                genre="mystery",
                story_id="story_010",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                sequence_number=1,
                objective="Test",
                chapter_range=(10, 5),
            )

    def test_chapter_range_with_negative_values(self):
        """Test that negative chapter_range values are rejected."""
        now = datetime.now()

        with pytest.raises(ValueError, match="chapter_range start and end must be > 0"):
            SequenceOutline(
                genre="mystery",
                story_id="story_011",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                sequence_number=1,
                objective="Test",
                chapter_range=(-1, 5),
            )

    def test_sequence_number_one_is_valid(self):
        """Test that sequence_number of 1 is valid."""
        now = datetime.now()

        outline = SequenceOutline(
            genre="mystery",
            story_id="story_012",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            sequence_number=1,
            objective="Test",
            chapter_range=(1, 5),
        )

        assert outline.sequence_number == 1

    def test_chapter_range_same_start_and_end_is_valid(self):
        """Test that chapter_range with start == end is valid."""
        now = datetime.now()

        outline = SequenceOutline(
            genre="mystery",
            story_id="story_013",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            sequence_number=1,
            objective="Test",
            chapter_range=(5, 5),
        )

        assert outline.chapter_range == (5, 5)


class TestSequenceOutlineGenreConsistency:
    """Test that SequenceOutline works identically across all genres."""

    @pytest.mark.parametrize("genre", ["mystery", "netorare", "gentlefemdom"])
    def test_sequence_outline_works_for_all_genres(self, genre):
        """Test that SequenceOutline class works for all 3 genres without special-casing."""
        now = datetime.now()

        outline = SequenceOutline(
            genre=genre,
            story_id=f"story_{genre}",
            name="Sequence",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            sequence_number=1,
            objective="Test objective",
            chapter_range=(1, 10),
        )

        assert outline.genre == genre
        assert outline.artifact_type() == "sequence_outline"
        assert outline.sequence_number == 1


class TestSequenceOutlineEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_sequence_outline_with_large_sequence_number(self):
        """Test with a very large sequence number."""
        now = datetime.now()

        outline = SequenceOutline(
            genre="mystery",
            story_id="story_014",
            name="Late Sequence",
            description="A late sequence in the narrative",
            created_at=now,
            modified_at=now,
            parent_id=None,
            sequence_number=100,
            objective="Final sequence",
            chapter_range=(400, 500),
        )

        assert outline.sequence_number == 100

    def test_sequence_outline_with_large_chapter_range(self):
        """Test with a large chapter range."""
        now = datetime.now()

        outline = SequenceOutline(
            genre="mystery",
            story_id="story_015",
            name="Epic Sequence",
            description="Epic sequence spanning many chapters",
            created_at=now,
            modified_at=now,
            parent_id=None,
            sequence_number=1,
            objective="Epic objective",
            chapter_range=(1, 1000),
        )

        assert outline.chapter_range == (1, 1000)

    def test_sequence_outline_with_long_objective(self):
        """Test with a long objective description."""
        now = datetime.now()
        long_objective = (
            "Introduce all major characters, establish the setting, "
            "present the inciting incident, and set up the central conflict "
            "that will drive the narrative forward"
        )

        outline = SequenceOutline(
            genre="mystery",
            story_id="story_016",
            name="Sequence",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            sequence_number=1,
            objective=long_objective,
            chapter_range=(1, 5),
        )

        assert outline.objective == long_objective

    def test_sequence_outline_with_empty_objective(self):
        """Test that empty objective is accepted (no content validation)."""
        now = datetime.now()

        outline = SequenceOutline(
            genre="mystery",
            story_id="story_017",
            name="Sequence",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            sequence_number=1,
            objective="",
            chapter_range=(1, 5),
        )

        assert outline.objective == ""
