# Global Map Architecture Value V3 — README (Backend-Agnostic Execution Contract)

**Version:** `global-map-architecture-value-v3` — **PREREGISTERED CANDIDATE, NOT YET FROZEN, NOT EXECUTED**
**Supersedes for execution:** V2 is FROZEN, EXECUTED (see `../global-map-architecture-value-v2/runs/20260828-agent-native-sonnet-opus-v2/`) — do not modify V2. V3 does not redesign V2's substantive experiment; it replaces V2's execution-contract language, which PR #147's own evidence-reconciliation pass showed was not backend-agnostic.

**Frozen narrative/source revision (unchanged):** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (PR #143 merge)
**Ledger (unchanged):** 33-item golden ledger `../global-map-architecture-value-v1/candidate-architecture-ledger.md`
**Source manifest (reused by reference):** `../global-map-architecture-value-v1/source-manifest.md` — not duplicated.
**Probes / evaluation rubric (reused by reference):** `../global-map-architecture-value-v2/decision-probes.md`, `../global-map-architecture-value-v2/evaluation-rubric.md` — not duplicated, not modified.

---

## What V3 changes (execution contract only)

V2's `condition-specification.md` §Control variables specified provider-API-shaped controls (exact `temperature`/`top_p`, `tools: none`, "same model/version") that PR #147 showed are not universally expressible across backends, and one condition-identity hygiene gap (E5) that V2 never addressed because V2 did not anticipate an agent-native generator-delivery mechanism. V3 replaces that section with `execution-contract.md`, a **role-scoped, backend-agnostic inference configuration contract** — see that file for the full specification.

**Everything else — research question, hypotheses, A/B/C conditions, fixture, ledger, probes, rubric, repetition count, invalidation rules, severe-negative treatment, no-single-score rule — is unchanged and reused by reference from V2.**

---

## Artifacts in this V3 directory

| file | purpose |
|---|---|
| `execution-contract.md` | The backend-agnostic inference configuration contract, in order: §1 inference configuration (per role), §2 model identity, §3 fresh-context/startup-context, §4 packet-delivery/tool capability, §5 opaque generator condition-identity, §6 raw-output immutability, §7 true pre-unblind Git freeze + unblinding semantics, §8 backend-qualification canary, §9 planned first execution, §10 protocol/source worktree topology, §11 PR #147 defect closure disposition. Provenance-category vocabulary and the backend-agnostic empirical invariant are stated up front, before §1. |
| `run-manifest-template.md` | Per-observation manifest template for a V3 run, extending V1/V2's template with the new provenance fields the execution contract requires (requested vs. resolved model identifiers, startup-context classification, packet-delivery mechanism, tool-use audit, provenance-category tags). |
| `README.md` | This file. |

**Reused by explicit reference (not duplicated):** `../global-map-architecture-value-v1/source-manifest.md`, `candidate-architecture-ledger.md`; `../global-map-architecture-value-v2/decision-probes.md`, `condition-specification.md` (substantive A/B/C sections only — its Control Variables section is superseded by `execution-contract.md` for V3 execution), `evaluation-rubric.md`.

Top-level `../global-map-architecture-value-experiment-v3.md` is the V3 summary entry point.

---

## How to run V3 (without redesigning the substantive experiment)

**Execution topology (see `execution-contract.md` §10 for the full rationale — this corrects an earlier, operationally broken "checkout `3cc4975...`" instruction):** operate from a **protocol/run worktree** checked out from the merged V3 protocol revision (`main`, post-merge). Read the frozen source-manifest, ledger, and Condition B implementation from that worktree, but first verify they are byte-identical to the **frozen source root** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (e.g. `git diff --stat 3cc4975 -- tests/fixtures/repeated_map_focus_v2/ src/auteur/series/repeated_map_focus.py docs/research/global-map-architecture-value-v1/` must be empty). Never check out `3cc4975` itself as the working tree for this run — that would remove the V3 protocol files from disk. Never commit run evidence on the historical `3cc4975` line.

1. On the protocol/run worktree, read the reused source-manifest + ledger (unchanged from V1/V2), having verified their identity with the frozen source root as above.
2. Select and preregister the execution backend for this run; run and record the **backend qualification canary** (`execution-contract.md` §8. Backend qualification canary — evidence split into category A runtime/backend-contract evidence and category B empirical canary evidence) before any experimental packet is built. If qualification fails, STOP — no synthetic fallback, no parent-agent-prose fallback, no template/heuristic fallback. If startup context classifies as `UNAVAILABLE` with no independent runtime guarantee, qualification **fails on that point** (`execution-contract.md` §3).
3. For each probe P01–P05 (P05 = Book4 paired with P03, per V2), build 3 condition packets per `../global-map-architecture-value-v2/condition-specification.md` §Conditions substantive content, using **opaque, non-condition-correlated observation IDs** for all filenames/paths/delegation strings and manifest rows (`execution-contract.md` §5. Opaque generator condition-identity contract).
4. Generate 3 independent observations per condition per probe under the fixed per-role inference configuration (`execution-contract.md` §1. Inference configuration contract), preserving every raw response immutably before any normalization (`execution-contract.md` §6. Raw-output immutability contract).
5. Build blinded evaluator packets (opaque IDs, global rubric, per-probe hidden signals only — no condition identity, no expected winner).
6. Perform blinded evaluation under the evaluator's fixed inference configuration, again preserving raw responses immutably before normalization (§6).
7. Freeze blinded judgments; create the **true pre-unblind Git commit** (`execution-contract.md` §7. True pre-unblind Git freeze) containing blind packets, raw outputs, raw evaluator responses, normalized judgments, and the **pre-unblind observation manifest** (opaque IDs only — no `condition_id` field, per §7's explicit rule), plus hashes, schedule, and a hash/commitment of the sealed map — but not the readable mapping.
8. Only after that commit exists, reveal the mapping and mechanically join into the **post-unblind joined artifact** (which adds a `condition_id` column). Record post-unblind reconciliation in a later, separate commit. See §7's precise definition of "unblind" — the mapping was already used operationally in step 3 to build packets; step 8 is specifically its use for condition-labelled joining and interpretation.
9. Apply the preregistered decision gate below to the frozen evidence.

No execution occurred in this preregistration task.

---

## Decision gate (preregistered, human, post-evidence — reused verbatim from the V3 preregistration task, not invented here)

Preserve per-probe/per-criterion evidence and severe negatives; do not reduce to one aggregate score.

- **CASE 1** — B shows a useful advantage over A **and** C shows a reproducible, mechanistically grounded advantage over B in the paired P03/P05 Book-4 decision family, without severe architecture-caused negatives:
  → architecture-rich causal/grouping representation is **PROMISING**;
  → authorize consideration of the *smallest* production/research capability that explains the observed C advantage;
  → likely next research boundary: extraction reliability;
  → do **not** automatically authorize a full Global Map.

- **CASE 2** — B shows a useful advantage over A but C shows no meaningful incremental value over B:
  → shipped Map/Focus captures most demonstrated representational value on this fixture;
  → defer richer architecture;
  → return to human Map/Focus usability/comprehension validation.

- **CASE 3** — result is unstable/noisy/inconsistent:
  → diagnose fixture discrimination, evaluator variance, ceiling effects, or model/runtime sensitivity;
  → do **not** automatically create V4 or productize architecture.

This is a **human decision gate**, applied after evidence is frozen and unblinded. The evaluator must never receive these cases, an expected winner, or any comparative outcome language. Generator and evaluator packets must not reference V3's follow-up uncertainty statement in `../global-map-architecture-value-experiment-v3.md` §1.

---

## Version / freeze semantics

- **V1:** FROZEN, NOT EXECUTED, SUPERSEDED FOR EXECUTION BY V2. Do not modify.
- **V2:** FROZEN, EXECUTED — agent-native empirical evidence preserved in `../global-map-architecture-value-v2/runs/20260828-agent-native-sonnet-opus-v2/`. Final classification: AGENT-NATIVE EMPIRICAL EXECUTION WITH DISCLOSED FROZEN-V2 EXECUTION DEVIATIONS — DIRECTIONALLY INTERPRETABLE FOR WITHIN-RUN A/B/C COMPARISON — NOT A STRICT FROZEN-CONTROL-CONFORMANT V2 REPLICATION. Do not modify.
- **V3 before this protocol PR merges:** `PREREGISTERED CANDIDATE`, `NOT EXECUTED`.
- **V3 after this protocol PR merges:** `FROZEN FOR EXECUTION`, `NOT YET EXECUTED`.
- **Once the first V3 experimental output exists:** do not silently change V3. A material protocol defect discovered afterward requires a V4.

## Next

After review and merge: execute one V3 replication (`NEXT: Auteur — Global Map — Architecture Value Experiment V3 — Execution`). Do not execute in this task. This protocol PR must not be merged by the agent that authored it — it is left open for human review.
