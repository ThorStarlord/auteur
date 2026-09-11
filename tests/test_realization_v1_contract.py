from __future__ import annotations

import pytest
from pydantic import ValidationError

from auteur.narrative_realization.orchestrator.scene_inspector import SceneInspector
from auteur.narrative_realization.schema.scene_action import (
    ArcBeatRealization,
    Decision,
    Goal,
    Opposition,
    Outcome,
    Turn,
)
from auteur.narrative_realization.schema.scene_outline import (
    SceneOutline,
    SceneStatus,
)
from auteur.narrative_realization.schema.scene_state import (
    EntryState,
    ExitState,
    KnowledgeFact,
)
from auteur.narrative_realization.validator.knowledge_validator import (
    KnowledgeValidator,
    KnowledgeViolationType,
)
from auteur.narrative_realization.validator.temporal_validator import (
    TemporalValidator,
    TemporalViolationType,
)


def _fact(what: str) -> KnowledgeFact:
    return KnowledgeFact(
        what=what,
        how_known="learned",
        degree="certain",
        source="chapter_position",
    )


def _ready_scene(
    scene_id: str,
    position: int,
    *,
    pov: str = "clara",
    entry: list[KnowledgeFact] | None = None,
    exit: list[KnowledgeFact] | None = None,
) -> SceneOutline:
    return SceneOutline(
        id=scene_id,
        chapter_id="chapter_01",
        status=SceneStatus.READY,
        narrative_position=position,
        story_time=f"day_1_segment_{position}",
        pov_character_id=pov,
        participants=[pov],
        goal=Goal(actor_id=pov, objective="Advance the scene objective"),
        opposition=Opposition(source_id="external", pressure="Meaningful resistance"),
        turn=Turn(type="discovery", event="New information arrives", impact="The situation changes"),
        decision=Decision(actor_id=pov, choice="Continue despite the cost"),
        outcome=Outcome(result="success"),
        entry_state=EntryState(knowledge=list(entry or [])),
        exit_state=ExitState(knowledge=list(exit or [])),
    )


def test_inspector_reads_canonical_realizes_arc_beats_field() -> None:
    scene = SceneOutline(
        id="scene_01_01",
        chapter_id="chapter_01",
        realizes_arc_beats=[ArcBeatRealization(beat_id="beat_01", degree="full")],
        status=SceneStatus.DRAFT,
    )
    inspector = SceneInspector()
    inspector.add_scene(scene)

    report = inspector.show_arc_beat_coverage()

    assert "beat_01" in report
    assert "1 scene" in report


def test_knowledge_continuity_rejects_missing_prior_fact() -> None:
    known = _fact("The archive door is trapped")
    first = _ready_scene("scene_01_01", 1, exit=[known])
    second = _ready_scene("scene_01_02", 2, entry=[])
    validator = KnowledgeValidator()
    validator.add_scene(first)
    validator.add_scene(second)

    result = validator.validate_all_scenes()

    assert result.is_valid is False
    assert any(
        violation.violation_type == KnowledgeViolationType.RETROACTIVE_FORGETTING
        and violation.scene_id == "scene_01_02"
        and violation.fact_what == known.what
        for violation in result.violations
    )


def test_knowledge_continuity_accepts_preserved_prior_fact() -> None:
    known = _fact("The archive door is trapped")
    first = _ready_scene("scene_01_01", 1, exit=[known])
    second = _ready_scene("scene_01_02", 2, entry=[known], exit=[known])
    validator = KnowledgeValidator()
    validator.add_scene(first)
    validator.add_scene(second)

    result = validator.validate_all_scenes()

    assert not any(
        violation.violation_type == KnowledgeViolationType.RETROACTIVE_FORGETTING
        for violation in result.violations
    )


def test_incomplete_scene_rejects_missing_dramatic_contract() -> None:
    with pytest.raises(ValidationError, match="goal is required"):
        SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.INCOMPLETE,
            narrative_position=1,
            pov_character_id="clara",
            participants=["clara"],
        )


def test_temporal_duplicate_position_is_detected_with_contract_valid_scenes() -> None:
    first = _ready_scene("scene_01_01", 1)
    second = _ready_scene("scene_01_02", 1)
    validator = TemporalValidator()
    validator.add_scene(first)
    validator.add_scene(second)

    result = validator.validate_all_scenes()

    assert result.is_valid is False
    assert any(
        violation.violation_type == TemporalViolationType.DUPLICATE_POSITION
        for violation in result.violations
    )
