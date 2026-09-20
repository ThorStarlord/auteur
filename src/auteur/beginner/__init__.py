"""Contracts for the Beginner Workspace vertical slice."""

from .contracts import (
    AcceptedMilestoneReference,
    CreateWorkspaceCommand,
    DecisionStage,
    LifecycleStatus,
    MutationCommand,
    RevisionRef,
    SessionEnvelope,
    StageAvailability,
    StageStatus,
    WorkingDecision,
)
from .mystery_adapter import register_mystery_guidance_adapter
from .post_draft import (
    AcceptanceReconciliation,
    ChapterProductionStatus,
    DraftReviewProjection,
    RevisionHandoff,
    accept_latest_chapter,
    prepare_revision_handoff,
    project_chapter_outcome,
    project_draft_review,
    project_next_chapter_context,
)
from .continuation import (
    AcceptedChapterOutcome,
    ChapterContinuationState,
    ContextualChapterPlan,
    ContextualDraftHandoff,
    ContextualScenePlan,
    build_contextual_chapter_plan,
    build_contextual_scene_plans,
)

register_mystery_guidance_adapter()

__all__ = [
    "AcceptedMilestoneReference",
    "CreateWorkspaceCommand",
    "DecisionStage",
    "LifecycleStatus",
    "MutationCommand",
    "RevisionRef",
    "SessionEnvelope",
    "StageAvailability",
    "StageStatus",
    "WorkingDecision",
    "AcceptanceReconciliation",
    "ChapterProductionStatus",
    "DraftReviewProjection",
    "RevisionHandoff",
    "accept_latest_chapter",
    "prepare_revision_handoff",
    "project_chapter_outcome",
    "project_draft_review",
    "project_next_chapter_context",
    "AcceptedChapterOutcome",
    "ChapterContinuationState",
    "ContextualChapterPlan",
    "ContextualDraftHandoff",
    "ContextualScenePlan",
    "build_contextual_chapter_plan",
    "build_contextual_scene_plans",
]
