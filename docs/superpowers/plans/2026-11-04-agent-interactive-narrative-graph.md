# Agent-Interactive Narrative Graph Prototype and Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for **inline/native** execution (the author previously selected no subagents); superpowers:subagent-driven-development is an available alternative only if the author later changes that preference. Execute task-by-task using checkbox (- [ ]) tracking. This plan intentionally produces an **isolated comparative prototype and evaluation**, not a production Studio feature.

**Goal:** Discover whether source-honest, component-aware graph interactions improve an author's ability to inspect Narrative Architecture, express creative intent, and hand a bounded revision question to a coding agent, without manually maintaining a graph or changing story authority.

**Architecture:** Use existing ArchitectureCandidate v2 and the actual PR #510 qualification candidate as immutable input to a pure ES-module semantic projection and intent-draft builder. Expose two distinct prototype interaction variants (B1 question-first inspection and B2 component-aware workbench) with no server or provider calls. Compare both against the current **served** Studio, including its readable overview and graph, before selecting any production integration.

**Tech Stack:** Existing vanilla JavaScript (ES modules), Node.js built-in node:test, CSS/HTML, Python >=3.11 pytest and the repository's established browser-test harness if available. Use no new dependencies, schema version or backend.

**Spec:** [Agent-Interactive Narrative Graph — Exploration Design](../specs/2026-11-04-agent-interactive-narrative-graph-design.md). Read the existing [agent-first design](../specs/2026-11-03-agent-first-ontology-grounded-narrative-architecture-design.md), [MISSION](../../../MISSION.md) and [semantic architecture](../../narrative-architecture.md).

**Status:** **PLAN ONLY / PROTOTYPE-FIRST / EVIDENCE-GATED.** User agrees with the exploration recommendation, not automatic production implementation or release. No task here may mutate production code, add canonical state or claim author validation from automated tests.

## Global Constraints

- Work in a real local Auteur checkout, on an isolated branch/worktree. Preserve unrelated work and valuable author project data.
- No auto-accept, no cloud/multi-author service, no new model provider, no new story/ontology owner, no silent CanvasStore writes, no new canonical schema.
- Active coding agent remains the primary architecture generator; graph actions **prepare author-intent drafts** but do not execute generation in this prototype.
- Keep actual candidate request SHA plus element kinds/IDs; invalid or superseded IDs stay unavailable, never rebound by title.
- Treat candidate nodes, relations, genre contracts, emotional targets and phases as **working proposals**, even if they include source-referenced definitions. A field value is not proof of accepted story authority.
- Never create an edge from proximity, same-name trope text, inferential plausibility, or button placement. Absent relation = **not recorded**, not “impossible”.
- Visual fold/group/selection are reversible presentation operations. A connect-to-ask gesture creates **only an editable question draft**, not a relationship in CanvasStore or the accepted story.
- Mirror all essential graph semantics in keyboard-accessible linear elements; use text labels, not only colors/lines. Respect narrow screens and reduced motion.
- Treat real browser operation, automated DOM tests, author comprehension and actual coding-agent execution as distinct evidence classes. A fixture demo is not an implemented production workflow.
- If a current feature already satisfies a proposed subtask, document **NO CHANGE REQUIRED** instead of cloning it.

## Review Focus — high-risk cases and owning tests

1. **Missing link:** Two selected entities with no recorded connection display “No recorded relation” and can form an ask_relation draft without creating a fabricated edge (Tasks 1–2).
2. **Candidate/source change:** Replacing the request SHA invalidates the old selection/draft instead of silently rebinding the same node title (Tasks 1–3).
3. **Scope and identity:** An emotion target ID, genre contract keyed by genre_node_id and a link ID cannot masquerade as generic node IDs (Task 1).
4. **Authority and wording:** Inference and a genre-proposed emotional target are not described as accepted story facts or proven reader effects (Tasks 2–5).
5. **Accessibility/density:** A keyboard-only or 390px-wide author can inspect and return without graph-geometry dependence; a dense fixture does not hide critical unknown/stale notices (Tasks 3–5).

---

## 0. File responsibilities and dependency order

### Existing owners: inspect, never replace during this plan

| File | How the prototype reuses it |
| --- | --- |
| src/auteur/beginner/studio_architecture.py | ArchitectureCandidate v2 fields and source-honest host request; **read-only for prototype** |
| src/auteur/beginner/browser/studio.js | Current graph, selection, directed edges, status and requestArchitecture; production baseline only |
| src/auteur/beginner/browser/studio_architecture_reader.js | Current readable candidate; baseline for comprehension comparisons |
| src/auteur/beginner/browser/studio_unfolding.js | Existing proposal-edge projection; compare, do not duplicate adoption semantics |
| src/auteur/beginner/browser/studio_explanation_views.js | Existing semantic explanations; compare navigation and evidence grammar |
| docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json | Recorded source fixture; no copy of synthetic altered narrative |
| docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-request.json | Exact source request SHA, status and context fixture |
| docs/qualification-evidence/agent-first-ontology-20261103/sparse-vision-candidate.json | Sparse/unknown coverage fixture |

### Prototype-only files (new; one responsibility each)

| File | Single responsibility |
| --- | --- |
| docs/prototypes/agent-interactive-graph/README.md | Run instructions, authority/evidence boundaries, real baseline path |
| docs/prototypes/agent-interactive-graph/index.html | Compare B1/B2, show current fixture/source and editable intention UI |
| docs/prototypes/agent-interactive-graph/styles.css | Lightweight responsive graph/linear semantic presentation |
| docs/prototypes/agent-interactive-graph/model.mjs | Pure source-bound anchor, component, relationship and intent-draft functions |
| docs/prototypes/agent-interactive-graph/model.test.mjs | Exact identity, uncertainty, draft and stale-state tests |
| docs/prototypes/agent-interactive-graph/app.mjs | DOM controller for B1/B2 and keyboard controls; no network beyond fixture loading |
| docs/prototypes/agent-interactive-graph/view.test.mjs | DOM semantics, event behavior, variant distinctions |
| docs/prototypes/agent-interactive-graph/fixtures/dense-synthetic.json | High-density **labeled synthetic** v2 candidate, not fictitious source evidence |
| tests/test_agent_interactive_graph_browser.py | Existing browser harness variant/task assertions; mark untested when runtime unavailable |
| docs/research/2026-11-04-agent-interactive-graph-prototype-assessment.md | Baseline/variant evidence, tradeoffs and go/no-go recommendation |

No new production JS, HTTP handlers, persistence files, ontology fields, accepted story assets or provider code may be added by this plan.

**Execution:** Task 0 baseline -> Task 1 pure semantic projection -> Task 2 pure intent grammar -> Task 3 B1 -> Task 4 B2 -> Task 5 comparative browser evaluation -> Task 6 synthesis/decision. Stop at legitimate environment boundary with the exact next command; do not invent observed success.

## Task 0 — Baseline and reproducible fixture admission

**Files:**
- Create: docs/prototypes/agent-interactive-graph/README.md
- Create: docs/research/2026-11-04-agent-interactive-graph-prototype-assessment.md (initial evidence ledger)
- Read: MISSION.md; STATUS.md; existing graph/reader/unfolding files and agent-first qualification evidence.

**Interfaces:**
- Consumes recorded candidate and request JSON; produces a fixture manifest with request SHA, candidate schema_version, observed IDs, synthetic-vs-recorded labels, and baseline capabilities.

- [ ] **Step 1: Verify a runnable checkout and baseline.** Run:
  ~~~bash
  git rev-parse --show-toplevel
  git status --short
  node --test tests/test_studio_architecture_reader.mjs tests/test_studio_unfolding_controller.mjs
  python -m pytest tests/test_beginner_studio_architecture_browser.py -q
  ~~~
  Record commit SHA and actual exit codes; do not misrepresent known unrelated failures.
- [ ] **Step 2: Inspect source identities.** Load recorded rich-vision-request.json and candidate.json, assert schema_version=2 and request_sha256 matches 64 lowercase hex characters. Identify actual Memory Economy, Wonder, mystery, one existing directed link, and a valid missing-link pair **from the fixture**. If a particular identifier is absent, choose an actual present ID and document it.
- [ ] **Step 3: Write README and initial ledger.** Document baseline, accepted-vs-working distinction, example author tasks, fixture locations, and exact serve URL:
  ~~~bash
  python -m http.server 8765
  ~~~
  Navigate to /docs/prototypes/agent-interactive-graph/ when the prototype exists.
- [ ] **Step 4: Commit documentation-only baseline** after checking every source claim against current files; no product file touched.

**Review gate:** The baseline is the actual current Studio, not the 2026-10-11 screenshots or a deliberately inferior mock. A reported HTTP/browser run must have an actual browser transcript.

## Task 1 — Source-bound semantic graph projection

**Files:**
- Create: docs/prototypes/agent-interactive-graph/model.mjs
- Create: docs/prototypes/agent-interactive-graph/model.test.mjs

**Interfaces:**
- Export resolveAnchor(candidate, requestSha, anchor) -> null | {kind,id,sourceRef,title,meaning,authority,components,relationships}.
- Export recordedRelations(candidate, anchors) -> Array<{kind,id,sourceRef,from,to,label,detail,authority}>. With one node anchor, return its **direct recorded** incident links/explicit contract references; with two node anchors, return only recorded relations **between those anchors** (no inferred or transitive edges). A selected relationship anchor returns that exact relationship.
- Anchors have the exact shape {kind, id}, with kind in node | link | genre_interaction | emotion_target | genre_contract | phase. The genre contract id is the actual genre_node_id.
- sourceRef is an **actual array location** in the immutable captured candidate, e.g. nodes/3, links/7, genre_contracts/1, located by the stable record ID/key and bound to the exact candidate request SHA. Carry the stable ID separately. Do not invent paths such as nodes/<id> that the candidate JSON cannot resolve; sourceRef is **not** a new canonical URI.

- [ ] **Step 1: Write failing pure tests.** Implement test names:
  ~~~javascript
  test('node and link anchors remain distinct and source-bound', () => {
    const engine = resolveAnchor(candidate, sha, {kind:'node', id: engineId});
    const link = resolveAnchor(candidate, sha, {kind:'link', id: linkId});
    assert.equal(engine.sourceRef, 'nodes/' + candidate.nodes.findIndex(n => n.id === engineId));
    assert.equal(link.sourceRef, 'links/' + candidate.links.findIndex(l => l.id === linkId));
    assert.equal(engine.authority, 'working_proposal');
  });

  test('missing relation stays unknown without inferred edges', () => {
    assert.deepEqual(recordedRelations(candidate, [unlinkedA, unlinkedB]), []);
  });
  ~~~
  Also test real genre_contracts/genre_interactions/phase/emotion ID lookup, missing/stale IDs, duplicates, reversed edge direction, identical-looking titles with distinct IDs, and that same-name trope_functions are not unified.
- [ ] **Step 2: Run to observe RED.**
  ~~~bash
  node --test docs/prototypes/agent-interactive-graph/model.test.mjs
  ~~~
  Expected initially: missing export/functions or targeted assertions fail.
- [ ] **Step 3: Implement pure deterministic selectors.** Map only existing candidate fields; expose provenance/status and sourceRef; use actual references, not label matching; carry explicit unknown for unsupported relationship claims. No writable state, client persistence, provider or graph schema.
- [ ] **Step 4: Run GREEN and regressions.** Run the model test plus tests/test_studio_architecture_reader.mjs; expected all added tests pass and existing baseline status stays as recorded.
- [ ] **Step 5: Commit** the pure model and tests.

**Review gate:** A selected relationship is a first-class **inspectable interaction target**, not a newly accepted domain relationship.

## Task 2 — Pure graph-to-agent intent-draft grammar

**Files:**
- Modify: docs/prototypes/agent-interactive-graph/model.mjs
- Modify: docs/prototypes/agent-interactive-graph/model.test.mjs

**Interfaces:**
- Export buildIntentDraft({candidate,requestSha,currentRequestSha,anchors,operation,authorText}) -> {kind,authority,status,request_sha256,operation,anchors,recorded_support,draft_instruction,warnings}.
- operation in ask_relation | trace | challenge | compare | revise.
- kind='studio_graph_intent_draft_v1'; authority='noncanonical_intent_draft'; status='prepared_not_executed'. Anchor count 1–3; ask_relation requires 2 distinct anchors; authorText length 0–4000, but revise requires nonempty explicit user intent. A stale SHA or unknown anchor must throw a specific, human-readable error rather than return a valid-looking draft.

- [ ] **Step 1: Write failing tests.** Verify source SHA and real IDs are present; ask_relation on unlinked engine/wonder emits "No recorded relation" and never adds an edge; challenge records actual source link; revise preserves the exact authorText; duplicate anchors, missing anchors, stale SHA and >4000 characters reject. Include the strongest user example: "Make wonder dominate fear while preserving mystery and the memory cost".
- [ ] **Step 2: Run RED** using node --test docs/prototypes/agent-interactive-graph/model.test.mjs; expected targeted errors until buildIntentDraft is implemented.
- [ ] **Step 3: Implement a concise, deterministic draft.** Include recorded source refs and bounded excerpts, not hidden manuscript/author facts. Never call a model or serialize accepted-story changes. Draft text must explicitly say "proposal to investigate/revise" rather than assert the requested outcome occurred.
- [ ] **Step 4: Run GREEN**, then review an actual draft side-by-side with the recorded rich-vision request. Verify source paths against the existing candidate and no false "accepted" or "agent executed" status.
- [ ] **Step 5: Commit** intent builder/tests.

**Review gate:** The prototype creates a *request draft*, not HostAgentRequest or an actual model invocation.

## Task 3 — B1: Question-First Semantic Inspector

**Files:**
- Create: docs/prototypes/agent-interactive-graph/index.html
- Create: docs/prototypes/agent-interactive-graph/app.mjs
- Create: docs/prototypes/agent-interactive-graph/styles.css
- Create: docs/prototypes/agent-interactive-graph/view.test.mjs

**Interfaces:**
- Export mountGraphExperiment(root, {candidate, requestSha, variant}) -> {destroy}; variant must be 'B1' or 'B2'. Initial task supports B1; B2 implemented Task 4.
- B1 supports selecting one node/link or two entities, inspecting real components/relationships, choosing ask_relation/trace/challenge/revise, editing an intention, and copying a draft. It displays the source authority and status above the action.

- [ ] **Step 1: Write failing DOM tests.** A keyboard user can select Memory Economy, navigate to an actual recorded relation, inspect its source and return; two selected anchors enable Connect-to-Ask and yield prepared_not_executed; missing-link query says "No recorded relation"; no DOM action calls fetch or writes localStorage; all candidate prose uses textContent, never untrusted innerHTML.
- [ ] **Step 2: Run RED** with node --test docs/prototypes/agent-interactive-graph/view.test.mjs.
- [ ] **Step 3: Build B1 UI.** Use real buttons/labels, accessible relationship list and local selection trail. A small static diagram may aid orientation but cannot be the only interaction mechanism. Mount only when source candidate and SHA are valid. Keep empty/unknown conditions visible; do not create a complex new graph renderer.
- [ ] **Step 4: Run GREEN** for model and view tests, then serve index.html with python -m http.server 8765 and verify B1 can be read without any agent running. If served-browser access is unavailable, record that ceiling explicitly.
- [ ] **Step 5: Commit** B1 files/tests.

**Review gate:** A question is visibly a question. Ordinary inspect/focus actions do not prepare a revision or modify a source.

## Task 4 — B2: Component-Aware Intent Workbench

**Files:**
- Modify: docs/prototypes/agent-interactive-graph/app.mjs
- Modify: docs/prototypes/agent-interactive-graph/index.html
- Modify: docs/prototypes/agent-interactive-graph/styles.css
- Modify: docs/prototypes/agent-interactive-graph/view.test.mjs
- Create: docs/prototypes/agent-interactive-graph/fixtures/dense-synthetic.json

**Interfaces:** Same mountGraphExperiment(..., variant='B2') interface. B2 reuses resolveAnchor, recordedRelations and buildIntentDraft; shows the selected entity's meaningful field-level components, one-hop recorded pathways, 1–3 selected anchors, context-sensitive actions, and a bounded draft for the active agent. Do not create a generic entity-component registry or new schema.

- [ ] **Step 1: Write failing B2 tests.** On the real Memory Economy fixture, inspect an engine's recorded links, an emotion target and relevant phase/genre contract; selecting multiple anchors produces a readable source-bound draft. A dense synthetic fixture shows bounded focus rather than 80 simultaneous cards; missing links still show unknown. Switching B1/B2 preserves the same fixture and actual source IDs.
- [ ] **Step 2: Run RED** with node --test docs/prototypes/agent-interactive-graph/view.test.mjs.
- [ ] **Step 3: Implement B2 by reusing the same pure model.** Render only present components, visually distinguish recorded link vs proposed interpretation, show exact anchor names and source refs, and allow returning to prior focus. The variant may be more information-dense than B1, but must not expose hidden facts.
- [ ] **Step 4: Run GREEN** plus node --test docs/prototypes/agent-interactive-graph/*.test.mjs. Inspect at 390px width and keyboard-only in a real browser if available. Do not claim a screen-reader audit from DOM tests.
- [ ] **Step 5: Commit** B2 and synthetic fixture with explicit synthetic origin.

**Review gate:** B2 must give the author a materially different *decision-making experience*, not just expose more JSON.

## Task 5 — Fair baseline, browser and usability comparison

**Files:**
- Create: tests/test_agent_interactive_graph_browser.py
- Modify: docs/research/2026-11-04-agent-interactive-graph-prototype-assessment.md
- Modify: docs/prototypes/agent-interactive-graph/README.md

**Interfaces:** Consumes actual served Studio as baseline (readable reader, graph, existing revise/status) and B1/B2 using the same recorded fixture. Produces an evidence matrix for the seven author tasks in the spec.

- [ ] **Step 1: Add browser tests using existing repository harness patterns.** Test actual DOM source status and prepared-not-executed badge, missing relation, selection/re-entry, stale source SHA, no persistent mutations, keyboard-only route and 390px responsive layout. A skipped test must report which browser dependency is absent.
- [ ] **Step 2: Run browser tests** with python -m pytest tests/test_agent_interactive_graph_browser.py -q. Expected: passing only if the relevant browser actually executed; never describe a mocked DOM as served-browser evidence.
- [ ] **Step 3: Conduct the same author tasks on current Studio, B1 and B2.** Use the recorded Memory Economy fixture and one sparse variant; include a dense synthetic stress scenario. Count explicit actions/detours and mark source or authority misunderstandings. Do not claim current Studio lacks a capability already present in Focused Unfolding or semantic facets.
- [ ] **Step 4: Perform two additional checks.** (a) Keyboard-only semantic equivalence and mobile width, (b) a review of exact text sent in a draft against source SHA/IDs and accepted-vs-provisional language. Human participant data, if unavailable, is "not obtained", not simulated human evaluation.
- [ ] **Step 5: Commit** the test and evidence matrix with exact environment, commands, results and blockers.

**Review gate:** Automated success is not evidence of improved author comprehension or literary quality. The matrix can legitimately conclude neither variant is better.

## Task 6 — Convergent selection and next authoritative boundary

**Files:**
- Modify: docs/research/2026-11-04-agent-interactive-graph-prototype-assessment.md
- Modify: docs/prototypes/agent-interactive-graph/README.md only for final scope/limitations

**Interfaces:** Produces one of: B1, B2, a bounded B1+B2 composition, NO PRODUCTION CHANGE or INSUFFICIENT EVIDENCE. It also states source/authority risks, absent qualification, and any narrowed future integration question.

- [ ] **Step 1: Compare against acceptance criteria in the spec.** A winner must have zero observed critical source/authority errors and at least one meaningful, evidenced advantage over current Studio on an author task, not just an aesthetic preference.
- [ ] **Step 2: Write an adversarial rejection case.** Try to make the new UI misrepresent accepted constraints, infer an absent cause, bind a stale anchor by matching title, or imply the host agent ran. Record exact outcome; fix a bug inside the prototype if discovered.
- [ ] **Step 3: Perform inline self-review and rerun changed test gates.** Run node --test docs/prototypes/agent-interactive-graph/*.test.mjs and python -m pytest tests/test_agent_interactive_graph_browser.py -q plus pertinent existing baseline tests; record actual results.
- [ ] **Step 4: Record the decision and evidence ceiling.** If a winner is credible, specify a *separate* production-design question: minimum Studio UI integration, server-validated anchor source/IDs at prepare time, compatibility with prepare_architecture and existing review status, and mitigation of existing misleading "preserved constraints" copy. No product integration is authorized within this plan.
- [ ] **Step 5: Commit documentation/evidence and open a focused PR** with precise changed paths. Review/merge the isolated prototype only through the repository's normal documentation/prototype policies. Do not merge it as a production feature or claim independent author testing.

**Review gate:** An insufficient result is a successful inquiry. Stop before production scope unless a future spec is explicitly approved.

## 7. Coverage audit and implementation handoff

| Spec obligation | Task(s) | Evidence |
| --- | --- | --- |
| Compare genuinely different approaches | 0, 3, 4, 5, 6 | Baseline + B1 + B2 matrix |
| Source-bound entities and component fields | 1, 4 | ID/provenance tests |
| First-class relationship inspection | 1, 3 | Directed-link inspection |
| Meaningful graph gestures without acceptance | 2, 3, 4 | ask_relation no-write tests |
| Bounded holistic agent-instruction draft | 2, 4 | source SHA/anchors + status tests |
| Missing/stale/ambiguous evidence | 1, 2, 3, 5 | negative/obsolete-ID cases |
| Accessibility and narrow-width usability | 3, 4, 5 | keyboard and real-browser evidence |
| Real evaluation rather than cosmetic selection | 5, 6 | observations + go/no-go |
| No production schema, provider or authority changes | Global constraints + 0–6 | diff audit |

**Dependencies and statuses:** The GitHub API can hold documentation but is not proof of a runnable local prototype; use an actual local checkout for Tasks 0–6. The executor may choose a smaller module arrangement if it preserves named interfaces, focused tests and the isolated-prototype boundary. A future integration phase needs its **own approved spec and plan**, not the uncontrolled expansion of this PR.

**Recommendation:** Execute **inline/native without subagents**, matching the author's most recent execution-method preference, and use narrow commits. Tasks 3 and 4 share the model but remain separable experiments; do not merge them prematurely.

### Three governing aphorisms

1. It is **not** a graph that authors must manually maintain; it is **actually** a semantic interface for directing agent reasoning.
2. It is **not** a source of story canon and is **not** a substitute for the active agent; it is **actually** an evidence-grounded creative interaction layer.
3. A useful graph gesture is **actually** a clearer, reviewable statement of author intent.
