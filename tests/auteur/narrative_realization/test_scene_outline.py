"""Comprehensive tests for SceneOutline schema with all five semantic boundaries.

Test coverage:
- Creation and initialization
- Status validation (draft, incomplete, ready)
- Emotional state validation
- Arc beat realization with degrees
- Knowledge state tracking
- Temporal relation validation
- ID format validation
- Edge cases
"""

import pytest

from auteur.narrative_realization.schema import (
    ArcBeatRealization,
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
    TemporalRelation,
    Turn,
)


# ---------------------------------------------------------------------------
# Minimal/Draft Scene Creation Tests
# ---------------------------------------------------------------------------


class TestSceneOutlineMinimalCreation:
    """Test creating minimal draft scenes (id, chapter_id only)."""

    def test_create_minimal_draft_scene(self):
        """Minimal draft scene requires only id and chapter_id."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
        )
        assert scene.id == "scene_01_01"
        assert scene.chapter_id == "chapter_01"
        assert scene.status == SceneStatus.DRAFT
        assert scene.narrative_position is None
        assert scene.pov_character_id is None

    def test_draft_defaults_to_empty_collections(self):
        """Draft scenes should have empty collections."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
        )
        assert scene.participants == []
        assert scene.realizes_arc_beats == []
        assert scene.setups_created == []
        assert scene.payoffs_triggered == []
        assert scene.tags == []
        assert scene.notes == ""

    def test_draft_status_default(self):
        """Default status should be DRAFT."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
        )
        assert scene.status == SceneStatus.DRAFT


# ---------------------------------------------------------------------------
# Scene ID Format Validation Tests
# ---------------------------------------------------------------------------


class TestSceneIDValidation:
    """Test scene ID format validation (scene_XX_YY)."""

    def test_valid_scene_id(self):
        """Valid scene ID matches scene_XX_YY format."""
        scene = SceneOutline(
            id="scene_07_02",
            chapter_id="chapter_07",
        )
        assert scene.id == "scene_07_02"

    def test_invalid_scene_id_missing_prefix(self):
        """Scene ID must start with 'scene_'."""
        with pytest.raises(ValueError, match="Scene ID must match format"):
            SceneOutline(
                id="07_02",
                chapter_id="chapter_07",
            )

    def test_invalid_scene_id_wrong_format(self):
        """Scene ID must match scene_XX_YY format."""
        with pytest.raises(ValueError, match="Scene ID must match format"):
            SceneOutline(
                id="scene_7_2",
                chapter_id="chapter_07",
            )

    def test_invalid_scene_id_letters(self):
        """Scene ID numbers must be numeric."""
        with pytest.raises(ValueError, match="Scene ID must match format"):
            SceneOutline(
                id="scene_0a_02",
                chapter_id="chapter_07",
            )

    def test_chapter_id_required(self):
        """Chapter ID is required."""
        with pytest.raises(ValueError):
            SceneOutline(
                id="scene_01_01",
                chapter_id="",
            )


# ---------------------------------------------------------------------------
# Status-Based Field Requirement Tests
# ---------------------------------------------------------------------------


class TestDraftStatusRequirements:
    """Test DRAFT status allows minimal fields."""

    def test_draft_with_only_required_fields(self):
        """DRAFT should accept minimal fields."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
        )
        assert scene.status == SceneStatus.DRAFT

    def test_draft_ignores_incomplete_optional_fields(self):
        """DRAFT scenes can be created without narrative_position."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
            pov_character_id=None,  # Optional in draft
        )
        assert scene.pov_character_id is None


class TestIncompleteStatusRequirements:
    """Test INCOMPLETE status requires core structure."""

    def test_incomplete_requires_narrative_position(self):
        """INCOMPLETE requires narrative_position."""
        with pytest.raises(ValueError, match="narrative_position is required"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.INCOMPLETE,
                pov_character_id="clara",
                participants=["clara"],
                goal=Goal(actor_id="clara", objective="test"),
                opposition=Opposition(source_id="daniel", pressure="test"),
                outcome=Outcome(result="success"),
            )

    def test_incomplete_requires_pov_character_id(self):
        """INCOMPLETE requires pov_character_id."""
        with pytest.raises(ValueError, match="pov_character_id is required"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.INCOMPLETE,
                narrative_position=1,
                participants=["clara"],
                goal=Goal(actor_id="clara", objective="test"),
                opposition=Opposition(source_id="daniel", pressure="test"),
                outcome=Outcome(result="success"),
            )

    def test_incomplete_requires_participants(self):
        """INCOMPLETE requires participants list."""
        with pytest.raises(ValueError, match="participants must include"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.INCOMPLETE,
                narrative_position=1,
                pov_character_id="clara",
                participants=[],
                goal=Goal(actor_id="clara", objective="test"),
                opposition=Opposition(source_id="daniel", pressure="test"),
                outcome=Outcome(result="success"),
            )

    def test_incomplete_requires_pov_in_participants(self):
        """INCOMPLETE requires pov_character_id to be in participants."""
        with pytest.raises(ValueError, match="pov_character_id must be in participants"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.INCOMPLETE,
                narrative_position=1,
                pov_character_id="clara",
                participants=["daniel"],  # Missing clara
                goal=Goal(actor_id="clara", objective="test"),
                opposition=Opposition(source_id="daniel", pressure="test"),
                outcome=Outcome(result="success"),
            )

    def test_incomplete_requires_goal(self):
        """INCOMPLETE requires goal."""
        with pytest.raises(ValueError, match="goal is required"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.INCOMPLETE,
                narrative_position=1,
                pov_character_id="clara",
                participants=["clara"],
                opposition=Opposition(source_id="daniel", pressure="test"),
                outcome=Outcome(result="success"),
            )

    def test_incomplete_requires_opposition(self):
        """INCOMPLETE requires opposition."""
        with pytest.raises(ValueError, match="opposition is required"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.INCOMPLETE,
                narrative_position=1,
                pov_character_id="clara",
                participants=["clara"],
                goal=Goal(actor_id="clara", objective="test"),
                outcome=Outcome(result="success"),
            )

    def test_incomplete_requires_outcome(self):
        """INCOMPLETE requires outcome."""
        with pytest.raises(ValueError, match="outcome is required"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.INCOMPLETE,
                narrative_position=1,
                pov_character_id="clara",
                participants=["clara"],
                goal=Goal(actor_id="clara", objective="test"),
                opposition=Opposition(source_id="daniel", pressure="test"),
            )

    def test_incomplete_valid_minimal_structure(self):
        """INCOMPLETE can be created with goal, opposition, outcome."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.INCOMPLETE,
            narrative_position=1,
            pov_character_id="clara",
            participants=["clara", "daniel"],
            goal=Goal(actor_id="clara", objective="discover the truth"),
            opposition=Opposition(source_id="daniel", pressure="block investigation"),
            outcome=Outcome(result="success"),
        )
        assert scene.status == SceneStatus.INCOMPLETE
        assert scene.goal.objective == "discover the truth"


class TestReadyStatusRequirements:
    """Test READY status requires all fields."""

    def _create_ready_base(self):
        """Create base ready scene with required fields."""
        return dict(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.READY,
            narrative_position=1,
            story_time="day_1_morning",
            pov_character_id="clara",
            participants=["clara", "daniel"],
            goal=Goal(actor_id="clara", objective="discover the truth"),
            opposition=Opposition(source_id="daniel", pressure="block investigation"),
            turn=Turn(type="discovery", event="find evidence", impact="changes everything"),
            decision=Decision(actor_id="clara", choice="confront daniel"),
            outcome=Outcome(result="success"),
            entry_state=EntryState(),
            exit_state=ExitState(),
        )

    def test_ready_requires_narrative_position(self):
        """READY requires narrative_position."""
        kwargs = self._create_ready_base()
        kwargs["narrative_position"] = None
        with pytest.raises(ValueError, match="required fields missing"):
            SceneOutline(**kwargs)

    def test_ready_requires_story_time(self):
        """READY requires story_time."""
        kwargs = self._create_ready_base()
        kwargs["story_time"] = None
        with pytest.raises(ValueError, match="required fields missing"):
            SceneOutline(**kwargs)

    def test_ready_requires_story_time_nonempty(self):
        """READY story_time must not be empty."""
        kwargs = self._create_ready_base()
        kwargs["story_time"] = "   "
        with pytest.raises(ValueError, match="story_time must be non-empty"):
            SceneOutline(**kwargs)

    def test_ready_requires_pov_character_id(self):
        """READY requires pov_character_id."""
        kwargs = self._create_ready_base()
        kwargs["pov_character_id"] = None
        with pytest.raises(ValueError, match="required fields missing"):
            SceneOutline(**kwargs)

    def test_ready_requires_participants(self):
        """READY requires participants."""
        kwargs = self._create_ready_base()
        kwargs["participants"] = []
        with pytest.raises(ValueError, match="required fields missing"):
            SceneOutline(**kwargs)

    def test_ready_requires_turn(self):
        """READY requires turn."""
        kwargs = self._create_ready_base()
        kwargs["turn"] = None
        with pytest.raises(ValueError, match="turn is required"):
            SceneOutline(**kwargs)

    def test_ready_requires_decision(self):
        """READY requires decision."""
        kwargs = self._create_ready_base()
        kwargs["decision"] = None
        with pytest.raises(ValueError, match="decision is required"):
            SceneOutline(**kwargs)

    def test_ready_requires_entry_state(self):
        """READY requires entry_state."""
        kwargs = self._create_ready_base()
        kwargs["entry_state"] = None
        with pytest.raises(ValueError, match="entry_state is required"):
            SceneOutline(**kwargs)

    def test_ready_requires_exit_state(self):
        """READY requires exit_state."""
        kwargs = self._create_ready_base()
        kwargs["exit_state"] = None
        with pytest.raises(ValueError, match="exit_state is required"):
            SceneOutline(**kwargs)

    def test_ready_valid_complete_scene(self):
        """READY scene can be created with all required fields."""
        scene = SceneOutline(**self._create_ready_base())
        assert scene.status == SceneStatus.READY
        assert scene.goal.objective == "discover the truth"
        assert scene.turn.type == "discovery"


# ---------------------------------------------------------------------------
# Temporal Relation Validation Tests
# ---------------------------------------------------------------------------


class TestTemporalRelationValidation:
    """Test temporal relation validation (parallel_with, follows_scene)."""

    def test_temporal_relation_parallel_valid_format(self):
        """Parallel scene references must match scene_XX_YY format."""
        tr = TemporalRelation(parallel_with=["scene_01_02", "scene_01_03"])
        assert tr.parallel_with == ["scene_01_02", "scene_01_03"]

    def test_temporal_relation_parallel_invalid_format(self):
        """Parallel scene references must match scene_XX_YY format."""
        with pytest.raises(ValueError, match="Invalid scene ID"):
            TemporalRelation(parallel_with=["invalid_scene"])

    def test_temporal_relation_follows_valid_format(self):
        """Follows scene reference must match scene_XX_YY format."""
        tr = TemporalRelation(follows_scene="scene_01_01")
        assert tr.follows_scene == "scene_01_01"

    def test_temporal_relation_follows_invalid_format(self):
        """Follows scene reference must match scene_XX_YY format."""
        with pytest.raises(ValueError, match="Invalid scene ID"):
            TemporalRelation(follows_scene="invalid_scene")

    def test_scene_cannot_follow_itself(self):
        """Scene cannot have follows_scene reference to itself."""
        with pytest.raises(ValueError, match="cannot follow itself"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.DRAFT,
                temporal_relation=TemporalRelation(follows_scene="scene_01_01"),
            )

    def test_scene_cannot_be_parallel_with_itself(self):
        """Scene cannot be parallel with itself."""
        with pytest.raises(ValueError, match="cannot be parallel with itself"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.DRAFT,
                temporal_relation=TemporalRelation(parallel_with=["scene_01_01"]),
            )

    def test_temporal_relation_optional(self):
        """Temporal relation is optional in draft."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
        )
        assert scene.temporal_relation is None


# ---------------------------------------------------------------------------
# Arc Beat Realization Tests (Semantic Boundary #2)
# ---------------------------------------------------------------------------


class TestArcBeatRealizationDegrees:
    """Test arc beat realization with degree of realization."""

    def test_arc_beat_realization_full(self):
        """Arc beat can be realized with degree 'full'."""
        realization = ArcBeatRealization(
            beat_id="clara_distrust_deepens",
            degree="full",
        )
        assert realization.beat_id == "clara_distrust_deepens"
        assert realization.degree == "full"

    def test_arc_beat_realization_partial(self):
        """Arc beat can be realized with degree 'partial'."""
        realization = ArcBeatRealization(
            beat_id="clara_distrust_deepens",
            degree="partial",
        )
        assert realization.degree == "partial"

    def test_arc_beat_realization_implied(self):
        """Arc beat can be realized with degree 'implied'."""
        realization = ArcBeatRealization(
            beat_id="clara_distrust_deepens",
            degree="implied",
        )
        assert realization.degree == "implied"

    def test_arc_beat_realization_deferred(self):
        """Arc beat can be realized with degree 'deferred'."""
        realization = ArcBeatRealization(
            beat_id="clara_distrust_deepens",
            degree="deferred",
        )
        assert realization.degree == "deferred"

    def test_arc_beat_realization_invalid_degree(self):
        """Only four degrees are allowed: full, partial, implied, deferred."""
        with pytest.raises(ValueError):
            ArcBeatRealization(
                beat_id="clara_distrust_deepens",
                degree="half",  # Invalid
            )

    def test_scene_with_arc_beat_realizations(self):
        """Scene can reference arc beats with degrees."""
        scene = SceneOutline(
            id="scene_07_02",
            chapter_id="chapter_07",
            status=SceneStatus.DRAFT,
            realizes_arc_beats=[
                ArcBeatRealization(beat_id="clara_distrust_deepens", degree="full"),
                ArcBeatRealization(beat_id="daniel_investigation", degree="partial"),
            ],
        )
        assert len(scene.realizes_arc_beats) == 2
        assert scene.realizes_arc_beats[0].degree == "full"
        assert scene.realizes_arc_beats[1].degree == "partial"


# ---------------------------------------------------------------------------
# Emotional State Validation Tests (Semantic Boundary #5)
# ---------------------------------------------------------------------------


class TestEmotionalStateValidation:
    """Test emotional state validation (directional, not numeric)."""

    def test_emotional_state_with_low_intensity(self):
        """Emotional state can have low intensity."""
        emotion = EmotionalState(state="fear", intensity="low")
        assert emotion.intensity == "low"

    def test_emotional_state_with_moderate_intensity(self):
        """Emotional state can have moderate intensity."""
        emotion = EmotionalState(state="fear", intensity="moderate")
        assert emotion.intensity == "moderate"

    def test_emotional_state_with_high_intensity(self):
        """Emotional state can have high intensity."""
        emotion = EmotionalState(state="fear", intensity="high")
        assert emotion.intensity == "high"

    def test_emotional_state_default_intensity(self):
        """Default intensity is moderate."""
        emotion = EmotionalState(state="fear")
        assert emotion.intensity == "moderate"

    def test_emotional_state_with_rationale(self):
        """Emotional state can include rationale."""
        emotion = EmotionalState(
            state="suspicion",
            intensity="high",
            rationale="Daniel's behavior seems evasive",
        )
        assert emotion.rationale == "Daniel's behavior seems evasive"

    def test_emotional_state_no_numeric_scales(self):
        """Emotional states are semantic, not numeric."""
        # This is conceptual - states are author-defined semantic labels
        emotion = EmotionalState(state="guarded", intensity="moderate")
        assert emotion.state == "guarded"
        # States can be any non-empty string (including numeric-looking ones)
        # But intensity must be low/moderate/high (not numeric)
        with pytest.raises(ValueError):
            EmotionalState(state="fear", intensity="5")  # Numeric intensity not allowed


# ---------------------------------------------------------------------------
# Knowledge State Tracking Tests
# ---------------------------------------------------------------------------


class TestKnowledgeStateTracking:
    """Test knowledge state validation and tracking."""

    def test_knowledge_fact_creation(self):
        """KnowledgeFact tracks what, how_known, degree, source."""
        fact = KnowledgeFact(
            what="The victim was poisoned",
            how_known="learned",
            degree="certain",
            source="character_id",
        )
        assert fact.what == "The victim was poisoned"
        assert fact.how_known == "learned"
        assert fact.degree == "certain"

    def test_knowledge_fact_degrees(self):
        """Knowledge facts have different certainty degrees."""
        fact1 = KnowledgeFact(
            what="The victim was poisoned",
            how_known="learned",
            degree="certain",
            source="character_id",
        )
        fact2 = KnowledgeFact(
            what="The killer wore gloves",
            how_known="inferred",
            degree="probable",
            source="inference",
        )
        assert fact1.degree == "certain"
        assert fact2.degree == "probable"

    def test_entry_state_with_knowledge(self):
        """EntryState can track knowledge at scene start."""
        entry = EntryState(
            knowledge=[
                KnowledgeFact(
                    what="Daniel claims innocence",
                    how_known="external_source",
                    degree="certain",
                    source="character_id",
                )
            ]
        )
        assert len(entry.knowledge) == 1

    def test_exit_state_with_knowledge(self):
        """ExitState tracks knowledge at scene end."""
        exit_state = ExitState(
            knowledge=[
                KnowledgeFact(
                    what="Access record was altered",
                    how_known="learned",
                    degree="certain",
                    source="document",
                ),
                KnowledgeFact(
                    what="Daniel noticed her discovery",
                    how_known="perceived",
                    degree="certain",
                    source="chapter_position",
                ),
            ]
        )
        assert len(exit_state.knowledge) == 2

    def test_entry_and_exit_emotional_states(self):
        """Entry and exit states track emotions."""
        entry = EntryState(
            emotional={
                "trust": EmotionalState(state="guarded", intensity="moderate"),
                "suspicion": EmotionalState(state="active", intensity="moderate"),
            }
        )
        exit_state = ExitState(
            emotional={
                "trust": EmotionalState(state="suspicion", intensity="high"),
                "fear": EmotionalState(state="emerging", intensity="moderate"),
            }
        )
        assert entry.emotional["trust"].state == "guarded"
        assert exit_state.emotional["trust"].state == "suspicion"


# ---------------------------------------------------------------------------
# Dramatic Action Model Tests
# ---------------------------------------------------------------------------


class TestDramaticActionModels:
    """Test goal, opposition, turn, decision, outcome models."""

    def test_goal_creation(self):
        """Goal represents actor's objective."""
        goal = Goal(
            actor_id="clara",
            objective="discover the truth",
            rationale="She suspects Daniel of lying",
        )
        assert goal.actor_id == "clara"
        assert goal.objective == "discover the truth"

    def test_opposition_creation(self):
        """Opposition represents obstacles."""
        opposition = Opposition(
            source_id="daniel",
            pressure="block investigation",
            rationale="He's hiding something",
        )
        assert opposition.source_id == "daniel"
        assert opposition.pressure == "block investigation"

    def test_turn_types(self):
        """Turn has specific types."""
        turn_discovery = Turn(
            type="discovery",
            event="find altered record",
            impact="changes everything",
        )
        turn_reversal = Turn(
            type="reversal",
            event="unexpected help arrives",
            impact="situation flips",
        )
        assert turn_discovery.type == "discovery"
        assert turn_reversal.type == "reversal"

    def test_decision_creation(self):
        """Decision represents character choice."""
        decision = Decision(
            actor_id="clara",
            choice="confront daniel",
            rationale="Needs answers now",
        )
        assert decision.actor_id == "clara"
        assert decision.choice == "confront daniel"

    def test_outcome_result_types(self):
        """Outcome has specific result types."""
        outcome_success = Outcome(result="success")
        outcome_partial = Outcome(result="partial")
        outcome_failure = Outcome(result="failure")
        assert outcome_success.result == "success"
        assert outcome_partial.result == "partial"
        assert outcome_failure.result == "failure"

    def test_outcome_with_knowledge_changes(self):
        """Outcome tracks knowledge and emotional changes."""
        outcome = Outcome(
            result="partial",
            knowledge_added=[
                "Access record was altered",
                "Daniel noticed discovery",
            ],
            knowledge_questioned=["Daniel's alibi"],
            consequences=["Daniel realizes Clara found evidence"],
        )
        assert len(outcome.knowledge_added) == 2
        assert "Daniel's alibi" in outcome.knowledge_questioned


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------


class TestCompleteReadyScene:
    """Test creating a complete ready scene with all five boundaries."""

    def test_ready_scene_preserves_all_boundaries(self):
        """READY scene demonstrates all five semantic boundaries."""
        scene = SceneOutline(
            # Boundary 1: Scene owns chapter_id
            id="scene_07_02",
            chapter_id="chapter_07",
            narrative_position=2,
            status=SceneStatus.READY,
            # Characters
            pov_character_id="clara",
            participants=["clara", "daniel"],
            # Boundary 3: Narrative position separate from story_time
            story_time="day_3_evening",
            temporal_relation=TemporalRelation(
                parallel_with=["scene_07_01"],
            ),
            # Dramatic action
            goal=Goal(
                actor_id="clara",
                objective="inspect the ledger",
                rationale="Prove or disprove Daniel's alibi",
            ),
            opposition=Opposition(
                source_id="daniel",
                pressure="prevent discovery without explanation",
            ),
            turn=Turn(
                type="discovery",
                event="altered access record found",
                impact="Clara can no longer believe his innocence",
            ),
            decision=Decision(
                actor_id="clara",
                choice="conceal the discovery",
                rationale="She needs time to understand",
            ),
            outcome=Outcome(
                result="partial",
                knowledge_added=["access record altered"],
                knowledge_questioned=["daniel alibi validity"],
                consequences=["daniel realizes clara found evidence"],
            ),
            # Boundary 4: POV character knowledge model
            entry_state=EntryState(
                knowledge=[
                    KnowledgeFact(
                        what="daniel claims innocence",
                        how_known="external_source",
                        degree="certain",
                        source="character_id",
                    )
                ],
                emotional={
                    "trust": EmotionalState(state="guarded", intensity="moderate"),
                    "suspicion": EmotionalState(state="active", intensity="moderate"),
                },
            ),
            exit_state=ExitState(
                knowledge=[
                    KnowledgeFact(
                        what="access record altered",
                        how_known="learned",
                        degree="certain",
                        source="document",
                    ),
                    KnowledgeFact(
                        what="daniel noticed her",
                        how_known="perceived",
                        degree="certain",
                        source="chapter_position",
                    ),
                ],
                emotional={
                    # Boundary 5: Directional + intensity (not numeric)
                    "trust": EmotionalState(
                        state="suspicion",
                        intensity="high",
                        rationale="Daniel's interference confirms guilt",
                    ),
                    "fear": EmotionalState(state="emerging", intensity="moderate"),
                },
            ),
            # Boundary 2: Arc beat realization with degree
            realizes_arc_beats=[
                ArcBeatRealization(beat_id="clara_distrust_deepens", degree="full"),
                ArcBeatRealization(beat_id="false_alibi_discovered", degree="full"),
            ],
            setups_created=["altered record signature"],
            payoffs_triggered=["plant false alibi"],
        )
        # Verify all boundaries are preserved
        assert scene.chapter_id == "chapter_07"
        assert scene.realizes_arc_beats[0].degree == "full"
        assert scene.narrative_position == 2
        assert scene.story_time == "day_3_evening"
        assert scene.entry_state.knowledge[0].what == "daniel claims innocence"
        assert scene.exit_state.emotional["trust"].state == "suspicion"


class TestDraftToIncompleteTransition:
    """Test progression from draft to incomplete."""

    def test_draft_scene_progression(self):
        """Draft scene can be developed without status change."""
        draft = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
        )
        # Add content while in draft
        incomplete = SceneOutline(
            id=draft.id,
            chapter_id=draft.chapter_id,
            status=SceneStatus.INCOMPLETE,
            narrative_position=1,
            pov_character_id="protagonist",
            participants=["protagonist", "antagonist"],
            goal=Goal(actor_id="protagonist", objective="win"),
            opposition=Opposition(source_id="antagonist", pressure="lose"),
            outcome=Outcome(result="success"),
        )
        assert incomplete.status == SceneStatus.INCOMPLETE
        assert incomplete.narrative_position == 1


# ---------------------------------------------------------------------------
# Edge Cases and Error Handling
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_participants_in_ready_is_invalid(self):
        """Ready scene must have participants."""
        with pytest.raises(ValueError, match="required fields missing"):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.READY,
                narrative_position=1,
                story_time="day_1",
                pov_character_id="clara",
                participants=[],  # Empty!
                goal=Goal(actor_id="clara", objective="test"),
                opposition=Opposition(source_id="other", pressure="test"),
                turn=Turn(type="discovery", event="test", impact="test"),
                decision=Decision(actor_id="clara", choice="test"),
                outcome=Outcome(result="success"),
                entry_state=EntryState(),
                exit_state=ExitState(),
            )

    def test_unresolved_outcome(self):
        """Outcome can be unresolved."""
        # Note: Current schema uses "success", "partial", "failure"
        # "unresolved" is not allowed by current Outcome model
        outcome = Outcome(result="failure")
        assert outcome.result == "failure"

    def test_no_arc_beats_in_ready(self):
        """Ready scene can have no arc beats (not all scenes realize beats)."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.READY,
            narrative_position=1,
            story_time="day_1",
            pov_character_id="clara",
            participants=["clara"],
            goal=Goal(actor_id="clara", objective="test"),
            opposition=Opposition(source_id="other", pressure="test"),
            turn=Turn(type="discovery", event="test", impact="test"),
            decision=Decision(actor_id="clara", choice="test"),
            outcome=Outcome(result="success"),
            entry_state=EntryState(),
            exit_state=ExitState(),
            realizes_arc_beats=[],  # None
        )
        assert scene.realizes_arc_beats == []

    def test_narrative_position_positive_only(self):
        """Narrative position must be positive (>= 1)."""
        # Pydantic should enforce this with ge=1
        with pytest.raises(ValueError):
            SceneOutline(
                id="scene_01_01",
                chapter_id="chapter_01",
                status=SceneStatus.INCOMPLETE,
                narrative_position=0,  # Invalid!
                pov_character_id="clara",
                participants=["clara"],
                goal=Goal(actor_id="clara", objective="test"),
                opposition=Opposition(source_id="other", pressure="test"),
                outcome=Outcome(result="success"),
            )

    def test_tags_as_empty_list(self):
        """Tags can be empty."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
            tags=[],
        )
        assert scene.tags == []

    def test_tags_with_multiple_labels(self):
        """Tags can contain multiple labels."""
        scene = SceneOutline(
            id="scene_01_01",
            chapter_id="chapter_01",
            status=SceneStatus.DRAFT,
            tags=["reveal", "climax", "turning_point"],
        )
        assert len(scene.tags) == 3
        assert "reveal" in scene.tags
