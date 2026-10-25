# Auteur UI Strategic Evolution Analysis — Connecting the Authoring Journey

**Analysis date:** 2026-10-24  
**Repository:** `ThorStarlord/auteur`  
**Current source basis:** `main@a8a090580e98cd5f6dcee1645375e2867e644350`; UI possibility landscape at [PR #485](https://github.com/ThorStarlord/auteur/pull/485) head `00d67018f6f80ff7f473b0a9566f255e3f1aa0d9`.  
**Status:** ADVISORY / UI-SPECIFIC STRATEGIC SYNTHESIS. This document records a recommended construction direction and bounded next inquiry, **not** a new owner-ratified product thesis, automatic implementation approval, rollout decision, or replacement for the [product roadmap](../product-evolution-roadmap.md).  
**Immediate disposition:** **INTEGRATION DIRECTION WARRANTED; BOUNDED INVESTIGATE BEFORE NEW BUILD**. See Sections 6–8.

## 1. Decision, continuity, and authority

**Decision:** Which coherent UI future should Auteur pursue **next**, given the twelve possibilities preserved in the [UI Possibility Landscape](auteur-ui-possibility-landscape.md)?

This is a narrower strategic question than `artifacts/strategic_repository_analysis.md` (September 20) and its [strategic reconciliation](../../artifacts/strategic_reconciliation.md). Those remain historical and important: they favor **product compression, source-bound composition of established owners, and observed author-workflow friction before new foundations**. October's Studio work changes the factual capability map, not Auteur's mission or the need for explicit narrative authority.

**Settled product constraints:**

- [MISSION](../../MISSION.md) keeps the product local-first, single-author, backend-neutral, non-autopublishing, and explicit about accepted story authority.
- [Living Story Studio](../design/2026-10-09-living-story-studio.md) **already selects graph-first Studio as the target default**, with scene writing and author-controlled provisional work. The older Beginner route remains a fallback; a new analysis does not silently substitute a prose-first default.
- [Unified Author Experience](../product/auteur-unified-author-experience-architecture.md) **already selects agent-first construction and natural-language revision** of working Narrative Architecture, with manual node editing optional. Seamlessness is a selected intention, not a proven live end-to-end experience.
- [Experience Frontier](../product/auteur-experience-frontier-construction-roadmap.md) and [current STATUS](../../STATUS.md) leave **F2 small-Book coherence / X3 persistent Book workspace** as the selected controlled frontier. X4 multi-thread exploration is **not selected**; prior simulated and Browser results do not establish human author comprehension.
- Any working note, spatial position, candidate, hypothetical consequence, or mentor advice remains noncanonical until the existing owning workflow accepts a change.

The analysis compares possible **experience compositions**. It does **not** reopen the narrative ontology, author-choice authority, graph-first selection, release gates, or Level-4 product thesis.

## 2. Current system: rich capabilities, consequential seams

### 2.1 Grounded authoring chain

```text
working Story Vision / free-form idea
    -> saved canvas + optional coding-agent Architecture request
    -> source-bound working ArchitectureCandidate and focused explanations
    -> inspect / revise / review -> apply to *working* candidate only
    -> selected component -> Story Realization working proposal
    -> working scene + optional Quick Draft + existing review/discovery path
    -> explicit owning-workflow acceptance (not a Studio canvas action)
    -> saved focus / Book orientation / Chapter re-entry
```

This chain describes **available source-level surfaces**, not one already-qualified uninterrupted author journey.

| Evidence | What it establishes | What it does **not** establish |
| --- | --- | --- |
| [Studio HTML](../../src/auteur/beginner/browser/studio.html) and [controller](../../src/auteur/beginner/browser/studio.js) | Story Vision, working canvas, architecture and realization workspaces, multiple views, source inspector, scene editor, Quick Draft and Book navigation exist | That their combined use feels natural or preserves the author's thought through every handoff |
| [ArchitectureCandidate and host contract](../../src/auteur/beginner/studio_architecture.py) | Prepared coding-agent request/validated response; graph proposals remain working; browser does not call an arbitrary host coding agent itself | Automatic agent execution or live delivery without an external host fulfilling the request |
| [PR #482](https://github.com/ThorStarlord/auteur/pull/482) | A focused Chromium regression supports saved Studio perspective on re-entry | General human long-horizon usefulness |
| [PR #483](https://github.com/ThorStarlord/auteur/pull/483) | Contextual Architecture -> Realization navigation preserves selected focus and avoids automatic provider/acceptance action | That every returned concrete proposal fulfills its focused request |
| [PR #484](https://github.com/ThorStarlord/auteur/pull/484) | An **open draft** proposes focused Realization reference-coverage validation and tests | A merged, fully executed, qualified repair; the PR reports no full repo test gate |
| [Studio scene editor](../../src/auteur/beginner/browser/studio.html) | Working prose and a separate required premise/scene-intent generation request exist; generated drafts remain unaccepted | That proposed Architecture/Realization meaning reliably reaches actual scene generation without duplicate author work |
| [W4 assessment](../reviews/2026-10-21-w4-narrative-architecture-qualitative-assessment-v1.md) | One diagnostically corrected source-bound architecture was found substantively coherent | Independent repeatability, reliable unmodified first-pass completion, live-model comparison, or later prose quality |
| [STATUS](../../STATUS.md) and [experience frontier](../product/auteur-experience-frontier-construction-roadmap.md) | Exact historical qualification boundaries and the active F2/X3 product-use frontier | Human UX, X4 selection, broad deployment, or a need to repeat an already-successful initial generation |

### 2.2 Strategic frontier: why this is not another feature backlog

**Frontier S1 — Author intention versus subsystem choreography.** The author should direct the work in story language. Architecture, Realization, Quick Draft, and accepted-story decisions have legitimate separate owners, but those owners need not become separate mental tasks. The key gap to investigate is where a *meaningful author intention* fails to survive a transition.

**Frontier S2 — Spatial understanding versus graph administration.** Graph-first is selected because spatial exploration and relationships matter; that does not imply every task needs the entire graph or that graph layout should gain story authority.

**Frontier S3 — Divergence versus long-term commitment.** Auteur can generate and compare choices. Complete alternative architecture preservation, causal projections, and source-bound author decisions have different identity and authority needs. Their attractiveness does not justify a second narrative-state platform.

**Frontier S4 — Long-horizon orientation versus interface density.** Existing source and focus history can help an author re-enter the Book, but adding a dashboard or more status controls before observing a concrete X3 failure may create administration instead of creative momentum.

## 3. Four coherent construction futures

These are **strategic pathways**, not twelve feature tickets. A pathway can incorporate an idea from another path later; the comparison concerns **which kind of author experience should receive the next concentrated investment**.

### PATH A — Connected Creative Thread (preferred direction)

**Future experience:** The author's Story Vision, specific architectural reason, selected Realization, and concrete scene remain one recognizable creative thread. The agent develops and revises working material; the graph explains it; the author writes and chooses what to accept.

- **Builds on:** P3 Seamless Agent Design, P9 Manuscript/Map, selected graph-first Studio, source-based reviews, contextual Architecture -> Realization action, and existing scene/Book flows.
- **Would require:** preserve exact intent/source/focus through existing handoffs; truthful pending/failure state; avoid duplicate scene input where the already-authored intent is sufficient; correct use of existing acceptance owners; selected-candidate validation including the concern raised by PR #484.
- **Unlocks:** a beginner can obtain value from sophisticated architecture without first learning the system's internal stages; an experienced author can still inspect and challenge the design.
- **Risk:** 'seamless' presentation can hide unresolved status, guess author intentions, or let an agent appear to accept story meaning. A truly automatic host bridge may be unavailable in the browser and is **not** authorized or implied here.
- **Reversibility:** high for contextual presentation/navigation changes that reuse existing source identities; lower for speculative new global state/protocol ownership.
- **Near-term constraint:** confirm a specific missing interaction instead of rebuilding PR #483 or duplicating open PR #484.
- **Future-state distinction:** **one source-linked authoring workpiece**, not just several feature-rich tabs.

### PATH B — Spatial Narrative Reasoning Studio

**Future experience:** A graph-first spatial investigation environment where the author can explore causal neighborhoods, evolving relationships, setting-generated choices, temporal reader promises, and cross-scale Book links while preserving uncertainty.

- **Builds on:** P4 Relationship Timewalk, P5 Living Setting Atlas, P6 Reader Journey Rehearsal, P10 Semantic Zoom, current directed graph, mentor, source views, and emotional/genre facets.
- **Would require:** task-specific navigation and source-proven explanations for each relation, careful separation of interpreted and accepted links, and a concrete scaling pressure at X4/X5.
- **Unlocks:** richer discovery than a general-purpose linked-notes canvas, especially in a complex multi-thread Book.
- **Risk:** information density, invented cross-scale semantics, false causal certainty, a graph that grows without author value; a 'setting map' must not become invented geography or a new ontology.
- **Reversibility:** high for read-only views over existing sources; lower for new data owners or automatic relationship history.
- **Evidence trigger:** X3 or later X4 shows that authors cannot comprehend or revise consequential relationships with existing focus/facets. X4 is not preselected.
- **Future-state distinction:** **understanding complex stories**, not merely generating more story material.

### PATH C — Parallel Architecture and Counterfactual Atelier

**Future experience:** Keep substantially different complete story architectures provisional; compare their sustaining engines and intended experience; inspect hypothetical consequences; deliberately recombine without losing the original alternatives.

- **Builds on:** P1 Intent Constellation, P7 Causal Fork, P8 Parallel Architecture Atelier, existing Story Discovery, [counterfactual planning](../architecture/v0.11.0-counterfactual-narrative-planning-design.md), [decision portfolios](../../src/auteur/portfolio/__init__.py), and ArchitectureCandidate.
- **Would require:** demonstrate a real complete-candidate preservation/identity gap; distinguish full architecture alternatives from combinations of smaller decision candidates; keep scenario assumptions and unknowns visible.
- **Unlocks:** genuine divergent world/story design beyond local mentorship suggestions, with a safe path back to one authored story.
- **Risk:** branch explosion, duplicate persistence, ambiguous ownership, overpromising literary causality, choice paralysis, and maintenance without a proven author need.
- **Reversibility:** presentation-only comparison can be cheap; complete-candidate versioning and promotion are not automatically cheap.
- **Evidence trigger:** an actual author loses or cannot compare causally distinct complete architecture candidates during revision, and simpler alternate summaries cannot solve the problem.
- **Future-state distinction:** **preserving competing possible stories**, not navigating one developing story.

### PATH D — Quiet Manuscript and Creative Re-entry

**Future experience:** The interface becomes unobtrusive while drafting, then restores the last source-backed purpose, unfinished question, and relevant Book context on return; author choice remains central.

- **Builds on:** P2 Question-Centered Studio, P11 Creative-Thread Re-entry, P12 Quiet Studio, saved focus, scene editor, Book orientation, contextual attention.
- **Would require:** clear distinction between recorded author intention and inferred retrospection, reliable lossless editor transitions, relevance filtering, and honest unresolved-work presentation.
- **Unlocks:** sustained creative momentum without requiring constant graph manipulation or dashboards.
- **Risk:** concealing a consequential source mismatch, inventing why the author made a choice, or reducing graph-first identity to an optional afterthought without explicit owner selection.
- **Reversibility:** high if implemented as a presentation preference over existing records.
- **Evidence trigger:** actual re-entry or writing sessions reveal persistent distraction or loss of the creative question despite currently available focus and Book views.
- **Future-state distinction:** **reducing attention and return costs**, not adding a new design instrument.

## 4. Qualitative path comparison (no numerical ranking)

| Question | PATH A — Connected thread | PATH B — Spatial reasoning | PATH C — Parallel atelier | PATH D — Quiet/re-entry |
| --- | --- | --- | --- | --- |
| **Direct current author value** | Integrates already selected graph + agent + writing responsibilities | Makes graph distinctively informative for complex Books | Protects creative option diversity | Protects writing momentum and Book continuation |
| **Grounding in current product direction** | Strong; already selected in principle | Strong graph identity, but deeper X4/X5 use unselected | Conceptually supported; whole-architecture versioning unproven | Strong as complementary view; replacement default unselected |
| **Main missing evidence** | Real, source-bound continuity across the last handoffs and actual author use | Which multi-thread task existing graph/facets fail | Whether complete candidate alternatives are really lost | Whether saved focus and Book re-entry still fail human tasks |
| **Highest cost/risk** | False seamlessness and external host integration assumptions | UI density and interpretive/source mapping | New candidate ownership and choice explosion | Hidden consequential warnings or fabricated author memory |
| **Least premature initial move** | Trace an existing author-intent journey; repair the first real seam | Try one source-backed multi-thread navigation task | Compare two *real* incompatible candidates first | Reopen and write with a real Book; observe missed focus |
| **Current strategic disposition** | **Preferred integration direction; bounded inquiry** | Retain as a conditional X4/X5 candidate | Defer any durable architecture/versioning | Retain as reversible improvement if X3/writing friction emerges |

These are not mutually exclusive forever. PATH A can include a P10 local graph view or a P12 quiet scene editor when these help the same authoring thread. Avoid describing that as five strategic programs running in parallel.

## 5. What the earlier divergence adds — and does not add

The [possibility landscape](auteur-ui-possibility-landscape.md) expanded the option space beyond 'improve the graph' versus 'switch to prose'. Its most consequential ideas are **compositions across existing owners**, not evidence of missing ontological primitives.

- **P1/P5 setting-and-atmosphere beginnings** challenge the assumption that 'premise first' is required. Studio already accepts non-premise material, so the test is qualitative distinctness of resulting story engines, not support for an extra input type.
- **P4/P6/P10 relationship, experience and semantic-zoom views** may increase the value of graph-first authoring at X4/X5, but cannot outrank the current controlled F2/X3 frontier without a decision-changing user/workflow trigger.
- **P7/P8 causal forks and complete alternative architectures** are powerful but materially different from already implemented decision portfolios. Do not infer a full versioned candidate workspace from the existence of scenario/portfolio code.
- **P2/P11/P12 question focus, creative re-entry and quiet drafting** could be cheap, useful complements to PATH A. Their warrant remains a specific author task that current saved focus/book view cannot satisfy.

This synthesis deliberately preserves the unselected alternatives and their counterarguments; it does not retroactively label them as 'rejected'.

## 6. Decision-changing uncertainty and minimum sufficient evidence

**Nearest uncertainty:** Does an author-origin intention persist in **meaning, source identity, focus, and work state** through Architecture -> focused Realization -> an actual working scene and Book re-entry, or does the author need to coordinate independent tools and restate the same meaning?

The current code supports some transitions, but that cross-boundary claim is **not** established by the cited component-specific tests.

### Bounded next responsibility: author-intent continuity trace

Use a **disposable, repository-accessible fixture** and the existing Studio/Beginner contracts. Reuse the existing W4 assessment as qualitative evidence; **do not restart its completed initial generation** or claim private workspace access. Work in the controlled F2/X3 product context rather than selecting a new X4 frontier.

1. **Capture one author-originated intention:** a saved Story Vision, a selected proposed Architecture node, its exact request/source SHA, and a concrete desired story continuation.
2. **Trace existing completed steps:** inspect current Architecture -> Realization focus semantics from merged PR #483, and separately account for the still-unmerged and unqualified PR #484 before claiming off-focus validation.
3. **Follow that intention into a scene:** verify what the existing Realization inspector/copy and working scene/Quick Draft surfaces can actually carry, and where premise/scene-intent or author choice must be repeated.
4. **Reopen and test meaning:** check selected component, working prose, current status, saved focus, stale source behavior, and the distinction between working/candidate/accepted. Do not modify canonical story artifacts.
5. **Classify the first material failure by owner:** presentation/navigation; cross-workflow intent propagation; host-agent execution bridge; craft knowledge; candidate/derived semantics; persistence/concurrency. A missing external agent bridge is **not** automatically a Browser UI defect.
6. **Choose the smallest useful intervention:** if a missing composition is proven and an existing owner can carry it, consider a reversible author-facing build with targeted verification; otherwise stop with a precise evidence gap. Avoid a generic UX framework, new accepted state, mandatory questionnaire, or second agent runtime.

**Sufficient evidence** is a reproducible account of each boundary, a preserved source/authority trace, and a concrete author task the proposed fix improves. A fresh end-to-end generation demo is not a substitute for diagnosing the unverified handoff. Where creative usefulness or comprehension is the claim, a genuine author comparison may still be necessary. The existing W4 assessment says one corrected candidate was coherent; it does not prove downstream Realization, prose effectiveness, or subjective UX quality.

### Decision triggers for the other paths

- **Choose PATH B for a bounded trial** if an X3/X4 author task demonstrates a consequential relationship or scale-navigation failure that existing focus/facets cannot adequately express.
- **Choose PATH C for a bounded trial** if a genuinely distinct full-story architecture is lost, overwritten, or impossible to compare without excessive workaround, and a concise comparison is insufficient.
- **Choose PATH D for a bounded trial** if ordinary drafting/re-entry shows repeated lost intent, context recreation, or visible distraction beyond what current saved-focus and scene-focus functionality already address.
- **Reconsider PATH A** if an actual author journey shows the component boundaries are already clear and the dominant obstacle is instead graph navigation, creative differentiation, or manuscript flow. Do not protect the preferred path against disconfirming evidence.

## 7. Strategic synthesis and selected control move

**Preferred Level-3 direction:** `PATH A — Connected Creative Thread`, **within** the existing graph-first, agent-first, explicit-authority thesis.

**Immediate disposition:** `INVESTIGATE` the smallest source-bound cross-workflow continuity gap described in Section 6. This is **not** `BUILD` a new global subsystem, not approval to merge PR #484, and not a declaration that F2/X3 has passed. If a local, reversible integration is shown to be valuable with no material new downside, **build-and-verify can dominate a detached prototype**; do not require a separate usability experiment for a mechanical source/focus integrity bug.

**Why not stop after the landscape?** A purely speculative wishlist would be less useful than a concrete comparison that keeps the active product thesis and implementation dependencies visible. The repository already has credible partial wiring and an unresolved consequential seam to inspect.

**Why not immediately build the most spectacular new UI?** Whole-architecture branching, deep relationship timelines, and rich reader-experience visualization each introduce scope, interpretation, or ownership questions. Their distinctive value has not been established in the current Book task, whereas basic continuity across existing steps is necessary for both simple and advanced use.

**What could change this judgment?** A concrete author task showing the graph already functions smoothly as one creative thread, or a rival path producing a clearly greater author decision benefit at no larger cost/authority risk.

## 8. Decision trace, boundary, and stop rules

- **Alternatives examined:** integrated coauthoring, spatial sensemaking, full-story divergence/counterfactuals, quiet manuscript/re-entry.
- **Expected value of preferred path:** more author-controlled creative progress with less coordination of existing tools and stronger reuse of stable source identities.
- **Selected action shape:** **PROBE / VERIFY** one end-to-end intent-continuity boundary first; then consider **REVERSIBLE BUILD** of the first proven low-level gap.
- **More conservative alternative:** stop with read-only research. Less warranted because the next discriminating task is concrete and can exploit existing code/fixtures; further brainstorming alone is unlikely to change the decision.
- **More aggressive alternative:** build a new architecture/versioning engine, multi-pane dashboard, or autonomous provider bridge. Less warranted because no irreducible domain distinction or release-level evidence supports it.
- **Authority:** writing this analysis does not authorize implementation, canonical story mutation, merge, deployment, release, or new owner-level product default. Protected decisions remain with the existing owner/governance process.
- **Stop:** at a verified completed cross-workflow trace with no material gap; a named source/host-access blocker; a genuine owner-sensitive product thesis choice; or the first irreducible error requiring a separately grounded responsibility. Do not manufacture a new UI backlog to avoid stopping.

## 9. Simulated author stress-test follow-up (2026-10-25)

A separate [simulated author / coding-agent UI stress test](../product-validation/living-story-studio/2026-10-25-simulated-author-ui-stress-test.md) examined the preferred integration path using **isolated source-derived model contracts and working-state simulations**, not Auteur's runtime or a human participant. Its 13/13 passing *harness assertions* identified two current-source integration issues: an off-focus Realization can pass the existing global-reference guard (open draft PR #484 contains the focused-coverage repair), and copying a proposed Realization scene does not supply the exact premise/intent fields required for Quick Draft. Two causally distinct abstract story engines were also **authored synthetically in this assistant session** and checked in a standalone schema replica; they do not demonstrate a complete alternative-architecture UI or live agent behavior.

**Reconciliation:** NO_MODEL_CHANGE / REAFFIRM PATH A. Qualify the existing focused-coverage PR and trace the Realization-to-scene continuity in the real project before additional UI design or a new subsystem. User preference, prose quality, and production readiness remain untested. The simulation's additional S13 case shows that **labeling a proposal with the right source ID does not prove it semantically realizes that source**. The simulation does not authorize implementation or merge.

## 10. Evidence and versioning notes

- [UI Possibility Landscape](auteur-ui-possibility-landscape.md), on the source branch of [PR #485](https://github.com/ThorStarlord/auteur/pull/485).
- [Prior Strategic Repository Analysis](../../artifacts/strategic_repository_analysis.md) and [Strategic Reconciliation](../../artifacts/strategic_reconciliation.md), historical source identities; not overwritten.
- [Mission](../../MISSION.md), [Current STATUS](../../STATUS.md), [Product Evolution Roadmap](../product-evolution-roadmap.md), and [Experience Frontier Roadmap](../product/auteur-experience-frontier-construction-roadmap.md).
- [Living Story Studio](../design/2026-10-09-living-story-studio.md), [Unified Author Experience](../product/auteur-unified-author-experience-architecture.md).
- [Studio HTML](../../src/auteur/beginner/browser/studio.html), [Studio controller](../../src/auteur/beginner/browser/studio.js), [ArchitectureCandidate contract](../../src/auteur/beginner/studio_architecture.py).
- [W4 qualitative assessment](../reviews/2026-10-21-w4-narrative-architecture-qualitative-assessment-v1.md).
- Merged [PR #482](https://github.com/ThorStarlord/auteur/pull/482), merged [PR #483](https://github.com/ThorStarlord/auteur/pull/483), and **open draft** [PR #484](https://github.com/ThorStarlord/auteur/pull/484), statuses verified at analysis time.

**Maintenance:** Reconcile future product evidence against the exact source revision, rather than converting this advisory analysis into a competing `STATUS`, `NOW` queue, or permanent controller artifact. If later evidence changes the selected path, record the triggering observation and decision explicitly.
