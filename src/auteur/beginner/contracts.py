from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DecisionStage(str, Enum):
    DISCOVER = "discover"
    STORY_IDENTITY = "story_identity"
    STORY_STRUCTURE = "story_structure"


class LifecycleStatus(str, Enum):
    NOT_STARTED = "not_started"
    WORKING = "working"
    COMPLETE = "complete"
    BLOCKED = "blocked"


class StageAvailability(str, Enum):
    AVAILABLE = "available"
    LOCKED = "locked"


class RevisionRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)
    revision: int = Field(ge=1)


class AcceptedMilestoneReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    milestone_id: str = Field(min_length=1)
    revision: RevisionRef
    accepted_content: str | None = None
    fingerprint: str | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_coercible_snapshot_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for name in ("accepted_content", "fingerprint"):
                if name in data and data[name] is not None and type(data[name]) is not str:
                    raise ValueError(f"{name} must be a string or None")
        return data


class WorkingDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: DecisionStage
    question: str = Field(min_length=1)
    options: list[str] = Field(default_factory=list)


class StageStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: DecisionStage
    lifecycle: LifecycleStatus
    availability: StageAvailability
    working_decision: WorkingDecision | None = None

    @model_validator(mode="after")
    def require_consistent_working_decision(self) -> Self:
        if self.working_decision is not None and self.working_decision.stage != self.stage:
            raise ValueError("working_decision.stage must match stage")
        return self


class SessionEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    session_version: int = Field(default=0, ge=0)
    project_id: str = Field(min_length=1)
    guidance_genre: str = Field(min_length=1)
    premise: str = Field(min_length=1)
    stages: dict[DecisionStage, StageStatus]
    accepted_milestones: list[AcceptedMilestoneReference] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_consistent_stage_graph(self) -> Self:
        expected_stages = set(DecisionStage)
        actual_stages = set(self.stages)
        if actual_stages != expected_stages or len(self.stages) != len(expected_stages):
            raise ValueError("stages must contain exactly one status for every decision stage")
        for stage, status in self.stages.items():
            if status.stage != stage:
                raise ValueError("StageStatus.stage must match its stage mapping key")
        return self

    @classmethod
    def new(cls, project_id: str, guidance_genre: str, premise: str) -> SessionEnvelope:
        return cls(
            project_id=project_id,
            guidance_genre=guidance_genre,
            premise=premise,
            stages={
                DecisionStage.DISCOVER: StageStatus(
                    stage=DecisionStage.DISCOVER,
                    lifecycle=LifecycleStatus.WORKING,
                    availability=StageAvailability.AVAILABLE,
                ),
                DecisionStage.STORY_IDENTITY: StageStatus(
                    stage=DecisionStage.STORY_IDENTITY,
                    lifecycle=LifecycleStatus.NOT_STARTED,
                    availability=StageAvailability.LOCKED,
                ),
                DecisionStage.STORY_STRUCTURE: StageStatus(
                    stage=DecisionStage.STORY_STRUCTURE,
                    lifecycle=LifecycleStatus.NOT_STARTED,
                    availability=StageAvailability.LOCKED,
                ),
            },
        )


class MutationCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_id: str = Field(min_length=1)
    expected_session_version: int = Field(ge=0)
    command_id: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)


class CreateWorkspaceCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
