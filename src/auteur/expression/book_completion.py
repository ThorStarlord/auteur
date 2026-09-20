"""Persistence seam for immutable Book reconciliation completion records.

This module owns only completion record/manifests/staging path mechanics and
idempotent lookup of an already-completed acceptance. Completion eligibility,
Chapter reconciliation inspection, accepted-source resolution, gate validation,
record construction, atomic publication ordering, and public workflow semantics
remain owned by `BookReconciliationStore`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class BookCompletionStore:
    """Persist and load Book reconciliation completion evidence."""

    def __init__(self, project: Path) -> None:
        self.project = Path(project)
        self.root = self.project / "book" / "expression" / "reconciliation"

    def completions_dir(self) -> Path:
        return self.root / "completions"

    def completion_path(self, completion_id: str) -> Path:
        return self.completions_dir() / f"{completion_id}.yaml"

    def completion_manifest_path(self, completion_id: str) -> Path:
        return self.completions_dir() / "manifests" / f"{completion_id}.yaml"

    def completion_staging_dir(self, completion_id: str) -> Path:
        return self.root / "staging" / f"completion_{completion_id}"

    def load_completion(self, completion_id: str) -> dict[str, Any]:
        path = self.completion_path(completion_id)
        if not path.exists():
            raise FileNotFoundError(
                f"Book reconciliation completion not found: {completion_id}"
            )
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def find_prior_completion(
        self,
        acceptance_id: str,
    ) -> dict[str, Any] | None:
        """Return an existing completion for an acceptance, preserving idempotency."""
        directory = self.completions_dir()
        if not directory.exists():
            return None
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if (
                isinstance(data, dict)
                and data.get("source_acceptance_id") == acceptance_id
            ):
                return data
        return None
