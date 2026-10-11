# Living Story Studio — Graph-First Beginner Experience

**Date:** 2026-10-09
**Status:** owner-selected product/interaction direction; construction is incremental and evidence-gated
**Scope:** local-first Beginner browser only
**Source baseline:** main at 85374e705115ec4884b8e0c85f3f69b6fe1c342a
**Authority:** UX/projection contract; not a new narrative layer, automatic acceptance mode, or release authorization.

## 1. Outcome and thesis

The first Auteur surface is a spatial story canvas. An author can record an idea, character, setting, scene, question, or fragment without committing to a premise or knowing the internal semantic layers. Nodes and links represent *working author material* unless bound to exact accepted sources. The canvas helps authoring; it never owns canonical story meaning.

A writer can reach prose directly from a scene. Graph-based explanations then make relationships, continuity, and change consequences visible when useful. A focused editor remains preferable to miniature prose nodes.

**Product decision update (2026-10-10):** Graph-first Studio is the **selected target default**, superseding the previous blanket opt-in-until-comparative-value policy. After essential real-browser/local safety checks, promote Studio as a reversible **development default**, then qualify early-user beta separately. A broad release remains a distinct decision. The previous Beginner Browser and CLI remain supported as fallbacks. See [Staged Default and Fair-Baseline Decision](../product-validation/living-story-studio/2026-10-10-staged-default-product-decision.md).

## 2. Owner-selected interaction decisions

| Decision | Selected behavior |
| --- | --- |
| Primary navigation | Interactive canvas from the first session |
| First action | Free-form note, character, place, scene, or optional premise |
| Default node | Unstructured note; semantic typing is optional |
| Working edges | Author-drawn associations remain working; Relations view includes them alongside separately marked source-bound, read-only relations |
| Layout | Presentation-only positions and viewport; never semantic authority |
| AI/projection nodes | Source-bound and explicitly provisional or accepted |
| Writing | Docked scene/manuscript editor alongside canvas, optional distraction-free full-width mode; source-bound Quick Draft handoff stays explicit |
| Story views | Create first; Relationships and Consequences when value demonstrated |
| Scaling | Focusable working groups, group-based arrangement, real visible-bounds Fit and bounded placement; do not claim an infinite canvas |
| Interaction | Pointer plus keyboard/assistive-technology alternatives |
| Backend | Current local HTTP API and existing narrative owners |
| Rollout | Selected target default; promote to reversible development default after essential safety qualification; retain fallback; beta/broad gates remain distinct |

## 3. Author mental model

1. Capture anything without naming or categorizing it.
2. Place and connect it to other ideas.
3. Inspect relevant narrative relationships without filling in missing facts.
4. Write directly from a scene node.
5. Review what prose discovered and deliberately choose what is worth keeping.
6. See accepted history and consequences without operating backend lifecycles.
7. Return after days or weeks to recognizable focus, manuscript and next action.

The UI must not demand a graph before first prose or translate a drag gesture into authorial commitment.

### Discovery-first interaction refinements (2026-10-10)

- **Create / Connect / Write** stay on the primary toolbar. Source IDs, import/export, Book and impact tooling remain available behind More tools rather than occupying the initial creation surface.
- **Relationships** includes author-created connections and connected working items; source-derived relationship nodes stay visibly dashed/read-only. Source evidence is available only when an existing workspace is explicitly loaded. Working edges never become accepted relationships through canvas edits.
- **Continuity** restores the last working selection, available view, group, editor mode and prose caret from browser-local *presentation preferences*; positions and zoom remain durable CanvasStore fields. Manuscript text is never stored only in browser preferences.
- **Writing** uses a docked scene editor, an optional wide focus mode, and an explicit one-click copy of existing scene notes into editable generation intent. A premise remains required for an actual Quick Draft request; it is not invented from unspecified material.
- **Spatial work** uses visible-content Fit and group focus/rearrangement. Default insertion remains inside the accepted position bounds; bounded prototype limits are explicit and not a mandate to build new graph infrastructure.
- **Claim ceiling** remains a candidate UX implementation; source inspection or simulated interactions do not prove browser reliability, accessibility or felt author value. A disposable scratch project is appropriate for exploratory inspection, not valuable manuscript storage.

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

**P6 — Staged adoption:** allow immediate disposable first-look sandbox feedback before safety-verified routine use; distinguish product-owner-selected direction, essential safety-verified development default, everyday-qualified beta default, and separately authorized broad release. Evaluate comparative author value when it could change the decision, but do not treat a population preference study as mandatory for reversible development adoption. Preserve fallback and explicit authority boundaries.

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

## 11. Discovery, qualification and claim ceiling

### First-look sandbox launch

From a checkout containing the **Studio draft branch** (not current `main`), with Auteur installed as described in the [README](../../README.md), open Studio against a disposable directory. For Windows PowerShell:

```powershell
$scratch = Join-Path $env:TEMP "auteur-studio-ux-scratch"
New-Item -ItemType Directory -Force -Path $scratch | Out-Null
python -m auteur.beginner.server --project $scratch --port 8765
```

Open **http://127.0.0.1:8765/studio.html**. No default-interface flag, host-agent provider or completed #360 qualification is required to *look at* an isolated sandbox prototype. This command is a launch recipe, **not an executed startup claim**. Use the disposable project only; do not rely on it for important prose before trusted-use checks.

Try adding and moving a note, connecting two characters, writing a scene, and navigating back. Prioritize direct author observations over another simulated test harness; record what actually felt confusing or useful and iterate quickly.

### Evidence thresholds

**Discovery:** a runnable/clickable sandbox plus direct author feedback is sufficient to decide what layout or interaction to change next. Lightweight checks may resolve a concrete startup or destructive-isolation issue; no formal test package, qualification issue, or frozen hash is mandatory just to inspect the UI.

**Stabilization / trusted writing:** to claim reliable persistence or promote the development default, execute the changed real Browser → HTTP/API → existing owner → persistent result path, including recovery and narrative-authority safety. Static assertions and simulated DOM behavior do not establish that stronger claim.



Use local-first tests by default; do not assume GitHub Actions credits. Distinguish code inspection, test evidence, runtime provider behavior and human preference.

The active F2/X3 controlled six-Chapter evidence mission (#318), host-agent Quick Draft dogfood (#310), and protected owner-only governance work (#338) retain their separate authorities. A graph prototype must not claim to close, bypass or preempt those gates.

**Promotion law (revised 2026-10-10):** selected product direction != executable safety PASS != development default != early-user beta != broadly qualified release. Safety checks are mandatory for author work; universal UX superiority is not a prerequisite for a reversible development default.

## 12. Stop and escalation boundaries

Stop or narrow scope if meaningful node edits cannot be persisted safely, if Studio introduces independent canonical authority, if a provider/environment cannot fulfill the existing Quick Draft handoff, if a new data model is not warranted, or if a real author task is made worse by mandatory node manipulation.

Choose the lowest owning repair before adding complexity. Preserve a usable current Browser fallback through reversible development/beta adoption; decide retirement later against observed benefits, accessibility and migration evidence. Do not treat the old UI as the presumed mature UX standard.


## 10. Story Vision and agent-generated whole-story architecture (owner-selected 2026-10-11)

**Purpose:** The primary authored input is a flexible story vision, not a manually constructed graph. Authors may start from target reader experience, aesthetic framing, tropes, genre progression, structural identity, a premise, or free prose. All fields except some meaningful authored text remain optional. Do not fabricate a premise to satisfy the separate DiscoveryBrief contract.

**P1 — Vision:** A single working Story Vision item in the existing noncanonical CanvasStore is durable, editable, and recoverable. The vision entry does not create Story Identity, a Story Lens command, or a second semantic layer.

**P2/P3 — Active coding agent and projections:** A backend-neutral host-agent request/response handoff uses exact request identity, source-state fingerprint, and version-aware completion. Proposals are candidate-only; their nodes/relations are validated and projected as noncanonical architecture evidence. Author edits stay in working state. No model-provider credential is necessary for the handoff, and a browser alone does not pretend it can invoke an absent host agent.

**P4 — Genre trajectory:** Separate the global governing genre/promise (Identity), local genre emphasis and overlapping narrative phases (Structure candidates), intended reader emotion (TargetExperience), and aesthetic modulation. A local genre interval is not automatically a new global genre commitment. Preserve unknown length, transitions, and parallel phases.

**P5 — Long horizon:** Use focused derived views across scope and phase rather than inserting every story element into the 200-item working canvas. A derived graph never becomes a universal ontology or canonical store; Source Identity/Structure/Realization/Series owners remain authoritative.

**P6 — Revision:** The agent may propose a targeted architecture revision, explain material differences and affected relationships, and retain earlier proposals. Revising working architecture does not change accepted story meaning; upstream changes must pass explicit existing owner actions. Stale requests cannot apply to current working material.

**Acceptance sequence:** author-editable no-premise vision → exact host-agent request and validated response → readable connected candidate graph → temporal genre/reader timeline → scope focus → bounded revision with impact preview. Test the concrete Browser/HTTP/store/host-agent boundaries before trust, not a new omnibus UX gate. No automatic acceptance, auto-publication, new provider configuration, or broad release.


### Host coding-agent handoff — operational recipe

The Browser is local and vendor-neutral. It **does not possess a callable parent-agent SDK**;
the Develop Architecture action prepares a request, not an automatic model call.
Run it inside a coding-agent environment that can read the local project, fulfill
the prompt, and submit an exact response. Current paths:

1. In Studio save Story Vision (no premise required), then click **Develop architecture with coding agent**.
2. The agent fetches GET /api/beginner/studio/canvases/{canvas-id}/architecture
   on the local Auteur server or reads the request under
   .auteur/beginner/studio/canvases/{canvas-id}/architecture/requests/.
3. The agent answers the request's system and user prompt with raw JSON
   matching the typed ArchitectureCandidate contract, without inventing author intent.
4. Host code wraps that exact JSON using build_host_agent_response from
   auteur.host_agent, passing HostAgentRequest(**status["request"]).
5. Submit the complete response object with POST to
   /api/beginner/studio/canvases/{canvas-id}/architecture/host-agent-response.
   The Browser can also accept pasted HostAgentResponse JSON as a fallback.
6. Click **Check agent result**. The proposed graph and genre timeline remain
   noncanonical; Copy as editable working idea preserves manual author freedom.
7. To revise, enter an instruction and request a revision. The response is **staged**,
   with node/link/phase difference preview. Click **Apply to working architecture**
   only if the proposal is desired. It never accepts Identity/Structure.
8. If source content changed, stale-response and stale-review checks block applying;
   inspect the retained request evidence and prepare a fresh request.

The agent should prefer a small readable architecture over 80 decorative nodes,
retain stable IDs on revision, and use Book/arc/chapter scopes and focused
neighborhoods rather than packing an entire long-running series onto one screen.
This is an operational handoff contract, **not** a claim of live-provider,
real-browser, or human-usability qualification.


For a local coding-agent operator, the simplest completion path is the built-in
CLI bridge. The canvas id appears in the Studio URL after the canvas is opened:

~~~powershell
python -m auteur.beginner.studio_architecture --project $scratch --canvas $canvasId show
# Host coding agent reads the printed system/user request, reasons, and writes raw candidate JSON.
python -m auteur.beginner.studio_architecture --project $scratch --canvas $canvasId complete-file --candidate .\candidate.json
~~~

The CLI validates and records the generated proposal through the exact same
host-agent response path as the Browser. A revision remains staged for explicit
working apply. Do not mistake a prepared request or synthetic candidate for
a live coding-agent invocation or independent creative-quality evidence.

## 13. Emotion-first architecture and distinct Story Realization (2026-10-11)

**Owner-selected correction:** Studio's *Narrative Architecture* action designs the machinery
of a story, **not** named characters, locations, factions or a proposed sequence of
specific plot events. Concrete material belongs in a separate author-facing *Story
Realization* workspace. A working proposal may mention user-supplied concrete terms,
but must not invent more of them to fill an architecture graph.

For this product iteration choose six **basic-emotion labels** as the working vocabulary:
`joy`, `sadness`, `fear`, `anger`, `disgust`, and `surprise`.
An optional complex emotion references two or more of those labels together
with a contextual interpretation. These are **narrative design approximations**,
not scientifically proved emotional equations, neural readouts or fixed percentages.
Do not force a complex-emotion annotation on every genre or scene. This chosen
model remains replaceable if actual authoring evidence warrants it.

The **genre contract** of this particular story links specific reader-directed
emotional targets, possible eliciting conditions, aesthetic strategies, trope
functions, renewable engine, structural pattern and payoff expectations.
Typed **genre interactions** explain reinforcement, enablement, constraints,
contrast, tension and convergence. A genre label alone is not integration.
The **composition timeline** references genre contracts and specifies active
mechanisms and targeted basic emotions in each interval. It supports genuine
pivots, overlaps, recurrence, unknown boundaries and stable global roles.

The **Narrative Architecture** tab projects these mechanisms and emotions,
with no invented concrete plot. The **Story Realization** tab develops actual
characters, locations, factions, events, plots, scenes and prose as working
proposals, traceably linked to relevant architecture. Neither tab creates a
canonical story owner. Unexpected concrete discoveries can generate an upstream
architecture revision proposal; they never silently mutate Identity or Structure.

**Delivery:** architecture-only agent contract → emotion/genre schema → inspector
and composition timeline → distinct connected tabs → realization agent handoff
→ bidirectional sourced revision. Keep current v1 candidate proposals readable,
and validate any new v2 candidate with stable IDs and strict links. Prioritize a
usable author interaction over process multiplication; preserve narrow real
Python/HTTP and Browser qualification ceilings before trusted use.
