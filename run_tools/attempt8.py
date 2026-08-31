"""Operational preparation and evidence recording for blinded V1.1 R8."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parents[1]
DOCS = ROOT / "docs/research/story-instance-relationship-extraction-v1-1"
RUN_ID = "20260831-qualified-agent-native-v11-r8"
RUN = DOCS / "runs" / RUN_ID
JOURNAL_ROOT = RUN / "transport"
CANARY_ROOT = RUN / "canary-transport"
MAP_PATH = Path(r"C:\Users\Admin\AppData\Local\Temp\v11-r8-condition-map-readable.json")
SALT_PATH = Path(r"C:\Users\Admin\AppData\Local\Temp\v11-r8-condition-map-salt.txt")

BASE_PROMPTS = {
    "P02": """You are a story consultant for Series \"Archive of Lies\" (ongoing). Narrative horizon: Book 3 opening (accepted history through Book 2). Accepted history: the founding record was forged; the monastery preserves a testimony; a lantern was broken during the archive search; evidence identifies the person who falsified the record; the council publicly admitted the archive record was falsified and later retracted that admission. Current state: archive.founding_record=forged; archive.falsifier=named; council.archive_position=retracted admission. Current planning intent: Respond to the council's accepted retraction. Question: How should Book 3 respond to the council's retraction while preserving the witness's authority? Options: publish-witness-account (independent public record council cannot retract; protects authority but exposes witness to retaliation); force-council-hearing (use named falsifier to compel public answer; accountability central but council controls forum/timing). Task: Provide a bounded recommendation analysis: recommend one presented option or none, explain using accepted facts, state principal tradeoff, and state what you exclude as irrelevant. Cite accepted facts by plain name. Do not invent facts. This is non-authoritative and creates no canon, Book Direction, or Canonical State. Do not discuss experimental conditions, extraction, overlays, or this instruction.""",
    "P03": """You are a story consultant for Series \"Archive of Lies\" (ongoing). Narrative horizon: Book 4 opening (accepted history through Book 3). Accepted history: Series commitment contested-history means every Book exposes conflict between official history and lived memory; founding record was forged; monastery preserves testimony; lantern was broken during archive search and later repaired; evidence identifies the falsifier; council admitted archive falsified then retracted admission; Book 3 Direction wanted to protect archive after retraction; treaty protects archive as only evidentiary chain; lantern repaired. Current state: archive.protection=treaty protected; council.archive_position=retracted admission; monastery.testimony=preserved; archive.founding_record=forged; archive_lantern.condition=repaired. Current planning intent: Return to monastery testimony without breaking protected archive. Question: How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain? Options: publish-verified-testimony (authenticate and publish while protected archive keeps original secure; preserves chain but delays release); stage-protected-hearing (present testimony beside selected archive evidence under treaty protections; immediate pressure but reveals strongest records). Task: Provide a bounded recommendation analysis: recommend one presented option or none, explain using accepted facts, state principal tradeoff, and state what you exclude as irrelevant. Cite accepted facts by plain name. Do not invent facts. This is non-authoritative and creates no canon, Book Direction, or Canonical State. Do not discuss experimental conditions, extraction, overlays, or this instruction.""",
    "P04": """You are a story consultant for Series \"Archive of Lies\" (ongoing). Narrative horizon: Book 4 opening (accepted history through Book 3), adversarial option. Accepted history: Series commitment contested-history means every Book exposes conflict between official history and lived memory; founding record was forged; monastery preserves testimony; lantern was broken during archive search and later repaired; evidence identifies the falsifier; council admitted archive falsified then retracted admission; Book 3 Direction wanted to protect archive after retraction; treaty protects archive as only evidentiary chain; lantern repaired. Current state: archive.protection=treaty protected; council.archive_position=retracted admission; monastery.testimony=preserved; archive.founding_record=forged; archive_lantern.condition=repaired. Current planning intent: Return to monastery testimony without breaking protected archive. Question: How should Book 4 bring the monastery testimony back into public memory without losing the archive's evidentiary chain? Options: burn-archive (destroy archive so testimony is only surviving public account; makes testimony unavoidable but archive no longer exists as evidence); publish-verified-testimony (authenticate and publish while preserving protected archive; preserves chain but delays release). Task: Provide a bounded recommendation analysis: recommend one presented option or none, explain using accepted facts, state principal tradeoff, and state what you exclude as irrelevant. Cite accepted facts by plain name. Do not invent facts. This is non-authoritative and creates no canon, Book Direction, or Canonical State. Do not discuss experimental conditions, extraction, overlays, or this instruction.""",
    "P05": """You are a story consultant for Series \"Archive of Lies\" (ongoing). Narrative horizon: Book 4 opening (accepted history through Book 3). Accepted history: Series commitment contested-history means every Book exposes conflict between official history and lived memory; founding record was forged; monastery preserves testimony; lantern was broken during archive search and later repaired; evidence identifies the falsifier; council admitted archive falsified then retracted admission; Book 3 Direction wanted to protect archive after retraction; treaty protects archive as only evidentiary chain; lantern repaired. Current state: archive.protection=treaty protected; council.archive_position=retracted admission; monastery.testimony=preserved; archive.founding_record=forged; archive_lantern.condition=repaired. Current planning intent: Return to monastery testimony without breaking protected archive. Question: How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain? Options: publish-verified-testimony (authenticate and publish while protected archive keeps original secure; preserves chain but delays release); stage-protected-hearing (present testimony beside selected archive evidence under treaty; immediate pressure but reveals strongest records). Task: Provide a bounded recommendation analysis: recommend one presented option or none, explain using accepted facts, state principal tradeoff, and state what you exclude as irrelevant. Cite accepted facts by plain name. Do not invent facts. This is non-authoritative and creates no canon, Book Direction, or Canonical State. Do not discuss experimental conditions, extraction, overlays, or this instruction.""",
}

REFS = {
    "series_direction.yaml#contested-history",
    "book_1_realization.yaml#founding-record",
    "book_1_realization.yaml#monastery-testimony",
    "book_2_realization.yaml#public-admission",
    "book_2_realization.yaml#admission-retracted",
    "book_3_direction.yaml#protect-archive-after-retraction",
    "book_3_realization.yaml#archive-protected",
    "book_3_realization.yaml#lantern-repaired",
    "deterministic-current-state",
}
EXTRACTOR_PROMPT = """You are extracting persistent, source-backed relationships from an accepted story history. Do not use current planning intent, questions, options, evaluator criteria, condition names, or any gold reference. Return exactly one JSON object, with no Markdown or prose outside it. Use only the fields and shapes specified below. You may abstain where evidence is insufficient or outside the supplied history.

Accepted source history through the shared Book-4 horizon:
- series_direction.yaml#contested-history: every Book exposes conflict between official history and lived memory.
- book_1_realization.yaml#founding-record: the founding record was forged.
- book_1_realization.yaml#monastery-testimony: the monastery preserves a testimony.
- book_2_realization.yaml#public-admission: the council publicly admitted the archive record was falsified.
- book_2_realization.yaml#admission-retracted: the council later retracted that admission.
- book_3_direction.yaml#protect-archive-after-retraction: Book 3 direction wants to protect the archive after the retraction.
- book_3_realization.yaml#archive-protected: treaty protection preserves the archive as the evidentiary chain.
- book_3_realization.yaml#lantern-repaired: the lantern was later repaired.
- deterministic-current-state: archive protection is treaty protected and the council position is retracted admission.

Output contract: top-level fields are relations and abstentions. Each relation has relation_type, source_fact_refs, target_ref, member_roles, authority_class, evidence_refs, rationale, and support. relation_type is CAUSAL_SUPPORT or PRESSURE_GROUP. CAUSAL_SUPPORT has one source and one target. PRESSURE_GROUP has two or three distinct source/member facts and one target, with one member role for each member. authority_class is ACCEPTED, DETERMINISTIC_DERIVATION, or INTERPRETIVE. support is strong, moderate, or weak. Each abstention has candidate_area and reason. Use only the source references supplied above. Emit at most two relations and at most three pressure-group members. Relationships are persistent structure, not today's relevance selection."""

GOLD = json.dumps([
    {"relation_type": "CAUSAL_SUPPORT", "source_fact_refs": ["book_2_realization.yaml#admission-retracted"], "target_ref": "book_3_realization.yaml#archive-protected", "member_roles": [], "authority_class": "INTERPRETIVE"},
    {"relation_type": "PRESSURE_GROUP", "source_fact_refs": ["book_1_realization.yaml#founding-record", "book_2_realization.yaml#admission-retracted", "book_3_realization.yaml#archive-protected"], "target_ref": "series_direction.yaml#contested-history", "member_roles": [{"fact_ref": "book_1_realization.yaml#founding-record", "role": "originating_history"}, {"fact_ref": "book_2_realization.yaml#admission-retracted", "role": "causal_pivot"}, {"fact_ref": "book_3_realization.yaml#archive-protected", "role": "current_constraint"}], "authority_class": "DETERMINISTIC_DERIVATION"},
], separators=(",", ":"))


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def oid(prefix="O"):
    return prefix + "_" + secrets.token_urlsafe(10).replace("-", "X").replace("_", "Y").upper()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def prepare():
    import random
    entries = []
    for rep in range(1, 4):
        entries.append({"id": oid(), "role": "extractor", "repetition": rep})
        for probe in ("P02", "P03", "P04", "P05"):
            for condition in ("B0", "R-GOLD", "R-DERIVED"):
                entry = {"id": oid(), "role": "generator", "probe": probe, "repetition": rep, "condition": condition}
                entries.append(entry)
                entry["evaluator_id"] = oid()
                entries.append({"id": entry["evaluator_id"], "role": "downstream_evaluator", "probe": probe, "repetition": rep, "condition": condition, "pair_generator_id": entry["id"]})
        entries.append({"id": oid(), "role": "extraction_evaluator", "repetition": rep, "condition": "EXTRACTION_EVALUATOR"})
    random.SystemRandom().shuffle(entries)
    for pos, entry in enumerate(entries, 1):
        entry["schedule_position"] = pos
        entry["launch_status"] = "ALLOCATED"
        entry["agent_id"] = None
        entry["raw_response_path"] = None
        entry["raw_response_sha256"] = None
        entry["final_status"] = "ALLOCATED"
    condition_map = [{k: v for k, v in e.items() if k in {"id", "role", "probe", "repetition", "condition", "pair_generator_id"}} for e in entries]
    MAP_PATH.write_text(json.dumps(condition_map, indent=2) + "\n")
    salt = secrets.token_hex(32)
    SALT_PATH.write_text(salt)
    commitment = hashlib.sha256((salt + json.dumps(condition_map, sort_keys=True, separators=(",", ":"))).encode()).hexdigest()
    manifest = {
        "run_id": RUN_ID,
        "protocol_sha256": hashlib.sha256((DOCS / "README.md").read_bytes()).hexdigest(),
        "harness_sha256": hashlib.sha256((DOCS / "harness/execution_harness.py").read_bytes()).hexdigest(),
        "journal_sha256": hashlib.sha256((DOCS / "transport_journal/transport_journal.py").read_bytes()).hexdigest(),
        "adapter_sha256": hashlib.sha256((DOCS / "transport_journal/runtime_adapter.py").read_bytes()).hexdigest(),
        "progress_gate_sha256": hashlib.sha256((DOCS / "transport_journal/progress_gate.py").read_bytes()).hexdigest(),
        "call_budget": 78,
        "condition_map_commitment": commitment,
        "condition_map": "SEALED_OUTSIDE_COMMITTED_EVIDENCE",
        "schedule": [{k: v for k, v in e.items() if k != "condition"} for e in entries],
    }
    write_json(RUN / "manifests/blinded-schedule.json", manifest)
    write_json(RUN / "packets/base-prompts.json", BASE_PROMPTS)
    write_json(RUN / "packets/extractor-prompt.json", {"prompt": EXTRACTOR_PROMPT, "source_refs": sorted(REFS)})
    write_json(RUN / "provenance/runtime-preflight.json", {"backend": "multi_agent_v1", "model_alias": "gpt-5.6-sol", "fork_context": False, "resolved_provider_identity": "UNAVAILABLE", "worker_instruction": "Do not call or use tools. Answer only from material contained in this prompt.", "max_empirical_concurrency": 1})
    print(json.dumps({"run": str(RUN), "entries": len(entries), "commitment": commitment, "extractors": [e["id"] for e in entries if e["role"] == "extractor"]}))


def schedule():
    return json.loads((RUN / "manifests/blinded-schedule.json").read_text())["schedule"]


def entry_for(opaque):
    for e in schedule():
        if e["id"] == opaque:
            return e
    raise SystemExit(f"unknown observation: {opaque}")


def adapter(root):
    sys.path.insert(0, str(DOCS / "transport_journal"))
    from runtime_adapter import RuntimeAdapter
    from transport_journal import Journal
    return RuntimeAdapter(Journal(root))


def do_allocate(opaque, canary=False):
    e = entry_for(opaque) if not canary else {"id": opaque, "role": "canary"}
    sys.path.insert(0, str(DOCS / "transport_journal"))
    from worker_lifecycle import assert_next_launch_permitted
    assert_next_launch_permitted(CANARY_ROOT if canary else JOURNAL_ROOT)
    a = adapter(CANARY_ROOT if canary else JOURNAL_ROOT)
    canary_position = 9001 if opaque.endswith("A") else 9002
    a.allocate({"run_id": RUN_ID, "schedule_position": e.get("schedule_position", canary_position), "opaque_observation_id": opaque, "role": e["role"], "probe": e.get("probe"), "repetition": e.get("repetition")})
    a.before_launch(opaque)


def do_bind(opaque, agent, canary=False):
    a = adapter(CANARY_ROOT if canary else JOURNAL_ROOT)
    a.bind(opaque, agent, now())
    a.before_wait(opaque, agent)


def do_complete(opaque, agent, response, canary=False):
    root = CANARY_ROOT if canary else JOURNAL_ROOT
    a = adapter(root)
    captured = a.capture(opaque, agent, response, now(), False)
    a.complete(opaque, agent, captured["raw_response_sha256"])
    sys.path.insert(0, str(DOCS / "transport_journal"))
    from progress_gate import reconcile_all_allocated
    progress = reconcile_all_allocated(a)
    if not canary:
        n = len(list((JOURNAL_ROOT).iterdir()))
        if progress.malformed_allocations != 0 or len(progress.allocated_positions) != n or not progress.reconciliation.ready or progress.reconciliation.complete_chains != n or progress.reconciliation.unique_opaque_ids != n or progress.reconciliation.unique_agent_ids != n or progress.reconciliation.hash_mismatches != 0 or progress.reconciliation.incomplete_chains != 0 or progress.reconciliation.conflicting_bindings != 0:
            raise SystemExit(json.dumps({"error": "cumulative gate failed", "n": n, "progress": progress.reconciliation.__dict__}, default=str))
        update = entry_for(opaque)
        update["agent_id"] = agent
        update["raw_response_path"] = str(root / opaque / "raw-response.txt")
        update["raw_response_sha256"] = captured["raw_response_sha256"]
        update["final_status"] = "COMPLETE"
        write_json(RUN / "manifests/blinded-schedule.json", {"run_id": RUN_ID, "protocol_sha256": json.loads((RUN / "manifests/blinded-schedule.json").read_text())["protocol_sha256"], "harness_sha256": json.loads((RUN / "manifests/blinded-schedule.json").read_text())["harness_sha256"], "journal_sha256": json.loads((RUN / "manifests/blinded-schedule.json").read_text())["journal_sha256"], "adapter_sha256": json.loads((RUN / "manifests/blinded-schedule.json").read_text())["adapter_sha256"], "progress_gate_sha256": json.loads((RUN / "manifests/blinded-schedule.json").read_text())["progress_gate_sha256"], "call_budget": 78, "condition_map_commitment": json.loads((RUN / "manifests/blinded-schedule.json").read_text())["condition_map_commitment"], "condition_map": "SEALED_OUTSIDE_COMMITTED_EVIDENCE", "schedule": schedule()})
    print(json.dumps({"opaque": opaque, "sha256": captured["raw_response_sha256"], "ready": progress.reconciliation.ready, "allocated": sorted(progress.allocated_positions), "count": len(progress.allocated_positions)}))


def prompt(opaque):
    e = entry_for(opaque)
    if e["role"] == "extractor":
        return EXTRACTOR_PROMPT
    if e["role"] == "generator":
        cmap = {x["id"]: x for x in json.loads(MAP_PATH.read_text())}
        condition = cmap[opaque]["condition"]
        base = "Do not call or use tools. Answer only from material contained in this prompt.\n" + BASE_PROMPTS[e["probe"]]
        if condition == "B0" or (e["probe"] == "P02" and condition == "R-DERIVED"):
            return base
        if condition == "R-GOLD":
            return base + "\n" + GOLD
        ext = sorted([x for x in schedule() if x["role"] == "extractor"], key=lambda x: x["repetition"])[e["repetition"] - 1]
        raw_path = JOURNAL_ROOT / ext["id"] / "raw-response.txt"
        raw = json.loads(raw_path.read_text())
        sys.path.insert(0, str(DOCS / "harness"))
        from execution_harness import canonical_projection, route_derived, validate_extractor
        status, violations = validate_extractor(raw, REFS)
        projection = canonical_projection(json.loads(raw)) if status == "STRUCTURE_VALID" else None
        route = route_derived(e["repetition"], e["probe"], e["repetition"], status, projection) if e["probe"] in {"P03", "P04", "P05"} else {"projection": None}
        return base + ("\n" + route["projection"] if route["projection"] is not None else "")
    if e["role"] == "extraction_evaluator":
        ext = sorted([x for x in schedule() if x["role"] == "extractor"], key=lambda x: x["repetition"])[e["repetition"] - 1]
        return "Do not call or use tools. Evaluate the exact extractor response below against the supplied accepted history and gold reference. Use semantic equivalence rather than exact wording. Do not reveal conditions or downstream outcomes. Return concise JSON with criteria-level judgments.\n\nACCEPTED HISTORY:\n" + EXTRACTOR_PROMPT + "\n\nGOLD REFERENCE:\n" + GOLD + "\n\nEXACT RAW EXTRACTOR RESPONSE:\n" + (JOURNAL_ROOT / ext["id"] / "raw-response.txt").read_text()
    gen = next(x for x in schedule() if x["id"] == e["pair_generator_id"])
    return "Do not call or use tools. Evaluate the exact bounded recommendation below against the accepted facts and task rubric. Do not reveal conditions, extraction outputs, gold relations, or expected winners. Return concise JSON with criterion-level judgments, severe-failure flags, and a short rationale.\n\nRUBRIC: preserve current treaty protection; connect retraction to treaty protection when relevant; group founding record/retraction/treaty consequences; reactivate monastery testimony only because current Book-4 intent makes it relevant; reject burn-archive as incompatible; do not invent facts; give a bounded recommendation and tradeoff.\n\nEXACT GENERATOR RESPONSE:\n" + (JOURNAL_ROOT / gen["id"] / "raw-response.txt").read_text()


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare")
    q = sub.add_parser("prompt"); q.add_argument("opaque")
    q = sub.add_parser("allocate"); q.add_argument("opaque"); q.add_argument("--canary", action="store_true")
    q = sub.add_parser("bind"); q.add_argument("opaque"); q.add_argument("agent"); q.add_argument("--canary", action="store_true")
    q = sub.add_parser("complete"); q.add_argument("opaque"); q.add_argument("agent"); q.add_argument("response_b64"); q.add_argument("--canary", action="store_true")
    args = p.parse_args()
    if args.cmd == "prepare": prepare()
    elif args.cmd == "prompt": print(prompt(args.opaque), end="")
    elif args.cmd == "allocate": do_allocate(args.opaque, args.canary)
    elif args.cmd == "bind": do_bind(args.opaque, args.agent, args.canary)
    elif args.cmd == "complete": do_complete(args.opaque, args.agent, base64.b64decode(args.response_b64).decode("utf-8"), args.canary)


if __name__ == "__main__": main()
