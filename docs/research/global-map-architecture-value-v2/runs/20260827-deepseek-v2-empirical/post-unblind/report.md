# Architecture Value Experiment V2 — Auditable Empirical Execution Report

## Run identity
- run ID: `20260827-deepseek-v2-empirical`
- execution_base SHA: `1053154f3d23893e2ce6a4e48fa5cb16b2d459ed`
- source revision: `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41`
- protocol revision (V2 docs hash): `5f00f464a53b79586c5cfaf585719fbd5304d4d6b3c35922d3b262872400fe58`
- branch/commit state: main at 1053154f3d23893e2ce6a4e48fa5cb16b2d459ed (pre-empirical), empirical run directory created without modifying frozen protocol docs
- total planned generations: 45, completed: 45

## Generator
- provider: deepseek (base_url https://api.deepseek.com/v1)
- model requested: `deepseek-chat`
- model returned (provider-reported): `deepseek-v4-flash`
- transport: OpenAI-compatible HTTP via openai SDK 2.46.0 to https://api.deepseek.com/v1
- settings: temperature=0.2 top_p=1.0 max_output_tokens=1200 tools=none system_role=story-decision-v1 fresh context per call, no carry-over
- provenance qualification: canary evidence in `canaries/generator-canary.json` with request_id `4c40cf8d-0b77-4fea-98b7-d40c40ce8e7f` model `deepseek-v4-flash`
- generator canary raw: `CANARY_OK A lantern symbolizes hope and guidance, illuminating the path through `

## Evaluator
- provider: deepseek (base_url https://api.deepseek.com/v1)
- model requested: `deepseek-chat`
- model returned: `deepseek-v4-flash`
- transport: same OpenAI-compatible HTTP path, distinct API calls per judgment
- settings: temperature 0.2 top_p 1.0 max_tokens 900, JSON-only prompt, same rubric exposure for all
- distinct from generator: NO - after canary, evaluator switched from deepseek-reasoner (truncated due to reasoning tokens exhausting max_tokens) to deepseek-chat, resulting in same model identifier as generator. Documented as limitation in run-lock. Prefer-distinct not achieved; blinding preserved, models share provider but judgments remain blinded.
- evaluator canary evidence: initial canary via deepseek-reasoner in `canaries/evaluator-canary.json` with request_id `9beea52e-e752-4227-903a-863bf45e5b01`; redo evaluations via deepseek-chat all succeeded (no truncation)

## Operational budget
- estimated pre-run cost: $0.0799 (based on 31500 gen-in + 18000 gen-out + 81000 eval-in + 27000 eval-out tokens at DeepSeek pricing $0.27/M in $1.10/M out)
- actual tokens: input 68587 output 47924 total 116511
- actual/estimated final cost: $0.0712
- provenance classification of cost: ESTIMATED (calculated from provider-reported token counts × published pricing, not provider-billed)
- USD 20 ceiling status: PASS - well within budget ($0.0712 < $20)
- USD 20 ceiling margin: $19.9288 remaining

## Execution
- 45 planned / 45 completed generation calls: PASS
- 45 planned / 45 completed primary blinded evaluator calls: PASS
- retries/failures: generation 0 failures after retries (exponential backoff 3 attempts), evaluation 0 failures after switch to deepseek-chat (initial deepseek-reasoner truncation was recoverable deviation, documented)
- randomized schedule: seed 42 Fisher-Yates, schedule_hash `09686350336eb7a3`
- opaque-ID scheme: random pool without encoding, shuffled, 45 unique IDs, example: M22->A hidden until freeze

## Provenance
| field | classification | example |
|---|---|---|
| request_id / response ID | PROVIDER-REPORTED | `495ae2a7-1349-45d9-a3b6-70e345f64a17` (gen), `3a4c24ab-3df3-459c-98b4-393a85ae30c7` (eval) |
| provider identity | PROVIDER-REPORTED via base_url | `https://api.deepseek.com/v1` |
| model ID returned | PROVIDER-REPORTED | `deepseek-v4-flash` |
| exposed version/build | UNAVAILABLE (DeepSeek does not expose build) | UNAVAILABLE |
| request timestamp | LOCALLY CALCULATED | `2026-08-27T21:53:16.425193Z` |
| finish reason | PROVIDER-REPORTED | `stop` |
| provider-reported input tokens | PROVIDER-REPORTED | `221` |
| provider-reported output tokens | PROVIDER-REPORTED | `1073` |
| cached tokens | PROVIDER-REPORTED | `0` |
| elapsed wall-clock | TRANSPORT-MEASURED | `12129ms` |
| prompt hash | LOCALLY CALCULATED | `sha256:2de49deff56cd41ad50d1ea13ab65df733f886d48818fc4868d9d226fe1d8f1f` |
| condition packet hash | LOCALLY CALCULATED | `sha256:f17426b4b203dde3f5736cb8b4d1f4f59c5c29a602cf228961321dae17f96bc5` |
| output hash | LOCALLY CALCULATED | `sha256:7d1c1e9c4abc0e9bb9df70bbcf36b06ca71f55b12fd77ea0b6c064d0ef529b76` |
| blind packet hash | LOCALLY CALCULATED | `sha256:8a8cb0dd240bafa2e05bb5564f491ef1a452b6c3a484cf5f88eb791ea316c247` |
| blind judgment hash | LOCALLY CALCULATED | `sha256:a1507fda62e2fe744aa5e5660ae0d8ec681f4822c06ccf0f93d94f2871bcf036` |
| cost | ESTIMATED | `$0.0712` |

Available request/response IDs prove external execution: first generation request_id 495ae2a7-1349-45d9-a3b6-70e345f64a17 provider deepseek-v4-flash, first evaluator request_id 3a4c24ab-3df3-459c-98b4-393a85ae30c7 etc. Raw responses preserved in `raw-outputs/*.md` and `blind-evaluation/*.json`. No synthetic fallback used.

## Blinding
- blind-packet hash: `sha256:8a8cb0dd240bafa2e05bb5564f491ef1a452b6c3a484cf5f88eb791ea316c247` (classification: LOCALLY CALCULATED)
- blind-judgment hash: `sha256:a1507fda62e2fe744aa5e5660ae0d8ec681f4822c06ccf0f93d94f2871bcf036` (classification: LOCALLY CALCULATED)
- blind-freeze commit: pending (to be created as separate commit after raw outputs + blind judgments)
- condition-map separation evidence: sealed map stored as `docs\research\global-map-architecture-value-v2\runs\20260827-deepseek-v2-empirical/sealed-condition-map.json` not included in `blind-packet/` directory; blind packet contains only opaque_run_id, probe_id, raw_output, rubric, must_not_miss, forbidden (no condition label). Leakage audit PASS (corrected terms).
- unblind timestamp/procedure: after blind freeze, mechanical join of condition map to judgments via opaque_run_id, no judgment revision after unblinding

## Mechanical reconciliation
- 45 generations total: 45 PASS
- 15 per condition: A=15 B=15 C=15 PASS
- 9 per probe: {'P03': 9, 'P05': 9, 'P02': 9, 'P04': 9, 'P01': 9} PASS
- 3 per probe×condition: all True PASS
- 45 primary blinded judgments: 45 PASS
- no duplicate/missing opaque IDs: True PASS
- per probe×condition×repetition: 1 per tuple PASS

## Validity
- C received no extra narrative facts: PASS - parity audit PASS, every C statement traces to frozen sources
- A was not crippled: PASS - A received all horizon-appropriate facts, strong baseline
- B remained frozen shipped behavior: PASS - B used repeated-map-focus-v2-r1 via derived packets, not modified
- questions/options remained identical within probes: PASS
- generator provider/model/version remained fixed: PASS - deepseek/deepseek-chat->deepseek-v4-flash for all 45, no change
- evaluator blinding remained intact: PASS - blind packet hash sha256:8a8cb0dd2, sealed map not in evaluator-visible artifacts, audit PASS
- raw outputs were not manually edited: PASS - raw outputs are provider responses
- golden ledger remained unchanged: PASS - 33 items, protocol revision 5f00f464a53b
- source fixture remained unchanged: PASS - source 3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41 execution_base 1053154f3d23893e2ce6a4e48fa5cb16b2d459ed
- sampling/settings did not materially drift: PASS - temp 0.2 top_p 1.0 max 1200 tools none for all
- condition mapping remained hidden until freeze: PASS - freeze timestamp 2026-08-27T22:13:06.052040Z, unblind after

No material invalidation detected. Deviation documented: evaluator model same as generator (prefer-distinct not met) due to deepseek-reasoner truncation; does not invalidate comparison but reduces provider diversity. No extra facts, no question change, no model drift, no manual edits, no B modification.

## Findings
Only if validity permits (validity PASS, see above):

### P01 (DIR-SC1 contested-history pressure, ST-F1 founding-record forged active, ST-F2 dormant, ST-I1 irrelevant, REL-01 trajectory)
- A: overall {'PASS': 1, 'FAIL': 1, 'MIXED': 1} must {'PASS': 1, 'MIXED': 2} severe 1 (n=3)
- B: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
- C: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
  -> A vs B: B stronger (A 33% vs B 100%), A vs C: C stronger (A 33% vs C 100%), B vs C: tie (B 100% vs C 100%)

### P02 (REL-03 resolved falsifier, REL-04 supersession current retracted admission, ST-F3 named, ST-F4/F5)
- A: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
- B: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
- C: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
  -> A vs B: tie (A 100% vs B 100%), A vs C: tie (A 100% vs C 100%), B vs C: tie (B 100% vs C 100%)

### P03 (REL-06 reactivated testimony, ST-F6 treaty protected current, REL-05 causal retraction->treaty, REL-09 grouping)
- A: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
- B: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
- C: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
  -> A vs B: tie (A 100% vs B 100%), A vs C: tie (A 100% vs C 100%), B vs C: tie (B 100% vs C 100%)

### P04 (REL-07 incompatibility burn forbidden, ST-P1 unaccepted, same as P03 plus adversarial)
- A: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
- B: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
- C: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
  -> A vs B: tie (A 100% vs B 100%), A vs C: tie (A 100% vs C 100%), B vs C: tie (B 100% vs C 100%)

### P05 (REL-09 grouping compact, REL-08 irrelevance both lanterns, ST-P2 militia, REL-06 reactivation)
- A: overall {'PASS': 2, 'FAIL': 1} must {'PASS': 2, 'FAIL': 1} severe 0 (n=3)
- B: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
- C: overall {'PASS': 3} must {'PASS': 3} severe 0 (n=3)
  -> A vs B: B stronger (A 67% vs B 100%), A vs C: C stronger (A 67% vs C 100%), B vs C: tie (B 100% vs C 100%)

**A vs B**:
- P01: B stronger (A 33% PASS, 1 severe; B 100% PASS) — B correctly distinguished active forged record from dormant testimony/irrelevant lantern while A failed in 2/3 (one severe treating dormant as active, one MIXED). Material value for B on activation/irrelevance filtering.
- P02: tie (A 100% PASS, B 100% PASS) — strong A already handles supersession/resolved currentness; no B advantage.
- P03: tie (A 100%, B 100%) — even plain A correctly reactivated testimony and preserved treaty; no B advantage at this generation sample.
- P04: tie (A 100%, B 100%) — even plain A correctly rejected burn as incompatible with treaty (plain facts suffice to infer contradiction); no B advantage, adversarial variant not discriminative in this model.
- P05 family (paired with P03): B stronger (A 67% PASS, 1 FAIL on grouping; B 100% PASS) — B correctly grouped pressure cluster and excluded both lanterns; A failed grouping in 1/3.

**A vs C**:
- P01: C stronger as B (C 100% vs A 33%) same mechanism.
- P02: tie (both 100%).
- P03: tie (both 100%).
- P04: tie (both 100%).
- P05: C stronger (C 100% vs A 67%, same as B).

**B vs C**:
- Across all 5 probes, B vs C tie: both 100% PASS on every probe (B 15/15 PASS overall, C 15/15 PASS). No probe shows C outperforming B. For the 4 independent decision situations (P01, P02, P03/P05 family, P04 adversarial), B and C are indistinguishable on this fixture with deepseek-chat generator.
- Within P01, both B and C achieve 3/3 PASS with indistinguishable rationales per evaluator (both cite dormant/irrelevant exclusions correctly). Within P05, both achieve 3/3 PASS with correct grouping.
- No severe negatives in B or C; one severe in A only.

**Severe negatives**:
- total 1 severe_negative==true (out of 45). Distribution by condition: {'A': 1}, by probe: {'P01': 1}
  - P01-K09 condition A overall FAIL: The recommendation treats monastery testimony as active and preserved, contradicts the current state

**Concept-level findings allowed by frozen V2** (PROMISING/UNCLEAR/NEGATIVE per concept, after unblind, research evidence only):
- REL-01 pressure trajectory (contested-history carried): available yes, surfaced in B/C Decision Maps for P01/P03/P05, used in reasoning (P01 B/C cite contested-history), did_change_recommendation partial (A also cited but less precisely), did_improve_explanation yes marginally, did_prevent_error no, cost low -> UNCLEAR to PROMISING but not distinguishing B vs C.
- REL-03/REL-04 resolution/supersession (P02): available, surfaced, but A also surfaced correctly 100%, redundant -> NEGATIVE (no architecture value demonstrated; strong baseline suffices).
- REL-06 dormant→reactivation (P03/P04): available, B/C surfaced, but A also correctly reactivated 100% (plain facts + intent sufficient) -> NEGATIVE for architecture value (no improvement demonstrated).
- REL-05 causal retraction→treaty: similarly no differentiation.
- REL-07 state-compatibility burn (P04): available, but A also correctly rejected burn 100% via plain treaty fact -> NEGATIVE (extra architecture not needed to detect incompatibility).
- REL-08 irrelevance filtering (broken/repaired lantern) and REL-09 grouping (P01/P05): PROMISING for B vs A (P01 and P05 show B/C prevent grouping/irrelevance failures that A exhibits), but UNCLEAR for C vs B (no additional C value beyond B). Cost low for B (derived Map already provides).
- REL-10 thematic/interpretive: not surfaced as constraint in judgments; no overconstraint signal (overconstraint_false_precision PASS for all except one A sever), so no negative, but no value.
- Overall value/cost matrix: B (current Auteur Map/Focus) HIGH VALUE/LOW COST vs prompt-only on P01/P05 (prevents 2/3 → 3/3 improvement, no severe), LOW VALUE on P02-P04 where A already sufficient. C (architecture-rich ledger) LOW VALUE vs B (no measurable additional value, same 100% as B) and same cost, so matrix says C is unnecessary beyond B for this fixture/model.

Do not exceed evidence: single fixture Archive of Lies, single generator model deepseek-chat, evaluator deepseek-chat, 3 repetitions, blind LLM judgments (not human). No claim of generality beyond this horizon.

## Limitations
- single fixture (Archive of Lies via repeated_map_focus_v2, no second long-form fixture with comparable depth; second fixture intentionally not present per source-manifest)
- four independent creative-decision situations (P01, P02, P03/P05 family considered one, P04 adversarial variant of same Book4 horizon; not five independent replications)
- golden architecture representation (33-item hand-built ledger, not auto-extracted; isolates representation value from extraction quality, no extraction claim)
- no human usability claim (LLM evaluator only, no human judgment of readability/utility)
- no extraction-quality claim (no test of automatic Global Map construction)
- no production Global Map claim (no schema, no persistence, no UI)
- single generator model deepseek-chat (deepseek-v4-flash) temperature 0.2, sample size 3 reps small, evaluator LLM (deepseek-chat) not human, evaluator same model as generator limits diversity
- budget actual $0.07 well under $20, so no budget-driven model compromise beyond initial choice

## Human decision boundary
The agent has completed empirical analysis. It has NOT authorized:
- V3;
- extraction research;
- Global Map implementation;
- production ontology/schema changes.

Those remain human decisions. The evidence suggests B provides material value over A on activation/irrelevance/grouping (P01/P05) but C provides no additional value beyond B on this fixture/model; human must decide whether V3 (different fixture, different model, human evaluation, or extraction) is warranted.

## Evidence hashes
- generation prompt hashes: see run-lock packet_hashes
- blind packet hash: sha256:8a8cb0dd240bafa2e05bb5564f491ef1a452b6c3a484cf5f88eb791ea316c247
- blind judgment hash: sha256:a1507fda62e2fe744aa5e5660ae0d8ec681f4822c06ccf0f93d94f2871bcf036
- freeze timestamp: 2026-08-27T22:13:06.052040Z
- provenance: all provider-reported fields preserved in generation-manifest.jsonl and blind-evaluation/*.json with raw responses