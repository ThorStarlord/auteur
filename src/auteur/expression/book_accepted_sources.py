"""Accepted Book-owned source and pointer storage.

This is the authority/persistence seam previously embedded in
BookReconciliationStore.  It owns only immutable accepted Book-owned source
revisions plus the mutable current pointers that select those revisions.
Recomposition, comparison, Book acceptance, and reconciliation completion stay
with their existing owners.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


ACCEPTED_SOURCE_TRANSFORMATION = {
    "id": "expression.accept_book_owned_source",
    "version": 1,
}
ACCEPTED_SOURCE_KIND = {
    "book_separator_candidate": "separator",
    "book_order_candidate": "order",
    "book_title_rendering_candidate": "title",
    "book_inserted_material_candidate": "material",
}
POINTER_TRANSFORMATION = {
    "id": "expression.point_accepted_book_source",
    "version": 1,
}


class AcceptedBookSourceStore:
    """Persist accepted Book-owned revisions and their current pointers."""

    def __init__(self, project: Path) -> None:
        self.project = Path(project)
        self.root = self.project / "book" / "expression" / "reconciliation"

    def accepted_sources_dir(self) -> Path:
        return self.root / "accepted-sources"

    def accepted_source_path(self, accepted_source_id: str) -> Path:
        return self.accepted_sources_dir() / f"{accepted_source_id}.yaml"

    def accepted_source_revision(
        self,
        book_id: str,
        target_id: Any,
        kind: str,
    ) -> int:
        directory = self.accepted_sources_dir()
        if not directory.exists():
            return 1
        revisions = [0]
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if (
                data.get("book_expression_id") == book_id
                and data.get("owned_kind") == kind
                and data.get("target_id") == target_id
            ):
                revisions.append(data.get("revision", 0))
        return max(revisions) + 1

    def create_accepted_source(
        self,
        candidate: dict[str, Any],
        decision: dict[str, Any],
        now: str,
    ) -> dict[str, Any]:
        candidate_type = candidate.get("artifact_type")
        kind = ACCEPTED_SOURCE_KIND.get(candidate_type, "unknown")
        book_id = candidate.get("book_expression_id")
        target_id = candidate.get("target_id")
        revision = self.accepted_source_revision(book_id, target_id, kind)
        accepted_source_id = (
            f"book_accepted_{kind}_v{revision:03d}_"
            + hashlib.sha256(decision["decision_id"].encode("utf-8")).hexdigest()[:16]
        )
        artifact = {
            "accepted_source_id": accepted_source_id,
            "artifact_type": "accepted_book_owned_source",
            "owned_kind": kind,
            "authority": "accepted",
            "lifecycle": "accepted",
            "book_expression_id": book_id,
            "target_id": target_id,
            "revision": revision,
            "source_decision_id": decision["decision_id"],
            "source_candidate_id": candidate.get("candidate_id"),
            "candidate_type": candidate_type,
            "publication_id": candidate.get("publication_id"),
            "source_book_revision": candidate.get("source_book_revision"),
            "source_book_hash": candidate.get("source_book_hash"),
            "original": candidate.get("original"),
            "proposed": candidate.get("proposed"),
            "transformation": dict(ACCEPTED_SOURCE_TRANSFORMATION),
            "created_at": now,
        }
        path = self.accepted_source_path(accepted_source_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(artifact, sort_keys=False), encoding="utf-8")
        return artifact

    def load_accepted_source(self, accepted_source_id: str) -> dict[str, Any]:
        path = self.accepted_source_path(accepted_source_id)
        if not path.exists():
            raise FileNotFoundError(
                f"Accepted Book-owned source not found: {accepted_source_id}"
            )
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def pointers_dir(self) -> Path:
        return self.accepted_sources_dir() / "pointers"

    @staticmethod
    def pointer_key(owned_kind: str, element_id: Any) -> str:
        digest = hashlib.sha256(
            f"{owned_kind}\0{element_id}".encode("utf-8")
        ).hexdigest()[:16]
        return f"book_pointer_{owned_kind}_{digest}"

    def pointer_path(self, owned_kind: str, element_id: Any) -> Path:
        return self.pointers_dir() / f"{self.pointer_key(owned_kind, element_id)}.yaml"

    def advance_pointer(
        self,
        candidate: dict[str, Any],
        accepted_source: dict[str, Any],
        decision: dict[str, Any],
        now: str,
    ) -> dict[str, Any]:
        owned_kind = accepted_source["owned_kind"]
        element_id = accepted_source["target_id"]
        book_id = accepted_source["book_expression_id"]
        path = self.pointer_path(owned_kind, element_id)
        existing = (
            yaml.safe_load(path.read_text(encoding="utf-8"))
            if path.exists()
            else None
        )
        history = (
            (existing or {}).get("history", [])
            if isinstance(existing, dict)
            else []
        )
        entry = {
            "revision": accepted_source["revision"],
            "accepted_source_id": accepted_source["accepted_source_id"],
            "decision_id": decision["decision_id"],
            "decision_sequence": decision["decision_sequence"],
            "publication_id": candidate.get("publication_id"),
            "decided_at": now,
            "reason": decision["decision"]["reason"],
        }
        pointer = {
            "pointer_id": self.pointer_key(owned_kind, element_id),
            "artifact_type": "current_accepted_source_pointer",
            "authority": "pointer",
            "lifecycle": "current",
            "owned_kind": owned_kind,
            "element_id": element_id,
            "book_expression_id": book_id,
            "current_revision": accepted_source["revision"],
            "current_accepted_source_id": accepted_source["accepted_source_id"],
            "active_decision_id": decision["decision_id"],
            "decision_sequence": decision["decision_sequence"],
            "publication_id": candidate.get("publication_id"),
            "source_book_revision": accepted_source.get("source_book_revision"),
            "source_book_hash": accepted_source.get("source_book_hash"),
            "decided_at": now,
            "reason": decision["decision"]["reason"],
            "transformation": dict(POINTER_TRANSFORMATION),
            "updated_at": now,
            "history": history + [entry],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(pointer, sort_keys=False), encoding="utf-8")
        return pointer

    def current_pointer(
        self,
        element_id: Any,
        owned_kind: str,
    ) -> dict[str, Any] | None:
        path = self.pointer_path(owned_kind, element_id)
        if not path.exists():
            return None
        return yaml.safe_load(path.read_text(encoding="utf-8")) or None

    def current_source(
        self,
        element_id: Any,
        owned_kind: str,
    ) -> dict[str, Any] | None:
        pointer = self.current_pointer(element_id, owned_kind)
        if pointer is None:
            return None
        return self.load_accepted_source(pointer["current_accepted_source_id"])

    def all_pointers(self) -> list[dict[str, Any]]:
        directory = self.pointers_dir()
        pointers: list[dict[str, Any]] = []
        if not directory.exists():
            return pointers
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if data.get("artifact_type") == "current_accepted_source_pointer":
                pointers.append(data)
        return pointers

    def current_sources(self, publication_id: str) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []
        for pointer in self.all_pointers():
            source = self.current_source(
                pointer["element_id"],
                pointer["owned_kind"],
            )
            if source is not None and source.get("publication_id") == publication_id:
                sources.append(source)
        return sources

    def accepted_source_history(
        self,
        element_id: Any,
        owned_kind: str,
    ) -> list[dict[str, Any]]:
        directory = self.accepted_sources_dir()
        revisions: list[dict[str, Any]] = []
        if not directory.exists():
            return revisions
        for path in sorted(directory.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if data.get("artifact_type") != "accepted_book_owned_source":
                continue
            if (
                data.get("owned_kind") == owned_kind
                and data.get("target_id") == element_id
            ):
                revisions.append(data)
        revisions.sort(key=lambda data: data.get("revision", 0))
        return revisions

    def pointer_history(
        self,
        element_id: Any,
        owned_kind: str,
    ) -> list[dict[str, Any]]:
        pointer = self.current_pointer(element_id, owned_kind)
        if pointer is None:
            return []
        return list(pointer.get("history", []))
