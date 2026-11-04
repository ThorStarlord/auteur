# Agent-First, Ontology-Grounded Narrative Architecture — Execution Evidence

**Execution date:** 2026-11-04 (America/Argentina/Buenos_Aires)  
**Executor:** Inline coding agent, no implementation/research/review/testing subagents  
**Plan:** [Agent-First, Ontology-Grounded Narrative Architecture](../superpowers/plans/2026-11-03-agent-first-ontology-grounded-narrative-architecture.md)  
**Spec:** [Approved design brief](../superpowers/specs/2026-11-03-agent-first-ontology-grounded-narrative-architecture-design.md)  
**Disposition:** **IMPLEMENTED FOR THE AUTHORIZED SCOPE; FOCUSED AND BEGINNER-WIDE TESTS PASS; FULL SUITE HAS 15 KNOWN BASELINE FAILURES; AUTHENTIC INLINE HOST-AGENT JOURNEYS AND A REAL CHROMIUM UI CHECK WERE OBSERVED.** This is not human-author qualification, literary-quality qualification, release qualification, or installed-artifact qualification.

The prior revision of this file recorded a blocked execution caused by `CHECKOUT_UNAVAILABLE` in a different runtime. That blocker did not reproduce in this local checkout: the executor could read and write the same disposable project files as the Auteur CLI. The prior blocked receipt remains in Git history.

## 1. Environment and repository identity

| Check | Observed |
| --- | --- |
| Workspace root | `H:/GithubRepositories/auteur` |
| Git common directory | `.git` (standalone checkout, not a linked worktree) |
| Branch | `feat/agent-first-ontology-grounded-architecture-20261103` |
| Reconciled base | `main @ 74539efe1a521f1ca74390dcf64664e6b4362caf` |
| Python | 3.14.3 |
| Node | v24.14.1 |
| Git | 2.51.0.windows.1 |
| OS | Microsoft Windows 10 Home Single Language 10.0.19045 |
| PowerShell | 5.1.19041.6456 |
| Host-agent filesystem | Shared: the active coding agent created and fulfilled requests in the same disposable project directory used by the Auteur CLI |
| Browser runtime | Playwright Chromium from the local `ms-playwright` cache; local loopback only |

No production author project, accepted Story Identity, blueprint, or shared ontology resource was used as a test fixture.

## 2. Baseline matrix

The baseline was measured before implementation on the reconciled `origin/main` source.

| Required behavior | Baseline finding | Implementation disposition |
| --- | --- | --- |
| Relevant ontology meanings, not filenames | Requests carried curated principles and a `data/ontology/base_ontology.yaml` reference, but no actual concept definitions or relationship directions. | **Implemented** in `studio_ontology_context.py`; new requests carry bounded definitions for 12 foundational concepts and explicit genre extensions. |
| Author-source versus guidance freshness | One combined fingerprint treated a guidance change as if the author changed the story. | **Implemented** with `freshness_format: 2`, separate `source_sha256`, `design_guidance_sha256`, and `guidance_changed` status. Legacy packet digests remain readable. |
| Complete first proposal without interview | The prompt already encouraged provisional defaults, but did not explicitly require a complete proposal without an interview or holistic revision breadth. | **Implemented** in the existing request contract; no schema change. |
| Holistic revision review | The review showed grouped IDs only. | **Implemented** in `studio_architecture_review.py` with changed meanings, preserved author-declared emotions, accepted constraints, and the candidate's own stated rationale. |
| Readable architecture before the graph | The browser exposed facets and a graph; there was no text-first overview generated from the candidate. | **Implemented** in `studio_architecture_reader.js`, wired into the existing Studio surface. |
| Cross-session/agent re-entry | Startup recovered canvases, but there was no source-honest resume packet. | **Implemented** as `project_architecture_resume` plus a `resume` CLI action. |
| Provisional concept continuity | No project-scoped provisional concept storage existed. | **Implemented** in `studio_concepts.py` using CanvasStore notes in a `provisional-concepts` group. |
| Honest host execution | The bridge already refused to fake a provider call. | **Preserved and exercised** with exact request/response packets. |

## 3. Task ledger

| Plan task | Status | Evidence |
| --- | --- | --- |
| Task 0 — runnable and honest baseline | **COMPLETE** | Checkout, tools, focused baseline (32 passed), Node baseline (8 passed), disposable canvas, exact request SHA recorded. |
| Task 1 — ontology meanings | **COMPLETE** | `studio_ontology_context.py`; 7 focused tests; request contains 16 concepts for the rich Vision. |
| Task 2 — story/guidance freshness | **COMPLETE** | `freshness_format: 2`; legacy digest tests; `guidance_changed` status; browser status text. |
| Task 3 — complete-first/holistic request | **COMPLETE** | Contract tests for complete-first, holistic revision, sparse Vision, accepted-identity conflict. |
| Task 4 — reviewable holistic revision | **COMPLETE** | Deterministic review projection; 8 focused tests; no invented rationale. |
| Task 5 — readable author view | **COMPLETE** | `studio_architecture_reader.js`; 5 pure JS tests; real Chromium desktop/mobile/pending/graph checks. |
| Task 6 — cross-agent resume | **COMPLETE** | 6 focused tests; fresh-process CLI resume; read-only file snapshot check. |
| Task 7 — provisional concepts | **COMPLETE** | 8 focused tests; CLI record-concept; resume inclusion; canonical ontology hash unchanged. |
| Task 8 — real journey/evidence | **COMPLETE WITH STATED EVIDENCE CEILING** | Rich and sparse authentic packet fulfillment, holistic revision, fresh-process resume, concept reuse, browser check, full-suite classification. |

## 4. Authentic inline host-agent journeys

The active coding agent read each exact saved `HostAgentRequest` and supplied the schema-v2 candidate through the existing `complete-file` boundary. Responses were not generated from a test fixture. They were produced by the same agent session executing this plan; no independent second model/runtime was launched.

### 4.1 Rich Vision → complete architecture

| Item | Observed |
| --- | --- |
| Request SHA-256 | `c6269dc2e1953498ced08c1e32fa10b4d7bf05274e72c6214bd8b1f5074b5d66` |
| Candidate ID | `studio-e6a7af38c0095650b777c06c` |
| Author-source SHA-256 | `6ec3e250ba15fea5c47725a8083f9f231a8628235b5a79012fd642069a18baf0` |
| Design-guidance SHA-256 | `df6d5adc303abb96c19f65f5f9e3330e0802d1fc1c7cb6db04d42e15af1160b0` |
| Ontology refs | `auteur.data.ontology:base_ontology.yaml`, `auteur.data.ontology:mystery_ontology.yaml` |
| Concepts in request | 16 |
| User packet size | 13,635 UTF-8 bytes |
| Result | `ready`; 18 nodes, 18 links, 4 phases, 3 genre contracts, 4 genre interactions |

Artifacts: [request](../qualification-evidence/agent-first-ontology-20261103/rich-vision-request.json), [raw response](../qualification-evidence/agent-first-ontology-20261103/rich-vision-response.json), [candidate](../qualification-evidence/agent-first-ontology-20261103/rich-vision-architecture.json), [settings receipt](../qualification-evidence/agent-first-ontology-20261103/rich-vision-guide.json).

The candidate covered the governing wonder/dread/hope progression, three genre roles and typed interactions, functional tropes, a memory-economy engine, four structural phases, and meaningful relationships among those systems. Author-declared emotions (`wonder`, `dread`, `hope`) were marked `author_declared`; other emotional targets were marked `agent_proposed`. It invented no cast, scene, or plotted event. This is a structural/comprehension observation, not a literary-quality score.

### 4.2 Holistic revision

Instruction:

> Make wonder dominate fear while preserving mystery, the founding crime, and the partial-record ending. Keep the intimate cost but let it sharpen wonder rather than replace it.

| Item | Observed |
| --- | --- |
| Request SHA-256 | `a21de02d6b7622d43e50e7d9b1e1023b5d8f21c5441fa88a1652d608abfad52d` |
| Prior candidate included in packet | Yes |
| Review status | `review_ready` |
| Changed components | 19 (summary, 4 phases, 3 nodes, 3 emotion targets, 2 complex emotions, 3 genre contracts, 3 genre interactions) |
| Author-declared preserved | `hope` |
| Author-declared changed | `wonder` (intended effect and eliciting condition), `dread` (role and intended effect) |
| Stated rationale | Provided from `candidate.summary`; the comparator invented none |
| Applied | `ready`; working architecture replaced only after explicit review apply |
| Canonical story files | None created |

Artifacts: [request](../qualification-evidence/agent-first-ontology-20261103/revision-request.json), [review](../qualification-evidence/agent-first-ontology-20261103/revision-review.json), [revised candidate](../qualification-evidence/agent-first-ontology-20261103/rich-vision-revised-candidate.json), [applied architecture](../qualification-evidence/agent-first-ontology-20261103/applied-architecture.json).

The review named every materially affected component with before/after meaning. It did not infer causality from JSON differences; the only rationale is the agent's own candidate summary. The changed author-declared emotion meanings remained visible rather than being silently reported as preserved.

### 4.3 Fresh-process continuation and provisional concept

A new CLI process invoked `resume`; it recovered the applied architecture, its request SHA, the exact ontology guidance used by that request, the four open author decisions, and the source-visibility metadata. It did not mutate any file.

The provisional concept [Memory Cartography](../qualification-evidence/agent-first-ontology-20261103/provisional-concept-memory-cartography.json) was then recorded through the CLI. Result:

- status `provisional`, authority `working_noncanonical`;
- stored as a working note in group `provisional-concepts`, not in a new canonical store;
- all four packaged ontology files retained byte-identical SHA-256 hashes;
- no `story_identity.yaml`, `blueprint.yaml`, or accepted ontology change existed;
- the next fresh-process `resume` included the concept.

This journey exposed a consequential freshness defect: recording an agent-proposed concept initially marked the author's architecture `stale`. The owning boundary was repaired so provisional concept notes are excluded from the author-source fingerprint and do not displace the bounded 24 author-working-item projection. Regression tests cover both behaviors.

Artifacts: [resume before concept](../qualification-evidence/agent-first-ontology-20261103/resume-before-concept.json), [record output](../qualification-evidence/agent-first-ontology-20261103/record-concept-output.json), [resume with concept](../qualification-evidence/agent-first-ontology-20261103/resume-with-concept.json).

### 4.4 Concept-aware continuation revision

A subsequent revision explicitly reused the provisional concept:

> Use the provisional concept Memory Cartography to make the map cost more concrete, while preserving wonder dominance, mystery, and the partial-record ending.

| Item | Observed |
| --- | --- |
| Request SHA-256 | `8651419929dda105d79956a0a6c0c8ed76874aa0462983231fcabf2814c02ca0` |
| Concept note in request | Yes, in the `provisional-concepts` working group |
| Review | `review_ready`; one added node, two added links, one changed genre contract, changed summary |
| Author-declared preserved | `wonder`, `dread`, `hope` |
| Applied | `ready`; the new architecture includes `memory_cartography` |
| Shared ontology | Unchanged |

Artifacts: [request](../qualification-evidence/agent-first-ontology-20261103/concept-revision-request.json), [review](../qualification-evidence/agent-first-ontology-20261103/concept-revision-review.json), [candidate](../qualification-evidence/agent-first-ontology-20261103/concept-revision-candidate.json), [applied](../qualification-evidence/agent-first-ontology-20261103/concept-revision-applied.json), [final resume](../qualification-evidence/agent-first-ontology-20261103/resume-final.json).

### 4.5 Sparse Vision and hidden excerpt

A second disposable canvas used a sparse Vision and 25 working manuscript items, one longer than the 1,000-character excerpt limit.

| Item | Observed |
| --- | --- |
| Request SHA-256 | `38360e093b3722405bba70eed257d14d7ef64d031a834076704ba8d13a687c82` |
| Genre extensions | None; only `base_ontology.yaml` |
| Author working items | 24 visible, 1 omitted |
| First item | Excerpt of 1,181 characters with a SHA-256 of the full text |
| Result | `ready`; 8 nodes, 4 phases, 0 genre contracts, 0 genre interactions |
| Genre handling | Explicitly left unknown; the candidate has no genre node or genre contract and asks the author for the framing genre |
| Invented cast/events | None |

Artifacts: [request](../qualification-evidence/agent-first-ontology-20261103/sparse-vision-request.json), [raw response](../qualification-evidence/agent-first-ontology-20261103/sparse-vision-response.json), [candidate](../qualification-evidence/agent-first-ontology-20261103/sparse-vision-architecture.json), [visibility receipt](../qualification-evidence/agent-first-ontology-20261103/sparse-vision-guide.json).

### 4.6 Real Chromium UI check

A local Auteur server was started on loopback and exercised with Playwright Chromium against the disposable project. This was an automated browser check, not a human usability or screen-reader audit.

| Check | Observed |
| --- | --- |
| Desktop reader | Visible before the graph viewport; contains title, authority label, emotional promise, genres, tropes, structure, mechanisms, relationships, and open questions; 8 headings |
| Desktop status | `Agent proposal ready · working, not accepted story.` |
| Mobile width (390×844) | Reader visible; no horizontal overflow (`scrollWidth == clientWidth`; body overflow 0) |
| Pending canvas | Reader hidden; status `Awaiting the active coding agent...`; no false `Agent proposal ready` claim |
| Graph fallback | Viewport visible; Full Architecture view opens; no console or page errors |
| Console errors | None |

Receipt: [browser-qualification.json](../qualification-evidence/agent-first-ontology-20261103/browser-qualification.json).

## 5. Source and authority audit

- The disposable project ended with no `story_identity.yaml` and no `blueprint.yaml`.
- No accepted Story Identity, Structure, Realization, Expression, or shared ontology resource was created or modified.
- The four packaged ontology files were byte-identical before and after provisional-concept recording.
- Working architecture changes remained in the canvas architecture directory until an explicit `apply` action.
- The review record is a comparison, not a story-impact or acceptance record.
- The provisional concept is project-scoped and remains `provisional`; a separate author-reviewed repository change is still required for shared ontology promotion.
- The resume packet is read-only and labels itself `working_noncanonical`.

## 6. Test and verification record

| Gate | Command (abridged) | Result |
| --- | --- | --- |
| Baseline focused | `pytest tests/test_beginner_studio_architecture.py tests/test_host_agent_handoff.py` | **32 passed** |
| Baseline Node | `node --test tests/test_studio_full_architecture.mjs` | **8 passed** |
| Changed-code focused | 7 architecture/ontology/review/resume/concepts/reentry/host-agent files | **73 passed** |
| Beginner-wide | all `tests/test_beginner_*.py` + `tests/test_host_agent_handoff.py` | **620 tests, 0 failed, 0 errors, 1 skipped** |
| Node Studio suite excluding known baseline failure | all `tests/test_studio_*.mjs` except Quick Draft session freshness | **126 passed** |
| Verification stack | `python scripts/check.py --skip-pytest --ruff-paths <changed paths>` | **passed** (repo validators and Ruff) |
| Full Python suite | `python -m pytest -q --tb=no --junitxml=...` | **5,701 tests, 5,684 passed, 15 failed, 2 skipped, 0 errors** |

The 15 full-suite failures are **known baseline failures**: all 15 reproduced identically on a clean `origin/main @ 74539efe` worktree. They are in Book comparison/recomposition, audit formatting, dashboard/workspace attention, expression composition, series productization/repeated-focus, story discovery, and story-state formatting. They are not caused by this change and are not fixed here.

The Node failure in `tests/test_studio_quick_draft_session_freshness.mjs` (`renderQuickDraftHandoff is not defined`, 2 failures) is also a known baseline failure: it reproduces identically on `origin/main`. It is unrelated to the changed Studio architecture files.

Exact counts and failure IDs: [test-summary.json](../qualification-evidence/agent-first-ontology-20261103/test-summary.json).

## 7. Technical decisions

1. **Ontology projection, not ontology duplication.** `build_relevant_ontology_context` reads the packaged `OntologyLoader`, emits only definition/relationship fields, always includes the foundational design vocabulary, and adds an installed genre only when the Vision or accepted Identity explicitly names it.
2. **Two freshness dimensions, one request binding.** New requests carry an author-source digest (working material plus accepted Identity) and a derived-guidance digest (principles, ontology projection, preference vocabulary, unknown policy). `request_sha256` still binds the exact packet. Pre-format requests keep their historical combined digest; v1 candidates and old review artifacts remain readable.
3. **Provisional concepts are working notes.** They use the existing `CanvasStore`, not a second persistence platform. They are excluded from author-source freshness and from the 24-item author-source budget, so an agent proposal cannot masquerade as an author edit or displace author manuscript context.
4. **Review is a deterministic projection.** `build_architecture_review` reports observable before/after fields and labels the candidate summary as the only rationale. It does not infer why a change was made.
5. **The readable view is a small browser adapter.** It consumes the existing candidate and exposes a text-first projection; it adds no canonical owner, no provider call, and no acceptance action. The existing graph remains available.
6. **Resume is read-only.** It reconstructs the current working state from repository files, the exact request that produced the candidate, accepted Identity if present, source-visibility metadata, and provisional concepts.

## 8. Evidence ceiling and remaining limitations

- **Same-agent host execution.** The requests were answered by the coding agent executing this plan, inline. This is authentic packet fulfillment, but it is not an independent second model or a distinct coding-agent session. Fresh-process recovery and re-entry were verified; independent-agent continuation remains unobserved.
- **No human author judgment.** Narrative coherence was inspected structurally, not judged by a real author. Comprehension, preference, emotional effect, and literary quality remain unverified.
- **Automated browser check only.** The Chromium run verified layout order, mobile width, pending-state honesty, and graph fallback. It was not a manual keyboard-only or screen-reader audit.
- **Known baseline failures remain.** The full suite is not green because of 15 pre-existing failures; no attempt was made to fix unrelated owners.
- **No release qualification.** No frozen candidate SHA, installed-wheel test, cross-platform release matrix, publication, or release-ready claim was produced.
- **Provisional concept promotion is still manual.** The recorded concept is usable for this project but has not entered the shared ontology and should not be presented as an accepted general definition.

## 9. Ruling and next steps

The authorized implementation plan is implemented and verified within the ceiling above. Focused, beginner-wide, and changed-boundary tests pass; the authentic inline journey exercised generation, holistic revision, review, fresh-process continuation, provisional-concept reuse, sparse Vision honesty, and real browser presentation. The full suite's only failures are known baseline failures reproduced on `origin/main`.

Warranted next steps:

1. Author review of the working behavior and the readable Studio projection.
2. If independent-agent continuity matters, repeat the resume/revision step with a genuinely different coding-agent runtime.
3. Promote any provisional concept only through a separate, author-reviewed ontology change with compatibility analysis.
4. Treat the 15 full-suite failures as a separate baseline-repair program, not as this package's regressions.
