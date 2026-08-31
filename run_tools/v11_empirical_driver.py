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


def _synthetic_observation(adapter: RuntimeAdapter, root: Path, schedule: Path,
                           item: dict, response: str) -> dict:
    oid = item["opaque_observation_id"]
    agent = f"synthetic-agent-{item['schedule_position']}"
    adapter.allocate({"run_id": "v11-dry-run", "schedule_position": item["schedule_position"],
                      "opaque_observation_id": oid, "role": item["role"]})
    adapter.before_launch(oid)
    adapter.bind(oid, agent, datetime.now(timezone.utc).isoformat())
    adapter.before_wait(oid, agent)
    captured = adapter.capture(oid, agent, response, datetime.now(timezone.utc).isoformat(), False)
    adapter.complete(oid, agent, captured["raw_response_sha256"])
    record_worker_closed(root, oid, agent, "synthetic-close", {"ok": True})
    assert_next_launch_permitted(root)
    persist_observation_completion(schedule, oid, agent, captured["raw_response_path"],
                                   captured["raw_response_sha256"])
    return captured


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
    extractors = [extractor_result_from_raw(_synthetic_payload(i), refs, i) for i in (1, 2, 3)]
    gold = extractors[0].projection or "[]"
    base = {(probe, rep): f"B0|{probe}|{rep}" for probe in PROBES for rep in (1, 2, 3)}
    generators = [compile_generator_packet(base[(probe, rep)], probe, condition, rep,
                                            gold, extractors[rep - 1])
                  for probe in PROBES for rep in (1, 2, 3) for condition in CONDITIONS]
    role_items = {role: [item for item in observations if item["role"] == role]
                  for role in {"extractor", "generator", "extraction_evaluator", "downstream_evaluator"}}
    extractor_raw = []
    for result, item in zip(extractors, sorted(role_items["extractor"], key=lambda x: x["schedule_position"])):
        extractor_raw.append(_synthetic_observation(adapter, journal_root, schedule_path, item,
                                                    _synthetic_payload(result.repetition)))
    generator_raw = []
    for packet, item in zip(generators, sorted(role_items["generator"], key=lambda x: x["schedule_position"])):
        generator_raw.append(_synthetic_observation(adapter, journal_root, schedule_path, item,
                                                    "GENERATOR:" + packet.packet))
    extraction_eval_raw = []
    for index, item in enumerate(sorted(role_items["extraction_evaluator"], key=lambda x: x["schedule_position"])):
        extraction_eval_raw.append(_synthetic_observation(adapter, journal_root, schedule_path, item,
                                                          "EXTRACTOR-EVAL:" + extractors[index].extractor_id))
    downstream_eval_raw = []
    for packet, item in zip(generators, sorted(role_items["downstream_evaluator"], key=lambda x: x["schedule_position"])):
        downstream_eval_raw.append(_synthetic_observation(adapter, journal_root, schedule_path, item,
                                                          "DOWNSTREAM-EVAL:" + packet.packet))
    evaluator_records = []
    for captured in extractor_raw:
        evaluator_records.append(build_evaluator_packet_from_path(
            Path(captured["raw_response_path"]), "EVAL:"))
    for captured in generator_raw:
        evaluator_records.append(build_evaluator_packet_from_path(
            Path(captured["raw_response_path"]), "EVAL:"))
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
            "evaluator_packets": {"extraction": 3, "downstream": 36,
                                  "integrity_all_exact": len(evaluator_records) == 39 and
                                  all(record["exact_match"] for _, record in evaluator_records)},
            "model_calls": 0, "agent_calls": 0, "provider_calls": 0}
