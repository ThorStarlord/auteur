"""Reconciliation proposal — typed proposals for candidate reconciliation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from auteur.convergence.models import (
    CandidateComparison,
    CandidateRef,
    ConflictFinding,
    ReconciliationProposal,
    RevisionTarget,
    SourceObligation,
)


def _read_yaml(path: Path) -> dict[str, Any] | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return None


class ProposalStore:
    """Manages reconciliation proposals."""

    def __init__(self, project: Path):
        self.project = Path(project)
        self.root = self.project / ".auteur" / "convergence"

    def _proposal_path(self, proposal_id: str) -> Path:
        return self.root / "proposals" / f"{proposal_id}.yaml"

    def _comparison_path(self, comparison_id: str) -> Path:
        return self.root / "comparisons" / f"{comparison_id}.yaml"

    def create_proposal(
        self,
        target: RevisionTarget,
        candidates: list[CandidateRef],
        comparison: CandidateComparison,
        obligations: list[SourceObligation],
    ) -> ReconciliationProposal:
        """Create a reconciliation proposal from candidates and comparison."""
        satisfied = _collect_satisfied(candidates)
        unsatisfied = _collect_unsatisfied(candidates)

        conflicts = self._collect_conflicts(candidates, comparison)

        continuity_risks = _find_continuity_risks(candidates)

        authority_choices = _find_authority_choices(candidates, conflicts)

        proposal = ReconciliationProposal(
            target_id=target.target_id,
            candidate_ids=[c.candidate_id for c in candidates],
            source_obligations=obligations,
            satisfied_obligations=satisfied,
            unsatisfied_obligations=unsatisfied,
            conflicts=conflicts,
            continuity_risks=continuity_risks,
            authority_required_choices=authority_choices,
            canonical=False,
        )

        self._save_proposal(proposal)
        return proposal

    def get_proposal(self, proposal_id: str) -> ReconciliationProposal | None:
        path = self._proposal_path(proposal_id)
        if not path.exists():
            return None
        data = _read_yaml(path)
        if data is None:
            return None
        return ReconciliationProposal(**data)

    def list_proposals(self, target_id: str) -> list[ReconciliationProposal]:
        proposals: list[ReconciliationProposal] = []
        proposals_dir = self.root / "proposals"
        if not proposals_dir.exists():
            return proposals
        for path in sorted(proposals_dir.glob("*.yaml")):
            data = _read_yaml(path)
            if data and data.get("target_id") == target_id:
                proposals.append(ReconciliationProposal(**data))
        return proposals

    def save_comparison(self, comparison: CandidateComparison) -> None:
        path = self._comparison_path(comparison.comparison_id)
        if path.exists():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        try:
            temp.write_text(yaml.safe_dump(comparison.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
            temp.replace(path)
        except Exception:
            if temp.exists():
                temp.unlink()
            raise

    def _save_proposal(self, proposal: ReconciliationProposal) -> None:
        path = self._proposal_path(proposal.proposal_id)
        if path.exists():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        try:
            temp.write_text(yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
            temp.replace(path)
        except Exception:
            if temp.exists():
                temp.unlink()
            raise

    def _collect_conflicts(
        self,
        candidates: list[CandidateRef],
        comparison: CandidateComparison,
    ) -> list[ConflictFinding]:
        existing = list(comparison.conflicts)
        for i, a in enumerate(candidates):
            for b in candidates[i + 1:]:
                for ob_id in a.obligations_satisfied:
                    if ob_id not in b.obligations_satisfied and ob_id not in a.obligations_unsatisfied:
                        pass
        return existing


def _collect_satisfied(candidates: list[CandidateRef]) -> list[str]:
    """Collect obligations satisfied across all candidates."""
    satisfied: set[str] = set()
    for c in candidates:
        satisfied.update(c.obligations_satisfied)
    return sorted(satisfied)


def _collect_unsatisfied(candidates: list[CandidateRef]) -> list[str]:
    """Collect obligations unsatisfied in any candidate."""
    unsatisfied: set[str] = set()
    all_obligations: set[str] = set()
    for c in candidates:
        all_obligations.update(c.obligations)
        unsatisfied.update(c.obligations_unsatisfied)
    # Only obligations that are not satisfied by any candidate
    satisfied = _collect_satisfied(candidates)
    still_unsatisfied = unsatisfied - set(satisfied)
    # Also include obligations that no candidate satisfied
    for ob in all_obligations:
        if ob not in satisfied:
            still_unsatisfied.add(ob)
    return sorted(still_unsatisfied)


def _find_continuity_risks(candidates: list[CandidateRef]) -> list[str]:
    """Identify continuity risks across candidates."""
    risks: list[str] = []
    for c in candidates:
        if c.generation_strategy == "structural_alternative":
            risks.append(f"Candidate {c.candidate_id} uses structural alternative strategy")
        if c.freshness == "stale":
            risks.append(f"Candidate {c.candidate_id} is stale")
    return risks


def _find_authority_choices(
    candidates: list[CandidateRef],
    conflicts: list[ConflictFinding],
) -> list[str]:
    """Identify where author authority is required."""
    choices: list[str] = []
    for conflict in conflicts:
        if conflict.severity == "warning":
            choices.append(
                f"Resolve conflict: {conflict.description} "
                f"between candidates {', '.join(conflict.candidate_ids)}"
            )
    for c in candidates:
        if c.authority == "authority_bearing":
            choices.append(f"External candidate {c.candidate_id} requires explicit acceptance")
    return choices
