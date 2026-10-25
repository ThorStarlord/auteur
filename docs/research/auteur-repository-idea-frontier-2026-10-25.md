# Auteur — Repository-Wide Idea Frontier Beyond Studio UI

**Exploration:** 2026-10-25  
**Source identity:** `ThorStarlord/auteur`, `main@a8a090580e98cd5f6dcee1645375e2867e644350`  
**Status:** EXPLORATORY / NOT RANKED / NOT AN APPROVED ROADMAP, VALIDATION PLAN, OR NEW PRODUCT THESIS  
**Relationship to other work:** Companion to the open [Studio UI divergent exploration (PR #485)](https://github.com/ThorStarlord/auteur/pull/485) and [UI strategic evolution/simulation (PR #486)](https://github.com/ThorStarlord/auteur/pull/486). **This document asks about story-making capabilities, not just interface representations.**

## 1. Why look beyond the latest UI repair?

Auteur's distinctive promise is more ambitious than a graph editor or a scene generator: it should help an author **discover which story is worth making, design it, write it, revise it, and complete an increasingly demanding Book**, retaining meaningful control. A studio can look integrated while underlying creative reasoning fails; conversely sophisticated reasoning can be difficult to reach. Both deserve investigation.

The [Product Evolution Roadmap](../product-evolution-roadmap.md) already labels multiple candidates and explicitly says **CANDIDATE != NOW**. The [Capability Frontier](../product/auteur-capability-frontier-construction-roadmap.md) and [Experience Frontier](../product/auteur-experience-frontier-construction-roadmap.md) form a *paired*, non-identical progression. [STATUS](../../STATUS.md) identifies **F2 (small-book continuity) + X3 (persistent Book workspace)** as the selected controlled frontier, not a general proof of human UX or F3–F7 readiness.

This is a **cross-domain possibility map**, not a new task backlog. It does not overturn the already-selected graph-first, agent-first Studio direction. It also does not treat an existing subsystem's code presence as empirical author value.

## 2. Source-grounded possibility families

The differentiator is the **author's job and a genuinely new outcome**, not a list of existing class/module names. Each family identifies the existing owner and a compelling opposing explanation.

| Family and author job | Existing source / current status | Potential distinctive value | Strongest challenge and evidence hinge |
| --- | --- | --- | --- |
| **A — Discover a story from tastes**: “I know which experiences, characters, places and themes I love, but not what story to write.” | [Story Opportunity Discovery](../story-opportunity-discovery.md) is documentation-first, pre-Identity and explicitly noncanonical. | Separate portable *mechanisms* from superficial imitation; synthesize several genuinely different opportunities before choosing a premise. | A good coding agent may already do this conversationally without another persistent feature. Prove that a small source-aware synthesis creates more useful alternatives than ordinary brainstorming. |
| **B — Assess narrative runway**: “Can this atmospheric premise sustain a long fantasy Book or series?” | [Premise Fitness](../premise-fitness.md) defines conditional efficacy, efficiency, renewable/finite runway, and scope fit; **not** a universal quality score. | Surface early over-commitment to an evocative but nonrenewable engine; choose viable scope without suppressing experimentation. | Forecasts can sound like objective quality measurements. Test whether agent reasoning distinguishes setup cost, renewal, and artistic effectiveness under one specified scope. |
| **C — Generate and challenge genuine story directions**: “Show me meaningfully different causal/ethical engines.” | Existing [Story Discovery/Unified Experience](../product/auteur-unified-author-experience-architecture.md), ArchitectureCandidate, and [contextual mentorship](../design/2026-10-13-contextual-narrative-mentorship.md). | A constructive writing partner challenges assumptions and offers options that would change the story's *causal work*. | Novel labels, premises or changes of mood do not prove deep divergence. Compare sources, sustaining mechanisms, consequences and sacrificed values in candidate responses. |
| **D — Reverse-engineer an existing manuscript**: “I already wrote scenes; help me discover what story they imply.” | Explicit **CANDIDATE** in the [Product Evolution Roadmap](../product-evolution-roadmap.md); Expression and derived Story Identity/Structure have distinct owners. | Let writers arrive with prose rather than a premise; reconstruct plausible arcs, unresolved questions, and conflicts **without rewriting the existing manuscript**. | Extraction may hallucinate canon or coerce contradictory prose into one confident plot. Require paragraph-level support, hypotheses, and explicit acceptance of interpretations. |
| **E — Make discoveries consequential, not bureaucratic**: “The draft introduced an important character; what should change?” | [Unified Author Experience: discovery propagation](../product/auteur-unified-author-experience-architecture.md), [Book reconciliation](../book-reconciliation.md) and existing Quick Draft. | Carry a surprising scene discovery forward with the smallest safe Story Identity/Structure/Realization decision rather than repeatedly rewriting all graphs. | Not every detail requires elevation or an Inbox item. Simulate small/large discoveries, stale sources, and a deliberately rejected proposed change. |
| **F — Reason over the entire Book**: “Does my ending honor promises made in the beginning?” | **CANDIDATE** Book-Level Reasoning/Editing in [Product Evolution Roadmap](../product-evolution-roadmap.md); [Book Expression](../book-expression.md) and existing cross-chapter workflows. | Compare Book-level promises, unresolved threads and realized payoffs while leaving the author free to interpret them. | A long summary may obscure temporal evidence. Start with a specific promise and source-linked Chapter span; do not invent a new Book canon. |
| **G — Deep character and relationship evolution**: “How did this friendship become a rivalry over ten chapters?” | [Character and Relationship Architecture](../character-and-relationship-architecture.md) explicitly separates Identity, Structure, Realization, Expression, and derived edges. | Expose the *causal and emotional trajectory* across planned arc, observed scenes, beliefs, and consequences—not merely a static relationship graph. | Plotting all relationships may overwhelm the author or mistake plans for facts. Try one source-linked relationship through several timepoints before building a history UI. |
| **H — F3 relevant memory**: “Which details matter to Chapter 9 of a multi-thread Book?” | [Capability Frontier F3](../product/auteur-capability-frontier-construction-roadmap.md) is **evidence-gated**; existing context composition and attention systems already exist. | Prove that context is relevant and appropriately scoped, not merely that the system can remember everything. | New retrieval architecture is premature without F3 failure. Simulate an 8–12-character multi-thread Book and compare included/excluded support against current bounded composition. |
| **I — F4 beliefs, secrecy and revelation**: “What is true, what each character believes, and what readers know?” | [Capability Frontier F4](../product/auteur-capability-frontier-construction-roadmap.md) explicitly identifies truth/belief/reader/POV distinctions as a future pressure, **not** permission for an epistemic ontology. | Handle mysteries, unreliable testimony, ideological conflicts, and dramatic irony without leaking future revelations into earlier scenes. | May be expressible by current Realization/provenance data. Before new schema, ask for the concrete representation operation that existing owners cannot carry. |
| **J — Change your mind mid-Book**: “Keep my best scenes, but revise the central arc.” | [Unified Author Experience: Change-my-mind](../product/auteur-unified-author-experience-architecture.md), impact, [counterfactuals](../architecture/v0.11.0-counterfactual-narrative-planning-design.md), and [Capability Frontier F5](../product/auteur-capability-frontier-construction-roadmap.md). | Preview minimal necessary changes, preserve unaffected work and continue writing without cascading manual bookkeeping. | Simulated projections can pretend certainty or cause broad invalidations. Compare touched/untouched artifacts and source freshness; never apply a hypothetical change silently. |
| **K — Series-scale memory and promises**: “Book 3 should remember Book 1 without flattening Book 2.” | [Capability Frontier F7](../product/auteur-capability-frontier-construction-roadmap.md); Universe/Series/Book scope contracts in [Narrative Architecture](../narrative-architecture.md). | Maintain cross-book obligations and coherent world evolution while respecting each Book's local dramatic function. | Series capabilities existing in code do not imply the complete author workflow is ready. Defer expensive expansion until smaller frontiers have been exercised. |
| **L — Craft expertise on demand**: “I need help with mystery construction / romance escalation / theme, not more UI controls.” | **CANDIDATE** Story Design Packs in the [Product Evolution Roadmap](../product-evolution-roadmap.md), as reusable knowledge rather than new canon or ontology. | Add small, contextual craft guidance when a repeated author decision reveals a genuine knowledge deficit. | Generic advice may already be sufficient. Admit a Pack only after a specific creative decision repeatedly lacks relevant guidance. |
| **M — Help me decide what matters now**: “What is my current creative problem?” | **CANDIDATE** Current Author Intent and Unified Decision Inbox in the [Product Evolution Roadmap](../product-evolution-roadmap.md). | Prioritize one consequential, source-bound pending choice instead of showing every diagnostic, option and subsystem. | An Inbox can become a new administrative queue or invent the author's intention. Prefer an optional question over persistent task machinery until a real task shows the need. |

### The non-obvious distinction

The later long-form families are **different stresses**, not increasingly elaborate versions of one UI: F3 asks for **relevance**; F4 asks for **epistemic distinctions**; F5 asks for **change propagation**; F7 asks for **scope-sensitive continuity**. A product can pass one and fail another. Treating them as one generic “smarter narrative AI” feature would conceal the real engineering owners.

## 3. Four broader product futures to retain as hypotheses

### Future 1 — Story Discovery Companion

An author arrives with influences, emotional desires or dissatisfaction with existing media. The coding agent identifies portable creative mechanisms, challenges superficial imitations, offers causally different possibilities, and distinguishes the author's preferences from third-party audience evidence. The author decides whether to turn any into a premise.

**Reuses:** A, B, C, L. **Do not build:** automatic popularity scraping, universal idea scoring, a new Layer 0, or forced intake forms.

### Future 2 — Manuscript-First Story Archaeologist

An author already has rough prose and incomplete scenes. Auteur derives *possible* story engines, unresolved relationships, and missing structural obligations while retaining precise textual source references. The author can correct misinterpretations and decide which inferred meaning should become accepted structure.

**Reuses:** D, E, F, G. **Do not build:** automatic canonical import, destructive rewriting, or assertions that invented interpretations were always the author's intention.

### Future 3 — Long-Horizon Narrative Strategist

An author plans a rich Book, tracks distinct character/reader knowledge, returns to unresolved promises, changes direction and keeps what still works. The agent projects alternatives and uncertainties over the current story state rather than forcing one deterministic plan.

**Reuses:** F, G, H, I, J, K. **Do not build:** a generic memory engine or new event-sourcing platform until an existing owner's missing operation is demonstrated.

### Future 4 — Adaptive Craft Collaborator

The agent teaches by analyzing the work, offers bounded alternatives, challenges a meaningful assumption, and grows reusable craft specificity only when the same shortcoming recurs. Its guidance remains interpretable, provisional and optional.

**Reuses:** C, E, L, M and existing mentorship. **Do not build:** a permanent psychographic model, hidden author-intent inference, universal craft metric, or another always-visible chat pane.

These futures can compose. This section is **divergence**, not approval to develop four concurrent platforms.

## 4. Agent-simulated author tasks that discriminate value without human input

The user should **not** be asked to manually supply fictional scenarios for mechanical verification. A coding agent can create bounded, disposable story fixtures, execute the existing owning contracts and report which claims are supported.

| Task | Adversarial scripted case | Decision-changing observation | No-go claim |
| --- | --- | --- | --- |
| **S1: No-premise start** | Fictional author supplies only “a warm, habitable academy, nostalgia, intelligent companionship, heroic protection” and requests 3 directions. | Do alternatives differ in renewable engine, reader promise, burden, genre fit, and author choice? Does the agent label its own inventions as proposals? | Agent sample != a real user's preferences or proof of a market gap. |
| **S2: Existing manuscript archaeology** | Disposable 2-scene prose with unreliable narrator and intentionally inconsistent testimony; the author later corrects one inference. | Does analysis cite the actual passage, preserve ambiguity, accept correction, and avoid writing Identity/Structure unless explicitly chosen? | A synthetic import is not evidence of full-book extraction accuracy. |
| **S3: Scene discovery delta** | An unplanned recurring ally appears in draft prose; the author wants to keep *only* that character and not a speculative new faction. | Does the proposed handoff identify the smallest relevant existing owner and exclude rejected discoveries? Does acceptance stay explicit? | A suggested update is not accepted canon. |
| **S4: Chapter-N context relevance** | A synthetic 10-chapter Book with 12 characters and 3 interleaved threads; ask for Chapter 9 context. | Which cited facts are relevant, omitted, duplicated or prematurely revealed? Can context remain bounded? | This does not select F3/X4 or justify a retrieval subsystem. |
| **S5: Belief and reveal timing** | Truth differs from protagonist belief, antagonist knowledge and reader knowledge. | Can current models trace the distinction and avoid leaking a future reveal? If not, identify the exact unexpressible operation. | One failure is not evidence for an entire epistemic layer. |
| **S6: Mid-Book revision** | Replace one Chapter 8 revelation while preserving two independent relationships and final-scene prose. | Does impact preview distinguish changed/unaffected artifacts and refuse automatic story-state mutation? | A counterfactual is not a prediction of artistic quality. |

**Test economy:** start with deterministic/offline fixtures and only the production APIs changed by the work. L1 tests should cover new/adjacent behavior; run an L2 UI or persistence simulation *only* for the named crossed boundary. The large Python suite, all Node tests, and unrelated F2/F7 tests are not default gates for a tiny Studio UI commit. Human usability and literary quality remain different claims, not requirements for these mechanical probes.

## 5. What to pursue next versus what to preserve

**Current selected lane:** the narrow Realization -> Quick Draft integration gap documented in [draft PR #487](https://github.com/ThorStarlord/auteur/pull/487) and focus integrity in [draft PR #484](https://github.com/ThorStarlord/auteur/pull/484). This remains **F2/X3-compatible** and should use agent-simulated author actions rather than human preference tests.

**Independently useful, cheap next inquiry:** S1 (Story Opportunity / Premise Fitness) and S2 (existing-manuscript archaeology) can be explored as **noncanonical coding-agent samples**, without adding a runtime subsystem. They may establish whether the current documented prompts/contracts are sufficiently usable. A bounded sample cannot establish broad model reliability.

**Deferred until evidence:** F3 relevance system, F4 schema expansion, F5 mass changes, F7 Series workspace, generalized Story Design Packs, and an author decision dashboard. Their candidate status remains unchanged.

**Strategic reasoning:** both 'only fix the UI' and 'build everything documented' are inadequate. The more valuable middle path is to keep the integrated author journey moving while deliberately probing different sources of creative value, with each candidate's failure owning its own bounded response. If two futures are equally expressive using existing components, prefer the simpler composition. If evidence changes the product direction, reconcile through the existing roadmap; this research file cannot do so silently.

## 6. Evidence integrity and maintenance

- **Source inspection:** the named primary contracts, repository roadmap, frontier roadmaps, and current Studio/Quick Draft evidence were read on the recorded SHA; the two UI PRs are separately linked as **open work**, not as merged capabilities.
- **No new execution claim:** S1–S6 are *test designs*, not completed simulated model runs. Agent-generated stories are hypotheses, not human creative-quality results. A successful fixture does not qualify F2/F3/F7, release or a redesigned UI.
- **Version distinction:** older docs describing unavailable/unfinished behavior are not automatically more current than merged source. Exact PR HEAD, current main, and Stage qualification control actual implementation claims.
- **Authority:** all proposed story opportunities, reverse-engineered facts, inferred motives, counterfactuals, and creative recommendations stay working/derived until the existing owning workflow explicitly accepts them.
- **Do not convert this into a queue:** add a new family only when it names a genuinely different author job/irreducible need and has an adversarial discriminator. Avoid repeating the much deeper [UI landscape PR #485](https://github.com/ThorStarlord/auteur/pull/485) in this repository-wide capability map.
