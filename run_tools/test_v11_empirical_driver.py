import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
HARNESS = ROOT / "docs/research/story-instance-relationship-extraction-v1-1/harness"
JOURNAL = ROOT / "docs/research/story-instance-relationship-extraction-v1-1/transport_journal"
for path in (HARNESS, JOURNAL):
    sys.path.insert(0, str(path))

from execution_harness import canonical_projection
from v11_empirical_driver import (
    RepresentabilityError,
    build_evaluator_packet_from_path,
    begin_observation,
    bind_observation,
    compile_generator_packet,
    extractor_result_from_raw,
    finish_observation,
    persist_observation_completion,
    qualify_full_synthetic_dry_run,
    record_verified_runtime_close,
    compile_extractor_packet,
)


def relation(source, target="FACT-T", authority="DETERMINISTIC_DERIVATION"):
    return {
        "relation_type": "CAUSAL_SUPPORT",
        "source_fact_refs": [source],
        "target_ref": target,
        "member_roles": [],
        "authority_class": authority,
        "evidence_refs": [source, target],
        "rationale": "synthetic",
        "support": "strong",
    }


def payload(*relations, invalid=False):
    result = {"relations": list(relations), "abstentions": []}
    if invalid:
        result["abstentions"] = [{"candidate_area": "FACT-A", "reason": "bad", "extra": "x"}]
    return result


def test_raw_response_is_parsed_once_at_boundary():
    raw = json.dumps(payload(relation("FACT-A")))
    result = extractor_result_from_raw(raw, {"FACT-A", "FACT-T"}, 1)
    assert result.status == "STRUCTURE_VALID"
    assert result.projection == canonical_projection(json.loads(raw))


def test_accepted_authority_fails_before_downstream_projection():
    with pytest.raises(RepresentabilityError):
        extractor_result_from_raw(
            json.dumps(payload(relation("FACT-A", authority="ACCEPTED"))),
            {"FACT-A", "FACT-T"}, 1,
        )


def test_p02_has_six_byte_identical_condition_packets():
    base = {"P02": {1: "B0-P02-1", 2: "B0-P02-2", 3: "B0-P02-3"}}
    gold = "[GOLD]"
    for repetition in (1, 2, 3):
        packets = [compile_generator_packet(base["P02"][repetition], "P02", c,
                                             repetition, gold, None).packet
                   for c in ("B0", "R-GOLD", "R-DERIVED")]
        assert packets[0] == packets[1] == packets[2]
        assert "GOLD" not in packets[1]


def test_book4_routes_e1_e2_e3_across_all_three_downstream_probes():
    refs = {"FACT-A", "FACT-B", "FACT-C", "FACT-T"}
    results = {
        1: extractor_result_from_raw(json.dumps(payload(relation("FACT-A"))), refs, 1),
        2: extractor_result_from_raw(json.dumps(payload(relation("FACT-A"), relation("FACT-B"))), refs, 2),
        3: extractor_result_from_raw(json.dumps(payload(relation("FACT-A"), invalid=True)), refs, 3),
    }
    for probe in ("P03", "P04", "P05"):
        for repetition in (1, 2, 3):
            result = compile_generator_packet("B0-BOOK4", probe, "R-DERIVED",
                                               repetition, "[GOLD]", results[repetition])
            if repetition == 3:
                assert result.packet == "B0-BOOK4"
            else:
                assert result.packet != "B0-BOOK4"


def test_schedule_completion_update_survives_reload(tmp_path):
    path = tmp_path / "schedule.json"
    path.write_text(json.dumps({"observations": [{
        "opaque_observation_id": "O1", "final_status": "ALLOCATED",
    }]}))
    persist_observation_completion(path, "O1", "agent-1", "raw.txt", "hash-1")
    persisted = json.loads(path.read_text())["observations"][0]
    assert persisted == {
        "opaque_observation_id": "O1", "final_status": "COMPLETE",
        "agent_id": "agent-1", "raw_response_path": "raw.txt",
        "raw_response_sha256": "hash-1",
    }


def test_evaluator_packet_uses_exact_raw_bytes(tmp_path):
    path = tmp_path / "raw.txt"
    path.write_bytes(b"exact response\n")
    packet, record = build_evaluator_packet_from_path(path, "EVAL:")
    assert packet == "EVAL:exact response\n"
    assert record["exact_match"] is True
    with pytest.raises(ValueError):
        build_evaluator_packet_from_path(path, "EVAL:", embedded="EVAL:changed")


def test_full_synthetic_dry_run_uses_all_78_positions(tmp_path):
    report = qualify_full_synthetic_dry_run(tmp_path, seed=17)
    assert report["schedule"] == {
        "extractor": 3, "generator": 36, "extraction_evaluator": 3,
        "downstream_evaluator": 36, "total": 78,
    }
    assert report["reconciliation"]["ready"] is True
    assert report["lifecycle"]["ready"] is True
    assert report["schedule_completed"] == 78
    assert report["evaluator_packets"] == {
        "extraction": 3, "downstream": 36, "integrity_all_exact": True,
    }
    assert report["extractor_packet_preflight"] == {
        "passed": True, "exact_fields": True,
    }
    assert report["model_calls"] == 0
    assert report["agent_calls"] == 0
    assert report["provider_calls"] == 0
    assert len(report["incremental_reconciliation"]) == 78
    assert all(gate["ready"] and gate["expected_count"] == gate["n"]
               for gate in report["incremental_reconciliation"])
    assert report["schedule_persistence"] == {"passed": 78, "total": 78}
    assert report["phase_order"] == ["extractor"] * 3 + ["generator"] * 36 + [
        "extraction_evaluator"] * 3 + ["downstream_evaluator"] * 36


def test_observation_transaction_owns_cumulative_gate_and_close(tmp_path):
    from runtime_adapter import RuntimeAdapter
    from transport_journal import Journal

    root = tmp_path / "journal"
    schedule = tmp_path / "schedule.json"
    schedule.write_text(json.dumps({"run_id": "run", "observations": [{
        "schedule_position": 1, "opaque_observation_id": "O1",
        "role": "extractor", "final_status": "ALLOCATED",
    }]}))
    adapter = RuntimeAdapter(Journal(root))
    item = {"schedule_position": 1, "opaque_observation_id": "O1",
            "role": "extractor"}
    context = begin_observation(adapter, root, schedule, item, "run")
    bind_observation(context, "agent-1", "now")
    finished = finish_observation(context, "response")
    assert finished["reconciliation"]["n"] == 1
    closed = record_verified_runtime_close(
        context, "agent-1", "multi_agent_v1__close_agent",
        {"status": "closed", "worker_id": "agent-1"},
    )
    assert closed["readiness"].ready is True
    persisted = json.loads((root / "O1" / "05-worker-closed.json").read_text())
    assert persisted["close_operation"] == "multi_agent_v1__close_agent"
    assert persisted["close_result"] == {"status": "closed", "worker_id": "agent-1"}


def test_live_close_rejects_missing_acknowledgement(tmp_path):
    context = _completed_context(tmp_path)
    with pytest.raises(ValueError):
        record_verified_runtime_close(context, "agent-1", "multi_agent_v1__close_agent", None)


def test_extractor_packet_has_exact_frozen_envelope_and_is_deterministic():
    packet = compile_extractor_packet("FACT-A: accepted fact", {"FACT-A"})
    assert packet == compile_extractor_packet("FACT-A: accepted fact", {"FACT-A"})
    for field in ("relations", "abstentions", "relation_type", "source_fact_refs",
                  "target_ref", "member_roles", "fact_ref", "role",
                  "authority_class", "evidence_refs", "rationale", "support",
                  "candidate_area", "reason"):
        assert field in packet
    assert "source\"" not in packet
    assert "sources\"" not in packet
    assert "candidate\"" not in packet
    assert "gold" not in packet.lower()
    assert "intent" not in packet.lower()


def test_begin_rejects_declared_run_id_mismatch_before_allocation(tmp_path):
    from runtime_adapter import RuntimeAdapter
    from transport_journal import Journal

    root = tmp_path / "journal"
    schedule = tmp_path / "schedule.json"
    schedule.write_text(json.dumps({"run_id": "run-a", "observations": []}))
    item = {"schedule_position": 1, "opaque_observation_id": "O1",
            "role": "extractor", "final_status": "ALLOCATED"}
    with pytest.raises(ValueError):
        begin_observation(RuntimeAdapter(Journal(root)), root, schedule, item, "run-b")
    assert not root.exists() or not list(root.iterdir())


def test_live_close_rejects_synthetic_operation(tmp_path):
    context = _completed_context(tmp_path)
    with pytest.raises(ValueError):
        record_verified_runtime_close(context, "agent-1", "synthetic-close", {"ok": True})


def test_live_close_rejects_wrong_agent(tmp_path):
    context = _completed_context(tmp_path)
    with pytest.raises(ValueError):
        record_verified_runtime_close(context, "wrong-agent", "multi_agent_v1__close_agent", {"ok": True})


def test_live_close_rejects_before_completion(tmp_path):
    context = _started_context(tmp_path)
    with pytest.raises(ValueError):
        record_verified_runtime_close(context, "agent-1", "multi_agent_v1__close_agent", {"ok": True})


def test_live_close_rejects_duplicate_evidence(tmp_path):
    context = _completed_context(tmp_path)
    record_verified_runtime_close(context, "agent-1", "multi_agent_v1__close_agent", {"ok": True})
    with pytest.raises(Exception):
        record_verified_runtime_close(context, "agent-1", "multi_agent_v1__close_agent", {"ok": True})


def test_next_launch_remains_blocked_until_verified_live_close(tmp_path):
    from worker_lifecycle import LifecycleError, assert_next_launch_permitted

    context = _completed_context(tmp_path)
    with pytest.raises(LifecycleError):
        assert_next_launch_permitted(context["journal_root"])
    record_verified_runtime_close(context, "agent-1", "multi_agent_v1__close_agent", {"ok": True})
    assert assert_next_launch_permitted(context["journal_root"]).ready


def _started_context(tmp_path):
    from runtime_adapter import RuntimeAdapter
    from transport_journal import Journal
    root = tmp_path / "journal"
    schedule = tmp_path / "schedule.json"
    schedule.write_text(json.dumps({"run_id": "run", "observations": [{
        "schedule_position": 1, "opaque_observation_id": "O1",
        "role": "extractor", "final_status": "ALLOCATED",
    }]}))
    adapter = RuntimeAdapter(Journal(root))
    item = {"schedule_position": 1, "opaque_observation_id": "O1", "role": "extractor"}
    context = begin_observation(adapter, root, schedule, item, "run")
    bind_observation(context, "agent-1", "now")
    return context


def _completed_context(tmp_path):
    context = _started_context(tmp_path)
    finish_observation(context, "response")
    return context
