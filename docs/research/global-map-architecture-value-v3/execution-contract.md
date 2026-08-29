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

**Do not claim** "the worker saw only the packet" unless genuinely demonstrated by the full backend-qualification evidence (§8. Backend qualification canary). Instead, require and separately record:

**Required (hard requirement, established by the complete backend-qualification evidence defined in §8, before any experimental observation):**
- a fresh inference context for every observation;
- no continuation/resume from another observation;
- no inheritance of another worker's conversation;
- no inheritance of orchestrator hidden reasoning.

These hard requirements must be established by the complete backend-qualification evidence defined in §8. Empirical canaries (§8.B) establish only observable properties of the sampled invocations — e.g. that a canary run showed no cross-nonce leakage, or that a worker's response showed no evidence of resumed context. Properties such as the absence of hidden orchestrator/runtime context are not directly observable from a canary sample alone; where they are not independently confirmed by runtime/backend contract evidence (§8.A), they remain unproven, not proven-by-canary, and this is treated per the strict startup-context qualification rule below (`UNAVAILABLE` classification, requiring either an independent runtime guarantee or qualification failure).

**Explicitly permitted, if documented (this is the fix for PR #147's E4):** standardized backend/runtime startup context, such as:
- system prompt;
- sub-agent prompt;
- repository agent instructions / `CLAUDE.md`;
- tool definitions;
- standard workspace metadata.

...provided it is:

1. **documented** — the run manifest states what startup context the backend is known or believed to supply;
2. **stable across treatment observations within a role** — the same startup context applies to every A/B/C observation for that role;
3. **not treatment-specific** — it must not itself contain A/B/C-condition-shaped content;
4. **free of experimental outcomes, evaluator secrets, expected winner, condition mapping, or hidden rubric material** — a repository-level `CLAUDE.md` that happened to describe this experiment's expected result, for instance, would violate this and must be excluded from the run or the run must use a backend/workspace where it is absent.

**Corrected framing (this document previously overclaimed on this point):** startup context that is stable across treatments is not itself treatment-assigned, but uniform exposure does not prove the absence of treatment interaction — a piece of startup context could in principle interact differently with different treatment content even while being byte-identical across observations. The purpose of conditions 1–4 above is to eliminate *known* condition-specific startup content and to disclose residual uncertainty, not to prove that no interaction could occur. This distinction matters most for §5's condition-identity guarantees (see the strict qualification rule below).

The run manifest must classify startup context per role as one of `KNOWN`, `PARTIALLY OBSERVABLE`, or `UNAVAILABLE`. **These classifications have different consequences for whether the run can claim strict V3 conformance — `UNAVAILABLE` is not a free pass:**

| classification | meaning | strict-V3-conformance consequence |
|---|---|---|
| `KNOWN` | The exact startup context is known and documented (e.g. captured verbatim in the manifest or referenced by file path + hash), and was audited against conditions 1–4 above. | Acceptable, if the audit confirms the content is safe (non-treatment-specific, no outcome/evaluator/mapping/rubric leakage). |
| `PARTIALLY OBSERVABLE` | Some startup context is known (e.g. "system prompt X is used") but its full extent is not independently verifiable. | Acceptable **only** when the observable runtime contract or backend documentation is sufficient to establish that the unobserved remainder is standardized, generic runtime scaffolding — not repository- or experiment-specific — and therefore cannot plausibly contain treatment/outcome/evaluator/mapping material. This determination and its basis must be recorded, not assumed. |
| `UNAVAILABLE` | Nothing about startup context beyond the experimental packet is known or observable. | **By itself, insufficient for a strict V3 replication.** `UNAVAILABLE` renames ignorance, it does not establish compliance. To proceed, the backend must either (a) provide an independent runtime guarantee — documented, not inferred — sufficient to exclude treatment/outcome/evaluator/mapping leakage even without visibility into the exact content, or (b) backend qualification **FAILS on this point** and execution stops (§8). A run that proceeds with `UNAVAILABLE` and no such independent guarantee must record the run as **not strict-V3-conformant on startup context** rather than silently treating `UNAVAILABLE` as equivalent to `PARTIALLY OBSERVABLE`. |

This is a deliberate tightening relative to PR #147's V2 replication, which used `UNAVAILABLE` and was accepted as genuine (but disclosed-non-conformant) empirical evidence. V3's purpose is to *close* E4, not merely restate it under a friendlier label — see §9's disposition table.

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

Instead, use opaque observation IDs assigned by the same randomization process V2 already uses for evaluator-facing labels (e.g. `G7K2Q`, `M41RX`) for **every** generator observation, not only evaluator-facing artifacts. The orchestrator may retain the sealed treatment mapping needed to construct packets and to unblind later — the generator must receive the treatment's actual *representation* (that is the treatment itself, and cannot be hidden), but must **not** receive an explicit A/B/C label or any condition-correlated metadata token (filename, ID, path segment) alongside it. This applies equally to every artifact and manifest row produced before the pre-unblind commit (§7) — see that section's explicit "no readable condition field pre-unblind" rule, which is the same requirement applied to structured data rather than filenames.

This closes E5 at the naming layer; §6 (raw-output immutability) and the leakage-audit step (§7 step F, "leakage audit," part of the pre-unblind pipeline — not a separately numbered section) close it operationally by verifying no condition token appears anywhere in a generator-facing artifact or in any pre-unblind manifest row.

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

**The pre-unblind Git commit (step K) must contain enough to prove the judgments were frozen before mapping revelation, but must NOT contain a readable treatment mapping — and no readable A/B/C condition identity anywhere in its contents, not just in a dedicated "mapping file."**

Preferred approach — the pre-unblind commit (step K) includes:
- blind packets (opaque filenames/IDs only, per §5);
- raw generator outputs (opaque filenames/IDs only);
- raw evaluator outputs (opaque filenames/IDs only);
- normalized blinded judgments (with recorded transformations per §6; opaque IDs only);
- the **PRE-UNBLIND observation manifest** — one row per observation, containing: opaque observation ID; probe ID/horizon; repetition index; role; raw/normalized artifact paths and hashes; tool-use audit; provenance-tagged fields (see "Provenance category vocabulary" above). **This manifest must contain NO `condition_id`/`hidden_condition_id` field or any other A/B/C-encoding column, value, filename, path segment, or worker/observation ID at this stage** — this is the direct, structured-data counterpart of §5's filename rule, and closes the same E5-class risk for manifest rows, not just packet filenames;
- hashes (schedule hash, blind-packet hash, judgment hash);
- the randomized schedule (opaque IDs only, no condition column);
- an **opaque mapping reference** — a hash or cryptographic commitment of the sealed treatment map (e.g. `sha256(sealed-condition-map.json)`), so the eventual revealed mapping can be verified against a value that existed before it was read — but **not** the readable mapping itself, and not a "commitment" that is trivially reversible (e.g. do not hash a map with only 45 entries and a small ID space in a way that permits brute-force recovery — use a keyed/salted commitment if the mapping space is small enough to be guessable).

The post-unblind commit (step M) then adds a **POST-UNBLIND joined artifact** — the readable `sealed-condition-map.json`, plus a joined table that *adds* a `condition_id` column to (a copy of) the pre-unblind manifest rows, plus reconciliation/results. Git history itself — commit K existing, with commit M strictly later and containing the mapping that commit K only hashed — is then independent proof of ordering, not merely a claim resting on script control-flow and a session transcript (PR #147's limitation).

**What "unblind" means, precisely (this corrects an ambiguity in the sequence above):** the sealed treatment mapping necessarily exists, and is necessarily used **operationally**, before treatment packets can be constructed at all (step B) — the orchestrator must know which opaque ID corresponds to which condition in order to build the correct A/B/C representation for it. That early, construction-time use is not "unblinding" and does not violate this contract. What this contract requires is:

- the mapping is generated (or fixed) before treatment-packet construction, and used by the orchestrator only for that construction purpose during steps B–J;
- the mapping must remain **inaccessible to generator workers and evaluator workers** at every step (enforced by §4's capability contract and §5's opaque-ID contract);
- evaluator judgments must be **completed and frozen** (steps G–J) — and the pre-unblind commit K created — **before** the mapping is used for condition-labelled joining, reconciliation, or interpretation;
- **"unblind" (step L) means specifically:** reveal/use the condition identity for post-evaluation joining and interpretation. It does not mean, and has never meant, that the orchestrator lacked the mapping until step L — only that the mapping's *analytical* use (joining conditions to judgments, computing per-condition results) is deferred until after judgments are frozen and committed.

If a genuinely better cryptographically-equivalent design is available for a given backend (e.g. a signed, timestamped external commitment service), it may be substituted, but only after being explained in the run's own provenance audit before adoption — do not weaken this requirement merely for convenience.

## 8. Backend qualification canary (required before any experimental invocation)

**Correction to an overclaim implicit in earlier drafts of this contract:** a canary can demonstrate certain *observable* properties of a specific run of a backend. It **cannot**, by itself, prove a negative — that no hidden runtime or orchestrator context was injected into a worker's context. Treating a canary `PASS` as proof of that negative would be exactly the kind of overclaim PR #147's own reconciliation had to walk back (see `../global-map-architecture-value-v2/runs/20260828-agent-native-sonnet-opus-v2/evidence-reconciliation.md` §B). This contract therefore separates qualification evidence into two distinct categories, and a `PASS` result must state which category each claim rests on.

**A. RUNTIME / BACKEND CONTRACT EVIDENCE** — evidence from the backend's own documentation, specification, or vendor-provided contract, not from observing one run:
- documented context-isolation behavior (e.g. a provider's API documentation stating each request is stateless and context-free unless a conversation ID is supplied);
- documented startup-context behavior (e.g. documentation of exactly what system prompt or scaffolding, if any, a given invocation type receives);
- tool/runtime capability guarantees (e.g. a documented sandbox that structurally prevents tool use beyond an allowlist, as opposed to an instruction that merely asks the worker not to use other tools).

**B. EMPIRICAL CANARY EVIDENCE** — evidence from actually running non-experimental canary invocations against the backend and observing the results:
- observable carry-over/leakage tests (e.g. distinct-nonce canaries run in parallel, checked for cross-contamination — this is what PR #147's canary did);
- fresh-worker behavior (no resume/continuation observed);
- raw-output capture mechanics (can the exact response be retrieved and hashed?);
- packet/tool delivery mechanics (does the preregistered delivery mechanism from §4 actually work, and is tool use auditable per invocation?);
- model-identity recording mechanics (can the requested identifier, and any resolved identifier, actually be captured per §2?).

Before any real V3 execution, the eventual run must preregister exactly what its canary will test from category B, and must state what it is separately relying on from category A (which may be `UNAVAILABLE`, per §3's strict rule for that case). The canary must use **no experimental probe content** — no Archive of Lies material, no probe questions/options, no rubric material.

**Run manifest requirement:** every qualification claim (e.g. "fresh context: PASS") must record its evidence basis — category A (cite the documentation/contract relied upon), category B (cite the canary observation), or both. A claim with no recorded evidence basis must not be marked `PASS`. In particular: a category-B `PASS` on "no hidden context" claims only "no *observed* leakage in the canary sample," not "no hidden context exists" — see §3 for how this interacts with the startup-context strict-conformance rule.

**Failure of backend qualification → STOP BEFORE EXPERIMENTAL MODEL CALLS.** No synthetic fallback. No parent-agent-prose fallback. No hard-coded templating fallback. No substring-heuristic "evaluator" fallback. This mirrors V2's own Phase 0 requirement and PR #147's canary evidence (`../global-map-architecture-value-v2/runs/20260828-agent-native-sonnet-opus-v2/execution-provenance-audit.md` §2. Canary (non-experimental) evidence), generalized to any backend and corrected to distinguish what that evidence actually proves.

## 9. Planned first V3 execution (recorded, not executed here)

To keep the substantive treatment/probes/roles stable while changing only the execution contract, and for direct comparability with PR #147:

- **Preferred generator requested runtime alias:** `sonnet`
- **Preferred evaluator requested runtime alias:** `opus`

...provided the execution backend selected for that run still supports those identifiers at qualification time (§8).

If those aliases are unavailable when V3 execution later begins: **STOP and make an explicit human decision.** Do not silently substitute different models and still call the result "the planned comparable replication" — record the substitution, the reason, and get explicit sign-off before proceeding, since generator/evaluator model identity is itself a preregistered, fixed control (§1–2).

**This preregistration performs no execution, no model calls, and generates no A/B/C observations.**

## 10. Protocol / source execution topology (fixes the ambiguous "checkout" instruction)

**Correction:** `README.md`'s original run procedure said "checkout `3cc4975...`" as its first step. Taken literally this is operationally broken: `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` predates this V3 protocol entirely (it is a `main` commit from V2's own execution base lineage, before V2 or V3 existed), so checking it out as the *working tree* would remove `docs/research/global-map-architecture-value-v3/` from disk and make it impossible to record run artifacts against this protocol. This section replaces that instruction with an explicit two-root topology.

**A. PROTOCOL / RUN WORKTREE** — the working tree the orchestrator actually operates in for the duration of the run:
- checked out from the merged/frozen V3 protocol revision (i.e. `main` at or after this PR's merge commit, once merged);
- owns run artifacts: `docs/research/global-map-architecture-value-v3/runs/{run_id}/`;
- owns the pre-unblind commit (§7 step K) and the post-unblind commit (§7 step M), both made on this worktree's branch/lineage.

**B. FROZEN SOURCE ROOT** — the exact repository state used to materialize narrative facts and Condition B's behavior:
- narrative facts (Condition A's plain facts, Condition C's golden-ledger Decision Map) are read from the frozen fixture content as it exists at `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` — since that fixture content (`tests/fixtures/repeated_map_focus_v2/`, the golden ledger docs) has not changed since V1/V2 froze it, reading it from the current protocol worktree's checkout (root A) is equivalent to reading it from `3cc4975` directly, **provided this is verified** (e.g. `git diff --stat 3cc4975 -- tests/fixtures/repeated_map_focus_v2/ docs/research/global-map-architecture-value-v1/` is empty) before the run begins;
- Condition B's behavior must come from `src/auteur/series/repeated_map_focus.py` `select_repeated_continuity` **exactly as it exists at `3cc4975`** — if current `main` has since modified this file (verify via the same `git diff --stat` check), the run must either (a) execute Condition B against a separate checkout of `3cc4975` specifically for that file, or (b) STOP and treat any B-affecting drift as a substantive protocol conflict requiring human decision, never silently execute Condition B against a modified implementation and still call it "Condition B."

**Rule:** do not silently execute the experiment against current production source if doing so would change Condition B's behavior or the narrative facts available to A/C. Do not create run-evidence commits (pre-unblind or post-unblind) on the historical `3cc4975` source line — those commits belong on the protocol/run worktree's lineage (root A), which descends from `3cc4975` through the frozen V1/V2/V3 protocol history, not from a detached checkout of `3cc4975` itself.

## 11. PR #147 defect closure disposition (RESOLVED vs. HONESTLY UNOBSERVABLE)

A defect being described as `UNAVAILABLE` in a future V3 run's manifest is not, by itself, "resolved" — it is disclosed, which is different. This section states, for each PR #147 defect, whether this *contract* structurally resolves it (closes the gap regardless of backend) or whether the contract only guarantees honest disclosure of a limitation that a given backend may still exhibit.

| defect | this contract's disposition | why |
|---|---|---|
| **E1** — unavailable sampling controls | **HONESTLY UNOBSERVABLE, backend-dependent** — §1 pins what's exposed and forbids `UNCONTROLLED CHANGE`, but cannot force a backend to expose `temperature`/`top_p`/`seed` if it structurally does not. A future run on a backend that *does* expose these is fully resolved by §1; a run on a backend that does not is honestly disclosed, not silently declared compliant. |
| **E2** — tools-none mismatch | **RESOLVED** — §4's two-layer split (delivery capability vs. reasoning/external-data capability) removes the category error itself; any backend can now express its actual delivery mechanism without that mechanism being miscategorized as a violation, and violations are audited per invocation. |
| **E3** — model-version observability | **HONESTLY UNOBSERVABLE, backend-dependent** — §2 structurally prevents the E3 *documentation-laundering* failure mode (never again treating an alias as a resolved version), which is fully resolved. Whether the exact version is *actually observable* remains a backend property outside this contract's control. |
| **E4** — startup context | **PARTIALLY RESOLVED, backend-dependent, now gated** — §3's strict rule is the key change from PR #147: `UNAVAILABLE` alone no longer permits a claim of strict V3 conformance; it requires either an independent runtime guarantee (category A evidence, §8) or qualification failure. This resolves the *silent-acceptance* failure mode (E4 as originally disclosed in PR #147 was accepted without this gate). Whether a *given* backend can actually supply `KNOWN`/`PARTIALLY OBSERVABLE` status, or must fail qualification, remains backend-dependent and cannot be predetermined here. |
| **E5** — condition-correlated generator metadata | **RESOLVED** — §5 (opaque filenames/IDs for all generator artifacts) plus §7's explicit no-condition-field-in-pre-unblind-manifest rule close this at both the filename layer and the structured-data layer. This is a protocol-level fix independent of backend. |
| **E61** — raw-response normalization | **RESOLVED** — §6's raw-first-immutable-then-separately-derived model, with mandatory diff-and-record of every transformation, structurally prevents an undisclosed paraphrase from occurring; this is a process fix independent of backend. |
| **blind chronology** — not Git-anchored | **RESOLVED** — §7's true pre-unblind Git commit (containing only a hash/commitment of the sealed map, never the readable mapping) makes ordering independently verifiable from Git history alone, not merely from script control-flow and a session transcript. This is a protocol-level fix independent of backend. |

**Summary:** E2, E5, E61, and blind-chronology are structural protocol fixes and are fully **RESOLVED** by this contract regardless of which backend V3 ultimately runs on. E1, E3, and E4 are **backend-dependent** — this contract resolves the *mishandling* of those gaps (silent deviation-labeling for E1, documentation-laundering for E3, silent acceptance of `UNAVAILABLE` for E4) but cannot resolve the underlying observability limitation if a chosen backend genuinely does not expose the relevant control. A V3 run must report each of E1/E3/E4 per its actual backend at qualification time (§8), and for E4 specifically, an `UNAVAILABLE` startup-context classification without an independent runtime guarantee means that run **fails strict V3 qualification on that point** and must either select a different backend or proceed only as an explicitly non-strict-conformant run, analogous to (but stricter than) how PR #147 was accepted.
