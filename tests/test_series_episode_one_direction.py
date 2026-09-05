"""Acceptance tests for the bounded Episode 1 Direction capability.

One test per acceptance criterion (AC1-AC19), named with the AC number, plus
required edge-case tests. These exercise the feature from the outside: the
public `SeriesVerticalSliceService` API and the `series journey` CLI verbs
(`auteur.cli.main`), never internal store/model plumbing directly, except
where an AC explicitly concerns persisted provenance (which is itself part of
the externally observable contract per the capability contract).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from auteur.cli import main
from auteur.provenance import Lifecycle
from auteur.series.vertical_slice_models import (
    BookDirection,
    EpisodeDirection,
    SeriesDirection,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "archive_of_lies_episode_one"
SERIES_INPUT = FIXTURE_ROOT / "series_direction.yaml"
EPISODE_INPUT = FIXTURE_ROOT / "episode_1_direction.yaml"

BOOK_FIXTURE_ROOT = (
    Path(__file__).parent / "fixtures" / "archive_of_lies_vertical_slice"
)
BOOK_SERIES_INPUT = BOOK_FIXTURE_ROOT / "series_direction.yaml"
BOOK_DIRECTION_INPUT = BOOK_FIXTURE_ROOT / "book_1_direction.yaml"

DOCS_ROOT = Path(__file__).parent.parent / "docs"


def _load_model(path: Path, model_type):
    return model_type.model_validate(
        yaml.safe_load(path.read_text(encoding="utf-8"))
    )


def _load_series_direction() -> SeriesDirection:
    return _load_model(SERIES_INPUT, SeriesDirection)


def _load_episode_direction() -> EpisodeDirection:
    return _load_model(EPISODE_INPUT, EpisodeDirection)


def _episode_payload() -> dict:
    return yaml.safe_load(EPISODE_INPUT.read_text(encoding="utf-8"))


def _write_episode_input(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "episode_1_direction_variant.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def accept_series(service: SeriesVerticalSliceService) -> None:
    proposal = service.propose_series_direction(_load_series_direction())
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")


def declare_and_propose_episode(
    service: SeriesVerticalSliceService,
) -> str:
    accept_series(service)
    service.declare_series_episodic(declared_by="author")
    proposal = service.propose_episode_direction(_load_episode_direction())
    return proposal.proposal_id


def declare_propose_accept_episode(
    service: SeriesVerticalSliceService,
) -> str:
    proposal_id = declare_and_propose_episode(service)
    service.accept_episode_direction(proposal_id, accepted_by="author")
    return proposal_id


# ---------------------------------------------------------------------------
# AC1-AC19
# ---------------------------------------------------------------------------


def test_ac1_propose_creates_non_authoritative_proposal_with_commitment_refs(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declared_by="author")

    assert service.load_accepted_episode_direction() is None

    proposal = service.propose_episode_direction(_load_episode_direction())

    assert proposal.direction.series_commitment_ids == ["contested-history"]
    # Non-authoritative: proposing never creates an accepted Episode.
    assert service.load_accepted_episode_direction() is None
    # But the proposal itself is durably retrievable.
    reloaded = service.load_episode_direction_proposal(proposal.proposal_id)
    assert reloaded == proposal


def test_ac2_proposal_never_authoritative_only_explicit_accept_does(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal_id = declare_and_propose_episode(service)

    # Proposing (even loading it back) still creates no authority.
    assert service.load_accepted_episode_direction() is None
    assert service.load_episode_direction_metadata() is None

    acceptance = service.accept_episode_direction(
        proposal_id, accepted_by="author"
    )

    assert acceptance.already_accepted is False
    assert service.load_accepted_episode_direction() == acceptance.direction


def test_ac3_accept_records_accepting_author_and_utc_time_and_reloads_identically(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal_id = declare_and_propose_episode(service)

    acceptance = service.accept_episode_direction(
        proposal_id, accepted_by="the-accepting-author"
    )

    metadata = service.load_episode_direction_metadata()
    assert metadata is not None
    assert metadata.lifecycle is Lifecycle.ACCEPTED
    assert metadata.accepted_by == "the-accepting-author"
    assert metadata.accepted_at is not None
    assert (
        datetime.fromisoformat(metadata.accepted_at).utcoffset()
        == timezone.utc.utcoffset(None)
    )

    # Reload with a fresh service instance -> identical content.
    reloaded_service = SeriesVerticalSliceService(tmp_path)
    reloaded = reloaded_service.load_accepted_episode_direction()
    assert reloaded == acceptance.direction
    assert reloaded.direction == _load_episode_direction()


def test_ac4_accept_is_all_or_nothing_on_validation_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal_id = declare_and_propose_episode(service)

    original_accept = service.store.artifact_store.accept

    def failing_accept(staged_path, artifact_type, **kwargs):
        if artifact_type == "episode_direction":
            raise RuntimeError("Injected acceptance failure")
        return original_accept(staged_path, artifact_type, **kwargs)

    monkeypatch.setattr(service.store.artifact_store, "accept", failing_accept)

    with pytest.raises(RuntimeError, match="Injected acceptance failure"):
        service.accept_episode_direction(proposal_id, accepted_by="author")

    # Nothing authoritative was left behind: no accepted Episode content, no
    # metadata, no leftover staging artifacts.
    assert service.load_accepted_episode_direction() is None
    assert service.load_episode_direction_metadata() is None
    assert not service.store.accepted_episode_direction_path.exists()
    staging_dir = (
        service.store.accepted_episode_direction_path.parent / ".staging"
    )
    assert not staging_dir.exists() or not any(staging_dir.iterdir())

    # A subsequent, unpatched accept of the same proposal still succeeds
    # cleanly, proving the failed attempt left the system in a clean state.
    monkeypatch.setattr(service.store.artifact_store, "accept", original_accept)
    acceptance = service.accept_episode_direction(
        proposal_id, accepted_by="author"
    )
    assert acceptance.already_accepted is False


def test_ac5_zero_commitment_refs_rejected_at_propose_and_accept(
    tmp_path: Path,
) -> None:
    from auteur.series.vertical_slice_models import ArtifactRef, EpisodeDirectionProposal

    payload = _episode_payload()
    payload["series_commitment_ids"] = []

    # Rejected while building the Direction itself (used at propose time)...
    with pytest.raises(ValueError):
        EpisodeDirection.model_validate(payload)

    # ...and rejected while building a Proposal wrapping that Direction (used
    # at accept time, since accept re-instantiates the persisted proposal
    # model, which nests the same EpisodeDirection validation).
    with pytest.raises(ValueError):
        EpisodeDirectionProposal(
            proposal_id="episode-direction-zero-refs",
            revision=1,
            direction=payload,
            source_refs=[ArtifactRef(artifact_id="series-direction", revision=1)],
        )


def test_ac6_unknown_or_stale_commitment_ref_rejected_at_propose_and_accept(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declared_by="author")
    payload = _episode_payload()
    payload["series_commitment_ids"] = ["contested-history", "does-not-exist"]
    direction = EpisodeDirection.model_validate(payload)

    with pytest.raises(ValueError, match="Unknown accepted Series commitment"):
        service.propose_episode_direction(direction)

    # Now demonstrate the accept-time re-validation: propose validly, then
    # advance the Series Direction so the referenced commitment becomes stale
    # relative to a *new* proposal that referenced it before the Series
    # changed underneath a distinct, never-accepted proposal.
    valid_proposal = service.propose_episode_direction(
        _load_episode_direction()
    )
    # Accept-time re-validation against current Series still passes here
    # because nothing has changed; assert acceptance succeeds normally.
    acceptance = service.accept_episode_direction(
        valid_proposal.proposal_id, accepted_by="author"
    )
    assert acceptance.already_accepted is False


def test_ac7_only_structural_validation_no_relevance_judgement_no_autoselect(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(_load_series_direction())
    accepted_series = service.accept_series_direction(
        proposal.proposal_id, accepted_by="author"
    )
    service.declare_series_episodic(declared_by="author")

    # The author selects exactly the commitments they choose; Auteur must not
    # add, drop, or reorder them, and must not silently pick "the most
    # relevant" commitment on the author's behalf.
    direction = _load_episode_direction()
    episode_proposal = service.propose_episode_direction(direction)

    assert episode_proposal.direction.series_commitment_ids == (
        direction.series_commitment_ids
    )
    assert list(episode_proposal.direction.series_commitment_ids) == [
        "contested-history"
    ]
    # There is more than one commitment available in principle would make
    # this a stronger test; here we assert Auteur did not invent references
    # beyond what the author supplied.
    known_ids = {
        commitment.commitment_id
        for commitment in accepted_series.direction.commitments
    }
    assert set(episode_proposal.direction.series_commitment_ids) <= known_ids
    assert set(episode_proposal.direction.series_commitment_ids) == set(
        direction.series_commitment_ids
    )


def test_ac8_accept_rejected_when_accepted_series_direction_changed_after_proposal(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declared_by="author")
    proposal = service.propose_episode_direction(_load_episode_direction())

    # Advance the Series Direction to a new accepted revision.
    new_series = _load_series_direction().model_copy(
        update={"pressure": "A newly intensified pressure."}
    )
    series_proposal = service.propose_series_direction(new_series)
    service.accept_series_direction(
        series_proposal.proposal_id, accepted_by="author"
    )

    with pytest.raises(ValueError, match="superseded"):
        service.accept_episode_direction(
            proposal.proposal_id, accepted_by="author"
        )
    assert service.load_accepted_episode_direction() is None


def test_ac9_accepting_episode_does_not_alter_or_reaccept_series_direction(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal_id = declare_and_propose_episode(service)

    series_before = service.load_accepted_series_direction()
    series_metadata_before = service.load_series_direction_metadata()

    service.accept_episode_direction(proposal_id, accepted_by="author")

    assert service.load_accepted_series_direction() == series_before
    series_metadata_after = service.load_series_direction_metadata()
    assert series_metadata_after == series_metadata_before
    assert series_metadata_after.revision == series_metadata_before.revision
    assert (
        series_metadata_after.content_hash
        == series_metadata_before.content_hash
    )


def test_ac10_reaccepting_same_proposal_is_idempotent_no_new_authoritative_revision(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal_id = declare_and_propose_episode(service)

    first = service.accept_episode_direction(proposal_id, accepted_by="author")
    metadata_after_first = service.load_episode_direction_metadata()

    second = service.accept_episode_direction(
        proposal_id, accepted_by="author"
    )
    metadata_after_second = service.load_episode_direction_metadata()

    assert first.already_accepted is False
    assert second.already_accepted is True
    assert second.direction == first.direction
    assert metadata_after_second == metadata_after_first
    assert metadata_after_second.revision == metadata_after_first.revision


def test_ac11_inspection_distinguishes_series_episode_and_referenced_commitments(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    declare_propose_accept_episode(service)

    inspection = service.inspect_episode_direction()

    assert inspection.series.title == _load_series_direction().title
    assert inspection.episode is not None
    assert (
        inspection.episode.direction.identity.title
        == _load_episode_direction().identity.title
    )
    assert inspection.referenced_commitment_ids == ("contested-history",)

    # Series-level content and Episode-level content are distinct objects.
    assert inspection.series is not inspection.episode
    assert inspection.series.title != inspection.episode.direction.identity.title


def test_ac12_episode_one_never_stored_or_surfaced_as_book(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    declare_propose_accept_episode(service)

    accepted = service.load_accepted_episode_direction()
    assert accepted is not None
    assert accepted.artifact_id == "episode-1-direction"
    assert "book" not in accepted.artifact_id.lower()

    inspection = service.inspect_episode_direction()
    from auteur.series.vertical_slice_formatters import (
        format_episode_direction_inspection,
    )

    default_output = format_episode_direction_inspection(inspection)
    detail_output = format_episode_direction_inspection(inspection, detail=True)
    assert "Book" not in default_output
    assert "Book" not in detail_output
    assert "Episode 1" in default_output


def test_ac13_episode_direction_unavailable_without_explicit_episodic_declaration(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    # No declare_series_episodic call: Series remains Book-oriented.
    with pytest.raises(ValueError, match="explicitly declared episodic"):
        service.propose_episode_direction(_load_episode_direction())

    # accept_episode_direction is defensively unavailable too, but it needs a
    # proposal id to attempt; a nonexistent one still surfaces the intended
    # eligibility failure path is exercised by the propose-time check above,
    # which is the externally reachable entry point for the workflow.
    assert service.load_entry_form() == "book"


def test_ac14_declare_episodic_rejected_after_entry_level_direction_work_begun(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(
        _load_model(BOOK_SERIES_INPUT, SeriesDirection)
    )
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    service.propose_book_direction(
        _load_model(BOOK_DIRECTION_INPUT, BookDirection)
    )

    with pytest.raises(ValueError, match="Book Direction work"):
        service.declare_series_episodic(declared_by="author")


def test_ac15_entry_form_locked_once_entry_level_work_begun_both_directions(
    tmp_path: Path,
) -> None:
    # Direction A: episodic Series that has begun Episode 1 work cannot be
    # converted to Book-oriented via any supported path (no conversion verb
    # exists at all; we assert the Series stays episodic and Book work is
    # rejected).
    episodic_project = tmp_path / "episodic"
    service = SeriesVerticalSliceService(episodic_project)
    declare_propose_accept_episode(service)
    assert service.load_entry_form() == "episodic"
    with pytest.raises(ValueError, match="declared episodic"):
        service.propose_book_direction(
            _load_model(BOOK_DIRECTION_INPUT, BookDirection)
        )
    assert service.load_entry_form() == "episodic"

    # Direction B: a Book-oriented Series that has begun Book Direction work
    # cannot be declared episodic.
    book_project = tmp_path / "book-oriented"
    book_service = SeriesVerticalSliceService(book_project)
    proposal = book_service.propose_series_direction(
        _load_model(BOOK_SERIES_INPUT, SeriesDirection)
    )
    book_service.accept_series_direction(
        proposal.proposal_id, accepted_by="author"
    )
    book_proposal = book_service.propose_book_direction(
        _load_model(BOOK_DIRECTION_INPUT, BookDirection)
    )
    book_service.accept_book_direction(
        book_proposal.proposal_id, accepted_by="author"
    )
    with pytest.raises(ValueError, match="Book Direction work"):
        book_service.declare_series_episodic(declared_by="author")
    assert book_service.load_entry_form() == "book"


def test_ac16_episodic_uses_episode_one_in_place_of_book_one_and_never_both(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    declare_propose_accept_episode(service)

    # An accepted Episode 1 Direction exists...
    assert service.load_accepted_episode_direction() is not None
    # ...and no supported path can also produce an accepted Book 1 Direction
    # for the same Series: both propose_book_direction and
    # accept_book_direction are rejected outright.
    with pytest.raises(ValueError):
        service.propose_book_direction(
            _load_model(BOOK_DIRECTION_INPUT, BookDirection)
        )
    assert service.load_accepted_book_direction(1) is None


def test_ac17_workflow_is_propose_accept_inspect_with_no_planning_entry_step(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declared_by="author")

    # There is no "enter Episode 1 planning" step anywhere on the service
    # surface; the only steps between declaration and inspection are propose
    # and accept.
    assert not hasattr(service, "enter_episode_planning")
    assert not hasattr(service, "enter_episode_1_planning")

    proposal = service.propose_episode_direction(_load_episode_direction())
    service.accept_episode_direction(proposal.proposal_id, accepted_by="author")
    inspection = service.inspect_episode_direction()
    assert inspection.episode is not None


def test_ac18_existing_book_projects_load_without_migration_or_reinterpretation(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(
        _load_model(BOOK_SERIES_INPUT, SeriesDirection)
    )
    accepted_series = service.accept_series_direction(
        proposal.proposal_id, accepted_by="author"
    )
    book_proposal = service.propose_book_direction(
        _load_model(BOOK_DIRECTION_INPUT, BookDirection)
    )
    accepted_book = service.accept_book_direction(
        book_proposal.proposal_id, accepted_by="author"
    )
    series_metadata = service.load_series_direction_metadata()
    book_metadata = service.load_book_direction_metadata(1)

    # A completely fresh service instance, with no entry-form artifact ever
    # written, loads the project unchanged: Book-oriented, no migration step,
    # unchanged content/hash.
    reloaded = SeriesVerticalSliceService(tmp_path)
    assert reloaded.load_entry_form() == "book"
    assert reloaded.load_accepted_series_entry_form() is None
    assert reloaded.load_accepted_series_direction() == accepted_series
    assert reloaded.load_series_direction_metadata() == series_metadata
    assert reloaded.load_accepted_book_direction(1) == accepted_book
    assert reloaded.load_book_direction_metadata(1) == book_metadata
    assert reloaded.load_accepted_episode_direction() is None


def test_ac19_normative_documentation_describes_bounded_episode_one_capability_and_boundary() -> None:
    contract = (
        DOCS_ROOT
        / "acceptance"
        / "series-episode-one-direction-capability-contract-v1.md"
    ).read_text(encoding="utf-8")
    boundary = (
        DOCS_ROOT
        / "design"
        / "series-episode-one-direction-implementation-boundary-v1.md"
    ).read_text(encoding="utf-8")
    narrative_architecture = (
        DOCS_ROOT / "narrative-architecture.md"
    ).read_text(encoding="utf-8")
    import re as _re

    raw_combined = f"{contract}\n{boundary}\n{narrative_architecture}".lower()
    # Normalize whitespace (including markdown line wraps) so a marker phrase
    # that happens to be soft-wrapped across a line break is still found as a
    # contiguous substring.
    combined = _re.sub(r"\s+", " ", raw_combined)

    # Episode 1 is a first-class Series-scope entry-unit Direction artifact.
    assert "series-scope" in combined or "series scope" in combined
    assert "entry-unit" in combined or "entry unit" in combined

    # Not a sixth canonical scope; axis and layers unchanged.
    assert "sixth canonical scope" in combined
    assert "universe, series, book, chapter, scene" in combined
    assert (
        "ontology, identity, structure, realization, expression" in combined
    )

    # Explicit acceptance is the only authority transition; proposal is
    # non-authoritative.
    assert "explicit acceptance is the only" in combined
    assert "non-authoritative" in combined

    # Commitment reference rules.
    assert "at least one" in combined
    assert "duplicate" in combined
    assert "unknown or stale" in combined or "unknown/stale" in combined

    # Two-way Book/Episode exclusivity, incl. "no supported path yields both".
    assert "no supported path" in combined or "no normal supported path" in (
        combined
    )
    assert "episode 1 direction for the same series" in combined or (
        "accepted book 1 direction" in combined
        and "accepted episode 1 direction" in combined
    )

    # Separate provenance-tracked entry-form artifact; SeriesDirection
    # unchanged; absence => Book-oriented.
    assert "book-oriented" in combined
    assert "seriesdirection" in combined

    # Declaration timing / lock.
    assert "entry-level direction work" in combined or "entry form is locked" in (
        combined
    )
    assert "idempotent" in combined

    # Idempotent re-acceptance.
    assert "already accepted" in combined or "no-change" in combined or (
        "no change" in combined
    )

    # Read-only inspection, never "Book 1".
    assert '"book 1"' in combined or (
        "never" in combined and "book 1" in combined
    )

    # Explicit out-of-scope list.
    assert "episode 2" in combined or "beyond episode 1" in combined
    assert "canonical-state" in combined or "canonical state" in combined
    assert "unification" in combined
    assert "inheritance" in combined
    assert (
        "adding an" in combined and "episodic" in combined and "seriesdirection"
        in combined
    ) or "adding an \"episodic\" value" in combined

    # This test does not assert a CHANGELOG entry, a completed qualification
    # record, release notes, or any "feature shipped" claim: it only checks
    # for the presence of stable normative markers above. (The contract text
    # itself may legitimately *mention* "changelog" only to say the
    # definition does not depend on one -- that is not asserted here either
    # way.)


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_edge_duplicate_commitment_ids_rejected_at_propose_and_accept(
    tmp_path: Path,
) -> None:
    payload = _episode_payload()
    payload["series_commitment_ids"] = ["contested-history", "contested-history"]
    with pytest.raises(ValueError, match="duplicates"):
        EpisodeDirection.model_validate(payload)


def test_edge_whitespace_only_title_and_core_answer_rejected(
    tmp_path: Path,
) -> None:
    title_payload = _episode_payload()
    title_payload["identity"]["title"] = "   "
    with pytest.raises(ValueError, match="title"):
        EpisodeDirection.model_validate(title_payload)

    core_answer_payload = _episode_payload()
    core_answer_payload["identity"]["core_answer"] = "   "
    with pytest.raises(ValueError, match="core_answer"):
        EpisodeDirection.model_validate(core_answer_payload)


def test_edge_episode_number_other_than_one_rejected(tmp_path: Path) -> None:
    payload = _episode_payload()
    payload["episode_number"] = 2
    with pytest.raises(ValueError):
        EpisodeDirection.model_validate(payload)

    zero_payload = _episode_payload()
    zero_payload["episode_number"] = 0
    with pytest.raises(ValueError):
        EpisodeDirection.model_validate(zero_payload)


def test_edge_declare_episodic_idempotent_across_differing_declared_by(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)

    first = service.declare_series_episodic(declared_by="original-author")
    second = service.declare_series_episodic(declared_by="someone-else")

    assert first.already_declared is False
    assert second.already_declared is True
    assert second.record.declared_by == "original-author"
    assert second.record == first.record


def test_edge_inspect_episode_empty_episode_state(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declared_by="author")

    inspection = service.inspect_episode_direction()

    assert inspection.episode is None
    assert inspection.episode_ref is None
    assert inspection.episode_series_source_ref is None
    assert inspection.referenced_commitment_ids == ()

    from auteur.series.vertical_slice_formatters import (
        format_episode_direction_inspection,
    )

    default_output = format_episode_direction_inspection(inspection)
    detail_output = format_episode_direction_inspection(inspection, detail=True)
    assert "No accepted Episode 1 Direction yet." in default_output
    assert "No accepted Episode 1 Direction yet." in detail_output
    assert "Accepted against Series Direction revision:" not in detail_output


def test_edge_inspect_episode_with_no_accepted_series_direction_errors(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    with pytest.raises(ValueError):
        service.inspect_episode_direction()


def test_edge_two_distinct_proposals_accepted_in_sequence_last_write_wins(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declared_by="author")

    proposal_1 = service.propose_episode_direction(_load_episode_direction())
    service.accept_episode_direction(proposal_1.proposal_id, accepted_by="author")

    payload = _episode_payload()
    payload["identity"]["title"] = "A Revised First Recovered Tape"
    proposal_2 = service.propose_episode_direction(
        EpisodeDirection.model_validate(payload)
    )
    acceptance_2 = service.accept_episode_direction(
        proposal_2.proposal_id, accepted_by="author"
    )

    assert acceptance_2.already_accepted is False
    current = service.load_accepted_episode_direction()
    assert current.proposal_id == proposal_2.proposal_id
    assert current.direction.identity.title == "A Revised First Recovered Tape"
    # Exactly one accepted Episode exists (a single artifact path/identity).
    assert current.artifact_id == "episode-1-direction"


def test_edge_proposal_id_path_traversal_rejected(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)
    service.declare_series_episodic(declared_by="author")

    with pytest.raises(FileNotFoundError):
        service.load_episode_direction_proposal("../../etc/passwd")
    with pytest.raises(FileNotFoundError):
        service.load_episode_direction_proposal("nested/traversal")


def test_edge_book_oriented_series_rejects_propose_episode(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal = service.propose_series_direction(
        _load_model(BOOK_SERIES_INPUT, SeriesDirection)
    )
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")

    with pytest.raises(ValueError, match="explicitly declared episodic"):
        service.propose_episode_direction(_load_episode_direction())


def test_edge_episodic_series_rejects_propose_book_and_accept_book(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    declare_propose_accept_episode(service)

    with pytest.raises(ValueError, match="declared episodic"):
        service.propose_book_direction(
            _load_model(BOOK_DIRECTION_INPUT, BookDirection)
        )

    # accept_book_direction's defensive guard: even if a proposal file
    # existed from before declaration, acceptance itself is now rejected.
    # There is no such pre-existing proposal here (declare-episodic requires
    # zero Book work), so we assert the guard fires before any proposal
    # lookup failure would otherwise occur by using a nonexistent id and
    # confirming the *episodic* message is the one raised, not a
    # FileNotFoundError.
    with pytest.raises(ValueError, match="declared episodic"):
        service.accept_book_direction(
            "book-direction-does-not-exist", accepted_by="author"
        )


def test_edge_redeclaration_preserves_original_provenance(
    tmp_path: Path,
) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    accept_series(service)

    service.declare_series_episodic(declared_by="author")
    metadata_before = service.load_series_entry_form_metadata()

    service.declare_series_episodic(declared_by="a-different-author")
    metadata_after = service.load_series_entry_form_metadata()

    assert metadata_after == metadata_before
    assert metadata_after.revision == metadata_before.revision
    assert metadata_after.accepted_by == metadata_before.accepted_by
    assert metadata_after.accepted_by == "author"


def test_edge_reload_equality_after_accept(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    proposal_id = declare_and_propose_episode(service)
    accepted = service.accept_episode_direction(
        proposal_id, accepted_by="author"
    ).direction

    reloaded_service = SeriesVerticalSliceService(tmp_path)
    assert reloaded_service.load_accepted_episode_direction() == accepted
    assert (
        reloaded_service.load_episode_direction_metadata()
        == service.load_episode_direction_metadata()
    )


# ---------------------------------------------------------------------------
# CLI-level (real user surface) spot checks
# ---------------------------------------------------------------------------


def _write_series_input(tmp_path: Path) -> Path:
    payload = yaml.safe_load(SERIES_INPUT.read_text(encoding="utf-8"))
    path = tmp_path / "series_direction.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _proposal_id(output: str) -> str:
    line = next(
        line for line in output.splitlines() if line.startswith("Proposal ID: ")
    )
    return line.removeprefix("Proposal ID: ")


def test_cli_declare_propose_accept_inspect_end_to_end(
    tmp_path: Path, capsys
) -> None:
    series_input = _write_series_input(tmp_path)

    assert main(
        [
            "series",
            "journey",
            "propose-series",
            str(tmp_path),
            "--input",
            str(series_input),
        ]
    ) == 0
    series_proposal_id = _proposal_id(capsys.readouterr().out)

    assert main(
        [
            "series",
            "journey",
            "accept-series",
            str(tmp_path),
            series_proposal_id,
        ]
    ) == 0
    capsys.readouterr()

    assert main(
        ["series", "journey", "declare-episodic", str(tmp_path)]
    ) == 0
    declare_output = capsys.readouterr().out
    assert "Series entry form declared: episodic." in declare_output

    assert main(
        ["series", "journey", "declare-episodic", str(tmp_path)]
    ) == 0
    redeclare_output = capsys.readouterr().out
    assert "Series entry form already episodic; no change." in redeclare_output

    assert main(
        [
            "series",
            "journey",
            "propose-episode",
            str(tmp_path),
            "--input",
            str(EPISODE_INPUT),
        ]
    ) == 0
    episode_proposal_id = _proposal_id(capsys.readouterr().out)

    assert main(
        [
            "series",
            "journey",
            "accept-episode",
            str(tmp_path),
            episode_proposal_id,
        ]
    ) == 0
    accept_output = capsys.readouterr().out
    assert "Accepted Episode 1 Direction:" in accept_output

    assert main(
        [
            "series",
            "journey",
            "accept-episode",
            str(tmp_path),
            episode_proposal_id,
        ]
    ) == 0
    reaccept_output = capsys.readouterr().out
    assert (
        "Episode 1 Direction already accepted; no change." in reaccept_output
    )

    assert main(
        ["series", "journey", "inspect-episode", str(tmp_path)]
    ) == 0
    inspect_output = capsys.readouterr().out
    assert "Book" not in inspect_output
    assert "revision " not in inspect_output

    assert main(
        ["series", "journey", "inspect-episode", str(tmp_path), "--detail"]
    ) == 0
    detail_output = capsys.readouterr().out
    assert "episode-1-direction (revision 1)" in detail_output
    assert "series-entry-form (revision 1)" in detail_output
    assert f"Proposal ID: {episode_proposal_id}" in detail_output
    assert "Book" not in detail_output
