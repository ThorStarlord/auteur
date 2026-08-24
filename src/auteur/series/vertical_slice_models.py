from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from auteur.identity import StoryIdentity


class ArtifactRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    revision: int


class AcceptedFactRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    revision: int
    fact_id: str


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


def _require_unique_transition_ids(
    transitions: list[StateTransition],
) -> list[StateTransition]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for transition in transitions:
        if transition.transition_id in seen:
            duplicates.add(transition.transition_id)
        seen.add(transition.transition_id)
    if duplicates:
        raise ValueError(
            "transition_id values must be unique: "
            + ", ".join(sorted(duplicates))
        )
    return transitions


class RealizationCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    book_number: int = Field(ge=1)
    summary: str
    transitions: list[StateTransition] = Field(min_length=1)
    source_refs: list[ArtifactRef] = Field(min_length=1)
    resolved_commitment_ids: list[str] = Field(default_factory=list)

    @field_validator("transitions")
    @classmethod
    def require_unique_transition_ids(
        cls, transitions: list[StateTransition]
    ) -> list[StateTransition]:
        return _require_unique_transition_ids(transitions)


class AcceptedRealizationBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    bundle_id: str
    candidate_id: str
    book_number: int = Field(ge=1)
    transitions: list[StateTransition] = Field(min_length=1)
    resolved_commitment_ids: list[str] = Field(default_factory=list)

    @field_validator("transitions")
    @classmethod
    def require_unique_transition_ids(
        cls, transitions: list[StateTransition]
    ) -> list[StateTransition]:
        return _require_unique_transition_ids(transitions)


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


class BookPlanningIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_number: int = Field(gt=1)
    intent: str
    relevance_refs: list[AcceptedFactRef] = Field(default_factory=list)


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


class DecisionOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: str
    label: str
    summary: str
    tradeoff: str


class NextDecisionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str
    book_number: int = Field(gt=1)
    question: str
    recommended_option_id: str
    options: list[DecisionOption] = Field(min_length=2)
    rationale: str
    accepted_input_refs: list[ArtifactRef] = Field(min_length=1)
    status: Literal["proposed", "resolved", "deferred"] = "proposed"

    @model_validator(mode="after")
    def require_presented_recommendation(self) -> Self:
        option_ids = [option.option_id for option in self.options]
        if len(option_ids) != len(set(option_ids)):
            raise ValueError("option_id values must be unique")
        if self.recommended_option_id not in option_ids:
            raise ValueError(
                "recommended_option_id must reference a presented option"
            )
        return self


class DecisionAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str
    action: Literal["choose_recommended", "choose_other", "defer"]
    selected_option_id: str | None = None
    recorded_at: datetime
