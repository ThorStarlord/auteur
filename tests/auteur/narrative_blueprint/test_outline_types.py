"""Tests for core outline types and enums."""

import pytest
from datetime import datetime
from auteur.narrative_blueprint.schema.outline_types import (
    ArcType,
    PhaseRange,
    OutlineArtifact,
    ContainerArtifact,
    OverlayArtifact,
)


class TestArcType:
    """Test ArcType enum."""

    def test_arc_type_character(self):
        """Test CHARACTER arc type."""
        assert ArcType.CHARACTER.value == "character"

    def test_arc_type_story(self):
        """Test STORY arc type."""
        assert ArcType.STORY.value == "story"

    def test_arc_type_theme(self):
        """Test THEME arc type."""
        assert ArcType.THEME.value == "theme"


class TestPhaseRange:
    """Test PhaseRange dataclass."""

    def test_valid_phase_range(self):
        """Test creating a valid PhaseRange."""
        pr = PhaseRange(start=1, peak=5, end=9)
        assert pr.start == 1
        assert pr.peak == 5
        assert pr.end == 9

    def test_phase_range_includes_phase(self):
        """Test includes_phase method."""
        pr = PhaseRange(start=2, peak=5, end=8)
        assert pr.includes_phase(2)
        assert pr.includes_phase(5)
        assert pr.includes_phase(8)
        assert pr.includes_phase(4)
        assert not pr.includes_phase(1)
        assert not pr.includes_phase(9)

    def test_phase_range_validates_start_le_peak(self):
        """Test that start must be <= peak."""
        with pytest.raises(ValueError):
            PhaseRange(start=6, peak=5, end=9)

    def test_phase_range_validates_peak_le_end(self):
        """Test that peak must be <= end."""
        with pytest.raises(ValueError):
            PhaseRange(start=1, peak=9, end=5)

    def test_phase_range_validates_phases_in_range(self):
        """Test that all phases must be 1-9."""
        with pytest.raises(ValueError):
            PhaseRange(start=0, peak=5, end=9)

        with pytest.raises(ValueError):
            PhaseRange(start=1, peak=10, end=9)

        with pytest.raises(ValueError):
            PhaseRange(start=1, peak=5, end=10)


class TestOutlineArtifact:
    """Test OutlineArtifact abstract base class."""

    def test_outline_artifact_cannot_be_instantiated(self):
        """Test that abstract base class cannot be instantiated directly."""
        with pytest.raises(TypeError):
            OutlineArtifact(
                genre="mystery",
                story_id="story_001",
                name="Test",
                description="Test description",
                created_at=datetime.now(),
                modified_at=datetime.now(),
            )

    def test_outline_artifact_abstract_method(self):
        """Test that artifact_type is abstract."""
        # Verify that the abstract method exists
        assert hasattr(OutlineArtifact, "artifact_type")
        assert getattr(OutlineArtifact.artifact_type, "__isabstractmethod__", False)


class TestContainerArtifact:
    """Test ContainerArtifact class."""

    def test_container_artifact_cannot_be_instantiated(self):
        """Test that abstract ContainerArtifact cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ContainerArtifact(
                genre="mystery",
                story_id="story_001",
                name="Test Container",
                description="Test description",
                created_at=datetime.now(),
                modified_at=datetime.now(),
                parent_id=None,
            )

    def test_container_artifact_subclass_instantiation(self):
        """Test that a concrete subclass of ContainerArtifact can be instantiated."""

        class ConcreteContainer(ContainerArtifact):
            def artifact_type(self) -> str:
                return "container"

        now = datetime.now()
        container = ConcreteContainer(
            genre="mystery",
            story_id="story_001",
            name="Test Container",
            description="Test description",
            created_at=now,
            modified_at=now,
            parent_id="parent_001",
        )

        assert container.genre == "mystery"
        assert container.story_id == "story_001"
        assert container.name == "Test Container"
        assert container.description == "Test description"
        assert container.created_at == now
        assert container.modified_at == now
        assert container.parent_id == "parent_001"
        assert container.artifact_type() == "container"

    def test_container_artifact_with_no_parent(self):
        """Test ContainerArtifact subclass with parent_id=None."""

        class ConcreteContainer(ContainerArtifact):
            def artifact_type(self) -> str:
                return "container"

        container = ConcreteContainer(
            genre="netorare",
            story_id="story_002",
            name="Root Container",
            description="No parent",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            parent_id=None,
        )

        assert container.parent_id is None


class TestOverlayArtifact:
    """Test OverlayArtifact class."""

    def test_overlay_artifact_cannot_be_instantiated(self):
        """Test that abstract OverlayArtifact cannot be instantiated directly."""
        with pytest.raises(TypeError):
            OverlayArtifact(
                genre="gentlefemdom",
                story_id="story_003",
                name="Test Overlay",
                description="Test description",
                created_at=datetime.now(),
                modified_at=datetime.now(),
                arc_type=ArcType.CHARACTER,
                span_chapters=[1, 2, 3],
            )

    def test_overlay_artifact_subclass_instantiation(self):
        """Test that a concrete subclass of OverlayArtifact can be instantiated."""

        class ConcreteOverlay(OverlayArtifact):
            def artifact_type(self) -> str:
                return "overlay"

        now = datetime.now()
        overlay = ConcreteOverlay(
            genre="mystery",
            story_id="story_001",
            name="Character Arc",
            description="Main character arc",
            created_at=now,
            modified_at=now,
            arc_type=ArcType.CHARACTER,
            span_chapters=[1, 2, 3, 4, 5],
        )

        assert overlay.genre == "mystery"
        assert overlay.story_id == "story_001"
        assert overlay.name == "Character Arc"
        assert overlay.arc_type == ArcType.CHARACTER
        assert overlay.span_chapters == [1, 2, 3, 4, 5]
        assert overlay.artifact_type() == "overlay"

    def test_overlay_artifact_all_arc_types(self):
        """Test OverlayArtifact with all arc types."""

        class ConcreteOverlay(OverlayArtifact):
            def artifact_type(self) -> str:
                return "overlay"

        now = datetime.now()

        for arc_type in [ArcType.CHARACTER, ArcType.STORY, ArcType.THEME]:
            overlay = ConcreteOverlay(
                genre="netorare",
                story_id="story_001",
                name=f"{arc_type.value} arc",
                description=f"Test {arc_type.value} arc",
                created_at=now,
                modified_at=now,
                arc_type=arc_type,
                span_chapters=[1, 2],
            )
            assert overlay.arc_type == arc_type

    def test_overlay_artifact_empty_chapters(self):
        """Test OverlayArtifact with empty span_chapters."""

        class ConcreteOverlay(OverlayArtifact):
            def artifact_type(self) -> str:
                return "overlay"

        overlay = ConcreteOverlay(
            genre="gentlefemdom",
            story_id="story_001",
            name="Empty Overlay",
            description="No chapters",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            arc_type=ArcType.STORY,
            span_chapters=[],
        )

        assert overlay.span_chapters == []
