# 06. Adjudication of the findings

Status: **working / noncanonical.** Adjudicates every finding in the Stage A report ([stage-a-report.md](review/stage-a-report.md)) and the Stage B report ([stage-b-report.md](review/stage-b-report.md)). It was written after the frozen reviews, the frozen crisis and the traces, so no decision here was made to fit the traces.

**Method.**
1. Each finding's quotations were checked against its packet with [check_quotes.py](evidence/check_quotes.py). Results: [quote-check-stage-a.txt](review/quote-check-stage-a.txt) and [quote-check-stage-b.txt](review/quote-check-stage-b.txt). Stage A: 61 found, 1 split, 8 not found. Stage B: 62 found, 3 split, 5 not found.
2. Each finding was then checked against the source text, and against the traces where the trace bears on it.
3. Classification uses the six categories in the mission. Each accepted defect was assigned an owning level, and the smallest repair was chosen.

**Quotation check, read carefully.** The eight Stage A and five Stage B quotations that were not found are not fabrications of substance. They are one of three things:
- formatting artefacts (bold markers or backticks inside the quoted text, such as "What does not bind.", which the packet bolds);
- the reviewer's own proposed wording, offered in a "what would settle it" line, not a claim about the packet (for example "the gift practice is counted for one window", and "sealed custody is never restored");
- paraphrases placed in quotation marks ("the high terraces [from] surfeit", "hands set draw", "model or warning", "conflicts from earlier successes"). These are the only inaccuracies in the reports, and each finding that relies on one was checked against the source text instead of the paraphrase.

---

## A. Stage A findings (final W2)

| ID | Classification | Owning level | Evidence | Decision |
|---|---|---|---|---|
| R1 | Verified defect (wording) with a credible concern | Whole-Series (finale A) | "Nobody issues a penalty" sits beside a schedule that ties a terrace's release to its labour. Mechanism 1 joins a physical consequence to an institutional rule. A's trace uses no penalty, so the comparison is unaffected. | **Errata E1.** Separate the physical consequence from the schedule rule, and list the rule as a cost of A. |
| R2 | Credible architectural concern | Character and institutional motivation; Whole-Series | The care floor's authority over draw is the Right's holders' consent. The trace shows it: the lineage's agreement is what funds the floor. | **Open author choice** (who holds the floor's authority). Recorded in 05 §3. Errata E2 names the dependence without choosing. |
| R3 | Verified defect (undeclared change to the gift practice) | Whole-Series (finale B) | B does not say whether gift-practice shares are inside the Long Rota. The trace had to decide, and it assigned them. That is a change to the gift practice that the construction did not declare. | **Errata E3.** Declare that the gift practice's shares are inside the window's rota, as a cost of B, and mark it for author confirmation. |
| R4 | Credible concern, realised in the trace | Whole-Series (finale B); Studio representation | The deficit is 19.8 hand-seasons in B. Recording it requires a keeper, and the Reading Hall would be that keeper. The debt ledger returns for one window. | **Errata E3** (same entry) and an open question: who records deficits. |
| R5 | Credible concern | Character and institutional motivation | Short versus refusing is undecided, and the outcomes differ sharply. The trace shows refusal's physical cost being socialised. | **Open author choice.** Not repaired. |
| R6 | Verified defect (cross-artifact: two readers of the gauge) | Whole-Series (finale C) | The Reading Hall reads the threshold in one place, and "the surveyor's reading" decides in another. The surveyor is a Council role, per the original. | **Errata E4.** The Reading Hall's published reading is the threshold reader. The challenge route stays an open author choice. |
| R7 | Credible concern, which the scenario states rather than decides | Physical world mechanism | A threshold needs uncertainty in the surge. W2 gives only a date, and the crisis assumes a range (INV-2). | **Open author choice** (whether the pulse's size is uncertain). The scenario declares its assumption. |
| R8 | **Verified defect** (in W2's Book 15 history, and in 01 §3) | Physical world mechanism (Book 15), with its Book 21 consequence | The original defines surfeit as too much return or stored water with no draw. Release from the cistern draws it down, so it cannot cause surfeit. W2 says it did, and 01 §3 calls a dry spring's release a surplus. | **W3-1** (`str_hollow_gate`): the surfeit's assumed cause is the trial's uncounted return labour. **Errata E5** (01 §1, §3). Not used in the crisis, so no trace changes. |
| R9 | Unresolved question, plus an author reservation | Whole-Series (the Gate's topology) | The two descriptions are compatible. A sluice that divides release also splits the pulse between the cistern and the channels. The real gaps are who ran the Gate before Book 6, and that the Gate's acceptance is not recorded in the candidate. | **W3-5** records the Gate's acceptance as not decided. The question about who ran the Gate before Book 6 stays open. The reviewer's "two topologies" claim is declined as an overreading. |
| R10 | **Verified defect** (cross-artifact in 01 §5) | Multi-Book (Books 20 and 23) | Book 20 repaired the Lowfen, a lower channel. Book 23 cites sealed leaks in the high channels from Book 20. Arc IV never contains that work. | **Errata E6**: drop the leak cause and keep the held water. Not in the candidate. |
| R11 | **Verified defect** (in W2) | Whole-Series (the governing variable); Local Book Structure (str_measured_turn, ph_4) | `str_measured_turn` says "Draw matched to labour" since Book 6, which contradicts `th_hands_and_draw` ("until Book 19 draw follows shares alone"). ph_4 says "for the first time since Book 6". | **W3-2** (`str_measured_turn`) and **W3-2b** (ph_4). |
| R12 | **Verified defect** (undeclared change, in W2) | Character and institutional motivation (the Stone Hall) | The original says "Hall split" in Book 5. W2 says "dissolves", and the summary does not declare the change. The reviewer's closed-futures argument is weaker: the original's closed futures do not require dissolution. | **W3-3** restores "splits", the original's word. A remnant still continues. |
| R13 | Credible concern | Whole-Series (the Compact's draw) | The conversion applies to Lower Ammen's share-holders, but the Compact's unhanded draw is exempt, and no reason is given. | **Open author choice.** Not repaired. |
| R14 | Credible concern | Character motivation (Hesper) | Hesper's cohort holds the belief that abundance needs no work. Her own household was cut. The reviewer reads that as a contradiction. The construction says her cohort "cannot see lineage labour", so the belief is partly explained. | **Open character question.** Not repaired. |
| R15 | **Verified defect** (cross-artifact, finale mapping) | Whole-Series (finale mapping) | The original's adopted Book 30 outcome, shared accounting of care that informs but binds no one, is A. W2's mapping sentence omits it. The original also commits a Compact share-plot settlement while listing the Compact's fate as open. | **W3-4** (`ph_5_unmeasured`). The Compact settlement is recorded as open. |
| R16 | Unsupported claim | Whole-Series (C and B's renewal) | No body is named that can ratify for the valley. | **W3-5** records it as not decided. The trace states its ratification as an assumption (04 C §1). |
| R17 | Credible concern (inherited), plus one verified wording defect | Physical world mechanism; Narrative reasoning method | The tally "holds the high cistern against surfeit", which assigns a physical effect to a record. The gauge's prediction of a dated pulse is an inherited premise. | **W3-2** corrects the wording: the labour holds the cistern, and the tally records it. The gauge's prediction is an inherited author premise and is not changed. |
| R18 | Unresolved questions, and terminology | Narrative reasoning method | "Upper" and "high" cistern are used interchangeably, and the external documents are not in the packet. | **Errata E7** (terminology). The external-document gaps are a packet limit, recorded in 00 §6. |

**Reviewer-level judgment.** The Stage A reviewer found the most consequential defects in W2: R8 (Book 15 physics), R11 (the governing variable), R12 (the Hall), and R15 (the finale mapping). Its finding on the Gate (R9) overreached, and its finding on the tally's physics (R17) was right about the wording and too broad about the inherited prediction.

---

## B. Stage B findings (H1-from-W2)

| ID | Classification | Owning level | Evidence | Decision |
|---|---|---|---|---|
| R1 | **Verified defect** (H1 propagation, undeclared) | Whole-Series (finale payoff); H1 propagation | The script changed the Book 30 payoff from "no single institution holds the record" to "one public keeper" without declaring it. The original and W2 both have the plural-record commitment. | **H1-1.** The finale consequence is declared in the payoff and in the summary, and is marked as reopening an author-reserved commitment. |
| R2 | **Verified defect** (H1 summary contradicts the revision) | H1 propagation | The summary still says Books 1–15 "keep the original's events", after H1 changes them. | **H1-2.** The summary lists the Book 1–15 changes. |
| R3 | **Verified defect** (original closed futures contradicted by H1) | Whole-Series; H1 path | The original's Book 1 and Book 6 closed futures say that sole custody is never restored and that no valley returns to the Hall's custody. H1 gives the committee sole custody in Books 5–15. | **H-E1** (errata for the H1 path): the closed futures are H1 consequences, declared as such. Not a candidate change beyond H1-2. |
| R4 | Unresolved question, with a credible concern | H1 story; author | What Dorran does in Book 1, and how Idrun's Book 1 closure survives, is not specified. | **Open author choice.** H1-2 records that the transfer's cause and Dorran's status are not yet specified. |
| R5 | Unsupported claim | H1 story; Multi-Book (custody) | The Book 15 transfer has no cause, and the order of events is circular. | **Open author choice.** Recorded in H1-2 and H1-3. |
| R6 | Credible concern | H1 story | Share authority in Books 5–15 is unassigned, and no guard against falsification is named. | **Open.** Not repaired. |
| R7 | Credible concern | H1 story (the readings) | The Book 8 and Book 12 readings are underspecified under committee custody. | **Open.** Not repaired. |
| R8 | Credible concern | H1 story (the open question) | Open question 15 is aimed at the Hall's future opposition, which is not the H1 question. | **H1-3.** The question is rewritten around the Book 15 transfer and the Reading Hall's custody. |
| R9 | Unresolved question | Author sanction | File 08 adds the custody-until-Book-15 structure, which file 07 does not contain. | **H1-2** states this in the header, and asks the author to confirm. |
| R10 | Unresolved question | H1 story (character and institution) | The bittersweet emotion's "custody" applies to a record, not a practice. | **Open.** Not repaired. |
| R11 | Unsupported claim | H1 story (thinning) | Falsified credit is said to cause a thinning, with no mechanism. | **Open.** Not repaired. |
| R12 | Minor | H1 story | The Book 5 timing and the word "from outside" are imprecise. | **Declined as a repair.** The wording is the instruction's, and the author may keep it. Recorded. |
| R13 | Minor | H1 story | The remnant's placement and the wording of the custody link. | **Declined as a repair.** Recorded. |
| R14 | Deliberate author choice | Whole-Series (reform stance) | Reform from within is the stance the author has reserved. | **Not decided.** |

**Reviewer-level judgment.** The Stage B reviewer's central result is sound. Its findings on the H1 propagation (R1, R2, R3) are verified, and the revision does not close them. Its preserved-element table is useful. Its finding that the bittersweet emotion is unclear (R10) is correct, and it is left open.

---

## C. Corrections decided

**W3 (the final candidate, corrected).** Field-level changes to W2, each with its stated defect, recorded in [w3-changes.md](corrections/w3-changes.md):
- **W3-1** `str_hollow_gate.summary`: Book 15 surfeit (R8).
- **W3-2** `str_measured_turn.summary`: labour matched to shares, and the tally's wording (R11, R17).
- **W3-2b** `ph_4_settled_water.narrative_function`: "for the first time in the series" (R11).
- **W3-3** `inst_stone_hall.summary`: "splits", as the original has it (R12).
- **W3-4** `ph_5_unmeasured.narrative_function`: the original's adopted outcome is A, and the Compact's settlement is open (R15).
- **W3-5** `summary`: the Gate's acceptance and the ratifying body are recorded as not decided (R9, R16).

**H1 (corrected, derived from W3).** H1-1 through H1-3, as above, applied by [make_w3_and_h1v2.py](evidence/make_w3_and_h1v2.py) after the recorded script has derived H1 from W3.

**Errata (prose, not changed in the PR #553 files)**, in [errata.md](corrections/errata.md): E1 to E7, and H-E1.

**Why these and not others.** Each W3 change is the smallest edit that removes a verified contradiction, and none adds a mechanism. The errata are in prose because the prose is part of PR #553, which this work must not rewrite.

---

## D. Earlier claims, tested by the new evidence

| Earlier claim (PR #553) | New evidence | Status |
|---|---|---|
| Arc IV is sufficient as causal scaffolding. | The crisis's conditions (hands, the Right, the Table, the declined share) are all supplied by Arc IV. The Book 15 physics (R8) and the hands-first claim (R11) were wrong. | **Supported for the crisis's needs; two errors corrected.** |
| Book 23's abundance has a mechanism (sealed leaks). | Book 20 repaired the Lowfen only (R10). | **Partly wrong.** Errata E6. |
| C is the working direction, and reviewers could not break it. | C's advantage over B is narrow: about 0.05 CU of capacity and 0.04 CU of surfeit. Its success depends on a ratifying body and a Compact clause that are not established (R16). | **Narrowed.** The review's failure to break C was a limit of its scope. |
| The Book 30 alternatives are materially different. | A and B/C differ in who bears the cost. B and C differ in process, deficit and timing, not in the water. | **Partly supported.** |
| The product's preserved check compares identifiers only. | It compares whole entries for equality (00 §5). | **Corrected** (00 §5). |
| Applied candidates equal their authored files, and the product reports the changes. | True. But the product did not detect R8, R11, R12 or R15, because they are contradictions of meaning. | **Supported for structure; not for meaning.** |
| The corrections were not re-reviewed. | The corrections are now reviewed, in finding-specific form (Stage F). | **Closed by Stage F.** |
| Care without debt is weakened most. | A keeps "nothing owed" but leaves the orchard's loss unassigned. B re-admits debt, and needs a record. C's deficit is a third of B's. | **Confirmed**, and the mechanism is now shown. |
| Lowland obligations are weakened. | The Compact's labour is owed under B and C, but the Harrow Lowe gate is outside every binding clause. | **Confirmed, and extended** to the gate. |
| The Hollow Gate addition is modest. | Every trace depends on it. Its physics is modest, its function is not. | **Qualified.** |

---

## E. Open items (for the author, not for the agent)

1. Whether the Compact's grain-labour is owed (B, C) or voluntary (A), and whether the Compact has a seat.
2. Whether the Harrow Lowe gate is part of the world. It is inherited from the original and absent from W2.
3. The high cistern's storage: whether it can take 0.6 to 0.65 CU above tolerance. The architecture does not bound it, and both B and C depend on it.
4. Whether gift-practice shares are inside the window's rota (B).
5. Who records deficits, and whether a record that re-admits debt is accepted (B, C).
6. Who holds the floor's authority over draw (A).
7. Who ratifies the instrument (C), and whether the threshold is read by the Reading Hall alone.
8. Whether the pulse's size is uncertain, which C's threshold requires.
9. H1 only: what causes the Book 15 transfer, what Dorran does in Book 1, and whether the file 08 additions are sanctioned.

---

## F. Verification of corrections, and the stopping rule

Each candidate change was verified by one fresh reviewer, on the changed text and the text it refers to, and the verification results are recorded verbatim in `review/`.

| Round | Candidate chain | Verification | Result |
|---|---|---|---|
| 1 | W2 to W3; H1-from-W2 to H1v2 | [stage-f-report.md](review/stage-f-report.md) (Stage F) | Of 15 items, 10 fixed and 4 partly fixed. One new defect, caused by erratum E3. |
| 2 | W3 to W4; H1v2 to H1v3 | [stage-f2-report.md](review/stage-f2-report.md) (Stage F2) | Of 8 items, 6 fixed (two of them, F-3 and F-7, with new defects attached) and 2 partly fixed. New defect ND-1 (the surfeit logic): W4-1 said surfeit is too much return, while W4-2 said labour holds it off. The H1 path also reintroduced "upper cistern". One erratum's text was lost to a cleanup step, so it was not checked. |
| 3 | W4 to W5; H1v3 to H1v4 | [stage-f3-report.md](review/stage-f3-report.md) (Stage F3) | Fixed 3 of 5. Two new minor defects, recorded as open below. The stopping rule applies from here. |

**Final candidate chain.** W2 (PR #553) is unchanged. W3, W4 and W5 are the successive corrected candidates, and each is kept. The H1 path follows the same chain: H1-from-W2, then H1v2, H1v3 and H1v4. The final candidate is **W5** (`corrections/05-working-candidate-v5.json`). The final H1 path is **H1v4** (`corrections/11-h1v4-from-w5.json`). Both pass the product's schema.

**Stopping rule.** Each round has surfaced a defect in the previous round's wording. The mission does not allow unlimited review-and-repair cycles, so round 3 is the last round of candidate changes, and no further change is verified. The residual items below are open.

### Residual open items after round 3

Each item is recorded with its proposed fix, which is not applied and not verified.

- **R-a. Mechanism 1's heading in 04 (Alternative A) still reads "Gate dependence".** The mechanism's body no longer mentions the Gate. Proposed: rename the heading to "Physical dependence of the channels" (Stage F3, ND-2).
- **R-b. E7's locations are wrong.** E7 cites "Books 1 and 6 and … the Book 6 closed future". The closed future does not contain the term. The uses are Book 1 enabled futures ("the first recorded thinning of the upper cistern"), Book 6 conflict ("The upper cistern thins"), and 02 §3.2 ("Consequence: the upper cistern thins"). Proposed: cite those three locations instead (Stage F3, E7).
- **R-c. E8's description.** The round-3 change record says E8 "asserted the same claim through labour". The prose it replaces does not mention labour, so the description is slightly wrong. The erratum itself is correct (Stage F3, observation 3).
- **R-d. The 1000-character cap.** W5-3 is exactly 1000 characters. The product's own validation passed it, so the cap is inclusive and the field is valid. Recorded here so the figure is not mistaken for a failure.
- **R-e. The original's Compact settlement.** The original both commits a share-plot settlement in its Book 30 closure and lists the Compact's fate as open. W5-3 says "committed there; open here". Which reading holds is the author's to decide (Stage F3, observation 1).
- **R-f. The surfeit mechanism (W4-1, errata E5).** It is a construction assumption that the original does not name. The candidate and the prose both say the author may reject it.

### Corrections that were proposed and not applied

- The Stage A R9 proposal to "fix the topology" (deep store, cistern, Gate, channels, with who ran the Gate before Book 6). The topology is consistent as written, and the missing piece is a fact the author must supply. Not applied.
- The Stage A R13 proposal to add a reason for exempting the Compact's draw from the conversion. This is a choice the author makes. Not applied.
- The Stage A R16 proposal to name a ratifying assembly. This is an author decision, and the candidate records it as not decided (W3-5). Not applied.
- The Stage B R4–R7 and R10–R11 items (Dorran, the custody transfer's cause, share authority, the Book 8 and 12 readings, the bittersweet referent, the thinning mechanism). These are H1 story questions for the author. H1v4 records the transfer's cause and Dorran's status as unspecified. Not applied.
