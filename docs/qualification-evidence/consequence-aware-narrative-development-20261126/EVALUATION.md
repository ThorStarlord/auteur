# Consequence-aware narrative development: exercise evidence (2026-11-26)

Design: [`../../design/2026-11-26-consequence-aware-narrative-development.md`](../../design/2026-11-26-consequence-aware-narrative-development.md).
Driver: `scripts/consequence_exercise.py`. Every answer below is a reasoning agent's unedited output, completed through its
owner. No provider was called. Each reasoning agent was a fresh general-purpose sub-agent on the sonnet model, given only its
own request file, with no hint about the expected conclusion. They are not the product's host agent; PR #645 disclosed the same.

Each folder that holds a superseded attempt says why it was superseded. Accepted results are the top-level `result-*.json`.

## Exercise A: the motivating case (PR #645 Book 20 conversion)

The reconstruction replays PR #645's recorded inputs (the grounded-arm discovery answer, the p3 deliberation answer, the h2
instruction and the revised candidate) and stops before Apply. The pending proposal matches the PR #645 review: one question
reworded (`q-conversion-settlement`, identity kept), origin p3, no component changes.

Two arms examine that same proposal, each in its own study copy:

| Arm | Capability | Attempts | Accepted result |
|---|---|---|---|
| 1, ordinary assistance | pending-review inquiry (`explain`, `target: pending_review`) | 2 | attempt 2 (`result-explain.json`) |
| 2, consequence-aware | consequence analysis of the pending review | 3 | attempt 3 (`result-consequence.json`) |

Refusals and superseded attempts, classified:

- **Arm 1, attempt 1: compliance failure.** Nine recorded observations against a stated limit of eight. The limit was not
  relaxed. Attempt 2 used the unchanged request and was accepted (`attempt-1-refused/`).
- **Arm 2, attempt 1: instruction defect.** The owner enforces a citation rule for each status that the instruction did not
  state. The rule is now stated and pinned by a test (`attempt-1-refused/`).
- **Arm 2, attempt 2: superseded by a packet fix.** The packet dropped every recorded reason, so the author's instruction behind
  the earlier identity introduction never reached the agent. The fix changed the evidence, so attempt 2 was re-run on the
  corrected packet (`attempt-2-superseded-by-packet-fix/`). Its answer was not discarded: it is a real reading of the earlier
  packet.

### What the arms found (accepted attempts)

Both arms found the central displacement. The settlement question "lasting settlement, or a stage the finale must revisit"
no longer has its own wording. Both declined to call that a mistake, both found the new reach question, and both noted the
author's intent is not recorded.

Found by both:
- The durability concern may be displaced, and the record does not show whether dropping it was meant.
- The reach question is new, and the proposal records no answer.
- The Compact question overlaps the reworded question.

Found only by the existing inquiry arm:
- Recorded mechanisms as reasoning material: it reasoned through the recorded links (`l_conversion_sets_draw`,
  `l_trade_draws_without_return`, `l_compact_hands_in_kind`) and named the nearest remaining carrier of the displaced concern
  (`q-finale-mechanism`). The consequence packet cannot cite links, so the consequence arm did not do this.
- It does not state the relationship to Book 24's decision.

Found only by the consequence arm (attempt 3):
- It separates two things the inquiry merges. The reworded question keeps its identity, and its focus moves from durability to
  scope. That is a transformation. The durability concern, which the wording no longer carries, is a possible displacement, with
  its intent not established.
- A recorded relationship to Book 24's decision, stated as a relationship by identity, not as a contradiction. Book 25 is named
  as listed by title only.
- Intent basis and counterevidence per concern. The counterevidence it gives is specific: E9 does not say the durability question
  is dropped.
- Four alternatives (retain, separate, integrate, reframe), each with gains and costs.

Weaknesses recorded, not repaired here:
- The consequence arm does not develop the finale link as far as the inquiry arm.
- Its alternatives use "retain" for keeping the baseline wording, and the approach names are not defined in the instruction.

Reading: the central displacement was available through the existing pending-review inquiry. What the new capability adds is the
recorded Book relationship, the transformation-versus-displacement distinction, and alternatives that can be investigated.
It does not yet add the mechanism-level reasoning the inquiry does.

## Exercise B: a deliberate retirement (contrasting case, same specimen)

The author's instruction retires `q-conversion-settlement`. A fresh agent wrote the candidate, which the owner accepted; the
proposal stayed pending. The removal is the conversion identity, and the other fifteen questions moved one place.

- **Attempt 1: packet defect, not a reasoning result** (`attempt-1-packet-defect/`). Position-only shifts filled the four
  examined slots, so the removed question was never examined, and the agent reported no concern from a packet that did not
  show it. Fixed in `build_consequence_packet` (removals and rewordings are examined first; position-only moves are not), and
  pinned by `test_a_removed_question_is_examined_before_the_positions_its_removal_shifts`.
- **Attempt 2: superseded by the recorded-reason fix** (`attempt-2-superseded-by-packet-fix/`). Same reason as Exercise A's
  attempt 2: the removal's packet lacked the recorded reasons.
- **Attempt 3 (accepted, `result-consequence.json`)**, on the final packet:
  - "Whether the Book 20 conversion is revisited in the finale": `possibly_displaced`, intent `instruction_names_it`. The
    record does not say whether the author means the conversion is settled or not wanted.
  - "The conversion remains part of the Series": `preserved`. The phase still records the conversion as an event.
  - "The finale still chooses who gives labour": `preserved`. The retirement does not touch the finale choice.
  - Recorded relationship: Book 24's decision is recorded against the retired question by identity.
  - Alternatives: retain (keep the retirement as instructed), reframe (carry the revisit concern inside the finale question),
    defer (until Book 25 is read). The retain label is again the naming gap, since the instruction keeps the retirement rather
    than the earlier concern.
  - Not established: why the author retired it, settled or irrelevant, Book 25's decisions, whether Book 24 needs a change.

Reading: with a deliberate retirement the analysis still reports the displacement and the recorded Book relationship, grounds
the displacement in the instruction, and does not call it a mistake. Its alternatives are weaker than Exercise A's.

## Verification of the recorded evidence

- Exercise A's accepted consequence packet was built on the final owner code; the attempt-2 packet is archived and differs
  only in the recorded reason on the identity introduction (checked as JSON).
- The served review panel was captured on the accepted Exercise A analysis (attempt 3) at 1440 px and 390 px, with no horizontal
  overflow at either width (`served/`).

## Limits

- One accepted run per arm and per exercise. Refused and superseded attempts are kept and classified above. The arms are compared
  on their accepted attempts.
- The consequence arm and the inquiry arm had different instructions. The consequence arm's instruction was repaired after its
  first refusal. The inquiry arm's instruction is the product's current one, unchanged.
- Mechanism evidence: the packet cannot cite recorded links or nodes. The consequence arm therefore did not reason through recorded
  mechanisms the way the inquiry arm did. This is the principal gap; the next build should make recorded mechanisms citable,
  selected for relevance rather than listed in full.
- The approach names are undefined in the instruction, and "retain" was used for a retirement in both exercises.
- Exercise B is an operator-authored instruction on the same specimen, not a second independent narrative.
- No human author judged the results. The judgements above are the designer's reading of the stored text.
