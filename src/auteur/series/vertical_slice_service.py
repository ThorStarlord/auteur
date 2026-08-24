from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

from auteur.provenance import ArtifactMetadata
from auteur.series.vertical_slice_models import (
    AcceptedBookDirection,
    AcceptedRealizationBundle,
    AcceptedSeriesDirection,
    ArtifactRef,
    BookDirection,
    BookDirectionProposal,
    BookPlanningContext,
    CanonicalState,
    CarryForwardItem,
    DecisionAction,
    DecisionOption,
    NextDecisionProposal,
    PlanningEntry,
    RealizationCandidate,
    SeriesDirection,
    SeriesDirectionProposal,
)
from auteur.series.vertical_slice_store import VerticalSliceStore


_BOOK_CONTEXT_DERIVATION_VERSION = "archive-of-lies-book-2-v1"
_BOOK_CONTEXT_STATE_TRANSITIONS = {
    ("archive-of-lies", 2): {
        (
            "realization-bundle-recovered-founding-ledger",
            1,
            "founding-ledger-exposed",
        ): (
            "The exposed founding fraud makes the archive's official history "
            "an active constraint on Book 2."
        )
    }
}
_BOOK_2_DECISION_CONTEXT_ITEMS = (
    "series-commitment-contested-history",
    "state-change-founding-ledger-exposed",
)


class SeriesVerticalSliceService:
    def __init__(self, project_root: Path) -> None:
        self.store = VerticalSliceStore(project_root)

    def propose_series_direction(
        self, direction: SeriesDirection
    ) -> SeriesDirectionProposal:
        proposal = SeriesDirectionProposal(
            proposal_id=f"series-direction-{uuid4().hex}",
            revision=1,
            direction=direction,
        )
        self.store.save_series_direction_proposal(proposal)
        return proposal

    def load_series_direction_proposal(
        self, proposal_id: str
    ) -> SeriesDirectionProposal:
        return self.store.load_series_direction_proposal(proposal_id)

    def accept_series_direction(
        self,
        proposal_id: str,
        *,
        accepted_by: str,
        rationale: str | None = None,
    ) -> AcceptedSeriesDirection:
        proposal = self.load_series_direction_proposal(proposal_id)
        accepted = AcceptedSeriesDirection(
            artifact_id="series-direction",
            proposal_id=proposal.proposal_id,
            direction=proposal.direction,
        )
        self.store.save_accepted_series_direction(
            accepted,
            accepted_by=accepted_by,
            rationale=rationale,
        )
        return accepted

    def load_accepted_series_direction(
        self,
    ) -> AcceptedSeriesDirection | None:
        return self.store.load_accepted_series_direction()

    def load_series_direction_metadata(self) -> ArtifactMetadata | None:
        return self.store.load_series_direction_metadata()

    def _accepted_series_source(
        self,
    ) -> tuple[AcceptedSeriesDirection, ArtifactMetadata]:
        accepted = self.load_accepted_series_direction()
        metadata = self.load_series_direction_metadata()
        if accepted is None or metadata is None:
            raise ValueError(
                "An accepted Series Direction is required for a Book Direction"
            )
        return accepted, metadata

    @staticmethod
    def _validate_series_commitments(
        book_direction: BookDirection,
        accepted_series: AcceptedSeriesDirection,
    ) -> None:
        known_ids = {
            commitment.commitment_id
            for commitment in accepted_series.direction.commitments
        }
        unknown_ids = sorted(
            set(book_direction.series_commitment_ids) - known_ids
        )
        if unknown_ids:
            raise ValueError(
                "Unknown accepted Series commitment reference(s): "
                + ", ".join(unknown_ids)
            )

    def propose_book_direction(
        self, book_direction: BookDirection
    ) -> BookDirectionProposal:
        accepted_series, series_metadata = self._accepted_series_source()
        self._validate_series_commitments(book_direction, accepted_series)
        proposal = BookDirectionProposal(
            proposal_id=f"book-direction-{uuid4().hex}",
            revision=1,
            direction=book_direction,
            source_refs=[
                ArtifactRef(
                    artifact_id=accepted_series.artifact_id,
                    revision=series_metadata.revision,
                )
            ],
        )
        self.store.save_book_direction_proposal(proposal)
        return proposal

    def load_book_direction_proposal(
        self, proposal_id: str
    ) -> BookDirectionProposal:
        return self.store.load_book_direction_proposal(proposal_id)

    def accept_book_direction(
        self,
        proposal_id: str,
        *,
        accepted_by: str,
        rationale: str | None = None,
    ) -> AcceptedBookDirection:
        proposal = self.load_book_direction_proposal(proposal_id)
        accepted_series, series_metadata = self._accepted_series_source()
        self._validate_series_commitments(proposal.direction, accepted_series)
        current_source = ArtifactRef(
            artifact_id=accepted_series.artifact_id,
            revision=series_metadata.revision,
        )
        if proposal.source_refs != [current_source]:
            raise ValueError(
                "Book Direction proposal does not reference the current accepted "
                "Series Direction revision"
            )
        accepted = AcceptedBookDirection(
            artifact_id=f"book-{proposal.direction.book_number}-direction",
            proposal_id=proposal.proposal_id,
            direction=proposal.direction,
        )
        self.store.save_accepted_book_direction(
            accepted,
            series_source=proposal.source_refs[0],
            accepted_by=accepted_by,
            rationale=rationale,
        )
        return accepted

    def load_accepted_book_direction(
        self, book_number: int
    ) -> AcceptedBookDirection | None:
        return self.store.load_accepted_book_direction(book_number)

    def load_book_direction_metadata(
        self, book_number: int
    ) -> ArtifactMetadata | None:
        return self.store.load_book_direction_metadata(book_number)

    def _accepted_book_source(
        self, book_number: int
    ) -> tuple[AcceptedBookDirection, ArtifactMetadata]:
        accepted = self.load_accepted_book_direction(book_number)
        metadata = self.load_book_direction_metadata(book_number)
        if accepted is None or metadata is None:
            raise ValueError(
                "An accepted Book Direction is required for a Realization"
            )
        return accepted, metadata

    def _current_book_source_ref(self, book_number: int) -> ArtifactRef:
        accepted, metadata = self._accepted_book_source(book_number)
        return ArtifactRef(
            artifact_id=accepted.artifact_id,
            revision=metadata.revision,
        )

    def propose_realization(
        self, candidate: RealizationCandidate
    ) -> RealizationCandidate:
        current_source = self._current_book_source_ref(candidate.book_number)
        if candidate.source_refs != [current_source]:
            raise ValueError(
                "Realization candidate does not reference the current accepted "
                "Book Direction revision"
            )
        self.store.validate_current_book_dependency(
            candidate.book_number, current_source
        )
        self.store.save_realization_candidate(candidate)
        return candidate

    def accept_realization(
        self,
        candidate_id: str,
        *,
        accepted_by: str,
        rationale: str | None = None,
    ) -> AcceptedRealizationBundle:
        candidate = self.store.load_realization_candidate(candidate_id)
        current_source = self._current_book_source_ref(candidate.book_number)
        if candidate.source_refs != [current_source]:
            raise ValueError(
                "Realization candidate does not reference the current accepted "
                "Book Direction revision"
            )
        accepted = AcceptedRealizationBundle(
            artifact_id=f"realization-bundle-{candidate.candidate_id}",
            bundle_id=f"realization-bundle-{candidate.candidate_id}",
            candidate_id=candidate.candidate_id,
            book_number=candidate.book_number,
            transitions=candidate.transitions,
        )
        previous_state = self.store.snapshot_canonical_state()
        metadata = self.store.save_accepted_realization_bundle(
            accepted,
            book_source=current_source,
            accepted_by=accepted_by,
            rationale=rationale,
        )
        try:
            self.rebuild_canonical_state()
        except Exception:
            self.store.rollback_accepted_realization_bundle(
                accepted.bundle_id, metadata.revision
            )
            self.store.restore_canonical_state(previous_state)
            raise
        return accepted

    def rebuild_canonical_state(self) -> CanonicalState:
        values: dict[str, str] = {}
        applied_bundle_ids: list[str] = []
        state_version = 0
        for bundle, _metadata in self.store.load_accepted_realization_bundles():
            for transition in bundle.transitions:
                key = f"{transition.subject}.{transition.attribute}"
                # A null before value means the attribute must not exist yet.
                if transition.before is None:
                    if key in values:
                        raise ValueError(
                            f"State transition {transition.transition_id} before "
                            f"value requires initial absence for {key}"
                        )
                elif values.get(key) != transition.before:
                    raise ValueError(
                        f"State transition {transition.transition_id} before "
                        f"value does not match {key}"
                    )
                values[key] = transition.after
            applied_bundle_ids.append(bundle.bundle_id)
            state_version += 1
        state = CanonicalState(
            state_version=state_version,
            values=values,
            applied_bundle_ids=applied_bundle_ids,
        )
        self.store.save_canonical_state(state)
        return state

    def load_canonical_state(self) -> CanonicalState:
        return self.store.load_canonical_state()

    def enter_book_planning(
        self, book_number: int, *, entered_by: str
    ) -> PlanningEntry:
        existing = self.store.load_planning_entry(book_number)
        if existing is not None:
            if existing.entered_by != entered_by:
                raise ValueError(
                    f"Book {book_number} planning was already entered by "
                    f"{existing.entered_by}"
                )
            return existing
        entry = PlanningEntry(
            book_number=book_number,
            entered_by=entered_by,
            entered_at=datetime.now(timezone.utc),
        )
        self.store.save_planning_entry(entry)
        return entry

    def derive_book_context(self, book_number: int) -> BookPlanningContext:
        if self.store.load_planning_entry(book_number) is None:
            raise ValueError(
                f"The author must explicitly enter Book {book_number} planning "
                "before context can be derived"
            )

        accepted_series, series_metadata = self._accepted_series_source()
        previous_book_number = book_number - 1
        accepted_book, book_metadata = self._accepted_book_source(
            previous_book_number
        )
        self.store.validate_book_context_source(
            series_metadata,
            artifact_id=accepted_series.artifact_id,
            artifact_type="series_direction",
            path=self.store.accepted_series_direction_path,
        )
        self.store.validate_book_context_source(
            book_metadata,
            artifact_id=accepted_book.artifact_id,
            artifact_type="book_direction",
            path=self.store.accepted_book_direction_path(previous_book_number),
        )
        series_ref = ArtifactRef(
            artifact_id=accepted_series.artifact_id,
            revision=series_metadata.revision,
        )
        book_ref = ArtifactRef(
            artifact_id=accepted_book.artifact_id,
            revision=book_metadata.revision,
        )

        commitments_by_id = {
            commitment.commitment_id: commitment
            for commitment in accepted_series.direction.commitments
        }
        items: list[CarryForwardItem] = []
        for commitment_id in accepted_book.direction.series_commitment_ids:
            commitment = commitments_by_id.get(commitment_id)
            if commitment is None:
                raise ValueError(
                    "Accepted Book Direction references an unknown current "
                    f"Series commitment: {commitment_id}"
                )
            items.append(
                CarryForwardItem(
                    item_id=f"series-commitment-{commitment.commitment_id}",
                    kind="series_commitment",
                    summary=commitment.statement,
                    why_matters_now=(
                        f"Book {previous_book_number} explicitly carried this "
                        f"Series commitment, so it still governs Book "
                        f"{book_number} planning."
                    ),
                    source_refs=[series_ref, book_ref],
                )
            )

        selected_transition_reasons = _BOOK_CONTEXT_STATE_TRANSITIONS.get(
            (accepted_series.direction.series_id, book_number), {}
        )
        selected_transition_sources: set[tuple[str, int, str]] = set()
        selected_bundle_refs: list[ArtifactRef] = []
        for bundle, metadata in self.store.load_accepted_realization_bundles():
            if bundle.book_number != previous_book_number:
                continue
            for transition in bundle.transitions:
                transition_source = (
                    bundle.artifact_id,
                    metadata.revision,
                    transition.transition_id,
                )
                why_matters_now = selected_transition_reasons.get(
                    transition_source
                )
                if why_matters_now is None:
                    continue
                self.store.validate_book_context_source(
                    metadata,
                    artifact_id=bundle.artifact_id,
                    artifact_type="accepted_realization_bundle",
                    path=self.store.accepted_realization_bundle_path(
                        bundle.bundle_id
                    ),
                )
                bundle_ref = ArtifactRef(
                    artifact_id=bundle.artifact_id,
                    revision=metadata.revision,
                )
                items.append(
                    CarryForwardItem(
                        item_id=f"state-change-{transition.transition_id}",
                        kind="state_change",
                        summary=(
                            f"{transition.subject}.{transition.attribute} "
                            f"changed to {transition.after}."
                        ),
                        why_matters_now=why_matters_now,
                        source_refs=[bundle_ref],
                    )
                )
                selected_transition_sources.add(transition_source)
                if bundle_ref not in selected_bundle_refs:
                    selected_bundle_refs.append(bundle_ref)

        missing_transition_sources = (
            set(selected_transition_reasons) - selected_transition_sources
        )
        if missing_transition_sources:
            raise ValueError(
                "Accepted Book state is missing a carry-forward source"
            )

        context = BookPlanningContext(
            book_number=book_number,
            generated_from=[series_ref, book_ref, *selected_bundle_refs],
            items=items,
            derivation_version=_BOOK_CONTEXT_DERIVATION_VERSION,
        )
        self.store.save_book_planning_context(context)
        return context

    def delete_derived_book_context(self, book_number: int) -> None:
        self.store.delete_book_planning_context(book_number)

    def propose_next_decision(
        self, book_number: int
    ) -> NextDecisionProposal:
        context = self.derive_book_context(book_number)
        self._validate_next_decision_context(context)

        proposal = NextDecisionProposal(
            proposal_id=f"book-{book_number}-next-decision-{uuid4().hex}",
            book_number=book_number,
            question=(
                "How should Book 2 turn the exposed founding fraud into a new "
                "conflict over official history?"
            ),
            recommended_option_id="center-living-witness",
            options=[
                DecisionOption(
                    option_id="center-living-witness",
                    label="Center a living witness",
                    summary=(
                        "Follow someone whose lived memory contradicts the "
                        "archive's newly exposed founding record."
                    ),
                    tradeoff=(
                        "This makes testimony and personal credibility central, "
                        "leaving the institutions that protected the fraud less "
                        "directly examined."
                    ),
                ),
                DecisionOption(
                    option_id="trace-institutional-cover-up",
                    label="Trace the cover-up",
                    summary=(
                        "Investigate who preserved the fraudulent founding "
                        "record and who still benefits from it."
                    ),
                    tradeoff=(
                        "This foregrounds institutional investigation, giving "
                        "less space to the lived memories harmed by the official "
                        "history."
                    ),
                ),
            ],
            rationale=(
                "Centering a living witness is preferred because the accepted "
                "Series commitment requires a consequential conflict between "
                "official history and lived memory, while the accepted "
                "founding-ledger exposure gives that witness a concrete record "
                "to contest."
            ),
            accepted_input_refs=context.generated_from,
        )
        self.store.save_next_decision_proposal(proposal)
        return proposal

    @staticmethod
    def _validate_next_decision_context(context: BookPlanningContext) -> None:
        context_item_ids = tuple(item.item_id for item in context.items)
        if (
            context.book_number != 2
            or context_item_ids != _BOOK_2_DECISION_CONTEXT_ITEMS
        ):
            raise ValueError(
                "The bounded Book 2 decision requires its two accepted "
                "carry-forward context items"
            )

    def record_decision_action(
        self,
        proposal_id: str,
        *,
        action: Literal["choose_recommended", "choose_other", "defer"],
        selected_option_id: str | None = None,
    ) -> DecisionAction:
        proposal = self.store.load_next_decision_proposal(proposal_id)
        existing_actions = self.store.load_decision_actions(proposal_id)
        option_ids = {option.option_id for option in proposal.options}

        if action == "choose_recommended":
            if (
                selected_option_id is not None
                and selected_option_id != proposal.recommended_option_id
            ):
                raise ValueError(
                    "The recommended action must select the recommended option"
                )
            selected_option_id = proposal.recommended_option_id
            status = "resolved"
        elif action == "choose_other":
            if selected_option_id not in option_ids:
                raise ValueError(
                    f"Unknown decision option: {selected_option_id}"
                )
            if selected_option_id == proposal.recommended_option_id:
                raise ValueError(
                    "Choose another option must select a presented alternative"
                )
            status = "resolved"
        elif action == "defer":
            if selected_option_id is not None:
                raise ValueError("A deferred decision cannot select an option")
            status = "deferred"
        else:
            raise ValueError(f"Unknown decision action: {action}")

        if proposal.status != "proposed":
            existing = existing_actions[0]
            if (
                existing.action == action
                and existing.selected_option_id == selected_option_id
            ):
                return existing
            raise ValueError(
                "Next Decision proposal already has a conflicting action"
            )

        current_context = self.derive_book_context(proposal.book_number)
        self._validate_next_decision_context(current_context)
        if proposal.accepted_input_refs != current_context.generated_from:
            raise ValueError(
                "Next Decision proposal accepted inputs are stale"
            )

        recorded = DecisionAction(
            proposal_id=proposal_id,
            action=action,
            selected_option_id=selected_option_id,
            recorded_at=datetime.now(timezone.utc),
        )
        self.store.validate_decision_action(proposal, recorded)
        self.store.save_decision_action_with_status(
            recorded,
            proposal.model_copy(update={"status": status}),
        )
        return recorded
