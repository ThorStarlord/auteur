from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PatchStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    APPLIED = "applied"
    STALE = "stale"


class PatchType(str, Enum):
    REPLACE_TEXT = "replace_text"


class EditLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_line_range(self) -> "EditLocation":
        if self.end_line < self.start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return self


class EditFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    pass_name: str
    issue_type: str
    severity: EditSeverity
    location: EditLocation
    evidence: str
    rationale: str


class PatchProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    finding_id: str
    patch_type: PatchType
    location: EditLocation
    original: str
    replacement: str
    confidence: float = Field(ge=0.0, le=1.0)
    status: PatchStatus = PatchStatus.PROPOSED


class EditReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter: int = Field(ge=1)
    source_file: str
    source_draft: str
    passes: list[str]
    findings: list[EditFinding]
    patches: list[PatchProposal]

