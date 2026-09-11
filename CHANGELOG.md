# Changelog

This file is the concise release index and post-release ledger for Auteur.

- Use [STATUS.md](STATUS.md) for the present-tense repository/development state.
- Use [docs/releases/](docs/releases/README.md) for release-specific evidence.
- Historical detailed changelog content previously stored here is preserved unchanged at [docs/releases/legacy-changelog-through-v0.12.0.md](docs/releases/legacy-changelog-through-v0.12.0.md).
- Do not infer that an open PR or experiment is shipped merely because it appears in repository history.

## Unreleased / `main` after v0.37.1

`pyproject.toml` still reports package version `0.37.1`. The items in this section describe development present on `main` after that release line; they are **not** a new release claim or version bump.

### Narrative Ontology V2 reconciliation

- Reconciled Layer 0 as the semantic substrate of the existing Narrative Architecture rather than a separate story-instance artifact pipeline.
- Added a typed, read-only `OntologyRegistry` backed by packaged YAML; `OntologyValidator` now consumes that registry instead of hardcoded Python concept/genre registries.
- Added modern Structure/Realization vocabulary (`StructuralBeat`, `Event`, `Fact`, `State`, `StateTransition`, `CharacterRelationship`) plus reusable relation-type vocabulary.
- Split ontology rules into schema constraints, deterministic semantic invariants, craft heuristics, and interpretive criteria; free-text conditions are documentation only, while deterministic execution uses named rule executors.
- Genre ontology extensions are discovered from packaged data; recognized product genres without an extension inherit the core ontology.
- Reconciled canonical Setup/Payoff semantics to many-to-many while preserving the historical Python facade as an explicit compatibility projection.
- Removed duplicate repository-root ontology YAML copies; `src/auteur/data/ontology/` is the single canonical specification location.
- ADR 020 ratifies medium-neutral `Entry` / `Segment` semantic vocabulary without migrating existing Book/Chapter persistence or authority.
- Added positive and rejection qualification for registry integrity, relation vocabulary, executable-rule behavior, legacy aliases, authority isolation, and scope compatibility.

### Guided author decision loop

- Decision-Oriented Tutor M1 is complete: deterministic Decision Cards, safe source-bound local sessions, root Tutor commands, stale-source blocking, and executable authority boundaries.
- Added Decision Handoff and a bounded Tutor-to-Structure proposal bridge while preserving the existing Structure ownership boundary.
- Added explicit Structure proposal inspect/select, fail-closed revision planning/validation, and fail-closed blueprint replacement validation.
- Added derived Narrative Change Preview and deterministic/read-only Decision Reassessment.
- Added dashboard Author Attention and the full hermetic Beginner Decision Loop.
- Added Guided Author Workspace V1 as a loopback-only, GET-only browser presentation with no mutation endpoints.
- Added a permanent full-suite Windows Python 3.13 CI leg alongside Linux validation and wheel smoke.

### Series / long-horizon productization posture

- Guided Series Continuity Review V1 and the bounded accepted-history/current-state/Global Map/Focus architecture are part of the current repository baseline.
- The long-horizon campaign remains `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION` with no active successor responsibility; no new long-horizon ontology experiment, automatic extraction, V2 review, or scale effort is authorized without a documented natural evidence trigger. The deterministic Narrative Ontology V2 reconciliation above is architecture-debt consolidation, not a campaign experiment or new long-horizon capability claim.

### Baseline stabilization

- PR #183 stabilized the Mode-B campaign baseline tests and promoted the qualified S15 tests-only baseline used by the current `main` head.

### Not shipped / superseded work

- PR #167 — historical bounded Episode 1 Direction implementation — closed / not merged / superseded; ADR 020 now supplies the medium-neutral Entry/Segment semantic direction while any future serial implementation remains separately gated.
- PR #166 — historical Windows CI candidate — closed / superseded; current CI now contains the later qualified Windows leg.

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
