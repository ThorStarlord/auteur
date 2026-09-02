from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Iterable, Literal
from uuid import uuid4

from auteur.provenance import ArtifactMetadata
from auteur.series.repeated_map_focus import (
    AcceptedHistorySnapshot,
    CurrentStateEvidence,
    RepeatedBookPlanningContext,
    RepeatedDecisionSeed,
    select_focus_from_global_map,
    select_repeated_continuity,
    selection_token_display,
    selection_token_for,
    validate_repeated_decision_proposal as validate_repeated_proposal,
)
from auteur.series.vertical_slice_models import (
    AcceptedFactRef,
    AcceptedBookDirection,
    AcceptedRealizationBundle,
    AcceptedSeriesDirection,
    ArtifactRef,
    BookDirection,
    BookDirectionProposal,
    BookPlanningContext,
    BookPlanningIntent,
    CanonicalState,
    CausalSupportRelation,
    CommitmentRef,
    GlobalMapEntry,
    GlobalMapSnapshot,
    MapCurrentStateEvidence,
    PressureGroupMember,
    PressureGroupRelation,
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
        accepted_series, _series_metadata = self._accepted_series_source()
        known_commitment_ids = {
            commitment.commitment_id
            for commitment in accepted_series.direction.commitments
        }
        unknown_resolved_ids = sorted(
            set(candidate.resolved_commitment_ids) - known_commitment_ids
        )
        if unknown_resolved_ids:
            raise ValueError(
                "Unknown accepted Series commitment resolution(s): "
                + ", ".join(unknown_resolved_ids)
            )
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
            resolved_commitment_ids=candidate.resolved_commitment_ids,
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

    def accept_realization_revision(
        self,
        artifact_id: str,
        candidate_id: str,
        *,
        accepted_by: str,
        rationale: str | None = None,
    ) -> AcceptedRealizationBundle:
        """Accept a new payload revision without changing narrative identity."""
        current = next(
            (
                bundle
                for bundle, _metadata in self.store.load_accepted_realization_bundles()
                if bundle.artifact_id == artifact_id
            ),
            None,
        )
        if current is None:
            raise ValueError(f"Unknown accepted realization: {artifact_id}")
        candidate = self.store.load_realization_candidate(candidate_id)
        if candidate.book_number != current.book_number:
            raise ValueError("Realization revision cannot change books")
        accepted_series, _series_metadata = self._accepted_series_source()
        known_commitment_ids = {
            commitment.commitment_id
            for commitment in accepted_series.direction.commitments
        }
        unknown_resolved_ids = sorted(
            set(candidate.resolved_commitment_ids) - known_commitment_ids
        )
        if unknown_resolved_ids:
            raise ValueError(
                "Unknown accepted Series commitment resolution(s): "
                + ", ".join(unknown_resolved_ids)
            )
        current_source = self._current_book_source_ref(candidate.book_number)
        if candidate.source_refs != [current_source]:
            raise ValueError(
                "Realization revision does not reference the current accepted "
                "Book Direction revision"
            )
        accepted = AcceptedRealizationBundle(
            artifact_id=current.artifact_id,
            bundle_id=current.bundle_id,
            candidate_id=candidate.candidate_id,
            book_number=current.book_number,
            transitions=candidate.transitions,
            resolved_commitment_ids=candidate.resolved_commitment_ids,
        )
        self.store.save_accepted_realization_bundle(
            accepted,
            book_source=current_source,
            accepted_by=accepted_by,
            rationale=rationale,
        )
        self.rebuild_canonical_state(allow_conflicts=True)
        return accepted

    def rebuild_canonical_state(self, *, allow_conflicts: bool = False) -> CanonicalState:
        bundles = [
            bundle
            for bundle, _metadata in (
                self.store.load_accepted_realization_bundles()
            )
        ]
        state = self._canonical_state_from_bundles(
            bundles, allow_conflicts=allow_conflicts
        )
        self.store.save_canonical_state(state)
        return state

    @staticmethod
    def _canonical_state_from_bundles(
        bundles: Iterable[AcceptedRealizationBundle],
        *,
        allow_conflicts: bool = False,
    ) -> CanonicalState:
        values: dict[str, str] = {}
        applied_bundle_ids: list[str] = []
        conflicts: list[str] = []
        state_version = 0
        for bundle in bundles:
            for transition in bundle.transitions:
                key = f"{transition.subject}.{transition.attribute}"
                # A null before value means the attribute must not exist yet.
                if transition.before is None:
                    if key in values:
                        if not allow_conflicts:
                            raise ValueError(
                                f"State transition {transition.transition_id} before "
                                f"value requires initial absence for {key}"
                            )
                        conflicts.append(
                            f"{transition.transition_id}: expected initial absence for {key}"
                        )
                elif values.get(key) != transition.before:
                    if not allow_conflicts:
                        raise ValueError(
                            f"State transition {transition.transition_id} before "
                            f"value does not match {key}"
                        )
                    conflicts.append(
                        f"{transition.transition_id}: expected {key}={transition.before!r}, "
                        f"found {values.get(key)!r}"
                    )
                values[key] = transition.after
            applied_bundle_ids.append(bundle.bundle_id)
            state_version += 1
        state = CanonicalState(
            state_version=state_version,
            values=values,
            applied_bundle_ids=applied_bundle_ids,
            conflicts=conflicts,
        )
        return state

    def load_canonical_state(self) -> CanonicalState:
        return self.store.load_canonical_state()

    def load_repeated_history_for_book(
        self, book_number: int
    ) -> AcceptedHistorySnapshot:
        """Load accepted authority through book_number - 1 only."""
        if book_number <= 1:
            raise ValueError(
                "Repeated history requires a planning Book number greater than 1"
            )

        accepted_series, series_metadata = self._accepted_series_source()
        self.store.validate_book_context_source(
            series_metadata,
            artifact_id=accepted_series.artifact_id,
            artifact_type="series_direction",
            path=self.store.accepted_series_direction_path,
        )
        series_ref = ArtifactRef(
            artifact_id=accepted_series.artifact_id,
            revision=series_metadata.revision,
        )

        books: list[AcceptedBookDirection] = []
        book_refs: list[ArtifactRef] = []
        for accepted_book_number in range(1, book_number):
            accepted_book, book_metadata = self._accepted_book_source(
                accepted_book_number
            )
            self.store.validate_book_context_source(
                book_metadata,
                artifact_id=accepted_book.artifact_id,
                artifact_type="book_direction",
                path=self.store.accepted_book_direction_path(
                    accepted_book_number
                ),
            )
            books.append(accepted_book)
            book_refs.append(
                ArtifactRef(
                    artifact_id=accepted_book.artifact_id,
                    revision=book_metadata.revision,
                )
            )

        realizations: list[AcceptedRealizationBundle] = []
        realization_refs: list[ArtifactRef] = []
        for bundle, metadata in self.store.load_accepted_realization_bundles():
            if bundle.book_number >= book_number:
                continue
            self.store.validate_book_context_source(
                metadata,
                artifact_id=bundle.artifact_id,
                artifact_type="accepted_realization_bundle",
                path=self.store.accepted_realization_bundle_path(
                    bundle.bundle_id
                ),
            )
            realizations.append(bundle)
            realization_refs.append(
                ArtifactRef(
                    artifact_id=bundle.artifact_id,
                    revision=metadata.revision,
                )
            )

        explicitly_resolved_commitment_ids = tuple(
            dict.fromkeys(
                commitment_id
                for bundle in realizations
                for commitment_id in bundle.resolved_commitment_ids
            )
        )
        accepted_fact_refs = tuple(
            AcceptedFactRef(
                artifact_id=bundle.artifact_id,
                revision=realization_ref.revision,
                fact_id=transition.transition_id,
            )
            for bundle, realization_ref in zip(
                realizations, realization_refs, strict=True
            )
            for transition in bundle.transitions
        )

        return AcceptedHistorySnapshot(
            planning_book_number=book_number,
            series=accepted_series,
            series_ref=series_ref,
            books=tuple(books),
            book_refs=tuple(book_refs),
            realizations=tuple(realizations),
            realization_refs=tuple(realization_refs),
            explicitly_resolved_commitment_ids=(
                explicitly_resolved_commitment_ids
            ),
            accepted_fact_refs=accepted_fact_refs,
            canonical_state=self._canonical_state_from_bundles(
                realizations, allow_conflicts=True
            ),
        )

    def derive_current_state_evidence(
        self, book_number: int
    ) -> dict[str, CurrentStateEvidence]:
        history = self.load_repeated_history_for_book(book_number)
        evidence: dict[str, CurrentStateEvidence] = {}
        for bundle, realization_ref in zip(
            history.realizations, history.realization_refs, strict=True
        ):
            for transition in bundle.transitions:
                key = f"{transition.subject}.{transition.attribute}"
                previous = evidence.get(key)
                superseded_fact_ids = (
                    ()
                    if previous is None
                    else (
                        *previous.superseded_fact_ids,
                        previous.current_fact_id,
                    )
                )
                evidence[key] = CurrentStateEvidence(
                    key=key,
                    current_value=transition.after,
                    current_fact_id=transition.transition_id,
                    current_source_ref=AcceptedFactRef(
                        artifact_id=bundle.artifact_id,
                        revision=realization_ref.revision,
                        fact_id=transition.transition_id,
                    ),
                    superseded_fact_ids=superseded_fact_ids,
                )
        return evidence

    def build_global_map(self, book_number: int) -> GlobalMapSnapshot:
        """Build the deterministic, disposable whole-history Map projection."""
        history = self.load_repeated_history_for_book(book_number)
        current_evidence = self.derive_current_state_evidence(book_number)
        source_revisions = [
            history.series_ref,
            *history.book_refs,
            *history.realization_refs,
        ]
        fact_rows = [
            (bundle, ref, transition)
            for bundle, ref in zip(
                history.realizations, history.realization_refs, strict=True
            )
            for transition in bundle.transitions
        ]
        fact_refs = [
            AcceptedFactRef(
                artifact_id=bundle.artifact_id,
                revision=ref.revision,
                fact_id=transition.transition_id,
            )
            for bundle, ref, transition in fact_rows
        ]
        relations: list[CausalSupportRelation | PressureGroupRelation] = []
        causal_pairs: list[tuple[AcceptedFactRef, AcceptedFactRef]] = []
        for earlier_index, (earlier_bundle, earlier_ref, earlier) in enumerate(
            fact_rows
        ):
            for later_bundle, later_ref, later in fact_rows[earlier_index + 1 :]:
                if (
                    earlier_bundle.book_number < later_bundle.book_number
                    and earlier.subject == later.subject
                    and earlier.attribute == later.attribute
                    and earlier.after == later.before
                ):
                    source = AcceptedFactRef(
                        artifact_id=earlier_bundle.artifact_id,
                        revision=earlier_ref.revision,
                        fact_id=earlier.transition_id,
                    )
                    target = AcceptedFactRef(
                        artifact_id=later_bundle.artifact_id,
                        revision=later_ref.revision,
                        fact_id=later.transition_id,
                    )
                    causal_pairs.append((source, target))
                    relations.append(
                        CausalSupportRelation(
                            relation_id=(
                                "causal-support-"
                                f"{source.artifact_id}-{source.revision}-"
                                f"{source.fact_id}-"
                                f"{target.artifact_id}-{target.revision}-"
                                f"{target.fact_id}"
                            ),
                            origin="DETERMINISTIC_DERIVATION",
                            source_fact_ref=source,
                            target_fact_ref=target,
                            evidence_refs=[source, target],
                            source_revision_refs=[
                                ArtifactRef(
                                    artifact_id=source.artifact_id,
                                    revision=source.revision,
                                ),
                                ArtifactRef(
                                    artifact_id=target.artifact_id,
                                    revision=target.revision,
                                ),
                            ],
                            rule_version="accepted-state-support-v1",
                        )
                    )
        map_entries = [
            GlobalMapEntry(
                entry_id=commitment.commitment_id,
                kind="commitment",
                summary=commitment.statement,
                source_refs=[
                    history.series_ref,
                    *[
                        book_ref
                        for book, book_ref in zip(
                            history.books, history.book_refs, strict=True
                        )
                        if commitment.commitment_id
                        in book.direction.series_commitment_ids
                    ],
                ],
                disposition=(
                    "resolved"
                    if commitment.commitment_id
                    in history.explicitly_resolved_commitment_ids
                    else "active"
                ),
            )
            for commitment in history.series.direction.commitments
            if any(
                commitment.commitment_id in book.direction.series_commitment_ids
                for book in history.books
            )
        ]
        map_entries.extend(
            GlobalMapEntry(
                entry_id=(
                    f"{ref.artifact_id}@{ref.revision}/"
                    f"{transition.transition_id}"
                ),
                kind="fact",
                summary=(
                    f"{transition.subject}.{transition.attribute} is "
                    f"{transition.after}."
                ),
                source_refs=[ref],
                disposition=(
                    "active"
                    if any(
                        evidence.current_source_ref == ref
                        for evidence in current_evidence.values()
                    )
                    else "superseded"
                ),
                currentness=(
                    "current"
                    if any(
                        evidence.current_source_ref == ref
                        for evidence in current_evidence.values()
                    )
                    else "historical"
                ),
                is_current_constraint=any(
                    evidence.current_source_ref == ref
                    for evidence in current_evidence.values()
                ),
                fact_ref=ref,
                subject=transition.subject,
                attribute=transition.attribute,
                before=transition.before,
                after=transition.after,
                explanation=transition.explanation,
                book_number=bundle.book_number,
                commitment_ids=[
                    commitment.commitment_id
                    for commitment in history.series.direction.commitments
                    if any(
                        commitment.commitment_id in book.direction.series_commitment_ids
                        for book in history.books
                        if book.direction.book_number == bundle.book_number
                    )
                ],
            )
            for (bundle, ref, transition), ref in zip(
                fact_rows, fact_refs, strict=True
            )
        )
        for commitment in history.series.direction.commitments:
            fact_refs_for_commitment = [
                ref
                for (bundle, _bundle_ref, transition), ref in zip(
                    fact_rows, fact_refs, strict=True
                )
                if any(
                    commitment.commitment_id in book.direction.series_commitment_ids
                    for book in history.books
                    if book.direction.book_number == bundle.book_number
                )
            ]
            causal_sources = {
                (source.artifact_id, source.revision, source.fact_id)
                for source, _target in causal_pairs
            }
            causal_targets = {
                (target.artifact_id, target.revision, target.fact_id)
                for _source, target in causal_pairs
            }
            members = []
            for ref in fact_refs_for_commitment:
                role = (
                    "current_constraint"
                    if any(
                        evidence.current_source_ref == ref
                        for evidence in current_evidence.values()
                    )
                    else "causal_pivot"
                    if (ref.artifact_id, ref.revision, ref.fact_id)
                    in causal_targets
                    else "originating_history"
                    if (ref.artifact_id, ref.revision, ref.fact_id)
                    in causal_sources
                    else None
                )
                if role is not None:
                    members.append(PressureGroupMember(fact_ref=ref, role=role))
            if len(members) >= 2:
                relations.append(
                    PressureGroupRelation(
                        relation_id=f"pressure-group-{commitment.commitment_id}",
                        origin="DETERMINISTIC_DERIVATION",
                        target_commitment_or_pressure_ref=CommitmentRef(
                            artifact_id=history.series_ref.artifact_id,
                            revision=history.series_ref.revision,
                            commitment_id=commitment.commitment_id,
                        ),
                        members=members,
                        evidence_refs=[member.fact_ref for member in members],
                        source_revision_refs=source_revisions,
                        rule_version="archive-of-lies-v1",
                    )
                )
        pressure_groups = [
            relation
            for relation in relations
            if isinstance(relation, PressureGroupRelation)
        ]
        state_evidence = {
            key: MapCurrentStateEvidence(
                key=value.key,
                current_value=value.current_value,
                current_fact_ref=value.current_source_ref,
                superseded_fact_ids=value.superseded_fact_ids,
            )
            for key, value in current_evidence.items()
        }
        currentness = {
            f"{ref.artifact_id}@{ref.revision}/{ref.fact_id}": (
                "active"
                if any(
                    evidence.current_fact_ref == ref
                    for evidence in state_evidence.values()
                )
                else "superseded"
            )
            for ref in fact_refs
        }
        fingerprint_payload = {
            "source_revisions": [ref.model_dump(mode="json") for ref in source_revisions],
            "state": {key: value.model_dump(mode="json") for key, value in state_evidence.items()},
            "relations": [relation.model_dump(mode="json") for relation in relations],
        }
        fingerprint = hashlib.sha256(
            json.dumps(fingerprint_payload, sort_keys=True).encode()
        ).hexdigest()
        snapshot = GlobalMapSnapshot(
            snapshot_id=f"global-map-book-{book_number}",
            planning_book_number=book_number,
            source_revisions=source_revisions,
            current_state_evidence=state_evidence,
            entries=map_entries,
            historical_fact_refs=fact_refs,
            relations=relations,
            pressure_groups=pressure_groups,
            currentness=currentness,
            derivation_version="global-map-v1",
            source_fingerprint=fingerprint,
            semantic_impact="contradictory" if history.canonical_state.conflicts else "clear",
        )
        self.store.save_global_map(snapshot)
        return snapshot

    def load_global_map(self, book_number: int) -> GlobalMapSnapshot | None:
        snapshot = self.store.load_global_map(book_number)
        if snapshot is None:
            return None
        current_refs = {
            ref.artifact_id: ref.revision for ref in snapshot.source_revisions
        }
        stale = any(
            (metadata := self.store.artifact_store.current(artifact_id)) is None
            or metadata.revision != revision
            for artifact_id, revision in current_refs.items()
        )
        return snapshot.model_copy(update={"freshness": "stale" if stale else "fresh"})

    def delete_global_map(self, book_number: int) -> None:
        self.store.delete_global_map(book_number)

    def derive_focus_from_global_map(self, book_number: int) -> RepeatedBookPlanningContext:
        snapshot = self.load_global_map(book_number)
        if snapshot is None:
            raise ValueError("A Global Map must be built before Focus")
        if snapshot.freshness == "stale":
            raise ValueError("Global Map is stale; rebuild it before Focus")
        planning_intent = self.store.load_book_planning_intent(book_number)
        if planning_intent is None:
            raise ValueError("A Book planning intent is required before Focus")
        context = select_focus_from_global_map(snapshot, planning_intent)
        self.store.save_repeated_book_context(context)
        return context

    def realization_impact(self, artifact_id: str) -> dict[str, object]:
        path = self.store.accepted_realization_bundle_path(artifact_id)
        status = self.store.artifact_store.status(path, "accepted_realization_bundle")
        state = self.load_canonical_state()
        conflict_transition_ids = {
            conflict.split(":", 1)[0] for conflict in state.conflicts
        }
        loaded = self.store.load_accepted_realization_bundles()
        metadata_by_id = {bundle.artifact_id: metadata for bundle, metadata in loaded}
        affected_ids: set[str] = set()
        changed_ids = {
            dependency.artifact_id
            for metadata in metadata_by_id.values()
            for dependency in metadata.dependencies
            if dependency.revision is not None
            and (
                current := self.store.artifact_store.current(dependency.artifact_id)
            ) is not None
            and current.revision > dependency.revision
        }
        pending = list(changed_ids)
        while pending:
            changed = pending.pop()
            for dependent_id, metadata in metadata_by_id.items():
                if any(
                    dependency.artifact_id == changed
                    for dependency in metadata.dependencies
                ) and dependent_id not in affected_ids:
                    affected_ids.add(dependent_id)
                    pending.append(dependent_id)
        target_bundle = next(
            (bundle for bundle, _metadata in loaded if bundle.artifact_id == artifact_id),
            None,
        )
        affected = artifact_id in affected_ids or (
            target_bundle is not None
            and any(
                transition.transition_id in conflict_transition_ids
                for transition in target_bundle.transitions
            )
        )
        effective_freshness = (
            "stale" if artifact_id in affected_ids else status.freshness
        )
        semantic_impact = "contradictory" if affected else "clear"
        return {
            "artifact_id": artifact_id,
            "health": status.health,
            "freshness": effective_freshness,
            "semantic_impact": semantic_impact,
            "reconciliation_required": (
                effective_freshness == "stale"
                or semantic_impact in {"suspect", "contradictory"}
            ),
        }

    def series_impact(self) -> list[dict[str, object]]:
        """Report accepted Book artifacts affected by the current Series revision."""
        affected: list[dict[str, object]] = []
        for path in sorted(
            (self.store.root / "accepted").glob("book-*-direction.yaml")
        ):
            book_number = int(path.stem.split("-")[1])
            status = self.store.artifact_store.status(path, "book_direction")
            affected.append(
                {
                    "book_number": book_number,
                    "artifact_id": path.stem,
                    "lifecycle": status.lifecycle.value,
                    "freshness": status.freshness,
                    "reconciliation_required": status.freshness == "stale",
                }
            )
        return affected

    def derive_repeated_book_context(
        self, book_number: int
    ) -> RepeatedBookPlanningContext:
        """Derive opening Book-N continuity from accepted history through N-1."""
        planning_entry = self.store.load_planning_entry(book_number)
        planning_intent = self.store.load_book_planning_intent(book_number)
        if planning_entry is None or planning_intent is None:
            raise ValueError(
                f"An explicit Book {book_number} planning intent is required "
                "before repeated continuity can be derived"
            )

        history = self.load_repeated_history_for_book(book_number)
        unknown_refs = [
            ref
            for ref in planning_intent.relevance_refs
            if ref not in history.accepted_fact_refs
        ]
        if unknown_refs:
            raise ValueError(
                "Planning intent relevance reference(s) are not in accepted "
                "history"
            )
        context = select_repeated_continuity(
            history,
            planning_intent,
            self.derive_current_state_evidence(book_number),
        )
        self.store.save_repeated_book_context(context)
        return context

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

    def list_accepted_facts(self, book_number: int) -> list[AcceptedFactRef]:
        """Return the accepted-fact refs through Book ``book_number - 1``.

        Deterministic: order derives from the already-deterministic accepted
        realization bundle ordering (sorted artifact ids) and each bundle's
        transition order. Only accepted facts are returned; proposed or
        unaccepted candidates never appear.
        """
        return [ref for _book, _position, ref in self._accepted_fact_rows(
            book_number
        )]

    def _accepted_fact_rows(
        self, book_number: int
    ) -> list[tuple[int, int, AcceptedFactRef]]:
        """Ordered ``(source_book, position_within_book, ref)`` accepted facts.

        ``position_within_book`` is 1-based and derives from the deterministic
        accepted realization bundle order, then each bundle's transition order.
        This is the single ordering both listing and resolution consume, so a
        selection token always reproduces the same display position for the same
        accepted snapshot.
        """
        history = self.load_repeated_history_for_book(book_number)
        rows: list[tuple[int, int, AcceptedFactRef]] = []
        counters: dict[int, int] = {}
        for bundle, realization_ref in zip(
            history.realizations, history.realization_refs, strict=True
        ):
            position = counters.get(bundle.book_number, 0) + 1
            for transition in bundle.transitions:
                counters[bundle.book_number] = position
                rows.append(
                    (
                        bundle.book_number,
                        position,
                        AcceptedFactRef(
                            artifact_id=bundle.artifact_id,
                            revision=realization_ref.revision,
                            fact_id=transition.transition_id,
                        ),
                    )
                )
                position += 1
        return rows

    def resolve_accepted_fact_selection_token(
        self, book_number: int, token: str
    ) -> AcceptedFactRef:
        """Resolve a selection token to exactly one exact AcceptedFactRef.

        The token must identify a current accepted fact for ``book_number``.
        Both a full display token (``B{book}-{position}~{fingerprint}``) and a
        bare fingerprint are accepted. Fail closed: zero matches raises
        (invalid/stale), more than one match raises (ambiguous). No fuzzy
        fallback and no alias system.
        """
        matches = []
        for source_book, position, ref in self._accepted_fact_rows(book_number):
            full = selection_token_display(
                source_book, position, ref
            )
            if token == full or token == selection_token_for(ref):
                matches.append(ref)
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValueError(
                f"Selection token {token!r} is ambiguous; it does not identify "
                "a single accepted fact"
            )
        raise ValueError(
            f"Selection token {token!r} no longer identifies a current accepted "
            "fact for this Book; re-list the accepted facts"
        )

    def enter_repeated_book_planning(
        self,
        book_number: int,
        *,
        entered_by: str,
        intent: str,
        relevance_refs: list[AcceptedFactRef],
    ) -> BookPlanningIntent:
        planning_intent = BookPlanningIntent(
            book_number=book_number,
            intent=intent,
            relevance_refs=relevance_refs,
        )
        accepted_history = self.load_repeated_history_for_book(book_number)
        unknown_refs = [
            ref
            for ref in planning_intent.relevance_refs
            if ref not in accepted_history.accepted_fact_refs
        ]
        if unknown_refs:
            rendered_refs = ", ".join(
                f"{ref.artifact_id}@{ref.revision}/{ref.fact_id}"
                for ref in unknown_refs
            )
            raise ValueError(
                "Planning intent relevance reference(s) are not in accepted "
                f"history: {rendered_refs}"
            )
        self.enter_book_planning(book_number, entered_by=entered_by)
        self.store.save_book_planning_intent(planning_intent)
        return planning_intent

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

    def propose_repeated_next_decision(
        self,
        book_number: int,
        *,
        decision_seed: RepeatedDecisionSeed,
    ) -> NextDecisionProposal:
        """Build a bounded proposal from the current repeated context."""
        if book_number <= 2:
            raise ValueError(
                "Repeated Next Decision proposals require Book 3 or later"
            )
        context = self.derive_repeated_book_context(book_number)
        proposal = NextDecisionProposal(
            proposal_id=(
                f"book-{book_number}-next-decision-{uuid4().hex}"
            ),
            book_number=book_number,
            question=decision_seed.question,
            recommended_option_id=decision_seed.recommended_option_id,
            options=tuple(
                option.model_copy(deep=True)
                for option in decision_seed.options
            ),
            rationale=decision_seed.rationale,
            accepted_input_refs=context.generated_from,
        )
        self.store.save_next_decision_proposal(proposal)
        return proposal

    def validate_repeated_decision_proposal(
        self,
        proposal: NextDecisionProposal,
    ) -> None:
        context = self.derive_repeated_book_context(proposal.book_number)
        validate_repeated_proposal(proposal, context)

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

        if proposal.book_number == 2:
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
        if proposal.book_number > 2:
            self.validate_repeated_decision_proposal(proposal)
        self.store.save_decision_action_with_status(
            recorded,
            proposal.model_copy(update={"status": status}),
        )
        return recorded
