# Living Story Studio — Graph-First Beginner Experience

**Date:** 2026-10-09
**Status:** owner-selected product/interaction direction; construction is incremental and evidence-gated
**Scope:** local-first Beginner browser only
**Source baseline:** main at 85374e705115ec4884b8e0c85f3f69b6fe1c342a
**Authority:** UX/projection contract; not a new narrative layer, automatic acceptance mode, or release authorization.

## 1. Outcome and thesis

The first Auteur surface is a spatial story canvas. An author can record an idea, character, setting, scene, question, or fragment without committing to a premise or knowing the internal semantic layers. Nodes and links represent *working author material* unless bound to exact accepted sources. The canvas helps authoring; it never owns canonical story meaning.

A writer can reach prose directly from a scene. Graph-based explanations then make relationships, continuity, and change consequences visible when useful. A focused editor remains preferable to miniature prose nodes.

The design is not a mandate to replace the current Beginner UI before a comparative workflow establishes value. Ship initially as an opt-in, reversible Studio. The current Browser and CLI remain supported.

## 2. Owner-selected interaction decisions

| Decision | Selected behavior |
| --- | --- |
| Primary navigation | Interactive canvas from the first session |
| First action | Free-form note, character, place, scene, or optional premise |
| Default node | Unstructured note; semantic typing is optional |
| Working edges | Associations with optional author-supplied meaning |
| Layout | Presentation-only positions and viewport; never semantic authority |
| AI/projection nodes | Source-bound and explicitly provisional or accepted |
| Writing | Inline micro-edits; expanded scene/manuscript editor for real prose |
| Story views | Create first; Relationships and Consequences when value demonstrated |
| Scaling | Focused subgraphs, search, grouping and semantic zoom, not an all-nodes hairball |
| Interaction | Pointer plus keyboard/assistive-technology alternatives |
| Backend | Current local HTTP API and existing narrative owners |
| Rollout | Opt-in feature/route; preserve fallback; cut over only after qualification |

## 3. Author mental model

1. Capture anything without naming or categorizing it.
2. Place and connect it to other ideas.
3. Inspect relevant narrative relationships without filling in missing facts.
4. Write directly from a scene node.
5. Review what prose discovered and deliberately choose what is worth keeping.
6. See accepted history and consequences without operating backend lifecycles.
7. Return after days or weeks to recognizable focus, manuscript and next action.

The UI must not demand a graph before first prose or translate a drag gesture into authorial commitment.

## 4. Distinguish five concepts

- **Working item:** author-created note, prose fragment, scene intent, or proposed entity. Durable but noncanonical.
- **Working connection:** an author-drawn link; unlabeled means association only. A label is not proof.
- **Derived element:** reconstruction from existing accepted/provisional sources, carrying its source id, revision/freshness, and authority status.
- **Visual layout:** positions, collapsed groups, zoom and focus. It cannot change story meaning.
- **Accepted story state:** exclusively owned by the existing Story Direction, Identity, Structure, Realization, Expression, relationship and Book/Series workflows.

A visual selection, connection creation, node move, inferred type, or generated suggestion never accepts a narrative change. Never introduce a Studio-specific is_canon flag as an authority alternative.

## 5. First-session contract

- Initial UI is a canvas with a friendly 'What story do you want to tell?' prompt and 'Add anything' affordance.
- No-premise entry is real. A standalone working canvas may exist before a Beginner SessionEnvelope (which currently requires a premise).
- First interaction may be free-form note, typed note, character, setting, scene, or story idea.
- If a premise is entered, a small initial constellation may be proposed: roughly three to six evidence-backed items; missing facts remain missing.
- The author may write first or shape first; these converge on the same existing owners.
- 'Write this scene' launches the current Quick Draft or chapter workflow with an explicit provisional premise and first-scene intent as needed.
- Pending host-agent requests, failure and recovery must retain exact source/response identity and must not imply prose has arrived.

## 6. Canvas actions and authority

| Interaction | Allowed effect |
| --- | --- |
| Create/edit/delete working note | Update working canvas with recoverability |
| Create/remove working connection | Update working canvas, not canonical relations |
| Drag/pan/zoom/group/filter | Presentation change only |
| Inspect existing relation | Read projection with explicit source, meaning and uncertainty |
| Inspect historical Chapter/Book | Read current source-backed orientation |
| Propose accepted meaning change | Invoke existing owning proposal/revision flow |
| Accept meaning change | Existing explicit author acceptance boundary only |
| Preview downstream change | Read derived impact; never mutate affected history |

No hidden auto-accept and no shadow state.

## 7. Data and persistence admission

First demonstrate the real no-premise/reopen task and inspect whether existing stores can express it. SessionEnvelope requires a nonempty premise; avoid stuffing arbitrary notes into it or inventing a fake premise to bypass that requirement.

If evidence confirms the gap, admit the smallest **noncanonical working-document** store in the Beginner product boundary, not a new semantic layer:

- Stable canvas id, document revision and schema version.
- Author-entered working item id/title/body/optional presentation kind/origin/source.
- Working connection id/source/target/author description.
- Independent layout positions/viewport/focus.
- Optional linkage to a real Beginner workspace.
- No duplication of source-backed accepted story payloads as truth.

Writes must be atomic, version-checked, idempotent on replay, local-only, path-safe, and recoverable. One browser tab must not silently overwrite a newer edit in another tab. Store meaningful content durably, not exclusively in browser localStorage. Derived graph nodes remain rebuildable.

A failure to establish this need is a stop condition, not an excuse to add a speculative persistence subsystem.

## 8. Composition and ownership boundaries

- Browser: plain-language interaction and display.
- Beginner product: noncanonical working session/orchestration and derived projections only.
- Story Lenses: interpreted narrative orientation, not independent canon.
- Relations: existing relations.yaml / change application for canonical relationship state.
- Impact: read-only dependency and consequence projection.
- Expression: existing exact-draft review and Chapter/Book acceptance.
- Quick Draft: existing host-agent-first backend-neutral generation and recovery.
- Series Map/Focus: derived, source-revision-bound history; never parallel canonical storage.

The graph does not calculate story truth from screen coordinates or edge color.

## 9. Implementation stages (separate semantic PRs)

**P0 — UX and isolated canvas:** document authority contract; opt-in Browser Studio; pan, zoom, keyboard traversal, note creation/editing and simple connections; do not mutate existing story services.

**P1 — Working durability:** qualify no-premise persistence requirement, implement bounded local store and API; idempotency, version conflicts, atomic writes, and recovery.

**P2 — Prose:** scene selection, scene intent and expanded editor; reuse Quick Draft/host-agent states, exact source binding and selected discoveries; preserve navigation state.

**P3 — Existing story projections:** Story Lenses, character relationships, source evidence, relevance focus; show unestablished and stale honestly.

**P4 — Consequence preview:** source-backed selective impact projections, separate prospective intent from revision to accepted history; use existing authority owner for change.

**P5 — Book scale:** Chapter/plot grouping, time-aware relations, focused subgraphs, Book orientation and meaningful next action.

**P6 — Qualification and cutover:** compare against current Beginner UI and Markdown/LLM where available; test authors' comprehension/value separately from mechanics; promote Studio to default only after evidence and release approval.

A completion claim for an earlier stage does not authorize speculative construction of all later stages.

## 10. Minimum prototype acceptance scenarios

1. On the first session, add a free note without a premise or mandatory node type.
2. Rename and move a note: only the note changes semantic content; moving it changes layout only.
3. Connect two notes: no canonical relationship appears.
4. Open a working scene: reach editable prose without accepting Story Identity first.
5. Reload/reopen: recover text, connections and spatial orientation without losing prior work.
6. A second tab edits old version: report conflict, preserve newer content.
7. Derived relationship: explain source/meaning and mark stale when source changes.
8. Accept selected creative discovery: run the owning existing workflow; unselected suggestions stay noncanonical.
9. Change an accepted Chapter event: preview impact without changing dependent accepted Chapter bytes.
10. Reopen a six-Chapter Book: identify current chapter, accepted changes, pending updates and one useful next action.
11. Keyboard-only user can create, locate, connect, edit and inspect elements.
12. Existing Beginner Browser/CLI golden paths remain functional.

## 11. Qualification and claim ceiling

At every changed boundary test real browser control -> HTTP/API dispatch -> existing owner -> persistent result; static DOM/substring tests alone do not close an integration claim.

Use local-first tests by default; do not assume GitHub Actions credits. Distinguish code inspection, test evidence, runtime provider behavior and human preference.

The active F2/X3 controlled six-Chapter evidence mission (#318), host-agent Quick Draft dogfood (#310), and protected owner-only governance work (#338) retain their separate authorities. A graph prototype must not claim to close, bypass or preempt those gates.

**Promotion law:** graph-first preferred product direction != tested usability != integrated implementation != qualified default != release.

## 12. Stop and escalation boundaries

Stop or narrow scope if meaningful node edits cannot be persisted safely, if Studio introduces independent canonical authority, if a provider/environment cannot fulfill the existing Quick Draft handoff, if a new data model is not warranted, or if a real author task is made worse by mandatory node manipulation.

Choose lowest owning repair before adding complexity. Preserve an inspectable current Browser fallback until author benefit and accessibility are substantiated.
