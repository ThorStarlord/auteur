# Auteur — Current Repository Status

**Last reconciled:** 2026-10-07  
**Reconciled baseline:** `main @ ecc42ec2b9faeb4fc8037ce88b2379e44a4102d2`  
**Latest published release:** `v0.37.1` (`pyproject.toml` metadata `1.0.0` is not publication evidence)

This file is a short operational handoff, not project history. Historical evidence belongs in Git, PRs, issues, qualification records, and release records.

Read [MISSION.md](MISSION.md) for product invariants, [docs/narrative-architecture.md](docs/narrative-architecture.md) for the semantic model, and [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md) for frontier policy.

## Current Frontier

**F2 — Small-Book Longitudinal Coherence + X3 — Persistent Book Workspace**

Qualification surface: issue #318 and the frozen six-Chapter **The Glass Archive** reference Book.

```text
run controlled Book
-> first material recurring failure
-> smallest owning repair
-> rerun same checkpoint
```

F3/X4 is not selected.

## Current Failure

Bounded relevant Chapter-N context exists. The unresolved product boundary is:

```text
contextual Chapter-N plan
-> author_context
-> exact host-agent request/response
-> freshness validation
-> one overwrite-safe Working draft
```

## Unqualified Integration Candidates

| Responsibility | Exact candidate |
| --- | --- |
| F2 Chapter-N generation | `qualify/f2-chapter-generation @ d82b938418b122a27ac29d695276aeee5dc6a812` |
| Quick Draft host-agent default | `qualify/quick-draft-host-agent @ c418709ea4d229c989d00a34de8e2037c29c6f73` |

F2 candidate contains #332 + #335 + #340 + #341. Quick Draft candidate contains #334 + #336 + #341. These branches are statically reviewed implementation candidates; exact-head Python execution is deferred rather than treated as a universal development gate.

Supporting draft PRs:
- #340 makes draft-version creation filesystem-exclusive.
- #341 gives host-agent request/response writes unique atomic staging files.
- #337 is this compact STATUS change.
- #339 gates new architecture on observed frontier evidence.

Listed PRs are review-ready unqualified candidates, not canonical behavior.

## Established Main Evidence

Current main already establishes explicit author acceptance, local-first validation, persistent Book orientation, bounded relevant Chapter-N context, and the neutral host-agent request/response contract.

Do not raise claims beyond the evidence available. These candidates may be integrated under an explicitly weakened development claim, but they are not `Implemented` under the formal release-state vocabulary until appropriate L1 evidence exists.

## Validation Posture

- **L1:** focused local evidence for ordinary development.
- **L2:** only for a named changed boundary.
- **L3:** explicit stabilization/milestone/recovery checkpoint.
- **Release Qualification:** separate frozen-candidate lifecycle.
- GitHub Actions remain optional remote execution.

Current agent environment cannot obtain a runnable checkout: local container DNS cannot resolve GitHub; the GitHub integration exposes no Codespaces/workflow-dispatch executor; the connected Vercel project is unrelated external infrastructure. This lowers the claim; it does not block ordinary reversible development or owner-authorized development integration.

## Other Gates

- **#272:** GitHub admin must require PR-only `main` without mandatory hosted Actions.
- **#338:** protected human commit must replace the absolute 500-line/12-file rejection rule and consolidate AGENTS/CLAUDE guidance.
- **#310:** real host-agent Quick Draft dogfood follows qualification/integration of its exact candidate.
- **#295 / #218:** separate qualification lanes; neither blocks F2 repository work.

## Deferred

MANA, Progressive Commitment runtime states, F3+, generalized retrieval/vector search, new semantic layers/global story-state enums, Episode 2+ expansion, another first-session feature wave, and #248 post-F2 decomposition remain deferred until their evidence gates are met.

## Next Trigger

1. Treat `d82b9384` as the current **unqualified F2 integration candidate**. Exact-head Python tests are deferred, not claimed passed.
2. When protected merge authority accepts the weakened claim, integrate #341 -> #340 -> #332 -> reconcile #335 onto contemporary main.
3. Resume the same Glass Archive checkpoint and let that controlled Book provide the next decision-relevant evidence.
4. Repair only the next observed material failure, or close F2/X3 mechanically at the claim level the returned evidence supports.
5. Treat `c418709e` as the current **unqualified Quick Draft integration candidate**; integrate #341 -> #334 -> reconciled #336 when protected authority accepts the weakened claim, then run #310 target-runtime dogfood.
6. Only after F2/X3 passes at the intended product-use boundary, resume #248 and reassess the next frontier.

## Simplification Rule

Preserve rigor where it protects story meaning and authority:

```text
accepted story
+ Working candidate
+ source freshness
+ explicit promotion
```

Reduce coordination machinery that exists mainly to operate the repository itself.
