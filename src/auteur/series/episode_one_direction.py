"""Bounded Episode 1 Direction: domain models and pure validation.

This module holds the Episode-specific semantics for the ratified
Bounded Episode 1 Direction capability contract. It adds new concrete
models and pure helpers only; it does not modify `SeriesDirection`, the
legacy Series type model, or any existing accepted-artifact hash, and it
does not introduce a sixth canonical scope.

The store and service keep thin persistence/orchestration hooks and import
the models and validators defined here, following the Repeated Map/Focus
precedent of a dedicated pure module.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from auteur.identity import StoryIdentity
from auteur.series.vertical_slice_models import (
    AcceptedSeriesDirection,
    ArtifactRef,
)


class EpisodicEntryFormDeclaration(BaseModel):
    """Authority-bearing Series identity decision: this Series is episodic.

    Persisted separately from `SeriesDirection` so that no existing accepted
    Series Direction, its content, or its content hash is rewritten. Absence
    of this artifact is defined as Book-oriented behavior.
    """

    model_config = ConfigDict(extra="forbid")

    declaration_id: str = Field(min_length=1)
    declaring_author: str = Field(min_length=1)
    declared_at: datetime
    series_direction: ArtifactRef

    @field_validator("declared_at")
    @classmethod
    def _require_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError(
                "Episodic entry-form declaration timestamp must be UTC"
            )
        return value


class AcceptedEpisodicEntryForm(BaseModel):
    """The accepted episodic entry-form authority artifact."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)
    declaration: EpisodicEntryFormDeclaration


class EpisodeDirection(BaseModel):
    """A Series-scope, Identity-layer entry-unit Direction for Episode 1.

    The episodic counterpart of a Book 1 Direction; not a relabelled Book
    Direction. It references at least one commitment from the current
    accepted Series Direction and performs no artistic judgement.
    """

    model_config = ConfigDict(extra="forbid")

    episode_number: Literal[1]
    identity: StoryIdentity
    series_commitment_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def _reject_duplicate_references(self) -> Self:
        if len(set(self.series_commitment_ids)) != len(
            self.series_commitment_ids
        ):
            raise ValueError(
                "Duplicate Series commitment references are not allowed"
            )
        return self


class EpisodeDirectionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str = Field(min_length=1)
    revision: int = Field(ge=1)
    direction: EpisodeDirection
    source_refs: list[ArtifactRef]


class AcceptedEpisodeDirection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(min_length=1)
    proposal_id: str = Field(min_length=1)
    direction: EpisodeDirection


class EpisodeDirectionAcceptance(BaseModel):
    """Result of an Episode 1 Direction acceptance action.

    ``changed`` is False when an already-accepted, content-identical Episode 1
    Direction was found; callers and the CLI present that explicitly as a
    no-change result, distinct from a first acceptance.
    """

    model_config = ConfigDict(extra="forbid")

    accepted: AcceptedEpisodeDirection
    changed: bool


def require_unique_references(direction: EpisodeDirection) -> None:
    """Reject duplicate Series commitment references.

    Duplicates are a structural violation at both proposal time and
    acceptance time; Auteur does not silently de-duplicate them.
    """
    if len(set(direction.series_commitment_ids)) != len(
        direction.series_commitment_ids
    ):
        raise ValueError(
            "Duplicate Series commitment references are not allowed"
        )


def validate_episode_references(
    direction: EpisodeDirection,
    accepted_series: AcceptedSeriesDirection,
) -> None:
    """Validate Episode 1 Direction references against the current authority.

    Structural only: at least one reference is present (model-enforced);
    duplicates are rejected; every referenced commitment must belong to the
    current accepted Series Direction. A reference to a commitment from a
    superseded Series Direction revision is unknown here and therefore
    invalid. No artistic or relevance judgement is performed.
    """
    require_unique_references(direction)
    known_ids = {
        commitment.commitment_id
        for commitment in accepted_series.direction.commitments
    }
    unknown_ids = sorted(set(direction.series_commitment_ids) - known_ids)
    if unknown_ids:
        raise ValueError(
            "Unknown accepted Series commitment reference(s): "
            + ", ".join(unknown_ids)
        )


def require_entry_form_eligibility(
    accepted_series: AcceptedSeriesDirection | None,
    *,
    has_book_direction_proposal: bool,
    has_accepted_book_direction: bool,
) -> None:
    """Check the entry-form declaration preconditions.

    The declaration is permitted only after an accepted Series Direction
    exists, and only while the Series has no Book Direction proposal and no
    accepted Book Direction. Once entry-level Direction work has begun in
    either form, the entry form is locked for this bounded capability.
    """
    if accepted_series is None:
        raise ValueError(
            "An accepted Series Direction is required before declaring an "
            "episodic entry form"
        )
    if has_book_direction_proposal:
        raise ValueError(
            "Cannot declare an episodic entry form after Book Direction "
            "work has begun"
        )
    if has_accepted_book_direction:
        raise ValueError(
            "Cannot declare an episodic entry form after a Book Direction "
            "has been accepted"
        )


def require_episodic_for_episode_direction(
    entry_form: AcceptedEpisodicEntryForm | None,
) -> None:
    """Episode Direction is available only for an explicitly episodic Series."""
    if entry_form is None:
        raise ValueError(
            "Episode Direction is available only for an explicitly episodic "
            "Series"
        )
