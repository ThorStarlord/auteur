# Hybrid Narrative Architecture Revision Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking. The author has previously preferred **native/inline execution without subagents**; honor that preference unless they change it.

**Goal:** Let an author understand and evaluate a coding agent's *holistic working Narrative Architecture revision* through a readable semantic change summary, synchronized Before/After architecture views, and a focused entity/relationship difference overlay, without changing source authority or the existing revision workflow.

**Architecture:** Compare the actual current and proposed ArchitectureCandidate v2 snapshots already present in Studio's review_ready response, using typed stable IDs, exact per-side source locations and deterministic field-level diffs. Stage 1 is a standalone source-bound visual comparison with recorded/synthetic fixtures and an evaluation. Stage 2 is a **conditional opt-in** Studio integration reusing the existing review_ready projection and apply endpoint, never a new version store or generation pipeline. Do not make it a release default without real-author evidence or an explicitly documented owner decision.

**Tech Stack:** Existing Python 3.11+ / Pydantic architecture schema, vanilla JS/DOM/SVG and CSS (no new frontend dependencies), Node built-in node:test, pytest, and established Playwright/Chromium browser tests where available.

**Spec:** [Hybrid Narrative Architecture Revision Review Design](../specs/2026-11-05-hybrid-narrative-architecture-revision-review-design.md).

**Prerequisites:** Read MISSION.md, STATUS.md, docs/narrative-architecture.md, previous 2026-11-03 agent-first architecture design, the 2026-11-04 graph exploration, and the PR #512 prototype assessment. Read current code rather than assuming that documentation claims have all been independently qualified.

**Decision:** The author selected **hybrid review** as the design direction: readable meaning first, side-by-side whole architectures second, focused overlay on demand. This plan is a planning artifact; no implementation or production activation has been authorized merely by its publication.

## Global Constraints

- **Authority:** No auto-accept, no accepted Identity/Structure/Realization/Expression/ontology write, and no mutation from viewing, selecting, comparing, panning, hovering or toggling overlays.
- **Lifecycle:** Reuse project_architecture -> review_ready -> apply_architecture_review; current/proposed snapshots remain distinct until explicit whole-working-revision apply.
- **Source:** Before = projection.candidate and candidate_request_sha256; After = projection.review.candidate and review.request_sha256; review.prior_request_sha256 must equal the Before request SHA.
- **Trust:** Candidate summary is **revised architecture summary**, not causal rationale. Constraints are **requirements to verify**, not proven preserved. The visual diff only establishes observable JSON/typed field changes.
- **Identity:** Pair by (kind, stable ID), with genre_contract keyed by genre_node_id. Never pair by title, narrative similarity, source array index, proximity or apparent layout.
- **Exact locations:** Determine per-side array positions from the actual input snapshot; never assume nodes/3 is stable across revisions, even if memory_economy ID is stable.
- **Boundaries:** Preserve existing Studio text review, facets, graph, Focused Unfolding, Full Architecture, and host-agent provider neutrality.
- **Presentation:** Accessible linear diff is authoritative fallback; SVG/visual arrangement is optional; no color-only semantics; no spatial proximity as a causal claim.
- **Compatibility:** Empty/legacy/unavailable comparison stays readable in the existing Studio; do not introduce v3 schema, new graph database, new persistence owner or a parallel apply endpoint.
- **Evidence:** Automated tests, actual served-browser observations, synthetic fixtures, independent agent execution and human author studies are not interchangeable.
- **Scope of previous defects:** Do not divert into unrelated B1/B2 prototype repairs or general Studio overhaul. The new review surface must independently avoid misleading evidence/authority copy.

## Review Focus — high-risk input classes

1. **Same geometry, changed meaning:** field-only changes to node summary or emotion target must appear in the summary, index and focus view (Tasks 1, 3, 5).
2. **Link rewiring, duplicate names and reordered arrays:** stable typed identity, before/after endpoints, and distinct source locations must remain correct (Tasks 1–2, 4).
3. **Removed/retyped author commitment and unverified constraint:** never falsely report "preserved"; show a review warning with exact old/new values (Tasks 1, 3, 6).
4. **Stale or superseded review/canvas:** old comparison must be hidden or disabled; the existing server must refuse outdated apply (Tasks 2, 7–8).
5. **No graph/dense graph/keyboard/mobile:** no fabricated edges, bounded focus, preserved text access and workable 390px view; empty/summary-only differences remain truthful (Tasks 2, 4–6).

---

## File ownership and decomposition

### Existing code — read and preserve ownership

| Path | Responsibility |
| --- | --- |
| src/auteur/beginner/studio_architecture.py | Current/proposed review projection, source freshness and apply guard |
| src/auteur/beginner/studio_architecture_review.py | Existing candidate_diff and changed_components for working review; do not replace |
| src/auteur/beginner/browser/studio.js | Main Studio lifecycle and review_ready/render/apply integration (minimal conditional change only) |
| src/auteur/beginner/browser/studio_architecture_reader.js | Existing readable architecture view, never replaced |
| src/auteur/beginner/browser/studio.html | Host area for an opt-in visual review if Stage 2 is authorized |
| src/auteur/beginner/browser/studio.css | Existing Studio styles and responsive baseline |
| src/auteur/beginner/server.py | Explicit allowlist mapping for any new production script |
| tests/test_beginner_studio_architecture_review.py | Existing Python diff and host-agent lifecycle regressions |

### Stage 1 — new isolated experiment files

| Path | Single responsibility |
| --- | --- |
| docs/prototypes/hybrid-architecture-revision/README.md | Serve/run instructions, known limits and fixtures |
| docs/prototypes/hybrid-architecture-revision/fixtures.mjs | Deterministic, explicitly **synthetic** revisions of the recorded rich candidate; no fabricated historical agent response |
| docs/prototypes/hybrid-architecture-revision/compare.mjs | Pure typed semantic diff / source mapping / summary and status model |
| docs/prototypes/hybrid-architecture-revision/layout.mjs | Stable union graph positions and one-hop focused subgraph; no semantic inference |
| docs/prototypes/hybrid-architecture-revision/view.mjs | Readable summary, before/after graphs, focus overlay and linear change index |
| docs/prototypes/hybrid-architecture-revision/index.html | Isolated, explicitly labeled research UI |
| docs/prototypes/hybrid-architecture-revision/styles.css | Responsive / focus / high-contrast presentation |
| docs/prototypes/hybrid-architecture-revision/compare.test.mjs | Pure diff, SHA, link redirection, provenance cases |
| docs/prototypes/hybrid-architecture-revision/layout.test.mjs | Pair alignment, dense and empty cases |
| docs/prototypes/hybrid-architecture-revision/view.test.mjs | DOM behavior, keyboard focus, view modes, text alternatives |
| tests/test_hybrid_architecture_revision_browser.py | Served Chromium and current Studio baseline comparisons |
| docs/research/2026-11-05-hybrid-architecture-revision-evaluation.md | Actual evidence matrix and go/no-go, not invented author feedback |

Stage 1 files must not load an actual provider, write CanvasStore, depend on cloud services, or suggest that a synthetic revision was generated by an independent agent.

### Stage 2 — conditional real Studio integration only after the gate

| Path | Single responsibility |
| --- | --- |
| src/auteur/beginner/browser/studio_architecture_revision_compare.js | Promoted, shared deterministic projection (move, do not maintain divergent copies) |
| src/auteur/beginner/browser/studio_architecture_revision_view.js | Read-only render/selection/overlay controller for production review area |
| src/auteur/beginner/browser/studio.html | Opt-in "Compare visually (experimental)" control inside existing architecture-review section |
| src/auteur/beginner/browser/studio.js | Wire current candidate, pending review candidate, request identities and text fallback to read-only view |
| src/auteur/beginner/browser/studio.css | Scope-specific responsive and accessible visual review styles |
| src/auteur/beginner/server.py | Allowlist only the new JS script assets |
| tests/test_studio_architecture_revision_compare.mjs | Production projection/test parity |
| tests/test_studio_architecture_revision_view.mjs | Production view and focus tests |
| tests/test_beginner_studio_architecture_visual_review.py | Exact review_ready and apply/freshness HTTP integration |
| tests/test_hybrid_architecture_revision_browser.py | Actual served Studio opt-in review across desktop/mobile |

No second persistence file, parallel graph store, new Studio route, or Pydantic candidate schema is planned.

---

## Stage 1 — Isolated source-bound comparison and evidence

### Task 0: Admit baseline, snapshots and a truthful research fixture

**Files:**
- Create: docs/prototypes/hybrid-architecture-revision/README.md
- Create: docs/prototypes/hybrid-architecture-revision/fixtures.mjs
- Create: docs/research/2026-11-05-hybrid-architecture-revision-evaluation.md
- Inspect: docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json, current review_ready contract and existing textual Studio review.

**Interfaces:**
- loadReviewFixture(name) -> {before,after,beforeRequestSha,afterRequestSha,expectedPriorSha,label,synthetic:true}.
- A deterministic synthetic mutation must include changed meaning, redirected link, changed genre or phase, author-declared target alteration, and a summary-only variant. Preserve v2 shape and validated unique IDs.

- [ ] **Step 1 — Record baseline.** Run git status --short, git rev-parse HEAD, node --test tests/test_studio_architecture_reader.mjs, and python -m pytest tests/test_beginner_studio_architecture_review.py tests/test_beginner_studio_architecture_browser.py -q; capture actual outcomes.
- [ ] **Step 2 — Admit source pair.** Build validated deterministic before/after fixtures using the *real recorded* candidate as Before and **clearly synthetic** After; preserve original source and record each synthetic edit.
- [ ] **Step 3 — Record provenance.** README/ledger distinguishes recorded prior agent candidate, test-generated mutation and real current Studio baseline; no human outcome claims.
- [ ] **Step 4 — Inspect current review behavior.** Demonstrate that a completed revision exposes both baseline and proposed candidates through project_architecture() while the baseline remains active until apply_architecture_review().
- [ ] **Step 5 — Commit** fixture and baseline evidence.

**Gate:** Synthetic revision is never presented as observed creative quality or a historical real-agent result.

### Task 1: Build the pure typed semantic difference model

**Files:**
- Create: docs/prototypes/hybrid-architecture-revision/compare.mjs
- Create: docs/prototypes/hybrid-architecture-revision/compare.test.mjs

**Interfaces:**
- compareArchitectureRevision({before,after,beforeRequestSha,afterRequestSha,expectedPriorSha}) -> {status, beforeRequestSha, afterRequestSha, summary, items, graph}.
- items entries: {kind,id,key,change,beforeRecord,afterRecord,beforeSourceRef,afterSourceRef,changedFields}, with key = kind + ':' + id and change in added | removed | changed | unchanged.
- changedFields entries: {field,beforeValue,afterValue} with actual values, not short narrative summaries.
- Include every existing comparable collection: nodes, links, emotion_targets, complex_emotions, genre_contracts, genre_interactions, phases; plus top-level summary as a singleton not a graph node.

- [ ] **Step 1 — Write failing tests.** Cases: unchanged node geometry with changed summary, link ID with changed endpoints/function, reordering arrays changes only sourceRef positions, genre contract keyed by genre_node_id, complex emotion nested list change, same titles with distinct IDs, removed/retitled/retyped author_declared emotion, summary-only and no-op comparisons.
- [ ] **Step 2 — Run RED:** node --test docs/prototypes/hybrid-architecture-revision/compare.test.mjs; expected failures until export exists.
- [ ] **Step 3 — Implement** deterministic comparison using exact typed IDs, per-snapshot array indices, field-level deep equality with order-sensitive arrays where semantic ordering matters; fail closed on invalid SHA or mismatched expectedPriorSha.
- [ ] **Step 4 — Run GREEN** plus existing Node reader tests; inspect one full JSON diff manually and confirm changed_fields include endpoints, nested phase activations and provenance.
- [ ] **Step 5 — Commit** model and tests.

**Gate:** No inferred link, renamed matching or claim that unchanged fields prove accepted author constraints were satisfied.

### Task 2: Build synchronized union-layout and local-focus projections

**Files:**
- Create: docs/prototypes/hybrid-architecture-revision/layout.mjs
- Create: docs/prototypes/hybrid-architecture-revision/layout.test.mjs

**Interfaces:**
- unionGraphLayout(comparison,{columns=6}={}) -> {positionsByNodeId,beforeGraph,afterGraph}, where identical node IDs have the same coordinates on both sides.
- focusedGraphDiff(comparison,{kind,id}) -> {focus,beforeNeighborhood,afterNeighborhood,fieldChanges,missingSide}, with at most recorded one-hop neighbors by explicit links or genre interactions.

- [ ] **Step 1 — Write failing tests** for stable shared-ID position, added/removed reserved positions, link redirection with separate old/new edge endpoints, reciprocal/directed links, non-spatial emotion/phase focus, empty topology, 80-node/180-link upper bound, and changed fields with no visible edges.
- [ ] **Step 2 — Run RED:** node --test docs/prototypes/hybrid-architecture-revision/layout.test.mjs.
- [ ] **Step 3 — Implement** deterministic union ordering and bounded one-hop projection, reading only actual candidate links/genre interactions and preserving per-side source refs. Do not invent transitions from proximity or phrases.
- [ ] **Step 4 — Run GREEN** and assert fixed positions for the same nodes even when Before and After arrays have different orders.
- [ ] **Step 5 — Commit** layout projection and tests.

**Gate:** Graph layout is presentation, not evidence of meaning; meaningful changes to a node remain inspectable with unchanged geometry.

### Task 3: Implement readable semantic summary and change index

**Files:**
- Create: docs/prototypes/hybrid-architecture-revision/view.mjs
- Create: docs/prototypes/hybrid-architecture-revision/view.test.mjs
- Create: docs/prototypes/hybrid-architecture-revision/index.html
- Create: docs/prototypes/hybrid-architecture-revision/styles.css

**Interfaces:**
- mountRevisionReview(root,{comparison,document,initialMode='summary'}) -> {setMode,selectFocus,reset,destroy}.
- mode in summary | compare | focus; mounted view is always read-only.
- A typed change-index button can focus any item, including emotion_target, complex_emotion, genre_contract, phase, and summary, even if the graph lacks a spatial node for it.

- [ ] **Step 1 — Write failing view tests** for text-first summary, visible requested change when supplied, added/removed/changed counts, clickable typed index and sourceRef labels, no-op/summary-only, author-declared loss alert, and accepted constraints labeled "Requirements to check (not verified)".
- [ ] **Step 2 — Run RED:** node --test docs/prototypes/hybrid-architecture-revision/view.test.mjs.
- [ ] **Step 3 — Implement** readable heading, exact changes and index. Label agent candidate summary "Revised architecture summary"; never generate causal rationale from candidate.summary. Show a usable fallback when visual data is unavailable.
- [ ] **Step 4 — Run GREEN** and inspect the rendered summary against the original and proposed candidate JSON. UI may abbreviate long text, but allow full expansion of every changed field.
- [ ] **Step 5 — Commit** summary/index view and tests.

**Gate:** Summary/semantic index alone answers what changed even with no SVG available.

### Task 4: Add synchronized Before/After graph comparison

**Files:**
- Modify: docs/prototypes/hybrid-architecture-revision/view.mjs
- Modify: docs/prototypes/hybrid-architecture-revision/view.test.mjs
- Modify: docs/prototypes/hybrid-architecture-revision/styles.css

**Interfaces:**
- setMode('compare') displays **Before — current working** and **After — un-applied proposal** from one union-layout map; selectFocus({kind,id}) highlights corresponding records on both sides without title matching.

- [ ] **Step 1 — Write failing tests** for labeled independent snapshots, shared-ID selection sync, added/removed absence labels, directional link redirection, no highlighted unchanged node merely because adjacent links changed, and index/graph equivalent navigation.
- [ ] **Step 2 — Run RED:** node --test docs/prototypes/hybrid-architecture-revision/view.test.mjs.
- [ ] **Step 3 — Implement** two explicit read-only graph surfaces with shared semantic coordinates, scope/filter/fit controls and a persistent linear relationship index; a graph path is a supported enhancement, not the only selectable control.
- [ ] **Step 4 — Run GREEN**, confirm stable layout during Before/After navigation, and inspect a pair where only a non-spatial phase or emotion changed.
- [ ] **Step 5 — Commit** whole-comparison UI and tests.

**Gate:** Side-by-side views never silently merge two proposals into one graph.

### Task 5: Add selected-entity and relationship focused overlay

**Files:**
- Modify: docs/prototypes/hybrid-architecture-revision/view.mjs
- Modify: docs/prototypes/hybrid-architecture-revision/view.test.mjs
- Modify: docs/prototypes/hybrid-architecture-revision/styles.css

**Interfaces:**
- setMode('focus') and selectFocus({kind,id}) display previous/proposed local records, full changedFields list and bounded recorded one-hop context, with explicit layer-toggle text **Before**, **After** and **Differences**. No inferred downstream narrative effects.

- [ ] **Step 1 — Write failing tests** for changed link endpoints, unchanged-ID semantic-only engine, genre-interaction mechanism, emotion provenance, phase nested activations, removed node placeholder, full long text and return-to-comparison selection.
- [ ] **Step 2 — Run RED** using the focused view test names from view.test.mjs.
- [ ] **Step 3 — Implement** a local before/after overlay of only the selected neighborhood plus a semantic field-change inspector, exposing actual side/request source references. Any inferred effect is labeled a question, not an observed result.
- [ ] **Step 4 — Run GREEN** and verify the author can explain a change without understanding SVG geometry.
- [ ] **Step 5 — Commit** focused overlay and regression tests.

**Gate:** The user examines a selected difference; no per-element apply control or hypothetical causality is introduced.

### Task 6: Conduct fair baseline comparison and record qualification ceiling

**Files:**
- Create: tests/test_hybrid_architecture_revision_browser.py
- Modify: docs/prototypes/hybrid-architecture-revision/README.md
- Modify: docs/research/2026-11-05-hybrid-architecture-revision-evaluation.md

**Interfaces:** Evaluate current Studio textual architecture review and current graph against isolated hybrid review, using equivalent recorded Before and synthetic After candidates with explicit provenance.

- [ ] **Step 1 — Write browser tests** for actual served module loading, readable summary, link redirection, focus overlay, keyboard change-index route, 390px Before/After/Differences switcher, no console errors and no mutation/network generation on inspection.
- [ ] **Step 2 — Run** node --test docs/prototypes/hybrid-architecture-revision/*.test.mjs and python -m pytest tests/test_hybrid_architecture_revision_browser.py -q; record real pass/fail/skip conditions, never convert missing browser to success.
- [ ] **Step 3 — Run the same author tasks** against actual served current Studio review (using a disposable project and a valid revision response), and against the hybrid prototype; record misleading states, navigation steps, time/lost context where legitimately observable, and which meanings are correctly explained.
- [ ] **Step 4 — Conduct an author-facing walkthrough if available;** otherwise record "human author evidence not obtained", clearly differentiate simulated executor use from actual author feedback. Include a short explicit go/no-go based on semantic understanding and practical decisions, not presentation attractiveness.
- [ ] **Step 5 — Commit** the comparative matrix and evidence receipts; preserve negative and unresolved findings.

**Gate:** If no consequential gain or no required author evidence is available, **stop here**. Do not call the later Studio integration ready or released.

---

## Stage 2 — Conditional, explicitly authorized Studio integration

**Entry condition:** Stage 1 demonstrates no authority/source mistakes, and the recorded author-facing comparison (or an explicit documented owner policy decision about evidence sufficiency) authorizes a narrowly scoped opt-in integration. If this condition fails, stop after Task 6 and retain the research artifact. No requirement to "finish all tasks" overrides this gate without a new explicit owner decision.

### Task 7: Connect the selected visual review to live review_ready snapshots

**Files:**
- Create: src/auteur/beginner/browser/studio_architecture_revision_compare.js
- Create: src/auteur/beginner/browser/studio_architecture_revision_view.js
- Modify: src/auteur/beginner/browser/studio.html
- Modify: src/auteur/beginner/browser/studio.js
- Modify: src/auteur/beginner/browser/studio.css
- Modify: src/auteur/beginner/server.py
- Create: tests/test_studio_architecture_revision_compare.mjs
- Create: tests/test_studio_architecture_revision_view.mjs

**Interfaces:**
- projectLiveRevision(projection) -> null | compareArchitectureRevision(...), only when status='review_ready', review has a complete candidate and review.prior_request_sha256 matches candidate_request_sha256.
- renderLiveRevision(root,projection,{open,focus,mode}) -> read-only view state. The underlying pure compare code is **moved/promoted**, not separately reimplemented with divergent semantics.
- A collapsed **Compare visually (experimental)** control sits inside #architecture-review; existing text review and current graph remain available.

- [ ] **Step 1 — Write failing unit and source-routing tests** for exact review_ready snapshots, no visual mode when awaiting_host_agent, missing review/candidate, mismatched SHA, and current canvas changes.
- [ ] **Step 2 — Run RED** for tests/test_studio_architecture_revision_compare.mjs and tests/test_studio_architecture_revision_view.mjs.
- [ ] **Step 3 — Promote and connect** Stage 1 comparator/view, add explicitly served JS assets, a scoped opt-in review container, and minimal integration hooks in applyArchitectureProjection(). Preserve text fallback and prevent shared layout state from mutating the normal Studio graph.
- [ ] **Step 4 — Run GREEN** with the new tests plus tests/test_studio_architecture_reader.mjs, tests/test_beginner_studio_architecture_browser.py and relevant JS Studio tests; compare output against original prototype.
- [ ] **Step 5 — Commit** the opt-in integration and targeted regression tests.

**Gate:** No extra persistence or review endpoint; no code path changes current candidate simply by opening the visual review.

### Task 8: Verify server-backed review/apply integrity and accessibility

**Files:**
- Create: tests/test_beginner_studio_architecture_visual_review.py
- Modify: tests/test_hybrid_architecture_revision_browser.py
- Modify: tests/test_beginner_studio_architecture_review.py only for directly relevant regression assertions.

**Interfaces:** Real host-agent response -> review_ready -> visual compare (read-only) -> explicit Apply -> new current working candidate; accepted story unchanged.

- [ ] **Step 1 — Write failing integration tests** for visual comparison before apply, accepted story untouched, old baseline remaining current, wrong request SHA rejection, superseded request rejection, stale Story Vision/guidance rejection and safe canvas switching.
- [ ] **Step 2 — Run RED** for targeted new tests against Stage 2 code.
- [ ] **Step 3 — Implement minimum guard/bridge adjustments** within existing owners; never create a second apply path or override backend validation. Add close/return focus, keyboard semantics, reduced-motion and 390px switched-mode behavior.
- [ ] **Step 4 — Run GREEN:** python -m pytest tests/test_beginner_studio_architecture_visual_review.py tests/test_beginner_studio_architecture_review.py tests/test_hybrid_architecture_revision_browser.py -q plus affected Node Studio gates. Record exact results and known pre-existing failures separately.
- [ ] **Step 5 — Commit** integration guards, accessibility and browser evidence.

**Gate:** "Applied to working architecture" is never represented as acceptance of canonical story. An old review cannot be applied after supersession.

### Task 9: Review, document and make a scoped product decision

**Files:**
- Modify: docs/research/2026-11-05-hybrid-architecture-revision-evaluation.md
- Modify: docs/prototypes/hybrid-architecture-revision/README.md
- Update: STATUS.md only if an actual integration/evidence state changed.

**Interfaces:** Select one outcome: keep isolated prototype; keep opt-in experimental Studio review; promote default visual comparison; or reject/retire. Default promotion is **not automatic**.

- [ ] **Step 1 — Perform adversarial self-review** for false constraint-preservation claims, fabricated agent rationale, stale request/canvas leaks, link endpoint rewiring, long nested values, and focus loss.
- [ ] **Step 2 — Rerun focused gates** and a served browser journey; record real environment, commit SHAs, pass/fail/skips and qualification ceiling.
- [ ] **Step 3 — State the evidence-based decision** and keep the default review text-first unless a real-author outcome or an explicit documented owner decision justifies promotion.
- [ ] **Step 4 — Open focused PR(s)** separating research-only work from conditional opt-in production integration. Do not merge/ship any part that violates repository authority or branch policy; do not claim human validation without a participant.
- [ ] **Step 5 — Integrate the verified permitted scope** and provide a concise status report with PRs, exact tests, what remains unqualified and what would be required for default/release qualification.

**Gate:** Release/default-authoring qualification and narrative-quality claims remain separate. A valid outcome may be a completed experiment with **no** Studio integration.

---

## Traceability and self-review

| Spec requirement | Owning task(s) | Expected evidence |
| --- | --- | --- |
| Readable summary precedes visual graph | 3, 7 | DOM and served-browser |
| Typed per-side source identity and complete semantic fields | 1, 3, 5 | pure tests; exact fixtures |
| Synchronized Before/After graph | 2, 4 | deterministic positions; browser selection |
| Focused one-hop overlay | 2, 5 | link/phase/engine scenarios |
| Genre/phase/emotion changes when topology unchanged | 1, 3, 5 | semantic-only test |
| Author constraint/source truthfulness | 1, 3, 8 | provenance and negative assertions |
| No inferred relation or causal claim | 1, 2, 5 | negative graph tests |
| Safe stale/absent review and apply authority | 1, 7, 8 | request SHA and server tests |
| Mobile/accessibility and large/empty cases | 2, 4, 5, 6, 8 | 390px/keyboard/dense |
| Actual value over baseline and qualification ceiling | 6, 9 | documented comparison |

### Execution posture

The first independently deliverable boundary is **Tasks 0–6: an isolated, evaluated hybrid review**. Tasks 7–9 require the explicit evidence/owner gate above and may be left unexecuted without making Tasks 0–6 a failure. Review after each task and commit coherent work. Use inline/native execution unless the author changes the preferred execution method.

**No completion claim in this planning turn:** This document only specifies future work. It does not mean the UI, a real author study, or production integration already exists.

## Three governing aphorisms

1. It is **not** the movement of nodes that proves a narrative revision; it is **actually** the change in documented narrative meaning.
2. It is **not** two indistinguishable graphs and is **not** an opaque list of JSON edits; it is **actually** a reviewable comparison of coherent working architectures.
3. A source-honest focused overlay is **actually** a way for the author to understand one change without losing the whole story.
