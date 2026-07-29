# Cartographer Evaluation Replay Harness Verification

## Repository

- Previous local main: `08105e7672dcf50614b1a9255eff11e1b49c258f`
- Synchronized baseline: `8e3985f961099c88d145dd07f9a72109329ca266`
- Branch: `feat/cartographer-evaluation-replay-v1`
- Implementation SHA: `94f21dd2184ad6866b53f183bc7b77cf10a129e1`
- Working tree: only the two intentionally uncommitted draft documents
- Draft evaluation SHA-256: `D9849D6776D01833573E84CE9A8C05EA7FB4B08CC4400AE75360C7A0C1A7019B`
- Draft specification SHA-256: `9706785245F3E2A3B4DA0DBEF3E916B0BFED00A03DF8CFFF2476B7382A12CEE4`

## Upstream synchronization

Origin advanced from `08105e7` with the required-elements diagnostics slice (`3769f61`, `8e3985f`). It changed only Series diagnostic handlers, advisory validation, and required-elements tests. It did not change `LLMRequest`, `LLMResponse`, `LLMClient`, `FakeClient`, `RetryingClient`, `build_client()`, `compile_outline()`, `PlanningCall`, Cartographer rendering/output models, parser behavior, package metadata, or evaluation infrastructure. The approved replay architecture remained valid. No conflicts occurred.

## Architecture

The live path remains `compile_outline()` → `PlanningCall.for_chapter()` → `render_cartographer_prompt()` → `LLMRequest` → `LLMClient.complete()` → YAML parser → `CartographerOutline.model_validate()`.

V1 adds `CartographerCaptureV1`, `CartographerEvaluationPairV1`, `CartographerReviewRecordV1`, canonical hashing, JSON loading/writing, and `ReplayLLMClient`. Replay returns the stored raw response through `LLMClient`; it does not contact a provider, retry, sleep, or use the provider factory. `compile_outline()` and its parser/validator path are reused unchanged.

## Canonicalization and integrity

- UTF-8 JSON; lexicographically sorted keys; compact separators; no insignificant whitespace.
- JSON-native null/boolean values and runtime JSON float encoding; no manual rounding.
- Prompt hash: canonical object containing exactly `system_prompt` and `user_prompt`.
- PlanningCall hash: canonical serialized PlanningCall payload.
- Raw-response hash: canonical object containing `raw_text`.
- Parsed-output hash: canonical parsed CartographerOutline mapping when present.
- Artifact hash: complete canonical capture object excluding only `integrity.artifact_hash`.
- Hashes use the `sha256:` prefix.
- Unknown additive fields are preserved with Pydantic `extra="allow"`; incompatible known fields and unsupported versions fail validation.

## Capture and security validation

The capture preserves identity, exact PlanningCall/prompt input, request settings, allowlisted provider metadata, raw response, derived parsed output, parse status, and all integrity hashes. Loading verifies every hash and never rewrites incorrect values. Structural secret-key scans reject fields matching API-key, authorization, token, secret, password, cookie, or credential patterns. No headers, environment dumps, or credentials are modeled.

## Replay

`ReplayLLMClient.complete()` compares current model, temperature, and max-token request fields, then verifies the exact system/user prompt hash. Any mismatch raises `ReplayMismatchError` with differing request paths. A matching request returns the exact captured raw text and token metadata. Replay performs no network calls and no retries. The stored parsed outline never bypasses the current parser.

## Pair validation

Pair validation requires control/treatment conditions, matching pair IDs, source Blueprint identity, authored target, source commit, provider, request settings, system prompt, and all non-profile PlanningCall fields. Only `planning_call.profile_emotional_targets` and its derived rendered section may differ. Stored prompts are re-rendered through the canonical renderer and unexpected drift is rejected with field-specific errors.

## Review records

Subjective review is separate from captures. `CartographerReviewRecordV1` distinguishes human/model reviewers, preserves blinded order and rubric version, constrains ratings to -2 through +2, and stores confidence/rationale independently.

## Compatibility

No Cartographer prompt, PlanningCall, output schema, provider client, retry wrapper, FakeClient, other planner, diagnostic, posture, package version, or release metadata changed. The evaluation module is not imported by normal production paths.

## Tests

- Candidate collection: 3,888 serial and 3,888 parallel; both exit 0.
- Replay focused tests: 11 passed, 0 failed/errors, exit 0.
- Affected suite including Cartographer, profile, release-integrity, and replay tests: passed, exit 0.
- Complete serial: 3,888 collected; 3,860 passed; 28 skipped; 0 failed; 0 errors; exit 0.
- Complete parallel: 3,888 collected; 3,860 passed; 28 skipped; 0 failed; 0 errors; exit 0.
- Expected candidate delta: +11 replay tests relative to synchronized baseline inventory.
- No markers, release-integrity tests, or production tests were weakened.

## Artifact hygiene

No real provider outputs, credentials, or raw captures were committed. JUnit, logs, and collection outputs are local-only through exact `.git/info/exclude` entries. The draft evaluation report and replay specification remain uncommitted. No tracked `.gitignore` change was made.

## Deferred work

Live recording, fixed provider/model configuration, real capture import, human review execution, scoring/aggregation, CLI, provider cache, generalized replay framework, and behavioral-usefulness conclusions remain deferred.

## Verdict

- Specification implemented: PASS
- Upstream synchronization safe: PASS
- Draft documents preserved: PASS
- Canonical hashing deterministic: PASS
- Capture integrity enforced: PASS
- Security allowlist enforced: PASS
- Replay no-network: PASS
- Replay no-retry: PASS
- Current parser path reused: PASS
- Prompt drift rejected: PASS
- Pair drift restricted: PASS
- Subjective reviews separated: PASS
- Production Cartographer unchanged: PASS
- Serial qualification clean: PASS
- Parallel qualification clean: PASS
- Artifact hygiene acceptable: PASS
- Ready for final review: YES

Behavioral usefulness is not proven by this harness implementation. The harness makes future evaluation repeatable; it does not itself provide live behavioral evidence.
