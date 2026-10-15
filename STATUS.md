# Auteur — Current Repository Status

**Last reconciled:** 2026-10-14
**Integrated baseline:** `main @ 4122321fe09d1959278fdd087fc29f85e2f3a9d2` (PR #436 merge)
**Latest published release:** `v0.37.1` (`pyproject.toml` `1.0.0` is not publication evidence)

Short operational handoff only; history belongs in Git, PRs, issues, qualification, and evidence records. Read [MISSION.md](MISSION.md), [docs/narrative-architecture.md](docs/narrative-architecture.md), and [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md).

## Current Frontier: F2 + X3

Issue #318 remains open. The controlled six-Chapter **The Glass Archive** journey began against the exact merged baseline above and stopped at Chapter 1 after a demonstrated Windows persistence defect.

- The first Chapter completion wrote LF candidate text as CRLF, so its persisted bytes did not match the completion receipt hash. Acceptance then encountered the same translation in `final.md`.
- `Project.write_draft` and `Project.write_final` now preserve LF bytes; byte-level regression assertions were added. Focused chapter-generation, acceptance, and project persistence tests pass (34 tests).
- The exact Chapter 1 host-agent response completed and was explicitly accepted in the disposable fixture after the repair. The generated scene was 946 words. No later Chapter has been run, so F2/X3 has **not** passed its journey gate.
- The failed pre-repair acceptance had already written Bible events before the wrapper rejected the CRLF final. Retrying that interrupted operation duplicated authority events in the disposable fixture. This is recorded as a consequence of the failed attempt, not a clean-run outcome. No production story was used.

The repair is currently an uncommitted worktree change based on merge SHA `4122321`; it is not yet a new exact-head qualification or a merged fix. Continue from a clean fixture after establishing an exact candidate SHA, then resume at Chapter 1 and proceed only while the same controlled checkpoint succeeds.

## Quick Draft (#310)

Four real host-agent Quick Draft scenarios were run (mystery, character-driven, speculative, intentionally vague). Each generated response remained a Working draft (`accepted: false`). The complete requests, responses, outputs, hashes, and measured word counts are in [post-#436 product-use evidence](qualification-evidence/4122321-post436-product-use.json).

Observed issue: a Browser session displayed `awaiting_host_agent`, disabled its editor, and did not expose the request prompt/hash in the page. No natural notification to the active coding-agent environment was observed; this run required task context and local request inspection. The API accepted a response, but the page did not update during the observed wait; reopening the session displayed the saved draft. This does not establish a general host bridge or successful unattended fulfillment.

Model identity and reliable per-request latency were unavailable, so they are recorded as unavailable. The four scenarios are agent-generated dogfood evidence, not human author feedback. Two outputs were below the prompt’s approximate 1,400-word target (1,030 and 1,076 words); the other two were 1,147 and 1,129 words.

## Current-main Beginner Narrative-Architecture Coherence

`CURRENT_MAIN_BEGINNER_COHERENCE_RECONCILIATION`: the Beginner path reuses the accepted whole-story Structure to derive Chapter and scene plans. Scene plans mark the **Structure → Realization** boundary; outline and Chapter plans remain derived proposals until the author explicitly accepts them. L3 verification and human qualification remain separate evidence gates. This handoff records agent product use only; no human author walkthrough occurred in this run.
## PR #436 integration and qualification evidence

PR #436 is merged. Its exact source qualification was recorded at `97354ee6ea293df6c6b15783406e6c1d560403bf`; the integration commit is `4122321fe09d1959278fdd087fc29f85e2f3a9d2`.

Recorded exact-source checks: Node 64/64; focused Python 28; `-k studio` 163; Stage B browser check 16/16; focused unfolding 11/11. The serial full Python suite had 5,591 passed, 24 failed, 2 skipped; all 24 failures matched the exact-main baseline and no candidate-only failure was recorded. GitHub Actions had no runs. These results do not qualify the subsequent Windows persistence repair.

A fresh mentorship response was also sampled through CanvasStore: one response passed the strict backend contract and offered three distinct options while preserving supplied constraints. It remains one agent sample, not a human study or product-readiness finding.

## Claim ceiling and next execution

The merged work is integrated development work. The Windows repair has focused test evidence only; the exact candidate SHA and broader post-repair qualification remain outstanding. Do not call F2/X3 complete, the fix merge-ready, or the experience product-ready yet.

1. Freeze and record the repair candidate SHA; run the required exact-head Node and Python qualification, including baseline comparison for required-check failures.
2. Resume the controlled Glass Archive from a clean fixture at Chapter 1; continue through the frozen checkpoints only while author authority and narrative state persist correctly.
3. Reconcile issue #318 using the actual journey evidence.
4. Reconcile issue #310 with the observed `awaiting_host_agent` interaction gap and four exact scenario outputs.
5. Use a real author walkthrough for creative mentorship and UX claims; current agent samples cannot answer those questions.

F3/X4 remains unselected. Do not add a host bridge, new test framework, or feature without evidence from the existing product-use boundaries.

## Governance / External Gates

- **#338:** human protected commit — replace the absolute 500-line/12-file rejection rule and consolidate AGENTS/CLAUDE guidance.
- **#272:** GitHub admin — require PR-only `main`, no mandatory hosted Actions.
- **#295 / #218:** separate qualification lanes; neither blocks current F2 product-use evidence.

## Simplification Rule

```text
accepted story
+ Working candidate
+ source freshness
+ explicit promotion
```

Preserve authorial authority and auditable provenance; reduce machinery that mainly administers the repository.
