# Agent-Interactive Narrative Graph — Prototype Assessment

**Date:** 2026-11-04  
**Plan:** [Agent-Interactive Narrative Graph Prototype and Evaluation](../superpowers/plans/2026-11-04-agent-interactive-narrative-graph.md)  
**Design:** [Exploration design](../superpowers/specs/2026-11-04-agent-interactive-narrative-graph-design.md)  
**Status:** IN PROGRESS — baseline admitted; prototypes and comparative evidence pending.

This is a prototype and evaluation record. It is not a production integration, release qualification, or claim of human author validation.

## 1. Environment and baseline

| Item | Observed |
| --- | --- |
| Workspace | `H:/GithubRepositories/auteur` |
| Branch | `feat/agent-interactive-graph-prototype-20261104` |
| Base commit | `e8d79988e026c07ec624e38995b71060c6015804` |
| Python | 3.14.3 |
| Node | v24.14.1 |
| OS | Windows 10.0.19045 |
| Baseline Node gate | `node --test tests/test_studio_architecture_reader.mjs tests/test_studio_unfolding_controller.mjs` — **35 passed** |
| Baseline Python browser gate | `python -m pytest tests/test_beginner_studio_architecture_browser.py -q` — **7 passed** |

### Current Studio capability inventory (baseline, not missing features)

| Capability | Existing owner / behavior |
| --- | --- |
| Candidate graph and directed links | `studio.js` architecture nodes, link edges, focus and inspector |
| Narrative perspectives | architecture facets: overview, emotions, genres, tropes, structure, timeline |
| Focused Unfolding | `studio_unfolding.js` / controller: focus-local proposal edges, explicit adoption |
| Architecture inspector | selected candidate component text, source and authority labels |
| Readable architecture overview | `studio_architecture_reader.js`: text-first candidate projection |
| Agent revision handoff | Studio `requestArchitecture` → exact `HostAgentRequest`; prepared vs completed status |
| Working versus accepted authority | working candidate, review, explicit apply; no accepted-story mutation |

The prototype must not relabel these as absent. Its comparison question is whether source-bound semantic interaction adds a **consequential author-task improvement** over this baseline.

## 2. Fixture manifest

| Fixture | Request SHA | Schema | Key identities |
| --- | --- | --- | --- |
| Recorded rich candidate | `c6269dc2e1953498ced08c1e32fa10b4d7bf05274e72c6214bd8b1f5074b5d66` | v2 | node `memory_economy` at `nodes/3`; emotion target `wonder` at `emotion_targets/0`; link `engine_drives_cost` at `links/3`; genre contract `literary_mystery` at `genre_contracts/0`; phase `strange_coast` at `phases/0` |
| Recorded sparse candidate | `38360e093b3722405bba70eed257d14d7ef64d031a834076704ba8d13a687c82` | v2 | no genre nodes or contracts; four phases; four open author questions |
| Dense synthetic fixture | `d…d` (64 `d`) | v2-shaped | **SYNTHETIC STRESS FIXTURE**; not recorded evidence; used only for bounded-focus and density checks |

The rich candidate's `memory_economy` has recorded links to `cost_escalation` and `founding_archive`, and is the target of `magical_map_instantiates`. It has **no recorded relation** to the emotion target `wonder`. That absence is the primary no-inference test case.

## 3. Evidence classes

| Class | What it can establish |
| --- | --- |
| Source inspection | What the candidate and request actually contain |
| Pure model tests | Deterministic identity, relationship, stale, and draft behavior |
| Automated DOM tests | Rendering and event semantics in a controlled fake DOM |
| Served-browser tests | Actual browser layout, keyboard operation, network silence |
| Simulated author tasks | Task completion and friction observed by the executor, not a human study |
| Human author validation | **Not obtained** in this inquiry |
| Independent coding-agent execution | **Not performed** in this inquiry |

## 4. Task ledger

| Task | Status |
| --- | --- |
| 0 — baseline and fixture admission | **COMPLETE** |
| 1 — source-bound semantic projection | **COMPLETE** |
| 2 — graph-to-agent intent grammar | **COMPLETE** |
| 3 — B1 Question-First Semantic Inspector | **COMPLETE** |
| 4 — B2 Component-Aware Intent Workbench | **COMPLETE** |
| 5 — comparative browser evaluation | **COMPLETE** |
| 6 — convergent recommendation | **COMPLETE** |

## 5. Baseline task observations

The current Studio was exercised in a real Chromium session against a disposable project containing the recorded rich candidate. This is the actual served Studio, not a mock.

| Observation | Result |
| --- | --- |
| Readable reader | Shows Memory economy and the emotional promise; **no `nodes/3` or `links/3` sourceRefs** |
| Graph | 18 candidate nodes; one Memory economy node |
| Inspector after selecting Memory economy | Shows meaning, category, `AGENT CANDIDATE / NOT ACCEPTED`, the agent response SHA, and outgoing/incoming relationships in readable prose; **no exact candidate sourceRef** |
| Existing semantic navigation | Emotions facet lists the basic and complex emotional design; genres/tropes/structure/timeline facets remain present |
| Holistic revision handoff | Prepares a real `studio_architecture` request with the exact instruction, previous candidate, and `source_sha256`/`design_guidance_sha256`; **no selected-anchor field** |
| Stale/guidance status | Real `stale` and `guidance_changed` states exist in the current Studio; not simulated |
| Mobile 390px | No horizontal overflow |
| Console | No page or console errors |

The Studio already has a strong inspection/revision surface. The prototype's relevant claim is narrower: exact source references, explicit missing-relation semantics for a selected pair, and an anchor-bound prepared instruction.

## 6. Prototype and comparative results

### B1 — Question-First Semantic Inspector

- Selects real anchors from the source index; the Memory economy anchor exposes `nodes/3` and the relation `engine_drives_cost` exposes `links/3`.
- Selecting a relation opens its recorded direction, function/source and authority; “Back to entity” returns to the previous focus.
- Memory economy + Wonder shows **No recorded relation** and does not invent an edge.
- The prepared draft is tagged `prepared_not_executed` / `noncanonical_intent_draft`, preserves the exact author intention, includes the captured request SHA, anchor IDs/source refs and recorded support, and never claims execution.
- Simulating a source change disables preparation, clears the draft, and shows a visible stale state; selections are not rebound by title.
- Keyboard activation was exercised for anchor selection, relation inspection and return; the 390px viewport had no horizontal overflow.
- No DOM action called `fetch`, wrote `localStorage`, or used `innerHTML`.

### B2 — Component-Aware Intent Workbench

- Reuses the same source model and produces the same source-bound draft behavior.
- Displays grouped components for up to three anchors. On the real Memory economy + Wonder selection it produced two component cards with Emotional and Causal groups.
- Switching B1/B2 preserved the same fixture, source IDs and selection; B1 has no component grid.
- The dense synthetic fixture (60 nodes, 65 links, 10 genre contracts, 8 phases) shows bounded focus: selecting one anchor produced one component card, not a flood of every card. The fixture is visibly labeled synthetic.
- No additional human-observed creative insight was established; the extra density is an interface difference, not a proven author benefit.

### Seven-task matrix

| Task | Current Studio | B1 | B2 |
| --- | --- | --- | --- |
| Inspect Memory economy and recorded wonder relations | Strong: reader, graph, inspector and facets; relations are readable prose, no exact sourceRef | Strong: exact `nodes/3`, direct link list, relation detail `links/3`, explicit unknown for the pair | Same plus grouped components; more density |
| Connect-to-ask without saving | No two-anchor question gesture; free-text revise request only | Two-anchor ask draft with “No recorded relation”; no edge saved | Same, with multi-anchor component context |
| Holistic direction | Actual `studio_architecture` request with instruction and previous candidate; no selected-anchor field | Prepared draft with exact instruction, anchor IDs and recorded support; not executed | Same as B1 |
| Challenge a link | Inspector shows the recording; challenge must be typed in free text | Link anchor selected; challenge draft carries `links/3` and the recorded function | Same as B1 |
| Freshness | Real `stale`/`guidance_changed` source status | Simulated stale disables draft and invalidates selections; prototype-only | Same as B1 |
| Keyboard and 390px | 390px no overflow; graph/facet controls are buttons; full keyboard traversal not audited | Keyboard activation and 390px checked | Same as B1 |
| Dense and sparse/empty | 18-node candidate; dense synthetic candidate not injected into Studio | Sparse fixture shows no genre/edges and explicit unknown | Dense 60-node fixture bounded to selected component cards |

## 7. Decision and evidence ceiling

### Decision

**Prototype recommendation: B1 — Question-First Semantic Inspector.**

**Production disposition: NO PRODUCTION INTEGRATION NOW; INSUFFICIENT EVIDENCE FOR AN EFFECTIVENESS CLAIM.**

B1 is the smallest credible direction because it demonstrates a specific, source-honest improvement over the current Studio without the extra decision surface of B2:

- the current Studio already shows meaning, relationships, facets and a real revision handoff, but it does not expose exact candidate source references or an explicit “No recorded relation” state for a selected pair;
- B1 adds exact `kind/ID`/sourceRef inspection, missing-relation honesty and an anchor-bound, editable draft with `prepared_not_executed` status;
- B2 adds grouped components and multi-anchor density, but no automated or simulated-author evidence showed a consequential advantage over B1. It is not rejected forever; it is not selected on current evidence;
- the current Studio remains superior for actually executing a revision because it produces a real `HostAgentRequest`. The prototype intentionally does not replace that workflow.

This is not proof that B1 improves author creativity, comprehension, speed or satisfaction. No human author study was performed. The difference is a source-precision difference with automated evidence, not a measured productivity or quality outcome.

### Smallest future production boundary (not authorized here)

If a future, separately approved design selects B1, the smallest integration question is a source-bound inspection panel inside the existing Studio that:

- accepts selected anchor `kind` and stable `ID`, not title matches;
- server-validates anchor identity atomically when `prepare_architecture` creates the request;
- preserves exact sourceRefs and “No recorded relation” semantics;
- reuses the existing host-agent prepare/complete/review workflow and working-candidate authority;
- keeps the readable reader, graph, facets and Focused Unfolding intact;
- does not add a new graph engine, persistence store, provider, ontology field or auto-accept path;
- checks and corrects any existing “preserved constraints” copy so the UI never claims preservation that was not verified.

### Evidence ceiling

- Automated Node tests: **22 model tests**, **9 DOM/view tests**, plus the existing 5 architecture-reader regressions — all passed in the combined run (**36 passed**).
- Served-browser tests: **3 passed** in `tests/test_agent_interactive_graph_browser.py` (B1 interaction/stale/mobile, B2 dense/bounded focus, current Studio baseline).
- Baseline gates from Task 0: Node **35 passed**, Python browser **7 passed**.
- Real Chromium was used for the served-browser checks; this is not a human usability, keyboard-only full-traversal, or screen-reader audit.
- The B1/B2 prototypes prepare drafts only; no coding-agent request was executed from them. The baseline Studio did prepare a real request in a disposable project; it was not completed.
- Human author validation and independent agent/runtime evaluation were **not obtained**.
- No production integration, release qualification, or creative-quality claim follows from this inquiry.
