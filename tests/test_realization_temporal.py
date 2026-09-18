"""Tests for Layer 3 temporal validation under the current SceneOutline contract."""

import pytest

from auteur.narrative_realization.schema import (
    Decision,
    EntryState,
    ExitState,
    Goal,
    Opposition,
    Outcome,
    SceneOutline,
    SceneStatus,
    TemporalRelation,
    Turn,
)
from auteur.narrative_realization.validator.temporal_validator import (
    TemporalValidator,
    TemporalViolation,
    TemporalViolationType,
)


def _ready_scene(
    scene_id: str,
    *,
    chapter_id: str = "chapter_01",
    position: int = 1,
    story_time: str = "day_1",
    pov: str = "clara",
    temporal_relation: TemporalRelation | None = None,
) -> SceneOutline:
    """Create a validation-ready scene without weakening SceneOutline semantics."""
    return SceneOutline(
        id=scene_id,
        chapter_id=chapter_id,
        status=SceneStatus.READY,
        narrative_position=position,
        story_time=story_time,
        pov_character_id=pov,
        participants=[pov],
        temporal_relation=temporal_relation,
        goal=Goal(actor_id=pov, objective="advance the scene goal"),
        opposition=Opposition(source_id="external", pressure="resist the goal"),
        turn=Turn(type="discovery", event="new evidence appears", impact="changes the situation"),
        decision=Decision(actor_id=pov, choice="act on the new evidence"),
        outcome=Outcome(result="partial"),
        entry_state=EntryState(),
        exit_state=ExitState(),
    )


class TestTemporalValidatorBasics:
    def test_validator_initialization(self):
        validator = TemporalValidator()
        assert validator.scenes == {}
        assert validator.violations == []

    def test_add_scene(self):
        validator = TemporalValidator()
        scene = SceneOutline(id="scene_01_01", chapter_id="chapter_01")
        validator.add_scene(scene)
        assert validator.scenes[scene.id] == scene

    def test_draft_scene_skipped(self):
        validator = TemporalValidator()
        scene = SceneOutline(id="scene_01_01", chapter_id="chapter_01")
        assert validator.validate_scene(scene).is_valid is True


class TestUniquePositions:
    def test_unique_positions_valid(self):
        validator = TemporalValidator()
        for i in range(1, 4):
            validator.add_scene(
                _ready_scene(
                    f"scene_01_0{i}", position=i, story_time=f"day_1_hour_{i}"
                )
            )

        result = validator.validate_all_scenes()
        assert result.is_valid is True
        assert result.violations == []

    def test_duplicate_positions_detected(self):
        validator = TemporalValidator()
        validator.add_scene(_ready_scene("scene_01_01", position=1))
        validator.add_scene(_ready_scene("scene_01_02", position=1))

        result = validator.validate_all_scenes()
        assert result.is_valid is False
        assert any(
            violation.violation_type == TemporalViolationType.DUPLICATE_POSITION
            for violation in result.violations
        )

    def test_different_chapters_allow_same_position(self):
        validator = TemporalValidator()
        validator.add_scene(
            _ready_scene("scene_01_01", chapter_id="chapter_01", position=1)
        )
        validator.add_scene(
            _ready_scene("scene_02_01", chapter_id="chapter_02", position=1)
        )

        result = validator.validate_all_scenes()
        assert not any(
            violation.violation_type == TemporalViolationType.DUPLICATE_POSITION
            for violation in result.violations
        )


class TestTemporalRelations:
    def test_valid_follows_scene(self):
        validator = TemporalValidator()
        first = _ready_scene("scene_01_01", position=1, story_time="day_1_morning")
        second = _ready_scene(
            "scene_01_02",
            position=2,
            story_time="day_1_afternoon",
            temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
        )
        validator.add_scene(first)
        validator.add_scene(second)

        assert validator.validate_scene(second).is_valid is True

    def test_invalid_follows_reference_detected(self):
        validator = TemporalValidator()
        scene = _ready_scene(
            "scene_01_01",
            temporal_relation=TemporalRelation(follows_scene="scene_01_99"),
        )
        validator.add_scene(scene)

        result = validator.validate_scene(scene)
        assert result.is_valid is False
        assert any(
            violation.violation_type == TemporalViolationType.INVALID_FOLLOWS_REFERENCE
            for violation in result.violations
        )

    def test_scene_model_rejects_self_follow(self):
        with pytest.raises(ValueError, match="cannot follow itself"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
            )


class TestParallelRelations:
    def test_valid_mutual_parallel(self):
        validator = TemporalValidator()
        validator.add_scene(
            _ready_scene(
                "scene_01_01",
                position=1,
                story_time="day_1_morning",
                temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
            )
        )
        validator.add_scene(
            _ready_scene(
                "scene_01_02",
                position=2,
                story_time="day_1_morning",
                pov="daniel",
                temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
            )
        )

        result = validator.validate_all_scenes()
        assert result.is_valid is True

    def test_non_mutual_parallel_detected(self):
        validator = TemporalValidator()
        validator.add_scene(
            _ready_scene(
                "scene_01_01",
                position=1,
                temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
            )
        )
        validator.add_scene(_ready_scene("scene_01_02", position=2, pov="daniel"))

        result = validator.validate_all_scenes()
        assert result.is_valid is False
        assert any(
            violation.violation_type == TemporalViolationType.NON_MUTUAL_PARALLEL
            for violation in result.violations
        )

    def test_scene_model_rejects_self_parallel(self):
        with pytest.raises(ValueError, match="cannot be parallel with itself"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
            )


class TestFollowsCycles:
    def test_mutual_parallel_is_not_a_cycle(self):
        validator = TemporalValidator()
        validator.add_scene(
            _ready_scene(
                "scene_01_01",
                position=1,
                temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
            )
        )
        validator.add_scene(
            _ready_scene(
                "scene_01_02",
                position=2,
                pov="daniel",
                temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
            )
        )

        result = validator.validate_all_scenes()
        assert not any(
            violation.violation_type == TemporalViolationType.CIRCULAR_PARALLEL
            for violation in result.violations
        )

    def test_circular_follows_chain_detected(self):
        validator = TemporalValidator()
        validator.add_scene(
            _ready_scene(
                "scene_01_01",
                position=1,
                temporal_relation=TemporalRelation(follows_scene="scene_01_03"),
            )
        )
        validator.add_scene(
            _ready_scene(
                "scene_01_02",
                position=2,
                temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
            )
        )
        validator.add_scene(
            _ready_scene(
                "scene_01_03",
                position=3,
                temporal_relation=TemporalRelation(follows_scene="scene_01_02"),
            )
        )

        result = validator.validate_all_scenes()
        assert result.is_valid is False
        assert any(
            violation.violation_type == TemporalViolationType.CIRCULAR_PARALLEL
            for violation in result.violations
        )


class TestPositionVsTime:
    def test_narrative_position_is_reading_order(self):
        validator = TemporalValidator()
        for i in range(1, 4):
            validator.add_scene(
                _ready_scene(
                    f"scene_01_0{i}", position=i, story_time=f"day_1_segment_{i}"
                )
            )

        result = validator.validate_all_scenes()
        assert not any(
            violation.violation_type == TemporalViolationType.DUPLICATE_POSITION
            for violation in result.violations
        )

    def test_story_time_allows_simultaneity(self):
        validator = TemporalValidator()
        validator.add_scene(
            _ready_scene(
                "scene_01_01",
                position=1,
                story_time="day_1_morning",
                temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
            )
        )
        validator.add_scene(
            _ready_scene(
                "scene_01_02",
                position=2,
                story_time="day_1_morning",
                pov="daniel",
                temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
            )
        )

        assert validator.validate_all_scenes().is_valid is True


class TestChronologicalConsistency:
    def test_follows_respects_position_order(self):
        validator = TemporalValidator()
        validator.add_scene(_ready_scene("scene_01_01", position=1))
        validator.add_scene(
            _ready_scene(
                "scene_01_02",
                position=2,
                temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
            )
        )

        assert validator.validate_all_scenes().is_valid is True

    def test_follows_rejects_reverse_position_order(self):
        validator = TemporalValidator()
        validator.add_scene(_ready_scene("scene_01_01", position=2))
        validator.add_scene(
            _ready_scene(
                "scene_01_02",
                position=1,
                temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
            )
        )

        result = validator.validate_all_scenes()
        assert result.is_valid is False
        assert any(
            violation.violation_type == TemporalViolationType.POSITION_AFTER_FOLLOWS
            for violation in result.violations
        )


class TestErrorReporting:
    def test_violation_report_no_errors(self):
        validator = TemporalValidator()
        assert "No temporal violations" in validator.report_temporal_violations([])

    def test_violation_report_includes_details(self):
        violation = TemporalViolation(
            scene_id="scene_01_01",
            violation_type=TemporalViolationType.DUPLICATE_POSITION,
            related_scene_id="scene_01_02",
            message="Duplicate position detected",
            suggestion="Change position",
        )
        report = TemporalValidator().report_temporal_violations([violation])
        assert "scene_01_01" in report
        assert "duplicate_position" in report
        assert "scene_01_02" in report
