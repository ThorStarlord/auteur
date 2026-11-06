# Creative Intention Continuity and Narrative Realization — Assessment (2026-11-06)

**Status:** Evidence-bounded development assessment. Experimental Studio feature; not release-qualified; no human author study.
**Baseline:** `main` at `0d7e06e366b7efb49143678b2795aea2a97360d6` (PR #518 merge).
**Evidence:** [journey ledger](../qualification-evidence/creative-intention-continuity-20261106/journey-ledger.json), [responses and critiques](../qualification-evidence/creative-intention-continuity-20261106/), [recovery brief](../qualification-evidence/creative-intention-continuity-20261106/recovery-brief.txt), [trimmed resume packet](../qualification-evidence/creative-intention-continuity-20261106/resume-summary.json).

## 1. Question

Can Auteur preserve and develop an author's creative intentions across successive revisions, narrative layers and independent agent sessions — not merely recover past conversations?

Three things are distinguished throughout:

| Concept | Where it lives | Authority |
|---|---|---|
| Conversation history | inquiry request/result artifacts; Mentor request/response artifacts | noncanonical evidence |
| Creative decision lineage | review records (`selected_creative_alternative`, `prior_request_sha256`) and inquiry results | historical decisions, noncanonical |
| Continuing creative intention | CanvasStore working note with `intention_status` and provenance | author-directed working direction; never canon |

No new persistence system was added. The intention reuses the existing working canvas (the same owner that already stores author notes and provisional concepts), and lineage walks the existing revision chain.

## 2. Verified gaps before repair

| # | Observation (persisted evidence) | Owning layer |
|---|---|---|
| 1 | After a second, unrelated revision and apply, `adopted_creative_alternative` became `None` although the first revision's `review.json` still recorded the adoption. The projection followed only the current request. | architecture resume projection |
| 2 | Explore rejected a genuinely different same-axis pair (renewal-bound debt vs. fixed tithe) with "must each declare a distinct divergence_axis", and accepted a different-axis allocation rename and identical descriptions. | inquiry creative contract |
| 3 | A completed inquiry's alternatives remained clickable after an applied revision because the browser refreshed inquiry state per canvas, not per baseline; the server then rejects the stale selection. | Studio browser |
| 4 | Mentor disclosed the first ten non-vision canvas items; in a 13-item canvas the newest kept ideas were invisible and non-citable. | Mentor context |
| 5 | Realization accepted only architecture node IDs; `emotion_target:dread` and a recorded link were rejected with HTTP 400. | Realization focus |
| 6 | No read-only path examined a pending, un-applied revision; inquiries bound only to the applied baseline. | inquiry target model |
| 7 | Recording an author intention immediately marked the just-applied architecture stale, blocking Realization. Found during the journey, not by inspection. | freshness boundary |

## 3. Implementation changes

| Change | Owner | Notes |
|---|---|---|
| Adoption lineage across the revision chain | `studio_architecture.py` | Walks `prior_request_sha256` (bounded, cycle-safe). `adopted_creative_alternative` is now the most recent adoption in the chain; `creative_adoption_lineage` lists every adoption newest-first with the request it was adopted in. |
| Author-directed continuing intentions | `studio_store.py`, `studio_architecture.py` | Optional `intention_status` (`provisional/active/superseded/withdrawn`) on a working note; requires directive text. CLI: `keep-intention`, `set-intention-status`, `intentions`. Intentions are disclosed with status and provenance in architecture and Mentor packets and in resume. |
| Intention freshness boundary | `studio_architecture.py` | Intentions bind **in-flight** requests (`intention_sha256`) but do not invalidate the applied candidate, so recording a direction does not block Realization. |
| Explore differentiation | `studio_architecture_inquiry.py` | Removed the pairwise-distinct-axis rule. Requires ≥2 alternatives, distinct titles, distinct descriptions, and a declared axis per alternative. Guidance now asks what changes at the story's decisive choice. |
| Baseline-keyed browser refresh | `studio.js`, creative panel | Inquiry projection refreshes when the canvas **or** baseline changes; stale alternatives are cleared; superseded exchanges render as labelled, non-selectable lineage. |
| Relevance-first disclosure | `studio_mentor.py` | Deterministic priority: focus, recorded relationship or kept-for-focus, explicit author reference, recent kept idea, other; bounded to 10 items / 6000 chars; every item has `selection_reason`; omitted count reported; only disclosed items are citable. |
| Typed Realization anchors | `studio_realization.py`, graph-intent resolver | 1–3 validated anchors resolved against the current candidate, carried as `creative_anchors` with exact `sourceRef` and a citable `ref`. Elements may cite `anchor_refs`; unknown refs are rejected. Node-only callers unchanged. |
| Pending-review inquiry | `studio_architecture_inquiry.py`, graph intent | `target: pending_review` carries baseline, proposal, requested change, changed components, adopted alternative and preserved commitments; observations resolve against the proposal and are labelled `observed_in`. Valid only while that review is pending; `revise` cannot target it. |

## 4. Creative intention continuity assessment

The authentic journey (fixture-admitted rich architecture, `connected-thread` canvas) ran:

1. **Explore** from a recorded relationship (`link:engine_drives_cost`) → three alternatives with distinct titles, descriptions and declared axes.
2. **Deliberate**: a follow-up referring to "the renewal-bound debt alternative" → the packet carried the prior exchange and the exact mechanism text; the answer resolved the referent from the request, not chat memory.
3. **Decide**: `h1` adopted explicitly through `selected_alternative`.
4. **Revise**: holistic revision with three anchors → nine coordinated changes; review recorded the adopted alternative, its axis and its inquiry.
5. **Review**: pending-review inquiry → context held baseline, proposal, requested change and the selection; the applied candidate stayed unchanged while the answer was produced.
6. **Realize**: `emotion_target:dread` plus `link:engine_drives_cost` carried into Story Realization; the scene cited both anchors.
7. **Evolve**: a further, unrelated revision packet automatically disclosed the active intention (status `active`, provenance `h1`). After applying it, the intention was still active and the adoption still in lineage. The intention was then **withdrawn**; a new revision packet disclosed status `withdrawn`.
8. **Recover**: a fresh agent read only the recovery brief and correctly recovered the direction, the withdrawn status, the adopted alternative with provenance, and the historical exchanges.

Continuity results:

| Intent | Survives? | Mechanism |
|---|---|---|
| Adopted direction across later unrelated revisions | **Yes** (was No) | adoption lineage |
| Author-directed intention across revisions | **Yes** (new) | canvas intention with status + provenance, disclosed in every revision packet |
| Modify/withdraw authority | **Yes** (new) | explicit `set-intention-status`; withdrawn remains visible with status, adoption stays as history |
| Distinguish history from current authority | **Yes** | status field plus superseded lineage; applied-baseline history separate from superseded exchanges |
| Ambiguity of *why* an adoption happened | **Partially** | provenance gives inquiry, hypothesis id, operation and the original author question; no separate rationale record |
| Supersession linkage between intentions | **No** | a superseded intention has no successor pointer; a replacement is a separate record |

## 5. Narrative divergence evaluation

Deterministic probes against the repaired contract (source-grounded examples, not category names):

| Case | Before | After |
|---|---|---|
| Same axis, genuinely different mechanisms (renewal-bound debt vs. fixed tithe) | **Rejected** (false negative) | **Accepted** |
| Different axes, same allocation mechanism (communal ledger vs. shared burden) | Accepted | Accepted — deterministic limit |
| Identical descriptions under different titles/axes | Accepted | **Rejected** |

The independent critic still judged the journey's set **PARTLY-RENAMED**, arguing that concealed cost hides the same transfer rather than changing allocation or recovery. That is the important result: structural validation can catch verbatim duplication and enforce declared differentiation, but it cannot establish creative substance. The critic remains necessary. The explore prompt now explicitly asks each alternative to state what changes at the decisive choice; no numerical score was introduced.

## 6. Realization continuity exercise

- Anchors prepared from a source-backed architecture: `emotion_target:dread` (`emotion_targets/1`), `link:engine_drives_cost` (`links/3`), and a node-only compatibility baseline.
- The emotion anchor carried its recorded intended effect and eliciting condition; the relationship anchor carried endpoints and function; the component form carries the selected field value.
- The completed proposal cited both anchors on the scene and the relationship on the arc, referenced existing architecture nodes, and did not assert any realization as established story fact.
- Independent critic: **CONCRETE-AND-GROUNDED**; anchors used as guidance, not prior events. Its risk note: the bureaucratic renewal notice may read as exposition rather than dread.
- Node-only preparation and completion remain unchanged.

## 7. Pending-revision narrative-impact review findings

The pending-review inquiry can show the author, before applying anything:

- the applied baseline and the complete proposal;
- the requested change and the adopted alternative with provenance;
- the deterministic changed-component list;
- preserved author-declared targets and accepted constraints;
- the proposal's own node/relationship evidence, with observations labelled `observed_in: proposed_revision`.

It cannot decide literary quality, and its evidence classes are only as good as the model's labelling. In the journey the answer distinguished recorded change, reasoned consequence, an author decision and a speculative reader risk. This is a read-only capability built on the existing inquiry and review owners; there is no second review system and no apply path.

## 8. Fresh-agent recovery evidence

The recovery packet contains: architecture and status, open questions, author-directed intentions with status and provenance, the adoption lineage with inquiry and request identities, current-baseline exchange history, superseded history (including pending-review examinations), and pending Mentor advice.

An independent fresh context that read **only** the rendered brief reconstructed the current direction, the withdrawal, the adopted alternative and its source exchange, and a valid next action. It was over-cautious about a non-existent pending revision — a comprehension imprecision, not a recovery failure. This is not human usability evidence.

## 9. Validation

**Code commit:** `9b7d7f1f` on `feat/creative-intention-continuity-20261106`, on top of `0d7e06e3`. Any later source change invalidates these counts.

| Check | Result |
|---|---|
| New Python tests (pending review 8, creative intentions 8, realization anchors 9, Mentor disclosure 5, plus 3 added to existing suites) | **33 new Python tests**; all pass |
| New Node tests (lineage rendering, stale invalidation) | 2 new tests; pass |
| Focused Python (all changed owners + served Chromium) | **182 passed, 0 failed** |
| Beginner-studio wide L2 (110 files) | **863 passed, 1 skipped, 0 failed** |
| Studio Node L2 (183 tests) | **181 pass, 2 fail** — both in `test_studio_quick_draft_session_freshness.mjs`, reproduced at HEAD `0d7e06e3` (known baseline) |
| Ruff | No new findings. 23 pre-existing E701/E702 in the two compact modules are unchanged; new tests clean. |
| Browser | Served Chromium: inquiry prepare without revision; alternative reaches the revision payload; **applying a revision clears stale alternatives and shows lineage**. |

**Not executed / not established:** full 5,700-test L3 suite; hosted CI; independent full-journey agent generation; human author comprehension, preference or literary quality; release qualification.

## 10. Limits and deferred work

- Intentions have no supersession pointer and no per-transition audit; current status plus provenance is the authority record.
- The browser exposes intention status and lineage through packets and the panel result; intention creation/status changes are CLI/API-first, matching the agent-first product stance. A richer intention UI was not added.
- Pending-review inquiries are CLI/API-first; no new review button was added.
- Architecture's own `_source` still discloses 24 items by insertion order; the relevance-first selector is implemented in the Mentor owner, where the verified defect was. Unifying the selection contract would change Architecture request hashes and is a separate decision.
- The deterministic divergence rule cannot detect semantic renamings; the critic remains the backstop.
- Disclosure "relevance" is recorded-relationship, origin and exact-mention based; it does not infer semantic relevance.

## 11. Final recommendation

**Auteur now supports a credible bounded creative-intention thread**: explore → deliberate → adopt → holistic revision → review (including a pending-revision critique) → realization from emotional/relational anchors → further revision that keeps the intention visible → explicit withdrawal → fresh-session recovery of active, historical and withdrawn decisions.

It remains **experimental**. The nearest decision-changing gap is no longer persistence; it is author experience: whether a human author can use the lineage, intention statuses and pending-review critique to make better creative decisions. That requires a small human study and an intention-management surface, not more storage.

Next bounded responsibilities, in order:

1. Human author walkthrough of Stages 1–8 with this implementation.
2. Intention management UI (create, supersede with successor, withdraw) reusing the canvas command path.
3. Optional unification of Architecture and Mentor disclosure behind the same bounded selector, with request-hash versioning.
