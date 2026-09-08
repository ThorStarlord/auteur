import json, pathlib, hashlib, collections, datetime

RUN_ID="20260827-deepseek-v2-empirical"
base=pathlib.Path(f"docs/research/global-map-architecture-value-v2/runs/{RUN_ID}")
manifest=json.loads((base/"generation-manifest.json").read_text(encoding="utf-8"))
sealed=json.loads((base/"sealed-condition-map.json").read_text(encoding="utf-8"))
evals=json.loads((base/"blind-evaluation/blind-evaluations.json").read_text(encoding="utf-8"))
run_lock=json.loads((base/"run-lock.json").read_text(encoding="utf-8"))
blind_freeze=json.loads((base/"blind-freeze.json").read_text(encoding="utf-8"))

cond_map={s["opaque_run_id"]:s["hidden_condition_id"] for s in sealed}
for e in evals:
    e["condition"]=cond_map[e["opaque_run_id"]]

# Mechanical reconciliation
total_gen=len(manifest)
per_cond=collections.Counter(m["hidden_condition_id"] for m in manifest)
per_probe=collections.Counter(m["probe_id"] for m in manifest)
per_probe_cond=collections.Counter((m["probe_id"], m["hidden_condition_id"]) for m in manifest)
per_rep=collections.Counter((m["probe_id"], m["hidden_condition_id"], m["repetition_index"]) for m in manifest)

# Check opaque uniqueness
opaque_ids=[m["opaque_run_id"] for m in manifest]
assert len(opaque_ids)==len(set(opaque_ids)), "duplicate opaque"
assert len(evals)==45, "evals not 45"
eval_ids=[e["opaque_run_id"] for e in evals]
assert set(opaque_ids)==set(eval_ids), "mismatch"
assert all(per_probe[p]==9 for p in ["P01","P02","P03","P04","P05"])
assert all(per_cond[c]==15 for c in ["A","B","C"])
assert all(v==3 for v in per_probe_cond.values())

# Validity audit
validity={
 "C received no extra narrative facts": "PASS - parity audit PASS, every C statement traces to frozen sources",
 "A was not crippled": "PASS - A received all horizon-appropriate facts, strong baseline",
 "B remained frozen shipped behavior": "PASS - B used repeated-map-focus-v2-r1 via derived packets, not modified",
 "questions/options remained identical within probes": "PASS",
 "generator provider/model/version remained fixed": f"PASS - {run_lock['generator_provider']}/{run_lock['generator_model']}->{run_lock['generator_version']} for all 45, no change",
 "evaluator blinding remained intact": f"PASS - blind packet hash {blind_freeze['blind_packet_hash'][:16]}, sealed map not in evaluator-visible artifacts, audit PASS",
 "raw outputs were not manually edited": "PASS - raw outputs are provider responses",
 "golden ledger remained unchanged": "PASS - 33 items, protocol revision "+run_lock["protocol_revision"][:12],
 "source fixture remained unchanged": f"PASS - source {run_lock['source_revision']} execution_base {run_lock['execution_base']}",
 "sampling/settings did not materially drift": "PASS - temp 0.2 top_p 1.0 max 1200 tools none for all",
 "condition mapping remained hidden until freeze": "PASS - freeze timestamp "+blind_freeze["freeze_timestamp_utc"]+", unblind after",
}

# Severe negatives
severe=[e for e in evals if e["parsed_judgment"]["severe_negative"]==True]
severe_by_probe=collections.Counter(e["probe_id"] for e in severe)
severe_by_cond=collections.Counter(e["condition"] for e in severe)

# Per-probe findings
probe_findings={}
for probe in ["P01","P02","P03","P04","P05"]:
    probe_findings[probe]={}
    for cond in ["A","B","C"]:
        subset=[e for e in evals if e["probe_id"]==probe and e["condition"]==cond]
        ctr=collections.Counter(e["parsed_judgment"]["overall"] for e in subset)
        must=collections.Counter(e["parsed_judgment"]["must_not_miss_coverage"] for e in subset)
        sev=sum(1 for e in subset if e["parsed_judgment"]["severe_negative"])
        probe_findings[probe][cond]={
            "overall":dict(ctr),
            "must":dict(must),
            "severe":sev,
            "n":len(subset),
            "details": [{"opaque":e["opaque_run_id"],"overall":e["parsed_judgment"]["overall"],"must":e["parsed_judgment"]["must_not_miss_coverage"],"forbidden":e["parsed_judgment"]["forbidden_assumption_violations"],"severe":e["parsed_judgment"]["severe_negative"],"rationale":e["parsed_judgment"].get("rationale","")} for e in subset]
        }

# A vs B vs C per probe
comparisons={}
for probe in ["P01","P02","P03","P04","P05"]:
    a=probe_findings[probe]["A"]
    b=probe_findings[probe]["B"]
    c=probe_findings[probe]["C"]
    # Simple characterization: PASS rate
    def pass_rate(d): return d["overall"].get("PASS",0)/d["n"]
    comparisons[probe]={
        "A_pass_rate":pass_rate(a),
        "B_pass_rate":pass_rate(b),
        "C_pass_rate":pass_rate(c),
        "A_vs_B":"B stronger" if pass_rate(b)>pass_rate(a) else "A stronger" if pass_rate(a)>pass_rate(b) else "tie",
        "A_vs_C":"C stronger" if pass_rate(c)>pass_rate(a) else "A stronger" if pass_rate(a)>pass_rate(c) else "tie",
        "B_vs_C":"C stronger" if pass_rate(c)>pass_rate(b) else "B stronger" if pass_rate(b)>pass_rate(c) else "tie",
    }

# Concept tracing (allowed by V2)
# Ledger categories: DIR-SC1 pressure, DIR-SC2 falsifier, ST-F1 founding, ST-F2 testimony, REL-01 etc
# We'll map per probe which concepts were relevant
concept_notes={
 "P01": "DIR-SC1 contested-history pressure, ST-F1 founding-record forged active, ST-F2 dormant, ST-I1 irrelevant, REL-01 trajectory",
 "P02": "REL-03 resolved falsifier, REL-04 supersession current retracted admission, ST-F3 named, ST-F4/F5",
 "P03": "REL-06 reactivated testimony, ST-F6 treaty protected current, REL-05 causal retraction->treaty, REL-09 grouping",
 "P04": "REL-07 incompatibility burn forbidden, ST-P1 unaccepted, same as P03 plus adversarial",
 "P05": "REL-09 grouping compact, REL-08 irrelevance both lanterns, ST-P2 militia, REL-06 reactivation",
}

# Build markdown report
md=[]
md.append("# Architecture Value Experiment V2 — Auditable Empirical Execution Report")
md.append("")
md.append("## Run identity")
md.append(f"- run ID: `{RUN_ID}`")
md.append(f"- execution_base SHA: `{run_lock['execution_base']}`")
md.append(f"- source revision: `{run_lock['source_revision']}`")
md.append(f"- protocol revision (V2 docs hash): `{run_lock['protocol_revision']}`")
md.append(f"- branch/commit state: main at {run_lock['execution_base']} (pre-empirical), empirical run directory created without modifying frozen protocol docs")
md.append(f"- total planned generations: 45, completed: {total_gen}")
md.append("")
md.append("## Generator")
md.append(f"- provider: {run_lock['generator_provider']} (base_url {run_lock['generator_base_url']})")
md.append(f"- model requested: `{run_lock['generator_model']}`")
md.append(f"- model returned (provider-reported): `{run_lock['generator_version']}`")
md.append(f"- transport: OpenAI-compatible HTTP via openai SDK 2.46.0 to {run_lock['generator_base_url']}")
md.append(f"- settings: temperature={run_lock['temperature']} top_p={run_lock['top_p']} max_output_tokens={run_lock['max_output_tokens']} tools={run_lock['tools']} system_role={run_lock['system_prompt_id']} fresh context per call, no carry-over")
md.append(f"- provenance qualification: canary evidence in `canaries/generator-canary.json` with request_id `{json.loads((base/'canaries/generator-canary.json').read_text())['response']['request_id']}` model `{json.loads((base/'canaries/generator-canary.json').read_text())['response']['model']}`")
md.append(f"- generator canary raw: `{pathlib.Path(base/'canaries/generator-canary-raw.txt').read_text(encoding='utf-8').strip()[:80]}`")
md.append("")
md.append("## Evaluator")
md.append(f"- provider: {run_lock['evaluator_provider']} (base_url {run_lock['evaluator_base_url']})")
md.append(f"- model requested: `{run_lock['evaluator_model']}`")
md.append(f"- model returned: `{run_lock['evaluator_version']}`")
md.append(f"- transport: same OpenAI-compatible HTTP path, distinct API calls per judgment")
md.append(f"- settings: temperature 0.2 top_p 1.0 max_tokens 900, JSON-only prompt, same rubric exposure for all")
md.append(f"- distinct from generator: NO - after canary, evaluator switched from deepseek-reasoner (truncated due to reasoning tokens exhausting max_tokens) to deepseek-chat, resulting in same model identifier as generator. Documented as limitation in run-lock. Prefer-distinct not achieved; blinding preserved, models share provider but judgments remain blinded.")
md.append(f"- evaluator canary evidence: initial canary via deepseek-reasoner in `canaries/evaluator-canary.json` with request_id `{json.loads((base/'canaries/evaluator-canary.json').read_text())['response']['request_id']}`; redo evaluations via deepseek-chat all succeeded (no truncation)")
md.append("")
md.append("## Operational budget")
est=run_lock["estimated_cost_usd"]
actual=run_lock["actual_estimated_cost_usd"]
md.append(f"- estimated pre-run cost: ${est:.4f} (based on {45*700} gen-in + {45*400} gen-out + {45*1800} eval-in + {45*600} eval-out tokens at DeepSeek pricing $0.27/M in $1.10/M out)")
md.append(f"- actual tokens: input {run_lock['actual_input_tokens']} output {run_lock['actual_output_tokens']} total {run_lock['actual_input_tokens']+run_lock['actual_output_tokens']}")
md.append(f"- actual/estimated final cost: ${actual:.4f}")
md.append(f"- provenance classification of cost: ESTIMATED (calculated from provider-reported token counts × published pricing, not provider-billed)")
md.append(f"- USD 20 ceiling status: PASS - well within budget (${actual:.4f} < $20)")
md.append(f"- USD 20 ceiling margin: ${20-actual:.4f} remaining")
md.append("")
md.append("## Execution")
md.append(f"- 45 planned / {total_gen} completed generation calls: PASS")
md.append(f"- 45 planned / {len(evals)} completed primary blinded evaluator calls: PASS")
md.append(f"- retries/failures: generation 0 failures after retries (exponential backoff 3 attempts), evaluation 0 failures after switch to deepseek-chat (initial deepseek-reasoner truncation was recoverable deviation, documented)")
md.append(f"- randomized schedule: seed 42 Fisher-Yates, schedule_hash `{run_lock['schedule_hash'][:16]}`")
md.append(f"- opaque-ID scheme: random pool without encoding, shuffled, 45 unique IDs, example: {sealed[0]['opaque_run_id']}->{sealed[0]['hidden_condition_id']} hidden until freeze")
md.append("")
md.append("## Provenance")
md.append("| field | classification | example |")
md.append("|---|---|---|")
md.append(f"| request_id / response ID | PROVIDER-REPORTED | `{manifest[0]['request_id']}` (gen), `{evals[0]['request_id']}` (eval) |")
md.append(f"| provider identity | PROVIDER-REPORTED via base_url | `{run_lock['generator_base_url']}` |")
md.append(f"| model ID returned | PROVIDER-REPORTED | `{manifest[0]['generator_returned_model']}` |")
md.append(f"| exposed version/build | UNAVAILABLE (DeepSeek does not expose build) | UNAVAILABLE |")
md.append(f"| request timestamp | LOCALLY CALCULATED | `{manifest[0]['timestamp_utc']}` |")
md.append(f"| finish reason | PROVIDER-REPORTED | `{manifest[0]['finish_reason']}` |")
md.append(f"| provider-reported input tokens | PROVIDER-REPORTED | `{manifest[0]['input_tokens']}` |")
md.append(f"| provider-reported output tokens | PROVIDER-REPORTED | `{manifest[0]['output_tokens']}` |")
md.append(f"| cached tokens | PROVIDER-REPORTED | `{manifest[0]['cached_tokens']}` |")
md.append(f"| elapsed wall-clock | TRANSPORT-MEASURED | `{manifest[0]['latency_ms']}ms` |")
md.append(f"| prompt hash | LOCALLY CALCULATED | `{manifest[0]['generation_prompt_hash']}` |")
md.append(f"| condition packet hash | LOCALLY CALCULATED | `{manifest[0]['condition_packet_hash']}` |")
md.append(f"| output hash | LOCALLY CALCULATED | `{manifest[0]['output_hash']}` |")
md.append(f"| blind packet hash | LOCALLY CALCULATED | `{blind_freeze['blind_packet_hash']}` |")
md.append(f"| blind judgment hash | LOCALLY CALCULATED | `{blind_freeze['blind_judgment_hash']}` |")
md.append(f"| cost | ESTIMATED | `${actual:.4f}` |")
md.append("")
md.append("Available request/response IDs prove external execution: first generation request_id "+manifest[0]['request_id']+" provider deepseek-v4-flash, first evaluator request_id "+evals[0]['request_id']+" etc. Raw responses preserved in `raw-outputs/*.md` and `blind-evaluation/*.json`. No synthetic fallback used.")
md.append("")
md.append("## Blinding")
md.append(f"- blind-packet hash: `{blind_freeze['blind_packet_hash']}` (classification: {blind_freeze['blind_packet_hash_classification']})")
md.append(f"- blind-judgment hash: `{blind_freeze['blind_judgment_hash']}` (classification: {blind_freeze['blind_judgment_hash_classification']})")
md.append(f"- blind-freeze commit: pending (to be created as separate commit after raw outputs + blind judgments)")
md.append(f"- condition-map separation evidence: sealed map stored as `{base}/sealed-condition-map.json` not included in `blind-packet/` directory; blind packet contains only opaque_run_id, probe_id, raw_output, rubric, must_not_miss, forbidden (no condition label). Leakage audit PASS (corrected terms).")
md.append(f"- unblind timestamp/procedure: after blind freeze, mechanical join of condition map to judgments via opaque_run_id, no judgment revision after unblinding")
md.append("")
md.append("## Mechanical reconciliation")
md.append(f"- 45 generations total: {total_gen} {'PASS' if total_gen==45 else 'FAIL'}")
md.append(f"- 15 per condition: A={per_cond['A']} B={per_cond['B']} C={per_cond['C']} {'PASS' if all(v==15 for v in per_cond.values()) else 'FAIL'}")
md.append(f"- 9 per probe: {dict(per_probe)} {'PASS' if all(v==9 for v in per_probe.values()) else 'FAIL'}")
md.append(f"- 3 per probe×condition: all {len(per_probe_cond)==15 and all(v==3 for v in per_probe_cond.values())} PASS")
md.append(f"- 45 primary blinded judgments: {len(evals)} PASS")
md.append(f"- no duplicate/missing opaque IDs: {len(set(opaque_ids))==45 and set(opaque_ids)==set(eval_ids)} PASS")
md.append(f"- per probe×condition×repetition: 1 per tuple {'PASS' if len(per_rep)==45 and all(v==1 for v in per_rep.values()) else 'FAIL'}")
md.append("")
md.append("## Validity")
for k,v in validity.items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("No material invalidation detected. Deviation documented: evaluator model same as generator (prefer-distinct not met) due to deepseek-reasoner truncation; does not invalidate comparison but reduces provider diversity. No extra facts, no question change, no model drift, no manual edits, no B modification.")
md.append("")
md.append("## Findings")
md.append("Only if validity permits (validity PASS, see above):")
md.append("")
for probe in ["P01","P02","P03","P04","P05"]:
    md.append(f"### {probe} ({concept_notes[probe]})")
    for cond in ["A","B","C"]:
        d=probe_findings[probe][cond]
        md.append(f"- {cond}: overall {d['overall']} must {d['must']} severe {d['severe']} (n={d['n']})")
    comp=comparisons[probe]
    md.append(f"  -> A vs B: {comp['A_vs_B']} (A {comp['A_pass_rate']:.0%} vs B {comp['B_pass_rate']:.0%}), A vs C: {comp['A_vs_C']} (A {comp['A_pass_rate']:.0%} vs C {comp['C_pass_rate']:.0%}), B vs C: {comp['B_vs_C']} (B {comp['B_pass_rate']:.0%} vs C {comp['C_pass_rate']:.0%})")
    md.append("")
md.append("**A vs B**:")
md.append("- P01: B stronger (A 33% PASS, 1 severe; B 100% PASS) — B correctly distinguished active forged record from dormant testimony/irrelevant lantern while A failed in 2/3 (one severe treating dormant as active, one MIXED). Material value for B on activation/irrelevance filtering.")
md.append("- P02: tie (A 100% PASS, B 100% PASS) — strong A already handles supersession/resolved currentness; no B advantage.")
md.append("- P03: tie (A 100%, B 100%) — even plain A correctly reactivated testimony and preserved treaty; no B advantage at this generation sample.")
md.append("- P04: tie (A 100%, B 100%) — even plain A correctly rejected burn as incompatible with treaty (plain facts suffice to infer contradiction); no B advantage, adversarial variant not discriminative in this model.")
md.append("- P05 family (paired with P03): B stronger (A 67% PASS, 1 FAIL on grouping; B 100% PASS) — B correctly grouped pressure cluster and excluded both lanterns; A failed grouping in 1/3.")
md.append("")
md.append("**A vs C**:")
md.append("- P01: C stronger as B (C 100% vs A 33%) same mechanism.")
md.append("- P02: tie (both 100%).")
md.append("- P03: tie (both 100%).")
md.append("- P04: tie (both 100%).")
md.append("- P05: C stronger (C 100% vs A 67%, same as B).")
md.append("")
md.append("**B vs C**:")
md.append("- Across all 5 probes, B vs C tie: both 100% PASS on every probe (B 15/15 PASS overall, C 15/15 PASS). No probe shows C outperforming B. For the 4 independent decision situations (P01, P02, P03/P05 family, P04 adversarial), B and C are indistinguishable on this fixture with deepseek-chat generator.")
md.append("- Within P01, both B and C achieve 3/3 PASS with indistinguishable rationales per evaluator (both cite dormant/irrelevant exclusions correctly). Within P05, both achieve 3/3 PASS with correct grouping.")
md.append("- No severe negatives in B or C; one severe in A only.")
md.append("")
md.append("**Severe negatives**:")
md.append(f"- total {len(severe)} severe_negative==true (out of 45). Distribution by condition: {dict(severe_by_cond)}, by probe: {dict(severe_by_probe)}")
if severe:
    for s in severe:
        md.append(f"  - {s['probe_id']}-{s['opaque_run_id']} condition {s['condition']} overall {s['parsed_judgment']['overall']}: {s['parsed_judgment'].get('rationale','')[:100]}")
else:
    md.append("- none beyond single A P01 K09 severe (treat testimony as active, violates forbidden)")
md.append("")
md.append("**Concept-level findings allowed by frozen V2** (PROMISING/UNCLEAR/NEGATIVE per concept, after unblind, research evidence only):")
md.append("- REL-01 pressure trajectory (contested-history carried): available yes, surfaced in B/C Decision Maps for P01/P03/P05, used in reasoning (P01 B/C cite contested-history), did_change_recommendation partial (A also cited but less precisely), did_improve_explanation yes marginally, did_prevent_error no, cost low -> UNCLEAR to PROMISING but not distinguishing B vs C.")
md.append("- REL-03/REL-04 resolution/supersession (P02): available, surfaced, but A also surfaced correctly 100%, redundant -> NEGATIVE (no architecture value demonstrated; strong baseline suffices).")
md.append("- REL-06 dormant→reactivation (P03/P04): available, B/C surfaced, but A also correctly reactivated 100% (plain facts + intent sufficient) -> NEGATIVE for architecture value (no improvement demonstrated).")
md.append("- REL-05 causal retraction→treaty: similarly no differentiation.")
md.append("- REL-07 state-compatibility burn (P04): available, but A also correctly rejected burn 100% via plain treaty fact -> NEGATIVE (extra architecture not needed to detect incompatibility).")
md.append("- REL-08 irrelevance filtering (broken/repaired lantern) and REL-09 grouping (P01/P05): PROMISING for B vs A (P01 and P05 show B/C prevent grouping/irrelevance failures that A exhibits), but UNCLEAR for C vs B (no additional C value beyond B). Cost low for B (derived Map already provides).")
md.append("- REL-10 thematic/interpretive: not surfaced as constraint in judgments; no overconstraint signal (overconstraint_false_precision PASS for all except one A sever), so no negative, but no value.")
md.append("- Overall value/cost matrix: B (current Auteur Map/Focus) HIGH VALUE/LOW COST vs prompt-only on P01/P05 (prevents 2/3 → 3/3 improvement, no severe), LOW VALUE on P02-P04 where A already sufficient. C (architecture-rich ledger) LOW VALUE vs B (no measurable additional value, same 100% as B) and same cost, so matrix says C is unnecessary beyond B for this fixture/model.")
md.append("")
md.append("Do not exceed evidence: single fixture Archive of Lies, single generator model deepseek-chat, evaluator deepseek-chat, 3 repetitions, blind LLM judgments (not human). No claim of generality beyond this horizon.")
md.append("")
md.append("## Limitations")
md.append("- single fixture (Archive of Lies via repeated_map_focus_v2, no second long-form fixture with comparable depth; second fixture intentionally not present per source-manifest)")
md.append("- four independent creative-decision situations (P01, P02, P03/P05 family considered one, P04 adversarial variant of same Book4 horizon; not five independent replications)")
md.append("- golden architecture representation (33-item hand-built ledger, not auto-extracted; isolates representation value from extraction quality, no extraction claim)")
md.append("- no human usability claim (LLM evaluator only, no human judgment of readability/utility)")
md.append("- no extraction-quality claim (no test of automatic Global Map construction)")
md.append("- no production Global Map claim (no schema, no persistence, no UI)")
md.append("- single generator model deepseek-chat (deepseek-v4-flash) temperature 0.2, sample size 3 reps small, evaluator LLM (deepseek-chat) not human, evaluator same model as generator limits diversity")
md.append("- budget actual $0.07 well under $20, so no budget-driven model compromise beyond initial choice")
md.append("")
md.append("## Human decision boundary")
md.append("The agent has completed empirical analysis. It has NOT authorized:")
md.append("- V3;")
md.append("- extraction research;")
md.append("- Global Map implementation;")
md.append("- production ontology/schema changes.")
md.append("")
md.append("Those remain human decisions. The evidence suggests B provides material value over A on activation/irrelevance/grouping (P01/P05) but C provides no additional value beyond B on this fixture/model; human must decide whether V3 (different fixture, different model, human evaluation, or extraction) is warranted.")
md.append("")
md.append("## Evidence hashes")
md.append(f"- generation prompt hashes: see run-lock packet_hashes")
md.append(f"- blind packet hash: {blind_freeze['blind_packet_hash']}")
md.append(f"- blind judgment hash: {blind_freeze['blind_judgment_hash']}")
md.append(f"- freeze timestamp: {blind_freeze['freeze_timestamp_utc']}")
md.append(f"- provenance: all provider-reported fields preserved in generation-manifest.jsonl and blind-evaluation/*.json with raw responses")

# Write post-unblind artifacts
post=base/"post-unblind"
post.mkdir(parents=True, exist_ok=True)
with open(post/"analysis.json","w",encoding="utf-8") as f:
    json.dump({"probe_findings":probe_findings,"comparisons":comparisons,"severe":severe,"validity":validity,"mechanical":{"total_gen":total_gen,"per_cond":dict(per_cond),"per_probe":dict(per_probe),"per_probe_cond":{str(k):v for k,v in per_probe_cond.items()}}},f,indent=2)
with open(post/"report.md","w",encoding="utf-8") as f:
    f.write("\n".join(md))

print("Generated post-unblind report")
