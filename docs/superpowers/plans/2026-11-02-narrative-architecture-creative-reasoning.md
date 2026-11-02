# Narrative Architecture Creative Reasoning UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Conditional tasks are not permission to build without their evidence trigger.

**Goal:** Make Auteur's existing graph-first Narrative Architecture a trustworthy author-directed medium for discovering, comparing, developing and revising materially different narrative possibilities, beginning with one real source-bound author-intent journey rather than a new graph or UI subsystem.

**Architecture:** Keep the local CanvasStore as the noncanonical working owner, ArchitectureCandidate v2 as abstract working design, Studio Mentor as source-scoped creative reasoning, Story Realization as optional concrete development, and existing review/Book/scene surfaces as the continuity path. Start by observing the complete journey with the active host coding agent. Repair only the first material failure in its existing owning layer; preserve alternative interpretations as provisional and route all accepted changes through established author authority.

**Tech Stack:** Python >=3.11; Pydantic 2; `auteur.beginner` Studio/CanvasStore and `auteur.host_agent`; vanilla browser JavaScript and existing Studio server; pytest 8; Node built-in `node:test`. No new external provider SDK, persistence platform or state-management library.

**Spec:** [Narrative Architecture as a creative-reasoning UI — strategic analysis `11](../../research/auteur-ui-strategic-evolution-2026-10-24.md#11-follow-on-strategic-evolution--narrative-architecture-as-a-creative-reasoning-ui-2026-11-02); [earlier Connected Creative Thread analysis](../../research/auteur-ui-strategic-evolution-2026-10-24.md#7-strategic-synthesis-and-selected-control-move).

**Planning baseline:** `main@9098c6677d6a0b5876183ddee44d7301a54390ec`, November 2, 2026 (documentation PR #502). The executor must re-read current `main` / `STATUS.md`; this hash is not a future worktree lease.

**Disposition:** `R0 SELECTED FOR REPRODUCIBLE INVESTIGATION`; R1–R3 are **conditional candidate repairs**, not a committed feature queue. Owner endorsement of the strategic direction and request for this plan do **not** authorize schema changes, a new state owner, permanent multi-architecture branching or a production rollout.

## Global Constraints

- `MISSION.md` wins: local-first, single-author, backend-neutral, no automated acceptance, no auto-publishing, no new service by default, no destructive author work, and no mutation of accepted StoryIdentity without explicit author action.
- Graph-first and active-host-agent-first are selected product directions; manually drawing graph nodes is optional, not a prerequisite for one rich working architecture from a Story Vision.
- Preserve distinction between *author-declared intention*, *observed source*, *agent hypothesis*, *working candidate*, *registered artifact dependency*, and *accepted story*. A dependency path is not fictional causality. No numerical literary-quality scores.
- Source freshness is mandatory for consequential handoffs: request ID, request SHA, source SHA, canvas revision and disclosed source references as applicable. Do not cite omitted text or pretend accepted Identity was bound to Studio Mentor when it was not.
- Reuse the existing `ArchitectureCandidate`, `MentorAdvice`, `RealizationCandidate` and `HostAgentRequest` contracts. Do not introduce a universal causal-edge taxonomy, a general graph retrieval engine, a new acceptance owner, or a multi-architecture state enum without separate evidence and authorization.
- Keep the controlled F2 small-Book + X3 persistent Book frontier and S2 authentic-host-agent probe separate. The latter is recorded as blocked before live execution in `STATUS.md`; a synthetic reply or JS harness must never be relabeled authentic provider execution.
- Preserve existing source documents, fixture content and working prose. Probe only a newly created disposable project outside the repository; never stage private author material in committed fixtures.
- Verification is proportional to the claim: focused contract tests for changed behavior, exact real-host traces for claims about the agent, and real human judgments for claims about creative usefulness. A skipped test is `NOT RUN`, never `PASS`. The owner previously permitted development integration without waiting for broad suites; do not reinterpret that as qualification.

## Review Focus

Five high-risk inputs/conditions are pinned to the owning tasks, not left as generic “edge cases”:

1. **A long or omitted source item** — truncated content is marked as incomplete, is not cited as if read, and cannot be used to invent manuscript facts (Tasks 1 and 3; existing `test_prose_first_architecture_request_labels_truncated_and_omitted_sources` and S2 stress).
2. **A changed vision or candidate during a host response** — old replies remain stale evidence, not ready guidance or accepted changes (Tasks 2 and 3; `test_vision_edit_rejects_stale_response_and_keeps_evidence` and `test_stale_reply_is_retained_as_stale_not_shown_as_fresh`).
3. **Dense/ambiguous focused relations or cross-namespace ID collisions** — no false source citations or invented multi-hop causality; missing context is declared (Tasks 2 and 4; `test_ready_candidate_cites_only_disclosed_neighbor_links_and_questions`, `test_working_id_collision_does_not_inherit_candidate_edges`).
4. **Two similar proposed directions or switching an edited preview** — causal difference is explicit, revised author text is not overwritten, and no option is saved passively (Tasks 2 and 5; `test_explore_rejects_relabelled_duplicate_mechanisms` and `test_studio_mentor_dialogue.mjs`).
5. **A Realization scene or architecture feedback that could overwrite authored work** — selected abstract focus must be meaningfully instantiated; generated scene/feedback stays noncanonical, stale or destructive copy is refused (Tasks 2 and 6; `test_beginner_studio_realization_creative_continuity.py` and `test_studio_generated_prose_copy.mjs`).

---

## 1. Scope, baseline and ownership map

**Do not rebuild existing functionality.** The reviewed code already supports:

- `studio_architecture.py`: `ArchitectureCandidate` v2; `prepare_architecture(store, instruction="")`; `complete_architecture(store, payload)`; `apply_architecture_review(store, request_sha256)`; request/response identity and stale-source checks. V2 abstract architecture disallows premature concrete `character` and `relationship` nodes.
- `studio_mentor.py`: `prepare_mentor(store, focus_id, focus_kind, purpose="explore", author_reply="")`, `complete_mentor` and `project_mentor`; `MentorAdvice` with up to **three** directions, `mechanism`, `consequence`, `tradeoff`, `distinguishing_factor`, `source_status` and `source_refs`. Candidate focus currently receives up to **12 direct relations**, **8 open questions**, bounded working context, and `accepted_identity_status="not_bound"`. It does **not** claim full multihop Book reasoning.
- `studio_mentor_dialogue_controller.js` and `studio_unfolding_controller.js`: on-demand host request, conditional alternatives already displayed with trade-offs, author-edited “Review as working idea” and explicit Keep into `CanvasStore` with `proposal_origin`. Dirty edits and stale packets block unsafe replacement.
- `studio_realization.py`: `prepare_realization(store, focus_ids=None, instruction="")`, `complete_realization`, `apply_realization_review`; concrete `architecture_refs` and optional `ArchitectureFeedback` are working proposals, not canon.
- `studio.js`: focused graph/inspector, source and freshness, architecture review, working scene copy with replacement confirmation, `proposeArchitectureFromRealization`, saved focus/re-entry and Book navigation. `studio_impact.py` is **artifact** dependency, not story causality.
- `scripts/probe_s2_manuscript_host_agent.py`: independent S2 manuscript/correction exercise. **Reuse it for S2 questions rather than introducing a second manuscript fixture driver**; this plan's R0 is a distinct **graph-to-story creative reasoning** journey.

| Responsibility | Existing implementation to use first | Targeted test/evidence owner |
| --- | --- | --- |
| Scratch source and working revisions | `src/auteur/beginner/studio_store.py` | `tests/test_beginner_studio_store.py`; scratch receipt |
| Abstract source packet and review | `src/auteur/beginner/studio_architecture.py` | `tests/test_beginner_studio_architecture.py` |
| Agent creative context / options | `src/auteur/beginner/studio_mentor.py` | `tests/test_studio_mentor_agent.py`; `tests/test_beginner_studio_mentor_http.py` |
| Visible options and explicit Keep | `src/auteur/beginner/browser/studio_mentor_dialogue_controller.js`; `studio_unfolding_controller.js` | `tests/test_studio_mentor_dialogue.mjs`; `tests/test_studio_mentor_synthetic_journey.mjs` |
| Concrete story and feedback | `src/auteur/beginner/studio_realization.py`; `studio.js` | `tests/test_beginner_studio_realization_creative_continuity.py`; `tests/test_beginner_studio_realization_browser.py` |
| Scene prose safety and re-entry | `studio.js`, `studio_store.py`, current Book UI | `tests/test_studio_generated_prose_copy.mjs`; `tests/test_beginner_studio_reentry_browser.py` |
| Operational status | `STATUS.md` + existing F2/X3 and S2 records | Distinct evidence in `docs/product-validation/living-story-studio/` only when an actual trace exists |

### Execution decision tree

```text
R0: SOURCE-BOUND AUTHOR INTENTION -> EXACT HOST ARCHITECTURE
    -> FOCUSED MENTOR -> REVIEWABLE ALTERNATIVES
    -> REALIZATION -> WORKING SCENE / ARCHITECTURE FEEDBACK -> RE-ENTRY
    |
    +-- blocked by no runnable checkout or host agent?
    |     -> BLOCKED at that boundary; retain only reproducible local evidence
    |
    +-- full trace works with no material author-task failure?
    |     -> NO_CHANGE; report useful capabilities and remaining evidence limits
    |
    +-- agent/context cannot reason from source?
    |     -> R1: smallest Mentor/context/instruction correction
    |
    +-- meaningful alternatives cannot be understood or retained?
    |     -> R2: smallest existing Mentor/review/working-idea UI correction
    |
    +-- source intent is lost between realization, scene and feedback?
          -> R3: smallest existing Realization/Studio/Book continuity correction
```

Only **one first material failure** selects the next code task. The remaining conditional tasks are alternatives, not an instruction to implement all three lanes.

## Task 0 — Preflight the real execution boundary (R0)

**Files:** Read `AGENTS.md`, `MISSION.md`, `STATUS.md`, `docs/plans/2026-10-26-s2-authentic-manuscript-agent-construction-plan.md` and the module files in `1`. No product-code changes. Record execution identity in the Task 2 receipt, not a new application state.

**Interfaces:** Consumes actual git/worktree identity, available Python/Node executables and an active host coding agent with filesystem access. Produces an explicitly classified `RUNNABLE` or `HOST_AGENT_EXECUTION_UNAVAILABLE` preflight.

- [ ] **Step 1: Verify the actual workspace.** Run `git rev-parse --show-toplevel`, `git rev-parse --git-common-dir`, `git rev-parse HEAD` and `git status --short`; do not assume the connector's repository is mounted as a runnable checkout.
- [ ] **Step 2: Establish runtime readiness.** Run `python --version`, `PYTHONPATH=src python -c "from auteur.beginner.studio_store import CanvasStore; print('CANVAS_IMPORT_OK')"` on a POSIX shell (use equivalent Windows environment assignment there), and `node --version`. Expected: Python >=3.11, import marker, available Node. Record failures verbatim.
- [ ] **Step 3: Identify the active host coding agent's exact shared request/response filesystem.** It must be able to read a saved `HostAgentRequest` and write *raw JSON* to a scratch path; a connector fetch, manual example or fake `LLMResponse` is not a substitute. Do not require an additional provider API key or vendor-specific adapter.
- [ ] **Step 4: Create a disposable scratch project outside the repository.** For example `<SCRATCH>` from a fresh temporary directory, canvas ID `creative-r0`. Snapshot the presence or SHA of any accepted story files **if they exist**. Never run on the frozen Glass Archive F2/X3 project or valued manuscripts.
- [ ] **Step 5: Gate.** If steps 1–3 are blocked, record `BLOCKED` with the smallest prerequisite and stop before claiming live R0. Do not introduce a workaround service, fake host response or product patch solely to make a progress metric move.

**Review outcome:** repeatable, truthful execution preflight; no claim of test success without actual output.

## Task 1 — Run one original creative-intent -> agent reasoning trace (R0)

**Files:** Use existing `studio_store.py`, `studio_architecture.py`, `studio_mentor.py`, `studio_realization.py` and Studio browser. Create scratch-only raw candidate/advice/realization files under `<SCRATCH>`. Do **not** create a second permanent probe runner unless a concrete reuse failure is demonstrated.

**Interfaces:**
- Consumes `CanvasStore(Path(<SCRATCH>), "creative-r0")` with `story-vision` and revision; current host `request.system`, `request.user` and SHA; an existing candidate node ID `<FOCUS_ID>`.
- Produces an exact source-bound `ArchitectureCandidate`, `MentorAdvice` and `RealizationCandidate` **only if returned by the actual host agent**, plus optional working scene/review; no accepted story changes.

- [ ] **Step 1: Stage a deliberately fictional creative intention** in a fresh `CanvasStore` using `store.create()` then `store.apply("create-item", expected_revision=0, command_id="creative-r0-vision", payload={"item": {"id": "story-vision", "kind": "note", "title": "Story Vision", "content": <VISION>}, "position": {"x": 40, "y": 40}})`. Use this **new scratch input**, not a claim about the literal W4 author's private preferences:

  > A coastal community experiences recurring floods. An incomplete historical ledger influences water allocation, but no record can resolve every present claim of fairness. Develop a renewable narrative architecture with mystery, communal disagreement, everyday generosity and meaningful consequences. Preserve uncertainty, avoid a predetermined moral verdict and do not create named characters at the abstract Architecture stage.

- [ ] **Step 2: Prepare the exact architecture request.** Run `PYTHONPATH=src python -m auteur.beginner.studio_architecture --project <SCRATCH> --canvas creative-r0 prepare`, then `... show`. Expected: `status="awaiting_host_agent"` with a `studio_architecture` request; capture `request_sha256`, `source_sha256`, visible source excerpt/omission information, and the exact request location.
- [ ] **Step 3: Have the active coding agent answer precisely that request**, obeying `system` + `user` and writing a raw `ArchitectureCandidate` v2 JSON to `<SCRATCH>/architecture.json`. Complete via `PYTHONPATH=src python -m auteur.beginner.studio_architecture --project <SCRATCH> --canvas creative-r0 complete-file --candidate <SCRATCH>/architecture.json`. Expected: `status="ready"` and a candidate; if invalid, stale or unavailable, record the actual error and do not fabricate success.
- [ ] **Step 4: Select one *real* returned engine/theme/structure node ID**; do not invent `<FOCUS_ID>`. Run `PYTHONPATH=src python -m auteur.beginner.studio_mentor --project <SCRATCH> --canvas creative-r0 prepare --focus-id <FOCUS_ID> --kind candidate --purpose explore`. Inspect disclosed `nodes/` / `links/` refs, local context, `accepted_identity_status="not_bound"` and source SHA.
- [ ] **Step 5: Obtain a real agent `MentorAdvice`** as raw JSON `<SCRATCH>/mentor-advice.json`; submit via `PYTHONPATH=src python -m auteur.beginner.studio_mentor --project <SCRATCH> --canvas creative-r0 complete-file --advice <SCRATCH>/mentor-advice.json`. Expected: `ready` advice with at least one *materially* different mechanism when exploration is warranted, honest `source_status`, relevant trade-off, and no canonical mutation. A schema-valid response alone is not a good-literature verdict.
- [ ] **Step 6: Compare the actual directions** against the same Story Vision: which assumption differs, what renewable mechanism changes, what conditional consequence follows, what is speculative, and what is lost? If directions are generic rewordings or cite missing edges, mark a *candidate R1/R2 failure* with exact evidence. Do **not** manufacture extra choices to satisfy a count.
- [ ] **Step 7: Keep one choice only through existing explicit working review**, if its source/revision is current; verify `proposal_origin` and author's editable content. Use existing UI rather than a direct canonical acceptance API. Preserve the unchosen direction in host advice/receipt; do not claim it is a versioned whole-story architecture.
- [ ] **Step 8: Prepare concrete Realization for the selected architectural focus.** Run `PYTHONPATH=src python -m auteur.beginner.studio_realization --project <SCRATCH> --canvas creative-r0 prepare --focus <FOCUS_ID>`. Have the same active host agent answer the exact request with raw JSON; complete via `... studio_realization --project <SCRATCH> --canvas creative-r0 complete-file --candidate <SCRATCH>/realization.json`. Expected: `architecture_refs` include the selected ID and its **description** substantively instantiates a mechanism; `architecture_feedback` remains a proposal.
- [ ] **Step 9: Inspect the Browser continuation** using the existing local Studio server, when runnable: review the concrete element, copy it to a *working* scene, inspect source/freshness and potential architecture feedback, and reopen the same canvas/Book navigation. Do not claim uninterrupted browser UX if only CLI stages were run. Snapshot accepted story files again; no accidental writes.
- [ ] **Step 10: Record the actual result** as `OBSERVED` / `NOT OBSERVED` / `BLOCKED` at each handoff, with selected focus ID, request SHA, source fingerprints, what the agent actually saw, omitted data, author decisions, outcome and failures. Avoid committing raw generated material/private user text unless explicitly safe.

**Acceptance:** one **authentic** Architecture -> focused Mentor -> Realization chain, plus traceable optional scene/re-entry, or an exact boundary-specific blocker. A partial trace is useful evidence if its ceiling is labeled.

## Task 2 — Adversarially inspect authority, omission, freshness and UI safety (R0)

**Files:** Existing tests; scratch-only project/candidate modifications. No new feature.

**Interfaces:** Consumes the Task 1 scratch and existing test fixtures; produces an explicit failure classification, not a score.

- [ ] **Step 1: Run only focused mechanical tests** in the runnable checkout:

  ```sh
  PYTHONPATH=src python -m pytest -q tests/test_beginner_studio_architecture.py tests/test_studio_mentor_agent.py tests/test_beginner_studio_realization_creative_continuity.py tests/test_beginner_studio_mentor_http.py
  node --test tests/test_studio_mentor_dialogue.mjs tests/test_studio_mentor_synthetic_journey.mjs tests/test_studio_generated_prose_copy.mjs
  ```

  Expected only if actually run: zero failures. Record skipped/unavailable commands without treating them as passes. Do not launch an unrelated full release suite just to validate one author-intent hypothesis.

- [ ] **Step 2: Exercise source visibility and omission** with the existing `tests/test_beginner_studio_architecture.py::test_prose_first_architecture_request_labels_truncated_and_omitted_sources` and S2 `stress` fixture **separately** if relevant. An excerpt or omitted item is never a claim to have read whole prose.
- [ ] **Step 3: Exercise stale and collision cases** using `tests/test_studio_mentor_agent.py::test_stale_reply_is_retained_as_stale_not_shown_as_fresh`, `::test_ready_candidate_cites_only_disclosed_neighbor_links_and_questions` and `::test_working_id_collision_does_not_inherit_candidate_edges`. Confirm first-hop relation limits and source-ref namespaces are honestly disclosed.
- [ ] **Step 4: Inspect alternatives and working preview safety** with existing `tests/test_studio_mentor_agent.py::test_explore_rejects_relabelled_duplicate_mechanisms` and `tests/test_studio_mentor_dialogue.mjs`. Verify no passive saves, no switching away from a dirty author preview, and no stale Keep.
- [ ] **Step 5: Inspect creative and prose continuity** with `tests/test_beginner_studio_realization_creative_continuity.py` and `tests/test_studio_generated_prose_copy.mjs`; run the existing re-entry browser check only if its browser dependencies are available and the claim requires it. Confirm no unconditional scene replacement or silent architecture revision.
- [ ] **Step 6: Compare actual source/canonical artifacts**: record original/after hashes where existing accepted files were present; if not, record their absence and the narrower result. Separate `SOURCE/CONTRACT PASS` from `HOST-AGENT REASONING OBSERVED` and `HUMAN-CREATIVE-USEFULNESS NOT YET TESTED`.

**Acceptance:** all five Review Focus cases either independently supported by fresh scoped evidence or listed as unresolved; one concrete first material failure is located and assigned to its actual process owner.

## Task 3 — Reconcile the R0 decision before modifying product code

**Files:** Create `docs/product-validation/living-story-studio/2026-11-02-creative-reasoning-author-journey.md` **only after there is a genuine R0 trace** (name by actual execution date if later). If blocked before execution, update the existing S2/frontier dependency record only if its operational status has actually changed; otherwise use a PR/issue receipt and stop. Do not produce a duplicate narrative strategy document.

**Interfaces:** Consumes Tasks 0–2 source/evidence. Produces one of `NO_CHANGE`, `REPAIR_MENTOR_CONTEXT`, `REPAIR_MENTOR_INSTRUCTION`, `REPAIR_ALTERNATIVE_REVIEW`, `REPAIR_REALIZATION_CONTINUITY`, `HOST_AGENT_EXECUTION_UNAVAILABLE`, or `OWNER_DECISION_REQUIRED` as **report labels**, not new persistent runtime enums.

- [ ] **Step 1: Tabulate evidence** by `author task | exact SHA/source | observed behavior | interpretation | negative alternative | owning boundary | what remains unqualified`.
- [ ] **Step 2: Identify the first genuinely material failure** in a normal creative task; distinguish presentation, context disclosure, agent prompt, real generation, craft understanding, workflow continuity, source freshness, schema representation, and external environment.
- [ ] **Step 3: Choose a *single* smallest remedy or `NO_CHANGE`.** Do not select R1+R2+R3 because the roadmap lists them. If ontology or author authority must change, stop and propose a separate owner decision/spec rather than opportunistically edit schema.
- [ ] **Step 4: Preserve the original alternative and counter-reading** in the evidence so the investigation does not self-validate only the favored narrative direction.
- [ ] **Step 5: Commit a grounded receipt if appropriate.** A report is not product qualification; do not upgrade `STATUS.md` or F2/X3 by inference.

**Acceptance:** reproducible reasoning for the selected next action, including legitimate stopping.

## Task 4 — Conditional R1: repair focused agent reasoning only if Task 3 selects it

**Trigger:** exact R0 response shows that the agent missed *disclosed* causal context, incorrectly implied complete context, fabricated provenance, or produced indistinguishable mechanisms in a decision where difference mattered.

**Files:**
- Modify, if context owner: `src/auteur/beginner/studio_mentor.py`, specifically `_context(store: CanvasStore, focus_id: str, focus_kind: str) -> dict`.
- Modify, if instruction owner: `src/auteur/beginner/studio_mentor.py::_SYSTEM`.
- Test: `tests/test_studio_mentor_agent.py`; `tests/test_beginner_studio_mentor_http.py` only for changed API behavior.
- Do **not** modify `ArchitectureCandidate`, `studio_store.py` or the accepted narrative ontology as a default.

**Interfaces:** Retain `prepare_mentor` / `complete_mentor` / `project_mentor` public signatures, `MentorAdvice` v1, explicit `allowed_refs` and existing `request_sha256`/`source_sha256` validation. Any added *explanatory* context field must be optional to generation and must be covered by the source fingerprint.

- [ ] **Step 1: Write one failing regression named after the observed error**, not an invented general “reasoning quality” check. For a verified **truncated direct-relation context** failure, add `test_candidate_focus_declares_omitted_direct_relations` to `tests/test_studio_mentor_agent.py`: construct a ready candidate with 13 focus-adjacent links; assert that the context exposes 12 with their original `links/<index>` references, `omitted_direct_relation_count == 1`, and `links/12` is not citable. If the observed failure differs, capture its exact input/expected contract instead of adding this illustrative field gratuitously.
- [ ] **Step 2: Verify RED.** Run `PYTHONPATH=src python -m pytest -q tests/test_studio_mentor_agent.py -k candidate_focus_declares_omitted_direct_relations`, and confirm the *intended* missing behavior fails (not an import/environment error).
- [ ] **Step 3: Repair the smallest owner.** For the *verified omission case only*, compute and expose the count from the same direct-link iteration in `_context`, without extending citable refs or changing candidate schema. For the *verified bad-instruction case only*, strengthen `_SYSTEM` to distinguish author premise, cited source, conditional mechanism, trade-off and explicit uncertainty; use the existing `MentorDirection` fields, not a parallel “ReasoningTrace” store.
- [ ] **Step 4: Verify GREEN and surrounding invariants.** Run the new focused test, then `PYTHONPATH=src python -m pytest -q tests/test_studio_mentor_agent.py tests/test_beginner_studio_mentor_http.py`. Recheck nonexistent refs, stale reply, unknown focus, same-ID collision, `no_intervention` and no writing to accepted state.
- [ ] **Step 5: Re-run the *same exact* creative intent and host-agent question** to see whether the formerly failing literary reasoning changes. New mechanical context visibility is not sufficient to claim agent usefulness; report when no host execution was possible.
- [ ] **Step 6: Commit one bounded change** with its exact reproduction and result. If the needed evidence is broader multihop causality or mandatory typed relations, **STOP for a separate scoped design/owner decision**; no automatic general retrieval subsystem.

**Acceptance:** specifically observed failure fixed with trustworthy exposed context or instruction and no loss of source/authority safety; or `NOT SELECTED` with no code.

## Task 5 — Conditional R2: improve comparison/preservation only when the current Mentor UI fails an author task

**Trigger:** an actual user cannot distinguish directions, loses important alternatives, or cannot preserve reviewed working ideas **despite** the existing cards and explicit Keep interaction.

**Files:** `src/auteur/beginner/browser/studio_mentor_dialogue_controller.js` and, only if an existing save boundary proves inadequate, `studio_unfolding_controller.js` / `studio.js`. Tests `tests/test_studio_mentor_dialogue.mjs` and `tests/test_studio_mentor_synthetic_journey.mjs`. Existing `CanvasStore` remains the sole working owner.

**Interfaces:** Consume current `MentorAdvice.directions[]` with `mechanism`, `consequence`, `tradeoff`, `distinguishing_factor`, `source_status` and `source_refs`. A reviewed Keep remains an explicit author action tied to the same focus/response identity; preserving multiple ideas must not bypass source-staleness or concurrency rules.

- [ ] **Step 1: Reproduce the precise friction** in the existing dialog: read-only comparison, preview editing, selecting a different option, Keep, reopening or re-entry. Record whether there is **already no gap**; the UI currently shows differentiators and trade-offs, and a matching test is not evidence of a missing feature.
- [ ] **Step 2: Select the smallest UI repair** only if its failure is witnessed: e.g. clarification of conditional consequence/source-status copy or a bounded comparison layout assembled from the **existing** direction fields. Do **not** create full-architecture branching, an additional canonical proposal store, or a new quality metric because “comparison” appears in the strategic model.
- [ ] **Step 3: Write a failing Node test** asserting that two source-distinct proposals render both mechanisms and trade-offs, use `textContent` (untrusted author/agent text is not HTML), and create **zero** writes until deliberate Keep. For an observed edited-preview conflict, assert the edited author's content survives selecting another suggestion.
- [ ] **Step 4: Verify RED, implement the minimal DOM/presentation change, verify GREEN.** Run `node --test tests/test_studio_mentor_dialogue.mjs tests/test_studio_mentor_synthetic_journey.mjs`. Validate stale packet, double click and source-collision guards. Prefer no new JS module where the controller already owns the interaction.
- [ ] **Step 5: If the actual problem is retaining *multiple complete architectures***, stop this task and first create a separately approved design for identity/versioning and explicit author review. A working Mentor card is not a whole-story fork.
- [ ] **Step 6: Commit and re-run the original author comparison.** Record whether comprehension improved as a human observation or only whether controls behaved mechanically.

**Acceptance:** a demonstrated local comparison/review issue corrected without automatic story writes, or `NOT SELECTED / NO_CHANGE`.

## Task 6 — Conditional R3: repair Architecture -> Realization -> scene -> feedback continuity

**Trigger:** actual source/focus, author intent, revision/provenance, working scene text, or proposed Architecture feedback is lost or incorrectly presented across an existing handoff.

**Files:** `src/auteur/beginner/studio_realization.py` (source/context/freshness); `src/auteur/beginner/browser/studio.js` (current `copyRealization` and `proposeArchitectureFromRealization` paths) **only as warranted**. Tests `tests/test_beginner_studio_realization_creative_continuity.py`, `tests/test_beginner_studio_realization_browser.py`, `tests/test_studio_generated_prose_copy.mjs` and `tests/test_beginner_studio_reentry_browser.py`.

**Interfaces:** Reuse `RealizationElement.architecture_refs`, `ArchitectureFeedback.architecture_node_id/observation/proposed_change`, `prepare_realization`, `prepare_architecture(..., instruction=...)` and the existing explicit working-review APIs. No new accepted-story mutation endpoint.

- [ ] **Step 1: Reproduce one exact continuity failure** from the Task 1 project, including source request SHA, author intention, selected Architecture node, returned concrete element and UI action. A merely matching `architecture_refs` ID is insufficient if the concrete description does not instantiate the mechanism.
- [ ] **Step 2: Write the failing owning-boundary test.** For a verified focus propagation defect, test `prepare_realization(store, focus_ids=[<FOCUS_ID>])` and `complete_realization` for exact requested focus coverage and meaningful source reference *contract*; for a UI feedback defect, test that clicking the existing “potential architecture refinement” path only **prepares a working revision request**. For an overwrite defect, exercise the existing user-confirmation branch rather than adding a second scene store.
- [ ] **Step 3: Verify RED**, implement the smallest fix in the existing owner, then verify GREEN with `PYTHONPATH=src python -m pytest -q tests/test_beginner_studio_realization_creative_continuity.py tests/test_beginner_studio_realization_browser.py` and `node --test tests/test_studio_generated_prose_copy.mjs`. Run the Browser re-entry check when the environment supports it; do not claim it passed without actually running.
- [ ] **Step 4: Verify no silent promotion:** `architecture_feedback` stays advisory; moving to Architecture invokes an explicit instruction/review, and accepted Identity, Structure, Relations, Realization and Chapter remain untouched until their own author-governed acceptance.
- [ ] **Step 5: Re-run the original creative thread** including a source edit and re-entry after restart. Confirm the selected node and author intent remain visible, stale work is flagged, and the draft is not overwritten by generated text.
- [ ] **Step 6: Commit a single source-bound correction and document its claim ceiling.** A failing semantic judgment about whether a character actually dramatizes a theme may call for better host reasoning/author review rather than an impossible deterministic “literary quality” validator.

**Acceptance:** observed continuity failure fixed at the correct owner, or `NOT SELECTED / NO_CHANGE`.

## Task 7 — Reconcile results, scope and next authority boundary

**Files:** Existing R0 evidence receipt (if run), `docs/product-evolution-roadmap.md` (only if the candidate's disposition materially changed), and `STATUS.md` **only** if its actual operational evidence/state changed. Keep this plan as the prospective checklist; avoid expanding it into a permanent competing status service.

**Interfaces:** Consumes exact merged commit, narrowly affected tests, any real host-agent outputs and author observations. Produces decision and clean traceability.

- [ ] **Step 1: Re-read the original spec (`11.1–11.8) and this plan.** For each requirement, mark `OBSERVED`, `MECHANICALLY VERIFIED`, `NOT OBSERVED`, `BLOCKED` or `NOT SELECTED`. Do not transform the labels into runtime state.
- [ ] **Step 2: Confirm the scope boundary:** no new canvas/acceptance owner, no auto-accepted plot, no unsupported graph-causal inference, no invented or hidden source, no unrequested platform/provider dependency, and no erased author prose.
- [ ] **Step 3: Inspect branch diff for unrelated files and run only focused checks whose outputs support the change.** Record **not run** tests and environmental limitations exactly; review current source revision before describing test applicability.
- [ ] **Step 4: Commit/PR the smallest independent delivery if one was selected.** Keep R0 evidence and R1/R2/R3 code separate when reviewers can independently accept/reject them; do not merge unselected future capabilities. User-authorized integration policy governs whether a PR can merge without broad tests; an untested merge does not mean qualification.
- [ ] **Step 5: Return one accountable outcome:** `NO_CHANGE` (existing journey sufficient for the task); `BOUNDARY REACHED` (host/human assessment unavailable); `REPAIRED` (exact observed failure and scoped proof); or `OWNER DECISION REQUIRED` (material ontology, product-thesis or canonical-authority change). Never fabricate additional tasks to avoid a legitimate stop.

### Rollout and success criteria (no arbitrary scorecard)

**Immediate completion for R0:** a reproducible exact host request, honest source limits, actual or explicitly blocked candidate/mentor/realization handoffs, a preserved author decision and a clear next-action/stop disposition.

**Author usefulness:** at least one real author can explain how two directions differ *causally* and what each sacrifices, decide which to develop, and return to a saved working scene without losing intention. This is **human evidence**, not inferred from JSON schema or a Node harness.

**Future expansions considered only if demanded:** bounded two-hop context, typed narrative relations, broad alternative-architecture versions, spatial relationship overlays and rich reader-experience causal maps. None is automatically selected by completion of R0–R3.

**Anti-goals:** bigger graph for its own sake; six new UI modes for six reasoning verbs; a second narrative source of truth; ungrounded “agent knows the whole story”; automatic authorial choice; permanent branches from a single synthetic stress test.

**Execution method recommendation:** use **subagent-driven development** when code changes are actually selected (one fresh worker for the smallest owning task and independent source/authority review). For R0, a native agent in a verified shared checkout is sufficient because the critical dependency is **real access to the exact saved host request**, not more simulated workers.

**Aphorisms:** It is not graph expansion; it is source-grounded creative reasoning. It is not automatic storytelling and not another dashboard; it is an author-controlled path from possibility to consequence. A well-preserved narrative alternative is actually creative optionality.
