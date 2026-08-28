# Global Map Architecture Value V3 — Backend-Agnostic Execution Contract

This file replaces V2 `condition-specification.md` §Control variables for V3 execution. It is the only part of the frozen V2 protocol that V3 changes. Everything substantive (research question, A/B/C, fixture, ledger, probes, rubric, repetition policy, invalidation rules, severe-negative treatment, no-single-score rule) is reused unchanged from V2 by reference — see `README.md`.

**Backend-agnostic empirical invariant (governs everything below):**

> Every empirical generation and evaluation observation must come from an explicit, fresh, isolated, auditable inference invocation. The inference backend may be API-backed, local, hosted, or agent-native, but ordinary orchestrator reasoning does not qualify as experimental output.
>
> The backend must provide enough provenance to distinguish runtime-reported, provider-reported, transport-observed, locally calculated, documentation-derived, estimated, and unavailable fields.

**Provenance category vocabulary (use consistently, never mix):**

| category | meaning |
|---|---|
| `RUNTIME-REPORTED` | Reported by the inference runtime/tool itself (e.g. a request-side parameter the orchestrator supplied and the runtime echoed, or invocation metadata the runtime returns). |
| `PROVIDER-REPORTED` | Reported by the underlying model provider in the response (e.g. a resolved model-version string, a provider request ID, provider-measured token usage). |
| `TRANSPORT-MEASURED` | Measured by the transport layer independent of provider self-report (e.g. wall-clock latency measured by the orchestrator around the call). |
| `LOCALLY CALCULATED` | Computed by the orchestrator from captured data (e.g. a SHA-256 hash of a raw response). |
| `DOCUMENTATION-DERIVED` | Known from external documentation about what an identifier/alias currently maps to, **never** treated as an execution-observed fact. |
| `ESTIMATED` | A heuristic estimate (e.g. word-count-based token estimate) explicitly flagged as non-evidentiary. |
| `UNAVAILABLE` | The backend does not expose this field at all; recorded honestly, not guessed, not silently omitted. |

A run manifest field with no evidence basis must be tagged `UNAVAILABLE`, never filled with a plausible-looking guess.

---

## 1. Inference configuration contract (per role)

Define configuration **separately for each role** — `GENERATOR` and `EVALUATOR` — since a V3 run may legitimately use different fixed backends/models for each (per V2's "prefer evaluator model distinct from generator" preference, reused unchanged).

For each role, a run must preregister and record:

- backend/runtime (e.g. "Claude Code Agent tool", "OpenAI Chat Completions API", "local vLLM server");
- inference interface (e.g. "sub-agent spawn", "HTTP POST /v1/chat/completions", "local socket");
- requested model identifier or alias;
- provider/runtime-resolved model identifier, if observable;
- exact model-version, if observable;
- temperature, if exposed;
- top_p, if exposed;
- seed, if exposed;
- max output limit, if exposed;
- other sampling controls, if exposed (e.g. frequency/presence penalty, stop sequences);
- tool/capability policy (see §4);
- packet-delivery mechanism (see §4);
- startup-context characteristics (see §3);
- fresh-context mechanism (see §3).

**Rule — pin what is exposed, disclose what is not:**

- A control the backend exposes **must** be pinned and held fixed within the relevant role for the entire run. Example: if `temperature` is exposed, one fixed value (V2's `0.2` is the preferred default if the backend supports it) must be used for every observation of that role.
- A control the backend does **not** expose is recorded as `UNAVAILABLE` and is **not automatically a protocol deviation** merely because it is absent — the frozen V2 language treating this as an automatic "deviation" is corrected here to distinguish *absence* from *drift*.
- A control must **never silently change mid-run**. Distinguish:
  - `UNAVAILABLE` — the backend never exposed it; nothing to hold fixed; no deviation.
  - `UNCONTROLLED CHANGE` — the backend exposes it, but it changed between observations of the same role without a preregistered reason. **This is a validity problem** and must be logged as a material deviation, potentially triggering the invalidation rules reused from V2 (`../global-map-architecture-value-v1/evaluation-rubric.md` §Invalidation conditions).

## 2. Model identity contract

Do not require evidence a backend cannot provide, and never convert documentation into execution provenance. Record, per role:

| field | meaning |
|---|---|
| `requested_model_identifier` | What the orchestrator asked for (e.g. `"sonnet"`, `"gpt-4o-2024-08-06"`). |
| `requested_model_identifier_type` | `alias` or `exact_version_string`. |
| `resolved_model_identifier` | What the backend/provider returned as the actual model identifier, if any. `UNAVAILABLE` if the backend never echoes this. |
| `resolved_model_identifier_source` | `PROVIDER-REPORTED` / `RUNTIME-REPORTED` / `UNAVAILABLE`. |
| `resolved_model_version` | Exact version string, if observable. `UNAVAILABLE` if not. |
| `resolved_model_version_source` | `PROVIDER-REPORTED` / `RUNTIME-REPORTED` / `UNAVAILABLE`. |

Example, valid and complete, per PR #147's actual backend:

```
requested_model_identifier: sonnet
requested_model_identifier_type: alias
resolved_model_identifier: UNAVAILABLE
resolved_model_identifier_source: UNAVAILABLE
resolved_model_version: UNAVAILABLE
resolved_model_version_source: UNAVAILABLE
```

This is a **complete and valid** manifest entry if that is genuinely all the backend exposes — it is not treated as a failure of the contract. What the contract forbids is treating `sonnet` as if it proved `claude-sonnet-5` was used: any such documentation-derived mapping must be recorded separately and tagged `DOCUMENTATION-DERIVED`, never folded into `resolved_model_identifier`/`resolved_model_version`.

Within each role:
- the requested identifier must remain fixed for the whole run;
- any observable resolved identifier must remain fixed for the whole run;
- if resolved version is unobservable, the manifest says so explicitly rather than omitting the field.

Generator and evaluator may intentionally use different fixed models — this is not a deviation, it is the preferred configuration (see §9).

## 3. Fresh-context / startup-context contract

**Do not claim** "the worker saw only the packet" unless genuinely demonstrated by a qualification canary (§12). Instead, require and separately record:

**Required (hard requirement, verified by canary before any experimental observation):**
- a fresh inference context for every observation;
- no continuation/resume from another observation;
- no inheritance of another worker's conversation;
- no inheritance of orchestrator hidden reasoning.

**Explicitly permitted, if documented (this is the fix for PR #147's E4):** standardized backend/runtime startup context, such as:
- system prompt;
- sub-agent prompt;
- repository agent instructions / `CLAUDE.md`;
- tool definitions;
- standard workspace metadata.

...provided it is:

1. **documented** — the run manifest states what startup context the backend is known or believed to supply;
2. **stable across treatment observations within a role** — the same startup context applies to every A/B/C observation for that role, so it cannot differentially advantage one condition;
3. **not treatment-specific** — it must not itself contain A/B/C-condition-shaped content;
4. **free of experimental outcomes, evaluator secrets, expected winner, condition mapping, or hidden rubric material** — a repository-level `CLAUDE.md` that happened to describe this experiment's expected result, for instance, would violate this and must be excluded from the run or the run must use a backend/workspace where it is absent.

The run manifest must classify startup context per role as one of:

| classification | meaning |
|---|---|
| `KNOWN` | The exact startup context is known and documented (e.g. captured verbatim in the manifest or referenced by file path + hash). |
| `PARTIALLY OBSERVABLE` | Some startup context is known (e.g. "system prompt X is used") but its full extent is not independently verifiable. |
| `UNAVAILABLE` | Nothing about startup context beyond the experimental packet is known or observable. |

`UNAVAILABLE` is not disqualifying on its own (PR #147's own execution used `UNAVAILABLE` for this and was still accepted as genuine empirical evidence with a disclosed limitation) — but it must be stated, not silently assumed to be "just the packet."

## 4. Packet-delivery / tool-capability contract

Replace V2's universal `tools: none` requirement, which mismatches any backend whose delivery mechanism itself requires a tool call (e.g. an agent-native "read this file" delivery). Define two layers:

**A. PACKET DELIVERY CAPABILITY** — the action(s) a worker is allowed to perform *in order to receive its experimental task*. A backend may require a delivery mechanism such as:
- direct prompt (content inlined in the invocation, no tool call needed); or
- exactly one `Read` of exactly one opaque, immutable packet path; or
- another explicitly preregistered local delivery mechanism.

That delivery action is allowed and preregistered per backend, and does not count as a protocol violation merely because V2's literal text said "tools none."

**B. REASONING / EXTERNAL-DATA CAPABILITY** — everything else. During experimental inference (generation or evaluation), workers must **not**:
- browse the repository beyond the one delivery action;
- search files;
- inspect other packets;
- read the condition map;
- access experiment results;
- access evaluator hidden material (for generator workers) or the condition mapping (for evaluator workers);
- browse the web;
- call external research tools;
- invoke any tool unrelated to the preregistered delivery mechanism.

**Verification, not assumption:** actual tool use must be audited after every invocation (e.g. PR #147's `tool_uses` count per invocation). Any tool use beyond the preregistered delivery mechanism is a **recorded protocol violation** for that observation, triggering the invalidation review reused from V2. A required packet-delivery `Read` (or equivalent) is never itself counted as a violation.

## 5. Opaque generator condition-identity contract (fixes E5)

Generator packet **file names and delegation paths/strings must be opaque** — this is the direct fix for PR #147's E5.

Never use condition-correlated names such as:

```
P01-A.txt
P01-B.txt
P01-C.txt
```

or otherwise expose an explicit A/B/C treatment label in:
- filenames;
- delegation task strings;
- worker IDs;
- observation IDs.

Instead, use opaque observation IDs assigned by the same randomization process V2 already uses for evaluator-facing labels (e.g. `G7K2Q`, `M41RX`) for **every** generator observation, not only evaluator-facing artifacts. The orchestrator may retain the sealed treatment mapping needed to construct packets and to unblind later — the generator must receive the treatment's actual *representation* (that is the treatment itself, and cannot be hidden), but must **not** receive an explicit A/B/C label or any condition-correlated metadata token (filename, ID, path segment) alongside it.

This closes E5 completely at the naming layer; §10 (raw-output immutability) and the leakage-audit step in §11 close it operationally by verifying no condition token appears anywhere in a generator-facing artifact.

## 6. Raw-output immutability contract (fixes E61)

For **every** generator and evaluator invocation:

1. capture the exact raw worker response **first**, before any parsing;
2. persist it immutably (append-only; never overwritten in place);
3. compute its hash;
4. never overwrite the raw artifact.

If parsing or normalization is required, it produces a **separate derived artifact**:

```
RAW RESPONSE  (immutable, hashed, primary)
      ↓
DERIVED NORMALIZED REPRESENTATION  (separate file, transformation recorded)
```

Every transformation applied when producing the normalized artifact must be recorded explicitly, naming the specific operation(s) performed, for example:
- JSON syntax closure (adding a missing closing quote/brace to make truncated JSON parseable);
- whitespace normalization;
- encoding repair;
- extraction of a JSON block from surrounding prose.

**Semantic paraphrase of a model response is never "normalization."** PR #147's E61 defect was exactly this: the orchestrator closed truncated JSON syntax *and* silently shortened the free-text rationale, and the shortening was not disclosed as a transformation — it was indistinguishable from a syntax fix until an independent reconciliation pass compared the two byte-for-byte. Under this contract, that comparison is instead a build-time (or transformation-time) requirement: whoever performs the normalization must diff the derived artifact against the raw artifact and record every substantive difference, or must not touch the wording at all.

If a response is malformed or truncated: preserve the raw response exactly as returned. Do **not** silently repair the only copy in place. If machine parsing requires repair (e.g. closing truncated JSON), create the derived artifact separately and record the repair as above. If substantive judgment content is ambiguous *because* of malformation (e.g. a truncated field makes the overall verdict itself unrecoverable, not just cosmetically incomplete), apply the preregistered adjudication/invalidation rule from V2's rubric rather than inventing or guessing the missing model content.

## 7. True pre-unblind Git freeze (fixes the chronology gap)

V3 must make blinding chronology **independently auditable**, not merely session-supported. Required sequence:

```
A. preregister/freeze protocol
B. create treatment packets + opaque schedule
C. generate observations
D. hash raw generation outputs
E. build opaque evaluator packets
F. leakage audit
G. perform blinded evaluations
H. persist exact raw evaluator outputs
I. derive normalized judgments (per §6, with recorded transformations)
J. hash/freeze blinded judgments
K. CREATE AN IMMUTABLE PRE-UNBLIND GIT COMMIT
L. only AFTER that commit exists, reveal/use the treatment mapping
M. derive post-unblind reconciliation/results in a LATER commit
```

**The pre-unblind Git commit (step K) must contain enough to prove the judgments were frozen before mapping revelation, but must NOT contain a readable treatment mapping.**

Preferred approach — the pre-unblind commit (step K) includes:
- blind packets;
- raw generator outputs;
- raw evaluator outputs;
- normalized blinded judgments (with recorded transformations per §6);
- hashes (schedule hash, blind-packet hash, judgment hash);
- the randomized schedule (opaque IDs only);
- a **hash or cryptographic commitment** of the sealed treatment map (e.g. `sha256(sealed-condition-map.json)`), so the eventual revealed mapping can be verified against a value that existed before it was read — but **not** the readable mapping itself.

The post-unblind commit (step M) then adds/reveals the mapping and the joined/reconciled results. Git history itself — commit K existing, with commit M strictly later and containing the mapping commit K only hashed — is then independent proof of ordering, not merely a claim resting on script control-flow and a session transcript (PR #147's limitation).

If a genuinely better cryptographically-equivalent design is available for a given backend (e.g. a signed, timestamped external commitment service), it may be substituted, but only after being explained in the run's own provenance audit before adoption — do not weaken this requirement merely for convenience.

## 8. Backend qualification canary (required before any experimental invocation)

Before any real V3 execution, the eventual run must perform a **non-experimental canary** and preregister exactly what it must test:

- worker invocation is genuinely separate from orchestrator prose;
- fresh context between workers;
- no resume/carry-over;
- raw response can be captured exactly;
- requested model identity can be recorded (§2);
- tool usage can be audited (§4);
- opaque packet delivery works (§5).

The canary must use **no experimental probe content** — no Archive of Lies material, no probe questions/options, no rubric material.

**Failure of backend qualification → STOP BEFORE EXPERIMENTAL MODEL CALLS.** No synthetic fallback. No parent-agent-prose fallback. No hard-coded templating fallback. No substring-heuristic "evaluator" fallback. This mirrors V2's own Phase 0 requirement and PR #147's canary evidence (`.../execution-provenance-audit.md` §2), generalized to any backend.

## 9. Planned first V3 execution (recorded, not executed here)

To keep the substantive treatment/probes/roles stable while changing only the execution contract, and for direct comparability with PR #147:

- **Preferred generator requested runtime alias:** `sonnet`
- **Preferred evaluator requested runtime alias:** `opus`

...provided the execution backend selected for that run still supports those identifiers at qualification time (§8).

If those aliases are unavailable when V3 execution later begins: **STOP and make an explicit human decision.** Do not silently substitute different models and still call the result "the planned comparable replication" — record the substitution, the reason, and get explicit sign-off before proceeding, since generator/evaluator model identity is itself a preregistered, fixed control (§1–2).

**This preregistration performs no execution, no model calls, and generates no A/B/C observations.**
