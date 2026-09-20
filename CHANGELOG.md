# Changelog

## Version 1.0 candidate / development line

Auteur's package metadata on current `main` is `1.0.0`, and the repository contains bounded Version 1.0 support contracts and qualification history. This is **not** a published-release claim: remote GitHub release/tag inspection on 2026-09-20 shows no `v1.0.0` release/tag; the latest published release remains `v0.37.1`.

Qualification evidence is recorded against exact candidate SHAs in `docs/qualification-evidence/`. Publication still requires the explicit frozen-candidate and release steps in `docs/engineering/release-qualification.md`.

See [docs/1.0-scope.md](docs/1.0-scope.md),
[docs/engineering/public-api-contract.md](docs/engineering/public-api-contract.md),
and [docs/engineering/cli-contract.md](docs/engineering/cli-contract.md) for
the supported boundary and contract rules.

This file is the concise release index and post-release ledger for Auteur.

- Use [STATUS.md](STATUS.md) for the present-tense repository/development state.
- Use [docs/releases/](docs/releases/README.md) for release-specific evidence.
- Historical detailed changelog content previously stored here is preserved unchanged at [docs/releases/legacy-changelog-through-v0.12.0.md](docs/releases/legacy-changelog-through-v0.12.0.md).
- Do not infer that an open PR or experiment is shipped merely because it appears in repository history.

## Unreleased / `main` after v0.37.1

`pyproject.toml` now reports package version `1.0.0`. The items in this section describe development present on `main` after the last published `v0.37.1` release; the metadata change and candidate history are **not** themselves a published `v1.0.0` release claim.

### Guided author decision loop

- Decision-Oriented Tutor M1 is complete: deterministic Decision Cards, safe source-bound local sessions, root Tutor commands, stale-source blocking, and executable authority boundaries.
- Added Decision Handoff and a bounded Tutor-to-Structure proposal bridge while preserving the existing Structure ownership boundary.
- Added explicit Structure proposal inspect/select, fail-closed revision planning/validation, and fail-closed blueprint replacement validation.
- Added derived Narrative Change Preview and deterministic/read-only Decision Reassessment.
- Added dashboard Author Attention and the full hermetic Beginner Decision Loop.
- Added Guided Author Workspace V1 as a loopback-only, GET-only browser presentation with no mutation endpoints.
- Added a permanent full-suite Windows Python 3.13 CI leg alongside Linux validation and wheel smoke.

### Beginner story development continuation

- Added the accepted-foundation → outline → Chapter 1 plan → scene plan → draft handoff path.
- Added contemporary post-draft review and generalized Chapter N → N+1 continuation through PR #246: matching draft/review evidence, noncanonical revision handoff, explicit existing-owner acceptance delegation with replay reconciliation, accepted-outcome context, Structure divergence reporting, contextual next-chapter planning, and browser/API surfaces.
- Corrected commitment/Review authority routing through PR #250 so `commit accept` fails closed when Review cannot complete an owning authority transition.
- These are development integrations on `main`; they are not a new package release claim.

### Series / long-horizon productization posture

- Guided Series Continuity Review V1 and the bounded accepted-history/current-state/Global Map/Focus architecture are part of the current repository baseline.
- The long-horizon campaign is currently `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION` with no active successor responsibility; no new ontology, automatic extraction, V2 review, or scale effort is authorized without a documented natural evidence trigger.

### Baseline stabilization

- PR #183 stabilized the Mode-B campaign baseline tests and promoted the qualified S15 tests-only baseline used by the current `main` head.

### Not shipped / superseded work

- PR #167 — historical bounded Episode 1 Direction implementation — closed / not merged / superseded; contemporary bounded reconstruction is tracked in #218.
- PR #166 — historical Windows CI candidate — closed / superseded; current CI now contains the later qualified Windows leg.
- PRs #131, #221, #222, #225, #227, and #245 — historical/divergent branches reconciled on 2026-09-20; current responsibilities live on contemporary `main` or in issues #247/#248/#249/#251 rather than in those old branches.

## Released

### v0.37.1 — Post-Release Reliability and Authority Hardening

Release record: [docs/releases/v0.37.1.md](docs/releases/v0.37.1.md)

Key release scope: negation-aware Genre Pack applicability, explicit confirmation for authority-bearing recommendation override, and Pydantic V2 scene-state configuration migration.

### v0.37.0

Release record: [docs/releases/v0.37.0.md](docs/releases/v0.37.0.md)

See the release document for the exact release classification, qualification evidence, and compatibility claims.

## Historical Changelog

The previous detailed changelog is preserved **bit-for-bit** as a frozen historical artifact:

- [legacy-changelog-through-v0.12.0.md](docs/releases/legacy-changelog-through-v0.12.0.md)

That archive contains the older detailed entries that were previously at the repository root, including the v0.12.0 Narrative Decision Portfolio, v0.11.0 Counterfactual Narrative Planning, v0.10.0 Project-Level Narrative Planning, and earlier release notes.

Intermediate historical behavior and qualification should be reconstructed from release records, Git history, PR evidence, ADRs, and qualification documents rather than retroactively inventing missing changelog entries.

## Documentation Authority

For future maintenance:

- **Release claims:** `docs/releases/` and exact qualification evidence.
- **Current development state:** `STATUS.md`.
- **Durable product contract:** `MISSION.md` and `docs/PRD.md`.
- **Canonical domain model:** `docs/narrative-architecture.md`.
- **Historical decisions/evidence:** ADRs, campaign records, research, experiments, and qualification reports.

This separation keeps release history stable while allowing the living repository status to evolve.