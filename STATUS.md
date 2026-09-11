# Auteur — Repository Status

**Last reconciled:** 2026-09-11  
**Reconciled baseline:** `main @ 40add1a2726911bdf474e42cf9e6526491f244fd`  
**Package metadata:** `0.37.1`  
**Role of this file:** living operational status and handoff; not a release record or idea backlog.

For product intent, read [MISSION.md](MISSION.md) and [docs/PRD.md](docs/PRD.md). For the canonical domain model, read [docs/narrative-architecture.md](docs/narrative-architecture.md). For forward-looking candidates, read [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md). Release evidence lives under [docs/releases/](docs/releases/README.md).

## Current Product Direction

Auteur is a local-first literary compiler and guided narrative-decision system for long-form fiction. Its first valuable outcome is a coherent, author-understood whole-story direction followed by bounded decisions that preserve accepted narrative state.

```text
accepted narrative authority
        ↓
derived context / diagnostics / craft knowledge
        ↓
one bounded author decision
        ↓
advisory recommendation + trade-offs
        ↓
author response
        ↓
explicit existing story-authority workflow when canon should change
        ↓
accepted narrative authority
```

Derived systems may orient, diagnose, compare, explain, and recommend. Determinism, persistence, currentness, or user selection do not grant story authority.

## Canonical Architecture

Auteur retains five semantic layers: **Ontology → Identity → Structure → Realization → Expression**. The independent scope axis remains **Universe → Series → Book → Chapter → Scene**. Scopes are containers, not additional semantic layers. Validation, orchestration, diagnostics, provenance, maps, Tutor guidance, planning, simulation, and other workflow systems remain cross-cutting capabilities.

## Authority Model

The central invariant remains explicit author authority.

- Accepted/revisioned narrative artifacts are authoritative only through their documented acceptance paths.
- Diagnostics, projections, recommendations, comparisons, maps, Decision Cards, and future Decision Handoffs are derived/advisory.
- Decision Cards are `DERIVED / NOT CANON`.
- Persisted Tutor sessions are `LOCAL / NONCANONICAL`.
- Story Design Packs and Genre Packs are reusable knowledge/context, not story-instance canon.
- No Tutor response may silently accept StoryIdentity, rewrite a blueprint, repair Structure, or otherwise mutate accepted story state.
- Failure at an authority-bearing boundary must leave prior authoritative state intact.

## Stable Capability Families on `main`

The production baseline includes:

- **Story Discovery and StoryIdentity** — multiple plausible story engines, recommendation/search support, explicit author acceptance, and validation.
- **Genre knowledge and authoring** — Genre Packs, overrides, diagnostics, and interactive genre-pipeline infrastructure.
- **Structure engine** — generation, diagnosis, deterministic findings, and explicit diagnose → propose → select → apply/revision lifecycle.
- **Story Design Packs** — reusable craft/design priors with deterministic composition.
- **Creative Writing Tutor V1** — legacy `auteur design tutor ...` guidance remains available.
- **Decision-Oriented Tutor M1** — deterministic Decision Cards, guidance/diagnostic adapters, local atomic source-aware sessions, root `auteur tutor next/explain/show/choose`, stale-source blocking, and cross-system authority death tests.
- **Realization/state/provenance** — state coordination plus impact, convergence, decision, review, planning, simulation, and portfolio support.
- **Series / long-horizon infrastructure** — accepted-history/current-state reconstruction, derived Global Map/Focus, continuity support, and Guided Series Continuity Review V1.
- **Outline and drafting** — Cartographer outline compilation, chapter contracts, Bard/Critics drafting, retry, and explicit acceptance.

## Decision-Oriented Tutor M1 — Complete

All bounded M1 packages are merged and qualified:

| Work item | Status | Result |
| --- | --- | --- |
| 0004 — Decision Card contract | ✅ | Stable semantic card identity and `DERIVED / NOT CANON` authority contract. |
| 0005 — Guidance/diagnostic adapters | ✅ | Existing guidance and Structure diagnostics can become Decision Cards without mutation. |
| #177 / 0006 — Safe Tutor advisory sessions | ✅ PR #187 | Atomic local persistence, source fingerprints, stale detection, advisory response lifecycle. |
| #178 / 0007 — Root Tutor workflow | ✅ PR #191 | `auteur tutor next/explain/show/choose`, human/JSON output, real project-source currentness checks. |
| #179 / 0008 — Authority-boundary death tests | ✅ PR #192 | Cross-system noncanon, staleness, no-repair, and canonical-file immutability proofs. |
| #180 / 0009 — Production Tutor documentation | ✅ PR #193 | [docs/design/decision-oriented-tutor.md](docs/design/decision-oriented-tutor.md) documents the shipped workflow and authority boundary. |

## Beginner Decision Golden Path — Evidence Complete

The post-M1 product-integration verification is now implemented by `tests/test_beginner_decision_golden_path.py` and documented in [docs/reviews/beginner-decision-golden-path.md](docs/reviews/beginner-decision-golden-path.md).

The exercised path is:

```text
raw premise
→ Story Discovery candidates
→ explicit StoryIdentity acceptance
→ blueprint seed
→ root Tutor Decision Card
→ explanation
→ author `choose`
→ resolved local Tutor session
```

The path succeeds through a safe recorded choice while preserving accepted StoryIdentity and `blueprint.yaml` byte-for-byte.

### Observed product friction

After `tutor choose`, the session is correctly `resolved`, `LOCAL / NONCANONICAL`, and still carries a `DERIVED / NOT CANON` Decision Card. However, the resolved response does not tell a beginner which existing authoritative workflow should enact the selected design direction.

The missing bridge is therefore:

```text
resolved advisory choice
→ ???
→ existing authority-bearing story workflow
```

This is classified as a **workflow/product-integration gap**, not a missing semantic layer or ontology.

## Current Selected Work — Decision-to-Authority Handoff

**Implement a bounded derived Decision Handoff that routes a resolved Tutor choice to an existing authority-bearing workflow without performing that authoritative action.**

Minimum contract:

```text
resolved Tutor choice
→ derived Decision Handoff
→ affected layer/artifact candidates
→ recommended existing authority workflow
→ why this route
→ explicit noncanonical/no-mutation status
```

Required guardrails:

1. Handoff generation and inspection are derived/read-only with respect to narrative authority.
2. The handoff must not create a second acceptance/revision system.
3. It may point to Identity, Structure, Realization, or another existing authority path only when evidence supports that route.
4. Insufficient evidence must produce an explicit unresolved/inspection result rather than a guessed mutation path.
5. Stale Tutor sessions cannot yield an actionable handoff.
6. `tutor choose` remains local advisory state; canonical mutation still occurs only through the owning workflow.
7. Tests must keep authoritative sentinel artifacts byte-identical during handoff generation/inspection.

## Subsequent Candidates — Not Yet Authorized

The current strongest hypothesis after a successful handoff is **Narrative Change Preview**, followed by **Decision Reassessment** and then **Unified Project Orientation**. These remain candidates until the handoff is exercised and produces the corresponding friction.

Do not pre-authorize them merely because the roadmap contains them.

## Long-Horizon Campaign Posture

The long-horizon campaign remains `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION` with **no active implementation responsibility**.

Do not manufacture another long-horizon experiment; do not start new ontology, automatic extraction, V2 continuity-review, or scale expansion without the campaign's documented natural Auteur-native evidence trigger. Global Map/Focus remain derived/rebuildable projections rather than second canon.

See [docs/campaign/auteur-long-horizon-campaign-state.md](docs/campaign/auteur-long-horizon-campaign-state.md).

## Significant Work Not on `main`

- PR #167 — bounded Episode 1 Direction support: **OPEN / NOT MERGED**.
- PR #166 — full-suite Windows CI leg: **OPEN / NOT MERGED**.
- PR #184 — older M1 0006 candidate: **CLOSED / SUPERSEDED** by #187.
- PR #189 — first M1 0007 candidate: **CLOSED / SUPERSEDED**; #190 repaired the unrelated README contract regression and #191 was requalified cleanly.

Do not describe open/unmerged PRs as shipped behavior.

## Documentation Map

- [MISSION.md](MISSION.md) — durable mission, scope, invariants, human/automation boundary.
- [docs/PRD.md](docs/PRD.md) — product contract and primary-user requirements.
- [docs/narrative-architecture.md](docs/narrative-architecture.md) — canonical five-layer × scope architecture.
- [docs/design/decision-oriented-tutor.md](docs/design/decision-oriented-tutor.md) — shipped Tutor workflow and authority/staleness model.
- [docs/reviews/beginner-decision-golden-path.md](docs/reviews/beginner-decision-golden-path.md) — current product-integration evidence selecting the handoff gap.
- [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md) — candidate directions/evidence gates; advisory except where current selection is mirrored here.
- [docs/architecture-roadmap.md](docs/architecture-roadmap.md) — architecture integrity/history, not the current product queue.
- [CHANGELOG.md](CHANGELOG.md) / [docs/releases/](docs/releases/README.md) — release history/evidence.

## Release / Qualification Notes

`pyproject.toml` still reports `0.37.1`; `main` contains post-release development, so package metadata is not the complete current-state indicator.

The Golden Path package is a hermetic integration verification over existing capabilities. It makes no external-provider or subjective production-quality claim.

## Reconciliation Rule

When behavior changes materially, update living surfaces in this order:

1. `STATUS.md` — current state and next action.
2. `README.md` — when user-facing capability, framing, or entry path changes.
3. `CHANGELOG.md` / `docs/releases/` — for release history.
4. `CONTEXT.md` — for runtime/domain terminology or compatibility changes.
5. `docs/product-evolution-roadmap.md` — when candidate state, evidence gate, or product-evolution policy changes.
6. Mission, PRD, canonical architecture, ADRs, and historical evidence only through their own change processes.
