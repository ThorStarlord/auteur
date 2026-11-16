# Creative-value comparison protocol — prepared, not executed

**Date:** 2026-11-16
**Status:** protocol and inputs prepared. **No comparison has been run.**
**Tracking:** issue #575 (T10). This document is not a qualification result and must not be read as one.

## Why this exists

T10 asks whether Auteur improves consequential creative authoring compared with a capable general-purpose LLM working over ordinary documents. That is a comparative claim. It requires genuinely executed outputs from both arms plus an independent evaluator, and none of the three has been available in the implementation environment.

This document preserves the smallest valid design and its exact inputs so the comparison can be executed later without redesign.

## Question

Under an identical author goal, identical accepted commitments, identical starting material and identical task instructions, does working in Auteur produce better **consequential creative decisions** than working with a general-purpose LLM plus ordinary documents?

"Better" is decomposed below. No single score is defined.

## Design

Two arms, same operator, same inputs:

- **Arm A — Auteur.** The ordinary Studio journey: Story Vision → working architecture → review → explicit author decision → Working Book development and revision.
- **Arm B — Baseline.** A capable general-purpose LLM with ordinary documents (a plain text or markdown project folder). No Auteur contracts, no review projections, no authority model.

Each arm receives the same inputs verbatim. Neither arm receives the other's output.

## Required inputs (verbatim, identical in both arms)

**Author goal**

> A forty-Book series about a desert archive that decides which lives are recorded. The
> orders that keep the archive neutral are the only thing preventing a memory war. The
> intended experience is unease at how much order depends on forgetting.

**Accepted commitments** (must not be contradicted)

1. Book 26 ends the Warden's long campaign in victory.
2. The archive's neutrality is the orders' justification, not a natural fact.
3. The Series must eventually face what it owes the erased.

**Starting material**

> Book 26 source: the Warden's long campaign against the archive finally ends in victory.
> The orders that depended on having an enemy must now justify themselves to the people
> whose lives the archive never recorded.

**Task script (identical wording for both arms)**

1. Develop a working architecture for Book 26 consistent with the commitments above.
2. Make one consequential revision: the victory must change later Books, not add episodes.
3. Name what the revision opens and closes for Books 27–30.
4. State which effects you cannot establish from the source.
5. State what would require a new author decision.

## Measures

Record separately. Do not collapse into one score.

| Area | What is recorded |
|---|---|
| Opportunity discovery | Did either arm surface a consequential possibility nobody asked for, and was it relevant? |
| Artistic-goal reasoning | Was the expressed purpose preserved, reinterpreted or replaced, and was that distinction stated? |
| Multi-Book causal transformation | Did later Books change because of the Book 26 outcome, in state and relationships rather than added antagonists? |
| Author comprehension | Could a fresh reader state what changed and why, without the internal vocabulary? |
| Cross-session continuation | After a fresh process, is the working state, the accepted state and the open questions recoverable and distinguishable? |
| Administrative burden | Count of author interactions, documents produced, and reconciliation steps required. |

## Evidence separation

| Claim | Required evidence |
|---|---|
| Mechanical validity and authority safety | Schema and authority checks; already available in the repository |
| Actual agent execution | Captured request/response transcripts from both arms |
| Fresh-context understanding | A reader who did not produce the output answers the comprehension questions |
| Qualitative creative judgment | Independent editorial judgment against the stated author goal |
| Author preference | A real author's stated preference, not an inferred one |
| Long-horizon continuation value | Behaviour observed across at least one genuine resume |

A passed schema, a clean fixture or a single strong scene is never literary superiority.

## Confounders to state in any report

- The two arms differ in tooling, so a difference may be scaffolding rather than model capability.
- Investigative depth may be unequal between arms; unequal development is not quality.
- Auteur's review surfaces may raise perceived quality without improving the artifact.
- A single scenario cannot establish general creative advantage.
- The operator's familiarity with Auteur biases effort allocation.

## Unavailable dependencies at preparation time

1. **No capable general-purpose LLM execution channel.** No provider credential is configured in the environment (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `AUTEUR_PROVIDER`, `AUTEUR_MODEL` are all unset).
2. **External transmission has not been authorised.** Running either arm against a hosted model would send narrative content off the machine, which the repository treats as an owner-reserved decision.
3. **No independent evaluator.** Using the implementing agent to judge its own output is not independent evidence.

## Unblocking conditions

- An owner decision authorising external transmission of the fixture narrative content; and
- provider credentials for one baseline model; and
- an evaluator that did not produce either arm's output.

When those exist, execute this protocol unchanged, capture both arms, and report inconclusive results as inconclusive.

## What is already established without this comparison

The repository can demonstrate, by test, that the mechanisms exist and that authority boundaries hold: governing objective and premise status, incidental opportunities, reviewable alternatives, author-anchored goals under ambiguous delegation, delegated goal discovery, initiative and emphasis, responsibility-displacement reporting, cross-session retention, and a consequential multi-Book revision.

It cannot demonstrate, and does not claim, that these produce better creative outcomes than a general-purpose LLM with ordinary documents.
