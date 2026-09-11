"""Tests for Layer 3 knowledge validation under the current SceneOutline contract."""

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


def _fact(what: str, *, source: str = "chapter_position") -> KnowledgeFact:
    return KnowledgeFact(
        what=what,
        how_known="perceived" if source == "chapter_position" else "external_source",
        degree="certain",
        source=source,
    )


def _ready_scene(
    scene_id: str,
    *,
    position: int,
    pov: str = "clara",
    entry_knowledge: list[KnowledgeFact] | None = None,
    exit_knowledge: list[KnowledgeFact] | None = None,
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
        turn=Turn(type="discovery", event="new evidence appears", impact="changes the situation"),
        decision=Decision(actor_id=pov, choice="act on the evidence"),
        outcome=Outcome(result="partial"),
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

    def test_draft_scene_skipped(self):
        validator = KnowledgeValidator()
        scene = SceneOutline(id="scene_01_01", chapter_id="chapter_01")
        result = validator.validate_scene(scene)
        assert result.is_valid is True
        assert result.violations == []


class TestKnowledgeConsistency:
    def test_ready_scene_with_empty_knowledge_is_valid(self):
        validator = KnowledgeValidator()
        scene = _ready_scene("scene_01_01", position=1)
        assert validator.validate_scene(scene).is_valid is True

    def test_entry_knowledge_preserved_in_exit_is_valid(self):
        secret = _fact("The victim was poisoned")
        validator = KnowledgeValidator()
        scene = _ready_scene(
            "scene_01_01",
            position=1,
            entry_knowledge=[secret],
            exit_knowledge=[secret],
        )
        assert validator.validate_scene(scene).is_valid is True

    def test_entry_knowledge_cannot_silently_disappear(self):
        secret = _fact("The victim was poisoned")
        validator = KnowledgeValidator()
        scene = _ready_scene(
            "scene_01_01",
            position=1,
            entry_knowledge=[secret],
            exit_knowledge=[],
        )

        result = validator.validate_scene(scene)
        assert result.is_valid is False
        assert any(
            violation.violation_type == KnowledgeViolationType.INCONSISTENT_ENTRY_EXIT
            and violation.fact_what == secret.what
            for violation in result.violations
        )


class TestCrossSceneKnowledge:
    def test_same_pov_keeps_prior_exit_knowledge(self):
        secret = _fact("The ledger exists")
        validator = KnowledgeValidator()
        validator.add_scene(
            _ready_scene(
                "scene_01_01",
                position=1,
                exit_knowledge=[secret],
            )
        )
        validator.add_scene(
            _ready_scene(
                "scene_01_02",
                position=2,
                entry_knowledge=[secret],
                exit_knowledge=[secret],
            )
        )

        assert validator.validate_all_scenes().is_valid is True

    def test_same_pov_rejects_retroactive_forgetting(self):
        secret = _fact("The ledger exists")
        validator = KnowledgeValidator()
        validator.add_scene(
            _ready_scene(
                "scene_01_01",
                position=1,
                exit_knowledge=[secret],
            )
        )
        validator.add_scene(
            _ready_scene(
                "scene_01_02",
                position=2,
                entry_knowledge=[],
                exit_knowledge=[],
            )
        )

        result = validator.validate_all_scenes()
        assert result.is_valid is False
        assert any(
            violation.violation_type == KnowledgeViolationType.RETROACTIVE_FORGETTING
            and violation.fact_what == secret.what
            for violation in result.violations
        )

    def test_different_pov_does_not_inherit_private_knowledge(self):
        secret = _fact("Clara knows the ledger exists")
        validator = KnowledgeValidator()
        validator.add_scene(
            _ready_scene(
                "scene_01_01",
                position=1,
                pov="clara",
                exit_knowledge=[secret],
            )
        )
        validator.add_scene(
            _ready_scene(
                "scene_01_02",
                position=2,
                pov="daniel",
                entry_knowledge=[],
                exit_knowledge=[],
            )
        )

        assert validator.validate_all_scenes().is_valid is True

    def test_validation_is_repeatable(self):
        secret = _fact("The ledger exists")
        validator = KnowledgeValidator()
        validator.add_scene(
            _ready_scene("scene_01_01", position=1, exit_knowledge=[secret])
        )
        validator.add_scene(
            _ready_scene("scene_01_02", position=2, entry_knowledge=[], exit_knowledge=[])
        )

        first = validator.validate_all_scenes()
        second = validator.validate_all_scenes()
        assert first == second


class TestSupportedKnowledgeSources:
    def test_message_like_external_source_is_preserved(self):
        message_fact = _fact("The train is delayed", source="character_id")
        scene = _ready_scene(
            "scene_01_01",
            position=1,
            entry_knowledge=[message_fact],
            exit_knowledge=[message_fact],
        )
        assert scene.entry_state is not None
        assert scene.entry_state.knowledge[0].source == "character_id"
        assert KnowledgeValidator().validate_scene(scene).is_valid is True

    def test_document_source_is_preserved(self):
        document_fact = _fact("The will names a second heir", source="document")
        scene = _ready_scene(
            "scene_01_01",
            position=1,
            entry_knowledge=[document_fact],
            exit_knowledge=[document_fact],
        )
        assert scene.entry_state is not None
        assert scene.entry_state.knowledge[0].source == "document"
        assert KnowledgeValidator().validate_scene(scene).is_valid is True


class TestEmptyAndMultipleSceneValidation:
    def test_validate_all_scenes_empty(self):
        result = KnowledgeValidator().validate_all_scenes()
        assert result.is_valid is True
        assert result.violations == []

    def test_validate_all_scenes_multiple_valid_scenes(self):
        validator = KnowledgeValidator()
        for i in range(1, 4):
            validator.add_scene(_ready_scene(f"scene_01_0{i}", position=i))

        result = validator.validate_all_scenes()
        assert result.is_valid is True
        assert result.violations == []


class TestErrorReporting:
    def test_violation_report_no_errors(self):
        report = KnowledgeValidator().report_knowledge_violations([])
        assert "No knowledge violations" in report

    def test_violation_report_format(self):
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


class TestKnowledgeStateModels:
    def test_knowledge_fact_creation(self):
        fact = _fact("The victim was poisoned")
        assert fact.what == "The victim was poisoned"
        assert fact.degree == "certain"

    def test_emotional_state_creation(self):
        emotion = EmotionalState(
            state="suspicious",
            intensity="high",
            rationale="Character suspects deception",
        )
        assert emotion.state == "suspicious"
        assert emotion.intensity == "high"

    def test_entry_state_creation(self):
        fact = _fact("Basic fact")
        entry = EntryState(knowledge=[fact])
        assert entry.knowledge == [fact]

    def test_exit_state_creation(self):
        facts = [_fact("Original fact"), _fact("Learned fact", source="inference")]
        exit_state = ExitState(knowledge=facts)
        assert exit_state.knowledge == facts
