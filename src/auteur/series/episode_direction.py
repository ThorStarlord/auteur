from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from auteur.series.vertical_slice_models import (
    AcceptedEpisodeDirection,
    AcceptedSeriesEntryForm,
    ArtifactRef,
    SeriesDirection,
)


DEFAULT_ENTRY_FORM: Literal["book"] = "book"


def interpret_entry_form(
    record: AcceptedSeriesEntryForm | None,
) -> Literal["book", "episodic"]:
    """Translate an optional accepted entry-form record into the canonical vocabulary.

    Absence of the record means the Series is Book-oriented (unchanged legacy
    behaviour); the only persisted value is ``"episodic"``.
    """
    if record is None:
        return DEFAULT_ENTRY_FORM
    return record.entry_form


@dataclass(frozen=True)
class EpisodeDirectionInspection:
    """Read-only view distinguishing Series-level from Episode-level authority.

    Carries only commitment IDs, never copied Series commitment statements.
    """

    series: SeriesDirection
    series_ref: ArtifactRef | None
    entry_form_ref: ArtifactRef | None
    episode: AcceptedEpisodeDirection | None
    episode_ref: ArtifactRef | None
    episode_series_source_ref: ArtifactRef | None
    referenced_commitment_ids: tuple[str, ...]


@dataclass(frozen=True)
class EpisodeDirectionAcceptance:
    """Result of accepting an Episode 1 Direction proposal."""

    direction: AcceptedEpisodeDirection
    already_accepted: bool


@dataclass(frozen=True)
class SeriesEntryFormDeclaration:
    """Result of declaring (or re-declaring) a Series episodic."""

    record: AcceptedSeriesEntryForm
    already_declared: bool
