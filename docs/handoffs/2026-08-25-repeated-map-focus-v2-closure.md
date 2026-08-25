# Repeated Map/Focus V2 Workstream Closure and Coding-Agent Handoff

Date: 2026-08-25
Status: closed; documentation-only handoff

## Exact repository state

- Worktree: `H:/GithubRepositories/auteur/.worktrees/repeated-map-focus-v2`
- Branch: `feat/repeated-map-focus-v2`
- Closure documentation base: `1536c06d3fa0a66bd85c6a7a723394af4208751d`; any later branch-tip commit is only a correction to this handoff.
- Working tree: clean
- Qualified product candidate: `2e066108db51ff4b42b41316d5ea5e8d627eef71`
- Candidate relationship: `2e06610` is an ancestor of `4721e2e`, and `4721e2e` is an ancestor of the closure documentation. `4721e2e` is the qualification handoff; `1536c06` begins the closure handoff.
- Mainline: `main` remains at `bcd8db2` and does not contain the candidate or handoff commits.
- Integration status: the implementation exists only on this feature branch/worktree. It has not been merged into mainline.
- `CONTEXT.md`: unchanged on this branch and left untouched because no safe milestone-only update was necessary.

## Product state before this campaign

Series Vertical Slice UX V1 was implemented and technically qualified for the bounded Archive of Lies Book 1 -> Book 2 journey. It established sparse Series Direction, local Book Direction, explicit author acceptance, accepted realization, a transition into later-Book planning, and Map/Focus presentation. It had not demonstrated repeated multi-Book continuity behavior.

That V1 state was awaiting real participant evidence. Synthetic probes were not treated as usability validation.

## What Repeated Map/Focus V2 added

V2 adds a narrow repeated opening-Book planning capability:

- accepted-history reading through Book `N - 1`;
- explicit `BookPlanningIntent` as a non-authoritative relevance trigger;
- projection-local current-state evidence and continuity dispositions;
- lifecycle-aware local relevance without introducing a universal lifecycle model;
- compact pressure grouping with exact source references and specific why-now explanations;
- delete/rebuild-equivalent derived context persistence;
- bounded current-Book Focus proposals for Book 3+;
- explicit stale and state-incompatible proposal rejection;
- current-Book Map/Focus presentation and real CLI dispatch;
- deterministic Book 3/4 decision seeds as qualification inputs only.

Task 11 added the corrected R1-R5 ledger and end-to-end acceptance scenarios. Task 12 independently qualified the exact candidate.

## Qualification evidence

Qualification report:
`docs/engineering/series-repeated-map-focus-qualification-v2.md`

Candidate-addressed source evidence:
`docs/qualification-evidence/2e066108db51ff4b42b41316d5ea5e8d627eef71.json`

Product candidate qualification:

- focused serial and parallel matrices: 212/212 passed in each;
- R1-R5 gate: 168/168 passed;
- complete source gate: 4,477 collected, 4,449 passed, 1 skipped, 27 xfailed, 0 xpassed, 0 failed, 0 errors;
- baseline comparison against `d3bb1eb`: no added or removed failure nodes;
- installed wheel: `auteur-0.37.1-py3-none-any.whl`, SHA-256 `c5a0e8df92c523f58a750e23db6acd174ea7680892d010e8da5edb476e908950`, all installed checks passed.

The source evidence was produced with `release_evidence.py --skip-wheel`. The wheel was qualified separately with `verify_wheel.py`; the JSON `wheel.status: NOT_RUN` is therefore correct historical evidence and must not be rewritten.

## Architectural invariants preserved

- Accepted Series Direction, Book Direction, realization, and Canonical State remain the authority owners.
- Opening Book-N Map/Focus uses accepted authority only through Book N-1.
- Present Book-N planning intent may trigger relevance but cannot become Book-N authority.
- Derived Map and Focus are non-authoritative, provenance-bearing, and rebuildable.
- Author action is explicit workflow history; it does not silently create canon.
- Historical ratification and current eligibility/currentness remain distinct.
- Relevance dispositions are projection-local and are not artifact lifecycle states.
- Pressure grouping is projection-local and is not a universal domain taxonomy.
- Stale or incompatible proposals are unavailable until explicitly recomputed.
- Default presentation uses progressive disclosure; detail reveals provenance rather than changing semantics.

## Product claims now supported

Auteur can carry accepted narrative history from Book 1 through later opening-Book planning checkpoints, select context by local relevance, explain why surfaced context matters now, preserve exact provenance, and present one bounded current-Book creative decision without silently authoring canon.

This is demonstrated by the corrected R1-R5 ledger, not by a general Series simulator.

## Explicit non-claims and deferred machinery

This workstream does not claim:

- finite-Series support;
- generalized Series-extent evolution;
- a universal lifecycle, relevance, or recommendation engine;
- free-form Book-N Direction authoring;
- human usability validation or participant evidence;
- release readiness.

Deferred machinery includes finite extent/evolution, universal narrative lifecycle, universal dependency/event graphs, numerical or learned relevance ranking, a universal PressureGroup taxonomy, a general recommendation engine, generic Author Decision aggregates, intra-Book checkpoints, cross-Series continuity, and browser/TUI/editor redesign.

## Remaining human-evidence questions

An actual long-form writer is still needed to determine:

- whether compact grouped history remains understandable as entries accumulate;
- whether why-now explanations are useful rather than burdensome;
- whether the distinction between workflow choice and canon is understood;
- whether bounded Focus options feel creatively useful or overly restrictive;
- whether the current presentation is appropriate for a beginner-facing product;
- whether recommendation content—not merely proposal shape—is valuable;
- which uncertainty most affects real writer value: finite/uncertain extent, recommendation content, human presentation, or another boundary.

These are open evidence questions, not a selected V2 priority.

## Remaining known capability gaps

- No finite or uncertain Series extent model exists.
- No contraction/expansion workflow exists for Series extent.
- No free-form author-authored Book-N Direction path exists.
- Repeated Focus requires caller-supplied bounded seeds; it does not generate broadly useful recommendation content.
- The current CLI is an adapter, not the settled beginner-facing interface.
- No real participant validation has been conducted.

## Process lessons

The approximately eight-hour campaign was dominated by sequential orchestration, repeated subagent review/wait cycles, and complete-suite qualification—not by the amount of production code.

Record these lightweight process rules for future work:

- prepare and freeze baseline evidence before implementation;
- use focused regressions during development;
- reserve complete source qualification primarily for the final candidate;
- parallelize independent read-only reviews where safe while preserving sequential dependent implementation;
- use review intensity proportional to semantic and architectural risk.

No large tooling project is implied.

## Durable pointers

- Behavioral contract: `docs/acceptance/series-repeated-map-focus-capability-contract-v1.md`
- Implementation boundary: `docs/design/series-repeated-map-focus-implementation-boundary-v1.md`
- TDD implementation plan: `docs/superpowers/plans/2026-08-24-repeated-map-focus-v2.md`
- Synthetic repeated-Map/Focus evidence: `docs/product-validation/series-vertical-slice-v1-synthetic-repeated-map-focus-probe.md`
- Qualification report: `docs/engineering/series-repeated-map-focus-qualification-v2.md`
- Candidate evidence: `docs/qualification-evidence/2e066108db51ff4b42b41316d5ea5e8d627eef71.json`

## Next-session decision question

> What remaining uncertainty is now most consequential to Auteur's ability to deliver value to an actual long-form writer?

Finite or uncertain Series extent, general recommendation-content generation, human-facing presentation, and another boundary discovered from current repository/product evidence are candidate areas only. This handoff deliberately selects no next capability and starts no new campaign.

## Fresh-session starting instruction

Begin by reading this handoff, the behavioral contract, the implementation-boundary analysis, the TDD plan, and the qualification report. Treat `2e06610` as the qualified product candidate, `4721e2e` as the qualification handoff, and `1536c06` as the closure commit. Preserve all explicit non-claims. Do not infer that the feature branch is integrated into mainline, and do not begin implementation or discovery until a separate next decision has been made.
