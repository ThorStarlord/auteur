# Agent-First, Ontology-Grounded Narrative Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking. Read the approved spec and current repository before changing code.

**Goal:** Make the active coding agent reliably construct a complete, intelligible first Narrative Architecture from a Story Vision, propose coherent holistic revisions, and continue ontology-grounded creative work across sessions and agents without silently accepting story or ontology changes.

**Architecture:** Extend the existing Studio CanvasStore -> ArchitectureCandidate v2 -> HostAgentRequest/Response -> working review pipeline. Reuse the packaged OntologyLoader, accepted Story Identity, existing source/freshness guards, CLI bridge and Studio browser; add only bounded source-grounded context, intelligible reviews and project-level provisional-concept continuity where demonstrated necessary. No parallel canonical store, mandatory external provider, new semantic layer or automatic acceptance.

**Tech Stack:** Python >=3.11, Pydantic >=2.6,<3, PyYAML >=6,<7; pytest >=8; vanilla JavaScript and Node built-in node:test; existing local Beginner HTTP server and coding-agent host handoff. No new external dependencies or provider-specific SDK.

**Spec:** [Approved design brief](../specs/2026-11-03-agent-first-ontology-grounded-narrative-architecture-design.md) (PR #507, merged 2026-11-03). Read [canonical semantic layers](../../narrative-architecture.md) and [MISSION](../../../MISSION.md) as authority.

**Relation to earlier work:** The [2026-11-02 creative-reasoning UI plan](2026-11-02-narrative-architecture-creative-reasoning.md) and [issue #504](https://github.com/ThorStarlord/auteur/issues/504) cover a particular blocked authentic host-agent R0 run. This plan covers the newly clarified **agent-first generation, holistic revision, ontology grounding, session continuity and provisional evolution** contract. Do not relabel unavailable real execution as a failed product behavior or close #504 using synthetic evidence.

**Plan status:** AUTHORIZED FOR PLANNING by author approval of the design brief; implementation, author-use qualification and release have **not** occurred. Execute tasks only in a full repository checkout with the required tools; if a real host agent is unavailable, finish only tests that can be honestly run and record the unqualified evidence ceiling.

## Global Constraints

- Preserve MISSION.md: **no auto-accept**, no new canonical story/ontology owner, no cloud/multi-author system, no automatic publishing; keep execution-backend neutrality and local-first, single-author behavior.
- Respect Ontology -> Identity -> Structure -> Realization -> Expression, and the distinction between abstract, noncanonical ArchitectureCandidate v2 and accepted commitments/plans.
- Given a nonempty Story Vision, create a **complete first abstract proposal** without a mandatory interview; do not invent cast, scenes, factions, plot acts or new accepted canon.
- Revising a material creative direction must reconsider all materially affected emotions, structure, genres, trope functions and mechanisms, **while preserving unrelated author decisions**.
- Source-backed ontology definitions and accepted Identity outrank agent guesses; distinguish author declarations, working agent proposals and unknowns.
- Provisional project concepts remain usable across agents/sessions but **never automatically enter shared accepted ontology**.
- Preserve historical request/current.json behavior, including schema-v1 reads, the v2 generation contract, SHA-256 request binding, source truncation/omission honesty, and stale/duplicate response safeguards.
- Use existing Studio and its browser as an optional inspection surface; the author must not need to operate the graph to obtain or revise architecture.
- Test changed behavior in the smallest owning modules. Deterministic tests cannot prove literary quality; reserve such claims for a real active-host-agent trace and author review.
- Keep each merged change narrowly scoped, with its focused tests and explicit evidence. No cross-cutting refactor by default.

## Review Focus

The following high-risk inputs may not be exhaustively specified by the brief; they receive explicit owning-task tests.

1. **Sparse Vision / unknown genre:** a short emotional vision yields provisional intent, not fabricated accepted genres or a blocking questionnaire (Task 3).
2. **Accepted Identity conflict:** a working holistic revision does not silently change hard constraints, accepted emotion promises or Story Identity (Tasks 3–4).
3. **Truncated working manuscript or 24-item omission:** the agent must not interpret unseen text as evidence (Task 1 and the actual trace in Task 8).
4. **Guidance/ontology updated but Vision unchanged:** the UI must not describe an ontology revision as an author editing their story; legacy in-flight packets remain readable (Task 2).
5. **Stale, duplicated or mismatched agent responses:** no replacement of current working architecture, no leaked acceptance, and an honest status (Tasks 2, 4, 8).

Representative exact assertions for new pure contracts (complete the surrounding fixture/setup in the indicated test files):

~~~python
def test_context_contains_reusable_meanings():
    result = build_relevant_ontology_context("A mystery about knowledge", None)
    concepts = {item["name"]: item for item in result["concepts"]}
    assert result["authority"] == "derived_ontology_guidance"
    assert "Theme" in concepts and concepts["Theme"]["definition"]
    assert "Conflict" in concepts and concepts["Conflict"]["relationships"]

def test_concept_proposal_is_not_accepted_ontology(tmp_path):
    store = CanvasStore(tmp_path, "test-concepts")
    store.create()
    record_provisional_concept(store, proposal, expected_revision=0, command_id="concept-1")
    assert list_provisional_concepts(CanvasStore(tmp_path, "test-concepts"))[0].status == "provisional"
    assert not (tmp_path / "story_identity.yaml").exists()
~~~

The Task 7 example's proposal is a valid ProvisionalNarrativeConcept fixture; use the existing package loader and a before/after hash to assert that canonical ontology resources are unchanged.

---

## 0. File responsibilities and dependency order

### Existing owners to reuse

| Existing file | Ownership / planned use |
| --- | --- |
| src/auteur/beginner/studio_architecture.py | ArchitectureCandidate v2, bounded source projection, generation request, validation, application, CLI, project_architecture projection |
| src/auteur/host_agent.py | Backend-neutral request/response packets and integrity; keep unchanged unless a real contract defect is demonstrated |
| src/auteur/beginner/studio_store.py | Local working canvas, revisions, atomic and idempotent working-note writes; no story canon |
| src/auteur/narrative_ontology/loader/ontology_loader.py | Packaged base and genre concept definitions; do not duplicate the accepted ontology |
| src/auteur/beginner/server.py | Existing Studio architecture prepare/response/apply/get routes |
| src/auteur/beginner/browser/studio.html, studio.js, studio.css | Existing Story Vision, request handoff, revision review, explanation facets, graph and status |
| src/auteur/beginner/browser/studio_full_architecture.js | Existing derived full-architecture read view; reuse where sufficient |

### Focused additions proposed for demonstrated gaps

| Proposed file | Single responsibility |
| --- | --- |
| src/auteur/beginner/studio_ontology_context.py | Deterministic, bounded, source-referenced relevant ontology definitions for an agent request |
| src/auteur/beginner/studio_architecture_review.py | Human-readable, deterministic before/after review projection, not invented agent rationale |
| src/auteur/beginner/browser/studio_architecture_reader.js | Readable architecture overview from the existing candidate, no new owner |
| src/auteur/beginner/studio_concepts.py | Validated **provisional project notes** using CanvasStore, not a universal ontology |
| tests/test_beginner_studio_ontology_context.py | Context relevance and provenance |
| tests/test_beginner_studio_architecture_review.py | Review diff/explanation behavior |
| tests/test_beginner_studio_architecture_resume.py | Cross-process and cross-agent re-entry contract |
| tests/test_beginner_studio_concepts.py | Provisional concept persistence/authority |
| tests/test_studio_architecture_reader.mjs | Plain-language projection, empty state, safe strings |
| docs/reviews/2026-11-03-agent-first-architecture-evidence.md | Actual run receipts, measured scope, blockers and qualification ceiling |

Keep existing tests/test_beginner_studio_architecture.py, tests/test_beginner_studio_architecture_browser.py, tests/test_beginner_studio_reentry.py, tests/test_host_agent_handoff.py and tests/auteur/narrative_ontology/test_ontology_loader.py as regression suites. Avoid a new module if an existing file is genuinely the smaller ownership boundary.

### Execution order

**Evidence baseline -> ontology context -> freshness distinction -> generation/revision behavior -> review explanation -> readable author view -> re-entry -> provisional concept evolution -> authentic qualification.**

A task may conclude **NO CHANGE REQUIRED** when a working, testable capability already satisfies it. Record the evidence; do not write gratuitous code. Each new capability must work without waiting for all later tasks.

## Task 0 — Establish a runnable and honest baseline

**Files:** Create docs/reviews/2026-11-03-agent-first-architecture-evidence.md; read STATUS.md, issue #504, MISSION.md, current spec and the existing architecture tests. No product change.

**Interfaces:** Consumes the existing Studio Architecture bridge. Produces a baseline matrix of observed/missing/unverified spec behaviors and an environment capability receipt for later tasks.

- [ ] **Step 1: Verify a real checkout.** Run:
  ~~~bash
  git rev-parse --show-toplevel
  git rev-parse HEAD
  git status --short
  python -m pytest tests/test_beginner_studio_architecture.py tests/test_host_agent_handoff.py -q
  node --test tests/test_studio_full_architecture.mjs
  ~~~
  Record actual commands and exit codes. If not inside a runnable checkout, stop execution and record HOST_AGENT_EXECUTION_UNAVAILABLE or CHECKOUT_UNAVAILABLE; connector inspection is not a substitute.
- [ ] **Step 2: Create a disposable local canvas and noncanonical Story Vision.** Use the existing CanvasStore commands from tests/test_beginner_studio_story_vision.py, never a production author project.
- [ ] **Step 3: Prepare and inspect one exact request.** Run python -m auteur.beginner.studio_architecture --project <scratch> --canvas <id> prepare. Save request SHA, existing context sources and whether the active coding agent shares the scratch filesystem.
- [ ] **Step 4: If a real coding agent is available, ask that agent to fulfill the exact saved HostAgentRequest**, capture its raw schema-v2 response, and run complete-file; otherwise record BLOCKED BEFORE LIVE GENERATION with no synthetic substitute.
- [ ] **Step 5: Write the evidence matrix.** Distinguish supported-by-source, mechanics-tested, host-agent-observed and human-judged. Commit the receipt. Proceed with deterministic code tasks only when a full checkout exists; postpone claims requiring unavailable live execution.

**Check:** No accepted story artifact changed; no claim of an executed agent unless an exact request/response pair was preserved.

## Task 1 — Deliver relevant ontology meanings, not just their filenames

**Files:** Create src/auteur/beginner/studio_ontology_context.py and tests/test_beginner_studio_ontology_context.py; modify src/auteur/beginner/studio_architecture.py around _narrative_design_context (approximately lines 294–417) and existing context test in tests/test_beginner_studio_architecture.py.

**Interfaces:** Produces build_relevant_ontology_context(vision: str, accepted_identity: dict | None) -> dict. Return a bounded JSON-compatible dictionary with authority="derived_ontology_guidance", source_refs, concepts with name/definition/relationships, and explicit selection rationale. Existing _narrative_design_context(store: CanvasStore) includes it as a nested optional field in new requests; preserve legacy readers.

- [ ] **Step 1: Write the failing tests.** Assert that the generated request contains actual accepted definitions and relationship directions for Theme, Conflict, Arc, Setup, Payoff, Revelation and Reversal from OntologyLoader, not only source-path strings. Test a sparse Story Vision and an explicit mystery genre separately. Assert that unsupported genres do not manufacture a package extension or author preference, and that omitted manuscript content remains explicitly omitted.
- [ ] **Step 2: Run tests and observe a relevant failure.** Run python -m pytest tests/test_beginner_studio_ontology_context.py tests/test_beginner_studio_architecture.py::test_architecture_request_carries_source_grounded_ontology_not_hidden_author_choices -q.
- [ ] **Step 3: Implement the minimal context builder.** Read packaged ontology through OntologyLoader; always select the bounded foundational relationship vocabulary and optionally add explicitly applicable, installed genre definitions. Keep the existing curated cross-layer design principles and separate accepted Identity source. Never parse random repository docs or put a full raw ontology dump into every request.
- [ ] **Step 4: Verify the new request's context is bounded, inspectable and semantically attributed.** Run the targeted tests and python -m pytest tests/auteur/narrative_ontology/test_ontology_loader.py -q. Record selected source refs in the request.
- [ ] **Step 5: Commit the context builder and its tests.** Do not change ArchitectureCandidate schema version or canonical ontology files.

**Success:** A fresh coding agent can see meaningful narrative definitions and relationships within the request itself, even if its host has not separately loaded AGENTS.md.

## Task 2 — Separate author-source freshness from ontology-guidance evolution

**Files:** Modify src/auteur/beginner/studio_architecture.py around _source_fingerprint, prepare_architecture, complete_architecture, apply_architecture_review and project_architecture (approximately lines 418–680); modify tests/test_beginner_studio_architecture.py; adjust status in src/auteur/beginner/browser/studio.js.

**Interfaces:** Preserve _source_fingerprint(store, request_user) -> str for historical packet formats. New request settings contain freshness_format=2, source_sha256 (author source and accepted Identity), and design_guidance_sha256 (derived context). project_architecture gains status="guidance_changed" when only generation guidance changed; retain ready/awaiting_host_agent/review_ready/stale/not_started.

- [ ] **Step 1: Write failing compatibility and freshness tests.** Existing pre-context and source-format-1 requests retain exact legacy digest. For new requests, modifying Story Vision or accepted Identity yields stale; modifying _DESIGN_PRINCIPLES or selected ontology definitions while holding author input fixed yields guidance_changed, not a false claim that the author edited the story. Wrong-request, duplicate and superseded responses must not mutate current.json.
- [ ] **Step 2: Run the targeted tests and observe failures.** Run python -m pytest tests/test_beginner_studio_architecture.py -q.
- [ ] **Step 3: Implement versioned freshness semantics in the existing architecture owner.** Use a request-user format marker to preserve old _source_fingerprint behavior; for new requests calculate author inputs and derived guidance separately while retaining request_sha256 binding to the exact packet. Reject/review responses whose relevant current sources no longer match; retain stale responses as inspectable evidence. Do not silently rewrite historical fingerprints.
- [ ] **Step 4: Make the Studio status explicit.** Show "Narrative design guidance changed; review or regenerate" for guidance_changed, and keep "Story Vision changed" only for actual author-input changes. Run targeted tests and existing browser/static status checks.
- [ ] **Step 5: Commit.** Record the compatibility rule and why source and ontology changes are distinct.

**Success:** A continuing agent can tell which conceptual framework a candidate used without treating an ontology upgrade as if the author changed their story.

## Task 3 — Enforce complete-first and holistic-revision behavior at the existing request boundary

**Files:** Modify _SYSTEM in src/auteur/beginner/studio_architecture.py only when the Task 0 request/real trace or the approved spec exposes a demonstrable missing rule; add precise tests to tests/test_beginner_studio_architecture.py and a small adversarial fixture in tests/fixtures only if needed.

**Interfaces:** Existing prepare_architecture(store: CanvasStore, instruction: str = "") -> dict; no new provider, request mode, mandatory question route or second candidate type.

- [ ] **Step 1: Add focused contract tests.** For first generation, an empty revision instruction still stages one whole-story candidate request requiring emotional promise, functional tropes, meaningful genre/structure/engine relationships and explicitly labeled provisional choices. For revision, the exact instruction and existing candidate appear together; prompt requires reconsideration of materially affected facets, stable IDs where possible, preserved accepted constraints and no invented concrete scenes. Test a short Vision that does not justify an asserted genre and a conflicting accepted Identity.
- [ ] **Step 2: Run tests to identify whether any required behavior is missing.** Run python -m pytest tests/test_beginner_studio_architecture.py -q; read the exact prepared system/user messages instead of inferring host context.
- [ ] **Step 3: Make the smallest prompt or context clarification that fixes proven gaps.** Keep candidate schema_version=2; use existing summary, node explanations, links, genre_contracts, phases and open_questions. Never require an author questionnaire or promise semantic quality from JSON validity. Do not change a schema merely to encode an untested hypothesis.
- [ ] **Step 4: Re-run the focused tests.** If a real host agent is available, inspect one first proposal and one revised proposal for causal coherence, revision breadth and preserved constraints; record observations rather than numerical quality scores.
- [ ] **Step 5: Commit the smallest defensible change, or record NO CHANGE REQUIRED** with an evidence reference.

**Success:** The agent request expresses the approved experience and the actual response can be evaluated, not merely parsed.

## Task 4 — Make holistic revisions reviewable without inventing explanations

**Files:** Create src/auteur/beginner/studio_architecture_review.py and tests/test_beginner_studio_architecture_review.py; modify the revision branch of complete_architecture in src/auteur/beginner/studio_architecture.py. Maintain the existing _candidate_diff result and review.json reading.

**Interfaces:** Produces build_architecture_review(previous: dict, proposed: dict, instruction: str) -> dict. Include requested_change, the existing grouped ID diff, changed_components with title/category/before/after summaries, preserved IDs or counts, and a clearly labeled proposed_rationale sourced from candidate.summary (never fabricated by the comparator). Existing review["candidate"] remains intact.

- [ ] **Step 1: Write failing review tests.** Given a change to intended emotion, a narrative engine, genre interaction and phase, check that the review names each affected component and shows before/after meaning, not just IDs. Confirm explicitly author-declared emotion targets and accepted constraints remain visible as preserved where their provenance is actually known, and that the exact instruction is shown. Do not infer author declarations for generic nodes that lack provenance. A missing rationale must be labeled missing, not invented.
- [ ] **Step 2: Run the failing tests.** Run python -m pytest tests/test_beginner_studio_architecture_review.py -q.
- [ ] **Step 3: Implement a deterministic semantic-field projection.** Reuse _candidate_diff and candidate text; do not infer causality from mere JSON differences. New review metadata is optional for reading old review.json artifacts. Apply still uses the existing locked apply_architecture_review authority/staleness checks.
- [ ] **Step 4: Verify legacy, stale, conflicting and duplicate reply behavior.** Run python -m pytest tests/test_beginner_studio_architecture_review.py tests/test_beginner_studio_architecture.py -q. Inspect that accepted story files are untouched.
- [ ] **Step 5: Commit.**

**Success:** The author can see the proposed coordinated changes, preserved choices and stated reasoning before applying a revision to the working candidate.

## Task 5 — Put a readable architecture ahead of graph manipulation

**Files:** Create src/auteur/beginner/browser/studio_architecture_reader.js and tests/test_studio_architecture_reader.mjs; modify src/auteur/beginner/browser/studio.html, studio.js and small scoped styles in studio.css; extend tests/test_beginner_studio_architecture_browser.py.

**Interfaces:** Expose window.AuteurStudioArchitectureReader.project(candidate) -> {summary, emotions, genres, tropes, structure, mechanisms, relationships, uncertainties}, and render(root, projection) -> void. In studio.js call it from applyArchitectureProjection using the **existing** candidate and status. The graph remains available through the current controls.

- [ ] **Step 1: Write failing pure JS tests.** Assert a v2 candidate projects governing/supporting emotion targets, functional trope choices, abstract structure/phases, a bounded set of relationships, uncertainties and "working proposal" authority. Empty candidate shows a truthful empty state. Hostile strings appear as text, never HTML or links. Run node --test tests/test_studio_architecture_reader.mjs and observe failure.
- [ ] **Step 2: Add the minimal reader projection and accessible markup.** Keep the graph and existing Full Architecture component intact. Expose a readable text-first overview after a completed candidate; do not force a graph-only first view or require six facet clicks before understanding a design.
- [ ] **Step 3: Connect revision display.** Render Task 4's requested change, changed meanings, preserved decisions and provisional rationale in the existing architecture-review section. Keep Apply explicitly working-only.
- [ ] **Step 4: Run changed JS and Studio tests.** Run node --test tests/test_studio_architecture_reader.mjs tests/test_studio_full_architecture.mjs and python -m pytest tests/test_beginner_studio_architecture_browser.py tests/test_beginner_studio_semantic_encoding.py -q. In a runnable browser, check keyboard reading order, mobile width, pending-state fidelity and graph fallback.
- [ ] **Step 5: Commit.**

**Success:** A new author can read and critique a generated architecture without understanding the graph UI or its ontology field names.

## Task 6 — Provide a source-honest, read-only re-entry packet for any coding agent

**Files:** Modify src/auteur/beginner/studio_architecture.py; create tests/test_beginner_studio_architecture_resume.py. Reuse CanvasStore, _source and project_architecture; no new persistence platform.

**Interfaces:** Produces project_architecture_resume(store: CanvasStore) -> dict. Add a "resume" action to existing python -m auteur.beginner.studio_architecture CLI (keeping prepare/show/complete-file unchanged). Include canvas_id, current Story Vision, current architecture and status, source request SHA, exact available ontology guidance refs, accepted_story_identity only when present, pending review/unknowns, bounded source visibility/omission metadata and any provisional project concept notes from Task 7. Never include fabricated readable text in place of omitted working items.

- [ ] **Step 1: Write failing re-entry tests.** Create a local canvas, Story Vision and valid v2 candidate through existing public functions. Instantiate a new CanvasStore and verify the same proposal/authority/SHAs and source visibility can be recovered. Verify absent Identity stays None; response from another canvas does not appear. Test that a new CLI invocation with resume emits machine-readable packet without altering files.
- [ ] **Step 2: Run python -m pytest tests/test_beginner_studio_architecture_resume.py -q** and observe the missing interface.
- [ ] **Step 3: Implement the read-only packet and CLI action.** Use existing source projection and candidate pointers, not chat history or a second story bible. Bound working material using existing excerpt/omission rules. Explicitly label the packet "working / noncanonical".
- [ ] **Step 4: Run re-entry and existing tests.** Run python -m pytest tests/test_beginner_studio_architecture_resume.py tests/test_beginner_studio_reentry.py tests/test_beginner_studio_story_vision.py -q.
- [ ] **Step 5: Commit.** Document the CLI invocation and how a new host agent reads it.

**Success:** A newly started agent can reconstruct the relevant working creative context from project state rather than relying on previous conversation memory.

## Task 7 — Preserve provisional narrative discoveries without modifying shared ontology

**Files:** Create src/auteur/beginner/studio_concepts.py and tests/test_beginner_studio_concepts.py; add optional provisional concept reporting to project_architecture_resume in src/auteur/beginner/studio_architecture.py. Do **not** modify data/ontology/*.yaml or src/auteur/data/ontology/*.yaml as a side effect.

**Interfaces:** Define ProvisionalNarrativeConcept(BaseModel) with name: str, definition: str, motivating_story_use: str, why_existing_concepts_insufficient: str, related_concepts: list[str], proposed_relations: list[str], compatibility_concerns: list[str], and status: Literal["provisional"] = "provisional". Provide record_provisional_concept(store: CanvasStore, concept: ProvisionalNarrativeConcept, *, expected_revision: int, command_id: str) -> WorkingCanvas and list_provisional_concepts(store: CanvasStore) -> list[ProvisionalNarrativeConcept]. Back these with CanvasStore's existing noncanonical note kind, in a clearly identified provisional-concepts group; no new canonical store. The note is also the **reviewable proposed extension**: it records why existing vocabulary is insufficient, suggested relationships and compatibility concerns. If necessary for the active agent's workflow, expose a single CLI action "record-concept" with a JSON file argument.

- [ ] **Step 1: Write failing tests.** A project-level provisional concept, including its proposed relationships and compatibility concerns, is readable for author review after a fresh-process reload and appears in resume, with its provenance clearly distinct from accepted ontology; duplicate command ID is idempotent; conflicting revision and invalid structure do not overwrite earlier working material. Check that neither canonical Story Identity nor packaged ontology files change.
- [ ] **Step 2: Run python -m pytest tests/test_beginner_studio_concepts.py tests/test_beginner_studio_architecture_resume.py -q** and observe failure.
- [ ] **Step 3: Implement the smallest working-note adapter.** Existing ontology definitions must be checked for possible equivalence in the proposed rationale; software cannot deterministically prove semantic novelty, so absence of duplicates remains a review judgment. Do not add proposed terms to global loader resolution until separately accepted by the author.
- [ ] **Step 4: Verify that new request/re-entry context identifies provisional concepts without treating them as author commitments.** Keep bounded excerpts and omitted counts honest if a large project exceeds context limits; run the focused tests, the ontology loader tests and stale-source tests.
- [ ] **Step 5: Commit.** Document that shared ontology promotion is a distinct author-reviewed repository change and that rejected proposals remain historical project notes, not approved general concepts.

**Success:** A useful new concept survives agent replacement, can influence the same working story provisionally, and cannot silently redefine common narrative vocabulary.

## Task 8 — Real journey, authority audit and acceptance evidence

**Files:** Modify only the evidence receipt docs/reviews/2026-11-03-agent-first-architecture-evidence.md and focused tests revealed by an observed defect. Do not create another orchestration subsystem to fake an agent.

**Interfaces:** Consumes the completed Tasks 1–7, the existing host-agent CLI, the Studio UI and a disposable author project. Produces a reproducible observation record and an exact remaining-blocker list.

- [ ] **Step 1: Run the changed-code gates.**
  ~~~bash
  python -m pytest tests/test_beginner_studio_architecture.py tests/test_beginner_studio_ontology_context.py tests/test_beginner_studio_architecture_review.py tests/test_beginner_studio_architecture_resume.py tests/test_beginner_studio_concepts.py tests/test_beginner_studio_reentry.py tests/test_host_agent_handoff.py -q
  node --test tests/test_studio_architecture_reader.mjs tests/test_studio_full_architecture.mjs
  ~~~
  Add the direct HTTP/Browser tests affected by actual edits, not unrelated broad suites by default. Record actual exit codes.
- [ ] **Step 2: Use a real active coding agent with an original noncanonical Story Vision.** Stage one request, answer the **exact** saved packet, complete the response through the existing boundary, and inspect a full abstract candidate. Include an intentionally sparse Vision and bounded hidden excerpt case; distinguish invented claims from provisional decisions.
- [ ] **Step 3: Ask for one holistic change:** "Make wonder dominate fear, preserve mystery and accepted hard constraints." Check whether consequences are considered across emotion, structure, genre and trope functions, and whether the review accurately identifies preserved choices. Do not count a valid JSON object as a literary pass.
- [ ] **Step 4: Restart with a distinct coding-agent session or runtime.** Recover the project using resume, revise without asking the author to repeat established constraints, and propose/reuse one provisional concept. Verify the shared ontology remains unchanged without separate review.
- [ ] **Step 5: Audit the source and write the final evidence receipt.** Include exact packet IDs/SHAs, agent/runtime, source files actually seen, commands, code/test outcomes, rejected/stale response behavior, noncanonical state checks, observations of comprehension and unresolved judgments. When the true host or Browser is unavailable, write the blocker, not a fabricated success, and preserve a precise next invocation.
- [ ] **Step 6: Commit evidence, reconcile STATUS.md or issue #504 only if their verified factual state changed, and request author review of the working behavior.** Do not claim product/UX qualification from simulated author or synthetic candidate fixtures.

**Success:** Demonstrated, source-auditable first generation -> holistic working revision -> fresh-agent continuation -> provisional concept reuse, or an explicit boundary with no false claim of completion.

## 9. Self-review: scope, ordering and proportion

| Spec requirement | Implementing task / evidence |
| --- | --- |
| Complete first proposal without interview | Task 0 baseline; Task 3 request contract; Task 8 real generation |
| Rich emotions, tropes, structure, mechanisms and relations | Task 1 definitions; Task 3 candidate contract; Task 5 readable projection; Task 8 qualitative examination |
| Holistic conversational revision with preserved constraints | Task 3 revision prompt; Task 4 comparison; Task 8 real revision |
| Repository-grounded ontology definitions | Task 1 |
| Distinguish accepted, author-declared, proposed, unknown | Tasks 1–5; Task 8 |
| Cross-session and cross-agent recoverability | Task 6; Task 8 |
| Provisional concepts and reviewed ontology evolution | Task 7; Task 8 |
| Honest request/response, no false host execution | Tasks 0, 2, 8 |
| No new story canon, no auto-accept | Global Constraints; tests in Tasks 2, 4, 6, 7, 8 |
| Graph optional for authoring; readable review | Task 5; Task 8 |
| Historical compatibility | Task 2 plus existing regression suite |

### Important design decisions left with the executor

The proposed module names/signatures make task ownership and tests concrete; a coding agent may identify a strictly smaller equivalent within existing owners, but must document that substitution and preserve observable interfaces. Choosing new libraries, provider integrations, a universal knowledge graph, new user authentication or a schema-v3 migration is **not authorized** by this plan. If a genuinely different ontology or authority owner becomes necessary, pause that specific change and document why the existing contract is inadequate.

No task authorizes changing the author-approved experience to a questionnaire-first flow. No task authorizes hidden story-acceptance or accepting an ontology extension just because the model returned it.

## Execution handoff

**Recommended method: Subagent-driven,** because ontology/freshness, review UI, provisional storage and real-agent qualification have different failure modes and benefit from fresh specialist review. Preserve source-level boundaries between author intent and derived guidance.

Before implementing, the executor should fetch the current main, read the approved spec, this plan, MISSION.md, STATUS.md and #504, and use the smallest per-task test gate. If the tool environment cannot provide a runnable checkout, leave an actionable blocker receipt rather than implement from an invented runtime.

### Three execution axioms

1. It is **not** a tool for manually assembling a graph; it is **actually** an agent-directed architecture design process.
2. It is **not** a transcript and is **not** a frozen dictionary; it is **actually** a durable, reviewable conceptual contract.
3. Creative continuity is **actually** ontology-grounded reasoning that survives the agent who first performed it.
