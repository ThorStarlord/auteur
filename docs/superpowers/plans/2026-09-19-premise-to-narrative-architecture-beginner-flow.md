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
- Modify: tests/fixtures/beginner_hybrid_mystery.py

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
    provider_id: str | None = None
    model_id: str | None = None
    summary: str = Field(min_length=1)
    components: tuple[ArchitectureComponent, ...]
    source_provenance: tuple[PackProvenance, ...] = ()
    adjustments: tuple[ArchitectureAdjustment, ...] = ()
    stale: bool = False
    availability_note: str | None = None
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"

    def component(self, component_id: str) -> ArchitectureComponent:
        for component in self.components:
            if component.component_id == component_id:
                return component
        raise KeyError(component_id)
~~~

Add to SessionEnvelope:

~~~python
architecture_analysis: NarrativeArchitectureAnalysis | None = None
~~~

Do not bump the session schema solely for this backward-compatible optional field.

- [ ] **Step 5: Establish the shared sanitized hybrid fixture immediately**

Replace the old shallow premise in tests/fixtures/beginner_hybrid_mystery.py with:

~~~python
HYBRID_MYSTERY_PREMISE = (
    "A celebrated masked superhero begins investigating inconsistencies around an intimate partner "
    "and a powerful rival. Each clue threatens the hero's secret public identity and changes how "
    "the hero understands trust, jealousy, and possible relationship betrayal. The story should "
    "remain a fair mystery while treating the private discoveries with erotic-betrayal tension "
    "and heightened melodramatic pressure."
)
~~~

Add a hybrid_analysis() fixture factory whose components include these exact labels/facets:

~~~text
Mystery                         genre_constellation / primary
Investigation and revelation    narrative_engine / primary
Superhero fiction               genre_constellation / supporting
Superhero public identity       setting_world / supporting
Relationship betrayal           relationship_dynamic / supporting
Erotic betrayal melodrama       aesthetic_framing / supporting
Protagonist / investigator      character_function / supporting
Intimate partner / uncertainty  character_function / supporting
Rival / disruptor               character_function / supporting
Secret identity                 trope_family / supporting
Suspicious behavior             trope_family / supporting
Revelation / confrontation      trope_family / supporting
~~~

Use premise excerpts as evidence, provider_id="fixture", model_id="fixture-model", and keep every component noncanonical. End the fixture factory section with:

~~~python
HYBRID_ANALYSIS = hybrid_analysis()
~~~

Later tasks extend this same fixture with analyzer/discovery test doubles; they must not invent a second hybrid premise.

- [ ] **Step 6: Add validation invariants**

Pin:
- component IDs unique;
- at most one PRIMARY per facet except genre constellation may have one primary plus supporting genres;
- alternatives nonblank and component-scoped;
- stale analyses remain inspectable/deserializable.

- [ ] **Step 7: Run tests and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_architecture_analysis.py tests/test_beginner_workspace_persistence.py -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 8: Commit**

~~~bash
git add src/auteur/beginner/architecture_models.py src/auteur/beginner/contracts.py tests/test_beginner_architecture_analysis.py tests/test_beginner_workspace_persistence.py tests/fixtures/beginner_hybrid_mystery.py
git commit -m "feat: add beginner narrative architecture contracts"
~~~

---

### Task 2: Implement Provider-Backed Analysis and Deterministic Fallback

**Files:**
- Create: src/auteur/beginner/architecture_analysis.py
- Modify: tests/test_beginner_architecture_analysis.py
- Modify: tests/fixtures/beginner_hybrid_mystery.py

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
    analysis = analyzer.analyze(premise=HYBRID_MYSTERY_PREMISE, source_provenance=())
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
    ) -> NarrativeArchitectureAnalysis:
        raise NotImplementedError
~~~

Provider JSON contains only summary plus component facet, label, role, certainty, rationale, exact premise evidence phrases, and component-local alternatives.

Provider does not choose IDs, activation, review state, canonical field paths, or authority status. Use temperature 0.2. ProviderArchitectureAnalyzer writes its configured provider_id/model_id into NarrativeArchitectureAnalysis so provenance is inspectable without trusting model output.

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

The rich analyzer returns exactly one NarrativeArchitectureAnalysis object for the whole premise. Competing whole-premise analyses are not a beginner result type; only ArchitectureComponent.alternatives may hold ambiguity.

Add reusable test doubles to tests/fixtures/beginner_hybrid_mystery.py:

~~~python
class StaticArchitectureAnalyzer:
    def __init__(self, analysis: NarrativeArchitectureAnalysis = HYBRID_ANALYSIS) -> None:
        self.analysis = analysis

    def analyze(
        self,
        *,
        premise: str,
        source_provenance: tuple[PackProvenance, ...],
    ) -> NarrativeArchitectureAnalysis:
        return self.analysis.model_copy(
            update={"premise_fingerprint": premise_fingerprint(premise)}
        )


class CountingArchitectureAnalyzer(StaticArchitectureAnalyzer):
    def __init__(self, analysis: NarrativeArchitectureAnalysis = HYBRID_ANALYSIS) -> None:
        super().__init__(analysis)
        self.calls = 0

    def analyze(
        self,
        *,
        premise: str,
        source_provenance: tuple[PackProvenance, ...],
    ) -> NarrativeArchitectureAnalysis:
        self.calls += 1
        return super().analyze(premise=premise, source_provenance=source_provenance)
~~~

- [ ] **Step 6: Run tests and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_architecture_analysis.py -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~bash
git add src/auteur/beginner/architecture_analysis.py tests/test_beginner_architecture_analysis.py tests/fixtures/beginner_hybrid_mystery.py
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
    analyzer = CountingArchitectureAnalyzer(HYBRID_ANALYSIS)
    app = BeginnerWorkspaceApplication(tmp_path, "analysis-workspace", architecture_analyzer=analyzer)
    created = app.create_workspace(
        command_id="create-analysis-workspace",
        project_id="project",
        premise=HYBRID_MYSTERY_PREMISE,
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
    self.session_store = BeginnerSessionStore(Path(project_root), workspace_id)
    self.receipt_store = CommandReceiptStore(Path(project_root), workspace_id)
    self.workspace_id = workspace_id
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
- Modify: tests/fixtures/beginner_hybrid_mystery.py

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
    app = create_hybrid_app(tmp_path)
    projection = app.projection()
    assert projection.guidance_inspector is not None
    assert "Superhero public identity" in projection.guidance_inspector.context_guidance.patterns
    assert projection.canonical_refs == ()
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

Update tests/fixtures/beginner_hybrid_mystery.py so create_hybrid_app() no longer confirms every dimension manually:

~~~python
def create_hybrid_app(tmp_path: Path) -> BeginnerWorkspaceApplication:
    app = BeginnerWorkspaceApplication(
        tmp_path,
        "hybrid-mystery",
        architecture_analyzer=StaticArchitectureAnalyzer(HYBRID_ANALYSIS),
    )
    app.create_workspace(
        command_id="create-hybrid-mystery",
        project_id="hybrid-project",
        premise=HYBRID_MYSTERY_PREMISE,
        guidance_genre="mystery",
    )
    return app
~~~

Change application._initial_composition() so a current architecture_analysis uses composition_from_analysis(); retain propose_dimensions() only for legacy sessions without analysis.

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
git add src/auteur/beginner/contracts.py src/auteur/beginner/dimensions.py src/auteur/beginner/application.py src/auteur/beginner/guidance.py tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_qualification.py tests/fixtures/beginner_hybrid_mystery.py
git commit -m "feat: activate inferred architecture for working guidance"
~~~

---

### Task 5: Add One Shared Story-Orientation Projection for Navigator and Story Map

**Files:**
- Create: src/auteur/beginner/architecture_projection.py
- Modify: src/auteur/beginner/projections.py
- Modify: src/auteur/beginner/server.py
- Create: tests/test_beginner_workspace_projections.py
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


def test_story_map_and_navigator_share_component_ids(tmp_path: Path) -> None:
    app = create_hybrid_app(tmp_path)
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

Use one analysis as source. Navigator includes active primary/supporting labels, certainty, review state, and activation. Story Map includes all components plus activation, rationale, evidence, and alternatives. Neither projection is persisted.

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
- Modify: tests/fixtures/beginner_hybrid_mystery.py

**Interfaces:**
- Consumes handle_identity_recommend(open_ended), Story Discovery comparative judgment, Task 1 analysis.
- Produces DiscoveryDirection, DiscoveryRecommendationStatus, DiscoveryRecommendation, DiscoveryRecommender, StoryDiscoveryRecommender, UnavailableDiscoveryRecommender, recommend_candidate_outputs(), SessionEnvelope.discovery_recommendation.

- [ ] **Step 1: Write failing service tests**

~~~python
def test_beginner_discovery_returns_one_recommended_direction_and_real_alternatives() -> None:
    scripted_client = HybridStoryDiscoveryClient()
    service = StoryDiscoveryRecommender(client=scripted_client)
    result = service.recommend(premise=HYBRID_MYSTERY_PREMISE, analysis=HYBRID_ANALYSIS)
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
    ).recommend(premise=HYBRID_MYSTERY_PREMISE, analysis=HYBRID_ANALYSIS)
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

    def direction(self, direction_id: str) -> DiscoveryDirection:
        for direction in self.directions:
            if direction.direction_id == direction_id:
                return direction
        raise KeyError(direction_id)
~~~

- [ ] **Step 4: Extract a pure comparative helper from Story Discovery**

Expose:

~~~python
def recommend_candidate_outputs(
    *,
    client: LLMClient,
    premise_text: str,
    candidate_outputs: list[Any],
    requested_candidates: int,
    genre: str | None,
    medium: str | None,
    mode: str | None,
    causal_profiles: dict[str, Any] | None = None,
) -> RecommendationJudgment:
    _require_distinct_engines(candidate_outputs)
    candidate_ids = [item.candidate_id for item in candidate_outputs]
    if len(candidate_outputs) == 1:
        return single_survivor_judgment(candidate_ids[0], requested_candidates)
    response = client.complete(
        _build_judge_request(
            premise_text,
            candidate_outputs,
            genre=genre,
            medium=medium,
            mode=mode,
            causal_profiles=causal_profiles,
        )
    )
    return _parse_judgment(
        response.text,
        candidate_ids,
        allow_explicit_intent_fit=False,
    )
~~~

Refactor current CLI dispatch to use this helper with requested_candidates=args.candidates. Existing CLI behavior and its honest not_adjudicable state remain unchanged.

Beginner mapping rule:
- judgment.status == "recommended" → DiscoveryRecommendationStatus.READY and recommended_direction_id is the winner;
- judgment.status == "not_adjudicable" → DiscoveryRecommendationStatus.NEEDS_AUTHOR_CHOICE and recommended_direction_id=None.

The normal product posture still asks Story Discovery to search for causally distinct directions and allows a strong advisory preference; it does not manufacture a winner when the calibrated judge says no preference is defensible.

- [ ] **Step 5: Implement StoryDiscoveryRecommender**

Flow:

~~~text
analysis
→ active architecture as design_context
→ handle_identity_recommend(open_ended, 3 candidates)
→ recommend_candidate_outputs(requested_candidates=3)
→ map candidates into DiscoveryDirection
→ no filesystem write
→ return DiscoveryRecommendation
~~~

Design context includes analysis summary plus active component labels/facets/roles/evidence. It does not give the model canonical field mutation authority.

- [ ] **Step 6: Extend the shared hybrid fixture with exact Identity/Discovery test data**

Add these deterministic identities to tests/fixtures/beginner_hybrid_mystery.py:

~~~python
HYBRID_SELECTED_IDENTITY = StoryIdentity(
    title="The Hero Who Needs the Truth",
    core_answer=(
        "A masked hero investigates apparent intimate betrayal while every clue "
        "also threatens the boundary between private trust and public identity."
    ),
    target_experience=TargetExperience(
        primary="jealous uncertainty",
        progression="suspicion -> evidence -> painful revelation",
        avoid=[],
    ),
    story_type=StoryType(
        mode=StoryMode.PROCEDURAL,
        genre=Genre.MYSTERY,
        subgenres=["superhero"],
    ),
    central_engine=HighLevelCentralEngine(
        want="Discover what is really happening between the partner and rival.",
        resistance="Secret identities, ambiguous evidence, and fear of what the truth means.",
        conflict="The need for certainty collides with love, jealousy, and heroic reputation.",
        stakes="The relationship, the hero's self-image, and public identity may all collapse.",
        change="The hero must choose how to live with the truth once certainty arrives.",
    ),
)

HYBRID_RELATIONSHIP_IDENTITY = HYBRID_SELECTED_IDENTITY.model_copy(
    update={
        "title": "Trust Under Siege",
        "core_answer": (
            "A relationship-centered psychological drama in which investigation matters "
            "mainly because suspicion changes intimacy and trust."
        ),
        "story_type": HYBRID_SELECTED_IDENTITY.story_type.model_copy(
            update={"mode": StoryMode.INTIMATE}
        ),
        "central_engine": HighLevelCentralEngine(
            want="Preserve the relationship without remaining willfully blind.",
            resistance="Longing, self-deception, and contradictory intimate signals.",
            conflict="The desire for intimacy collides with mounting evidence of betrayal.",
            stakes="Trust may be destroyed even if the feared betrayal is misunderstood.",
            change="The protagonist learns that intimacy cannot be preserved by refusing uncertainty.",
        ),
    }
)

HYBRID_CAMPY_IDENTITY = HYBRID_SELECTED_IDENTITY.model_copy(
    update={
        "title": "Masks, Rivals, and Scandal",
        "core_answer": (
            "A heightened superhero melodrama where escalating suspicious encounters "
            "turn private jealousy into public spectacle."
        ),
        "story_type": HYBRID_SELECTED_IDENTITY.story_type.model_copy(
            update={"mode": StoryMode.COMIC}
        ),
        "central_engine": HighLevelCentralEngine(
            want="Expose the rival before the scandal consumes the hero's relationship.",
            resistance="Public spectacle, theatrical misunderstandings, and secret identities.",
            conflict="The hero's need to control the narrative fuels ever-larger confrontations.",
            stakes="Romance, reputation, and heroic legitimacy become part of the same scandal.",
            change="The hero gives up controlling appearances and confronts the relationship directly.",
        ),
    }
)
~~~

After discovery_models.py exists, add:

~~~python
HYBRID_DISCOVERY = DiscoveryRecommendation(
    recommendation_id="hybrid-discovery-1",
    source_analysis_id=HYBRID_ANALYSIS.analysis_id,
    source_basis_fingerprint=analysis_basis_fingerprint(HYBRID_ANALYSIS),
    status=DiscoveryRecommendationStatus.READY,
    recommended_direction_id="direction-investigative-betrayal",
    rationale=(
        "Investigation is the strongest causal engine while superhero identity and "
        "relationship betrayal make each clue carry public and intimate consequences."
    ),
    directions=(
        DiscoveryDirection(
            direction_id="direction-investigative-betrayal",
            title=HYBRID_SELECTED_IDENTITY.title,
            summary=HYBRID_SELECTED_IDENTITY.core_answer,
            identity_candidate=HYBRID_SELECTED_IDENTITY,
            architecture_summary="Mystery primary; superhero and relationship-betrayal support.",
            tradeoffs=("Requires fair clue logic while preserving intimate ambiguity.",),
            source_analysis_id=HYBRID_ANALYSIS.analysis_id,
            source_component_ids=tuple(
                component.component_id for component in HYBRID_ANALYSIS.components
            ),
        ),
        DiscoveryDirection(
            direction_id="direction-relationship-drama",
            title=HYBRID_RELATIONSHIP_IDENTITY.title,
            summary=HYBRID_RELATIONSHIP_IDENTITY.core_answer,
            identity_candidate=HYBRID_RELATIONSHIP_IDENTITY,
            architecture_summary="Relationship drama primary; mystery as uncertainty mechanism.",
            tradeoffs=("Reduces puzzle centrality in exchange for deeper psychological focus.",),
            source_analysis_id=HYBRID_ANALYSIS.analysis_id,
            source_component_ids=tuple(
                component.component_id for component in HYBRID_ANALYSIS.components
            ),
        ),
        DiscoveryDirection(
            direction_id="direction-campy-melodrama",
            title=HYBRID_CAMPY_IDENTITY.title,
            summary=HYBRID_CAMPY_IDENTITY.core_answer,
            identity_candidate=HYBRID_CAMPY_IDENTITY,
            architecture_summary="Campy superhero melodrama primary; mystery as suspense support.",
            tradeoffs=("Heightened spectacle weakens detailed psychological realism.",),
            source_analysis_id=HYBRID_ANALYSIS.analysis_id,
            source_component_ids=tuple(
                component.component_id for component in HYBRID_ANALYSIS.components
            ),
        ),
    ),
)
~~~

Add the reusable recommender test double:

~~~python
class CountingDiscoveryRecommender:
    def __init__(self, result: DiscoveryRecommendation = HYBRID_DISCOVERY) -> None:
        self.result = result
        self.calls = 0

    def recommend(
        self,
        *,
        premise: str,
        analysis: NarrativeArchitectureAnalysis,
    ) -> DiscoveryRecommendation:
        self.calls += 1
        return self.result.model_copy(
            update={
                "source_analysis_id": analysis.analysis_id,
                "source_basis_fingerprint": analysis_basis_fingerprint(analysis),
            }
        )
~~~

Update create_hybrid_app() to accept an optional discovery_recommender and pass it into BeginnerWorkspaceApplication:

~~~python
def create_hybrid_app(
    tmp_path: Path,
    *,
    discovery_recommender: DiscoveryRecommender | None = None,
) -> BeginnerWorkspaceApplication:
    resolved_discovery = discovery_recommender or CountingDiscoveryRecommender()
    app = BeginnerWorkspaceApplication(
        tmp_path,
        "hybrid-mystery",
        architecture_analyzer=StaticArchitectureAnalyzer(HYBRID_ANALYSIS),
        discovery_recommender=resolved_discovery,
    )
    app.create_workspace(
        command_id="create-hybrid-mystery",
        project_id="hybrid-project",
        premise=HYBRID_MYSTERY_PREMISE,
        guidance_genre="mystery",
    )
    return app
~~~

Add this deterministic provider double to tests/fixtures/beginner_hybrid_mystery.py so the service test exercises the real open-ended Story Discovery path without hiding response ordering:

    class HybridStoryDiscoveryClient:
        def __init__(self) -> None:
            self._candidate_index = 0
            self.calls: list[LLMRequest] = []

        def complete(self, request: LLMRequest) -> LLMResponse:
            self.calls.append(request)

            if "comparative narrative architect" in request.system:
                payload = {
                    "recommendation_status": "recommended",
                    "recommendation_basis": "advisory_artistic_preference",
                    "recommended_candidate_id": "candidate_1",
                    "recommendation_rationale": (
                        "Candidate 1 keeps investigation causal while making superhero identity "
                        "and intimate betrayal consequential."
                    ),
                    "candidate_tradeoffs": {
                        "candidate_2": "Candidate 2 makes relationship psychology primary.",
                        "candidate_3": "Candidate 3 makes spectacle and melodrama primary.",
                    },
                }
                return LLMResponse(
                    text=json.dumps(payload),
                    input_tokens=1,
                    output_tokens=1,
                )

            if "summarizing a story identity" in request.system:
                return LLMResponse(
                    text=json.dumps(
                        {
                            "summary": "A distinct hybrid-story direction.",
                            "tradeoffs": ["One governing engine must remain legible."],
                            "risks": ["Supporting dimensions can crowd the primary engine."],
                            "best_for": ["A hybrid mystery with consequential relationship stakes."],
                        }
                    ),
                    input_tokens=1,
                    output_tokens=1,
                )

            identities = (
                HYBRID_SELECTED_IDENTITY,
                HYBRID_RELATIONSHIP_IDENTITY,
                HYBRID_CAMPY_IDENTITY,
            )
            identity = identities[self._candidate_index]
            self._candidate_index += 1
            return LLMResponse(
                text=yaml.safe_dump(identity.model_dump(mode="json"), sort_keys=False),
                input_tokens=1,
                output_tokens=1,
            )

The service test instantiates HybridStoryDiscoveryClient directly. If candidate validation causes this double to receive more than three generation requests, the resulting IndexError is intentional evidence that one fixture identity no longer survives the existing StoryIdentity contract.

- [ ] **Step 7: Add discovery_recommendation to SessionEnvelope**

Default None for legacy sessions.

- [ ] **Step 8: Run and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_discovery.py tests/test_story_discovery_recommendation_basis.py -q --tb=short
~~~

Expected: PASS; existing Story Discovery CLI behavior remains unchanged.

- [ ] **Step 9: Commit**

~~~bash
git add src/auteur/beginner/discovery_models.py src/auteur/beginner/discovery.py src/auteur/story_discovery_recommend.py src/auteur/beginner/contracts.py tests/test_beginner_discovery.py tests/test_story_discovery_recommendation_basis.py tests/fixtures/beginner_hybrid_mystery.py
git commit -m "feat: adapt story discovery for beginner direction search"
~~~

---

### Task 7: Orchestrate Analysis → Discovery → Story Direction → Identity Preview

**Files:**
- Modify: src/auteur/beginner/application.py
- Modify: src/auteur/beginner/projections.py
- Modify: src/auteur/beginner/contracts.py
- Modify: tests/test_beginner_workspace_application.py
- Modify: tests/test_beginner_workspace_authority.py
- Modify: tests/fixtures/beginner_hybrid_mystery.py

**Interfaces:**
- Consumes Task 6 DiscoveryRecommender and Task 5 story orientation.
- Produces continue_from_architecture(), select_story_direction(), revised accept_story_direction(), DiscoveryProjection, IdentityCandidateProjection.

- [ ] **Step 1: Write failing journey tests and deterministic journey helpers**

Add these helpers to tests/fixtures/beginner_hybrid_mystery.py; they intentionally call Task 7 commands that do not exist yet, so the focused test run is RED for the product behavior rather than for an undefined helper:

~~~python
def app_at_discovery(tmp_path: Path) -> BeginnerWorkspaceApplication:
    app = create_hybrid_app(
        tmp_path,
        discovery_recommender=CountingDiscoveryRecommender(HYBRID_DISCOVERY),
    )
    app.continue_from_architecture(
        command_id="hybrid-continue-architecture",
        expected_session_version=app.projection().session_version,
    )
    return app


def app_after_direction_acceptance(tmp_path: Path) -> BeginnerWorkspaceApplication:
    app = app_at_discovery(tmp_path)
    app.select_story_direction(
        direction_id="direction-investigative-betrayal",
        command_id="hybrid-select-direction",
        expected_session_version=app.projection().session_version,
    )
    app.accept_story_direction(
        command_id="hybrid-accept-direction",
        expected_session_version=app.projection().session_version,
    )
    return app
~~~

Then add:

~~~python
def test_fresh_workspace_starts_with_architecture_not_discovery_card(tmp_path: Path) -> None:
    app = create_hybrid_app(tmp_path)
    projection = app.projection()
    assert projection.story_orientation is not None
    assert projection.primary_surface == "architecture"
    assert projection.discovery is None
    assert projection.decision_card is None


def test_continue_from_architecture_generates_discovery_once(tmp_path: Path) -> None:
    recommender = CountingDiscoveryRecommender(HYBRID_DISCOVERY)
    app = create_hybrid_app(tmp_path, discovery_recommender=recommender)
    result = app.continue_from_architecture(
        command_id="continue-architecture",
        expected_session_version=app.projection().session_version,
    )
    assert recommender.calls == 1
    assert result.discovery.recommended_direction_id == "direction-investigative-betrayal"


def test_accept_direction_unlocks_identity_without_writing_story_identity(tmp_path: Path) -> None:
    app = app_at_discovery(tmp_path)
    app.select_story_direction(
        direction_id="direction-investigative-betrayal",
        command_id="select-direction",
        expected_session_version=app.projection().session_version,
    )
    result = app.accept_story_direction(
        command_id="accept-direction",
        expected_session_version=app.projection().session_version,
    )
    assert result.accepted is True
    assert not (tmp_path / "story_identity.yaml").exists()
    assert app.session_store.load().stages[DecisionStage.STORY_IDENTITY].availability is StageAvailability.AVAILABLE
~~~

- [ ] **Step 2: Run and verify RED**

~~~powershell
python -m pytest tests/test_beginner_workspace_application.py tests/test_beginner_workspace_authority.py -k "architecture or direction or identity_preview" -q --tb=short
~~~

Expected: FAIL.

- [ ] **Step 3: Add derived primary-surface state**

Use these values:

~~~python
PrimaryWorkspaceSurface = Literal[
    "architecture",
    "discovery",
    "story_identity",
    "structure",
    "complete",
]
~~~

Derive the value from persisted session/canon state; do not create a second persisted workflow state machine.

- [ ] **Step 4: Implement continue_from_architecture()**

Requirements:
- reject stale analysis;
- generate Discovery only in this mutating command;
- persist the Discovery recommendation in SessionEnvelope;
- record architecture_seen in journey sidecar only as presentation history;
- never create canonical state;
- if recommender is unavailable, leave the legacy curated fallback available and expose the reason.

- [ ] **Step 5: Implement direction selection**

select_story_direction():
- verifies direction belongs to the current recommendation;
- writes selected_direction_id into the immutable recommendation copy;
- does not write StoryIdentity;
- records nonrecommended selection as nonblocking authorial divergence.

- [ ] **Step 6: Rework Story Direction acceptance**

When rich Discovery exists:
- require selected direction;
- fingerprint selected candidate Identity + source analysis ID;
- append accepted story_direction milestone;
- unlock Story Identity;
- preserve candidate as derived input;
- do not create story_identity.yaml.

Keep the legacy card-based acceptance path only when rich Discovery is unavailable.

- [ ] **Step 7: Project Story Identity candidate review**

IdentityCandidateProjection contains:
- candidate title/core answer;
- genre/subgenres;
- target experience;
- central engine;
- source Discovery direction;
- active architecture components;
- working/not-canon label;
- mapping preview once Task 8 connects it.

No mandatory Story Identity card is required merely to restate candidate fields.

- [ ] **Step 8: Run and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_workspace_application.py tests/test_beginner_workspace_authority.py -k "architecture or direction or identity_preview" -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 9: Commit**

~~~bash
git add src/auteur/beginner/application.py src/auteur/beginner/projections.py src/auteur/beginner/contracts.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_authority.py tests/fixtures/beginner_hybrid_mystery.py
git commit -m "feat: reorder beginner journey around premise analysis"
~~~

---

### Task 8: Promote the Selected Discovery Candidate Through Existing Identity Authority

**Files:**
- Modify: src/auteur/beginner/application.py
- Modify: src/auteur/beginner/promotion.py
- Modify: src/auteur/beginner/composition.py
- Modify: tests/test_beginner_workspace_authority.py
- Modify: tests/test_beginner_workspace_mapping.py
- Modify: tests/test_beginner_workspace_qualification.py

**Interfaces:**
- Consumes accepted Story Direction candidate + active mapping records.
- Produces identity_semantic_projection() and promotion preview from current canonical Identity to selected-direction candidate plus deterministic composition mappings.

- [ ] **Step 1: Write failing candidate/promotion tests**

~~~python
def test_identity_preview_starts_from_selected_discovery_candidate(tmp_path: Path) -> None:
    app = app_after_direction_acceptance(tmp_path)
    preview = app.projection().mapping_preview
    assert preview.candidate_identity.core_answer == HYBRID_SELECTED_IDENTITY.core_answer
    assert preview.candidate_identity.central_engine.conflict == HYBRID_SELECTED_IDENTITY.central_engine.conflict
    assert preview.current_identity != preview.candidate_identity


def test_accepting_identity_is_first_canonical_identity_write(tmp_path: Path) -> None:
    app = app_after_direction_acceptance(tmp_path)
    before = app.projection()
    assert not (tmp_path / "story_identity.yaml").exists()
    result = app.accept_story_identity(
        command_id="accept-identity",
        expected_session_version=before.session_version,
    )
    assert result.accepted is True
    canonical = StoryIdentity.from_yaml(tmp_path / "story_identity.yaml")
    assert canonical.central_engine.conflict == before.mapping_preview.candidate_identity.central_engine.conflict
~~~

Also add semantic-diff tests for core_answer, story_type, target_experience, central_engine, architecture_preferences, hard_constraints, not_this, open_questions, characters, and genre_profile.

- [ ] **Step 2: Run and verify RED**

~~~powershell
python -m pytest tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_qualification.py -k "selected_discovery or first_canonical or semantic_projection" -q --tb=short
~~~

Expected: FAIL because current preview starts from the default/canonical identity and semantic diff covers too few fields.

- [ ] **Step 3: Compose mappings over the selected candidate**

Change composition refresh to accept candidate_identity. Use active dimensions and compose mappings over the selected Discovery candidate rather than _default_identity().

- [ ] **Step 4: Expand semantic Identity diff**

Use:

~~~python
_SEMANTIC_IDENTITY_FIELDS = (
    "core_answer",
    "target_experience",
    "story_type",
    "central_engine",
    "architecture_preferences",
    "hard_constraints",
    "not_this",
    "open_questions",
    "characters",
    "genre_profile",
)


def identity_semantic_projection(identity: StoryIdentity) -> dict[str, object]:
    dumped = identity.model_dump(mode="json")
    return {field: dumped.get(field) for field in _SEMANTIC_IDENTITY_FIELDS}
~~~

Do not stale Structure from confidence, recommendation rationale, generated alternatives, or advisory metadata alone.

- [ ] **Step 5: Keep promotion loss visible**

Promotion preview groups:
- becomes canonical;
- remains downstream guidance;
- preserved as provenance;
- unresolved/not representable.

Trope, character-function, and aesthetic meaning must not silently disappear.

- [ ] **Step 6: Preserve authority/recovery implementation**

Final promotion still crosses AcceptanceRegistry.accept() with the same caller-supplied command_id. Retain:
- durable promotion intent;
- expected artifact revision guard;
- owner recovery;
- atomic canonical write + sidecar;
- semantic-change-only downstream staleness.

- [ ] **Step 7: Run and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_qualification.py -k "selected_discovery or first_canonical or semantic_projection or staleness or recovery" -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 8: Commit**

~~~bash
git add src/auteur/beginner/application.py src/auteur/beginner/promotion.py src/auteur/beginner/composition.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_qualification.py
git commit -m "feat: promote selected discovery identity through authority"
~~~

---

### Task 9: Add Optional Architecture Refinement and Pre-Identity Reanalysis

**Files:**
- Modify: src/auteur/beginner/architecture_models.py
- Modify: src/auteur/beginner/architecture_analysis.py
- Modify: src/auteur/beginner/dimensions.py
- Modify: src/auteur/beginner/application.py
- Modify: tests/test_beginner_architecture_analysis.py
- Modify: tests/test_beginner_workspace_application.py
- Modify: tests/fixtures/beginner_hybrid_mystery.py

**Interfaces:**
- Produces confirm_architecture_component(), suppress_architecture_component(), restore_architecture_component(), rename_architecture_component(), add_architecture_component(), reanalyze_premise().

- [ ] **Step 1: Write failing refinement tests**

First add this exact premise variant to tests/fixtures/beginner_hybrid_mystery.py:

~~~python
REVISED_HYBRID_MYSTERY_PREMISE = (
    "A celebrated masked superhero begins investigating inconsistencies around an intimate partner "
    "and a powerful rival. Each clue threatens the hero's secret public identity and changes how "
    "the hero understands trust, jealousy, and possible relationship betrayal. The story should "
    "remain a fair mystery while treating the private discoveries as campy erotic-betrayal "
    "melodrama rather than psychological realism."
)
~~~

Then add:

~~~python
def test_suppressing_superhero_changes_guidance_without_touching_canon(tmp_path: Path) -> None:
    app = create_hybrid_app(tmp_path)
    before = app.projection()
    superhero = next(
        item
        for facet in before.story_orientation.story_map_facets
        for item in facet.components
        if item.label == "Superhero fiction"
    )

    app.suppress_architecture_component(
        component_id=superhero.component_id,
        rationale="Keep powers as background only.",
        command_id="suppress-superhero",
        expected_session_version=before.session_version,
    )

    after = app.projection()
    superhero_after = next(
        item
        for facet in after.story_orientation.story_map_facets
        for item in facet.components
        if item.component_id == superhero.component_id
    )
    active_labels = {
        dimension.label
        for dimension in after.working_composition.dimensions
        if dimension.activation is GuidanceActivation.ACTIVE
    }
    assert superhero_after.activation == "suppressed"
    assert "Superhero fiction" not in active_labels
    assert after.canonical_refs == ()


def test_pre_identity_premise_reanalysis_invalidates_old_discovery(tmp_path: Path) -> None:
    app = app_at_discovery(tmp_path)
    old_id = app.session_store.load().discovery_recommendation.recommendation_id
    app.reanalyze_premise(
        premise=REVISED_HYBRID_MYSTERY_PREMISE,
        command_id="reanalyze",
        expected_session_version=app.projection().session_version,
    )
    session = app.session_store.load()
    assert session.premise == REVISED_HYBRID_MYSTERY_PREMISE
    assert session.discovery_recommendation is None
    assert session.architecture_analysis.premise_fingerprint == premise_fingerprint(REVISED_HYBRID_MYSTERY_PREMISE)
    assert old_id not in json.dumps(session.model_dump(mode="json"))
~~~

- [ ] **Step 2: Run and verify RED**

~~~powershell
python -m pytest tests/test_beginner_architecture_analysis.py tests/test_beginner_workspace_application.py -k "suppress or restore or rename or reanalyze" -q --tb=short
~~~

Expected: FAIL.

- [ ] **Step 3: Implement pure immutable adjustment functions**

~~~python
def _replace_component(
    analysis: NarrativeArchitectureAnalysis,
    updated: ArchitectureComponent,
    adjustment: ArchitectureAdjustment,
) -> NarrativeArchitectureAnalysis:
    components = tuple(
        updated if item.component_id == updated.component_id else item
        for item in analysis.components
    )
    return analysis.model_copy(
        update={
            "components": components,
            "adjustments": (*analysis.adjustments, adjustment),
        }
    )


def suppress_component(
    analysis: NarrativeArchitectureAnalysis,
    component_id: str,
    rationale: str,
) -> NarrativeArchitectureAnalysis:
    component = analysis.component(component_id)
    updated = component.model_copy(
        update={
            "activation": ArchitectureActivation.SUPPRESSED,
            "review_state": ArchitectureReviewState.AUTHOR_MODIFIED,
            "author_rationale": rationale,
        }
    )
    adjustment = ArchitectureAdjustment(
        action="suppress",
        component_id=component_id,
        before_label=component.label,
        after_label=component.label,
        rationale=rationale,
    )
    return _replace_component(analysis, updated, adjustment)


def restore_component(
    analysis: NarrativeArchitectureAnalysis,
    component_id: str,
    rationale: str,
) -> NarrativeArchitectureAnalysis:
    component = analysis.component(component_id)
    updated = component.model_copy(
        update={
            "activation": ArchitectureActivation.ACTIVE,
            "review_state": ArchitectureReviewState.AUTHOR_MODIFIED,
            "author_rationale": rationale,
        }
    )
    adjustment = ArchitectureAdjustment(
        action="restore",
        component_id=component_id,
        before_label=component.label,
        after_label=component.label,
        rationale=rationale,
    )
    return _replace_component(analysis, updated, adjustment)


def confirm_component(
    analysis: NarrativeArchitectureAnalysis,
    component_id: str,
    rationale: str,
) -> NarrativeArchitectureAnalysis:
    component = analysis.component(component_id)
    updated = component.model_copy(
        update={
            "review_state": ArchitectureReviewState.AUTHOR_CONFIRMED,
            "author_rationale": rationale,
        }
    )
    adjustment = ArchitectureAdjustment(
        action="confirm",
        component_id=component_id,
        before_label=component.label,
        after_label=component.label,
        rationale=rationale,
    )
    return _replace_component(analysis, updated, adjustment)


def rename_component(
    analysis: NarrativeArchitectureAnalysis,
    component_id: str,
    label: str,
    rationale: str,
) -> NarrativeArchitectureAnalysis:
    component = analysis.component(component_id)
    updated = component.model_copy(
        update={
            "label": label,
            "review_state": ArchitectureReviewState.AUTHOR_MODIFIED,
            "author_rationale": rationale,
        }
    )
    adjustment = ArchitectureAdjustment(
        action="rename",
        component_id=component_id,
        before_label=component.label,
        after_label=label,
        rationale=rationale,
    )
    return _replace_component(analysis, updated, adjustment)


def add_author_component(
    analysis: NarrativeArchitectureAnalysis,
    *,
    facet: ArchitectureFacet,
    label: str,
    role: ArchitectureRole,
    rationale: str,
) -> NarrativeArchitectureAnalysis:
    component_id = _component_id(facet, label)
    component = ArchitectureComponent(
        component_id=component_id,
        facet=facet,
        label=label,
        role=role,
        certainty=ArchitectureCertainty.CLEAR,
        activation=ArchitectureActivation.ACTIVE,
        review_state=ArchitectureReviewState.AUTHOR_MODIFIED,
        rationale=rationale,
        author_rationale=rationale,
    )
    adjustment = ArchitectureAdjustment(
        action="add",
        component_id=component_id,
        after_label=label,
        rationale=rationale,
    )
    return analysis.model_copy(
        update={
            "components": (*analysis.components, component),
            "adjustments": (*analysis.adjustments, adjustment),
        }
    )
~~~

Author-added components use CLEAR, AUTHOR_MODIFIED, ACTIVE, and explicit author rationale.

- [ ] **Step 4: Reproject WorkingComposition after adjustment**

Preserve valid author overrides and acknowledgement state by stable IDs. Remove derived mappings from suppressed components. Invalidate current Discovery recommendation because its basis changed.

- [ ] **Step 5: Implement pre-Identity reanalyze_premise()**

Transaction:

~~~text
claim receipt
→ analyze new premise
→ reconcile prior author adjustments by facet + normalized concept
→ replace session premise + architecture analysis
→ reproject WorkingComposition
→ clear Discovery recommendation/selection
→ reset noncanonical Discover state
→ update basis digest
→ complete receipt
~~~

Reject direct reanalysis after canonical Story Identity acceptance. Task 12 handles revision-overlay reanalysis.

- [ ] **Step 6: Run and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_architecture_analysis.py tests/test_beginner_workspace_application.py -k "suppress or restore or rename or reanalyze" -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~bash
git add src/auteur/beginner/architecture_models.py src/auteur/beginner/architecture_analysis.py src/auteur/beginner/dimensions.py src/auteur/beginner/application.py tests/test_beginner_architecture_analysis.py tests/test_beginner_workspace_application.py tests/fixtures/beginner_hybrid_mystery.py
git commit -m "feat: refine inferred narrative architecture"
~~~

---

### Task 10: Replace Fixed 3/4/3 Qualification with Bounded Adaptive Stage Decisions

**Files:**
- Create: src/auteur/beginner/decision_inventory.py
- Modify: src/auteur/beginner/mystery_adapter.py
- Modify: src/auteur/beginner/application.py
- Modify: src/auteur/beginner/projections.py
- Create: tests/test_beginner_decision_inventory.py
- Modify: tests/test_beginner_mystery_adapter.py
- Modify: tests/test_beginner_workspace_application.py

**Interfaces:**
- Produces structure_inventory_for(session, analysis, accepted_identity) -> QualificationInventory.

- [ ] **Step 1: Write failing inventory tests**

~~~python
def test_rich_flow_does_not_require_legacy_discovery_or_identity_cards(tmp_path: Path) -> None:
    app = app_after_direction_acceptance(tmp_path)
    session = app.session_store.load()
    assert session.architecture_analysis is not None
    inventory = structure_inventory_for(
        session=session,
        analysis=session.architecture_analysis,
        accepted_identity=HYBRID_SELECTED_IDENTITY,
    )
    assert all(card.stage is QualificationStage.STRUCTURE for card in inventory.cards)
    assert "discover.story-experience" not in {card.card_id for card in inventory.cards}
    assert not any(card.card_id.startswith("story_identity.") for card in inventory.cards)


def test_mystery_adapter_no_longer_requires_exact_3_4_3_counts() -> None:
    inventory = QualificationInventory(
        cards=tuple(
            card for card in mystery_qualification_inventory().cards
            if card.stage is QualificationStage.STRUCTURE
        )
    )
    MysteryGuidanceAdapter.validate_inventory(inventory)
~~~

- [ ] **Step 2: Run and verify RED**

~~~powershell
python -m pytest tests/test_beginner_decision_inventory.py tests/test_beginner_mystery_adapter.py tests/test_beginner_workspace_application.py -k "inventory or stage_counts or legacy" -q --tb=short
~~~

Expected: FAIL because the current adapter requires fixed stage counts and the journey assumes Discovery/Identity cards.

- [ ] **Step 3: Remove exact-count validation**

Keep:
- unique card IDs;
- evidence source validity;
- option/recommendation consistency;
- stage validity.

Delete only the requirement that every inventory has exactly three Discovery, four Identity, and three Structure cards.

- [ ] **Step 4: Add deterministic Structure-card eligibility**

For the first implementation:
- active/accepted Mystery engine → include the three existing Mystery Structure cards;
- no Mystery engine → do not manufacture Mystery-specific Structure questions.

This is bounded selection over curated card families, not LLM-generated questioning.

- [ ] **Step 5: Make stage readiness independent of card quotas**

Use these rules:

~~~text
Discovery review available:
  current Discovery recommendation exists
  AND selected_direction_id exists

Story Identity review available:
  Story Direction accepted
  AND current promotion preview exists

Structure review available:
  every eligible Structure card answered
~~~

Do not render Story Identity as “0/0 unanswered”.

- [ ] **Step 6: Keep the legacy fallback explicit**

If rich Discovery is unavailable:
- current curated Mystery Discovery/Identity cards may remain available as degraded fallback;
- surface the provider-unavailable note;
- never present that fallback as equivalent to full architecture reasoning.

- [ ] **Step 7: Run and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_decision_inventory.py tests/test_beginner_mystery_adapter.py tests/test_beginner_workspace_application.py -k "inventory or stage_counts or readiness or legacy" -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 8: Commit**

~~~bash
git add src/auteur/beginner/decision_inventory.py src/auteur/beginner/mystery_adapter.py src/auteur/beginner/application.py src/auteur/beginner/projections.py tests/test_beginner_decision_inventory.py tests/test_beginner_mystery_adapter.py tests/test_beginner_workspace_application.py
git commit -m "feat: make beginner decisions adaptive by stage"
~~~

---

### Task 11: Wire Runtime Dependencies, JSON Commands, and the New Browser Journey

**Files:**
- Modify: src/auteur/beginner/server.py
- Modify: src/auteur/beginner/browser/index.html
- Modify: src/auteur/beginner/browser/app.js
- Modify: src/auteur/beginner/browser/styles.css
- Modify: tests/test_beginner_workspace_server.py
- Modify: tests/test_beginner_workspace_browser.py

**Interfaces:**
- Consumes all prior Beginner services.
- Produces BeginnerRuntimeDependencies, server CLI provider/model options, new JSON commands, and projection-only browser flow.

- [ ] **Step 1: Write failing HTTP/browser contract tests**

~~~python
def test_http_fresh_workspace_returns_story_orientation_before_decision_card(running_rich_server) -> None:
    _, projection = post_json(
        running_rich_server,
        "/api/beginner/workspaces",
        hybrid_create_payload(),
    )
    assert projection["primary_surface"] == "architecture"
    assert projection["story_orientation"]["heading"] == "Here is what Auteur sees"
    assert projection["decision_card"] is None


def test_browser_does_not_render_internal_dimension_vocabulary() -> None:
    source = browser_asset("app.js")
    html = browser_asset("index.html")
    assert "PRIMARY_ENGINE" not in html
    assert "SETTING_WORLD" not in html
    assert "RELATIONSHIP_THEMATIC" not in html
    assert "Use this lens" not in html
    assert "Refine this interpretation" in source or "Refine this interpretation" in html
~~~

Also pin HTTP routes:
- continue-architecture
- select-direction
- confirm-architecture-component
- suppress-architecture-component
- restore-architecture-component
- add-architecture-component
- reanalyze-premise

- [ ] **Step 2: Run and verify RED**

~~~powershell
python -m pytest tests/test_beginner_workspace_server.py tests/test_beginner_workspace_browser.py -q --tb=short
~~~

Expected: FAIL.

- [ ] **Step 3: Add runtime dependency construction**

~~~python
@dataclass(frozen=True)
class BeginnerRuntimeDependencies:
    architecture_analyzer: ArchitectureAnalyzer
    discovery_recommender: DiscoveryRecommender
~~~

Server behavior:
- with --provider: build one existing retrying LLMClient, then construct ProviderArchitectureAnalyzer + StoryDiscoveryRecommender;
- optional --model flows to the existing build_client contract;
- without --provider: DeterministicArchitectureAnalyzer + UnavailableDiscoveryRecommender;
- tests inject scripted dependencies and never access network.

- [ ] **Step 4: Serialize the new surfaces**

Projection JSON includes:
- primary_surface;
- story_orientation;
- discovery;
- identity_candidate;
- mapping_preview;
- eligible Structure decision_card;
- existing canonical/revision state.

Do not serialize Python enum names as beginner copy.

- [ ] **Step 5: Rebuild the Navigator**

Default left rail:

~~~text
Your story
  Narrative architecture
  Discovery
  Story Identity
  Structure
  Realization — Later
  Expression — Later
~~~

Stage completion/progress remains secondary metadata.

- [ ] **Step 6: Rebuild the first central surface**

Exact primary actions:
- Looks right — continue
- Refine this interpretation
- Why does Auteur see this?

Label analysis as a working interpretation / not canon.

- [ ] **Step 7: Rebuild Story Map from the same projection**

Expanded read-only sections:
- genre constellation;
- narrative machinery;
- character functions;
- aesthetic framing;
- trope families;
- emotional/relationship dynamics;
- world/setting logic;
- themes/motifs;
- evidence/ambiguity;
- accepted milestones;
- revision state.

No mutation controls in Story Map.

- [ ] **Step 8: Replace the old Working Composition panel with optional refinement**

Default collapsed title: **Refine story interpretation**.

Beginner labels:
- Main story engine
- Genre / story tradition
- Emotional & aesthetic framing
- Relationship & thematic dynamic
- World & setting logic

Controls:
- Confirm/keep
- Reduce/remove
- Restore
- Rename
- Add missing component

Raw mapping IDs/enums move under **Advanced mapping details**.

- [ ] **Step 9: Render Discovery and Identity as dedicated surfaces**

Discovery:
- recommended direction as primary card;
- alternatives with tradeoffs;
- select direction;
- explicit Story Direction review/acceptance;
- derived/not-canon label.

Identity:
- candidate commitments;
- promotion preview grouped canonical/guidance/provenance/unresolved;
- explicit Accept Story Identity;
- no mandatory “0/4 answered”.

Structure:
- eligible curated Decision Cards.

- [ ] **Step 10: Run tests and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_workspace_server.py tests/test_beginner_workspace_browser.py -q --tb=short
~~~

Expected: PASS.

- [ ] **Step 11: Commit**

~~~bash
git add src/auteur/beginner/server.py src/auteur/beginner/browser/index.html src/auteur/beginner/browser/app.js src/auteur/beginner/browser/styles.css tests/test_beginner_workspace_server.py tests/test_beginner_workspace_browser.py
git commit -m "feat: present premise architecture before beginner decisions"
~~~

---

### Task 12: Harden Currentness, Idempotency, Crash Recovery, and Revision Isolation

**Files:**
- Modify: src/auteur/beginner/application.py
- Modify: src/auteur/beginner/persistence.py
- Modify: src/auteur/beginner/contracts.py
- Modify: tests/test_beginner_workspace_persistence.py
- Modify: tests/test_beginner_workspace_authority.py
- Modify: tests/test_beginner_workspace_qualification.py

**Interfaces:**
- Consumes CommandReceiptStore, existing acceptance-journal recovery, analysis/discovery basis fingerprints.
- Produces durable provider-command recovery and revision-safe architecture overlays.

- [ ] **Step 1: Write failing no-double-generation crash test**

~~~python
class _ProcessCrash(BaseException):
    pass


def test_retry_after_discovery_persisted_before_receipt_completion_does_not_regenerate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recommender = CountingDiscoveryRecommender(HYBRID_DISCOVERY)
    app = create_hybrid_app(tmp_path, discovery_recommender=recommender)
    real_complete = app.receipt_store.complete

    def crash_after_persist(*args: Any, **kwargs: Any) -> Any:
        receipt = args[0]
        if receipt.command_id == "continue-after-analysis":
            raise _ProcessCrash("process terminated after session persistence")
        return real_complete(*args, **kwargs)

    monkeypatch.setattr(app.receipt_store, "complete", crash_after_persist)

    with pytest.raises(_ProcessCrash, match="session persistence"):
        app.continue_from_architecture(
            command_id="continue-after-analysis",
            expected_session_version=app.projection().session_version,
        )

    assert recommender.calls == 1
    assert app.session_store.load().discovery_recommendation is not None

    recovered_app = BeginnerWorkspaceApplication(
        tmp_path,
        app.workspace_id,
        architecture_analyzer=StaticArchitectureAnalyzer(HYBRID_ANALYSIS),
        discovery_recommender=recommender,
    )
    recovered = recovered_app.continue_from_architecture(
        command_id="continue-after-analysis",
        expected_session_version=recovered_app.projection().session_version,
    )

    assert recovered.discovery.recommendation_id == HYBRID_DISCOVERY.recommendation_id
    assert recommender.calls == 1
~~~

- [ ] **Step 2: Write stale-basis tests**

~~~python
def test_stale_analysis_blocks_discovery_generation(tmp_path: Path) -> None:
    app = create_hybrid_app(tmp_path)
    session = app.session_store.load()
    assert session.architecture_analysis is not None
    app.session_store.update(
        session.session_version,
        lambda current: current.model_copy(
            update={
                "architecture_analysis": current.architecture_analysis.model_copy(
                    update={"premise_fingerprint": "sha256:stale"}
                )
            }
        ),
    )

    with pytest.raises(BeginnerWorkspaceError, match="architecture analysis is stale"):
        app.continue_from_architecture(
            command_id="continue-stale-analysis",
            expected_session_version=app.projection().session_version,
        )


def test_stale_discovery_basis_blocks_story_direction_acceptance(tmp_path: Path) -> None:
    app = app_at_discovery(tmp_path)
    app.select_story_direction(
        direction_id="direction-investigative-betrayal",
        command_id="select-before-stale",
        expected_session_version=app.projection().session_version,
    )
    session = app.session_store.load()
    composition = session.working_composition
    assert composition is not None
    target = next(
        dimension
        for dimension in composition.dimensions
        if dimension.category is DimensionCategory.SETTING_WORLD
    )
    changed = target.model_copy(update={"activation": GuidanceActivation.SUPPRESSED})
    changed_composition = composition.model_copy(
        update={
            "dimensions": tuple(
                changed if item.dimension_id == target.dimension_id else item
                for item in composition.dimensions
            )
        }
    )
    app.session_store.update(
        session.session_version,
        lambda current: current.model_copy(
            update={"working_composition": changed_composition}
        ),
    )

    with pytest.raises(BeginnerWorkspaceError, match="discovery recommendation is stale"):
        app.accept_story_direction(
            command_id="accept-stale-direction",
            expected_session_version=app.projection().session_version,
        )
~~~

- [ ] **Step 3: Write post-Identity revision-isolation tests**

After canonical Story Identity exists:
- direct reanalyze_premise without an active Identity revision is rejected;
- in an Identity revision, revised premise + analysis + composition exist only in revision overlay;
- cancel returns parent premise/analysis bytes exactly;
- accepting revised Identity promotes only through explicit authority.

- [ ] **Step 4: Persist provider-command recovery intent**

For continue_from_architecture and reanalyze_premise, receipt intent stores:
- premise fingerprint;
- source analysis ID;
- analysis basis fingerprint;
- expected session version;
- operation fingerprint.

On retry, if the session already contains the exact operation result, complete/replay the receipt without invoking provider again.

Do not apply canonical artifact revision semantics to noncanonical provider commands.

- [ ] **Step 5: Make Discovery currentness depend on active composition**

DiscoveryRecommendation.source_basis_fingerprint includes:
- analysis ID/fingerprint;
- material active/suppressed WorkingComposition dimensions;
- author adjustments that change guidance.

Persistence-only metadata changes do not invalidate it.

- [ ] **Step 6: Preserve all PR #237 canonical recovery invariants**

Rerun tests for:
- owner recovery without duplicate promotion;
- durable semantic-change intent;
- artifact pre/post revision guard;
- metadata-only Identity revisions keep downstream fresh;
- semantic Identity revisions stale Structure.

- [ ] **Step 7: Run focused tests and verify GREEN**

~~~powershell
python -m pytest tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_qualification.py -k "recovery or crash or stale or revision or idempot" -q --tb=short
~~~

Expected: PASS, aside from the documented Windows symlink-permission skip when the host lacks symlink privilege.

- [ ] **Step 8: Commit**

~~~bash
git add src/auteur/beginner/application.py src/auteur/beginner/persistence.py src/auteur/beginner/contracts.py tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_qualification.py
git commit -m "fix: harden premise analysis recovery and revision isolation"
~~~

---

### Task 13: Prove the Sanitized Hybrid Journey End-to-End

**Files:**
- Modify: tests/fixtures/beginner_hybrid_mystery.py
- Modify: tests/test_beginner_workspace_qualification.py
- Modify: docs/engineering/beginner-workspace-qualification.md

**Interfaces:**
- Consumes complete Browser → HTTP → Application → analysis/discovery → authority path.
- Produces deterministic sanitized qualification evidence.

- [ ] **Step 1: Reuse the single sanitized hybrid fixture established in Task 1**

Assert HYBRID_MYSTERY_PREMISE still exactly matches the approved sanitized premise and contains no private/raw story material. Do not create an alternate fixture premise for qualification.

- [ ] **Step 2: Extend the fixture with deterministic rich-analysis and Story Discovery responses**

The fixture provider must produce:
- Mystery as primary genre/engine;
- superhero public/private identity as world context;
- relationship betrayal as relationship dynamic;
- erotic-betrayal tension + heightened melodrama as aesthetic framing;
- protagonist/investigator, intimate partner/source of uncertainty, rival/disruptor as character functions;
- relevant trope families;
- one bounded aesthetic alternative;
- at least two genuinely different Story Discovery directions;
- recommended direction = investigative betrayal mystery.

- [ ] **Step 3: Write real HTTP end-to-end qualification**

The test crosses the real local HTTP handler and asserts:

~~~text
create workspace
→ first response primary_surface = architecture
→ no canonical refs
→ analysis contains Mystery + superhero + relationship/aesthetic material
→ continue architecture
→ Discovery recommendation exists
→ select recommended direction
→ accept Story Direction
→ story_identity.yaml still absent
→ Identity candidate includes selected Discovery engine
→ mapping preview exposes canonical + guidance/provenance/unresolved groups
→ accept Story Identity
→ canonical story_identity.yaml exists
→ Structure becomes available
→ answer eligible Structure decisions
→ accept Whole-Story Structure
→ three accepted milestones present
~~~

- [ ] **Step 4: Add differential-guidance assertions**

Compare Mystery-only and hybrid analysis/composition for the same Mystery Structure decision.

Required:
- Mystery remains primary in both;
- hybrid context/consequences/provenance differs;
- superhero source appears only in hybrid;
- relationship/aesthetic source appears only in hybrid;
- hybrid clue consequences include relationship trust/intimacy or public/private identity pressure.

- [ ] **Step 5: Add beginner-language assertions**

Default beginner browser content must not expose:
- PRIMARY_ENGINE
- SETTING_WORLD
- RELATIONSHIP_THEMATIC
- PROPOSED
- “Use this lens”

It must expose:
- “Here is what Auteur sees”
- “Refine this interpretation”
- “Story direction”
- “Story Identity”
- “Structure”
- explicit working/noncanonical status.

- [ ] **Step 6: Run the complete focused Beginner suite**

~~~powershell
python -m pytest -q tests/test_beginner_architecture_analysis.py tests/test_beginner_discovery.py tests/test_beginner_decision_inventory.py tests/test_beginner_mystery_adapter.py tests/test_beginner_workspace_contracts.py tests/test_beginner_workspace_mapping.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_qualification.py --tb=short
~~~

Record separately:
- collected;
- passed;
- skipped;
- xfailed;
- xpassed;
- failed;
- errors.

Expected: zero failed/errors. Record the Windows symlink-permission skip separately if the host lacks WinError 1314 privilege.

- [ ] **Step 7: Run Ruff and diff verification**

~~~powershell
python -m ruff check src/auteur/beginner src/auteur/story_discovery_recommend.py tests/test_beginner_architecture_analysis.py tests/test_beginner_discovery.py tests/test_beginner_decision_inventory.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_qualification.py
git diff --check
~~~

Expected: both exit 0.

- [ ] **Step 8: Update automated qualification evidence only**

Record:
- implementation SHA;
- exact focused command and result counts;
- any environment skip;
- exact L1/L2/L3 status if already available;
- human gate pending.

Do not mark human usability passed from automated evidence.

- [ ] **Step 9: Commit**

~~~bash
git add tests/fixtures/beginner_hybrid_mystery.py tests/test_beginner_workspace_qualification.py docs/engineering/beginner-workspace-qualification.md
git commit -m "test: qualify premise architecture beginner journey"
~~~

---

### Task 14: Exact-Head Validation, Stabilization, and Human Qualification Handoff

**Files:**
- Modify only after evidence exists: docs/engineering/beginner-workspace-qualification.md
- No product source changes after candidate freeze.

**Interfaces:**
- Produces final candidate evidence packet; does not authorize merge/publication.

- [ ] **Step 1: Verify repository identity and freeze the candidate**

~~~powershell
git status --short
git rev-parse HEAD
git rev-parse --show-toplevel
git rev-parse --git-common-dir
~~~

Requirements:
- tracked working tree clean;
- .superpowers/ remains excluded;
- full candidate SHA recorded;
- branch pushed;
- no source/test/resource changes after freeze.

- [ ] **Step 2: Obtain exact-head L1**

Open/update a draft PR for the new implementation branch so Validation runs against the exact candidate SHA.

Verify:
- workflow head SHA equals the frozen candidate;
- L1 focused validation concludes success;
- focused verification stack concludes success.

Do not reuse PR #237 L1 because PR #237 is pinned to 019e7c39abe577c9a03c60d2c1d8d5be0eb000d2.

- [ ] **Step 3: Run targeted L2**

Record the boundary reason exactly:

> Premise interpretation and Story Discovery now cross provider reasoning → durable Beginner session state → WorkingComposition → Browser/HTTP/Application → StoryIdentity authority while preserving noncanonical/currentness and crash-recovery boundaries.

Run:

~~~powershell
python -m pytest -q tests/test_beginner_architecture_analysis.py tests/test_beginner_discovery.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_qualification.py --tb=short
~~~

Record exact counts and environment skip.

- [ ] **Step 4: Run exactly one L3 Stabilization checkpoint**

This package is an explicit product-architecture stabilization milestone.

Run the repository manual Stabilization workflow once against the frozen SHA.

If it fails:
- stop;
- preserve the exact failure evidence;
- do not rerun;
- do not change code until the failure is classified.

If it passes:
- proceed to human qualification.

- [ ] **Step 5: Prepare, but do not operate, a fresh human workspace**

Use:
- fresh workspace ID;
- approved sanitized hybrid premise;
- provider-backed rich analysis;
- frozen candidate code.

Return:
- local URL;
- workspace ID;
- exact premise;
- concise operating instructions;
- observation checklist.

The executor stops before making creative choices.

- [ ] **Step 6: Human qualification checklist**

The actual human author evaluates:

1. Does the first screen answer “what story does Auteur think I have?” without ontology knowledge?
2. Are Mystery, superhero, relationship/erotic-betrayal, character-function, aesthetic, trope, and world signals understandable?
3. Is inference clearly distinct from canon?
4. Is refinement obviously optional?
5. Does Discovery feel like choosing what the story could become rather than restating the premise?
6. Does Story Identity feel like explicit commitment?
7. Does Structure feel downstream of accepted Identity?
8. Does superhero context materially change consequences/reasoning?
9. Does relationship/erotic-betrayal framing materially change the emotional meaning of clues/trust?
10. Are ambiguity and evidence understandable without raw enum/implementation vocabulary?
11. Is the promotion preview understandable?
12. Does revision exploration remain visibly noncanonical?
13. Is there any material friction that prevents independent use?

- [ ] **Step 7: Record human evidence only after the human reports it**

If the human finds a material defect:
- stop qualification;
- record the finding;
- return to brainstorming or systematic debugging according to issue type;
- do not merge.

If the human passes:
- update qualification evidence in a documentation-only follow-up;
- explicitly distinguish frozen product candidate SHA from evidence-only documentation commit if repository policy permits;
- retain publication/integration as separate authority.

- [ ] **Step 8: Keep integration separate**

After human qualification:
- perform whole-branch code review;
- decide whether the new PR supersedes/closes PR #237;
- mark the new PR ready only when evidence/review are clean;
- merge only with explicit integration authorization.

PR #237 remains draft/unmerged until that decision.

---

## Implementation Sequence and Review Gates

~~~text
Task 1  contracts
  ↓
Task 2  analysis engine
  ↓
Task 3  session persistence/currentness
  ↓
Task 4  active WorkingComposition projection
  ↓
Task 5  story orientation projection
  ↓
Task 6  Story Discovery adapter
  ↓
Task 7  journey reorder
  ↓
Task 8  Identity promotion
  ↓
Task 9  optional refinement/reanalysis
  ↓
Task 10 adaptive Structure inventory
  ↓
Task 11 HTTP/browser product surface
  ↓
Task 12 reliability/revision hardening
  ↓
Task 13 deterministic end-to-end qualification
  ↓
Task 14 exact-head L1 → L2 → one L3 → human qualification
~~~

With subagent-driven execution, each task receives a fresh implementation review before the next task.

## Whole-Branch Review Focus

Before candidate freeze, explicitly review for:

1. **Authority leakage:** analysis/discovery/refinement creates or mutates story_identity.yaml before explicit Identity acceptance.
2. **Duplicate story models:** Story Navigator/Story Map persists a second independent architecture model.
3. **Provider calls on GET:** browser refresh or projection invokes LLM work.
4. **False confidence:** fallback/provider result presents unsupported interpretation as clear.
5. **Stale-basis acceptance:** Discovery/Identity can accept after analysis or active composition changed.
6. **Lost architecture meaning:** meaningful components vanish during Identity promotion without guidance/provenance/unresolved visibility.
7. **PR #237 reliability regression:** crash recovery, revision isolation, idempotency, semantic-only staleness, mapping override validation.
8. **Internal vocabulary leakage:** raw enum/status names appear in beginner UI.
9. **Fixed-card inertia:** 3/4/3 reappears as a required invariant.
10. **Fixture overfitting:** product code branches on hybrid fixture literals.

## Definition of Done

~~~text
raw premise
→ one coherent derived Narrative Architecture Analysis
→ Story Navigator shows what Auteur sees
→ author may continue without confirming every component
→ optional refinement changes working guidance only
→ Discovery recommends coherent story direction + meaningful alternatives
→ author accepts Story Direction without creating canonical StoryIdentity
→ Story Identity preview shows explicit commitments + visible loss/remainder
→ explicit Identity acceptance creates canonical StoryIdentity
→ Structure asks planning questions relevant to accepted story
→ semantic revisions stale downstream; metadata-only revisions do not
→ provider/restart recovery is idempotent
→ exact-head L1 PASS
→ targeted L2 PASS
→ one stabilization L3 PASS
→ independent human qualification PASS
~~~

Automated evidence is necessary but cannot substitute for the final human usability gate.