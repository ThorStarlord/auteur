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
| 1 — source-bound semantic projection | PENDING |
| 2 — graph-to-agent intent grammar | PENDING |
| 3 — B1 Question-First Semantic Inspector | PENDING |
| 4 — B2 Component-Aware Intent Workbench | PENDING |
| 5 — comparative browser evaluation | PENDING |
| 6 — convergent recommendation | PENDING |

## 5. Baseline task observations (to complete during Task 5)

The actual current Studio will be exercised with the recorded Memory Economy material for the seven author tasks. Results will be recorded here as observations, not as a deliberately inferior mock.

| Task | Current Studio observation |
| --- | --- |
| Inspect Memory Economy and recorded wonder relations | Pending served-browser run |
| Connect-to-ask Memory Economy + Wonder without saving | Pending |
| Holistic direction draft | Pending |
| Challenge a recorded causal link | Pending |
| Stale source handling | Pending |
| Keyboard and 390px traversal | Pending |
| Dense and sparse/empty handling | Pending |

## 6. Prototype results (to complete)

Pending Tasks 1–5.

## 7. Decision and evidence ceiling

Pending Task 6. No production integration is authorized by this plan.
