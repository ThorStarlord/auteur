# Auteur — Current Repository Status

**Last reconciled:** 2026-10-07  
**Current main:** `ecc42ec2b9faeb4fc8037ce88b2379e44a4102d2`  
**Package metadata:** `1.0.0` — development metadata, not a release claim  
**Latest published release:** `v0.37.1`  
**Role of this file:** short operational handoff only. Historical work belongs in Git history, PRs, issues, qualification records, and release records.

For product intent and hard invariants read [MISSION.md](MISSION.md). For the canonical semantic model read [docs/narrative-architecture.md](docs/narrative-architecture.md). For candidate future directions read [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md).

## Current Product Frontier

**F2 — Small-Book Longitudinal Coherence + X3 — Persistent Book Workspace**

Authoritative qualification surface: issue #318 and its frozen **The Glass Archive** six-Chapter reference Book.

The governing rule remains:

```text
run the controlled Book
-> observe the first material recurring failure
-> repair the smallest owning boundary
-> rerun the same checkpoint
-> do not prebuild the next frontier
```

F3/X4 is not selected unless F2/X3 passes.

## Current First Failure

The latest F2 evidence established bounded relevant Chapter-N context but exposed an orchestration gap:

```text
contextual Chapter-N plan
-> author_context
-> Bard request
-> host-agent generation
-> Working draft
```

The relevant context exists; the missing responsibility is connecting that context to exact, freshness-bound Chapter-N generation.

## Active Work

- **PR #332 — Chapter-N host-agent generation orchestration** — draft / current F2 repair.
- **PR #335 — interrupted Chapter-generation recovery** — draft child of #332; reserves the exact Working-draft version before publication so exact retry does not manufacture a second draft.
- **PR #334 — false-guarantee repairs** — draft; fixes staged Book-completion identity validation and makes pending/failed Quick Draft sessions projectable.
- **PR #336 — Quick Draft host-agent default** — draft child of #334; makes host-agent the default Beginner runtime and direct-provider use explicit.

These PRs are implementation candidates, not merged/canonical state.

## Established Evidence

Current main already establishes:

- explicit author acceptance remains the canon boundary;
- local-first validation is the development default;
- Beginner persistent Book orientation exists;
- bounded relevant Chapter-N author context exists;
- neutral host-agent request/response machinery exists for Quick Draft;
- direct provider adapters remain compatibility/standalone backends.

Do not raise the claim ceiling from an open PR. Exact-head validation belongs to the exact implementation head being claimed.

## Validation Posture

- **L1 Focused Validation** — ordinary development evidence, normally local.
- **L2 Targeted Integration** — only for a named changed boundary/risk.
- **L3 Full Regression** — explicit stabilization/milestone/recovery checkpoint.
- **Release Qualification** — separate frozen-candidate activity.
- GitHub Actions are optional remote execution, not a normal development dependency.

## Known Blockers / External Gates

- **#272 — main integration enforcement:** GitHub branch/ruleset administration is external to the connected integration. The current local-first direction does not justify making hosted Actions a mandatory merge dependency.
- **#295 — formal L3 requalification:** remains a qualification lane; focused repair evidence does not close it.
- **#218 — Episode 1 Direction qualification:** remains separate from the current F2/X3 product frontier.
- Human prose preference/usability claims remain human-evidence claims.

An external blocker on one lane does not freeze independently warranted repository work.

## Deferred Lanes

The following are deliberately off the current critical path:

- MANA / audience-effect expansion (former PR #311);
- Progressive Commitment durable-state promotion (former PR #315);
- F3+ multi-thread / larger-Book frontiers;
- generalized retrieval or vector search;
- new semantic layers or global story-state enums;
- Episode 2+ / generalized serial architecture;
- another first-session feature wave.

Reopen a deferred lane only when normal workflow evidence makes it the smallest correct owner of an observed failure.

## Next Trigger

1. Qualify the exact #332 + recovery behavior.
2. Continue **The Glass Archive** from the same frozen F2 checkpoint.
3. If a new material failure appears, classify its smallest owning layer and repair only that boundary.
4. If F2 and X3 both pass, reassess whether F3/X4 is actually warranted rather than promoting it automatically.

## Repository Simplification Direction

Preserve semantic rigor where it protects story authority:

```text
accepted story
+ Working candidate
+ source freshness
+ explicit promotion
```

Reduce administrative rigor that exists mainly to operate the repository itself. Prefer one independently verifiable semantic responsibility over arbitrary line-count-driven slicing, but protected factory-policy changes remain owner-only until committed through the repository's stated authority path.
