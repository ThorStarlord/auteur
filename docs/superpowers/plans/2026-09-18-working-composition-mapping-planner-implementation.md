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
- [ ] Verify the current L1/L2/L3 policy in `docs/engineering/release-qualification.md`, `scripts/check.py`, and the current CI workflow before selecting the final validation commands.
- [ ] If any contract, authority boundary, or validation-policy assumption differs materially from this plan, stop execution. Amend and re-review this plan or the design specification before writing implementation code.
- [ ] Do not continue with a merely recorded mismatch; a material mismatch is a planning gate.

Run:

```powershell
git rev-parse --show-toplevel
git rev-parse --git-common-dir
git rev-parse HEAD
pytest tests/test_beginner_workspace_contracts.py tests/test_beginner_workspace_authority.py -q
```

Expected: repository identity is explicit and the existing focused tests pass before changes.

Concrete preflight record:

```text
repo_root = <git rev-parse --show-toplevel>
git_common_dir = <git rev-parse --git-common-dir>
head = <git rev-parse HEAD>
identity_authority = <verified module/function>
validation_policy = <verified L1/L2/L3 commands>
plan_assumptions_match = true
```

## Task 1: Working composition contract

**Files:**

- Modify: `src/auteur/beginner/contracts.py`
- Test: `tests/test_beginner_workspace_contracts.py`

**Interfaces:**

- Produces Pydantic contracts for dimension category, origin, lifecycle, mapping disposition, review status, mapping strength, evidence class, tension records, and `WorkingComposition`.
- Produces strict serialization/deserialization suitable for the existing session envelope and revision snapshots.
- Does not create canonical Identity fields or mutate domain artifacts.

Minimal contract shape:

```python
from auteur.story_design_packs.models import PackProvenance

class DimensionCategory(str, Enum):
    PRIMARY_ENGINE = "PRIMARY_ENGINE"
    GENRE_SUBGENRE = "GENRE_SUBGENRE"
    EMOTIONAL_AESTHETIC = "EMOTIONAL_AESTHETIC"
    RELATIONSHIP_THEMATIC = "RELATIONSHIP_THEMATIC"
    SETTING_WORLD = "SETTING_WORLD"

class DimensionOrigin(str, Enum):
    DETECTED_FROM_PACK = "DETECTED_FROM_PACK"
    INFERRED_FROM_STORY = "INFERRED_FROM_STORY"
    AUTHOR_DEFINED = "AUTHOR_DEFINED"
    AUTHOR_MODIFIED = "AUTHOR_MODIFIED"

class DimensionStatus(str, Enum):
    DETECTED = "DETECTED"
    PROPOSED = "PROPOSED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"

class MappingDisposition(str, Enum):
    MAPS_TO_CANON = "MAPS_TO_CANON"
    CONTRIBUTES_TO_CANON = "CONTRIBUTES_TO_CANON"
    GUIDANCE_CONTEXT = "GUIDANCE_CONTEXT"
    PROVENANCE_ONLY = "PROVENANCE_ONLY"
    REQUIRES_AUTHOR_DECISION = "REQUIRES_AUTHOR_DECISION"
    NOT_REPRESENTABLE_BY_CURRENT_DOMAIN = "NOT_REPRESENTABLE_BY_CURRENT_DOMAIN"
    NOT_RELEVANT_TO_THIS_MILESTONE = "NOT_RELEVANT_TO_THIS_MILESTONE"

class MappingReviewStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    OVERRIDDEN = "OVERRIDDEN"

class MappingStrength(str, Enum):
    DIRECT_DOMAIN_MAPPING = "DIRECT_DOMAIN_MAPPING"
    SUPPORTED_CONTRIBUTION = "SUPPORTED_CONTRIBUTION"
    CONTEXTUAL_INFLUENCE = "CONTEXTUAL_INFLUENCE"
    UNRESOLVED_INTERPRETATION = "UNRESOLVED_INTERPRETATION"

class EvidenceClass(str, Enum):
    DOMAIN_CONTRACT = "DOMAIN_CONTRACT"
    PACK_METADATA = "PACK_METADATA"
    CURATED_COMPOSITION_RULE = "CURATED_COMPOSITION_RULE"
    AUTHOR_CONFIRMED_DECISION = "AUTHOR_CONFIRMED_DECISION"
    EXISTING_CANONICAL_STATE = "EXISTING_CANONICAL_STATE"

class WorkingDimension(BaseModel):
    dimension_id: str
    category: DimensionCategory
    origin: DimensionOrigin
    status: DimensionStatus
    label: str
    author_rationale: str | None = None
    detection_evidence: tuple[str, ...] = ()
    source_provenance: tuple[PackProvenance, ...] = ()
    confirmed_by_author: bool = False

class CompositionTension(BaseModel):
    tension_id: str
    dimension_ids: tuple[str, ...]
    explanation: str
    affected_decision_or_contract: str
    acknowledged: bool = False
    blocks_acceptance: bool = False

class AuthorOverride(BaseModel):
    original_value: str
    replacement_value: str
    rationale: str
    affected_dimension_ids: tuple[str, ...]
    validation_result: str

class MappingRecord(BaseModel):
    mapping_id: str
    source_dimension_id: str
    source_category: DimensionCategory
    source_origin: DimensionOrigin
    source_provenance: tuple[PackProvenance, ...] = ()
    destination_field: str | None = None
    proposed_value: str | None = None
    contribution: str | None = None
    mapping_strength: MappingStrength
    evidence_class: EvidenceClass
    disposition: MappingDisposition
    review_status: MappingReviewStatus = MappingReviewStatus.PROPOSED
    rationale: str
    unmapped_remainder: tuple[str, ...] = ()
    author_override: AuthorOverride | None = None

class WorkingComposition(BaseModel):
    workspace_id: str
    composition_id: str
    schema_version: int
    revision_id: str | None = None
    base_canonical_refs: tuple[str, ...] = ()
    source_provenance: tuple[PackProvenance, ...] = ()
    dimensions: tuple[WorkingDimension, ...]
    tensions: tuple[CompositionTension, ...] = ()
    mapping_records: tuple[MappingRecord, ...] = ()

class DimensionProposalSet(BaseModel):
    proposals: tuple[WorkingDimension, ...]
    source_provenance: tuple[PackProvenance, ...] = ()

class MappingDomainContext(BaseModel):
    vocabulary: dict[str, tuple[str, ...]]
    source_provenance: tuple[PackProvenance, ...] = ()

class MappingCollision(BaseModel):
    destination_field: str
    mapping_ids: tuple[str, ...]
    explanation: str
    requires_author_decision: bool

class UnmappedRemainder(BaseModel):
    dimension_id: str
    text: str
    acknowledged: bool = False
    blocks_acceptance: bool = False

class SemanticChange(BaseModel):
    destination_field: str
    before: str | None = None
    after: str | None = None
    mapping_ids: tuple[str, ...] = ()
```

- [ ] Write failing tests for:
  - category/origin/status axis separation;
  - rejected/deferred mappings preserving active source dimensions;
  - strict enum validation;
  - complete author-override payload;
  - explicit tension record fields;
  - stable schema-versioned serialization;
  - revision-overlay identity.

Concrete red test:

```python
def test_rejected_mapping_does_not_reject_source_dimension():
    dimension = confirmed_dimension(category=DimensionCategory.RELATIONSHIP_THEMATIC)
    mapping = mapping_record(review_status=MappingReviewStatus.REJECTED)
    composition = WorkingComposition(dimensions=(dimension,), mapping_records=(mapping,))

    assert composition.dimensions[0].status is DimensionStatus.CONFIRMED
```
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_contracts.py -q
```

Expected: new tests fail because the composition contracts do not exist.

- [ ] Implement the smallest immutable/validated contracts compatible with the existing `SessionEnvelope` model.
- [ ] Add validators requiring a source dimension on every mapping and requiring an `author_override` payload to include original value, replacement value, rationale, affected dimension IDs, and validation result.
- [ ] Ensure `INVALID_FOR_CURRENT_VOCABULARY` is represented as a validation diagnostic/result, not as disposition or review status.
- [ ] Add round-trip tests and verify the existing session contract tests remain green.
- [ ] Commit:

```powershell
git add src/auteur/beginner/contracts.py tests/test_beginner_workspace_contracts.py
git commit -m "feat: add beginner working composition contracts"
```

## Task 2: Deterministic dimension detection and author confirmation

**Files:**

- Create: `src/auteur/beginner/dimensions.py`
- Modify: `src/auteur/beginner/contracts.py` only for the confirmed command payload already defined by Task 1
- Test: `tests/test_beginner_workspace_dimensions.py`
- Test: `tests/test_beginner_workspace_application.py`

**Interfaces:**

- `propose_dimensions(premise, guidance_genre, available_sources) -> DimensionProposalSet`
- `confirm_dimension(composition, dimension_id, *, label=None, rationale=None) -> WorkingComposition`
- `reject_dimension(composition, dimension_id, *, rationale=None) -> WorkingComposition`
- `add_author_dimension(composition, *, category, label, rationale) -> WorkingComposition`
- `DimensionProposalSet` preserves detection evidence and source pack/version/hash references.

- [ ] Write failing tests for the sanitized hybrid case:

```python
def test_proposes_mystery_superhero_and_relationship_dimensions():
    proposals = propose_dimensions(
        premise=HYBRID_MYSTERY_PREMISE,
        guidance_genre="mystery",
        available_sources=qualification_sources(),
    )

    assert [item.category for item in proposals.proposals] == [
        DimensionCategory.PRIMARY_ENGINE,
        DimensionCategory.SETTING_WORLD,
        DimensionCategory.RELATIONSHIP_THEMATIC,
    ]
    assert all(item.status is DimensionStatus.PROPOSED for item in proposals.proposals)
    assert all(item.detection_evidence for item in proposals.proposals)
```

- [ ] Add tests proving author confirmation changes only dimension lifecycle and rationale, not canonical Identity.
- [ ] Add tests proving rejection leaves the proposal in provenance and author-defined dimensions preserve exact wording.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_dimensions.py tests/test_beginner_workspace_application.py -q
```

Expected: FAIL because no deterministic detection or confirmation path exists.

- [ ] Implement curated, deterministic detection over existing pack applicability/source metadata. Do not infer a canonical genre or silently select a pack.
- [ ] Implement confirmation, rejection, and author-defined dimension operations as working-state transformations.
- [ ] Persist pack provenance and detection evidence in the returned composition projection.
- [ ] Use this detection algorithm: evaluate available sources against the premise; create one proposal per qualifying source/category; force the configured guidance genre into `PRIMARY_ENGINE`; preserve all other candidates as `PROPOSED`; never mark a proposal `CONFIRMED` during detection.
- [ ] Use this confirmation transition: copy the selected proposal, set `status=CONFIRMED`, set `confirmed_by_author=True`, record the rationale, and leave canonical artifacts untouched. Rejection changes only proposal status and provenance.
- [ ] Run the focused tests and verify canonical artifacts are byte-equivalent before and after confirmation.
- [ ] Commit:

```powershell
git add src/auteur/beginner/dimensions.py src/auteur/beginner/contracts.py tests/test_beginner_workspace_dimensions.py tests/test_beginner_workspace_application.py
git commit -m "feat: propose and confirm story dimensions"
```

## Task 3: Per-dimension deterministic mapping

**Files:**

- Create: `src/auteur/beginner/mapping.py`
- Modify: `src/auteur/beginner/__init__.py` only if public exports are required by existing conventions
- Test: `tests/test_beginner_workspace_mapping.py`

**Interfaces:**

- `map_dimension(dimension, canonical_identity, domain_context) -> tuple[MappingRecord, ...]`
- `validate_author_override(mapping, override, canonical_vocabulary) -> OverrideValidationResult`
- `OverrideValidationResult.valid` is false with diagnostic `INVALID_FOR_CURRENT_VOCABULARY` for unsupported replacements.

Minimal implementation shape:

```python
def map_dimension(
    dimension: WorkingDimension,
    canonical_identity: StoryIdentity,
    domain_context: MappingDomainContext,
) -> tuple[MappingRecord, ...]:
    # Return only destinations present in domain_context.vocabulary.
    raise NotImplementedError

class OverrideValidationResult(BaseModel):
    valid: bool
    diagnostic: str | None = None
    accepted_value: str | None = None
```

- [ ] Write failing tests for:
  - direct Mystery mapping when the current domain supports it;
  - supported contribution when an existing destination is legal;
  - contextual-only mapping;
  - author-defined source provenance preservation;
  - unsupported override diagnostic;
  - rejected/deferred mapping preserving the confirmed source dimension;
  - no pack confirmation becoming canon automatically.

Concrete red test:

```python
def test_unsupported_override_is_not_in_candidate_mapping():
    mapping = map_dimension(mystery_dimension(), empty_identity(), mystery_context())[0]
    result = validate_author_override(mapping, "invented-canonical-value", mystery_context().vocabulary)

    assert result.valid is False
    assert result.diagnostic == "INVALID_FOR_CURRENT_VOCABULARY"
```
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_mapping.py -q
```

Expected: FAIL because the mapping module and contracts are not implemented.

- [ ] Implement deterministic mapping rules that read existing vocabulary and pack metadata.
- [ ] Never invent a destination field or canonical value.
- [ ] Preserve source dimension, pack/version/hash, evidence class, rationale, and unmapped remainder.
- [ ] For each confirmed dimension, enumerate only the destination fields in `MappingDomainContext.vocabulary`; emit one direct mapping, contribution, contextual mapping, or unresolved record; attach the source dimension ID/category and exact source provenance to every record.
- [ ] Run the mapping tests and the existing Identity validation tests.
- [ ] Commit:

```powershell
git add src/auteur/beginner/mapping.py tests/test_beginner_workspace_mapping.py
git commit -m "feat: add deterministic dimension mappings"
```

## Task 4: Composition and collision resolver

**Files:**

- Create: `src/auteur/beginner/composition.py`
- Test: `tests/test_beginner_workspace_mapping.py`

**Interfaces:**

- `compose_mappings(mappings, canonical_identity) -> CompositionResolution`
- `CompositionResolution` contains compatible contributions, collisions, candidate Identity data, and unmapped remainder.
- Composition order is stable for explanation but never changes semantics unless an explicit curated precedence rule applies.

Minimal implementation shape:

```python
class CompositionResolution(BaseModel):
    candidate_identity: StoryIdentity
    mappings: tuple[MappingRecord, ...]
    collisions: tuple[MappingCollision, ...] = ()
    unmapped_remainder: tuple[UnmappedRemainder, ...] = ()
    blocking_items: tuple[str, ...] = ()

def compose_mappings(
    mappings: tuple[MappingRecord, ...],
    canonical_identity: StoryIdentity,
) -> CompositionResolution:
    raise NotImplementedError
```

- [ ] Write failing tests for:
  - compatible multi-source contributions;
  - conflicting values targeting one canonical field;
  - collision preservation with all source mappings;
  - unmapped remainder classification;
  - no silent field loss;
  - semantic candidate generation independent of incidental insertion order.

Concrete red tests:

```python
def test_acknowledged_nonrepresentable_remainder_does_not_block():
    result = compose_mappings((nonrepresentable_mapping(acknowledged=True),), identity())

    assert result.blocking_items == ()
    assert result.unmapped_remainder

def test_unresolved_primary_engine_blocks_identity_acceptance():
    result = compose_mappings((unresolved_primary_engine(),), identity())

    assert "primary_engine_mapping_required" in result.blocking_items
```
- [ ] Run the focused mapping tests and verify failure.
- [ ] Implement grouping, contribution merging, collision reporting, and candidate construction.
- [ ] Keep unsupported information in guidance/provenance rather than arbitrary canonical free-text fields.
- [ ] Group records by `destination_field`; merge records only when the existing vocabulary accepts their combined contribution; otherwise create a `MappingCollision` and add a blocking item only when the destination is required for Identity coherence.
- [ ] Build the candidate by applying accepted mappings to a copy of current Identity; never mutate the loaded canonical object.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_contracts.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/composition.py tests/test_beginner_workspace_mapping.py
git commit -m "feat: resolve composed identity mappings"
```

## Task 5: Promotion preview and semantic diff

**Files:**

- Create: `src/auteur/beginner/promotion.py`
- Modify: `src/auteur/beginner/projections.py` only for the preview projection
- Test: `tests/test_beginner_workspace_mapping.py`
- Test: `tests/test_beginner_workspace_application.py`

**Interfaces:**

- `build_promotion_preview(current_identity, resolution, existing_mapping_provenance) -> PromotionPreview`
- `PromotionPreview` exposes current Identity, candidate Identity, semantic diff, mapping explanations, unresolved items, dispositions, and downstream impact.
- Semantic diff excludes labels, pack references, provenance text, and working metadata.

Minimal implementation shape:

```python
class PromotionPreview(BaseModel):
    current_identity: StoryIdentity
    candidate_identity: StoryIdentity
    semantic_changes: tuple[SemanticChange, ...]
    mapping_records: tuple[MappingRecord, ...]
    unresolved_items: tuple[str, ...]
    blocking_items: tuple[str, ...]
    downstream_impact: tuple[str, ...]
    ready_to_accept: bool
```

- [ ] Write failing tests for:
  - canonical/context/provenance/unresolved classifications;
  - explicit mapping links for every proposed canonical change;
  - visible unmapped remainder;
  - unchanged semantic Identity producing no staleness;
  - semantic Identity change producing an impact record;
  - mapping collision blocking only when required for canonical coherence;
  - confirmed primary engine without a valid canonical mapping blocking Identity acceptance;
  - acknowledged nonrepresentable remainder remaining nonblocking;
  - tension acknowledgement changing a productive tension from attention-required to nonblocking;
  - pack/provenance-only changes producing an empty semantic diff.

Concrete red test:

```python
def test_preview_blocks_only_materially_unresolved_identity_mapping():
    preview = build_promotion_preview(identity(), unresolved_primary_resolution(), ())

    assert preview.ready_to_accept is False
    assert "primary_engine_mapping_required" in preview.blocking_items
```
- [ ] Run the focused tests and verify failure.
- [ ] Implement preview composition over existing canonical artifacts; do not mutate canon.
- [ ] Delegate candidate validation to the existing domain service and retain diagnostics in the preview.
- [ ] Compute semantic changes by comparing canonical Identity fields before and after the candidate; exclude composition labels, pack hashes, provenance text, and mapping review metadata from that diff.
- [ ] Set `ready_to_accept` only when domain diagnostics and the explicit blocking rules contain no blocking item.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/promotion.py src/auteur/beginner/projections.py tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py
git commit -m "feat: add identity promotion preview"
```

## Task 6: Existing authority integration

**Files:**

- Modify: `src/auteur/beginner/application.py`
- Modify: `src/auteur/beginner/acceptance.py` if the preflight confirms the existing authority adapter needs a narrow mapping/provenance input
- Modify: `tests/test_beginner_workspace_authority.py`

**Interfaces:**

- Existing acceptance commands receive a validated promotion proposal and the existing idempotency/command identifier.
- Canonical mutation remains in the existing acceptance registry/service.
- Mapping provenance is recorded alongside the accepted canonical change.
- Tension acknowledgement is a separate working-state command and never performs canonical mutation.

Minimal command shape:

```python
def accept_composed_identity(
    *,
    preview: PromotionPreview,
    command_id: str,
    expected_session_version: int,
) -> AcceptanceResult:
    # Validate, promote, record provenance, and reconcile atomically.
    raise NotImplementedError
```

- [ ] Write failing tests for:
  - no canonical mutation during detection, confirmation, or preview;
  - explicit acceptance required;
  - atomic Identity promotion with mapping provenance;
  - failed validation leaving prior canon unchanged;
  - idempotent retry not duplicating promotion;
  - semantic staleness only after changed canonical values;
  - pack/provenance-only changes not staling downstream artifacts.

Concrete red test:

```python
def test_failed_composed_acceptance_keeps_previous_identity(tmp_path):
    before = load_canonical_identity(tmp_path)
    with pytest.raises(BeginnerWorkspaceError):
        app.accept_composed_identity(invalid_preview(), command_id="c1", expected_session_version=version)

    assert load_canonical_identity(tmp_path) == before
```
- [ ] Run the authority tests and verify failure.
- [ ] Integrate the proposal with the existing authority boundary without duplicating acceptance logic.
- [ ] Preserve crash recovery, command receipts, and provenance behavior already tested by the Beginner Workspace.
- [ ] Execute acceptance in this order: acquire the existing command receipt; reload and version-check the session; validate the preview through the existing authority service; atomically write canonical Identity plus mapping provenance; compute semantic staleness; persist the refreshed session; complete the receipt; replay the stored result on retry.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_application.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/application.py src/auteur/beginner/acceptance.py tests/test_beginner_workspace_authority.py
git commit -m "feat: promote mapped identity through authority"
```

## Task 7: Durable session and revision persistence

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

Minimal persistence shape:

```python
class SessionEnvelope(BaseModel):
    # Existing fields remain unchanged.
    working_composition: WorkingComposition | None = None

class RevisionSnapshot(BaseModel):
    # Existing revision fields remain unchanged.
    working_composition: WorkingComposition | None = None
```

- [ ] Write failing tests for:
  - autosaved composition reload;
  - atomic session write;
  - revision overlay isolation;
  - cancellation restoring canonical artifact bytes and base composition while allowing expected session-version/receipt changes;
  - stale command rejection;
  - exact N+1 session version behavior;
  - crash recovery without duplicate canonical promotion.
  - exact pack ID, version, content hash, source dimension ID, and semantic source category surviving persistence/reload.

Concrete red test:

```python
def test_revision_cancel_preserves_canon_and_discards_overlay(tmp_path):
    canonical_before = (tmp_path / "story_identity.yaml").read_bytes()
    base_composition = store.load().working_composition
    version_before = store.load().session_version
    app.open_revision(stage="story_identity", revision_id="r1", command_id="open-1")
    app.confirm_dimension(dimension_id="relationship-lens", command_id="confirm-1")
    app.cancel_revision(revision_id="r1", command_id="cancel-1")

    assert (tmp_path / "story_identity.yaml").read_bytes() == canonical_before
    assert store.load().working_composition == base_composition
    assert not store.revision_session_path("r1").exists()
    assert store.load().session_version > version_before
```

Concrete provenance round-trip test:

```python
def test_pack_provenance_round_trips_with_dimension_role(tmp_path):
    provenance = PackProvenance(pack_id="superhero", version="0.1.0", content_hash="sha256:fixture")
    composition = hybrid_composition(
        source_provenance=(provenance,),
        category=DimensionCategory.SETTING_WORLD,
    )
    store.save(replace_session(working_composition=composition))

    loaded = store.load().working_composition
    assert loaded.dimensions[0].source_provenance[0].model_dump() == provenance.model_dump()
    assert loaded.dimensions[0].category is DimensionCategory.SETTING_WORLD
    assert loaded.mapping_records[0].source_dimension_id == loaded.dimensions[0].dimension_id
    assert loaded.mapping_records[0].source_category is DimensionCategory.SETTING_WORLD
```
- [ ] Run the persistence tests and verify failure.
- [ ] Add only the fields needed to persist working composition and mapping history; do not create a second store.
- [ ] Preserve existing locking, path containment, receipt ownership, and immutable revision semantics.
- [ ] Serialize `WorkingComposition` through the existing session envelope writer and revision snapshot writer; load it before projection; on cancel delete only the revision overlay and restore the base working composition while retaining normal version/receipt bookkeeping.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_application.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/contracts.py src/auteur/beginner/persistence.py src/auteur/beginner/application.py tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_application.py
git commit -m "feat: persist beginner composition revisions"
```

## Task 8: Composed guidance and Mystery adapter

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

Minimal implementation shape:

```python
def guidance_for(card_id: str, session: SessionEnvelope) -> BeginnerGuidance:
    composition = session.working_composition
    context = compose_guidance_context(card_id, composition, session)
    return build_beginner_guidance(card_id, session, context)
```

- [ ] Write failing tests for the sanitized hybrid case:
  - Mystery remains primary;
  - superhero guidance is surfaced when relevant;
  - relationship/thematic guidance is surfaced when relevant;
  - author-defined wording is preserved;
  - compatible tensions are explained rather than treated as errors;
  - unsupported content remains context/provenance;
  - no boilerplate empty semantic areas are emitted.

Concrete differential test:

```python
def test_confirmed_supporting_dimensions_change_provenance_traced_guidance():
    mystery_only = guidance_for("story_identity.relationship-pressure", mystery_session())
    hybrid = guidance_for("story_identity.relationship-pressure", hybrid_session())

    assert mystery_only.recommendation != hybrid.recommendation or mystery_only.option_impacts != hybrid.option_impacts
    assert hybrid.context_guidance.pack_sources
    assert any("superhero" in source.pack_id or "relationship" in source.pack_id
               for source in hybrid.context_guidance.pack_sources)
    assert "mystery" in {source.pack_id for source in hybrid.pack_sources}
```
- [ ] Run the adapter/guidance tests and verify failure.
- [ ] Implement deterministic composition of existing knowledge sources.
- [ ] Keep the fixed Mystery card inventory as the first qualification fixture while allowing the composed context to enrich its guidance.
- [ ] Build guidance context by starting with Mystery card evidence, selecting confirmed supporting dimensions relevant to the card, composing their curated contributions, and attaching source dimension IDs and pack provenance to each derived consequence.
- [ ] Emit a semantic area only when at least one nonblank relevant consequence exists; never manufacture empty emotional, relationship, or trope sections.
- [ ] Run:

```powershell
pytest tests/test_beginner_mystery_adapter.py tests/test_beginner_workspace_application.py tests/test_story_discovery_guidance.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/guidance.py src/auteur/beginner/mystery_adapter.py tests/test_beginner_mystery_adapter.py tests/test_beginner_workspace_application.py
git commit -m "feat: compose beginner narrative guidance"
```

## Task 9: Workspace projection and HTTP boundary

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
- `BeginnerWorkspaceApplication.acknowledge_tension(tension_id, *, expected_session_version, command_id) -> WorkspaceProjection` updates only working composition state and returns the refreshed projection.

Required command routes (slugs may follow existing naming conventions):

```text
POST /api/beginner/workspaces/{id}/dimensions/confirm
POST /api/beginner/workspaces/{id}/dimensions/reject
POST /api/beginner/workspaces/{id}/dimensions/add
POST /api/beginner/workspaces/{id}/tensions/acknowledge
POST /api/beginner/workspaces/{id}/mapping/review
POST /api/beginner/workspaces/{id}/mapping/preview
POST /api/beginner/workspaces/{id}/milestones/accept
```

Every mutating payload includes `command_id` and `expected_session_version`.
Every successful response returns the refreshed combined workspace projection.

- [ ] Write failing boundary tests for:
  - GET returning one coherent composition/projection snapshot;
  - confirmation/rejection/author-defined dimension commands;
  - mapping review and override commands;
  - promotion preview;
  - invalid vocabulary diagnostics;
  - revision open/cancel/recompute behavior;
  - no browser-side authority mutation.

Concrete red boundary test:

```python
def test_acknowledge_tension_returns_updated_projection(http_client):
    response = http_client.post(
        "/api/beginner/workspaces/w1/tensions/acknowledge",
        json={"tension_id": "t1", "command_id": "c1", "expected_session_version": 4},
    )

    assert response.status_code == 200
    assert response.json()["tensions"]["t1"]["acknowledged"] is True
    assert response.json()["canonical_refs"] == []
```
- [ ] Run the server tests and verify failure.
- [ ] Implement thin routing and serialization over application commands.
- [ ] Ensure the server does not duplicate mapping or domain rules.
- [ ] Route each command to the application with its command ID and expected session version, then serialize the single refreshed projection; `acknowledge_tension` updates the tension record and readiness only, while promotion routes exclusively to the existing acceptance command.
- [ ] Run:

```powershell
pytest tests/test_beginner_workspace_server.py tests/test_beginner_workspace_application.py -q
```

- [ ] Commit:

```powershell
git add src/auteur/beginner/projections.py src/auteur/beginner/server.py src/auteur/beginner/application.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_application.py
git commit -m "feat: expose composition workspace boundary"
```

## Task 10: Browser composition and promotion review

**Files:**

- Modify: `src/auteur/beginner/browser/app.js`
- Modify: `src/auteur/beginner/browser/index.html`
- Modify: `src/auteur/beginner/browser/styles.css` only for required composition/review states
- Test: `tests/test_beginner_workspace_browser.py`

**Interfaces:**

- Browser renders server projections and sends commands only.
- Browser shows detected/proposed/confirmed/rejected dimensions, mapping dispositions, review statuses, tensions, unresolved items, and promotion preview.
- Browser clearly distinguishes working composition, guidance context, proposed canonical changes, and canonical state.

Minimal client shape:

```javascript
async function sendBeginnerCommand(slug, payload) {
  const response = await fetch(`/api/beginner/workspaces/${workspaceId}/${slug}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ ...payload, command_id: crypto.randomUUID(), expected_session_version: state.session_version }),
  });
  state = await response.json();
  renderWorkspace(state);
}
```

The browser may render `state.working_composition`, `state.mapping_preview`, and
`state.tensions`, but it must not calculate mappings or canonical destinations.

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

Concrete red browser assertion matching the existing Python file-read harness:

```python
def test_browser_renders_composition_dispositions_without_internal_state_labels():
    html = _read(INDEX)
    js = _read(APP)
    combined = html + js

    assert "Will remain context / provenance" in combined
    assert "Will become canonical" in combined
    assert "working_composition" not in combined
    assert "mapping_preview" in js
```
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

## Task 11: Qualification and regression gate

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
- [ ] Add an explicit qualification assertion that the same Mystery card produces different, provenance-traceable guidance under Mystery-only versus confirmed hybrid composition while Mystery remains the primary engine.
- [ ] Run the focused qualification tests and verify failure.
- [ ] Implement the fixture assertions through the real Browser → HTTP → Application → authority boundary.
- [ ] Run focused Beginner tests:

```powershell
pytest tests/test_beginner_workspace_contracts.py tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_qualification.py -q
```

- [ ] Run the named integration slice and record collected, passed, skipped, xfailed, xpassed, failed, and error counts separately.
- [ ] Apply the validation policy recorded during Task 0: run the required L1/L2 checks for the changed boundaries, and schedule exactly the stabilization gate required by the current authority/persistence policy before human qualification. Do not infer the gate from this plan if the repository policy changed.
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

Concrete final command record:

```text
candidate_sha = <exact committed and pushed SHA>
focused_pytest = <collected/passed/skipped/xfailed/xpassed/failed/errors>
beginner_integration = <named command and result>
l1 = <exact-head result>
stabilization_gate = <policy-selected result>
human_gate = pending until independently operated
```

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
