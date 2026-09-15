import json
import inspect
import os
import subprocess
import threading
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError
import pytest

from auteur.beginner.contracts import SessionEnvelope
from auteur.beginner.contracts import AcceptedMilestoneReference, RevisionRef
from auteur.beginner.persistence import (
    BeginnerConcurrencyError,
    BeginnerCommandType,
    BeginnerMilestone,
    BeginnerPersistenceError,
    BeginnerSessionStore,
    CommandReceipt,
    CommandReceiptStore,
    JsonObject,
    JsonValue,
    ReceiptAcquisition,
    _FilesystemLock,
)
import auteur.beginner.persistence as persistence


def make_session() -> SessionEnvelope:
    return SessionEnvelope.new("project-1", "mystery", "A missing heir returns home.")


def begin_workspace_command(store: CommandReceiptStore, command_id: str = "command-1") -> ReceiptAcquisition:
    return store.begin(command_id, command_type="create_workspace")


def build_receipt_acquisition(payload: dict[str, Any]) -> ReceiptAcquisition:
    return ReceiptAcquisition.model_validate({"command_id": "command-1", **payload})


def test_session_store_writes_and_reloads_a_versioned_envelope(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")

    saved = store.save(make_session())

    assert saved.session_version == 1
    assert store.session_path == tmp_path / ".auteur" / "beginner" / "workspaces" / "workspace-1" / "session.json"
    assert store.load() == saved


@pytest.mark.parametrize("field_value", ["not-an-integer", ""])
def test_corrupted_session_envelope_is_rejected_before_write(tmp_path: Path, field_value: str) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    original = store.save(make_session())
    corrupted = original.model_copy(update={"session_version": field_value} if field_value != "" else {"premise": ""})

    with pytest.raises(BeginnerPersistenceError):
        store.save(corrupted, expected_session_version=original.session_version)

    assert store.load() == original


def test_update_rejects_nested_wrong_type_before_mutating_persisted_session(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    milestone = AcceptedMilestoneReference(
        milestone_id="milestone-1", revision=RevisionRef(artifact_id="artifact-1", revision=2)
    )
    original = store.save(make_session().model_copy(update={"accepted_milestones": [milestone]}))
    corrupted_revision = milestone.revision.model_copy(update={"revision": "2"})
    corrupted = original.model_copy(
        update={"accepted_milestones": [milestone.model_copy(update={"revision": corrupted_revision})]}
    )
    before = store.session_path.read_bytes()

    with pytest.raises(BeginnerPersistenceError):
        store.update(original.session_version, lambda session: corrupted)

    assert store.session_path.read_bytes() == before
    assert store.load() == original


def test_corrupted_revision_envelope_is_rejected_before_write(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    corrupted = make_session().model_copy(update={"premise": ""})

    with pytest.raises(BeginnerPersistenceError):
        store.save_revision("revision-1", corrupted)

    assert not store.revision_session_path("revision-1").exists()


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


def test_initial_creation_rejects_nonzero_envelope_version(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    supplied = make_session().model_copy(update={"session_version": 41})

    with pytest.raises(BeginnerPersistenceError, match="initial session version"):
        store.save(supplied)

    assert not store.session_path.exists()


def test_initial_save_and_create_reject_unexpected_expected_version_without_creating(tmp_path: Path) -> None:
    save_store = BeginnerSessionStore(tmp_path, "save-workspace")
    create_store = BeginnerSessionStore(tmp_path, "create-workspace")

    with pytest.raises(BeginnerConcurrencyError):
        save_store.save(make_session(), expected_session_version=7)
    with pytest.raises(BeginnerConcurrencyError):
        create_store.create(make_session(), expected_session_version=7)

    assert not save_store.session_path.exists()
    assert not create_store.session_path.exists()


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
        claims.append(begin_workspace_command(store))

    threads = [threading.Thread(target=claim) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sum(claim.acquired for claim in claims) == 1
    assert {claim.status for claim in claims} == {"in_progress"}


def test_in_progress_receipt_with_missing_owner_is_rejected(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    path = store.receipt_path("command-1")
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "command_id": "command-1",
                "status": "in_progress",
                "owner_token": None,
                "command_type": "create_workspace",
                "result": None,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(BeginnerPersistenceError, match="in_progress receipt must have an owner_token"):
        store.load("command-1")


def test_in_progress_receipt_with_result_is_rejected_even_with_owner(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    path = store.receipt_path("command-1")
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "command_id": "command-1",
                "status": "in_progress",
                "owner_token": "owner",
                "command_type": "create_workspace",
                "result": {"x": 1},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(BeginnerPersistenceError, match="in_progress receipt must not have a result"):
        store.load("command-1")


@pytest.mark.parametrize("value", ["CON", "con", "PrN", "aux", "NUL", "COM1", "com9", "LPT1", "lpt9"])
def test_windows_reserved_device_names_are_rejected_before_io(tmp_path: Path, value: str) -> None:
    with pytest.raises(ValueError):
        BeginnerSessionStore(tmp_path, value)

    store = BeginnerSessionStore(tmp_path, "workspace-1")
    with pytest.raises(ValueError):
        store.revision_session_path(value)
    receipt_store = CommandReceiptStore(tmp_path, "workspace-1")
    with pytest.raises(ValueError):
        receipt_store.receipt_path(value)


def test_receipt_non_json_result_raises_persistence_error(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    receipt = begin_workspace_command(store)

    with pytest.raises(BeginnerPersistenceError, match="receipt"):
        store.complete(receipt, cast(JsonValue, object()))


def test_receipt_directory_failure_raises_persistence_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")

    def fail_mkdir(*args: object, **kwargs: object) -> None:
        raise OSError("mkdir failed")

    monkeypatch.setattr("auteur.beginner.persistence.Path.mkdir", fail_mkdir)
    with pytest.raises(BeginnerPersistenceError, match="mkdir failed"):
        begin_workspace_command(store)


def test_receipt_write_failure_raises_persistence_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    receipt = begin_workspace_command(store)

    monkeypatch.setattr("auteur.beginner.persistence.os.replace", lambda source, destination: (_ for _ in ()).throw(OSError("write failed")))
    with pytest.raises(BeginnerPersistenceError, match="write failed"):
        store.complete(receipt, {"ok": True})


def test_receipt_replay_returns_recorded_result_and_does_not_duplicate(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")

    first = begin_workspace_command(store)
    completed = store.complete(first, {"workspace_id": "workspace-1"})
    replay = store.replay("command-1")

    assert completed.status == "complete"
    assert replay is not None
    assert replay.result == {"workspace_id": "workspace-1"}
    assert len(list(store.receipts_path.glob("*.json"))) == 1
    replay_claim = begin_workspace_command(store)
    assert replay_claim.outcome == "completed_replay"
    assert replay_claim.result == completed.result


def test_receipt_persists_command_and_promotion_intent_metadata(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")

    claim = store.begin(
        "command-1",
        command_type="promote_milestone",
        target_milestone="identity-accepted",
        promotion_intent={"source": "beginner"},
        domain_result_reference={"artifact_id": "identity-1", "revision": 2},
    )

    loaded = store.load("command-1")
    assert claim.command_type == "promote_milestone"
    assert loaded.command_type == "promote_milestone"
    assert loaded.target_milestone == "identity-accepted"
    assert loaded.promotion_intent == {"source": "beginner"}
    assert loaded.domain_result_reference == {"artifact_id": "identity-1", "revision": 2}


@pytest.mark.parametrize(
    "changed_intent",
    [
        {"command_type": "other_command"},
        {"target_milestone": "different-milestone"},
        {"promotion_intent": {"source": "different"}},
    ],
)
def test_reusing_command_id_with_different_intent_rejects(
    tmp_path: Path, changed_intent: dict[str, Any]
) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    store.begin(
        "command-1",
        command_type="promote_milestone",
        target_milestone="identity-accepted",
        promotion_intent={"source": "beginner"},
        domain_result_reference={"artifact_id": "identity-1", "revision": 2},
    )

    with pytest.raises((BeginnerPersistenceError, ValidationError)):
        store.begin(
            "command-1",
            command_type=cast(BeginnerCommandType, changed_intent.get("command_type", "promote_milestone")),
            target_milestone=cast(BeginnerMilestone, changed_intent.get("target_milestone", "identity-accepted")),
            promotion_intent=cast(JsonObject, changed_intent.get("promotion_intent", {"source": "beginner"})),
        )


def test_reusing_command_id_with_omitted_intent_rejects(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    store.begin("command-1", command_type="promote_milestone", target_milestone="identity-accepted")

    assert inspect.signature(store.begin).parameters["command_type"].default is inspect.Parameter.empty


def test_complete_persists_authoritative_domain_result_reference(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    owner = store.begin("command-1", command_type="promote_milestone", target_milestone="identity-accepted")

    completed = store.complete(
        owner,
        {"accepted": True},
        domain_result_reference={"artifact_id": "identity-1", "revision": 3},
    )

    assert completed.domain_result_reference == {"artifact_id": "identity-1", "revision": 3}
    assert store.load("command-1").domain_result_reference == completed.domain_result_reference
    replay = store.replay("command-1")
    assert replay is not None
    assert replay.result == {"accepted": True}

    retried = store.begin("command-1", command_type="promote_milestone", target_milestone="identity-accepted")
    assert retried.outcome == "completed_replay"
    assert retried.result == {"accepted": True}


def test_receipt_json_values_are_normalized_for_retry_and_persistence(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    owner = store.begin(
        "command-1",
        command_type="promote_milestone",
        target_milestone="identity-accepted",
        promotion_intent={"choices": ["identity", "structure"]},
    )

    store.complete(
        owner,
        ["accepted", True],
        domain_result_reference={"revision": [1, 2]},
    )

    loaded = store.load("command-1")
    retry = store.begin(
        "command-1",
        command_type="promote_milestone",
        target_milestone="identity-accepted",
        promotion_intent={"choices": ["identity", "structure"]},
    )
    assert loaded.result == ["accepted", True]
    assert loaded.domain_result_reference == {"revision": [1, 2]}
    assert loaded.promotion_intent == {"choices": ["identity", "structure"]}
    assert retry.outcome == "completed_replay"
    assert retry.result == ["accepted", True]


def test_empty_command_type_is_not_defaulted(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")

    with pytest.raises(ValidationError):
        store.begin("command-1", command_type=cast(BeginnerCommandType, ""))


@pytest.mark.parametrize(
    ("command_type", "target_milestone"),
    [
        (None, None),
        ("unknown", None),
        ("promote_milestone", None),
        ("promote_milestone", "not-an-approved-milestone"),
        ("create_workspace", "identity-accepted"),
    ],
)
def test_receipt_intent_requires_approved_command_and_milestone(
    tmp_path: Path, command_type: object, target_milestone: object
) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")

    with pytest.raises(ValidationError):
        store.begin(
            "command-1",
            command_type=cast(BeginnerCommandType, command_type),
            target_milestone=cast(BeginnerMilestone | None, target_milestone),
        )


def test_completed_receipt_rejects_conflicting_domain_result_reference(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    owner = store.begin(
        "command-1",
        command_type="promote_milestone",
        target_milestone="identity-accepted",
        domain_result_reference={"artifact_id": "identity-1", "revision": 2},
    )
    store.complete(owner, {"accepted": True}, domain_result_reference={"artifact_id": "identity-1", "revision": 3})

    replay = store.begin(
        "command-1",
        command_type="promote_milestone",
        target_milestone="identity-accepted",
        domain_result_reference={"artifact_id": "identity-1", "revision": 2},
    )
    assert replay.outcome == "completed_replay"

    with pytest.raises(BeginnerPersistenceError, match="intent conflict"):
        store.begin(
            "command-1",
            command_type="promote_milestone",
            target_milestone="identity-accepted",
            domain_result_reference={"artifact_id": "identity-2", "revision": 3},
        )


@pytest.mark.parametrize(
    ("field_name", "first_value", "retry_value"),
    [("promotion_intent", True, 1), ("domain_result_reference", 1, 1.0)],
)
def test_receipt_intent_comparison_uses_canonical_json_identity(
    tmp_path: Path, field_name: str, first_value: JsonValue, retry_value: JsonValue
) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    first: JsonObject = {"value": first_value}
    retry: JsonObject = {"value": retry_value}
    if field_name == "promotion_intent":
        store.begin("command-1", command_type="create_workspace", promotion_intent=first)
    else:
        store.begin("command-1", command_type="create_workspace", domain_result_reference=first)

    with pytest.raises(BeginnerPersistenceError, match="intent conflict"):
        if field_name == "promotion_intent":
            store.begin("command-1", command_type="create_workspace", promotion_intent=retry)
        else:
            store.begin("command-1", command_type="create_workspace", domain_result_reference=retry)


def test_complete_completed_receipt_revalidates_acquisition_metadata(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    owner = store.begin("command-1", command_type="create_workspace")
    store.complete(owner, {"accepted": True})
    forged = owner.model_copy(update={"command_type": "promote_milestone", "target_milestone": "identity-accepted"})

    with pytest.raises(BeginnerPersistenceError, match="intent conflict"):
        store.complete(forged, {"accepted": True})


def test_atomic_create_and_replace_sync_containing_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    synced: list[Path] = []
    monkeypatch.setattr(persistence, "_sync_directory", lambda path: synced.append(path))

    store = BeginnerSessionStore(tmp_path, "workspace-1")
    store.save(make_session())
    store.save(store.load(), expected_session_version=1)

    assert len(synced) >= 2


def test_post_commit_directory_sync_failure_keeps_session_successful(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_sync(path: Path) -> None:
        raise OSError("directory sync failed")

    monkeypatch.setattr(persistence, "_sync_directory", fail_sync)
    store = BeginnerSessionStore(tmp_path, "workspace-1")

    saved = store.save(make_session())

    assert store.load() == saved


def test_post_commit_receipt_sync_failure_keeps_owner_claim_recoverable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_sync(path: Path) -> None:
        raise OSError("directory sync failed")

    monkeypatch.setattr(persistence, "_sync_directory", fail_sync)
    store = CommandReceiptStore(tmp_path, "workspace-1")

    owner = store.begin("command-1", command_type="create_workspace")
    retry = store.begin("command-1", command_type="create_workspace")

    assert owner.outcome == "owner_claim"
    assert retry.outcome == "existing_in_progress"
    assert store.load("command-1").owner_token == owner.owner_token


def test_in_progress_reference_is_part_of_retry_intent(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    store.begin("command-1", command_type="create_workspace", domain_result_reference={"artifact_id": "first"})

    with pytest.raises(BeginnerPersistenceError, match="intent conflict"):
        store.begin("command-1", command_type="create_workspace", domain_result_reference={"artifact_id": "second"})


@pytest.mark.parametrize("value", ["Workspace-1", "Revision-1", "Command-1"])
def test_uppercase_ids_are_rejected_as_noncanonical(tmp_path: Path, value: str) -> None:
    with pytest.raises(BeginnerPersistenceError, match="lowercase"):
        BeginnerSessionStore(tmp_path, value)

    store = BeginnerSessionStore(tmp_path, "workspace-1")
    with pytest.raises(BeginnerPersistenceError, match="lowercase"):
        store.revision_session_path(value)
    receipt_store = CommandReceiptStore(tmp_path, "workspace-1")
    with pytest.raises(BeginnerPersistenceError, match="lowercase"):
        receipt_store.receipt_path(value)


def test_symlinked_workspace_escape_is_rejected_before_write(tmp_path: Path) -> None:
    workspaces = tmp_path / ".auteur" / "beginner" / "workspaces"
    workspaces.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    escaped = workspaces / "workspace-1"
    try:
        escaped.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    with pytest.raises(ValueError, match="escapes intended root"):
        BeginnerSessionStore(tmp_path, "workspace-1")


def test_revision_directory_escape_is_rejected_before_write(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    revisions = store._workspace_path / "revisions"
    sibling = tmp_path / "revision-sibling"
    sibling.mkdir()
    revisions.parent.mkdir(parents=True, exist_ok=True)

    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(revisions), str(sibling)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            pytest.skip("junction creation unavailable")
    else:
        try:
            revisions.symlink_to(sibling, target_is_directory=True)
        except OSError as exc:
            pytest.skip(f"symlink creation unavailable: {exc}")

    with pytest.raises(ValueError, match="escapes intended root"):
        store.revision_session_path("revision-1")
    with pytest.raises(ValueError, match="escapes intended root"):
        store.save_revision("revision-1", make_session())


def _redirect_directory(path: Path, target: Path) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(path), str(target)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            pytest.skip("junction creation unavailable")
    else:
        try:
            path.symlink_to(target, target_is_directory=True)
        except OSError as exc:
            pytest.skip(f"symlink creation unavailable: {exc}")


def test_session_io_revalidates_replaced_workspace_container(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    sibling = tmp_path / "workspace-sibling"
    sibling.mkdir()
    store._workspace_path.parent.mkdir(parents=True, exist_ok=True)
    _redirect_directory(store._workspace_path, sibling)

    with pytest.raises(ValueError, match="escapes intended root"):
        store.save(make_session())
    assert not (sibling / "session.json").exists()


def test_revision_io_revalidates_replaced_revisions_container(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    revisions = store._workspace_path / "revisions"
    sibling = tmp_path / "revisions-sibling"
    sibling.mkdir()
    revisions.parent.mkdir(parents=True, exist_ok=True)
    _redirect_directory(revisions, sibling)

    with pytest.raises(ValueError, match="escapes intended root"):
        store.save_revision("revision-1", make_session())
    assert not (sibling / "revision-1" / "session.json").exists()


def test_receipt_io_revalidates_replaced_commands_container(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    sibling = tmp_path / "commands-sibling"
    sibling.mkdir()
    store.receipts_path.parent.mkdir(parents=True, exist_ok=True)
    _redirect_directory(store.receipts_path, sibling)

    with pytest.raises(ValueError, match="escapes intended root"):
        store.begin("command-1", command_type="create_workspace")
    assert not (sibling / "command-1.json").exists()


def test_receipts_reject_coercible_bytes_values() -> None:
    with pytest.raises(ValidationError, match="receipt result"):
        CommandReceipt(
            command_id="command-1",
            status="complete",
            owner_token="owner-1",
            command_type="create_workspace",
            result=cast(JsonValue, b"result"),
        )
    with pytest.raises(ValidationError, match="acquisition result"):
        ReceiptAcquisition(
            command_id="command-1",
            status="complete",
            outcome="completed_replay",
            command_type="create_workspace",
            result=cast(JsonValue, b"result"),
        )


@pytest.mark.parametrize("field_name", ["command_type", "target_milestone"])
def test_receipts_reject_coercible_identity_intent_strings(field_name: str) -> None:
    receipt_values: dict[str, Any] = {
        "command_id": "command-1",
        "status": "complete",
        "owner_token": "owner-1",
        field_name: b"not-a-string",
    }
    acquisition_values: dict[str, Any] = {
        "command_id": "command-1",
        "status": "complete",
        "outcome": "completed_replay",
        field_name: b"not-a-string",
    }

    with pytest.raises(ValidationError):
        CommandReceipt.model_validate(receipt_values)
    with pytest.raises(ValidationError):
        ReceiptAcquisition.model_validate(acquisition_values)


@pytest.mark.parametrize(
    "payload",
    [
        {"status": "complete", "outcome": "owner_claim", "owner_token": "token", "result": None},
        {"status": "complete", "outcome": "existing_in_progress", "owner_token": None, "result": None},
        {"status": "in_progress", "outcome": "owner_claim", "owner_token": "token", "result": {"done": True}},
        {"status": "complete", "outcome": "completed_replay", "owner_token": "token", "result": {"done": True}},
    ],
)
def test_receipt_acquisition_rejects_inconsistent_status_outcome_combinations(
    payload: dict[str, Any],
) -> None:
    with pytest.raises(ValidationError):
        build_receipt_acquisition(payload)


def test_replay_returns_receipt_like_completed_acquisition(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    owner = begin_workspace_command(store)
    store.complete(owner, {"accepted": True})

    replay = store.replay("command-1")

    assert replay is not None
    assert replay.outcome == "completed_replay"
    assert replay.result == {"accepted": True}


def test_receipt_load_rejects_command_id_mismatch_and_replay_cannot_cross_commands(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    receipt = begin_workspace_command(store)
    store.complete(receipt, {"command": "one"})
    path = store.receipt_path("command-1")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["command_id"] = "command-2"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(BeginnerPersistenceError, match="command_id"):
        store.load("command-1")
    with pytest.raises(BeginnerPersistenceError, match="command_id"):
        store.replay("command-1")


def test_existing_in_progress_begin_returns_valid_acquisition_result(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    owner = begin_workspace_command(store)
    contender = begin_workspace_command(store)

    assert isinstance(contender, ReceiptAcquisition)
    assert contender.outcome == "existing_in_progress"
    assert contender.owner_token is None
    assert owner.outcome == "owner_claim"
    assert ReceiptAcquisition.model_validate_json(contender.model_dump_json(), strict=True) == contender


def test_receipt_completion_requires_owner_token(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    owner = begin_workspace_command(store)
    contender = begin_workspace_command(store)

    with pytest.raises(BeginnerConcurrencyError, match="owner"):
        store.complete(contender, {"ok": True})

    assert store.replay("command-1") is None
    assert owner.acquired is True
    assert contender.acquired is False


def test_receipt_completion_rejects_never_begun_command(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    never_begun = CommandReceipt(
        command_id="command-1", status="in_progress", owner_token="token", command_type="create_workspace"
    )

    with pytest.raises(BeginnerPersistenceError, match="never begun"):
        store.complete(never_begun, {"ok": True})


def test_concurrent_completion_is_serialized_and_idempotent(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")
    owner = begin_workspace_command(store)
    results: list[CommandReceipt] = []
    failures: list[Exception] = []

    def complete(value: str) -> None:
        try:
            results.append(store.complete(owner, {"value": value}))
        except Exception as exc:  # pragma: no cover - assertion below identifies unexpected failures
            failures.append(exc)

    threads = [threading.Thread(target=complete, args=(value,)) for value in ("first", "second")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(2)

    persisted = store.load("command-1")
    assert failures == []
    assert len(results) == 2
    assert all(result == persisted for result in results)
    assert persisted.status == "complete"


def test_repeated_independent_receipt_completions_have_no_lock_open_race(tmp_path: Path) -> None:
    first_store = CommandReceiptStore(tmp_path, "workspace-1")
    second_store = CommandReceiptStore(tmp_path, "workspace-1")

    for iteration in range(50):
        command_id = f"command-{iteration}"
        owner = begin_workspace_command(first_store, command_id)
        completions: list[CommandReceipt] = []
        failures: list[Exception] = []

        def complete(store: CommandReceiptStore, value: str) -> None:
            try:
                completions.append(store.complete(owner, {"value": value}))
            except Exception as exc:  # pragma: no cover - assertion below identifies unexpected failures
                failures.append(exc)

        threads = [
            threading.Thread(target=complete, args=(first_store, "first")),
            threading.Thread(target=complete, args=(second_store, "second")),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(2)

        assert failures == []
        assert len(completions) == 2
        assert all(completion == first_store.load(command_id) for completion in completions)


def test_failed_lock_enter_closes_contender_handle(tmp_path: Path) -> None:
    store = BeginnerSessionStore(tmp_path, "workspace-1")
    with _FilesystemLock(store._session_lock):
        with pytest.raises(BeginnerPersistenceError, match="timed out"):
            _FilesystemLock(store._session_lock, timeout=0.01).__enter__()

    store._session_lock.unlink()


def test_incomplete_receipt_can_be_loaded_for_recovery(tmp_path: Path) -> None:
    store = CommandReceiptStore(tmp_path, "workspace-1")

    pending = begin_workspace_command(store)

    loaded = store.load("command-1")
    assert loaded.command_id == pending.command_id
    assert loaded.status == pending.status
    assert pending.outcome == "owner_claim"
    assert pending.owner_token == loaded.owner_token
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
    receipt = begin_workspace_command(store)

    assert json.loads(store.receipt_path(receipt.command_id).read_text(encoding="utf-8"))["command_id"] == "command-1"
