# Auteur — Repository Status

**Last reconciled:** 2026-09-11  
**Reconciled baseline:** `main @ 50f5028409e3153385c22783a92ee032b6554bf9`  
**Package metadata:** `0.37.1`  
**Role of this file:** living operational status and handoff; not a release record or idea backlog.

For product intent, read [MISSION.md](MISSION.md) and [docs/PRD.md](docs/PRD.md). For the canonical domain model, read [docs/narrative-architecture.md](docs/narrative-architecture.md). For forward-looking product/repository candidates, read [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md). Release evidence lives under [docs/releases/](docs/releases/README.md).

The reconciled baseline includes the establishment of the dedicated Product Evolution Roadmap on `main` via PR #186 and the merged M1 0006 safe Tutor advisory-session capability via PR #187. Roadmap candidates remain advisory and do not change runtime capability or authorize implementation merely by being documented.

## Current Product Direction

Auteur is a local-first literary compiler and guided narrative-decision system for long-form fiction. Its intended beginner experience is not "generate prose immediately"; the first valuable outcome is a coherent, author-understood whole-story direction, followed by bounded decisions that preserve accepted narrative state.

The product direction is converging on this loop:

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

Derived systems can orient, diagnose, compare, explain, and recommend. They do not acquire story authority merely because their output is deterministic, persisted, or selected by a user.

## Canonical Architecture

Auteur retains five semantic layers:

1. **Ontology** — concepts, relationships, vocabulary, domain rules.
2. **Identity** — story commitments and intended experience.
3. **Structure** — plans, arcs, beats, threads, setup/payoff intentions.
4. **Realization** — events and state changes.
5. **Expression** — prose and language realization.

The scope axis remains **Universe → Series → Book → Chapter → Scene**. Scopes are containers across layers; they are not additional semantic layers.

Cross-cutting systems such as validation, orchestration, editing, diagnostics, provenance, versioning, Global Map/Focus, planning, simulation, portfolios, Story Design Packs, and Tutor guidance do not create new semantic layers.

## Authority Model

The repository's central invariant remains explicit author authority.

- Author-accepted/revisioned narrative artifacts are authoritative according to their documented acceptance paths.
- Diagnostics, projections, recommendations, maps, comparisons, and Decision Cards are derived or advisory.
- Story Design Packs and Genre Packs are reusable knowledge/context, not story-instance canon.
- Interactive genre sessions are noncanonical until explicitly compiled/accepted through their documented path.
- Tutor sessions are local/advisory state, not canonical story history.
- No recommendation should silently become StoryIdentity, rewrite a blueprint, repair Structure, or otherwise mutate accepted story state.
- Failure at an authority-bearing boundary must leave the prior authoritative state intact.

## Stable Capability Families on `main`

The current production baseline contains substantial capability beyond the original Story Discovery → Structure → Drafting path:

- **Story Discovery and StoryIdentity** — multiple plausible story engines, bounded recommendation, explicit author acceptance, and identity validation.
- **Genre knowledge and authoring** — Genre Packs, overrides, subgenre validation, and neutral interactive genre-pipeline infrastructure.
- **Structure engine** — top-down generation, bottom-up symptom diagnosis, deterministic findings, and explicit repair-proposal lifecycle.
- **Realization and state coordination** — state/provenance machinery plus impact, convergence, decision, review, planning, simulation, and portfolio support accumulated across prior releases.
- **Story Design Packs** — reusable craft/design priors with deterministic composition.
- **Creative Writing Tutor V1 surface** — current `auteur design tutor ...` guidance remains available and advisory.
- **Decision Card foundation** — deterministic `DecisionCard` contract plus adapters from existing Tutor guidance and deterministic diagnostics are present on `main`; Decision Cards are `DERIVED / NOT CANON`.
- **Safe Tutor advisory sessions** — M1 0006 is now on `main` via PR #187, including local atomic persistence, deterministic session identity, source-fingerprint currentness/staleness checks, advisory response lifecycle, and canonical-state immutability coverage. Tutor sessions remain `LOCAL / NONCANONICAL`.
- **Series / long-horizon infrastructure** — accepted-history/current-state reconstruction, derived Global Map/Focus machinery, continuity support, and Guided Series Continuity Review V1 exist within the bounded architecture already qualified by the long-horizon campaign.
- **Outline and drafting pipeline** — Cartographer outline compilation, chapter contracts, Bard/Critics drafting and explicit acceptance/retry flows remain downstream consumers.

## Active Milestone — Decision-Oriented Tutor M1

The semantic foundation and safe advisory-session layer are merged, but the root decision-oriented Tutor workflow is **not yet complete on `main`**.

| Work item | Status | Meaning |
| --- | --- | --- |
| 0004 — Decision Card contract | ✅ Implemented on `main` | Stable derived card identity/authority contract exists. |
| 0005 — Guidance/diagnostic adapters | ✅ Implemented on `main` | Existing Tutor guidance and diagnostics can become Decision Cards without mutation. |
| [#177 / 0006 — Safe Tutor advisory sessions](https://github.com/ThorStarlord/auteur/issues/177) | ✅ Implemented on `main` via PR #187 | Local atomic advisory-session persistence, fingerprints/currentness, staleness, and response lifecycle are merged without canonical mutation. |
| [#178 / 0007 — Root Tutor workflow](https://github.com/ThorStarlord/auteur/issues/178) | ⬜ Open — next | Add `auteur tutor next/show/explain/choose` over the merged card/session contracts. |
| [#179 / 0008 — Authority-boundary death tests](https://github.com/ThorStarlord/auteur/issues/179) | ⬜ Open | Make noncanon/staleness/side-effect boundaries executable regression invariants. |
| [#180 / 0009 — Decision-Oriented Tutor docs](https://github.com/ThorStarlord/auteur/issues/180) | ⬜ Open | Document the actual merged root workflow after 0007–0008 exist. |

### Required ordering

Continue the remaining milestone in dependency order:

```text
0007 root Tutor CLI
  → 0008 boundary/death tests
  → 0009 production Tutor documentation
```

Do not document nonexistent root Tutor flags or treat `tutor choose` as canonical story acceptance. The issue contract explicitly requires Tutor responses to remain advisory/local.

## Long-Horizon Campaign Posture

Current campaign posture is `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION` with **no active implementation responsibility**.

Guided Series Continuity Review V1 produced positive bounded usability evidence, but the campaign explicitly does not authorize a V2, new ontology, automatic extraction, or scale work until a naturally occurring Auteur-native later-entry planning case produces material evidence.

Therefore:

- do not manufacture another long-horizon experiment;
- do not start ontology/extraction/scale expansion speculatively;
- preserve Global Map/Focus as derived, rebuildable projections rather than second canon;
- return to campaign reassessment only when the documented evidence trigger occurs.

See [docs/campaign/auteur-long-horizon-campaign-state.md](docs/campaign/auteur-long-horizon-campaign-state.md).

## Significant Work Not on `main`

The following work must not be described as shipped production behavior:

- [PR #167 — bounded Episode 1 Direction support](https://github.com/ThorStarlord/auteur/pull/167): **OPEN / NOT MERGED**. It adds an explicitly episodic Series entry-unit Direction path without adding a sixth scope, but is not part of the current `main` baseline.
- [PR #166 — full-suite Windows CI leg](https://github.com/ThorStarlord/auteur/pull/166): **OPEN / NOT MERGED**. Current production CI should not be described as having this additional Windows leg until merged.

PR #184, an earlier candidate for M1 0006, is **closed without merge as superseded by PR #187** and should not be treated as active work or current qualification evidence.

## Recommended Next Development Action

**Implement #178 / M1 0007 — expose the root `auteur tutor next/show/explain/choose` workflow over the now-merged Decision Card and safe-session contracts.**

Why this is first:

1. Decision Cards and their adapters are already on `main`.
2. Safe local Tutor advisory sessions are now on `main` via PR #187.
3. The root Tutor CLI is the next missing user-facing integration step.
4. Authority death tests are most useful after the complete bounded root flow exists.
5. User-facing Tutor documentation should describe the real parser and merged behavior, not a planned interface.

After 0007–0009 are complete and qualified, run one end-to-end beginner decision loop as a product integration check before selecting another major capability family. Candidate directions beyond that point—including Decision-to-Authority Handoff, Narrative Change Preview, Decision Reassessment, Unified Project Orientation, Guided Author Workspace, and bounded serial progression—live in [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md) and do not become authorized merely by being listed there.

## Documentation Map

Use these documents for distinct purposes:

- [MISSION.md](MISSION.md) — durable mission, scope, invariants, and human/automation boundary.
- [docs/PRD.md](docs/PRD.md) — product contract and primary-user requirements.
- [docs/narrative-architecture.md](docs/narrative-architecture.md) — canonical five-layer × scope architecture.
- [docs/opinionated-narrative-engine.md](docs/opinionated-narrative-engine.md) — product-design framing, first value, guided authoring, Global Map/Decision Map/Focus model.
- [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md) — forward-looking candidate directions, evidence gates, and the product/repository evolution loop; advisory, not implementation authority.
- [docs/architecture-roadmap.md](docs/architecture-roadmap.md) — architecture integrity and architecture-specific extension history; not the current product queue.
- [CONTEXT.md](CONTEXT.md) — runtime/domain terminology and compatibility context.
- [STATUS.md](STATUS.md) — **current operational development state**.
- [CHANGELOG.md](CHANGELOG.md) — concise release index and post-release ledger.
- [docs/releases/](docs/releases/README.md) — release-specific evidence and historical release notes.
- ADRs, campaign records, qualification reports, experiments, and product-validation documents — historical decision/evidence records; do not rewrite them merely to make current status look cleaner.

## Release / Version Note

`pyproject.toml` currently reports package version `0.37.1`, while `main` also contains post-release development. Treat the package version as package metadata, not as a complete description of current development state.

Use:

- `STATUS.md` for what is currently present/pending on `main`;
- `docs/releases/v0.37.1.md` for the v0.37.1 release claim;
- `CHANGELOG.md` for the release index and unreleased ledger;
- Git history / PR qualification records for exact candidate evidence.

## Engineering / Qualification Notes

- The current `main` branch is not protected by a native GitHub branch-protection rule; repository safety therefore depends heavily on the documented PR, validation, qualification, and factory governance process.
- Code-bearing changes should follow the exact-candidate qualification rules in [docs/engineering/release-qualification.md](docs/engineering/release-qualification.md).
- Documentation-only changes should still be reviewed for executable-command accuracy, authority wording, broken links, and accidental claims about unmerged work.
- Historical qualification and product-validation documents are evidence. Preserve them rather than retroactively editing them into present-tense status reports.

## Reconciliation Rule for Future Sessions

When repository behavior changes materially, update the living surfaces in this order:

1. `STATUS.md` — current state and next action.
2. `README.md` — only if user-facing capability, product framing, or entry path changed.
3. `CHANGELOG.md` / `docs/releases/` — when release or post-release history changed.
4. `CONTEXT.md` — only when runtime/domain terminology or compatibility context changed.
5. `docs/product-evolution-roadmap.md` — only when candidate direction, selection state, evidence gate, or product-evolution policy changes.
6. Mission, PRD, canonical architecture, ADRs, and historical evidence — only when their own authority/change process explicitly requires it.

This keeps current state legible without rewriting the repository's decision history or turning future ideas into accidental production scope.
