import json
import random

from progress_gate import derive_allocated_positions, reconcile_all_allocated
from runtime_adapter import RuntimeAdapter
from transport_journal import Journal, reconcile


def payload(pos, oid, role="extractor"):
    return {
        "run_id": "synthetic-progress-gate",
        "schedule_position": pos,
        "opaque_observation_id": oid,
        "role": role,
    }


def complete(adapter, pos, oid, agent):
    adapter.allocate(payload(pos, oid))
    adapter.before_launch(oid)
    adapter.bind(oid, agent, "launch")
    adapter.before_wait(oid, agent)
    captured = adapter.capture(oid, agent, f"response-{pos}", "done", False)
    adapter.complete(oid, agent, captured["raw_response_sha256"])


def test_g1_g2_g3_non_contiguous_accumulation_and_singleton_failure(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    complete(adapter, 14, "O_SYNTH_A", "A_SYNTH_A")

    first = reconcile_all_allocated(adapter)
    assert first.expected_positions == {14}
    assert first.allocated_positions == {14}
    assert first.reconciliation.ready

    complete(adapter, 43, "O_SYNTH_B", "A_SYNTH_B")
    singleton = reconcile(adapter.journal.root, expected_positions={43})
    assert not singleton.ready

    cumulative = reconcile_all_allocated(adapter)
    assert cumulative.expected_positions == {14, 43}
    assert cumulative.allocated_positions == {14, 43}
    assert cumulative.reconciliation.ready


def test_allocated_position_derivation_reads_authoritative_events(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    adapter.allocate(payload(43, "O_B"))
    adapter.allocate(payload(7, "O_A"))

    assert derive_allocated_positions(adapter.journal.root) == {7, 43}


def test_g4_third_non_contiguous_observation_accumulates(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    for pos in (14, 43, 7):
        complete(adapter, pos, f"O_{pos}", f"A_{pos}")

    result = reconcile_all_allocated(adapter)
    assert result.expected_positions == {7, 14, 43}
    assert result.reconciliation.ready


def test_g5_incomplete_current_observation_refuses_readiness(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    complete(adapter, 14, "O_A", "A_A")
    complete(adapter, 43, "O_B", "A_B")
    adapter.allocate(payload(7, "O_C"))
    adapter.bind("O_C", "A_C", "launch")

    result = reconcile_all_allocated(adapter)
    assert result.expected_positions == {7, 14, 43}
    assert not result.reconciliation.ready
    assert result.reconciliation.incomplete_chains >= 1


def test_g6_hash_mismatch_refuses_readiness(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    complete(adapter, 14, "O_A", "A_A")
    capture = adapter.journal.root / "O_A" / "03-response-captured.json"
    data = json.loads(capture.read_text())
    data["raw_response_sha256"] = "0" * 64
    capture.write_text(json.dumps(data, sort_keys=True) + "\n")

    result = reconcile_all_allocated(adapter)
    assert not result.reconciliation.ready
    assert result.reconciliation.hash_mismatches == 1


def test_g7_binding_conflict_refuses_readiness(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    complete(adapter, 14, "O_A", "A_SHARED")
    complete(adapter, 43, "O_B", "A_SHARED")

    result = reconcile_all_allocated(adapter)
    assert not result.reconciliation.ready
    assert result.reconciliation.conflicting_bindings == 1


def test_g8_missing_event_refuses_readiness(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    complete(adapter, 14, "O_A", "A_A")
    (adapter.journal.root / "O_A" / "04-complete.json").unlink()

    result = reconcile_all_allocated(adapter)
    assert not result.reconciliation.ready
    assert result.reconciliation.incomplete_chains == 1


def test_g9_malformed_allocation_refuses_readiness(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    complete(adapter, 14, "O_A", "A_A")
    malformed = adapter.journal.root / "O_MALFORMED"
    malformed.mkdir()
    (malformed / "01-allocated.json").write_text(
        json.dumps({"opaque_observation_id": "O_MALFORMED"}) + "\n"
    )

    result = reconcile_all_allocated(adapter)
    assert result.expected_positions == {14}
    assert not result.reconciliation.ready
    assert result.malformed_allocations == 1


def test_g10_randomized_78_observations_pass_incrementally(tmp_path):
    adapter = RuntimeAdapter(Journal(tmp_path / "transport"))
    positions = list(range(1, 79))
    random.Random(20260830).shuffle(positions)

    checks = []
    for index, pos in enumerate(positions, start=1):
        complete(adapter, pos, f"O_{index:03}", f"A_{index:03}")
        result = reconcile_all_allocated(adapter)
        checks.append(result)
        assert result.expected_positions == set(positions[:index])
        assert result.allocated_positions == set(positions[:index])
        assert result.reconciliation.ready
        assert result.reconciliation.complete_chains == index
        assert result.reconciliation.unique_opaque_ids == index
        assert result.reconciliation.unique_agent_ids == index
        assert result.reconciliation.hash_mismatches == 0
        assert result.reconciliation.incomplete_chains == 0
        assert result.reconciliation.conflicting_bindings == 0

    assert len(checks) == 78
    assert checks[0].expected_positions == {positions[0]}
    assert checks[-1].expected_positions == set(range(1, 79))
