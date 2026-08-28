# Global Map Architecture Value Experiment V3 — Backend-Agnostic Execution Contract (Preregistration)

**Status:** `PREREGISTERED CANDIDATE` — **NOT YET FROZEN, NOT EXECUTED.** Frozen for execution only once this protocol PR merges (see `../global-map-architecture-value-v2/README.md`-equivalent freeze semantics in `global-map-architecture-value-v3/README.md`).

**Publication prerequisite (verified before this document was written):** PR #147 (agent-native V2 replication) merged at `46497621602c238624e77b6c50223dfc34ebbaea`; post-merge Validation `#375` (GitHub Actions run `33218255225`) SUCCEEDED on that exact commit. ARCHITECTURE VALUE V2 AGENT-NATIVE PUBLICATION: COMPLETE.

**Frozen narrative/source revision (unchanged from V1/V2):** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (PR #143 merge, `origin/main`).
**Experiment version:** `global-map-architecture-value-v3` (successor to `global-map-architecture-value-v2` for execution; V2 remains FROZEN, EXECUTED, do not modify).
**Artifacts:** `docs/research/global-map-architecture-value-v3/` (`README.md`, `execution-contract.md`, `run-manifest-template.md`). This file is the V3 summary entry point.

---

## Why V3 exists (execution contract only, one defect class)

PR #147 (`docs/research/global-map-architecture-value-v2/runs/20260828-agent-native-sonnet-opus-v2/`) produced genuine agent-native empirical evidence for the frozen V2 substantive experiment, but its own evidence-reconciliation pass (`.../evidence-reconciliation.md`) found that V2's execution *controls* — written when the experiment assumed a provider-API backend — are not backend-agnostic and were not fully honored by an agent-native backend:

- **E1** — sampling parameters (temperature/top_p/seed/max_output_tokens) not exposed by the backend, so frozen V2's exact values could not be pinned or verified.
- **E2** — frozen V2's `tools: none` control mismatched a `general-purpose` sub-agent's inherent full tool access; the restriction was enforced only by instruction, not sandboxed.
- **E3** — exact resolved provider model-version was not observable through the backend; only the requested model alias was confirmable.
- **E4** — ordinary sub-agent runtime/startup context beyond the experimental packet was not independently verified as absent.
- **E5** — generator packet filenames were condition-correlated (`P01-A.txt`, `P01-B.txt`, `P01-C.txt`), exposing the A/B/C letter to generator workers as a filename token — a real, non-uniform, agent-native execution-contract deviation (not a frozen-V2 invalidation, since frozen V2 requires only evaluator-side blinding, but a defect worth closing).
- **E61** — one evaluator response was returned truncated; the orchestrator's normalized artifact both closed the JSON syntax and (undisclosed at first) paraphrased the free-text rationale, rather than preserving the raw response as the primary artifact and treating normalization as a separate, disclosed derivation.
- **Blinding chronology** — freeze-before-unblind ordering was session-supported/self-audited only; no independently Git-anchored pre-unblind commit existed to prove the ordering outside the orchestrator's own transcript.

None of these are defects in the *substantive* V2 experiment (research question, hypotheses, A/B/C conditions, fixture, ledger, probes, rubric). V3 exists solely to replace the execution-contract language that assumed a provider-API backend with an explicit, backend-agnostic inference contract that any qualified backend — API-backed, local, hosted, or agent-native — can satisfy, be measured against, and be audited against. See `global-map-architecture-value-v3/execution-contract.md` §11. PR #147 defect closure disposition (RESOLVED vs. HONESTLY UNOBSERVABLE) for exactly how each item is addressed — not every item is claimed fully "resolved"; §11 distinguishes structural fixes from backend-dependent, honestly-disclosed limitations.

---

## 1. Research question, hypotheses (unchanged from V2, reused by reference)

> What explicit narrative architecture does Auteur need to make materially better long-horizon creative decisions than a prompt/context-only system and current Repeated Map/Focus, without unacceptable maintenance cost, false precision, stale structure, or authority confusion?

`H0`/`H1` unchanged — see `../global-map-architecture-value-v2/README.md` and `global-map-architecture-value-experiment-v2.md`. V3 does not redesign the research question.

**V3's specific follow-up purpose:**

> V3 preserves the frozen V2 substantive Architecture Value experiment while replacing provider-specific execution controls with an explicit, backend-agnostic inference contract. Its purpose is to determine whether V2's observed treatment differences reproduce under a clean, independently auditable execution in which fresh-context isolation, treatment delivery, model identity, raw-output preservation, and freeze-before-unblind chronology are correctly specified for the chosen backend.

**The central follow-up uncertainty V3 exists to test:**

> Does the observed C-over-B advantage in causal trace, pressure grouping, and explanation within the paired P03/P05 Book-4 decision family reproduce when the execution-contract defects identified in PR #147 are removed?

This is a question, not a predicted answer. It is stated here, in the human-facing summary document, for interpretation purposes only — it must never appear in any generator packet (which contains only the substantive content described in `../global-map-architecture-value-v2/condition-specification.md` §Conditions plus the opaque observation ID scheme in `execution-contract.md` §5) or evaluator packet (which contains only the global rubric and per-probe hidden signals from `../global-map-architecture-value-v2/evaluation-rubric.md`, per the blind-evaluation procedure reused from V2). Neither packet type may contain this uncertainty statement, an expected winner, or any of the decision-gate cases in §6 below.

## 2. Conditions (unchanged, reused by reference)

- **A — Prompt/context-only baseline:** unchanged, see `../global-map-architecture-value-v2/condition-specification.md` §A.
- **B — Current Auteur (shipped):** unchanged, `src/auteur/series/repeated_map_focus.py` `select_repeated_continuity` (`_DERIVATION_VERSION=repeated-map-focus-v2-r1`). No modification.
- **C — Architecture-rich (golden):** unchanged, same 33-item ledger (`../global-map-architecture-value-v1/candidate-architecture-ledger.md`) → Global Map → Decision Map. Ledger not enriched.

## 3. Fixture, ledger, probes (unchanged, reused by reference)

- Fixture: *Archive of Lies* via `tests/fixtures/repeated_map_focus_v2/`, frozen at `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41`. No second fixture.
- 33-item golden ledger: `../global-map-architecture-value-v1/candidate-architecture-ledger.md`. Not enriched.
- 5 probes P01–P05, same decision questions/options/horizons: `../global-map-architecture-value-v2/decision-probes.md`. P03/P05 remain **one paired Book-4 decision family**, not two independent replications; P04 remains the adversarial state-compatibility variant of the same Book-4 horizon. 4 independent decision situations total, unchanged.
- 3 observations per condition per probe (45 total) unless the chosen backend is genuinely deterministic, in which case 1 is sufficient and must be recorded as such.

## 4. Evaluation (unchanged, reused by reference)

- Same 11 global criteria, same hidden per-probe must-not-miss/forbidden signals: `../global-map-architecture-value-v2/evaluation-rubric.md`.
- Same no-single-weighted-score rule; same severe-negative treatment (recorded separately, not averaged away).
- Same authority constraints (recommendation is non-authoritative, does not create canon).
- Same distinction between representation *value* (what V3 tests) and extraction *quality* (out of scope — ledger remains hand-built golden).

## 5. What V3 changes (execution contract only)

See `global-map-architecture-value-v3/execution-contract.md` for the full backend-agnostic inference configuration contract: §1 per-role (generator/evaluator) fixed inference configuration (addresses E1); §2 the model-identity contract, requested vs. resolved identifiers (addresses E3); §3 the fresh-context/startup-context contract, with a strict qualification rule (addresses E4); §4 the packet-delivery/tool-capability contract (addresses E2); §5 opaque generator condition-identity (addresses E5); §6 raw-output immutability (addresses E61); §7 the true pre-unblind Git freeze plus precise unblinding semantics (addresses the blinding-chronology gap); §8 the backend-qualification canary, split into runtime/backend-contract evidence and empirical canary evidence; §9 the planned first execution; §10 protocol/source worktree topology; §11 the honest RESOLVED-vs-HONESTLY-UNOBSERVABLE disposition for every defect. See `execution-contract.md` §11 for which defects this contract resolves structurally (E2, E5, E61, blinding chronology) versus which remain backend-dependent even though the contract fixes how they are handled (E1, E3, E4).

## 6. Decision gate (preregistered, human, post-evidence)

See `global-map-architecture-value-v3/README.md` "## Decision gate (preregistered, human, post-evidence — reused verbatim from the V3 preregistration task, not invented here)" for the three preregistered interpretation cases (CASE 1/2/3). The evaluator must never receive these cases or any expected comparative outcome.

## 7. Scope exclusions (unchanged from V2, restated)

No production Global Map implementation; no extraction engine; no second fixture; no new probes; no C enrichment; no B modification; no ontology/schema/persistence/CLI/UI changes; no `.github/workflows`/build changes; no ADR. This document and its companions are protocol only — no model calls occurred in producing them.

## 8. Freeze rule

On merge of the V3 protocol PR, this document and `global-map-architecture-value-v3/` become `FROZEN FOR EXECUTION, NOT YET EXECUTED`. A material defect discovered after the first V3 experimental output exists requires a V4, not a silent V3 edit — same discipline as V1→V2. V1 and V2 remain untouched by this document.

---

## Next step

After review and merge: execute one V3 replication (`NEXT: Auteur — Global Map — Architecture Value Experiment V3 — Execution`), following the qualification-canary-then-experiment sequence in `execution-contract.md`. Do not execute in this task.
