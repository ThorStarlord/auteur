from __future__ import annotations

from pathlib import Path

import yaml
import pytest

from auteur.series.vertical_slice_models import (
    AcceptedFactRef,
    ArtifactRef,
    BookDirection,
    BookPlanningIntent,
    CausalSupportRelation,
    PressureGroupRelation,
    RealizationCandidate,
    SeriesDirection,
    StateTransition,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "archive_of_lies_vertical_slice"


def _load(name: str, model_type):
    return model_type.model_validate(
        yaml.safe_load((FIXTURE_ROOT / name).read_text(encoding="utf-8"))
    )


def _prepare_three_books(tmp_path: Path) -> SeriesVerticalSliceService:
    service = SeriesVerticalSliceService(tmp_path)
    series = _load("series_direction.yaml", SeriesDirection)
    series_proposal = service.propose_series_direction(series)
    service.accept_series_direction(series_proposal.proposal_id, accepted_by="author")
    base_book = _load("book_1_direction.yaml", BookDirection)
    for book_number in (1, 2, 3):
        book = base_book.model_copy(update={"book_number": book_number})
        book_proposal = service.propose_book_direction(book)
        service.accept_book_direction(book_proposal.proposal_id, accepted_by="author")
        direction_ref = ArtifactRef(
            artifact_id=f"book-{book_number}-direction", revision=1
        )
        transitions = {
            1: [
                StateTransition(
                    transition_id="founding-ledger-exposed",
                    subject="archive",
                    attribute="founding_record",
                    after="confirmed fraudulent",
                    explanation="The ledger proves the founding record was forged.",
                )
            ],
            2: [
                StateTransition(
                    transition_id="admission-recorded",
                    subject="archive",
                    attribute="custodian_admission",
                    after="admitted",
                    explanation="The custodian admits protecting the record.",
                )
            ],
            3: [
                StateTransition(
                    transition_id="archive-protected",
                    subject="archive",
                    attribute="custodian_admission",
                    before="admitted",
                    after="protected",
                    explanation="The treaty protects the admitting custodian.",
                )
            ],
        }[book_number]
        candidate = RealizationCandidate(
            candidate_id=f"book-{book_number}-realization",
            book_number=book_number,
            summary=f"Book {book_number} realization",
            transitions=transitions,
            source_refs=[direction_ref],
        )
        service.propose_realization(candidate)
        service.accept_realization(candidate.candidate_id, accepted_by="author")
    service.enter_book_planning(4, entered_by="author")
    service.store.save_book_planning_intent(
        BookPlanningIntent(
            book_number=4,
            intent="Protect the archive while tracing the admission.",
            relevance_refs=[
                AcceptedFactRef(
                    artifact_id="realization-bundle-book-3-realization",
                    revision=1,
                    fact_id="archive-protected",
                )
            ],
        )
    )
    return service


def test_typed_story_instance_relation_shapes_are_narrow() -> None:
    source = AcceptedFactRef(artifact_id="realization-bundle-book-2-realization", revision=1, fact_id="admission-recorded")
    target = AcceptedFactRef(artifact_id="realization-bundle-book-3-realization", revision=1, fact_id="archive-protected")
    causal = CausalSupportRelation(
        relation_id="admission-supports-protection",
        origin="DETERMINISTIC_DERIVATION",
        source_fact_ref=source,
        target_fact_ref=target,
        evidence_refs=[source, target],
        source_revision_refs=[ArtifactRef(artifact_id=source.artifact_id, revision=source.revision)],
        rule_version="archive-of-lies-v1",
    )
    group = PressureGroupRelation(
        relation_id="contested-history-pressure",
        origin="DETERMINISTIC_DERIVATION",
        target_commitment_or_pressure_ref=ArtifactRef(artifact_id="series-direction", revision=1),
        members=[
            {"fact_ref": source, "role": "causal_pivot"},
            {"fact_ref": target, "role": "current_constraint"},
        ],
    )
    assert causal.kind == "causal_support"
    assert group.kind == "pressure_group"
    assert len(group.members) == 2


def test_retroactive_realization_revision_preserves_payload_and_order(tmp_path: Path) -> None:
    service = _prepare_three_books(tmp_path)
    original = service.store.load_accepted_realization_bundles()[1][0]
    revision = RealizationCandidate(
        candidate_id="book-2-revision",
        book_number=2,
        summary="Book 2 revised realization",
        transitions=[
            StateTransition(
                transition_id="admission-recorded",
                subject="archive",
                attribute="custodian_admission",
                after="retracted",
                explanation="The custodian retracts the admission under pressure.",
            )
        ],
        source_refs=[ArtifactRef(artifact_id="book-2-direction", revision=1)],
    )
    service.propose_realization(revision)
    accepted = service.accept_realization_revision(
        original.artifact_id, revision.candidate_id, accepted_by="author"
    )

    assert accepted.artifact_id == original.artifact_id
    assert service.store.load_realization_revision(original.artifact_id, 1) == original
    loaded = service.store.load_accepted_realization_bundles()
    assert [bundle.artifact_id for bundle, _metadata in loaded] == [
        "realization-bundle-book-1-realization",
        "realization-bundle-book-2-realization",
        "realization-bundle-book-3-realization",
    ]
    assert [metadata.revision for _bundle, metadata in loaded] == [1, 2, 1]
    assert service.load_canonical_state().conflicts


def test_global_map_focus_d13_and_rebuild_survive_historical_member(tmp_path: Path) -> None:
    service = _prepare_three_books(tmp_path)
    first = service.build_global_map(4)
    assert first.pressure_groups
    group = first.pressure_groups[0]
    assert any(member.role == "originating_history" for member in group.members)
    focus = service.derive_focus_from_global_map(4)
    projected = focus.group(group.relation_id)
    assert projected.member_roles
    assert any(
        focus.item(entry_id).disposition in {"dormant", "superseded", "reactivated"}
        for entry_id in projected.entry_ids
    )

    service.delete_global_map(4)
    service.delete_derived_book_context(4)
    rebuilt = service.build_global_map(4)
    rebuilt_focus = service.derive_focus_from_global_map(4)
    assert rebuilt.model_dump(mode="json") == first.model_dump(mode="json")
    assert rebuilt_focus.model_dump(mode="json") == focus.model_dump(mode="json")


def test_global_map_revision_impact_keeps_downstream_accepted(tmp_path: Path) -> None:
    service = _prepare_three_books(tmp_path)
    original_map = service.build_global_map(4)
    original = service.store.load_accepted_realization_bundles()[1][0]
    revision = RealizationCandidate(
        candidate_id="book-2-impact-revision",
        book_number=2,
        summary="Book 2 impact revision",
        transitions=[
            StateTransition(
                transition_id="admission-recorded",
                subject="archive",
                attribute="custodian_admission",
                after="retracted",
                explanation="The admission is retracted.",
            )
        ],
        source_refs=[ArtifactRef(artifact_id="book-2-direction", revision=1)],
    )
    service.propose_realization(revision)
    service.accept_realization_revision(original.artifact_id, revision.candidate_id, accepted_by="author")
    assert service.load_global_map(4).freshness == "stale"
    try:
        service.derive_focus_from_global_map(4)
    except ValueError as error:
        assert "stale" in str(error)
    else:
        raise AssertionError("stale Global Map was used for Focus")
    rebuilt_map = service.build_global_map(4)
    assert rebuilt_map.model_dump(mode="json") != original_map.model_dump(mode="json")
    report = service.realization_impact("realization-bundle-book-3-realization")
    assert report["freshness"] == "stale"
    assert report["semantic_impact"] == "contradictory"
    assert service.store.artifact_store.current("realization-bundle-book-3-realization").lifecycle.value == "accepted"


def test_series_revision_reports_each_affected_book_without_rewriting(tmp_path: Path) -> None:
    service = _prepare_three_books(tmp_path)
    series = service.load_accepted_series_direction()
    assert series is not None
    proposal = service.propose_series_direction(
        series.direction.model_copy(update={"promise": "A revised promise."})
    )
    service.accept_series_direction(proposal.proposal_id, accepted_by="author")
    impact = service.series_impact()
    assert [item["book_number"] for item in impact] == [1, 2, 3]
    assert all(item["lifecycle"] == "accepted" for item in impact)
    assert all(item["reconciliation_required"] for item in impact)


def test_failed_realization_revision_restores_previous_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _prepare_three_books(tmp_path)
    original = service.store.load_accepted_realization_bundles()[1][0]
    revision = RealizationCandidate(
        candidate_id="book-2-failed-revision",
        book_number=2,
        summary="Failed Book 2 revision",
        transitions=original.transitions,
        source_refs=[ArtifactRef(artifact_id="book-2-direction", revision=1)],
    )
    service.propose_realization(revision)

    def fail_accept(*args, **kwargs):
        raise OSError("metadata write failed")

    monkeypatch.setattr(service.store.artifact_store, "accept", fail_accept)
    with pytest.raises(OSError, match="metadata write failed"):
        service.accept_realization_revision(
            original.artifact_id, revision.candidate_id, accepted_by="author"
        )
    assert service.store.load_accepted_realization_bundles()[1][0] == original
    assert service.store.load_realization_revision(original.artifact_id, 1) == original
