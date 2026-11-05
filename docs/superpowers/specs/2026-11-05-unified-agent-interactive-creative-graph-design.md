# Unified Agent-Interactive Creative Graph — Design Specification

**Date:** 2026-11-05
**Status:** Selected design, proposed implementation; not implemented or release-qualified.
**Surface:** Auteur Living Story Studio — Narrative Architecture.

## 1. Product intention and decision

Auteur's graph should be an interface for **thinking creatively with the coding agent through narrative meaning**, not a graph-editing obligation. The agent remains the main author of complete Narrative Architecture proposals and holistic revisions, while the author directs the creative intent.

**Selected design:** Entities, meaningful components, and recorded relationships are equally **first-class semantic selection targets**, though their visual affordances differ. Context-sensitive actions expose appropriate choices: Inspect, Trace, Explain, Challenge, Explore, Compare, Connect-to-Ask, and Revise.

**Explicit operation rule:** Explain/Challenge/Explore/Compare/Connect-to-Ask are read-only inquiries that do **not** create or apply a new ArchitectureCandidate. Only an explicit Revise/Rebalance/Restructure action prepares a complete holistic architecture revision through the existing host-agent workflow and the existing explicit apply-to-working-architecture step. An inquiry cannot silently escalate to Revise.

The desired author journey: Read complete proposal → select entity/field/relationship → express intention → source-verified agent request or deterministic inspection → receive grounded explanation/alternatives or holistic proposal → return to original graph focus → review all changes with existing hybrid Before/After → continue or explicitly apply the whole *working* revision.

## 2. Existing implementation to preserve

- src/auteur/beginner/studio_architecture.py implements ArchitectureCandidate v2, prepare_architecture(store, instruction), complete_architecture, project_architecture, apply_architecture_review. Currently prepared revisions contain plain instruction text; **no server-validated selected anchors yet**.
- src/auteur/beginner/browser/studio.js and studio.html contain the graph, node selection, SVG directed links, genre interactions, reader, facets, inspector, Focused Unfolding, timeline, and architecting controls.
- src/auteur/host_agent.py provides backend-neutral, authenticated-to-request HostAgentRequest and HostAgentResponse contracts.
- docs/prototypes/agent-interactive-graph/ contains B1/B2 source-bound inspector and editable intent draft experiments, **not executable host-agent requests**.
- PR #514 added optional read-only hybrid review via studio_architecture_revision_compare.mjs, studio_architecture_revision_view.mjs and studio_architecture_revision_bridge.js.
- Existing project rules in MISSION.md are binding: local-first, single-author, backend-neutral, no auto-accept, deterministic validation, no accepted-story mutation through working architecture.

Do not replace the current working-architecture storage owner, schema, host-agent backend, text reader, graph, prior prototyping evidence, or the hybrid comparison.

## 3. Alternative interaction architectures

| Alternative | Advantage | Risk | Decision |
| --- | --- | --- | --- |
| Entity-only actions | Simplest menu | Relationships become second-class; creative causal questions get obscured | Reject as default |
| Universal draggable component/edge editor | Maximum manual precision | Forces author to administer graph, introduces extra persistence/ontology complexity | Reject as default |
| **Typed semantic selection + progressive disclosure** | First-class entities, fields and relations without manual graph management | Requires exact source verification and coordinated agent feedback | **Selected** |

**UI:** Compact action menu attached to selection; persistent creative-agent panel for longer dialogue and prompts. Components expand inside entity inspectors. Graph remains optional to understand: equivalent keyboard and linear source index must exist.

## 4. Exact kinds of first-class selection

All selection resolves against one current ArchitectureCandidate v2 and its request SHA. Client labels and presented source references are hints, **never server authority**.

### 4.1 Entities

Address source-owned records by (kind, stable ID):
- node → ArchitectureNode.id
- emotion_target → EmotionTarget.id
- complex_emotion → ComplexEmotion.id
- genre_contract → GenreContract.genre_node_id
- phase → NarrativePhase.id

Do not create a relationship *node*: ArchitectureCandidate v2 forbids character and relationship node categories even though the legacy node type enumerates them. A relationship is selected through its actual link/interaction/reference.

### 4.2 Explicit edges

- link → ArchitectureLink.id, actual source, target, directed function.
- genre_interaction → GenreInteraction.id, actual source_genre_id, target_genre_id, kind, mechanism, risk.

A link is not synonymous with every typed narrative reference.

### 4.3 Source-backed references

Recorded references inside existing fields may be selected through a **qualified snapshot-local address**: owner kind + owner stable ID + field name + referenced kind/target stable ID + candidate request SHA.

Supported initial fields: genre_contract.emotion_target_ids, genre_contract.complex_emotion_ids, phase.genre_activations, phase.parallel_with, and node.parent_id. Server derives their exact source locations from the current candidate, not from a supplied index. Duplicate indistinguishable references are **ambiguous** and cannot be addressably revised until explicitly disambiguated by source; do not invent persistent edge IDs.

A reference to an EmotionTarget is **not** a stored ArchitectureLink. A missing relationship between Memory Economy and Wonder is **No recorded relation**, never automatically an edge.

### 4.4 Components

A component is a **top-level field of a source record** selected by (kind, ID, field) against that record's actual schema. Fields such as intended_effect, eliciting_condition, narrative_engine, structural_pattern, trope_functions, genre_activations, narrative_function, summary and transition are addressable. Nested list values remain inspectable text; do not invent stable IDs for list items.

Selections have one primary target and up to **three anchors total**, matching the bounded B2 direction. Duplicate or stale selections fail closed. SourceRef is shown for human verification and recomputed server-side.

## 5. Context-sensitive action grammar

| Operation | Availability | Result | May mutate working architecture? |
| --- | --- | --- | --- |
| Inspect | Any selected target | Exact recorded meaning/field and provenance | No |
| Trace | Entities or explicit relationships/references | Recorded one-hop directed links and reference chain, bounded | No |
| Explain | Any valid target | Read-only agent inquiry of narrative function | No |
| Challenge | Node, component or relation | Read-only critique, weaknesses, unsupported assumptions | No |
| Explore | One to three targets | Read-only set of distinct alternative hypotheses | No |
| Compare | Multiple selected meanings/possibilities | Read-only interpretation contrast | No |
| Connect-to-Ask | Exactly two source-verified anchors | Explore potential relation; no edge is written | No |
| Revise | One to three anchors plus explicit author instruction | Full proposed ArchitectureCandidate v2 | Only the existing explicit whole-working-revision Apply |
| Rebalance/Restructure | Contextual Revise actions for emotional/genre/structural targets | Same as Revise | Same |

Show at most three or four relevant actions initially, with an expansion for others. Action availability is schema/category-based, **not** hard-coded to specific named story fixtures.

**Example:** Memory Economy node + Wonder emotion target have no recorded direct edge. Connect-to-Ask with the author's text "How could the Memory Economy create more wonder while retaining mystery and intimate loss?" produces agent hypotheses, not an ArchitectureLink. A later explicit Revise may request a valid holistic rewrite.

## 6. Host-agent contract and server trust

Create a versioned GraphIntent payload containing operation, expected current candidate_request_sha256, 1–3 typed anchors, exact author_text (server bound at existing 4,000 character revision ceiling), and a snapshot-scoped focus receipt. A field and a qualified reference are address choices, not trusted JSON evidence.

**Under the existing CanvasStore filesystem lock**, the server must:
1. Confirm canvas identity, latest working candidate and request SHA, source and design-guidance freshness.
2. Validate every kind/ID/field/reference against actual ArchitectureCandidate v2 structures; require a qualified reference to be recorded and uniquely addressable.
3. Resolve exact current sourceRef locations, directed links/recorded references and bounded support excerpts.
4. Reject missing, duplicated, stale, malformed, oversized or ambiguous selections; never match by title, semantic similarity or visual proximity.
5. Preserve user author_text verbatim inside the request content; distinguish recorded support from hypotheses.

**Revision:** Add optional validated graph_intent to prepare_architecture and the existing architecture/prepare POST route, while preserving every existing caller that supplies only instruction. No second revision pipeline; existing prepare/complete/review/apply, source SHA, design guidance SHA and working-vs-accepted authority remain the owners.

**Inquiry:** Reuse host_agent.py request/response validation with distinct role studio_architecture_inquiry. A successful inquiry response is a validated **read-only inquiry result**, not an ArchitectureCandidate. Its fields include analysis (explicitly agent interpretation), bounded recorded_observations with source-addressable anchors, alternative hypotheses, and uncertainties. Model-generated claims are not automatically proven by referencing a source record. Keep immutable inquiry packets/receipts under the current canvas architecture subtree; do not create another persistence owner, autonomous agent provider, canonical fact, or graph edge.

UI must distinguish draft, prepared_not_executed, awaiting_host_agent, response_received, ready_for_review, stale/guidance_changed, superseded and error where applicable. Stale inquiry results may remain **historical evidence**, never current advice. A request prepared is **not** a model call completed.

## 7. Author-facing interaction and continuity

1. Reader shows the complete architecture. The graph is optional for general comprehension.
2. Selecting a node, edge, named component field or qualified recorded reference opens the compact contextual actions and updates the persistent creative-agent panel.
3. The panel shows anchor chips with type/ID, direction and source status; an editable author intention; relevant recorded support; no made-up relationship.
4. Inspect and Trace operate deterministically. Inquiry operations prepare a typed host-agent packet and show explicit processing status; a later completed inquiry is shown with grounded observations, creative hypotheses and uncertainty labels.
5. Hypotheses stay noncanonical and cannot masquerade as candidate edges. The author can copy/refine one into a new question or explicitly start Revise.
6. Revise attaches validated graph context to the existing holistic request. An actual returned candidate is reviewed, not auto-applied.
7. On inquiry response, restore selected source context in graph/panel. On revision review_ready, the hybrid comparison opens with original typed focus where resolvable but still shows the **full** working candidate diff; an absent selected element is marked Removed in proposal, never rebound by matching title.
8. An author explicitly applies or rejects the *whole working revision*. Accepted Story Identity, Structure, Realization, Expression and ontology remain independent.

No permanent new branching/version graph is required. Persist only what is necessary to recover exact prepared host-agent requests and their source receipts using existing architecture storage ownership. Ephemeral UI selection can be lost on page close without losing canonical story state.

## 8. Layout, component UX, accessibility and performance

- Graph edge selection: give actual recorded directed SVG paths a generous **transparent hit target** without stealing pan/zoom. Expose exact same actions through keyboard-operable linear relationship index and inspector; no SVG-only discovery.
- Component selection: select meaningful field rows inside inspector, not new draggable component nodes. Display compact source-backed values and expand for long text.
- Side panel: remains visible during graph navigation, provides selected anchors, source authority, tailored actions, exact editable author text, status and agent results. Clear focus without deleting recorded agent responses.
- Source labels: recorded link, recorded reference, hypothetical relation and absent relation are visibly different. Do not imply narrative causality from topological adjacency.
- Mobile: 390px stacked graph/panel; accessible keyboard, screen-reader, reduced-motion, focus preservation, no color-only status.
- Dense case: 80-node/180-link bound, bounded one-hop context, filtering and textual navigation. Unsupported or duplicate references expose uncertainty instead of invented identities.

## 9. Creative feedback through the existing hybrid review

Use exact interaction receipt for the initial request: canvas ID, baseline candidate request SHA, operation, validated selected anchors and author text. An inquiry result links back to the receipt. For revision, project this validated request focus inside review_ready and offer an opt-in focused entry into existing hybrid comparison; allow a one-click return to whole-architecture summary.

**Three different evidentiary classes remain distinct:**
- Direct recorded field/edge diff (provable from two candidates).
- Other changed records explicitly connected to selected anchors (recorded references).
- Agent interpretation of downstream narrative consequences (hypothetical reasoning, not mechanically proven).

A changed or redirected edge shows old and new endpoints and source refs. An unchanged graph shape can still have meaningful changed field values. No per-element acceptance, no automatic apply and no statement that an unchanged field proves compliance with author constraints.

## 10. Scope, evidence gates, and exit conditions

**Not in scope:** new graph engine/graph DB, new persistent universal component IDs, ontology v3, direct drag-to-create canonical links, always-on model execution, automatic causal simulation, full architecture version tree, new provider, replacing Studio, accepted story mutations, release claims based solely on test passes.

**Minimum meaningful evidence:** source/authority negative tests; actual served Chromium desktop and 390px plus keyboard/edge interaction; current Studio vs enriched graph author tasks on the same recorded candidate; inquiry and revision responses from correctly identified backends; comparison preserves all changes, not just selected focus.

**Release/default gate:** No automatic default promotion without an author-facing comparison or explicitly documented owner sufficiency decision. An opt-in integration may be constructed as an experiment if it preserves authority and backward compatibility. If no credible author benefit is observed, retain a smaller inspector or stop integration and record the negative result.

**Selected development sequence:** deterministic target resolution → contextual actions and spatial selection → source-verified read-only agent inquiry → graph-grounded holistic revision → unified feedback and hybrid review → user-task evaluation and bounded product decision.

**Companion implementation plan:** [Unified Agent-Interactive Creative Graph](../plans/2026-11-05-unified-agent-interactive-creative-graph.md).
