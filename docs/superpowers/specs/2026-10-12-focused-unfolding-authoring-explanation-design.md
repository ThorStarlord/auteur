# Focused Unfolding: Authoring and Explanation in One Narrative Architecture UI

**Date:** 2026-10-12
**Status:** Written design for owner review; not yet implementation authorization.
**Product:** Auteur graph-first Living Story Studio.
**Grounded baseline:** `main` at `a6808210318d27cd2867f63bfe4404a43896840e` has the standalone explanation/semantic-navigation prototypes (#393–#400). The actual Studio remains in unmerged UX PRs #386–#392, with explanatory integration PRs #401–#403 also draft. Reconcile exact heads before any Studio implementation.

## 1. Intended author experience

Auteur **progressively explains and helps author** one interconnected narrative architecture. The real graph is the main workspace **from the first session**. Starting with intended **reader emotion** is the recommended invitation, but never mandatory: authors can begin with premise, character, genre, trope, world/setting, theme, conflict, or a free-form idea.

Selecting a concept shows **two or three provisional suggestions near that focus**, rather than scattering AI-generated branches across the graph. Each possible branch answers: *What is this? Why might it be relevant? What relationship is proposed? What evidence supports it?* The author may **Explore**, **Adopt into working architecture**, **Dismiss**, or request alternatives. An unadopted suggestion leaves the main graph when the author changes focus; adopted working ideas persist. Collapsing a group hides visual complexity without changing its meaning or contents.

These choices are already established in conversation: progressive explanation **and** progressive authoring, proactive but author-governed suggestions, 2–3 local ghost branches, reversible navigation, and noncanonical suggestions. Owner decision selected here: an emotion-first default with **unrestricted alternative starting anchors**.

## 2. Approaches and tradeoffs

| Option | Benefit | Failure mode | Decision |
| --- | --- | --- | --- |
| Mandatory emotion → trope → structure wizard | Simple novice teaching | Controls creative order and obscures the graph | Reject |
| Continuous full-graph AI expansion | Wide exploration | Recreates clutter, risks cost and authority confusion | Reject |
| **Focused, reversible unfolding** | Local, explainable discovery; preserves graph-first creativity | Needs careful persistence/status semantics | **Select** |

The recommended emotion → trope → structure journey is **one suggestion for how to explore**, not a universal causal dependency or requirement. Alternative paths are equally legitimate.

## 3. Three independent state dimensions

Distinguish **authority**, **visibility**, and **evidence**. Never let visual treatment imply canonical status.

- **Authority:** `agent_proposal` (unadopted, noncanonical), `author_working` (editable, durably saved in CanvasStore), and `knowledge_reference` (attributed read-only genre information). An **accepted story fact** remains under its existing explicit author/review authority, never inferred from adoption.
- **Visibility:** `focused`, `locally_revealed`, `collapsed`, `hidden`. Visibility never affects ownership or persistence.
- **Evidence:** `author_intent`, `source_backed_proposal`, `verified_pack_rule` if an actual pack is attached, `legacy_contract`, `model_hypothesis`, `unknown`. A source-backed proposal is not canon, and intended reader emotion is not guaranteed audience reaction.

Use labelled dashed cards for suggestions, distinct persistent working nodes, and explicitly attributed read-only knowledge. Labels, keyboard navigation and source descriptions must convey state without relying on color alone.

## 4. Interaction and authoring flow

1. Blank graph shows a **compact starting anchor**: “What should readers experience?” and a nearby “Start elsewhere” choice. Creating the anchor is an explicit editable *working* item, never canon.
2. Selecting an anchor focuses the relevant graph neighborhood. Show **up to 3 local ghost branches** on desktop and initially 2 on narrow mobile. Example: Joy through generous heroism → *Earned Breakthrough*, *Generosity empowers others*, *Restoration after loss*. All are illustrative hypotheses unless specifically supported by actual candidate evidence.
3. Clicking a ghost **inspects** its meaning, proposed source-local relation, potential effects, caveats, and provenance. It changes neither CanvasStore nor accepted story.
4. **Adopt** explicitly copies the selected suggestion into an editable working architecture node with an origin pointer. The author can edit it in place and then unfold its own neighbors. Adoption does not invoke accept/canon, and a duplicate click cannot create a second copy.
5. **Dismiss** hides only that focus-local suggestion, not a working node. The dismissal should remain effective across refresh for that same source revision as a presentation preference; it does not delete any source.
6. Changing focus removes other unadopted ghosts from the main canvas. Adopted nodes stay. “Unfold alternatives” expands choices in a bounded explicit explorer instead of silently crowding the graph.
7. A changed premise/emotion or regenerated candidate marks dependent unadopted suggestions **stale / needs reconsideration**, without automatically deleting or rewriting downstream author-owned work.
8. Compact/collapse grouped adopted nodes visually; allow expanding groups and returning to the selected concept, preserving semantic-link Back/context/focus behavior.

**Relationship claims are explicit:** a proposed trope may support an emotion, but a genre's emotional target does **not** mean that every trope causes that emotion. Two genres may assign distinct roles to the same trope. An absent Genre Pack cannot establish genre exclusion, originality, or a rule violation.

## 5. Source and model generation policy

**Stage A: proactive discovery from already available evidence.** Select up to 3 suggestions from the current architecture candidate, already supplied host-agent suggestion response, explicit source-linked edges, or verified pack evidence. Prefer direct declared relationships, variation in creative function, and candidates not already adopted or dismissed. Do not deduce a causal link by word similarity. If there are no justified candidates, show “No supported suggestions for this focus yet” with the next available action. Rendering and focus changes perform **zero invisible provider calls**.

**Stage B: fresh AI suggestions through the existing host-agent contract.** A “Develop more possibilities” action prepares a bounded, exact focus + revision + author-goal-scoped host-agent request. Validate candidate roles, reasoning, provenance and source IDs on response. The current host-agent workflow owns invocation; there is no new parallel model provider or silent paid request. Optional proactive *prefetch* requires a separate session-level consent/provider/budget contract, not authorized by this design alone.

This is honest about the existing host-agent-first runtime: “proactive” means visible local suggestions immediately where evidence exists, not a promise that a provider is already running.

## 6. Persistence and canonical boundary

**Existing source:** `src/auteur/beginner/studio_store.py` uses `CanvasItem` kinds `note|character|scene|place|question`, stores working positions/connections, and applies `replace-working-document` with revision/idempotency checks. Current Architecture candidate projections are **read-only**. Do not introduce a second canonical meaning store.

**Proposed minimal optional working-document schema extension:** keep existing `CanvasItem.kind`; add nullable `architecture_role` (emotion/trope/structure/genre/premise/theme/conflict/setting/relationship/other) plus a bounded nullable `proposal_origin` with source request SHA and source-local reference. Existing canvases default to null and remain loadable. These fields describe **working author ideas**, not accepted genre facts or canon. Any author edit makes the origin historical provenance, not a claim of unchanged source meaning.

Adoption is an explicit, atomic CanvasStore operation (reuse existing command/revision machinery), with a stable request identity and duplicate-source guard. Save failure leaves the item **unadopted** and surfaces a recovery action; no success UI until the store confirms the revision. Suggested edges are not silently persisted as authored assertions: relationship adoption, if offered, requires a clear independent confirmation.

Save focus, collapsed groups and dismissed-ghost IDs as canvas/revision-scoped *presentation preferences*, not secret authoring content. A source request SHA change invalidates stale ghosts and their display cache, never adopted notes. Preserve working-note text, caret and Story Realization selection on tab/workspace transitions.

## 7. UX hierarchy, navigation and accessibility

Retain **one spatial graph** and one compact explainer at a time. Suggestion branches are positioned in a clear local arc without covering the focused node or adopted neighbors. On narrow screens use two stacked choices and no horizontal overflow. Avoid new permanent sidebars, popover farms, and repetitive graph clones across Genres/Tropes/Structure.

Reuse the semantic-navigation links, context and bounded Back/history already developed in #398–#403; do not create competing routing histories. Keep full-graph mode, filters, local focus, collapse/expand and keyboard/tab order reversible. Respect reduced motion. “Source / hypothesis” information opens on explicit inspection. An unfocused or empty graph has an understandable next action.

## 8. End-to-end acceptance and adversarial scenarios

- **Emotion-first paladin:** Enter Joy through generous heroism → 2–3 provisional options → inspect why Earned Breakthrough *might* help → adopt → edit → unfold structural possibilities → visit the genre explanation → return to original focus. Accepted story must remain unchanged.
- **Nonlinear author:** Start from a premise or character. Never require emotion selection. Later add or revise emotional targets without deleting author-owned plot structure.
- **Mixed genres and provenance:** One trope can have different genre-relative roles; unavailable Pack rules remain unknown; conflicting proposed mechanisms are labelled alternatives, not automatically reconciled.
- **Many nodes:** Repeated focus shifts never accumulate ghost branches globally; collapsing groups retains every working node. At 390px, visible controls and labels remain usable.
- **Failure and authority:** Unknown/deleted focus, stale SHA, double Adopt, revision race, save failure, refresh, Back/Forward and return to Realization do not corrupt or duplicate working content. Ghost exploration triggers no working-document writes; adoption triggers one explicit working save, not canon acceptance.
- **Actual verification:** test pure suggestion-selection/ID logic; Python CanvasStore schema/backward-compatibility/idempotency; real served Studio HTTP; desktop/intermediate/mobile browser, keyboard, focus, persistence reopen, high-density graph, and author-centered tasks. Inline browser harness is not a substitute for the real server.

## 9. Implementation program boundaries

This crosses presentation, durable authoring and host-agent orchestration. Decompose into separate tested responsibilities:

1. **Isolated interaction prototype:** focused reveal, contextual ghost explanation, adopt/dismiss, local density/collapse, emotion-first alternative anchors. Synthetic fixture only; no production persistence claim.
2. **Working architecture integration:** optional CanvasStore role/provenance schema, atomic/adversarial adoption, duplicate prevention, working-note preservation and stale-source rules. No new canonical owner.
3. **Studio and host-agent handoff:** reconcile open PR #386–#403 lineage; compose graph and explanatory lenses, real source-scoped suggestions, scoped host-agent requests, mobile/keyboard/runtime tests. Only qualify and merge production integration when real story persistence is demonstrated.

**Non-goals:** mandatory wizard, always-on provider background generation, changing accepted story directly, new genre/trope canonical ontology, invented Genre Packs, total graph-engine replacement, predictive “creativity score”, and a new independently persisted architecture story store.

## 10. Review questions and explicit owner decisions

Owner selections already made: **both creation and explanation**, **proactive locally presented suggestions**, **2–3 ghost branches around the focus**, **author-controlled adoption**, **reversible exploration**, and **progressive visual density**. Default to emotion-first with a free choice of other entry points. Keep the graph as the central UI. Adopted working != canon. Provider calls are never a side effect of passive navigation.

**Remaining review boundary:** The decision to extend CanvasStore's noncanonical working item schema and the exact host-agent auto-prefetch consent policy affects ownership and user-visible semantics. Treat this document as a design proposal, not approval to implement; review before a step-by-step coding plan.