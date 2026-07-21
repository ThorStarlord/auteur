"""Persistence — immutable convergence artifact storage."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.convergence.models import (
    CandidateComparison,
    CandidateRef,
    ConvergenceState,
    ConvergenceAction,
    ReconciliationProposal,
    RevisionTarget,
    SourceObligation,
)


class ConvergenceStore:
    """Immutable convergence artifact persistence.

    Layout:
    .auteur/convergence/
        targets/        — immutable target records
        candidates/     — immutable candidate records
        comparisons/    — immutable comparison records
        proposals/      — immutable proposal records
        latest/         — replaceable convenience pointers
    """

    def __init__(self, project: Path):
        self.project = Path(project)
        self.root = self.project / ".auteur" / "convergence"

    def save_target(self, target: RevisionTarget) -> str:
        return self._write_immutable("targets", target.target_id, target.model_dump(mode="json"))

    def save_candidate(self, candidate: CandidateRef) -> str:
        return self._write_immutable("candidates", candidate.candidate_id, candidate.model_dump(mode="json"))

    def save_comparison(self, comparison: CandidateComparison) -> str:
        return self._write_immutable("comparisons", comparison.comparison_id, comparison.model_dump(mode="json"))

    def save_proposal(self, proposal: ReconciliationProposal) -> str:
        return self._write_immutable("proposals", proposal.proposal_id, proposal.model_dump(mode="json"))

    def get_target(self, target_id: str) -> dict[str, Any] | None:
        return self._read("targets", target_id)

    def get_candidate(self, candidate_id: str) -> dict[str, Any] | None:
        return self._read("candidates", candidate_id)

    def get_comparison(self, comparison_id: str) -> dict[str, Any] | None:
        return self._read("comparisons", comparison_id)

    def get_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        return self._read("proposals", proposal_id)

    def list_targets(self) -> list[dict[str, Any]]:
        return self._list_dir("targets")

    def list_candidates(self, target_id: str | None = None) -> list[dict[str, Any]]:
        results = self._list_dir("candidates")
        if target_id:
            return [c for c in results if c.get("target_id") == target_id]
        return results

    def list_comparisons(self, target_id: str | None = None) -> list[dict[str, Any]]:
        results = self._list_dir("comparisons")
        if target_id:
            return [c for c in results if c.get("target_id") == target_id]
        return results

    def list_proposals(self, target_id: str | None = None) -> list[dict[str, Any]]:
        results = self._list_dir("proposals")
        if target_id:
            return [p for p in results if p.get("target_id") == target_id]
        return results

    def update_latest(self, artifact_type: str, artifact_id: str) -> None:
        """Atomically update a convenience pointer."""
        latest_dir = self.root / "latest"
        latest_dir.mkdir(parents=True, exist_ok=True)
        pointer = latest_dir / f"{artifact_type}.txt"
        old_pointer = pointer.with_suffix(".txt.old")
        if pointer.exists():
            pointer.rename(old_pointer)
        try:
            pointer.write_text(artifact_id, encoding="utf-8")
            if old_pointer.exists():
                old_pointer.unlink()
        except Exception:
            if old_pointer.exists():
                old_pointer.rename(pointer)
            raise

    def get_latest(self, artifact_type: str) -> str | None:
        pointer = self.root / "latest" / f"{artifact_type}.txt"
        if pointer.exists():
            return pointer.read_text(encoding="utf-8").strip()
        return None

    def gather_state(self, project: str) -> ConvergenceState:
        """Gather current convergence state for display."""
        latest_target_id = self.get_latest("target")
        target = None
        if latest_target_id:
            t = self.get_target(latest_target_id)
            if t:
                target = RevisionTarget(**t)

        candidates = []
        if target:
            for c in self.list_candidates(target.target_id):
                candidates.append(CandidateRef(**c))

        return ConvergenceState(
            project=project,
            target=target,
            candidates=candidates,
            status_summary=self._generate_summary(target, candidates),
        )

    def _generate_summary(
        self,
        target: RevisionTarget | None,
        candidates: list[CandidateRef],
    ) -> str:
        if target is None:
            return "No active revision target"
        parts = [f"Target: {target.scope.value} {target.chapter_index}"]
        if target.scene_id:
            parts.append(f"/ {target.scene_id}")
        parts.append(f" ({len(candidates)} candidate(s))")
        fresh = sum(1 for c in candidates if c.freshness == "fresh")
        stale = sum(1 for c in candidates if c.freshness == "stale")
        if fresh:
            parts.append(f", {fresh} fresh")
        if stale:
            parts.append(f", {stale} stale")
        return "".join(parts)

    def _write_immutable(self, subdir: str, artifact_id: str, data: dict[str, Any]) -> str:
        """Write an immutable artifact with atomic replace."""
        directory = self.root / subdir
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{artifact_id}.yaml"
        if path.exists():
            return artifact_id  # immutable; don't overwrite
        temp = path.with_suffix(".tmp")
        try:
            temp.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            temp.replace(path)
        except Exception:
            if temp.exists():
                temp.unlink()
            raise
        return artifact_id

    def _read(self, subdir: str, artifact_id: str) -> dict[str, Any] | None:
        path = self.root / subdir / f"{artifact_id}.yaml"
        if not path.exists():
            return None
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, yaml.YAMLError):
            return None

    def _list_dir(self, subdir: str) -> list[dict[str, Any]]:
        directory = self.root / subdir
        if not directory.exists():
            return []
        results = []
        for path in sorted(directory.glob("*.yaml")):
            data = self._read(subdir, path.stem)
            if data:
                results.append(data)
        return results
