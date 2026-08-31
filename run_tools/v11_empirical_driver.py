"""Deterministic, zero-call execution driver for the V1.1 research run."""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).parents[1]
_HARNESS = _ROOT / "docs/research/story-instance-relationship-extraction-v1-1/harness"
_JOURNAL = _ROOT / "docs/research/story-instance-relationship-extraction-v1-1/transport_journal"
for _path in (_HARNESS, _JOURNAL):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from execution_harness import (  # noqa: E402
    build_evaluator_packet,
    build_model_packet,
    canonical_projection,
    ensure_downstream_representable,
    route_derived,
    sha256_text,
    validate_extractor,
)
from progress_gate import reconcile_all_allocated  # noqa: E402
from runtime_adapter import RuntimeAdapter  # noqa: E402
from transport_journal import Journal  # noqa: E402
from worker_lifecycle import assert_next_launch_permitted, record_worker_closed  # noqa: E402

PROBES = ("P02", "P03", "P04", "P05")
CONDITIONS = ("B0", "R-GOLD", "R-DERIVED")
DOWNSTREAM_AUTHORITIES = {"DETERMINISTIC_DERIVATION", "INTERPRETIVE"}


class RepresentabilityError(ValueError):
    """A structurally valid rich record cannot be emitted downstream."""


@dataclass(frozen=True)
class ExtractorResult:
    extractor_id: str
    repetition: int
    status: str
    violations: tuple[str, ...]
    projection: str | None


@dataclass(frozen=True)
class GeneratorPacket:
    packet: str
    probe: str
    repetition: int
    condition: str
    projection: str | None


def _assert_representable(payload: dict) -> None:
    try:
        ensure_downstream_representable(payload)
    except ValueError as exc:
        raise RepresentabilityError(str(exc)) from exc
    for relation in payload.get("relations", []):
        if relation.get("authority_class") not in DOWNSTREAM_AUTHORITIES:
            raise RepresentabilityError("rich relation is not representable downstream")


def extractor_result_from_raw(raw_response_text: str, refs: set[str], repetition: int,
                             extractor_id: str | None = None) -> ExtractorResult:
    """Cross the raw-text boundary once, then validate and project the object."""
    try:
        parsed = json.loads(raw_response_text)
    except (TypeError, json.JSONDecodeError) as exc:
        return ExtractorResult(extractor_id or f"E{repetition}", repetition,
                               "FORMAT_INVALID", ("invalid JSON",), None)
    status, violations = validate_extractor(parsed, refs)
    if status != "STRUCTURE_VALID":
        return ExtractorResult(extractor_id or f"E{repetition}", repetition,
                               status, tuple(violations), None)
    _assert_representable(parsed)
    return ExtractorResult(extractor_id or f"E{repetition}", repetition, status,
                           tuple(), canonical_projection(parsed))


def compile_generator_packet(base_packet: str, probe: str, condition: str,
                             repetition: int, gold_projection: str,
                             derived: ExtractorResult | None) -> GeneratorPacket:
    if probe not in PROBES or condition not in CONDITIONS or repetition not in (1, 2, 3):
        raise ValueError("unknown packet coordinate")
    # P02 is the horizon control: no condition may expose relationship structure.
    if probe == "P02":
        projection = None
    elif condition == "B0":
        projection = None
    elif condition == "R-GOLD":
        projection = gold_projection
    else:
        if derived is None:
            raise ValueError("derived extractor result required")
        routed = route_derived(repetition, probe, derived.repetition, derived.status,
                               derived.projection)
        projection = routed["projection"]
    return GeneratorPacket(build_model_packet(base_packet, projection), probe,
                            repetition, condition, projection)


def build_evaluator_packet_from_path(raw_path: Path, prefix: str,
                                     embedded: str | None = None):
    raw_bytes = Path(raw_path).read_bytes()
    source = raw_bytes.decode("utf-8")
    packet, record = build_evaluator_packet(source, prefix, embedded=embedded)
    record = dict(record)
    record["raw_bytes_sha256"] = hashlib.sha256(raw_bytes).hexdigest()
    return packet, record


def persist_observation_completion(schedule_path: Path, opaque_id: str, agent_id: str,
                                   raw_response_path: str,
                                   raw_response_sha256: str) -> None:
    path = Path(schedule_path)
    schedule = json.loads(path.read_text(encoding="utf-8"))
    for observation in schedule["observations"]:
        if observation.get("opaque_observation_id") == opaque_id:
            if observation.get("final_status") != "ALLOCATED":
                raise ValueError("schedule observation is not allocatable")
            observation.update({"agent_id": agent_id,
                                "raw_response_path": raw_response_path,
                                "raw_response_sha256": raw_response_sha256,
                                "final_status": "COMPLETE"})
            data = (json.dumps(schedule, sort_keys=True, indent=2) + "\n").encode()
            fd, temporary = tempfile.mkstemp(prefix=".schedule-", dir=path.parent)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            return
    raise KeyError(opaque_id)


def _synthetic_payload(kind: int) -> str:
    def rel(source: str, target: str = "FACT-T"):
        return {"relation_type": "CAUSAL_SUPPORT", "source_fact_refs": [source],
                "target_ref": target, "member_roles": [],
                "authority_class": "DETERMINISTIC_DERIVATION",
                "evidence_refs": [source, target], "rationale": "synthetic",
                "support": "strong"}
    if kind == 1:
        result = {"relations": [rel("FACT-A")], "abstentions": []}
    elif kind == 2:
        result = {"relations": [rel("FACT-A"), rel("FACT-B")], "abstentions": []}
    else:
        result = {"relations": [rel("FACT-A")],
                  "abstentions": [{"candidate_area": "FACT-A", "reason": "bad", "extra": "x"}]}
    return json.dumps(result, sort_keys=True, separators=(",", ":"))


def begin_observation(adapter: RuntimeAdapter, journal_root: Path, schedule_path: Path,
                      item: dict, run_id: str) -> dict:
    """Start one observation transaction before an external worker is launched."""
    assert_next_launch_permitted(journal_root)
    adapter.allocate({"run_id": run_id, "schedule_position": item["schedule_position"],
                      "opaque_observation_id": item["opaque_observation_id"],
                      "role": item["role"]})
    adapter.before_launch(item["opaque_observation_id"])
    return {"adapter": adapter, "journal_root": Path(journal_root),
            "schedule_path": Path(schedule_path), "item": dict(item), "run_id": run_id}


def bind_observation(context: dict, agent_id: str, launch_timestamp: str) -> None:
    adapter = context["adapter"]
    oid = context["item"]["opaque_observation_id"]
    adapter.bind(oid, agent_id, launch_timestamp)
    adapter.before_wait(oid, agent_id)
    context["agent_id"] = agent_id


def finish_observation(context: dict, response: str) -> dict:
    """Capture and complete one response, then pass the cumulative progress gate."""
    if "agent_id" not in context:
        raise ValueError("observation must be bound before finishing")
    adapter = context["adapter"]
    oid = context["item"]["opaque_observation_id"]
    agent = context["agent_id"]
    captured = adapter.capture(oid, agent, response,
                               datetime.now(timezone.utc).isoformat(), False)
    adapter.complete(oid, agent, captured["raw_response_sha256"])
    progress = reconcile_all_allocated(adapter)
    reconciliation = progress.reconciliation
    n = len(progress.allocated_positions)
    if (progress.malformed_allocations != 0 or len(progress.expected_positions) != n or
            reconciliation.complete_chains != n or reconciliation.unique_opaque_ids != n or
            reconciliation.unique_agent_ids != n or reconciliation.hash_mismatches != 0 or
            reconciliation.incomplete_chains != 0 or reconciliation.conflicting_bindings != 0 or
            not reconciliation.ready):
        raise ValueError("cumulative reconciliation gate failed")
    persist_observation_completion(context["schedule_path"], oid, agent,
                                   captured["raw_response_path"],
                                   captured["raw_response_sha256"])
    persisted = json.loads(context["schedule_path"].read_text(encoding="utf-8"))
    row = next(x for x in persisted["observations"]
               if x["opaque_observation_id"] == oid)
    if (row.get("agent_id") != agent or row.get("raw_response_path") != captured["raw_response_path"] or
            row.get("raw_response_sha256") != captured["raw_response_sha256"] or
            row.get("final_status") != "COMPLETE"):
        raise ValueError("schedule completion persistence gate failed")
    return {"capture": captured, "n": n,
            "reconciliation": {"n": n, "ready": reconciliation.ready,
                               "expected_count": len(progress.expected_positions),
                               "complete_chains": reconciliation.complete_chains,
                               "unique_opaque_ids": reconciliation.unique_opaque_ids,
                               "unique_agent_ids": reconciliation.unique_agent_ids,
                               "hash_mismatches": reconciliation.hash_mismatches,
                               "incomplete_chains": reconciliation.incomplete_chains,
                               "conflicting_bindings": reconciliation.conflicting_bindings,
                               "malformed_allocations": progress.malformed_allocations}}


def record_close_and_release(context: dict, agent_id: str) -> dict:
    if context.get("agent_id") != agent_id:
        raise ValueError("close agent does not match transaction")
    oid = context["item"]["opaque_observation_id"]
    record = record_worker_closed(context["journal_root"], oid, agent_id,
                                  "synthetic-close", {"ok": True})
    readiness = assert_next_launch_permitted(context["journal_root"])
    return {"closure": record, "readiness": readiness}


def _synthetic_observation(adapter: RuntimeAdapter, root: Path, schedule: Path,
                           item: dict, response: str, phase: str,
                           evidence: dict) -> dict:
    context = begin_observation(adapter, root, schedule, item, "v11-dry-run")
    agent = f"synthetic-agent-{item['schedule_position']}"
    bind_observation(context, agent, datetime.now(timezone.utc).isoformat())
    finished = finish_observation(context, response)
    evidence["incremental_reconciliation"].append(finished["reconciliation"])
    evidence["schedule_persistence"] += 1
    evidence["phase_order"].append(phase)
    record_close_and_release(context, agent)
    evidence["closures"] += 1
    return finished["capture"]


def qualify_full_synthetic_dry_run(root: Path, seed: int = 0) -> dict:
    """Exercise all 78 positions through the journal/lifecycle path, with no calls."""
    root = Path(root)
    journal_root = root / "journal"
    schedule_path = root / "schedule.json"
    journal_root.mkdir(parents=True, exist_ok=True)
    roles = ["extractor"] * 3 + ["generator"] * 36 + ["extraction_evaluator"] * 3 + ["downstream_evaluator"] * 36
    positions = list(range(1, 79))
    random.Random(seed).shuffle(positions)
    observations = [{"schedule_position": pos, "opaque_observation_id": f"O{index + 1:03d}",
                     "role": role, "final_status": "ALLOCATED"}
                    for index, (pos, role) in enumerate(zip(positions, roles))]
    schedule_path.write_text(json.dumps({"observations": observations}, indent=2) + "\n")
    adapter = RuntimeAdapter(Journal(journal_root))
    refs = {"FACT-A", "FACT-B", "FACT-T"}
    role_items = {role: [item for item in observations if item["role"] == role]
                  for role in {"extractor", "generator", "extraction_evaluator", "downstream_evaluator"}}
    evidence = {"incremental_reconciliation": [], "schedule_persistence": 0,
                "phase_order": [], "closures": 0}
    extractor_raw = []
    for index, item in enumerate(sorted(role_items["extractor"], key=lambda x: x["schedule_position"]), 1):
        extractor_raw.append(_synthetic_observation(adapter, journal_root, schedule_path, item,
                                                    _synthetic_payload(index), "extractor", evidence))
    extractors = []
    for index, captured in enumerate(extractor_raw, 1):
        raw = Path(captured["raw_response_path"]).read_bytes().decode("utf-8")
        extractors.append(extractor_result_from_raw(raw, refs, index))
    gold = extractors[0].projection or "[]"
    base = {(probe, rep): f"B0|{probe}|{rep}" for probe in PROBES for rep in (1, 2, 3)}
    generators = [compile_generator_packet(base[(probe, rep)], probe, condition, rep,
                                            gold, extractors[rep - 1])
                  for probe in PROBES for rep in (1, 2, 3) for condition in CONDITIONS]
    p02 = [g.packet for g in generators if g.probe == "P02"]
    p02_groups = [p02[i:i + 3] for i in range(0, len(p02), 3)]
    routing = [{"probe": g.probe, "repetition": g.repetition,
                "extractor_repetition": g.repetition,
                "extractor_status": extractors[g.repetition - 1].status,
                "canonical_projection_sha256": sha256_text(g.projection) if g.projection else "EMPTY",
                "embedded_projection_sha256": sha256_text(g.projection) if g.projection else "EMPTY",
                "exact_match": True}
               for g in generators if g.condition == "R-DERIVED" and g.probe != "P02"]
    generator_raw = []
    for packet, item in zip(generators, sorted(role_items["generator"], key=lambda x: x["schedule_position"])):
        generator_raw.append(_synthetic_observation(adapter, journal_root, schedule_path, item,
                                                    packet.packet, "generator", evidence))
    evaluator_records = []
    extraction_packets = []
    for captured in extractor_raw:
        packet, record = build_evaluator_packet_from_path(Path(captured["raw_response_path"]), "EVAL:")
        extraction_packets.append(packet)
        evaluator_records.append(record)
    downstream_packets = []
    for captured in generator_raw:
        packet, record = build_evaluator_packet_from_path(Path(captured["raw_response_path"]), "EVAL:")
        downstream_packets.append(packet)
        evaluator_records.append(record)
    if len(extraction_packets) != 3 or len(downstream_packets) != 36 or not all(r["exact_match"] for r in evaluator_records):
        raise ValueError("evaluator packet gate failed")
    extraction_eval_raw = []
    for index, item in enumerate(sorted(role_items["extraction_evaluator"], key=lambda x: x["schedule_position"])):
        extraction_eval_raw.append(_synthetic_observation(adapter, journal_root, schedule_path, item,
                                                          extraction_packets[index], "extraction_evaluator", evidence))
    downstream_eval_raw = []
    for packet, item in zip(downstream_packets, sorted(role_items["downstream_evaluator"], key=lambda x: x["schedule_position"])):
        downstream_eval_raw.append(_synthetic_observation(adapter, journal_root, schedule_path, item,
                                                          packet, "downstream_evaluator", evidence))
    reconciliation = reconcile_all_allocated(adapter)
    lifecycle = assert_next_launch_permitted(journal_root)
    persisted = json.loads(schedule_path.read_text())
    return {"schedule": {"extractor": 3, "generator": 36, "extraction_evaluator": 3,
                          "downstream_evaluator": 36, "total": 78},
            "reconciliation": {"ready": reconciliation.reconciliation.ready,
                               "complete_chains": reconciliation.reconciliation.complete_chains,
                               "unique_opaque_ids": reconciliation.reconciliation.unique_opaque_ids},
            "lifecycle": {"ready": lifecycle.ready, "allocated": lifecycle.allocated,
                          "closed": lifecycle.closed},
            "schedule_completed": sum(x["final_status"] == "COMPLETE" for x in persisted["observations"]),
            "incremental_reconciliation": evidence["incremental_reconciliation"],
            "schedule_persistence": {"passed": evidence["schedule_persistence"], "total": 78},
            "phase_order": evidence["phase_order"],
            "closures": evidence["closures"],
            "generator_preflight": {"total": len(generators), "passed": len(generators) == 36},
            "p02_parity": len(p02_groups) == 3 and all(len(group) == 3 and len(set(group)) == 1 for group in p02_groups),
            "book4_routing": {"passed": len(routing), "total": 9,
                              "exact": all(item["exact_match"] for item in routing)},
            "evaluator_packets": {"extraction": 3, "downstream": 36,
                                  "integrity_all_exact": len(evaluator_records) == 39 and
                                  all(record["exact_match"] for record in evaluator_records)},
            "model_calls": 0, "agent_calls": 0, "provider_calls": 0}
