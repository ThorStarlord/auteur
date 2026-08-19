# Phase E — Story Discovery Founder Creative Adjudication

## Status

Founder review in progress.

This phase follows the qualified Phase D synthetic product-confidence gate. It adds a deliberately small human creative-judgment layer without pretending to be a multi-writer usability study.

## Research question

> Is Auteur's opinion worth hearing — does a recommendation make the creative decision clearer, even when the founder would choose differently?

## Evidence boundary

The six review cases use premises and narrative-engine seeds from the Phase D qualified synthetic corpus.

Phase D intentionally used generic comparative fixture copy to test mechanics. That copy is not suitable for a creative-usefulness review. Therefore, Phase E permits the coding agent to write premise-specific **simulated** recommendation rationales and alternative tradeoffs from the existing candidate commitments.

The founder is evaluating the usefulness of the recommendation concept and surface under controlled examples, not live-provider performance.

### Allowed claim if results support it

> Selected high-information Story Discovery cases passed founder creative adjudication: the controlled simulated recommendation experience exposed understandable, defensible narrative tradeoffs and helped one human author make a more conscious story decision.

### Claims this phase must not make

Phase E does not establish:

- quality or diversity of live Anthropic/OpenAI generations;
- live-model comparative-judge quality;
- broad writer usability or preference;
- population-level acceptance rates;
- that a simulated rationale matches what a production provider would generate.

## Blinding rules

During first-pass review, the founder should use only the founder-review packet and the case-specific simulated author brief presented for adjudication.

The review surface omits:

- Phase D case IDs and premise classes;
- candidate IDs and fixture keys;
- generation lenses;
- contract-fit values;
- synthetic-provider self-evaluation;
- automated expected-winner mechanics;
- selection rationale for why a case entered Phase E.

No post-hoc metadata or comparison with Phase D expectations should be revealed until the founder has recorded a first-pass response for the case.

## Protocol amendments learned during review

### Intent adequacy

Case 1 showed that a sparse premise can support exploration without supplying enough author intent to justify a comparative claim that one direction is **best**.

For adjudication cases after Case 1, the founder receives a clearly labeled **simulated author brief**. The brief may contain:

- literal premise;
- primary genre / genre promise;
- target audience;
- target emotion / reader experience;
- hard story constraints;
- authorial complexity preference;
- causation preference.

These fields are research scaffolding. Their presence does not imply that the current production Story Discovery front door already collects them.

The literal premise should remain story content. Authorial preferences such as maximalism should be recorded as intent alongside the premise rather than rewritten into the premise sentence itself.

A fifth valid outcome is therefore recognized:

- **Not adjudicable — insufficient author intent**: the directions may be distinct and the recommendation may be understandable, but there is not enough declared author intent to justify ranking one direction as best.

### Authorial complexity and causation preferences

Case 2 revealed that an author may prefer a strong primary narrative engine while also wanting compatible mechanisms from losing alternatives.

Phase E therefore permits simulated author briefs to state preferences such as:

- **Maximalism** — prefer layered story architecture, multiple interacting dramatic mechanisms, and dense but legible causation rather than the minimum sufficient mechanism.
- **Mixed causation** — prefer major events, reversals, and outcomes to arise from several compatible causal layers rather than a single isolated cause.

These preferences do **not** mean every candidate should become an undifferentiated mixture of all alternatives. The intended hierarchy is:

> one primary engine governs the reader promise; secondary mechanisms may deepen motive, obstruction, consequence, or reversal without displacing that engine.

A recommendation may therefore succeed even when the author wants to compose subordinate mechanisms from alternatives into the recommended engine.

### Narrative-engine distinctness

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

## Case selection

Six cases are selected from the Phase D corpus for high information value. Selection favors cases where:

- multiple directions are plausibly attractive;
- the recommendation requires an actual creative tradeoff rather than obvious defect detection;
- premise constraints create pressure on interpretation;
- emotional, structural, genre, authority, complexity, or causal choices can pull in different directions.

The packet is not intended to estimate a success rate across the full corpus.

## Founder response protocol

For each case, first ask whether the author brief contains enough intent to determine what the recommendation should optimize for.

Then record one primary reaction:

1. **Strong agreement** — the recommendation is the direction the founder also finds strongest.
2. **Respectful disagreement** — the founder would choose another direction, but Auteur's recommendation is intelligent and useful.
3. **Unpersuaded** — the founder does not find the recommendation defensible or illuminating.
4. **False choice** — the directions are not meaningfully different enough to support the presented decision.
5. **Not adjudicable — insufficient author intent** — there is not enough declared intent to justify ranking the options.

Then briefly address:

- **Baseline fit:** Do the directions satisfy the declared genre, audience, target experience, and hard constraints?
- **Causal distinctness:** Do the directions imply genuinely different primary actions, obstacles, reversals, and climax mechanics?
- **Recommendation clarity:** Is it clear why Auteur prefers its recommendation relative to the declared author brief?
- **Insight:** Did the comparison reveal or clarify something about the story decision?
- **Alternative fairness:** Are the alternatives presented as credible options rather than strawmen?
- **Authority feel:** Does Auteur remain opinionated without making disagreement feel like disobedience?
- **Composition:** If the founder wants elements from multiple alternatives, can one primary engine remain legible while subordinate mechanisms are composed into it?

Short prose is preferred over numeric scoring.

## Healthy vs unhealthy disagreement

Strong agreement is not the only success state.

A **respectful disagreement** is healthy when the founder can say, in effect:

> I would choose another direction, but Auteur exposed a real tradeoff and made my choice more conscious.

A **composition preference** can also be healthy when the founder accepts the recommended primary engine but wants compatible mechanisms from alternatives layered beneath it.

An **unpersuaded** result is more serious:

> I cannot see why this recommendation deserves preference over the alternatives.

## Failure classification

Classify negative or non-adjudicable cases as:

- **CONTEXT / INTENT FAILURE** — the recommendation problem is under-specified relative to the author's desired genre promise, audience, target experience, complexity preference, causation preference, or hard constraints;
- **SEARCH / CHOICE FAILURE** — directions are not meaningfully distinct at the level of primary causal strategy;
- **JUDGMENT FAILURE** — the recommended direction is not defensible relative to the alternatives and declared intent;
- **RATIONALE / SURFACE FAILURE** — the underlying choice may be sound, but the explanation is generic, unfair, or unhelpful;
- **AUTHORITY UX FAILURE** — the recommendation presentation feels coercive or pre-canonical.

A case may have more than one classification if the founder response supports it.

## Decision rule

Do not make production changes from one isolated preference disagreement.

Move to implementation only if founder responses reveal a repeated pattern tied to a specific subsystem. Examples:

- repeated context / intent failures → revisit what Story Discovery needs to know before comparative judgment;
- repeated false choices → revisit search diversity and causal distinctness;
- repeated unpersuaded recommendations with attractive alternatives → revisit comparative judgment;
- repeated understanding without insight → revisit recommendation rationale / surface;
- repeated composition requests → investigate a post-recommendation operation that preserves the primary engine while borrowing subordinate mechanisms;
- repeated authority discomfort → revisit recommendation language and handoff.

If most adequately specified cases are either strong agreement or respectful disagreement, with credible alternatives, causal distinctness, and clear authority, the founder-confidence layer is considered encouraging and the next product question may move to conversational onboarding or optional live-provider dogfood.

## Workflow

1. Founder reviews the six cases using only the blinded research surface and simulated author briefs.
2. Founder responses are recorded without editing the underlying candidate set after the response is known.
3. Coding agent classifies patterns and maintains the findings document.
4. Any proposed production change is separated into its own issue / PR.
5. This Phase E research PR remains research-only until findings are complete.