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
- [ ] Reconcile README/STATUS/product roadmap to the selected program after code qualification.

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
- [x] No category-C need for a new provenance subsystem was found; preserve existing dedicated lifecycle stores.

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
- [x] project-root/path confinement.
- [x] structured blocked/error outcomes and negative tests.

## Milestone 4 — Production reliability

### WP-11 — Provider failure contract
- [x] Add stable provider-independent error codes for missing/invalid auth, rate limiting, timeout, connection, provider 5xx, malformed response, structured-output failure, retry exhaustion, user interruption, and unknown provider error.
- [x] Preserve bounded retry compatibility while making retry exhaustion explicit.
- [ ] Exact-head tests must pass before this is qualified.

### WP-12 — Real-provider qualification
- [x] Add one opt-in release runner parameterized for Anthropic or OpenAI.
- [x] Record provider/model/candidate/package/evidence without credentials or literary-quality claims.
- [ ] Run Anthropic smoke with authorized credentials on the frozen candidate.
- [ ] Run OpenAI smoke with authorized credentials on the frozen candidate.

### WP-13 — Restart/recovery
- [x] Add explicit `structure revision recover` for plans stranded in `applying`.
- [x] Return to `ready` only when hashes prove all authority targets unchanged.
- [x] Mark ambiguous changed/unverifiable target state `failed`; never automatically replay authority.
- [x] Add restart/recovery death tests.
- [ ] Broader corruption/rebuildability matrix remains release qualification work.

### WP-14 — Platform qualification
- [ ] Exact final candidate: Linux Python 3.11/3.12/3.13.
- [ ] Exact final candidate: Windows Python 3.13.
- [ ] Final candidate artifact/platform invariants per `v1-qualification-matrix.md`.

## Milestone 5 — Golden Author Journey

### WP-15 — realistic qualification fixture
- [x] Add a hermetic 20-Chapter / 60-Scene accepted-state topology with restart and downstream Expression staleness.
- [ ] One continuous fixture combining full Book topology, structural revision, and publication remains a final qualification improvement; current bundle composes existing dedicated Golden Path and publishing evidence.

### WP-16 — automated journey
- [x] Add `scripts/qualify_v1_author_journey.py` combining the beginner decision Golden Path, Workspace, Expression boundary, recovery, Book-scale topology, provider failure contract, and HTML/EPUB release tests.
- [ ] Exact candidate bundle PASS required before release.

### WP-17 — beginner owner dogfood
- [ ] Traverse the core Workspace V2 loop without raw YAML or implementation documentation.
- [ ] Classify any friction as UX/workflow/craft/domain/infrastructure before opening architecture.

## Milestone 6 — Release closure

### WP-18 — V1 completeness audit
- [x] Create `v1-completeness-audit.md` with implementation and remaining evidence separated.
- [ ] Every required release-evidence row must be PASS or explicitly removed before freeze.

### WP-19 — exact candidate qualification
- [ ] clean/frozen SHA.
- [ ] full supported test matrix and repository verification.
- [ ] wheel/sdist hashes and fresh-install smoke.
- [ ] live-provider release smoke with authorized credentials.
- [ ] hermetic V1 author-journey bundle.

### WP-20/21 — release record and publication
- [ ] finalize `1.0.0` metadata and release notes only after exact candidate evidence exists.
- [ ] satisfy source-qualified = artifact-built = installed-qualified = final-release/tag peeled commit.
- [ ] publish tag/GitHub Release only after all release gates are satisfied.

## Package discipline

Each implementation package should have one primary problem, one authority boundary, focused positive tests, negative/rejection tests, required CI qualification, and documentation reconciliation. Do not combine unrelated architecture expansion with closure work.

## Failure rule

If a work package discovers a missing capability outside the current V1 Product Contract, classify it and preserve it as a candidate. Do not silently expand V1 scope. If it invalidates a promised V1 capability, either implement the smallest correct fix or explicitly narrow the contract before candidate freeze.
