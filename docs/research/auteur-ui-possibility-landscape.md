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

1. **Divergent Exploration:** Expand and organize materially different author jobs, interaction models, and combinations. Record the repository source each idea reuses and what would actually be novel. This document is the initial landscape, **not a completed exhaustive search**.
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
