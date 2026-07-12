"""Tests for SeriesOutline artifact."""

import pytest
from datetime import datetime
from auteur.narrative_blueprint.schema.series_outline import SeriesOutline


class TestSeriesOutlineCreation:
    """Test basic SeriesOutline creation and initialization."""

    def test_series_outline_creation_with_all_fields(self):
        """Test successful creation with all required fields."""
        now = datetime.now()
        book_ids = ["book_001", "book_002", "book_003"]
        character_evolution = {
            "Michael": "from control → acceptance",
            "Sarah": "from innocence → awareness",
        }
        thematic_progression = [
            "Book 1: Setup - the status quo",
            "Book 2: Escalation - pressure increases",
            "Book 3: Resolution - new equilibrium",
        ]

        outline = SeriesOutline(
            genre="mystery",
            story_id="series_story_001",
            name="Mystery Series",
            description="A three-book mystery series",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="Detective Chronicles",
            book_ids=book_ids,
            long_term_character_evolution=character_evolution,
            thematic_progression=thematic_progression,
        )

        assert outline.genre == "mystery"
        assert outline.story_id == "series_story_001"
        assert outline.name == "Mystery Series"
        assert outline.description == "A three-book mystery series"
        assert outline.created_at == now
        assert outline.modified_at == now
        assert outline.parent_id is None
        assert outline.series_name == "Detective Chronicles"
        assert outline.book_ids == book_ids
        assert outline.long_term_character_evolution == character_evolution
        assert outline.thematic_progression == thematic_progression

    def test_series_outline_artifact_type(self):
        """Test that artifact_type() returns 'series_outline'."""
        now = datetime.now()

        outline = SeriesOutline(
            genre="netorare",
            story_id="series_story_002",
            name="Series",
            description="Test series",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="Test Series",
            book_ids=[],
            long_term_character_evolution={},
            thematic_progression=[],
        )

        assert outline.artifact_type() == "series_outline"

    def test_series_outline_with_empty_book_ids(self):
        """Test creation with empty book_ids list."""
        now = datetime.now()

        outline = SeriesOutline(
            genre="gentlefemdom",
            story_id="series_story_003",
            name="Series",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="Incomplete Series",
            book_ids=[],
            long_term_character_evolution={},
            thematic_progression=[],
        )

        assert outline.book_ids == []

    def test_series_outline_with_empty_character_evolution(self):
        """Test creation with empty character evolution dict."""
        now = datetime.now()

        outline = SeriesOutline(
            genre="mystery",
            story_id="series_story_004",
            name="Series",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="No Characters",
            book_ids=["book_001"],
            long_term_character_evolution={},
            thematic_progression=[],
        )

        assert outline.long_term_character_evolution == {}

    def test_series_outline_with_empty_thematic_progression(self):
        """Test creation with empty thematic progression list."""
        now = datetime.now()

        outline = SeriesOutline(
            genre="netorare",
            story_id="series_story_005",
            name="Series",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="No Themes",
            book_ids=["book_001", "book_002"],
            long_term_character_evolution={},
            thematic_progression=[],
        )

        assert outline.thematic_progression == []

    def test_series_outline_with_multiple_books(self):
        """Test creation with multiple books tracked correctly."""
        now = datetime.now()
        books = [
            "book_001",
            "book_002",
            "book_003",
            "book_004",
            "book_005",
        ]

        outline = SeriesOutline(
            genre="gentlefemdom",
            story_id="series_story_006",
            name="Long Series",
            description="A series with many books",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="Epic Series",
            book_ids=books,
            long_term_character_evolution={},
            thematic_progression=[],
        )

        assert len(outline.book_ids) == 5
        assert outline.book_ids == books
        assert outline.book_ids[0] == "book_001"
        assert outline.book_ids[4] == "book_005"

    def test_series_outline_with_multiple_character_arcs(self):
        """Test creation with multiple character evolution tracks."""
        now = datetime.now()
        characters = {
            "Protagonist": "from doubt → confidence",
            "Antagonist": "from hidden → exposed",
            "Ally": "from distant → close",
            "Love Interest": "from stranger → partner",
            "Mentor": "from active → reflective",
        }

        outline = SeriesOutline(
            genre="mystery",
            story_id="series_story_007",
            name="Complex Series",
            description="Series with many character arcs",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="Complex Story",
            book_ids=["book_001", "book_002", "book_003"],
            long_term_character_evolution=characters,
            thematic_progression=[],
        )

        assert len(outline.long_term_character_evolution) == 5
        assert outline.long_term_character_evolution == characters

    def test_series_outline_with_multiple_themes(self):
        """Test creation with multiple thematic progressions."""
        now = datetime.now()
        themes = [
            "Book 1: Foundation - establishing the world",
            "Book 2: Complexity - adding layers and twists",
            "Book 3: Convergence - all threads come together",
            "Book 4: Transformation - the world changes",
            "Book 5: Legacy - consequences unfold",
        ]

        outline = SeriesOutline(
            genre="netorare",
            story_id="series_story_008",
            name="Thematic Series",
            description="Series with rich thematic progression",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="Thematic Arc",
            book_ids=[],
            long_term_character_evolution={},
            thematic_progression=themes,
        )

        assert len(outline.thematic_progression) == 5
        assert outline.thematic_progression == themes

    def test_series_outline_with_parent_id(self):
        """Test creation with parent_id."""
        now = datetime.now()

        outline = SeriesOutline(
            genre="mystery",
            story_id="series_story_009",
            name="Series",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id="universe_001",
            series_name="Part of Universe",
            book_ids=[],
            long_term_character_evolution={},
            thematic_progression=[],
        )

        assert outline.parent_id == "universe_001"


class TestSeriesOutlineValidation:
    """Test SeriesOutline validation logic (minimal, as per spec)."""

    def test_series_outline_accepts_all_empty_collections(self):
        """Test that all collections can be empty (no special validation)."""
        now = datetime.now()

        # This should not raise any exceptions
        outline = SeriesOutline(
            genre="mystery",
            story_id="series_story_010",
            name="Minimal Series",
            description="Series with no data",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="Minimal",
            book_ids=[],
            long_term_character_evolution={},
            thematic_progression=[],
        )

        assert outline.book_ids == []
        assert outline.long_term_character_evolution == {}
        assert outline.thematic_progression == []

    def test_series_outline_accepts_single_character(self):
        """Test that a single character arc is accepted."""
        now = datetime.now()

        outline = SeriesOutline(
            genre="netorare",
            story_id="series_story_011",
            name="Single Character",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="Single",
            book_ids=["book_001"],
            long_term_character_evolution={"Protagonist": "transformation arc"},
            thematic_progression=[],
        )

        assert len(outline.long_term_character_evolution) == 1


class TestSeriesOutlineGenreConsistency:
    """Test that SeriesOutline works identically across all genres."""

    @pytest.mark.parametrize("genre", ["mystery", "netorare", "gentlefemdom"])
    def test_series_outline_works_for_all_genres(self, genre):
        """Test that SeriesOutline class works for all 3 genres without special-casing."""
        now = datetime.now()

        outline = SeriesOutline(
            genre=genre,
            story_id=f"series_{genre}",
            name="Series",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name=f"Series for {genre}",
            book_ids=["book_001", "book_002"],
            long_term_character_evolution={"Hero": "arc"},
            thematic_progression=["Theme 1"],
        )

        assert outline.genre == genre
        assert outline.artifact_type() == "series_outline"
        assert len(outline.book_ids) == 2


class TestSeriesOutlineEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_series_outline_with_many_books(self):
        """Test with a very large series."""
        now = datetime.now()
        books = [f"book_{i:04d}" for i in range(1, 51)]  # 50 books

        outline = SeriesOutline(
            genre="mystery",
            story_id="series_story_012",
            name="Epic Series",
            description="A 50-book series",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="The Fifty",
            book_ids=books,
            long_term_character_evolution={},
            thematic_progression=[],
        )

        assert len(outline.book_ids) == 50
        assert outline.book_ids[0] == "book_0001"
        assert outline.book_ids[49] == "book_0050"

    def test_series_outline_with_many_characters(self):
        """Test with many character arcs."""
        now = datetime.now()
        characters = {f"Character_{i}": f"arc_{i}" for i in range(1, 21)}  # 20 characters

        outline = SeriesOutline(
            genre="netorare",
            story_id="series_story_013",
            name="Many Characters",
            description="Series with many characters",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="Ensemble Cast",
            book_ids=[],
            long_term_character_evolution=characters,
            thematic_progression=[],
        )

        assert len(outline.long_term_character_evolution) == 20

    def test_series_outline_with_empty_strings(self):
        """Test that empty strings in collections are accepted."""
        now = datetime.now()

        outline = SeriesOutline(
            genre="gentlefemdom",
            story_id="series_story_014",
            name="Empty Data",
            description="Test",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="",  # Empty series name
            book_ids=[""],  # Book with empty ID
            long_term_character_evolution={"": ""},  # Character with empty arc
            thematic_progression=[""],  # Empty theme
        )

        assert outline.series_name == ""
        assert outline.book_ids == [""]
        assert outline.long_term_character_evolution == {"": ""}
        assert outline.thematic_progression == [""]

    def test_series_outline_with_long_character_arc_descriptions(self):
        """Test with long character arc descriptions."""
        now = datetime.now()
        characters = {
            "Protagonist": (
                "A journey from deep doubt and self-destructive patterns "
                "toward self-acceptance and genuine connection with others"
            ),
            "Mentor": (
                "Transition from controlling wisdom to empowering guidance, "
                "learning to trust the protagonist's own path"
            ),
        }

        outline = SeriesOutline(
            genre="mystery",
            story_id="series_story_015",
            name="Detailed Arcs",
            description="Series with detailed character development",
            created_at=now,
            modified_at=now,
            parent_id=None,
            series_name="Deep Development",
            book_ids=["book_001", "book_002"],
            long_term_character_evolution=characters,
            thematic_progression=[],
        )

        assert outline.long_term_character_evolution == characters
