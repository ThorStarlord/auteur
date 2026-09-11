# Auteur — Repository Status

**Last reconciled:** 2026-09-11  
**Reconciled implementation baseline:** `main @ 99e6c1d05760cce5cb721f7b585e4f85e481bdcc`  
**Package metadata:** `0.37.1`  
**Role of this file:** living operational status and handoff; not a release record or idea backlog.

The reconciled baseline includes the completed decision-loop product stack plus its beginner guide. Subsequent documentation-only reconciliation commits do not change the capability evidence summarized here.

For product intent, read [MISSION.md](MISSION.md) and [docs/PRD.md](docs/PRD.md). For the canonical domain model, read [docs/narrative-architecture.md](docs/narrative-architecture.md). For forward-looking candidates, read [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md). Release evidence lives under [docs/releases/](docs/releases/README.md).

## Current Product Direction

Auteur is a local-first literary compiler and guided narrative-decision system for long-form fiction. The current product loop is now executable end to end:

```text
accepted narrative authority
→ derived context / diagnostics / craft knowledge
→ one bounded author decision
→ advisory recommendation + trade-offs
→ explicit advisory response
→ derived authority handoff
→ concrete noncanonical proposal when supported
→ explicit proposal selection
→ revision plan + validation
→ derived change preview
→ explicit owning-workflow authority action
→ bounded reassessment
→ project orientation
```

Derived systems may orient, diagnose, compare, explain, recommend, prepare, preview, and reassess. Determinism, persistence, currentness, or user selection do not grant story authority.

## Canonical Architecture

Auteur retains five semantic layers: **Ontology → Identity → Structure → Realization → Expression**. The independent scope axis remains **Universe → Series → Book → Chapter → Scene**. Scopes are containers, not additional semantic layers. Validation, orchestration, diagnostics, provenance, maps, Tutor guidance, planning, simulation, dashboards, and browser presentation remain cross-cutting capabilities.

## Authority Model

The central invariant remains explicit author authority.

- Story Discovery candidates remain advisory until explicit StoryIdentity acceptance.
- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- Decision Handoffs are derived routing, not mutation.
- Tutor-generated Structure proposals are noncanonical working artifacts until explicitly selected.
- Structure revision plans and Narrative Change Preview are not applied story state.
- `structure revision apply --confirm` is the explicit Structure authority boundary in the qualified Tutor-to-Structure path.
- Decision Reassessment, Author Attention, Dashboard, and Guided Author Workspace V1 are read-only projections.
- Failure at an authority-bearing boundary must leave prior authoritative state intact.

## Stable Capability Families on `main`

The production baseline includes:

- **Story Discovery and StoryIdentity** — multiple plausible story engines, recommendation/search support, explicit author acceptance, and validation.
- **Genre knowledge and authoring** — Genre Packs, overrides, diagnostics, and interactive genre-pipeline infrastructure.
- **Story Design Packs / Tutor** — reusable craft priors, Decision Cards, source-aware Tutor sessions, `next/explain/show/choose/handoff/propose`, and stale-source blocking.
- **Structure engine** — generation/diagnostics plus explicit proposal inspect/select, fail-closed revision planning/validation, derived preview, confirmed application, and read-only reassessment.
- **Project orientation** — deterministic Author Attention in the existing dashboard and loopback-only Guided Author Workspace V1.
- **Realization/state/provenance** — state coordination plus impact, convergence, decision, review, planning, simulation, and portfolio support.
- **Series / long-horizon infrastructure** — accepted-history/current-state reconstruction, derived Global Map/Focus, continuity support, and Guided Series Continuity Review V1.
- **Outline and drafting** — Cartographer outline compilation, chapter contracts, Bard/Critics drafting, retry, and explicit acceptance.

## Decision-Loop Milestone — Complete

The evidence-led continuation after Tutor M1 is merged and qualified:

| Package | Result |
| --- | --- |
| Beginner Decision Golden Path | Exposed the missing post-choice authority route without mutating accepted story state. |
| Decision-to-Authority Handoff | Routes a resolved supported Tutor choice to the existing owning authority workflow without executing it. |
| Tutor → Structure Proposal Bridge | Produces one validated, unselected, noncanonical concrete Structure proposal. |
| Structure Proposal Review / Selection | Adds explicit inspect/select while keeping blueprint authority unchanged. |
| Revision continuation + fail-closed hardening | Selected Tutor proposals create meaningful plans; stale/invalid/destructive paths fail closed. |
| Narrative Change Preview | Read-only preview over existing revision/dependency evidence; no second impact engine. |
| Decision Reassessment | Re-runs exact native diagnostic evidence when available and returns `not_assessable` rather than inventing craft certainty. |
| Unified Project Orientation | Dashboard Author Attention prioritizes the next safe decision artifact/action. |
| Full Beginner Decision Loop | Hermetic integration proof crosses the explicit Structure authority boundary only at confirmed application. |
| Guided Author Workspace V1 | Local `127.0.0.1` GET-only beginner presentation over dashboard/attention semantics; no mutation endpoints. |

The beginner-facing walkthrough is [docs/guides/guided-author-decision-loop.md](docs/guides/guided-author-decision-loop.md).

## Qualification State

The code-bearing packages in the completed stack were qualified on their exact candidate heads with:

- Linux Python 3.11 / 3.12 / 3.13 validation;
- full Windows Python 3.13 test coverage;
- repository verification;
- installed-wheel smoke.

The full Golden Path proves:

1. StoryIdentity remains byte-identical through the complete Tutor/Structure decision loop.
2. `blueprint.yaml` remains byte-identical until explicit `structure revision apply --confirm`.
3. proposal selection, planning, validation, preview, and reassessment preserve their documented boundaries.
4. Tutor/craft reassessment does not manufacture a deterministic resolution claim.
5. after the blueprint changes, prior source-bound Tutor advice is surfaced as stale by project orientation.

This is hermetic repository evidence, not an external-provider or subjective story-quality claim.

## Current Selected Work

**No additional product package is implicitly authorized by the completed roadmap sequence.**

The next product package should be selected from observed use of the now-complete loop rather than extending ontology or adding another subsystem by default. Strong preserved candidates include:

- Unified Decision Inbox / broader attention-source coverage;
- Current Author Intent if relevance friction appears;
- demand-driven Story Design Pack growth;
- Existing-Manuscript Reverse Engineering;
- Book-Level Reasoning and Editing;
- bounded Episode 1 Direction reconstruction when the serial lane is deliberately selected.

A small discoverability follow-up may also be warranted if beginner use shows the new workspace/decision surfaces are hard to find from root CLI help. That is a UX problem, not a reason for new narrative architecture.

## Serial / Episode Posture

Historical PR #167 is **closed / not merged / superseded**. Its bounded Episode 1 Direction contract remains useful, but the old 4k-line implementation is not contemporary production evidence.

Fresh issue #218 preserves the reconstruction contract: Episode 1 remains a Series-scope, Identity-layer entry-unit Direction artifact for explicitly episodic Series and **does not become a sixth canonical scope**. Any future implementation must start from contemporary `main` in bounded packages.

Broader Episode 2+/season expansion remains subject to the separate long-horizon evidence gate.

## Long-Horizon Campaign Posture

The long-horizon campaign remains `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION` with **no active implementation responsibility**.

Do not manufacture another long-horizon experiment; do not start new ontology, automatic extraction, V2 continuity-review, or scale expansion without the campaign's documented natural Auteur-native evidence trigger. Global Map/Focus remain derived/rebuildable projections rather than second canon.

See [docs/campaign/auteur-long-horizon-campaign-state.md](docs/campaign/auteur-long-horizon-campaign-state.md).

## Repository / CI Notes

- Full-suite Windows Python 3.13 validation is now part of the current CI workflow; historical PR #166 is closed/superseded.
- Historical Episode 1 PR #167 is closed/superseded by contemporary reconstruction issue #218.
- Draft PR #131 is still open from an older Story Discovery composition baseline; it was **not assessed by this milestone** and must not be treated as shipped or current selected work without separate reconciliation.
- `pyproject.toml` still reports `0.37.1`; `main` contains post-release development, so package metadata alone is not the complete current-state indicator.

## Documentation Map

- [docs/guides/guided-author-decision-loop.md](docs/guides/guided-author-decision-loop.md) — beginner-facing end-to-end decision loop.
- [docs/design/decision-oriented-tutor.md](docs/design/decision-oriented-tutor.md) — Tutor/session/handoff authority and staleness model.
- [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md) — candidate directions/evidence gates.
- [docs/reviews/beginner-decision-golden-path.md](docs/reviews/beginner-decision-golden-path.md) — original post-M1 evidence that selected the handoff gap.
- [docs/narrative-architecture.md](docs/narrative-architecture.md) — canonical five-layer × scope architecture.
- [docs/architecture-roadmap.md](docs/architecture-roadmap.md) — architecture integrity/history, not the current product queue.
- [CHANGELOG.md](CHANGELOG.md) / [docs/releases/](docs/releases/README.md) — release history/evidence.

## Reconciliation Rule

When behavior changes materially, update living surfaces in this order:

1. `STATUS.md` — current state and next action.
2. `README.md` — when user-facing capability, framing, or entry path changes.
3. `CHANGELOG.md` / `docs/releases/` — for release history.
4. `CONTEXT.md` — for runtime/domain terminology or compatibility changes.
5. `docs/product-evolution-roadmap.md` — when candidate state, evidence gate, or product-evolution policy changes.
6. Mission, PRD, canonical architecture, ADRs, and historical evidence only through their own change processes.
