from auteur.beginner.continuation import (
    ChapterPlan,
    ContinuationState,
    DraftHandoff,
    OutlineProposal,
    ScenePlan,
)
from auteur.beginner.contracts import SessionEnvelope


def test_continuation_artifacts_have_explicit_authority_states() -> None:
    outline = OutlineProposal(
        proposal_id="outline-1",
        title="The story outline",
        source_refs=("story_identity", "whole_story_structure"),
        chapters=(),
    )
    chapter = ChapterPlan(
        chapter_index=1,
        role="Destabilize the protagonist",
        what_changes="The protagonist loses their safe assumption.",
        advancing_threads=("main",),
        character_pressure="The protagonist must choose whether to act.",
        setup=("The hidden message",),
        payoff=(),
        reader_knows="The premise is now active.",
        reader_feels="Uneasy curiosity.",
        recommended_shape="Enter stable, pressure the want, end with a decision.",
    )
    scene = ScenePlan(
        scene_id="scene-01-01",
        purpose="Force the first decision",
        pov="protagonist",
        entry_state="The protagonist believes the day is ordinary.",
        immediate_goal="Find out who left the message.",
        conflict="The message is dangerous to investigate.",
        important_change="The protagonist chooses to follow the clue.",
        ending_state="The protagonist leaves safety.",
        continuity_constraints=("Keep the message contents consistent.",),
    )
    handoff = DraftHandoff(
        chapter_index=1,
        accepted_inputs=("story_identity", "whole_story_structure", "outline", "chapter_plan", "scene_plan"),
        command="auteur draft PROJECT 1",
    )
    state = ContinuationState(outline_proposal=outline, chapter_plan=chapter, scene_plans=(scene,), draft_handoff=handoff)

    assert state.outline_proposal is outline
    assert state.chapter_plan is chapter
    assert state.scene_plans[0].scene_id == "scene-01-01"
    assert state.draft_handoff is handoff


def test_session_round_trip_preserves_continuation_state() -> None:
    session = SessionEnvelope.new("project", "mystery", "A locked room")
    session.continuation = ContinuationState(
        outline_proposal=OutlineProposal(
            proposal_id="outline-1",
            title="A locked room",
            source_refs=("story_identity", "whole_story_structure"),
            chapters=(),
        )
    )

    restored = SessionEnvelope.model_validate_json(session.model_dump_json(), strict=True)

    assert restored.continuation is not None
    assert restored.continuation.outline_proposal is not None
    assert restored.continuation.outline_proposal.proposal_id == "outline-1"
