# Generative Long-Form Narrative Architecture — Ontology and Development Direction

**Date:** 2026-11-07  
**Status:** OWNER-ENDORSED PRODUCT PRIORITY + ADVISORY RESEARCH/DESIGN DIRECTION. Not a canonical ontology amendment, completed coverage assessment, selected implementation, empirical qualification, or change to the existing long-horizon campaign's execution gate.  
**Scope:** The ability of an agent to create, reason through, revise, and communicate sophisticated Narrative Architecture for very long stories and multi-book series. Narrative Realization and Expression remain necessary downstream consumers and feedback sources, but are not the principal differentiator under investigation.  
**Canonical authority:** [Narrative Architecture](../narrative-architecture.md), [base ontology](../../data/ontology/base_ontology.yaml), focused semantic contracts and accepted repository decisions. This document does not introduce a sixth layer, a second canonical story graph, or a new authority path.

## 1. Product direction and the actual capability claim

**Owner-endorsed priority:** Auteur's distinctive value should center on ontology-grounded, agent-created Narrative Architecture: the ability to design a compelling narrative system at scales exceeding an individual scene, chapter, or book. Agent-generated prose can already be compelling in general; the product's differentiator must be more than another competent prose-generation interface.

The proposed north-star question is:

> Can the active coding agent construct, understand, critique, creatively transform, and progressively maintain a coherent and generative Narrative Architecture for a very long story or series of books, while preserving the author's intentions and retaining usable creative flexibility?

The desired ability combines at least four separable outcomes:

- **Creative conception:** invent distinctive, renewable narrative engines, consequential conflicts, meaningful character/relationship/institutional transformations, and strong intended reader experiences.
- **Cross-horizon composition:** coordinate local actions, individual Book functions, multi-Book arcs, long-delayed promises, concurrent threads, changing genres and world systems without assuming all must be subordinated to one plot.
- **Reflective control:** notice unproductive repetition, unsupported necessity claims, hidden premise changes, scope mismatch, exhausted engines, contradictory structures, and premature or unproductive planning; revise the lowest necessary level.
- **Durable authoring:** make the design understandable, source-bound, selectively revisable, recoverable across sessions and agents, and safe to hand off to Realization and Expression without silently accepting speculative ideas.

These are target competencies, not demonstrated performance. Valid schema, a large ontology, a lengthy series synopsis, and one compelling chapter are insufficient evidence by themselves.

## 2. Existing repository foundation — reuse before extending

The concepts are distributed across owners, not absent from the repository.

| Source | Relevant existing knowledge | Boundary |
| --- | --- | --- |
| [Base Narrative Ontology](../../data/ontology/base_ontology.yaml) | Character, Arc, Theme, Goal, Conflict, Payoff, Symbol, Relationship, Beat, Setup, Revelation, Reversal and conceptual relationships | Twelve base concepts do not formalize every long-form generative operation |
| [Premise Fitness](../premise-fitness.md) | Narrative runway, engine renewability, expansion capacity, multi-engine compatibility, payoff latency/density, marginal story cost, scope and complexity costs | Strong craft vocabulary; not proof that an agent can design 30+ Books |
| [Structure Engine V1](../structure-engine-v1.md) | Structural forces, main/subordinate threads, carriers, resonance, supporting functions, whole-story engine proposals | Historical/specification scope and current implementation must be checked separately |
| [Series Engine ADR 012](../adr/012-series-engine-v1.md), [SeriesIdentity](../../src/auteur/series/models.py), [Artifacts](../artifacts.md) | Global arc, Book plans, character/relationship/faction/thematic arcs, mysteries, dependencies, chronology, setups and payoffs | A well-formed SeriesIdentity is a plan/continuity contract, not evidence of creative quality |
| [Studio Architecture](../../src/auteur/beginner/studio_architecture.py), [Agent-first design brief](../superpowers/specs/2026-11-03-agent-first-ontology-grounded-narrative-architecture-design.md) | Abstract engines, threads, emotion targets, phases, trope functions, genre interactions, agent-first working generation and holistic revision | Working ArchitectureCandidate is not a canonical 30-Book Series plan |
| [Detailed Narrative Architecture V1](../architecture/detailed-narrative-architecture-v1.md), [ADR 019](../adr/019-derived-global-map-and-story-instance-relation-authority.md) | Accepted history, current-state projection, source-linked relations/pressure groups, rebuildable Global Map, bounded Focus, revision impact | Primarily long-horizon continuity/relevance reasoning, distinct from prospectively *inventing* a whole-series design |
| [Theme/Motif](../theme-and-motif-contract.md), [Character/Relationships](../character-and-relationship-architecture.md), [Emotional Trajectory](../emotional-trajectory-contract.md) | Different kinds of commitments, planned transformation, realization evidence, expressive rendering | Existing semantic owners must not be collapsed |
| [Reasoning Architecture](../reasoning-architecture.md), [November 2026 coverage assessment](2026-11-06-narrative-architecture-ontology-and-reasoning-coverage-assessment.md), [bell-keeper reconciliation](2026-11-07-bell-keeper-reflective-reasoning-replication-run2-evaluation.md) | Grounding, hypotheses, evidence/inference and authorial authority; observed weakness in modal inference and premise preservation | A reporting vocabulary does not guarantee creative metareasoning |

Important known implementation boundaries: Studio's abstract candidate and canonical SeriesIdentity are separate contracts; general Studio Architecture links permit free-text functions; certain genre/engine, thematic-test, phase-cycle and chronology/disclosure relationships are not fully typed. The earlier adversarial review found useful expressiveness and some machine-query limitations, not a mandate to introduce new schema. See [adversarial findings](../reviews/2026-10-21-initial-narrative-architecture-adversarial-review.md).

The [long-horizon campaign state](../campaign/auteur-long-horizon-campaign-state.md) remains in prospective native evidence incubation, without an automatically selected ontology, extraction, generalized scale, or next Guided Review responsibility. This new owner direction asks a **different creative-construction question** from that campaign's earlier history-reconstruction/productization questions. It is an invitation to a distinct scoped coverage inquiry, not retrospective authorization for the deferred campaign changes.

## 3. Five connected ontology-and-reasoning inquiry families

For each family, distinguish **(a) existing vocabulary**, **(b) proposed semantic relationships**, **(c) operations the agent must perform**, **(d) characteristic failure evidence**. The relationships below are research candidates. Their names are not admitted Layer-0 types or production schema fields.

### 3.1 Composition — several engines, one coherent narrative ecology

**Question:** How can an agent combine multiple narrative engines, without requiring them to be either independent mini-plots or subordinate to a single dominant plot?

A long series may contain a political engine (institutions competing for legitimacy), a progression engine (growing capability produces new responsibilities), a relationship engine (loyalty changes strategic options), and a mystery engine (partial knowledge changes choices). The same event may serve several engines. Their effects can reinforce, compete, constrain, amplify, redirect, or temporarily eclipse one another.

**Existing:** Studio engine nodes and links, ensemble/layered preferences, genre contracts/interactions, Series central engines and book functions, Structure Engine thread functions, Premise Fitness multi-engine compatibility.

**Explore:** compositional roles (governing, co-governing, subordinate, local, dormant, transitioning); conceptual distinctions among structural containment, causal dependence, thematic resonance and shared consequences; engine-to-engine interdependence versus simple coexistence; a series' capacity for genuine changes in which engine currently governs.

**Agent operations:** identify each engine's renewable causal loop, what other engines consume/produce, what it contributes to reader experience, which decisions are jointly generated, and which structural constraints prevent arbitrary accumulation. Generate a rival organization (for example layered versus ensemble), expose trade-offs, and select a working proposal without treating author preferences as inferred facts.

**Failure signal:** several individually plausible engine descriptions generate the same conflicts repeatedly; a purported shared engine has no causal interaction; every book follows the identical plot loop; the agent silently invents a single center despite a supported ensemble design.

**Admission boundary:** conceptual relations may be explained in source-grounded text before typed engine links are warranted. Do not confuse the candidate graph's parent_id structural containment with causal priority.

### 3.2 Transformation — change the series without destroying its identity

**Question:** How can long-form fiction transform relationships, institutions, threats, roles, genre emphasis and thematic interpretation without becoming a disconnected successor story?

A five-Book rebellion may transition into the politics of rebuilding the society it overthrew. This should not be classified automatically as narrative drift. It may be a deep transformation of the same causal system: success changed the actors, obligations and pressures.

**Existing:** Arc and Reversal, Book/Series functions, changing character/faction/relationship states, planned thematic progressions, accepted realization transitions and supersession, authorial identity commitments, evolution and revision impacts.

**Explore:** distinction between creative identity and static status quo; transformation as conserved premise plus altered state; changing hierarchy of engines; aftermath-generated conflict; irreversible consequences and conditional futures; transitions from one long-form mode into another.

**Agent operations:** distinguish what must remain recognizable from what may change; generate alternative transformations from accepted or provisional outcomes; trace how a Book's resolution changes future available choices; surface value loss if a redesign destroys a governing emotional or thematic commitment.

**Failure signal:** agent relies on arbitrary new antagonists when an earlier success should create consequential problems; an era transition silently abandons the Series premise; an immutable plan blocks an unexpectedly compelling but authorized development.

**Admission boundary:** author-approved changes belong to existing Identity/Structure/Realization owners. An interpretive "series identity continuity" explanation is not a new canonical truth merely because a model asserts it.

### 3.3 Coordination across horizons — relate now, next, and distant futures

**Question:** How do local wins, Book functions, multi-Book arcs and distant promises remain connected while permitting progressively more detailed planning?

Long horizons are **not** just larger versions of a chapter outline. Some relationships exist between different scales (a scene choice changes an institutional trajectory), and some between different kinds of time (an event occurs early, but its meaning is disclosed much later).

**Existing:** Universe/Series/Book/Chapter/Scene scopes, Series book functions and dependency edges, thematic and character arcs, setups/payoffs, timelines, distinction of accepted history and current state, Global Map/Focus, revision impact, chronology and disclosure descriptions.

**Explore:** multi-horizon functional contributions; latent versus activated pressures; distant payoff obligations; nested/overlapping arcs and era-level transitions (as optional design groupings, not a sixth scope); event chronology versus revelation/disclosure order; optional versus author-committed future beats; and the effect of early revisions on long-delayed designs.

**Agent operations:** design a whole-Series spine, then explain what the next Book must advance without exhausting later promises; expand an arc into Book functions and compress Book proposals back to the governing architecture; inspect distant dependency and payoff risks; preserve unrelated premises in counterfactual revisions.

**Failure signal:** Book 8 resolves a commitment whose continuation requires it to remain open; Book 1 changes a secret's logic and the distant reveal is left impossible; unrelated arcs consume space but create no shared consequences; detailed future Book synopses are treated as canon despite never being accepted.

**Admission boundary:** use existing accepted Series Direction, Book plans, source refs and derived projections first; do not create an independent canonical global story graph.

### 3.4 Generativity and renewal — produce meaningful development, not more episodes

**Question:** Why can the series keep producing consequential conflicts after major victories, setbacks and revelations, rather than merely postponing closure or replacing the cast of opponents?

A renewable engine has a loop in which choices change the narrative state and the consequences generate **qualitatively different** future pressures. This is not an infinite-content guarantee. Engines can also legitimately end, split, combine, or be superseded.

**Existing:** Premise Fitness's runway, renewability, expansion, marginal cost and payoff-density vocabulary; Structure Engine's want/resistance/stakes/change; Studio's renewable mechanism instruction; Series planned escalation/complication/collapse/cooldown.

**Explore:** self-transforming causal loops; renewal versus repetition; generativity from established rules rather than imported novelties; engine exhaustion and graceful closure; nested closure (a Book delivers value while opening a new real problem); renewal through transformation instead of treadmill escalation.

**Agent operations:** derive multiple genuinely different conflict situations from one proposed engine; explain why their differences follow from earlier outcomes; test a resolution, then ask what new options and pressures it causes; distinguish an interesting long series from a short premise artificially inflated.

**Failure signal:** serial conflicts are cosmetic reskins; every threat is bigger only numerically; deferred payoff is the only motivation to continue reading; later arcs require repeated arbitrary exceptions to the story's rules.

**Admission boundary:** these are creative craft judgments until a source-grounded distinction requires new queryable relationships. Do not equate a deterministic cycle count with narrative quality.

### 3.5 Reflective creative regulation — diagnose the thinking process itself

**Question:** How does the coding agent decide whether the current creative reasoning strategy is appropriate, rather than simply generating more of the same?

This family combines narrative diagnosis with metareasoning: sometimes the problem is a poor mechanism; sometimes the agent chose the wrong question, unit of analysis or stage of commitment. A stalled agent may need to explore different possible ends, compare rival causal frames, analyze a specific dependency, challenge an unsupported inference, or return to author intent.

**Existing:** Reasoning Architecture's observation/evidence/hypothesis/recommendation distinctions; Studio's inquiry, holistic revision and candidate authority; the observed bell-keeper premise-drift/necessity weaknesses; Premise Fitness and architecture reviewer criteria.

**Explore:** recognition of repeated ideas, shallow causal variation, premature convergence, unproductive divergence, missing relevant evidence, author-authority drift, and incompatible assumptions. Classify these as possible reasoning-method failures before declaring new ontology deficiencies.

**Agent operations:** periodically ask: (1) What kind of creative question am I answering? (2) Is the current strategy producing meaningfully new possibilities? (3) Which premises are fixed, working or unknown? (4) What would disconfirm this design? (5) Is the smallest necessary repair at the mechanism, scene, Book plan, series thesis, or reasoning method itself? (6) Should I act, explore, compare, challenge, retrieve, or ask the author? Use these only when consequential, not as a mandatory visible checklist on every step.

**Failure signal:** an agent repeatedly paraphrases a weak engine; uses ontology labels without real causal reasoning; mistakes compatibility for necessity; changes a fixed author premise during a counterfactual; responds to a bad scene by redesigning the entire Series when a local repair suffices.

**Admission boundary:** reflective regulation is primarily a **reasoning method** unless a persistent narrative distinction demonstrably cannot be represented. Avoid introducing reasoning-policy machinery as a sixth narrative layer.

## 4. Ontology versus craft knowledge versus reasoning method versus product view

A detailed conceptual foundation is useful only if each kind of knowledge is placed at the right owner.

| Question | Primary home | Example |
| --- | --- | --- |
| What is an Arc, Setup, Theme, or a novel concept with stable cross-story semantics? | Layer-0 Ontology, only after admission | Arc and Setup relationship |
| What did this author choose about their particular series? | Series/Book Identity or Structure, via explicit acceptance | Governing theme and book-specific narrative function |
| What reliably helps writers develop a renewable engine? | Reusable craft/Story Design Pack guidance | Consequence-led conflict renewal |
| How should the agent decide between deeper exploration and convergence? | Agent-facing creative reasoning method | Re-examine repeated ideas before accepting a design |
| What does the author need to inspect and revise? | Studio presentation and contextual interactions | Selected engine plus Book-horizon implications |
| What actually happened, and what follows for current continuity? | Accepted Realization and derived Global Map/Focus | A Book 4 reversal constrains Book 12 |
| What makes scenes and prose satisfy the chosen design? | Realization/Expression plus qualitative review | Character choice enacts an institution's contradiction |

Ontology admission requires a recurring, consequential distinction that current definitions/free-text/accepted owners cannot preserve sufficiently for the selected workflow. A named idea alone is not evidence. Likewise, a full ontology dump in the agent prompt is not evidence of correct use.

## 5. Up-front detailed planning versus adaptive development

These are distinct strategies, and the difference changes user experience, obligations, evaluation and potentially data-management demands. Neither is inherently superior.

### 5.1 Front-loaded extensive series plan

An agent develops many Book functions, character destinations, institution/relationship trajectories, mysteries, setups, reveals and possibly concrete plot designs before drafting Book 1.

**Benefits:** strong long-range orchestration, deliberate foreshadowing, interlocking mysteries, synchronized climaxes, and fewer decisions deferred until drafting.

**Costs:** high speculative-detail cost; future apparent obligations may crowd out better discoveries; substantial revision impact when Book 1 changes; possible false precision about story outcomes not yet realized.

**Appropriate when:** author specifically requests a tightly predetermined epic, mystery, intricate chronology, planned climax, or a production environment that needs detailed advance coordination.

**Important:** detailed planning is **not automatically accepted authority**. A 30-Book working blueprint can be elaborate yet fully provisional until its parts are ratified.

### 5.2 Progressive and adaptive series plan

An agent establishes an initially sufficient whole-series thesis, mechanisms, long-range promises and broad arc functions; elaborates nearer Books more fully; later Books are further specified as earlier work reveals new opportunities or constraints.

**Benefits:** preserved exploration, fewer unnecessary future claims, stronger ability to exploit surprising characters/events, lower cost of rewriting uncommitted specifics, organic transformation.

**Costs:** risk of loose foreshadowing, early decisions closing future options, accidental thematic drift, late discovery that a distant payoff is unworkable, or losing a promised end-state.

**Appropriate when:** the author wants ongoing serialized exploration, a flexible time horizon, or development through prose discoveries and changing series-scale themes.

**Important:** progressive planning does **not** mean merely improvising one Book at a time. It still requires a long-term creative architecture and obligations.

### 5.3 Recommended default: deep architectural foresight, progressively committed detail

**Proposal, not a ratified user choice between the two modes.** Generate a complete first *abstract whole-Series architecture* before extensive downstream drafting; do not require detailed plans for every remote Book. Allow the author to request much greater early detail without forcing it into canon.

The key distinction is **detail density versus commitment authority**:

- A far-future finale may be a sparse but firm author commitment.
- A near-term chapter outline may be extremely detailed but still working.
- A Book 12 mystery can have a committed thematic payoff but provisional mechanisms.
- An accepted Book 1 event is fixed history even if its future meaning remains open.
- A hypothetical alternate Book 20 climax is not canon because the agent elaborated it vividly.

Suggested **planning horizons** (illustrative, not fixed default numbers):

| Horizon | Prioritize | Avoid |
| --- | --- | --- |
| Whole Series | Distinctive identity, reader promise, governing/ensemble mechanisms, long thematic questions, consequential constraints, high-level transitions and desired long payoffs | Exhaustively plotting every local scene |
| Macro arc / cycle of Books | What changes in the main engines, institutional/faction states, relationships and reader expectations; how one arc enables another | Treating every illustrative future Book as accepted |
| Near Books | Book function, central pressure, meaningful choices, setups/payoffs, interactions among threads, projected transitions | Endless abstract strategy without developing usable local material |
| Current Book / Chapter | Dramatic structure, character/relationship trajectories, context-specific constraints and revision consequences | Breaking the Series thesis without explicit review |
| Realization / Expression | Specific events, state changes, language and discoveries that test the design | Silently rewriting the plan or denying creative discovery |

This is **progressive elaboration, not scope substitution**. Macro arcs or cycles are optional organizational projections within existing Series/Structure responsibilities, not additional canonical scopes. A 30-Book series may need a clear whole-Series engine and 3–5 meaningful long trajectories without 30 fully plotted synopses upfront.

### 5.4 Explicitly compare both modes during design

The agent should explain the cost of the chosen planning posture in terms of:

1. **Foreshadowing debt:** which early commitments must already exist to make distant revelations satisfying?
2. **Revision blast radius:** how much provisional future material must be reconsidered if a major earlier event changes?
3. **Creative option value:** which questions benefit from remaining unresolved?
4. **Narrative runway:** can the established engine sustain the declared horizon?
5. **Author's desired control:** which outcomes must be chosen now, which should the agent propose, and which remain open?
6. **Production requirements:** must multiple Books, media installments, or collaborators be coordinated before prose? (No change to Auteur's single-author/local-first product scope is implied.)

A user may choose strict upfront planning, adaptive discovery, or the hybrid, for the whole series or different arcs. The app should **not** infer that preference simply from a requested book count or the word "epic."

## 6. Illustrative 30-Book reasoning example (not a story specification)

Assume a fantasy Series whose early Books are about a community overturning an unjust magical institution.

- **Series-scale identity:** Restoring shared life without reproducing coercive institutions; beauty/belonging and high-stakes transformation coexist.
- **Governing mechanisms:** Public responsibility and legitimacy; dangerous collective power; relationships of trust under changing institutional roles. These are proposals, not automatic author commitments.
- **Early Books:** Discover what the institution protects and harms; force a choice with real cost; make victory change the political and emotional landscape.
- **Middle macro arcs:** Rebuilding creates conflicting kinds of solidarity and new distributions of power; progress generates unintended responsibilities; the original engine *transforms* rather than merely repeating the old antagonist.
- **Later macro arcs:** Distant commitments test whether the new society still honors the Series' central question; some promised consequences are planned early, while specific implementations remain provisional.
- **Current-Book planning:** Elaborate the chosen near Book in detail while retaining source references to the whole-Series pressures and authorship status.
- **Reflective challenge:** If the proposed Book 17 conflict is just "a stronger corrupt leader," challenge the *renewability strategy*. Derive different pressure from prior institutional success instead of mechanically increasing antagonist power.
- **Revision:** If an accepted Book 2 revelation changes the system's origin, report its consequences for the Book 9 and Book 24 plans, preserve unaffected commitments, and offer alternative futures for author choice.

This example is intended to expose the difference between a **series architecture** and a **30-item plot list**.

## 7. Strategic construction order — user-endorsed priority, conditional tasks

**Priority 1 — Conceptual foundation and coverage.** Determine whether the existing distributed ontology, Premise Fitness, Structure/Series contracts, Studio schema, theme/character/emotion contracts and long-horizon research can support the five families. Perform source-grounded semantic and reasoning coverage assessment before schema expansion. Identify concepts, relations, operations and owner/authority, plus what remains untested.

**Priority 2 — Agent creative reasoning.** Investigate how the coding agent generates, develops, challenges, compares, synthesizes, revises and coordinates long-form mechanisms and rival plans. Reuse existing ontology definitions and source-linked guidance. Improve methods only when a real failure or reversible creative-building trial supports doing so. Do not turn creativity into a mandatory fixed reasoning pipeline.

**Priority 3 — Studio as inspectable, revisable Series Architecture.** Preserve the selected coding-agent-first interface and complete initial proposal, natural-language holistic revision, graph-grounded context interaction and source-bound continuity. Prefer horizon-sensitive focus and human-readable explanation to a single giant graph. Prove any handoff or presentation gap before inventing new canonical graph stores or arbitrary node-scale infrastructure.

**Priority 4 — Realization and Expression as tests and development partners.** Exercise selected architecture mechanisms in concrete scenes, Books and prose. Use resulting weaknesses and creative discoveries to propose changes to the *lowest correct owning level* without silently modifying accepted Series/Book authority. These stages are necessary to assess efficacy, not the primary product differentiation.

These are **strategic priorities**, not a claim that each earlier priority must be 100% complete before later work, and not an automatic implementation queue. The existing F2/X3 operational frontier and the long-horizon campaign's gated responsibilities are not silently closed or replaced by this document.

## 8. Proposed investigation and empirical ladder

### Phase A — Coverage assessment, no production mutation

Produce a crosswalk for each of the five families:

- Existing canonical definitions, advisory craft descriptions, accepted state models, candidate schemas, actual agent-request context and observed capabilities.
- Required semantic distinctions and reasoning operations.
- Clear classification: already sufficient; expressible but not operationally guided; untested; observed representational gap; observed method failure; context-delivery issue; UI issue.
- Strongest next responsibility and any unresolved product/owner decision.

A gap in **formal typing** is not automatically a gap in **creative reasoning**, and the reverse is also true.

### Phase B — Divergent ontology/operation exploration, conditional on meaningful coverage gaps

Explore candidate concept families, including alternatives that reorganize existing concepts instead of adding new ones. Include adversarial and radically different narrative forms: ensemble versus central-engine; cyclical/contemplative versus escalating; open-ended serial versus tightly concluded; political/institutional versus intimate; many-focal versus one-protagonist series.

Classify every candidate by likely owner (ontology, craft method, Structure/Series, UI, derived reasoning) and the example that demonstrates its necessity. Do not add candidates merely to reach a numerical count.

### Phase C — Convergent synthesis and depth

Select the most promising *mechanisms*, not the most impressive vocabulary. Analyze one or two in depth: how they change a real creative decision, what they require, their failure modes, and why existing distinctions cannot perform the same function. Favor reusable context/craft reasoning improvements when a new ontology entity has no demonstrated operational value.

### Phase D — Authentic long-form creative construction

Using an unfamiliar and demanding original Story Vision, ask a genuinely executing agent to design a coherent 8–12 Book architecture with several interacting engines, multiple transformation trajectories, distant payoffs, distinct Book functions, at least one non-character causal system, and a meaningful revisable author intention. The goal is compelling **architecture**, not 12 arbitrary synopses or prose generation.

Inspect whether the agent can:

- produce meaningful causal variation rather than decorative variety;
- explain why each Book materially changes the Series;
- preserve the central creative identity while allowing transformation;
- sustain distant expectations with intermediate satisfactions;
- offer multiple genuine alternatives with coherent trade-offs;
- revise an earlier assumption and correctly trace consequences into later Books;
- distinguish accepted, provisional and unsupported claims;
- recover the architecture after a fresh context without changing core meanings.

Judgments of originality, emotional power and narrative quality remain qualitative/editorial. Mechanical validation checks structural/provenance behavior; it cannot establish literary success. Keep blind-worker/reviewer contamination and test-source provenance visible.

### Phase E — Scale progressively only when it changes the decision

If the first long-form design is strong, explore 20–30 Book planning with abstract macro arcs and selectively detailed Books. Do **not** manufacture 100 full Book outlines or assume a single gigantic graph is required. A 50/100+ Book case is warranted when the tested capability makes context budget, evolving commitments, or multi-horizon navigation genuinely decision-critical.

Use Realization/Expression selectively to test whether proposed mechanisms produce dramatically viable scenes and prose, not as an automatic prerequisite to every abstract design inquiry.

## 9. Design evaluation: meaningful questions, not a single score

For a proposed whole-Series architecture, assess these independently:

| Evaluation dimension | Consequential question |
| --- | --- |
| Distinctiveness | What could this Series generate that a generic same-genre outline would not? |
| Renewable causality | Do decisions create changing states and new meaningful pressures rather than reskinned repetitions? |
| Multi-engine coherence | Do arcs interact causally and thematically without unjustified subordination or fragmentation? |
| Horizon coordination | How does the planned Book contribute to larger promises without premature or arbitrary resolution? |
| Creative transformation | Can the architecture change political, interpersonal and thematic modes while retaining the intended identity? |
| Authorial fidelity | Which commitments were given, accepted, proposed, counterfactual or unknown? |
| Reasoning warrant | What is entailed, conditional, merely compatible, imagined, or contradicted? |
| Reflective adaptability | Does the agent notice an inadequate design or strategy and revise the lowest necessary level? |
| Durability and legibility | Can another session/agent reconstruct and explain the creative reasons behind the design? |
| Realization potential | Can at least selected mechanisms generate consequential scenes and intended reader experiences? |

A validated diagram or well-formed Series file cannot alone answer these questions. Do not assign a universal weighted creativity score.

## 10. Decision status and next warranted responsibility

**Recorded user direction:** prioritize Narrative Architecture as Auteur's distinct value; advance the five generative families and associated creative reasoning; then improve Studio inspection/revision; use Realization and Prose for creative stress and feedback.

**Recommendation, not recorded owner selection:** default to *deep architectural foresight + progressively committed detail*, while preserving a user-selectable extensive upfront planning mode. The distinction matters even when both generate a whole-Series proposal: they differ in early commitments, planning specificity, cost of future revision, payoff design and capacity for discovery.

**Next candidate responsibility:** a bounded source-grounded **Generative Long-Form Narrative Architecture Ontology and Creative Reasoning Coverage Assessment** against current repository contracts. Its purpose is to determine what concepts, links, reasoning operations, and context delivery are already sufficient, what is merely untested, and which *specific* improvement would make a meaningful difference to an agent's Series design.

**Not authorized by this document:** modifications to base_ontology.yaml, canonical Series/Identity/Structure schemas, agent prompts, Studio UI, Global Map/Focus, provider integration, automatic story canon, performance scale work, or new long-horizon campaign responsibilities.

**Open owner choice:** extensive up-front detail, adaptive progressive planning, or the proposed hybrid as the default for the author-facing Series workflow. Until explicitly decided, avoid treating the hybrid as an accepted author preference.

The governing distinctions are:

1. A larger ontology is not creative intelligence; the capability is using warranted narrative relationships to invent, compare and transform meaningful possibilities.
2. A long series is not many outlines and not perpetual postponement; it is a changing system of renewable causes, earned consequences and coordinated promises.
3. Deep long-range intention is compatible with adaptive discovery; **architectural foresight is not the same as irreversible detail**.

## Research follow-up — coverage assessment (2026-11-07)

The [Generative Long-Form Narrative Architecture coverage assessment](2026-11-07-generative-long-form-narrative-architecture-coverage-assessment.md) examines existing concepts, representations, agent-facing delivery, authentic bounded evidence, and the smallest warranted next responsibility at `main@2dbd1d2077b2d03b16ee6570db10d5c37d223aaf`. Its findings are advisory; this pointer does not change the owner-endorsed priority, accept the proposed planning-mode default, amend the ontology, or authorize implementation.

## Research follow-up — Wandering Islands scope and learning reconciliation (2026-11-10)

The [Wandering Islands cross-stage retrospective](2026-11-10-wandering-islands-creative-scope-drift-reconciliation.md) reviews the **draft, noncanonical** twelve-Book research sequence in PRs #528–#540. It documents an observed transition from architecture construction and counterfactual renewal toward one Book 11 contact sequence, extended prose, model-reader feedback, and a sentence-level correction. It distinguishes that **research scope drift** from the unproven hypotheses of premature convergence, provisional commitment accumulation, and session-level task-selection failure.

The findings reinforce the existing Priority 4 boundary: Realization and Expression can test architectural mechanisms, but locally successful prose iteration does not qualify long-form Architecture and does not automatically warrant the next prose task. Before continuing this research line, compare a proposed local task's **decision value for the original Series Architecture capability** with returning to architectural alternatives and the lowest correct owning layer. This is advisory continuation guidance, **not** a mandatory workflow, changed product thesis, ontology/schema decision, authorization for further experiments, or acceptance of the fictional proposal.
