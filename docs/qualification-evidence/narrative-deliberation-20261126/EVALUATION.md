# Narrative deliberation: first exercise record (2026-11-26)

One exercise, two arms, one creative question, one Architecture baseline. This is initial product evidence. It is not a
benchmark, and it does not show general superiority across narratives, models or authors.

## What was compared

- **Question (both arms):** three continuing questions of the Spring Ledger study, `q-reform-stance` (12),
  `q-plurality` (13) and `q-gate-table` (14), under one `compare` inquiry. The author question asks whether the questions
  share one problem, whether the Gate Table develops reform and plurality together or warns against one, and whether
  the questions should stay independent.
- **Baseline arm A (current state):** the desk's inquiry as sent with no recorded history
  (`prepare_architecture_inquiry(..., question_history=False)`). The agent sees the working Architecture, the anchors'
  current wording and the recorded graph.
- **Historical arm B (grounded):** the same inquiry with the recorded-history packet attached
  (`deliberation`, schema `studio-question-deliberation/1`). It carries the current wording, the recorded history of each
  question (for `q-gate-table`: introduced at revision 3 and reworded at revision 4, each with its recorded instruction),
  the Book 24 decision for each question with its identity basis, and the co-reference fact that Book 24 refers to all
  three.
- **Isolation:** each arm was prepared in its own copy of the same study, so neither could appear as a prior exchange.
  Both `prior_exchanges` are 0. Each fresh sub-agent received only its own packet file and wrote only its own answer file.
- **Agents:** two fresh general-purpose sub-agents, same model (sonnet), same budget instructions. They are not the
  product's host agent; the answers were completed through `complete_architecture_inquiry`, which validates them and
  retains the evidence.

## Attempt 1 was rejected, and the instruction was corrected

Both agents wrote `source_kind` and `source_id` in `recorded_observations`, because the instruction said "source kind,
id". The owner rejected both answers at validation. This was an instruction defect, not a reasoning failure, and it would
have affected every coding agent answering an inquiry. The instruction now names the exact keys (`kind`, `id`, `claim`)
and the allowed kinds, and a test pins it to the owner's model. Attempt 1 is kept under `attempt-1-instruction-defect/`.
Both arms were then re-prepared on the corrected instruction and re-run.

## Results (attempt 2, the valid pair)

| Criterion | A (current state) | B (historically grounded) |
|---|---|---|
| Specificity to the actual narrative | High. Names the graph links that tie both practices to one outlet (`l_measured_holds_gate`, `l_unmeasured_needs_release`) and the Table's risk (`gi_pastoral_political_gate`). | High. Same graph facts, plus the reword instruction and Book 24's decision text. |
| Source grounding | Observations cite real ids. Interpretation is labelled "not graph proof". | Observations cite real ids and state which parts are recorded and which are interpretation. The analysis is split into RECORDED and INTERPRETATION sections. |
| Historical awareness | None. The packet had no history, so the answer does not mention revisions. | Uses the recorded reason for the reword. States that the reason "says what was asked, not what was achieved". Says the revision-3 identity was matched by the owner, not asserted by the author. Leaves `no_identity_before` unfilled. |
| Recognition of creative tension | Clear: reform and plurality pull apart on the "seat of power" reading. | Clear, and it separates the tension from the Table's wording. |
| Alternatives | Four distinct readings, including independence. Each states gain and cost. | Four distinct readings, including independence. Each states gain and cost, and two of them are tied to Book 24's decisions. |
| Discovery of possibilities | One hopeful single-spine reading, one critical reading, one dependency reading, one independence reading. | Similar set. Adds an order dependency (settle `q-gate-table` first) and frames the Table as the institution changing by hosting its rivals. |
| Counterevidence | Partial. Observes that `q-plurality` names the Table only implicitly, but does not flag the exercise premise. | Explicit. States that the premise "all three name the Gate Table" is not borne out for `q-plurality`, citing its wording and Book 24's decision text. |
| Established vs proposed | Separated by observations vs hypotheses. | Separated by sections, observations, hypotheses, and an explicit list of author decisions. |
| Practical usefulness | Concise, with a clear recommendation and a sensible list of outcomes. | Longer. Ends with the decisions the author still owns. Useful, but heavier to read. |

## Where the history helped, and what enabled it

1. **The premise check.** Arm B separated `q-plurality` from the other two using the Book 24 decision text for that question.
   Only arm B was given decision texts, so this is the evidence that enabled the correction.
2. **The reason boundary.** Arm B separated the author's recorded instruction from any achieved consequence, using the
   revision-4 reason. Arm A had no reason to separate.
3. **The identity basis.** Arm B said each Book decision was matched to its question by the owner from the version it
   names, not asserted by the author. This is the distinction the mission asks the packet to keep visible.
4. **The unfilled gap.** Arm B named the missing pre-identity history and did not fill it in.

## Where the history added noise

- Arm B's analysis is about 50% longer (5,931 characters against 3,835). Much of the added length is labelled scaffolding
  that repeats the observations. The format is heavier, and the extra length does not by itself make the reasoning better.
- Every Book decision's standing came back `current`, so the standing field added no signal in this exercise.
- Arm B hypothesis h2 ("the Table warns against reform from within") depends on reading the Council's passage as the
  revised wording's reform. Arm B flagged that as uncertain. Arm A reached a similar reading without the history.

## Limits, stated plainly

- One exercise, one creative question, one model, one run per arm. Variance is unknown.
- The premise error was mine. The exercise prompt said the three questions "each name the Gate Table, or the stance it
  stands for". `q-plurality` does not name it, and the record shows that. Arm B's correction is therefore evidence of
  careful reading, not a designed trap. I am recording the error here rather than removing it.
- The Book decisions in this study resolve to their questions through the owner, not through an author-asserted identity.
  No decision here records identity itself.
- Creative quality is not clearly separated between the arms. The historical arm improved epistemic discipline and premise
  checking. It did not clearly produce better or more diverse alternatives.
- No human author has judged either answer.

## Verdict

The recorded-history packet improved source discipline and counterevidence attention in this exercise. It was not clearly
better at creative divergence, and it made the answer longer. The result is positive for grounding and inconclusive for
creative quality. It does not establish that historical grounding is generally superior.

## Files

- `request-A-current.json`, `request-B-historical.json`: the prepared requests (system, user, settings) of attempt 2.
- `result-A-current.json`, `result-B-historical.json`: the validated owner results. B carries `deliberation` and
  `deliberation_standing`.
- `prepared.json`: identities, questions, creative question and the two arm projects.
- `attempt-1-instruction-defect/`: the rejected first attempt and its requests.
- `served/`: screenshots from the served journey test, when the test is run with `AUTEUR_DELIBERATION_EVIDENCE` set.
