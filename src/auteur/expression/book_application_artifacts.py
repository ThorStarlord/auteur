"""Storage seam for Book reconciliation Phase A/B artifacts.

This module owns path construction and loading for inspection, proposal, plan,
publication, preview, and candidate artifacts. Inspection/routing/planning/
publication semantics, freshness checks, candidate construction, and authority
rules remain owned by `BookReconciliationStore`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class BookApplicationArtifactStore:
    """Locate and load noncanonical Book reconciliation application artifacts."""

    def __init__(self, project: Path) -> None:
        self.project = Path(project)
        self.root = self.project / "book" / "expression" / "reconciliation"

    def inspection_path(self, inspection_id: str) -> Path:
        return self.root / "inspections" / f"{inspection_id}.yaml"

    def load_inspection(self, inspection_id: str) -> dict[str, Any]:
        path = next(self.root.glob(f"inspections/{inspection_id}.yaml"), None)
        if path is None:
            raise FileNotFoundError(f"Book inspection not found: {inspection_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def proposal_path(self, proposal_id: str) -> Path:
        return self.root / "proposals" / f"{proposal_id}.yaml"

    def load_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        path = self.proposal_path(proposal_id)
        if not path.exists():
            return None
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def plan_path(self, plan_id: str) -> Path:
        return self.root / "plans" / f"{plan_id}.yaml"

    def load_plan(self, plan_id: str) -> dict[str, Any]:
        path = self.plan_path(plan_id)
        if not path.exists():
            raise FileNotFoundError(f"Book application plan not found: {plan_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def publication_path(self, publication_id: str) -> Path:
        return self.root / "publications" / f"{publication_id}.yaml"

    def load_publication(self, publication_id: str) -> dict[str, Any]:
        path = self.publication_path(publication_id)
        if not path.exists():
            raise FileNotFoundError(f"Book publication not found: {publication_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def preview_path(self, publication_id: str) -> Path:
        return self.root / "previews" / f"{publication_id}.yaml"

    def load_preview(self, publication_id: str) -> dict[str, Any]:
        path = self.preview_path(publication_id)
        if not path.exists():
            raise FileNotFoundError(f"Book preview not found: {publication_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def candidate_path(self, candidate_id: str) -> Path:
        return self.root / "candidates" / f"{candidate_id}.yaml"

    def load_candidate(self, candidate_id: str) -> dict[str, Any]:
        path = self.candidate_path(candidate_id)
        if not path.exists():
            raise FileNotFoundError(f"Book candidate not found: {candidate_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
