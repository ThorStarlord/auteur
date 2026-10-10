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


def test_whole_working_document_replace_is_versioned(tmp_path):
    store = CanvasStore(tmp_path, "canvas-5")
    store.create()
    payload = {
        "items": [item("alpha", "First")],
        "connections": [],
        "positions": {"alpha": {"x": 200, "y": 140}},
        "viewport": {"pan_x": 22, "pan_y": -15, "zoom": 1.2},
    }
    saved = mutate(store, 0, "replace-a", "replace-working-document", payload)
    assert saved.revision == 1
    assert saved.viewport.zoom == 1.2
    assert store.load().items[0].title == "First"
    with pytest.raises(BeginnerConcurrencyError):
        mutate(store, 0, "replace-stale", "replace-working-document", payload)
    assert store.load().revision == 1


def test_invalid_full_working_document_never_mutates(tmp_path):
    store = CanvasStore(tmp_path, "canvas-6")
    store.create()
    with pytest.raises(ValueError):
        mutate(store, 0, "bad-full", "replace-working-document", {
            "items": [item("alpha")],
            "connections": [{"id": "e", "source": "alpha", "target": "missing", "label": "claim"}],
            "positions": {"alpha": {"x": 1, "y": 1}},
            "viewport": {"pan_x": 0, "pan_y": 0, "zoom": 1},
        })
    assert store.load().revision == 0


def test_scene_provisional_intent_and_session_reference_survive_restart(tmp_path):
    store = CanvasStore(tmp_path, "scene-work")
    store.create()
    scene = {
        "id": "scene-one", "title": "Opening", "kind": "scene", "content": "Draft prose",
        "scene_premise": "An investigator questions a suspect.",
        "scene_intent": "The suspect reveals an impossible clue.",
        "quick_draft_session_id": "session-example",
    }
    updated = mutate(store, 0, "scene-create", "create-item", {
        "item": scene, "position": {"x": 10, "y": 11}
    })
    assert updated.revision == 1
    reopened = CanvasStore(tmp_path, "scene-work").load()
    assert reopened.items[0].scene_intent == scene["scene_intent"]
    assert reopened.items[0].quick_draft_session_id == "session-example"
    assert not (tmp_path / "story_identity.yaml").exists()


def test_nonfinite_canvas_coordinates_rejected(tmp_path):
    store = CanvasStore(tmp_path, "nonfinite")
    store.create()
    with pytest.raises(ValueError):
        mutate(store, 0, "nan-coordinate", "create-item", {
            "item": item("bad"), "position": {"x": float("nan"), "y": 10}
        })
    assert store.load().revision == 0


def test_whole_document_replacement_retains_recoverable_deletions(tmp_path):
    store = CanvasStore(tmp_path, "full-delete")
    store.create()
    current = mutate(store, 0, "create-a", "create-item", {
        "item": item("first", "Remember this"), "position": {"x": 10, "y": 20}
    })
    current = mutate(store, current.revision, "create-b", "create-item", {
        "item": item("second", "Keep this"), "position": {"x": 100, "y": 20}
    })
    current = mutate(store, current.revision, "link", "connect", {
        "connection": {"id": "edge-1", "source": "first", "target": "second", "label": "knows"}
    })
    removed = mutate(store, current.revision, "snapshot-deleted", "replace-working-document", {
        "items": [item("second", "Keep this")],
        "connections": [], "positions": {"second": {"x": 100, "y": 20}},
        "viewport": {"pan_x": 0, "pan_y": 0, "zoom": 1},
    })
    assert removed.deleted["first"].item.title == "Remember this"
    assert removed.deleted["first"].connections[0].id == "edge-1"
    reopened = CanvasStore(tmp_path, "full-delete").load()
    assert "first" in reopened.deleted
    restored = mutate(store, reopened.revision, "snapshot-restored", "replace-working-document", {
        "items": [item("first", "Remember this"), item("second", "Keep this")],
        "connections": [{"id": "edge-1", "source": "first", "target": "second", "label": "knows"}],
        "positions": {"first": {"x": 10, "y": 20}, "second": {"x": 100, "y": 20}},
        "viewport": {"pan_x": 0, "pan_y": 0, "zoom": 1},
    })
    assert "first" not in restored.deleted
    assert len(restored.connections) == 1


def test_incomplete_canvas_command_rejected_without_internal_error(tmp_path):
    store = CanvasStore(tmp_path, "missing-fields")
    store.create()
    with pytest.raises(ValueError, match="missing required fields"):
        mutate(store, 0, "missing-item", "create-item", {"position": {"x": 1, "y": 2}})
    assert store.load().revision == 0
