# Auteur — Repository Status

**Last reconciled:** 2026-09-11  
**Reconciled baseline:** `main @ 783c592f85dcd1b2f96ee8e058087c9c8589150e`  
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
- Diagnostics, projections, recommendations, comparisons, maps, and Decision Cards are derived/advisory.
- Decision Cards are `DERIVED / NOT CANON`.
- Persisted Tutor sessions are `LOCAL / NONCANONICAL`.
- Story Design Packs and Genre Packs are reusable knowledge/context, not story-instance canon.
- Interactive genre sessions remain noncanonical until their documented compile/accept boundary.
- No Tutor response may silently accept StoryIdentity, rewrite a blueprint, repair Structure, or otherwise mutate accepted story state.
- Failure at an authority-bearing boundary must leave prior authoritative state intact.

## Stable Capability Families on `main`

The production baseline now includes:

- **Story Discovery and StoryIdentity** — multiple plausible story engines, recommendation, explicit author acceptance, and validation.
- **Genre knowledge and authoring** — Genre Packs, overrides, diagnostics, and interactive genre-pipeline infrastructure.
- **Structure engine** — generation, diagnosis, deterministic findings, and explicit diagnose → propose → select → apply repair lifecycle.
- **Story Design Packs** — reusable craft/design priors with deterministic composition.
- **Creative Writing Tutor V1** — legacy `auteur design tutor ...` guidance remains available.
- **Decision-Oriented Tutor M1** — deterministic Decision Cards, adapters from guidance/diagnostics, local atomic source-aware sessions, root `auteur tutor next/explain/show/choose`, stale-source blocking, and cross-system authority death tests.
- **Realization/state/provenance** — state coordination plus impact, convergence, decision, review, planning, simulation, and portfolio support.
- **Series / long-horizon infrastructure** — accepted-history/current-state reconstruction, derived Global Map/Focus, continuity support, and Guided Series Continuity Review V1.
- **Outline and drafting** — Cartographer outline compilation, chapter contracts, Bard/Critics drafting, retry, and explicit acceptance.

## Decision-Oriented Tutor M1 — Complete

All bounded M1 packages are implemented and qualified:

| Work item | Status | Result |
| --- | --- | --- |
| 0004 — Decision Card contract | ✅ | Stable semantic card identity and `DERIVED / NOT CANON` authority contract. |
| 0005 — Guidance/diagnostic adapters | ✅ | Existing guidance and Structure diagnostics can become Decision Cards without mutation. |
| #177 / 0006 — Safe Tutor advisory sessions | ✅ PR #187 | Atomic local persistence, source fingerprints, stale detection, advisory response lifecycle. |
| #178 / 0007 — Root Tutor workflow | ✅ PR #191 | `auteur tutor next/explain/show/choose`, human/JSON output, real project-source currentness checks. |
| #179 / 0008 — Authority-boundary death tests | ✅ PR #192 | Cross-system noncanon, staleness, no-repair, and canonical-file immutability proofs. |
| #180 / 0009 — Production Tutor documentation | ✅ current reconciliation | [docs/design/decision-oriented-tutor.md](docs/design/decision-oriented-tutor.md) documents the shipped workflow and exact authority boundary. |

The root workflow is intentionally advisory:

```text
Decision Card — DERIVED / NOT CANON
→ optional Tutor session — LOCAL / NONCANONICAL
→ author response
→ existing authority-bearing workflow if the story should change
```

`tutor choose` does not accept StoryIdentity, update `blueprint.yaml`, rewrite canon, or apply Structure repair.

## Current Selected Next Work — Beginner Decision Golden Path

With M1 complete, the next authorized activity is a bounded product-integration check rather than another foundational subsystem.

Exercise one beginner-style project through:

```text
raw premise
→ Story Discovery
→ explicit StoryIdentity acceptance
→ lightweight Structure
→ diagnostic / craft decision
→ Tutor Decision Card
→ explain / alternatives
→ author response
→ identify the existing authority-bearing next action
```

The purpose is to observe concrete product friction. Do not manufacture a favorable result and do not silently cross the authority boundary merely to complete the diagram.

Expected questions include:

- After `tutor choose`, can the author tell how to enact the choice safely?
- Is the surfaced decision relevant enough to current author intent?
- Do multiple subsystems compete for attention?
- Does the user understand advice versus canon?
- Does the workflow require reconstructing information Auteur already stores?

Select the next capability from observed evidence. The leading hypothesis is **Decision-to-Authority Handoff**, but it is not considered validated until the Golden Path produces that friction.

## Long-Horizon Campaign Posture

The long-horizon campaign remains `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION` with **no active implementation responsibility**.

Do not manufacture another long-horizon experiment; do not start new ontology, automatic extraction, V2 continuity-review, or scale expansion without the campaign's documented natural Auteur-native evidence trigger. Global Map/Focus remain derived/rebuildable projections rather than second canon.

See [docs/campaign/auteur-long-horizon-campaign-state.md](docs/campaign/auteur-long-horizon-campaign-state.md).

## Significant Work Not on `main`

- PR #167 — bounded Episode 1 Direction support: **OPEN / NOT MERGED**.
- PR #166 — full-suite Windows CI leg: **OPEN / NOT MERGED**.
- PR #184 — older M1 0006 candidate: **CLOSED / SUPERSEDED** by #187.
- PR #189 — first M1 0007 candidate: **CLOSED / SUPERSEDED** after its full-suite run exposed an unrelated README contract regression; #190 repaired that baseline and #191 was requalified cleanly.

Do not describe any open/unmerged PR as shipped behavior.

## Documentation Map

- [MISSION.md](MISSION.md) — durable mission, scope, invariants, human/automation boundary.
- [docs/PRD.md](docs/PRD.md) — product contract and primary-user requirements.
- [docs/narrative-architecture.md](docs/narrative-architecture.md) — canonical five-layer × scope architecture.
- [docs/design/decision-oriented-tutor.md](docs/design/decision-oriented-tutor.md) — shipped root Tutor workflow and authority/staleness model.
- [docs/opinionated-narrative-engine.md](docs/opinionated-narrative-engine.md) — product-design framing and guided authoring.
- [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md) — candidate directions and evidence gates; advisory, not implementation authority.
- [docs/architecture-roadmap.md](docs/architecture-roadmap.md) — architecture integrity/history, not the current product queue.
- [CONTEXT.md](CONTEXT.md) — runtime/domain terminology and compatibility context.
- [CHANGELOG.md](CHANGELOG.md) / [docs/releases/](docs/releases/README.md) — release history/evidence.

Historical ADRs, campaign records, qualification reports, experiments, and product-validation documents remain evidence and should not be rewritten into present-tense status reports.

## Release / Qualification Notes

`pyproject.toml` still reports `0.37.1`; `main` contains post-release development, so package metadata is not the complete current-state indicator.

- #187 exact candidate passed Validation before merge.
- #191 exact candidate passed the full Python 3.11/3.12/3.13 suites, repository verification, and installed-wheel smoke before merge.
- #192 is tests-only and passed focused boundary tests plus repository verification across the Python matrix; the production head it protects was already full-suite qualified by #191.
- #190 repaired the pre-existing README/CI contract surfaced by the first #178 qualification attempt.

Use `STATUS.md` for present development state and release records for release claims.

## Reconciliation Rule

When behavior changes materially, update living surfaces in this order:

1. `STATUS.md` — current state and next action.
2. `README.md` — when user-facing capability, framing, or entry path changes.
3. `CHANGELOG.md` / `docs/releases/` — for release history.
4. `CONTEXT.md` — for runtime/domain terminology or compatibility changes.
5. `docs/product-evolution-roadmap.md` — when candidate state, evidence gate, or product-evolution policy changes.
6. Mission, PRD, canonical architecture, ADRs, and historical evidence only through their own change processes.
