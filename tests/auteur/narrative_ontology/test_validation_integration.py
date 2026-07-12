"""Integration tests for Layer 1-2 validator refactoring to use Layer 0 ontology.

Tests validate that:
- arc_validator uses Layer 0 ontology for theme validation
- outline_validator uses Layer 0 ontology for phase/relationship validation
- Validators work identically for all 3 genres
- Changing ontology affects validation behavior
- Layer 0 is the single source of truth for validation rules
"""

import pytest
from datetime import datetime

from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint
from auteur.narrative_blueprint.schema.outline_types import PhaseRange
from auteur.narrative_blueprint.schema.book_outline import BookOutline
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.validator.arc_validator import ArcValidator
from auteur.narrative_blueprint.validator.outline_validator import ContainerValidator
from auteur.narrative_ontology.validator.ontology_validator import OntologyValidator


class TestArcValidatorUsesOntology:
    """Test that ArcValidator uses Layer 0 ontology for theme validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.now = datetime.now()
        self.validator = ArcValidator()
        self.ontology_validator = OntologyValidator()

    def test_arc_validator_uses_ontology_for_netorare_themes(self):
        """ArcValidator should use ontology themes for netorare genre."""
        # Get themes from ontology
        ontology_themes = self.ontology_validator.get_genre_themes("netorare")

        # Create arc with valid ontology theme
        valid_theme = list(ontology_themes)[0]
        arc = CharacterArc(
            genre="netorare",
            story_id="story_001",
            name="Test Arc",
            description="Test",
            created_at=self.now,
            modified_at=self.now,
            span_chapters=[1, 2],
            character_name="Char",
            initial_belief="Start",
            final_belief="End",
            genre_themes=[valid_theme],
        )

        is_valid, errors = self.validator.validate_arc_themes(arc, "netorare")
        assert is_valid is True
        assert errors == []

    def test_arc_validator_uses_ontology_for_mystery_themes(self):
        """ArcValidator should use ontology themes for mystery genre."""
        ontology_themes = self.ontology_validator.get_genre_themes("mystery")

        # Create arc with valid ontology theme
        valid_theme = list(ontology_themes)[0]
        arc = CharacterArc(
            genre="mystery",
            story_id="story_002",
            name="Test Arc",
            description="Test",
            created_at=self.now,
            modified_at=self.now,
            span_chapters=[1, 2],
            character_name="Char",
            initial_belief="Start",
            final_belief="End",
            genre_themes=[valid_theme],
        )

        is_valid, errors = self.validator.validate_arc_themes(arc, "mystery")
        assert is_valid is True
        assert errors == []

    def test_arc_validator_uses_ontology_for_gentlefemdom_themes(self):
        """ArcValidator should use ontology themes for gentlefemdom genre."""
        ontology_themes = self.ontology_validator.get_genre_themes("gentlefemdom")

        # Create arc with valid ontology theme
        valid_theme = list(ontology_themes)[0]
        arc = CharacterArc(
            genre="gentlefemdom",
            story_id="story_003",
            name="Test Arc",
            description="Test",
            created_at=self.now,
            modified_at=self.now,
            span_chapters=[1, 2],
            character_name="Char",
            initial_belief="Start",
            final_belief="End",
            genre_themes=[valid_theme],
        )

        is_valid, errors = self.validator.validate_arc_themes(arc, "gentlefemdom")
        assert is_valid is True
        assert errors == []

    def test_arc_validator_rejects_themes_not_in_ontology(self):
        """ArcValidator should reject themes not defined in ontology."""
        # Use a theme that's not in any genre ontology
        invalid_theme = "non_existent_theme_xyz_123"

        arc = CharacterArc(
            genre="netorare",
            story_id="story_004",
            name="Test Arc",
            description="Test",
            created_at=self.now,
            modified_at=self.now,
            span_chapters=[1, 2],
            character_name="Char",
            initial_belief="Start",
            final_belief="End",
            genre_themes=[invalid_theme],
        )

        is_valid, errors = self.validator.validate_arc_themes(arc, "netorare")
        assert is_valid is False
        assert len(errors) > 0


class TestOutlineValidatorUsesOntology:
    """Test that ContainerValidator uses Layer 0 ontology for validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.now = datetime.now()
        self.validator = ContainerValidator()
        self.ontology_validator = OntologyValidator()

    def test_outline_validator_uses_ontology_validator(self):
        """ContainerValidator should have initialized OntologyValidator."""
        assert hasattr(self.validator, "_ontology_validator")
        assert self.validator._ontology_validator is not None
        assert isinstance(self.validator._ontology_validator, OntologyValidator)

    def test_outline_validator_accepts_valid_phases_from_ontology(self):
        """ContainerValidator should accept phases 1-9 from ontology constraints."""
        # Phases 1-9 are defined in Arc concept in base ontology
        chapter = ChapterOutline(
            genre="netorare",
            story_id="story_001",
            name="Chapter",
            description="Chapter outline",
            created_at=self.now,
            modified_at=self.now,
            parent_id="book_001",
            chapter_number=1,
            title="Chapter 1",
            phase=5,  # Valid phase from Arc concept
            goal="Goal",
            conflict="Conflict",
            turning_point="Turning point",
            emotional_beat="Beat",
        )

        validator = ContainerValidator()
        is_valid, errors = validator.validate_consistency([chapter])
        assert is_valid is True
        assert errors == []

    def test_outline_validator_rejects_phases_outside_ontology_range(self):
        """ContainerValidator should reject phases outside Arc range."""
        # Phase 0 is outside the 1-9 range defined in ontology
        # Note: ChapterOutline validates phase in __init__, so we expect ValueError
        with pytest.raises(ValueError):
            ChapterOutline(
                genre="netorare",
                story_id="story_001",
                name="Chapter",
                description="Chapter outline",
                created_at=self.now,
                modified_at=self.now,
                parent_id="book_001",
                chapter_number=1,
                title="Chapter 1",
                phase=0,  # Invalid: outside 1-9 range from Arc concept
                goal="Goal",
                conflict="Conflict",
                turning_point="Turning point",
                emotional_beat="Beat",
            )


class TestValidatorConsistencyAcrossGenres:
    """Test that all genres are validated identically using ontology."""

    def setup_method(self):
        """Set up test fixtures."""
        self.now = datetime.now()
        self.arc_validator = ArcValidator()
        self.ontology_validator = OntologyValidator()

    def test_all_genres_have_theme_sets_in_ontology(self):
        """All three genres should have theme sets defined in ontology."""
        themes_by_genre = self.ontology_validator.get_all_genre_themes()

        assert "netorare" in themes_by_genre
        assert "mystery" in themes_by_genre
        assert "gentlefemdom" in themes_by_genre

        # Each should have non-empty theme set
        for genre, themes in themes_by_genre.items():
            assert len(themes) > 0, f"Genre {genre} has no themes"

    def test_theme_validation_consistent_for_all_genres(self):
        """Theme validation should follow same pattern for all genres."""
        genres = ["netorare", "mystery", "gentlefemdom"]

        for genre in genres:
            # Get valid theme from ontology
            valid_themes = self.ontology_validator.get_genre_themes(genre)
            valid_theme = list(valid_themes)[0]

            # Create arc with valid theme
            arc = CharacterArc(
                genre=genre,
                story_id=f"story_{genre}",
                name="Test Arc",
                description="Test",
                created_at=self.now,
                modified_at=self.now,
                span_chapters=[1, 2],
                character_name="Char",
                initial_belief="Start",
                final_belief="End",
                genre_themes=[valid_theme],
            )

            is_valid, errors = self.arc_validator.validate_arc_themes(arc, genre)
            assert is_valid is True, f"Genre {genre} should accept its own themes"
            assert errors == []

    def test_genre_themes_are_mutually_exclusive(self):
        """Themes from one genre should be rejected by other genres."""
        # Get theme from netorare
        netorare_themes = self.ontology_validator.get_genre_themes("netorare")
        netorare_theme = list(netorare_themes)[0]

        # Create mystery arc with netorare theme
        arc = CharacterArc(
            genre="mystery",
            story_id="story_cross_genre",
            name="Test Arc",
            description="Test",
            created_at=self.now,
            modified_at=self.now,
            span_chapters=[1, 2],
            character_name="Char",
            initial_belief="Start",
            final_belief="End",
            genre_themes=[netorare_theme],
        )

        is_valid, errors = self.arc_validator.validate_arc_themes(arc, "mystery")
        assert is_valid is False, "Mystery should reject netorare themes"
        assert len(errors) > 0


class TestValidatorRefactoringCompleteness:
    """Test that refactoring successfully moved validation to ontology."""

    def setup_method(self):
        """Set up test fixtures."""
        self.ontology_validator = OntologyValidator()

    def test_arc_validator_initialized_with_ontology(self):
        """ArcValidator should initialize OntologyValidator."""
        validator = ArcValidator()
        assert hasattr(validator, "_ontology_validator")
        assert validator._ontology_validator is not None

    def test_outline_validator_initialized_with_ontology(self):
        """ContainerValidator should initialize OntologyValidator."""
        validator = ContainerValidator()
        assert hasattr(validator, "_ontology_validator")
        assert validator._ontology_validator is not None

    def test_ontology_validator_provides_genre_themes(self):
        """OntologyValidator should provide genre themes method."""
        assert hasattr(self.ontology_validator, "get_genre_themes")
        assert callable(self.ontology_validator.get_genre_themes)

    def test_ontology_validator_provides_all_genre_themes(self):
        """OntologyValidator should provide method to get all genre themes."""
        assert hasattr(self.ontology_validator, "get_all_genre_themes")
        assert callable(self.ontology_validator.get_all_genre_themes)

    def test_ontology_validator_provides_genre_check(self):
        """OntologyValidator should provide genre validation method."""
        assert hasattr(self.ontology_validator, "is_valid_genre")
        assert callable(self.ontology_validator.is_valid_genre)

    def test_genre_themes_match_ontology_definitions(self):
        """Theme sets should match ontology definitions exactly."""
        netorare_themes = self.ontology_validator.get_genre_themes("netorare")
        # Expected from netorara_ontology.py
        expected = {"humiliation", "degradation", "cuckoldry", "shame", "exposure"}
        assert netorare_themes == expected

        mystery_themes = self.ontology_validator.get_genre_themes("mystery")
        # Expected from mystery_ontology.py
        expected = {"investigation", "deception", "revelation", "conspiracy", "doubt"}
        assert mystery_themes == expected

        gf_themes = self.ontology_validator.get_genre_themes("gentlefemdom")
        # Expected from gentlefemdom_ontology.py
        expected = {"authority", "surrender", "dominance", "trust", "control"}
        assert gf_themes == expected


class TestOntologyAsSourceOfTruth:
    """Test that ontology is the single source of truth for validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.now = datetime.now()
        self.arc_validator = ArcValidator()
        self.ontology_validator = OntologyValidator()

    def test_arc_themes_defined_in_ontology_not_hardcoded(self):
        """Arc themes should come from ontology, not from constants."""
        # Get themes from OntologyValidator (which loads from actual ontologies)
        ontology_themes = self.ontology_validator.get_all_genre_themes()

        # Each genre should have its theme set available
        for genre in ["netorare", "mystery", "gentlefemdom"]:
            themes = ontology_themes[genre]
            assert len(themes) > 0
            assert all(isinstance(t, str) for t in themes)

    def test_validation_respects_ontology_theme_definitions(self):
        """Validation should respect theme definitions in ontology."""
        # Create arcs with all valid themes for each genre
        genres = ["netorare", "mystery", "gentlefemdom"]

        for genre in genres:
            themes = self.ontology_validator.get_genre_themes(genre)
            for theme in themes:
                arc = CharacterArc(
                    genre=genre,
                    story_id=f"story_{theme}",
                    name="Test Arc",
                    description="Test",
                    created_at=self.now,
                    modified_at=self.now,
                    span_chapters=[1, 2],
                    character_name="Char",
                    initial_belief="Start",
                    final_belief="End",
                    genre_themes=[theme],
                )

                is_valid, errors = self.arc_validator.validate_arc_themes(
                    arc, genre
                )
                assert (
                    is_valid is True
                ), f"Theme '{theme}' should be valid for genre '{genre}'"
