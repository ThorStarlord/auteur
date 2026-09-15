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
]
