from pathlib import Path

import pytest
import yaml

from auteur.provenance import Lifecycle
from auteur.series.vertical_slice_models import SeriesDirection
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "archive_of_lies_vertical_slice"
    / "series_direction.yaml"
)


def load_direction() -> SeriesDirection:
    return SeriesDirection.model_validate(
        yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    )


def test_proposal_round_trips_without_becoming_accepted(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)

    proposal = service.propose_series_direction(load_direction())

    assert service.load_series_direction_proposal(proposal.proposal_id) == proposal
    assert service.load_accepted_series_direction() is None
    assert service.load_series_direction_metadata() is None
    assert (
        tmp_path
        / ".auteur"
        / "series"
        / "vertical-slice"
        / "proposals"
        / "series-direction"
        / f"{proposal.proposal_id}.yaml"
    ).is_file()
    assert not (tmp_path / ".auteur" / "series" / "vertical-slice" / "accepted").exists()
    assert not (
        tmp_path
        / ".auteur"
        / "series"
        / "vertical-slice"
        / "derived"
        / "canonical-state.yaml"
    ).exists()


def test_acceptance_round_trip_preserves_author_and_source_revision(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(load_direction())

    accepted = service.accept_series_direction(
        proposal.proposal_id,
        accepted_by="archive-author",
        rationale="This is the intended long-horizon promise.",
    )

    assert service.load_accepted_series_direction() == accepted
    assert accepted.proposal_id == proposal.proposal_id
    assert accepted.direction == proposal.direction
    assert service.load_series_direction_proposal(accepted.proposal_id).revision == 1

    metadata = service.load_series_direction_metadata()
    assert metadata is not None
    assert metadata.artifact_id == accepted.artifact_id
    assert metadata.lifecycle is Lifecycle.ACCEPTED
    assert metadata.accepted_by == "archive-author"
    assert metadata.rationale == "This is the intended long-horizon promise."
    assert metadata.revision == 1
    assert metadata.dependencies == []

    accepted_path = (
        tmp_path
        / ".auteur"
        / "series"
        / "vertical-slice"
        / "accepted"
        / "series-direction.yaml"
    )
    stored_payload = yaml.safe_load(accepted_path.read_text(encoding="utf-8"))
    assert stored_payload == accepted.model_dump(mode="json")
    assert {
        "accepted_by",
        "accepted_at",
        "revision",
        "content_hash",
        "dependencies",
        "freshness",
    }.isdisjoint(stored_payload)
    assert not accepted_path.with_suffix(".tmp").exists()


def test_accepting_unknown_series_direction_proposal_is_rejected(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)

    with pytest.raises(FileNotFoundError, match="Unknown Series Direction proposal"):
        service.accept_series_direction("missing-proposal", accepted_by="author")

    assert service.load_accepted_series_direction() is None
    assert service.load_series_direction_metadata() is None


def test_new_proposal_does_not_modify_accepted_series_direction(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    first = service.propose_series_direction(load_direction())
    service.accept_series_direction(first.proposal_id, accepted_by="author")
    accepted_before = service.load_accepted_series_direction()
    metadata_before = service.load_series_direction_metadata()

    alternative = load_direction().model_copy(
        update={"open_question": "Will preserving every truth destroy the people it names?"}
    )
    service.propose_series_direction(alternative)

    assert service.load_accepted_series_direction() == accepted_before
    assert service.load_series_direction_metadata() == metadata_before
