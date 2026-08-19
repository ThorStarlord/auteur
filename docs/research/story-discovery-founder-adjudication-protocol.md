# Phase E — Story Discovery Founder Creative Adjudication

## Status

**Complete.** Founder creative adjudication concluded on 2026-08-19 after the six-case review sequence produced convergent product-level findings. The phase is closed as a research pass; production changes are intentionally deferred to a separate implementation phase.

This phase follows the qualified Phase D synthetic product-confidence gate. It adds a deliberately small human creative-judgment layer without pretending to be a multi-writer usability study.

## Research question

> Is Auteur's opinion worth hearing — does a recommendation make the creative decision clearer, even when the founder would choose differently?

## Evidence boundary

The six review cases use premises and narrative-engine seeds from the Phase D qualified synthetic corpus.

Phase D intentionally used generic comparative fixture copy to test mechanics. That copy is not suitable for a creative-usefulness review. Therefore, Phase E permits the coding agent to write premise-specific **simulated** recommendation rationales and alternative tradeoffs from the existing candidate commitments.

The founder is evaluating the usefulness of the recommendation concept and surface under controlled examples, not live-provider performance.

### Qualified conclusion

Phase E supports the bounded conclusion that the Story Discovery recommendation concept is worth continuing: when author intent is sufficiently specified and the candidates differ at the level of causal strategy, the recommendation can expose useful narrative tradeoffs while preserving author authority. The review also surfaced concrete requirements around intent capture, causal distinctness, architecture-preference vocabulary, emotional hierarchy, composition, and craft-teaching explanations.

### Claims this phase does not establish

Phase E does not establish:

- quality or diversity of live Anthropic/OpenAI generations;
- live-model comparative-judge quality;
- broad writer usability or preference;
- population-level acceptance rates;
- that a simulated rationale matches what a production provider would generate.

## Blinding rules

During first-pass review, the founder used only the founder-review packet and the case-specific simulated author brief presented for adjudication.

The review surface omitted:

- Phase D case IDs and premise classes;
- candidate IDs and fixture keys;
- generation lenses;
- contract-fit values;
- synthetic-provider self-evaluation;
- automated expected-winner mechanics;
- selection rationale for why a case entered Phase E.

The original founder-review packet remains unchanged as historical evidence of what was presented. Protocol and findings documents may record later interpretations without rewriting that packet.

## Protocol amendments learned during review

### 1. Intent adequacy

Case 1 showed that a sparse premise can support exploration without supplying enough author intent to justify a comparative claim that one direction is **best**.

For adjudication cases after Case 1, the founder received a clearly labeled **simulated author brief**. The brief could contain:

- literal premise;
- primary genre / genre promise;
- target audience;
- target experience / reader experience;
- hard story constraints;
- authorial complexity preference;
- causation preference.

These fields were research scaffolding. Their presence does not imply that the current production Story Discovery front door already collects them.

The literal premise remains story content. Authorial preferences are intent alongside the premise rather than prose inserted into the premise itself.

A fifth valid outcome was therefore recognized:

- **Not adjudicable — insufficient author intent**: the directions may be distinct and the recommendation may be understandable, but there is not enough declared author intent to justify ranking one direction as best.

### 2. Authorial architecture preferences

Case 2 and the later Case 4 discussion showed that an author may prefer a strong primary narrative engine while also wanting compatible mechanisms from losing alternatives.

Phase E therefore recognized two explicit preference dimensions:

- **Maximalism** — prefer layered story architecture, multiple interacting dramatic mechanisms, and dense but legible causation rather than the minimum sufficient mechanism.
- **Mixed causation** — prefer major events, reversals, and outcomes to arise from several compatible causal layers rather than a single isolated cause.

The intended hierarchy remains important:

> one primary engine governs the reader promise; secondary mechanisms may deepen motive, obstruction, consequence, or reversal without displacing that engine.

The review later clarified that these are not target emotions or story-type values. They are best treated as **authorial narrative-architecture preferences**: ontology concepts at Layer 0, instantiated as author commitments at Layer 1 Identity, and realized concretely in Layer 2 Structure and downstream events.

A minimal implementation hypothesis is therefore:

- **complexity preference:** focused / layered / maximalist;
- **causal-distribution preference:** concentrated / layered / mixed;
- **engine-hierarchy preference:** single-center / primary-with-layers / ensemble.

These labels remain implementation hypotheses until the production phase validates naming and compatibility with the existing ontology.

### 3. Narrative-engine distinctness

Case 3 showed that alternatives can sound different while remaining too similar at the level of external causal action.

Two candidates are not meaningfully distinct merely because they use different thematic framing, metaphors, institutional vocabulary, or stated advantages.

A materially different narrative engine should change the causal strategy by which the protagonist pursues the central objective and therefore imply meaningfully different:

- major external actions;
- obstacles;
- reversals;
- scene pressure;
- climax mechanics.

Useful shorthand:

> Different engine ≠ different interpretation.
>
> Different engine = different causal strategy producing different major scenes and resolution mechanics.

Candidates may share ingredients, but their **primary causal engines** should be separable enough that the author is choosing among genuinely different stories.

### 4. Craft-layer propagation

Case 5 exposed a surface requirement beyond simple `What you gain / What you give up` prose. A useful recommendation should teach **which craft layer changes** and how that decision propagates downstream into the actual writing and reader experience.

For Phase E, distinguish at least these explanatory layers:

1. **Author intent** — genre promise, audience, target experience, hard constraints, complexity preference, causation preference.
2. **Primary causal engine** — the dominant system of forces that repeatedly converts character intention into conflict, consequence, escalation, and resolution.
3. **Agency / causal ownership** — which character, relationship, institution, or system owns the decisive causal weight.
4. **External action pattern** — what characters repeatedly do: investigate, repair, negotiate, deceive, rescue, confront, and so on.
5. **Pressure system** — what repeatedly makes those actions difficult and escalating.
6. **Scene texture** — the recurring experiential quality and family of scenes the author will spend pages writing.
7. **Aesthetic / tonal framing** — the genre-tonal interpretation of that scene experience.
8. **Reader experience** — the emotional progression those choices are expected to create.
9. **Thematic consequence** — what the resulting causal pattern implies about the story's underlying questions.

The causal engine is therefore **not identical** to external acts, texture, aesthetic framing, or audience emotion. It is generally upstream of them, while target experience also acts as an upstream author constraint when selecting among engines.

A strong alternative explanation should make the propagation legible:

> craft layer changed → different causal weight / protagonist verbs → different scene families and pressure → different texture / aesthetic → different reader emotion → different thematic implication.

`What you gain / What you give up` should identify **where narrative weight moves** and what the author will concretely write more or less of as a result.

For composable alternatives, the surface should also say:

- which layer is being borrowed;
- whether it remains primary or becomes subordinate;
- what emotional or thematic effect the borrowed layer adds;
- what risk would cause it to displace the intended primary engine.

### 5. Emotional hierarchy is rich, but under-exposed

The Case 6 discussion clarified a terminology issue rather than revealing a missing emotional ontology.

Auteur already has a rich `TargetExperience` model with a primary emotional promise, secondary palette, macro emotional trajectory, genre-emotion roles, and optional POV-specific experience contracts. Phase E therefore should **not** introduce a parallel primary/secondary-emotion system.

The relevant distinction is:

- **target audience** — who the story is for;
- **primary emotional promise** — the dominant, governing experience the story sells;
- **secondary emotional palette** — supporting or contrasting feelings;
- **emotional trajectory** — how the experience changes over the story.

Rich emotional variation is compatible with coherence when the emotional hierarchy and trajectory remain legible. Mixed causation is a different axis: it describes how outcomes are caused, not what the audience should feel.

The production opportunity is therefore to collect and expose the existing emotional contract more effectively during Story Discovery, not to duplicate it.

## Founder response protocol used during Phase E

For each case, the review first asked whether the author brief contained enough intent to determine what the recommendation should optimize for.

Primary reactions included:

1. **Strong agreement** — the recommendation is the direction the founder also finds strongest.
2. **Respectful disagreement** — the founder would choose another direction, but Auteur's recommendation is intelligent and useful.
3. **Unpersuaded** — the founder does not find the recommendation defensible or illuminating.
4. **False choice** — the directions are not meaningfully different enough to support the presented decision.
5. **Not adjudicable — insufficient author intent** — there is not enough declared intent to justify ranking the options.

The review also considered baseline fit, causal distinctness, recommendation clarity, craft-layer clarity, reader-experience propagation, insight, alternative fairness, authority feel, and composition.

## Failure classification

Negative or non-adjudicable results are classified as:

- **CONTEXT / INTENT FAILURE** — the recommendation problem is under-specified relative to the author's desired genre promise, audience, target experience, architecture preferences, or hard constraints;
- **SEARCH / CHOICE FAILURE** — directions are not meaningfully distinct at the level of primary causal strategy;
- **JUDGMENT FAILURE** — the recommended direction is not defensible relative to the alternatives and declared intent;
- **RATIONALE / SURFACE FAILURE** — the underlying choice may be sound, but the explanation is generic, unfair, unhelpful, or fails to teach how the craft-layer change propagates into scenes and reader experience;
- **AUTHORITY UX FAILURE** — the recommendation presentation feels coercive or pre-canonical.

A case may have more than one classification if the founder response supports it.

## Stop rule and final decision

Phase E was never intended to estimate a success rate across the synthetic corpus. It was a high-information founder-adjudication pass designed to reveal repeated product patterns.

The review stopped after the Case 6 synthesis because additional cases were no longer producing independent uncertainty about whether the recommendation concept was useful. Instead, the open questions had converged on implementable product requirements:

- author-intent capture before intent-optimal ranking;
- causal rather than rhetorical candidate diversity;
- first-class architecture-preference vocabulary;
- use of the existing rich target-experience hierarchy;
- explanatory tradeoffs that teach craft-layer propagation;
- optional composition under a legible primary engine;
- preservation of explicit author acceptance as the canonical authority boundary.

The next uncertainty is therefore implementation quality, not whether these requirements exist.

## Handoff

Production work must occur in a separate issue / PR series. Phase E itself remains research/docs only and makes no canonical product-state mutation beyond documenting the founder findings.