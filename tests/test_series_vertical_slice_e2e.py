from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from auteur.provenance import Lifecycle
from auteur.series.vertical_slice_formatters import (
    format_series_journey_focus,
    format_series_journey_map,
)
from auteur.series.vertical_slice_models import (
    BookDirection,
    BookPlanningContext,
    NextDecisionProposal,
    RealizationCandidate,
    SeriesDirection,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


FIXTURE_ROOT = (
    Path(__file__).parent / "fixtures" / "archive_of_lies_vertical_slice"
)


def _load_fixture(name: str, model_type: type[BaseModel]) -> Any:
    payload = yaml.safe_load(
        (FIXTURE_ROOT / name).read_text(encoding="utf-8")
    )
    return model_type.model_validate(payload)


def _authority_snapshot(service: SeriesVerticalSliceService) -> tuple[object, ...]:
    return (
        service.load_accepted_series_direction(),
        service.load_series_direction_metadata(),
        service.load_accepted_book_direction(1),
        service.load_book_direction_metadata(1),
        service.load_accepted_book_direction(2),
        service.load_book_direction_metadata(2),
        service.store.load_accepted_realization_bundles(),
        service.load_canonical_state(),
    )


def test_archive_of_lies_series_vertical_slice_end_to_end(tmp_path: Path) -> None:
    project = tmp_path / "archive-of-lies"
    service = SeriesVerticalSliceService(project)
    series_direction = _load_fixture("series_direction.yaml", SeriesDirection)
    book_direction = _load_fixture("book_1_direction.yaml", BookDirection)
    outcome = _load_fixture("book_1_outcome.yaml", RealizationCandidate)
    expected_context = _load_fixture(
        "book_2_context_expected.yaml", BookPlanningContext
    )

    assert series_direction.series_type == "ongoing"
    assert "book_plans" not in series_direction.model_dump()
    series_proposal = service.propose_series_direction(series_direction)
    assert service.load_series_direction_proposal(series_proposal.proposal_id) == series_proposal
    assert service.load_accepted_series_direction() is None
    assert service.load_series_direction_metadata() is None
    assert service.load_accepted_book_direction(1) is None
    assert service.store.load_accepted_realization_bundles() == []

    accepted_series = service.accept_series_direction(
        series_proposal.proposal_id,
        accepted_by="archive-author",
    )
    accepted_series_metadata = service.load_series_direction_metadata()
    assert accepted_series.direction == series_direction
    assert accepted_series_metadata is not None
    assert accepted_series_metadata.lifecycle is Lifecycle.ACCEPTED
    assert accepted_series_metadata.revision == 1

    book_proposal = service.propose_book_direction(book_direction)
    assert service.load_book_direction_proposal(book_proposal.proposal_id) == book_proposal
    assert service.load_accepted_book_direction(1) is None
    accepted_book = service.accept_book_direction(
        book_proposal.proposal_id,
        accepted_by="archive-author",
    )
    assert accepted_book.direction == book_direction
    assert service.load_accepted_series_direction() == accepted_series
    assert service.load_series_direction_metadata() == accepted_series_metadata

    state_before_outcome = service.load_canonical_state()
    proposed_outcome = service.propose_realization(outcome)
    assert proposed_outcome == outcome
    assert service.load_canonical_state() == state_before_outcome
    assert service.store.load_accepted_realization_bundles() == []

    accepted_bundle = service.accept_realization(
        outcome.candidate_id,
        accepted_by="archive-author",
    )
    state_after_outcome = service.load_canonical_state()
    assert accepted_bundle.transitions == outcome.transitions
    assert state_after_outcome != state_before_outcome
    assert state_after_outcome.values["archive.founding_record"] == "confirmed fraudulent"
    assert state_after_outcome.applied_bundle_ids == [accepted_bundle.bundle_id]

    service = SeriesVerticalSliceService(project)
    assert service.load_accepted_series_direction() == accepted_series
    assert service.load_accepted_book_direction(1) == accepted_book
    assert service.store.load_accepted_realization_bundles()[0][0] == accepted_bundle
    assert service.rebuild_canonical_state() == state_after_outcome

    state_before_planning = service.load_canonical_state()
    authority_before_planning = _authority_snapshot(service)
    planning_entry = service.enter_book_planning(2, entered_by="archive-author")
    assert planning_entry.book_number == 2
    assert service.load_accepted_book_direction(2) is None
    assert service.load_book_direction_metadata(2) is None
    assert _authority_snapshot(service) == authority_before_planning

    context = service.derive_book_context(2)
    assert context == expected_context
    assert [item.item_id for item in context.items] == [
        "series-commitment-contested-history",
        "state-change-founding-ledger-exposed",
    ]
    assert all(item.why_matters_now.strip() for item in context.items)
    assert all(item.source_refs for item in context.items)
    context_source_refs = {
        (source_ref.artifact_id, source_ref.revision)
        for source_ref in context.generated_from
    } | {
        (source_ref.artifact_id, source_ref.revision)
        for item in context.items
        for source_ref in item.source_refs
    }
    for artifact_id, revision in context_source_refs:
        metadata = service.store.artifact_store.current(artifact_id)
        assert metadata is not None
        assert metadata.lifecycle is Lifecycle.ACCEPTED
        assert metadata.revision == revision

    unrelated_book_1_datum = book_direction.identity.open_questions[0]
    surfaced_context = "\n".join(
        f"{item.summary}\n{item.why_matters_now}" for item in context.items
    )
    assert unrelated_book_1_datum not in surfaced_context

    authority_before_rebuild = _authority_snapshot(service)
    service.delete_derived_book_context(2)
    assert not service.store.book_planning_context_path(2).exists()
    rebuilt_context = service.derive_book_context(2)
    assert rebuilt_context.model_dump(mode="json") == context.model_dump(mode="json")
    assert rebuilt_context == expected_context
    assert _authority_snapshot(service) == authority_before_rebuild
    assert service.load_canonical_state() == state_before_planning

    decision = service.propose_next_decision(2)
    expected_decision = _load_fixture(
        "book_2_decision_expected.yaml", NextDecisionProposal
    ).model_copy(update={"proposal_id": decision.proposal_id})
    assert decision == expected_decision
    assert len(decision.options) == 2
    assert len({option.summary for option in decision.options}) == 2
    assert len({option.tradeoff for option in decision.options}) == 2

    alternative_option_id = next(
        option.option_id
        for option in decision.options
        if option.option_id != decision.recommended_option_id
    )
    actions = (
        ("recommended", "choose_recommended", None),
        ("another", "choose_other", alternative_option_id),
        ("defer", "defer", None),
    )
    for copy_name, action, selected_option_id in actions:
        isolated_project = tmp_path / f"archive-of-lies-{copy_name}"
        shutil.copytree(project, isolated_project)
        isolated_service = SeriesVerticalSliceService(isolated_project)
        authority_before_action = _authority_snapshot(isolated_service)

        recorded = isolated_service.record_decision_action(
            decision.proposal_id,
            action=action,
            selected_option_id=selected_option_id,
        )

        assert recorded.action == action
        assert isolated_service.load_accepted_book_direction(2) is None
        assert isolated_service.load_book_direction_metadata(2) is None
        assert _authority_snapshot(isolated_service) == authority_before_action
        assert not list(isolated_project.rglob("bible.json"))

    map_output = format_series_journey_map(context, decision)
    focus_output = format_series_journey_focus(decision)
    detailed_map = format_series_journey_map(context, decision, detail=True)
    detailed_focus = format_series_journey_focus(decision, detail=True)

    assert "Next available decision" in map_output
    assert decision.question in map_output
    assert "Why it matters now" in map_output
    assert "Open Focus" in map_output
    assert unrelated_book_1_datum not in map_output
    assert "Why this is preferred" in focus_output
    assert decision.rationale in focus_output
    assert "Principal tradeoff" in focus_output
    assert decision.options[0].tradeoff in focus_output
    assert "Choose recommended" in focus_output
    assert "Choose another option" in focus_output
    assert "Defer" in focus_output
    assert "revision 1" not in map_output
    assert "revision 1" not in focus_output
    assert "Source references" in detailed_map
    assert "Accepted input sources" in detailed_focus
    assert "series-direction (revision 1)" in detailed_map
    assert "realization-bundle-recovered-founding-ledger (revision 1)" in detailed_focus
