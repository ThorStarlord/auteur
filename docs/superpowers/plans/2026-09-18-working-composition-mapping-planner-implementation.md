# Working Composition and Mapping Planner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic, author-confirmed multi-dimension guidance and explicit promotion mapping to the Beginner Workspace without creating a second canonical narrative authority.

**Architecture:** Extend the Beginner session/application layer with a durable noncanonical `WorkingComposition` and deterministic Mapping Planner. Compose per-dimension proposals into a candidate `StoryIdentity`, show a promotion preview, and delegate final validation, canonical mutation, provenance, and semantic staleness to existing domain services. The browser renders projections and sends commands; it does not infer narrative meaning.

**Tech Stack:** Python 3.11, Pydantic 2, pytest, existing Auteur domain services, vanilla browser JavaScript, the existing local Beginner HTTP server.

**Spec:** `docs/superpowers/specs/2026-09-18-working-composition-mapping-planner-design.md`

## Global Constraints

- `WorkingComposition` is durable working/session state and is never canonical.
- Existing `StoryIdentity`, Structure, validation, provenance, acceptance, and staleness services remain authoritative.
- Pack selection, dimension confirmation, mapping proposals, and guidance never mutate canon without explicit milestone acceptance.
- Mapping Planner may perform preflight vocabulary checks and delegate candidate validation; it does not own final canonical validation or mutation.
- Semantic canonical changes, not labels, pack references, or provenance churn, determine downstream staleness.
- Rejected or deferred mappings do not deactivate their source dimensions.
- `INVALID_FOR_CURRENT_VOCABULARY` is a validation diagnostic, not a mapping disposition or review status.
- The first acceptance case is sanitized Mystery + superhero + relationship/thematic guidance.
- Do not add LLM inference, a canonical lens artifact, broad Genre Pack generalization, or unrelated Beginner UX polish.
- Preserve `uv.lock`, `.auteur/`, and unrelated user changes.
- Do not run human qualification during implementation; create the final candidate only after automated checks pass.

---

## Repository map and implementation boundaries

The implementation follows existing boundaries:

- `src/auteur/beginner/contracts.py`: session-envelope contracts and persisted working state.
- `src/auteur/beginner/persistence.py`: durable atomic session/revision persistence.
- `src/auteur/beginner/guidance.py`: derived guidance and consequence models.
- `src/auteur/beginner/mystery_adapter.py`: Mystery qualification inventory and domain evidence.
- `src/auteur/beginner/application.py`: commands, lifecycle, acceptance coordination, and revisions.
- `src/auteur/beginner/projections.py`: combined workspace read model.
- `src/auteur/beginner/server.py`: thin HTTP serialization and command routing.
- `src/auteur/beginner/browser/app.js`: presentation and command client only.
- `tests/test_beginner_workspace_contracts.py`: contract serialization and invariants.
- `tests/test_beginner_workspace_application.py`: orchestration and lifecycle behavior.
- `tests/test_beginner_workspace_authority.py`: canonical promotion and provenance.
- `tests/test_beginner_workspace_persistence.py`: atomicity, revisions, and recovery.
- `tests/test_beginner_workspace_server.py`: HTTP boundary.
- `tests/test_beginner_workspace_browser.py`: browser contract and presentation behavior.
- `tests/test_beginner_workspace_qualification.py`: end-to-end qualification scenarios.

No existing canonical artifact receives a new lens object in this plan.

## Task 0: Repository-contract preflight

**Files:**

- Read: `docs/narrative-architecture.md`
- Read: `docs/superpowers/specs/2026-09-18-working-composition-mapping-planner-design.md`
- Read: `src/auteur/identity.py`
- Read: `src/auteur/blueprint.py`
- Read: `src/auteur/genre_packs/models.py`
- Read: `src/auteur/story_design_packs/models.py`
- Read: `src/auteur/beginner/contracts.py`
- Read: `src/auteur/beginner/application.py`
- Read: `src/auteur/beginner/persistence.py`
- Read: `src/auteur/beginner/guidance.py`

- [ ] Verify the exact checked-out repository root, Git common directory, branch/worktree identity, and HEAD before implementation.
- [ ] Verify the current `StoryIdentity` fields and legal vocabulary used by the existing authority path.
- [ ] Verify how existing acceptance services represent candidates, provenance, command IDs, and semantic staleness.
- [ ] Verify the current session-envelope serialization and revision snapshot boundaries.
- [ ] Record any file/function boundary refinement in the implementation branch before proceeding; do not silently change the architecture.
- [ ] Commit the preflight note only if the executor needs a repository-grounded implementation note; otherwise keep the result as execution evidence.

Run:

```powershell
git rev-parse --show-toplevel
git rev-parse --git-common-dir
git rev-parse HEAD
pytest tests/test_beginner_workspace_contracts.py tests/test_beginner_workspace_authority.py -q
```

Expected: repository identity is explicit and the existing focused tests pass before changes.

## Task 1: Working composition contract

**Files:**

- Modify: `src/auteur/beginner/contracts.py`
- Test: `tests/test_beginner_workspace_contracts.py`

**Interfaces:**

- Produces Pydantic contracts for dimension category, origin, lifecycle, mapping disposition, review status, mapping strength, evidence class, tension records, and `WorkingComposition`.
- Produces strict serialization/deserialization suitable for the existing session envelope and revision snapshots.
- Does not create canonical Identity fields or mutate domain artifacts.

- [ ] Write failing tests for:
  - category/origin/status axis separation;
  - rejected/deferred mappings preserving active source dimensions;
  - strict enum validation;
  - complete author-override payload;
  - explicit tension record fields;
  - stable schema-versioned serialization;
  - revision-overlay identity.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_contracts.py -q
```

Expected: new tests fail because the composition contracts do not exist.

- [ ] Implement the smallest immutable/validated contracts compatible with the existing `SessionEnvelope` model.
- [ ] Ensure `INVALID_FOR_CURRENT_VOCABULARY` is represented as a validation diagnostic/result, not as disposition or review status.
- [ ] Add round-trip tests and verify the existing session contract tests remain green.
- [ ] Commit:

```powershell
git add src/auteur/beginner/contracts.py tests/test_beginner_workspace_contracts.py
git commit -m "feat: add beginner working composition contracts"
```

## Task 2: Per-dimension deterministic mapping

**Files:**

- Create: `src/auteur/beginner/mapping.py`
- Modify: `src/auteur/beginner/__init__.py` only if public exports are required by existing conventions
- Test: `tests/test_beginner_workspace_mapping.py`

**Interfaces:**

- `map_dimension(dimension, canonical_identity, domain_context) -> tuple[MappingRecord, ...]`
- `validate_author_override(mapping, override, canonical_vocabulary) -> OverrideValidationResult`
- `OverrideValidationResult.valid` is false with diagnostic `INVALID_FOR_CURRENT_VOCABULARY` for unsupported replacements.

- [ ] Write failing tests for:
  - direct Mystery mapping when the current domain supports it;
  - supported contribution when an existing destination is legal;
  - contextual-only mapping;
  - author-defined source provenance preservation;
  - unsupported override diagnostic;
  - rejected/deferred mapping preserving the confirmed source dimension;
  - no pack confirmation becoming canon automatically.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_mapping.py -q
```

Expected: FAIL because the mapping module and contracts are not implemented.

- [ ] Implement deterministic mapping rules that read existing vocabulary and pack metadata.
- [ ] Never invent a destination field or canonical value.
- [ ] Preserve source dimension, pack/version/hash, evidence class, rationale, and unmapped remainder.
- [ ] Run the mapping tests and the existing Identity validation tests.
- [ ] Commit:

```powershell
git add src/auteur/beginner/mapping.py tests/test_beginner_workspace_mapping.py
git commit -m "feat: add deterministic dimension mappings"
```

## Task 3: Composition and collision resolver

**Files:**

- Create: `src/auteur/beginner/composition.py`
- Test: `tests/test_beginner_workspace_mapping.py`

**Interfaces:**

- `compose_mappings(mappings, canonical_identity) -> CompositionResolution`
- `CompositionResolution` contains compatible contributions, collisions, candidate Identity data, and unmapped remainder.
- Composition order is stable for explanation but never changes semantics unless an explicit curated precedence rule applies.

- [ ] Write failing tests for:
  - compatible multi-source contributions;
  - conflicting values targeting one canonical field;
  - collision preservation with all source mappings;
  - unmapped remainder classification;
  - no silent field loss;
  - semantic candidate generation independent of incidental insertion order.
- [ ] Run the focused mapping tests and verify failure.
- [ ] Implement grouping, contribution merging, collision reporting, and candidate construction.
- [ ] Keep unsupported information in guidance/provenance rather than arbitrary canonical free-text fields.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_contracts.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/composition.py tests/test_beginner_workspace_mapping.py
git commit -m "feat: resolve composed identity mappings"
```

## Task 4: Promotion preview and semantic diff

**Files:**

- Create: `src/auteur/beginner/promotion.py`
- Modify: `src/auteur/beginner/projections.py` only for the preview projection
- Test: `tests/test_beginner_workspace_mapping.py`
- Test: `tests/test_beginner_workspace_application.py`

**Interfaces:**

- `build_promotion_preview(current_identity, resolution, existing_mapping_provenance) -> PromotionPreview`
- `PromotionPreview` exposes current Identity, candidate Identity, semantic diff, mapping explanations, unresolved items, dispositions, and downstream impact.
- Semantic diff excludes labels, pack references, provenance text, and working metadata.

- [ ] Write failing tests for:
  - canonical/context/provenance/unresolved classifications;
  - explicit mapping links for every proposed canonical change;
  - visible unmapped remainder;
  - unchanged semantic Identity producing no staleness;
  - semantic Identity change producing an impact record;
  - mapping collision blocking only when required for canonical coherence.
- [ ] Run the focused tests and verify failure.
- [ ] Implement preview composition over existing canonical artifacts; do not mutate canon.
- [ ] Delegate candidate validation to the existing domain service and retain diagnostics in the preview.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/promotion.py src/auteur/beginner/projections.py tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py
git commit -m "feat: add identity promotion preview"
```

## Task 5: Existing authority integration

**Files:**

- Modify: `src/auteur/beginner/application.py`
- Modify: `src/auteur/beginner/acceptance.py` if the preflight confirms the existing authority adapter needs a narrow mapping/provenance input
- Modify: `tests/test_beginner_workspace_authority.py`

**Interfaces:**

- Existing acceptance commands receive a validated promotion proposal and the existing idempotency/command identifier.
- Canonical mutation remains in the existing acceptance registry/service.
- Mapping provenance is recorded alongside the accepted canonical change.

- [ ] Write failing tests for:
  - no canonical mutation during detection, confirmation, or preview;
  - explicit acceptance required;
  - atomic Identity promotion with mapping provenance;
  - failed validation leaving prior canon unchanged;
  - idempotent retry not duplicating promotion;
  - semantic staleness only after changed canonical values;
  - pack/provenance-only changes not staling downstream artifacts.
- [ ] Run the authority tests and verify failure.
- [ ] Integrate the proposal with the existing authority boundary without duplicating acceptance logic.
- [ ] Preserve crash recovery, command receipts, and provenance behavior already tested by the Beginner Workspace.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_application.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/application.py src/auteur/beginner/acceptance.py tests/test_beginner_workspace_authority.py
git commit -m "feat: promote mapped identity through authority"
```

## Task 6: Durable session and revision persistence

**Files:**

- Modify: `src/auteur/beginner/contracts.py`
- Modify: `src/auteur/beginner/persistence.py`
- Modify: `src/auteur/beginner/application.py`
- Test: `tests/test_beginner_workspace_persistence.py`
- Test: `tests/test_beginner_workspace_application.py`

**Interfaces:**

- Working composition is persisted in the existing session envelope.
- Revision workspaces persist isolated composition overlays using existing revision paths and version checks.
- Session reload reconstructs the same working composition, mapping preview, and provenance references.

- [ ] Write failing tests for:
  - autosaved composition reload;
  - atomic session write;
  - revision overlay isolation;
  - cancellation restoring byte-equivalent canonical session state;
  - stale command rejection;
  - exact N+1 session version behavior;
  - crash recovery without duplicate canonical promotion.
- [ ] Run the persistence tests and verify failure.
- [ ] Add only the fields needed to persist working composition and mapping history; do not create a second store.
- [ ] Preserve existing locking, path containment, receipt ownership, and immutable revision semantics.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_application.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/contracts.py src/auteur/beginner/persistence.py src/auteur/beginner/application.py tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_application.py
git commit -m "feat: persist beginner composition revisions"
```

## Task 7: Composed guidance and Mystery adapter

**Files:**

- Modify: `src/auteur/beginner/guidance.py`
- Modify: `src/auteur/beginner/mystery_adapter.py`
- Modify: `src/auteur/story_design_packs/composition.py` only if preflight confirms a narrow reusable adapter is required
- Test: `tests/test_beginner_mystery_adapter.py`
- Test: `tests/test_beginner_workspace_application.py`

**Interfaces:**

- `guidance_for(card_id, session)` consumes confirmed working composition and returns derived guidance.
- Guidance exposes relevant semantic areas only when supported by the current decision.
- Guidance preserves pack provenance, dimension provenance, tension explanations, and unmapped remainder.

- [ ] Write failing tests for the sanitized hybrid case:
  - Mystery remains primary;
  - superhero guidance is surfaced when relevant;
  - relationship/thematic guidance is surfaced when relevant;
  - author-defined wording is preserved;
  - compatible tensions are explained rather than treated as errors;
  - unsupported content remains context/provenance;
  - no boilerplate empty semantic areas are emitted.
- [ ] Run the adapter/guidance tests and verify failure.
- [ ] Implement deterministic composition of existing knowledge sources.
- [ ] Keep the fixed Mystery card inventory as the first qualification fixture while allowing the composed context to enrich its guidance.
- [ ] Run:

```powershell
pytest tests/test_beginner_mystery_adapter.py tests/test_beginner_workspace_application.py tests/test_story_discovery_guidance.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/guidance.py src/auteur/beginner/mystery_adapter.py tests/test_beginner_mystery_adapter.py tests/test_beginner_workspace_application.py
git commit -m "feat: compose beginner narrative guidance"
```

## Task 8: Workspace projection and HTTP boundary

**Files:**

- Modify: `src/auteur/beginner/projections.py`
- Modify: `src/auteur/beginner/server.py`
- Modify: `src/auteur/beginner/application.py` for commands required by the projection
- Test: `tests/test_beginner_workspace_server.py`
- Test: `tests/test_beginner_workspace_application.py`

**Interfaces:**

- The combined workspace projection contains composition state, current Decision Card guidance, mapping preview, review readiness, canonical references, revision state, and available actions.
- HTTP serialization retains internal IDs for identity/provenance and exposes beginner-readable labels and explanations.
- Commands use expected session version and idempotency identifiers.

- [ ] Write failing boundary tests for:
  - GET returning one coherent composition/projection snapshot;
  - confirmation/rejection/author-defined dimension commands;
  - mapping review and override commands;
  - promotion preview;
  - invalid vocabulary diagnostics;
  - revision open/cancel/recompute behavior;
  - no browser-side authority mutation.
- [ ] Run the server tests and verify failure.
- [ ] Implement thin routing and serialization over application commands.
- [ ] Ensure the server does not duplicate mapping or domain rules.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_server.py tests/test_beginner_workspace_application.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/projections.py src/auteur/beginner/server.py src/auteur/beginner/application.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_application.py
git commit -m "feat: expose composition workspace boundary"
```

## Task 9: Browser composition and promotion review

**Files:**

- Modify: `src/auteur/beginner/browser/app.js`
- Modify: `src/auteur/beginner/browser/index.html`
- Modify: `src/auteur/beginner/browser/styles.css` only for required composition/review states
- Test: `tests/test_beginner_workspace_browser.py`

**Interfaces:**

- Browser renders server projections and sends commands only.
- Browser shows detected/proposed/confirmed/rejected dimensions, mapping dispositions, review statuses, tensions, unresolved items, and promotion preview.
- Browser clearly distinguishes working composition, guidance context, proposed canonical changes, and canonical state.

- [ ] Write failing browser contract tests for:
  - primary engine and supporting dimensions;
  - author confirmation/rejection;
  - author-defined lens;
  - tension acknowledgement;
  - mapping review and valid override;
  - invalid vocabulary feedback;
  - unmapped remainder visibility;
  - canonical preview before acceptance;
  - revision overlay and unchanged canon;
  - no raw internal identifiers as beginner-facing labels.
- [ ] Run the browser tests and verify failure.
- [ ] Implement only projection rendering and command dispatch; do not add narrative rules to JavaScript.
- [ ] Keep existing Story Navigator, Decision Card, Inspector, review, and revision semantics intact.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_server.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/browser/app.js src/auteur/beginner/browser/index.html src/auteur/beginner/browser/styles.css tests/test_beginner_workspace_browser.py
git commit -m "feat: render composed beginner guidance"
```

## Task 10: Qualification and regression gate

**Files:**

- Modify: `tests/test_beginner_workspace_qualification.py`
- Modify: `tests/fixtures/beginner_sealed_elevator.py` only for composition assertions that remain sanitized and fixture-stable
- Create: `tests/fixtures/beginner_hybrid_mystery.py`
- Modify: `docs/engineering/beginner-workspace-qualification.md` only after the candidate is verified

- [ ] Write failing qualification scenarios for:
  - Mystery + superhero + relationship/thematic dimensions;
  - explicit author confirmation;
  - rejected/deferred mapping preserving its source dimension;
  - compatible contribution and collision;
  - unmapped remainder;
  - author override;
  - atomic canonical promotion;
  - semantic-diff-only staleness;
  - revision isolation and cancellation;
  - failed promotion preserving canon.
- [ ] Run the focused qualification tests and verify failure.
- [ ] Implement the fixture assertions through the real Browser → HTTP → Application → authority boundary.
- [ ] Run focused Beginner tests:

```powershell
pytest tests/test_beginner_workspace_contracts.py tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_qualification.py -q
```

- [ ] Run the named integration slice and record collected, passed, skipped, xfailed, xpassed, failed, and error counts separately.
- [ ] Run exact-head L1 only after the implementation candidate is committed and pushed.
- [ ] Freeze the exact candidate SHA before human qualification.
- [ ] Create a fresh human workspace using a sanitized hybrid Mystery premise and perform the complete journey.
- [ ] Human qualification must verify:
  - dimensions are understandable;
  - the author can confirm/reject/add a lens;
  - guidance reflects relevant dimensions;
  - unmapped remainder is visible;
  - working versus canonical state is clear;
  - promotion preview is understandable;
  - canonical acceptance is explicit;
  - revision exploration does not mutate canon;
  - and no material friction appears.
- [ ] Do not mark human usability as passed from agent-observed browser automation.
- [ ] Update qualification evidence only after the independent human gate passes.

## Final self-review checklist

- [ ] Every requirement in the approved design has a corresponding task.
- [ ] No task creates a canonical lens artifact.
- [ ] No task moves authority into the browser or Mapping Planner.
- [ ] No task treats pack confirmation as canonical acceptance.
- [ ] No task makes provenance churn cause staleness.
- [ ] No task silently discards unmapped author intent.
- [ ] All new identifiers and interfaces are defined before later tasks consume them.
- [ ] The first acceptance case remains sanitized and reproducible.
- [ ] Implementation planning is complete, but production implementation remains gated on explicit plan approval.
