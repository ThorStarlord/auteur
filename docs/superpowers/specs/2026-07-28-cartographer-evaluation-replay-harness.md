# Cartographer Evaluation Replay Harness Specification

## Status

Proposed / awaiting approval. Specification-only; no implementation is included.

## Problem

Cartographer profile-emotional-target transport is deterministic, but behavioral influence and usefulness remain unproven. Live provider calls are expensive, nondeterministic, credential-dependent, and not replayable. Auteur needs the smallest trustworthy loop for preserving an exact request/response interaction and inspecting paired control/treatment cases without contacting a provider on every review pass.

## Proven current behavior

The live path is:

`compile_outline()` → `PlanningCall.for_chapter()` → `render_cartographer_prompt()` → `LLMRequest(system, user, temperature=0.1, max_tokens=4000)` → injected/default `LLMClient.complete()` → raw response → YAML parse → `CartographerOutline.model_validate()`.

The default client is built by `build_client()` for Anthropic or OpenAI and wrapped in `RetryingClient(max_retries=3)`. `FakeClient` exists for test-only scripted responses. The Cartographer output schema and production invocation path are unchanged by this design.

## Evaluation gap

Prompt transport can be tested locally, but transport does not establish that an external model changes outlines usefully, preserves authored authority, or avoids inventing weight semantics. A replayable raw-response artifact is needed before human comparison can be repeatable.

## Definitions

- Capture: persist one exact request/response interaction and provenance.
- Replay: return a stored raw response without network access, then use the current parser.
- Evaluation: compare paired artifacts with a versioned human rubric.
- Live generation: call an external provider to create a new capture; deferred from V1.
- Deterministic replay: the stored response is returned exactly.
- Reproducible evaluation: reviewers inspect the same retained prompt/output evidence.
- Deterministic generation: not claimed; provider generation may remain stochastic.

Replay makes evaluation repeatable; it does not make the original model generation deterministic.

## Non-goals

Do not change Cartographer prompts, PlanningCall schemas, output schemas, provider behavior, EmotionalBlueprint, diagnostics, posture, other planners, package metadata, or release files. Do not add automated emotional scoring, fulfillment claims, a generalized LLM replay framework, a public CLI, provider caching, or live-capture automation in V1.

## Existing infrastructure inventory

| Existing component | Current role | Reusable? | Gap |
| --- | --- | :---: | --- |
| `LLMRequest` | Typed system/user/model/settings request | Yes | Capture envelope needed |
| `LLMResponse` | Raw text plus token counts | Yes | Persist response metadata |
| `LLMClient` protocol | Provider boundary | Yes | Replay implementation needed |
| `RetryingClient` | Production transient retries | No for replay | Replay must never retry |
| Provider adapters/factory | Anthropic/OpenAI live calls | Deferred | Credentials and nondeterminism |
| `FakeClient` | Scripted test responses | Partly | Does not preserve live provenance |
| `compile_outline()` | Cartographer parse/validation path | Yes | Accept injected replay client already |
| Prompt renderer | Exact system/user prompt generation | Yes | Hash and retain output |
| Pydantic models | Validation and serialization | Yes | New evaluation models |
| Existing tests/fixtures | Deterministic pipeline checks | Yes | Replay and pair tests |
| CLI commands | Existing product workflows | No for V1 | Avoid premature public surface |
| Artifact conventions | YAML/JSON project artifacts | Partly | Local capture policy required |

No existing cache, redaction, or evaluation subsystem was found that should be generalized for this slice.

## Options considered

- Manual artifact import: smallest and credential-free, but manual integrity risk.
- Provider-wrapper capture: accurate but touches provider paths and secret handling.
- Proxy recording client: clean boundary, but larger than the first replay need.
- Test-only fixture capture: deterministic, but cannot represent imported live evidence.

V1 selects explicit/manual capture import plus replay. An opt-in recording client is deferred until the artifact contract is proven.

## Selected architecture

The single first implementation boundary is:

`CartographerCaptureV1` → `ReplayLLMClient` → existing `compile_outline()` parser/validator path → deterministic parsed result.

`CartographerEvaluationPairV1` verifies control/treatment equality and permits only `profile_emotional_targets` plus its expected rendered prompt section to differ. This is smaller and safer than provider recording, provider caching, a generalized replay framework, automated scoring, a public CLI, or output-schema traceability.

## Capture artifact

Use one canonical JSON document, `CartographerCaptureV1`, with `artifact_type: cartographer_evaluation_capture` and `schema_version: 1`.

Required fields:

```json
{
  "artifact_type": "cartographer_evaluation_capture",
  "schema_version": 1,
  "case_id": "emotional-target-r1",
  "pair_id": "emotional-target-r1",
  "condition": "control",
  "repetition": 0,
  "created_at": "2026-07-28T00:00:00Z",
  "source_blueprint_hash": "sha256:...",
  "source_commit": "...",
  "planning_call": {},
  "system_prompt": "...",
  "user_prompt": "...",
  "profile_emotional_targets": {},
  "authored_emotional_target": "...",
  "request": {
    "model": "...",
    "temperature": 0.1,
    "max_tokens": 4000,
    "seed": null
  },
  "provider": {
    "name": "anthropic",
    "requested_model": "...",
    "resolved_model": "...",
    "response_id": null,
    "invocation_at": "...",
    "retry_count": 0,
    "input_tokens": 0,
    "output_tokens": 0
  },
  "response": {
    "raw_text": "...",
    "parsed_outline": null,
    "parse_status": "not_attempted",
    "error": null
  },
  "integrity": {
    "prompt_hash": "sha256:...",
    "planning_call_hash": "sha256:...",
    "raw_response_hash": "sha256:...",
    "parsed_output_hash": null,
    "artifact_hash": "sha256:...",
    "redaction_status": "allowlisted"
  }
}
```

The canonical hash excludes the artifact hash field itself and uses stable JSON serialization. Exact system/user prompts and raw response text are retained. Parsed output is retained when parsing succeeds, but raw text remains authoritative evidence.

## Pair manifest

Use a separate `CartographerEvaluationPairV1` JSON/YAML manifest:

```yaml
artifact_type: cartographer_evaluation_pair
schema_version: 1
evaluation_id: cartographer-profile-emotions-v1
pair_id: emotional-target-r1
control_artifact: captures/emotional-target-r1-control.json
treatment_artifact: captures/emotional-target-r1-treatment.json
only_expected_input_difference:
  - planning_call.profile_emotional_targets
  - rendered_profile_prompt_section
rubric_version: 1
review_status: pending
```

Pair validation compares canonical PlanningCall input, authored target, Blueprint identity/hash, chapter scope, provider/model, request settings, prompt-template identity, and output-schema version. It rejects unexpected drift; it does not silently normalize differences.

## Review record

Subjective review is a separate `CartographerReviewRecordV1` artifact containing evaluation ID, pair ID, reviewer ID or pseudonym, blinded condition order, rubric version, ordinal ratings, confidence, rationale, timestamp, and reveal result. Human and model reviews have distinct reviewer types and are never merged into raw captures.

## Replay boundary

Replay occurs at the LLM client boundary. `ReplayLLMClient` implements `LLMClient`, loads one capture, verifies request identity and prompt hash, returns the stored raw `LLMResponse`, and never contacts a provider or retries. The current YAML parser and `CartographerOutline` validator then run unchanged through `compile_outline()`.

Exact current prompt/request match proceeds. A mismatch fails loudly. An explicit archival-inspection mode may display historical artifacts without claiming compatibility, and must label the result as historical replay. Parsed-output-only replay is not the default because it would bypass the parser boundary.

## Prompt identity and drift

Store the exact system prompt, user prompt, prompt hash, PlanningCall hash, source commit, and renderer/template identity. Never regenerate a prompt and pair it with an old response silently. Current replay rejects hash mismatch unless archival mode is explicitly selected.

## Schema versioning

V1 is additive-only. Unknown additive fields are ignored by readers after validating required fields; incompatible or unsupported schema versions are rejected. Existing V1 artifacts remain readable. Migrations are explicit functions, not implicit coercion. Fixtures pin exact schema versions.

## Storage policy

Raw captures are local-only by default under `.local/evaluations/cartographer/`, which is not a tracked product artifact. Selected sanitized, licensed, non-sensitive fixtures may be reviewed for tracking under `tests/fixtures/cartographer_replay/`. Manifests and review summaries may live under `docs/reviews/` after review. No external artifact store is assumed in V1.

## Security and redaction

Capture uses an allowlist. It must never store API keys, authorization headers, environment dumps, credentials, or unrelated user data. Provider name, model identifiers, response IDs, timestamps, token counts, retry counts, and cost may be stored when supplied and safe. Sensitive-content detection marks an artifact non-shareable or refuses export; it does not attempt unsafe broad redaction. Raw sensitive captures remain local-only.

## Live-provider relationship

V1 imports manually supplied captures and replays them. Live generation is not required and no live-provider command is added. A later opt-in recording client may wrap an `LLMClient`, capture request/response data after allowlist checks, and preserve retry history, but it requires a separate approved design.

## CLI decision

No CLI in V1. A Python API/loader and tests are sufficient for an internal artifact contract. Public commands such as `eval cartographer replay` are deferred until artifact formats and privacy rules stabilize.

## Backward compatibility

Production Cartographer invocation, prompts, schemas, parser, provider defaults, package metadata, and release behavior remain unchanged. Replay is injected through the existing `LLMClient` parameter. The harness is an evaluation-only consumer.

## Counterfactual acceptance tests

- valid V1 capture loads and stable hashes verify;
- missing required field and unsupported version are rejected;
- unknown additive fields follow the stated policy;
- secrets cannot appear in the allowlisted metadata;
- replay returns raw text exactly and never calls a provider or retries;
- current parser runs and preserves parse success/failure;
- prompt or request hash mismatch fails unless archival mode is explicit;
- pair validation permits only profile target and derived profile-section differences;
- authored target, Blueprint identity, model, settings, template, and schema drift fail;
- empty control mapping is valid;
- review records require rubric version and keep blinded ordering;
- production invocation and prompts remain unchanged.

## Implementation surface

| File/component | Change | Risk | Required |
| --- | --- | ---: | ---: |
| Evaluation models | Add `CartographerCaptureV1`, pair, and review models | Low | Yes |
| Evaluation loader | JSON load, canonical hashes, validation | Low | Yes |
| Replay client | Implement existing `LLMClient` boundary | Low | Yes |
| Tests/fixtures | Synthetic sanitized raw responses and no-network tests | Low | Yes |
| `.local/evaluations/cartographer/` | Local capture convention | Low | Documentation only |
| Provider adapters | Unchanged in V1 | — | No |
| CLI | Unchanged in V1 | — | No |
| Production prompts/schemas | Unchanged | — | No |

## Delivery sequence

1. Approve this specification.
2. Add V1 models and canonical hashing/validation.
3. Add replay client with no-network and no-retry guarantees.
4. Add parser-path replay tests and pair drift tests.
5. Add sanitized synthetic fixtures only if needed for tests.
6. Manually import a small real capture later under the storage/security policy.
7. Build pair manifests and conduct human review.

## Risks

Raw provider output may contain private or licensed story material. Model/provider updates may invalidate behavioral comparisons. Hashing the wrong request subset could create false replay confidence. A replay harness can prove parser and comparison repeatability but cannot prove original generation determinism or emotional fulfillment.

## Open decisions

- Exact redaction detector and export policy.
- Whether selected sanitized real captures may be committed.
- Renderer identity format and source commit policy.
- Whether a later opt-in recorder should capture provider response IDs/costs.
- Human review ownership and blinded assignment workflow.

## Recommendation

Approve one narrow first slice: `CartographerCaptureV1` → `ReplayLLMClient` → existing `compile_outline()` parser/validator path, plus `CartographerEvaluationPairV1` input-drift validation. Store exact prompts and raw responses, verify hashes, keep captures local-only by default, and keep subjective review separate. Do not add live-provider automation, scoring, traceability fields, or a CLI until this artifact contract proves trustworthy.

## Final design answers

1. Replay solves repeatable inspection of exact prompts, responses, metadata, and parser behavior without network calls.
2. Replay does not prove deterministic generation, provider quality, usefulness, or fulfillment.
3. Replay belongs at the existing LLM client boundary.
4. Store raw response text; retain parsed output as derived evidence.
5. Yes, store exact system and user prompts.
6. Use canonical prompt and request hashes plus renderer/source identity.
7. Compare canonical inputs and reject unexpected drift.
8. Yes, subjective reviews are separate artifacts.
9. Raw captures are local-only by default.
10. No CLI is required in V1.
11. V1 does not call a live provider.
12. V1 does not modify production Cartographer behavior.
13. Yes; it reuses `LLMClient` without creating a general framework.
14. Implementation is not ready; this specification requires approval first.
15. Approval, V1 models/loader/replay tests, and later safe capture import remain required before behavioral evaluation.
