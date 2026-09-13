from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CampaignStateError(RuntimeError):
    """A persisted Campaign cannot be safely interpreted or written."""


class Campaign(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: int = 1
    campaign_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    phase: Literal["identity", "structure", "realization", "expression", "complete"] = "identity"
    source_revisions: dict[str, str] = Field(default_factory=dict)
    pending_handoffs: list[str] = Field(default_factory=list)
    recovery_status: Literal["clean", "recovery_required"] = "clean"

    @field_validator("source_revisions")
    @classmethod
    def reject_empty_revision_keys(cls, value: dict[str, str]) -> dict[str, str]:
        if any(not key or not revision for key, revision in value.items()):
            raise ValueError("source_revisions must contain non-empty paths and revisions")
        return value
