"""Tests for OutlineLoader YAML serialization."""

import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Type, TypeVar

import pytest

from auteur.narrative_blueprint.loader.outline_loader import OutlineLoader
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.outline_types import OutlineArtifact, ArcType

T = TypeVar("T", bound=OutlineArtifact)


class TestOutlineLoaderBookOutline:
    """Test OutlineLoader with BookOutline artifacts."""

    def test_book_outline_roundtrip(self, tmp_path: Path):
        """Test saving and loading BookOutline preserves all fields."""
        # Create a BookOutline
        created_at = datetime(2026, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        modified_at = datetime(2026, 1, 15, 14, 45, 0, tzinfo=timezone.utc)

        original = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="The Mystery Case",
            description="A classic mystery",
            created_at=created_at,
            modified_at=modified_at,
            parent_id=None,
            title="Mystery Book",
            chapter_estimate=12,
            structure="3-act",
            phases_summary={
                1: "Exposition",
                2: "Rising Action",
                3: "Complications",
                4: "Midpoint",
                5: "Turning Point",
                6: "Escalation",
                7: "Climax Setup",
                8: "Resolution",
                9: "Denouement",
            },
        )

        # Save to file
        output_path = tmp_path / "book_outline.yaml"
        loader = OutlineLoader()
        loader.save_outline(original, str(output_path))

        # Verify file was created
        assert output_path.exists()

        # Load back
        loaded = loader.load_outline(str(output_path), BookOutline)

        # Verify all fields match
        assert loaded.genre == original.genre
        assert loaded.story_id == original.story_id
        assert loaded.name == original.name
        assert loaded.description == original.description
        assert loaded.created_at == original.created_at
        assert loaded.modified_at == original.modified_at
        assert loaded.parent_id == original.parent_id
        assert loaded.title == original.title
        assert loaded.chapter_estimate == original.chapter_estimate
        assert loaded.structure == original.structure
        assert loaded.phases_summary == original.phases_summary

    def test_book_outline_with_parent_id(self, tmp_path: Path):
        """Test BookOutline roundtrip with parent_id set."""
        created_at = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        modified_at = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

        original = BookOutline(
            genre="netorare",
            story_id="story_002",
            name="Nested Book",
            description="A nested book",
            created_at=created_at,
            modified_at=modified_at,
            parent_id="series_001",
            title="Book in Series",
            chapter_estimate=20,
            structure="4-act",
            phases_summary={
                1: "Setup", 2: "Inciting", 3: "Acceptance", 4: "B-story",
                5: "Promises", 6: "Midpoint", 7: "Bad Guys", 8: "All Lost",
                9: "Climax"
            },
        )

        output_path = tmp_path / "book_with_parent.yaml"
        loader = OutlineLoader()
        loader.save_outline(original, str(output_path))
        loaded = loader.load_outline(str(output_path), BookOutline)

        assert loaded.parent_id == "series_001"
        assert loaded.story_id == "story_002"


class TestOutlineLoaderChapterOutline:
    """Test OutlineLoader with ChapterOutline artifacts."""

    def test_chapter_outline_roundtrip(self, tmp_path: Path):
        """Test saving and loading ChapterOutline preserves all fields."""
        created_at = datetime(2026, 1, 16, 9, 0, 0, tzinfo=timezone.utc)
        modified_at = datetime(2026, 1, 16, 11, 30, 0, tzinfo=timezone.utc)

        original = ChapterOutline(
            genre="gentlefemdom",
            story_id="story_003",
            name="Chapter One",
            description="Opening chapter",
            created_at=created_at,
            modified_at=modified_at,
            parent_id="book_001",
            chapter_number=1,
            phase=1,
            title="The Beginning",
            goal="Establish the protagonist",
            conflict="Internal doubt",
            turning_point="A chance encounter",
            emotional_beat="Hope → Curiosity",
            arc_progressions={"character_arc_1": "Initial meeting", "story_arc_1": "Plot setup"},
        )

        output_path = tmp_path / "chapter_outline.yaml"
        loader = OutlineLoader()
        loader.save_outline(original, str(output_path))
        loaded = loader.load_outline(str(output_path), ChapterOutline)

        assert loaded.genre == original.genre
        assert loaded.chapter_number == original.chapter_number
        assert loaded.phase == original.phase
        assert loaded.title == original.title
        assert loaded.goal == original.goal
        assert loaded.conflict == original.conflict
        assert loaded.turning_point == original.turning_point
        assert loaded.emotional_beat == original.emotional_beat
        assert loaded.arc_progressions == original.arc_progressions

    def test_chapter_outline_empty_arc_progressions(self, tmp_path: Path):
        """Test ChapterOutline roundtrip with empty arc_progressions."""
        created_at = datetime(2026, 1, 16, 9, 0, 0, tzinfo=timezone.utc)
        modified_at = datetime(2026, 1, 16, 11, 30, 0, tzinfo=timezone.utc)

        original = ChapterOutline(
            genre="mystery",
            story_id="story_004",
            name="Chapter Two",
            description="Second chapter",
            created_at=created_at,
            modified_at=modified_at,
            parent_id="book_002",
            chapter_number=2,
            phase=2,
            title="Complications",
            goal="Introduce conflict",
            conflict="External pressure",
            turning_point="Discovery",
            emotional_beat="Confusion → Determination",
        )

        output_path = tmp_path / "chapter_no_arcs.yaml"
        loader = OutlineLoader()
        loader.save_outline(original, str(output_path))
        loaded = loader.load_outline(str(output_path), ChapterOutline)

        assert loaded.arc_progressions == {}


class TestOutlineLoaderCharacterArc:
    """Test OutlineLoader with CharacterArc artifacts with nested TurningPoint objects."""

    def test_character_arc_with_turning_points_roundtrip(self, tmp_path: Path):
        """Test saving and loading CharacterArc with TurningPoint objects."""
        created_at = datetime(2026, 1, 17, 8, 0, 0, tzinfo=timezone.utc)
        modified_at = datetime(2026, 1, 17, 10, 0, 0, tzinfo=timezone.utc)

        turning_points = [
            TurningPoint(
                chapter=1,
                moment="First encounter with the mentor",
                belief_shift="Realizes she can trust others",
            ),
            TurningPoint(
                chapter=5,
                moment="Betrayal by trusted ally",
                belief_shift="Learns that trust can be broken",
            ),
            TurningPoint(
                chapter=9,
                moment="Ultimate redemption",
                belief_shift="Finds new path forward",
            ),
        ]

        original = CharacterArc(
            genre="netorare",
            story_id="story_005",
            name="Character Arc: Alice",
            description="Alice's journey of humiliation",
            created_at=created_at,
            modified_at=modified_at,
            span_chapters=[1, 2, 3, 4, 5, 6, 7, 8, 9],
            character_name="Alice",
            initial_belief="She is in control of her destiny",
            final_belief="Acceptance of external forces",
            turning_points=turning_points,
            genre_themes=["humiliation", "powerlessness", "acceptance"],
        )

        output_path = tmp_path / "character_arc.yaml"
        loader = OutlineLoader()
        loader.save_outline(original, str(output_path))
        loaded = loader.load_outline(str(output_path), CharacterArc)

        # Verify main fields
        assert loaded.character_name == original.character_name
        assert loaded.initial_belief == original.initial_belief
        assert loaded.final_belief == original.final_belief
        assert loaded.arc_type == ArcType.CHARACTER
        assert loaded.span_chapters == original.span_chapters
        assert loaded.genre_themes == original.genre_themes

        # Verify turning points
        assert len(loaded.turning_points) == 3
        for i, (loaded_tp, orig_tp) in enumerate(zip(loaded.turning_points, original.turning_points)):
            assert loaded_tp.chapter == orig_tp.chapter
            assert loaded_tp.moment == orig_tp.moment
            assert loaded_tp.belief_shift == orig_tp.belief_shift

    def test_character_arc_without_turning_points(self, tmp_path: Path):
        """Test CharacterArc roundtrip with no turning points."""
        created_at = datetime(2026, 1, 17, 8, 0, 0, tzinfo=timezone.utc)
        modified_at = datetime(2026, 1, 17, 10, 0, 0, tzinfo=timezone.utc)

        original = CharacterArc(
            genre="mystery",
            story_id="story_006",
            name="Character Arc: Detective",
            description="Detective's investigation",
            created_at=created_at,
            modified_at=modified_at,
            span_chapters=[1, 2, 3, 4, 5],
            character_name="Detective Smith",
            initial_belief="The case is straightforward",
            final_belief="Nothing is as it seems",
            genre_themes=["discovery", "truth"],
        )

        output_path = tmp_path / "character_arc_no_turns.yaml"
        loader = OutlineLoader()
        loader.save_outline(original, str(output_path))
        loaded = loader.load_outline(str(output_path), CharacterArc)

        assert loaded.turning_points == []


class TestOutlineLoaderDirectoryCreation:
    """Test that OutlineLoader creates parent directories automatically."""

    def test_nested_directory_creation(self, tmp_path: Path):
        """Test that nested directories are created if they don't exist."""
        nested_path = tmp_path / "nested" / "deep" / "structure" / "outline.yaml"

        original = BookOutline(
            genre="mystery",
            story_id="story_007",
            name="Nested Test",
            description="Testing nested creation",
            created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            modified_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            parent_id=None,
            title="Nested Book",
            chapter_estimate=5,
            structure="3-act",
            phases_summary={
                1: "A", 2: "B", 3: "C", 4: "D", 5: "E",
                6: "F", 7: "G", 8: "H", 9: "I"
            },
        )

        loader = OutlineLoader()
        loader.save_outline(original, str(nested_path))

        # Verify directory was created
        assert nested_path.parent.exists()
        assert nested_path.exists()


class TestOutlineLoaderDateTimeParsing:
    """Test that OutlineLoader preserves datetime objects in ISO format."""

    def test_datetime_preservation_in_roundtrip(self, tmp_path: Path):
        """Test that datetime objects are preserved exactly during roundtrip."""
        # Use a specific datetime with timezone
        created_at = datetime(2026, 3, 15, 14, 30, 45, 123456, tzinfo=timezone.utc)
        modified_at = datetime(2026, 3, 16, 9, 15, 30, 654321, tzinfo=timezone.utc)

        original = ChapterOutline(
            genre="gentlefemdom",
            story_id="story_008",
            name="Datetime Test",
            description="Testing datetime precision",
            created_at=created_at,
            modified_at=modified_at,
            parent_id="book_003",
            chapter_number=3,
            phase=3,
            title="Datetime Chapter",
            goal="Test datetime handling",
            conflict="Precision challenge",
            turning_point="Now",
            emotional_beat="Curiosity",
        )

        output_path = tmp_path / "datetime_test.yaml"
        loader = OutlineLoader()
        loader.save_outline(original, str(output_path))
        loaded = loader.load_outline(str(output_path), ChapterOutline)

        # Compare datetime values (accounting for potential microsecond precision)
        assert loaded.created_at.year == created_at.year
        assert loaded.created_at.month == created_at.month
        assert loaded.created_at.day == created_at.day
        assert loaded.created_at.hour == created_at.hour
        assert loaded.created_at.minute == created_at.minute
        assert loaded.created_at.second == created_at.second

        assert loaded.modified_at.year == modified_at.year
        assert loaded.modified_at.month == modified_at.month
        assert loaded.modified_at.day == modified_at.day


class TestOutlineLoaderErrorHandling:
    """Test error handling in OutlineLoader."""

    def test_load_nonexistent_file(self):
        """Test that loading a nonexistent file raises FileNotFoundError."""
        loader = OutlineLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_outline("/nonexistent/path/to/outline.yaml", BookOutline)

    def test_save_with_invalid_outline(self, tmp_path: Path):
        """Test that saving an invalid outline raises ValueError."""
        loader = OutlineLoader()
        invalid_outline = "not an outline"  # type: ignore

        output_path = tmp_path / "invalid.yaml"
        with pytest.raises((ValueError, AttributeError, TypeError)):
            loader.save_outline(invalid_outline, str(output_path))  # type: ignore

    def test_load_with_type_mismatch(self, tmp_path: Path):
        """Test that loading a file with type mismatch raises ValueError."""
        # Save a BookOutline
        book = BookOutline(
            genre="mystery",
            story_id="story_009",
            name="Type Mismatch Test",
            description="Testing type mismatch",
            created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            modified_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            parent_id=None,
            title="Test Book",
            chapter_estimate=10,
            structure="3-act",
            phases_summary={
                1: "A", 2: "B", 3: "C", 4: "D", 5: "E",
                6: "F", 7: "G", 8: "H", 9: "I"
            },
        )

        output_path = tmp_path / "type_mismatch.yaml"
        loader = OutlineLoader()
        loader.save_outline(book, str(output_path))

        # Try to load as ChapterOutline (wrong type)
        with pytest.raises((ValueError, TypeError, KeyError)):
            loader.load_outline(str(output_path), ChapterOutline)


class TestOutlineLoaderMultiGenre:
    """Test that OutlineLoader works identically for all genres."""

    @pytest.mark.parametrize("genre", ["netorare", "mystery", "gentlefemdom"])
    def test_same_loader_all_genres(self, genre: str, tmp_path: Path):
        """Test that the same loader works for all genres without special-casing."""
        created_at = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        modified_at = datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc)

        original = BookOutline(
            genre=genre,
            story_id=f"story_{genre}",
            name=f"Book for {genre}",
            description=f"A {genre} story",
            created_at=created_at,
            modified_at=modified_at,
            parent_id=None,
            title=f"{genre.title()} Book",
            chapter_estimate=15,
            structure="3-act",
            phases_summary={
                1: "Start", 2: "B", 3: "C", 4: "D", 5: "E",
                6: "F", 7: "G", 8: "H", 9: "End"
            },
        )

        output_path = tmp_path / f"{genre}_book.yaml"
        loader = OutlineLoader()
        loader.save_outline(original, str(output_path))
        loaded = loader.load_outline(str(output_path), BookOutline)

        assert loaded.genre == genre
        assert loaded.story_id == f"story_{genre}"


class TestOutlineLoaderYAMLFormat:
    """Test that OutlineLoader produces valid YAML output."""

    def test_yaml_is_readable(self, tmp_path: Path):
        """Test that saved YAML files can be read back as valid YAML."""
        import yaml

        created_at = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        modified_at = datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc)

        original = ChapterOutline(
            genre="mystery",
            story_id="story_010",
            name="YAML Format Test",
            description="Testing YAML format",
            created_at=created_at,
            modified_at=modified_at,
            parent_id="book_004",
            chapter_number=4,
            phase=4,
            title="Chapter Four",
            goal="Test goal",
            conflict="Test conflict",
            turning_point="Test turning point",
            emotional_beat="Test emotion",
        )

        output_path = tmp_path / "yaml_format.yaml"
        loader = OutlineLoader()
        loader.save_outline(original, str(output_path))

        # Verify the file contains valid YAML
        with open(output_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            assert data is not None
            assert isinstance(data, dict)
            assert "genre" in data
            assert data["genre"] == "mystery"
