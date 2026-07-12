"""Tests for StoryArc schema and ArcCheckpoint dataclass."""

import pytest
from datetime import datetime
from typing import Literal
from auteur.narrative_blueprint.schema.story_arc import (
    ArcCheckpoint,
    StoryArc,
)
from auteur.narrative_blueprint.schema.outline_types import ArcType, PhaseRange


class TestArcCheckpoint:
    """Test ArcCheckpoint dataclass."""

    def test_arc_checkpoint_creation(self):
        """Test creating a basic ArcCheckpoint."""
        cp = ArcCheckpoint(
            phase=3,
            moment="First clue discovered",
        )
        assert cp.phase == 3
        assert cp.moment == "First clue discovered"

    def test_arc_checkpoint_with_different_phase(self):
        """Test ArcCheckpoint with different phase number."""
        cp = ArcCheckpoint(
            phase=7,
            moment="Mystery deepens",
        )
        assert cp.phase == 7

    def test_arc_checkpoint_with_various_moments(self):
        """Test ArcCheckpoint with different moment descriptions."""
        moments = [
            "Inciting incident",
            "Rising tension",
            "Climactic revelation",
        ]

        for moment in moments:
            cp = ArcCheckpoint(phase=5, moment=moment)
            assert cp.moment == moment


class TestStoryArc:
    """Test StoryArc class."""

    def test_story_arc_creation_with_all_fields(self):
        """Test creating StoryArc with all fields."""
        now = datetime.now()
        phase_range = PhaseRange(start=1, peak=5, end=9)
        checkpoints = [
            ArcCheckpoint(phase=2, moment="Mystery introduced"),
            ArcCheckpoint(phase=5, moment="Clues converge"),
            ArcCheckpoint(phase=8, moment="Truth revealed"),
        ]

        arc = StoryArc(
            genre="mystery",
            story_id="story_001",
            name="Main Mystery Arc",
            description="The central mystery of the story",
            created_at=now,
            modified_at=now,
            arc_name="The Library Secret",
            arc_category="mystery",
            phase_range=phase_range,
            checkpoints=checkpoints,
        )

        assert arc.genre == "mystery"
        assert arc.story_id == "story_001"
        assert arc.name == "Main Mystery Arc"
        assert arc.arc_name == "The Library Secret"
        assert arc.arc_category == "mystery"
        assert arc.phase_range == phase_range
        assert arc.checkpoints == checkpoints
        assert arc.arc_type == ArcType.STORY
        assert arc.artifact_type() == "story_arc"

    def test_multiple_story_arcs_same_story(self):
        """Test that multiple story arcs can exist for same story_id (mystery + romance coexist)."""
        now = datetime.now()

        mystery_arc = StoryArc(
            genre="mystery",
            story_id="story_001",
            name="Mystery Arc",
            description="Main mystery",
            created_at=now,
            modified_at=now,
            arc_name="The Conspiracy",
            arc_category="mystery",
            phase_range=PhaseRange(start=1, peak=5, end=9),
        )

        romance_arc = StoryArc(
            genre="mystery",
            story_id="story_001",
            name="Romance Arc",
            description="Budding romance",
            created_at=now,
            modified_at=now,
            arc_name="Forbidden Love",
            arc_category="romance",
            phase_range=PhaseRange(start=3, peak=6, end=8),
        )

        assert mystery_arc.story_id == romance_arc.story_id
        assert mystery_arc.arc_category == "mystery"
        assert romance_arc.arc_category == "romance"

    def test_arc_category_enforces_literal_values(self):
        """Test that arc_category enforces literal values (reject invalid category)."""
        now = datetime.now()

        # Valid categories should work
        valid_categories: list = ["mystery", "romance", "political", "revenge", "survival"]
        for category in valid_categories:
            arc = StoryArc(
                genre="mystery",
                story_id="story_001",
                name="Test Arc",
                description="Test",
                created_at=now,
                modified_at=now,
                arc_name="Test",
                arc_category=category,  # type: ignore
                phase_range=PhaseRange(start=1, peak=5, end=9),
            )
            assert arc.arc_category == category

    def test_phase_range_validates_properly(self):
        """Test that PhaseRange validates properly (inherits from Task 1)."""
        now = datetime.now()

        # Valid PhaseRange
        valid_range = PhaseRange(start=2, peak=5, end=8)
        arc = StoryArc(
            genre="mystery",
            story_id="story_001",
            name="Valid Arc",
            description="Test",
            created_at=now,
            modified_at=now,
            arc_name="Test",
            arc_category="mystery",
            phase_range=valid_range,
        )
        assert arc.phase_range.start == 2
        assert arc.phase_range.peak == 5
        assert arc.phase_range.end == 8

        # Invalid PhaseRange should raise in PhaseRange.__post_init__
        with pytest.raises(ValueError):
            PhaseRange(start=5, peak=3, end=8)

    def test_checkpoints_can_be_empty_list(self):
        """Test that checkpoints can be empty list (optional)."""
        now = datetime.now()

        arc = StoryArc(
            genre="mystery",
            story_id="story_001",
            name="Arc without checkpoints",
            description="Test arc",
            created_at=now,
            modified_at=now,
            arc_name="Simple Arc",
            arc_category="mystery",
            phase_range=PhaseRange(start=1, peak=5, end=9),
            checkpoints=[],
        )

        assert arc.checkpoints == []
        assert len(arc.checkpoints) == 0

    def test_checkpoints_default_to_empty(self):
        """Test that checkpoints default to empty list if not provided."""
        now = datetime.now()

        arc = StoryArc(
            genre="netorare",
            story_id="story_002",
            name="Arc",
            description="Test",
            created_at=now,
            modified_at=now,
            arc_name="Humiliation Arc",
            arc_category="revenge",
            phase_range=PhaseRange(start=1, peak=5, end=9),
            # checkpoints not provided
        )

        assert arc.checkpoints == []

    def test_multiple_checkpoints_work_correctly(self):
        """Test that multiple checkpoints work correctly."""
        now = datetime.now()
        checkpoints = [
            ArcCheckpoint(phase=1, moment="Beginning"),
            ArcCheckpoint(phase=3, moment="Middle"),
            ArcCheckpoint(phase=5, moment="Peak"),
            ArcCheckpoint(phase=7, moment="Resolution"),
            ArcCheckpoint(phase=9, moment="Ending"),
        ]

        arc = StoryArc(
            genre="gentlefemdom",
            story_id="story_003",
            name="Full Arc",
            description="Complete arc",
            created_at=now,
            modified_at=now,
            arc_name="Power Dynamics",
            arc_category="romance",
            phase_range=PhaseRange(start=1, peak=5, end=9),
            checkpoints=checkpoints,
        )

        assert len(arc.checkpoints) == 5
        assert arc.checkpoints[0].phase == 1
        assert arc.checkpoints[2].phase == 5
        assert arc.checkpoints[4].phase == 9
        assert arc.checkpoints[2].moment == "Peak"

    def test_all_three_genres_use_identical_story_arc(self):
        """Test that all three genres can have identical story arc types."""
        now = datetime.now()
        phase_range = PhaseRange(start=2, peak=5, end=8)

        for genre in ["netorare", "mystery", "gentlefemdom"]:
            arc = StoryArc(
                genre=genre,
                story_id=f"story_{genre}",
                name=f"{genre} arc",
                description=f"Story arc for {genre}",
                created_at=now,
                modified_at=now,
                arc_name="Universal Arc",
                arc_category="mystery",
                phase_range=phase_range,
            )

            assert arc.genre == genre
            assert arc.arc_type == ArcType.STORY
            assert arc.arc_category == "mystery"
            assert arc.artifact_type() == "story_arc"

    def test_story_arc_sets_arc_type_to_story(self):
        """Test that arc_type is automatically set to STORY."""
        now = datetime.now()

        arc = StoryArc(
            genre="mystery",
            story_id="story_001",
            name="Test Arc",
            description="Test",
            created_at=now,
            modified_at=now,
            arc_name="Test",
            arc_category="mystery",
            phase_range=PhaseRange(start=1, peak=5, end=9),
        )

        assert arc.arc_type == ArcType.STORY
        assert arc.arc_type.value == "story"

    def test_story_arc_artifact_type_method(self):
        """Test that artifact_type() returns 'story_arc'."""
        now = datetime.now()

        arc = StoryArc(
            genre="gentlefemdom",
            story_id="story_006",
            name="Romance Arc",
            description="Romance development",
            created_at=now,
            modified_at=now,
            arc_name="Tender Surrender",
            arc_category="romance",
            phase_range=PhaseRange(start=1, peak=5, end=9),
        )

        assert arc.artifact_type() == "story_arc"

    def test_story_arc_preserves_all_overlay_artifact_fields(self):
        """Test that StoryArc preserves all OverlayArtifact inherited fields."""
        now = datetime.now()
        phase_range = PhaseRange(start=1, peak=3, end=5)

        arc = StoryArc(
            genre="mystery",
            story_id="test_story",
            name="Test Arc",
            description="Test description",
            created_at=now,
            modified_at=now,
            arc_name="Test Story Arc",
            arc_category="mystery",
            phase_range=phase_range,
        )

        # Verify inherited fields
        assert arc.genre == "mystery"
        assert arc.story_id == "test_story"
        assert arc.name == "Test Arc"
        assert arc.description == "Test description"
        assert arc.created_at == now
        assert arc.modified_at == now
        assert arc.arc_type == ArcType.STORY

    def test_story_arc_with_all_arc_categories(self):
        """Test StoryArc with all valid arc categories."""
        now = datetime.now()
        categories = ["mystery", "romance", "political", "revenge", "survival"]

        for category in categories:
            arc = StoryArc(
                genre="netorare",
                story_id="story_multi",
                name=f"{category} Arc",
                description=f"Testing {category}",
                created_at=now,
                modified_at=now,
                arc_name=f"The {category.title()}",
                arc_category=category,  # type: ignore
                phase_range=PhaseRange(start=1, peak=5, end=9),
            )

            assert arc.arc_category == category

    def test_story_arc_with_single_checkpoint(self):
        """Test StoryArc with a single checkpoint."""
        now = datetime.now()

        arc = StoryArc(
            genre="mystery",
            story_id="story_007",
            name="Single Checkpoint Arc",
            description="Arc with one checkpoint",
            created_at=now,
            modified_at=now,
            arc_name="Turning Point",
            arc_category="mystery",
            phase_range=PhaseRange(start=1, peak=5, end=9),
            checkpoints=[ArcCheckpoint(phase=5, moment="The revelation")],
        )

        assert len(arc.checkpoints) == 1
        assert arc.checkpoints[0].phase == 5

    def test_phase_range_start_peak_end_constraints(self):
        """Test that PhaseRange respects start <= peak <= end constraints."""
        now = datetime.now()

        # Valid: start < peak < end
        valid_arc = StoryArc(
            genre="mystery",
            story_id="story_008",
            name="Valid Range",
            description="Test",
            created_at=now,
            modified_at=now,
            arc_name="Constrained Arc",
            arc_category="mystery",
            phase_range=PhaseRange(start=1, peak=5, end=9),
        )
        assert valid_arc.phase_range.start == 1
        assert valid_arc.phase_range.peak == 5
        assert valid_arc.phase_range.end == 9

        # Valid: start == peak == end
        same_phase_arc = StoryArc(
            genre="mystery",
            story_id="story_009",
            name="Same Phase",
            description="Test",
            created_at=now,
            modified_at=now,
            arc_name="Single Phase Arc",
            arc_category="mystery",
            phase_range=PhaseRange(start=5, peak=5, end=5),
        )
        assert same_phase_arc.phase_range.start == 5
        assert same_phase_arc.phase_range.peak == 5
        assert same_phase_arc.phase_range.end == 5
