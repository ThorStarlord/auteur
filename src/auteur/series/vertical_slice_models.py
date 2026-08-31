from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Self

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


AcceptedContinuitySourceRef = ArtifactRef | AcceptedFactRef
ContinuityDisposition = Literal[
    "active",
    "resolved",
    "dormant",
    "reactivated",
    "superseded",
    "irrelevant",
]


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


RelationOrigin = Literal[
    "DECLARED", "DETERMINISTIC_DERIVATION", "INTERPRETIVE"
]
RelationDisposition = Literal["active", "stale", "rejected"]
PressureMemberRole = Literal[
    "originating_history", "causal_pivot", "current_constraint"
]


class PressureGroupMember(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact_ref: AcceptedFactRef
    role: PressureMemberRole


class CommitmentRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    revision: int
    commitment_id: str


class GlobalMapEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: str
    kind: Literal["commitment", "fact"]
    summary: str
    source_refs: list[AcceptedContinuitySourceRef] = Field(min_length=1)
    disposition: ContinuityDisposition
    is_current_constraint: bool = False
    fact_ref: AcceptedFactRef | None = None
    subject: str | None = None
    attribute: str | None = None
    before: str | None = None
    after: str | None = None
    book_number: int | None = Field(default=None, ge=1)


class CausalSupportRelation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["causal_support"] = "causal_support"
    relation_id: str
    origin: RelationOrigin
    source_fact_ref: AcceptedFactRef
    target_fact_ref: AcceptedFactRef
    evidence_refs: list[AcceptedContinuitySourceRef] = Field(default_factory=list)
    source_revision_refs: list[ArtifactRef] = Field(default_factory=list)
    rule_version: str | None = None
    disposition: RelationDisposition = "active"


class PressureGroupRelation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["pressure_group"] = "pressure_group"
    relation_id: str
    origin: RelationOrigin
    target_commitment_or_pressure_ref: CommitmentRef | AcceptedFactRef
    members: list[PressureGroupMember] = Field(min_length=2)
    evidence_refs: list[AcceptedContinuitySourceRef] = Field(default_factory=list)
    source_revision_refs: list[ArtifactRef] = Field(default_factory=list)
    rule_version: str | None = None
    disposition: RelationDisposition = "active"


StoryInstanceRelation = Annotated[
    CausalSupportRelation | PressureGroupRelation,
    Field(discriminator="kind"),
]


class MapCurrentStateEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    current_value: str
    current_fact_ref: AcceptedFactRef
    superseded_fact_ids: tuple[str, ...] = ()


class GlobalMapSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_id: str
    planning_book_number: int = Field(gt=1)
    source_revisions: list[ArtifactRef] = Field(min_length=1)
    current_state_evidence: dict[str, MapCurrentStateEvidence] = Field(
        default_factory=dict
    )
    entries: list[GlobalMapEntry] = Field(default_factory=list)
    historical_fact_refs: list[AcceptedFactRef] = Field(default_factory=list)
    relations: list[StoryInstanceRelation] = Field(default_factory=list)
    pressure_groups: list[PressureGroupRelation] = Field(default_factory=list)
    currentness: dict[str, ContinuityDisposition] = Field(default_factory=dict)
    derivation_version: str
    source_fingerprint: str
    freshness: Literal["fresh", "stale"] = "fresh"
    semantic_impact: Literal["clear", "suspect", "contradictory"] = "clear"


class CanonicalState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state_version: int = Field(ge=0)
    values: dict[str, str] = Field(default_factory=dict)
    applied_bundle_ids: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)


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


class ContinuityEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: str
    kind: Literal["commitment", "fact"]
    summary: str
    why_matters_now: str
    source_refs: tuple[AcceptedContinuitySourceRef, ...] = Field(min_length=1)
    disposition: ContinuityDisposition
    group_id: str | None = None
    is_current_constraint: bool

    @property
    def item_id(self) -> str:
        """Keep the Task 5 item identifier available to existing callers."""
        return self.fact_id or self.entry_id

    @property
    def fact_id(self) -> str | None:
        if self.kind != "fact":
            return None
        return next(
            (
                ref.fact_id
                for ref in self.source_refs
                if isinstance(ref, AcceptedFactRef)
            ),
            None,
        )


class ContinuityGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_id: str
    summary: str
    why_matters_now: str
    source_refs: list[AcceptedContinuitySourceRef] = Field(min_length=1)
    entry_ids: list[str] = Field(min_length=1)
    relation_id: str | None = None
    member_roles: dict[str, PressureMemberRole] = Field(default_factory=dict)


class RepeatedBookPlanningContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_number: int = Field(gt=1)
    generated_from: list[ArtifactRef] = Field(min_length=1)
    groups: list[ContinuityGroup] = Field(default_factory=list)
    entries: list[ContinuityEntry] = Field(default_factory=list)
    history_entries: list[ContinuityEntry] = Field(default_factory=list)
    trigger_refs: list[AcceptedFactRef] = Field(default_factory=list)
    derivation_version: str

    @property
    def items(self) -> tuple[ContinuityEntry, ...]:
        """Expose all derived items for Task 5 compatibility."""
        return tuple((*self.entries, *self.history_entries))

    @property
    def active_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.entry_id
            for entry in self.entries
            if entry.kind == "commitment"
            and entry.disposition in {"active", "reactivated"}
        )

    @property
    def active_fact_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.fact_id
            for entry in self.entries
            if entry.kind == "fact"
            and entry.disposition in {"active", "reactivated"}
            and entry.fact_id is not None
        )

    @property
    def resolved_history_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.entry_id
            for entry in self.items
            if entry.disposition == "resolved"
        )

    @property
    def dispositions(self) -> dict[str, ContinuityDisposition]:
        dispositions = {
            entry.entry_id: entry.disposition for entry in self.items
        }
        fact_id_counts: dict[str, int] = {}
        for entry in self.items:
            if entry.fact_id is not None:
                fact_id_counts[entry.fact_id] = (
                    fact_id_counts.get(entry.fact_id, 0) + 1
                )
        dispositions.update(
            {
                entry.fact_id: entry.disposition
                for entry in self.items
                if entry.fact_id is not None
                and fact_id_counts[entry.fact_id] == 1
            }
        )
        return dispositions

    @property
    def group_ids(self) -> tuple[str, ...]:
        return tuple(group.group_id for group in self.groups)

    def item(self, entry_id: str) -> ContinuityEntry:
        exact_matches = [
            entry for entry in self.items if entry.entry_id == entry_id
        ]
        if exact_matches:
            return exact_matches[0]
        fact_matches = [
            entry for entry in self.items if entry.fact_id == entry_id
        ]
        if len(fact_matches) == 1:
            return fact_matches[0]
        if len(fact_matches) > 1:
            raise ValueError(
                f"Continuity fact ID {entry_id!r} is ambiguous; use its "
                "composite entry ID"
            )
        raise KeyError(entry_id)

    def group(self, group_id: str) -> ContinuityGroup:
        return next(group for group in self.groups if group.group_id == group_id)

    def group_source_fact_ids(self, group_id: str) -> set[str]:
        return {
            entry.fact_id
            for entry_id in self.group(group_id).entry_ids
            if (entry := self.item(entry_id)).fact_id is not None
        }


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
    incompatible_with_state_refs: list[ArtifactRef] = Field(
        default_factory=list
    )
    incompatibility_reason: str | None = None


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
