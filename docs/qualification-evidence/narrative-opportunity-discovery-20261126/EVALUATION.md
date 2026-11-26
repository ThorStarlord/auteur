# Narrative opportunity discovery: first exercise record (2026-11-26)

One discovery exercise, two arms, one author question, one Architecture. This is initial product evidence. It is not a
benchmark, and it does not show general creative superiority over an unaided coding agent.

## Question and arms

- **Author question (both arms, no hint about any answer):** "What promising creative opportunities am I overlooking?"
- **Specimen:** the Spring Ledger study: 16 continuing open questions, the recorded graph, five genre interactions, the
  Hollow Gate and finale alternatives, and Working Book 24.
- **Arm A, current-state orientation (baseline):** each question's current wording and Book references, without its last
  recorded change, its recorded reason, or Book decision texts.
- **Arm B, grounded orientation (the product path):** the same, plus each question's last recorded change and reason and
  up to two Book decision texts per question, bounded and counted.
- **Isolation:** each arm was its own copy of the same study. Two fresh general-purpose sub-agents (sonnet), one run each,
  each given only its own packet file and asked to write only its own answer file. No provider was called.
- **Completion:** each unedited answer was validated and stored through `complete_architecture_discovery`. The owner
  checked every reference against its own request before storing.

## Attempts

- **Attempt 1 (rejected, kept in `attempt-1-instruction-bounds/`).** Both answers exceeded the length limits, which the
  instruction did not state (A: one field; B: four fields). The owner refused A. The instruction now states every limit,
  and the limits are generated from the model's own constants; a test pins them. Both arms were re-prepared and re-run
  on the corrected instruction.
- **Attempt 2 (the recorded pair).** Both validated. Four possibilities each, all references resolved inside their request.

## Results (attempt 2, unedited)

Shared across the two arms: "A ledger that counts hours…" (overlooked consequence; `q-other-3`, `q-conversion-settlement`,
`q-plurality`) and the cistern-headroom mechanism (`q-surge-route`, `q-other-15`, `q-other-8`). Two independent runs
reached the same recorded tensions, which suggests the record invites them.

| Possibility | Arm A (current state) | Arm B (grounded) |
|---|---|---|
| Ledger hours and care | "makes care auditable": cites `eng_ledger`, `l_tally_counts_hands`, `alt_a_reciprocal`, `str_unmeasured_return` | "could turn the care tally into a count of debt": cites the same plus `dec-plurality` (a Book decision) and `l_conversion_sets_draw` |
| Cistern headroom and the Long Return | shared mechanism, grounded in `str_hollow_gate` and the two release links | pre-pulse headroom, grounded in the same plus `alt_c_ratified_trigger` and `l_declined_goes_wild` |
| The conversion and purchased draw | not found | **found**: whether the Book 20 conversion reaches purchased draw. The record does not say; it cites `dec-compact-settlement` and three links |
| Responsiveness and balance | thematic resonance: intent versus balance, the Old Hand readings (`eng_source`, `eng_old_hand`, `gn_epic_fantasy`) | not found |
| Lowland debt as water | narrative inheritance, labelled speculative | not found |
| Revocation as reform's test | not found | speculative productive tension across `q-right-revocable`, `q-reform-stance`, `q-hesper-motive`, citing `dec-reform-stance`; states that Hesper is not an Architecture node |

Each possibility carries counterevidence, an assumption list where relevant, and a concrete next investigation in both arms.

## Assessment against the mission's criteria

- **Specificity.** Both arms are specific to this narrative. The grounded arm's possibilities cite Book decisions, and
  their uncertainties name particular gaps (Hesper is not an Architecture node).
- **Novelty.** The grounded arm's conversion-and-purchased-draw possibility is a consequence the record leaves open. The
  baseline did not find it. The baseline's responsiveness possibility is also new relative to the grounded arm.
- **Grounding.** Both arms cite only ids that resolve; the owner refused none in attempt 2.
- **Critical judgment.** Both arms state counterevidence. The grounded arm states what it could not establish.
- **Developability.** Each possibility gives a concrete next investigation.
- **Authority.** Each speculative possibility is labelled as such. No possibility claims acceptance.

## What the history contributed, and what it did not

- It contributed Book-decision evidence to three of the grounded arm's four possibilities, and the conversion gap
  depends on a Book decision the baseline never saw.
- The arms differ in two ways at once: recorded reasons and Book decision texts. The exercise cannot separate them, so
  it does not establish how much the reasons alone contributed.
- The grounded arm's answer is no longer than the baseline's (this time), so length is not the difference here.

## Limits, stated plainly

- One run per arm, one model (sonnet sub-agents, not the product's host agent), one specimen, one author question.
- The author question was written by the exercise designer. It is open and names no question, but the designer chose
  the specimen and the question.
- Two of four possibilities converged across arms, which is evidence of robustness, not of novelty.
- No human author has judged either arm. Creative quality is judged here by the designer's reading, not by an
  independent critic.

## Verdict

The grounded orientation produced a possibility the baseline missed, grounded partly in Book decisions, and stated its
limits more explicitly. The result is positive for discovery and for grounding, and inconclusive for general creative
superiority. It does not show that the reasons, as distinct from the Book texts, produced the difference.

## Files

- `request-A-current-state.json`, `request-B-grounded.json`: the prepared requests of attempt 2 (system, user, settings).
- `answer-A-current-state-unedited.json`, `answer-B-grounded-unedited.json`: the unedited answers.
- `result-A-current-state.json`, `result-B-grounded.json`: the owner's stored results.
- `attempt-1-instruction-bounds/`: the rejected first attempt, with its answers and requests.
