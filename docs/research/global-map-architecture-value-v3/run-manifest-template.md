# Global Map Architecture Value V3 — Run Manifest Template

Extends V1's `../global-map-architecture-value-v1/run-manifest-template.md` (reused by reference for fields that are unchanged) with the fields `execution-contract.md` requires. One row per generation/evaluation observation.

## Per-role configuration block (recorded once per run, per role — GENERATOR and EVALUATOR separately)

| field | example | notes |
|---|---|---|
| `role` | `GENERATOR` / `EVALUATOR` | |
| `backend` | `Claude Code Agent tool` / `OpenAI Chat Completions API` / `local vLLM` | |
| `inference_interface` | `sub-agent spawn` / `HTTP POST /v1/chat/completions` | |
| `requested_model_identifier` | `sonnet` | see execution-contract.md §2 |
| `requested_model_identifier_type` | `alias` / `exact_version_string` | |
| `resolved_model_identifier` | value or `UNAVAILABLE` | |
| `resolved_model_identifier_source` | `PROVIDER-REPORTED` / `RUNTIME-REPORTED` / `UNAVAILABLE` | |
| `resolved_model_version` | value or `UNAVAILABLE` | |
| `resolved_model_version_source` | `PROVIDER-REPORTED` / `RUNTIME-REPORTED` / `UNAVAILABLE` | |
| `documentation_derived_model_note` | e.g. "alias `sonnet` currently documented as claude-sonnet-5" | tagged `DOCUMENTATION-DERIVED`; never conflated with resolved_model_* above |
| `temperature` | value or `UNAVAILABLE` | pinned for the whole role if exposed |
| `top_p` | value or `UNAVAILABLE` | |
| `seed` | value or `UNAVAILABLE` | |
| `max_output_tokens` | value or `UNAVAILABLE` | |
| `other_sampling_controls` | value or `UNAVAILABLE` | |
| `tool_capability_policy` | e.g. "exactly one Read of one opaque packet path, no other tool" | see execution-contract.md §4 |
| `packet_delivery_mechanism` | `direct prompt` / `single Read of opaque path` / other, preregistered | |
| `startup_context_classification` | `KNOWN` / `PARTIALLY OBSERVABLE` / `UNAVAILABLE` | see execution-contract.md §3 |
| `startup_context_detail` | free text or file ref + hash | required if `KNOWN`; best-effort if `PARTIALLY OBSERVABLE` |
| `fresh_context_mechanism` | e.g. "no `to:`/resume parameter used; each invocation a new spawn" | |
| `runtime_contract_evidence_refs` | e.g. "provider docs §X: requests are stateless" or `UNAVAILABLE` | category-A evidence citations backing any runtime/backend contract claim, see execution-contract.md §8.A |
| `runtime_contract_qualification` | `PASS` / `FAIL` / `PARTIAL` / `UNAVAILABLE` | must not claim more than the cited `runtime_contract_evidence_refs` actually prove |
| `empirical_canary_evidence_refs` | e.g. canary run artifact paths/hashes, distinct-nonce test IDs | category-B evidence, see execution-contract.md §8.B |
| `empirical_canary_result` | `PASS` / `FAIL` | means only that the preregistered *observable* canary checks (nonce leakage, fresh-worker behavior, raw-output capture, packet/tool mechanics) passed — not that hidden context is absent |
| `backend_qualification_result` | `PASS` / `FAIL` | `PASS` only if every hard requirement in execution-contract.md §3 has sufficient evidence under §3 + §8 (runtime-contract evidence, or observable-canary evidence, or both, as required per the §3 strict rule). **`empirical_canary_result: PASS` alone MUST NOT imply `backend_qualification_result: PASS`.** |
| `strict_v3_conformance_status` | `ELIGIBLE` / `NOT_ELIGIBLE` | experimental invocation of this role may begin only when `ELIGIBLE`; `NOT_ELIGIBLE` means proceed only as an explicitly non-strict-conformant run (or stop), per execution-contract.md §3/§8/§11 |

## PRE-UNBLIND observation manifest (one row per generation or evaluation; committed in the pre-unblind Git commit, execution-contract.md §7)

**No `condition_id` / `hidden_condition_id` field, and no other A/B/C-encoding value, exists anywhere in this table.** Condition identity is added only in the separate POST-UNBLIND joined artifact below, per execution-contract.md §7's explicit rule (this corrects an earlier draft of this template, which listed a `hidden_condition_id` field directly in this table while simultaneously claiming pre-unblind artifacts carry no readable condition identity — an internal contradiction).

| field | example | notes |
|---|---|---|
| `experiment_version` | `global-map-architecture-value-v3` | |
| `source_revision` | `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` | unchanged from V1/V2 |
| `probe_id` | `P01` … `P05` | |
| `probe_horizon` | `Book 2` / `Book 3` / `Book 4` | |
| `opaque_observation_id` | e.g. `G7K2Q` | never condition-correlated (fixes E5); used for generator AND evaluator artifacts alike |
| `sealed_mapping_reference` | e.g. `sha256:…` of `sealed-condition-map.json`, or a per-row opaque mapping-slot reference | **a hash/commitment reference only — never the readable A/B/C value**; lets a reader later verify the revealed mapping is consistent with what existed at freeze time, without revealing anything now |
| `repetition_index` | `1` / `2` / `3` | |
| `role` | `GENERATOR` / `EVALUATOR` | links to the per-role configuration block above |
| `raw_response_path` | `raw/{opaque_observation_id}.raw.txt` | immutable, captured before any parsing |
| `raw_response_hash` | `sha256:…` | |
| `normalized_artifact_path` | `normalized/{opaque_observation_id}.json` or `N/A` | only if a derived representation was needed |
| `normalization_transformations` | list, or `NONE` | e.g. `["json_syntax_closure"]`; must never include unrecorded wording changes |
| `tool_use_audit` | e.g. `1 Read call, no other tool` | verified per invocation, see execution-contract.md §4 |
| `protocol_violation` | `none` or description | any tool use or content beyond the preregistered delivery mechanism |
| `instruction_shell_hash` | `sha256:…` | hash of the invariant generator instructions/question/output-contract text shared by all conditions for this probe. **MUST be identical across A/B/C for the same probe** — this is what actually proves parity (the field previously misnamed `generation_prompt_hash` claimed to prove parity while covering the full, necessarily-different, invocation). |
| `condition_packet_hash` | `sha256:…` | hash of the complete treatment-specific context block (the A/B/C representation itself). **EXPECTED to differ between A/B/C** for the same probe — this is the treatment, not a parity signal. |
| `full_invocation_hash` | `sha256:…`, optional but recommended | hash of the exact worker-visible invocation after combining `instruction_shell` + `condition_packet` (i.e. what the worker actually received). Expected to differ across A/B/C wherever the treatment content differs; recompute-and-compare against `instruction_shell_hash` + `condition_packet_hash` to catch accidental cross-contamination between the shell and the packet. |
| `timestamp_utc` | ISO8601 | |
| `latency` | value + provenance tag, or `UNAVAILABLE` | tag as `TRANSPORT-MEASURED` if orchestrator-timed, `PROVIDER-REPORTED` if returned by the provider, `ESTIMATED` if heuristic |
| `input_tokens` / `output_tokens` | value + provenance tag, or `UNAVAILABLE` | tag per the provenance vocabulary in execution-contract.md |
| `cost_usd` | value + provenance tag, or `UNAVAILABLE` | |
| `evaluator_id` | (evaluator rows only) | an opaque evaluator/session identifier if multiple evaluator invocations occur; never a condition-revealing value |
| `judgment_hash` | (evaluator rows only) `sha256:…` | |

## POST-UNBLIND joined artifact (one row per observation; committed only in the later, separate post-unblind commit)

Constructed by taking a copy of the frozen pre-unblind manifest above and adding exactly the columns needed for condition-labelled analysis — never by editing the pre-unblind rows in place:

| field | example | notes |
|---|---|---|
| *(all PRE-UNBLIND fields above, copied verbatim, byte-identical to the frozen pre-unblind commit)* | | |
| `condition_id` | `A` / `B` / `C` | revealed here for the first time; this is the only table in which this column exists |
| `overall` / criterion fields / etc. | (from the normalized judgment) | joined in for per-condition mechanical reconciliation |

## Pre-unblind / post-unblind commit structure (execution-contract.md §7)

```
runs/{run_id}/
  pre-unblind/            <- committed in the PRE-UNBLIND commit
    packets/               (opaque filenames only)
    raw/                    (raw generator + evaluator responses, immutable)
    normalized/             (derived judgments, transformations recorded)
    schedule.json
    schedule_hash.txt
    blind_packet_hash.txt
    judgment_hash.txt
    sealed_condition_map_hash.txt   <- hash/commitment only, NOT the mapping
  post-unblind/           <- committed in a LATER, separate commit
    sealed-condition-map.json        <- the readable mapping, revealed only here
    full-evaluations-with-conditions.jsonl
    invalidation-audit.json
    severe-negatives.json
    result.md
```

## Template invariants (unchanged principle from V1, restated for V3)

- Do not fabricate values; leave a field `UNAVAILABLE` rather than guessing.
- Never write a `DOCUMENTATION-DERIVED` value into a `PROVIDER-REPORTED`/`RUNTIME-REPORTED` field.
- If a control is `UNAVAILABLE`, that is not automatically a deviation; if a control is exposed but changes mid-run without a preregistered reason, that is an `UNCONTROLLED CHANGE` and **is** a deviation.
- No manual editing of raw responses, ever. Normalization only produces a separate derived artifact with transformations recorded (execution-contract.md §6).
- The pre-unblind commit must never contain the readable treatment mapping, and the PRE-UNBLIND observation manifest must never contain a `condition_id` field or any other A/B/C-encoding value — see execution-contract.md §7's explicit rule and this file's PRE-UNBLIND/POST-UNBLIND manifest split above.
- `instruction_shell_hash` matching across A/B/C proves parity; `condition_packet_hash` (and `full_invocation_hash`, if used) is *expected* to differ — never cite a full-invocation-level hash match as evidence of parity, since A/B/C must, by design, contain different treatment representations.
