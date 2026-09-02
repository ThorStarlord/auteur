"""Author-facing product boundary for the bounded Global Map pilot."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from auteur.series.vertical_slice_models import (
    AcceptedContinuitySourceRef,
    ArtifactRef,
    ContinuityEntry,
    ContinuityGroup,
    GlobalMapEntry,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


class FocusConnection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation_id: str
    summary: str
    source_refs: list[AcceptedContinuitySourceRef] = Field(min_length=1)
    target_refs: list[AcceptedContinuitySourceRef] = Field(min_length=1)


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
        "Review affected accepted artifacts; no downstream artifact was rewritten."
    )


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
        entry_by_fact: dict[str, GlobalMapEntry] = {
            entry.fact_ref.fact_id: entry
            for entry in snapshot.entries
            if entry.fact_ref is not None
        }
        connections = []
        for relation in snapshot.relations:
            if relation.kind != "causal_support":
                continue
            source_entry = entry_by_fact.get(relation.source_fact_ref.fact_id)
            target_entry = entry_by_fact.get(relation.target_fact_ref.fact_id)
            source_meaning = source_entry.explanation if source_entry and source_entry.explanation else source_entry.summary if source_entry else relation.source_fact_ref.fact_id
            target_meaning = target_entry.explanation if target_entry and target_entry.explanation else target_entry.summary if target_entry else relation.target_fact_ref.fact_id
            connections.append(
                FocusConnection(
                    relation_id=relation.relation_id,
                    summary=(
                        f"{relation.source_fact_ref.fact_id} ({source_meaning}) supports "
                        f"{relation.target_fact_ref.fact_id} ({target_meaning}) — earlier narrative history enables the later consequence."
                    ),
                    source_refs=[relation.source_fact_ref],
                    target_refs=[relation.target_fact_ref],
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
