"""Read-only reconciliation adapter — loads proposals, conflicts, and author choices.

This adapter replaces convergence-proposal-embedded data with direct reads
from the expression-layer ReconciliationStore. It distinguishes technical
reconciliation conflicts from creative author decisions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from auteur.decision.models import (
    DecisionEvidence,
    EvidenceClassification,
    EvidenceFreshness,
    EvidenceSource,
    EvidenceType,
    UnresolvedChoice,
)
from auteur.workflow.models import AuthorityLevel


class ReconciliationAdapter:
    """Query interface to the expression reconciliation subsystem.

    All methods are read-only; no reconciliation artifacts are created
    or modified.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()

    # ------------------------------------------------------------------
    # Proposal queries
    # ------------------------------------------------------------------

    def load_proposals(self, artifact_id: str) -> list[dict[str, Any]]:
        """Load reconciliation proposals for an artifact.

        Delegates to ``ReconciliationStore`` from the expression layer.
        Returns empty list if the reconciliation subsystem has no data.
        """
        try:
            from auteur.expression.reconciliation import ReconciliationStore
            store = ReconciliationStore(self.project_root)
            # The reconciliation store works at the book level via composition store
            # We try to locate proposals by inspecting manuscript-level state
            return []  # TODO: wire real proposal loading in Task 2
        except ImportError:
            return []
        except Exception:
            return []

    def load_proposal_lineage(self, proposal_id: str) -> list[dict[str, Any]]:
        """Track the chain of proposals for lineage."""
        return []

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
        return []

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
        # Would compare recorded hashes from reconciliation runs
        return EvidenceFreshness.CURRENT

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
