from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from auteur.identity import StoryIdentity


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


class BookDirection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_number: int = Field(ge=1)
    identity: StoryIdentity
    series_commitment_ids: list[str] = Field(min_length=1)


class BookDirectionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str
    revision: int = Field(ge=1)
    direction: BookDirection
    source_refs: list[ArtifactRef]


class AcceptedBookDirection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    proposal_id: str
    direction: BookDirection


class StateTransition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transition_id: str
    subject: str
    attribute: str
    before: str | None = None
    after: str
    explanation: str


class RealizationCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    book_number: int = Field(ge=1)
    summary: str
    transitions: list[StateTransition] = Field(min_length=1)
    source_refs: list[ArtifactRef] = Field(min_length=1)


class AcceptedRealizationBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    bundle_id: str
    candidate_id: str
    book_number: int = Field(ge=1)
    transitions: list[StateTransition] = Field(min_length=1)


class CanonicalState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state_version: int = Field(ge=0)
    values: dict[str, str] = Field(default_factory=dict)
    applied_bundle_ids: list[str] = Field(default_factory=list)


class PlanningEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_number: int = Field(gt=1)
    entered_by: str
    entered_at: datetime


class CarryForwardItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    kind: Literal["series_commitment", "state_change"]
    summary: str
    why_matters_now: str
    source_refs: list[ArtifactRef] = Field(min_length=1)


class BookPlanningContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_number: int = Field(gt=1)
    generated_from: list[ArtifactRef] = Field(min_length=1)
    items: list[CarryForwardItem] = Field(min_length=1)
    derivation_version: str
