"""Build generation-manifest.jsonl from schedule + raw-outputs, with hashes."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).parent
schedule = json.loads((OUT / "schedule.json").read_text())

GENERATOR_MODEL = "sonnet (claude-sonnet-5, spawned sub-agent, Agent tool)"
rows = []
for slot in schedule:
    oid = slot["opaque_run_id"]
    out_path = OUT / "raw-outputs" / f"{oid}.md"
    text = out_path.read_text(encoding="utf-8")
    output_hash = hashlib.sha256(text.encode()).hexdigest()
    rows.append(dict(
        experiment_version="global-map-architecture-value-v2",
        source_revision="3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41",
        probe_id=slot["probe_id"],
        opaque_run_id=oid,
        repetition_index=slot["repetition_index"],
        generator_backend="Agent tool (general-purpose sub-agent, run_in_background=false)",
        generator_model=GENERATOR_MODEL,
        system_prompt_id="story-decision-v1-agent-native",
        generation_prompt_hash="sha256:" + slot["packet_hash"],
        condition_packet_hash="sha256:" + slot["packet_hash"],
        sampling="not directly controllable via Agent tool (no temperature/top_p/seed parameter exposed to orchestrator) — DEVIATION, logged",
        max_output_tokens="not directly controllable via Agent tool — DEVIATION, logged",
        tool_availability="general-purpose sub-agent has full tool access by definition; isolation enforced by instruction (exactly one Read call on the frozen packet file, no other tool) — DEVIATION from 'tools: none' frozen control, logged; observed tool_uses=1 (Read only) for every one of the 45 invocations, no other tool calls occurred",
        output_hash="sha256:" + output_hash,
        output_path=f"raw-outputs/{oid}.md",
        protocol_deviation=(
            "generation backend is a spawned Agent-tool sub-agent reading a frozen packet file, "
            "not a direct provider API call with explicit temperature/top_p/seed/max_tokens; "
            "sampling parameters are therefore NOT independently verifiable or controllable — "
            "logged as a material control-variable deviation from condition-specification.md Control variables"
        ),
    ))

(OUT / "generation-manifest.jsonl").write_text(
    "\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n", encoding="utf-8"
)
manifest_hash = hashlib.sha256((OUT / "generation-manifest.jsonl").read_bytes()).hexdigest()
print("rows:", len(rows))
print("generation-manifest hash:", manifest_hash)
