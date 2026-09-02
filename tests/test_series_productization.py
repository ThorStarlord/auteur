from __future__ import annotations

from pathlib import Path

import yaml

from auteur.cli import main
from auteur.series.productization import SeriesProductizationService
from auteur.series.vertical_slice_models import (
    AcceptedFactRef,
    ArtifactRef,
    BookDirection,
    BookPlanningIntent,
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


def _prepare_project(tmp_path: Path) -> None:
    service = SeriesVerticalSliceService(tmp_path)
    series_proposal = service.propose_series_direction(
        _load("series_direction.yaml", SeriesDirection)
    )
    service.accept_series_direction(series_proposal.proposal_id, accepted_by="author")
    base_book = _load("book_1_direction.yaml", BookDirection)
    transitions = {
        1: ("archive-founded", None, "forged"),
        2: ("archive-admitted", "forged", "admitted"),
        3: ("archive-protected", "admitted", "protected"),
    }
    for book_number, (transition_id, before, after) in transitions.items():
        direction = base_book.model_copy(update={"book_number": book_number})
        book_proposal = service.propose_book_direction(direction)
        service.accept_book_direction(book_proposal.proposal_id, accepted_by="author")
        candidate = RealizationCandidate(
            candidate_id=f"productization-book-{book_number}",
            book_number=book_number,
            summary=f"Book {book_number} realization",
            transitions=[
                StateTransition(
                    transition_id=transition_id,
                    subject="archive",
                    attribute="status",
                    before=before,
                    after=after,
                    explanation=f"Book {book_number} changes the archive.",
                )
            ],
            source_refs=[ArtifactRef(artifact_id=f"book-{book_number}-direction", revision=1)],
        )
        service.propose_realization(candidate)
        service.accept_realization(candidate.candidate_id, accepted_by="author")
    service.enter_book_planning(4, entered_by="author")
    service.store.save_book_planning_intent(
        BookPlanningIntent(
            book_number=4,
            intent="Decide whether to expose the archive.",
            relevance_refs=[
                AcceptedFactRef(
                    artifact_id="realization-bundle-productization-book-3",
                    revision=1,
                    fact_id="archive-protected",
                )
            ],
        )
    )


def test_productization_builds_rebuildable_author_focus_from_normal_project(
    tmp_path: Path,
) -> None:
    _prepare_project(tmp_path)
    product = SeriesProductizationService(tmp_path)

    first = product.build_focus(4)
    product.service.delete_global_map(4)
    rebuilt = product.build_focus(4)

    assert first.map_snapshot_id == "global-map-book-4"
    assert first.decision == "Decide whether to expose the archive."
    assert first.active_constraints
    assert first.relevant_history
    assert first.long_range_connections
    assert all(item.why_matters_now for item in first.relevant_history)
    assert first.provenance
    assert rebuilt.model_dump(mode="json") == first.model_dump(mode="json")


def test_productization_revision_report_preserves_accepted_state_and_review_order(
    tmp_path: Path,
) -> None:
    _prepare_project(tmp_path)
    product = SeriesProductizationService(tmp_path)
    original = product.service.store.load_accepted_realization_bundles()[1][0]
    revision = RealizationCandidate(
        candidate_id="productization-book-2-revision",
        book_number=2,
        summary="Book 2 revised realization",
        transitions=[
            StateTransition(
                transition_id="archive-admitted-revised",
                subject="archive",
                attribute="status",
                before="forged",
                after="contested",
                explanation="Book 2 changes the archive admission.",
            )
        ],
        source_refs=[ArtifactRef(artifact_id="book-2-direction", revision=1)],
    )
    product.service.propose_realization(revision)
    product.service.accept_realization_revision(
        original.artifact_id, revision.candidate_id, accepted_by="author"
    )

    report = product.revision_impact()

    assert report.affected_artifacts
    assert report.review_order
    assert product.service.store.artifact_store.current(
        "realization-bundle-productization-book-3"
    ).lifecycle.value == "accepted"
    assert report.reconciliation_boundary == (
        "Review affected accepted artifacts; no downstream artifact was rewritten."
    )


def test_series_focus_cli_is_author_readable_and_hides_internal_ids_by_default(
    tmp_path: Path, capsys
) -> None:
    _prepare_project(tmp_path)

    assert main(["series", "focus", str(tmp_path), "--book", "4"]) == 0

    output = capsys.readouterr().out
    assert "DECISION" in output
    assert "ACTIVE CONSTRAINTS" in output
    assert "RELEVANT HISTORY" in output
    assert "PERSISTENT PRESSURES" in output
    assert "LONG-RANGE CONNECTIONS" in output
    assert "PROVENANCE" in output
    assert "revision 1" in output
    assert "Relation:" not in output


def test_series_impact_cli_explains_review_boundary(tmp_path: Path, capsys) -> None:
    _prepare_project(tmp_path)

    assert main(["series", "impact", str(tmp_path)]) == 0

    output = capsys.readouterr().out
    assert "Revision impact" in output
    assert "REVIEW ORDER" in output
    assert "no downstream artifact was rewritten" in output
