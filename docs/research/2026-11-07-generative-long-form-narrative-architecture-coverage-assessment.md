# Generative Long-Form Narrative Architecture — Ontology and Creative Reasoning Coverage Assessment

**Assessment date:** 2026-11-07  
**Repository / authoritative baseline:** ThorStarlord/auteur, main at 2dbd1d2077b2d03b16ee6570db10d5c37d223aaf (PR #525 merge)  
**Status:** Source-grounded documentation assessment; advisory findings, not an ontology amendment, architecture decision, implementation authorization, or creative qualification  
**Authority and scope:** Read-only assessment of authoritative documentation, code and prior evidence. No story canon, schema, prompt, Studio UI, runtime or long-horizon Campaign state changed.  
**Strategic source:** [Generative Long-Form Narrative Architecture strategy](2026-11-07-generative-long-form-narrative-architecture-strategy.md), owner-endorsed priority but advisory design hypotheses.

## 1. Executive assessment and principal answer

**Answer:** Auteur has a substantial, distributed conceptual foundation for long-form Narrative Architecture. The twelve-concept base ontology, Premise Fitness, Structure Engine, SeriesIdentity, dependency semantics, Studio working Architecture, authority contracts, and long-horizon research already support most of the *vocabulary and explanatory distinctions* needed by the five families. They have not established that an actual coding agent can consistently create, sustain, evaluate and transform a compelling 8–12 Book system.

The highest-confidence limitation is therefore **creative reasoning competence and point-of-use guidance/evidence**, not a demonstrated inability of the ontology to represent long-form design. Concrete machine-query limitations exist, especially general Studio engine/link functions, chronology versus disclosure, engine-to-genre ownership, and per-plan commitment status. They are **not** proof that a new Layer-0 entity is necessary. Existing free-text explanations, working candidates, Series arcs and accepted-plan owners can express more than the current validators can verify.

**Overall disposition:** preserve the five-layer model and existing contracts; do not expand Layer 0 or revise schemas on this assessment alone. Select **C — one authentic 8–12 Book creative-construction exercise** as the single next responsibility, with an unfamiliar Story Vision and a qualitative, source-aware review. Its outcome should discriminate a reasoning/craft/context problem from an actual representational obstruction before intervention.

**Five-family provisional synthesis:**

| Family | Best supported today | Principal limit / evidence ceiling |
| --- | --- | --- |
| A. Composition | Abstract engines, free-text causal links, ensemble preference, typed genre interactions; Series Book threads | Causal co-governance and engine-role transitions are not uniformly typed; long-series agent composition untested |
| B. Transformation | Arc/Reversal, Series character/relationship/faction/thematic trajectories, historical supersession and revision impact | Identity-conserving change can be explained; generative transformation by an agent across many Books untested |
| C. Coordination across horizons | Book plans/functions, setups/payoffs, directed dependencies, continuity diagnostics, accepted history and derived impact | Proposed versus accepted future commitments are not per-field typed in SeriesIdentity; complete revision-to-future reasoning untested |
| D. Generativity and renewal | Detailed Premise Fitness runway/renewability/cost vocabulary and Structure forces | Mostly craft guidance rather than an agent-facing long-series generative method; no observed 8–12 Book quality qualification |
| E. Reflective creative regulation | Reasoning provenance, Studio explain/challenge/explore/compare, concrete bell-keeper correction evidence | Prompted correction is mixed, misses premise drift and introduces errors; spontaneous method selection and reliable local repair unproven |

The word **SUPPORTED** below applies to the stated layer (definition, representation or demonstrated mechanical behavior), never silently to creative excellence.

## 2. Method, source inventory and evidence hierarchy

Baseline was checked against the repository's main branch at the SHA above; the [strategy](2026-11-07-generative-long-form-narrative-architecture-strategy.md) is present, while this assessment did not exist on main at inspection. PR #525 is merged. Historical proposals remain historical even where implementation has since advanced.

**Authoritative conceptual sources inspected:**

- [Canonical Narrative Architecture, lines 8–75](../narrative-architecture.md#L8-L75): Layer 0–4 owners, Universe/Series/Book/Chapter/Scene scopes, pre-Identity search and accepted versus derived status.
- [Base ontology](../../data/ontology/base_ontology.yaml), [Layer-0 guide](../superpowers/layer0-ontology.md): Character, Arc, Theme, Goal, Conflict, Payoff, Symbol, Relationship, Beat, Setup, Revelation, Reversal, concept relations and genre extension mechanism.
- [Emotional trajectory](../emotional-trajectory-contract.md), [theme/motif](../theme-and-motif-contract.md), [character/relationship](../character-and-relationship-architecture.md), [revision/staleness](../revision-staleness-contract.md): semantic owners and cross-layer meaning.
- [Story Opportunity Discovery](../story-opportunity-discovery.md), [Premise Fitness](../premise-fitness.md#L105-L208), [Structure Engine](../structure-engine-v1.md#L70-L143), [Opinionated Narrative Engine](../opinionated-narrative-engine.md): design and creative-search craft knowledge.
- [ADR 012](../adr/012-series-engine-v1.md), [ADR 013](../adr/013-series-graph-semantics.md#L14-L46), [Series artifacts](../artifacts.md#L56-L140), [Series models](../../src/auteur/series/models.py#L15-L284), [dependency builder](../../src/auteur/series/graph.py#L15-L93), [continuity validators](../../src/auteur/series/continuity_validators.py): current Series vocabulary, accepted semantics and actual mechanics.
- [Detailed Narrative Architecture V1](../architecture/detailed-narrative-architecture-v1.md#L126-L211), its [gap matrix](../architecture/detailed-narrative-architecture-v1-gap-matrix.md), [ADR 019](../adr/019-derived-global-map-and-story-instance-relation-authority.md), [Campaign specification](../campaign/auteur-long-horizon-narrative-intelligence-campaign.md), [Campaign state](../campaign/auteur-long-horizon-campaign-state.md#L303-L336), and [Dense Trilogy reassessment](dense-trilogy-v1-campaign-reassessment.md): continuity, authority, projection and their explicit evidence gates.
- [Reasoning Architecture](../reasoning-architecture.md), [Studio Architecture implementation](../../src/auteur/beginner/studio_architecture.py), [Studio ontology context](../../src/auteur/beginner/studio_ontology_context.py), [Studio Inquiry](../../src/auteur/beginner/studio_architecture_inquiry.py), [graph intent](../../src/auteur/beginner/studio_architecture_graph_intent.py), [Architecture preferences](../../src/auteur/narrative_ontology/architecture_preferences.py), [Studio revision review](../../src/auteur/beginner/studio_architecture_review.py), [Studio Realization](../../src/auteur/beginner/studio_realization.py).

**Observed and analytical evidence inspected:** [initial architecture adversarial review](../reviews/2026-10-21-initial-narrative-architecture-adversarial-review.md), [November 6 coverage assessment](2026-11-06-narrative-architecture-ontology-and-reasoning-coverage-assessment.md), [connected creative thread](2026-11-06-connected-creative-thread-evaluation.md), [hybrid revision](2026-11-05-hybrid-architecture-revision-evaluation.md), [bell-keeper run 1](2026-11-07-bell-keeper-reflective-reasoning-probe-execution-evaluation.md), and [bell-keeper run 2 with cross-run reconciliation](2026-11-07-bell-keeper-reflective-reasoning-replication-run2-evaluation.md).

**Claim hierarchy:** accepted canonical contracts and executable models establish current ownership and mechanical constraints; advisory craft documents establish available knowledge, not agent execution; actual recorded exercises establish only their bounded observed behavior; analytical counterexamples below expose logical affordances and risks but are **not new executed experiments**. No model runs, live requests, Studio or Series compilers, or new validators were executed for this report.

## 3. Existing ontology, craft and data-owner crosswalk

| Conceptual responsibility | Current source and owner | What can be expressed | What is not thereby established |
| --- | --- | --- | --- |
| Narrative concepts and relations | [Base ontology](../../data/ontology/base_ontology.yaml), [Layer 0](../superpowers/layer0-ontology.md) | Arc, Goal, Conflict, Setup, Payoff, Revelation, Reversal, Theme, Relationship and typed conceptual relations | Engine renewal, multi-Book composition or agent competence are not defined by concept names alone |
| Governing experience and identity | [Narrative Architecture](../narrative-architecture.md#L8-L33), [emotional contract](../emotional-trajectory-contract.md#L25-L105) | Reader promise, theme and architectural identity separate from individual events | Emotion labels are not proof of emotional impact |
| Pre-Identity possibility and premise evaluation | [Story Opportunity](../story-opportunity-discovery.md#L48-L88), [Premise Fitness](../premise-fitness.md#L105-L208) | Alternative ends, causal differentiation, runway, renewability and scope fit | Advisory forecasts are not accepted designs or realized effectiveness |
| Causal composition and narrative structure | [Structure Engine](../structure-engine-v1.md#L70-L143), [Studio models](../../src/auteur/beginner/studio_architecture.py#L51-L223) | Want/resistance/stakes/change, thread functions, engine nodes, links, genre interactions and phases | Not all causal relations are typed or verified by schema validation |
| Long-series intentional design | [SeriesIdentity](../../src/auteur/series/models.py#L50-L240), [artifacts](../artifacts.md#L56-L140) | Book functions, global arc, character/faction/relationship/thematic trajectories, mysteries, setups/payoffs, chronology | A valid Series file does not demonstrate that its 12 Books form a compelling architecture |
| Dependency and retrospective impact | [ADR 013](../adr/013-series-graph-semantics.md#L14-L46), [Series graph](../../src/auteur/series/graph.py#L23-L93), [Detailed architecture](../architecture/detailed-narrative-architecture-v1.md#L391-L424) | Source-affects-target edges; dependency and freshness/semantic-impact review against accepted sources | Graph reachability does not prove a specific artistic/causal consequence |
| Reflection, inquiry and revision | [Reasoning Architecture](../reasoning-architecture.md#L18-L102), [Studio Inquiry](../../src/auteur/beginner/studio_architecture_inquiry.py#L20-L109), [revision review](../../src/auteur/beginner/studio_architecture_review.py) | Distinct observation/hypothesis/evaluation/recommendation; challenge/explore/compare; noncanonical review | A method being documentable is not evidence of spontaneous, correct method choice |
| Historical continuity and relevant focus | [ADR 019](../adr/019-derived-global-map-and-story-instance-relation-authority.md), [Detailed architecture](../architecture/detailed-narrative-architecture-v1.md#L317-L424) | Accepted history, current-state projection, declared/deterministic/interpretive relations, Focus and staleness | Reconstructing established story meaning is not creatively planning its future |

**Naming caution:** a genre's governing role, a phase's locally governing genre participation, and an author's engine-hierarchy preference are different owners. Studio node parent_id indicates structural containment, not causal dominance. Series BookPlan.central_engine is a Book-level field; it is not proof that a whole series cannot have co-governing engines.

## 4. Five-family coverage matrices

For every matrix, the nine requested dimensions are assessed at their specific level rather than collapsed into a single score.

### A. Composition — several engines, one story

| Dimension | Evidence-grounded assessment |
| --- | --- |
| Existing concepts | Conflict, Arc, Theme; Premise Fitness multi-engine compatibility; Structure Engine threads; Studio engine/genre nodes and ensemble preference |
| Existing relationships | General ArchitectureLink.function; typed GenreInteraction kinds reinforces/enables/constrains/contrasts/creates_tension/converges; thread support functions; Series dependency edges |
| Data owners | Layer 0 conceptual vocabulary; working Studio ArchitectureCandidate; accepted Identity/Structure and Series Book plans |
| Required operations | Identify each engine's causal loop, consumers and effects; test shared consequences; compare ensemble vs hierarchy; expose tradeoffs without inventing author preference |
| Agent-facing delivery | Studio develop/revise packet includes the candidate, small source-referenced principles, base ontology projection and three independent preference axes; it does not supply the whole Premise Fitness/Structure corpus |
| Authentic/mechanical evidence | [Adversarial review](../reviews/2026-10-21-initial-narrative-architecture-adversarial-review.md#L54-L92) validated ensemble, shared non-agent mechanism and typed genre interaction counterexamples; also accepted a disconnected label-only candidate |
| Limitations | General link function remains prose; no typed co-governing engine role, cross-engine resource/exchange link or transition; disconnected candidate passes structural validation |
| Classification | **REPRESENTABLE BUT UNDER-GUIDED** for long-form design; **FORMALLY UNTYPED** for general causal engine links; **UNTESTED** as 8–12 Book creative output |
| Smallest improving action | In the selected creative-construction exercise, require two rival engine organizations and show actual cross-engine causes in at least three Book functions |

**Boundary:** Source-level representation of an ensemble is supported; reliable ensemble construction by an agent is not.

### B. Transformation — identity preserved through change

| Dimension | Evidence-grounded assessment |
| --- | --- |
| Existing concepts | Arc, Reversal, thematic progression; Series character, relationship, faction states; identity and accepted-history contracts |
| Existing relationships | Book states and transitions, transformative dependency edges, theme advancement, revision impacts, planned versus realized transitions |
| Data owners | Accepted Identity for governing commitments, Structure/Series for intended trajectories, Realization for events and state, derived Map/Focus for interpretation |
| Required operations | Separate conserved creative identity from mutable state; derive aftermath-generated pressure; compare continuity, replacement, drift and provisional alternate futures |
| Agent-facing delivery | Working Studio has phases, links and source-referenced principles; specific identity and working proposals are included where available; detailed Series transformation knowledge is not automatically in every packet |
| Authentic/mechanical evidence | Models support trajectories and states; [Detailed architecture](../architecture/detailed-narrative-architecture-v1.md#L126-L211) defines source and supersession; no recorded long-series constructive transformation demonstration identified |
| Limitations | No formally defined engine-role-transition relation spanning many Books; a changed phase need not explain the retained identity; accepted edits do not automatically rewrite descendants |
| Classification | **SUPPORTED** conceptually/representationally; **REPRESENTABLE BUT UNDER-GUIDED** for causal era changes; **UNTESTED** creatively |
| Smallest improving action | Test whether the agent can transform a resolved revolt into causally necessary reconstruction conflicts without importing an unrelated antagonist |

**Boundary:** Preservation of accepted historical authority is a different claim from preservation of the reader's artistic sense of the same series.

### C. Coordination across horizons — near Book and distant payoff

| Dimension | Evidence-grounded assessment |
| --- | --- |
| Existing concepts | Scope axis, global arc, BookPlan.series_function, mystery payoff book, setups/payoffs, thematic and relationship trajectories, knowledge/state and revision provenance |
| Existing relationships | Declared/derived dependencies use source-affects-target; Book-to-arc transformations; setup/payoff references; semantic-impact and staleness reports |
| Data owners | SeriesIdentity and accepted Book plans for intentions; accepted Structure and Realization for plans and facts; derived Series Bible/graph/Global Map/Focus for views |
| Required operations | Propagate premise changes across Book 2/4/12; distinguish chronological event from disclosure order; preserve unaffected promises; maintain provisional alternative futures |
| Agent-facing delivery | Studio candidate carries a compact abstract architecture, not a 12-Book Series dependency package; focused context may require deliberate retrieval of Series/Book sources |
| Authentic/mechanical evidence | [Series models](../../src/auteur/series/models.py#L58-L240), [ADR 013](../adr/013-series-graph-semantics.md#L14-L46), [Series graph](../../src/auteur/series/graph.py#L23-L93), [Dense Trilogy](dense-trilogy-v1-campaign-reassessment.md#L92-L128) show bounded dependency/history machinery |
| Limitations | BookPlan has no per-field accepted/provisional status; chronology versus disclosure is not uniformly typed; a graph impact path is not an artistic repair; dense-trilogy evidence was synthetic and bounded |
| Classification | **SUPPORTED** for basic Series planning/declared impact; **FORMALLY UNTYPED** for fine-grained future authority/disclosure; **UNTESTED** for coherent prospective 12-Book repair |
| Smallest improving action | Require an early Book-premise revision, trace specific dependent and unaffected Book outcomes, and label each proposal's authority in the exercise |

**Boundary:** At [SeriesIdentity validation](../../src/auteur/series/models.py#L240-L284), limited_series requires its complete contiguous BookPlan list and ongoing requires at least two. This favors complete accepted limited-series representations; a sparse whole-series working sketch can be expressed in noncanonical prose/Studio proposals, but is not the same as a valid accepted twelve-Book SeriesIdentity.

### D. Generativity and renewal — change rather than repetition

| Dimension | Evidence-grounded assessment |
| --- | --- |
| Existing concepts | Narrative runway, engine renewability, expansion capacity, payoff density/latency, complexity and marginal story cost; Structure want/resistance/stakes/change |
| Existing relationships | Problem → choice → changed state → newly caused pressure → new choice; genre/engine compatibility; supporting thread functions; nested setup/payoff |
| Data owners | Advisory Premise Fitness and Structure Engine; working ArchitectureCandidate proposals; accepted Identity/Structure when author chooses a mechanism |
| Required operations | Derive materially different pressures from an outcome, test major resolution and exhaustion, compare transformative renewal with arbitrary escalation or delayed closure |
| Agent-facing delivery | A compact Studio principle requests causal engines, but the full [Premise Fitness agent protocol](../premise-fitness.md#L793-L821) is not injected verbatim into every Studio request |
| Authentic/mechanical evidence | [Premise Fitness runway](../premise-fitness.md#L105-L208) and [dimensions](../premise-fitness.md#L413-L468) give strong craft definitions; bell-keeper runs produced stronger local mechanisms under guidance, not series-renewal qualification |
| Limitations | No evidence of sustained creative variety over Books; a premise can legitimately finish; no universal runway metric or objective quality test |
| Classification | **SUPPORTED** as craft vocabulary; **REPRESENTABLE BUT UNDER-GUIDED** as a long-series agent operation; **UNTESTED** for quality |
| Smallest improving action | Test whether the agent can sustain several genuinely distinct Book conflicts after its central engine resolves in Book 5 and recognize when ending is better |

**Boundary:** A non-escalating, contemplative series can renew meaning through relations and reader attention; increasing antagonist power is neither necessary nor evidence of good runway.

### E. Reflective creative regulation — check the thinking, not only the story

| Dimension | Evidence-grounded assessment |
| --- | --- |
| Existing concepts | Reasoning observation/evidence/hypothesis/evaluation/claim/recommendation; authority and epistemic status; Studio operations explain/challenge/explore/compare/revise |
| Existing relationships | Observation justifies hypotheses; review compares working alternatives; consequence and authorial constraint must be separated; proposal needs explicit action to enter working revision |
| Data owners | Derived Reasoning reports, noncanonical Studio Inquiry exchanges and review, accepted Identity/Structure remain separate |
| Required operations | Diagnose wrong question, method, assumption or scale; detect renamed possibilities, premature convergence, unbounded exploration, necessity overclaims, premise drift and inconsistent revised rules |
| Agent-facing delivery | [Studio Inquiry](../../src/auteur/beginner/studio_architecture_inquiry.py#L20-L80) has operation-specific guidance and same-baseline prior exchanges, but not a general persistent metareasoning controller |
| Authentic evidence | [Connected creative thread](2026-11-06-connected-creative-thread-evaluation.md#L25-L103) found partly renamed alternatives; [bell-keeper cross-run reconciliation](2026-11-07-bell-keeper-reflective-reasoning-replication-run2-evaluation.md#L164-L227) found real prompted corrections and persistent errors |
| Limitations | Prompts can induce correction, but neither spontaneous method selection nor consistent lowest-level repair is shown; better labels sometimes coexist with unchanged or new invalid inferences |
| Classification | **OBSERVED REASONING FAILURE** on specific cases; **SUPPORTED** for prompted reflection as an available operation; **UNTESTED** for reliable adaptive/metareasoning competence |
| Smallest improving action | In the new-series exercise, introduce one substantial architecture weakness and an early-premise counterfactual, then observe whether the agent identifies and repairs the lowest appropriate level without being given the answer |

**Boundary:** Bell-keeper is evidence that existing concepts can be used and misused. It is not evidence that more ontology fields solve an inference error. Run 2's inherited repository instructions prevented strict clean-context qualification, and neither run establishes improvement attributable to ontology exposure.

## 5. Semantic and representational boundaries

1. **Layer versus scope.** Layer 0 defines concept kinds; Series is a scope across layers, not a sixth semantic layer. Macro Book cycles are optional Structure groupings, not new canonical scopes. [Narrative Architecture](../narrative-architecture.md#L8-L40).
2. **Containment versus cause.** Studio parent_id is a hierarchy edge; ArchitectureLink.function can describe causal or thematic functions but is free text. GenreInteraction.kind is typed only between genre contracts. [Studio models](../../src/auteur/beginner/studio_architecture.py#L51-L223).
3. **Genre governance versus engine governance.** A GenreContract.role, a phase's GenreParticipation.role, and independent engine-hierarchy preferences do not imply the same authority or temporal level. [Architecture preferences](../../src/auteur/narrative_ontology/architecture_preferences.py#L14-L66).
4. **Series plan versus working proposal.** An accepted SeriesIdentity has one central_engine field for each Book plan and required BookPlan entries. This can coexist with narrative descriptions of multiple co-governing engines, but typed global engine hierarchy/transition is limited. Do not misstate this as proven impossibility. [Series models](../../src/auteur/series/models.py#L58-L74).
5. **Future detail versus authority.** Vivid proposed future Book material is noncanonical until accepted; there is no general SeriesIdentity per-assertion authority enum. Store different authorities in their appropriate accepted/working provenance, not by inventing a new story-canon graph. [Detailed architecture](../architecture/detailed-narrative-architecture-v1.md#L185-L211).
6. **Historical state versus prospective invention.** Global Map and Focus reconstruct and select relevant accepted history; they do not automatically design an unaccepted future. Interpretive relations never become truth by being indexed. [ADR 019](../adr/019-derived-global-map-and-story-instance-relation-authority.md).
7. **Chronology versus disclosure.** TimelineEvent covers event time and Book position; Studio phases can narrate reveal order in text. The two are not uniformly separate typed axes. Do not infer an unrepresentable story from non-queryable text. [Series model](../../src/auteur/series/models.py#L170-L185).
8. **Contract-valid versus art-valid.** The real Studio adversarial validator accepted both meaningful abstract non-agent architectures and a disconnected label-only candidate. Structural validation is not a causal-quality validator. [Adversarial review](../reviews/2026-10-21-initial-narrative-architecture-adversarial-review.md#L54-L92).
9. **Judgment versus canon.** Studio Inquiry may interpret or challenge, but only explicit author action promotes permitted material into accepted owners. [Studio Inquiry](../../src/auteur/beginner/studio_architecture_inquiry.py#L222-L289), [Narrative Architecture](../narrative-architecture.md#L68-L75).

## 6. Agent-facing delivery, reasoning and observed creative effectiveness

**What actually reaches the host-agent develop/revise request:** [prepare_architecture](../../src/auteur/beginner/studio_architecture.py#L949-L1022) serializes working source (including Story Vision), accepted Identity context where available, compact source-referenced composition/authority principles, preference vocabulary, and [base ontology definitions plus directed relations](../../src/auteur/beginner/studio_ontology_context.py#L91-L149). Installed genre extensions are added only when the Vision/accepted Identity explicitly names them. The response is schema-validated and remains a working candidate; [complete/apply](../../src/auteur/beginner/studio_architecture.py#L1023-L1147) guard freshness and never accept Identity/Structure canon.

**What an inquiry receives:** [prepare_architecture_inquiry](../../src/auteur/beginner/studio_architecture_inquiry.py#L222-L289) sends the working candidate, resolved graph anchors and relations, author_question, derived narrative_design_context and up to three prior same-baseline exchanges. Its payload is not the complete original Story Vision. If an author-fixed premise was never represented in the candidate, source refs and SHA receipts alone do not make its content visible to the inquiry. This is a **plausible / previously documented context-delivery asymmetry** requiring a concrete packet and decision-specific consequence before treating it as a new product defect. It is separate from the original direct-prompt bell-keeper errors, where the premise was given to the worker.

**What is not guaranteed:** the full Premise Fitness manual, a Series-scale dependency map, accepted-authority metadata for each imagined Book 20 detail, a self-selected creative reasoning strategy, or proof that the host agent opened a referenced document. The code establishes request assembly, not worker attention or imaginative effectiveness.

**Actual evidence, kept separate:**

- [Initial adversarial review](../reviews/2026-10-21-initial-narrative-architecture-adversarial-review.md#L54-L100): schema accepted difficult forms, but also a disconnected label list; an earlier live attempt initially failed a 120-character link-function bound, and a repaired copy rendered. This is structural/interface evidence, not long-series literary quality.
- [Connected creative thread](2026-11-06-connected-creative-thread-evaluation.md#L25-L103): initial alternatives were judged partly renamed. Later changes carried divergence axes, inquiry continuity, alternative adoption and resume lineage. Distinct axes are not proof of genuinely distinct causal mechanisms.
- [Bell-keeper run 1](2026-11-07-bell-keeper-reflective-reasoning-probe-execution-evaluation.md#L24-L85): first-pass largely sensible, real prompted corrections, missed secrecy premise and internally inconsistent revision; Stage 3 incorrectly skipped.
- [Bell-keeper run 2](2026-11-07-bell-keeper-reflective-reasoning-replication-run2-evaluation.md#L18-L129) and [cross-run reconciliation](2026-11-07-bell-keeper-reflective-reasoning-replication-run2-evaluation.md#L164-L227): substantive corrections and more specific creative mechanisms coexisted with misclassified entailment, premise drift and fresh contradictions. The worker inherited context and there is no causal attribution to ontology or generic guidance.
- [Dense Trilogy reassessment](dense-trilogy-v1-campaign-reassessment.md#L92-L128): bounded synthetic historical continuity and projection, not an exercise constructing an emotionally compelling new multi-book narrative.

**Competency claim ceiling:** no 8–12 Book authentic generative construction was identified in the inspected evidence. No source can establish reader response, comparative originality, reliable self-correction or the effect of selectively delivering the ontology.

## 7. Planning strategies and the detail-versus-authority distinction

| Question | Strategy A: extensive upfront | Strategy B: progressive adaptive | Proposed hybrid: deep foresight, progressively committed detail |
| --- | --- | --- | --- |
| Whole-Series identity | Establish before Book 1 | Establish before Book 1 | Establish identity and high-level engines early |
| Book-level specificity | Many Books sketched in detail | Near Books detailed, future Books selectively sketched | Distant promises and era functions clear; fine detail deferred where possible |
| Distant payoff | Strong ability to place early foreshadowing, with large revision cost | More optionality, with risk of inadequate early planting | Firm sparse payoff obligations plus provisional implementation routes |
| Engine transformation | Planned transitions in advance | Informed by emerging consequences | Anchor plausible transformations while allowing new ones |
| Revision cost | High blast radius when early plans change | Lower drafting waste, possible cross-horizon omissions | Review dependents selectively and revise only affected projections |
| Working vs accepted | Easy to mistake detailed plan for accepted canon | Easy to mistake open plan for no commitment | Explicitly separate *detail density* from *commitment authority* |
| Evidence today | Models support extensive BookPlan lists | Working Studio and prose support partial plans; ongoing Series permits >=2 Book plans | Conceptually consistent with existing owners; **not tested as the default workflow** |

Critical counterexamples:

- A Book 12 revelation may be **author-accepted in meaning** but have a provisional mechanism. This fits distinct Identity commitment versus working Structure plan; no special new Layer-0 concept is required.
- A detailed Book 4 draft may still be **unaccepted**. Source density and numerical Book position do not promote it to canon.
- An accepted early Realization event remains authoritative history after a provisional future plan changes. [Detailed architecture](../architecture/detailed-narrative-architecture-v1.md#L126-L211) preserves revisions rather than silently rewriting descendants.
- A limited SeriesIdentity currently requires all declared Book plans and contiguous numbering; this **does not** mean the author must pre-accept every speculative future idea. It does mean current accepted schema shape is not a partial-horizon candidate contract. [Series validation](../../src/auteur/series/models.py#L240-L266).

**Assessment:** hybrid planning is a strong *hypothesis*, not an owner-ratified product default. No repository observation proves it artistically superior to upfront or adaptive planning. No default should be inferred from a 20-Book target, maximalist preferences or the word “epic.”

## 8. Analytical counterexamples (not new model experiments)

| Case | Can concepts express it? | Relation / context and reasoning issue | Bounded outcome |
| --- | --- | --- | --- |
| **A. Multi-engine political fantasy**: progression, politics, exploration, intimacy and mystery with no single villain | **Yes in working form.** Engine nodes, ensemble preferences, links, threads, genre interactions and Book functions allow it | Engine resource/pressure exchanges must be argued causally; general links are not fully typed; Stage 1 Studio guidance may favor compressed hierarchies | **REPRESENTABLE BUT UNDER-GUIDED** and **FORMALLY UNTYPED**; agent quality **UNTESTED** |
| **B. Transformative epic**: rebellion succeeds, reconstruction begins | **Yes.** Arc/Reversal, phase transitions, Book functions, faction and theme states can express continuity | Must distinguish identity-preserving consequence from new unrelated engine, and accepted change from provisional era proposal | **SUPPORTED** vocabulary; creative transformation **UNTESTED** |
| **C. Book 12 revelation depends on Book 2; Book 2 edited during Book 4** | **Yes at declared dependency/plan level.** Source-affects-target and setups/payoffs exist | Explicit dependencies can flag reconsideration, but which artistic solution survives needs interpretation; not all future details have typed authority; preserve unaffected commitments | **SUPPORTED** mechanical concepts; **FORMALLY UNTYPED** fine-grained commitment; prospective reasoning **UNTESTED** |
| **D. Non-escalating contemplative cycle**: meaning changes through ritual and relationships | **Yes in free text and abstract Studio proposal.** The adversarial validator accepted a cyclical/non-agent form | Premise Fitness asks renewability without requiring bigger threats; a competent agent must make changing interpretation matter to readers | Representable, **UNTESTED** as literary achievement; numeric escalation **NOT REQUIRED** |
| **E. Adversarial creative reasoning**: repeated ideas, optional mechanism treated as necessary, provisional future promoted | **Yes as critique/authority distinctions.** Studio explain/challenge/explore and Reasoning Architecture can state the issue | Authentic bell-keeper errors and partly renamed alternatives show that available distinctions can be mishandled even when present | **OBSERVED REASONING FAILURE** in bounded cases; no proof of ontology absence |

**Illustrated Book 5 resolution choice:** a twenty-Book series must not be prolonged just because twenty Books were requested. The agent should compare (i) institutional and interpersonal consequences of victory, (ii) newly central subordinate engines, (iii) shifted thematic questions, and (iv) **intentional closure**. Runway measures meaningful state transformations and costs; endless postponement and numerical threat inflation are not substitutes. [Premise Fitness](../premise-fitness.md#L105-L208), [dimensions](../premise-fitness.md#L413-L468).

## 9. Confirmed, plausible and untested gaps

| Claim | Classification | Exact boundary and evidence |
| --- | --- | --- |
| Studio generic architecture relations do not share a typed causal vocabulary | **FORMALLY UNTYPED** | ArchitectureLink.function is a bounded string, versus typed GenreInteraction.kind; [models](../../src/auteur/beginner/studio_architecture.py#L51-L124). Not a semantic impossibility |
| Engine co-governance and engine transition are not separately typed in candidate/Series data | **FORMALLY UNTYPED** | [Studio models](../../src/auteur/beginner/studio_architecture.py#L51-L223), [Series models](../../src/auteur/series/models.py#L58-L74). Existing descriptive composition remains possible |
| Per-Book future detail cannot individually record accepted/provisional in SeriesIdentity | **FORMALLY UNTYPED** in that model | [SeriesIdentity fields](../../src/auteur/series/models.py#L213-L240), while existing accepted and working provenance remain distinct elsewhere |
| Studio Inquiry may not receive a fixed Vision premise unless candidate or author_question carries it | **CONTEXT-DELIVERY GAP**, conditional | [Inquiry payload](../../src/auteur/beginner/studio_architecture_inquiry.py#L222-L289) lacks raw Vision; real significance depends on what the candidate includes |
| Agent produces renamed alternatives and misstates entailment, premises or later rule consistency | **OBSERVED REASONING FAILURE** | [Creative thread](2026-11-06-connected-creative-thread-evaluation.md#L44-L54), [bell-keeper reconciliation](2026-11-07-bell-keeper-reflective-reasoning-replication-run2-evaluation.md#L164-L227) |
| Available Premise Fitness concepts are not a complete live 12-Book agent procedure | **REPRESENTABLE BUT UNDER-GUIDED** | [Premise Fitness protocol](../premise-fitness.md#L793-L821) exists as documentation; [Studio guidance](../../src/auteur/beginner/studio_architecture.py#L398-L447) is curated/short |
| Comprehensive creative competence on engine renewal, ensemble composition and long-horizon revision | **UNTESTED** | Existing direct exercises are local mechanisms; Dense Trilogy tests history/projections, not new-series invention |
| A new Layer-0 concept is strictly required | **UNTESTED / not established** | No observed case shows a consequential distinction cannot be expressed through existing owners. Therefore extension is **NOT REQUIRED now** |
| Numerical threat escalation or mandatory infinite renewal | **NOT REQUIRED** | Premise Fitness allows deliberate closure and non-escalating forms |

A representation gap is **observed** only when a consequential distinction cannot survive any existing accepted or working owner in the necessary workflow. The present evidence identifies typed-query limits, **not an observed loss of the artistic distinction itself**.

## 10. Ontology expansion necessity assessment

Responses to the eight requested questions:

1. **Present under other names:** reusable transformation is Arc/Reversal/Series state change; generativity is runway/renewability/expansion; coordinated commitments are Series dependencies and setups/payoffs; reflection is Reasoning Architecture plus Studio challenge/inquiry.
2. **Already representable:** plural engines, institutional transformation, distant revelations, non-escalating arcs and provisional futures through working text, Studio graph, Series plans and accepted-artifact authority.
3. **Need better examples/methods before new types:** causal engine interaction, post-victory renewal, distinguishing intent-preserving transformation from drift, diagnosis of false necessity, and rule consistency after revision.
4. **Could benefit from tighter semantics without new entities:** cause versus support versus containment, engine-governance transition, chronology versus disclosure, and source-backed future-obligation dependencies.
5. **May need improved delivery:** long-form craft context and relevant Series-plan/author constraints on the particular host-agent request. Source presence or a path reference is not an actual read.
6. **Current model constraints:** general Studio graph links use text; v2 Studio candidate forbids instantiating character/relationship nodes (it is deliberately abstract); per-Book central_engine is singular; limited_series BookPlan list is complete; SeriesIdentity has no per-claim provisional flag.
7. **New Layer-0 definitions demonstrably required:** **none** on current evidence. Do not universalize a project-specific “engine phase” or “future Book promise” before an agent use-case fails in existing representations.
8. **Interesting but not justified:** a universal 100-Book ontology, independent canonical story graph, fixed creativity score, mandatory metareasoning controller, machine-enforced emotional ladder or automatic future canon.

**Candidate improvements are hypotheses, not implementation tasks:**

| Candidate | Decision improved and existing alternative | Why not admit now / risks | Evidence gate |
| --- | --- | --- | --- |
| Explicit engine-to-engine causal relation | Decide whether political and relationship engines genuinely generate joint consequences; use ArchitectureLink.function and explanatory reviews today | Typed ontology may narrow unanticipated forms and duplicate genre interactions | A real multi-engine proposal loses relevant relation identity or cannot be meaningfully reviewed |
| Engine role transition | Recognize co-governor becoming local or central after a victory; use phases, Book functions, narrative explanation | Over-formalizes narrative era changes; global role may differ from local role | Actual series revision cannot preserve the difference in existing Structure/Series owners |
| Future obligation and disclosure distinction | Preserve Book 12 revelation when Book 2 changes; use setup/payoff, dependency edge, descriptive chronology/disclosure, accepted provenance | Extra graph owners or bidirectional semantics could duplicate current authority | Observed missed dependency or wrong future promotion despite all context present |
| Consequential-inference review method | Reduce false necessity and premise drift before revising a mechanism; reuse Reasoning Architecture and Studio challenge | Checklist overhead and premature caution could weaken divergent creativity | A fresh ordinary-operation comparison shows better warranted decisions *without reducing* creative diversity |

Every candidate's proposed consumer is a creative agent or reviewer performing a concrete decision. None warrants a production ontology change now; proof of inadequate old representation and qualitative value must precede formalization.

## 11. Highest-value opportunities for creative conception

The value frontier is **using** available knowledge to construct better stories, not growing the ontology for its own sake.

- **Causal engine interaction:** ask how one engine changes the available choices and costs in another, rather than whether both appear in a synopsis. Preserve ensemble possibility and distinct reader functions.
- **Consequences of success:** turn an achieved goal into changed actors, institutions, obligations and pressures. Accept closure where renewal would be artificial.
- **Long-range dependency reasoning:** test a distant payoff against its upstream premises; distinguish what must be repaired from what survives unchanged.
- **Critical creativity, not cautious paraphrase:** after identifying an unsupported necessity, revise the actual mechanism and verify its newly introduced rules. Bell-keeper shows improvement and regression can coexist.
- **Planning posture as an author-governed choice:** expose upfront/adaptive/hybrid tradeoffs without silently converting detailed sketches into accepted story material.

These can be advanced as **one cohesive creative-construction exercise** with an actual agent, rather than several ontology/implementation responsibilities. Future method or context repair should be selected from *observed* failures.

## 12. Implications for future Studio Architecture UX (not authorized work)

A future horizon-sensitive Studio might expose: (a) a legible whole-Series governing promise and interacting engines, (b) optional macro-cycle views, (c) selectively detailed near Books, (d) distant setup/payoff and institutional/relationship trajectories, and (e) provenance-aware questions about why a Book serves the whole. Relationships and explicit revisions should remain first-class inquiry targets. Keep node/link selection grounded in validated IDs and candidate revision hashes.

The present working [ArchitectureCandidate](../../src/auteur/beginner/studio_architecture.py#L154-L223), [graph-intent contract](../../src/auteur/beginner/studio_architecture_graph_intent.py), [Studio Inquiry](../../src/auteur/beginner/studio_architecture_inquiry.py#L222-L289) and [review](../../src/auteur/beginner/studio_architecture_review.py) already support much of the interaction foundation. That does not prove that a single graph is the right UX at Series scale. Prefer context focus and explanation to indiscriminate node proliferation. No UI change follows from this document.

## 13. Relation to Narrative Realization and Expression

Narrative Architecture is the product differentiator under investigation, but eventual effectiveness requires testing whether planned causal engines generate meaningful events, character choices, relationship consequences and prose scenes. [Canonical layers](../narrative-architecture.md#L8-L33), [emotional trajectory](../emotional-trajectory-contract.md), [theme/motif](../theme-and-motif-contract.md) and [Studio realization proposal](../../src/auteur/beginner/studio_realization.py) preserve these distinct owners. Realization evidence may reveal that a supposedly generative engine is sterile, and prose may expose a promised emotion that is not earned.

Those observations should prompt an author-reviewed proposal to the **lowest correct owner** (Expression, Realization, Structure or Identity), not silent story-wide rewriting. A scene test can later be useful for discriminating two rival mechanisms; it is not a mandatory precondition for this documentation assessment or the first abstract 8–12 Book exercise.

## 14. Evidence limits, uncertainty and campaign boundary

- No new coding-agent generation, independent reviewer, reader study, Series compiler invocation or Studio E2E execution was performed in this assessment. All five counterexamples are **analytical thought probes**.
- The prior Studio candidate validator probes demonstrate structural permissiveness; their relevance to quality of generated long series is unknown.
- The bell-keeper exercises are real but sequential, local-scope and partly contaminated by inherited context; a prompted correction is not spontaneous metareasoning, a reviewer preference is not reader impact, and multiple errors remained.
- The exact effect of Premise Fitness context delivery on an ordinary coding agent is unknown. Do not infer that an omitted document caused a failure whose task already included its premise.
- Main-level GitHub source inspection supports the cited code shape, not exhaustive runtime reachability across every host/adapter. This assessment does not claim new successful tool execution.
- [Long-horizon Campaign state](../campaign/auteur-long-horizon-campaign-state.md#L303-L336) remains **PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION**, no active successor, no approved ontology/extraction/scale implementation. Its historical reconstruction mission must not be reopened by this independent future-construction inquiry.
- The hybrid planning posture is still advisory; the author retains the future choice of upfront, adaptive or hybrid as an interface default.

## 15. Exactly one next responsibility

**SELECT C — Authentic Creative Construction Exercise.**

**Why C rather than A/B/D/E?** Coverage and available semantics are already sufficiently broad to attempt construction: further divergent naming or ontology depth would add uncertainty without testing the core product thesis. A demonstrated, localized implementation defect in long-series creative production has not been established, so D would be premature. E/no action would leave the owner's newly selected differentiator unexamined. One genuinely executed, bounded exercise is the least additional evidence that can discriminate craft-method, context, reasoning and representation problems.

**Scope of the next separately authorized responsibility (not executed here):**

1. Use an unfamiliar original Story Vision, ordinary repository-capable coding-agent context, exact baseline, and real source-read/request/response receipts.
2. Construct an **8–12 Book** working Series Architecture, not twelve plot synopses: meaningful central/ensemble interactions, one non-character causal engine, Book functions, long-horizon promises, a transformative era change and differentiated emotional/thematic progression.
3. Compare at least two actual causal organizations, with author-given constraints held fixed; do not assume the author approved a planning-mode default.
4. Introduce a consequential Book 2 premise revision during Book 4 planning and inspect the Book 12 reveal and unaffected commitments; retain explicit accepted/provisional/unknown status in existing working artifacts.
5. Challenge an exhausted or repetitive engine (e.g., a conflict substantively resolved by Book 5); require causally derived alternatives, including legitimate closure, not escalating clones.
6. Ask the same working agent to critique/revise the **lowest necessary** level; save the original and revised mechanisms and explain gains and new inconsistencies.
7. Have a separate source-aware reviewer evaluate distinctiveness, renewable causality, engine interaction, horizon coordination, fidelity, sound entailments and meaningful reader promise; treat literary strength as editorial judgment and preserve contrary findings.
8. Inspect whether another fresh context can reconstruct the working architecture and author/agent commitments from recorded artifacts. Do not produce a new canonical schema or auto-accept any proposal.

**Decision after that evidence:** if construction is strong, retain the present model and test further only for a concrete future decision; if it fails, identify the smallest observed owner (retrieval, creative method, Series coordination, representation or author UX). Do not pre-authorize any subsequent fix, benchmark expansion or Campaign reopening.

## 16. Completion and validation boundary

This document assesses the five families using the current baseline, cites existing source definitions and observed exercises, records the distinctions among conceptual, representational, delivered, reasoning and creative capability, compares planning postures, tests five analytical counterexamples and selects **one** next responsibility.

**Documentation-only constraint:** The only permitted changes in its PR are this report and (if useful) a pointer from the existing strategy. Structural link/source inspection and PR diff review are not equivalent to runtime tests or creative qualification. CI absent means **not run**, never passed.

**Final finding:** the current warrant favors **an authentic creative-construction observation using the existing narrative knowledge**, while leaving ontology expansion unselected and preserving the author-controlled authority model.
