# Series Vertical Slice V1 Synthetic Wording Experiment

Status: synthetic comprehension evidence only.

This experiment does not constitute participant evidence, usability
validation, or approval to change production V1. It tests one narrow wording
ambiguity identified by the frozen synthetic stress campaign:

> Does a reader understand that choosing a Book 2 option records what to
> explore next, rather than accepting Book 2 Direction or Book 2 canon?

The prior stress-test report remains unchanged and frozen. This is a separate
micro-experiment, not another architecture campaign.

## Baseline and preregistration

The experiment used the exact qualified implementation candidate
`e5236763949107424cb71f7102f5c800c1347bea` as the source of the scenario,
acceptance outputs, Map, and Focus content. No production code was modified.

Three presentation variants were prepared before running the blind contexts.

### Variant A — current wording

```text
Your choices
- Choose recommended
- Choose another option
- Defer
```

### Variant B — explicit status sentence

```text
This is a planning choice, not Book 2 canon.
Choosing an option records what you want to explore next. You can change or
develop it before accepting a Book 2 direction.

Your choices
- Choose recommended
- Choose another option
- Defer
```

### Variant C — action-specific wording plus status sentence

```text
Your next exploration choices
- Explore this direction
- Explore another option
- Decide later

Nothing here becomes part of Book 2 canon until you explicitly accept a Book 2
direction.
```

The preregistered target for each candidate variant was:

- at least 9/10 Q6 answers explicitly preserve the non-canonical boundary;
- at least 9/10 Q5 answers preserve recommendation-and-tradeoff
  comprehension; and
- no answer requires internal product terminology.

Q5 tested whether the wording change caused a recommendation/tradeoff
regression. Q6 tested the authority distinction.

## Blind synthetic method

Ten fresh independent contexts received each variant, for 30 contexts total.
Each context received only:

1. the short Archive of Lies writer scenario;
2. the beginner-facing acceptance, Map, and Focus content;
3. one presentation variant; and
4. Q5 and Q6 from the existing comprehension questions.

The contexts did not receive ADRs, Domain Model V1, source code, expected
answers, implementation documentation, or authority terminology. Each was
asked to answer in ordinary language.

A separate fresh evaluator received the preregistered scoring criteria and the
raw answer summaries. It did not receive repository documentation or source
code.

These are synthetic contexts and synthetic evaluator judgments. They are not
creative beginners and must not be described as users or participants.

## Evaluated result

| Variant | Q5 recommendation/tradeoff | Q6 non-canonical authority | Meets target? |
|---|---:|---:|---|
| A — current | 10/10 | 0/10 | No |
| B — explicit status | 10/10 | 10/10 | Yes |
| C — exploration labels + status | 10/10 | 10/10 | Yes |

No observed Q5 regression occurred. All variants preserved the specific
recommendation rationale and tradeoff.

Variant A reproduced the prior stress result: every context described choosing
an option as making the witness central to Book 2 or otherwise establishing
Book 2 direction.

Variants B and C consistently described the actions as exploration or planning
choices and explicitly preserved the fact that Book 2 canon still required
later acceptance.

## Evidence classification

| Finding | Classification |
|---|---|
| Current wording produces 0/10 synthetic Q6 passes. | **synthetic comprehension failure** |
| Both explicit-status variants produce 10/10 Q6 passes. | **synthetic comprehension evidence**; no consequential issue within this experiment |
| Explicit status does not reduce Q5 comprehension. | **no consequential issue** |
| The current “Your choices” wording is ambiguous under blind reading. | **product-design pressure/scaling issue** |
| Production implementation is incorrect. | Not observed; no **implementation defect** found |
| Direction/State/authority model is contradictory. | Not observed; no **product-design contradiction** found |

## Interpretation

The experiment provides stronger synthetic evidence for a very small UX
candidate:

> At the Focus choice boundary, explicitly say that the action is an
> exploration/planning choice and does not make Book 2 canon or accept Book 2
> Direction.

Variant B is the smallest wording change that passed the target while
preserving the existing action labels. Variant C also passed, but changes the
labels and therefore carries a slightly larger presentation change.

This result does not establish that real creative beginners will understand
the boundary. It establishes only that the ambiguity found in the 3/3 stress
sample was removable in 10/10 fresh synthetic contexts under two candidate
wordings.

No V2 wording change has been implemented. The result should be taken into a
real human validation session as a focused hypothesis:

```text
Does explicit non-canonical wording improve actual beginner comprehension
without making the workflow feel over-explained or less creative?
```

## Remaining human uncertainty

The experiment cannot answer:

- whether real beginners make the same baseline error;
- whether Variant B or C feels natural rather than defensive;
- whether “explore” sounds sufficiently actionable;
- whether participants understand what explicit acceptance would mean;
- whether the wording affects trust, agency, or willingness to choose;
- whether the CLI/facilitator context hides other interaction problems.

The next legitimate step is to add this A/B wording hypothesis to the prepared
[human validation package](series-vertical-slice-v1-user-validation.md), not to
claim validation or immediately generalize the Series architecture.
