# Auteur — Current Repository Status

**Last reconciled:** 2026-10-07  
**Reconciled baseline:** `main @ 0c7ef04a55eddfb7bd4d5f621b78f26915a09f9f`  
**Latest published release:** `v0.37.1` (`pyproject.toml` `1.0.0` is not publication evidence)

Short operational handoff only; history belongs in Git, PRs, issues, qualification, and release records. Read [MISSION.md](MISSION.md), [docs/narrative-architecture.md](docs/narrative-architecture.md), and [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md).

## Current Frontier

**F2 — Small-Book Longitudinal Coherence + X3 — Persistent Book Workspace**  
Evidence surface: issue #318 and the frozen six-Chapter **The Glass Archive**.

Current `main` now contains the unqualified F2 implementation:
- #341 — unique atomic host-agent packet staging;
- #340 — filesystem-exclusive draft-version creation;
- #332 — Chapter-N host-agent orchestration;
- #335 — crash/replay recovery plus exact response/provenance binding.

```text
integrated implementation
-> run same controlled Book
-> first recurring material failure
-> smallest owning repair
-> rerun same checkpoint
```

F3/X4 is not selected.

## Quick Draft Runtime

Current `main` also contains the unqualified host-agent-first Quick Draft implementation:
- #334 — Book completion / pending-failure guarantee repairs;
- #336 — host-agent-first Browser/API/CLI path with replay/overwrite protection;
- #341 — shared atomic host-agent packet persistence.

Next evidence surface: issue #310, using the real target host-agent environment.

## Claim Ceiling

These changes are **integrated unqualified development work**.

```text
merged
!= exact-head tests passed
!= formal Implemented lifecycle state
!= regression checkpoint passed
!= release qualified
```

The owner explicitly chose to defer another mandatory exact-head Python rerun rather than block development. Existing regression tests remain executable specifications and should run when a suitable environment is available.

## Validation Posture

- **L1:** focused ordinary-development evidence.
- **L2:** only for a named changed boundary.
- **L3:** explicit stabilization/milestone/recovery checkpoint.
- **Release Qualification:** separate frozen-candidate lifecycle.
- GitHub Actions remain optional.

Current agent environment still has no runnable Auteur checkout: container DNS cannot resolve GitHub, the GitHub integration exposes no Codespaces/workflow-dispatch executor, and the connected Vercel project is unrelated infrastructure. This lowers the claim; it does not invalidate the integrated development state.

## Governance / External Gates

- **#338:** human protected commit — replace the absolute 500-line/12-file rejection rule and consolidate AGENTS/CLAUDE guidance.
- **#272:** GitHub admin — require PR-only `main`, no mandatory hosted Actions.
- **#295 / #218:** separate qualification lanes; neither blocks F2 product-use evidence.

The architecture admission guard is now integrated via #339: new durable architecture must be earned by observed frontier failure plus a behavioral distinction the existing model cannot express.

## Deferred

MANA, Progressive Commitment runtime states, F3+, generalized retrieval/vector search, new semantic layers/global story-state enums, Episode 2+ expansion, another first-session feature wave, and #248 post-F2 decomposition remain deferred.

## Next Trigger

1. Resume the same Glass Archive checkpoint in #318 against integrated `main`.
2. If it exposes a material recurring failure, repair the smallest owning boundary and rerun that checkpoint.
3. If F2/X3 succeeds at the intended product-use boundary, close/reconcile that frontier at the evidence-supported claim level and activate #248.
4. Run #310 real host-agent Quick Draft dogfood; specifically observe request fulfillment, first-scene adherence, provisional-assumption leakage, discovery behavior, latency, and whether Browser `awaiting_host_agent` is naturally fulfilled.
5. Let those two product-use surfaces choose any next repair; do not promote F3/X4 or invent a host bridge speculatively.

## Simplification Rule

```text
accepted story
+ Working candidate
+ source freshness
+ explicit promotion
```

Preserve rigor around story meaning/authority; reduce machinery that mainly administers the repository.
