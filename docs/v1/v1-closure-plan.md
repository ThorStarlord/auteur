# Auteur V1.0 Closure Plan

**Program type:** closure and qualification.  
**Selected baseline:** `main @ 2182da50f56df5a9bc139eb0b310cc18fd1d7e4a`.  
**Stop condition:** every `SUPPORTED`/`BOUNDED` contract item has the required implementation and evidence, or the contract is explicitly narrowed before candidate freeze.

Checkboxes describe repository implementation. External/exact-candidate evidence remains explicitly open where it cannot be manufactured from repository-only work.

## Milestone 0 — Program selection

- [x] Reconcile current `main`, `STATUS.md`, PRD, Mission, architecture, release policy, and roadmap.
- [x] Establish `docs/v1/` as the bounded program record.
- [x] Freeze architecture-expansion work unless required by a V1 contract failure.

## Milestone 1 — Product contract

- [x] Define supported author journey.
- [x] Define scope/interface/platform/provider dispositions.
- [x] Define claim ceiling and V1 non-goals.
- [x] Reconcile README/STATUS/product roadmap to the selected program without claiming `1.0.0` released.

## Milestone 2 — Semantic and authority closure

### WP-03 — Authority-bearing artifact matrix
- [x] Create the V1 matrix.
- [x] Classify authority-bearing/derived/out-of-V1 families against implementation.

### WP-04 — Realization ↔ Expression boundary
- [x] Reconcile `docs/expression-boundary.md` with canonical architecture.
- [x] Preserve the rule: Expression may render/elaborate Realization but cannot silently redefine authority-bearing facts.
- [x] Add `ExpressionBoundaryService` and death tests: structured contradiction blocks acceptance while Scene Realization stays byte-identical.

### WP-06/07 — Provenance/staleness closure
- [x] Audit V1 authority-bearing artifact families.
- [x] Classify findings as already implemented, semantically equivalent, derived/not required, or out of V1.
- [x] Narrow Universe to experimental/optional rather than inventing a provenance-normalized V1 vertical.
- [x] Fix non-YAML semantic hashing so line endings/trailing spaces/Unicode NFC normalize correctly.
- [x] Propagate accepted Chapter upstream staleness into Book freshness.
- [x] Block publication of a transitively stale accepted Book.
- [x] No category-C need for a new provenance subsystem remains; preserve existing dedicated lifecycle stores.

## Milestone 3 — Beginner control plane

### WP-08 — Application service boundary
- [x] Extract Structure proposal review/selection into `ProposalReviewService`.
- [x] Add transport-neutral `AuthorActionService` over existing Tutor/Structure application operations.
- [x] CLI proposal selection and browser proposal selection use the same service; browser never shells out to CLI.

### WP-09 — Guided Author Workspace V2
- [x] Add bounded POST actions for Tutor choice/handoff/proposal and the qualified Structure decision loop.
- [x] Preserve separate explicit confirmation for canonical Structure mutation.
- [x] Return refreshed project orientation after actions.

### WP-10 — Local browser hardening
- [x] loopback-only bind.
- [x] Host/Origin validation.
- [x] session CSRF token.
- [x] POST-only mutation routes.
- [x] bounded request payloads.
- [x] project-root/path confinement.
- [x] structured blocked/error outcomes and negative tests.

## Milestone 4 — Production reliability

### WP-11 — Provider failure contract
- [x] Add stable provider-independent error codes for missing/invalid auth, rate limiting, timeout, connection, provider 5xx, malformed response, structured-output failure, retry exhaustion, user interruption, and unknown provider error.
- [x] Preserve bounded retry compatibility while making retry exhaustion explicit.
- [x] Type invalid Tutor→Structure generated JSON/schema/patch content as `structured_output_invalid` while preserving existing `ValueError` compatibility.
- [ ] Exact final-candidate tests must pass before provider behavior is release-qualified.

### WP-12 — Real-provider qualification
- [x] Add one opt-in release runner parameterized for Anthropic or OpenAI.
- [x] Bind evidence to the explicit candidate SHA and record provider/model/package/outcome without credentials or literary-quality claims.
- [ ] Run Anthropic smoke with authorized credentials on the frozen candidate.
- [ ] Run OpenAI smoke with authorized credentials on the frozen candidate.

### WP-13 — Restart/recovery/corruption
- [x] Add explicit `structure revision recover` for plans stranded in `applying`.
- [x] Return to `ready` only when hashes prove all authority targets unchanged.
- [x] Mark ambiguous changed/unverifiable target state `failed`; never automatically replay authority.
- [x] Add restart/recovery death tests.
- [x] Add authoritative Book corruption detection and derived publishing-record rebuildability tests.

### WP-14 — Platform invariants and qualification infrastructure
- [x] Add deterministic semantic-hash tests for CRLF/LF, trailing spaces, key order, and Unicode normalization.
- [x] Add Unicode artifact path and project-relocation tests.
- [x] Add locale/timezone-environment independence checks.
- [x] Bind the V1 evidence artifact to the true PR/candidate head rather than GitHub's synthetic pull-request merge SHA.
- [ ] Exact final candidate: Linux Python 3.11/3.12/3.13 PASS.
- [ ] Exact final candidate: Windows Python 3.13 PASS.
- [ ] Exact final candidate installed-wheel/repository verification PASS.

## Milestone 5 — Golden Author Journey

### WP-15 — realistic qualification fixture
- [x] Add a 20-Chapter / 60-Scene accepted-state topology with restart and downstream Expression staleness.
- [x] Add one continuous realistic fixture traversing accepted Scene Expression → Chapter Expression → Book Expression → HTML/EPUB publication.
- [x] In that fixture, revise one accepted Scene and prove Chapter→Book staleness plus publication rejection without silent rewriting.

### WP-16 — automated journey
- [x] Add `scripts/qualify_v1_author_journey.py` combining the beginner decision Golden Path, Workspace V2, Tutor structured-output bridge, Expression boundary, recovery, Book-scale topology, realistic Book journey, corruption/rebuildability, provider failure contract, platform invariants, and HTML/EPUB release tests.
- [x] Add a dedicated CI evidence job that uploads the exact-head result artifact.
- [ ] Exact final-candidate bundle PASS required before release.

### WP-17 — beginner owner dogfood
- [x] Add `workspace-v2-owner-dogfood.md` with exact steps, questions, evidence schema, friction classes, and decision rules.
- [ ] Perform the protocol on the frozen release candidate; repository automation cannot manufacture owner usability evidence.

## Milestone 6 — Release closure

### WP-18 — V1 completeness audit
- [x] Create `v1-completeness-audit.md` with implementation and remaining evidence separated.
- [x] Create `v1-release-candidate-checklist.md` for source/artifact/provider/owner/final-invariant qualification.
- [ ] Every required release-evidence row must be PASS or explicitly removed before freeze.

### WP-19 — exact candidate qualification
- [ ] clean/frozen SHA.
- [ ] full supported test matrix and repository verification.
- [ ] wheel/sdist hashes and fresh-install smoke.
- [ ] live-provider release smoke with authorized credentials.
- [ ] hermetic V1 author-journey bundle.
- [ ] owner Workspace V2 dogfood.

### WP-20/21 — release record and publication
- [ ] finalize `1.0.0` metadata and release notes only after exact candidate evidence exists.
- [ ] satisfy source-qualified = artifact-built = installed-qualified = final-release/tag peeled commit.
- [ ] publish tag/GitHub Release only after all release gates and publication authorization are satisfied.

## Repository implementation disposition

All work that can be implemented and honestly qualified through repository code/docs/tests in this closure program is represented above. The remaining unchecked items are **future-state evidence conditions** tied to a frozen final release candidate, external credentials/availability, owner usability, or final publication authorization. They must remain unchecked until those events actually occur.

## Package discipline

Each implementation package should have one primary problem, one authority boundary, focused positive tests, negative/rejection tests, required CI qualification, and documentation reconciliation. Do not combine unrelated architecture expansion with closure work.

## Failure rule

If a qualification run discovers a concrete defect, fix the smallest owning boundary and create a new exact candidate where required. If it discovers a missing capability outside the V1 Product Contract, preserve it as a candidate rather than silently expanding V1 scope.
