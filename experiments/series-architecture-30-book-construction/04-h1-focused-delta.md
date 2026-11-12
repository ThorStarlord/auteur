# 04 — H1 focused delta (hypothetical; not accepted)

Status: **hypothetical, author-proposed counterfactual, not accepted.** It is a focused delta on the working construction ([03-working-candidate-v2.json](03-working-candidate-v2.json)). It is not a second complete candidate. Nothing here changes the original experiment (PR #551), the fixed brief, or any accepted artifact. The H1 path is produced by `evidence/make_h1_path.py` and was applied in canvas `h1final` (run record in `evidence/product/`).

---

## 1. The premise

In Book 5 the Stone Hall's own head, Keeper Anselm Corrow, opens the records to **public access**, as a reform that protects the Hall's standing against a thinning its own falsified credit helped cause. A lower-terrace household's **evidence forces the timing**. The reform committee keeps **physical custody** of the Stones and the master record, and keeps the **debt reading**, until Book 15. At Book 15 custody passes to the **Reading Hall**, and the debt-keeping members become Corrow's **remnant**, which stands outside the Gate Table. The Hall is reformed, not destroyed.

H1 does not change the Source, the three loops, the Arc II trade mechanism, the Book 15 gift reading, the Unmeasured Return, Arc IV's two conflicts, or the finale's three mechanisms. It changes who opens the records, who keeps custody and when, and when the remnant forms.

## 2. Baseline correction: the original premise is not seizure

The counterfactual's first assumption (C-revision-delta §2, A1) says Idrun's Arc I agency "is seizure (tenders force the Hall)". That baseline is not in the original. The original's Book 1 closes through proof and coalition:

- `A-studio-candidate-original.json`, `ph_1`: "Protagonist's agency comes from evidence and a coalition, not inheritance."
- `A-original-architecture.md` §5, Book 1: "Idrun and Dorran Vesk read the Stone by lamp and sounding, prove the false credit, and restore the lower channel."

The word "seizure" appears only in the counterfactual's own delta (its §2 and §8). The corrected contrast is:

- **Original path:** evidence and an outside coalition force the Hall to yield (Book 5).
- **H1 path:** the same kind of evidence forces the *timing* of the Hall's own reform (Book 5). The change is who acts, not whether evidence is the lever.

Neither W2 nor the H1 path contains the word "seizure". A blind host run did reintroduce it (see [06](06-validation-and-review.md) §4).

## 3. The focused delta (what the script changes)

Every change is made by `make_h1_path.py` on the working candidate, and every replaced field is asserted to exist first.

| Element | Change under H1 |
|---|---|
| Summary | Prefixed with a labelled hypothetical premise. The W2 summary follows unchanged. |
| `inst_stone_hall` | Retitled "reform committee; remnant from Book 15". Summary: public access (Book 5), committee custody and debt reading (to Book 15), remnant from Book 15. |
| `inst_reading_hall` | Summary: founded at Book 15 with the full reading; takes physical custody of the Stones and the master record at Book 15; publishes the Gate gauge and the Balance Stones; no authority over the schedule. |
| `th_custody` | Summary separates public access (from Book 5) from physical custody (committee to Book 15, then the Reading Hall). |
| `eng_ledger` | "opened to public access by the Hall's own reform once evidence forces it (Book 5)". |
| `th_witness` (added) | "A lower-terrace household's evidence forces the timing of the Hall's own reform (Book 5). In the original path the same evidence, with a coalition from outside, forces the Hall to yield." |
| Links (added) | `l_witness_forces_reform`; `l_reform_keeps_debt` (until Book 15); `l_custody_passes_reading_hall` (at Book 15). |
| `l_custody_grants_hall` | Function changed from "until Book 5" (original path) to "until Book 15". |
| `ph_1` | Narrative: the reform protects the Hall against "a thinning its own falsified credit helped cause", and the committee keeps custody. Transition and the `gn_mystery_discovery` activation updated. |
| `ph_2` | Narrative and the `gn_political_institutional` activation: the committee's sale rules, and the committee's authorship of the first partial reading of the script (Book 8). |
| `ph_3` | Narrative: the committee's custody ends with the full reading, and the debt-keepers form the remnant. "The Book 12 partial reading is made under the committee's custody." Transition: "Custody passes to the Reading Hall at Book 15, so the record has one public keeper while the readings stay plural." Activation: the remnant forms at Book 15, not before. |
| `ph_4` | Appends: the remnant "stands outside the Gate Table and argues for counting" (not a seat). |
| `et_grief_of_orders` | Eliciting condition re-pointed from "the Stone Hall's fall in Book 5" to "the committee's loss of custody at Book 15 and Keeper Corrow's remnant's dissent". The intended effect is unchanged. |
| `ce_bittersweet_return` | Context: "a practice honoured after the institution that held it has lost custody of it". |
| `gn_political_institutional` | Payoffs: "the Stone Hall's monopoly of access ends in Book 5; its monopoly of custody ends in Book 15", and "in Book 30 the record has one public keeper, and no single body holds both the record and the Gate schedule". |
| `open_questions[14]` | Rewritten to state the H1 question: whether reform from within stays credible under Books 15 and 30, and whether the Gate Table models or warns against it. The list stays at sixteen. |

Unchanged in H1: the other nodes and links of W2, the phase fields not named above, the emotion targets not named above (including the anger target, see §4), and the complex emotion `ce_awe_of_source`.

## 4. Corrections, and how H1 handles each

**From the PR #552 review.** Findings 15–19, 21, 22 and 24 are handled as before. The grief target and the bittersweet context are re-pointed to custody. The remnant forms at Book 15. Access and custody are separated. The seizure baseline is corrected in §2. Revision status is removed from `th_witness`, but the H1 summary keeps a hypothetical label, because the product copies the rationale from the summary ([05](05-consistency-record.md) B9). The "falsified record" trope stays in the political contract.

**From the semantic review of the first H1 derivation.** Corrected in this version:
- The custody link carries a Book 15 bound (it said "until Book 5" in W2).
- The Reading Hall's node no longer says it was founded after custody passes; it takes custody at Book 15.
- Custody is one public keeper from Book 15, not "plural".
- The remnant stands outside the Gate Table and does not hold a seat or a voice inside it.
- The Book 12 reader is named: the committee's custody.
- The reform's motive names the thinning its own credit helped cause.
- The bittersweet context no longer implies a voluntary handover.
- The Book 30 payoff is restated with one public keeper.

Not adopted, with the reason in [06](06-validation-and-review.md) §3: the reader-experience line for Arc I (it would reintroduce the mixed anger register), the witness's name (a household, not a character), and separate open-question entries (the list is capped at sixteen, so the H1 question is merged into one entry).

**The anger target is not changed in H1.** R-A changed `et_anger_at_hidden_credit` to "unease" at the reform, which gave one label two emotions. H1 keeps the Book 1 anger and carries the reform's cost in the grief target and the consequential-loss reader experience. A reviewer may challenge this.

## 5. What H1 changes for Arc IV and the finale

- **Arc IV:** the Book 15 remnant argues for counting from outside the Gate Table. This makes the Table more contested. It does not change Conflict A.
- **Book 30:** H1 supplies an earlier example of institutional self-correction. The finale's distinctiveness rests more on the cost of counting. [02](02-finale-alternatives.md) is not changed by H1, except that the record's keeper is now public from Book 15.

## 6. What H1 does not decide

- Whether reform from within is the series' stance, or a stage the finale must oppose. This is an author choice and stays open.
- Whether a committee that holds custody until the reading of Book 15 is credible, given that the Reading Hall takes custody in the same Book.
- The medium of record. The original candidate (PR #551) says in `ph_1` that "Book 1 gives the first partial reading of the First Stones", while `A-original-architecture.md` §3.3 and §6 place the partial readings in Books 8 and 12. Its `inst_stone_hall` says the Hall "dissolves in Book 5". None of these files is changed. [05](05-consistency-record.md) records this.

## 7. Reproduction

```bash
python experiments/series-architecture-30-book-construction/evidence/make_h1_path.py \
  experiments/series-architecture-30-book-construction/03-working-candidate-v2.json \
  <scratch>/h1-from-w2.json
```

The output is validated against `ArchitectureCandidate` (schema 2) and applied as a revision to canvas `h1final` using `evidence/instruction-h1.txt`. Hashes are in [06](06-validation-and-review.md) §1.
