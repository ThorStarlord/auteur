"""Read-only reconciliation adapter — loads proposals, conflicts, and author choices.

The adapter reads the durable proposal artifacts produced by the Expression
reconciliation subsystem. It distinguishes technical reconciliation conflicts
from creative author decisions and fails closed when persisted evidence cannot
be parsed.
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

    # ------------------------------------------------------------------
    # Proposal queries
    # ------------------------------------------------------------------

    def load_proposals(self, artifact_id: str) -> list[dict[str, Any]]:
        """Load durable Expression reconciliation proposals for an artifact.

        Expression reconciliation stores proposal YAML below each Chapter's
        reconciliation directory. The adapter treats malformed evidence as an
        error rather than silently converting it into "no conflicts".
        """
        proposals: list[dict[str, Any]] = []
        pattern = "chapters/*/expression/reconciliation/proposals/*.yaml"
        for path in sorted(self.project_root.glob(pattern)):
            try:
                payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError) as exc:
                raise ValueError(f"Cannot read reconciliation proposal {path}: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"Invalid reconciliation proposal {path}: expected a mapping")

            source_assembly = payload.get("source_assembly")
            source_artifact_id = (
                source_assembly.get("artifact_id")
                if isinstance(source_assembly, dict)
                else None
            )
            if payload.get("target_artifact_id") == artifact_id or source_artifact_id == artifact_id:
                proposals.append(payload)
        return proposals

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
        # Reconciliation evidence does not yet expose source hashes through
        # this adapter. Callers must not use this method as acceptance proof.
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
