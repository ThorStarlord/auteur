# Unified Agent-Interactive Creative Graph Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking. Previous owner preference for this project is **native/inline execution without subagents**; honor it if that remains in force.

**Goal:** Make Auteur's existing Narrative Architecture graph an agent-first creative interaction surface: select real narrative entities, component fields and recorded relationships, ask source-verified questions, request explicit holistic revisions, and return to the selected graph context and hybrid revision comparison.

**Architecture:** Add a small typed source-intent resolver beneath existing architecture owners; a lightweight action/selection/panel layer alongside Studio's graph, facets and inspectors; a separate read-only host-agent inquiry contract; and an optional graph-intent path into the existing architecture prepare/complete/review/apply lifecycle. Reuse ArchitectureCandidate v2, CanvasStore's architecture subtree, HostAgentRequest/Response and the existing hybrid semantic comparison. No new graph database or generation provider.

**Tech Stack:** Python 3.11+, Pydantic v2, vanilla JS/DOM/SVG/CSS, Node built-in node:test, pytest, existing Chromium browser tests and existing host-agent packet helpers.

**Spec:** [Unified Agent-Interactive Creative Graph Design](../specs/2026-11-05-unified-agent-interactive-creative-graph-design.md)

**Repository baseline:** Main reviewed 2026-11-05 at 62070f5d4bdfdccab0067b92ccc7a1c5c8b780ec. Verify the implementation checkout before acting; never assume it remains HEAD.

## Global Constraints

- Author and canonical authority are unchanged: no auto-accept, no automatic Story Identity/Structure/Realization/Expression or ontology mutation.
- Current working ArchitectureCandidate v2 remains the sole authoring projection. No v3 migration, graph database, universal component store, extra graph persistence owner or separate provider.
- Use the active coding agent through the existing host-agent-neutral request/response infrastructure.
- **Explore/Challenge/Explain/Compare/Connect-to-Ask produce inquiry**, not revised candidates. Only an explicit Revise/Rebalance/Restructure author action may prepare a holistic revision.
- Selected anchors: one to three maximum, each typed; stable identity by kind + ID (genre_contract by genre_node_id), optionally qualified top-level field or recorded reference tuple; no title or SVG-position identity.
- Recorded links and genre interactions are first-class on day one. Explicit contract/phase/parent references are selectable only when unambiguously source-addressable; they are not ArchitectureLinks.
- The client may display sourceRef but cannot declare trusted source evidence. All anchors, refs, fields, candidate SHA and support excerpts are resolved atomically by the server under the existing canvas lock.
- Read-only inquiry status must never be misreported as revised architecture ready; prepared_not_executed must never be reported as executed.
- The existing readable reader, six facets, graph pan/zoom, Focused Unfolding, Full Architecture, working-canvas editing, standard text revision and opt-in hybrid review must remain usable.
- Source freshness and design guidance freshness remain separate; reject stale/superseded/incorrect-canvas operation. Reuse the existing request SHA and apply guard.
- Never infer stored relationships from text similarity, proximity or the absence of a recorded direct link. No recorded relation means unknown, not disproven.
- Source model and field-level/JSON support do not prove literary causation or preservation of all accepted constraints.
- Keyboard, touch and 390px navigation must provide equivalent textual interaction to the spatial graph. Use safe DOM text, not untrusted HTML interpolation.
- Tests and evidence must distinguish pure Node, Python host lifecycle, actual served Chromium, independent agent execution and real author observation; success in one does not substitute for another.

## Review Focus — five adversarial input classes

1. **Same title, different ID; reordered arrays; duplicate names:** selecting/revising by a node title must never target a different record; exact server-side IDs and live sourceRef indices are decisive (Task 1, Task 4).
2. **Ambiguous or absent reference:** a field inside a genre contract or phase is not a synthetic ArchitectureLink; duplicate indistinguishable target references cannot be silently picked (Tasks 1–3).
3. **Stale source or superseded response:** source, guidance, candidate SHA or canvas changes after selection or request preparation must invalidate work and prevent wrong-candidate inquiry/review/apply (Tasks 1, 4–5, 7–8).
4. **Graph rendering rerenders during keyboard and pointer interactions:** edge hit areas must not break zoom or block nodes; a filter/text field must retain focus and edited author intention (Tasks 2–3, 6, 8).
5. **Inquiry confused with authority or holistic revision:** inquiries must not create architecture versions or write canon; a selected anchor must not hide unrelated changes in the full hybrid review (Tasks 5, 7–9).

---

## File map and interface ownership

| Existing owner | Responsibility / authorized modification |
| --- | --- |
| src/auteur/beginner/studio_architecture.py | Optional source-bound graph intent for existing revise prepare; request projection; no schema or accepted-story changes |
| src/auteur/beginner/server.py | Extend existing prepare POST and add two architecture inquiry POSTs plus inquiry GET; no replacement route |
| src/auteur/host_agent.py | Reuse existing packet builders/validators unchanged wherever possible |
| src/auteur/beginner/browser/studio.js | Minimal selection/refresh/review hooks only, not a rewrite of its existing graph/facets |
| src/auteur/beginner/browser/studio.html | Contextual action and persistent creative-agent panel within architecture workspace |
| src/auteur/beginner/browser/studio.css | Scoped responsive styles |
| src/auteur/beginner/browser/studio_architecture_revision_bridge.js | Optional focused-entry handoff to existing hybrid comparison |
| src/auteur/beginner/browser/studio_architecture_revision_view.mjs | Existing setMode/selectFocus API; changes only if source-backed entry needs a narrow extension |
| src/auteur/beginner/browser/studio_architecture_reader.js | Preserve read-first narrative architecture; no new mandatory graph step |

### New files by single responsibility

| File | Owner of |
| --- | --- |
| src/auteur/beginner/studio_architecture_graph_intent.py | Pydantic GraphIntent, typed anchor validation and server-resolved source support |
| src/auteur/beginner/studio_architecture_inquiry.py | Read-only agent inquiry prepare/complete/project lifecycle and bounded response |
| src/auteur/beginner/browser/studio_architecture_graph_actions.js | Pure source-side action availability, typed selection and recorded-relationship projection |
| src/auteur/beginner/browser/studio_architecture_graph_selection.js | DOM pointer/keyboard selection of nodes, edges, references and component fields |
| src/auteur/beginner/browser/studio_architecture_creative_panel.js | Persistent selected-context and editable author-question interface |
| src/auteur/beginner/browser/studio_architecture_agent_bridge.js | Host-agent inquire/revise request and completion status routing |
| src/auteur/beginner/browser/studio_architecture_creative_feedback.js | Re-focus same IDs on inquiry and entered hybrid revision review |
| tests/test_beginner_studio_architecture_graph_intent.py | Server-side source, field, reference and freshness contract |
| tests/test_studio_architecture_graph_actions.mjs | Pure action availability and no-inference rules |
| tests/test_studio_architecture_graph_selection.mjs | SVG/linear/field selection and focus semantics |
| tests/test_beginner_studio_architecture_graph_revision.py | Existing full-candidate revise lifecycle with validated graph context |
| tests/test_beginner_studio_architecture_inquiry.py | Read-only inquiry packet, response, concurrency, persistence separation |
| tests/test_studio_architecture_creative_panel.mjs | Panel action, author text, statuses and no silent revisions |
| tests/test_studio_architecture_creative_feedback.mjs | Return to source selection and hybrid source-backed focus |
| tests/test_beginner_studio_architecture_interactive_browser.py | Actual served desktop/mobile/keyboard and host-agent journeys |
| docs/research/2026-11-05-unified-agent-interactive-graph-evaluation.md | Grounded evidence comparison and go/no-go decision |

The existing recorded rich/sparse candidates in docs/qualification-evidence/agent-first-ontology-20261103/ are the canonical test sources. Add synthetic variants **only** with explicit labeling. New application scripts must be added to server.py's existing _BROWSER_ASSETS allowlist and the Studio HTML script sequence.

## Stage A — Source semantics and graph interaction

### Task 1: Build authoritative typed graph-intent resolution

**Files**
- Create: src/auteur/beginner/studio_architecture_graph_intent.py
- Create: tests/test_beginner_studio_architecture_graph_intent.py
- Inspect: src/auteur/beginner/studio_architecture.py:50-220 and existing B1 model.

**Interfaces**
- GraphAnchor: Pydantic object with kind, id, optional field, optional recorded reference address. Validate mutually exclusive field/reference and bounded strings.
- GraphIntent: operation = explain|challenge|explore|compare|connect_to_ask|revise, expected_candidate_request_sha256, anchors (1–3), author_text (maximum 4000 chars); client-supplied sourceRef is not a field.
- resolve_graph_intent(candidate: dict, actual_candidate_request_sha256: str, intent: GraphIntent) -> dict: canonical resolved anchors with actual record, current sourceRef, field value/reference endpoints and bounded recorded support. This is **pure**; callers acquire the existing filesystem lock before verifying live state and invoking it.

- [ ] **Step 1 — Write failing tests** for all seven entity/link/genre interaction kinds plus complex emotion; genre_contract by genre_node_id; source field path; exact per-side sourceRef after array reorder; ambiguous duplicate reference rejection; absent two-anchor relation; same title different ID; invalid/duplicate anchors; wrong SHA; author_text limit. Expected: unresolved GraphIntent/resolve_graph_intent tests FAIL.
- [ ] **Step 2 — Run RED:** python -m pytest tests/test_beginner_studio_architecture_graph_intent.py -q. Expected: failures due to missing source resolver, not test-import syntax mistakes.
- [ ] **Step 3 — Implement minimal resolver** using actual v2 schema and explicit references only. No circular import: resolver accepts validated candidate dictionaries and imports no Studio architecture runtime from its caller. A reference with ambiguous repeated owner/field/target must error, not acquire fabricated identity.
- [ ] **Step 4 — Run GREEN:** the same pytest file and existing tests/test_beginner_studio_architecture_review.py. Expected: all test cases in both files pass on implementation checkout.
- [ ] **Step 5 — Commit** source resolver + tests. Suggested message: feat(studio): resolve typed graph intention against current candidate.

**Acceptance:** No fabricated relation or unchecked client sourceRef can enter a host-agent packet.

### Task 2: Provide a pure contextual action and relationship projection

**Files**
- Create: src/auteur/beginner/browser/studio_architecture_graph_actions.js
- Create: tests/test_studio_architecture_graph_actions.mjs

**Interfaces**
- projectGraphSelection(candidate, selectedAnchors) -> {anchors, recordedRelations, missingRelation, components}. Source locations are **tentative UI projections** only.
- availableGraphActions(candidate, selectedAnchors) -> [{operation,label,description,kind}], deterministic and bounded.
- traceRecordedRelationships(candidate, anchor, {maxHops:1}) -> recorded typed links and references, not inferred dependencies.

- [ ] **Step 1 — Write failing Node tests:** nodes/links/genre interactions, emotion and phase fields, source-backed references, no recorded Memory Economy↔Wonder direct relation, at most three anchors, two-anchor Connect-to-Ask, no "Revise" automatically invoked, and deterministic story-independent action ordering.
- [ ] **Step 2 — Run RED:** node --test tests/test_studio_architecture_graph_actions.mjs. Expected: missing production exports / failing assertions.
- [ ] **Step 3 — Implement** a pure projector, reusing B1's ideas without importing its prototype as an authority; do not copy its unverified edge inference or sourceRef logic blindly.
- [ ] **Step 4 — Run GREEN:** node --test tests/test_studio_architecture_graph_actions.mjs tests/test_studio_architecture_reader.mjs. Expected: all tests pass.
- [ ] **Step 5 — Commit** projector/tests. Suggested message: feat(studio): project typed graph creative actions.

**Acceptance:** Relation types stay separate; no direct edge is generated from a genre contract's emotion field.

### Task 3: Make nodes, edges and component fields directly selectable

**Files**
- Create: src/auteur/beginner/browser/studio_architecture_graph_selection.js
- Create: tests/test_studio_architecture_graph_selection.mjs
- Modify: src/auteur/beginner/browser/studio.js (minimal graph draw and inspector hooks)
- Modify: src/auteur/beginner/browser/studio.html (linear relationship index and contextual menu)
- Modify: src/auteur/beginner/browser/studio.css (hit targets / focused states)
- Modify: src/auteur/beginner/server.py (new asset allowlist entry)

**Interfaces**
- createGraphSelectionController({getCandidate,onSelect,graphRoot,indexRoot,inspectorRoot}) -> {select,clear,onCandidateChange,destroy}.
- Selection callback uses (kind,id,optional field/reference) with existing canvas and active request SHA; it never writes CanvasStore.
- Visible direct SVG edges currently have data-architecture-link-id and data-genre-interaction-id inside #edges, which is aria-hidden; add separate hit targets for pointer use and equivalent keyboard buttons in a real linear index outside the aria-hidden SVG.

- [ ] **Step 1 — Write failing UI/controller tests** for click on node, recorded directed link and genre interaction; inspector field; recorded contract/phase reference; keyboard linear index; selected anchor chips; panning/zoom coexistence; typing after rerender; different canvas/source clears selection.
- [ ] **Step 2 — Run RED:** node --test tests/test_studio_architecture_graph_selection.mjs. Expected: controls do not exist or new interaction fails.
- [ ] **Step 3 — Implement** event routing and minimal Studio hooks, preserving existing chooseCandidate, renderer, facets and Focused Unfolding. Do not turn the SVG itself into the sole keyboard interaction surface.
- [ ] **Step 4 — Run GREEN:** new selection tests plus tests/test_studio_architecture_reader.mjs and tests/test_studio_unfolding_controller.mjs. Expected: passed; no inspector focus regression.
- [ ] **Step 5 — Commit** selection/UI code and tests. Suggested message: feat(studio): first-class semantic graph selection.

**Acceptance:** A real edge can be selected as easily as a node; no graph presentation gesture changes architecture data.

## Stage B — Validated agent interaction and explicit holistic revision

### Task 4: Allow source-verified graph intent in the existing Revise workflow

**Files**
- Modify: src/auteur/beginner/studio_architecture.py:792-832, 833-944 (only required request/review projection changes)
- Modify: src/auteur/beginner/server.py (existing architecture/prepare handler)
- Create: tests/test_beginner_studio_architecture_graph_revision.py

**Interfaces**
- prepare_architecture(store: CanvasStore, instruction: str="", graph_intent: dict|None=None) -> dict, backward-compatible. If supplied, graph_intent.operation must equal revise and graph_intent.author_text must equal submitted instruction exactly.
- Under the existing canvas filesystem lock, current candidate/SHA/source/guidance must be current and resolve_graph_intent must succeed before writing a HostAgentRequest. Include canonical selected support as additional structured request context; record the focus receipt inside request.user, not in a second revision store.
- Existing complete_architecture remains full valid ArchitectureCandidate v2; project_architecture exposes validated review focus without changing canonical authoring data.

- [ ] **Step 1 — Write failing lifecycle tests:** valid node/link/field anchored holistic revision; no-intent legacy prepare unchanged; wrong current candidate SHA, changed source/guidance and cross-canvas anchor rejected without new latest_request pointer; no title rebound; only explicit revision triggers prepare; complete and apply remain whole-working only.
- [ ] **Step 2 — Run RED:** python -m pytest tests/test_beginner_studio_architecture_graph_revision.py -q. Expected: new graph intent not supported.
- [ ] **Step 3 — Implement** optional server-verified intent plus persistence in the existing signed host-agent request user payload; do not loosen complete/review/apply concurrency checks or create a graph-specific candidate format.
- [ ] **Step 4 — Run GREEN:** new graph revision tests and tests/test_beginner_studio_architecture_review.py, plus the existing focused agent-first architecture tests listed in STATUS.md. Expected: old callers and new anchored callers pass.
- [ ] **Step 5 — Commit** backward-compatible request integration. Suggested message: feat(studio): source-bound graph context for holistic revision.

**Acceptance:** A selected graph anchor is a context qualifier, never authority to change canon or to skip whole-candidate validation.

### Task 5: Build a separate read-only agent inquiry lifecycle

**Files**
- Create: src/auteur/beginner/studio_architecture_inquiry.py
- Create: tests/test_beginner_studio_architecture_inquiry.py
- Modify: src/auteur/beginner/server.py (architecture/inquiry GET and prepare/host-agent-response POST)
- Reuse: src/auteur/host_agent.py (do not duplicate packet validation)

**Interfaces**
- prepare_architecture_inquiry(store: CanvasStore, graph_intent: dict) -> dict
- complete_architecture_inquiry(store: CanvasStore, payload: dict) -> dict
- project_architecture_inquiry(store: CanvasStore) -> dict
- ArchitectureInquiryResult: structured v1 analysis; 0–8 source-addressable recorded_observations; 0–5 alternative hypotheses; 0–8 uncertainties; literal provenance labels. A model-generated claim is an interpretation, not source-validated truth.
- Host role = studio_architecture_inquiry; store immutable packets/receipts only under CanvasStore's existing architecture subtree without touching architecture/latest_request.json or architecture/current.json.
- HTTP: GET /api/beginner/studio/canvases/{canvas}/architecture/inquiry; POST .../architecture/inquiry/prepare and .../architecture/inquiry/host-agent-response.

- [ ] **Step 1 — Write failing tests:** inquiry explains/challenges/explores without a revised candidate; valid host-agent request SHA/response verification; no architecture pointer/current write; duplicate completion idempotence; wrong response SHA rejection; source/guidance/canvas changes make response historical-stale; unsupported hypothesis masquerading as recorded link not auto-admitted.
- [ ] **Step 2 — Run RED:** python -m pytest tests/test_beginner_studio_architecture_inquiry.py -q. Expected: new inquiry contract not defined.
- [ ] **Step 3 — Implement** signed host-agent packet, validated bounded read-only response, append-only request/receipt under the existing architecture folder, and three narrow routes. No provider-specific API and no ArchitectureCandidate coercion for inquiry.
- [ ] **Step 4 — Run GREEN:** new inquiry tests plus existing host-agent request/response tests and tests/test_beginner_studio_architecture_review.py. Expected: all targeted cases pass.
- [ ] **Step 5 — Commit** inquiry and tests. Suggested message: feat(studio): read-only graph grounded agent inquiry.

**Acceptance:** Challenge and Explore never produce review_ready, working architecture writes or accepted-story mutations.

### Task 6: Implement the persistent graph-grounded creative-agent panel

**Files**
- Create: src/auteur/beginner/browser/studio_architecture_creative_panel.js
- Create: src/auteur/beginner/browser/studio_architecture_agent_bridge.js
- Create: tests/test_studio_architecture_creative_panel.mjs
- Modify: src/auteur/beginner/browser/studio.html, studio.js, studio.css
- Modify: src/auteur/beginner/server.py (asset allowlist)

**Interfaces**
- createCreativePanel({root,onAction,onRevise,onClear}) -> {setSelection,setStatus,setInquiryResult,setAuthorText,reset,destroy}.
- createArchitectureAgentBridge({canvasId,fetchJson,readProjection,onInquiryResult,onRevisionProjection}) -> {prepareInquiry,completeInquiry,prepareRevision,refresh,reset}.
- Preserve author_text exactly; explicit button labels distinguish **Ask coding agent (no revision)** from **Request holistic revision**. A draft is never labeled "completed" until a validated HostAgentResponse is received.

- [ ] **Step 1 — Write failing DOM/client tests** for tailored action menu, bounded 1–3 anchor chips and exact author instruction, edited text preservation across rerenders, prepare vs execute status, no fetch on Inspect/Trace, distinct inquiry/revision routes, stale selection clearing, escaped untrusted text.
- [ ] **Step 2 — Run RED:** node --test tests/test_studio_architecture_creative_panel.mjs. Expected: new panel/bridge API absent.
- [ ] **Step 3 — Implement** the panel and bridge using minimal Studio integration. Reuse current server routes and neutral host-agent handoff UI patterns; no silent provider calls and no creation of inquiry results without valid completion.
- [ ] **Step 4 — Run GREEN:** panel tests, graph action/selection tests and existing Studio reader/facet tests. Expected: all pass with one selected node, one edge, a component and a two-anchor pair.
- [ ] **Step 5 — Commit** panel/bridge and tests. Suggested message: feat(studio): contextual agent conversation from graph selection.

**Acceptance:** The author always knows the selected source, whether an agent ran, and whether an architecture revision was actually requested.

## Stage C — Return to selected context and evaluate a coherent journey

### Task 7: Link inquiry results and holistic revisions back to graph focus

**Files**
- Create: src/auteur/beginner/browser/studio_architecture_creative_feedback.js
- Create: tests/test_studio_architecture_creative_feedback.mjs
- Modify: src/auteur/beginner/browser/studio_architecture_revision_bridge.js
- Modify: src/auteur/beginner/browser/studio.js (small projection/selection hooks)
- Modify: src/auteur/beginner/studio_architecture.py only if Task 4 has not already exposed focus receipt.

**Interfaces**
- createCreativeFeedbackController({getCandidate,selectGraphFocus,openHybridReview,renderInquiry}) -> {onInquiry,onReviewReady,onSourceChanged,destroy}.
- Existing hybrid mountRevisionReview has selectFocus({kind,id}); bridge may add an optional source-backed initial focus, without replacing readable summary or whole diff.
- A component focus maps to its owner record (kind,ID) with optional field hint; a reference focus maps to recorded owner/relationship context; a removed After element shows a missing-side state.

- [ ] **Step 1 — Write failing tests:** inquiry response restores original node/edge/field; revision review_ready auto-opens only opt-in focused view; before/after selected link old/new endpoints; unchanged shape changed meaning; removed element has no title rebinding; unrelated changes remain visible via whole summary; canvas switch clears stale focus.
- [ ] **Step 2 — Run RED:** node --test tests/test_studio_architecture_creative_feedback.mjs. Expected: focus bridge not implemented.
- [ ] **Step 3 — Implement** source receipt propagation and hybrid focused entry with no new diff computation or per-node apply controls. The normal readable review stays available.
- [ ] **Step 4 — Run GREEN:** feedback tests, current hybrid view/compare tests and relevant Studio architecture review tests. Expected: passed; exact source refs remain distinct Before/After.
- [ ] **Step 5 — Commit** return-to-focus feature. Suggested message: feat(studio): return graph creative focus after agent response.

**Acceptance:** The graph explains the *whole* change and can return to a particular source; selected focus never hides the full candidate diff.

### Task 8: Verify actual served Studio, authority and accessibility

**Files**
- Create: tests/test_beginner_studio_architecture_interactive_browser.py
- Modify: tests/test_beginner_studio_architecture_graph_revision.py, tests/test_beginner_studio_architecture_inquiry.py and relevant Node tests for discovered failures
- Inspect: tests/test_beginner_studio_architecture_browser.py, tests/test_beginner_studio_architecture_visual_review.py, tests/test_focused_unfolding_browser.py

**Interfaces**
- Test a genuine disposable CanvasStore with recorded rich candidate, source-validated inquiry HostAgentResponse, an explicitly prepared holistic revision and an actual review_ready proposal. The agent response may be fixture-generated for lifecycle testing, but must be labeled simulated; do not claim an independent agent executed.

- [ ] **Step 1 — Write failing served-browser tests** for direct SVG link pointer selection and equivalent keyboard linear index; component fields and explicit-reference actions; no invented Memory Economy↔Wonder link; two-anchor Connect-to-Ask returns alternatives not a candidate; explicit Revise creates pending request; completed revision reopens original typed focus; 390px and no console error.
- [ ] **Step 2 — Run RED:** python -m pytest tests/test_beginner_studio_architecture_interactive_browser.py -q. Expected: new interactive journey unsupported before final browser wiring.
- [ ] **Step 3 — Resolve observed integration and accessibility findings** with test-first fixes only: focus continuity across DOM rerender, high-DPI edge hit targets, scroll/zoom, stale action disabling, HTML script allowlist, host-agent packet completion and backward compatibility.
- [ ] **Step 4 — Run GREEN:** the new browser tests, tests/test_beginner_studio_architecture_browser.py, tests/test_beginner_studio_architecture_visual_review.py, tests/test_focused_unfolding_browser.py, all new Node tests and relevant Python host-agent tests. Then run the full repository standard suite and record every pre-existing failure against baseline. Expected: affected tests pass; full-suite status accurately documented without hiding failures/skips.
- [ ] **Step 5 — Commit** verified browser journey and corrections. Suggested message: test(studio): qualify interactive creative graph browser journey.

**Acceptance:** Test evidence must distinguish real served Chromium, simulated coding-agent completion and author experience; do not equate one with the others.

### Task 9: Comparative evaluation, final design decision and merge

**Files**
- Create: docs/research/2026-11-05-unified-agent-interactive-graph-evaluation.md
- Modify: STATUS.md after actual implementation results exist
- Modify: docs/superpowers/specs/2026-11-05-unified-agent-interactive-creative-graph-design.md only if findings legitimately change an agreed requirement (record rationale)

**Interfaces**
- Comparative task matrix: actual current Studio baseline vs unified graph, same recorded Memory Economy candidate, same questions, same source authority. Distinguish inspect, critique recorded link, Connect-to-Ask missing relation, holistic revision, focus return, accessible navigation and stale-source errors.

- [ ] **Step 1 — Record source-grounded comparison tasks** with observable outcomes: correct source identity, successful author question, ability to distinguish recorded link from hypothesis, completeness of revision context, ability to find original focus after revision, and observed navigation effort.
- [ ] **Step 2 — Run a real author walkthrough if one is available** and document participant/task conditions; if unavailable, explicitly state **no human author evidence** and do not make up comprehension or quality scores.
- [ ] **Step 3 — Perform adversarial final source review** for mistaken source authority, stale/cross-canvas leakage, prompt/response spoofing, unintended writes, false causal rationale, complex-emotion/reference selection, no-op responses, accessibility and long candidate text. Add focused RED→GREEN regression tests for any important faults found.
- [ ] **Step 4 — Rerun the targeted and full suites** plus genuine served-browser journey; write actual commands, commit IDs, environment and observed pass/fail/skip counts in the evidence ledger. Select outcome: isolated research only, opt-in experiment, verified default integration, or reject/rework. Default/release promotion needs relevant human evidence or a separate explicitly documented owner sufficiency decision.
- [ ] **Step 5 — Open and reconcile focused PR(s)** separating independently reviewable source resolver, UI and inquiry work as appropriate; merge only verified repository-policy-permitted work, update STATUS.md with exact qualification ceiling, and report owner rulings and deferred issues. Never substitute an implementation report for tests that were not executed.

**Acceptance:** A successful result may remain opt-in with unqualified author benefit. No feature is declared more creative simply because it renders or validates source IDs.

---

## Delivery checkpoints and authority boundaries

- **Checkpoint A (Tasks 1–3):** Author can source-honestly inspect nodes, edges, components and explicit references and compose contextual intentions. No provider call, no architecture mutation.
- **Checkpoint B (Tasks 4–6):** Author can submit a validated read-only inquiry or explicitly request a complete working revision. Both use actual host-agent packet contracts; source freshness is enforced.
- **Checkpoint C (Tasks 7–9):** Results return to the selected graph focus, with the existing hybrid comparison for revisions and truthful final qualification.

**No completion claims in this planning turn.** This plan is actionable documentation, not evidence that the new graph interactions, inquiry routes or agent integration have been implemented.

## Governing design aphorisms

1. It is **not** a graph that authors must manually engineer; it is **actually** a semantic interface to the coding agent's creative reasoning.
2. It is **not** a source of automatically accepted story facts and is **not** a replacement for author judgment; it is **actually** a source-verified, reviewable creative dialogue.
3. A meaningful relationship is **actually** a first-class creative question, not merely a line between nodes.
