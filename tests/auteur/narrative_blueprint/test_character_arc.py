"""Tests for CharacterArc schema and TurningPoint dataclass."""

import pytest
from datetime import datetime
from auteur.narrative_blueprint.schema.character_arc import (
    TurningPoint,
    CharacterArc,
)
from auteur.narrative_blueprint.schema.outline_types import ArcType


class TestTurningPoint:
    """Test TurningPoint dataclass."""

    def test_turning_point_creation(self):
        """Test creating a basic TurningPoint."""
        tp = TurningPoint(
            chapter=3,
            moment="Character realizes the truth",
            belief_shift="Changed from believing in love to fearing rejection",
        )
        assert tp.chapter == 3
        assert tp.moment == "Character realizes the truth"
        assert tp.belief_shift == "Changed from believing in love to fearing rejection"

    def test_turning_point_with_different_chapter(self):
        """Test TurningPoint with different chapter number."""
        tp = TurningPoint(
            chapter=7,
            moment="Major revelation",
            belief_shift="Understanding shifts",
        )
        assert tp.chapter == 7


class TestCharacterArc:
    """Test CharacterArc class."""

    def test_character_arc_creation_with_all_fields(self):
        """Test creating CharacterArc with all fields."""
        now = datetime.now()
        turning_points = [
            TurningPoint(
                chapter=2,
                moment="First doubt",
                belief_shift="Questions initial assumptions",
            ),
            TurningPoint(
                chapter=5,
                moment="Crisis point",
                belief_shift="Fundamentally changes perspective",
            ),
        ]

        arc = CharacterArc(
            genre="mystery",
            story_id="story_001",
            name="Detective Arc",
            description="Growth of main detective",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2, 3, 4, 5],
            character_name="Detective Jane",
            initial_belief="The case is simple",
            final_belief="The case involves corruption at all levels",
            turning_points=turning_points,
            genre_themes=["investigation", "trust", "deception"],
        )

        assert arc.genre == "mystery"
        assert arc.story_id == "story_001"
        assert arc.name == "Detective Arc"
        assert arc.character_name == "Detective Jane"
        assert arc.initial_belief == "The case is simple"
        assert arc.final_belief == "The case involves corruption at all levels"
        assert arc.turning_points == turning_points
        assert arc.genre_themes == ["investigation", "trust", "deception"]
        assert arc.arc_type == ArcType.CHARACTER
        assert arc.artifact_type() == "character_arc"

    def test_character_arc_requires_non_empty_genre_themes(self):
        """Test that genre_themes must not be empty."""
        now = datetime.now()

        with pytest.raises(ValueError, match="genre_themes must not be empty"):
            CharacterArc(
                genre="netorare",
                story_id="story_002",
                name="Character Arc",
                description="Test arc",
                created_at=now,
                modified_at=now,
                span_chapters=[1, 2, 3],
                character_name="Character",
                initial_belief="Initial",
                final_belief="Final",
                turning_points=[],
                genre_themes=[],  # Empty - should fail
            )

    def test_character_arc_with_single_genre_theme(self):
        """Test CharacterArc with single genre theme."""
        now = datetime.now()

        arc = CharacterArc(
            genre="gentlefemdom",
            story_id="story_003",
            name="Submissive Arc",
            description="Character journey",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2],
            character_name="Alex",
            initial_belief="Power is about control",
            final_belief="Power is about connection",
            turning_points=[],
            genre_themes=["surrender"],
        )

        assert arc.genre_themes == ["surrender"]
        assert arc.arc_type == ArcType.CHARACTER

    def test_character_arc_with_empty_turning_points(self):
        """Test CharacterArc with empty turning points list."""
        now = datetime.now()

        arc = CharacterArc(
            genre="mystery",
            story_id="story_004",
            name="Simple Arc",
            description="Character development",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2, 3],
            character_name="Supporting Character",
            initial_belief="Belief A",
            final_belief="Belief B",
            turning_points=[],  # Empty turning points is allowed
            genre_themes=["clarity", "doubt"],
        )

        assert arc.turning_points == []
        assert len(arc.turning_points) == 0

    def test_character_arc_sets_arc_type_to_character(self):
        """Test that arc_type is automatically set to CHARACTER."""
        now = datetime.now()

        arc = CharacterArc(
            genre="netorare",
            story_id="story_005",
            name="Protagonist Arc",
            description="Main character",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2, 3, 4, 5, 6],
            character_name="Protagonist",
            initial_belief="I am in control",
            final_belief="I am helpless",
            turning_points=[],
            genre_themes=["humiliation", "helplessness"],
        )

        # Verify arc_type is set to CHARACTER
        assert arc.arc_type == ArcType.CHARACTER
        assert arc.arc_type.value == "character"

    def test_character_arc_artifact_type_method(self):
        """Test that artifact_type() returns 'character_arc'."""
        now = datetime.now()

        arc = CharacterArc(
            genre="gentlefemdom",
            story_id="story_006",
            name="Dominance Arc",
            description="Power dynamics",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2],
            character_name="Dominant",
            initial_belief="Power comes from command",
            final_belief="Power comes from understanding",
            turning_points=[],
            genre_themes=["authority", "respect"],
        )

        assert arc.artifact_type() == "character_arc"

    def test_character_arc_with_all_three_genres(self):
        """Test CharacterArc works with all three genres."""
        now = datetime.now()

        genres_and_themes = [
            ("netorare", ["humiliation", "betrayal"]),
            ("mystery", ["deception", "truth"]),
            ("gentlefemdom", ["authority", "surrender"]),
        ]

        for genre, themes in genres_and_themes:
            arc = CharacterArc(
                genre=genre,
                story_id=f"story_{genre}",
                name=f"{genre} arc",
                description=f"Character arc for {genre}",
                created_at=now,
                modified_at=now,
                span_chapters=[1, 2, 3],
                character_name="Character",
                initial_belief="Initial state",
                final_belief="Final state",
                turning_points=[],
                genre_themes=themes,
            )

            assert arc.genre == genre
            assert arc.genre_themes == themes
            assert arc.arc_type == ArcType.CHARACTER

    def test_character_arc_preserves_all_overlay_artifact_fields(self):
        """Test that CharacterArc preserves all OverlayArtifact inherited fields."""
        now = datetime.now()
        span = [1, 3, 5, 7, 9]

        arc = CharacterArc(
            genre="mystery",
            story_id="test_story",
            name="Test Arc",
            description="Test description",
            created_at=now,
            modified_at=now,
            span_chapters=span,
            character_name="Test Character",
            initial_belief="Initial",
            final_belief="Final",
            turning_points=[],
            genre_themes=["theme1", "theme2"],
        )

        # Verify inherited fields
        assert arc.genre == "mystery"
        assert arc.story_id == "test_story"
        assert arc.name == "Test Arc"
        assert arc.description == "Test description"
        assert arc.created_at == now
        assert arc.modified_at == now
        assert arc.span_chapters == span

    def test_character_arc_with_multiple_turning_points(self):
        """Test CharacterArc with multiple TurningPoint objects."""
        now = datetime.now()
        turning_points = [
            TurningPoint(chapter=1, moment="Start", belief_shift="Initial doubt"),
            TurningPoint(chapter=3, moment="Middle", belief_shift="Growing certainty"),
            TurningPoint(chapter=5, moment="Peak", belief_shift="Transformation"),
            TurningPoint(chapter=7, moment="End", belief_shift="New equilibrium"),
        ]

        arc = CharacterArc(
            genre="gentlefemdom",
            story_id="story_journey",
            name="Full Journey",
            description="Complete character transformation",
            created_at=now,
            modified_at=now,
            span_chapters=[1, 2, 3, 4, 5, 6, 7],
            character_name="Traveler",
            initial_belief="Power is external",
            final_belief="Power is internal",
            turning_points=turning_points,
            genre_themes=["power", "surrender", "discovery"],
        )

        assert len(arc.turning_points) == 4
        assert arc.turning_points[0].chapter == 1
        assert arc.turning_points[3].chapter == 7
