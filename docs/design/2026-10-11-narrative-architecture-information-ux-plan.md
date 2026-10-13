# Narrative Architecture Studio — Information Hierarchy and High-Density UX

**Decision date:** 2026-10-11  
**Status:** Owner-selected UX direction; UX-0–UX-5 implemented on stacked draft PRs #387–#392, not merged or runtime-qualified  
**Target:** Living Story Studio, local-first Browser, Narrative Architecture workspace  
**Baseline:** Stacked experimental Studio branch ending in PR #385; preserve PR #375–#385 capabilities  
**Owner boundary:** Presentation/projection only; no new narrative authority, canonical state, rollout or merge decision.

## 1. Problem and intended outcome

The graph-first Studio now creates useful emotion-first architecture proposals, but the author must scan unrelated controls, long emotion paragraphs, crowded generic nodes/edges, and horizontally overflowing phase documents to understand the design. The screenshots from the 2026-10-11 paladin progression-fantasy session demonstrate valuable *content* but weak *information hierarchy*.

The product goal is **high useful information density with low simultaneous interpretive load**. Preserve deep content, agent-first node construction, manual optional editing, spatial exploration, source provenance and an independent Story Realization workflow. Do not simplify the narrative model to simplify its UI.

**First-screen focal point:** the **interactive architecture graph**, not a marketing-style hero banner, long Story Vision form or expanded textual report. A compact Story Vision summary supplies context; the adjacent facet navigator and contextual inspector supply orientation and detail.

**Distinguish two responsibilities:**
- **Section contents:** What is known or proposed about an emotion, genre, trope or structure?
- **Cross-section relationships:** How does that component contribute to, depend on, constrain, contrast with or transform other components?

Both must be directly navigable. Four isolated detail panels do not solve the relationship problem.

## 2. Confirmed implementation baseline and observed issues

The current candidate already exposes six basic-emotion targets, optional complex compositions, genre contracts with trope functions and structural patterns, typed genre interactions, candidate nodes/links and genre phase activations. Story Realization is a separate author-facing workflow, and proposals are not accepted story.

Current UI gaps to correct:

| Observation | Concrete implication |
| --- | --- |
| Emotional Design appears as a block of ungrouped paragraphs | Convert to browsable compact summaries; full text lives in an inspector |
| Trope functions appear within genre contracts, phase text and some graph nodes | Introduce a dedicated **Tropes** facet without duplicating the source of truth |
| Structural patterns, engines, phase functions and structure nodes are scattered | Introduce a dedicated **Structure** facet, distinct from concrete plot |
| Genre interactions and other graph connections look similar | Add a small, consistent relationship grammar with readable meanings |
| All candidate nodes share nearly identical purple styling | Encode semantic category, selection, and proposal status separately |
| Timeline cards repeat full genre mechanisms and interactions | Render concise local variation; reference the reusable global genre contract |
| An editable Story Vision note can remain selected in the architecture inspector | Make the inspector respect the active workspace and current visible selection |
| The Realization action bar appears in Architecture in the provided screenshot | Fix hidden-state behavior; shared .architecture-actions {display:flex} requires a reliable [hidden] rule |
| Large Story Vision and tool rows push the graph down | Compact and collapse secondary material after saving, without hiding it permanently |

These are UI/presentation findings. They do not establish failure of the emotion theory, agent-generated narrative architecture or existing backend ownership.

## 3. Selected information architecture

Maintain two **primary workspaces**: Narrative Architecture and Story Realization. Inside Narrative Architecture, expose one coordinated exploration system:

- **Overview:** default focused graph with a short story-architecture summary.
- **Emotions:** the six chosen basic emotions, optional complex compositions, intended effects, eliciting conditions and aesthetic strategies.
- **Genres:** governing/supporting roles, contextual genre contracts, emotional targets, narrative engines, trope functions, structural grammar and payoffs.
- **Tropes:** each identified trope and its narrative *function*, related genres, intended emotions, and role in structure. Not a mere trope-name inventory.
- **Structure:** renewable engines, structural patterns, escalation, temporal functions, convergence, setup/payoff intentions and genre modulation. No unsolicited named acts or plot events.
- **Timeline:** an alternate temporal projection over these same components, not an independent narrative database.

Use compact facet navigation (rail on wide screens; accessible dropdown or tabs on narrow screens). Switching a facet changes graph emphasis and inspector defaults; it must not delete unrelated nodes or accepted working context. Include **Show related** and **Show all** actions so cross-facet paths remain inspectable.

**Shared narrative anchors:** the author's Story Vision and the current working architecture summary remain easily reachable from either workspace, but neither occupies the main graph area by default.

## 4. Content and relationship semantics

| Facet | Primary content | Connections to expose |
| --- | --- | --- |
| Emotions | Basic-emotion targets, local/primary role, optionally composed complex emotion, eliciting condition and aesthetic strategy | Genre mechanisms and trope functions **intended** to evoke them; structural phases emphasizing them |
| Genres | Genre role, mechanism, aesthetic approach, structural pattern, trope functions, payoff | Emotions targeted, trope functions used, structure enabled, and typed cross-genre reinforcement/tension |
| Tropes | Name, contextual narrative function, variation, provenance | Genres employing the trope; emotional targets supported; structural functions it helps achieve |
| Structure | Engine, pattern, phase function, planned escalation or payoff | Genres supplying the mechanisms; emotions being modulated; tropes implementing structural functions |

Each relationship should carry an understandable verb: e.g. *uses*, *aims to evoke*, *enables*, *constrains*, *contrasts*, *transforms*, *converges* or an existing authored edge label. Keep **author-declared**, **agent-proposed**, **source-derived accepted**, **uncertain** and **stale** distinguishable. Edge color, spatial placement and proximity are NEVER evidence that a story fact was accepted.

Only show a relationship when its source contract/edge actually supports it. An appealing visual connection is not authorization to infer one. Do not create semantic edges by matching words in prose.

### Current contract limitation and minimum viable solution

The existing v2 genre contracts contain **trope_functions and structural_pattern as text**, not globally stable trope/structure identifiers. In the initial implementation:
- Show these as navigable, **source-linked read-only facets or inspector entries** of their owning genre/phase.
- Reuse actual ArchitectureNode IDs and actual edge/contract references where they exist.
- Mark an unlinked trope/structural phrase as locally scoped; do not pretend it is a shared canonical node.
- Introduce stable IDs or a backwards-compatible v3 optional reference only if a real user task needs cross-genre trope identity, cross-facet editing or persistence of those links. Keep older v1/v2 proposal files readable.

This meets the current visibility need without starting a competing universal ontology or duplicating semantics.

## 5. Visual hierarchy, layout, and interaction

Recommended wide-screen composition:

~~~text
[Workspace: Narrative Architecture | Story Realization]
[Compact Story Vision: one/two-line summary                    Edit / Expand]
[Primary action: Develop / Revise architecture             status / More]
+--------------+------------------------------------+-------------------+
| FACETS       | PRIMARY SPATIAL GRAPH              | INSPECTOR         |
| Overview     | Focused, readable nodes & edges    | Selected element  |
| Emotions     | Related items can expand on demand | Own content       |
| Genres       |                                    | Related elements  |
| Tropes       | [fit] [search] [focus] [all]       | Source / status   |
| Structure    |                                    | Relevant actions  |
| Timeline     |                                    |                   |
+--------------+------------------------------------+-------------------+
~~~

The graph is the **dominant visual work surface**. The inspector explains only the selected element, including its meaningful relations. The navigation offers orientation, not four permanently open multi-page columns. The timeline replaces the graph **within the primary work area**, rather than becoming another dense section above or below the graph.

On narrow screens: retain workspace switch, compact Story Vision, and a full-width graph; move facets and inspector into accessible collapsible surfaces. Do not shrink the graph to an unusable thumbnail or trap keyboard focus.

**Default:** Overview graph in Narrative Architecture. Story Vision collapses automatically after it has useful saved content, with a clear Edit/Expand control. The author may explicitly pin it open. Keep an optional immediately accessible blank-start capture path and Writing-first in the separate Realization workspace.

**Primary actions:** one contextually relevant Develop/Revise command, Check result/status, and lightweight view controls. Put request JSON, canvas technical IDs, impact internals, export/import and other specialist actions behind More tools or explicit advanced disclosure.

**Inspector precedence:** visible selected architecture node > visible derived source > neutral architectural orientation. A hidden working Story Vision selection must not show its editable relationship controls in Architecture; show its editor only on explicit Edit Story Vision or working-note selection in Realization.

## 6. Restrained category color and connection grammar

Initial **semantic category** palette (tokens, adaptable after checking contrast):
- **Emotions:** restrained coral/rose.
- **Genres:** muted purple.
- **Tropes:** amber/gold.
- **Structure/engines:** teal.
- **Other/unknown:** neutral gray.

Apply the same category tokens to the facet rail, graph, inspector headings, and temporal view. Avoid a new color for every emotion or individual trope. Use labels and small shapes/icons so users with color-vision differences do not lose meaning.

Encode **meaning** independently of status:
- Node shape/label/border accent: semantic category.
- Explicit badge/text or border pattern: agent proposal versus source-backed/accepted or stale.
- Selected outline: keyboard/pointer focus, not semantic acceptance.
- Edge: visible type label or accessible inspection; direction when supported; limited line styles for working association versus typed source relation.
- Edge visibility: dim unrelated relationships when focusing; never erase them or silently claim a broken dependency.

Avoid a full graph of all possible cross-category links by default. Show the selected item's immediate meaningful neighborhood; permit expanding more relationships and returning to Overview. Use an accessible relationship list as a nonspatial equivalent.

## 7. Timeline redesign: local modulation, not repeated genre essays

The temporal view should show *how* reusable contracts are activated across narrative intervals. It should not repeat every contract's global narrative engine in every phase.

**Compact phase default:** phase label, key active genre roles, basic-emotion targets, one locally relevant trope function, one structural purpose, and an indicator for overlap/pivot/uncertainty. Optional complex-emotion label where useful. Distinguish **global genre role** from **locally dominant role**.

**On selection:** inspector reveals the full phase-specific activation, causal interactions, aesthetic strategy, transition, open questions and links to the underlying genre contracts. Selecting a genre in a phase should jump to its global contract and allow returning to the same interval.

Preserve unknown lengths and overlapping/parallel intervals; order is not an invented chapter number. For the paladin example, do not reproduce "Progression Fantasy — Challenge, effort, growth..." in five separate columns: show "Progression: foreground" and the **distinct local reason**.

Begin with compact, selectable phase cards/rows and a timeline inspector. Adopt multilane/zoomable tracks only if observed scope/overlap tasks warrant their added complexity.

## 8. State and provenance

Presentation-only state includes active facet, selected architecture node, visible relationship filters, graph viewport/focus, selected timeline phase and inspector expansion. Reopening should restore meaningful focus or fall back to Overview if a referenced candidate disappeared. Existing working Story Vision persists in CanvasStore; browser-local display choices are not a second story-content store.

Agent proposals must remain source-bound and noncanonical. Preserve existing exact host-agent request/response identity, freshness, deterministic change preview and explicit working-review lifecycle. No spatial gesture, facet selection or colored edge accepts story meaning.

## 9. Sequenced engineering packages (small, reviewable PRs)

### UX-0 — Remove concrete workspace incoherence first

**Files:** studio.css, studio.js, focused existing browser tests.

- Enforce hidden-state styling for both action bars and contextual panels, including rules with display:flex.
- Make inspector content follow the active workspace/view and visible selection; restore neutral inspector on view switch.
- Hide Story Realization actions while in Narrative Architecture, and vice versa.
- Test hidden action bars, a lingering Story Vision selection, switching tabs, and reopen restoration.

**Done:** only the relevant workflow actions and inspector appear; existing working text survives.

### UX-1 — Make the graph the first-class focus

**Files:** studio.html, studio.css, studio.js; focused interaction assertions.

- Introduce lightweight Architecture heading/context and compact Story Vision summary with Edit/Expand.
- Reduce permanent command-bar clutter; move advanced controls to existing More tools.
- Allocate the remaining viewport primarily to the graph, with a clearly bounded inspector.
- Preserve graph-first first session and free-form authoring; do not impose four required entry forms.
- Make narrow-screen workspace/facet/inspector navigation responsive and keyboard accessible.

**Done:** at ordinary desktop size the author can inspect the graph without scrolling through the full emotional report; compact vision can reopen without losing text.

### UX-2 — Four coherent facet perspectives

**Files:** studio.js and HTML/CSS; optional small, pure projection helper and tests if needed.

- Add Overview/Emotions/Genres/Tropes/Structure navigation.
- Present six basic-emotion targets as compact rows/cards; optional complex compositions expand in the inspector.
- Present genre contracts as readable summaries; preserve contextual genre interaction inspection.
- Surface trope functions and structural patterns from existing contracts/phase data with honest scoped provenance.
- Enable contextual related-item traversal, including a way to return to the originating facet.

**Done:** the author can answer "what does this trope do?", "which genre uses it?", and "what emotional/structural function does it serve?" without navigating a wall of unrelated prose.

### UX-3 — Semantic visual encoding and readable connections

**Files:** studio.css, studio.js; focused visual/DOM accessibility checks.

- Introduce category color tokens and node label/category distinctions; retain neutral unknowns.
- Provide a compact visual legend and text/accessible equivalents.
- Style typed inter-genre links differently from generic working associations; expose their meaning in selection/edge inspection.
- Prefer grouped or neighborhood layout and predictable placement over another unbounded full-graph layout engine.
- Verify contrast, focus visibility, keyboard navigation and readable connection paths.

**Done:** category and connection purpose are distinguishable without opening every node; color is not the sole carrier of meaning.

### UX-4 — Compact temporal projection

**Files:** studio.js, studio.css, studio.html and timeline tests.

- Replace repeated genre contract essays with short interval summaries and emotion/role badges.
- Move complete activation/transition/genre-interaction explanations to contextual inspector.
- Link timeline phase → genre contract → relevant trope/structure/emotional target → back to phase.
- Preserve parallel intervals, unknown lengths, local roles and global governing commitments.
- Keep independent timeline focus when toggling back to graph.

**Done:** the paladin's five phases remain understandable on screen without five multi-paragraph columns; detailed information stays one selection away.

### UX-5 — Cross-perspective continuity and real interaction checks

**Files:** focused browser tests and the smallest repairs arising from them.

- Verify selection and scroll/zoom/facet/timeline preservation after reload and workspace switching.
- Verify author edits, architecture regenerations and pending host-agent responses do not reset unrelated focus or accepted narrative data.
- Exercise a dense long-book/series candidate and a genre-switching case with meaningful overlaps.
- Verify keyboard and small-screen alternatives; avoid turning these into a new broad test bureaucracy.
- Fix only observed regressions rather than starting an unrelated UI redesign.

**Done:** the same architecture is navigable through focused graph, facet and timeline views with no unintended story mutation.

**Delivery order:** UX-0 → UX-1 → UX-2 → UX-3 → UX-4 → UX-5. UX-2 and UX-3 may share one bounded PR when they rely on the same local projection. Each PR remains within the repository's 500-line / 12-file cap. Review and run relevant local tests instead of depending on GitHub Actions credits.

## 10. Representative acceptance scenarios

**A. Paladin architecture:** Starting with the previously provided paladin progression-fantasy premise, the agent's v2 architecture is shown as an Overview. Emotional targets are accessible through Emotions, genre contracts through Genres, trope purposes through Tropes, and escalating narrative mechanisms through Structure. No newly invented concrete names/events are needed.

**B. Cross-facet trace:** Select **Earned Breakthrough** (trope) → inspect which Progression Fantasy contract uses it → inspect intended **Joy** target and eliciting condition → inspect its Challenge/Effort/Growth structural function → return to the original selection. Where stable source references are absent, show scoped relationship and do not fabricate global identity.

**C. Genre composition:** A phase emphasizes Progression and another emphasizes Heroic Fantasy. Each interval shows *its own* local emotional and structural function; the global genre explanations appear once and remain discoverable.

**D. Competing genre mechanisms:** The user focuses on *increasing power may undermine suspense*. Typed link displays creates_tension/constraint and its explanation; corresponding reader emotions and structure remain navigable without every edge showing at once.

**E. Workspace boundary:** Architecture reveals only architecture controls and candidate inspector; Realization reveals concrete authoring and character/scene controls. No hidden panel occupies layout space. Switching does not destroy Story Vision or manuscript.

**F. Long-form recovery:** After focusing a nested book/arc neighborhood and a phase, reopening Studio restores that useful context, or presents a clear safe fallback if the item was superseded. Accepted data remains unchanged.

## 11. Verification and claim boundaries

- **Mechanical/source:** JS parse, DOM ID/control references, CSS [hidden] behavior, stable source references and deterministic projection tests. These do not prove visual usability.
- **Live Browser/HTTP:** Open current branch's Studio in a disposable local project. Inspect typical desktop and narrow viewport, interactions, state restore, real request/response loading, and working data retention.
- **Creative-quality probe:** Reuse actual paladin architecture and one long-form genre-changing story. Ask whether a specific author's relationship/navigation task has become easier; do not infer subjective satisfaction from generated fixture counts.
- **Regression focus:** test the exact failures shown in screenshots (simultaneous action bars, wrong inspector, graph pushed below content, repeated timeline text) and any fixes.
- **Safety:** proposal vs accepted distinction, source/stale states, explicit owner acceptance and Realization separation remain intact. No provider call or new canonical store is necessary for UX restructuring.

Document implementation status per package. **Plan accepted** is not **code implemented**; JS parse is not a real-browser validation; a draft PR is not a merge or release.

## 12. Non-goals and owner-selected decisions

- Do not replace the graph with a wizard, documents-only editor or fixed questionnaire.
- Do not split Emotions, Genres, Tropes and Structure into four competing databases.
- Do not create separate canonical owners for narrative architecture facets, timeline or layout.
- Do not add a universal score for good writing, arbitrary emotion intensity percentages or a different basic-emotion theory.
- Do not automatically invent concrete plot/characters during architecture exploration.
- Do not use color as the only source of meaning, or create a unique color per trope/emotion.
- Do not implement a sophisticated graph rendering engine or zoomable Gantt timeline without evidence that focused projections are insufficient.
- Do not require broad end-user qualification before reversible local discovery improvements; also do not promote to trusted manuscript use without necessary real Browser/persistence checks.

**Owner decisions selected for implementation:** graph is the visual center; Story Vision is compact but always editable; four facets are projections of one architecture; inspector shows selected detail and relationship paths; restrained category colors; timeline shows local differences, not repeated global contracts; cross-workflow authority stays explicit.

## 13. Delivery tracking (2026-10-11, connected GitHub implementation)

The following changes are **committed as stacked draft pull requests**, not merged into `main` or runtime-qualified:

| Package | PR | Committed scope |
| --- | --- | --- |
| UX-0 | [#387](https://github.com/ThorStarlord/auteur/pull/387) | Hidden controls, workspace-aware inspector and working-item routing |
| UX-1 | [#388](https://github.com/ThorStarlord/auteur/pull/388) | Architecture-first graph, compact Story Vision and responsive visual hierarchy |
| UX-2 | [#389](https://github.com/ThorStarlord/auteur/pull/389) | Overview/Emotions/Genres/Tropes/Structure/Timeline source-linked facets |
| UX-3 | [#390](https://github.com/ThorStarlord/auteur/pull/390) | Semantic category palette, labels, accessible relationship navigation |
| UX-4 | [#391](https://github.com/ThorStarlord/auteur/pull/391) | Compact local phase cards, selectable phase inspector and cross-links |
| UX-5 | [#392](https://github.com/ThorStarlord/auteur/pull/392) | Cross-facet history, search/scope restoration, stale-selection recovery, focused tests |

**Current verification ceiling:** Connected JavaScript syntax checks and HTML ID/reference inspections were executed for the changed source, and focused regression tests were committed. Python test execution, actual HTTP smoke tests, browser rendering, keyboard and narrow-screen accessibility checks, and a paladin/dense-series task walkthrough **have not been executed in this workspace**. No claim of tested end-user usability or production readiness follows from these PRs.

**Next executable responsibility:** In an isolated local checkout of the exact #392 head, run the focused Studio tests including the new files, smoke-test the actual served UI on desktop and narrow mobile width, and follow the representative scenarios in section 10. Repair observed regressions in the smallest PR. Verify the full base stack against current `main` and only then decide readiness/merge order; do not spend GitHub Actions billing credits unnecessarily.
