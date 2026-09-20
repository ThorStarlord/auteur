"""Pure first-draft continuation transitions for the Beginner Workspace.

This module owns no persistence, receipts, projections, or canonical story
authority. It only derives the next durable ContinuationState from an already
loaded SessionEnvelope. BeginnerWorkspaceApplication remains the public
orchestration facade and owns optimistic concurrency and idempotent command
receipts.
"""

from __future__ import annotations

from pathlib import Path

from .continuation import (
    ChapterPlan,
    ContinuationState,
    DraftHandoff,
    OutlineProposal,
    ScenePlan,
    accepted_milestone_fingerprint,
    derive_outline_chapters,
)
from .contracts import SessionEnvelope


class ContinuationTransitionError(ValueError):
    """A requested continuation transition is not valid from the current state."""


def propose_outline(
    session: SessionEnvelope,
    *,
    workspace_id: str,
    identity_title: str,
    project_root: Path,
) -> ContinuationState:
    if "whole_story_structure" not in {
        reference.milestone_id for reference in session.accepted_milestones
    }:
        raise ContinuationTransitionError(
            "accept whole-story Structure before proposing an outline"
        )
    current = session.continuation
    if current is not None and current.outline_proposal is not None:
        return current
    proposal = OutlineProposal(
        proposal_id=f"outline:{workspace_id}:1",
        title=identity_title,
        source_refs=("story_identity", "whole_story_structure"),
        source_fingerprint=accepted_milestone_fingerprint(session.accepted_milestones),
        chapters=derive_outline_chapters(project_root, premise=session.premise),
    )
    return ContinuationState(outline_proposal=proposal)


def accept_outline(current: ContinuationState | None) -> ContinuationState:
    if current is None or current.outline_proposal is None:
        raise ContinuationTransitionError("propose an outline before accepting it")
    if current.outline_accepted:
        return current
    return current.model_copy(update={"outline_accepted": True})


def propose_chapter_plan(current: ContinuationState | None) -> ContinuationState:
    if current is None or not current.outline_accepted:
        raise ContinuationTransitionError(
            "accept the whole-story outline before planning Chapter 1"
        )
    if current.chapter_plan is not None:
        return current
    assert current.outline_proposal is not None
    source = current.outline_proposal.chapters[0]
    plan = ChapterPlan(
        chapter_index=source.chapter_index,
        role=source.role,
        what_changes=source.purpose,
        advancing_threads=source.advancing_threads,
        character_pressure=source.character_pressure,
        setup=source.setup,
        payoff=source.payoff,
        reader_knows=source.reader_after,
        reader_feels="The story's central pressure is now active.",
        recommended_shape=(
            "Enter from the current state, apply pressure, and end with a changed choice."
        ),
    )
    return current.model_copy(update={"chapter_plan": plan})


def accept_chapter_plan(current: ContinuationState | None) -> ContinuationState:
    if current is None or current.chapter_plan is None:
        raise ContinuationTransitionError(
            "propose a Chapter 1 plan before accepting it"
        )
    if current.chapter_plan_accepted:
        return current
    return current.model_copy(update={"chapter_plan_accepted": True})


def propose_scene_plans(current: ContinuationState | None) -> ContinuationState:
    if current is None or not current.chapter_plan_accepted:
        raise ContinuationTransitionError(
            "accept the Chapter 1 plan before planning scenes"
        )
    if current.scene_plans:
        return current
    assert current.chapter_plan is not None
    plan = current.chapter_plan
    scene = ScenePlan(
        scene_id="scene-01-01",
        purpose=plan.what_changes,
        pov="protagonist",
        entry_state=(
            "The protagonist is still operating under the prior story assumption."
        ),
        immediate_goal="Respond to the chapter's immediate pressure.",
        conflict=plan.character_pressure,
        important_change=plan.what_changes,
        ending_state=(
            "The protagonist leaves the scene with a changed immediate situation."
        ),
        continuity_constraints=(
            "Preserve accepted StoryIdentity and Structure commitments.",
        ),
    )
    return current.model_copy(update={"scene_plans": (scene,)})


def accept_scene_plans(current: ContinuationState | None) -> ContinuationState:
    if current is None or not current.scene_plans:
        raise ContinuationTransitionError("propose scene plans before accepting them")
    if current.scene_plans_accepted:
        return current
    return current.model_copy(update={"scene_plans_accepted": True})


def prepare_draft_handoff(current: ContinuationState | None) -> ContinuationState:
    if current is None or not current.scene_plans_accepted:
        raise ContinuationTransitionError(
            "accept the Chapter 1 scene plans before drafting"
        )
    if current.draft_handoff is not None and current.draft_status == "ready":
        return current
    assert current.outline_proposal is not None
    handoff = DraftHandoff(
        chapter_index=1,
        accepted_inputs=(
            "story_identity",
            "whole_story_structure",
            "outline",
            "chapter_plan",
            "scene_plan",
        ),
        command="auteur draft <project> 1",
        source_fingerprint=current.outline_proposal.source_fingerprint,
    )
    return current.model_copy(
        update={"draft_handoff": handoff, "draft_status": "ready"}
    )
