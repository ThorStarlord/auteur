"""Concurrent CanvasStore reads never make a save fail, and never see a partial document (#617).

On Windows, `os.replace` is refused while another handle has the target open, and
opening the target while it is being replaced is refused too. Both are transient
sharing conflicts: writers hold `.canvas.lock`, so the revision checked under it
stays current while the replace is retried for a bounded time.
"""
import os
import threading
import time
from pathlib import Path

import pytest

from auteur.beginner import persistence
from auteur.beginner.persistence import BeginnerConcurrencyError, BeginnerPersistenceError
from auteur.beginner.studio_store import CanvasStore

windows_only = pytest.mark.skipif(os.name != "nt", reason="Windows file-sharing semantics")


def document(text):
    return {"items": [{"id": "s", "title": "Scene", "content": text}], "connections": [],
            "positions": {"s": {"x": 0, "y": 0}}, "viewport": {"pan_x": 0, "pan_y": 0, "zoom": 1}}


def save(store, revision, text, command_id=None):
    return store.apply("replace-working-document", expected_revision=revision,
                       command_id=command_id or f"save-{revision}", payload=document(text))


def test_saves_and_loads_succeed_while_other_threads_keep_reading(tmp_path):
    store = CanvasStore(tmp_path, "race")
    store.create()
    stop, failures, revisions = threading.Event(), [], []

    def reader():
        last = -1
        while not stop.is_set():
            try:
                canvas = store.load()
            except Exception as exc:  # any failed read is a defect here
                failures.append(f"load: {exc}")
                continue
            if canvas.revision < last:
                failures.append(f"revision went back from {last} to {canvas.revision}")
            last = canvas.revision
            revisions.append(canvas.revision)

    readers = [threading.Thread(target=reader) for _ in range(3)]
    for thread in readers:
        thread.start()
    try:
        for revision in range(60):
            try:
                assert save(store, revision, "x" * revision).revision == revision + 1
            except BeginnerPersistenceError as exc:
                failures.append(f"save {revision}: {exc}")
                break
    finally:
        stop.set()
        for thread in readers:
            thread.join()
    assert failures == []
    assert store.load().revision == 60 and store.load().items[0].content == "x" * 59
    assert revisions, "readers ran"


def test_a_save_waits_for_a_reader_that_still_has_the_file_open(tmp_path):
    store = CanvasStore(tmp_path, "held")
    store.create()
    held = (store.directory / "canvas.json").open("rb")
    threading.Timer(0.1, held.close).start()
    assert save(store, 0, "after the reader").revision == 1
    assert store.load().items[0].content == "after the reader"


@windows_only
def test_a_replace_that_stays_refused_fails_within_the_bound_and_changes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(persistence, "_SHARING_RETRY_SECONDS", 0.2)
    store = CanvasStore(tmp_path, "stuck")
    store.create()
    before = (store.directory / "canvas.json").read_bytes()
    with (store.directory / "canvas.json").open("rb"):
        started = time.monotonic()
        with pytest.raises(BeginnerPersistenceError, match="atomic write failed"):
            save(store, 0, "never saved")
        assert time.monotonic() - started < 2
    assert (store.directory / "canvas.json").read_bytes() == before
    assert [p.name for p in store.directory.iterdir() if p.name.startswith(".canvas.json.")] == []
    assert save(store, 0, "saved once released").revision == 1


@windows_only
def test_a_load_retries_a_sharing_refusal_but_not_other_failures(tmp_path, monkeypatch):
    store = CanvasStore(tmp_path, "load")
    store.create()
    real_read = Path.read_text
    calls = []

    def refused_twice(path, *args, **kwargs):
        calls.append(path.name)
        if len(calls) <= 2:
            raise PermissionError(13, "Permission denied")
        return real_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", refused_twice)
    assert store.load().revision == 0 and len(calls) == 3

    monkeypatch.setattr(persistence, "_SHARING_RETRY_SECONDS", 0.1)
    monkeypatch.setattr(Path, "read_text", lambda *a, **k: (_ for _ in ()).throw(PermissionError(13, "denied")))
    with pytest.raises(BeginnerPersistenceError, match="could not read canvas"):
        store.load()


def test_missing_corrupt_and_stale_canvases_keep_their_distinct_failures(tmp_path):
    store = CanvasStore(tmp_path, "kinds")
    with pytest.raises(FileNotFoundError):
        store.load()
    store.create()
    assert save(store, 0, "first").revision == 1
    with pytest.raises(BeginnerConcurrencyError, match="canvas version mismatch"):
        save(store, 0, "stale", command_id="stale-save")
    assert store.load().items[0].content == "first"
    (store.directory / "canvas.json").write_text('{"canvas_id": "kinds", "revision": "x"', encoding="utf-8")
    started = time.monotonic()
    with pytest.raises(BeginnerPersistenceError, match="could not read canvas"):
        store.load()
    assert time.monotonic() - started < 0.5  # an invalid document is never retried
