"""Active contract tests for Layer 3 knowledge validation."""

from __future__ import annotations

from auteur.narrative_realization.schema.scene_action import Decision, Goal, Opposition, Outcome, Turn
from auteur.narrative_realization.schema.scene_outline import SceneOutline, SceneStatus
from auteur.narrative_realization.schema.scene_state import EntryState, ExitState, KnowledgeFact
from auteur.narrative_realization.validator.knowledge_validator import (
    KnowledgeValidator,
    KnowledgeViolation,
    KnowledgeViolationType,
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
    chapter_id: str = "chapter_01",
    entry: list[KnowledgeFact] | None = None,
    exit: list[KnowledgeFact] | None = None,
    learned: list[str] | None = None,
) -> SceneOutline:
    return SceneOutline(
        id=scene_id,
        chapter_id=chapter_id,
        status=SceneStatus.READY,
        narrative_position=position,
        story_time=f"day_1_segment_{position}",
        pov_character_id=pov,
        participants=[pov],
        goal=Goal(actor_id=pov, objective="Advance the objective"),
        opposition=Opposition(source_id="external", pressure="Meaningful resistance"),
        turn=Turn(type="discovery", event="New information arrives", impact="The situation changes"),
        decision=Decision(actor_id=pov, choice="Continue"),
        outcome=Outcome(result="success", knowledge_added=list(learned or [])),
        entry_state=EntryState(knowledge=list(entry or [])),
        exit_state=ExitState(knowledge=list(exit or [])),
    )


def test_validator_initializes_empty() -> None:
    validator = KnowledgeValidator()
    assert validator.scenes == {}
    assert validator.violations == []


def test_draft_scene_is_skipped() -> None:
    scene = SceneOutline(id="scene_01_01", chapter_id="chapter_01", status=SceneStatus.DRAFT)
    result = KnowledgeValidator().validate_scene(scene)
    assert result.is_valid is True
    assert result.violations == []


def test_ready_scene_with_empty_states_is_valid() -> None:
    scene = _ready_scene("scene_01_01", 1)
    result = KnowledgeValidator().validate_scene(scene)
    assert result.is_valid is True


def test_local_entry_exit_paraphrase_is_not_rejected_without_fact_ids() -> None:
    scene = _ready_scene(
        "scene_01_01",
        1,
        entry=[_fact("Daniel is aware she is investigating the archive")],
        exit=[_fact("Daniel is aware she is investigating")],
    )
    result = KnowledgeValidator().validate_scene(scene)
    assert result.is_valid is True


def test_outcome_learning_summary_is_not_treated_as_knowledge_identity() -> None:
    structured = _fact("The archive door is trapped")
    scene = _ready_scene(
        "scene_01_01",
        1,
        learned=["door trap discovered"],
        exit=[structured],
    )
    result = KnowledgeValidator().validate_scene(scene)
    assert result.is_valid is True


def test_same_pov_cannot_forget_prior_exit_knowledge() -> None:
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
        and violation.scene_id == second.id
        and violation.fact_what == known.what
        for violation in result.violations
    )


def test_same_pov_preserving_prior_exit_knowledge_is_valid() -> None:
    known = _fact("The archive door is trapped")
    first = _ready_scene("scene_01_01", 1, exit=[known])
    second = _ready_scene("scene_01_02", 2, entry=[known], exit=[known])
    validator = KnowledgeValidator()
    validator.add_scene(first)
    validator.add_scene(second)
    result = validator.validate_all_scenes()
    assert result.is_valid is True


def test_fact_comparison_normalizes_case_and_whitespace() -> None:
    first = _ready_scene("scene_01_01", 1, exit=[_fact("The archive door is trapped")])
    second = _ready_scene("scene_01_02", 2, entry=[_fact("  the ARCHIVE door is trapped  ")])
    validator = KnowledgeValidator()
    validator.add_scene(first)
    validator.add_scene(second)
    result = validator.validate_all_scenes()
    assert result.is_valid is True


def test_different_pov_does_not_inherit_other_characters_knowledge() -> None:
    known = _fact("The archive door is trapped")
    first = _ready_scene("scene_01_01", 1, pov="clara", exit=[known])
    second = _ready_scene("scene_01_02", 2, pov="daniel", entry=[])
    validator = KnowledgeValidator()
    validator.add_scene(first)
    validator.add_scene(second)
    result = validator.validate_all_scenes()
    assert not any(
        violation.violation_type == KnowledgeViolationType.RETROACTIVE_FORGETTING
        for violation in result.violations
    )


def test_same_pov_different_chapter_does_not_require_direct_carryover() -> None:
    known = _fact("The archive door is trapped")
    first = _ready_scene("scene_01_01", 1, chapter_id="chapter_01", exit=[known])
    second = _ready_scene("scene_02_01", 1, chapter_id="chapter_02", entry=[])
    validator = KnowledgeValidator()
    validator.add_scene(first)
    validator.add_scene(second)
    result = validator.validate_all_scenes()
    assert result.is_valid is True


def test_violation_report_contains_actionable_fields() -> None:
    violation = KnowledgeViolation(
        scene_id="scene_01_02",
        violation_type=KnowledgeViolationType.RETROACTIVE_FORGETTING,
        character_id="clara",
        fact_what="The archive door is trapped",
        message="Knowledge disappeared",
        suggestion="Carry the fact into entry state",
    )
    report = KnowledgeValidator().report_knowledge_violations([violation])
    assert "scene_01_02" in report
    assert "retroactive_forgetting" in report
    assert "clara" in report
    assert "Carry the fact" in report
