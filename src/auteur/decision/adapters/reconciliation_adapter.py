"""Read-only reconciliation adapter — loads proposals, conflicts, and author choices.

This adapter replaces convergence-proposal-embedded data with direct reads
from the expression-layer ReconciliationStore. It distinguishes technical
reconciliation conflicts from creative author decisions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from auteur.decision.models import (
    DecisionEvidence,
    EvidenceClassification,
    EvidenceFreshness,
    EvidenceSource,
    EvidenceType,
    UnresolvedChoice,
)


class ReconciliationAdapter:
    """Query interface to the expression reconciliation subsystem.

    All methods are read-only; no reconciliation artifacts are created
    or modified.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.read_errors: list[str] = []

    # ------------------------------------------------------------------
    # Proposal queries
    # ------------------------------------------------------------------

    def load_proposals(self, artifact_id: str) -> list[dict[str, Any]]:
        """Load reconciliation proposals for an artifact.

        Delegates to ``ReconciliationStore`` from the expression layer.
        Returns empty list if the reconciliation subsystem has no data.
        """
        proposals: list[dict[str, Any]] = []
        proposal_root = self.project_root / "chapters"
        if not proposal_root.exists():
            return proposals

        # ReconciliationStore owns the artifact layout.  This adapter remains
        # read-only and deliberately uses the same project-relative location
        # rather than copying proposal data into the decision subsystem.
        for path in sorted(proposal_root.glob("*/expression/reconciliation/proposals/*.yaml")):
            try:
                proposal = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except (OSError, yaml.YAMLError):
                self.read_errors.append(str(path))
                continue
            if not isinstance(proposal, dict):
                continue
            source_assembly = proposal.get("source_assembly") or {}
            if (
                proposal.get("target_artifact_id") == artifact_id
                or source_assembly.get("artifact_id") == artifact_id
            ):
                proposals.append(proposal)
        return proposals

    def load_proposal_lineage(self, proposal_id: str) -> list[dict[str, Any]]:
        """Track the chain of proposals for lineage."""
        proposal = self._load_proposal(proposal_id)
        if proposal is None:
            return []
        source_inspection = proposal.get("source_inspection")
        if not source_inspection:
            return [proposal]
        lineage = []
        for path in sorted(self.project_root.glob("chapters/*/expression/reconciliation/proposals/*.yaml")):
            try:
                candidate = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except (OSError, yaml.YAMLError):
                self.read_errors.append(str(path))
                continue
            if isinstance(candidate, dict) and candidate.get("source_inspection") == source_inspection:
                lineage.append(candidate)
        return lineage or [proposal]

    def get_conflicts(self, artifact_id: str) -> list[dict[str, Any]]:
        """Extract reconciliation conflicts for an artifact.

        Returns a list of conflict dicts with ``type``, ``description``,
        ``source_subsystem``, and ``is_blocking`` fields.
        """
        conflicts: list[dict[str, Any]] = []
        proposals = self.load_proposals(artifact_id)
        for proposal in proposals:
            for conflict in proposal.get("conflicts", []):
                conflicts.append({
                    "conflict_id": conflict.get("id", conflict.get("conflict_id")),
                    "type": self._classify_conflict_type(conflict),
                    "description": conflict.get("description", ""),
                    "source_subsystem": "reconciliation",
                    "is_blocking": conflict.get("blocking", True),
                    "proposal_id": proposal.get("proposal_id"),
                })
        return conflicts

    def get_unresolved_obligations(self, artifact_id: str) -> list[str]:
        """Get obligation IDs that remain unresolved."""
        obligations: list[str] = []
        for conflict in self.get_conflicts(artifact_id):
            if conflict.get("is_blocking"):
                conflict_id = conflict.get("conflict_id")
                if conflict_id:
                    obligations.append(str(conflict_id))
        return obligations

    def _load_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        for path in self.project_root.glob("chapters/*/expression/reconciliation/proposals/*.yaml"):
            if path.stem != proposal_id:
                continue
            try:
                proposal = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except (OSError, yaml.YAMLError):
                self.read_errors.append(str(path))
                return None
            return proposal if isinstance(proposal, dict) else None
        return None

    def get_author_choices(self, artifact_id: str) -> list[UnresolvedChoice]:
        """Identify creative author decisions needed.

        Distinguishes technical conflicts (can be reconciled automatically)
        from creative choices (require author judgment).
        """
        choices: list[UnresolvedChoice] = []
        proposals = self.load_proposals(artifact_id)
        for proposal in proposals:
            for conflict in proposal.get("conflicts", []):
                ctype = self._classify_conflict_type(conflict)
                if ctype == "creative":
                    choices.append(
                        UnresolvedChoice.create(
                            question=conflict.get("description", f"Resolve: {conflict.get('id', 'unknown')}"),
                            options=conflict.get("options"),
                            affected_candidates=[proposal.get("proposal_id", "")],
                            blocking_status=conflict.get("blocking", True),
                        )
                    )
        return choices

    def needs_reconciliation(self, artifact_id: str) -> bool:
        """Check if an artifact has unresolved reconciliation conflicts."""
        conflicts = self.get_conflicts(artifact_id)
        technical = [c for c in conflicts if c.get("type") == "technical"]
        return len(technical) > 0

    def needs_author_decision(self, artifact_id: str) -> bool:
        """Check if an artifact needs creative author input."""
        choices = self.get_author_choices(artifact_id)
        return len([c for c in choices if c.blocking_status]) > 0

    # ------------------------------------------------------------------
    # Conflict evidence conversion
    # ------------------------------------------------------------------

    def conflicts_to_evidence(
        self,
        conflicts: list[dict[str, Any]],
    ) -> list[DecisionEvidence]:
        """Convert reconciliation conflicts to DecisionEvidence entries.

        Technical conflicts → DERIVED_INFERENCE
        Creative conflicts  → AUTHOR_CHOICE
        """
        evidence: list[DecisionEvidence] = []
        for conflict in conflicts:
            ctype = conflict.get("type", "technical")
            evidence.append(
                DecisionEvidence.create(
                    source_subsystem=EvidenceSource.RECONCILIATION,
                    source_artifact_id=conflict.get("conflict_id", "unknown"),
                    claim=conflict.get("description", ""),
                    evidence_type=EvidenceType.RECONCILIATION_CONFLICT,
                    classification=(
                        EvidenceClassification.AUTHOR_CHOICE
                        if ctype == "creative"
                        else EvidenceClassification.DERIVED_INFERENCE
                    ),
                    freshness=EvidenceFreshness.CURRENT,
                    supporting_reference=conflict.get("proposal_id"),
                )
            )
        return evidence

    # ------------------------------------------------------------------
    # Staleness
    # ------------------------------------------------------------------

    def detect_staleness(self, target_artifact: str, source_hash: str | None = None) -> EvidenceFreshness:
        """Detect if reconciliation data for an artifact is stale."""
        proposals = self.load_proposals(target_artifact)
        if self.read_errors:
            return EvidenceFreshness.UNKNOWN
        if not proposals:
            return EvidenceFreshness.UNKNOWN

        recorded_hashes = {
            str(proposal.get("source_assembly", {}).get("content_hash", "")) for proposal in proposals
        }
        if not recorded_hashes or "" in recorded_hashes:
            return EvidenceFreshness.UNKNOWN
        if source_hash is None:
            live_hashes = {
                live_hash
                for proposal in proposals
                if (live_hash := self._current_source_hash(proposal.get("source_assembly", {}).get("artifact_id")))
            }
            if not live_hashes or len(live_hashes) != 1:
                return EvidenceFreshness.UNKNOWN
            source_hash = next(iter(live_hashes))
        return (
            EvidenceFreshness.CURRENT
            if recorded_hashes == {source_hash}
            else EvidenceFreshness.STALE
        )

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_conflict_type(conflict: dict[str, Any]) -> str:
        """Determine if a conflict is technical or creative.

        Uses conflict metadata or heuristics:
        - 'source' field with value 'technical' → technical
        - 'classification' field → direct mapping
        - 'options' field with meaningful alternatives → creative
        - Default: technical
        """
        source = conflict.get("source", "")
        if source == "technical":
            return "technical"
        classification = conflict.get("classification", "")
        if classification in ("factual", "structural"):
            return "technical"
        if classification == "creative":
            return "creative"
        # Conflicts with multiple options are usually creative
        if conflict.get("options") and len(conflict["options"]) > 1:
            return "creative"
        return "technical"

    def _current_source_hash(self, artifact_id: Any) -> str | None:
        """Read the owning expression artifact's current hash without mutation."""
        if not artifact_id:
            return None
        try:
            from auteur.expression.composition import ChapterExpressionStore

            return ChapterExpressionStore(self.project_root).inspect(str(artifact_id)).content_hash
        except (FileNotFoundError, ValueError, KeyError, OSError):
            return None
