"""Workflow data models — typed enums and dataclasses for the Guided Author Workflow."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


class WorkflowStage(enum.Enum):
    IDENTITY = "identity"
    STRUCTURE = "structure"
    REALIZATION = "realization"
    DRAFTING = "drafting"
    REASONING = "reasoning"
    RECONCILIATION = "reconciliation"
    ACCEPTANCE = "acceptance"
    ASSEMBLY = "assembly"
    PUBLISHING = "publishing"


class AuthorityLevel(enum.Enum):
    READ_ONLY = "read_only"
    DERIVED_ARTIFACT = "derived_artifact"
    CANDIDATE_GENERATION = "candidate_generation"
    PROPOSAL_GENERATION = "proposal_generation"
    AUTHORITY_BEARING = "authority_bearing"
    CANONICAL_MUTATION = "canonical_mutation"


SAFE_AUTHORITIES = {
    AuthorityLevel.READ_ONLY,
    AuthorityLevel.DERIVED_ARTIFACT,
    AuthorityLevel.CANDIDATE_GENERATION,
}

EXECUTABLE_AUTHORITIES = {
    AuthorityLevel.READ_ONLY,
    AuthorityLevel.DERIVED_ARTIFACT,
    AuthorityLevel.CANDIDATE_GENERATION,
}

# PROPOSAL_GENERATION is intentionally excluded from autonomous execution
# in v0.4.0. Though proposals are noncanonical and do not mutate accepted
# artifacts, the explicit exclusion ensures author oversight for any
# generated-repair scenario. It may be added to EXECUTABLE_AUTHORITIES
# in a future release when a concrete action requires it.


class BlockerSeverity(enum.Enum):
    BLOCKING = "blocking"
    WARNING = "warning"
    INFO = "info"


class BlockerCategory(enum.Enum):
    MISSING_PREREQUISITE = "missing_prerequisite"
    INVALID_ARTIFACT = "invalid_artifact"
    STALE_ARTIFACT = "stale_artifact"
    BLOCKING_REASONING = "blocking_reasoning"
    UNRESOLVED_RECONCILIATION = "unresolved_reconciliation"
    AUTHORITY_REQUIRED = "authority_required"
    AMBIGUOUS_CANDIDATE = "ambiguous_candidate"
    UNSUPPORTED_STATE = "unsupported_state"


@dataclass
class WorkflowBlocker:
    category: BlockerCategory
    severity: BlockerSeverity
    message: str
    artifact: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowAction:
    label: str
    command: str
    authority: AuthorityLevel
    description: str = ""
    auto_executable: bool = False


@dataclass
class StageProgress:
    stage: WorkflowStage
    is_complete: bool
    current_artifact: str | None = None
    blockers: list[WorkflowBlocker] = field(default_factory=list)


@dataclass
class WorkflowState:
    project_path: str
    current_stage: WorkflowStage | None
    stages: list[StageProgress] = field(default_factory=list)
    blockers: list[WorkflowBlocker] = field(default_factory=list)
    actions: list[WorkflowAction] = field(default_factory=list)
    status_summary: str = ""

    def stage_by_name(self, name: str) -> StageProgress | None:
        for s in self.stages:
            if s.stage.value == name:
                return s
        return None

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict."""
        return {
            "project_path": self.project_path,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "status_summary": self.status_summary,
            "stages": [
                {
                    "stage": sp.stage.value,
                    "is_complete": sp.is_complete,
                    "current_artifact": sp.current_artifact,
                    "blockers": [
                        {
                            "category": b.category.value,
                            "severity": b.severity.value,
                            "message": b.message,
                            "artifact": b.artifact,
                            "details": b.details,
                        }
                        for b in sp.blockers
                    ],
                }
                for sp in self.stages
            ],
            "blockers": [
                {
                    "category": b.category.value,
                    "severity": b.severity.value,
                    "message": b.message,
                    "artifact": b.artifact,
                    "details": b.details,
                }
                for b in self.blockers
            ],
            "actions": [
                {
                    "label": a.label,
                    "command": a.command,
                    "authority": a.authority.value,
                    "description": a.description,
                    "auto_executable": a.auto_executable,
                }
                for a in self.actions
            ],
        }
