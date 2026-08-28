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
| `canary_qualification_result` | `PASS` / `FAIL` + evidence ref | must be `PASS` before any experimental invocation of this role |

## Per-observation manifest (one row per generation or evaluation)

| field | example | notes |
|---|---|---|
| `experiment_version` | `global-map-architecture-value-v3` | |
| `source_revision` | `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` | unchanged from V1/V2 |
| `probe_id` | `P01` … `P05` | |
| `probe_horizon` | `Book 2` / `Book 3` / `Book 4` | |
| `opaque_observation_id` | e.g. `G7K2Q` | never condition-correlated (fixes E5); used for generator AND evaluator artifacts alike |
| `hidden_condition_id` | `A` / `B` / `C` | sealed; **not** present in the pre-unblind commit's readable form (see execution-contract.md §7) |
| `repetition_index` | `1` / `2` / `3` | |
| `role` | `GENERATOR` / `EVALUATOR` | links to the per-role configuration block above |
| `raw_response_path` | `raw/{opaque_observation_id}.raw.txt` | immutable, captured before any parsing |
| `raw_response_hash` | `sha256:…` | |
| `normalized_artifact_path` | `normalized/{opaque_observation_id}.json` or `N/A` | only if a derived representation was needed |
| `normalization_transformations` | list, or `NONE` | e.g. `["json_syntax_closure"]`; must never include unrecorded wording changes |
| `tool_use_audit` | e.g. `1 Read call, no other tool` | verified per invocation, see execution-contract.md §4 |
| `protocol_violation` | `none` or description | any tool use or content beyond the preregistered delivery mechanism |
| `condition_packet_hash` | `sha256:…` | hash of the condition-specific context block |
| `generation_prompt_hash` | `sha256:…` | proves parity across A/B/C within a probe |
| `timestamp_utc` | ISO8601 | |
| `latency` | value + provenance tag, or `UNAVAILABLE` | tag as `TRANSPORT-MEASURED` if orchestrator-timed, `PROVIDER-REPORTED` if returned by the provider, `ESTIMATED` if heuristic |
| `input_tokens` / `output_tokens` | value + provenance tag, or `UNAVAILABLE` | tag per the provenance vocabulary in execution-contract.md |
| `cost_usd` | value + provenance tag, or `UNAVAILABLE` | |
| `evaluator_id` | (evaluator rows only) | |
| `judgment_hash` | (evaluator rows only) `sha256:…` | |

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
- The pre-unblind commit must never contain the readable treatment mapping.
