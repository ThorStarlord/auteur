"""Persistence seam for reconciliation-accepted Book revisions and records.

This module owns only the storage mechanics for the reconciliation acceptance
authority boundary: immutable acceptance records, immutable accepted Book
revisions, the mutable current accepted-Book pointer, and acceptance staging
paths. Eligibility/revalidation, atomic publication ordering, comparison
semantics, and reconciliation completion remain owned by
`BookReconciliationStore`.

Keeping this seam storage-only preserves the public facade and the existing
authority model while reducing the Book reconciliation hotspot incrementally.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class BookAcceptanceStore:
    """Persist and load reconciliation-accepted Book authority artifacts."""

    def __init__(self, project: Path) -> None:
        self.project = Path(project)
        self.root = self.project / "book" / "expression" / "reconciliation"

    def acceptances_dir(self) -> Path:
        return self.root / "acceptances"

    def acceptance_path(self, acceptance_id: str) -> Path:
        return self.acceptances_dir() / f"{acceptance_id}.yaml"

    def acceptance_manifest_path(self, acceptance_id: str) -> Path:
        return self.acceptances_dir() / "manifests" / f"{acceptance_id}.yaml"

    def acceptance_staging_dir(self, acceptance_id: str) -> Path:
        return self.root / "staging" / f"acceptance_{acceptance_id}"

    def accepted_book_pointer_path(self) -> Path:
        return self.project / "book" / "expression" / "accepted-book-pointer.yaml"

    def accepted_book_revision_path(self, book_id: str, revision: int) -> Path:
        return (
            self.project
            / "book"
            / "expression"
            / f"book_{book_id}_v{revision:03d}_accepted.yaml"
        )

    def load_accepted_book_pointer(self) -> dict[str, Any] | None:
        """Return the current reconciliation-accepted Book pointer, if any."""
        path = self.accepted_book_pointer_path()
        if not path.exists():
            return None
        return yaml.safe_load(path.read_text(encoding="utf-8")) or None

    def current_accepted_book_pointer(self) -> dict[str, Any] | None:
        return self.load_accepted_book_pointer()

    def load_accepted_book_revision(
        self,
        book_id: str,
        revision: int,
    ) -> dict[str, Any]:
        path = self.accepted_book_revision_path(book_id, revision)
        if not path.exists():
            raise FileNotFoundError(
                f"Accepted Book revision not found: {book_id} v{revision}"
            )
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def load_book_acceptance(self, acceptance_id: str) -> dict[str, Any]:
        path = self.acceptance_path(acceptance_id)
        if not path.exists():
            raise FileNotFoundError(
                f"Book acceptance record not found: {acceptance_id}"
            )
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def find_prior_acceptance(
        self,
        comparison_id: str,
    ) -> dict[str, Any] | None:
        """Return an existing acceptance for a comparison, preserving idempotency."""
        directory = self.acceptances_dir()
        if not directory.exists():
            return None
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if (
                isinstance(data, dict)
                and data.get("source_comparison_id") == comparison_id
            ):
                return data
        return None
