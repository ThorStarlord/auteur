# Agent-Interactive Narrative Graph — Exploration Design

**Date:** 2026-11-04
**Status:** SELECTED EXPLORATION DIRECTION / PROPOSED INTERACTION CONTRACT — not approved production integration or release authorization
**Scope:** Isolated comparison of semantic graph interactions for Auteur's Narrative Architecture, then a reasoned go/no-go decision.
**Authority:** This research does not amend narrative ontology, Story Identity, accepted Structure/Realization/Expression, Studio acceptance, or the existing five-layer architecture.

## 1. Product question and motivation

**Question:** What value can authors gain from interacting with Narrative Architecture entities and components as **semantic invitations to coding-agent reasoning**, beyond what Auteur already provides through a readable architecture, source-bound graph, inspectors, Focused Unfolding, and conversational revision?

Current Auteur already has candidate nodes, directed links, semantic facets, emotion/genre contracts, phases, a text-first architecture reader, and a host-agent architecture revision pipeline. The exploration must not relabel those as missing features.

**Product thesis (agreed direction):** The active coding agent remains the primary constructor and reviser of architecture. An author may use graph entities and their inspectable components to direct the agent toward a particular creative problem. Graph gestures are questions or working proposals, not unreviewed changes to accepted story meaning. Manual graph assembly remains optional.

**Priority ideas:** G05 agent-mediated gestures, G06 relationship objects, G07 context-sensitive actions, G09 causal pathway explanation, G14 provenance-aware graph, G20 graph-to-agent creative handoff. G01/G03 composable/nested components inform presentation, not a universal component schema. G10/G11/G13/G15 remain distinct follow-up hypotheses.

## 2. Existing evidence and boundaries

Read the [MISSION](../../../MISSION.md) (local-first, single-author, backend-neutral, no auto-accept), [Narrative Architecture](../../narrative-architecture.md) (semantic authority), [Unified Author Experience](../../product/auteur-unified-author-experience-architecture.md), [Living Story Studio](../../design/2026-10-09-living-story-studio.md), [Architecture UX](../../design/2026-10-11-narrative-architecture-information-ux-plan.md), [Focused Unfolding](2026-10-12-focused-unfolding-authoring-explanation-design.md), [UI Divergent Exploration](../../research/narrative-architecture-usability-divergent-exploration-2026-11-02.md), and [Agent-First Narrative Architecture](2026-11-03-agent-first-ontology-grounded-narrative-architecture-design.md).

Use the [recorded rich candidate](../../qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json) and [its exact request](../../qualification-evidence/agent-first-ontology-20261103/rich-vision-request.json) as reproducible source fixtures. These were same-agent qualification artifacts, **not independently demonstrated literary quality**.

Existing owners: src/auteur/beginner/studio_architecture.py (v2 candidate and prepare/revise), src/auteur/beginner/browser/studio.js, studio_architecture_reader.js, studio_unfolding.js, studio_explanations.js, studio_explanation_views.js, and src/auteur/beginner/studio_store.py.

## 3. Competing approaches

| Approach | Author experience | Main advantage | Main risk | Disposition |
| --- | --- | --- | --- | --- |
| A. Manual component workbench | Wire component sockets and edit structured graph | Fine control | Makes author graph administrator; invents universal schema | Reject as default; keep optional working edits |
| B. Agent-interactive semantic graph | Inspect an entity/relation, choose intent, prepare bounded agent revision | Fits agent-first pipeline | Visual gesture may imply commitment | **Selected exploration** |
| C. Full simulation laboratory | Manipulate alternatives and projected causes | Broad creative search | Unsupported predictions and parallel state complexity | Separate future inquiry |

Compare two variants within B: **B1 Question-First Inspector** (minimal semantic questions and evidence) and **B2 Component-Aware Workbench** (multi-anchor context, more creative actions). Both compare with the real current Studio baseline. Neither wins by being more decorative.

## 4. Proposed interaction grammar

| Action | Meaning | Permitted effect |
| --- | --- | --- |
| Select entity | Inspect existing meaning, components and source | Local view only |
| Select relationship | Inspect existing endpoints, direction and function | Local view only |
| Trace | Traverse only recorded links and contract references | Read-only explanation |
| Connect-to-ask | Ask how two elements *might* relate | Prepared question, **no edge assertion** |
| Challenge | Ask what is unsupported or uncertain | Prepared critical inquiry |
| Compare | Ask for a design alternative | Draft, not fabricated branch |
| Revise | Express a holistic desired change | Prepared instruction for agent |
| Group, arrange, fold | Control attention | Presentation only |
| Adopt | Save noncanonical suggestion via current working owner | **Deferred** from isolated prototype |
| Accept story meaning | Author explicitly accepts via existing owner | **Not offered** in prototype |

Moving nodes closer together, folding or connecting a visual question has no semantic/canonical effect. A written link may be an agent working proposal, not proven reader causality.

## 5. Entities and components

An experimental “entity” means a **source-identifiable element of current ArchitectureCandidate v2**, not a new persistence class. Existing inspectable elements include:
- ArchitectureNode.id: reader experience, genre, trope, engine, thread, structure, theme, aesthetic, other.
- ArchitectureLink.id and actual source/target/function.
- GenreInteraction.id and actual source_genre_id/target_genre_id/kind/mechanism.
- EmotionTarget.id with intended effect, role, eliciting condition, strategy, and provenance.
- GenreContract keyed by genre_node_id, never a manufactured contract ID.
- NarrativePhase.id with order, local activations, function, and reader experience.

A component is a **projection of an existing field or attributed relationship**, such as an engine function, genre promise or emotional eliciting condition. A field such as trope_functions is text owned by a genre/phase until real stable IDs exist; matching the same phrase across genres does not create a shared instance.

Every displayed relation must arise from an existing directed link, genre interaction or explicit contract/phase reference. An absent relation is **not recorded / unknown**, not automatic proof of narrative failure. Do not invent links by semantic similarity or by graph geometry.

## 6. Graph-to-agent handoff

The experiment produces an **editable, copyable draft** of an agent instruction, not an executable request. Each draft includes:
- Exact candidate request SHA and source-addressable selected anchor kind/ID.
- Action: ask_relation, trace, challenge, compare or revise.
- Author's desired change text, preserved verbatim and appropriately bounded.
- Actual recorded relation/component excerpts tied to those anchors.
- authority = noncanonical_intent_draft; status = prepared_not_executed.
- An explicit stale/unavailable warning if source identity no longer matches.

The experimental prototype never sends a model request, writes CanvasStore, alters ontology, or accepts story meaning. Rendering, clicking, tracing, grouping and copying cause no hidden network/model call.

Future production integration, if independently approved, must reuse the existing exact HostAgentRequest prepare/complete/review workflow, server-validate anchor identity atomically with request creation, and preserve honest status; client text alone cannot become trusted source references.

## 7. Comparative author tasks

Using the same Memory Economy candidate/source identities:
1. **Inspect:** Find Memory Economy and explain which of its relations to wonder are actually recorded; distinguish direct evidence from interpretive possibility.
2. **Connect-to-ask:** Select Memory Economy and Wonder, ask how they might relate, and ensure no link is saved.
3. **Holistic direction:** Form “Make wonder dominate fear while preserving mystery and the memory cost”; preserve anchor IDs and stated constraints without claiming semantic preservation was verified.
4. **Critique:** Challenge one proposed causal link; distinguish source link from inference.
5. **Freshness:** Replace the request SHA; old selections/drafts must become invalid or visibly stale.
6. **Accessibility:** Complete inspection, question preparation and return using keyboard-only and a linear relationship alternative; test narrow viewport.
7. **Large and empty:** A dense graph and absent relation show meaningful bounded context or explicit unknown rather than fabricated edges or clipped status.

Use the recorded [sparse candidate](../../qualification-evidence/agent-first-ontology-20261103/sparse-vision-candidate.json) plus a high-density **synthetic and visibly labeled** fixture for stress.

## 8. Evidence and go/no-go gate

Compare **current served Studio** against B1 and B2. Record for each task: correct source/authority interpretation, successful question/intent preparation, actual new creative insight rather than cosmetic differences, navigation detours, unintended state effects, stale/empty handling, and accessible traversal.

Evidence categories must remain separate: source inspection, pure-model tests, real served-browser interaction, simulated agent, actual author comprehension, and independent agent/runtime are not interchangeable.

**To advance to production design**, a variant must have no observed critical authority/source errors and at least one clear, evidenced consequential author-task improvement over the current interface. If the improvement is only cosmetic, unsupported or absent: **stop; preserve the negative result**. This is a selection condition, not a guarantee.

## 9. Explicit non-goals, governance and next boundary

No production Studio JS/CSS/HTML edits, server routes, Pydantic/schema changes, CanvasStore extensions, accepted story mutations, ontology changes, v3 candidate migration, new provider or graph database during this prototype exploration.

The current agent-first narrative workflow remains primary. Existing revision-review truthfulness concerns must be checked before any future production reuse; an unverified “preserved constraints” claim is not acceptable in a new interactive view.

If the evaluation supports an improvement, draft a **separate** production integration design and implementation plan; submit the design for author review before product implementation. If not, report no change recommended. This exploration does not authorize either integration or release.

## 10. Design disposition

Proceed through [Agent-Interactive Narrative Graph Prototype and Evaluation Plan](../plans/2026-11-04-agent-interactive-narrative-graph.md). The conclusion must choose B1, B2, a bounded combination or **no integration**, preserving evidence and uncertainty.
