"""Tests for ArcValidator ensuring genre-aware arc validation.

This test suite validates the critical weak boundary where character arcs
must respect genre-specific themes. All three genres are tested to ensure
proper enforcement of genre contracts.
"""

import pytest
from datetime import datetime

from auteur.narrative_blueprint.schema.character_arc import CharacterArc, TurningPoint
from auteur.narrative_blueprint.schema.story_arc import StoryArc, ArcCheckpoint
from auteur.narrative_blueprint.schema.outline_types import PhaseRange
from auteur.narrative_blueprint.validator.arc_validator import (
    ArcValidator,
    GENRE_THEMES,
)


class TestGenreThemesMapping:
    """Test the GENRE_THEMES constant is properly defined."""

    def test_genre_themes_has_all_genres(self):
        """All three genres should have theme definitions."""
        assert "netorare" in GENRE_THEMES
        assert "mystery" in GENRE_THEMES
        assert "gentlefemdom" in GENRE_THEMES

    def test_genre_themes_netorare(self):
        """Netorara should have humiliation-related themes."""
        themes = GENRE_THEMES["netorare"]
        assert "humiliation" in themes
        assert "degradation" in themes
        assert "cuckoldry" in themes
        assert "shame" in themes
        assert "exposure" in themes

    def test_genre_themes_mystery(self):
        """Mystery should have investigation-related themes."""
        themes = GENRE_THEMES["mystery"]
        assert "investigation" in themes
        assert "deception" in themes
        assert "revelation" in themes
        assert "conspiracy" in themes
        assert "doubt" in themes

    def test_genre_themes_gentlefemdom(self):
        """Gentle femdom should have authority-related themes."""
        themes = GENRE_THEMES["gentlefemdom"]
        assert "authority" in themes
        assert "surrender" in themes
        assert "dominance" in themes
        assert "trust" in themes
        assert "control" in themes


class TestValidateArcThemes:
    """Test CharacterArc theme validation against genre expectations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.now = datetime.now()

    def _create_character_arc(
        self, genre: str, genre_themes: list, character_name: str = "Test Character"
    ) -> CharacterArc:
        """Helper to create a CharacterArc with specified themes."""
        return CharacterArc(
            genre=genre,
            story_id="story_001",
            name=f"{character_name} Arc",
            description="Test arc",
            created_at=self.now,
            modified_at=self.now,
            span_chapters=[1, 2, 3],
            character_name=character_name,
            initial_belief="Initial belief",
            final_belief="Final belief",
            turning_points=[
                TurningPoint(chapter=2, moment="Event", belief_shift="Shift")
            ],
            genre_themes=genre_themes,
        )

    def test_netorare_arc_with_matching_themes_passes(self):
        """Netorara arc with humiliation/cuckoldry themes should pass validation."""
        arc = self._create_character_arc(
            "netorare", ["humiliation", "shame"], "John"
        )
        validator = ArcValidator()
        is_valid, errors = validator.validate_arc_themes(arc, "netorare")
        assert is_valid is True
        assert errors == []

    def test_netorare_arc_with_single_matching_theme_passes(self):
        """Netorara arc with any single matching theme should pass."""
        arc = self._create_character_arc("netorare", ["humiliation"], "Jane")
        validator = ArcValidator()
        is_valid, errors = validator.validate_arc_themes(arc, "netorare")
        assert is_valid is True
        assert errors == []

    def test_netorare_arc_with_mismatched_themes_fails(self):
        """Netorara arc with gentle femdom themes should fail validation."""
        arc = self._create_character_arc(
            "netorare", ["authority", "surrender"], "James"
        )
        validator = ArcValidator()
        is_valid, errors = validator.validate_arc_themes(arc, "netorare")
        assert is_valid is False
        assert len(errors) > 0
        assert "don't match" in errors[0]

    def test_gentlefemdom_arc_with_matching_themes_passes(self):
        """Gentle femdom arc with authority/surrender themes should pass."""
        arc = self._create_character_arc(
            "gentlefemdom", ["authority", "control"], "Dominatrix"
        )
        validator = ArcValidator()
        is_valid, errors = validator.validate_arc_themes(arc, "gentlefemdom")
        assert is_valid is True
        assert errors == []

    def test_gentlefemdom_arc_with_netorare_themes_fails(self):
        """Gentle femdom arc with netorare themes should fail validation."""
        arc = self._create_character_arc(
            "gentlefemdom", ["humiliation", "degradation"], "Sub"
        )
        validator = ArcValidator()
        is_valid, errors = validator.validate_arc_themes(arc, "gentlefemdom")
        assert is_valid is False
        assert len(errors) > 0

    def test_mystery_arc_with_matching_themes_passes(self):
        """Mystery arc with investigation/deception themes should pass."""
        arc = self._create_character_arc(
            "mystery", ["investigation", "revelation"], "Detective"
        )
        validator = ArcValidator()
        is_valid, errors = validator.validate_arc_themes(arc, "mystery")
        assert is_valid is True
        assert errors == []

    def test_mystery_arc_with_single_matching_theme_passes(self):
        """Mystery arc with any single matching theme should pass."""
        arc = self._create_character_arc("mystery", ["deception"], "Suspect")
        validator = ArcValidator()
        is_valid, errors = validator.validate_arc_themes(arc, "mystery")
        assert is_valid is True
        assert errors == []

    def test_mystery_arc_with_gentlefemdom_themes_fails(self):
        """Mystery arc with gentle femdom themes should fail validation."""
        arc = self._create_character_arc("mystery", ["authority", "dominance"], "Clue")
        validator = ArcValidator()
        is_valid, errors = validator.validate_arc_themes(arc, "mystery")
        assert is_valid is False
        assert len(errors) > 0

    def test_error_message_includes_theme_details(self):
        """Error message should include the mismatched themes and expected themes."""
        arc = self._create_character_arc(
            "netorare", ["authority", "surrender"], "BadArc"
        )
        validator = ArcValidator()
        is_valid, errors = validator.validate_arc_themes(arc, "netorare")
        assert is_valid is False
        error_msg = errors[0]
        assert "Character arc themes" in error_msg
        assert "authority" in error_msg or "surrender" in error_msg
        assert "netorare" in error_msg.lower()


class TestValidateStoryArcPhases:
    """Test StoryArc phase validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.now = datetime.now()

    def _create_story_arc(
        self,
        genre: str = "mystery",
        phase_range: PhaseRange = None,
        checkpoints: list = None,
    ) -> StoryArc:
        """Helper to create a StoryArc."""
        if phase_range is None:
            phase_range = PhaseRange(start=1, peak=5, end=9)
        if checkpoints is None:
            checkpoints = [
                ArcCheckpoint(phase=1, moment="Setup"),
                ArcCheckpoint(phase=5, moment="Climax"),
                ArcCheckpoint(phase=9, moment="Resolution"),
            ]

        return StoryArc(
            genre=genre,
            story_id="story_002",
            name="Main Plot Arc",
            description="The main story arc",
            created_at=self.now,
            modified_at=self.now,
            arc_name="Main Mystery Arc",
            arc_category="mystery",
            span_chapters=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            phase_range=phase_range,
            checkpoints=checkpoints,
        )

    def test_valid_story_arc_passes(self):
        """StoryArc with valid phases should pass validation."""
        arc = self._create_story_arc()
        validator = ArcValidator()
        is_valid, errors = validator.validate_story_arc_phases(arc, num_chapters=10)
        assert is_valid is True
        assert errors == []

    def test_story_arc_with_all_phases_valid(self):
        """StoryArc with phases 1-9 should all be valid."""
        checkpoints = [
            ArcCheckpoint(phase=i, moment=f"Phase {i}")
            for i in range(1, 10)
        ]
        arc = self._create_story_arc(
            phase_range=PhaseRange(start=1, peak=5, end=9), checkpoints=checkpoints
        )
        validator = ArcValidator()
        is_valid, errors = validator.validate_story_arc_phases(arc, num_chapters=9)
        assert is_valid is True
        assert errors == []

    def test_story_arc_with_invalid_start_phase_fails(self):
        """PhaseRange with start < 1 should fail."""
        with pytest.raises(ValueError):
            # PhaseRange validates in __post_init__, so this should fail at creation
            PhaseRange(start=0, peak=5, end=9)

    def test_story_arc_with_invalid_end_phase_fails(self):
        """PhaseRange with end > 9 should fail."""
        with pytest.raises(ValueError):
            # PhaseRange validates in __post_init__
            PhaseRange(start=1, peak=5, end=10)

    def test_story_arc_checkpoint_with_invalid_phase_fails(self):
        """StoryArc with checkpoint phase outside 1-9 range should fail validation."""
        # Create a checkpoint with invalid phase
        checkpoints = [
            ArcCheckpoint(phase=0, moment="Invalid"),  # Invalid
            ArcCheckpoint(phase=5, moment="Valid"),
        ]
        arc = self._create_story_arc(checkpoints=checkpoints)
        validator = ArcValidator()
        is_valid, errors = validator.validate_story_arc_phases(arc, num_chapters=10)
        assert is_valid is False
        assert len(errors) > 0

    def test_story_arc_checkpoint_with_phase_too_high_fails(self):
        """StoryArc with checkpoint phase > 9 should fail validation."""
        checkpoints = [
            ArcCheckpoint(phase=1, moment="Setup"),
            ArcCheckpoint(phase=10, moment="Invalid phase"),  # Invalid
        ]
        arc = self._create_story_arc(checkpoints=checkpoints)
        validator = ArcValidator()
        is_valid, errors = validator.validate_story_arc_phases(arc, num_chapters=10)
        assert is_valid is False
        assert len(errors) > 0

    def test_story_arc_with_empty_checkpoints_passes(self):
        """StoryArc with no checkpoints should pass (optional field)."""
        arc = self._create_story_arc(checkpoints=[])
        validator = ArcValidator()
        is_valid, errors = validator.validate_story_arc_phases(arc, num_chapters=10)
        assert is_valid is True
        assert errors == []

    def test_error_message_includes_invalid_phase_info(self):
        """Error message should identify which checkpoint has invalid phase."""
        checkpoints = [
            ArcCheckpoint(phase=1, moment="Setup"),
            ArcCheckpoint(phase=15, moment="Bad phase"),
        ]
        arc = self._create_story_arc(checkpoints=checkpoints)
        validator = ArcValidator()
        is_valid, errors = validator.validate_story_arc_phases(arc, num_chapters=10)
        assert is_valid is False
        error_msg = " ".join(errors)
        assert "phase" in error_msg.lower()
        assert "15" in error_msg or "checkpoint" in error_msg.lower()


class TestArcValidatorIntegration:
    """Integration tests for ArcValidator across all genres."""

    def setup_method(self):
        """Set up test fixtures."""
        self.now = datetime.now()
        self.validator = ArcValidator()

    def test_all_three_genres_properly_distinguished(self):
        """Each genre should reject themes from other genres."""
        # Netorara rejects mystery themes
        netorare_arc = CharacterArc(
            genre="netorare",
            story_id="story_003",
            name="Wrong Themes Arc",
            description="Uses mystery themes",
            created_at=self.now,
            modified_at=self.now,
            span_chapters=[1, 2],
            character_name="Netorara Char",
            initial_belief="Start",
            final_belief="End",
            genre_themes=["investigation", "deception"],
        )
        is_valid, errors = self.validator.validate_arc_themes(netorare_arc, "netorare")
        assert is_valid is False

        # Mystery rejects gentlefemdom themes
        mystery_arc = CharacterArc(
            genre="mystery",
            story_id="story_003",
            name="Wrong Themes Arc",
            description="Uses gentle femdom themes",
            created_at=self.now,
            modified_at=self.now,
            span_chapters=[1, 2],
            character_name="Mystery Char",
            initial_belief="Start",
            final_belief="End",
            genre_themes=["authority", "dominance"],
        )
        is_valid, errors = self.validator.validate_arc_themes(mystery_arc, "mystery")
        assert is_valid is False

        # Gentlefemdom rejects netorare themes
        gf_arc = CharacterArc(
            genre="gentlefemdom",
            story_id="story_003",
            name="Wrong Themes Arc",
            description="Uses netorare themes",
            created_at=self.now,
            modified_at=self.now,
            span_chapters=[1, 2],
            character_name="GF Char",
            initial_belief="Start",
            final_belief="End",
            genre_themes=["humiliation", "cuckoldry"],
        )
        is_valid, errors = self.validator.validate_arc_themes(gf_arc, "gentlefemdom")
        assert is_valid is False

    def test_mixed_valid_and_invalid_themes_still_passes_with_one_valid(self):
        """Arc passes if at least ONE theme matches genre."""
        # Mix of valid and invalid themes - should pass because "humiliation" is valid
        arc = CharacterArc(
            genre="netorare",
            story_id="story_004",
            name="Mixed Themes Arc",
            description="Mixed themes",
            created_at=self.now,
            modified_at=self.now,
            span_chapters=[1, 2],
            character_name="Mixed",
            initial_belief="Start",
            final_belief="End",
            genre_themes=["humiliation", "authority", "investigation"],  # Mix
        )
        is_valid, errors = self.validator.validate_arc_themes(arc, "netorare")
        assert is_valid is True  # Passes because "humiliation" is in GENRE_THEMES["netorare"]
