# Agent-First, Ontology-Grounded Narrative Architecture — Design Brief

**Date:** 2026-11-03
**Status:** DRAFT FOR AUTHOR REVIEW — product design, not implementation authorization
**Scope:** Auteur's author-facing creation, understanding, holistic revision, and longitudinal continuity of working Narrative Architecture
**Authority:** This document describes the desired experience and constraints. It does not supersede canonical narrative contracts, accept any Story Identity or Structure, change the shared ontology, or select an engineering implementation.

## 1. Purpose and product thesis

The author wants to describe a Story Vision and ask a coding agent to construct a **complete first Narrative Architecture**: the intended audience experience and emotions, narrative structure, genres, trope functions, narrative mechanisms, and their causal and temporal relationships. The author may then request **holistic revisions** in natural language. The coding agent is the primary authoring interface; the visual Studio and graph can help the author inspect or directly change parts, but the author must not need to manipulate nodes or master an ontology before obtaining a coherent proposal.

The architecture must use Auteur's **repository-grounded narrative ontology**, not the improvised vocabulary of an individual chat session. Creativity may reveal useful new concepts. Those concepts can be recorded and reused provisionally, including after a new agent takes over, without automatically promoting them into the shared ontology. The ontology is stable enough for continuity and open enough to evolve through review.

The central outcome is **an author-directed, agent-constructed, understandable and revisable story design that survives session and agent boundaries**.

## 2. Agreed decisions versus proposed refinements

### Explicit author selections

- The coding agent, not a manually operated graph, is the primary interface for constructing Narrative Architecture.
- Given a Story Vision, generate a complete first proposal rather than delaying for a required creative interview.
- The minimum useful architecture includes target audience emotion, narrative structure and trope choices; explain how they work together.
- Revising a significant creative objective should be **holistic**, not limited mechanically to one changed field.
- Generation and revision should follow the narrative ontology established in the repository for conceptual consistency across sessions.
- An agent may propose an ontology extension for review; a software system must be capable of evolution.
- Narrative concepts found in one session should remain available to later sessions or different coding agents.
- Technical implementation details, including how provisional knowledge is stored and passed between agents, belong primarily to the coding agent.

### Design recommendations to validate, not additional author commitments

- Distinguish **author-declared**, **accepted**, **agent-proposed**, **provisional**, and **unknown** claims in reviewable explanations.
- Present a short readable architecture first, with optional graph and deeper technical views.
- Explain holistic changes as: requested direction; affected relationships; proposed coordinated changes; preserved commitments; remaining choices.
- Let a provisional concept support ongoing project work without treating it as a newly approved universal ontology definition.
- Make the boundary between preparing an agent request, successfully executing it, receiving a candidate, and accepting a story decision unambiguous.

## 3. Approaches considered and selected

| Design choice | Alternative | Decision and reason |
| --- | --- | --- |
| Initial authoring | Manually build a graph before generation | **Not selected.** Makes operating the tool the prerequisite to telling the story. The existing graph may remain valuable as an optional inspector. |
| Initial authoring | Required interview or incremental co-design | **Not selected as default.** The author wants a complete first proposal, not a series of blocking questions. |
| Initial authoring | Agent creates one coherent proposal from the Story Vision | **Selected.** Preserves creative momentum and lets the author react to a concrete design. |
| Revisions | Change only the directly named field | **Not selected as default.** It can leave emotions, tropes and structure inconsistent. |
| Revisions | Holistic reasoning across connected narrative elements | **Selected.** The agent proposes coordinated changes while preserving explicit constraints and author control. |
| Conceptual vocabulary | Freeze ontology permanently | **Not selected.** Prevents meaningful conceptual evolution. |
| Conceptual vocabulary | Automatically promote every discovered term to shared ontology | **Not selected.** Risks duplicates, incompatible meanings and drift. |
| Conceptual vocabulary | Reusable provisional concepts with reviewed shared extensions | **Selected direction.** Enables discovery and continuity without silently changing common definitions. |

This selects product behavior, not code, storage formats, prompt layouts, API boundaries, or a replacement for the existing graph-first Studio target.

## 4. Author experience

### Journey A — First architecture from a Story Vision

1. The author supplies a free-form vision, ranging from a short premise to a richer description of themes, intended feelings, genres and creative constraints.
2. The agent consults relevant established repository concepts and any actually accepted project commitments, interpreting absent preferences as unknown rather than inventing author decisions.
3. Without requiring follow-up answers, the agent produces a **complete, self-consistent first proposal** at the appropriate abstract level. Where the input is insufficient, it makes plainly labeled provisional choices and records consequential unresolved author preferences.
4. The author receives a readable overview, reasons for major choices, and optional ways to inspect relationships or the underlying graph.
5. The author may keep the working proposal, ask for a revision, compare alternatives, or inspect specific concepts. Generating or viewing a proposal does not itself accept canonical story commitments.

**Expected experience:** “I described the story I want; the coding agent designed an intelligible architecture I can react to.”

### Journey B — Holistic natural-language revision

1. The author expresses a creative change: for example, “Make wonder the dominant audience experience; retain mystery, but make the structural progression more adventurous.”
2. The agent considers the affected emotion promise, supporting palette, structural progression, narrative engines, trope functions, genre interactions, payoff expectations, and relevant thematic consequences.
3. It proposes a coherent revised architecture rather than blindly replacing one label. It identifies choices maintained, changes prompted by causal dependencies, additional optional suggestions and conflicts with accepted author commitments.
4. The author can compare the proposed and previous versions, keep or reject the working revision, and request further changes. Direct low-level editing remains possible but is not the primary path.
5. No working revision silently rewrites accepted Identity, Structure, Realization, Expression, or shared ontology.

**Expected experience:** “I changed the creative direction; the agent reconciled the story design, explained its reasoning, and preserved my authority.”

### Journey C — New conversation or coding agent

1. A later agent enters the same project without depending on the previous conversation history.
2. It can recover the Story Vision or accepted story sources, latest relevant working architecture, applicable conceptual definitions, known author constraints, unresolved decisions, and any recorded provisional concepts.
3. The new agent distinguishes what the author actually accepted from prior agent interpretations and can continue or revise without contradicting established terms merely because the conversation changed.
4. If sources or ontology guidance have changed, the agent acknowledges meaningful differences instead of pretending the prior design used the current definitions unchanged.

**Expected experience:** “I can switch agents without explaining the whole narrative system or rediscovering the same creative decisions.”

### Journey D — An ontology extension is needed

1. During story design, the agent identifies a useful concept that the current ontology cannot adequately express.
2. It explores the concept as a labeled project-level proposal, checking whether an existing concept already covers it.
3. It may propose a reusable shared extension with its definition, distinctions, relations, motivating use, and compatibility concerns.
4. The author reviews shared conceptual changes separately from the story's creative development. Pending or rejected extensions must not masquerade as accepted shared vocabulary.
5. Provisional project knowledge remains understandable and reusable across sessions without requiring immediate universal promotion.

**Expected experience:** “A new creative idea helps this story now, and Auteur can learn from it later without losing conceptual discipline.”

### Journey E — A host agent has not actually run

The interface distinguishes a request prepared for an external coding agent from a request executed, a response received, a response ready for review, and an accepted decision. It never reports a generated architecture solely because a handoff was staged. A failed or unavailable execution does not invent completion.

## 5. Minimum useful Narrative Architecture

A first proposal should be **coherent and complete as an abstract design**, not a fully plotted story. Its explanations should cover, to the extent supported by the Vision:

- **Reader promise and emotional design:** primary intended experience, supporting and contrasting emotions, avoided experiences when expressed, contextual means of eliciting them, and broad emotional progression. Basic emotion labels are not substitutes for richer effects such as wonder, belonging or dread.
- **Genre composition:** roles and interactions of genres, including what each contributes to reader experience, structure and recurring narrative mechanisms.
- **Tropes as functional choices:** why a trope matters, what it enables or constrains, and how it contributes to the story rather than functioning as a decorative checklist.
- **Narrative mechanisms and causal organization:** renewable sources of conflict, pressure, discovery, reversal, consequence and payoff, including concentrated or distributed causal designs when justified.
- **Narrative structure:** abstract progression, phases or threads, ordering, transitions, important overlaps, and the evolution of reader expectations. Abstract architecture is not a requirement to invent chapter numbers, concrete events or an entire scene outline.
- **Relationships and coherence:** meaningful connections among emotion, genre, trope, engine, structure, aesthetics and themes; no fabricated links solely to make a connected graph.
- **Creative rationale and uncertainties:** which choices came from the author, which are agent proposals, what evidence supports the interpretations, and what remains unknown.

The architecture should be rich enough for later story development without crossing into unsupported concrete plot invention. If the author supplies concrete canon, the agent can cite it as a constraint; it must not silently fabricate additional canonical details.

## 6. Ontology, authority and continuity boundaries

- **Ontology defines meanings.** It provides narrative concepts, relationships, constraints and distinctions.
- **Identity owns accepted story commitments.** The agent may propose but must not silently rewrite them.
- **Structure owns accepted plans.** Abstract Studio proposals do not automatically become canonical outlines.
- **Realization and Expression remain separate.** An architecture proposal is not a concrete event history or finished prose.
- **Working exploration remains noncanonical.** Visual graph nodes, candidate architecture, rationale and provisional concepts remain distinguishable from accepted source contracts.
- **Continuity is repository-grounded.** A change of session, model, or coding agent should not alter conceptual definitions merely because the prior chat is unavailable.
- **Evolution is explicit.** New concepts may be proposed, reviewed and, when justified, accepted without silently changing historical interpretations of prior work.
- **Freshness is intelligible.** Distinguish changes in author-authored story sources from changes in interpretive guidance or ontology, leaving the exact technical mechanism to implementation planning.

The agent should consult relevant authoritative definitions instead of assuming that a file mentioned in a development-agent instruction was necessarily read by the creative host agent. What the creative agent actually saw must be inspectable when continuity or compliance is at issue.

## 7. Interface principles

- **Conversation is the authoring default.** The author requests first generation, major revisions, deeper explanations and alternatives through the coding agent.
- **A readable explanation comes first.** The author can grasp the emotional promise, structural logic and trope functions before drilling into technical fields.
- **The graph is an inspection and optional editing surface.** It should illuminate relationships without obliging authors to build those relationships by hand. The existing graph-first Studio direction remains a product constraint; how conversational control coexists with its navigation is an implementation design question.
- **Meaningful changes are reviewable.** The author can identify what changed, what remained stable and why.
- **Unknown is legitimate.** A sparse Story Vision should prompt provisional reasoning, not false certainty or an unnecessary required questionnaire.
- **Technical status is honest.** The interface must not confuse an instruction to an agent with completed generation, or a draft with an accepted source.
- **Accessibility and alternate views matter.** The agent-driven workflow must not require visual graph comprehension, and architecture should be intelligible in a linear textual form.

## 8. Non-goals and anti-goals

**Not required:** a new ontology layer, new persistence service, universal orchestration framework, automatic story publication, autonomous acceptance of canon, forced ontology approval before exploring a story, complete plotted content from an abstract Vision, or replacing existing Studio and narrative contracts.

**A failure even if code works:** the agent outputs a plausible list with no explanatory connections; a session switch loses the meaning or status of earlier ideas; the system silently accepts story or ontology changes; a revision ignores related narrative systems; the interface promises execution that never occurred; or writing a story requires manually authoring a graph first.

## 9. Validation through author-facing scenarios

The future implementation plan should derive evidence-producing checks from these behaviors, not assume narrative quality from schema validation alone.

1. **Initial generation:** From an unfamiliar Story Vision, produce a complete abstract design with emotions, structure, functional tropes and causal relationships. The author can explain why they fit together.
2. **Holistic change:** Shift the primary reader experience and inspect whether all materially affected elements are reconsidered without gratuitously changing unaffected commitments.
3. **Preservation:** Supply an accepted Identity that conflicts with a revision request; the agent surfaces the conflict rather than rewriting it.
4. **Cross-session continuation:** Continue with a different agent or a fresh conversation using repository state, with concepts, unresolved questions and provenance recoverable.
5. **Provisional novelty:** Introduce a useful concept outside current vocabulary, reuse it provisionally, and propose a reviewed extension without accidentally canonizing it.
6. **Honest execution:** With no runnable host-agent path, show a real pending/blocked state instead of a false completed candidate.
7. **Comprehension:** Without manually editing a graph, the author can read the proposal, inspect the effects of a requested change and request another revision.

These are required demonstration scenarios, not claims that the current product already passes them. Actual usability and creative quality remain unverified until observed.

## 10. Existing repository context and constraints

- [Canonical narrative architecture](../../narrative-architecture.md) defines semantic-layer authority and scope.
- [Living Story Studio design](../../design/2026-10-09-living-story-studio.md) already selects a graph-first Studio, agent-generated architecture and source-honest handoff model.
- [Ontology base concepts](../../../data/ontology/base_ontology.yaml) and [architecture preferences](../../../src/auteur/narrative_ontology/architecture_preferences.py) encode reusable concepts and independent, optional preference dimensions.
- [Initial architecture adversarial review](../../reviews/2026-10-21-initial-narrative-architecture-adversarial-review.md) found that current generation context uses curated, source-referenced principles but may omit relevant definitions; representational validation is not proof of coherent architecture. Its hybrid selective-context suggestion is a technical hypothesis, not a requirement here.
- [UI usability divergent exploration](../../research/narrative-architecture-usability-divergent-exploration-2026-11-02.md) catalogs unranked interface possibilities; the author's later clarification prioritizes agent-first creative work over manual graph usability as the primary interface problem.
- [Narrative Architecture creative-reasoning plan](../plans/2026-11-02-narrative-architecture-creative-reasoning.md) identifies an environment-specific real-host-agent execution blocker. That blocker does not demonstrate a product defect or authorize bypassing the actual agent.
- Repository product constraints remain local-first, single-author, backend-neutral, and author-governed. Do not invent a second source of accepted story truth.

## 11. Engineering delegation and next planning step

**Leave to the coding agent:** source discovery, narrowly scoped architecture, context selection, state and provenance representation, session re-entry and handoff, compatibility and migrations, schema/prompt changes (if warranted), UX placement, runtime execution integrations, and appropriate tests. Prefer reuse of existing owners and contracts over parallel infrastructure.

**Require from the future plan:** a baseline assessment of current capabilities versus this brief; the smallest coherent delivery sequence; tests that demonstrate actual agent execution and author comprehension; preservation of accepted-source boundaries; distinct treatment of ontology evolution versus project-level story development; and a candid distinction between implemented behavior, exploratory ideas and unqualified claims.

**Decision requested:** Approve or revise this design brief before an engineering plan is written. Approval authorizes planning, not automatic acceptance of story canon or unreviewed ontology changes.
