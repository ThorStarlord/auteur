# Auteur — Current Repository Status

**Last reconciled:** 2026-10-07  
**Baseline:** `main @ ecc42ec2b9faeb4fc8037ce88b2379e44a4102d2`  
**Latest release:** `v0.37.1` (`pyproject.toml` `1.0.0` is not publication evidence)

Short operational handoff only; history belongs in Git, PRs, issues, qualification, and release records. Read [MISSION.md](MISSION.md), [docs/narrative-architecture.md](docs/narrative-architecture.md), and [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md).

## Current Frontier

**F2 — Small-Book Longitudinal Coherence + X3 — Persistent Book Workspace**  
Surface: issue #318 and frozen six-Chapter **The Glass Archive**.

```text
run controlled Book
-> first recurring material failure
-> smallest owning repair
-> rerun same checkpoint
```

F3/X4 is not selected.

## Current Failure

Bounded relevant Chapter-N context exists. Unresolved boundary:

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

F2 = #332 + #335 + #340 + #341. Quick Draft = #334 + #336 + #341. Exact-head Python execution is deferred rather than treated as a universal development gate.

Supporting review-ready PRs:
- #340 — filesystem-exclusive draft-version creation.
- #341 — unique atomic host-agent request/response staging.
- #337 — this compact STATUS.
- #339 — evidence-gated architecture admission.

Current main already establishes explicit author acceptance, local-first validation, persistent Book orientation, bounded relevant Chapter-N context, and the neutral host-agent request/response contract. Candidates are not canonical behavior and are not formal `Implemented` state until appropriate L1 evidence exists.

## Validation Posture

- **L1:** focused ordinary-development evidence.
- **L2:** only for a named changed boundary.
- **L3:** explicit stabilization/milestone/recovery checkpoint.
- **Release Qualification:** separate frozen-candidate lifecycle.
- GitHub Actions remain optional.

Current agent environment has no runnable checkout: container DNS cannot resolve GitHub, the GitHub integration exposes no Codespaces/workflow-dispatch executor, and the connected Vercel project is unrelated infrastructure. This lowers the claim; it does not block ordinary reversible work or owner-authorized development integration.

## Other Gates

- **#272:** GitHub admin — require PR-only `main`, no mandatory hosted Actions.
- **#338:** human protected commit — replace absolute 500-line/12-file rejection and consolidate AGENTS/CLAUDE guidance.
- **#310:** real host-agent Quick Draft dogfood after integration.
- **#295 / #218:** separate qualification lanes; neither blocks F2 work.

## Deferred

MANA, Progressive Commitment runtime states, F3+, generalized retrieval/vector search, new semantic layers/global story-state enums, Episode 2+ expansion, another first-session feature wave, and #248 post-F2 decomposition remain deferred.

## Next Trigger

1. Treat `d82b9384` as the **unqualified F2 integration candidate**; tests are deferred, not claimed passed.
2. Protected integration: #341 -> #340 -> #332 -> reconciled #335.
3. Resume the same Glass Archive checkpoint; repair only its next material failure or close F2/X3 at the evidence-supported claim level.
4. Treat `c418709e` as the **unqualified Quick Draft integration candidate**; protected integration: #341 -> #334 -> reconciled #336, then #310 dogfood.
5. Only after F2/X3 product-use success, resume #248 and reassess the next frontier.

## Simplification Rule

```text
accepted story
+ Working candidate
+ source freshness
+ explicit promotion
```

Preserve rigor around story meaning/authority; reduce machinery that mainly administers the repository.
