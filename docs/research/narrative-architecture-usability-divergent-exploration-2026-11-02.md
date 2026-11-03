# Divergent Exploration — Narrative Architecture UI Usability as Creative Comprehension

**Date:** 2026-11-02  
**Repository/source baseline:** \`ThorStarlord/auteur\`, \`main@7a0c244181b38d5d041fa0b7142b7360acb97e30\`  
**Disposition:** **DIVERGENT / UNRANKED / DOCUMENTATION ONLY**. No preferred direction, convergent evaluation, product commitment, implementation plan, accepted story mutation, roadmap promotion, or UX-quality claim.  
**Question:** What materially different experiences could make Auteur's Narrative Architecture easier to *understand, navigate, interrogate and use* without reducing its expressive depth?

## 1. Frame: usability is not merely a smaller graph

The earlier [UI Possibility Landscape](auteur-ui-possibility-landscape.md) explores six seed futures and twelve extended possibilities, P1–P12. Those emphasize **what kinds of stories and authoring experiences** the UI may enable: Intent Constellation, Question-Centered Studio, Semantic Zoom, Quiet Studio, Manuscript/Map Dual Plane, parallel alternatives, and so on.

This new round asks a different question: **How does an author learn what the interface means, find their way through it, act without accidentally asserting story facts, and recover when a complex representation becomes confusing?** The object of discovery is *interaction intelligibility*, not another domain ontology or a new story-development subsystem.

**Strength of the framing:** It separates a UI comprehension problem from a generator/graph coverage problem. A valid, sophisticated candidate can still be difficult to read.

**Counterargument:** “Usability” could become an endless inventory of hover states, colors, labels and progressive disclosures. Each possibility below therefore has to change a user's **cognitive task, interaction contract, or meaning of an action**—not merely decorate the same navigation model.

**Authority and operating constraints:** [MISSION](../../MISSION.md) preserves local-first, single-author, backend-neutral creative work; no automatic acceptance, publication, unbounded provider integration, or new source of story canon. The graph-first target is already selected in the [Living Story Studio design](../design/2026-10-09-living-story-studio.md); a speculative alternative presentation is not an implicit reversal of that product decision.

## 2. What the current repository actually exposes

| Established surface | Code-grounded affordance | What is *not* established |
| --- | --- | --- |
| **Studio shell and graph** | [studio.html](../../src/auteur/beginner/browser/studio.html), [studio.js](../../src/auteur/beginner/browser/studio.js): Narrative Architecture / Story Realization workspaces, source-bound proposal nodes and directed links, working nodes, inspector, search, focus, fit and pan/zoom. | That first-time authors naturally infer graph meaning or locate the right action. |
| **Six lenses** | Overview, Emotions, Genres, Tropes, Structure and Timeline; there are also Focused Unfolding and Full Architecture depth surfaces, a facet history and a semantic trail. | That these navigational axes form one intuitive mental model; source-level functionality is not experienced clarity. |
| **Semantic explanations** | [Studio explanatory views](../../src/auteur/beginner/browser/studio_explanation_views.js), [Full Architecture](../../src/auteur/beginner/browser/studio_full_architecture.js), inspector and edge labels offer distinct explanatory projections. | That node/link language is comprehensible without domain vocabulary or an explanatory tour. |
| **Creative intervention** | [Mentor dialogue](../../src/auteur/beginner/browser/studio_mentor_dialogue_controller.js) and [Focused Unfolding](../../src/auteur/beginner/browser/studio_unfolding_controller.js) expose proposals and author-controlled, editable working previews. | That the steps between “explore,” “keep,” “revise” and “write” feel continuous to an actual writer. |
| **Host-agent lifecycle** | Architecture/Realization/Mentor prepare, response, status, stale and review flows exist; advanced raw request/response disclosures and “Check result” controls are visible. | That an author understands which step Auteur performs and which step still requires an active host coding agent. |
| **Accessibility and small screens** | Semantic HTML buttons, outlines, labels, focus indicators, a narrow-screen media query and reduced-motion rules appear in [studio.css](../../src/auteur/beginner/browser/studio.css). | Complete keyboard/screen-reader navigation, graph understanding without vision, or comfortable phone use. |

### Historical evidence and its time boundary

- The [October 11 information-UX report](../design/2026-10-11-narrative-architecture-information-ux-plan.md) recorded crowded controls, nearly identical node styling, repeated timeline prose, insufficiently legible relationships and incorrect workspace/inspector pairing in historical screenshots. It also specified targeted UX-0–UX-5 corrections; **do not resurrect those old defects as claims about current \`main\` without retesting**.
- The [October 12 explanatory-views comparison](../reviews/2026-10-12-studio-explanatory-views-comparison.md) found source-bounded advantages and limitations of Genre Anatomy, Convention vs. Invention, and Narrative Mechanism Map **in a prototype**. Its actual Chromium checks did not use the production server, and no novice comprehension study was performed.
- The [earlier adversarial UX review](../product-validation/living-story-studio/adversarial-ux-review.md) reproduced a then-existing unsaved-inspector-edit loss and identified historical canvas re-entry confusion; later source includes save/re-entry work. The new exploration treats *recovery as a user experience* without assuming those defects still exist.
- The [November 2 creative-reasoning strategy](auteur-ui-strategic-evolution-2026-10-24.md#11-follow-on-strategic-evolution--narrative-architecture-as-a-creative-reasoning-ui-2026-11-02) focuses on the agent's prospective use of architecture. This exploration remains about *the author's experience of that reasoning*.
- As of this source inspection, no new production Browser session, real-user comprehension test or live host-agent creative journey was run. [R0 execution limitation](https://github.com/ThorStarlord/auteur/issues/504) is a separate environment boundary, not a usability verdict.

## 3. Morphological axes missing or underdeveloped in P1–P12

Each row is a spectrum of possibilities, not a recommended setting or a state machine.

| Dimension | Distinct interaction possibilities | Usability misconception being challenged |
| --- | --- | --- |
| **Navigation question** | “Where am I?” / “Why am I here?” / “What can I do from here?” / “Where is the evidence?” | Six category facets alone establish orientation. |
| **Explanation grammar** | Node labels / full relation sentences / mini-argument / concrete counterexample / dramatic enactment | Seeing a directed arrow is understanding a narrative connection. |
| **Attention unit** | Whole graph / local neighborhood / one author task / one comparison / one unresolved unknown | Fixed node count or zoom level is the right measure of cognitive load. |
| **Authority legibility** | Always-visible summary / on-demand provenance / exposed host input window / before-and-after freshness explanation | A small “proposed” label makes all agent-authorship boundaries obvious. |
| **Action semantics** | Move presentation / ask a question / sketch a hypothesis / keep a working idea / review a narrative change | A gesture on a graph necessarily edits the story. |
| **Learning posture** | Optional plain-language translation / worked example / author teach-back / specialist register | Every writer enters with the same narrative-design vocabulary. |
| **Representation language** | Diagram / argument / museum exhibit / theatre rehearsal / orchestral score / sequential audio route | A graph is the only meaningful way to grasp a graph-shaped model. |
| **Use context** | Desktop exploration / narrow-screen reading / keyboard-only traversal / printout / return after lost focus | One reduced-scale spatial canvas is universally usable. |
| **Recovery** | Empty-result explanation / stale-source diagnosis / old-focus rescue / deliberate undo | Errors need only a technically accurate message. |

## 4. Nine overlapping conceptual families, twenty-seven distinct possibilities

The identifiers U01–U27 are *stable research references*, not priorities. Each idea provides a specific hypothetical experience, an inspiration, a difference from current/prior concepts, and a credible cost or failure condition.

### Family A — Finding one's way without learning Auteur's taxonomy first

#### U01 — Author-Task Compass
- **Experience:** The author asks “What is holding this story together?” or “Why does this choice matter?”; the interface offers a route through *existing* Structure, relationship inspector and Mentor rather than asking the author to choose a category facet first.
- **Inspiration:** Information scent and wayfinding; museum visitor asks a question before selecting an exhibition wing.
- **Novel distinction:** Unlike P2 Question-Centered Studio, the question is an **ephemeral wayfinding task about the interface**, not a persisted dramatic question about the story.
- **Trade-off:** A task launcher could become another toolbar or incorrectly guess the author's intention.

#### U02 — Guided Thread with an Exit
- **Experience:** Choose “Explain the ledger's role” and follow a short, reversible path through ledger → obligations → genre function → reader intention; at each step, the author sees the relation used and an explicit Return to Origin.
- **Inspiration:** Guided museum tours and stepwise debugging.
- **Novel distinction:** P10 Semantic Zoom changes **scale**; this changes **navigation contract** from free wandering to a bounded explanatory itinerary. Current semantic trails and facet history are substrate, not proof that this guided task exists or is needed.
- **Trade-off:** Any preconstructed route may imply a connected causal chain that source links do not actually support.

#### U03 — Narrative Landmarks and Home Base
- **Experience:** The current Vision, selected working question and inspected architectural concept remain recognizable landmarks while the author changes facets; a compact “You are viewing X because you followed Y” appears without losing the graph.
- **Inspiration:** Geographic landmarks and breadcrumbs.
- **Novel distinction:** P11 Creative-Thread Re-entry concerns returning **across sessions**; this concerns orientation **within one complex exploration**. Existing semantic arrival/history provides a partial foundation.
- **Trade-off:** Too many landmarks repeat the clutter they were meant to solve.

### Family B — Making relationships legible as arguments

#### U04 — The Arrow Becomes a Sentence
- **Experience:** Selecting a link reads “The annual allocation decision carries inherited obligations into the following flood season,” with *source*, *relationship wording* and *target* distinctly visible. A direction marker remains, but a short sentence does the explanatory work.
- **Inspiration:** Plain-language logic and subject–verb–object reading.
- **Novel distinction:** Existing edge labels/titles expose relationship text; this idea asks whether **a complete readable proposition as the primary object** is easier than spatial line inspection.
- **Trade-off:** Turning short, ambiguous free-text \`ArchitectureLink.function\` into grammar could invent causal certainty.

#### U05 — Multiple Readings of One Relation
- **Experience:** The same ledger → unease edge can be inspected as “what is stated,” “what is only interpretive,” and “what would make this causal?” without silently creating another edge.
- **Inspiration:** Literary close reading and legal interpretation of evidence.
- **Novel distinction:** Rather than a new typed-edge ontology, this is a **critical reading interaction over one source claim**. Its multiple interpretations must remain labelled hypotheses.
- **Trade-off:** Excessive interpretation could make even a simple edge laborious to understand.

#### U06 — Explain the Missing Connection
- **Experience:** After selecting a mechanism and an intended emotion, the UI can say “No disclosed source link connects these concepts,” optionally offering a **question** the author might investigate, rather than an invented colored arrow.
- **Inspiration:** Negative space in maps, explicit unknowns in scientific diagrams.
- **Novel distinction:** Existing Structure prototypes already suppress unsupported arrows; this explores **absence as intelligible information**, not an automatic link-prediction feature.
- **Trade-off:** Absence of a recorded relation is not evidence that the story lacks that relationship; the copy must not condemn an underdocumented work.

### Family C — Controlling cognitive load without impoverishing the design

#### U07 — Meaningful Folded Neighborhoods
- **Experience:** A dense flood/ledger/obligation neighborhood is temporarily represented by a card explaining the shared mechanism; opening it restores every underlying node and source relation.
- **Inspiration:** Hierarchical document folding and cartographic generalization.
- **Novel distinction:** P10 Semantic Zoom moves between **Book/Chapter/scene scales**; this folds **same-level explanatory detail** without creating a supernode in story canon.
- **Trade-off:** Machine-generated compression may conceal disagreement, direction or independent meanings.

#### U08 — Attention by Purpose, Not by Node Count
- **Experience:** “Understand reader unease” foregrounds only the relevant declared emotion, genre and phase evidence; “understand renewability” foregrounds a different subset of the same candidate. No components are deleted or accepted.
- **Inspiration:** Selective attention and task-specific scientific visualization.
- **Novel distinction:** Existing filters/focused neighborhoods are largely category, search or spatial; here **author purpose** governs temporary salience.
- **Trade-off:** Relevance filtering can hide the very counterexample the author needed.

#### U09 — First-Class Linear Architecture
- **Experience:** The whole abstract architecture can be read as a structured, navigable argument—Vision → mechanisms → relationships → intended experiences → open questions—with direct links to the same graph nodes.
- **Inspiration:** Book tables of contents and accessible structured documents.
- **Novel distinction:** Current UI has an accessible outline of visible story items and Full Architecture text. This possibility treats **linear comprehension as an equal alternative interaction**, not merely a fallback index.
- **Trade-off:** Lists can erase unexpected spatial relationships; the linear view must not reassign authority or invent a privileged order.

### Family D — Interacting with the graph without accidentally asserting narrative meaning

#### U10 — Connect-to-Ask
- **Experience:** An author indicates two concepts spatially and chooses “Ask how these might relate” rather than “Create a relationship.” The result is an explicitly provisional question or Mentor hypothesis.
- **Inspiration:** Exploratory sketching and conversational questioning.
- **Novel distinction:** Current \`Connect\` saves an author-working association, while agent-proposed source links have another owner. This interaction keeps **asking** distinct from **asserting**.
- **Trade-off:** New gestures could be confused with existing dragging, linking and working-author edit controls.

#### U11 — What Will This Action Change?
- **Experience:** Before a consequential action, a compact explanation distinguishes “move this visual card,” “save a working idea,” “request an agent revision,” and “review a working candidate.” Accepted story remains untouched by all four unless an existing acceptance owner explicitly acts.
- **Inspiration:** Direct-manipulation previews and mistake-proofing in industrial design.
- **Novel distinction:** P7 Causal Fork Bench previews **hypothetical story consequences**; this previews **the actual meaning and persistence effect of a UI action**.
- **Trade-off:** Confirmations on every harmless click would make exploration irritating.

#### U12 — Pencil Marks on the Graph
- **Experience:** The author temporarily circles an ambiguous pair, marks an edge “questionable” or draws a proposed relation without saving that mark as a story fact. On leaving exploration, they can consciously discard it or turn it into an explicit working question.
- **Inspiration:** Annotations on architects' tracing paper.
- **Novel distinction:** Current Unfolding offers proposal ghosts around source-related focus. This possibility is **user-initiated, reversible inquiry over an ambiguous relationship**, not a second canonical graph or persistent complete architecture fork.
- **Trade-off:** If the pencil layer becomes permanent state by stealth, it creates a new unsupported ownership problem.

### Family E — The agent and the evidence becoming understandable

#### U13 — Honest Request Journey
- **Experience:** One visible explanation shows “Request prepared → needs your host coding agent → response available → working review pending → source changed” as genuinely separate conditions, with the next possible action. It never says “Generating…” unless an agent actually runs.
- **Inspiration:** Package tracking and explicit state-transition explanations.
- **Novel distinction:** P3 Seamless Agent Design emphasizes **continuous authoring**; this emphasizes **truthful operational comprehension** even when the agent is external/manual.
- **Trade-off:** A process tracker can make Auteur feel like infrastructure management instead of writing software.

#### U14 — What the Agent Actually Saw
- **Experience:** Beside an explanation or candidate, the author can inspect the exact disclosed Vision, excerpt lengths, omitted working items and cited source references, with a clear distinction from unseen Book content.
- **Inspiration:** Scientific provenance cards and reproducible experimental notebooks.
- **Novel distinction:** Existing requests carry source/omission information and advanced disclosures. This possibility shifts **input visibility into the author's comprehension path** rather than making it an operator-only JSON inspection.
- **Trade-off:** Technical fingerprints and source volume can overwhelm nontechnical writers; exposing source text must respect local privacy.

#### U15 — Staleness as a Human-Readable Difference
- **Experience:** Instead of only “This architecture is stale,” the author sees “You changed the Story Vision after this proposal; the earlier answer may no longer reflect the new intention,” plus both identified versions where available and a safe review path.
- **Inspiration:** Version-control diffs translated into task consequences.
- **Novel distinction:** The backend already protects stale sources. This explores **understanding and repair**, not weakening freshness to make old work appear valid.
- **Trade-off:** An incomplete difference summary must not be presented as an exhaustive explanation of why all downstream consequences changed.

### Family F — Learning narrative architecture without a prerequisite course

#### U16 — Two Registers: Writer Language and Design Language
- **Experience:** “What makes this story keep producing events?” appears beside “Narrative Engine”; “What do we want the reader to feel?” beside “Emotion Target.” An author can move between registers without changing the underlying graph model.
- **Inspiration:** Bilingual technical manuals and progressive conceptual scaffolding.
- **Novel distinction:** P12 Quiet Studio hides distractions; this explicitly **translates the same semantic content** for different levels of narrative-design literacy.
- **Trade-off:** Simplification can erase real distinctions; experienced authors may prefer immediate precision.

#### U17 — One Worked Example, One Counterexample
- **Experience:** On an engine or trope function, the UI shows a tiny fictional **illustration** of a renewable mechanism and a nonrenewable lookalike. It labels examples as educational hypotheses, not as generated scenes or approved story facts.
- **Inspiration:** Contrastive teaching and worked examples.
- **Novel distinction:** Existing explanations describe content and source; this teaches **how to interpret the type of content** by contrasting valid and misleading readings.
- **Trade-off:** Illustrations can bias the author toward canned genre conventions or be mistaken for literal story proposals.

#### U18 — Optional Teach-Back
- **Experience:** The author can answer “What do you think this relation means for your story?” and compare their understanding with the literal recorded edge and alternative interpretations. No numerical competence score and no required onboarding quiz.
- **Inspiration:** Socratic tutoring and educational teach-back.
- **Novel distinction:** Current Mentor asks creative questions; here the object is **checking the interface's communicative clarity**, including whether it caused a misunderstanding.
- **Trade-off:** A forced or patronizing tutorial is worse than an imperfect graph.

### Family G — Dramatizing architecture through unfamiliar visual metaphors

#### U19 — Rehearsal Stage
- **Experience:** An abstract mechanism is illustrated by a deliberately hypothetical 60-second “rehearsal”: a flood creates scarce water, two anonymous roles interpret the ledger differently, a decision changes future obligations. The author returns to the abstract node afterward.
- **Inspiration:** Theatre rehearsals and thought experiments.
- **Novel distinction:** P9 Manuscript/Map Dual Plane concerns **actual drafting continuity**. This is **provisional dramatization to understand a mechanism**, not production prose, canon or Realization acceptance.
- **Trade-off:** A vivid rehearsal may be mistaken for chosen characters/events or narrow a deliberately abstract design.

#### U20 — Museum of Story Mechanisms
- **Experience:** The architecture can be experienced as a sequence of exhibit placards: each shows one mechanism, the author's intention, source evidence, what it enables, an opposing interpretation and a door back to the full map.
- **Inspiration:** Exhibition design and object-centered interpretation.
- **Novel distinction:** U02 routes through **relations toward a particular task**; this treats each concept as a **self-contained object of contemplation**, not a node to navigate past.
- **Trade-off:** Beautiful exhibits can make an architecture feel complete and settled even when it is uncertain.

#### U21 — Orchestration Score
- **Experience:** Genre functions and narrative engines appear as simultaneous “voices” entering, reinforcing, contesting or receding across phases; author-declared and hypothesized transitions remain marked distinctly.
- **Inspiration:** Orchestral scores and polyphonic composition, using a visual metaphor rather than playing music.
- **Novel distinction:** P6 Reader Journey Rehearsal follows **intended emotional experience over time**; this shows **the interplay of several mechanisms at the same time**, not a predicted audience emotion or a prettier timeline.
- **Trade-off:** Musical vocabulary may be less intuitive than a table, especially for readers who do not use music notation.

### Family H — Different authors, devices and perceptual modes

#### U22 — Narrated Relationship Route
- **Experience:** A keyboard/screen-reader user follows an ordered list of actual source-linked propositions with “previous / next / inspect source / return”; it announces direction, uncertainty and current location without requiring perception of SVG geometry.
- **Inspiration:** Audio descriptions and accessible guided reading.
- **Novel distinction:** This is not merely alt text for graph nodes or the existing visible-item outline. It is **independent traversal of architectural relationships** using exactly the same source identities.
- **Trade-off:** Linear traversal can become exhausting for large networks; a meaningful skip/group facility matters.

#### U23 — Pocket Architecture
- **Experience:** On a small screen, one selected concept, its related claims and the next safe action fill the viewport; the entire graph is a secondary orientation surface, not a miniature two-dimensional desktop.
- **Inspiration:** Pocket field guides and mobile wayfinding.
- **Novel distinction:** The existing responsive CSS stacks panels. This possibility reconsiders **which cognitive task a narrow device serves**, rather than only fitting desktop controls into the width.
- **Trade-off:** Mobile-first simplification can split the user's mental model across devices and hide productive complexity.

#### U24 — Printable/Portable Story Argument
- **Experience:** The author carries a printed or static, readable architecture explanation with a selection of relations, open questions and provenance, and later returns to the corresponding source node in Auteur.
- **Inspiration:** Index cards, architectural blueprints, annotated books and analog creative practice.
- **Novel distinction:** Existing JSON export is a portable **data backup**; this is a portable **comprehension artifact**, not another story store or native application.
- **Trade-off:** Printed summaries become stale and cannot carry real-time interactive context; their status and source revision must remain clear.

### Family I — Failure, emptiness and recovery as normal creative states

#### U25 — Honest Empty Space
- **Experience:** When a facet has no proposed trope or source relationship, it says why that absence is expected or unknown and invites an author-owned question instead of simply showing an empty panel.
- **Inspiration:** Empty-state interaction design and epistemic humility.
- **Novel distinction:** Existing facets say “No [category] proposed yet.” This possibility asks whether an **absence explanation can preserve creative possibility** without fabricating a missing domain concept.
- **Trade-off:** Wrong diagnosis (“your story needs X”) turns a neutral gap into coercive advice.

#### U26 — Lost-Focus Rescue
- **Experience:** After an architecture revision removes a previously selected node, the user is shown the last known title/source identity and what is still accessible, then can consciously return to the graph or choose a new anchor.
- **Inspiration:** File recovery and broken-link repair.
- **Novel distinction:** Existing source handles stale selection and saved-focus fallback; this explores the **human experience of continuity after a removed/superseded referent**, not the long-horizon creative memory of P11.
- **Trade-off:** Resurrecting an old-looking node could imply that a superseded candidate is still current.

#### U27 — Undo the Exploration, Not the Story
- **Experience:** A user can retrace a temporary comparison, highlight, facet change or abandoned pencil sketch without touching saved working ideas. A committed working edit remains separately subject to its existing save/review rules.
- **Inspiration:** Exploratory undo and reversible direct manipulation.
- **Novel distinction:** This explores the difference between **navigation reversibility** and **story mutation rollback**, not a new accepted-state undo feature.
- **Trade-off:** A universal Undo that silently rolls back different authorities is dangerous; the meaning of reversible actions must be explicit.

## 5. Novelty crosswalk: how this round differs from P1–P12

| Earlier candidate | Superficially similar new proposals | Material difference |
| --- | --- | --- |
| P2 Question-Centered Studio | U01, U25 | P2 stores a **story question** as creative material; U01 routes an **interface comprehension task** and U25 explains absent evidence. |
| P3 Seamless but Inspectable Agent Design | U13–U15 | P3 follows an author revision through agent work; U13–U15 make the **operational and evidential truth of each step** intelligible without pretending to automate it. |
| P6 Reader Journey Rehearsal | U21 | P6 examines the intended reader's experience over phases; U21 examines simultaneous **genre and mechanism polyphony**, without asserting effects on an actual reader. |
| P7 Causal Fork Bench | U11, U12 | P7 compares hypothetical **fictional outcomes**; U11 explains the real persistence effect of a UI action and U12 sketches a temporary **question**. |
| P9 Manuscript/Map Dual Plane | U19, U24 | P9 unites actual prose work with structure; U19 is a hypothetical explanatory enactment and U24 is portable **reading**, not an alternative manuscript owner. |
| P10 Semantic Zoom | U02, U07, U09 | P10 traverses narrative scale; U02 constructs an explanatory path, U07 folds **same-level detail**, U09 makes a parallel linear reading first-class. |
| P11 Creative-Thread Re-entry | U03, U26 | P11 recovers a creative purpose after absence; U03 and U26 preserve **in-session orientation and honest loss of a changed target**. |
| P12 Quiet Studio | U08, U16 | P12 subtracts visible distractions during focused writing; U08 varies relevant evidence by task and U16 offers equivalent **language registers** for different literacy. |

**Research warning:** Some ideas may already be partially supported by code, as stated explicitly. “Different possible interaction” does not imply “missing feature,” and it certainly does not imply a validated user problem.

## 6. Overlaps and unexpected combinations (not implementation bundles)

These are *nonexclusive conceptual intersections*, with no selection or promise to build them.

- **Language-first graph (U01 + U04 + U09 + U22):** One narrative query, a readable source-accurate sentence and a nonspatial route could support both novice comprehension and screen-reader navigation.
- **Architecture as an exhibition (U03 + U20 + U21):** Static landmarks and exhibit-like explanations could help an author understand simultaneous mechanisms without forcing the graph to display every field at once.
- **Epistemic sketchbook (U06 + U10 + U12 + U14):** Unknown connections become questions; provisional user marks and actual agent input visibility remain separate from working/accepted facts.
- **Transparent host workflow (U11 + U13 + U15 + U26):** Every step explains what changes, what remains pending and how old focus/source survives or is superseded. This could be reassuring or visually bureaucratic.
- **Learning through drama (U05 + U17 + U18 + U19):** Competing readings, examples and rehearsal could teach narrative functions without teaching a compulsory ontology course. Its danger is stronger artificial interpretations than the evidence warrants.
- **Architecture away from the desktop (U09 + U22 + U23 + U24):** The same source-grounded meaning travels through text, audio/keyboard traversal, a phone and paper; preserving meaning matters more than preserving identical geometry.

## 7. Assumptions worth keeping open

1. **“Graph-first means the graph must always dominate screen space.”** The selected graph-first entry does not by itself establish the optimal view for every explanatory subtask; a temporary linear or theatrical perspective need not replace the default.
2. **“Six facets make the ontology understandable.”** Facets make content reachable. They may not teach how a theme, engine, genre contract, trope function, structural phase and reader promise differ.
3. **“More visible data is better transparency.”** Complete raw request JSON may be truthful but unusable; conversely, plain-language explanation without access to actual inputs can conceal omission.
4. **“A readable arrow is a causal arrow.”** Directed, labelled links can express interpretive, thematic or merely enabling relationships. Usability should not upgrade free-text function to a strong causal theorem.
5. **“A writer wants one stable mental model.”** Some writers may prefer different representations for inventing, understanding, evaluating, drafting, recovering and teaching; switching costs could outweigh any gain.
6. **“Accessibility is the graph with different controls.”** A meaningful screen-reader journey may need a different **order of comprehension**, not just keyboard access to spatial elements.
7. **“Wrong user action means insufficient training.”** If moving, connecting, retaining a proposal and accepting story are difficult to distinguish, the interaction contract may be the problem.
8. **“Error states interrupt writing and should disappear.”** Honest stale, missing-evidence and incomplete-agent states can preserve authorship when they communicate recovery rather than system internals alone.
9. **“More beautiful visual metaphors are automatically more usable.”** An exhibition, theatre or score may improve understanding for one author and create worse uncertainty and navigation for another.

## 8. Distinct author encounters that could reveal different kinds of usability

These are **exploratory situations**, not a benchmark, test plan or ranking method.

| Hypothetical author encounter | What it could reveal without asserting a result |
| --- | --- |
| A newcomer sees a 12-node Tidal Archive design and asks “What makes this story work?” | Whether category labels, arrows or a narrative-language route provide the intended understanding. |
| An author switches through Emotions, Genres, Tropes and Structure while tracking one connection | Whether identity, source and return-to-origin remain obvious across the six current facets. |
| The author selects a free-text link that looks causal but may only be thematic | Whether the UI lets the user tell recorded statement from agent interpretation. |
| The author sees a candidate pending with no host-agent completion | Whether “prepared,” “waiting for external agent,” and “completed” are accurately distinguished without tech jargon. |
| The author changes the Vision after Mentor advice and reopens an old focus | Whether a stale result is visible as historical work and a new task is understandable, rather than silently reused. |
| A screen-reader user needs to understand why two engine concepts are connected | Whether an accessible outline is enough or source-grounded relational traversal is necessary. |
| An author reads the architecture on a phone, then writes at a desk | Whether the same source identity and task purpose survive across very different attention and screen constraints. |
| A prolific author intentionally declines all guidance and wants fast keyboard navigation | Whether an explanatory interface can remain optional and proportionate rather than coercively tutorial. |
| The author encounters a blank trope facet or an absent relationship | Whether no-data and unknown-data are conflated, or a neutral absence supports curiosity. |

**What this round did not do:** no direct usability testing, no visual screenshot comparison against current served Studio, no measured task times, no scores, no candidate filtering, no code implementation, no UX claim of improvement, no revised product priority, and no automatic promotion of concepts into a backlog or curated idea library.

## 9. Source and inspiration index

**Repository sources (current evidence and historical interpretation):**
- [Studio HTML](../../src/auteur/beginner/browser/studio.html), [Studio controller](../../src/auteur/beginner/browser/studio.js), [Studio CSS](../../src/auteur/beginner/browser/studio.css).
- [Studio explanatory views](../../src/auteur/beginner/browser/studio_explanation_views.js), [Full Architecture](../../src/auteur/beginner/browser/studio_full_architecture.js), [Mentor dialogue](../../src/auteur/beginner/browser/studio_mentor_dialogue_controller.js) and [Focused Unfolding controller](../../src/auteur/beginner/browser/studio_unfolding_controller.js).
- [Initial UI Possibility Landscape](auteur-ui-possibility-landscape.md) and [Creative Reasoning strategic extension](auteur-ui-strategic-evolution-2026-10-24.md#11-follow-on-strategic-evolution--narrative-architecture-as-a-creative-reasoning-ui-2026-11-02).
- [Information UX design](../design/2026-10-11-narrative-architecture-information-ux-plan.md), [Explanatory-prototype comparison](../reviews/2026-10-12-studio-explanatory-views-comparison.md), [Historical adversarial UX review](../product-validation/living-story-studio/adversarial-ux-review.md), [2026-10-21 W4 qualitative assessment](../reviews/2026-10-21-w4-narrative-architecture-qualitative-assessment-v1.md), [Current STATUS](../../STATUS.md).

**Cross-domain inspiration (analogies, not imported requirements or UX evidence):** wayfinding, museum exhibitions, cartographic generalization, close reading, readable logic, scientific provenance, annotated architectural tracing paper, industrial mistake-proofing, Socratic teaching, contrastive examples, theatre rehearsals, orchestration scores, assistive audio navigation, pocket field guides, print-first creative practice and version-control explanations.

**End of divergent round:** Preserve all materially different possibilities. Their costs and doubts are part of each hypothesis, not evidence for ranking, removing or prematurely selecting any one. A later convergence request would be a distinct owner-governed activity.
