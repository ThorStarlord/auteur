# Changelog

This file is the concise release index and post-release ledger for Auteur.

- Use [STATUS.md](STATUS.md) for the present-tense repository/development state.
- Use [docs/releases/](docs/releases/README.md) for release-specific evidence.
- Historical detailed changelog content previously stored here is preserved unchanged at [docs/releases/legacy-changelog-through-v0.12.0.md](docs/releases/legacy-changelog-through-v0.12.0.md).
- Do not infer that an open PR, closure program, or experiment is released merely because it appears in repository history.

## Unreleased / V1.0 closure after v0.37.1

`pyproject.toml` still reports package version `0.37.1`. The items below describe development toward the V1 Product Contract; they are **not** a `1.0.0` release claim or version bump.

### V1 product and architecture closure

- Added `docs/v1/` with the explicit V1 Product Contract, claim ceiling, authority-bearing artifact matrix, closure plan, qualification matrix, provenance audit, and completeness audit.
- Narrowed the V1 promise instead of expanding architecture: Scene/Chapter/Book are supported authoring scopes; Series is bounded; Universe is experimental/optional context; generalized Episode progression and 50/100+ Book scale are outside the V1 claim.
- Reconciled the canonical Narrative Architecture so the bounded Realization ↔ Expression boundary is specified rather than listed as unresolved.
- Added `ExpressionBoundaryService` and death tests proving structured Realization contradictions can block prose acceptance and create only noncanonical upstream proposals while accepted Scene Realization remains unchanged.

### Beginner control plane

- Extracted `ProposalReviewService` so Structure proposal inspection/selection is shared by CLI and browser adapters rather than owned by CLI presentation code.
- Added transport-neutral `AuthorActionService` over Tutor/Structure application operations.
- Upgraded Guided Author Workspace to a bounded V2 control plane over those same application services.
- Workspace mutation is loopback-only and protected by Host/Origin validation, a session-specific CSRF token, POST-only action routes, bounded request bodies, project-path confinement, and separate explicit confirmation for the authority-bearing Structure apply action.
- Workspace actions refresh the existing Author Attention/dashboard projection; no second acceptance system or project-state database was introduced.

### Production reliability and recovery

- Added stable provider-independent LLM failure categories for missing/invalid credentials, rate limiting, timeouts, connection failure, provider 5xx, malformed responses, structured-output failure, retry exhaustion, user interruption, and generic provider transport failure.
- Retry exhaustion is explicit while retaining `RetriableError` compatibility for existing callers.
- Added `auteur structure revision recover`: plans stranded in `applying` return to `ready` only when target hashes prove no authority change; ambiguous changed/unverifiable targets become `failed`; authority is never automatically replayed.

### V1 qualification infrastructure

- Added a hermetic V1 author-journey runner combining the existing Beginner Decision Golden Path, Workspace V2, Realization/Expression boundary, revision recovery, provider failure contract, Book-scale topology/restart/staleness, platform invariants, and HTML/EPUB release tests.
- Added a dedicated `v1 closure evidence` CI job that records its exact-head evidence artifact.
- Added a 20-Chapter / 60-Scene accepted-state topology test with full process-store reconstruction and downstream Expression staleness after accepted Scene revision.
- Added cross-platform invariant tests for semantic YAML/Markdown hashing across line endings/key order/Unicode normalization, Unicode artifact paths, and project relocation.
- Added an opt-in live-provider qualification runner for Anthropic/OpenAI that records provider/model/candidate/package/outcome evidence without storing credentials or claiming literary quality.

### Release boundary

- `1.0.0` remains blocked on exact frozen-candidate qualification, authorized live Anthropic/OpenAI smokes, bounded owner usability dogfood of Workspace V2, and the existing exact release invariant.
- No `1.0.0` metadata/tag/GitHub Release is authorized by the closure implementation alone.

### Previously shipped guided author decision loop

- Decision-Oriented Tutor M1 is complete: deterministic Decision Cards, safe source-bound local sessions, root Tutor commands, stale-source blocking, and executable authority boundaries.
- Decision Handoff and a bounded Tutor-to-Structure proposal bridge preserve the existing Structure ownership boundary.
- Explicit Structure proposal inspect/select, fail-closed revision planning/validation, Narrative Change Preview, Decision Reassessment, dashboard Author Attention, and the hermetic Beginner Decision Loop are established baseline capabilities.
- The earlier Guided Author Workspace V1 was loopback-only and GET-only; the current V1 closure line supersedes that presentation limitation with the bounded Workspace V2 actions above.

### Series / long-horizon posture

- Guided Series Continuity Review V1 and the bounded accepted-history/current-state/Global Map/Focus architecture remain part of the repository baseline.
- The long-horizon campaign remains `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION`; no new ontology, automatic extraction, Review V2, generalized Episode progression, or scale program is authorized without its documented natural evidence trigger.

### Not shipped / superseded work

- PR #167 — historical bounded Episode 1 Direction implementation — closed / not merged / superseded; contemporary bounded reconstruction is tracked in #218 and is not a V1 blocker.
- PR #166 — historical Windows CI candidate — closed / superseded; current CI contains the later qualified Windows leg.

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

Intermediate historical behavior and qualification should be reconstructed from release records, Git history, PR evidence, ADRs, and qualification documents rather than retroactively inventing missing changelog entries.

## Documentation Authority

- **Release claims:** `docs/releases/` and exact qualification evidence.
- **Current development state:** `STATUS.md`.
- **V1 closure scope:** `docs/v1/v1-product-contract.md` and `docs/v1/v1-closure-plan.md`.
- **Durable product contract:** `MISSION.md` and `docs/PRD.md`.
- **Canonical domain model:** `docs/narrative-architecture.md`.
- **Historical decisions/evidence:** ADRs, campaign records, research, experiments, and qualification reports.
