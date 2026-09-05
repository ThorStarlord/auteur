from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from auteur.series.vertical_slice_models import (
    AcceptedEpisodeDirection,
    AcceptedSeriesEntryForm,
    ArtifactRef,
    BookDirection,
    EpisodeDirection,
    EpisodeDirectionProposal,
    SeriesDirection,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "archive_of_lies_vertical_slice"
SERIES_FIXTURE = FIXTURE_ROOT / "series_direction.yaml"
BOOK_FIXTURE = FIXTURE_ROOT / "book_1_direction.yaml"


def _load_series_direction() -> SeriesDirection:
    return SeriesDirection.model_validate(
        yaml.safe_load(SERIES_FIXTURE.read_text(encoding="utf-8"))
    )


def _load_book_direction() -> BookDirection:
    return BookDirection.model_validate(
        yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    )


def _episode_direction_payload() -> dict:
    raw = yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    return {
        "identity": raw["identity"],
        "series_commitment_ids": raw["series_commitment_ids"],
    }


def _load_episode_direction() -> EpisodeDirection:
    return EpisodeDirection.model_validate(_episode_direction_payload())


def _accept_series(service: SeriesVerticalSliceService) -> ArtifactRef:
    proposal = service.propose_series_direction(_load_series_direction())
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_series_direction_metadata()
    assert metadata is not None
    return ArtifactRef(artifact_id="series-direction", revision=metadata.revision)


def _advance_series(service: SeriesVerticalSliceService) -> ArtifactRef:
    revised = _load_series_direction().model_copy(
        update={"promise": "Every recovered account changes who controls history."}
    )
    proposal = service.propose_series_direction(revised)
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_series_direction_metadata()
    assert metadata is not None
    return ArtifactRef(artifact_id="series-direction", revision=metadata.revision)


# ---------------------------------------------------------------------------
# Entry-form persistence
# ---------------------------------------------------------------------------


def test_save_accepted_series_entry_form_writes_file_and_sidecar(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    current_source = _accept_series(service)
    record = AcceptedSeriesEntryForm(entry_form="episodic", declared_by="author")

    metadata = service.store.save_accepted_series_entry_form(
        record, series_source=current_source
    )

    assert service.store.accepted_series_entry_form_path.is_file()
    assert metadata.accepted_by == record.declared_by
    assert metadata.accepted_at is not None
    assert (
        datetime.fromisoformat(metadata.accepted_at).utcoffset()
        == timezone.utc.utcoffset(None)
    )
    assert len(metadata.dependencies) == 1
    dependency = metadata.dependencies[0]
    assert dependency.artifact_id == "series-direction"
    assert dependency.path == str(
        service.store.accepted_series_direction_path.resolve().relative_to(
            tmp_path.resolve()
        )
    )
    persisted = yaml.safe_load(
        service.store.accepted_series_entry_form_path.read_text(encoding="utf-8")
    )
    assert persisted == record.model_dump(mode="json")


def test_save_accepted_series_entry_form_staging_failure_restores_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    current_source = _accept_series(service)
    record = AcceptedSeriesEntryForm(entry_form="episodic", declared_by="author")

    def _boom(self, path, model) -> None:
        raise RuntimeError("staging failure")

    monkeypatch.setattr(
        service.store.__class__, "_write_model", _boom
    )

    with pytest.raises(RuntimeError, match="staging failure"):
        service.store.save_accepted_series_entry_form(
            record, series_source=current_source
        )

    assert not service.store.accepted_series_entry_form_path.is_file()
    assert service.store.load_accepted_series_entry_form() is None


def test_load_accepted_series_entry_form_survives_series_advance(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    current_source = _accept_series(service)
    record = AcceptedSeriesEntryForm(entry_form="episodic", declared_by="author")
    service.store.save_accepted_series_entry_form(
        record, series_source=current_source
    )

    _advance_series(service)

    loaded = service.store.load_accepted_series_entry_form()
    assert loaded == record


@pytest.mark.parametrize(
    "corrupt",
    ["missing_sidecar", "wrong_type", "wrong_hash", "wrong_dependency_count"],
)
def test_load_accepted_series_entry_form_returns_none_when_invalid(
    tmp_path: Path, corrupt: str
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    current_source = _accept_series(service)
    record = AcceptedSeriesEntryForm(entry_form="episodic", declared_by="author")
    service.store.save_accepted_series_entry_form(
        record, series_source=current_source
    )
    path = service.store.accepted_series_entry_form_path
    sidecar = service.store.artifact_store.sidecar_path(path.stem)

    if corrupt == "missing_sidecar":
        sidecar.unlink()
    elif corrupt == "wrong_type":
        payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
        payload["artifact_type"] = "not_series_entry_form"
        sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    elif corrupt == "wrong_hash":
        payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
        payload["content_hash"] = "sha256:0" * 8
        sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    elif corrupt == "wrong_dependency_count":
        payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
        payload["dependencies"] = []
        sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.store.load_accepted_series_entry_form() is None


# ---------------------------------------------------------------------------
# has_any_book_direction_work
# ---------------------------------------------------------------------------


def test_has_any_book_direction_work_false_when_no_work(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    _accept_series(service)

    assert service.store.has_any_book_direction_work() is False


def test_has_any_book_direction_work_true_for_nested_proposal_book_1(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    _accept_series(service)
    service.propose_book_direction(_load_book_direction())

    assert service.store.has_any_book_direction_work() is True


def test_has_any_book_direction_work_true_for_nested_proposal_book_2(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    _accept_series(service)
    proposal = service.store.save_book_direction_proposal
    from auteur.series.vertical_slice_models import BookDirectionProposal

    book_2_direction = _load_book_direction().model_copy(
        update={"book_number": 2}
    )
    proposal(
        BookDirectionProposal(
            proposal_id="book-direction-book-2-test",
            revision=1,
            direction=book_2_direction,
            source_refs=[ArtifactRef(artifact_id="series-direction", revision=1)],
        )
    )

    assert service.store.has_any_book_direction_work() is True


def test_has_any_book_direction_work_true_for_accepted_book_1(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    _accept_series(service)
    proposal = service.propose_book_direction(_load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")

    assert service.store.has_any_book_direction_work() is True


def test_has_any_book_direction_work_true_for_accepted_book_2(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    _accept_series(service)
    proposal = service.propose_book_direction(_load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    # Fabricate an accepted Book 2 direction file directly (real accepted shape).
    accepted_book_1 = service.load_accepted_book_direction(1)
    assert accepted_book_1 is not None
    book_2_path = service.store.accepted_book_direction_path(2)
    book_2_path.parent.mkdir(parents=True, exist_ok=True)
    book_2_path.write_text(
        yaml.safe_dump(
            accepted_book_1.model_copy(
                update={
                    "artifact_id": "book-2-direction",
                    "direction": accepted_book_1.direction.model_copy(
                        update={"book_number": 2}
                    ),
                }
            ).model_dump(mode="json"),
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    assert service.store.has_any_book_direction_work() is True


def test_has_any_book_direction_work_false_again_after_removal(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    _accept_series(service)
    proposal = service.propose_book_direction(_load_book_direction())
    proposal_path = service.store._find_book_direction_proposal_path(
        proposal.proposal_id
    )
    proposal_path.unlink()

    assert service.store.has_any_book_direction_work() is False


# ---------------------------------------------------------------------------
# Episode Direction proposal persistence
# ---------------------------------------------------------------------------


def test_episode_direction_proposal_round_trips(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = EpisodeDirectionProposal(
        proposal_id="episode-direction-test",
        revision=1,
        direction=_load_episode_direction(),
        source_refs=[ArtifactRef(artifact_id="series-direction", revision=1)],
    )

    service.store.save_episode_direction_proposal(proposal)
    loaded = service.store.load_episode_direction_proposal(proposal.proposal_id)

    assert loaded == proposal


def test_episode_direction_proposal_path_rejects_path_separators(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)

    with pytest.raises(FileNotFoundError):
        service.store.episode_direction_proposal_path("../escape")


# ---------------------------------------------------------------------------
# Accepted Episode Direction persistence
# ---------------------------------------------------------------------------


def test_save_accepted_episode_direction_persists_supplied_model_and_revisions(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    current_source = _accept_series(service)
    entry_form = AcceptedSeriesEntryForm(
        entry_form="episodic", declared_by="author"
    )
    service.store.save_accepted_series_entry_form(
        entry_form, series_source=current_source
    )
    accepted_1 = AcceptedEpisodeDirection(
        proposal_id="episode-direction-1", direction=_load_episode_direction()
    )

    metadata_1 = service.store.save_accepted_episode_direction(
        accepted_1,
        series_source=current_source,
        accepted_by="author",
        rationale=None,
    )
    assert metadata_1.revision == 1
    persisted = yaml.safe_load(
        service.store.accepted_episode_direction_path.read_text(encoding="utf-8")
    )
    assert persisted == accepted_1.model_dump(mode="json")

    accepted_2 = AcceptedEpisodeDirection(
        proposal_id="episode-direction-2", direction=_load_episode_direction()
    )
    metadata_2 = service.store.save_accepted_episode_direction(
        accepted_2,
        series_source=current_source,
        accepted_by="author",
        rationale="revision",
    )
    assert metadata_2.revision == 2


def test_save_accepted_episode_direction_injected_failure_leaves_nothing_authoritative(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    current_source = _accept_series(service)
    accepted = AcceptedEpisodeDirection(
        proposal_id="episode-direction-1", direction=_load_episode_direction()
    )

    def _boom(*args, **kwargs):
        raise RuntimeError("accept failure")

    monkeypatch.setattr(service.store.artifact_store, "accept", _boom)

    with pytest.raises(RuntimeError, match="accept failure"):
        service.store.save_accepted_episode_direction(
            accepted,
            series_source=current_source,
            accepted_by="author",
            rationale=None,
        )

    assert not service.store.accepted_episode_direction_path.is_file()
    assert service.store.load_accepted_episode_direction() is None
    staging_dir = service.store.accepted_episode_direction_path.parent / ".staging"
    assert not staging_dir.exists()


def test_load_accepted_episode_direction_is_none_before_first_accept(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    _accept_series(service)

    assert service.store.load_accepted_episode_direction() is None
    assert service.store.load_episode_direction_metadata() is None


def test_load_accepted_episode_direction_survives_series_advance(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    current_source = _accept_series(service)
    accepted = AcceptedEpisodeDirection(
        proposal_id="episode-direction-1", direction=_load_episode_direction()
    )
    service.store.save_accepted_episode_direction(
        accepted, series_source=current_source, accepted_by="author", rationale=None
    )

    _advance_series(service)

    loaded = service.store.load_accepted_episode_direction()
    metadata = service.store.load_episode_direction_metadata()
    assert loaded == accepted
    assert metadata is not None
    assert metadata.dependencies[0].revision == current_source.revision
