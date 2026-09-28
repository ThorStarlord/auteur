"""Persistence and service tests for bounded Episode 1 Direction.

Covers acceptance invariants 1-3 and 5-11 of the ratified capability contract:
propose is non-authoritative, explicit acceptance is the only authority
transition, atomicity, series-immutability, idempotent re-acceptance, episodic
availability, entry-form eligibility/lock, and two-way Book/Episode exclusivity.
"""

from pathlib import Path

import pytest
import yaml

from auteur.series.episode_one_direction import EpisodeDirection
from auteur.series.vertical_slice_models import (
    BookDirection,
    SeriesDirection,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService

FIXTURES = Path(__file__).parent / "fixtures" / "archive_of_lies_vertical_slice"
SERIES_FIXTURE = FIXTURES / "series_direction.yaml"
BOOK_FIXTURE = FIXTURES / "book_1_direction.yaml"


def load_series() -> SeriesDirection:
    return SeriesDirection.model_validate(
        yaml.safe_load(SERIES_FIXTURE.read_text(encoding="utf-8"))
    )


def load_book() -> BookDirection:
    return BookDirection.model_validate(
        yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    )


def load_identity() -> dict:
    return yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))["identity"]


def accept_series(service: SeriesVerticalSliceService) -> None:
    proposal = service.propose_series_direction(load_series())
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")


def episode_direction(commitment_ids: list[str]) -> EpisodeDirection:
    return EpisodeDirection(
        episode_number=1,
        identity=load_identity(),
        series_commitment_ids=commitment_ids,
    )


def first_commitment_id() -> str:
    return load_series().commitments[0].commitment_id


def test_declare_requires_accepted_series(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    with pytest.raises(ValueError, match="accepted Series Direction is required"):
        service.declare_series_episodic(declaring_author="author")


def test_declare_rejected_after_accepted_book_direction(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    proposal = service.propose_book_direction(load_book())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    with pytest.raises(ValueError, match="Book Direction"):
        service.declare_series_episodic(declaring_author="author")


def test_declare_is_idempotent_and_preserves_author(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    first = service.declare_series_episodic(declaring_author="author")
    second = service.declare_series_episodic(declaring_author="someone-else")
    assert second == first
    assert second.declaration.declaring_author == "author"
    assert service.load_accepted_episodic_entry_form() == first


def test_propose_requires_episodic_entry_form(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    with pytest.raises(ValueError, match="explicitly episodic"):
        service.propose_episode_direction(episode_direction([first_commitment_id()]))


def test_propose_rejects_unknown_commitment(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declaring_author="author")
    with pytest.raises(ValueError, match="Unknown accepted Series commitment"):
        service.propose_episode_direction(
            episode_direction(["not-a-current-commitment"])
        )


def test_accept_is_explicit_authority_and_preserves_series(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declaring_author="author")
    series_hash_before = service.store.artifact_store.content_hash(
        service.store.accepted_series_direction_path
    )

    proposal = service.propose_episode_direction(
        episode_direction([first_commitment_id()])
    )
    assert service.load_accepted_episode_direction() is None

    result = service.accept_episode_direction(
        proposal.proposal_id, accepted_by="author"
    )
    assert result.changed is True
    assert service.load_accepted_episode_direction() == result.accepted
    assert result.accepted.direction.series_commitment_ids == [
        first_commitment_id()
    ]
    series_hash_after = service.store.artifact_store.content_hash(
        service.store.accepted_series_direction_path
    )
    assert series_hash_after == series_hash_before


def test_reaccept_same_proposal_is_no_change(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declaring_author="author")
    proposal = service.propose_episode_direction(
        episode_direction([first_commitment_id()])
    )
    first = service.accept_episode_direction(
        proposal.proposal_id, accepted_by="author"
    )
    revision_after_first = service.load_episode_direction_metadata().revision

    second = service.accept_episode_direction(
        proposal.proposal_id, accepted_by="author"
    )
    assert second.changed is False
    assert second.accepted == first.accepted
    assert (
        service.load_episode_direction_metadata().revision
        == revision_after_first
    )


def test_moving_series_direction_invalidates_entry_form(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declaring_author="author")
    proposal = service.propose_episode_direction(
        episode_direction([first_commitment_id()])
    )

    changed = load_series().model_copy(
        update={"promise": "A materially different promise."}
    )
    series_proposal = service.propose_series_direction(changed)
    service.accept_series_direction(
        series_proposal.proposal_id, accepted_by="author"
    )

    with pytest.raises(
        ValueError,
        match="does not reference the current accepted Series Direction revision",
    ):
        service.accept_episode_direction(
            proposal.proposal_id, accepted_by="author"
        )
    assert service.load_accepted_episode_direction() is None


def test_book_direction_unavailable_when_episodic(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declaring_author="author")
    with pytest.raises(ValueError, match="unavailable for an explicitly episodic"):
        service.propose_book_direction(load_book())


def test_acceptance_is_all_or_nothing(tmp_path: Path, monkeypatch) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declaring_author="author")
    proposal = service.propose_episode_direction(
        episode_direction([first_commitment_id()])
    )

    def boom(*args, **kwargs):
        raise RuntimeError("injected acceptance failure")

    monkeypatch.setattr(service.store.artifact_store, "accept", boom)
    with pytest.raises(RuntimeError, match="injected acceptance failure"):
        service.accept_episode_direction(proposal.proposal_id, accepted_by="author")

    assert service.load_accepted_episode_direction() is None
    assert service.load_episode_direction_metadata() is None


def test_entry_form_acceptance_is_all_or_nothing(
    tmp_path: Path, monkeypatch
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)

    def boom(*args, **kwargs):
        raise RuntimeError("injected entry-form failure")

    monkeypatch.setattr(service.store.artifact_store, "accept", boom)
    with pytest.raises(RuntimeError, match="injected entry-form failure"):
        service.declare_series_episodic(declaring_author="author")

    assert service.load_accepted_episodic_entry_form() is None
    assert service.store.load_episodic_entry_form_metadata() is None


def test_accept_rejects_unknown_reference_at_acceptance_time(
    tmp_path: Path,
) -> None:
    from auteur.series.episode_one_direction import EpisodeDirectionProposal
    from auteur.series.vertical_slice_models import ArtifactRef

    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declaring_author="author")
    accepted_series = service.load_accepted_series_direction()
    metadata = service.load_series_direction_metadata()
    assert accepted_series is not None and metadata is not None
    bad = episode_direction(["not-a-current-commitment"])
    proposal = EpisodeDirectionProposal(
        proposal_id="episode-direction-stale-accept",
        revision=1,
        direction=bad,
        source_refs=[
            ArtifactRef(
                artifact_id=accepted_series.artifact_id,
                revision=metadata.revision,
            )
        ],
    )
    service.store.save_episode_direction_proposal(proposal)
    with pytest.raises(ValueError, match="Unknown accepted Series commitment"):
        service.accept_episode_direction(proposal.proposal_id, accepted_by="author")
    assert service.load_accepted_episode_direction() is None


def test_different_proposal_identical_content_is_no_change(
    tmp_path: Path,
) -> None:
    from auteur.series.episode_one_direction import EpisodeDirectionProposal
    from auteur.series.vertical_slice_models import ArtifactRef

    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declaring_author="author")
    proposal = service.propose_episode_direction(
        episode_direction([first_commitment_id()])
    )
    first = service.accept_episode_direction(
        proposal.proposal_id, accepted_by="author"
    )
    assert first.changed is True
    accepted_series = service.load_accepted_series_direction()
    metadata = service.load_series_direction_metadata()
    assert accepted_series is not None and metadata is not None
    twin = EpisodeDirectionProposal(
        proposal_id="episode-direction-twin-content",
        revision=1,
        direction=proposal.direction,
        source_refs=[
            ArtifactRef(
                artifact_id=accepted_series.artifact_id,
                revision=metadata.revision,
            )
        ],
    )
    service.store.save_episode_direction_proposal(twin)
    second = service.accept_episode_direction(twin.proposal_id, accepted_by="author")
    assert second.changed is False
    assert second.accepted == first.accepted


def test_book_oriented_project_byte_stable_across_episode_paths(
    tmp_path: Path, capsys
) -> None:
    from auteur.cli import main

    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    book_proposal = service.propose_book_direction(load_book())
    service.accept_book_direction(book_proposal.proposal_id, accepted_by="author")
    series_hash_before = service.store.artifact_store.content_hash(
        service.store.accepted_series_direction_path
    )
    book_hash_before = service.store.artifact_store.content_hash(
        service.store.accepted_book_direction_path(1)
    )
    assert (
        main(["series", "journey", "inspect-episode", str(tmp_path)]) == 0
    )
    assert "Book-oriented" in capsys.readouterr().out
    assert service.load_accepted_book_direction(1) is not None
    assert (
        service.store.artifact_store.content_hash(
            service.store.accepted_series_direction_path
        )
        == series_hash_before
    )
    assert (
        service.store.artifact_store.content_hash(
            service.store.accepted_book_direction_path(1)
        )
        == book_hash_before
    )


def test_inspection_reports_stale_commitments(tmp_path: Path) -> None:
    from auteur.series.episode_one_direction import (
        describe_episode_one_direction_inspection,
    )
    from auteur.series.vertical_slice_formatters import (
        format_episode_one_direction_inspection,
    )

    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declaring_author="author")
    proposal = service.propose_episode_direction(
        episode_direction([first_commitment_id()])
    )
    service.accept_episode_direction(proposal.proposal_id, accepted_by="author")
    accepted_episode = service.load_accepted_episode_direction()
    assert accepted_episode is not None
    current_series = service.load_accepted_series_direction()
    assert current_series is not None
    moved = current_series.model_copy(
        update={
            "direction": current_series.direction.model_copy(
                update={
                    "commitments": [
                        c.model_copy(update={"commitment_id": "replaced-history"})
                        for c in current_series.direction.commitments
                    ]
                }
            )
        }
    )
    inspection = describe_episode_one_direction_inspection(
        moved,
        service.load_accepted_episodic_entry_form(),
        accepted_episode,
    )
    assert inspection.stale_commitment_ids == [first_commitment_id()]
    assert inspection.referenced_commitments == []
    rendered = format_episode_one_direction_inspection(inspection)
    assert "stale" in rendered
    assert first_commitment_id() in rendered
