# Auteur Studio Creative Collaboration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let an author move from free-form Story Vision to an understandable, source-honest, revisable graph of creative possibilities while concealing unnecessary agent machinery and preserving explicit author authority.

**Architecture:** Reuse noncanonical CanvasStore, `studio_architecture` typed candidate + request SHA, scoped `studio_mentor` directions, existing graph and dedicated explanatory views. Improve the presentation and manual handoff first; attach execution only through a real trusted host callback, never through arbitrary browser-side commands. Accepted narrative owners remain untouched.

**Tech Stack:** Python 3.11+, Pydantic, existing local `BeginnerWorkspaceServer`, plain HTML/CSS/JavaScript, Node built-in test runner, pytest, Playwright Chromium Stage B. No new web framework, graph engine, cloud service, provider configuration, or paid CI requirement.

**Spec:** `docs/superpowers/specs/2026-10-15-studio-creative-collaboration.md`.

## Global Constraints

- Start from the current actual `main`; at planning time `bb9c102d6cc4e9473ca7cffc5253ed72361ef37a`, with #439 merged. Resolve current heads before work; do not modify or rely on the dirty user's primary worktree.
- Respect `MISSION.md`, `FACTORY_RULES.md`, `AGENTS.md` and owner-selected `docs/design/2026-10-09-living-story-studio.md`: no auto-accept, local-first, vendor-neutral host generation, graph-first experience, explicit working/canon split.
- Preserve current candidate v1/v2 readability, CanvasStore revision/conflict guarantees, `HostAgentRequest`/`HostAgentResponse` SHA and validation semantics. Existing Story Realization and Book workflows stay in their own subsystems.
- Retain host-agent/manual fallback and status truth. Never claim a callable host without actual capability; never call a provider on passive render, silently change provider, or run author-controlled shell commands.
- Reuse `MentorAdvice`/`MentorDirection` for meaningful alternatives; no new global chat system or arbitrary preference learner.
- Preserve known knowledge limits: Progression/Heroic Fantasy do not have verified versioned Genre Packs in the previously reviewed source. Missing evidence is unknown, not an implied prohibition or originality claim.
- Keep PRs reviewably narrow (current factory cap: 500 lines / 12 files when it applies). Local test evidence is acceptable only at its actual claim scope; protected merge/release is separate.

## Review Focus — Five High-Risk Cases

1. **Invented paladin flaw:** an agent's solitary-protector lesson must display as hypothesis, never as quoted/approved author intent. Pin in Tasks 1–2.
2. **No connected host:** clicking the primary control must lead to a truthful actionable fallback, not an endless "generating" state. Pin in Task 3.
3. **Late/stale or cross-canvas response:** cannot overwrite a current candidate, accepted story, or another canvas. Pin in Tasks 3–4.
4. **No verified genre evidence:** a conventionality/subversion display must abstain from unsupported labels. Pin in Task 5.
5. **Focus, mobile, and accessibility:** changing views or opening an alternative must preserve unsaved work, a navigable graph, readable focus, and keyboard/back access. Pin in Tasks 2, 5–6.

## Baseline and File Map

Existing owners to **reuse**, not replace:
- `src/auteur/beginner/studio_architecture.py`: `prepare_architecture`, `complete_architecture`, `project_architecture`, `apply_architecture_review`, `ArchitectureCandidate`.
- `src/auteur/beginner/studio_mentor.py`: existing `MentorAdvice`, `MentorDirection`, source refs and deliberate working adoption.
- `src/auteur/beginner/studio_store.py`: author-owned working items and revisioned persistence.
- `src/auteur/beginner/browser/studio.js`, `studio.html`, `studio.css`: primary graph and Story Vision.
- `src/auteur/beginner/browser/studio_mentor_context.js`, `studio_mentor_dialogue_controller.js`: contextual exploration and review.
- `src/auteur/beginner/browser/studio_explanations.js`, `studio_explanation_views.js`: existing genre, trope and structure explanatory heroes.
- `src/auteur/beginner/server.py`: local HTTP routing and injectable runtime dependencies.
- `scripts/studio_stage_b_check.py`: actual served Browser safety regression.

New code should have only two small presentation controllers and, **conditionally**, one trusted execution-boundary module:
- `src/auteur/beginner/browser/studio_author_intent.js`: pure projection of author text versus agent proposal, with no semantic guessing.
- `src/auteur/beginner/browser/studio_agent_handoff.js`: request/capability UI state and bounded status checking.
- `src/auteur/beginner/studio_host_dispatch.py` **only if a usable callable host adapter is available**: typed opt-in execution port; not a daemon or provider integration by itself.

### Task 1: Source-honest author-intent and proposal view

**Files:** Create `src/auteur/beginner/browser/studio_author_intent.js`, `tests/test_studio_author_intent.mjs`; modify `studio.js`, `studio.html`, `studio.css` narrowly.

**Interfaces:** `AuteurStudioAuthorIntent.project(items, architectureProjection)` returns `{authorVision, proposal, sourceStatus}`; `authorVision` comes solely from `canvas/items/story-vision`, and `proposal` is labeled `agent_proposal` with `candidate_request_sha256` when available. No source classification by fuzzy text matching.

- [ ] **RED:** Add `node:test` fixtures for an exact paladin Story Vision, a candidate positing a solitary-protector flaw, an empty vision, and a stale proposal. Assert that no proposed flaw is included in `authorVision` and stale material never appears as current evidence. Run `node --test tests/test_studio_author_intent.mjs`; expect missing function or failed assertions.
- [ ] **BUILD:** Implement the pure projection and wire one compact "Your story vision" display beside "Auteur's proposed interpretation" in the current Studio context. Do not turn an agent's self-declared `author_declared` field into verified author input. Keep source/version details accessible on explicit inspection.
- [ ] **GREEN:** Rerun the same Node test and `node --check` on changed scripts. Assert that opening/closing the compact vision preserves CanvasStore content and graphical focus.
- [ ] **REVIEW/COMMIT:** Verify no Story Identity, Structure or accepted prose is mutated. Commit only the focused source and tests.

**Acceptance:** An author can point to what they typed versus what AI suggested without opening JSON.

### Task 2: Compare creative alternatives using existing mentorship

**Files:** Modify `studio_mentor_dialogue_controller.js`, `studio_mentor_context.js` (only if source context is missing), `studio.js` and `studio.html` as needed; test `tests/test_studio_mentor_dialogue.mjs`, `tests/test_studio_mentorship.mjs`, and `tests/test_studio_mentor_agent.py`.

**Interfaces:** Use existing `MentorAdvice.directions[]` fields `mechanism`, `consequence`, `tradeoff`, `distinguishing_factor`, `divergence_axis`, `source_status`, `source_refs`; existing preview/Keep/Discard CanvasStore pathway remains the only write.

- [ ] **RED:** Add a paladin example with distinct trajectories: generous growth without an obligatory starting flaw, and stewardship dilemmas as an optional tension. Assert that each card shows differences/tradeoffs and provenance, and that absence of actual alternatives is a truthful empty result. Run `node --test tests/test_studio_mentor_dialogue.mjs tests/test_studio_mentorship.mjs` and focused mentor pytest; expect the new presentation assertions to fail.
- [ ] **BUILD:** Add a clearly named "Explore other interpretations" action for the selected concept, using existing mentor prepare/response. Show a compact comparison rather than automatically replacing the architecture; never force exactly three directions or silently claim a chosen central dramatic question.
- [ ] **GREEN:** Test source/selected-focus SHA, explicit Keep as working, edited-preview protection, rejected stale replies, preserved alternative choices when navigating away and back. Verify no acceptance or new story authority.
- [ ] **REVIEW/COMMIT:** Keep mentor actions optional and context-local; commit a self-contained alternatives UX slice.

**Acceptance:** A paladin author can reject the imposed hero flaw and deliberately preserve a different working trajectory.

### Task 3: Make the manual agent handoff truthful, short and recoverable

**Files:** Create `src/auteur/beginner/browser/studio_agent_handoff.js`, `tests/test_studio_agent_handoff.mjs`; modify `studio.js`, `studio.html`, `studio.css`, and narrowly `server.py` for a capability read if needed.

**Interfaces:** GET `/api/beginner/studio/host-capabilities` returns `{"studio_architecture":{"attached":false}}` by default (Task 4 may truthfully set it to true). `AuteurStudioAgentHandoff.present(architectureProjection, hostCapability)` returns presentation-only `{mode, primaryAction, message}`. Modes are `not_started`, `manual_required`, `awaiting_response`, `review_ready`, `ready`, `stale`, `error`. These are UI labels derived from existing backend statuses, **not another persisted lifecycle**.

- [ ] **RED:** Write cases for no connected host, waiting with no result, a saved previous candidate, stale revision, malformed response and a user returning after reload. Run the focused Node test; expect RED.
- [ ] **BUILD:** Keep a single prominent author-facing action and actionable plain-language status. Put raw packet/completion JSON in a collapsed "Advanced: agent handoff" section. Offer one-click copy of the actual pending request (or clearly selectable text/CLI instructions if Clipboard API is unavailable). Bounded polling checks the existing GET projection; stop on completion, hidden page, navigation, or exhaustion.
- [ ] **GREEN:** Simulate late responses and switching canvases while waiting; assert previous proposals stay visible, missing capability never says "AI is generating", and manual JSON response still validates via the existing POST route.
- [ ] **REVIEW/COMMIT:** No executor, model call, or new backend status storage is introduced in this slice.

**Acceptance:** An unconnected Browser is still honest and usable. A technical author can complete the exact request without guessing which packet or response format applies.

### Task 4: Optional real host-agent execution attachment — gated by runtime capability

**Files:** If and only if a callable host exists: create `src/auteur/beginner/studio_host_dispatch.py` and `tests/test_beginner_studio_host_dispatch.py`; modify `server.py`, `studio_agent_handoff.js`, `studio.js`, and an HTTP test file. If none exists, do not add a nonfunctional execution service; record this slice as an external integration dependency and keep Task 3 working.

**Interfaces:** `StudioArchitectureExecutor.enqueue(project_root: Path, canvas_id: str, request: HostAgentRequest) -> None` (trusted attached port). Default is `None`. The existing capability GET reports `attached:true` only when this port is registered. POST `/api/beginner/studio/canvases/{canvas}/architecture/dispatch` takes `{request_sha256}`, verifies the exact latest pending packet, calls the attached executor, and returns `{"request_sha256":"<exact-sha>","state":"submitted"}` only after truthful submission; a missing adapter or superseded packet yields a conflict/unavailable error. Normal completion still goes through `complete_architecture`.

- [ ] **GATE:** Identify an actual callable host integration in the target runtime; check its consent, concurrency, cancellation and credential boundaries. No generic shell command API, no model-specific Browser contract, and no executable shim that only reports "queued" without any worker.
- [ ] **RED:** With a fake injected executor, assert one deliberate dispatch receives the exact request, unavailable adapter rejects truthfully, changed vision/canvas or mismatched SHA blocks dispatch, repeated completion is idempotent, conflicting completion is refused. Run the new focused pytest and HTTP tests.
- [ ] **BUILD:** Implement the smallest typed attachment and opt-in UI action. Reuse existing persistence and response validation, bound waiting, and current-canvas checks. Do not invoke the model on page load or implicitly switch to paid direct-provider mode.
- [ ] **GREEN:** Run fake-adapter tests, then one **authentic** Browser → attached coding agent → typed `ArchitectureCandidate` → existing validation → graph journey on a disposable project. Document the actual runtime, request SHA, status, and cost/latency only if observable.
- [ ] **REVIEW/COMMIT:** Only claim "one-click agent generation" after the authentic path works; otherwise keep the task deferred while Tasks 1–3 and 5 remain useful.

**Acceptance:** A configured host can fulfill an explicitly requested proposal without manual JSON. The default unconnected environment never pretends it can.

### Task 5: Integrate narrative explanation and restore graph hierarchy

**Files:** Modify `studio_explanations.js`, `studio_explanation_views.js`, `studio.js`, `studio.html`, `studio.css`; test `tests/test_studio_explanations_unit.mjs`, `tests/test_studio_explanation_views.mjs`, `tests/test_studio_author_intent.mjs`.

**Interfaces:** Retain existing `AuteurStudioExplanationViews.renderGenre/renderTrope/renderStructure` and source-local IDs. Each facet uses one selected explanation as its dominant visual hero; Overview remains a spatial graph and the author may return to the same selection.

- [ ] **RED:** Test absent versioned Progression/Heroic Fantasy packs, a legacy Epic Fantasy convention, a trope related to two genres, an unsupported causal arrow, long labels and an explicit Back action. Run the existing explanation Node test files; expect new assertions to fail.
- [ ] **BUILD:** Present Genres as promise → engine/pressures → payoff; Tropes as independently sourced genre expectation versus this story's proposed treatment; Structure as recorded relation verbs and causal hypotheses; Timeline as concise phase modulation. Use existing reference APIs and proposal IDs; show "no verified pack" rather than invented universal rules.
- [ ] **HIERARCHY:** Compact the tall Story Vision toolbar, avoid persistent empty inspector and duplicated navigation, reveal advanced tools on demand, and preserve the selected node and working editor state. Keep consistent category colors **plus** text/status/shape cues; don't use colors as an authority substitute.
- [ ] **GREEN:** Rerun Node explanation tests; verify keyboard navigation, visible focus, no unsupported edges, correct "why this link" inspection, source revision invalidation, one-click return to Overview, and 390px responsiveness.
- [ ] **REVIEW/COMMIT:** Do not add an ontology, a second semantic graph, mandatory Genre Packs, or decorative new facets.

**Acceptance:** An author can answer "What does this genre promise?", "Is this trope expected or an AI idea?", and "How is this mechanism intended to work?" without interpreting backend state.

### Task 6: Qualify the integrated author journey, then test comprehension

**Files:** Extend `scripts/studio_stage_b_check.py` with small actual-browser checks only where coverage is missing; use existing `tests/test_beginner_studio_architecture.py`, `tests/test_studio_mentor_agent.py` and relevant Node tests. Record a concise finding in the existing qualification/evidence structure after actual execution, not in an invented pass report.

**Interfaces:** Existing CanvasStore/HTTP endpoints and typed host contracts; no novel test framework. Use a disposable paladin vision and, separately, an empty/no-provider workspace.

**Mandatory Stage 6 completion gate — Narrative Architecture E2E proof:** Follow the normative protocol in the companion specification, section 7. Do not close the integrated Narrative Architecture responsibility from unit tests, a prepared handoff packet, valid candidate JSON, backend-only API checks, a graph screenshot, or a canned/model-stubbed response. Prove the full author-visible path with the actual served Browser and an actual coding agent. Keep **manual-host E2E**, **connected-host E2E**, **mechanical automated tests**, and **human comprehension** as four separate result claims.

- [ ] **EXACT SOURCE:** Pin the combined candidate SHA, local checkout/environment, disposable project path, clean starting state, and Story Vision source bytes. Verify scripts/assets are served from the pinned tree, not stale installed packages. Record whether #441 and #442 are tested alone or as an integrated stack.
- [ ] **AUTHENTIC MANUAL END-TO-END:** In the actual Browser, enter the paladin generous-heroism vision, save and reopen, prepare the request, capture SHA, hand its exact packet to an actual active coding agent, and complete the matching typed response through the existing CLI/API. No prewritten creative answer or fake model adapter may count as creative generation proof. If the coding agent is unavailable, record **BLOCKED** and name that boundary.
- [ ] **GRAPH IS USEFUL:** Confirm a validated, nonempty graph appears in the same Browser. Inspect a reader experience, genre, trope and structural mechanism; inspect a concrete declared relation with its real source; use Genres/Tropes/Structure explanations; return to Overview and verify selection/navigation and proposed-versus-author-authored labels.
- [ ] **REAL CREATIVE REVISION:** Ask the existing mentor for at least two causally different interpretations when warranted. Specifically verify that the paladin need not be given a moral flaw the author did not choose. Keep or reject a choice only through the explicit working pathway; verify accepted-story files/receipts remain untouched.
- [ ] **REOPEN + FAILURE:** Close/reopen Studio and find the same working vision, candidate and deliberately kept working choice. Demonstrate at least one stale/cross-canvas/wrong-SHA or unavailable-host failure that is visible and non-destructive. Compare canonical/story SHA-256 before and after.
- [ ] **CONNECTED-HOST IS SEPARATE:** Claim automatic one-click execution only if the actual attached executor carries the Browser request through agent fulfillment, schema validation and graph rendering without manual transfer. With no real adapter, record **BLOCKED — no attached executor**, not PASS and not a fake provider integration. Do not hold unrelated manual UX repairs hostage to this missing capability.
- [ ] **REPEATABLE TEST:** Retain the smallest executable Browser/agent journey harness and regression checks needed to reproduce these observations (reuse Stage B/architecture HTTP/mentor suites). Use synthetic candidate fixtures for **renderer and protocol regression only**; they cannot replace the authentic agent run above. Inspect a materially different premise before claiming genre-general functionality.
- [ ] **PROOF RECEIPT:** In existing qualification-evidence records and PR descriptions, include exact baseline/candidate/integrated SHAs, timestamp, actual runtime/model or unavailable, request/response SHA and source revision, steps/results marked PASS/FAIL/BLOCKED, Browser logs/screenshots when available, test commands and counts, file-hash comparison, failures/retries and claim ceiling. Do not fabricate human participation, silently relabel an unavailable executor, or mark a partial check as the integrated E2E.

**Closure condition:** Integrated Narrative Architecture receives only **PASS — bounded manual E2E** when the live Browser + real coding-agent manual flow works. **PASS — connected E2E** additionally requires an actual attached execution run. Either may remain FAIL/BLOCKED without invalidating independently useful, truthfully scoped component work; neither establishes human UX or product readiness.

- [ ] **RED:** Establish the baseline task failures or missing behavior before integration where feasible; record actual observations separately from the desired results.
- [ ] **BROWSER:** Start the real local server. Exercise saved paladin vision → requested working architecture → source distinction → alternative hypothesis → deliberate working Keep or reject → graph facet explanation → back → reload. Run desktop and 390px Chromium, plus a keyboard-only path. Compare canonical/story hashes before and after.
- [ ] **FAILURE PATH:** Repeat with no connected host, invalid JSON, stale source SHA, two tabs/canvases, delayed response, interrupted request, missing pack evidence, and unsaved working edits. Confirm recoverability and no silent canonical writes.
- [ ] **REGRESSION:** Run `python -m pytest -q tests/test_beginner_studio_architecture.py tests/test_studio_mentor_agent.py tests/test_beginner_studio_mentor_http.py`, relevant `node --test` targets, and `python scripts/studio_stage_b_check.py`. Record exact SHA, counts and baseline-identical failures; do not describe a partial suite as a full suite.
- [ ] **HUMAN UX:** Perform a separate ~10–15-minute author walkthrough: identify exact author constraints, spot an AI-invented flaw, choose an alternative, explain a genre/trope/structure connection and source, recover the original selection after returning. Capture actual misinterpretations, hesitation and assistance without asking the participant to accept canon.
- [ ] **CLOSE:** Reconcile evidence with product status; keep human-use claim unqualified until a human actually performs the walkthrough. Stop when the bounded path works, rather than repeating broad test rituals.

**Acceptance:** The integrated experience is a usable graph-first creative exploration loop **at its demonstrated engineering scope**. Human comprehensibility and product/beta readiness remain separate decisions.

## Incremental PR Sequence and Stop Conditions

| PR-sized slice | Tasks | Independent retained value |
| --- | --- | --- |
| A — Honest intent/proposal UI | 1 | Stops agent-authored dramatic assumptions from looking author-approved |
| B — Contextual divergent interpretations | 2 | Author can challenge a proposed arc and keep only what they choose |
| C — Clear request status/manual handoff | 3 | Browser stays useful without a connected agent |
| D — Real opt-in host callback (conditional) | 4 | End-to-end one-click generation **only when a real host is available** |
| E — Source-explained spatial architecture | 5 | Graph teaches genre/trope/structure meaning instead of showing an inventory |
| F — Integrated qualification | 6 | Detects cross-surface regressions, then obtains human comprehension evidence |

Run local focused tests and review each slice before beginning unrelated work. PR D may be deferred while A/B/C/E proceed; no phantom adapter PR. If one task needs an upstream product decision that changes author authority, stop that task rather than hiding it in a refactor.

## Self-review / Contract Map

- **Source truth:** Task 1 owns comparison of exact author input vs proposal; Task 2 owns alternatives and deliberate working selection.
- **Agent execution:** Task 3 owns truthful fallback/status; Task 4 alone owns optional connected host dispatch.
- **Visual meaning:** Task 5 reuses the selected explanatory views and prior comparison; Task 6 verifies the full journey.
- **Non-negotiable:** No auto-accept, speculative genre rules, second mentorship store, provider-specific product identity, false ready states, or unverified human-usability claims.
- **Not in this wave:** Production release, new Genre Packs, general long-book performance re-architecture, direct ChatGPT session connection, native app, provider credentials, or a new semantic layer.

**Execution method:** Recommend **subagent-driven review per PR-sized slice** if the local coding environment supports independent reviewers, since the host bridge and author/canon distinction have distinct failure modes. Otherwise use native sequential implementation with one independent whole-branch review; honor the repository's protected merge process.
