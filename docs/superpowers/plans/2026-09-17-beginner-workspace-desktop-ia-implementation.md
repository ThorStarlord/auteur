# Beginner Workspace desktop IA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current desktop Beginner Workspace composition with a Decision Card-first workspace and an ontology-aware, on-demand Tutor Inspector without changing narrative authority, persistence, revision, or canonical promotion semantics.

**Architecture:** Extend the existing combined WorkspaceProjection with additive projections for the current decision and its derived guidance. Python composes semantic consequences; the browser only renders projections and sends existing commands. The migration is presentation-first: keep the current UI compatible until equivalent Inspector content and tests exist.

**Tech Stack:** Python 3.12, Pydantic, pytest, stdlib HTTP server, vanilla JavaScript, HTML/CSS, existing Beginner Workspace application and Mystery adapter.

---

## Scope guardrails

The implementation must preserve:

- WorkspaceProjection as the single combined read model.
- SessionEnvelope as the durable exploration envelope.
- autosaved noncanonical choices.
- Story Direction acceptance without creating canonical StoryIdentity.
- existing Identity and Structure authority services.
- isolated revision exploration, at-risk preview, cancellation, and post-acceptance staleness.
- current-canon Story Map semantics: each accepted milestone appears once while history remains provenance.
- browser JavaScript as a renderer/command client, never a semantic or authority engine.
- uv.lock and .auteur/ as unrelated local state that must never be staged.
- no new workspace or qualification run during implementation.
- no L3 or release qualification before the redesigned human gate.

## File map

| File | Responsibility |
| --- | --- |
| src/auteur/beginner/guidance.py | Derived semantic consequence and Inspector guidance models; compatibility projection from current guidance |
| src/auteur/beginner/mystery_adapter.py | Curated Mystery content mapped to relevant semantic areas |
| src/auteur/beginner/projections.py | Composition of decision-workspace and Inspector projections from one snapshot |
| src/auteur/beginner/application.py | Symmetric receipt freezing/thawing only if additive projection data is persisted in existing receipts |
| src/auteur/beginner/server.py | Additive JSON serialization; unchanged command routes |
| src/auteur/beginner/browser/index.html | Desktop regions, Inspector affordance, accessible disclosure containers |
| src/auteur/beginner/browser/app.js | Projection rendering, Inspector toggling, existing command dispatch |
| src/auteur/beginner/browser/styles.css | Decision Card-first grid, right Inspector overlay, responsive drawers |
| tests/test_beginner_mystery_adapter.py | Semantic consequence and no-boilerplate tests |
| tests/test_beginner_workspace_application.py | Combined projection and authority-preservation tests |
| tests/test_beginner_workspace_server.py | HTTP serialization and command-boundary tests |
| tests/test_beginner_workspace_browser.py | Browser structure and thin-client tests |
| tests/test_beginner_workspace_qualification.py | Existing qualification scenarios; no status update during implementation |
| docs/engineering/beginner-workspace-qualification.md | Update only after the new human walkthrough |

## Task 1: Add ontology-aware derived guidance types

**Files:**

- Modify: src/auteur/beginner/guidance.py near OptionImpact
- Test: tests/test_beginner_mystery_adapter.py

- [ ] **Step 1: Write the failing model-contract tests**

Add tests that require explicit semantic areas, optional relevance-driven fields, and rejection of blank populated values:

~~~python
def test_narrative_consequence_supports_relevance_driven_semantic_fields() -> None:
    consequence = NarrativeConsequence(
        semantic_area=SemanticArea.STRUCTURE,
        summary="Even clues keep the reader reasoning throughout the inquiry.",
        implications=("The reversal must reinterpret evidence.",),
        what_becomes_easier=("Maintaining a fair inference path",),
        risks=("The middle may feel less urgent without setbacks",),
    )
    assert consequence.semantic_area is SemanticArea.STRUCTURE
    assert consequence.what_becomes_harder == ()
    assert consequence.compensating_requirements == ()


def test_narrative_consequence_rejects_blank_populated_fields() -> None:
    with pytest.raises(ValueError, match="nonblank"):
        NarrativeConsequence(
            semantic_area=SemanticArea.IDENTITY,
            summary=" ",
        )


def test_option_impact_remains_compatible_and_projects_derived_guidance() -> None:
    guidance = guidance_for("discover.story-experience", fresh_mystery_session())
    impact = guidance.option_impacts[guidance.recommendation]
    assert impact.authority_status == "DERIVED / NOT CANON"
    assert impact.narrative_consequences
~~~

Import the actual public names used by the implementation. Assert semantic
categories and the contract, not exact prose.

- [ ] **Step 2: Run the focused tests and verify failure**

~~~powershell
$env:PYTHONPATH="$(Get-Location);$(Join-Path (Get-Location) 'src')"
pytest -q tests/test_beginner_mystery_adapter.py -k "narrative_consequence or option_impact_remains"
~~~

Expected: FAIL because the semantic-area model and derived fields do not exist.

- [ ] **Step 3: Implement the minimal derived types**

Add a string enum with exactly IDENTITY, STRUCTURE, REALIZATION, and EXPRESSION.
Add a frozen Pydantic NarrativeConsequence with:

~~~python
semantic_area: SemanticArea
summary: str
implications: tuple[str, ...] = ()
what_becomes_easier: tuple[str, ...] = ()
what_becomes_harder: tuple[str, ...] = ()
risks: tuple[str, ...] = ()
compensating_requirements: tuple[str, ...] = ()
~~~

Reject blank strings in summary and populated tuples. Extend derived OptionImpact
with narrative_consequences and authority_status while retaining existing fields
and serialization compatibility. Do not add fields to StoryIdentity, blueprint
artifacts, or the session canon.

- [ ] **Step 4: Run the focused tests**

~~~powershell
pytest -q tests/test_beginner_mystery_adapter.py
~~~

Expected: all adapter tests and the new model tests pass.

- [ ] **Step 5: Commit**

~~~powershell
git add src/auteur/beginner/guidance.py tests/test_beginner_mystery_adapter.py
git commit -m "feat: model semantic beginner consequences"
~~~

## Task 2: Compose relevant Mystery consequences

**Files:**

- Modify: src/auteur/beginner/mystery_adapter.py
- Modify: src/auteur/beginner/guidance.py
- Test: tests/test_beginner_mystery_adapter.py

- [ ] **Step 1: Write failing content tests**

Walk every qualification card and option. Require concrete content, semantic
areas, and no generic fallback:

~~~python
def test_every_mystery_option_has_relevant_non_generic_consequences() -> None:
    inventory = MYSTERY_GUIDANCE_ADAPTER.inventory()
    for card in inventory.cards:
        impacts = option_impacts_for(card)
        assert set(impacts) == set(card.options)
        for option in card.options:
            impact = impacts[option]
            assert impact.narrative_consequences
            assert all(item.summary.strip() for item in impact.narrative_consequences)
            rendered = " ".join(
                [impact.audience_experience, impact.aesthetic_framing,
                 impact.narrative_structure]
                + list(impact.tradeoffs)
                + [item.summary for item in impact.narrative_consequences]
            ).casefold()
            assert "a different approach" not in rendered
            assert "emphasizes a different" not in rendered


def test_irrelevant_semantic_areas_are_omitted() -> None:
    card = MYSTERY_GUIDANCE_ADAPTER.inventory().card("discover.story-experience")
    impact = option_impacts_for(card)["Detective procedural"]
    areas = {item.semantic_area for item in impact.narrative_consequences}
    assert SemanticArea.IDENTITY in areas
    assert SemanticArea.STRUCTURE in areas
    assert SemanticArea.REALIZATION not in areas
    assert SemanticArea.EXPRESSION not in areas
~~~

- [ ] **Step 2: Run and verify failure**

~~~powershell
pytest -q tests/test_beginner_mystery_adapter.py -k "every_mystery_option or irrelevant_semantic"
~~~

Expected: FAIL because current impacts are flat.

- [ ] **Step 3: Implement deterministic curated composition**

For all ten qualification cards, add semantic consequences to every option using
existing Howdunit evidence and each card's meaning. Populate only relevant
Identity, Structure, Realization, and Expression items. Include concrete effects,
implications, and risks or compensating requirements when created.

Keep existing flat fields for compatibility. Compose the enriched tuple in the
Python guidance adapter/projection, never in JavaScript, and never persist it as
canonical story state.

- [ ] **Step 4: Run all Mystery guidance tests**

~~~powershell
pytest -q tests/test_beginner_mystery_adapter.py
~~~

Expected: PASS with deterministic, option-specific output and no generic fallback.

- [ ] **Step 5: Commit**

~~~powershell
git add src/auteur/beginner/guidance.py src/auteur/beginner/mystery_adapter.py tests/test_beginner_mystery_adapter.py
git commit -m "feat: enrich Mystery guidance by narrative layer"
~~~

## Task 3: Add composed workspace and Inspector projections

**Files:**

- Modify: src/auteur/beginner/projections.py
- Modify: src/auteur/beginner/application.py only if existing receipt freeze/thaw requires additive data
- Modify: src/auteur/beginner/server.py
- Test: tests/test_beginner_workspace_application.py
- Test: tests/test_beginner_workspace_server.py

- [ ] **Step 1: Write failing projection and HTTP tests**

Require both conceptual surfaces to derive from one application projection:

~~~python
def test_projection_composes_decision_workspace_and_inspector_from_one_snapshot(tmp_path: Path) -> None:
    app = make_application(tmp_path)
    projection = app.projection()
    assert projection.decision_workspace.current_focus.question == projection.decision_card.question
    assert projection.decision_workspace.next_action
    assert projection.guidance_inspector.recommendation == projection.decision_card.recommendation
    assert projection.guidance_inspector.authority_status == "DERIVED / NOT CANON"
    assert projection.guidance_inspector.narrative_consequences


def test_projection_separates_story_consequences_from_auteur_reasoning(tmp_path: Path) -> None:
    inspector = make_application(tmp_path).projection().guidance_inspector
    assert {item.semantic_area for item in inspector.narrative_consequences}
    assert inspector.recommendation_rationale
    assert inspector.evidence
    assert all(item.authority_status == "DERIVED / NOT CANON"
               for item in inspector.narrative_consequences)
~~~

Add an HTTP round-trip assertion for the additive fields while checking that
existing command URLs and session_version behavior remain unchanged.

- [ ] **Step 2: Run and verify failure**

~~~powershell
pytest -q tests/test_beginner_workspace_application.py tests/test_beginner_workspace_server.py -k "inspector or composed_decision"
~~~

Expected: FAIL because WorkspaceProjection has no composed projections.

- [ ] **Step 3: Implement additive projections**

Add frozen projection types:

~~~python
class DecisionOptionProjection:
    label: str
    selected: bool
    recommended: bool

class DecisionWorkspaceProjection:
    stage: DecisionStage
    position: str
    question: str
    why_this_matters_now: str
    options: tuple[DecisionOptionProjection, ...]
    immediate_consequence: str | None
    working_state: str
    active_issue_summary: str | None
    next_action: str
    authority_status: str

class GuidanceInspectorProjection:
    recommendation: str
    recommendation_rationale: str
    selected_choice_relationship: str
    narrative_consequences: tuple[NarrativeConsequence, ...]
    alternatives: tuple[str, ...]
    tradeoffs: tuple[str, ...]
    craft_principles: tuple[str, ...]
    evidence: tuple[str, ...]
    freshness: str
    authority_status: str
~~~

Add these to WorkspaceProjection with defaults, deriving both in the same
build_workspace_projection call. The decision workspace gets next_action from
application readiness and accepted state. The Inspector gets selected-option
impacts and omits absent semantic areas. Never add a second persistence file or
change session envelope schema.

- [ ] **Step 4: Run projection and authority regressions**

~~~powershell
pytest -q tests/test_beginner_workspace_application.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_authority.py
~~~

Expected: PASS, including canonical, revision, concurrency, and HTTP behavior.

- [ ] **Step 5: Commit**

~~~powershell
git add src/auteur/beginner/projections.py src/auteur/beginner/application.py src/auteur/beginner/server.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_server.py
git commit -m "feat: compose beginner decision and inspector projections"
~~~

## Task 4: Build the desktop Decision Card and Inspector layout

**Files:**

- Modify: src/auteur/beginner/browser/index.html
- Modify: src/auteur/beginner/browser/styles.css
- Modify: src/auteur/beginner/browser/app.js
- Test: tests/test_beginner_workspace_browser.py

- [ ] **Step 1: Write failing browser contract tests**

~~~python
def test_browser_has_decision_workspace_and_on_demand_inspector() -> None:
    html = browser_file("index.html")
    js = browser_file("app.js")
    css = browser_file("styles.css")
    assert 'id="decision-workspace"' in html
    assert 'id="guidance-inspector"' in html
    assert "Explore guidance" in html
    assert "guidance_inspector" in js
    assert "decision-workspace" in css


def test_browser_does_not_build_semantics_or_readiness() -> None:
    js = browser_file("app.js")
    assert "narrative_consequences" not in js.replace("guidance_inspector", "")
    assert "ready_to_accept" not in js
~~~

The second assertion checks browser field access without treating the literal
projection property name as forbidden. The purpose is to prove that JavaScript
does not calculate semantic consequences or readiness.

- [ ] **Step 2: Run and verify failure**

~~~powershell
pytest -q tests/test_beginner_workspace_browser.py
~~~

Expected: FAIL because guidance accordions are currently primary-card content.

- [ ] **Step 3: Implement semantic HTML**

Create a main decision-workspace region containing focus, question, Why this
matters now, compact suggestion, choices, immediate consequence, active issue,
working state, and next action. Create an accessible guidance-inspector region
with an Explore guidance control and disclosures for teaching, rationale,
comparison, impact, and evidence. Keep the Inspector closed by default and keep
the Decision Card as the only decision form.

- [ ] **Step 4: Implement desktop hierarchy**

Use a persistent left Navigator and dominant center Decision Card. Give the card
the primary width, typography, and scroll position. Open the Inspector as a
bounded right overlay/docked panel with its own scroll container and no card
resize or reflow. Use explicit width, z-index, and focus styles.

- [ ] **Step 5: Render projections only**

Render DecisionWorkspaceProjection in the center and
GuidanceInspectorProjection in the Inspector. Use:

~~~text
Auteur suggests: <recommendation> · Why?
~~~

Render semantic sections only when arrays are nonempty. Use projection labels
and keep command payloads identical to the existing envelope. JavaScript must
not calculate lifecycle, readiness, semantic areas, impacts, or authority.

- [ ] **Step 6: Run focused checks**

~~~powershell
node --check src/auteur/beginner/browser/app.js
pytest -q tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_server.py
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~powershell
git add src/auteur/beginner/browser/index.html src/auteur/beginner/browser/app.js src/auteur/beginner/browser/styles.css tests/test_beginner_workspace_browser.py
git commit -m "feat: make desktop decision card the workspace focus"
~~~

## Task 5: Implement Inspector behavior and accessibility

**Files:**

- Modify: src/auteur/beginner/browser/index.html
- Modify: src/auteur/beginner/browser/app.js
- Modify: src/auteur/beginner/browser/styles.css
- Test: tests/test_beginner_workspace_browser.py

- [ ] **Step 1: Write failing behavior tests**

~~~python
def test_browser_inspector_and_navigator_are_accessible_drawers() -> None:
    html = browser_file("index.html")
    js = browser_file("app.js")
    css = browser_file("styles.css")
    assert 'aria-controls="guidance-inspector"' in html
    assert 'aria-expanded="false"' in html
    assert 'aria-live="polite"' in html
    assert ".guidance-inspector.is-open" in css
    assert "window.innerWidth <= 800" in js
~~~

- [ ] **Step 2: Run and verify failure**

~~~powershell
pytest -q tests/test_beginner_workspace_browser.py -k "inspector or accessible or drawer"
~~~

Expected: FAIL until the new regions expose the accessibility contract.

- [ ] **Step 3: Implement behavior**

The Explore guidance control toggles one Inspector state, updates aria-expanded,
preserves the card, selected option, and scroll position, and closes on Escape.
Selection never opens the Inspector automatically. The current decision heading
remains the first meaningful heading in the main region.

On narrow screens, Inspector and Navigator become drawers. Keep current-stage
orientation in the header. Expose selected and recommended state without color
alone and announce save/error state through the existing status region.

- [ ] **Step 4: Run regressions**

~~~powershell
node --check src/auteur/beginner/browser/app.js
pytest -q tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_server.py
~~~

Expected: PASS with unchanged autosave, Continue, review, and acceptance.

- [ ] **Step 5: Commit**

~~~powershell
git add src/auteur/beginner/browser/index.html src/auteur/beginner/browser/app.js src/auteur/beginner/browser/styles.css tests/test_beginner_workspace_browser.py
git commit -m "feat: add accessible beginner guidance inspector"
~~~

## Task 6: Verify the thin-client and authority boundaries

**Files:**

- Test: tests/test_beginner_workspace_application.py
- Test: tests/test_beginner_workspace_server.py
- Test: tests/test_beginner_workspace_authority.py
- Test: tests/test_beginner_workspace_browser.py

- [ ] **Step 1: Add boundary regressions**

Through the Browser → HTTP → Application path prove that:

- GET and Inspector open do not mutate session or canonical files;
- selecting an option changes only working state;
- accepting a milestone remains the only canonical mutation;
- revision projections show at-risk information without premature staleness;
- JavaScript contains no readiness or semantic consequence decision logic.

Use the existing server fixture and compare canonical file bytes before and after
GET, Inspector open, and selection. Reuse authority tests for promotion and
revision semantics rather than duplicating domain rules in browser tests.

- [ ] **Step 2: Run the named boundary suite**

~~~powershell
pytest -q tests/test_beginner_workspace_application.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_browser.py
~~~

Expected: PASS with unchanged authority, persistence, and revision semantics.

- [ ] **Step 3: Commit**

~~~powershell
git add tests/test_beginner_workspace_application.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_browser.py
git commit -m "test: protect beginner desktop authority boundaries"
~~~

## Task 7: Final focused implementation verification

**Files:**

- Test: tests/test_beginner_workspace_qualification.py
- Test: tests/test_beginner_mystery_adapter.py
- Test: tests/test_beginner_workspace_application.py
- Test: tests/test_beginner_workspace_server.py
- Test: tests/test_beginner_workspace_browser.py

- [ ] **Step 1: Run the complete focused Beginner suite**

~~~powershell
$env:PYTHONPATH="$(Get-Location);$(Join-Path (Get-Location) 'src')"
pytest -q tests/test_beginner_workspace_server.py tests/test_beginner_workspace_qualification.py tests/test_beginner_workspace_persistence.py tests/test_beginner_workspace_contracts.py tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_authority.py tests/test_beginner_workspace_application.py tests/test_beginner_mystery_adapter.py
node --check src/auteur/beginner/browser/app.js
git diff --check
~~~

Record collected, passed, skipped, xfailed, xpassed, failed, and error counts
separately. The Windows symlink privilege skip remains environmental evidence.

- [ ] **Step 2: Run targeted HTTP/browser integration**

Start the exact worktree candidate with npm start. Create no new workspace.
Run the named HTTP/browser integration tests against existing fixtures and
confirm the projection fields and browser composition are served from the same
origin while command routes remain unchanged.

- [ ] **Step 3: Review implementation against the spec**

Map every acceptance criterion in the amended desktop IA spec to a passing test
or a manual observation step. Do not update qualification evidence yet.

- [ ] **Step 4: Commit the final implementation package**

~~~powershell
git status --short
git add src/auteur/beginner tests/test_beginner_mystery_adapter.py tests/test_beginner_workspace_application.py tests/test_beginner_workspace_server.py tests/test_beginner_workspace_browser.py tests/test_beginner_workspace_qualification.py
git diff --cached --name-only
git commit -m "feat: deliver beginner desktop IA redesign"
~~~

Verify uv.lock and .auteur/ are absent from the staged path list before commit.

## Execution and qualification after plan approval

1. Commit the approved spec and this plan to the PR branch; do not push until
   the plan receives human approval.
2. Push the implementation candidate and require exact-head GitHub L1 PASS.
3. Freeze the exact passing SHA.
4. Create one fresh workspace with the transfer Mystery premise. Do not reuse
   librarian-human-123b; it records the pre-redesign IA finding.
5. Perform the independent human desktop walkthrough for decision prominence,
   Inspector subordination, ontology-aware usefulness, safe disagreement,
   concrete consequences, state vocabulary, and scroll behavior.
6. Only if the human gate passes, update
   docs/engineering/beginner-workspace-qualification.md and mark HUMAN
   USABILITY PASS.
7. Then consider PR #233 ready for review and run one L3 stabilization
   checkpoint. Release qualification remains separate.

## Self-review checklist

- [x] Spec coverage: ontology sources, taxonomy, consequence contract, layout
  alternatives, projection contract, testing, migration, risks, accessibility,
  and acceptance criteria map to tasks above.
- [x] Authority coverage: no task changes session canon, acceptance services,
  revision semantics, or current-canon Story Map semantics.
- [x] Placeholder scan: every implementation step is specified with files,
  tests, commands, and expected outcomes.
- [x] Type consistency: SemanticArea and NarrativeConsequence precede the
  projection types; the browser consumes the projection names introduced here.
- [x] Qualification boundary: no new workspace, human claim, L3 run, release
  claim, merge, or PR-ready transition occurs during implementation.
