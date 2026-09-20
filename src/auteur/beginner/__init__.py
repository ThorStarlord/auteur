"""Beginner-facing projections over Auteur's existing narrative authorities."""

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
    ChapterPlan,
    ContinuationState,
    DraftHandoff,
    ScenePlan,
    build_chapter_plan,
    build_scene_plans,
)

__all__ = [
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
    "ChapterPlan",
    "ContinuationState",
    "DraftHandoff",
    "ScenePlan",
    "build_chapter_plan",
    "build_scene_plans",
]
