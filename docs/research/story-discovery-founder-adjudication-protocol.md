# Phase E — Story Discovery Founder Creative Adjudication

## Status

Founder review pending.

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

During first-pass review, the founder should use only `story-discovery-founder-review-packet.md`.

The review packet omits:

- Phase D case IDs and premise classes;
- candidate IDs and fixture keys;
- generation lenses;
- contract-fit values;
- synthetic-provider self-evaluation;
- automated expected-winner mechanics;
- selection rationale for why a case entered Phase E.

No post-hoc metadata or comparison with Phase D expectations should be revealed until the founder has recorded a first-pass response for all six cases.

## Case selection

Six cases are selected from the Phase D corpus for high information value. Selection favors cases where:

- multiple directions are plausibly attractive;
- the recommendation requires an actual creative tradeoff rather than obvious defect detection;
- premise constraints create pressure on interpretation;
- emotional, structural, genre, or authority choices can pull in different directions.

The packet is not intended to estimate a success rate across the full corpus.

## Founder response protocol

For each case, record one primary reaction:

1. **Strong agreement** — the recommendation is the direction the founder also finds strongest.
2. **Respectful disagreement** — the founder would choose another direction, but Auteur's recommendation is intelligent and useful.
3. **Unpersuaded** — the founder does not find the recommendation defensible or illuminating.
4. **False choice** — the directions are not meaningfully different enough to support the presented decision.

Then answer five compact questions:

- **Meaningful choice:** Are the three directions genuinely different stories worth choosing between?
- **Recommendation clarity:** Is it clear why Auteur prefers the recommended direction?
- **Insight:** Did the recommendation reveal or clarify something about the premise?
- **Alternative fairness:** Are the alternatives presented as credible options rather than strawmen?
- **Authority feel:** Does Auteur remain opinionated without making disagreement feel like disobedience?

Short prose is preferred over numeric scoring. The founder may identify a preferred alternative when disagreeing.

## Healthy vs unhealthy disagreement

Strong agreement is not the only success state.

A **respectful disagreement** is healthy when the founder can say, in effect:

> I would choose another direction, but Auteur exposed a real tradeoff and made my choice more conscious.

An **unpersuaded** result is more serious:

> I cannot see why this recommendation deserves preference over the alternatives.

## Failure classification

After all responses are frozen, classify any negative cases as:

- **SEARCH / CHOICE FAILURE** — directions are not meaningfully distinct;
- **JUDGMENT FAILURE** — the recommended direction is not defensible relative to alternatives;
- **RATIONALE / SURFACE FAILURE** — the underlying choice may be sound, but the explanation is generic, unfair, or unhelpful;
- **AUTHORITY UX FAILURE** — the recommendation presentation feels coercive or pre-canonical.

A case may have more than one classification if the founder response supports it.

## Decision rule

Do not make production changes from one isolated preference disagreement.

Move to implementation only if founder responses reveal a repeated pattern tied to a specific subsystem. Examples:

- repeated false choices → revisit search diversity;
- repeated unpersuaded recommendations with attractive alternatives → revisit comparative judgment;
- repeated understanding without insight → revisit recommendation rationale/surface;
- repeated authority discomfort → revisit recommendation language and handoff.

If most cases are either strong agreement or respectful disagreement, with credible alternatives and clear authority, the founder-confidence layer is considered encouraging and the next product question may move to conversational onboarding or optional live-provider dogfood.

## Workflow

1. Founder reviews all six cases using only the blinded packet.
2. Founder responses are recorded without editing the cases.
3. Coding agent classifies patterns and prepares a findings document.
4. Any proposed production change is separated into its own issue/PR.
5. This Phase E research PR remains research-only.
