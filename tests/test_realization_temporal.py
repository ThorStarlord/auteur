"""Active contract tests for Layer 3 temporal validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from auteur.narrative_realization.schema.scene_action import Decision, Goal, Opposition, Outcome, Turn
from auteur.narrative_realization.schema.scene_outline import SceneOutline, SceneStatus, TemporalRelation
from auteur.narrative_realization.schema.scene_state import EntryState, ExitState
from auteur.narrative_realization.validator.temporal_validator import (
    TemporalValidator,
    TemporalViolationType,
)


def _ready_scene(
    scene_id: str,
    position: int,
    *,
    chapter_id: str = "chapter_01",
    story_time: str | None = None,
    pov: str = "clara",
    temporal_relation: TemporalRelation | None = None,
) -> SceneOutline:
    return SceneOutline(
        id=scene_id,
        chapter_id=chapter_id,
        status=SceneStatus.READY,
        narrative_position=position,
        story_time=story_time or f"day_1_segment_{position}",
        pov_character_id=pov,
        participants=[pov],
        goal=Goal(actor_id=pov, objective="Advance the objective"),
        opposition=Opposition(source_id="external", pressure="Meaningful resistance"),
        turn=Turn(type="discovery", event="New information arrives", impact="The situation changes"),
        decision=Decision(actor_id=pov, choice="Continue"),
        outcome=Outcome(result="success"),
        entry_state=EntryState(),
        exit_state=ExitState(),
        temporal_relation=temporal_relation,
    )


def test_validator_initializes_empty() -> None:
    validator = TemporalValidator()
    assert validator.scenes == {}
    assert validator.violations == []


def test_draft_scene_is_skipped() -> None:
    scene = SceneOutline(id="scene_01_01", chapter_id="chapter_01", status=SceneStatus.DRAFT)
    result = TemporalValidator().validate_scene(scene)
    assert result.is_valid is True


def test_unique_positions_are_valid() -> None:
    validator = TemporalValidator()
    for position in range(1, 4):
        validator.add_scene(_ready_scene(f"scene_01_0{position}", position))
    result = validator.validate_all_scenes()
    assert result.is_valid is True


def test_duplicate_positions_in_same_chapter_are_rejected() -> None:
    validator = TemporalValidator()
    validator.add_scene(_ready_scene("scene_01_01", 1))
    validator.add_scene(_ready_scene("scene_01_02", 1))
    result = validator.validate_all_scenes()
    assert result.is_valid is False
    assert any(
        violation.violation_type == TemporalViolationType.DUPLICATE_POSITION
        for violation in result.violations
    )


def test_same_position_in_different_chapters_is_valid() -> None:
    validator = TemporalValidator()
    validator.add_scene(_ready_scene("scene_01_01", 1, chapter_id="chapter_01"))
    validator.add_scene(_ready_scene("scene_02_01", 1, chapter_id="chapter_02"))
    result = validator.validate_all_scenes()
    assert not any(
        violation.violation_type == TemporalViolationType.DUPLICATE_POSITION
        for violation in result.violations
    )


def test_valid_follows_reference_is_accepted() -> None:
    validator = TemporalValidator()
    first = _ready_scene("scene_01_01", 1)
    second = _ready_scene(
        "scene_01_02",
        2,
        temporal_relation=TemporalRelation(follows_scene=first.id),
    )
    validator.add_scene(first)
    validator.add_scene(second)
    assert validator.validate_all_scenes().is_valid is True


def test_missing_follows_reference_is_rejected() -> None:
    validator = TemporalValidator()
    scene = _ready_scene(
        "scene_01_01",
        1,
        temporal_relation=TemporalRelation(follows_scene="scene_01_99"),
    )
    validator.add_scene(scene)
    result = validator.validate_all_scenes()
    assert any(
        violation.violation_type == TemporalViolationType.INVALID_FOLLOWS_REFERENCE
        for violation in result.violations
    )


def test_scene_schema_rejects_self_follows_reference() -> None:
    with pytest.raises(ValidationError, match="Scene cannot follow itself"):
        _ready_scene(
            "scene_01_01",
            1,
            temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
        )


def test_mutual_parallel_relationship_is_valid() -> None:
    validator = TemporalValidator()
    first = _ready_scene(
        "scene_01_01",
        1,
        story_time="day_1_morning",
        temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
    )
    second = _ready_scene(
        "scene_01_02",
        2,
        story_time="day_1_morning",
        pov="daniel",
        temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
    )
    validator.add_scene(first)
    validator.add_scene(second)
    assert validator.validate_all_scenes().is_valid is True


def test_non_mutual_parallel_relationship_is_rejected() -> None:
    validator = TemporalValidator()
    first = _ready_scene(
        "scene_01_01",
        1,
        temporal_relation=TemporalRelation(parallel_with=["scene_01_02"]),
    )
    second = _ready_scene("scene_01_02", 2, pov="daniel")
    validator.add_scene(first)
    validator.add_scene(second)
    result = validator.validate_all_scenes()
    assert any(
        violation.violation_type == TemporalViolationType.NON_MUTUAL_PARALLEL
        for violation in result.violations
    )


def test_scene_schema_rejects_self_parallel_reference() -> None:
    with pytest.raises(ValidationError, match="Scene cannot be parallel with itself"):
        _ready_scene(
            "scene_01_01",
            1,
            temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
        )


def test_circular_follows_chain_is_rejected() -> None:
    validator = TemporalValidator()
    first = _ready_scene(
        "scene_01_01",
        1,
        temporal_relation=TemporalRelation(follows_scene="scene_01_02"),
    )
    second = _ready_scene(
        "scene_01_02",
        2,
        temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
    )
    validator.add_scene(first)
    validator.add_scene(second)
    result = validator.validate_all_scenes()
    assert any(
        violation.violation_type == TemporalViolationType.CIRCULAR_PARALLEL
        for violation in result.violations
    )


def test_story_time_may_be_shared_when_reading_positions_are_distinct() -> None:
    validator = TemporalValidator()
    validator.add_scene(_ready_scene("scene_01_01", 1, story_time="day_1_morning"))
    validator.add_scene(_ready_scene("scene_01_02", 2, story_time="day_1_morning", pov="daniel"))
    result = validator.validate_all_scenes()
    assert not any(
        violation.violation_type == TemporalViolationType.DUPLICATE_POSITION
        for violation in result.violations
    )


def test_chronological_consistency_rejects_backward_follows_position() -> None:
    validator = TemporalValidator()
    first = _ready_scene("scene_01_01", 2)
    second = _ready_scene(
        "scene_01_02",
        1,
        temporal_relation=TemporalRelation(follows_scene=first.id),
    )
    validator.add_scene(first)
    validator.add_scene(second)
    violations = validator.validate_chronological_consistency()
    assert any(
        violation.violation_type == TemporalViolationType.POSITION_AFTER_FOLLOWS
        for violation in violations
    )
