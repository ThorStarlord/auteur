# Development exercise: one discovered possibility, carried through the workflow (2026-11-26)

Possibility `p3` from the grounded arm's answer (see `../EVALUATION.md`): "Does the Book 20 conversion reach the Compact's
purchased draw?", about `q-conversion-settlement`, `q-compact-settlement` and `q-other-1`. It was chosen by the exercise
operator after the answers were read, as the one whose gap the record leaves open. It was not chosen because it fits a
prepared expectation.

## Path, each step through its owner

1. **Discovery** (grounded arm, unedited answer stored by `complete_architecture_discovery`).
2. **Investigation.** `prepare_architecture_inquiry` with `from_discovery` (request `e32c1509…`, possibility `p3`). The
   owner checked that the possibility is transferable and that its three questions are exactly the anchors. A fresh
   sub-agent answered the inquiry; the owner validated and stored it (`answer-deliberation-unedited.json`,
   `result-deliberation.json`).
3. **Alternative.** The inquiry offered four readings (h1 exempt, h2 brought under the conversion, h3 a contrast of
   standing and obligation, h4 keep the questions independent). The operator took **h2 as the framing of the question,
   not as its answer**, and wrote the instruction in `revision-instruction.txt`.
4. **Revision.** `prepare_architecture` with `selected_alternative` (the inquiry and h2). A fresh sub-agent wrote the
   revised candidate (`revised-candidate-unedited.json`). The owner completed it and applied the reviewed working revision.
5. **Review.** Stored in `revision-review.json`: the question changed was `q-conversion-settlement` (reworded, identity
   kept). Scope: considered three, changed one, changed outside none.

## What changed, field by field

- Only `open_questions` changed, and only index 5, the Book 20 conversion question. Identities, nodes (0 of 31) and links
  (0 of 32) are unchanged.
- Before: "Is the Book 20 hands-to-draw conversion a lasting settlement, or a stage the finale must revisit?"
- After: "Does the Book 20 hands-to-draw conversion reach the shares the Mill Compact purchased, or do those shares stay
  outside it? Not decided."

## What the author should weigh (stated, not hidden)

The rewording did what the instruction asked and kept the question's identity, but it also replaced the earlier
"lasting settlement or a stage the finale must revisit" framing rather than adding to it. The owner does not judge
semantic equivalence, so that narrowing is for the author's review, not for the owner's acceptance. The revision is a
working proposal until the author applies it, and it decides nothing about whether the conversion reaches purchased
shares.

## Consequences as the owners now record them

- The question's history reads: introduced at revision 3 (the identity assignment), reworded at revision 4, with the
  revision instruction and the chosen alternative recorded on the second span.
- Book 24's decision about this question (`dec-conversion-settlement`) is now `reworded`, resolved by the Book owner from
  the version it names. The reading says it may warrant reconsideration; it does not say the Book is inconsistent.
- The discovered possibility `p3` now reads `reworded`: formulated against an earlier wording, still transferable, with
  one investigation and an applied revision. Its record is kept; nothing was rebound.

## Limits

- One run each: one sub-agent for the answer and one for the revision, both sonnet, neither the product's host agent.
- The instruction and the choice of alternative were the exercise operator's, written as the author would write them. No
  human author judged the result.
- The result shows that the workflow carries a discovered possibility to a reviewed, applied, traceable change. It does
  not show that the change is the right creative decision.
