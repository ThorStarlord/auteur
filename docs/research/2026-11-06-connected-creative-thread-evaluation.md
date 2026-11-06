# Connected Creative Thread — Creative Deliberation Evaluation (2026-11-06)

**Status:** Evidence-bounded development evaluation. Not a human author study, not release qualification, not default promotion.
**Baseline:** `main` at `02793d485d7c657f423de5c149a45dc0903dbe8d` (PR #517 merge) before this work.
**Machine-readable ledger:** [exercise-ledger.json](../qualification-evidence/creative-deliberation-20261106/exercise-ledger.json). Responses and the trimmed final resume packet sit beside it in the same folder.

## 1. Question and authority

Can an author select a real narrative meaning or relationship, receive differentiated creative reasoning, develop it across more than one exchange, preserve that direction through a holistic revision, continue it into later development, and recover it in a fresh coding-agent context?

Authority is unchanged: inquiries are read-only and noncanonical; revisions remain working candidates applied only by the explicit whole-working-revision action; Identity, Structure, Realization, Expression and the shared ontology are untouched. No new persistence owner, provider, chat platform or graph engine was added.

## 2. Evidence classes used

| Label | Meaning in this evaluation |
|---|---|
| Fixture-admitted recorded candidate | `rich-vision-candidate.json` (2026-11-03 evidence) re-admitted through the real prepare → response → complete lifecycle. Not newly generated. |
| Same-agent coordinator | Answers written by the coding agent in this session against the packet content. Not independent of the coordinator. |
| Fresh-context subagent | Separate task context. Used for short reads, short judgements and one blind critique. Long creative generation through this channel failed repeatedly and is not counted as evidence. |
| Simulated author | The coordinator wrote the author questions and selections. |
| Served Chromium | Playwright against the served Studio on a disposable project with a labelled fixture inquiry. |

No independent coding-agent execution of the full creative journey was achieved. No human author observation exists.

## 3. Journey before fixes (baseline `5a9898c4…`)

Disposable project under `%TEMP%\opencode\auteur-exercise`; served through `auteur.beginner.server`.

| Step | Observation (persisted evidence) | Owner layer of first material problem |
|---|---|---|
| 0 Fixture | Recorded candidate admitted: `ready`, 18 nodes, 18 links. | — |
| 1 Explain (`memory_economy`) | Completed; three observations source-verified (`nodes/3`, `links/3`, `links/4`). A first BOM-prefixed packet was superseded by a second request and is recorded as `not_completed`. | None material. Analysis prose assembled from chunked fresh-context parts repeats itself; chunking is a channel artifact. |
| 2 Challenge (`dilemma_produces_hope`) | Completed; two alternatives, no differentiation field. | None material for the contract; quality judged in §4. |
| 3 Explore (`memory_economy`) | Accepted with three alternatives (Communal ledger, Delegated cost, Restorable cost). Contract checks only count and distinct titles. | **Creative contract (generic prompt, weak validator).** Independent critic: PARTLY-RENAMED (§4). |
| 4 Follow-up referencing "the restorable-cost alternative from my last question" | Stored as ready, but the packet contained **0 of 9** prior-question or prior-alternative markers. A fresh-context reader returned **NOT-FOUND**. The answer was restated from conversation memory and labelled as such. | **Missing multi-turn deliberation continuity** in the inquiry owner. Not a model problem. |
| 5 Holistic revision via graph intent (3 anchors) | Review ready: 8 changed components, author-declared `dread` change flagged. Packet carried no explored alternative. Receipt held anchors only. | **Deliberation-to-revision provenance missing** (owner: revision prepare/review). |
| 6 Review | Field-level diff with full values in the hybrid compare; author-declared warnings present; no per-change rationale and no narrative-significance statement (by design). | Presentation is faithful at field level; **narrative-impact explanation is absent**. Not yet shown to decide better (no author study). |
| 7 Apply → Realization (node `memory_economy`) | Node focus accepted (202). Focus on emotion target `dread` and recorded link were both rejected (400). Realization packet carried no inquiry, alternative or author question. | **Incomplete cross-workflow integration**: realization focus accepts architecture node IDs only. |
| 8 Fresh-session resume | Architecture, status and pending state recovered; **no inquiry, mentor or alternative content**. Matches for `inquir`/`explore` were ontology or candidate text only. | **Recovery projection gap** (owner: resume packet). |
| Mentor explore → follow-up | Follow-up packet contained no prior advice; only the reply text ("Develop the second direction…"). | **Missing multi-turn continuity** in the existing Mentor owner. |
| Mentor working context | Verified: `_context` discloses the first 10 non-vision canvas items. For a 13-item canvas the newest kept idea and one other were not citable. | **Owner-level disclosure policy.** Codified by an existing test (`test_disclosed_working_sources_are_the_only_citable_canvas_sources`). Left for owner decision (§7). |
| Inquiry supersession | Preparing a second inquiry orphans a pending first one; its response cannot be completed. | Deliberate: an existing test codifies latest-request-only semantics. Not changed. |

## 4. Creative reasoning: substance and differentiation

**Explain and challenge.** The fresh-context explain prose is substantive and grounded. It argues that accuracy stops being neutral, distinguishes recorded structure from interpretation, and names trade-offs (for example, that elaborate rules could turn the fantasy into a puzzle device). The challenge (coordinator-authored) identified a real underdetermination: the recorded relation does not say who makes the remembrance choice, and the candidate's own open questions leave that unresolved.

**Explore, before fixes.** The coordinator's first explore set was judged by a blind fresh-context critic as **PARTLY-RENAMED**: "Communal ledger and delegated cost … vary only the allocation of the same survey cost, so they are two settings of one dial, even though the analysis claims all three change different variables." Restorable cost was judged genuinely distinct. The verdict is preserved verbatim in [critical-review-explore-before.txt](../qualification-evidence/creative-deliberation-20261106/critical-review-explore-before.txt).

This shows two things. First, the generic explore contract did not enforce differentiation: it accepted renamings of one variable. Second, a same-model output can claim differentiation it does not have, so the claim must be checked independently.

**Explore, after fixes.** The explore contract now requires each alternative to declare a `divergence_axis` from the Studio Mentor vocabulary, and the axes must be pairwise distinct. The revised explore set uses `social_scale`, `causal_engine` and `reader_emotion`, and replaces the allocation variant with a reader-knowledge mechanism. This is structural evidence of declared differentiation. It is **not** proof that the axes are causally independent; the critic remains the backstop for that.

## 5. Changes made

| Area | Change | Owner |
|---|---|---|
| Inquiry thread | Each packet carries up to three completed exchanges for the **same baseline** (`prior_exchanges`). Exchanges never cross a changed baseline. | `studio_architecture_inquiry.py` |
| Differentiation | Per-operation obligations appended to the inquiry system prompt. Explore requires ≥2 alternatives, distinct titles, and distinct declared axes. Explain is unaffected. | same |
| Stable IDs | Server assigns `h1…hn` to alternatives, stored with axis. Older results receive the same order-derived IDs. | same |
| History and lineage | `project_architecture_inquiry` returns `history` for the current baseline. `superseded_history` returns earlier-baseline exchanges as labelled lineage, never as prompt context. | same |
| Explicit adoption | Optional `selected_alternative {inquiry_request_sha256, hypothesis_id}` on the existing revise prepare. It is validated against the exact current baseline, fails closed when stale, superseded or unknown, and is recorded in the request and review as `selected_creative_alternative`. | `studio_architecture.py`, `server.py` |
| Revision prompt | One paragraph: develop a selected noncanonical alternative coherently, keep unrelated decisions and accepted constraints, never present it as canon. | `studio_architecture.py` |
| Fresh recovery | Resume adds `creative_deliberation` (current history, superseded lineage, latest fresh Mentor advice, and prior Mentor advice while a follow-up is pending) and `adopted_creative_alternative`. | `studio_architecture.py` |
| Mentor continuity | A follow-up carries the latest completed advice for the same focus, only while its source is still current (`prior_exchange`). | `studio_mentor.py` |
| Host bridge | `python -m auteur.beginner.studio_architecture_inquiry --project … --canvas … show|prepare|complete-file`, mirroring the Mentor bridge. | same |
| Browser | Earlier exchanges shown on canvas load, without selecting graph focus. Alternatives have explicit IDs, varies-axis text, and an explicit "Use as revision basis" action that requires a selection and author text. The inquiry packet is never sent as a revision. | `studio.js`, `studio_architecture_creative_panel.js`, `studio_architecture_agent_bridge.js` |

Scope discipline: no new schema for the architecture candidate, no new store, no provider, no ontology change, and no change to the single-latest-request concurrency rule.

## 6. Journey after fixes (final run, baseline `44a4f587…`)

Same author texts; the explain, challenge and explore responses were replayed on the final code. The explore response was revised after the critic's finding, as described in §4. The follow-up response was rewritten to match the new alternatives.

| Step | Result |
|---|---|
| Explain | ready |
| Challenge | ready |
| Explore | ready; alternatives `h1 Communal ledger` (social_scale), `h2 Restorable cost` (causal_engine), `h3 Concealed cost` (reader_emotion) |
| Follow-up (referring to "the restorable-cost alternative") | ready. Packet carried **3 prior exchanges**, including `h2 Restorable cost` with its axis. |
| Revision, adopting `h1` through `selected_alternative` | review ready. Review records `selected_creative_alternative` = h1, social_scale, from the explore request. Same 8 changed components as before, and the author-declared dread change is still flagged. |
| Apply | ready |
| Fresh resume | ready. Current-baseline history 0 (expected after a new baseline). **Lineage: explore, explore, challenge, explain.** Adopted alternative recovered. |
| Mentor explore → follow-up | ready. Follow-up carried the two prior directions. A pending follow-up's prior advice is recovered by resume. |
| Realization | Unchanged: node 202; emotion target 400; recorded link 400. |

## 7. Failure classification and disposition

| Problem | Classification | Disposition |
|---|---|---|
| Follow-up referents unresolvable | Missing multi-turn continuity in the inquiry owner | **Fixed** (prior exchanges, same baseline) |
| Explore accepted renamed alternatives | Weak creative contract (prompt and validator) | **Partly fixed**: declared distinct axes. Causal independence still depends on critique. |
| Adoption not carried into revision or review | Missing deliberation-to-revision provenance | **Fixed** (explicit, baseline-bound, fail-closed) |
| Fresh recovery loses deliberation | Recovery projection gap | **Fixed** (lineage, adopted alternative, Mentor prior advice) |
| Mentor follow-up stateless | Missing multi-turn continuity in the existing Mentor owner | **Fixed** (fresh prior advice only) |
| Realization accepts node focus only | Incomplete cross-workflow integration | **Not fixed.** Owner decision on focus model (§8) |
| No narrative-significance explanation for a revision | Presentation of meaning is absent. Deterministic review is faithful only at field level. | **Not built.** See §8 for the minimal next step |
| Canvas disclosure keeps the first ten items | Owner-level disclosure policy, codified by a test | **Owner decision** (§8) |
| Only the latest inquiry or Mentor request is projected | Projection design, codified by tests | **Retained.** Lineage is recoverable through resume |
| Long creative generation through a subagent channel failed | Environment channel limitation | **Recorded**, not a product defect |
| Packet `user` is one escaped line, and line-limited readers truncate it | Handoff presentation friction | **Recorded**, not fixed. Changing the request body would change hashed contracts. Mitigated by the new CLI, which prints JSON. |

## 8. Recommended next bounded responsibilities (not implemented)

1. **Owner decision on disclosure.** Should the Mentor's and architecture's working-source disclosure prefer the most recent items, the focus-relevant items, or the first ten? The current test encodes first-ten. This is user-visible and therefore not changed here.
2. **Realization focus carry-over (R3).** Let a graph anchor that is not a node contribute its owning node(s) or a bounded creative-context block to the realization request. This changes the focus validation contract, so it needs its own design.
3. **Narrative-impact explanation for an unapplied review.** The minimal shape is a read-only inquiry whose input is the pending review candidate, not the applied baseline. Today inquiries bind only to the applied baseline, so an author cannot ask about the proposed change. This should be tested with an author before any default.
4. **Human author evaluation** of two or three tasks (explore → adopt → review → resume) before any default promotion.

## 9. Qualification evidence (exact)

**Code commit covered by these results:** `877f4b98` on `feat/connected-creative-thread-20261106`, on top of `02793d48`. Any later source change invalidates these counts and requires a rerun.

| Check | Command or source | Result |
|---|---|---|
| New Python behaviour (L1) | pytest, 32 tests in five new files (`-o addopts=""`) | 32 new tests; see the focused run below |
| Focused Python (L1) | inquiry thread, deliberation continuity, mentor follow-up, graph revision, interactive browser, existing inquiry, review, architecture, resume, mentor agent, mentor HTTP | **106 passed**, 0 failed |
| Node new and changed (L1) | `test_studio_architecture_creative_deliberation.mjs`, panel and bridge | **20 passed** across three files (6 new) |
| Beginner-studio wide (L2) | 106 Python files: `test_beginner_*`, `test_studio_*`, `test_hybrid_*`, agent-interactive graph browser, realization suites | **829 passed, 1 skipped, 0 failed** |
| Studio Node wide (L2) | 24 `.mjs` files: `test_studio_*`, architecture, mentor, focused | **181 tests: 179 pass, 2 fail.** The 2 failures are in `test_studio_quick_draft_session_freshness.mjs`, reproduced identically at HEAD `02793d48` in a clean worktree: **known baseline failure**. |
| Pre-existing browser failure | `test_beginner_studio_architecture_edges_browser.py` | Reproduced at HEAD. #517 added an aria-hidden transparent hit target, which made a strict locator ambiguous. **Test-only update**: the assertions now select the visible layer. The test passes. |
| Ruff | changed and new files | New test files clean. The 13 pre-existing E701/E702 findings in the touched production modules are unchanged. One pre-existing unused import in an existing test was left alone. |
| #517 gaps | graph revision lifecycle (9 characterization tests, all pass on existing behaviour); served-browser journey (2 tests, Chromium) | Closed as bounded regression evidence |

**Not executed:** the full 5,700-test Python suite (L3 not triggered by this change); GitHub Actions (no hosted run was requested or observed); any human author study; any release qualification.

## 10. Continuation guidance for a fresh coding agent

Nothing here depends on the original conversation. The state lives in the project:

1. **Recover the thread:** `python -m auteur.beginner.studio_architecture --project <P> --canvas <C> resume`. Read `creative_deliberation` (lineage and Mentor advice) and `adopted_creative_alternative`.
2. **Ask a read-only question:** `python -m auteur.beginner.studio_architecture_inquiry --project <P> --canvas <C> prepare --op explore --anchor node:<id> --text-file <q.txt>`. Copy the printed packet to the coding agent. Its `prior_exchanges` are the author's context for this baseline.
3. **Complete it:** `… complete-file --response-file <json>`. The response must follow the packet's `system` text. Explore needs two or more alternatives, each with a distinct `divergence_axis`.
4. **Adopt an alternative:** write the author's intention, then POST `architecture/prepare` with `instruction`, `graph_intent` and `selected_alternative {inquiry_request_sha256, hypothesis_id}`. The hypothesis ID comes from the completed inquiry. A superseded baseline is refused.
5. **Review, then decide:** `architecture/host-agent-response` produces a review. Only `architecture/apply` changes the working architecture, and that requires the author's explicit action.

Do not treat any of this as accepted story canon. Identity and Structure are separate, explicit acceptance paths.

## 11. Final product recommendation

**Auteur now supports a credible, bounded, continuous creative thread on one working baseline.** An author can select a recorded element, receive differentiated alternatives with declared causal axes, follow up against the earlier exchanges, explicitly adopt one into a holistic working revision with provenance, review it, apply it, and recover the whole lineage in a fresh session.

**It does not yet support:**
- continuation of an emotional or relational focus into Story Realization;
- an explanation of a pending revision's narrative significance;
- any claim about the quality of the creative reasoning beyond one simulated author and one independent critic;
- human usability, or any default promotion.

**Keep the feature experimental.** The next evidence that would change the decision is a short human author study of the explore → adopt → review → resume path, plus the owner decision on disclosure (§8.1).
