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
    compile_generator_packet,
    extractor_result_from_raw,
    persist_observation_completion,
    qualify_full_synthetic_dry_run,
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
    assert report["model_calls"] == 0
    assert report["agent_calls"] == 0
    assert report["provider_calls"] == 0
