# Narrative Architecture Explanatory Views Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Build and compare three fixture-driven visual explanations of genre morphology and story-specific narrative architecture, then select a justified Studio interaction direction without shipping experimental behavior prematurely.

**Architecture:** An isolated HTML/CSS/ES-module prototype reuses a single immutable source-grounded fixture model and projects three alternative presentations. A read-only semantic adapter separates genre expectation strength, proposal-specific treatment, derivation, provenance, and authority; no prototype writes to the existing CanvasStore, architecture requests, or accepted story. The production integration is a separately warranted follow-up plan after the comparison.

**Tech Stack:** Python >=3.11, pytest >=8, standard-library JSON and HTTP server, vanilla browser JavaScript/ES modules, HTML/CSS; no new web framework, graph engine, UI dependency, provider call or GitHub Actions requirement.

**Spec:** docs/superpowers/specs/2026-10-12-narrative-architecture-visual-explanation.md

## Global Constraints

- **Baseline:** Use unmerged PR #392 (head d33bd2f4aa92b4ff6e29443859bf27751f7e0237 at planning time) and its ancestry #386–#391 as a comparison, not as a qualified release. Recheck exact heads before implementation.
- **Repository:** Main at 85374e705115ec4884b8e0c85f3f69b6fe1c342a at planning time does not contain this Studio; build prototypes in a separate isolated branch/worktree and do not silently merge the draft stack.
- **Scope:** This plan produces a prototype comparison and a selected design recommendation, **not production integration**. Use a separate subsequent implementation plan for a winner.
- **Safety:** Existing Story Vision, CanvasStore persistence, explicit author acceptance, agent request/response source binding, proposal review, and Story Realization remain unchanged.
- **Knowledge:** Current versioned Genre Pack source is erotic_fiction only; legacy Epic Fantasy contract is not a versioned Progression/Heroic Fantasy pack. Mark gaps and disputed requirements honestly. Absence in a pack is unknown coverage, not evidence that something is incompatible, unconventional, or globally original.
- **Evidence:** Do not fabricate screenshot-only source IDs or edge claims. Use verified fixtures where available; label invented demonstration content synthetic.
- **Representation:** Genre convention strength and *story treatment* are independent axes. Neither inferred nor curated knowledge is author acceptance.
- **Review:** Keep each engineering PR at <=500 changed lines and <=12 files, as required by the existing Studio UX plan. Prefer local focused tests to paid GitHub Actions.
- **UI:** Overview remains graph-first; perspective prototypes can have different heroes. Keyboard navigation, visible focus, adequate contrast, and a readable narrow screen are required to recommend adoption.

## Review Focus

1. **Absent Progression Fantasy pack:** must display an inference/coverage gap, never fabricate a curated genre rule. Assert in Task 1 and inspect in Task 5.
2. **Legacy Epic Fantasy required trope:** must preserve the legacy label with provenance, not claim all epic fantasy requires prophecy/chosen one. Assert in Task 2 and inspect in Task 4.
3. **Same trope used differently by multiple genres:** must retain separate genre-relative relationships; must not flatten to one global classification. Absence from one pack must not automatically become a negative expectation. Assert in Task 2 and Task 5.
4. **No supported causal edge:** the mechanism view must leave the relationship unknown rather than drawing a convincing unsupported arrow. Assert in Task 6.
5. **Long label, mobile width, empty selection, stale/replaced node:** avoid permanent empty inspector, clipping or unrecoverable focus. Exercise in Tasks 3 and 7.

---

## File Map — Discovery Branch Only

- Create docs/prototypes/studio-explanations/README.md — run instructions, experimental scope, exact fixtures and truth boundaries.
- Create docs/prototypes/studio-explanations/fixtures/paladin.json — reconstructed screenshot-backed paladin example, explicitly illustrative where necessary.
- Create docs/prototypes/studio-explanations/fixtures/hybrid.json — long-form multi-genre fixture based on repository tests; mark extra material synthetic.
- Create docs/prototypes/studio-explanations/fixtures/genre-evidence.json — explicitly sourced legacy conventions/pack availability and missing coverage.
- Create docs/prototypes/studio-explanations/model.mjs — pure normalization and cross-genre projection, no DOM/network/state writes.
- Create docs/prototypes/studio-explanations/model.test.mjs — runtime tests of the pure projection using node:test (where Node is installed).
- Create docs/prototypes/studio-explanations/index.html — one comparable shell and Overview baseline.
- Create docs/prototypes/studio-explanations/app.mjs — route variant navigation/selection and preserve focus.
- Create docs/prototypes/studio-explanations/styles.css — shared responsive shell and semantic tokens.
- Create docs/prototypes/studio-explanations/views/anatomy.mjs — candidate A grammar view.
- Create docs/prototypes/studio-explanations/views/comparison.mjs — candidate B convention/story view.
- Create docs/prototypes/studio-explanations/views/mechanism.mjs — candidate C functional/causal view.
- Create tests/test_studio_explanatory_fixtures.py — fixture/provenance/authority invariants.
- Create tests/test_studio_explanatory_prototypes.py — static navigation/semantic/accessibility contracts.
- Create docs/reviews/2026-10-12-studio-explanatory-views-comparison.md — observed walkthrough results and selected recommendation (or abstention).

**No production files changed in this plan.** In particular do not alter src/auteur/beginner/browser/studio.js, studio.html, studio.css, src/auteur/genre_packs/, or the original Studio store/API. Group reviewable prototype pieces into small commits/PRs rather than submitting all proposed files as one PR.

## Shared Pilot Interface Contract

Every rendered item references a common noncanonical model (do not create one model per view):

- id: source-local stable key within the fixture, not a fabricated global trope identity.
- label, type: human-readable presentation labels.
- genre_links: zero or more entries with genre_id, relation, rule_strength if known, evidence_source, source_ref, and optional version/hash.
- story_treatment: proposed_adoption / proposed_adaptation / proposed_story_specific / proposed_subversion / unresolved; always noncanonical.
- derivation: premise_explicit / curated_match / model_inference / author_added.
- certainty: clear / likely / uncertain, independent of derivation.
- supported_links: actual fixture source-backed edges with target_id, verb, source_ref, support_status.
- authority_status: literal DERIVED / NOT CANON.
- freshness: current / stale / unavailable.
- coverage: pack_backed / legacy_contract / design_pack / inference_only / missing.

**Functions (exports from model.mjs):**
- normalizeEvidence(story, genreEvidence) -> explanationModel (pure, deterministic, rejects dangling source-backed link IDs).
- entriesForPerspective(model, perspective) -> array of source-scoped items; perspective = overview | anatomy | comparison | mechanism.
- connectionsForSelection(model, itemId) -> array of supported links only; absent connections return [] with an explanatory empty state.

The prototype reads its static JSON using fetch from the local HTTP server. Never derive an exact pack strength from an LLM guess; use null/unknown where there is no appropriate authored source.

### Task 1: Freeze Comparable Test Stories and Evidence

**Files:** Create the three fixtures and README.md; Test: tests/test_studio_explanatory_fixtures.py.

**Interfaces:** JSON with story_id, scenario, nodes, genres, genre_links, proposal_edges, phases, and source references. Later tasks consume these exact top-level keys.

- [ ] **Step 1 — Write failing tests** for two story IDs (paladin, hybrid), no duplicate node IDs, no accepted/canonical flag, no dangling proposal_edges, and no fake Progression/Heroic versioned pack.
- [ ] **Step 2 — Verify RED:** Run python -m pytest tests/test_studio_explanatory_fixtures.py -q; expect file-not-found/failing assertions.
- [ ] **Step 3 — Write minimal fixtures:** Reconstruct screenshot-backed names only as an illustrative case; use the test architecture candidate's mystery/horror phases for the second; source real legacy Epic Fantasy facts from src/auteur/genres/data/epic_fantasy.yaml and record unresolved classification for missing packs.
- [ ] **Step 4 — Verify GREEN:** Rerun the same pytest file; expect PASS. Review every classification for source attribution. README states what is synthetic.
- [ ] **Step 5 — Commit:** git add docs/prototypes/studio-explanations/fixtures docs/prototypes/studio-explanations/README.md tests/test_studio_explanatory_fixtures.py && git commit -m "test(studio): ground visual-explanation prototype fixtures".

**Acceptance:** Both fixtures are usable for all candidates without provider calls; unsupported claims and invented canonical events are absent.

### Task 2: Implement the Read-Only Semantic Bridge

**Files:** Create model.mjs and model.test.mjs; modify tests/test_studio_explanatory_fixtures.py.

**Interfaces:** Implement the three exported functions in Shared Pilot Interface Contract; no external packages, browser APIs, mutation, or server calls within the pure functions.

- [ ] **Step 1 — Add failing semantic tests:** In model.test.mjs use node:test and node:assert/strict to call normalizeEvidence with the two shared fixtures. Check two distinct genre_links for a shared trope; preserve legacy source label (required_tropes), never map it implicitly to a universal HARD_CONSTRAINT; missing packs keep null rule_strength. A missing convention is not an exclusion. Bad supported_links target IDs fail safely or become visibly unavailable, not invented links.
- [ ] **Step 2 — Verify RED:** Run node --test docs/prototypes/studio-explanations/model.test.mjs; expect module-not-found before implementation. Also run python -m pytest tests/test_studio_explanatory_fixtures.py -q. If Node is unavailable, record that projection runtime behavior remains unverified; do not present static grep checks as equivalent.
- [ ] **Step 3 — Implement the functions:** Build a single immutable projection consumed by A/B/C; preserve source_ref verbatim, distinguish intended causal language from established cause, and resolve cross-genre relationships only by actual fixture edges.
- [ ] **Step 4 — Verify GREEN:** Rerun focused pytest, node --test docs/prototypes/studio-explanations/model.test.mjs, and node --check on the module when Node is available; inspect output for independent genre/story/provenance axes.
- [ ] **Step 5 — Commit:** git add docs/prototypes/studio-explanations/model.mjs docs/prototypes/studio-explanations/model.test.mjs tests/test_studio_explanatory_fixtures.py && git commit -m "feat(studio): add noncanonical explanatory projection".

**Acceptance:** Same semantic output for every visualization, including accurate abstention when no curated genre knowledge exists.

### Task 3: Build a Neutral Comparison Shell and Graph Baseline

**Files:** Create index.html, app.mjs, styles.css; Test: tests/test_studio_explanatory_prototypes.py.

**Interfaces:** app.mjs calls entriesForPerspective; its screen switcher offers Overview, A, B, C and fixture choice. Selected item ID and return origin remain local display state.

- [ ] **Step 1 — Write failing shell tests:** One clearly identified main visualization per active perspective; no permanently reserved empty Story Details column; explicit fixture selector, "Return to Overview", status/provenance region and keyboard-focusable nav; all referenced IDs exist once.
- [ ] **Step 2 — Verify RED:** Run python -m pytest tests/test_studio_explanatory_prototypes.py -q.
- [ ] **Step 3 — Implement the shell:** Use graph-like Overview as the comparison baseline but avoid recreating production persistence or graph editing. All three views receive the same fixture and shared controls; inactive views do not occupy screen space.
- [ ] **Step 4 — Verify GREEN and preview:** Rerun pytest; start python -m http.server 8765 from repository root and open http://localhost:8765/docs/prototypes/studio-explanations/ . Confirm fixture switch preserves truth status while resetting invalid selection.
- [ ] **Step 5 — Commit:** git add docs/prototypes/studio-explanations/index.html docs/prototypes/studio-explanations/app.mjs docs/prototypes/studio-explanations/styles.css tests/test_studio_explanatory_prototypes.py && git commit -m "feat(studio): add comparable explanation prototype shell".

**Acceptance:** Overview is usable without opening a blank inspector; only one explanatory hero occupies the main area.

### Task 4: Candidate A — Genre Anatomy

**Files:** Create views/anatomy.mjs; modify styles.css and tests/test_studio_explanatory_prototypes.py.

**Interfaces:** export renderAnatomy(root, model, genreId, onSelect). Inputs are read-only; onSelect receives source-local item ID.

- [ ] **Step 1 — Write failing assertions:** Genre promise, typical engine loop, characteristic conflict, optional alternatives and payoffs appear as distinct labeled areas; every claimed "expected" relationship displays source and rule strength (or "hypothesis").
- [ ] **Step 2 — Verify RED:** Run focused prototype pytest; assert required headings/ARIA landmark missing initially.
- [ ] **Step 3 — Implement compact explanatory grammar:** Use directed segments and an optional renewable cycle, with no universal fixed-act timeline. For Epic Fantasy show "legacy contract" and its source; for Progression Fantasy expose a provisional interpretive loop with the missing-pack warning.
- [ ] **Step 4 — Verify GREEN + inspect:** Rerun pytest and open both fixtures in a browser. Check the promise-engine-payoff chain remains readable without a full dense graph.
- [ ] **Step 5 — Commit:** git add docs/prototypes/studio-explanations/views/anatomy.mjs docs/prototypes/studio-explanations/styles.css tests/test_studio_explanatory_prototypes.py && git commit -m "feat(studio): prototype genre anatomy explanations".

**Acceptance:** A reader can distinguish a characteristic tendency from a claim about this paladin story in one view.

### Task 5: Candidate B — Convention vs. Invention

**Files:** Create views/comparison.mjs; modify styles.css and tests/test_studio_explanatory_prototypes.py.

**Interfaces:** export renderComparison(root, model, itemId, onSelect).

- [ ] **Step 1 — Write failing tests:** Render two independent axes (genre relationship and story treatment); shared trope may have multiple genre rows; missing pack displays "Not classified by a versioned pack" rather than a false expectation; missing mention is distinct from an explicitly sourced exclusion; explicit subversion is distinct from unknown fit.
- [ ] **Step 2 — Verify RED:** Run focused prototype pytest; expect missing comparison regions.
- [ ] **Step 3 — Implement the visual contrast:** Left = attributed conventions / what the genre can supply; right = story-specific proposed treatment; bottom = the function of the resulting synthesis, when supported. Avoid an absolute "original vs derivative" creativity score.
- [ ] **Step 4 — Verify GREEN + inspect:** Rerun pytest. Inspect hybrid shared-trope and paladin generosity cases, testing disputed legacy required_tropes labeling.
- [ ] **Step 5 — Commit:** git add docs/prototypes/studio-explanations/views/comparison.mjs docs/prototypes/studio-explanations/styles.css tests/test_studio_explanatory_prototypes.py && git commit -m "feat(studio): prototype convention-versus-invention view".

**Acceptance:** Authors can see "typical", "modified", "explicitly excluded by documented evidence", and "not documented / unknown" without unsupported novelty or incompatibility claims.

### Task 6: Candidate C — Narrative Mechanism Map

**Files:** Create views/mechanism.mjs; modify styles.css and tests/test_studio_explanatory_prototypes.py.

**Interfaces:** export renderMechanism(root, model, itemId, onSelect); consume connectionsForSelection, never infer edges from prose similarity.

- [ ] **Step 1 — Write failing tests:** At most one focused chain/neighborhood in the hero; each visible arrow has an explicit verb, supporting source or visible "hypothesis" state; no arrow when source evidence is absent; accessible ordered text equivalent.
- [ ] **Step 2 — Verify RED:** Run focused prototype pytest.
- [ ] **Step 3 — Implement:** Use selected trope or engine → causal/structural function → intended reader effect when supported. Visually distinguish intended effect, tension, constraint and temporal transformation. Do not invent guaranteed emotions or scene-level plot events.
- [ ] **Step 4 — Verify GREEN + inspect:** Rerun pytest; inspect both fixtures and an intentionally disconnected source item. Test "Back" returns to source item, not a reset graph.
- [ ] **Step 5 — Commit:** git add docs/prototypes/studio-explanations/views/mechanism.mjs docs/prototypes/studio-explanations/styles.css tests/test_studio_explanatory_prototypes.py && git commit -m "feat(studio): prototype source-backed mechanism explanation".

**Acceptance:** The view explains why elements are related, rather than simply decorating a dependency graph.

### Task 7: Controlled Walkthrough and Visual Adversarial Review

**Files:** Create docs/reviews/2026-10-12-studio-explanatory-views-comparison.md; modify tests/test_studio_explanatory_prototypes.py only for observed deterministic regressions.

**Interfaces:** Report must contain an evidence row for each candidate, each fixture, each acceptance task, and each materially observed failure. It is not a new production data model.

- [ ] **Step 1 — Write the evaluation matrix:** Tasks are genre promise, convention/story difference, trope→structure→intended feeling trace, missing-pack honesty, and navigation back to original context. Include genre-switching overlap/long-text and stale-source probes.
- [ ] **Step 2 — Capture a consistent baseline:** Review owner screenshots and, if an isolated local runtime is available, current PR #392 without editing it. State clearly whether baseline was live or screenshot-only.
- [ ] **Step 3 — Exercise variants:** At desktop 1440x900, intermediate 900x700 and mobile 390x844, inspect reading order, clipping, one-handed navigation, focus visibility, contrast, empty inspector, and meaningful main-area use. Keyboard-only navigate every major interaction.
- [ ] **Step 4 — Record quantitative/qualitative evidence:** task completion, wrong inference, navigation detours, unnecessary reading, visible competing surfaces, time when measurable, and serious authority/provenance errors. Distinguish author observation from heuristic or simulated judgments.
- [ ] **Step 5 — Repair only deterministic regressions and commit evidence:** Rerun focused pytest/Node syntax checks. Commit the comparison and any targeted test repairs in a small reviewable change.

**Acceptance:** Comparison identifies which explanatory questions each candidate answers well and badly; does not equate source-test success with usability.

### Task 8: Choose or Abstain, Then Hand Off a Separate Integration Package

**Files:** Finalize docs/reviews/2026-10-12-studio-explanatory-views-comparison.md and link this plan; **do not edit production files**.

**Interfaces:** Record exactly one decision: SELECT_ANATOMY / SELECT_COMPARISON / SELECT_MECHANISM / BOUNDED_HYBRID / NO_CHANGE. Link the specific evaluated prototype commit and failures/advantages.

- [ ] **Step 1 — Apply hard rejection criteria:** Reject any candidate inventing pack-backed expectations, implying author acceptance, deleting Overview access, obscuring intended-vs-proven effects, or losing meaningful focus.
- [ ] **Step 2 — Compare surviving candidates:** Prefer the option that answers the five user tasks with least interpretive clutter. A bounded hybrid is allowed only when specific complementary views justify its complexity.
- [ ] **Step 3 — Record the selected composition:** Which visual hero belongs to Genres, Tropes and Structure; how Overview and Timeline remain accessible; where context/provenance details live; how empty/missing-pack cases behave.
- [ ] **Step 4 — Define the next *separate* implementation responsibility:** Integrate chosen UI with source-backed read-only projection from the then-current Studio head, including existing state restoration and responsive/browser tests. Only commission a versioned Progression/Heroic Fantasy pack pilot if lack of curated data actually blocked a task.
- [ ] **Step 5 — Commit and stop at decision boundary:** Publish evidence and a proposed follow-up integration plan; leave the current prototype-only work out of main until authorized integration. Do not represent a selected design as shipped software.

**Acceptance:** An engineer can reproduce the comparison, understand the winner's semantics and identify the exact next implementation boundary.

## Evaluation Decision Rubric (Non-Scalar)

| Question | Favorable signal | Reject/repair signal |
| --- | --- | --- |
| Story-first meaning | Distinctive paladin mechanism is prominent | Generic textbook conventions eclipse this story |
| Explanatory clarity | Author can trace conventional role, story treatment and intended effect | Same graph merely dimmed; long lists duplicate nodes |
| Honest genre knowledge | Explicit legacy/pack/inference labels and coverage gaps | Invented Progression or Heroic Pack support |
| Cognitive economy | One hero, details on demand, returnable context | Permanent empty inspector, repeated bars, long scroll |
| Creative autonomy | Variations and subversions remain legitimate | "Required" becomes universal or analysis implies acceptance |
| Robustness | Readable without color, keyboard and mobile, stale fallback | Lost navigation state, clipped content, unsupported edges |

## PR and Verification Strategy

1. **Prototype data + semantic model** (Tasks 1–2): data validity and epistemic rules before visuals.
2. **Shell + A** (Tasks 3–4): one usable prototype baseline and first visual grammar.
3. **B + C** (Tasks 5–6): divergent alternatives on identical source material.
4. **Comparison + decision** (Tasks 7–8): recorded evidence and next-project warrant; no implementation claims.

Each PR must meet the repository change caps independently and be reviewed for source correctness; if a grouped PR would exceed its budget, split along independently testable responsibilities. Use local commands:

- python -m pytest tests/test_studio_explanatory_fixtures.py tests/test_studio_explanatory_prototypes.py -q
- node --test docs/prototypes/studio-explanations/model.test.mjs and node --check docs/prototypes/studio-explanations/model.mjs (if Node is present; otherwise the runtime verification gap remains explicit)
- python -m http.server 8765 (from repository root for a real-browser review)

**No full suite, provider invocation, expensive CI or production merge is warranted solely to compare these views.** The eventual integration package has a different validation boundary: focused Studio tests, served-HTTP browser walkthrough, responsive and keyboard review, zero data mutation from browsing, then exact-head integration reconciliation.

## Self-Review Checklist

- [ ] Both genre-relation and story-treatment axes represented without conflation.
- [ ] A/B/C visualize different explanations, not three skins over the same graph.
- [ ] All views share one fixture set, adapter, provenance and authority state.
- [ ] Paladin sample clearly distinguishes observed labels from invented demonstration links.
- [ ] Hybrid and absent-pack/disputed-rule scenarios are first-class.
- [ ] Every Review Focus risk has an owning task/test.
- [ ] No prematurely invented versioned Genre Packs, globally canonical trope IDs, or additional accepted story owner.
- [ ] Prototype success is not called a real-user usability proof or released Studio.
- [ ] The next implementation project has a clear stop/go boundary with a comparison report.
