from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from auteur.provenance import (
    ArtifactMetadata,
    DependencyKind,
    DependencySource,
    Lifecycle,
)
from auteur.series.vertical_slice_models import (
    AcceptedSeriesDirection,
    ArtifactRef,
    BookDirection,
    SeriesDirection,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "archive_of_lies_vertical_slice"
    / "series_direction.yaml"
)
BOOK_FIXTURE = FIXTURE.with_name("book_1_direction.yaml")


def load_direction() -> SeriesDirection:
    return SeriesDirection.model_validate(
        yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    )


def load_book_direction() -> BookDirection:
    return BookDirection.model_validate(
        yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    )


def accept_archive_series(
    service: SeriesVerticalSliceService,
) -> tuple[AcceptedSeriesDirection, ArtifactMetadata]:
    proposal = service.propose_series_direction(load_direction())
    accepted = service.accept_series_direction(
        proposal.proposal_id, accepted_by="archive-author"
    )
    metadata = service.load_series_direction_metadata()
    assert metadata is not None
    return accepted, metadata


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
    assert not (accepted_path.parent / ".staging" / accepted_path.name).exists()


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


def test_accepted_series_direction_requires_metadata_sidecar(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(load_direction())
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_series_direction_metadata()
    assert metadata is not None

    service.store.artifact_store.sidecar_path(metadata.artifact_id).unlink()

    assert service.load_accepted_series_direction() is None


def test_accepted_series_direction_rejects_modified_payload(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(load_direction())
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    accepted_path = service.store.accepted_series_direction_path
    payload = yaml.safe_load(accepted_path.read_text(encoding="utf-8"))
    payload["direction"]["promise"] = "Tampered after acceptance."
    accepted_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    assert service.load_accepted_series_direction() is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_id", "other-artifact"),
        ("artifact_type", "blueprint"),
        ("lifecycle", "draft"),
    ],
)
def test_accepted_series_direction_requires_matching_accepted_metadata(
    tmp_path: Path,
    field: str,
    value: str,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(load_direction())
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_series_direction_metadata()
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload[field] = value
    sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.load_accepted_series_direction() is None


def test_failed_metadata_accept_preserves_previous_series_direction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal_a = service.propose_series_direction(load_direction())
    accepted_a = service.accept_series_direction(
        proposal_a.proposal_id, accepted_by="author"
    )
    metadata_a = service.load_series_direction_metadata()
    assert metadata_a is not None
    revisions_a = service.store.artifact_store.list_revisions(metadata_a.artifact_id)

    direction_b = load_direction().model_copy(
        update={"promise": "A replacement direction that must not be accepted."}
    )
    proposal_b = service.propose_series_direction(direction_b)
    original_accept = service.store.artifact_store.accept

    def fail_accept(*args: object, **kwargs: object) -> None:
        original_accept(*args, **kwargs)
        raise OSError("metadata persistence failed")

    monkeypatch.setattr(service.store.artifact_store, "accept", fail_accept)

    with pytest.raises(OSError, match="metadata persistence failed"):
        service.accept_series_direction(proposal_b.proposal_id, accepted_by="author")

    accepted_path = service.store.accepted_series_direction_path
    assert service.load_accepted_series_direction() == accepted_a
    assert service.load_series_direction_metadata() == metadata_a
    assert service.store.artifact_store.list_revisions(metadata_a.artifact_id) == revisions_a
    assert service.store.artifact_store.content_hash(accepted_path) == metadata_a.content_hash
    assert not (accepted_path.parent / ".staging" / "series-direction.yaml").exists()


@pytest.mark.parametrize(
    ("field", "value"),
    [("book_number", 0), ("series_commitment_ids", [])],
)
def test_book_direction_enforces_local_typed_boundary(
    field: str,
    value: object,
) -> None:
    raw = yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    raw[field] = value

    with pytest.raises(ValidationError, match=field):
        BookDirection.model_validate(raw)


def test_book_direction_rejects_undeclared_fields() -> None:
    raw = yaml.safe_load(BOOK_FIXTURE.read_text(encoding="utf-8"))
    raw["book_plans"] = []

    with pytest.raises(ValidationError, match="book_plans"):
        BookDirection.model_validate(raw)


def test_book_direction_requires_accepted_series_direction(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)

    with pytest.raises(ValueError, match="accepted Series Direction"):
        service.propose_book_direction(load_book_direction())

    assert service.load_accepted_book_direction(1) is None
    assert not (
        tmp_path
        / ".auteur"
        / "series"
        / "vertical-slice"
        / "proposals"
        / "book-direction"
    ).exists()


def test_accepting_book_direction_does_not_mutate_series_direction(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    series_before = service.load_accepted_series_direction()
    metadata_before = service.load_series_direction_metadata()
    series_path = service.store.accepted_series_direction_path
    series_bytes_before = series_path.read_bytes()

    proposal = service.propose_book_direction(load_book_direction())
    accepted = service.accept_book_direction(
        proposal.proposal_id,
        accepted_by="archive-author",
        rationale="This Book exposes the first consequential archival lie.",
    )

    assert service.load_accepted_book_direction(1) == accepted
    assert service.load_accepted_series_direction() == series_before
    assert service.load_series_direction_metadata() == metadata_before
    assert series_path.read_bytes() == series_bytes_before

    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    assert metadata.artifact_id == "book-1-direction"
    assert metadata.artifact_type == "book_direction"
    assert metadata.lifecycle is Lifecycle.ACCEPTED
    assert metadata.accepted_by == "archive-author"
    assert metadata.rationale == "This Book exposes the first consequential archival lie."
    assert len(metadata.dependencies) == 1
    dependency = metadata.dependencies[0]
    assert dependency.artifact_id == "series-direction"
    assert dependency.artifact_type == "series_direction"
    assert dependency.kind is DependencyKind.SEMANTIC
    assert dependency.source is DependencySource.DECLARED
    assert dependency.revision == metadata_before.revision
    assert dependency.fields == []
    assert dependency.projection.id == "full"
    assert Path(dependency.path) == Path(
        ".auteur/series/vertical-slice/accepted/series-direction.yaml"
    )

    accepted_path = service.store.accepted_book_direction_path(1)
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


def test_unaccepted_book_direction_has_no_authority(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accepted_series, series_metadata = accept_archive_series(service)

    proposal = service.propose_book_direction(load_book_direction())

    assert service.load_book_direction_proposal(proposal.proposal_id) == proposal
    assert proposal.source_refs == [
        ArtifactRef(
            artifact_id=accepted_series.artifact_id,
            revision=series_metadata.revision,
        )
    ]
    assert service.load_accepted_book_direction(1) is None
    assert service.load_book_direction_metadata(1) is None
    assert service.store.book_direction_proposal_path(
        1, proposal.proposal_id
    ).is_file()
    assert not service.store.accepted_book_direction_path(1).exists()


def test_book_direction_reload_preserves_book_number_commitment_refs_and_source(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accepted_series, series_metadata = accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    accepted = service.accept_book_direction(
        proposal.proposal_id, accepted_by="archive-author"
    )

    reloaded = SeriesVerticalSliceService(tmp_path)
    reloaded_proposal = reloaded.load_book_direction_proposal(proposal.proposal_id)
    reloaded_accepted = reloaded.load_accepted_book_direction(1)
    reloaded_metadata = reloaded.load_book_direction_metadata(1)

    assert reloaded_accepted == accepted
    assert reloaded_accepted.direction.book_number == 1
    assert reloaded_accepted.direction.series_commitment_ids == [
        "contested-history"
    ]
    assert reloaded_proposal.source_refs == [
        ArtifactRef(
            artifact_id=accepted_series.artifact_id,
            revision=series_metadata.revision,
        )
    ]
    assert reloaded_metadata is not None
    assert [dependency.revision for dependency in reloaded_metadata.dependencies] == [
        series_metadata.revision
    ]


def test_book_direction_rejects_unknown_series_commitment(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    invalid = load_book_direction().model_copy(
        update={"series_commitment_ids": ["invented-commitment"]}
    )

    with pytest.raises(ValueError, match="invented-commitment"):
        service.propose_book_direction(invalid)

    assert not (
        service.store.root / "proposals" / "book-direction"
    ).exists()


def test_accepting_unknown_book_direction_proposal_is_rejected(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)

    with pytest.raises(FileNotFoundError, match="Unknown Book Direction proposal"):
        service.accept_book_direction("missing-proposal", accepted_by="author")

    assert service.load_accepted_book_direction(1) is None
    assert service.load_book_direction_metadata(1) is None


def test_accepted_book_direction_rejects_modified_payload(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    accepted_path = service.store.accepted_book_direction_path(1)
    payload = yaml.safe_load(accepted_path.read_text(encoding="utf-8"))
    payload["direction"]["identity"]["title"] = "Tampered after acceptance"
    accepted_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    assert service.load_accepted_book_direction(1) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_id", "other-artifact"),
        ("artifact_type", "blueprint"),
        ("lifecycle", "draft"),
        ("dependencies", []),
    ],
)
def test_accepted_book_direction_requires_matching_accepted_metadata(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload[field] = value
    sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.load_accepted_book_direction(1) is None


def test_accepted_book_direction_rejects_invented_dependency_revision(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload["dependencies"][0]["revision"] = 999
    sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.load_accepted_book_direction(1) is None


def test_accepted_book_direction_rejects_altered_projected_hash(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload["dependencies"][0]["projected_hash"] = "sha256:altered"
    sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.load_accepted_book_direction(1) is None


def test_accepted_book_direction_rejects_altered_full_content_hash(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    metadata = service.load_book_direction_metadata(1)
    assert metadata is not None
    sidecar = service.store.artifact_store.sidecar_path(metadata.artifact_id)
    payload = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
    payload["dependencies"][0]["full_content_hash"] = "sha256:altered"
    sidecar.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    assert service.load_accepted_book_direction(1) is None


def test_book_acceptance_requires_valid_current_series_authority(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    series_sidecar = service.store.artifact_store.sidecar_path("series-direction")
    payload = yaml.safe_load(series_sidecar.read_text(encoding="utf-8"))
    payload["lifecycle"] = "draft"
    series_sidecar.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="accepted Series Direction"):
        service.accept_book_direction(proposal.proposal_id, accepted_by="author")

    assert not service.store.accepted_book_direction_path(1).exists()
    assert service.load_book_direction_metadata(1) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_id", "other-artifact"),
        ("artifact_type", "blueprint"),
        ("lifecycle", "draft"),
        ("content_hash", "sha256:altered"),
    ],
)
def test_accepted_book_direction_requires_valid_series_dependency_revision(
    tmp_path: Path,
    field: str,
    value: str,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    service.accept_book_direction(proposal.proposal_id, accepted_by="author")
    revision_path = (
        service.store.artifact_store.root
        / "revisions"
        / "series-direction"
        / "000001.yaml"
    )
    payload = yaml.safe_load(revision_path.read_text(encoding="utf-8"))
    payload[field] = value
    revision_path.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )

    assert service.load_accepted_book_direction(1) is None


@pytest.mark.parametrize(
    "tamper",
    ["missing", "invalid_lifecycle", "mismatched_hash"],
)
def test_book_acceptance_validates_series_revision_before_writing(
    tmp_path: Path,
    tamper: str,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal = service.propose_book_direction(load_book_direction())
    revision_path = (
        service.store.artifact_store.root
        / "revisions"
        / "series-direction"
        / "000001.yaml"
    )
    if tamper == "missing":
        revision_path.unlink()
    else:
        payload = yaml.safe_load(revision_path.read_text(encoding="utf-8"))
        if tamper == "invalid_lifecycle":
            payload["lifecycle"] = "draft"
        else:
            payload["content_hash"] = "sha256:mismatched"
        revision_path.write_text(
            yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
        )

    with pytest.raises(ValueError, match="Series Direction dependency revision"):
        service.accept_book_direction(proposal.proposal_id, accepted_by="author")

    accepted_path = service.store.accepted_book_direction_path(1)
    assert not accepted_path.exists()
    assert service.load_book_direction_metadata(1) is None
    assert service.store.artifact_store.list_revisions("book-1-direction") == []
    assert not (accepted_path.parent / ".staging" / accepted_path.name).exists()


def test_accepted_book_direction_remains_loadable_when_series_becomes_stale(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    book_proposal = service.propose_book_direction(load_book_direction())
    accepted_book = service.accept_book_direction(
        book_proposal.proposal_id, accepted_by="author"
    )
    book_metadata = service.load_book_direction_metadata(1)
    assert book_metadata is not None
    assert book_metadata.dependencies[0].revision == 1

    revised_series = load_direction().model_copy(
        update={"promise": "Every recovered account changes who controls history."}
    )
    series_proposal = service.propose_series_direction(revised_series)
    service.accept_series_direction(series_proposal.proposal_id, accepted_by="author")

    assert service.load_accepted_book_direction(1) == accepted_book
    preserved_metadata = service.load_book_direction_metadata(1)
    assert preserved_metadata is not None
    assert preserved_metadata.dependencies[0].revision == 1
    status = service.store.artifact_store.status(
        service.store.accepted_book_direction_path(1), "book_direction"
    )
    assert status.lifecycle is Lifecycle.ACCEPTED
    assert status.freshness == "stale"
    assert status.stale_reasons[0].previous_revision == 1
    assert status.stale_reasons[0].current_revision == 2


def test_failed_book_metadata_accept_preserves_previous_book_direction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_archive_series(service)
    proposal_a = service.propose_book_direction(load_book_direction())
    accepted_a = service.accept_book_direction(
        proposal_a.proposal_id, accepted_by="author"
    )
    metadata_a = service.load_book_direction_metadata(1)
    assert metadata_a is not None
    accepted_path = service.store.accepted_book_direction_path(1)
    accepted_bytes_a = accepted_path.read_bytes()
    revisions_a = service.store.artifact_store.list_revisions(
        metadata_a.artifact_id
    )

    replacement_identity = load_book_direction().identity.model_copy(
        update={"title": "The Counterfeit Ledger"}
    )
    replacement = load_book_direction().model_copy(
        update={"identity": replacement_identity}
    )
    proposal_b = service.propose_book_direction(replacement)
    original_accept = service.store.artifact_store.accept

    def fail_accept(*args: object, **kwargs: object) -> None:
        original_accept(*args, **kwargs)
        raise OSError("book metadata persistence failed")

    monkeypatch.setattr(service.store.artifact_store, "accept", fail_accept)

    with pytest.raises(OSError, match="book metadata persistence failed"):
        service.accept_book_direction(proposal_b.proposal_id, accepted_by="author")

    assert service.load_accepted_book_direction(1) == accepted_a
    assert service.load_book_direction_metadata(1) == metadata_a
    assert accepted_path.read_bytes() == accepted_bytes_a
    assert service.store.artifact_store.list_revisions(metadata_a.artifact_id) == (
        revisions_a
    )
    assert not (accepted_path.parent / ".staging" / accepted_path.name).exists()
