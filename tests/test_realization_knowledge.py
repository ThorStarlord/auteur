"""Tests for the current Layer 3 knowledge-state and validator boundary.

The Scene state schema represents authored knowledge facts, acquisition source,
certainty, entry state, exit state, and outcome knowledge changes. The current
KnowledgeValidator intentionally does not infer richer contradiction,
communication, or omniscience semantics that are not structurally represented.
"""

from __future__ import annotations

import pytest

from auteur.narrative_realization.schema import (
    Decision,
    EmotionalState,
    EntryState,
    ExitState,
    Goal,
    KnowledgeFact,
    Opposition,
    Outcome,
    SceneOutline,
    SceneStatus,
    Turn,
)
from auteur.narrative_realization.validator.knowledge_validator import (
    KnowledgeValidator,
    KnowledgeViolation,
    KnowledgeViolationType,
)


def _fact(
    what: str,
    *,
    how_known: str = "perceived",
    degree: str = "certain",
    source: str = "chapter_position",
) -> KnowledgeFact:
    return KnowledgeFact(
        what=what,
        how_known=how_known,
        degree=degree,
        source=source,
    )


def _ready_scene(
    scene_id: str,
    *,
    position: int,
    pov: str = "clara",
    entry_knowledge: list[KnowledgeFact] | None = None,
    exit_knowledge: list[KnowledgeFact] | None = None,
    knowledge_added: list[str] | None = None,
    knowledge_questioned: list[str] | None = None,
) -> SceneOutline:
    return SceneOutline(
        id=scene_id,
        chapter_id="chapter_01",
        status=SceneStatus.READY,
        narrative_position=position,
        story_time=f"day_1_segment_{position}",
        pov_character_id=pov,
        participants=[pov],
        goal=Goal(actor_id=pov, objective="advance the scene goal"),
        opposition=Opposition(source_id="external", pressure="resist the goal"),
        turn=Turn(
            type="discovery",
            event="new evidence appears",
            impact="changes the situation",
        ),
        decision=Decision(actor_id=pov, choice="act on the evidence"),
        outcome=Outcome(
            result="partial",
            knowledge_added=knowledge_added or [],
            knowledge_questioned=knowledge_questioned or [],
        ),
        entry_state=EntryState(knowledge=entry_knowledge or []),
        exit_state=ExitState(knowledge=exit_knowledge or []),
    )


class TestKnowledgeValidatorBasics:
    def test_validator_initialization(self):
        validator = KnowledgeValidator()
        assert validator.scenes == {}
        assert validator.violations == []

    def test_add_scene(self):
        validator = KnowledgeValidator()
        scene = SceneOutline(id="scene_01_01", chapter_id="chapter_01")
        validator.add_scene(scene)
        assert validator.scenes[scene.id] == scene

    def test_draft_scene_is_valid_without_full_state(self):
        validator = KnowledgeValidator()
        scene = SceneOutline(id="scene_01_01", chapter_id="chapter_01")

        result = validator.validate_scene(scene)

        assert result.is_valid is True
        assert result.violations == []
        assert result.warnings == []


class TestKnowledgeStateRepresentation:
    def test_ready_scene_carries_entry_outcome_and_exit_knowledge(self):
        prior = _fact("Daniel claims he was at the archive")
        learned = _fact(
            "Archive access record was altered",
            how_known="external_source",
            source="document",
        )
        scene = _ready_scene(
            "scene_01_01",
            position=1,
            entry_knowledge=[prior],
            exit_knowledge=[prior, learned],
            knowledge_added=[learned.what],
            knowledge_questioned=[prior.what],
        )

        assert scene.entry_state is not None
        assert scene.exit_state is not None
        assert scene.outcome is not None
        assert scene.entry_state.knowledge == [prior]
        assert scene.exit_state.knowledge == [prior, learned]
        assert scene.outcome.knowledge_added == [learned.what]
        assert scene.outcome.knowledge_questioned == [prior.what]

    @pytest.mark.parametrize(
        ("how_known", "source"),
        [
            ("learned", "chapter_position"),
            ("external_source", "character_id"),
            ("external_source", "document"),
            ("inferred", "inference"),
        ],
    )
    def test_supported_knowledge_origins_round_trip(self, how_known, source):
        fact = _fact(
            "A traceable fact",
            how_known=how_known,
            degree="probable",
            source=source,
        )
        state = ExitState(knowledge=[fact])

        assert state.knowledge[0].how_known == how_known
        assert state.knowledge[0].source == source
        assert state.knowledge[0].degree == "probable"

    def test_blank_knowledge_fact_is_rejected(self):
        with pytest.raises(ValueError, match="what"):
            _fact("   ")

    def test_invalid_knowledge_mechanism_is_rejected(self):
        with pytest.raises(ValueError):
            _fact("A fact", how_known="telepathy")

    def test_emotional_state_remains_semantic_not_numeric(self):
        emotion = EmotionalState(
            state="suspicious",
            intensity="high",
            rationale="Evidence contradicts the alibi",
        )
        assert emotion.state == "suspicious"
        assert emotion.intensity == "high"


class TestKnowledgeValidatorCurrentBoundary:
    def test_complete_ready_scene_validates_without_false_positive(self):
        known = _fact("The victim was found at midnight")
        scene = _ready_scene(
            "scene_01_01",
            position=1,
            entry_knowledge=[known],
            exit_knowledge=[known],
        )

        result = KnowledgeValidator().validate_scene(scene)

        assert result.is_valid is True
        assert result.violations == []

    def test_validator_does_not_infer_unmodeled_cross_character_knowledge(self):
        clara_fact = _fact("Clara saw the altered record")
        clara = _ready_scene(
            "scene_01_01",
            position=1,
            pov="clara",
            exit_knowledge=[clara_fact],
        )
        daniel = _ready_scene(
            "scene_01_02",
            position=2,
            pov="daniel",
            entry_knowledge=[],
            exit_knowledge=[],
        )
        validator = KnowledgeValidator()
        validator.add_scene(clara)
        validator.add_scene(daniel)

        result = validator.validate_all_scenes()

        assert result.is_valid is True
        assert not any(
            violation.violation_type == KnowledgeViolationType.IMPOSSIBLE_OMNISCIENCE
            for violation in result.violations
        )

    def test_validate_all_scenes_is_repeatable_for_same_registered_state(self):
        validator = KnowledgeValidator()
        validator.add_scene(_ready_scene("scene_01_01", position=1))
        validator.add_scene(_ready_scene("scene_01_02", position=2))

        first = validator.validate_all_scenes()
        second = validator.validate_all_scenes()

        assert first == second

    def test_validate_all_scenes_empty(self):
        result = KnowledgeValidator().validate_all_scenes()
        assert result.is_valid is True
        assert result.violations == []


class TestKnowledgeReporting:
    def test_violation_report_no_errors(self):
        report = KnowledgeValidator().report_knowledge_violations([])
        assert "No knowledge violations" in report

    def test_violation_report_includes_structured_fields(self):
        violation = KnowledgeViolation(
            scene_id="scene_01_01",
            violation_type=KnowledgeViolationType.RETROACTIVE_FORGETTING,
            character_id="clara",
            fact_what="secret_revealed",
            message="Clara forgets previously established knowledge",
            suggestion="Restore the fact to entry knowledge",
        )

        report = KnowledgeValidator().report_knowledge_violations([violation])

        assert "scene_01_01" in report
        assert "retroactive_forgetting" in report
        assert "clara" in report
        assert "secret_revealed" in report
