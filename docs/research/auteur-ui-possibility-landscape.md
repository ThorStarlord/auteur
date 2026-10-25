# Auteur UI Possibility Landscape

**Recorded:** 2026-10-24  
**Source baseline:** `ThorStarlord/auteur` `main@a8a090580e98cd5f6dcee1645375e2867e644350`  
**Status:** EXPLORATORY / UNRANKED / DOCUMENTATION ONLY  
**Authority:** This is a pre-selection research index, not a product decision, feature backlog, implementation plan, approved roadmap, UX qualification, or change to narrative canon.

## 1. Purpose and scope

Ask **what authoring experiences Auteur could enable that the current interaction model does not yet deliver well**, not merely which controls or views could be added.

Auteur already has substantial graph-first Studio, agent-first narrative-design, writing, continuity, guidance, and reasoning infrastructure. The next search should distinguish:

1. **Already selected** — an established product direction, whether or not its full experience is implemented.
2. **Already implemented** — code for an interaction or capability exists; this alone does not establish real-author usefulness.
3. **Partially connected** — capabilities exist, but an author-facing workflow or composition may be incomplete.
4. **Open possibility** — a genuinely different interaction, composition, or experience is not yet selected or evidenced.

These are **research descriptions**, not new roadmap lifecycle states. The landscape preserves alternatives before judgment. It neither reopens the owner-selected graph-first direction automatically nor makes current architecture an unquestionable solution to every authoring need.

### Hard boundaries

- Preserve [MISSION](../../MISSION.md): single-author, local-first, backend-neutral; no auto-accept, cloud collaboration, native GUI app, payments, auto-publishing, or third-party story scraping.
- **Working idea, derived proposal, explicit author choice, and accepted story state remain distinct.** UI position, graph edges, generated text, and speculative consequence projections never become independent story authority.
- Reuse the five-layer narrative architecture and existing acceptance, provenance, safety, and persistence owners. A UI hypothesis does not authorize a new ontology, graph database, shadow canon, or mutation path.
- This review is source-grounded, not a fresh live-browser, host-agent, accessibility, or human-author evaluation. Source presence is not proof of smooth or valuable interaction.
- The current [roadmap](../product-evolution-roadmap.md) and [STATUS](../../STATUS.md) govern active frontiers and execution. An entry here is not a `NOW`, `NEXT`, or `BUILD` decision.

## 2. Current baseline and evidence ceiling

| Area | Grounded baseline | What remains a product question |
| --- | --- | --- |
| Primary interaction | [Living Story Studio](../design/2026-10-09-living-story-studio.md) selects a graph-first spatial experience; [Studio browser source](../../src/auteur/beginner/browser/studio.html) has the working graph, inspector, tools, and writing panel. | How much spatial interaction helps rather than distracts an author, especially over long books. |
| Agent-first design | [Unified Author Experience](../product/auteur-unified-author-experience-architecture.md) selects coding-agent-generated/revised working Narrative Architecture; manual node assembly stays optional. | Whether the request/response handoff feels like continuous authoring rather than operating an engineering tool. |
| Narrative perspectives | [Architecture Information UX](../design/2026-10-11-narrative-architecture-information-ux-plan.md) describes graph, emotions, genres, tropes, structure, and timeline perspectives. | Whether switching perspectives improves comprehension or fragments one creative mental model. |
| Prose and Book | Studio includes a docked scene editor, Quick Draft linkage, Book orientation, and re-entry; the [adversarial UX review](../product-validation/living-story-studio/adversarial-ux-review.md) describes earlier workflow seams and their follow-ups. | Whether graph-to-prose-to-discovery-to-accepted-story-to-graph is one recognizable workpiece. |
| Alternatives and consequences | Story Discovery, [counterfactual planning](../architecture/v0.11.0-counterfactual-narrative-planning-design.md), and decision portfolios contain relevant noncanonical comparison machinery. | Whether a visual comparison or causal exploration UI would add genuine author value beyond existing tools. |
| Evidence and quality | [W4 Narrative Architecture assessment](../reviews/2026-10-21-w4-narrative-architecture-qualitative-assessment-v1.md) provisionally supports one coherent working design after a one-field diagnostic correction. | Independent generation reliability, subsequent realization quality, sustained author usefulness, and human UI comprehension remain unproven by that result. |

Recent source history also includes directed architecture links ([PR #480](https://github.com/ThorStarlord/auteur/pull/480)), preserved saved perspective ([PR #482](https://github.com/ThorStarlord/auteur/pull/482)), and focus-preserving navigation into Story Realization ([PR #483](https://github.com/ThorStarlord/auteur/pull/483)). As of this snapshot, [PR #484](https://github.com/ThorStarlord/auteur/pull/484), validating focused Realization output coverage, remains open. Do not describe proposed or narrowly tested behavior as fully qualified author experience.

## 3. Seed possibilities: six directions, not six feature commitments

The purpose of these seeds is to retain **distinct hypotheses** and their strongest counterarguments, not to rank or implement six subsystems.

### A. Agent-First Narrative Architect

- **Already present:** Selected default design responsibility; source-bound generation and revision, working candidates, explanations, and explicit review. See [Unified Author Experience](../product/auteur-unified-author-experience-architecture.md) and [Studio design](../design/2026-10-09-living-story-studio.md).
- **Potential difference:** A continuous author-intent -> agent proposal -> inspect/change -> focused realization experience in which request details and response envelopes remain inspectable but do not dominate normal creative work.
- **Merit / risk:** Removes mechanical assembly from the beginner; may obscure what the agent inferred or what an explicit author action actually accepted.
- **Open test:** Can the author direct one meaningful revision in story language, understand what changed, and resume without managing prompt/JSON plumbing?

### B. Living Manuscript and Story Map

- **Already present:** Scene drafting, a docked editor, chapter/navigation continuation, and a credible graph/manuscript hybrid comparator in the [adversarial product review](../product-validation/living-story-studio/adversarial-product-review.md).
- **Potential difference:** Graph and manuscript become synchronized views of the same working context, so the author can move from a scene to its narrative function, revise prose, and return without re-entering intent.
- **Merit / risk:** Joins spatial reasoning with actual writing; may add a split-pane burden and another layer of state synchronization.
- **Open test:** Does a paired graph/manuscript composition reduce context loss versus current Studio/Quick Draft transitions without making writing slower?

### C. Narrative Causality Laboratory

- **Already present:** Derived impact projections and deterministic [counterfactual scenario comparison](../architecture/v0.11.0-counterfactual-narrative-planning-design.md); scenario assumptions and unknowns must remain explicit.
- **Potential difference:** A navigable, *hypothetical* visual playground for changing a goal, relationship, event, or structural decision and inspecting possible downstream dependencies and alternative interpretations.
- **Merit / risk:** Makes consequence reasoning tangible; a diagram can falsely imply causal certainty or become a competing narrative-state engine.
- **Open test:** Can an author distinguish an evidenced dependency from an agent hypothesis and decide something useful without mistaking the projection for what will happen?

### D. Reader Experience Composer

- **Already present:** Emotion targets, complex emotions, genre roles and interactions, phases, and timeline views in [Architecture Information UX](../design/2026-10-11-narrative-architecture-information-ux-plan.md).
- **Potential difference:** Explore coordinated modulation of emotion, genre, tension, pacing, and payoff *across time*, not just read separate facet reports. Any editing would prepare a noncanonical revision proposal through existing ownership.
- **Merit / risk:** Makes the intended audience experience visible; could encourage false precision or superficial numeric optimization of artistic effects.
- **Open test:** Does temporal comparison reveal a meaningful tradeoff that the current facets and graph conceal?

### E. Alternative Architectures Laboratory

- **Already present:** Multiple Story Discovery directions, revisable working architecture, and bounded candidate-combination reasoning; these are **not** evidence of a complete side-by-side ArchitectureCandidate UI.
- **Potential difference:** Keep two or more *complete working architectural interpretations* available for comparison, selective recombination, and explicit author choice without premature canonical promotion.
- **Merit / risk:** Protects creative divergence and exposes fundamental alternatives; may multiply storage, visual density, and reconciliation work.
- **Open test:** Are alternatives materially different in mechanism and author experience, or merely variants of labels and layout?

### F. Long-Horizon Creative Memory

- **Already present:** Book re-entry, saved graph focus, chapter continuity, provenance, accepted-history reconstruction, and next-action orientation. See [Studio design](../design/2026-10-09-living-story-studio.md) and [Unified Author Experience](../product/auteur-unified-author-experience-architecture.md).
- **Potential difference:** An author-facing return experience that briefly reconstructs *why this story was taking this shape*, which decisions and alternative ideas remain unresolved, and where creative work can resume.
- **Merit / risk:** Rebuilds momentum after interruptions; may turn continuity into a noisy dashboard or invent the author's earlier intent.
- **Open test:** After a genuine time gap, can an author resume a specific creative thread from source-backed context without reading a technical activity log?

## 4. Distinct interaction philosophies to keep comparable

These are **competing or combinable compositions**, not new ratified product directions.

| Philosophy | Center of author attention | What might make it valuable | Strongest challenge |
| --- | --- | --- | --- |
| **Graph-first creative workspace** (selected target) | Spatial ideas and relationships; writing and evidence are accessible in context. | Discovery through relationships and narrative structure. | Graph upkeep could become administration rather than storytelling. |
| **Graph/manuscript hybrid** (credible comparator) | Spatial and linear writing surfaces remain coequal or fluidly docked. | Maintains prose momentum while keeping structure close. | Multiple synchronized surfaces may raise navigation and cognitive costs. |
| **Agent-led, inspectable design** (selected responsibility; compositional alternatives open) | Natural-language creative intent and visible, revisable agent proposals. | Turns complex narrative design into an author-guided interaction. | Author may become a passive reviewer; provenance and meaningful choices could disappear behind convenience. |

The central question is not which rendering technology wins. It is **where creative agency and attention should reside at each moment**. A graph-first product may still use a focused manuscript view or agent-led construction without surrendering its spatial identity.

## 5. Divergent Exploration questions

Preserve serious counterexamples and combinations before attempting to choose one solution:

1. **Entry:** What should happen when an author arrives with only an atmosphere, desired reader emotion, place, image, trope, scene, or unfinished fragment rather than a premise?
2. **Agency:** Which creative decisions genuinely benefit from direct spatial manipulation, and which should the agent handle while preserving author oversight?
3. **Representation:** Which tasks need a graph, manuscript, timeline, causal neighborhood, explanation, or compact list? What context must remain stable while switching?
4. **Multiplicity:** How might an author entertain competing story architectures, ambiguous commitments, and unchosen possibilities without multiplying accepted state?
5. **Temporality:** Can authors reason about emotional and genre modulation across arcs without turning subjective craft into misleading metrics?
6. **Consequences:** How could Auteur explain *possible* downstream changes while displaying source strength, assumptions, and unresolved uncertainty?
7. **Long horizon:** What should a productive return after several weeks feel like, beyond a summary of files and changes?
8. **Subtraction:** Which existing controls, transitions, and duplicated author inputs could disappear if the underlying workflow became coherent?

Divergence includes alternatives that would *simplify* the UI, not just ambitious new panels. Recombine compatible ideas; challenge the selected graph-first baseline without silently revoking it.

## 6. Evidence that would discriminate proposals

| Matched author task | Competing question | Evidence to collect if decision-relevant |
| --- | --- | --- |
| Story Vision -> generated graph -> selected mechanism -> Story Realization -> scene | One coherent journey or a chain of tools? | Re-entered intent, lost focus, request friction, actionable author understanding; exact source and nonacceptance state. |
| Compare two causally different versions of one story decision | Does visual comparison add insight? | New, explainable tradeoffs discovered versus maintenance and interpretation cost. |
| Revise an accepted or proposed event | Do projected consequences look like facts? | Author interpretation, source/uncertainty labeling, unchanged accepted files unless explicitly authorized. |
| Navigate a dense multi-thread architecture | Graph, focused neighborhood, or manuscript context? | Meaningful tasks completed, focus continuity, navigation burden, keyboard/assistive access when applicable. |
| Reopen a multi-chapter story after absence | Does the interface restore creative momentum? | Recovery of the last creative question, accepted/provisional distinctions, next meaningful author action. |

Use existing source and scripted evidence where sufficient; use a disposable clickable comparison when a concrete interaction remains ambiguous; use actual human observation for claims of comprehension, preference, or creative usefulness. A passing Browser test cannot establish literary quality. A pleasing mockup cannot establish safe persistence.

## 7. Exploration -> strategy -> action boundary

1. **Divergent Exploration:** Expand and organize materially different author jobs, interaction models, and combinations. Record the repository source each idea reuses and what would actually be novel. Sections 1–8 establish the initial landscape; Section 9 expands it with one bounded divergent round. Neither constitutes an exhaustive search.
2. **Adversarial challenge / recombination:** Challenge assumed user value, workflow cost, cognitive load, authority, long-horizon durability, and alternative simpler representations. Preserve credible counterarguments rather than forcing consensus.
3. **Strategic Evolution Analysis:** Only after the possibility space is sufficiently informative, evaluate coherent construction paths, dependencies, frontier effects, and decision-changing uncertainty. Reconcile with the [product evolution roadmap](../product-evolution-roadmap.md) and current [STATUS](../../STATUS.md).
4. **Bounded construction, if warranted:** Build or prototype the smallest reversible, valuable author-facing improvement; verify the specific workflow and consequence it claims, proportionate to risk. Do not automatically turn landscape entries into PRs or milestones.

**Stop exploring** when another concept is only a rephrasing of an existing one, further breadth is unlikely to change the decision, or the next uncertainty requires actual author use rather than more brainstorming. Candidate counts and novelty scores are not success measures.

### Maintenance rules

- Add findings with a specific author job, mechanism, source, counterargument, and next discriminating uncertainty. Avoid standalone wishlist bullets.
- Link to existing design/implementation/qualification documents instead of copying their specifications. Distinguish observed source behavior from a proposed interaction and an unverified UX claim.
- When a possibility is selected or rejected elsewhere, reference that decision; do not make this file a second authority or a shadow backlog.
- Revisit source identity before using this snapshot as current status. The older [Strategic Repository Analysis](../../artifacts/strategic_repository_analysis.md) predates much of the October Studio construction and should not be treated as a current UI decision.

## 8. Primary source index

- [Mission and hard invariants](../../MISSION.md)
- [Unified Author Experience Architecture](../product/auteur-unified-author-experience-architecture.md)
- [UX / Product Requirements](../product/auteur-ux-product-requirements.md)
- [Living Story Studio design](../design/2026-10-09-living-story-studio.md)
- [Architecture Information UX](../design/2026-10-11-narrative-architecture-information-ux-plan.md)
- [Contextual Narrative Mentorship](../design/2026-10-13-contextual-narrative-mentorship.md)
- [Living Story Studio adversarial product review](../product-validation/living-story-studio/adversarial-product-review.md)
- [Living Story Studio adversarial UX review](../product-validation/living-story-studio/adversarial-ux-review.md)
- [Counterfactual Narrative Planning design](../architecture/v0.11.0-counterfactual-narrative-planning-design.md)
- [W4 Architecture quality assessment](../reviews/2026-10-21-w4-narrative-architecture-qualitative-assessment-v1.md)
- [Product Evolution Roadmap](../product-evolution-roadmap.md)
- [Current Repository Status](../../STATUS.md)

---

## 9. Divergent Exploration — expanded round (2026-10-24)

**Role:** source-grounded expansion of possible author experiences. **Status:** exploratory and unranked; no product-direction, construction, release, or acceptance authority. This round is broader than the six seed directions above but is not a claim of exhaustive discovery.

**Method and evidence:** contrast existing authoring jobs and product contracts with the actual Studio Browser, contextual mentor, narrative candidate schema, counterfactual planning, and experience-frontier roadmap. Recombine coherent mechanisms across their current owners; challenge the graph-first assumption without silently overriding the already-selected target. Distinguish what **code demonstrably exposes** from what **authors might value**. No real-browser session, human study, qualitative manuscript assessment, or new generated architecture was conducted in this round.

Repository anchors: [Studio HTML](../../src/auteur/beginner/browser/studio.html), [Studio controller](../../src/auteur/beginner/browser/studio.js), [contextual mentor](../../src/auteur/beginner/browser/studio_mentorship.js), [ArchitectureCandidate schema](../../src/auteur/beginner/studio_architecture.py), [experience frontier](../product/auteur-experience-frontier-construction-roadmap.md), [Story Opportunity Discovery](../story-opportunity-discovery.md), [counterfactual planning](../architecture/v0.11.0-counterfactual-narrative-planning-design.md), and [decision portfolios](../../src/auteur/portfolio/__init__.py).

### 9.1 Reframe from widgets to consequential author jobs

| Author's job | Existing starting point | Decision-changing question |
| --- | --- | --- |
| Find a story worth making from atmosphere, place, influence, or desire | Premise-optional Story Vision and documented upstream Story Opportunity Discovery | Does spatially externalizing attractive fragments produce substantively different stories, or is plain text already better? |
| Convert creative intention into a coherent mechanism | Agent-first ArchitectureCandidate generation, revision, and review | Can the author direct the design without administering host-agent requests and schemas? |
| Understand how ideas affect one another | Working/derived graphs, directed links, Focused/Full views, facets, explanations | Which tasks genuinely benefit from the whole graph versus a relationship-local or temporal explanation? |
| Discover and challenge possibilities | Mentorship Learn/Explore/Question/Challenge, Story Discovery, hypothetical decisions | Are alternatives sufficiently different in *cause and story promise*, or merely rewordings? |
| Write scenes while preserving design intent | Studio scene panel, focus writing, Story Realization, Quick Draft | Can one intention travel through drafting and revision without duplicate entry or lost focus? |
| Reframe story decisions without rewriting canon | Impact projection, counterfactual scenarios, author review | Can uncertainty and consequence be explained without presenting projections as facts? |
| Continue after a long interruption | Saved focus, Book orientation, working canvases, accepted history | Does re-entry recover why the author was doing something, or only where they stopped? |
| Work without being managed by the UI | Progressive disclosure, optional mentor, focused editor | What could disappear while keeping power and author control available? |

These are different cognitive tasks; making one view do all of them may be the wrong optimization.

### 9.2 Morphological exploration: change independent dimensions

This matrix deliberately avoids starting with a preferred screen layout.

| Dimension | Distinct plausible choices |
| --- | --- |
| **Entry material** | Story Vision; unconnected fragments; emotion or mood; place; character relationship; unanswered question; existing prose; resume a Book |
| **Primary object** | An attractive possibility; narrative engine; relationship change; intended reader journey; draft scene; hypothesis; pending decision; accepted history |
| **View** | Whole graph; selected causal neighborhood; manuscript; cards; phase/timeline; setting-centered local network; comparison; quiet mode |
| **Agent posture** | Construct working design; explain source; contrast mechanisms; propose concrete realization; challenge assumption; recover context; remain silent |
| **Time horizon** | Idea; one scene; a sequence; entire Book; Series |
| **Authority** | Unselected working idea; derived proposal; hypothetical consequence; accepted fact through its existing owner only |

A genuine alternative changes **where an author starts, what they can reason about, how a creative choice happens, or how uncertainty is understood**. A different label, color, animation, or sidebar location is not a separate experience hypothesis.

### 9.3 Twelve distinct experience possibilities

The following are **possibility families, not twelve feature requests**. For each, the novel interaction is separated from already present capability. Order does not imply priority.

#### P1 — Intent Constellation: atmosphere before premise

- **Experience:** An author begins with 'a beautiful school, belonging, generous heroism, secrets, and an eventual loss' instead of a plot. They arrange working fragments and request two causally different sustaining engines with legible reasons and sacrifices.
- **Already present:** Optional Story Vision, working Idea/Place/Question nodes, Story Opportunity Discovery, Story Discovery, and agent-generated candidate architecture.
- **New composition:** Fragments remain visible as author-owned attractions while alternative *interpretations* are proposed and can be compared, rather than requiring a premise at the start.
- **Counterargument:** This can duplicate a freeform Story Vision field and flood the author with variations. A single strong written vision may be more efficient.
- **Discriminator:** Does the interaction expose a durable new mechanism, not just more descriptive text? Does it keep inspiration distinct from accepted story meaning?

#### P2 — Question-Centered Studio: the unfinished decision as a navigation anchor

- **Experience:** Return to 'Can the mentor remain loving while hiding the truth?' and see source-backed character tensions, candidate architecture, a related scene, and unchosen interpretations around that question.
- **Already present:** Working question nodes, contextual mentor questioning, graph focus, and the roadmap's unselected Current Author Intent concept.
- **New composition:** Persist an explicit creative question *as orientation*, reusing source references and existing author decisions rather than inventing a task-management system.
- **Counterargument:** The author may not want all creative ambiguity treated as a task or inbox item. Search and graph selection might already suffice.
- **Discriminator:** Does the user find the relevant creative material and resume a meaningful choice more easily than in the current graph?

#### P3 — Seamless but inspectable Agent Design

- **Experience:** 'Make the middle more unsettling, keep the romance, and preserve the resolution' becomes a legible working revision whose actual changes the author can inspect before developing a scene.
- **Already present:** **Selected product direction** in the Unified Author Experience; Studio ArchitectureCandidate and Story Realization host-agent handoffs, working diffs, explicit apply-to-working controls.
- **New composition:** Normal authoring stays in story language while exact requests, source fingerprints, errors, and manual completion remain available when needed.
- **Counterargument:** A continuous illusion of autonomy can conceal stale data, hidden authorship decisions, or unfulfilled requests.
- **Discriminator:** Can one ordinary-language change pass through revise, inspect, working apply, realization, and re-entry without manual protocol handling and without implying canonical acceptance?

#### P4 — Relationship Timewalk: characters change across scenes

- **Experience:** Select two characters and walk through how trust, rivalry, complicity, protection, or mutual dependence changes over three points of the Book.
- **Already present:** Character/relationship architecture concepts, chapter-filtered relationship evidence, scenes and character-arc data.
- **New composition:** A time-sensitive *explanation* of the relation with source-linked scene evidence and clearly marked interpretations; the graph remains available for context.
- **Counterargument:** Human relationships are interpretive. A structured progression could make ambiguous interactions look definite or generate bookkeeping.
- **Discriminator:** Can the author discover and correct a consequential missing relationship transformation without adding unsupported facts?

#### P5 — Living Setting Atlas: places as generators of stories

- **Experience:** Selecting a school, sanctuary, or city reveals how its routines, institutions, material constraints, people, and aesthetic qualities generate choices and emotional attachment. A relevant scene is one click away.
- **Already present:** Working Place nodes, narrative relation/scene links, mentor questions about setting, and Story Realization.
- **New composition:** A **setting-as-causal-character** presentation, not an automatic geographical map or new worldbuilding database.
- **Counterargument:** Fictional places are often more evocative in prose. Spatial interfaces might reduce setting to cartography and decoration.
- **Discriminator:** Does the place-centered view uncover a meaningful setting-dependent choice, recurring story engine, or distinctive lived atmosphere?

#### P6 — Reader Journey Rehearsal: intended experience across time

- **Experience:** The author traverses a designed transition from wonder to dread to restoration, seeing which mechanisms and hypothetical scenes might create each step and where support is weak.
- **Already present:** Emotion intentions, genre contracts/interactions, phases, tropes, architecture facets and timeline.
- **New composition:** One continuous, explanatory walk through *intended* experience rather than separate reports or numeric feeling predictions.
- **Counterargument:** Actual reader response is not known. Visualizing intentions can encourage deterministic or formulaic thinking about subjective art.
- **Discriminator:** Can it reveal one unsupported transition or contradictory payoff not already evident in the existing facets?

#### P7 — Causal Fork Bench: compare a decision's consequences

- **Experience:** Place two hypothetical story decisions beside the same captured baseline, follow projected dependencies, and understand both explicit assumptions and unknowns.
- **Already present:** Deterministic [counterfactual planning](../architecture/v0.11.0-counterfactual-narrative-planning-design.md), impact, review, and [decision portfolios](../../src/auteur/portfolio/__init__.py).
- **New composition:** A story-language view of the **existing** hypothetical models, not another impact engine.
- **Counterargument:** A convincing causal visualization can overstate creative predictions or conflate source-level dependencies with interpretation.
- **Discriminator:** Can the author identify fact, assumption, projection, and unknown before choosing, while confirming no accepted pointers changed?

#### P8 — Parallel Architecture Atelier: keep whole stories divergent

- **Experience:** Compare two complete working architectures with different sustaining engines, genre functions, character relationships, and reader promises. Explore whether a selective recombination deserves a *third working candidate*.
- **Already present:** ArchitectureCandidate generation/revision, Story Discovery directions, decision alternatives, and portfolios.
- **New composition:** Identity, preservation, and comparison of **complete working architecture alternatives**; existing decision-portfolio infrastructure does *not* prove whole-ArchitectureCandidate versioning exists.
- **Counterargument:** Multiple large graphs multiply storage, visual burden, and indecision. Concise compareable synopses may suffice.
- **Discriminator:** Can a genuinely valuable whole-story alternative be preserved through a revision today, or is it lost? What is the smallest adequate retention mechanism?

#### P9 — Manuscript / Map Dual Plane: prose and structure as one workpiece

- **Experience:** Draft a scene, inspect its causal/thematic purpose, adjust the working intention, and return to the same prose position and unsaved thought.
- **Already present:** Studio working scene editor, graph, focused writing, saved view, Quick Draft, Story Realization, and Book re-entry.
- **New composition:** A lossless, comprehensible transition between manuscript and structural meaning, without creating a second manuscript owner.
- **Counterargument:** Permanent side-by-side surfaces can squeeze prose and amplify distractions. Switching cleanly between full screens may be superior.
- **Discriminator:** Does the dual-plane experience reduce duplicated intention and lost focus while improving actual scene construction?

#### P10 — Semantic Zoom: the same narrative at different scales

- **Experience:** Move from a Book-level mechanism to one Chapter function, a concrete scene, and a working question, then return along a meaningful navigation trail.
- **Already present:** Narrative scope model, Studio Focused/Full architecture, inspector, semantic trail, Book view, and scene links.
- **New composition:** Coordinated navigation **by existing source identity and narrative function**, rather than representing every level as an equivalent flat node.
- **Counterargument:** Automatic cross-scale links may fabricate structure or confuse which layer the author is inspecting.
- **Discriminator:** Can a multi-thread Book task be completed without getting lost, and can the author always answer 'Why am I here?'?

#### P11 — Creative-Thread Re-entry: remember purpose, not merely position

- **Experience:** After a month away, Auteur shows the last working question, the accepted changes since then, relevant unfinished alternatives, and one sensible continuation with citations to local sources.
- **Already present:** Focus persistence, Book history, source fingerprints, source-linked questions, and work-status projections.
- **New composition:** Recover *source-backed creative intent* across sessions without manufacturing personal memories or a new long-term knowledge subsystem.
- **Counterargument:** An AI-generated summary of why the author made a decision may be false. A plain recent-items list is less glamorous but more trustworthy.
- **Discriminator:** Can an author resume the correct creative thread and correct the system's uncertain interpretation rather than receive a misleading confident summary?

#### P12 — Quiet Studio: radical subtraction

- **Experience:** A focused authoring mode hides mentor advice, technical controls, global graph and noncritical alerts; the next relevant narrative question remains recoverable.
- **Already present:** Focus-writing editor, progressive disclosure, collapsible mentorship, current graph-first target.
- **New composition:** Rules for **what not to show**, without undoing the owner's graph-first selected default or losing saved state.
- **Counterargument:** A quiet mode could hide a genuinely blocking contradiction or just duplicate existing focus writing.
- **Discriminator:** Can an author draft for longer uninterrupted intervals and still recognize a consequential source or acceptance mismatch when needed?

### 9.4 Capability-to-interaction crosswalk: do not reinvent

| Opportunity | Existing owner/substrate | Where change could legitimately live | Non-solution to avoid |
| --- | --- | --- | --- |
| Agent-led architecture | Architecture candidate handoff + author review | Interaction composition and status language | Another provider protocol; silent auto-accept |
| Creative mentorship | Mentor Learn/Explore/Question/Challenge | Relevance and local presentation | Global compulsory chat sidebar |
| Hypothetical consequences | Simulation, impact, portfolio | Comparative story-language visualization | New hypothetical-state store |
| Emotional progression | Genre/emotion/phase contracts | Cross-facet reader-intent explanation | Emotional prediction scores |
| Whole-story alternatives | Discovery and working ArchitectureCandidate | Only evidence-supported working-candidate comparison | Treating decision portfolios as complete story branches |
| Character relationship changes | Character/relationship and Chapter evidence | Temporal linked interpretation | Unsupported relationship canon |
| Settings | Working places and realization source links | Place-to-choice and scene explanation | Invented geographic coordinates or default map engine |
| Book memory | Book orientation, focus, history | Transparent creative-thread re-entry | Unverifiable background 'AI memory' |
| Drafting | Scene editor and Quick Draft | Lossless workflow continuity | Second accepted-manuscript store |

### 9.5 Deliberately different recombinations

These are examples of *author journeys*, not approved prototype tickets:

1. **From beautiful place to consequential scene (P1 + P5 + P9).** The author starts from a place they want to inhabit, learns what daily life and institutional constraints make possible, and chooses a scene where a distinctive choice becomes dramatic. **Falsifier:** the interaction delivers only decorative setting detail, not new narrative function.
2. **Question -> alternatives -> consequence -> scene (P2 + P3 + P7 + P9).** Start from one hard creative question, compare two mechanisms, inspect speculative effects, review a working architecture revision, then draft the affected scene. **Falsifier:** the user must repeat the same intention or mistakes a working hypothetical for accepted story.
3. **One character relationship across the whole Book (P4 + P6 + P10).** Trace a relationship from its setup through transformation and reader-intended payoff, zooming to source scenes when evidence is disputed. **Falsifier:** the view fabricates psychological states or duplicates existing explanatory facets.
4. **Return and choose without a dashboard (P8 + P11 + P12).** Reopen preserved alternatives and the last unresolved question, then choose comparison or immediate focused writing. **Falsifier:** the interface becomes a backlog-management cockpit rather than a creative invitation.

### 9.6 Cross-domain patterns and their limits

These examples are external *interaction analogies*, not recommendations to clone software or add external integrations:

- [Scrivener — official overview](https://www.literatureandlatte.com/scrivener/overview) relates corkboard index cards and an outline to manuscript sections. **Question for Auteur:** which visual changes should reorganize actual manuscript order, and which must remain nonauthoritative spatial layout?
- [Obsidian Canvas — official help](https://obsidian.md/help/plugins/canvas) permits positioning, connecting, and grouping cards, files, and media in a spatial surface. **Question:** why should Auteur's canvas be more than a general linked-note board? Answer may lie in narrative function, provenance and creative consequence.
- [Novelcrafter — official writing guide](https://www.novelcrafter.com/courses/ultimate-beginners-guide/writing-your-first-prose) and [Codex guide](https://www.novelcrafter.com/help/docs/codex/the-codex) show manuscript-proximate story context. **Question:** can relevant story evidence be accessible during prose work without forcing tab switching or repeating intent?
- [Twine — official website](https://www.twinery.org/) is centered on interactive, nonlinear stories. **Question:** does a diagram represent *the reader's actual branching story* or *the author's provisional alternative designs*? These are different semantics and should not be conflated.

These examples do not establish author preference, feature parity, or adoption requirements for Auteur.

### 9.7 Adversarial tests of the experience thesis

| Appealing claim | Strong counterargument | Smaller alternative |
| --- | --- | --- |
| Whole graph should be the continuous center of attention | The author may only need one causal relationship while writing | Focused neighborhood with predictable return path |
| More autonomous AI means less author work | Hidden generation may reduce intentional authorship and obscure stale requests | Inspectable working proposals with clear source identity |
| More alternatives are always more creative | Similar variants consume attention without adding different mechanisms | Fewer, causally distinct options with costs |
| Reader feelings can be optimized on a chart | Reader experience is an intended artistic effect, not a measured output | Evidence-linked promise, phase function, and uncertainty |
| More graph nodes make a richer story | A large graph can be descriptive rather than causally productive | High-value engines, relationships, choices and transformations |
| One unified pane should expose everything | Simultaneous capability density can make the author manage tooling | Contextual disclosure and quiet focus |
| Long-term AI recollection is a reliable memory | Retrospective motivations may be invented | Source-bound work history and visible uncertainty |
| Literal maps make setting vivid | Places matter through experience and constraints, not coordinates alone | Place -> choice -> scene navigation |

**Negative space matters.** No justification emerged here for a universal conversation sidebar, new ontology, automatic canonical promotion, numeric reader-quality model, all-purpose graph database, mandatory preference questionnaire, or dashboard-first default.

### 9.8 Evidence to distinguish the strongest rival experiences

Do not reduce these qualitative futures to a single ranking score. If a next decision requires evidence, use a task that could genuinely change the chosen representation.

| Rival interpretation | Smallest discriminating author task | Relevant finding |
| --- | --- | --- |
| Story Vision text is enough **vs** Intent Constellation adds something | Start from the same setting/mood fragments in either interface | Distinct sustaining story mechanism found without extra administration |
| Whole graph is preferable **vs** question-local/semantic zoom | Find and explain a changing relationship across three Chapter scenes | Correct source and consequence with less lost context |
| Existing facets suffice **vs** reader-journey rehearsal | Identify where a promised tonal transition lacks narrative support | New causal insight rather than a prettier timeline |
| One current working candidate suffices **vs** parallel whole architectures | Preserve two incompatible story engines through a meaningful revision and re-entry | Demonstrable alternative preservation gap |
| Separate prose and graph are fine **vs** dual-plane integration | Draft, inspect structural function, revise intention, and return to prose | Lower repeated input, intact caret/edits, clear acceptance state |
| Reopen last focus is enough **vs** creative-thread re-entry | Resume a multi-Chapter project after a real absence | Correct last creative question and next action with transparent source grounding |

For preference/comprehension claims, use a reversible clickable comparison and actual human task observation when needed. For persistence/authority claims, verify exact old/new source identity and that accepted story state remains untouched. Browser tests do not establish literary quality; a polished sketch does not prove durability.

### 9.9 End-of-round synthesis — no strategic selection yet

The expanded landscape now names **twelve conceptually distinct author-job/interaction compositions**, their repo substrates, their strongest counterarguments, and discriminating evidence; it also documents recombinations and subtractive non-solutions. Some entries, especially P3 and portions of P9/P11/P12, are **already selected or partially implemented**. They are included as alternative *experience compositions*, not falsely presented as new capabilities.

**The major uncertainty left to Strategic Evolution Analysis** is whether to obtain the next unit of author value by **connecting established capabilities into one coherent creative workflow**, **deepening a distinctive visual reasoning mode**, or **making existing writing and re-entry dramatically simpler**. This review does not settle that choice.

**Stop rule for this exploration round:** further candidate labels are unlikely to improve decisions without observing an author job or encountering a demonstrable workflow gap. Revisit possibilities only when new evidence changes their distinctness or feasibility. The current F2/X3 controlled frontier and existing product authority remain unchanged. Neither this research file nor its PR grants implementation, merge, release, or thesis-change authority.

**Companion strategic synthesis:** [Auteur UI Strategic Evolution Analysis](auteur-ui-strategic-evolution-2026-10-24.md) compares coherent construction futures separately. This possibility landscape remains unranked and does not authorize work.
