# Agent-Simulated Authoring and Repository Exploration — Execution Plan

**Date:** 2026-10-25  
**Decision:** Qualify the existing focused Story Realization + Quick Draft handoff, then probe two independently valuable creative capabilities without inventing new infrastructure.  
**Status:** BOUNDED EXECUTION PLAN / NOT A NEW APPROVED ROADMAP OR RELEASE DECISION.  
**Base source:** `ThorStarlord/auteur` `main@a8a090580e98cd5f6dcee1645375e2867e644350`; recheck all heads before execution.  
**Scope:** existing single-author, graph-first, agent-first Auteur. The selected controlled frontiers remain F2 small-Book coherence and X3 persistent Book workspace.  
**Companions:** [repository-wide idea frontier](../research/auteur-repository-idea-frontier-2026-10-25.md), [UI possibility landscape (PR #485)](https://github.com/ThorStarlord/auteur/pull/485), [UI strategic evolution + isolated stress evidence (PR #486)](https://github.com/ThorStarlord/auteur/pull/486), [development validation policy](../engineering/release-qualification.md), [mission](../../MISSION.md).

## 1. What the latest work established, and what it did not

| Finding | Grounded evidence | Claim ceiling / next discriminator |
| --- | --- | --- |
| Story Realization reference integrity is narrower than creative fidelity | Existing `_assert_refs` on main checks globally valid Architecture references; draft [PR #484](https://github.com/ThorStarlord/auteur/pull/484) adds focused-reference coverage. Isolated stress checks reproduce the distinction. | An output can cite the selected ID while ignoring its *meaning*. Deterministic reference integrity is not an artistic-validity test. Execute PR #484's actual focused tests, then examine creative fidelity via explicit source-bound agent output/review only when needed. |
| There is a real Story Realization -> Quick Draft continuity seam | Draft [PR #487](https://github.com/ThorStarlord/auteur/pull/487) changes copied concrete scene intent, explicit Vision reuse, overlength refusal, provenance labels, and working-only status. | The source diff is not a completed full-application journey; the isolated 3-case Node and 9-checkpoint Chromium fixture reported in the PR discussion does not validate HTTP/CanvasStore/persistence end to end. |
| A coding agent can simulate *mechanical author actions* | PR #487 includes `tests/test_studio_quick_draft_agent_simulation.mjs`; it reads selected action bodies from real `studio.js` and uses deterministic DOM/network seams to exercise exact handoff inputs. | An excerpt/DOM simulation is a fast L1 unit test, **not an independent coding agent invoking a real host model**, a running browser app, or literary-quality evidence. Keep those execution levels separate. |
| Focusing tests on the commit is appropriate | [Validation policy](../engineering/release-qualification.md) explicitly selects focused L1; L2 requires a named changed integration boundary; L3 is not the ordinary commit loop. | "Only new tests" is too narrow when existing invariants are reachable. Run new tests **plus the smallest adjacent sentinel cases**, not all unit tests. |
| The repository has a larger opportunity surface than Studio layout | [Repository-wide idea frontier](../research/auteur-repository-idea-frontier-2026-10-25.md) maps Story Opportunity, Premise Fitness, manuscript archaeology, F3–F7 narrative pressures, craft, and attention. | Possibility enumeration does not select all candidates. Probe specific author jobs against existing owners before admitting a new UI, store, ontology, or agent runtime. |

**Strategic reconciliation:** NO_MODEL_CHANGE / REAFFIRM the connected creative-thread direction for the *current UI work*. Preserve four broader creative futures as **hypotheses**, not an implementation queue. The new information changes execution/evidence responsibilities, not the product thesis.

### One evidence ladder, without inventing new runtime states

1. **Source inspection / isolated contract replica** — shows what the code appears to permit or an independently recreated model predicts.
2. **L1 against exact production files** — unit tests, source-loaded UI action simulations, relevant deterministic validators and syntax/lint.
3. **L2 served HTTP + automated Browser + CanvasStore** — a coding agent follows a scripted fictional author's actual interface journey and verifies saved/unsaved state. Browser steps need no human actor.
4. **Actual host-agent sample (when the claim requires generation)** — the coding agent processes a real prepared request through the existing host contract, returns a response, and the system validates it. A canned response may test transport but **must not** be called a live generation/critique success.
5. **Human creative/UX evidence, only for human claims** — preference, felt usability, literary effectiveness, and reader response cannot be inferred from agent-only samples.

**Never promote evidence up this ladder by relabeling it.** A negative control that fails when a behavior is removed makes a unit test useful; it does not make that test an integrated UI journey.

## 2. Execution sequence and dependencies

```text
P0. Recheck source / fixture / PR identity
    |
    +--> P1. Focused backend validation: PR #484
    |
    +--> P2. Coding-agent simulated author UI: PR #487
                 |
                 +--> P3. One cross-boundary F2/X3-compatible journey,
                      only if the independent focused gates pass
    |
    +--> P4. Independent, noncanonical S1 and S2 creative probes
                 |
                 +--> P5. Reconcile capability findings and choose
                      zero or one bounded next product responsibility

Separate docs integration: #485 -> #486 (stacked); #488 independent.
No automatic merge, new story canon, release, or frontier promotion.
```

### P0 — Establish ground truth and prevent duplicate work

**Actions:** Re-read `main`, PR #484/#485/#486/#487/#488 heads, bases, overlap, current [STATUS](../../STATUS.md), and the relevant source/test files. For local execution, verify `git rev-parse --show-toplevel`, `--git-common-dir`, `HEAD`, Python and Node interpreter paths, and whether the checkout is standalone or linked. Confirm the fixture is disposable and never use the owner's private manuscript.

**Deliverable:** PR-level execution note recording exact HEAD, base, existing evidence, command selection, environment availability, and explicit claim ceiling.

**Gate:** No claim about the current source depends solely on an earlier chat report or a branch that has changed. If a coding-agent execution environment is unavailable, leave the work **blocked at that gate**, do not replace it with an unrelated simulated success.

### P1 — Qualify focused Architecture -> Realization source integrity (PR #484)

**Changed owner:** `src/auteur/beginner/studio_realization.py::_assert_refs`. Do not duplicate this guard inside a new UI helper.

**L1 focused commands on the exact PR #484 head:**

```sh
python -m pytest -q tests/test_beginner_studio_realization_creative_continuity.py
python -m pytest -q tests/test_beginner_studio_realization.py -k "invalid_links_and_unsupported_architecture_refs or realization_is_created_only_after_architecture"
ruff check tests/test_beginner_studio_realization_creative_continuity.py src/auteur/beginner/studio_realization.py
python factory/guard.py --base origin/main --head HEAD
```

**Adversarial cases / acceptance:**

- One selected Architecture node is covered; omitted selected node rejected.
- Two selected nodes require both references; a partial result is rejected.
- Whole-story no-focus request is still permitted.
- Nonexistent references are rejected; stale response cannot replace the working current candidate.
- No data is automatically accepted as Identity, Structure, Realization truth, or prose canon.
- **Known limit:** attaching a correct ID to unrelated text can still pass. Do not misdescribe the ID guard as deep narrative fidelity.

**Exit:** exact-head L1 passes and any failures are classified as code defect, contract mismatch, or environment blocker. If runtime unavailable, keep the PR draft and record commands, not an invented pass.

### P2 — Qualify author-simulated scene handoff (PR #487)

**Changed owner:** existing `studio.js`, `studio.html`, working CanvasStore fields and Quick Draft initiation. There is no new canonical story-state owner.

**L1: run only the new simulated author actions and cheap safety checks on the exact PR #487 head:**

```sh
node --check src/auteur/beginner/browser/studio.js
node --test tests/test_studio_quick_draft_agent_simulation.mjs
ruff check tests/test_beginner_studio_architecture_to_realization_browser.py
python factory/guard.py --base origin/main --head HEAD
```

**L2 is justified only by this named changed boundary:** Browser -> Studio working scene -> explicit Quick Draft POST -> CanvasStore persistence/re-entry. Run **the two named new Playwright tests**, not the entire Beginner/Studio test suite:

```sh
python -m pytest -q tests/test_beginner_studio_architecture_to_realization_browser.py -k "realization_scene_carries_editable_intent_to_quick_draft or vision_to_premise_refuses_truncation_or_fabrication"
```

**Coding agent plays this fictional author on a disposable served workspace:**

1. Save a broad, noncanonical Story Vision; load a valid *working* Architecture and a proposed focused Realization scene (deterministic fixture is acceptable **only** for transport/UI mechanics).
2. Click the Realization scene, copy it into an editable working scene, and verify the exact scene description is the editable intent. Source ID/origin stay visible, **not** in the Quick Draft prompt.
3. Attempt "generate" without premise. Expect zero network POSTs and no accepted files.
4. Explicitly copy Story Vision into a premise, edit it, and ensure a second copy action cannot overwrite the edit.
5. Submit through the explicit Quick Draft control. Assert the exact `premise` and `first_scene` request payload and staged noncanonical session ID.
6. Save, reload, restore focus and scene fields; verify existing story Identity/Structure/accepted Chapter files are unchanged.
7. Try empty Vision, overlength Vision, overlength scene notes, and intact provenance footer; expect refusal rather than silently fabricated, overwritten, leaked, or truncated inputs.
8. If the changed UI layout is exercised at 390px, verify the new control remains reachable, labeled, and does not obscure the original input path. This checks a mechanical presentation condition, **not** human usability.

**Negative control:** deliberately remove/disable the scene-intent transfer *in a disposable test copy* and ensure the target test fails for that reason; restore production source before recording evidence. A regression test should be able to falsify its own claim.

**Exit:** L1 and L2 evidence on the exact head, with preserved author source, no unintended canonical writes, and no unclassified failures. A transport-only fixture is not a claim that host generation worked. A full L3 run is **not** required for an ordinary commit.

### P3 — Check the combined handoff without creating a new acceptance owner

**Prerequisite:** P1 and P2 focused evidence is available. This is a **single targeted integration slice**, not a new broad story-creation demonstration.

- Reconcile the validated heads against current `main` before integration.
- Use an existing source-bound Architecture focus -> Realization request -> concrete working scene -> optional Quick Draft staging -> save/reopen journey.
- Preserve the distinction between simulated UI transport and actual coding-agent generation. If the host model is genuinely invoked, record which request and generated output are authentic.
- Validate **no automatic canonical mutation**, provenance/source freshness, no lost author edits, and a clear recoverable failure state.
- Execute the smallest existing tests that cover the changed crossed boundaries. No repository-wide full suite without a separate stabilization/release trigger.

**Exit:** either one precisely qualified continuation or a named owning-layer defect plus focused repair. Do not repeat the original successful first architecture-generation demonstration or expand the demo to six Chapters just to create activity.

### P4 — Probe two *different* sources of creative value, independent of UI qualification

These investigations are not gated on the Browser PR; their value is in choosing future **creative capabilities** instead of merely improving navigation. Use the existing coding agent and documented methods, keep all outputs WORKING / NOT ACCEPTED, and use original synthetic inputs only (no third-party-story importing or scraping).

#### S1 — Story Opportunity Discovery + Premise Fitness (exploratory, no new runtime)

**Question:** When the fictional author supplies only attractions/desired experience, does the existing documented method help the coding agent produce **causally distinct** story directions instead of decorative variations?

**Fixture A:** A warm academy, intelligent companionship, mystery, and generous heroism; no settled plot, cast, or cosmology.  
**Fixture B:** A bleak, time-constrained voyage involving an unreliable witness and a costly rescue; no settled ending.

**Agent exercise:** For each fixture, propose three *working* directions with source-attributed stated desires versus invented proposals; governing causal engine; renewable/finite runway conditional on intended horizon; genre/reader promise; unique sacrifices/tradeoffs; and the smallest next author decision. Compare the documented [Story Opportunity Discovery](../story-opportunity-discovery.md) + [Premise Fitness](../premise-fitness.md) protocol with a plain unstructured alternative only when a comparison changes the decision.

**Adversarial conditions:** reject cosmetic reskins, unattributed market/popularity assertions, inferred preferences presented as authored facts, score-based "best idea" claims, and forced automatic selection. Check whether all three directions could sustain *different* scenes rather than merely different names.

**Evidence:** keep the exact synthetic input, request, response, mechanisms, source-status notes, critique and uncertainty. No user preference, market demand, generalized model reliability, or actual reader pleasure is established.

**Next decision:** If a coding agent already performs this reasonably from documentation, **do not build a new Opportunity UI or storage layer**. If a repeated specific failure remains, identify the lowest owner: source prompt/context, comparison presentation, or missing documented craft method.

#### S2 — Manuscript-First Story Archaeology (exploratory, no canonical import)

**Question:** Can the coding agent interpret existing *original* prose as several possible stories, without treating its inference as fact?

**Fixture:** Two brief fictional scenes with (i) an apparent rescue, (ii) mutually contradictory accounts of why it happened, and (iii) a detail that may support either altruism or concealment. Freeze each paragraph with a stable source line/ID. Later deliver an invented author correction that rules out one plausible inference.

**Agent exercise:** Extract only observed textual claims with source citations; distinguish uncertain hypotheses about engine, character motive, structure, and relationship; propose two materially different noncanonical interpretations; then update the analysis after correction without rewriting the source scenes or producing accepted Story Identity.

**Adversarial conditions:** no confident invented character history, no fake source lines, no promotion of an interpretation into canon, and no "correction" that quietly overrides preserved textual evidence.

**Evidence:** exact scenes, source-linked interpretations, unsupported/hallucinated assertions, response to correction, and minimal current-owner handoff needed if the author later chooses a hypothesis.

**Next decision:** If the existing agent-and-document method suffices, retain this as a **documentation-first capability**, not a new manuscript parser or forced first-screen workflow. Build only after an observed repeated concrete need and a bounded owner are identified.

### P5 — Reconciling results and considering later candidates

Do **not** automatically implement S3–S6 or all 13 families from the [idea frontier](../research/auteur-repository-idea-frontier-2026-10-25.md).

| Future trigger | Small next probe if the trigger appears | Still not automatically authorized |
| --- | --- | --- |
| S1/S2 repeatedly lose the author's intention when crossing a specific workflow | Source-linked intent-to-existing-owner composition | New general intent store, new acceptance path |
| An authentic draft introduces consequential material that cannot be captured without duplicate author entry | S3: selective discovery delta, with explicitly rejected discoveries | Automatic canon synchronization |
| F2/X3 is qualified and an F3 multi-thread Book repeatedly includes irrelevant context | S4: Chapter-N included/omitted context trace | Generalized retrieval/knowledge engine |
| Actual mystery/revelation authoring cannot express protagonist, reader and world knowledge separately | S5: truth/belief/reveal diagnostic on existing owners | A new epistemic semantic layer on speculation |
| A selected later frontier demonstrates cascading unnecessary invalidation after a major revision | S6: changed/untouched artifact audit | Automatic mass revision and silent acceptance |
| Repeated specific creative decisions lack necessary guidance | One narrowly scoped Story Design Pack sample | Whole craft encyclopedia or universal premise score |

**Reconciliation:** Return findings through the existing PR/evidence surfaces. Update [Product Evolution Roadmap](../product-evolution-roadmap.md) only if a candidate is genuinely selected/deferred based on new evidence; update [STATUS](../../STATUS.md) only for actual integrated operational state. Keep UI landscape and repository-wide future-map documents as **possibility references** rather than rewriting them as authorities.

## 3. Verification and recording matrix

For every executed case, preserve a compact receipt **inside the relevant existing PR or qualification record**, not a new master orchestration ledger:

| Required field | Why |
| --- | --- |
| Git main/base/HEAD and touched files | Makes claims reproducible after other work merges |
| Exact executable/tool version and repo root | Distinguishes stale-path or missing-runtime failures from code defects |
| Fixture provenance and source identity | Separates genuine author text from agent invention |
| Exact command / automated browser task and exit code | Confirms a gate actually ran |
| Collected, passed, failed, skipped and incomplete, where applicable | Prevents a green-sounding summary from hiding missing checks |
| Positive result + at least one falsifier/negative control | Demonstrates that the focused test would detect the behavior it protects |
| Working versus accepted writes and stale-source result | Preserves the mission's author-authority invariants |
| Scope of claim, unresolved risk and owning next action | Avoids turning synthetic performance into creative or release readiness |

**L1** tests modified/deterministic behavior and adjacent reachable invariants. **L2** is for a named integration seam. **L3** only at an explicit broader checkpoint. Never weaken tests or fake a coding-agent provider response to claim successful creative drafting. Never infer that all agents/models behave the same from one synthetic sample.

## 4. PR integration and documentation hygiene

- [PR #484](https://github.com/ThorStarlord/auteur/pull/484): backend focus guard; remains draft until exact-head relevant Python L1/guard passes.
- [PR #487](https://github.com/ThorStarlord/auteur/pull/487): working scene/Quick Draft bridge; remains draft until exact-head Node L1 and named Browser L2 passes.
- [PR #485](https://github.com/ThorStarlord/auteur/pull/485): unranked UI divergent landscape; docs-only, independent of #484/#487.
- [PR #486](https://github.com/ThorStarlord/auteur/pull/486): UI strategic comparison + synthetic contract evidence; **stacked on #485**. Integrate #485 before retargeting/reconciling #486.
- [PR #488](https://github.com/ThorStarlord/auteur/pull/488): repository-wide creative futures + **this operational plan**; independent docs branch.

Recheck exact heads and real merge protections at integration time. `mergeable=true` means Git can form a merge, **not** that the PR was qualified. This plan requests no merge, release, deploy, external data transfer, permanent product-scope change, or author commitment.

### Evidence-based stop rules

Stop the current work package when its relevant exact-head evidence passes or its concrete execution dependency is unavailable. Continue with an **independently warranted** creative probe if available; do not route around the blocked gate. Stop expanding exploration once new ideas rephrase existing families or would not change the next decision. Prefer **one bounded current responsibility at a time** over an open-ended feature campaign.

## 5. Decision trace

**Selected:** focused qualification of two existing code PRs, plus independent cheap noncanonical S1/S2 research probes. This creates immediate product confidence and explores distinct sources of author value.

**More conservative alternative — only keep discussing UI concepts:** insufficient. It cannot establish production-code correctness or reveal whether Opportunity/Manuscript capabilities offer value beyond existing methods.

**More aggressive alternative — implement all documented futures:** unwarranted. It would duplicate owners, increase maintenance and undermine the current F2/X3 evidence frontier without discriminating which author job truly needs new code.

**Expected end state:** either (a) two exact-head bounded engineering gates with noncanonical author-flow continuity, and source-linked learning from S1/S2; or (b) explicit missing evidence and narrowly owned follow-ups. In either case the graph-first decision, five semantic layers, creative-authority boundary and release policy remain unchanged.

## 6. Returned evidence — 2026-10-25 execution addendum

This section records **what actually happened** against the plan, not a permanent status tracker or a claim that blocked phases passed.

- **P0:** The GitHub connection returned `main@a8a090580e98cd5f6dcee1645375e2867e644350`, draft PR #484 head `2f606d54ae7f71db34f9244ada8cf30a8cb3460d`, draft PR #487 head `a8811a3cf48a34cc7a98019b75573ebf9627a28f`, and open documentation PRs #485/#486/#488. The execution container has Python 3.13.5 and Node 22.16.0, **no Auteur Git checkout**, and direct `git ls-remote https://github.com/ThorStarlord/auteur.git HEAD` failed DNS resolution. No exact-head repository identity or VCS topology can be certified in that local container.
- **P1:** Re-ran the source-derived, **not-imported** 13-assertion Python/Pydantic contract harness from the [previous UI stress bundle](../product-validation/living-story-studio/2026-10-25-simulated-author-ui-stress-test.md); **13/13 harness assertions passed**, including draft focus coverage, off-focus negative cases, and the reference-label-laundering residual. The required **real PR #484 production-module pytest/ruff/guard commands did not run**. PR remains draft.
- **P2:** Re-ran the local source-excerpt Node test fixture `node --test /mnt/data/auteur_agent_sim/tests/test_studio_quick_draft_agent_simulation.mjs`: **3 passed, 0 failed**; earlier recorded negative-control mutation causes the two relevant tests to fail, as intended. Also ran `python /mnt/data/auteur_agent_sim/agent_browser_check.py`: **9 scripted headless Chromium fixture checkpoints passed, zero page errors, one explicit mocked request**. These tests **do not** run the complete `studio.js`, served Auteur app, CanvasStore or the two committed PR #487 Playwright tests. `node --check` on the local selected-function excerpt passed; full exact-head syntax/guard/ruff and L2 remain missing. PR remains draft.
- **P3:** **BLOCKED** at a genuine cross-component gate. Connector source trace shows existing Architecture preparation and working Realization, explicit scene copy, optional Quick Draft staging and noncanonical storage, but neither the exact PR #484+#487 integrated app nor a real host coding-agent request has been exercised. An excerpt simulation or canned response cannot be promoted into this milestone. Do not repeat the previous first-architecture demonstration to disguise the missing gate.
- **P4:** Executed two **assistant-authored original synthetic creative probes** under the documented methods; see [complete S1/S2 worked evidence](../product-validation/2026-10-25-s1-s2-agent-creative-probes.md). S1 contains two opposite no-premise fixtures and six causally differentiated WORKING directions with scope-fit/tradeoff analysis. S2 contains four frozen paragraphs, five cited observations, two hypotheses and an explicit author-correction revision. No independent host agent, actual Auteur API, human author or real book was involved.
- **P5:** **NO_MODEL_CHANGE / REAFFIRM** Connected Creative Thread for current UI work. Retain Story Opportunity Discovery and manuscript archaeology as separate documentation-first options. **Do not build new runtime, score, canonical importer, ontology, retrieval engine, or UI by default.** The missing exact-head L1/L2/P3 gates have explicit owning PRs and do not block this separate noncanonical exploration conclusion.

**Next bounded execution boundary:** In a real checkout at PR #484 and #487 exact HEADs, run the L1 and two named L2 tests above, fix only demonstrated failures, then execute the single P3 combined journey. Recheck `main` before integration; do not automatically merge or release. A qualified outcome may justify another bounded authoring improvement, not the entire ideas backlog. The original user did not need to provide synthetic inputs; the unsatisfied dependency is actual source-execution access, not owner preference.
