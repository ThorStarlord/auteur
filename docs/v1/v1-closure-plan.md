# Auteur V1.0 Closure Plan

**Program type:** closure and qualification.  
**Selected baseline:** `main @ 2182da50f56df5a9bc139eb0b310cc18fd1d7e4a`.  
**Stop condition:** every `SUPPORTED`/`BOUNDED` contract item has the required implementation and evidence, or the contract is explicitly narrowed before candidate freeze.

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
- [ ] Replace every `VERIFY` disposition with implementation evidence or an explicit bounded/excluded disposition.

### WP-04 — Realization ↔ Expression boundary
- [x] Reconcile existing `docs/expression-boundary.md` with canonical architecture.
- [x] Preserve the rule: Expression may render/elaborate Realization but cannot silently redefine authority-bearing facts.
- [ ] Strengthen deterministic death tests around structured contradictions/upstream-review requirements where coverage is missing.

### WP-06/07 — Provenance/staleness closure
- [ ] Audit V1 authority-bearing artifact families against the matrix.
- [ ] Classify findings as already implemented, semantically equivalent, genuinely missing, derived/not required, or out of V1.
- [ ] Implement only genuine V1 blockers.

## Milestone 3 — Beginner control plane

### WP-08 — Application service boundary
- [ ] Ensure browser actions call typed application services rather than shelling out to CLI commands.
- [ ] Keep CLI and browser as adapters over the same authority operations.

### WP-09 — Guided Author Workspace V2
- [ ] Add bounded POST actions for the qualified Structure decision loop.
- [ ] Preserve explicit confirmation for canonical mutation.
- [ ] Return project orientation after each action.

### WP-10 — Local browser hardening
- [ ] loopback-only bind.
- [ ] Host/Origin validation.
- [ ] session CSRF token.
- [ ] POST-only mutation.
- [ ] project-root/path confinement.
- [ ] structured error outcomes and negative tests.

## Milestone 4 — Production reliability

### WP-11 — Provider failure contract
- [ ] Normalize missing/invalid auth, rate-limit, timeout, connection, provider 5xx, malformed response, structured-output invalid, retry exhaustion, and user interruption.
- [ ] Verify provider failure never creates partial canonical mutation.

### WP-12 — Real-provider qualification
- [ ] Add an opt-in release qualification runner for Anthropic.
- [ ] Add an opt-in release qualification runner for OpenAI.
- [ ] Record provider/model/candidate/package/evidence without claiming literary quality.

### WP-13 — Restart/recovery
- [ ] Detect/reconcile interrupted authority workflows.
- [ ] distinguish authoritative corruption from rebuildable derived-state failure.
- [ ] add crash/restart/corruption fixtures.

### WP-14 — Platform qualification
- [ ] Linux Python 3.11/3.12/3.13.
- [ ] Windows Python 3.13.
- [ ] canonical hash/path/line-ending/Unicode/timezone/locale/project-relocation checks required by the V1 matrix.

## Milestone 5 — Golden Author Journey

### WP-15 — realistic qualification fixture
- [ ] one Book-scale topology with 15–30 Chapters, 50–100 Scenes, multiple characters/relationships/setup-payoffs, at least one accepted structural revision, stale downstream state, restart/resume, and publication.
- [ ] prose volume may remain synthetic/bounded; state topology must exercise real cross-artifact behavior.

### WP-16 — automated journey
- [ ] premise → accepted Identity → Structure → Tutor decision → proposal → preview → explicit apply → staleness → Realization/Expression → restart → HTML/EPUB.
- [ ] record before/after authoritative hashes at every acceptance boundary.

### WP-17 — beginner owner dogfood
- [ ] traverse the core decision loop without raw YAML or implementation documentation.
- [ ] classify friction as UX/workflow/craft/domain/infrastructure before opening architecture.

## Milestone 6 — Release closure

### WP-18 — V1 completeness audit
- [ ] every required contract row is PASS or explicitly removed before freeze.
- [ ] no required row remains PARTIAL/UNKNOWN.

### WP-19 — exact candidate qualification
- [ ] clean/frozen SHA.
- [ ] full supported test matrix and repository verification.
- [ ] wheel/sdist hashes and fresh-install smoke.
- [ ] real-provider release smoke when credentials/authorization are available.
- [ ] Golden Author Journey.

### WP-20/21 — release record and publication
- [ ] finalize `1.0.0` metadata and release notes only after exact candidate evidence exists.
- [ ] satisfy source-qualified = artifact-built = installed-qualified = final-release/tag peeled commit.
- [ ] publish tag/GitHub Release only with explicit publication authorization.

## Package discipline

Each implementation package should have one primary problem, one authority boundary, focused positive tests, negative/rejection tests, required CI qualification, and documentation reconciliation. Do not combine unrelated architecture expansion with closure work.

## Failure rule

If a work package discovers a missing capability outside the current V1 Product Contract, classify it and preserve it as a candidate. Do not silently expand V1 scope. If it invalidates a promised V1 capability, either implement the smallest correct fix or explicitly narrow the contract before candidate freeze.
