import dataclasses
from pathlib import Path

import pytest
import yaml

from auteur.series.episode_direction import (
    DEFAULT_ENTRY_FORM,
    EpisodeDirectionAcceptance,
    EpisodeDirectionInspection,
    SeriesEntryFormDeclaration,
    interpret_entry_form,
)
from auteur.series.vertical_slice_models import (
    AcceptedEpisodeDirection,
    AcceptedSeriesEntryForm,
    ArtifactRef,
    EpisodeDirection,
    SeriesDirection,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "archive_of_lies_vertical_slice"
    / "series_direction.yaml"
)
BOOK_FIXTURE = FIXTURE.with_name("book_1_direction.yaml")


def _load_series_direction() -> SeriesDirection:
    return SeriesDirection.model_validate(
        yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    )


def _load_episode_direction() -> EpisodeDirection:
    raw = yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    return EpisodeDirection.model_validate(
        {
            "identity": raw["identity"],
            "series_commitment_ids": raw["series_commitment_ids"],
        }
    )


def test_default_entry_form_is_book() -> None:
    assert DEFAULT_ENTRY_FORM == "book"


def test_interpret_entry_form_none_is_book() -> None:
    assert interpret_entry_form(None) == "book"


def test_interpret_entry_form_episodic_record_is_episodic() -> None:
    record = AcceptedSeriesEntryForm(entry_form="episodic", declared_by="author")

    assert interpret_entry_form(record) == "episodic"


def test_episode_direction_inspection_is_frozen() -> None:
    inspection = EpisodeDirectionInspection(
        series=_load_series_direction(),
        series_ref=ArtifactRef(artifact_id="series-direction", revision=1),
        entry_form_ref=None,
        episode=None,
        episode_ref=None,
        episode_series_source_ref=None,
        referenced_commitment_ids=(),
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        inspection.series = _load_series_direction()  # type: ignore[misc]


def test_episode_direction_acceptance_is_frozen() -> None:
    accepted = AcceptedEpisodeDirection(
        proposal_id="episode-direction-1",
        direction=_load_episode_direction(),
    )
    acceptance = EpisodeDirectionAcceptance(
        direction=accepted, already_accepted=False
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        acceptance.already_accepted = True  # type: ignore[misc]


def test_series_entry_form_declaration_is_frozen() -> None:
    record = AcceptedSeriesEntryForm(entry_form="episodic", declared_by="author")
    declaration = SeriesEntryFormDeclaration(record=record, already_declared=False)

    with pytest.raises(dataclasses.FrozenInstanceError):
        declaration.already_declared = True  # type: ignore[misc]


def test_episode_direction_inspection_carries_series_and_distinct_refs() -> None:
    accepted = AcceptedEpisodeDirection(
        proposal_id="episode-direction-1",
        direction=_load_episode_direction(),
    )
    series_ref = ArtifactRef(artifact_id="series-direction", revision=2)
    episode_series_source_ref = ArtifactRef(
        artifact_id="series-direction", revision=1
    )

    inspection = EpisodeDirectionInspection(
        series=_load_series_direction(),
        series_ref=series_ref,
        entry_form_ref=None,
        episode=accepted,
        episode_ref=ArtifactRef(artifact_id="episode-1-direction", revision=1),
        episode_series_source_ref=episode_series_source_ref,
        referenced_commitment_ids=("contested-history",),
    )

    assert isinstance(inspection.series, SeriesDirection)
    assert inspection.series_ref != inspection.episode_series_source_ref
    assert inspection.referenced_commitment_ids == ("contested-history",)
