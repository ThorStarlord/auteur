import hashlib
import json
from pathlib import Path

import pytest

from transport_journal import (
    JournalError,
    Journal,
    rebuild_ledger,
    reconcile,
)


def make_journal(tmp_path):
    return Journal(tmp_path / "transport")


def payload(pos=1, oid="O_SYNTH", role="generator"):
    return {"run_id": "synthetic", "schedule_position": pos,
            "opaque_observation_id": oid, "role": role, "probe": "P02",
            "repetition": 1}


def complete(j, pos=1, oid="O_SYNTH", agent="agent-1", response="ok"):
    j.allocate(payload(pos, oid))
    j.bind(oid, agent, "2026-01-01T00:00:01Z")
    raw = j.capture(oid, agent, response, "2026-01-01T00:00:02Z", False)
    j.complete(oid, agent, raw["raw_response_sha256"])
    return raw


def test_j1_normal_lifecycle_and_j10_full_journal(tmp_path):
    j = make_journal(tmp_path)
    for i in range(1, 79):
        complete(j, i, f"O_{i:03}", f"A_{i:03}", f"response-{i}")
    result = reconcile(j.root, expected_positions=range(1, 79))
    assert result.ready
    assert result.complete_chains == 78
    assert result.unique_opaque_ids == 78
    assert result.unique_agent_ids == 78
    assert result.hash_mismatches == 0
    assert len(list(j.root.iterdir())) == 78
    ledger = rebuild_ledger(j.root)
    assert ledger["derived"] == "REBUILDABLE_NON_AUTHORITATIVE"
    assert len(ledger["records"]) == 78


def test_j2_binding_overwrite_refused_and_bytes_unchanged(tmp_path):
    j = make_journal(tmp_path)
    j.allocate(payload())
    j.bind("O_SYNTH", "agent-1", "t")
    p = j.root / "O_SYNTH" / "02-agent-bound.json"
    before = p.read_bytes()
    with pytest.raises(JournalError):
        j.bind("O_SYNTH", "agent-2", "t2")
    assert p.read_bytes() == before


def test_j3_capture_overwrite_refused_and_bytes_unchanged(tmp_path):
    j = make_journal(tmp_path)
    j.allocate(payload())
    j.bind("O_SYNTH", "agent-1", "t")
    j.capture("O_SYNTH", "agent-1", "first", "t2", False)
    p = j.root / "O_SYNTH" / "03-response-captured.json"
    before = p.read_bytes()
    with pytest.raises(JournalError):
        j.capture("O_SYNTH", "agent-1", "second", "t3", False)
    assert p.read_bytes() == before


def test_j4_failed_derived_rebuild_does_not_touch_previous_ledger(tmp_path):
    j = make_journal(tmp_path)
    complete(j)
    target = tmp_path / "ledger.json"
    rebuild_ledger(j.root, target)
    before = target.read_bytes()
    with pytest.raises(JournalError):
        rebuild_ledger(j.root, target, simulate_failure=True)
    assert target.read_bytes() == before


def test_j5_hash_mismatch_is_reported_without_mutation(tmp_path):
    j = make_journal(tmp_path)
    raw = complete(j, response="stable")
    event = j.root / "O_SYNTH" / "03-response-captured.json"
    before = event.read_bytes()
    event_data = json.loads(before)
    event_data["raw_response_sha256"] = "0" * 64
    event.write_bytes(json.dumps(event_data, sort_keys=True).encode() + b"\n")
    result = reconcile(j.root, expected_positions=[1])
    assert result.hash_mismatches == 1
    assert json.loads(event.read_bytes())["raw_response_sha256"] == "0" * 64
    assert before != event.read_bytes()


def test_j6_rebuild_after_derived_ledger_deleted(tmp_path):
    j = make_journal(tmp_path)
    complete(j)
    target = tmp_path / "ledger.json"
    first = rebuild_ledger(j.root, target)
    target.unlink()
    second = rebuild_ledger(j.root, target)
    assert first == second


def test_j7_missing_event_refuses_readiness(tmp_path):
    j = make_journal(tmp_path)
    complete(j)
    (j.root / "O_SYNTH" / "04-complete.json").unlink()
    assert not reconcile(j.root, expected_positions=[1]).ready


def test_j8_duplicate_agent_refuses_readiness(tmp_path):
    j = make_journal(tmp_path)
    complete(j, 1, "O_ONE", "same")
    complete(j, 2, "O_TWO", "same")
    result = reconcile(j.root, expected_positions=[1, 2])
    assert not result.ready
    assert result.conflicting_bindings == 1


def test_j9_duplicate_opaque_id_refused(tmp_path):
    j = make_journal(tmp_path)
    j.allocate(payload(1, "O_DUP"))
    with pytest.raises(JournalError):
        j.allocate(payload(2, "O_DUP"))


def test_crash_recovery_is_incomplete(tmp_path):
    j = make_journal(tmp_path)
    j.allocate(payload())
    j.bind("O_SYNTH", "agent-1", "t")
    result = reconcile(j.root, expected_positions=[1])
    assert not result.ready
    assert result.incomplete_chains == 1
    assert not (j.root / "O_SYNTH" / "04-complete.json").exists()

