# Phase H — Agent Semantic Dogfood / Story Discovery plausibility protocol

## Status

**H1 complete; H2 producer pass active.**

Phase G established the writer-facing Story Discovery workflow under controlled evidence. H1 then qualified a reproducible live-provider evidence-capture harness in PR #120. The project has deliberately weakened the remaining Phase H claim: Phase H no longer requires paid Anthropic/OpenAI execution and does not claim live-provider quality.

The H1 harness remains valid optional infrastructure for a later live-provider study. Phase H closure now depends only on bounded coding-agent semantic dogfood.

## Research question

> On a small representative benchmark, can a separated coding-agent producer/evaluator dogfood pass produce and evaluate plausible, meaningfully distinct, intent-aware Story Discovery directions while preserving explicit author authority?

This is a semantic **plausibility** question, not a provider-quality or human-usability question.

## Evidence boundary

Phase H may support only a bounded claim about the tested six-case corpus and the agent-mediated producer/evaluator protocol.

It does **not** establish:

- production Anthropic quality;
- production OpenAI quality;
- cross-provider robustness;
- real-provider prompt reliability;
- experienced-writer acceptance;
- population-level creative usefulness;
- independence equivalent to human adjudication;
- that agent-simulated outputs predict future provider behavior.

The same model family may perform producer and evaluator roles only through explicitly separated passes. Frozen H2 evidence and a reduced H3 evaluator packet reduce self-evaluation bias but do not eliminate it.

## Benchmark corpus

The corpus is `docs/research/story-discovery-phase-h-cases.yaml`.

The six cases encode explicit, production-valid declared author intent and preserve the high-information premises that drove Phase E founder adjudication. The corpus is the fixed H2 input. H2 must copy each declared brief exactly into its frozen evidence.

## Production semantic contracts used by H2

The producer is grounded in the current repository contracts rather than a free-form story-ideation rubric.

### Candidate search / intent

Explicit declared author intent outranks candidate-generated preferences. Hard constraints are hard boundaries. Omitted values remain UNKNOWN. The intent-aware decision priority optimizes first for declared genre/reader promise, target audience and target experience, then declared architecture preferences.

Candidate IDs, generation provenance, confidence, contract-fit values and candidate self-advocacy are not creative-quality evidence.

### Causal qualification (F3)

A direction is causally distinct only when choosing it materially changes major story mechanics such as:

- protagonist or ensemble verbs;
- causal owner;
- recurring pressure system;
- reversal mechanics;
- climax resolution mechanic;
- representative scene families.

Different titles, themes, metaphors, aesthetic adjectives or emotional labels do not establish causal difference by themselves.

For each candidate H2 records:

- primary causal strategy;
- causal owner;
- external action pattern;
- pressure system;
- reversal mechanics;
- climax mechanic;
- representative scene families;
- evidence gaps.

Pairwise classification uses the production vocabulary `distinct`, `near_duplicate`, or `uncertain`. Any near-duplicate or uncertain set is non-adjudicable rather than forced to a winner.

### Comparative recommendation

When F3-style evidence is adjudicable, the producer makes one advisory recommendation against the declared brief. Contract fit is compliance evidence, not artistic quality. Complexity and profile length are not automatic quality signals. The recommendation must explain actual tradeoffs against every surviving alternative.

### Craft impact (F4)

For each losing alternative, H2 separates:

- causal strategy / causal ownership;
- external actions;
- pressure system and scene families;
- story texture / aesthetic emphasis;
- reader experience;
- thematic consequence.

It records what is gained, what is given up, and one composability classification using the production vocabulary:

- `compatible_as_secondary`;
- `requires_reframing`;
- `mutually_exclusive_with_primary`;
- `uncertain`.

Architecture preferences are not emotions. `maximalist` + `mixed` may support multiple mechanisms, but `primary_with_layers` still requires one legible governing engine.

## Execution sequence

### H1 — Evidence-capture infrastructure — COMPLETE

PR #120 added:

- the versioned six-case corpus;
- reproducible provider/case capture infrastructure;
- provenance and redaction controls;
- a hard no-acceptance invariant;
- offline qualification tests.

Validation #316 passed Python 3.11/3.12/3.13, repository verification/Ruff and wheel smoke.

The strongest H1 claim remains only that Auteur can reproducibly capture provider evidence without crossing canonical authority. H1 is not itself semantic-quality evidence.

### H2 — Frozen coding-agent producer pass

The producer receives only the fixed benchmark briefs plus the production semantic contracts summarized above. For every case it creates three candidate directions, causal profiles, pairwise causal classification, one recommendation if adjudicable, alternative-specific craft impacts and bounded composition notes.

The producer **must not evaluate its own output**. H2 contains no `convincing`, `defensible with concerns`, `failure`, score, pass rate, or equivalent evaluator verdict.

H2 is complete when the full producer packet is committed and merged unchanged, with the exact repository revision and producer role recorded.

### H3 — Context-reduced semantic evaluator pass

H3 starts only after H2 is frozen. Build an evaluator packet from H2 that preserves author intent and candidate/craft evidence while removing quality-irrelevant cues where feasible:

- producer commentary;
- candidate-order significance;
- generation provenance;
- confidence or contract-fit ranking cues;
- any metadata that implies which direction was intended to win beyond the recommendation being evaluated.

For each case the evaluator records one qualitative outcome:

- **convincing**;
- **defensible with concerns**;
- **failure**;
- **not adjudicable**.

Then review causal distinctness, causal-profile accuracy, recommendation defensibility, craft teaching, alternative fairness, authority feel and creative usefulness. Use failure categories rather than a weighted score.

### H4 — Bounded composition semantic dogfood

Use only cases whose frozen H2 F4-style evidence marks at least one losing mechanism `compatible_as_secondary`. Apply an explicit human-authored borrow instruction or clearly labeled fixed research instruction.

Evaluate whether the original primary engine remains governing, the borrowed mechanism stays subordinate, the composition adds useful architecture rather than density for its own sake, and displacement risk is correctly named.

This is semantic plausibility evidence about the composition contract, not live-provider F5 quality.

### H5 — Synthesis and closure

Synthesize repeated patterns across the six cases without reporting a pseudo-statistical success rate. Record supported bounded claims, unresolved risks, concrete prompt/product-contract defects, and whether a later live-provider or human-writer study is worth its cost.

If repeated failures reveal a concrete boundary, open narrow follow-up work rather than broadening the Phase H claim.

## Failure taxonomy

Reuse Phase E categories:

- **CONTEXT / INTENT FAILURE**
- **SEARCH / CHOICE FAILURE**
- **JUDGMENT FAILURE**
- **RATIONALE / SURFACE FAILURE**
- **AUTHORITY UX FAILURE**

Phase H evidence-specific categories:

- **PRODUCER CONTRACT FAILURE** — producer cannot satisfy the semantic/artifact contract without inventing unsupported intent or violating a hard constraint;
- **EVALUATION SEPARATION FAILURE** — producer information materially leaks into the evaluator packet;
- **EVIDENCE CAPTURE FAILURE** — frozen producer/evaluator evidence is missing, mutable or internally inconsistent.

## Hard invariants

1. No Phase H dogfood action automatically calls `story-discovery accept`.
2. Canonical `story_identity.yaml` is never created by the dogfood.
3. Frozen producer evidence is immutable for H3; corrections require a new version/run.
4. Candidate IDs/order/provenance/confidence/contract-fit are not creative-quality signals.
5. F3 near-duplicate/uncertain remains fail-closed.
6. F4 remains derived/noncanonical evidence.
7. F5 remains the only production composition engine; simulated H4 composition cannot be cited as live F5 provider quality.
8. Composition remains candidate-only and must preserve the governing primary engine.
9. No automatic aggregate numeric score or weighted leaderboard substitutes for qualitative adjudication.
10. H2 and H3 are separate approval slices.

## Phase H claim ceiling

The strongest permitted closure claim is:

> On a small representative benchmark, a separated coding-agent producer/evaluator dogfood pass found the Story Discovery semantic contracts capable of producing and evaluating plausible, meaningfully distinct, intent-aware narrative directions while preserving explicit author authority.

Any weaker result must be reported as such. Phase H must never be cited as evidence of live Anthropic/OpenAI quality or human-writer validation.
