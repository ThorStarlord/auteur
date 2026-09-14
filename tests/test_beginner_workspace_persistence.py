import json
import threading
from pathlib import Path

import pytest

from auteur.beginner.contracts import SessionEnvelope
from auteur.beginner.persistence import (
    BeginnerConcurrencyError,
    BeginnerPersistenceError,
    BeginnerSessionStore,
    CommandReceiptStore,
    _FilesystemLock,
)
import auteur.beginner.persistence as persistence


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


def test_revision_session_can_be_created_saved_and_reloaded_without_parent_collision(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    parent = store.save(make_session())

    saved_revision = store.create_revision("revision-1", parent)

    assert saved_revision == parent
    assert store.load_revision("revision-1") == parent
    assert store.revision_session_path("revision-1").exists()
    assert store.load() == parent


def test_revision_session_is_immutable_and_does_not_replace_existing_revision(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    parent = store.save(make_session())
    store.create_revision("revision-1", parent)
    revision = parent.model_copy(update={"premise": "A different premise."})

    with pytest.raises(BeginnerPersistenceError, match="already exists"):
        store.save_revision("revision-1", revision)

    assert store.load_revision("revision-1") == parent
    assert store.load() == parent


def test_update_owns_version_progression_even_when_mutator_tampers_with_version(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    original = store.save(make_session())

    updated = store.update(
        original.session_version,
        lambda session: session.model_copy(update={"session_version": 999, "premise": "Changed."}),
    )

    assert updated.session_version == original.session_version + 1
    assert store.load().session_version == original.session_version + 1
    assert store.load().premise == "Changed."


def test_failed_mutation_leaves_prior_session_unchanged(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    original = store.save(make_session())

    def fail(session: SessionEnvelope) -> SessionEnvelope:
        session.premise = "Transient mutation."
        raise RuntimeError("mutation failed")

    with pytest.raises(RuntimeError, match="mutation failed"):
        store.update(original.session_version, fail)

    assert store.load() == original


def test_session_update_serializes_same_version_updates(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    original = store.save(make_session())
    successes: list[SessionEnvelope] = []
    failures: list[Exception] = []

    def update(premise: str) -> None:
        try:
            successes.append(
                store.update(
                    original.session_version,
                    lambda session: session.model_copy(update={"premise": premise}),
                )
            )
        except Exception as exc:  # pragma: no cover - assertion below identifies the expected exception
            failures.append(exc)

    threads = [threading.Thread(target=update, args=(f"Premise {index}",)) for index in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(successes) == 1
    assert len(failures) == 1
    assert isinstance(failures[0], BeginnerConcurrencyError)
    assert store.load().session_version == original.session_version + 1
    assert store.load().premise == successes[0].premise


def test_separate_session_stores_serialize_same_version_updates(tmp_path: Path) -> None:
    first_store = BeginnerSessionStore(tmp_path, "workspace-1")
    second_store = BeginnerSessionStore(tmp_path, "workspace-1")
    original = first_store.save(make_session())
    first_started = threading.Event()
    release_first = threading.Event()
    second_entered = threading.Event()
    successes: list[SessionEnvelope] = []
    failures: list[Exception] = []

    def first_mutator(session: SessionEnvelope) -> SessionEnvelope:
        first_started.set()
        release_first.wait(2)
        return session.model_copy(update={"premise": "First."})

    def second_mutator(session: SessionEnvelope) -> SessionEnvelope:
        second_entered.set()
        return session.model_copy(update={"premise": "Second."})

    def first_update() -> None:
        try:
            successes.append(
                first_store.update(original.session_version, first_mutator)
            )
        except Exception as exc:  # pragma: no cover - assertion below identifies the expected exception
            failures.append(exc)

    def second_update() -> None:
        try:
            successes.append(
                second_store.update(original.session_version, second_mutator)
            )
        except Exception as exc:  # pragma: no cover - assertion below identifies the expected exception
            failures.append(exc)

    first_thread = threading.Thread(target=first_update)
    second_thread = threading.Thread(target=second_update)
    first_thread.start()
    assert first_started.wait(2)
    second_thread.start()
    assert not second_entered.wait(0.1)
    release_first.set()
    first_thread.join(2)
    second_thread.join(2)

    assert len(successes) == 1
    assert len(failures) == 1
    assert isinstance(failures[0], BeginnerConcurrencyError)
    assert first_store.load().session_version == original.session_version + 1
    assert first_store.load().premise == successes[0].premise


def test_lock_timeout_after_commit_is_classified_as_concurrency_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    original = store.save(make_session())
    committed = original.model_copy(update={"session_version": original.session_version + 1, "premise": "Committed."})
    monkeypatch.setattr(persistence, "_SESSION_LOCK_TIMEOUT", 0.01)
    outcome: list[Exception] = []

    with _FilesystemLock(store._session_lock):
        store.session_path.write_text(committed.model_dump_json(), encoding="utf-8")

        def contend() -> None:
            try:
                store.update(original.session_version, lambda session: session)
            except Exception as exc:  # pragma: no cover - assertion below identifies the expected exception
                outcome.append(exc)

        thread = threading.Thread(target=contend)
        thread.start()
        thread.join(2)

    assert len(outcome) == 1
    assert isinstance(outcome[0], BeginnerConcurrencyError)
    assert store.load() == committed


def test_abandoned_lock_file_does_not_block_new_store(tmp_path: Path) -> None:
    first_store = BeginnerSessionStore(tmp_path, "workspace-1")
    second_store = BeginnerSessionStore(tmp_path, "workspace-1")
    original = first_store.save(make_session())
    first_store._session_lock.write_text("abandoned owner", encoding="utf-8")

    updated = second_store.update(
        original.session_version,
        lambda session: session.model_copy(update={"premise": "Recovered."}),
    )

    assert updated.session_version == original.session_version + 1
    assert second_store.load().premise == "Recovered."


def test_save_requires_current_version_and_never_regresses_persisted_version(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    original = store.save(make_session())
    stale = original.model_copy(update={"session_version": 0})

    with pytest.raises(BeginnerConcurrencyError):
        store.save(stale, expected_session_version=0)

    saved = store.save(stale, expected_session_version=original.session_version)

    assert saved.session_version == original.session_version + 1
    assert store.load().session_version == original.session_version + 1


def test_create_is_create_only(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    store.create(make_session())

    with pytest.raises(BeginnerPersistenceError, match="already exists"):
        store.create(make_session())


@pytest.mark.parametrize("value", ["../outside", "nested/value", r"nested\\value", ".", "..", ""])
def test_workspace_and_artifact_ids_reject_path_traversal(tmp_path: Path, value: str) -> None:
    if value == "":
        with pytest.raises(ValueError):
            BeginnerSessionStore(tmp_path, value)
        return

    if value in {"../outside", "nested/value", r"nested\value", ".", ".."}:
        with pytest.raises(ValueError):
            BeginnerSessionStore(tmp_path, value)

    store = BeginnerSessionStore(tmp_path, "workspace-1")
    with pytest.raises(ValueError):
        store.revision_session_path(value)
    receipt_store = CommandReceiptStore(tmp_path, "workspace-1")
    with pytest.raises(ValueError):
        receipt_store.receipt_path(value)
    assert not (tmp_path / "outside").exists()


def test_competing_receipt_claims_have_one_new_owner(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    claims = []

    def claim() -> None:
        claims.append(store.begin("command-1"))

    threads = [threading.Thread(target=claim) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sum(claim.acquired for claim in claims) == 1
    assert {claim.status for claim in claims} == {"in_progress"}


def test_receipt_non_json_result_raises_persistence_error(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    receipt = store.begin("command-1")

    with pytest.raises(BeginnerPersistenceError, match="receipt"):
        store.complete(receipt, object())


def test_receipt_directory_failure_raises_persistence_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")

    def fail_mkdir(*args: object, **kwargs: object) -> None:
        raise OSError("mkdir failed")

    monkeypatch.setattr("auteur.beginner.persistence.Path.mkdir", fail_mkdir)
    with pytest.raises(BeginnerPersistenceError, match="mkdir failed"):
        store.begin("command-1")


def test_receipt_write_failure_raises_persistence_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    receipt = store.begin("command-1")

    monkeypatch.setattr("auteur.beginner.persistence.os.replace", lambda source, destination: (_ for _ in ()).throw(OSError("write failed")))
    with pytest.raises(BeginnerPersistenceError, match="write failed"):
        store.complete(receipt, {"ok": True})


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


def test_wrong_typed_persisted_session_json_raises_clear_persistence_error(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    payload = make_session().model_dump(mode="json")
    payload["session_version"] = "7"
    store.session_path.parent.mkdir(parents=True)
    store.session_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(BeginnerPersistenceError, match="session"):
        store.load()


def test_receipt_json_is_valid_json(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    receipt = store.begin("command-1")

    assert json.loads(store.receipt_path(receipt.command_id).read_text(encoding="utf-8"))["command_id"] == "command-1"
