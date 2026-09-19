# Premise-to-Narrative-Architecture Beginner Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Reorder the Beginner Workspace so a fresh premise first produces an explicit, inspectable, noncanonical Narrative Architecture Analysis; make that analysis the default working guidance context; then let Discovery search coherent story directions, Story Identity ratify explicit commitments, and Structure plan the accepted story.

**Architecture:** Keep Auteur's canonical five-layer model unchanged. Add a bounded Beginner-only derived analysis contract backed by the existing LLM client abstraction and deterministic fallback, persist it inside the existing noncanonical session envelope, project only material active components into WorkingComposition, reuse Story Discovery for direction generation/comparison, and keep all canonical mutation behind the existing Story Identity/Structure authority services.

**Tech Stack:** Python 3.11+, Pydantic v2, existing Auteur LLM client abstraction, existing Story Discovery and StoryIdentity models, Beginner Workspace application/persistence/authority stack, local JSON API, vanilla JavaScript/CSS, pytest, Ruff.

**Spec:** docs/superpowers/specs/2026-09-19-premise-to-narrative-architecture-beginner-flow.md

## Global Constraints

- Canonical semantic architecture remains exactly Ontology → Identity → Structure → Realization → Expression.
- Narrative Architecture Analysis is derived and noncanonical.
- The author can continue without individually confirming every inferred component.
- Guidance activation, author review/confirmation, and canonical authority are separate axes.
- Composition is optional refinement, not an admission gate.
- Discovery searches coherent story directions; Story Identity owns commitments; Structure owns plans.
- Do not preserve the current 3/4/3 card quota as a product invariant.
- Do not expose internal enum tokens in the default beginner UI.
- Provider failure/absence must degrade explicitly and must not fabricate rich interpretation.
- PR #237 remains draft and unmerged during implementation and qualification.
- Reuse its WorkingComposition, Mapping Planner, authority, provenance, revision isolation, crash recovery, and semantic-staleness substrate.
- No provider calls from GET/projection code.
- Legacy session JSON that omits new optional fields must continue to parse.
- Use TDD for every behavior change.
- Do not modify or commit .superpowers/.
- Any source/test change after candidate freeze invalidates downstream evidence.

## Review Focus

1. Ambiguous component alternatives must remain component-scoped rather than becoming competing whole-premise analyses.
2. Provider unavailable/malformed must degrade explicitly without unsupported psychological/aesthetic claims.
3. Active inferred but unconfirmed components must affect guidance while remaining noncanonical.
4. Stale analysis/discovery must not silently drive acceptance.
5. Crash retry must not duplicate provider generation or canonical promotion.

---

## File Structure Locked by This Plan

~~~text
src/auteur/beginner/
├── architecture_models.py
├── architecture_analysis.py
├── architecture_projection.py
├── discovery_models.py
├── discovery.py
├── decision_inventory.py
├── application.py
├── contracts.py
├── dimensions.py
├── guidance.py
├── mapping.py
├── promotion.py
├── projections.py
├── persistence.py
├── server.py
└── browser/
    ├── index.html
    ├── app.js
    └── styles.css
~~~

Do not introduce a generic narrative database or a new semantic layer.

---

### Task 1: Add Typed Narrative Architecture Analysis Contracts

**Files:**
- Create: src/auteur/beginner/architecture_models.py
- Modify: src/auteur/beginner/contracts.py
- Create: tests/test_beginner_architecture_analysis.py
- Modify: tests/test_beginner_workspace_persistence.py

**Interfaces:**
- Consumes: PackProvenance from auteur.story_design_packs.models.
- Produces: ArchitectureFacet, ArchitectureCertainty, ArchitectureRole, ArchitectureActivation, ArchitectureReviewState, ArchitectureEvidence, ArchitectureAlternative, ArchitectureAdjustment, ArchitectureComponent, NarrativeArchitectureAnalysis, and additive SessionEnvelope.architecture_analysis.

- [ ] **Step 1: Verify the execution base before editing**

Run:

~~~powershell
git rev-parse --show-toplevel
git rev-parse --git-common-dir
git rev-parse HEAD
git status --short
~~~

Expected:
- repository is ThorStarlord/Auteur;
- implementation branch descends from the approved design branch and includes frozen substrate SHA 019e7c39abe577c9a03c60d2c1d8d5be0eb000d2;
- .superpowers/ is not staged;
- no unrelated tracked edits.

- [ ] **Step 2: Write failing strict-contract tests**

~~~python
from auteur.beginner.architecture_models import (
    ArchitectureActivation,
    ArchitectureCertainty,
    ArchitectureComponent,
    ArchitectureEvidence,
    ArchitectureFacet,
    ArchitectureReviewState,
    ArchitectureRole,
    NarrativeArchitectureAnalysis,
)


def test_analysis_contract_separates_activation_review_and_authority() -> None:
    component = ArchitectureComponent(
        component_id="genre:mystery",
        facet=ArchitectureFacet.GENRE_CONSTELLATION,
        label="Mystery",
        role=ArchitectureRole.PRIMARY,
        certainty=ArchitectureCertainty.CLEAR,
        activation=ArchitectureActivation.ACTIVE,
        review_state=ArchitectureReviewState.UNREVIEWED,
        rationale="The premise is organized around discovering hidden truth.",
        evidence=(
            ArchitectureEvidence(
                source_kind="premise",
                label="Premise",
                excerpt="investigates the inconsistencies",
            ),
        ),
    )
    assert component.activation is ArchitectureActivation.ACTIVE
    assert component.review_state is ArchitectureReviewState.UNREVIEWED
    assert component.authority_status == "DERIVED / NOT CANON"


def test_analysis_is_noncanonical_even_when_every_component_is_clear() -> None:
    analysis = NarrativeArchitectureAnalysis(
        analysis_id="analysis:fixture",
        schema_version=1,
        premise_fingerprint="sha256:fixture",
        analyzer_id="test-analyzer",
        analyzer_version="1",
        summary="A superhero relationship-betrayal mystery.",
        components=(),
    )
    assert analysis.authority_status == "DERIVED / NOT CANON"
~~~

Also add a compatibility test that removes architecture_analysis from serialized SessionEnvelope JSON and proves SessionEnvelope.model_validate() loads it as None.

- [ ] **Step 3: Run test to verify RED**

~~~powershell
python -m pytest tests/test_beginner_architecture_analysis.py tests/test_beginner_workspace_persistence.py -q --tb=short
~~~

Expected: FAIL because the new module/types/field do not exist.

- [ ] **Step 4: Implement the strict models**

Use these public values:

~~~python
class ArchitectureFacet(str, Enum):
    GENRE_CONSTELLATION = "genre_constellation"
    NARRATIVE_ENGINE = "narrative_engine"
    CHARACTER_FUNCTION = "character_function"
    AESTHETIC_FRAMING = "aesthetic_framing"
    TROPE_FAMILY = "trope_family"
    RELATIONSHIP_DYNAMIC = "relationship_dynamic"
    SETTING_WORLD = "setting_world"
    THEME_MOTIF = "theme_motif"


class ArchitectureCertainty(str, Enum):
    CLEAR = "clear"
    LIKELY = "likely"
    UNCERTAIN = "uncertain"


class ArchitectureRole(str, Enum):
    PRIMARY = "primary"
    SUPPORTING = "supporting"
    FLAVOR = "flavor"


class ArchitectureActivation(str, Enum):
    ACTIVE = "active"
    SUPPRESSED = "suppressed"


class ArchitectureReviewState(str, Enum):
    UNREVIEWED = "unreviewed"
    AUTHOR_CONFIRMED = "author_confirmed"
    AUTHOR_MODIFIED = "author_modified"


class ArchitectureEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    source_kind: Literal["premise", "genre_pack", "design_pack", "accepted_state"]
    label: str = Field(min_length=1)
    excerpt: str | None = None
    source_ref: str | None = None


class ArchitectureAlternative(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    label: str = Field(min_length=1)
    rationale: str = Field(min_length=1)


class ArchitectureAdjustment(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    action: Literal["confirm", "suppress", "restore", "rename", "add"]
    component_id: str = Field(min_length=1)
    before_label: str | None = None
    after_label: str | None = None
    rationale: str | None = None


class ArchitectureComponent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    component_id: str = Field(min_length=1)
    facet: ArchitectureFacet
    label: str = Field(min_length=1)
    normalized_concept: str | None = None
    role: ArchitectureRole = ArchitectureRole.SUPPORTING
    certainty: ArchitectureCertainty
    activation: ArchitectureActivation = ArchitectureActivation.ACTIVE
    review_state: ArchitectureReviewState = ArchitectureReviewState.UNREVIEWED
    rationale: str = Field(min_length=1)
    evidence: tuple[ArchitectureEvidence, ...] = ()
    alternatives: tuple[ArchitectureAlternative, ...] = ()
    source_provenance: tuple[PackProvenance, ...] = ()
    author_rationale: str | None = None
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"


class NarrativeArchitectureAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    analysis_id: str = Field(min_length=1)
    schema_version: Literal[1] = 1
    premise_fingerprint: str = Field(min_length=1)
    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    components: tuple[ArchitectureComponent, ...]
    source_provenance: tuple[PackProvenance, ...] = ()
    adjustments: tuple[ArchitectureAdjustment, ...] = ()
    stale: bool = False
    availability_note: str | None = None
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"
~~~

Add to SessionEnvelope:

~~~python
architecture_analysis: NarrativeArchitectureAnalysis | None = None
~~~

Do not bump the session schema solely for this backward-compatible optional field.

- [ ] **Step 5: Add validation invariants**

Pin:
- component IDs unique;
- at most one PRIMARY per facet except genre constellation may have one primary plus supporting genres;
- alternatives nonblank and component-scoped;
- stale analyses remain inspectable/deserializable.

- [ ] **Step 6: Run tests and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_architecture_analysis.py tests/test_beginner_workspace_persistence.py -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~bash
git add src/auteur/beginner/architecture_models.py src/auteur/beginner/contracts.py tests/test_beginner_architecture_analysis.py tests/test_beginner_workspace_persistence.py
git commit -m "feat: add beginner narrative architecture contracts"
~~~

---

### Task 2: Implement Provider-Backed Analysis and Deterministic Fallback

**Files:**
- Create: src/auteur/beginner/architecture_analysis.py
- Modify: tests/test_beginner_architecture_analysis.py

**Interfaces:**
- Consumes: LLMClient.complete(LLMRequest), Task 1 models.
- Produces: ArchitectureAnalyzer Protocol, ProviderArchitectureAnalyzer, DeterministicArchitectureAnalyzer, premise_fingerprint(), analysis_basis_fingerprint().

- [ ] **Step 1: Write failing provider/fallback tests**

~~~python
def test_provider_analysis_returns_one_coherent_interpretation_with_component_alternative() -> None:
    client = FakeClient([LLMResponse(text=VALID_HYBRID_ANALYSIS_JSON, input_tokens=10, output_tokens=20)])
    analyzer = ProviderArchitectureAnalyzer(
        client=client,
        analyzer_id="beginner-architecture",
        analyzer_version="1",
        model_id="fixture-model",
    )
    analysis = analyzer.analyze(premise=HYBRID_PREMISE, source_provenance=())
    assert analysis.summary == "A superhero relationship-betrayal mystery."
    framing = next(c for c in analysis.components if c.facet is ArchitectureFacet.AESTHETIC_FRAMING)
    assert framing.label == "Erotic betrayal melodrama"
    assert [alt.label for alt in framing.alternatives] == ["Campy erotic melodrama"]


def test_provider_evidence_excerpt_must_come_from_premise() -> None:
    client = FakeClient([LLMResponse(text=JSON_WITH_INVENTED_QUOTE, input_tokens=1, output_tokens=1)])
    analyzer = ProviderArchitectureAnalyzer(client, "beginner-architecture", "1", "fixture-model")
    with pytest.raises(ArchitectureAnalysisError, match="evidence excerpt"):
        analyzer.analyze(premise="A hero investigates betrayal.", source_provenance=())


def test_deterministic_fallback_does_not_invent_erotic_psychology() -> None:
    analysis = DeterministicArchitectureAnalyzer().analyze(
        premise="A superhero investigates a public betrayal.",
        source_provenance=(),
    )
    labels = {component.label.casefold() for component in analysis.components}
    assert "superhero fiction" in labels
    assert "mystery" in labels
    assert not any("erotic" in label for label in labels)
    assert analysis.availability_note is not None
~~~

- [ ] **Step 2: Run and verify RED**

~~~powershell
python -m pytest tests/test_beginner_architecture_analysis.py -q --tb=short
~~~

Expected: FAIL.

- [ ] **Step 3: Implement analyzer protocol and provider draft**

~~~python
class ArchitectureAnalyzer(Protocol):
    def analyze(
        self,
        *,
        premise: str,
        source_provenance: tuple[PackProvenance, ...],
    ) -> NarrativeArchitectureAnalysis: ...
~~~

Provider JSON contains only summary plus component facet, label, role, certainty, rationale, exact premise evidence phrases, and component-local alternatives.

Provider does not choose IDs, activation, review state, canonical field paths, or authority status. Use temperature 0.2.

Stable ID:

~~~python
def _component_id(facet: ArchitectureFacet, label: str) -> str:
    normalized = " ".join(label.casefold().split())
    digest = hashlib.sha256((facet.value + "\\0" + normalized).encode("utf-8")).hexdigest()[:12]
    return f"{facet.value}:{digest}"
~~~

- [ ] **Step 4: Validate evidence and ambiguity**

Normalize case/whitespace and require every premise evidence excerpt to occur in the premise. Reject rich analysis on invented evidence.

Keep alternatives only on UNCERTAIN components and cap at three.

- [ ] **Step 5: Implement deterministic fallback**

~~~python
_EXPLICIT_SIGNALS = {
    "mystery": ("investigate", "investigation", "clue", "mystery", "discover the truth"),
    "superhero fiction": ("superhero", "masked hero", "superhuman", "cape"),
    "relationship betrayal": ("partner", "lover", "spouse", "relationship", "betrayal", "affair"),
    "secret identity": ("secret identity", "masked identity", "public identity"),
}
~~~

Fallback may infer relationship betrayal only when relationship + betrayal signals co-occur. It does not infer erotic psychological drama, campy melodrama, humiliation, or other deep framing unless explicit. availability_note tells the user richer interpretation is unavailable.

- [ ] **Step 6: Run tests and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_architecture_analysis.py -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~bash
git add src/auteur/beginner/architecture_analysis.py tests/test_beginner_architecture_analysis.py
git commit -m "feat: analyze beginner premises into narrative architecture"
~~~

---

### Task 3: Persist Analysis in Workspace Creation and Enforce Currentness

**Files:**
- Modify: src/auteur/beginner/application.py
- Modify: src/auteur/beginner/contracts.py
- Modify: tests/test_beginner_workspace_application.py
- Modify: tests/test_beginner_workspace_persistence.py

**Interfaces:**
- Consumes: ArchitectureAnalyzer.analyze(), premise_fingerprint().
- Produces: architecture_analyzer constructor injection, _architecture_analysis(), _analysis_is_current().

- [ ] **Step 1: Write failing creation/restart/currentness tests**

~~~python
def test_create_workspace_persists_analysis_and_never_regenerates_on_get(tmp_path: Path) -> None:
    analyzer = CountingAnalyzer(HYBRID_ANALYSIS)
    app = BeginnerWorkspaceApplication(tmp_path, "analysis-workspace", architecture_analyzer=analyzer)
    created = app.create_workspace(
        command_id="create-analysis-workspace",
        project_id="project",
        premise=HYBRID_PREMISE,
        guidance_genre="mystery",
    )
    assert created.architecture_analysis == HYBRID_ANALYSIS
    assert analyzer.calls == 1

    reopened = BeginnerWorkspaceApplication(tmp_path, "analysis-workspace", architecture_analyzer=analyzer)
    reopened.projection()
    assert analyzer.calls == 1
~~~

Also pin wrong premise fingerprint → derived stale projection, and legacy architecture_analysis=None → readable without GET mutation.

- [ ] **Step 2: Run and verify RED**

~~~powershell
python -m pytest tests/test_beginner_workspace_application.py tests/test_beginner_workspace_persistence.py -k "analysis or architecture" -q --tb=short
~~~

Expected: FAIL.

- [ ] **Step 3: Inject analyzer**

~~~python
def __init__(
    self,
    project_root: Path | str,
    workspace_id: str,
    *,
    authority_registry: AcceptanceRegistry | None = None,
    architecture_analyzer: ArchitectureAnalyzer | None = None,
    discovery_recommender: DiscoveryRecommender | None = None,
) -> None:
    ...
    self.architecture_analyzer = architecture_analyzer or DeterministicArchitectureAnalyzer()
    self.discovery_recommender = discovery_recommender
~~~

Use TYPE_CHECKING for DiscoveryRecommender until Task 6.

- [ ] **Step 4: Persist analysis with session creation**

Order:

~~~text
claim create receipt
→ analyze premise
→ build SessionEnvelope with architecture_analysis
→ build current initial composition
→ one BeginnerSessionStore.create
→ update journey basis
→ complete receipt
~~~

Never call analyzer from projection().

- [ ] **Step 5: Derive currentness**

Current only when premise fingerprint and referenced registered pack/design-pack hashes still match. Project stale state without mutating it in GET.

- [ ] **Step 6: Run tests and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_workspace_application.py tests/test_beginner_workspace_persistence.py -k "analysis or architecture" -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~bash
git add src/auteur/beginner/application.py src/auteur/beginner/contracts.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_persistence.py
git commit -m "feat: persist premise architecture analysis"
~~~

---

### Task 4: Project Analysis into Active Working Composition

**Files:**
- Modify: src/auteur/beginner/contracts.py
- Modify: src/auteur/beginner/dimensions.py
- Modify: src/auteur/beginner/application.py
- Modify: src/auteur/beginner/guidance.py
- Modify: tests/test_beginner_workspace_mapping.py
- Modify: tests/test_beginner_workspace_application.py
- Modify: tests/test_beginner_workspace_qualification.py

**Interfaces:**
- Produces GuidanceActivation, WorkingDimension.activation, composition_from_analysis(), active_dimensions().

- [ ] **Step 1: Write failing activation tests**

~~~python
def test_inferred_dimensions_are_active_without_author_confirmation() -> None:
    composition = composition_from_analysis(workspace_id="hybrid", analysis=HYBRID_ANALYSIS, prior=None)
    superhero = next(d for d in composition.dimensions if "Superhero" in d.label)
    assert superhero.activation is GuidanceActivation.ACTIVE
    assert superhero.confirmed_by_author is False


def test_active_unconfirmed_dimension_changes_guidance_but_not_canon(tmp_path: Path) -> None:
    app = create_hybrid_app_without_manual_confirmation(tmp_path)
    guidance = current_hybrid_guidance(app)
    assert "Superhero public identity" in guidance.context_guidance.patterns
    assert app.projection().canonical_refs == ()
~~~

- [ ] **Step 2: Run and verify RED**

~~~powershell
python -m pytest tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_qualification.py -k "active or unconfirmed or hybrid" -q --tb=short
~~~

Expected: FAIL because current code filters CONFIRMED only.

- [ ] **Step 3: Add separate activation axis**

~~~python
class GuidanceActivation(str, Enum):
    ACTIVE = "ACTIVE"
    SUPPRESSED = "SUPPRESSED"
~~~

Add activation: GuidanceActivation = ACTIVE to WorkingDimension. Keep DimensionStatus as lifecycle/review history.

- [ ] **Step 4: Implement composition_from_analysis()**

Projection rules:

~~~text
primary narrative engine       → PRIMARY_ENGINE
genre constellation            → GENRE_SUBGENRE
aesthetic framing              → EMOTIONAL_AESTHETIC
relationship dynamic           → RELATIONSHIP_THEMATIC
setting/world                  → SETTING_WORLD
character function             → analysis/provenance only
trope family                   → analysis/provenance only
theme/motif                    → analysis/provenance only unless later mapping explicitly needs it
~~~

Stable WorkingDimension IDs derive from ArchitectureComponent.component_id. Preserve premise evidence and registered pack provenance.

- [ ] **Step 5: Use active dimensions for guidance**

~~~python
def active_dimensions(composition: WorkingComposition) -> tuple[WorkingDimension, ...]:
    return tuple(
        dimension
        for dimension in composition.dimensions
        if dimension.activation is GuidanceActivation.ACTIVE
        and dimension.status not in {DimensionStatus.REJECTED, DimensionStatus.SUPERSEDED}
    )
~~~

Use this in compose_guidance_context() and _compose_option_impacts().

- [ ] **Step 6: Use active dimensions for mapping proposals**

Replace the current CONFIRMED-only filter in application._refresh_composition() with active_dimensions(). The resulting mappings remain noncanonical and still require explicit Identity acceptance.

Pin:
- mapping proposal exists for active inferred dimensions;
- story_identity.yaml still does not exist.

- [ ] **Step 7: Make supporting consequences facet-aware**

At minimum:

~~~python
if dimension.category is DimensionCategory.SETTING_WORLD:
    implications += (
        f"{dimension.label} changes the cost, evidence, or public/private consequences of the investigation.",
    )
elif dimension.category is DimensionCategory.RELATIONSHIP_THEMATIC:
    implications += (
        f"{dimension.label} makes clues change trust, intimacy, or relationship power rather than only case knowledge.",
    )
~~~

Do not reduce the output to generic “supporting lenses add pressure”.

- [ ] **Step 8: Run and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_qualification.py -k "active or unconfirmed or hybrid or composition" -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 9: Commit**

~~~bash
git add src/auteur/beginner/contracts.py src/auteur/beginner/dimensions.py src/auteur/beginner/application.py src/auteur/beginner/guidance.py tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_qualification.py
git commit -m "feat: activate inferred architecture for working guidance"
~~~

---

### Task 5: Add One Shared Story-Orientation Projection for Navigator and Story Map

**Files:**
- Create: src/auteur/beginner/architecture_projection.py
- Modify: src/auteur/beginner/projections.py
- Modify: src/auteur/beginner/server.py
- Create/Modify: tests/test_beginner_workspace_projections.py
- Modify: tests/test_beginner_workspace_server.py

**Interfaces:**
- Produces ArchitectureComponentProjection, ArchitectureFacetProjection, StoryOrientationProjection, build_story_orientation(), WorkspaceProjection.story_orientation.

- [ ] **Step 1: Write failing projection tests**

~~~python
def test_story_orientation_leads_with_architecture_not_stage_counts() -> None:
    projection = build_story_orientation(
        analysis=HYBRID_ANALYSIS,
        analysis_current=True,
        accepted_milestones=(),
    )
    assert projection.heading == "Here is what Auteur sees"
    assert projection.summary == "A superhero relationship-betrayal mystery."
    assert projection.authority_status == "DERIVED / NOT CANON"


def test_story_map_and_navigator_share_component_ids() -> None:
    projection = app.projection()
    compact = {
        item.component_id
        for facet in projection.story_orientation.navigator_facets
        for item in facet.components
    }
    expanded = {
        item.component_id
        for facet in projection.story_orientation.story_map_facets
        for item in facet.components
    }
    assert compact <= expanded
~~~

- [ ] **Step 2: Run and verify RED**

~~~powershell
python -m pytest tests/test_beginner_workspace_projections.py tests/test_beginner_workspace_server.py -k "orientation or story_map or architecture" -q --tb=short
~~~

Expected: FAIL.

- [ ] **Step 3: Build pure projections**

Use one analysis as source. Navigator includes active primary/supporting labels, certainty, review state. Story Map includes all components plus rationale, evidence, alternatives. Neither projection is persisted.

Exact labels:

~~~python
FACET_LABELS = {
    ArchitectureFacet.GENRE_CONSTELLATION: "Genre constellation",
    ArchitectureFacet.NARRATIVE_ENGINE: "Narrative machinery",
    ArchitectureFacet.CHARACTER_FUNCTION: "Character functions",
    ArchitectureFacet.AESTHETIC_FRAMING: "Aesthetic framing",
    ArchitectureFacet.TROPE_FAMILY: "Common trope families",
    ArchitectureFacet.RELATIONSHIP_DYNAMIC: "Emotional & relationship dynamics",
    ArchitectureFacet.SETTING_WORLD: "World & setting logic",
    ArchitectureFacet.THEME_MOTIF: "Themes & motifs",
}
~~~

- [ ] **Step 4: Extend WorkspaceProjection and server JSON**

Expose:
- heading;
- summary;
- current/stale state;
- authority status;
- navigator_facets;
- story_map_facets;
- availability note.

No raw enum tokens are used as beginner-facing labels.

- [ ] **Step 5: Run and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_workspace_projections.py tests/test_beginner_workspace_server.py -k "orientation or story_map or architecture" -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 6: Commit**

~~~bash
git add src/auteur/beginner/architecture_projection.py src/auteur/beginner/projections.py src/auteur/beginner/server.py tests/test_beginner_workspace_projections.py tests/test_beginner_workspace_server.py
git commit -m "feat: project narrative architecture into story orientation"
~~~

---

### Task 6: Reuse Story Discovery for a Durable Beginner Direction Recommendation

**Files:**
- Create: src/auteur/beginner/discovery_models.py
- Create: src/auteur/beginner/discovery.py
- Modify: src/auteur/story_discovery_recommend.py
- Modify: src/auteur/beginner/contracts.py
- Create: tests/test_beginner_discovery.py
- Modify: tests/test_story_discovery_recommendation_basis.py

**Interfaces:**
- Consumes handle_identity_recommend(open_ended), Story Discovery comparative judgment, Task 1 analysis.
- Produces DiscoveryDirection, DiscoveryRecommendationStatus, DiscoveryRecommendation, DiscoveryRecommender, StoryDiscoveryRecommender, UnavailableDiscoveryRecommender, recommend_candidate_outputs(), SessionEnvelope.discovery_recommendation.

- [ ] **Step 1: Write failing service tests**

~~~python
def test_beginner_discovery_returns_one_recommended_direction_and_real_alternatives() -> None:
    service = StoryDiscoveryRecommender(client=scripted_story_discovery_client())
    result = service.recommend(premise=HYBRID_PREMISE, analysis=HYBRID_ANALYSIS)
    assert result.status is DiscoveryRecommendationStatus.READY
    assert result.recommended_direction_id is not None
    assert len(result.directions) >= 2
    recommended = result.direction(result.recommended_direction_id)
    assert recommended.identity_candidate.story_type.genre.value == "mystery"
    assert "superhero" in recommended.architecture_summary.casefold()
    assert result.authority_status == "DERIVED / NOT CANON"


def test_discovery_unavailable_does_not_invent_story_directions() -> None:
    result = UnavailableDiscoveryRecommender(
        reason="No reasoning provider configured."
    ).recommend(premise=HYBRID_PREMISE, analysis=HYBRID_ANALYSIS)
    assert result.status is DiscoveryRecommendationStatus.UNAVAILABLE
    assert result.directions == ()
    assert result.recommended_direction_id is None
~~~

- [ ] **Step 2: Run and verify RED**

~~~powershell
python -m pytest tests/test_beginner_discovery.py tests/test_story_discovery_recommendation_basis.py -q --tb=short
~~~

Expected: FAIL.

- [ ] **Step 3: Define discovery contracts**

~~~python
class DiscoveryRecommendationStatus(str, Enum):
    READY = "ready"
    NEEDS_AUTHOR_CHOICE = "needs_author_choice"
    UNAVAILABLE = "unavailable"


class DiscoveryDirection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    direction_id: str
    title: str
    summary: str
    identity_candidate: StoryIdentity
    architecture_summary: str
    tradeoffs: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    source_analysis_id: str
    source_component_ids: tuple[str, ...]
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"


class DiscoveryRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    recommendation_id: str
    source_analysis_id: str
    source_basis_fingerprint: str
    status: DiscoveryRecommendationStatus
    recommended_direction_id: str | None
    rationale: str
    directions: tuple[DiscoveryDirection, ...]
    selected_direction_id: str | None = None
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"
~~~

- [ ] **Step 4: Extract a pure comparative helper from Story Discovery**

Expose:

~~~python
def recommend_candidate_outputs(
    *,
    client: LLMClient,
    premise_text: str,
    candidate_outputs: list[Any],
    genre: str | None,
    medium: str | None,
    mode: str | None,
    causal_profiles: dict[str, Any] | None = None,
    require_recommendation: bool = False,
) -> RecommendationJudgment:
    ...
~~~

Refactor current CLI dispatch to use this helper with require_recommendation=False so output remains unchanged.

For Beginner mode, require_recommendation=True asks for a bounded advisory preference whenever defensible, while still allowing not_adjudicable when no criterion can be justified.

- [ ] **Step 5: Implement StoryDiscoveryRecommender**

Flow:

~~~text
analysis
→ active architecture as design_context
→ handle_identity_recommend(open_ended, 3 candidates)
→ recommend_candidate_outputs(require_recommendation=True)
→ map candidates into DiscoveryDirection
→ no filesystem write
→ return DiscoveryRecommendation
~~~

Design context includes analysis summary plus active component labels/facets/roles/evidence. It does not give the model canonical field mutation authority.

- [ ] **Step 6: Add discovery_recommendation to SessionEnvelope**

Default None for legacy sessions.

- [ ] **Step 7: Run and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_discovery.py tests/test_story_discovery_recommendation_basis.py -q --tb=short
~~~

Expected: PASS; existing Story Discovery CLI behavior remains unchanged.

- [ ] **Step 8: Commit**

~~~bash
git add src/auteur/beginner/discovery_models.py src/auteur/beginner/discovery.py src/auteur/story_discovery_recommend.py src/auteur/beginner/contracts.py tests/test_beginner_discovery.py tests/test_story_discovery_recommendation_basis.py
git commit -m "feat: adapt story discovery for beginner direction search"
~~~
