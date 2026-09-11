# Auteur — Repository Status

**Last reconciled:** 2026-09-11  
**Selected program baseline:** `main @ 2182da50f56df5a9bc139eb0b310cc18fd1d7e4a`  
**Active implementation:** PR #222 — `work/v1-closure-program`  
**Package metadata:** `0.37.1` — **not yet `1.0.0`**  
**Role of this file:** living operational status and handoff; not a release record or idea backlog.

For the selected closure scope, read [docs/v1/v1-product-contract.md](docs/v1/v1-product-contract.md), [docs/v1/v1-closure-plan.md](docs/v1/v1-closure-plan.md), and [docs/v1/v1-completeness-audit.md](docs/v1/v1-completeness-audit.md). For durable product intent use [MISSION.md](MISSION.md) and [docs/PRD.md](docs/PRD.md); for the canonical domain model use [docs/narrative-architecture.md](docs/narrative-architecture.md).

## Current Selected Work — V1.0 Closure Program

Auteur has moved from architecture expansion to **contract closure and qualification**. The selected objective is:

> Close the existing architecture into a supportable `1.0.0` product contract. Stop when every capability promised by that contract has a complete authority-safe path, supported persistence/freshness semantics, beginner-operable entry where required, and release evidence on the supported runtime matrix.

This selection supersedes the previous `no additional product package implicitly authorized` posture only for bounded V1 closure. It does **not** authorize generalized Episode progression, universal ontology/extraction, generic graph infrastructure, 50/100+ Book scale architecture, cloud/collaboration, adaptive writer-skill state, or speculative craft-pack expansion.

## Current Product Direction

Auteur remains a local-first literary compiler and guided narrative-decision system for long-form fiction. The supported decision loop is:

```text
accepted narrative authority
→ derived context / diagnostics / craft knowledge
→ one bounded author decision
→ recommendation + trade-offs
→ explicit advisory response
→ derived authority handoff
→ concrete noncanonical proposal
→ explicit proposal selection
→ revision plan + validation
→ derived change preview
→ explicit owning-workflow authority action
→ bounded reassessment
→ project orientation
```

Derived systems may orient, diagnose, compare, explain, recommend, prepare, preview, and reassess. Determinism, persistence, currentness, UI selection, or user interaction do not grant story authority by themselves.

## Canonical Architecture

The five semantic layers remain **Ontology → Identity → Structure → Realization → Expression** across the independent **Universe → Series → Book → Chapter → Scene** scope axis. Scopes remain containers rather than extra layers.

The previously open Realization ↔ Expression seam is now specified for the bounded V1 Scene path in [docs/expression-boundary.md](docs/expression-boundary.md): Expression may render/elaborate accepted Realization but cannot silently redefine event/state facts. Structured contradictions can block Expression acceptance and produce a noncanonical upstream proposal; Realization changes still require an explicit owning-workflow action.

The emotional-trajectory contract remains post-v1/evidence-gated by default. V1 does not require a new semantic layer.

## V1 Closure Implementation on PR #222

The current branch adds the following bounded closure capabilities:

- **V1 Product Contract / claim ceiling** — exact supported scopes, interfaces, platform/provider posture, and explicit non-goals under `docs/v1/`.
- **Authority/provenance audit** — reconciles V1 authority-bearing families against existing ArtifactStore/dedicated lifecycle stores instead of creating a second canon database.
- **Realization ↔ Expression boundary service** — structured contradiction evidence makes a draft prose candidate review-required/invalid while leaving accepted Scene Realization unchanged.
- **Shared proposal/action services** — `ProposalReviewService` and `AuthorActionService` make CLI and browser adapters call the same application boundaries.
- **Guided Author Workspace V2** — loopback-only browser control plane for bounded Tutor/Structure actions with Host/Origin checks, session CSRF, POST-only mutation routes, project-path confinement, refreshed orientation, and a separate explicit confirmation before Structure authority changes.
- **Provider failure contract** — stable provider-independent auth/rate-limit/timeout/connection/5xx/malformed-response/retry-exhaustion categories while preserving bounded retry behavior.
- **Revision recovery** — `auteur structure revision recover` fail-closes plans stranded in `applying`; unchanged hash-proven targets may return to `ready`, but ambiguous changed targets become `failed` and are never replayed automatically.
- **V1 qualification harness** — a dedicated CI evidence job plus a 20-Chapter/60-Scene topology/restart/staleness test and platform invariants for line endings, semantic hashing, Unicode paths, and project relocation.
- **Opt-in live-provider runner** — records bounded Anthropic/OpenAI operational evidence without credentials or literary-quality claims.

## Authority Model

The central invariant remains explicit author authority.

- Story Discovery candidates remain advisory until explicit StoryIdentity acceptance.
- Decision Cards and handoffs are derived/noncanonical.
- Tutor sessions are local/noncanonical and source-currentness-bound.
- Structure proposals remain noncanonical through inspection and selection.
- Revision plans and Narrative Change Preview remain non-applying.
- `structure revision apply --confirm` remains the explicit Structure authority boundary.
- Workspace V2 calls the same application services and does not introduce a second acceptance system.
- Expression findings/upstream proposals never silently mutate Realization.
- Failure at an authority-bearing boundary must leave prior authoritative state intact unless a durable partial-application record explicitly says otherwise.

## V1 Scope Boundary

### Supported / bounded for the release contract

- Scene, Chapter, and Book authoring paths.
- Story Discovery / StoryIdentity.
- Structure diagnosis, proposal/revision, Tutor decision support, and project orientation.
- Scene Expression boundary and accepted Expression workflows.
- Book assembly/reconciliation and HTML/EPUB output.
- Bounded Series accepted-history/current-state/continuity support.
- Anthropic and OpenAI adapters when optional dependencies/credentials are available.
- Linux Python 3.11/3.12/3.13 and Windows Python 3.13, subject to exact release-candidate qualification.

### Experimental / outside the V1 authority-complete claim

- Universe remains optional supporting tooling rather than a provenance-normalized V1 authoring vertical.
- Episode 1 reconstruction remains future/experimental; issue #218 preserves the bounded contract.
- Episode 2+, season/general serial abstractions, and 50/100+ Book scale are not V1 claims.
- Automatic story-instance extraction, generic graph DB, cloud collaboration, and generic workflow engines remain out of scope.

## Qualification State

### Repository implementation evidence

The pre-closure baseline already had qualified Linux 3.11/3.12/3.13, Windows 3.13, repository verification, installed-wheel smoke, and the hermetic Beginner Decision Loop. The V1 closure PR is re-running the exact-head CI matrix and adds a dedicated `v1 closure evidence` job.

### Release gates still intentionally open

`1.0.0` must **not** be claimed or tagged until the exact frozen release candidate has all required evidence in [docs/v1/v1-qualification-matrix.md](docs/v1/v1-qualification-matrix.md), including:

1. exact-head Linux/Windows/repository/wheel qualification;
2. hermetic V1 closure evidence PASS;
3. authorized live Anthropic operational smoke;
4. authorized live OpenAI operational smoke;
5. bounded beginner owner dogfood of Workspace V2;
6. candidate freeze + final artifact qualification under the existing exact-release invariant.

Those external/owner gates cannot be replaced with synthetic claims. Package metadata therefore remains `0.37.1` during closure implementation.

## Serial / Long-Horizon Posture

Historical PR #167 remains closed/not merged/superseded. Issue #218 preserves the contemporary bounded Episode 1 Direction contract, but it is not selected V1 closure work.

The long-horizon campaign remains `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION`. Guided Series Continuity Review V1 and accepted-history/current-state mechanics are bounded product evidence; no new ontology, automatic extraction, Review V2, or scale program is authorized without its documented natural Auteur-native evidence trigger.

## Current Next Action

1. Let PR #222 qualify its exact code-bearing head through the full CI matrix and dedicated V1 evidence job.
2. Fix any concrete failing test/verification evidence at the smallest owning boundary.
3. Merge the closure implementation only after required PR-head CI passes.
4. After merge, run the remaining live-provider and owner-dogfood release gates on a frozen `1.0.0` candidate; do not publish/tag 1.0 before they pass.

## Documentation Map

- [V1 Product Contract](docs/v1/v1-product-contract.md) — exact 1.0 promise and claim ceiling.
- [V1 Closure Plan](docs/v1/v1-closure-plan.md) — selected program and remaining gates.
- [V1 Authority Artifact Matrix](docs/v1/v1-authority-artifact-matrix.md) — authority/provenance classification.
- [V1 Qualification Matrix](docs/v1/v1-qualification-matrix.md) — release evidence requirements.
- [V1 Completeness Audit](docs/v1/v1-completeness-audit.md) — implemented vs still-unqualified surfaces.
- [Guided Author Decision Loop](docs/guides/guided-author-decision-loop.md) — beginner decision workflow.
- [Product Evolution Roadmap](docs/product-evolution-roadmap.md) — preserved candidates/evidence gates outside selected closure work.
- [Canonical Narrative Architecture](docs/narrative-architecture.md) — five-layer × scope architecture.
- [Release Qualification](docs/engineering/release-qualification.md) — candidate/release evidence policy.
- [CHANGELOG.md](CHANGELOG.md) / [docs/releases/](docs/releases/README.md) — release history/evidence.

## Reconciliation Rule

When behavior changes materially, update living surfaces in this order:

1. `STATUS.md` — current state and next action.
2. `README.md` — user-facing capability/framing/entry path.
3. `CHANGELOG.md` / `docs/releases/` — release history.
4. `CONTEXT.md` — runtime/domain terminology or compatibility changes.
5. `docs/product-evolution-roadmap.md` — candidate state/evidence gate/product-evolution policy.
6. Mission, PRD, canonical architecture, ADRs, and historical evidence only through their own change processes.
