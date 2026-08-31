import json

import pytest

from runtime_adapter import RuntimeAdapter
from transport_journal import Journal, JournalError
from worker_lifecycle import (
    LifecycleError,
    assert_next_launch_permitted,
    record_worker_closed,
)


def payload(pos, oid):
    return {"run_id": "synthetic-lifecycle", "schedule_position": pos,
            "opaque_observation_id": oid, "role": "canary"}


def completed(adapter, pos, oid, agent):
    adapter.allocate(payload(pos, oid))
    adapter.before_launch(oid)
    adapter.bind(oid, agent, "launch")
    adapter.before_wait(oid, agent)
    captured = adapter.capture(oid, agent, f"response-{pos}", "done", False)
    adapter.complete(oid, agent, captured["raw_response_sha256"])


def close(adapter, oid, agent):
    return record_worker_closed(
        adapter.journal.root, oid, agent, "multi_agent_v1__close_agent",
        {"previous_status": {"completed": "synthetic"}},
    )


def test_l1_completed_chain_and_successful_close_permit_next_launch(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    completed(adapter, 14, "O_A", "A_A")
    evidence = close(adapter, "O_A", "A_A")

    assert evidence["agent_id"] == "A_A"
    assert assert_next_launch_permitted(adapter.journal.root).ready


def test_l2_completed_chain_without_close_record_refuses(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    completed(adapter, 14, "O_A", "A_A")

    with pytest.raises(LifecycleError):
        assert_next_launch_permitted(adapter.journal.root)


def test_l3_close_record_for_wrong_agent_refuses(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    completed(adapter, 14, "O_A", "A_A")

    with pytest.raises(LifecycleError):
        record_worker_closed(
            adapter.journal.root, "O_A", "A_WRONG",
            "multi_agent_v1__close_agent", {"ack": True},
        )


def test_l4_close_before_response_completion_refuses(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    adapter.allocate(payload(14, "O_A"))
    adapter.bind("O_A", "A_A", "launch")

    with pytest.raises(LifecycleError):
        record_worker_closed(
            adapter.journal.root, "O_A", "A_A",
            "multi_agent_v1__close_agent", {"ack": True},
        )


def test_l5_duplicate_close_evidence_is_write_once(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    completed(adapter, 14, "O_A", "A_A")
    close(adapter, "O_A", "A_A")
    before = (adapter.journal.root / "O_A" / "05-worker-closed.json").read_bytes()

    with pytest.raises(LifecycleError):
        close(adapter, "O_A", "A_A")

    assert (adapter.journal.root / "O_A" / "05-worker-closed.json").read_bytes() == before


def test_l6_any_prior_completed_observation_without_close_blocks(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    completed(adapter, 14, "O_A", "A_A")
    completed(adapter, 43, "O_B", "A_B")
    close(adapter, "O_A", "A_A")

    with pytest.raises(LifecycleError):
        assert_next_launch_permitted(adapter.journal.root)

    assert not (adapter.journal.root / "O_B" / "05-worker-closed.json").exists()
