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
