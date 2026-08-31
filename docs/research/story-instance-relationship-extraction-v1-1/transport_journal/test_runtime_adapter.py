import hashlib

import pytest

from transport_journal import Journal, JournalError, rebuild_ledger
from runtime_adapter import RuntimeAdapter


def p(pos=1, oid="O_SYNTH"):
    return {"run_id": "synthetic-adapter", "schedule_position": pos,
            "opaque_observation_id": oid, "role": "canary"}


def test_a1_and_a6_normal_lifecycle_reconciles_complete(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    adapter.allocate(p())
    adapter.before_launch("O_SYNTH")
    adapter.bind("O_SYNTH", "agent-1", "launch")
    adapter.before_wait("O_SYNTH", "agent-1")
    captured = adapter.capture("O_SYNTH", "agent-1", "CANARY_A_READY", "done", False)
    adapter.complete("O_SYNTH", "agent-1", captured["raw_response_sha256"])
    result = adapter.reconcile([1])
    assert result.ready
    assert result.complete_chains == 1


def test_a2_launch_gate_refuses_without_allocation(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    with pytest.raises(JournalError):
        adapter.before_launch("O_MISSING")


def test_a3_changed_agent_binding_refuses(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    adapter.allocate(p())
    adapter.bind("O_SYNTH", "agent-1", "launch")
    with pytest.raises(JournalError):
        adapter.bind("O_SYNTH", "agent-2", "launch-2")


def test_a4_capture_wrong_agent_refuses(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    adapter.allocate(p())
    adapter.bind("O_SYNTH", "agent-1", "launch")
    with pytest.raises(JournalError):
        adapter.capture("O_SYNTH", "agent-2", "CANARY", "done", False)


def test_a5_complete_before_capture_refuses(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    adapter.allocate(p())
    adapter.bind("O_SYNTH", "agent-1", "launch")
    with pytest.raises(JournalError):
        adapter.complete("O_SYNTH", "agent-1", "0" * 64)


def test_a7_restart_after_binding_reports_incomplete(tmp_path):
    root = tmp_path / "transport"
    adapter = RuntimeAdapter(Journal(root))
    adapter.allocate(p())
    adapter.bind("O_SYNTH", "agent-1", "launch")
    restarted = RuntimeAdapter(Journal(root))
    result = restarted.reconcile([1])
    assert not result.ready
    assert result.incomplete_chains == 1


def test_a8_derived_failure_preserves_authoritative_chain(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    adapter.allocate(p())
    adapter.bind("O_SYNTH", "agent-1", "launch")
    captured = adapter.capture("O_SYNTH", "agent-1", "CANARY_B_READY", "done", False)
    adapter.complete("O_SYNTH", "agent-1", captured["raw_response_sha256"])
    target = tmp_path / "ledger.json"
    rebuild_ledger(adapter.journal.root, target)
    event_hash = hashlib.sha256(
        (adapter.journal.root / "O_SYNTH" / "04-complete.json").read_bytes()
    ).hexdigest()
    ledger_hash = hashlib.sha256(target.read_bytes()).hexdigest()
    with pytest.raises(JournalError):
        adapter.rebuild_ledger(target, simulate_failure=True)
    assert hashlib.sha256(
        (adapter.journal.root / "O_SYNTH" / "04-complete.json").read_bytes()
    ).hexdigest() == event_hash
    assert hashlib.sha256(target.read_bytes()).hexdigest() == ledger_hash

