"""Author-facing product boundary for the bounded Global Map pilot."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from auteur.series.vertical_slice_models import (
    AcceptedContinuitySourceRef,
    ArtifactRef,
    ContinuityEntry,
    ContinuityGroup,
    DirectionCommitment,
    MapCurrentStateEvidence,
    RelationDisposition,
    RelationOrigin,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


class FocusConnection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation_id: str
    summary: str
    source_refs: list[AcceptedContinuitySourceRef] = Field(min_length=1)
    target_refs: list[AcceptedContinuitySourceRef] = Field(min_length=1)
    origin: RelationOrigin
    disposition: RelationDisposition
    rule_version: str | None = None
    evidence_refs: list[AcceptedContinuitySourceRef] = Field(default_factory=list)
    source_revision_refs: list[ArtifactRef] = Field(default_factory=list)


class ImpactItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    book_number: int = Field(ge=1)
    freshness: str
    semantic_impact: str
    reconciliation_required: bool


class AuthorFocusReport(BaseModel):
    """Small, read-only projection of a derived Global Map for one decision."""

    model_config = ConfigDict(extra="forbid")

    book_number: int = Field(gt=1)
    decision: str
    active_constraints: list[ContinuityEntry] = Field(default_factory=list)
    relevant_history: list[ContinuityEntry] = Field(default_factory=list)
    persistent_pressures: list[ContinuityGroup] = Field(default_factory=list)
    long_range_connections: list[FocusConnection] = Field(default_factory=list)
    risks_or_conflicts: list[str] = Field(default_factory=list)
    provenance: list[ArtifactRef] = Field(min_length=1)
    map_snapshot_id: str
    map_freshness: str
    semantic_impact: str


class RevisionImpactReport(BaseModel):
    """Impact handoff for author review; it never changes accepted artifacts."""

    model_config = ConfigDict(extra="forbid")

    affected_artifacts: list[ImpactItem] = Field(default_factory=list)
    review_order: list[str] = Field(default_factory=list)
    series_direction_impact: list[dict[str, object]] = Field(default_factory=list)
    reconciliation_boundary: str = (
        "Affected accepted artifacts remain accepted; no downstream artifact was rewritten."
    )


class ContinuityImpactReport(BaseModel):
    """Impact evidence composed for continuity review, without review priority."""

    model_config = ConfigDict(extra="forbid")

    affected_artifacts: list[ImpactItem] = Field(default_factory=list)
    series_direction_impact: list[dict[str, object]] = Field(default_factory=list)
    reconciliation_boundary: str = (
        "Affected accepted artifacts remain accepted; no downstream artifact was rewritten."
    )


class SeriesContinuityReviewReport(BaseModel):
    """Read-only composition of accepted Series continuity for one Book."""

    model_config = ConfigDict(extra="forbid")

    book_number: int = Field(gt=1)
    planning_intent: str
    promise: str
    pressure: str
    open_question: str
    active_commitments: list[DirectionCommitment] = Field(default_factory=list)
    resolved_commitments: list[DirectionCommitment] = Field(default_factory=list)
    current_context: list[ContinuityEntry] = Field(default_factory=list)
    relevant_history: list[ContinuityEntry] = Field(default_factory=list)
    current_state_evidence: dict[str, MapCurrentStateEvidence] = Field(
        default_factory=dict
    )
    revision_impact: ContinuityImpactReport
    supporting_connections: list[FocusConnection] = Field(default_factory=list)
    provenance: list[ArtifactRef] = Field(min_length=1)
    map_snapshot_id: str
    freshness: str
    semantic_impact: str
    warnings: list[str] = Field(default_factory=list)


class SeriesProductizationService:
    """Normal-project façade over the existing accepted-state slice service."""

    def __init__(self, project_root: Path) -> None:
        self.service = SeriesVerticalSliceService(project_root)

    def build_global_map(self, horizon: int):
        """Build the disposable Map from the current accepted project state."""
        return self.service.build_global_map(horizon)

    def build_focus(self, horizon: int) -> AuthorFocusReport:
        """Rebuild and render a Focus without creating or changing story authority."""
        snapshot = self.build_global_map(horizon)
        context = self.service.derive_focus_from_global_map(horizon)
        connections = []
        for relation in snapshot.relations:
            if relation.kind != "causal_support":
                continue
            connections.append(
                FocusConnection(
                    relation_id=relation.relation_id,
                    summary=(
                        "Accepted history connects an earlier state to a later "
                        "state across the Series."
                    ),
                    source_refs=[relation.source_fact_ref],
                    target_refs=[relation.target_fact_ref],
                    origin=relation.origin,
                    disposition=relation.disposition,
                    rule_version=relation.rule_version,
                    evidence_refs=relation.evidence_refs,
                    source_revision_refs=relation.source_revision_refs,
                )
            )
        risks = []
        if snapshot.semantic_impact != "clear":
            risks.append(
                f"Accepted history has {snapshot.semantic_impact} semantic impact; review before relying on this Focus."
            )
        return AuthorFocusReport(
            book_number=horizon,
            decision=self.service.store.load_book_planning_intent(horizon).intent,
            active_constraints=list(context.entries),
            relevant_history=list(context.history_entries),
            persistent_pressures=list(context.groups),
            long_range_connections=connections,
            risks_or_conflicts=risks,
            provenance=list(snapshot.source_revisions),
            map_snapshot_id=snapshot.snapshot_id,
            map_freshness=snapshot.freshness,
            semantic_impact=snapshot.semantic_impact,
        )

    def revision_impact(self) -> RevisionImpactReport:
        """Aggregate existing impact reports into an author review handoff."""
        items: list[ImpactItem] = []
        for bundle, _metadata in self.service.store.load_accepted_realization_bundles():
            result = self.service.realization_impact(bundle.artifact_id)
            items.append(
                ImpactItem(
                    artifact_id=bundle.artifact_id,
                    book_number=bundle.book_number,
                    freshness=str(result["freshness"]),
                    semantic_impact=str(result["semantic_impact"]),
                    reconciliation_required=bool(result["reconciliation_required"]),
                )
            )
        affected = [item for item in items if item.reconciliation_required]
        affected.sort(key=lambda item: item.book_number)
        return RevisionImpactReport(
            affected_artifacts=affected,
            review_order=[item.artifact_id for item in affected],
            series_direction_impact=self.service.series_impact(),
        )

    def build_continuity_review(self, book_number: int) -> SeriesContinuityReviewReport:
        """Compose existing Series intelligence without recording review state."""
        planning_intent = self.service.store.load_book_planning_intent(book_number)
        if planning_intent is None:
            raise ValueError(
                f"An explicit Book {book_number} planning intent is required "
                "before continuity review"
            )
        accepted_series = self.service.load_accepted_series_direction()
        if accepted_series is None:
            raise ValueError(
                "An accepted Series Direction is required before continuity review"
            )
        history = self.service.load_repeated_history_for_book(book_number)
        focus = self.build_focus(book_number)
        snapshot = self.service.load_global_map(book_number)
        if snapshot is None:
            raise ValueError("A Global Map is required before continuity review")
        resolved_ids = set(history.explicitly_resolved_commitment_ids)
        commitments = accepted_series.direction.commitments
        impact = self.revision_impact()
        continuity_impact = ContinuityImpactReport(
            affected_artifacts=impact.affected_artifacts,
            series_direction_impact=impact.series_direction_impact,
            reconciliation_boundary=impact.reconciliation_boundary,
        )
        return SeriesContinuityReviewReport(
            book_number=book_number,
            planning_intent=planning_intent.intent,
            promise=accepted_series.direction.promise,
            pressure=accepted_series.direction.pressure,
            open_question=accepted_series.direction.open_question,
            active_commitments=[
                item for item in commitments if item.commitment_id not in resolved_ids
            ],
            resolved_commitments=[
                item for item in commitments if item.commitment_id in resolved_ids
            ],
            current_context=focus.active_constraints,
            relevant_history=focus.relevant_history,
            current_state_evidence=snapshot.current_state_evidence,
            revision_impact=continuity_impact,
            supporting_connections=focus.long_range_connections,
            provenance=snapshot.source_revisions,
            map_snapshot_id=snapshot.snapshot_id,
            freshness=snapshot.freshness,
            semantic_impact=snapshot.semantic_impact,
            warnings=focus.risks_or_conflicts,
        )
