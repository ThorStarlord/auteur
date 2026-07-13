"""Tests for RealizationValidator.

Tests validate:
- Valid beat references
- Invalid beat IDs detected
- Realization degree validation
- Evidence for partial/implied realizations
- Critical beat validation
"""

import pytest

from auteur.narrative_realization.schema.scene_outline import (
    SceneOutline,
    SceneStatus,
)
from auteur.narrative_realization.schema.scene_action import ArcBeatRealization
from auteur.narrative_realization.validator.realization_validator import (
    RealizationValidator,
    RealizationViolationType,
)


def make_beat(beat_id: str, degree: str = "full") -> ArcBeatRealization:
    """Helper to create ArcBeatRealization objects."""
    return ArcBeatRealization(beat_id=beat_id, degree=degree)


class TestRealizationValidatorBasics:
    """Test basic realization validator functionality."""

    def test_validator_initialization(self):
        """Test validator initializes empty."""
        validator = RealizationValidator()
        assert validator.scenes == {}
        assert validator.arc_beats == {}
        assert len(validator.violations) == 0

    def test_add_scene(self):
        """Test adding scenes to validator."""
        validator = RealizationValidator()
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)
        assert scene.id in validator.scenes

    def test_register_arc_beat(self):
        """Test registering arc beats."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_clara_trust", "clara_trust_arc", critical=True)
        assert "beat_clara_trust" in validator.arc_beats
        assert validator.arc_beats["beat_clara_trust"]["critical"] is True

    def test_draft_scene_skipped(self):
        """Test draft scenes are skipped in validation."""
        validator = RealizationValidator()
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
        )
        result = validator.validate_scene(scene)
        assert result.is_valid is True


class TestBeatReferences:
    """Test beat reference validation."""

    def test_valid_beat_reference(self):
        """Test scene with valid beat reference."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01")

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_01")],
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)

        result = validator.validate_scene(scene)
        beat_ref_errors = [
            v
            for v in result.violations
            if v.violation_type == RealizationViolationType.INVALID_BEAT_REFERENCE
        ]
        assert len(beat_ref_errors) == 0

    def test_invalid_beat_reference_detected(self):
        """Test non-existent beat reference is detected."""
        validator = RealizationValidator()

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_nonexistent")],
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)

        result = validator.validate_scene(scene)
        assert result.is_valid is False
        assert any(
            v.violation_type == RealizationViolationType.INVALID_BEAT_REFERENCE
            for v in result.violations
        )

    def test_multiple_beat_references(self):
        """Test scene with multiple beat references."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01")
        validator.register_arc_beat("beat_02", "arc_02")

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_01"), make_beat("beat_02")],
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)

        result = validator.validate_scene(scene)
        # No beat reference errors
        beat_errors = [
            v
            for v in result.violations
            if v.violation_type == RealizationViolationType.INVALID_BEAT_REFERENCE
        ]
        assert len(beat_errors) == 0

    def test_mixed_valid_invalid_beats(self):
        """Test scene with both valid and invalid beat references."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01")
        # beat_02 not registered

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_01"), make_beat("beat_02")],
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)

        result = validator.validate_scene(scene)
        # Should report beat_02 as invalid
        assert any(
            v.violation_type == RealizationViolationType.INVALID_BEAT_REFERENCE
            and v.beat_id == "beat_02"
            for v in result.violations
        )


class TestRealizationDegree:
    """Test realization degree validation."""

    def test_valid_degrees_recognized(self):
        """Test valid realization degrees are accepted."""
        # Valid degrees: full, partial, implied, deferred
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01")

        degrees = ["full", "partial", "implied", "deferred"]
        for i, degree in enumerate(degrees):
            scene = SceneOutline(
                id=f"scene_01_{i+1:02d}",
                chapter_id="chapter_01",
                narrative_position=i + 1,
                story_time="day_1",
                pov_character_id="clara",
                participants=["clara"],
                realizes_arc_beats=[make_beat("beat_01", degree)],
                status=SceneStatus.DRAFT,
            )
            validator.add_scene(scene)
            result = validator.validate_scene(scene)
            # All degrees are valid
            assert result.is_valid is True


class TestCriticalBeatRealization:
    """Test critical beat realization validation."""

    def test_critical_beat_fully_realized(self):
        """Test critical beat is fully realized."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_critical", "arc_01", critical=True)

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_critical", "full")],
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)

        result = validator.validate_all_scenes()
        # Critical beat is realized, should be valid
        critical_errors = [
            v
            for v in result.violations
            if "critical" in v.violation_type.value
        ]
        assert len(critical_errors) == 0

    def test_critical_beat_not_realized(self):
        """Test missing critical beat is detected."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_critical", "arc_01", critical=True)
        # Don't create any scenes realizing this beat

        result = validator.validate_all_scenes()
        assert result.is_valid is False
        assert any(
            v.violation_type == RealizationViolationType.CRITICAL_BEAT_NOT_FULLY_REALIZED
            and v.beat_id == "beat_critical"
            for v in result.violations
        )

    def test_critical_beat_partial_not_sufficient(self):
        """Test critical beat with partial realization is not sufficient."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_critical", "arc_01", critical=True)

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_critical", "partial")],
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)

        result = validator.validate_all_scenes()
        # Partial realization is not sufficient for critical beats
        assert result.is_valid is False

    def test_multiple_critical_beats(self):
        """Test multiple critical beats validation."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_critical_01", "arc_01", critical=True)
        validator.register_arc_beat("beat_critical_02", "arc_02", critical=True)

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[
                make_beat("beat_critical_01", "full"),
                make_beat("beat_critical_02", "full"),
            ],
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)

        result = validator.validate_all_scenes()
        # Both critical beats realized
        critical_errors = [
            v
            for v in result.violations
            if "critical" in v.violation_type.value
        ]
        assert len(critical_errors) == 0


class TestNonCriticalBeats:
    """Test non-critical beat handling."""

    def test_non_critical_beats_unrealized(self):
        """Test non-critical beats don't need to be realized."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_non_critical", "arc_01", critical=False)

        result = validator.validate_all_scenes()
        # No error for unrealized non-critical beat
        assert result.is_valid is True

    def test_non_critical_beat_can_be_partial(self):
        """Test non-critical beats can be partially realized."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01", critical=False)

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_01", "partial")],
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)

        result = validator.validate_all_scenes()
        assert result.is_valid is True


class TestMultipleScenes:
    """Test validation across multiple scenes."""

    def test_beat_realized_in_one_scene(self):
        """Test beat realized in single scene."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01")

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_01")],
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)

        result = validator.validate_all_scenes()
        assert result.is_valid is True

    def test_beat_realized_in_multiple_scenes(self):
        """Test beat referenced in multiple scenes."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01", critical=True)

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_01", "partial")],
            status=SceneStatus.DRAFT,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_2",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_01", "full")],
            status=SceneStatus.DRAFT,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        # Critical beat is fully realized (in scene2)
        assert result.is_valid is True

    def test_different_arcs_in_different_scenes(self):
        """Test beats from different arcs in different scenes."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01")
        validator.register_arc_beat("beat_02", "arc_02")

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[make_beat("beat_01")],
            status=SceneStatus.DRAFT,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_2",
            pov_character_id="daniel",
            participants=["daniel"],
            realizes_arc_beats=[make_beat("beat_02")],
            status=SceneStatus.DRAFT,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        assert result.is_valid is True


class TestEmptyScenes:
    """Test scenes with no beats."""

    def test_scene_without_beats(self):
        """Test scene that realizes no beats."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01")

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            realizes_arc_beats=[],  # No beats
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)

        result = validator.validate_scene(scene)
        assert result.is_valid is True

    def test_no_scenes_critical_beat_unrealized(self):
        """Test validator with no scenes but critical beat registered."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01", critical=True)

        result = validator.validate_all_scenes()
        # Critical beat is unrealized when no scenes exist
        assert not result.is_valid


class TestErrorReporting:
    """Test error message generation."""

    def test_violation_report_no_errors(self):
        """Test report generation with no violations."""
        validator = RealizationValidator()
        report = validator.report_realization_violations([])
        assert "No realization violations" in report

    def test_violation_report_includes_beat(self):
        """Test report includes beat information."""
        from auteur.narrative_realization.validator.realization_validator import (
            RealizationViolation,
        )

        violation = RealizationViolation(
            scene_id="scene_01_01",
            violation_type=RealizationViolationType.INVALID_BEAT_REFERENCE,
            beat_id="beat_missing",
            message="Beat not found",
            suggestion="Create beat or update reference",
        )

        validator = RealizationValidator()
        report = validator.report_realization_violations([violation])
        assert "scene_01_01" in report
        assert "beat_missing" in report
        assert "invalid_beat_reference" in report


class TestBeatArcAssociation:
    """Test beat-arc association validation."""

    def test_beat_associated_with_arc(self):
        """Test beat is correctly associated with arc."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_trust_01", "clara_trust_arc")

        assert validator.arc_beats["beat_trust_01"]["arc_id"] == "clara_trust_arc"

    def test_multiple_beats_same_arc(self):
        """Test multiple beats from same arc."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01")
        validator.register_arc_beat("beat_02", "arc_01")

        assert validator.arc_beats["beat_01"]["arc_id"] == "arc_01"
        assert validator.arc_beats["beat_02"]["arc_id"] == "arc_01"

    def test_beats_different_arcs(self):
        """Test beats from different arcs."""
        validator = RealizationValidator()
        validator.register_arc_beat("beat_01", "arc_01")
        validator.register_arc_beat("beat_02", "arc_02")

        assert validator.arc_beats["beat_01"]["arc_id"] == "arc_01"
        assert validator.arc_beats["beat_02"]["arc_id"] == "arc_02"


class TestRealizationIntegration:
    """Integration tests for realization validation."""

    def test_complex_story_arc(self):
        """Test complex story with multiple arcs and beats."""
        validator = RealizationValidator()

        # Clara's trust arc
        validator.register_arc_beat("beat_trust_01", "clara_trust", critical=True)
        validator.register_arc_beat("beat_trust_02", "clara_trust", critical=True)

        # Daniel's deception arc
        validator.register_arc_beat("beat_deception_01", "daniel_deception", critical=False)

        # Scenes
        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara", "daniel"],
            realizes_arc_beats=[make_beat("beat_trust_01", "full")],
            status=SceneStatus.DRAFT,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_2",
            pov_character_id="daniel",
            participants=["daniel", "clara"],
            realizes_arc_beats=[make_beat("beat_deception_01", "full")],
            status=SceneStatus.DRAFT,
        )

        scene3 = SceneOutline(
            id="scene_01_03",
            chapter_id="chapter_01",
            narrative_position=3,
            story_time="day_3",
            pov_character_id="clara",
            participants=["clara", "daniel"],
            realizes_arc_beats=[make_beat("beat_trust_02", "full")],
            status=SceneStatus.DRAFT,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)
        validator.add_scene(scene3)

        result = validator.validate_all_scenes()
        # Both critical trust beats are realized
        assert result.is_valid is True
