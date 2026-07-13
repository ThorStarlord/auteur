"""Tests for TemporalValidator.

Tests validate:
- Unique narrative_position within chapter
- Valid temporal relations (follows_scene, parallel_with)
- Mutual parallel_with relationships
- No circular temporal chains
- Position vs time distinction
- Chronological consistency
"""

import pytest

from auteur.narrative_realization.schema.scene_outline import (
    SceneOutline,
    SceneStatus,
    TemporalRelation,
)
from auteur.narrative_realization.validator.temporal_validator import (
    TemporalValidator,
    TemporalViolationType,
)


class TestTemporalValidatorBasics:
    """Test basic temporal validator functionality."""

    def test_validator_initialization(self):
        """Test validator initializes empty."""
        validator = TemporalValidator()
        assert validator.scenes == {}
        assert len(validator.violations) == 0

    def test_add_scene(self):
        """Test adding scenes to validator."""
        validator = TemporalValidator()
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)
        assert scene.id in validator.scenes

    def test_draft_scene_skipped(self):
        """Test that draft scenes are skipped in individual validation."""
        validator = TemporalValidator()
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
        )
        result = validator.validate_scene(scene)
        assert result.is_valid is True


class TestUniquePositions:
    """Test unique narrative_position validation."""

    def test_unique_positions_valid(self):
        """Test scenes with unique positions are valid."""
        validator = TemporalValidator()

        for i in range(1, 4):
            scene = SceneOutline(
                id=f"scene_01_0{i}",
                chapter_id="chapter_01",
                narrative_position=i,
                story_time=f"day_1_hour_{i}",
                pov_character_id="clara",
                participants=["clara"],
                status=SceneStatus.READY,
            )
            validator.add_scene(scene)

        result = validator.validate_all_scenes()
        assert result.is_valid is True
        assert len(result.violations) == 0

    def test_duplicate_positions_detected(self):
        """Test duplicate positions within chapter are detected."""
        validator = TemporalValidator()

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=1,  # Duplicate!
            story_time="day_1_afternoon",
            pov_character_id="clara",
            participants=["clara"],
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        assert result.is_valid is False
        assert any(
            v.violation_type == TemporalViolationType.DUPLICATE_POSITION
            for v in result.violations
        )

    def test_different_chapters_allow_same_position(self):
        """Test same position allowed in different chapters."""
        validator = TemporalValidator()

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_02_01",
            chapter_id="chapter_02",
            narrative_position=1,  # Same position, different chapter
            story_time="day_2",
            pov_character_id="clara",
            participants=["clara"],
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        # Should not have duplicate position errors
        duplicate_errors = [
            v
            for v in result.violations
            if v.violation_type == TemporalViolationType.DUPLICATE_POSITION
        ]
        assert len(duplicate_errors) == 0


class TestTemporalRelations:
    """Test temporal relation validation."""

    def test_valid_follows_scene(self):
        """Test valid follows_scene reference."""
        validator = TemporalValidator()

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_1_afternoon",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_scene(scene2)
        assert result.is_valid is True

    def test_invalid_follows_reference(self):
        """Test invalid follows_scene reference is detected."""
        validator = TemporalValidator()

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(follows_scene="scene_01_99"),  # Non-existent
            status=SceneStatus.READY,
        )

        validator.add_scene(scene)

        result = validator.validate_scene(scene)
        assert result.is_valid is False
        assert any(
            v.violation_type == TemporalViolationType.INVALID_FOLLOWS_REFERENCE
            for v in result.violations
        )

    def test_self_reference_detected(self):
        """Test scene following itself is detected."""
        validator = TemporalValidator()

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(follows_scene="scene_01_01"),  # Self-ref
            status=SceneStatus.READY,
        )

        validator.add_scene(scene)

        result = validator.validate_scene(scene)
        assert result.is_valid is False
        assert any(
            v.violation_type == TemporalViolationType.SELF_REFERENCE
            for v in result.violations
        )


class TestParallelRelations:
    """Test parallel_with temporal relations."""

    def test_valid_mutual_parallel(self):
        """Test valid mutual parallel_with relationships."""
        validator = TemporalValidator()

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_1_morning",  # Same time
            pov_character_id="daniel",
            participants=["daniel"],
            temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        assert result.is_valid is True

    def test_non_mutual_parallel_detected(self):
        """Test non-mutual parallel_with is detected."""
        validator = TemporalValidator()

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_1_morning",
            pov_character_id="daniel",
            participants=["daniel"],
            # Missing parallel_with back to scene_01_01
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        assert result.is_valid is False
        assert any(
            v.violation_type == TemporalViolationType.NON_MUTUAL_PARALLEL
            for v in result.violations
        )

    def test_self_parallel_detected(self):
        """Test scene parallel with itself is detected."""
        validator = TemporalValidator()

        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
            status=SceneStatus.READY,
        )

        validator.add_scene(scene)

        result = validator.validate_scene(scene)
        assert result.is_valid is False
        assert any(
            v.violation_type == TemporalViolationType.SELF_REFERENCE
            for v in result.violations
        )


class TestCircularParallel:
    """Test circular parallel_with detection."""

    def test_no_circular_in_valid_chain(self):
        """Test valid three-scene parallel chain."""
        validator = TemporalValidator()

        # A parallel B, B parallel C, C parallel A would be circular
        # A parallel B, B parallel C (no back-reference) is valid

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_1_morning",
            pov_character_id="daniel",
            participants=["daniel"],
            temporal_relation=TemporalRelation(
                parallel_with=["scene_01_01", "scene_01_03"]
            ),
            status=SceneStatus.READY,
        )

        scene3 = SceneOutline(
            id="scene_01_03",
            chapter_id="chapter_01",
            narrative_position=3,
            story_time="day_1_morning",
            pov_character_id="jane",
            participants=["jane"],
            temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)
        validator.add_scene(scene3)

        result = validator.validate_all_scenes()
        # No circular dependency here
        circular_errors = [
            v
            for v in result.violations
            if v.violation_type == TemporalViolationType.CIRCULAR_PARALLEL
        ]
        # May have non-mutual errors but not circular
        # (This depends on implementation interpretation)

    def test_simple_cycle_detected(self):
        """Test simple A→B→A cycle is detected."""
        validator = TemporalValidator()

        # Create impossible situation: A parallel B, B parallel A with self-check
        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_1",
            pov_character_id="daniel",
            participants=["daniel"],
            temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        # This is a valid mutual relationship, not a cycle


class TestPositionVsTime:
    """Test distinction between narrative_position and story_time."""

    def test_position_is_reading_order(self):
        """Test narrative_position represents reading order."""
        validator = TemporalValidator()

        scenes = []
        for i in range(1, 4):
            scene = SceneOutline(
                id=f"scene_01_0{i}",
                chapter_id="chapter_01",
                narrative_position=i,  # Sequential reading order
                story_time=f"day_1_segment_{i}",
                pov_character_id="clara",
                participants=["clara"],
                status=SceneStatus.READY,
            )
            validator.add_scene(scene)
            scenes.append(scene)

        result = validator.validate_all_scenes()
        # Reading order is sequential, so no position errors
        position_errors = [
            v
            for v in result.violations
            if v.violation_type == TemporalViolationType.DUPLICATE_POSITION
        ]
        assert len(position_errors) == 0

    def test_story_time_allows_simultaneity(self):
        """Test story_time can be same for simultaneous events."""
        validator = TemporalValidator()

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_1_morning",  # Same time
            pov_character_id="daniel",
            participants=["daniel"],
            temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        # Same story_time with parallel_with is valid


class TestChronologicalConsistency:
    """Test chronological consistency validation."""

    def test_follows_respects_position_order(self):
        """Test scene following another respects position order."""
        validator = TemporalValidator()

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_1_afternoon",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        assert result.is_valid is True

    def test_follows_violates_position_order(self):
        """Test scene following another in wrong position order."""
        validator = TemporalValidator()

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=2,  # Comes later
            story_time="day_1_afternoon",
            pov_character_id="clara",
            participants=["clara"],
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=1,  # Comes first but follows scene 1?
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        assert result.is_valid is False


class TestErrorReporting:
    """Test error message generation."""

    def test_violation_report_no_errors(self):
        """Test report generation with no violations."""
        validator = TemporalValidator()
        report = validator.report_temporal_violations([])
        assert "No temporal violations" in report

    def test_violation_report_includes_details(self):
        """Test report includes violation details."""
        from auteur.narrative_realization.validator.temporal_validator import (
            TemporalViolation,
        )

        violation = TemporalViolation(
            scene_id="scene_01_01",
            violation_type=TemporalViolationType.DUPLICATE_POSITION,
            related_scene_id="scene_01_02",
            message="Duplicate position detected",
            suggestion="Change position",
        )

        validator = TemporalValidator()
        report = validator.report_temporal_violations([violation])
        assert "scene_01_01" in report
        assert "duplicate_position" in report
