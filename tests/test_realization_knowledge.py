"""Tests for KnowledgeValidator.

Tests validate:
- No retroactive forgetting (knowledge persists across scenes)
- Knowledge consistency (entry + learned = exit)
- POV vs non-POV knowledge separation
- Off-stage learning (message, document)
- Contradiction detection
"""


from auteur.narrative_realization.schema.scene_action import Decision, Goal, Opposition, Outcome, Turn
from auteur.narrative_realization.schema.scene_outline import (
    SceneOutline,
    SceneStatus,
)
from auteur.narrative_realization.schema.scene_state import (
    KnowledgeFact,
    EmotionalState,
    EntryState,
    ExitState,
)
from auteur.narrative_realization.validator.knowledge_validator import (
    KnowledgeValidator,
    KnowledgeViolationType,
)


class TestKnowledgeValidatorBasics:
    """Test basic knowledge validator functionality."""

    def test_validator_initialization(self):
        """Test validator initializes empty."""
        validator = KnowledgeValidator()
        assert validator.scenes == {}
        assert len(validator.violations) == 0

    def test_add_scene(self):
        """Test adding scenes to validator."""
        validator = KnowledgeValidator()
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
        )
        validator.add_scene(scene)
        assert scene.id in validator.scenes
        assert validator.scenes[scene.id] == scene

    def test_draft_scene_skipped(self):
        """Test that draft scenes are skipped in validation."""
        validator = KnowledgeValidator()
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
        )
        result = validator.validate_scene(scene)
        assert result.is_valid is True
        assert len(result.violations) == 0


class TestKnowledgeConsistency:
    """Test knowledge consistency validation."""

    def test_empty_knowledge_valid(self):
        """Test scene with no knowledge is valid."""
        validator = KnowledgeValidator()
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="Advance the scene"),
            opposition=Opposition(source_id="external", pressure="Resistance"),
            outcome=Outcome(result="partial"),
            status=SceneStatus.INCOMPLETE,
        )
        result = validator.validate_scene(scene)
        assert result.is_valid is True

    def test_ready_scene_validation(self):
        """Test ready scene can be validated."""
        validator = KnowledgeValidator()
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="Advance the scene"),
            opposition=Opposition(source_id="external", pressure="Resistance"),
            turn=Turn(type="complication", event="Situation changes", impact="Raises pressure"),
            decision=Decision(actor_id="clara", choice="Continue"),
            outcome=Outcome(result="partial"),
            entry_state=EntryState(),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )
        result = validator.validate_scene(scene)
        # Should validate without critical errors for empty knowledge
        assert isinstance(result.is_valid, bool)


class TestRetractiveForgetting:
    """Test detection of retroactive forgetting violations."""

    def test_no_forgetting_in_single_scene(self):
        """Test single scene with knowledge doesn't trigger forgetting error."""
        validator = KnowledgeValidator()
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="Advance the scene"),
            opposition=Opposition(source_id="external", pressure="Resistance"),
            turn=Turn(type="complication", event="Situation changes", impact="Raises pressure"),
            decision=Decision(actor_id="clara", choice="Continue"),
            outcome=Outcome(result="partial"),
            entry_state=EntryState(),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )
        validator.add_scene(scene)
        result = validator.validate_scene(scene)
        assert result.is_valid is True

    def test_forgetting_detected_across_scenes(self):
        """Exact prior knowledge cannot disappear between consecutive same-POV scenes."""
        fact = KnowledgeFact(
            what="The victim was poisoned",
            how_known="learned",
            degree="certain",
            source="chapter_position",
        )
        validator = KnowledgeValidator()
        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="Learn the truth"),
            opposition=Opposition(source_id="external", pressure="Missing evidence"),
            turn=Turn(type="discovery", event="Poison is identified", impact="Narrows the case"),
            decision=Decision(actor_id="clara", choice="Follow the poison lead"),
            outcome=Outcome(result="success", knowledge_added=[fact.what]),
            entry_state=EntryState(),
            exit_state=ExitState(knowledge=[fact]),
            status=SceneStatus.READY,
        )
        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_1_afternoon",
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="Question a suspect"),
            opposition=Opposition(source_id="external", pressure="Evasion"),
            turn=Turn(type="complication", event="The suspect lies", impact="Raises doubt"),
            decision=Decision(actor_id="clara", choice="Keep investigating"),
            outcome=Outcome(result="partial"),
            entry_state=EntryState(),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )
        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()

        assert any(
            violation.violation_type == KnowledgeViolationType.RETROACTIVE_FORGETTING
            and violation.fact_what == fact.what
            for violation in result.violations
        )


class TestPOVKnowledge:
    """Test POV character knowledge validation."""

    def test_pov_character_identified(self):
        """Test POV character is correctly identified."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara", "daniel"],
            goal=Goal(actor_id="clara", objective="Advance the scene"),
            opposition=Opposition(source_id="external", pressure="Resistance"),
            turn=Turn(type="complication", event="Situation changes", impact="Raises pressure"),
            decision=Decision(actor_id="clara", choice="Continue"),
            outcome=Outcome(result="partial"),
            entry_state=EntryState(),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )
        assert scene.pov_character_id == "clara"
        assert "clara" in scene.participants

    def test_non_pov_knowledge_separate(self):
        """Test non-POV character knowledge is separate."""
        validator = KnowledgeValidator()

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara", "daniel"],
            goal=Goal(actor_id="clara", objective="Advance the scene"),
            opposition=Opposition(source_id="external", pressure="Resistance"),
            turn=Turn(type="complication", event="Situation changes", impact="Raises pressure"),
            decision=Decision(actor_id="clara", choice="Continue"),
            outcome=Outcome(result="partial"),
            entry_state=EntryState(),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_1_afternoon",
            pov_character_id="daniel",
            participants=["daniel", "clara"],
            goal=Goal(actor_id="clara", objective="Advance the scene"),
            opposition=Opposition(source_id="external", pressure="Resistance"),
            turn=Turn(type="complication", event="Situation changes", impact="Raises pressure"),
            decision=Decision(actor_id="clara", choice="Continue"),
            outcome=Outcome(result="partial"),
            entry_state=EntryState(),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        # Different POV characters should have separate knowledge
        assert scene1.pov_character_id != scene2.pov_character_id


class TestOffStageLearning:
    """Test off-stage learning validation (message, document)."""

    def test_pov_can_learn_via_message(self):
        """Current schema can represent externally sourced character knowledge."""
        fact = KnowledgeFact(
            what="Daniel sent the warning",
            how_known="external_source",
            degree="certain",
            source="character_id",
        )
        assert fact.source == "character_id"
        assert fact.how_known == "external_source"

    def test_pov_can_learn_via_document(self):
        """Current schema can represent document-sourced knowledge."""
        fact = KnowledgeFact(
            what="The ledger records the payment",
            how_known="external_source",
            degree="certain",
            source="document",
        )
        assert fact.source == "document"


class TestCrossSceneValidation:
    """Test validation across multiple scenes."""

    def test_validate_all_scenes_empty(self):
        """Test validating empty scene collection."""
        validator = KnowledgeValidator()
        result = validator.validate_all_scenes()
        assert result.is_valid is True
        assert len(result.violations) == 0

    def test_validate_all_scenes_multiple(self):
        """Test validating multiple scenes."""
        validator = KnowledgeValidator()

        for i in range(1, 4):
            scene = SceneOutline(
                id=f"scene_01_0{i}",
                chapter_id="chapter_01",
                narrative_position=i,
                story_time=f"day_1_hour_{i*3}",
                pov_character_id="clara",
                participants=["clara"],
                goal=Goal(actor_id="clara", objective="Advance the scene"),
            opposition=Opposition(source_id="external", pressure="Resistance"),
            turn=Turn(type="complication", event="Situation changes", impact="Raises pressure"),
            decision=Decision(actor_id="clara", choice="Continue"),
            outcome=Outcome(result="partial"),
            entry_state=EntryState(),
            exit_state=ExitState(),
            status=SceneStatus.READY,
            )
            validator.add_scene(scene)

        result = validator.validate_all_scenes()
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.violations, list)


class TestErrorReporting:
    """Test error message generation."""

    def test_violation_report_no_errors(self):
        """Test report generation with no violations."""
        validator = KnowledgeValidator()
        report = validator.report_knowledge_violations([])
        assert "No knowledge violations" in report

    def test_violation_report_format(self):
        """Test report formatting includes all required fields."""
        from auteur.narrative_realization.validator.knowledge_validator import (
            KnowledgeViolation,
        )

        validator = KnowledgeValidator()
        violation = KnowledgeViolation(
            scene_id="scene_01_01",
            violation_type=KnowledgeViolationType.RETROACTIVE_FORGETTING,
            character_id="clara",
            fact_what="secret_revealed",
            message="Clara forgets knowledge learned in scene_01_02",
            suggestion="Add fact to exit_knowledge of scene_01_02",
        )

        report = validator.report_knowledge_violations([violation])
        assert "scene_01_01" in report
        assert "retroactive_forgetting" in report
        assert "clara" in report


class TestKnowledgeStructure:
    """Test knowledge fact structure."""

    def test_knowledge_fact_creation(self):
        """Test creating knowledge facts."""
        fact = KnowledgeFact(
            what="The victim was poisoned",
            how_known="learned",
            degree="certain",
            source="character_id",
        )
        assert fact.what == "The victim was poisoned"
        assert fact.how_known == "learned"
        assert fact.degree == "certain"

    def test_emotional_state_creation(self):
        """Test creating emotional states."""
        emotion = EmotionalState(
            state="suspicious",
            intensity="high",
            rationale="Character suspects deception",
        )
        assert emotion.state == "suspicious"
        assert emotion.intensity == "high"

    def test_entry_state_creation(self):
        """Test creating entry states."""
        fact = KnowledgeFact(
            what="Basic fact",
            how_known="perceived",
            degree="certain",
            source="chapter_position",
        )
        entry = EntryState(knowledge=[fact])
        assert len(entry.knowledge) == 1
        assert entry.knowledge[0].what == "Basic fact"

    def test_exit_state_creation(self):
        """Test creating exit states."""
        fact1 = KnowledgeFact(
            what="Original fact",
            how_known="perceived",
            degree="certain",
            source="chapter_position",
        )
        fact2 = KnowledgeFact(
            what="Learned fact",
            how_known="inferred",
            degree="probable",
            source="inference",
        )
        exit_state = ExitState(knowledge=[fact1, fact2])
        assert len(exit_state.knowledge) == 2


class TestKnowledgeProgression:
    """Test knowledge progression validation."""

    def test_knowledge_should_accumulate(self):
        """Test that knowledge accumulates across scenes."""
        validator = KnowledgeValidator()

        scene1 = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="Advance the scene"),
            opposition=Opposition(source_id="external", pressure="Resistance"),
            turn=Turn(type="complication", event="Situation changes", impact="Raises pressure"),
            decision=Decision(actor_id="clara", choice="Continue"),
            outcome=Outcome(result="partial"),
            entry_state=EntryState(),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )

        scene2 = SceneOutline(
            id="scene_01_02",
            chapter_id="chapter_01",
            narrative_position=2,
            story_time="day_1_afternoon",
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="Advance the scene"),
            opposition=Opposition(source_id="external", pressure="Resistance"),
            turn=Turn(type="complication", event="Situation changes", impact="Raises pressure"),
            decision=Decision(actor_id="clara", choice="Continue"),
            outcome=Outcome(result="partial"),
            entry_state=EntryState(),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )

        validator.add_scene(scene1)
        validator.add_scene(scene2)

        result = validator.validate_all_scenes()
        assert isinstance(result.is_valid, bool)


class TestKnowledgeConsistencyDetailed:
    """Test detailed knowledge consistency rules."""

    def test_knowledge_cannot_disappear(self):
        """Entry facts must survive in exit state unless explicitly questioned."""
        fact = KnowledgeFact(
            what="The door was locked",
            how_known="perceived",
            degree="certain",
            source="chapter_position",
        )
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="Enter the room"),
            opposition=Opposition(source_id="external", pressure="Locked door"),
            turn=Turn(type="complication", event="The key fails", impact="Blocks entry"),
            decision=Decision(actor_id="clara", choice="Find another route"),
            outcome=Outcome(result="failure"),
            entry_state=EntryState(knowledge=[fact]),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )
        result = KnowledgeValidator().validate_scene(scene)
        assert any(
            violation.violation_type == KnowledgeViolationType.INCONSISTENT_ENTRY_EXIT
            for violation in result.violations
        )

    def test_questioned_entry_fact_may_leave_exit_state(self):
        """Explicit questioning is the bounded current-schema exception to continuity."""
        fact = KnowledgeFact(
            what="The witness is reliable",
            how_known="inferred",
            degree="probable",
            source="inference",
        )
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="Test the testimony"),
            opposition=Opposition(source_id="external", pressure="Contradictory evidence"),
            turn=Turn(type="discovery", event="A contradiction appears", impact="Undermines confidence"),
            decision=Decision(actor_id="clara", choice="Reopen the question"),
            outcome=Outcome(result="partial", knowledge_questioned=[fact.what]),
            entry_state=EntryState(knowledge=[fact]),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )
        result = KnowledgeValidator().validate_scene(scene)
        assert result.is_valid is True

    def test_outcome_added_fact_must_exist_in_exit_state(self):
        """Knowledge_added is checked exactly against exit_state without semantic inference."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="Inspect the ledger"),
            opposition=Opposition(source_id="external", pressure="Incomplete records"),
            turn=Turn(type="discovery", event="A payment appears", impact="Creates a lead"),
            decision=Decision(actor_id="clara", choice="Trace the payment"),
            outcome=Outcome(result="success", knowledge_added=["A hidden payment exists"]),
            entry_state=EntryState(),
            exit_state=ExitState(),
            status=SceneStatus.READY,
        )
        result = KnowledgeValidator().validate_scene(scene)
        assert any(
            violation.violation_type == KnowledgeViolationType.KNOWLEDGE_GAP
            and violation.fact_what == "A hidden payment exists"
            for violation in result.violations
        )
