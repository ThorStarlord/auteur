from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ArtifactRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    revision: int


class DirectionCommitment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commitment_id: str
    statement: str
    scope: Literal["series", "book"]


class SeriesDirection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    series_id: str
    title: str
    series_type: Literal["ongoing"]
    promise: str
    pressure: str
    open_question: str
    commitments: list[DirectionCommitment] = Field(min_length=1)


class SeriesDirectionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str
    revision: int = Field(ge=1)
    direction: SeriesDirection
    source_refs: list[ArtifactRef] = Field(default_factory=list)


class AcceptedSeriesDirection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    proposal_id: str
    direction: SeriesDirection
