import json
from pathlib import Path

import pytest

from auteur.beginner.contracts import SessionEnvelope
from auteur.beginner.persistence import (
    BeginnerConcurrencyError,
    BeginnerPersistenceError,
    BeginnerSessionStore,
    CommandReceiptStore,
)


def make_session() -> SessionEnvelope:
    return SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")


def test_session_store_writes_and_reloads_a_versioned_envelope(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")

    saved = store.save(make_session())

    assert saved.session_version == 1
    assert store.session_path == tmp_path / ".auteur" / "beginner" / "workspaces" / "workspace-1" / "session.json"
    assert store.load() == saved


def test_stale_session_version_rejects_without_writing_or_calling_mutator(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    store.save(make_session())
    before = store.session_path.read_bytes()
    called = False

    def mutator(session: SessionEnvelope) -> SessionEnvelope:
        nonlocal called
        called = True
        return session

    with pytest.raises(BeginnerConcurrencyError):
        store.update(0, mutator)

    assert called is False
    assert store.session_path.read_bytes() == before


def test_atomic_write_failure_leaves_prior_session_intact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    original = store.save(make_session())

    def fail_replace(source: str, destination: str) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr("auteur.beginner.persistence.os.replace", fail_replace)

    with pytest.raises(BeginnerPersistenceError, match="replace failed"):
        store.update(original.session_version, lambda session: session)

    assert store.load() == original


def test_revision_path_is_separate_from_parent_session_path(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")

    revision_path = store.revision_session_path("revision-1")

    assert revision_path == store.session_path.parent / "revisions" / "revision-1" / "session.json"
    assert revision_path != store.session_path


def test_receipt_replay_returns_recorded_result_and_does_not_duplicate(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")

    first = store.begin("command-1")
    completed = store.complete(first, {"workspace_id": "workspace-1"})
    replay = store.replay("command-1")

    assert completed.status == "complete"
    assert replay == {"workspace_id": "workspace-1"}
    assert len(list(store.receipts_path.glob("*.json"))) == 1
    assert store.begin("command-1") == completed


def test_incomplete_receipt_can_be_loaded_for_recovery(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")

    pending = store.begin("command-1")

    assert store.load("command-1") == pending
    assert pending.status == "in_progress"
    assert store.replay("command-1") is None


def test_malformed_persisted_json_raises_clear_persistence_error(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    store.session_path.parent.mkdir(parents=True)
    store.session_path.write_text("{not json", encoding="utf-8")

    with pytest.raises(BeginnerPersistenceError, match="session"):
        store.load()


def test_receipt_json_is_valid_json(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    receipt = store.begin("command-1")

    assert json.loads(store.receipt_path(receipt.command_id).read_text(encoding="utf-8"))["command_id"] == "command-1"
