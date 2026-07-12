"""Tests for BookOutline artifact."""

import pytest
from datetime import datetime
from auteur.narrative_blueprint.schema.book_outline import BookOutline


class TestBookOutlineCreation:
    """Test basic BookOutline creation and initialization."""

    def test_book_outline_creation_with_all_fields(self):
        """Test successful creation with all required fields."""
        now = datetime.now()
        phases = {
            1: "Setup",
            2: "Inciting Incident",
            3: "Rising Action 1",
            4: "Rising Action 2",
            5: "Midpoint",
            6: "Rising Action 3",
            7: "Climax Setup",
            8: "Climax",
            9: "Resolution",
        }

        outline = BookOutline(
            genre="mystery",
            story_id="story_001",
            name="Book Outline",
            description="A mystery book outline",
            created_at=now,
            modified_at=now,
            parent_id="series_001",
            title="The Mystery Case",
            chapter_estimate=24,
            structure="3-act",
            phases_summary=phases,
        )

        assert outline.genre == "mystery"
        assert outline.story_id == "story_001"
        assert outline.name == "Book Outline"
        assert outline.description == "A mystery book outline"
        assert outline.created_at == now
        assert outline.modified_at == now
        assert outline.parent_id == "series_001"
        assert outline.title == "The Mystery Case"
        assert outline.chapter_estimate == 24
        assert outline.structure == "3-act"
        assert outline.phases_summary == phases

    def test_book_outline_artifact_type(self):
        """Test that artifact_type() returns 'book_outline'."""
        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        outline = BookOutline(
            genre="netorare",
            story_id="story_002",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=10,
            structure="4-act",
            phases_summary=phases,
        )

        assert outline.artifact_type() == "book_outline"

    def test_book_outline_with_4_act_structure(self):
        """Test creation with 4-act structure."""
        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        outline = BookOutline(
            genre="gentlefemdom",
            story_id="story_003",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test Book",
            chapter_estimate=15,
            structure="4-act",
            phases_summary=phases,
        )

        assert outline.structure == "4-act"

    def test_book_outline_with_none_parent_id(self):
        """Test creation with None parent_id."""
        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        outline = BookOutline(
            genre="mystery",
            story_id="story_004",
            name="Standalone Book",
            description="A standalone book",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Standalone",
            chapter_estimate=20,
            structure="3-act",
            phases_summary=phases,
        )

        assert outline.parent_id is None


class TestBookOutlineValidation:
    """Test BookOutline validation logic."""

    def test_phases_summary_must_have_exactly_9_keys(self):
        """Test that phases_summary must have exactly 9 keys."""
        now = datetime.now()

        # Only 8 phases
        phases_8 = {i: f"Phase {i}" for i in range(1, 9)}

        with pytest.raises(ValueError, match="must have exactly 9 phases"):
            BookOutline(
                genre="mystery",
                story_id="story_005",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                title="Test",
                chapter_estimate=10,
                structure="3-act",
                phases_summary=phases_8,
            )

    def test_phases_summary_must_have_all_phases_1_to_9(self):
        """Test that phases_summary keys must be 1 through 9."""
        now = datetime.now()

        # Has 9 entries but not 1-9 (0-8 instead)
        phases_wrong = {i: f"Phase {i}" for i in range(0, 9)}

        with pytest.raises(ValueError, match="phases_summary must have keys 1 through 9"):
            BookOutline(
                genre="mystery",
                story_id="story_006",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                title="Test",
                chapter_estimate=10,
                structure="3-act",
                phases_summary=phases_wrong,
            )

    def test_phases_summary_with_missing_middle_phase(self):
        """Test that missing phase (e.g., phase 5) is rejected due to wrong count."""
        now = datetime.now()

        # Missing phase 5 - only 8 phases
        phases_missing = {i: f"Phase {i}" for i in range(1, 10) if i != 5}

        with pytest.raises(ValueError, match="phases_summary must have exactly 9 phases"):
            BookOutline(
                genre="mystery",
                story_id="story_007",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                title="Test",
                chapter_estimate=10,
                structure="3-act",
                phases_summary=phases_missing,
            )

    def test_chapter_estimate_must_be_positive(self):
        """Test that chapter_estimate must be > 0."""
        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        with pytest.raises(ValueError, match="chapter_estimate must be > 0"):
            BookOutline(
                genre="mystery",
                story_id="story_008",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                title="Test",
                chapter_estimate=0,
                structure="3-act",
                phases_summary=phases,
            )

    def test_chapter_estimate_negative_is_rejected(self):
        """Test that negative chapter_estimate is rejected."""
        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        with pytest.raises(ValueError, match="chapter_estimate must be > 0"):
            BookOutline(
                genre="mystery",
                story_id="story_009",
                name="Test",
                description="Test",
                created_at=now,
                modified_at=now,
                parent_id=None,
                title="Test",
                chapter_estimate=-5,
                structure="3-act",
                phases_summary=phases,
            )

    def test_chapter_estimate_one_is_valid(self):
        """Test that chapter_estimate of 1 is valid."""
        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        outline = BookOutline(
            genre="mystery",
            story_id="story_010",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test",
            chapter_estimate=1,
            structure="3-act",
            phases_summary=phases,
        )

        assert outline.chapter_estimate == 1


class TestBookOutlineGenreConsistency:
    """Test that BookOutline works identically across all genres."""

    @pytest.mark.parametrize("genre", ["mystery", "netorare", "gentlefemdom"])
    def test_book_outline_works_for_all_genres(self, genre):
        """Test that BookOutline class works for all 3 genres without special-casing."""
        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        outline = BookOutline(
            genre=genre,
            story_id=f"story_{genre}",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title=f"Book for {genre}",
            chapter_estimate=12,
            structure="3-act",
            phases_summary=phases,
        )

        assert outline.genre == genre
        assert outline.artifact_type() == "book_outline"
        assert outline.chapter_estimate == 12


class TestBookOutlineEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_book_outline_with_large_chapter_estimate(self):
        """Test with a very large chapter estimate."""
        now = datetime.now()
        phases = {i: f"Phase {i}" for i in range(1, 10)}

        outline = BookOutline(
            genre="mystery",
            story_id="story_011",
            name="Epic",
            description="Epic book",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Epic Book",
            chapter_estimate=500,
            structure="3-act",
            phases_summary=phases,
        )

        assert outline.chapter_estimate == 500

    def test_phases_summary_with_empty_strings(self):
        """Test that empty phase summaries are accepted (no content validation)."""
        now = datetime.now()
        phases = {i: "" for i in range(1, 10)}

        outline = BookOutline(
            genre="mystery",
            story_id="story_012",
            name="Test",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Test",
            chapter_estimate=10,
            structure="3-act",
            phases_summary=phases,
        )

        assert outline.phases_summary == phases

    def test_phases_summary_with_long_descriptions(self):
        """Test phases_summary with long descriptive text."""
        now = datetime.now()
        phases = {
            1: "Introduction of the protagonist in their ordinary world",
            2: "An unexpected event that disrupts the status quo",
            3: "Initial response and escalation of tensions",
            4: "Deepening complications and raising stakes",
            5: "The central turning point where everything changes",
            6: "Consequences unfold from the midpoint decision",
            7: "All forces converge toward the final confrontation",
            8: "The climactic sequence where conflicts resolve",
            9: "Resolution and new equilibrium established",
        }

        outline = BookOutline(
            genre="mystery",
            story_id="story_013",
            name="Detailed Outline",
            description="Book with detailed phase summaries",
            created_at=now,
            modified_at=now,
            parent_id=None,
            title="Detailed Book",
            chapter_estimate=50,
            structure="4-act",
            phases_summary=phases,
        )

        assert outline.phases_summary == phases
