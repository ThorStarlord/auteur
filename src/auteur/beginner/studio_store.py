"""Durable, noncanonical working canvas notes; never a StoryIdentity owner.

A separate store is required because Beginner SessionEnvelope requires a premise.
All mutations are atomic, version checked and idempotent under one file lock.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .persistence import (
    BeginnerConcurrencyError,
    BeginnerPersistenceError,
    _FilesystemLock,
    _atomic_create,
    _atomic_write,
    _contained_path,
    _safe_segment,
)

ItemKind = Literal["note", "character", "scene", "place", "question"]


class CanvasItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    kind: ItemKind = "note"
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(default="", max_length=20000)
    scene_premise: str = Field(default="", max_length=4000)
    scene_intent: str = Field(default="", max_length=4000)
    quick_draft_session_id: str = Field(default="", max_length=120)
    group: str = Field(default="", max_length=80)


class CanvasConnection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    label: str = Field(default="", max_length=120)


class CanvasPosition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)

    x: float = Field(ge=0, le=1400)
    y: float = Field(ge=0, le=1040)


class CanvasViewport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)

    pan_x: float = Field(default=0, ge=-5000, le=5000)
    pan_y: float = Field(default=0, ge=-5000, le=5000)
    zoom: float = Field(default=1, ge=0.5, le=1.5)


class DeletedItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    item: CanvasItem
    position: CanvasPosition
    connections: list[CanvasConnection] = Field(default_factory=list)


class WorkingCanvas(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    canvas_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$", max_length=80)
    revision: int = Field(default=0, ge=0)
    items: list[CanvasItem] = Field(default_factory=list, max_length=200)
    connections: list[CanvasConnection] = Field(default_factory=list, max_length=500)
    positions: dict[str, CanvasPosition] = Field(default_factory=dict)
    viewport: CanvasViewport = Field(default_factory=CanvasViewport)
    deleted: dict[str, DeletedItem] = Field(default_factory=dict)
    command_hashes: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_graph(self) -> "WorkingCanvas":
        ids = [item.id for item in self.items]
        edge_ids = [edge.id for edge in self.connections]
        if len(ids) != len(set(ids)) or len(edge_ids) != len(set(edge_ids)):
            raise ValueError("duplicate canvas item or connection id")
        active = set(ids)
        if set(self.positions) != active or active.intersection(self.deleted):
            raise ValueError("positions or deleted items do not match active items")
        if any(edge.source not in active or edge.target not in active or edge.source == edge.target
               for edge in self.connections):
            raise ValueError("canvas connection references missing or identical nodes")
        if any(key != tombstone.item.id for key, tombstone in self.deleted.items()):
            raise ValueError("deleted item identity mismatch")
        return self


class CanvasStore:
    """Atomic local-only working document store; no accepted-story mutation."""

    def __init__(self, project_root: Path, canvas_id: str) -> None:
        self.project_root = Path(project_root).resolve()
        self.canvas_id = _safe_segment(canvas_id, "canvas_id")
        if len(self.canvas_id) > 80:
            raise ValueError("canvas id exceeds 80 characters")
        self.directory = _contained_path(
            self.project_root / ".auteur" / "beginner" / "studio" / "canvases",
            self.canvas_id,
            containment_root=self.project_root,
        )

    def _path(self, name: str) -> Path:
        return _contained_path(self.directory, name, containment_root=self.project_root)

    def load(self) -> WorkingCanvas:
        path = self._path("canvas.json")
        try:
            return WorkingCanvas.model_validate_json(path.read_text(encoding="utf-8"), strict=True)
        except FileNotFoundError:
            raise
        except (OSError, ValueError) as exc:
            raise BeginnerPersistenceError(f"could not read canvas {self.canvas_id}: {exc}") from exc

    def create(self) -> WorkingCanvas:
        with _FilesystemLock(self._path(".canvas.lock")):
            initial = WorkingCanvas(canvas_id=self.canvas_id)
            if not _atomic_create(self._path("canvas.json"), initial.model_dump_json()):
                return self.load()
            return initial

    def apply(self, action: str, *, expected_revision: int, command_id: str, payload: dict) -> WorkingCanvas:
        if action not in {"create-item", "update-item", "delete-item", "restore-item",
                          "connect", "disconnect", "move-item", "replace-working-document"}:
            raise ValueError("unsupported working canvas command")
        _safe_segment(command_id, "command_id")
        if len(command_id) > 80 or not isinstance(payload, dict):
            raise ValueError("invalid canvas command")
        required_keys = {
            "create-item": {"item", "position"},
            "update-item": {"item"},
            "delete-item": {"item_id"},
            "restore-item": {"item_id"},
            "connect": {"connection"},
            "disconnect": {"connection_id"},
            "move-item": {"item_id", "position"},
            "replace-working-document": {"items", "connections", "positions", "viewport"},
        }[action]
        if not required_keys.issubset(payload):
            raise ValueError("canvas command is missing required fields")
        digest = hashlib.sha256(
            json.dumps({"action": action, "payload": payload}, sort_keys=True, ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        with _FilesystemLock(self._path(".canvas.lock")):
            current = self.load()
            if command_id in current.command_hashes:
                if current.command_hashes[command_id] != digest:
                    raise BeginnerConcurrencyError("canvas command id reused with different intent")
                return current
            if current.revision != expected_revision:
                raise BeginnerConcurrencyError(
                    f"canvas version mismatch: expected {expected_revision}, found {current.revision}"
                )
            raw = current.model_dump(mode="python")
            items, edges, positions, deleted = raw["items"], raw["connections"], raw["positions"], raw["deleted"]
            active = {item["id"] for item in items}
            if action == "replace-working-document":
                if set(payload) != {"items", "connections", "positions", "viewport"}:
                    raise ValueError("working document replacement requires exact known fields")
                next_items = [CanvasItem.model_validate(item, strict=True) for item in payload["items"]]
                next_ids = {item.id for item in next_items}
                for previous in items:
                    removed_id = previous["id"]
                    if removed_id not in next_ids:
                        attached = [edge for edge in edges if edge["source"] == removed_id or edge["target"] == removed_id]
                        deleted[removed_id] = {
                            "item": previous, "position": positions[removed_id], "connections": attached
                        }
                # A reintroduced note explicitly restores its working identity.
                # Previously recorded deletions remain recoverable across restarts.
                for next_id in next_ids:
                    deleted.pop(next_id, None)
                raw["items"] = payload["items"]
                raw["connections"] = payload["connections"]
                raw["positions"] = payload["positions"]
                raw["viewport"] = CanvasViewport.model_validate(payload["viewport"], strict=True).model_dump()
            elif action == "create-item":
                item = CanvasItem.model_validate(payload["item"], strict=True)
                position = CanvasPosition.model_validate(payload["position"], strict=True)
                if item.id in active or item.id in deleted:
                    raise ValueError("working item already exists")
                items.append(item.model_dump())
                positions[item.id] = position.model_dump()
            elif action == "update-item":
                item = CanvasItem.model_validate(payload["item"], strict=True)
                if item.id not in active:
                    raise ValueError("working item does not exist")
                raw["items"] = [item.model_dump() if old["id"] == item.id else old for old in items]
            elif action == "delete-item":
                item_id = _safe_segment(payload["item_id"], "item_id")
                old = next((item for item in items if item["id"] == item_id), None)
                if old is None:
                    raise ValueError("working item does not exist")
                attached = [edge for edge in edges if edge["source"] == item_id or edge["target"] == item_id]
                deleted[item_id] = {"item": old, "position": positions.pop(item_id), "connections": attached}
                raw["items"] = [item for item in items if item["id"] != item_id]
                raw["connections"] = [edge for edge in edges if edge not in attached]
            elif action == "restore-item":
                item_id = _safe_segment(payload["item_id"], "item_id")
                if item_id not in deleted or item_id in active:
                    raise ValueError("deleted item not found")
                tombstone = deleted.pop(item_id)
                items.append(tombstone["item"])
                positions[item_id] = tombstone["position"]
                for edge in tombstone["connections"]:
                    others = set([edge["source"], edge["target"]]) - set([item_id])
                    if others.issubset(active) and not any(existing["id"] == edge["id"] for existing in edges):
                        edges.append(edge)
            elif action == "connect":
                edge = CanvasConnection.model_validate(payload["connection"], strict=True)
                if edge.source not in active or edge.target not in active or edge.source == edge.target:
                    raise ValueError("connection must reference distinct existing items")
                if any(existing["id"] == edge.id for existing in edges):
                    raise ValueError("connection id already exists")
                edges.append(edge.model_dump())
            elif action == "disconnect":
                edge_id = _safe_segment(payload["connection_id"], "connection_id")
                if not any(edge["id"] == edge_id for edge in edges):
                    raise ValueError("connection not found")
                raw["connections"] = [edge for edge in edges if edge["id"] != edge_id]
            elif action == "move-item":
                item_id = _safe_segment(payload["item_id"], "item_id")
                if item_id not in active:
                    raise ValueError("working item not found")
                positions[item_id] = CanvasPosition.model_validate(payload["position"], strict=True).model_dump()
            raw["revision"] = current.revision + 1
            raw["command_hashes"][command_id] = digest
            updated = WorkingCanvas.model_validate(raw, strict=True)
            _atomic_write(self._path("canvas.json"), updated.model_dump_json())
            return updated


def list_canvas_summaries(project_root: Path) -> list[dict]:
    """Recent local noncanonical canvases; corrupt documents remain visible."""
    root = Path(project_root).resolve()
    base = root / ".auteur" / "beginner" / "studio" / "canvases"
    if not base.is_dir():
        return []
    summaries: list[dict] = []
    for path in base.iterdir():
        if not path.is_dir() or path.is_symlink():
            continue
        try:
            canvas_store = CanvasStore(root, path.name)
        except (OSError, ValueError, BeginnerPersistenceError):
            continue
        try:
            document = canvas_store.load()
            modified_ns = canvas_store._path("canvas.json").stat().st_mtime_ns
            summaries.append({
                "canvas_id": document.canvas_id,
                "title": document.items[0].title[:80] if document.items else "Untitled working canvas",
                "item_count": len(document.items), "revision": document.revision,
                "state": "ready", "modified_ns": modified_ns,
            })
        except (OSError, ValueError, BeginnerPersistenceError):
            # A damaged canvas is still an existing document, not a reason to
            # silently create an apparently empty replacement.
            summaries.append({
                "canvas_id": canvas_store.canvas_id, "title": "Working canvas needs recovery",
                "item_count": 0, "revision": None, "state": "unavailable", "modified_ns": 0,
            })
    return sorted(summaries, key=lambda entry: (-entry["modified_ns"], entry["canvas_id"]))
