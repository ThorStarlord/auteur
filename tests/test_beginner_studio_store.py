"""Working canvas store authority, durability, conflict and retry tests."""
from __future__ import annotations

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_store import CanvasStore


def mutate(store, rev, command, action, payload):
    return store.apply(action, expected_revision=rev, command_id=command, payload=payload)


def item(item_id, title="Idea"):
    return {"id": item_id, "title": title, "kind": "note", "content": "Anything can start here."}


def test_no_premise_reopen_and_working_only(tmp_path):
    store = CanvasStore(tmp_path, "canvas-1")
    start = store.create()
    assert start.revision == 0
    one = mutate(store, 0, "create-one", "create-item", {
        "item": item("first"), "position": {"x": 120, "y": 50}
    })
    assert one.revision == 1
    assert store.load().items[0].title == "Idea"
    assert not (tmp_path / ".auteur" / "beginner" / "workspaces").exists()
    assert CanvasStore(tmp_path, "canvas-1").create().revision == 1


def test_edges_are_noncanonical_and_recoverable(tmp_path):
    store = CanvasStore(tmp_path, "canvas-2")
    current = store.create()
    for number in (1, 2):
        current = mutate(store, current.revision, f"create-{number}", "create-item", {
            "item": item(f"item-{number}"), "position": {"x": number * 40, "y": 70}
        })
    current = mutate(store, current.revision, "edge-create", "connect", {
        "connection": {"id": "edge-1", "source": "item-1", "target": "item-2", "label": "might know"}
    })
    assert current.connections[0].label == "might know"
    current = mutate(store, current.revision, "remove-one", "delete-item", {"item_id": "item-1"})
    assert not current.connections and "item-1" in current.deleted
    current = mutate(store, current.revision, "restore-one", "restore-item", {"item_id": "item-1"})
    assert len(current.items) == 2 and len(current.connections) == 1
    assert not (tmp_path / "relations.yaml").exists()


def test_retry_does_not_apply_twice_or_mutate_with_reused_command(tmp_path):
    store = CanvasStore(tmp_path, "canvas-3")
    store.create()
    payload = {"item": item("first"), "position": {"x": 1, "y": 2}}
    first = mutate(store, 0, "create-once", "create-item", payload)
    repeated = mutate(store, 0, "create-once", "create-item", payload)
    assert repeated.revision == first.revision == 1
    assert len(repeated.items) == 1
    with pytest.raises(BeginnerConcurrencyError):
        mutate(store, 0, "create-once", "create-item", {
            "item": item("other"), "position": {"x": 1, "y": 2}
        })


def test_stale_edit_cannot_overwrite_and_invalid_edit_is_atomic(tmp_path):
    store = CanvasStore(tmp_path, "canvas-4")
    store.create()
    first = mutate(store, 0, "create-one", "create-item", {
        "item": item("first"), "position": {"x": 1, "y": 2}
    })
    contents = store._path("canvas.json").read_bytes()
    with pytest.raises(BeginnerConcurrencyError):
        mutate(store, 0, "stale-edit", "update-item", {"item": item("first", "Wrong")})
    with pytest.raises(ValueError):
        mutate(store, 1, "bad-connect", "connect", {
            "connection": {"id": "bad", "source": "first", "target": "missing", "label": ""}
        })
    assert store._path("canvas.json").read_bytes() == contents
    assert store.load().revision == first.revision


def test_path_traversal_rejected(tmp_path):
    for segment in ("../escape", "CON", "UPPER"):
        with pytest.raises((ValueError, RuntimeError)):
            CanvasStore(tmp_path, segment)
