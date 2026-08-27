# Global Map Architecture Value V1 — Run Manifest Template

One row per generation (45 rows for 3×3×5; 15 rows if deterministic). One file per experiment execution, plus sealed mapping file.

## Public run manifest (shared with evaluator as opaque IDs only)

CSV/JSON template — evaluator sees `opaque_run_id` only; `hidden_condition_id` is sealed.

| field | example | notes |
|---|---|---|
| `experiment_version` | `global-map-architecture-value-v1` | frozen |
| `source_revision` | `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` | from `source-manifest.md` |
| `source_manifest_hash` | `sha256:…` | hash of source-manifest.md + fixtures directory |
| `probe_id` | `P01` … `P05` | from `decision-probes.md` |
| `probe_horizon` | `Book 2` (P01), `Book 3` (P02/P05), `Book 4` (P03/P04) | |
| `opaque_run_id` | `X17` | randomized, blind label shown to evaluator |
| `hidden_condition_id` | `A` / `B` / `C` | **DO NOT share with evaluator** until unblinding |
| `repetition_index` | `1` / `2` / `3` | per condition per probe |
| `generator_provider` | `openai` / `anthropic` / `openrouter` | same across A/B/C |
| `generator_model` | `MODEL_TBD` (e.g., `gpt-4o-2024-08-06`) | exact version frozen |
| `system_prompt_id` | `story-decision-v1` | same across conditions |
| `generation_prompt_hash` | `sha256:…` | hash of full prompt sent (proves parity) |
| `condition_packet_hash` | `sha256:…` | hash of condition-specific context block (A plain vs B Map vs C ledger slice) |
| `sampling` | `temperature: 0.2, top_p: 1.0` | frozen |
| `seed` | `42` or `NO_SEED_SUPPORT` | if provider supports deterministic seed |
| `max_output_tokens` | `1200` | frozen |
| `tool_availability` | `none` | frozen |
| `input_tokens` | `1234` | from provider usage |
| `output_tokens` | `567` | |
| `latency_ms` | `2345` | |
| `cost_usd` | `0.012` | if available |
| `output_hash` | `sha256:…` | hash of raw output text |
| `output_path` | `runs/v1/P01-X17.md` | opaque file |
| `timestamp_utc` | `2026-08-27T…Z` | |
| `protocol_deviation` | `none` or description | any deviation from control variables |
| `evaluator_id` | `human-1` or `model:…` | after evaluation |
| `evaluator_model` | `…` (if LLM) | distinct from generator if possible |
| `judgment_hash` | `sha256:…` | hash of evaluator judgment row |

## Sealed condition mapping file (never shared pre-unblinding)

```
opaque_run_id, hidden_condition_id, probe_id, generator_model, output_hash
X17, A, P01, MODEL_TBD, sha256:…
Q04, B, P01, MODEL_TBD, sha256:…
...
```

## Output file naming

- Generation output: `runs/global-map-architecture-value-v1/{probe_id}-{opaque_run_id}.md` containing raw model output (opaque label in header, no condition hint).
- Manifest: `runs/global-map-architecture-value-v1/run-manifest.json` (or csv) with all rows.
- Sealed mapping: `runs/global-map-architecture-value-v1/_sealed-condition-map.json` (private).

## Template invariants

- Do not fabricate values; leave `MODEL_TBD` until execution; record actual provider/model/version at run time.
- If seed not supported, record `NO_SEED_SUPPORT` explicitly.
- If condition packets differ beyond planned treatment (e.g., context length truncation), record as deviation and likely invalidation.
- No manual editing of outputs before evaluation — if editing occurs, record as invalidation.
