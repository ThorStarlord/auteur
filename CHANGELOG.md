# Changelog

This file is the concise release index and post-release ledger for Auteur.

- Use [STATUS.md](STATUS.md) for the present-tense repository/development state.
- Use [docs/releases/](docs/releases/README.md) for release-specific evidence.
- Historical detailed changelog content previously stored here is preserved unchanged at [docs/releases/legacy-changelog-through-v0.12.0.md](docs/releases/legacy-changelog-through-v0.12.0.md).
- Do not infer that an open PR or experiment is shipped merely because it appears in repository history.

## Unreleased / `main` after v0.37.1

`pyproject.toml` still reports package version `0.37.1`. The items in this section describe development present on `main` after that release line; they are **not** a new release claim or version bump.

### Decision-Oriented Tutor M1 foundation

- Added the deterministic `DecisionCard` contract for one bounded author-decidable creative decision.
- Decision Cards explicitly carry `DERIVED / NOT CANON` authority status.
- Added stable semantic card identity/source-fingerprint support.
- Added adapters from existing Story Design Pack Tutor guidance and deterministic structure diagnostics into Decision Cards without applying repairs or mutating story authority.
- Remaining M1 work is intentionally separate and still open: safe local Tutor sessions (#177), root `auteur tutor` workflow (#178), authority/staleness death tests (#179), and final root-workflow documentation (#180).

### Series / long-horizon productization posture

- Guided Series Continuity Review V1 and the bounded accepted-history/current-state/Global Map/Focus architecture are part of the current repository baseline.
- The long-horizon campaign is currently `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION` with no active successor responsibility; no new ontology, automatic extraction, V2 review, or scale effort is authorized without a documented natural evidence trigger.

### Baseline stabilization

- PR #183 stabilized the Mode-B campaign baseline tests and promoted the qualified S15 tests-only baseline used by the current `main` head.

### Not shipped from open PRs

The following are intentionally **not** listed as current production capability:

- PR #167 — bounded Episode 1 Direction support — open / not merged.
- PR #166 — full-suite Windows CI leg — open / not merged.

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
