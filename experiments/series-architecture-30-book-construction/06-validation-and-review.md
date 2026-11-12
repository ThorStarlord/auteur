# 06 — Validation, independent review, and adjudication

Status: **working / noncanonical.** This record separates four kinds of claim, because the mission asks for them separately:

- **Mechanical validation:** the schema and the Studio operations accepted the artifacts. This is not a judgment of quality.
- **Independent critique:** two fresh-context reviewers and one blind host run, verbatim in `review/`, and how each finding was adjudicated.
- **Coherent working construction:** the candidates and mechanisms in [01](01-causal-construction.md)–[05](05-consistency-record.md). They are internally consistent by our reading, and they are not yet tested in prose.
- **Author acceptance:** none. Nothing here is accepted.

---

## 1. Mechanical validation

| Check | Artifact | Result |
|---|---|---|
| Strict schema v2 (`ArchitectureCandidate`) | W1 `03-working-candidate.json` (reviewed; kept as evidence) | Valid. 32 nodes, 34 links, 5 phases, 7 emotion targets, 16 open questions. sha256 `718c2763…`. |
| Strict schema v2 | **W2 `03-working-candidate-v2.json` (final working candidate)** | Valid. 32 nodes, 34 links, 5 phases, 7 emotion targets, 16 open questions, summary 1,575 characters. sha256 `0fbf5c9c…`. |
| Strict schema v2 | H1 derived from W1 (`h1v1`) | Valid. 33 nodes, 37 links, 16 open questions. sha256 `5ea399e4…`. |
| Strict schema v2 | H1 derived from W2 (`h1final`, **final H1 path**) | Valid. 33 nodes, 37 links, 16 open questions, summary 2,013 characters. sha256 `face0464…`. |
| Studio host-response acceptance (`complete-file`) | W1 (canvas `w1`) | `review_ready`. |
| Studio host-response acceptance | W2 as a revision of W1 (canvas `w1`) | `review_ready`. 8 components changed. |
| Studio host-response acceptance | H1 from W1 (`h1v1`); H1 from W2 (`h1final`) | `review_ready` both. 15 and 17 components changed respectively. |
| Studio host-response acceptance | Blind host response (canvas `blindtest`) | **Refused.** `genre_contracts.3.role`: "background" is not a genre-contract role (`governing`, `supporting`, `tertiary`, `local`). Nothing applied. |
| Baseline acceptance | PR #551 original (sha256 `a78ce7d5…`) for canvases `w1` and `blindtest`; W1 for `h1v1`; W2 for `h1final` | `ready` each time. |
| Applied revisions (`apply_architecture_review`) | canvases `w1` (W1, then W2), `h1v1` (H1 from W1), `h1final` (H1 from W2) | Applied. Each applied candidate equals its authored file after normalisation through `ArchitectureCandidate`. Checked for W2 and H1-from-W2 (`w1`, `h1final`) and for W1 and H1-from-W1 (`w1`, `h1v1`). |
| Intentions | all canvases | Four author-fixed intentions recorded as `active`, copied from PR #551's `intention-1..4`. |
| Re-entry packet (`resume`) | canvas `w1`, after W1 apply | Produced. 57,756 characters, against about 43,000 in PR #551. |
| Pending review after apply | canvas `w1` | None. |

**What these checks do not show.** They confirm structure, freshness and identity. They do not show that the Arc IV conflicts are good drama, that the finale mechanisms work, or that the candidate reads well. Two gaps are inherited from the product and not closed here: the bridge has no `apply` command, and the `preserved` check compares identifiers only.

### 1.1 What the product's own review reported

| Revision | Changed components | Preserved |
|---|---|---|
| W1 against the PR #551 original | 58 (summary 1, node 24, link 18, phase 5, emotion target 6, genre contract 3, genre interaction 1) | nodes 8, links 16, emotion targets 1, complex emotions 2, genre contracts 1, genre interactions 4 |
| W2 against W1 | 8 (summary 1, node 4, link 2, genre contract 1) | nodes 28, links 32, phases 5, emotion targets 7, complex emotions 2, genre contracts 3, genre interactions 5 |
| H1 from W1 (`h1v1`) | 15 | nodes 29, links 34, phases 1, emotion targets 6, complex emotions 1, genre contracts 3, genre interactions 5 |
| H1 from W2 (`h1final`, final) | 17 | nodes 28, links 33, phases 1, emotion targets 6, complex emotions 1, genre contracts 3, genre interactions 5 |

The product's review object for each run is in `evidence/product/`. The run summary is `evidence/product/run-summary.json`.

## 2. Independent review

The mission requires a fresh-context reviewer where one is available. Three subagents ran in this session: two reviewers (Opus) and one blind host (Haiku). They are separate contexts from the constructor. Each is one reviewer, with the limits in §5.

### 2.1 Packets and withholdings

| Review | Packet | Withheld |
|---|---|---|
| Causal adequacy (R1) | `review/causal-packet/` (manifest there) | PR #551's §8 self-assessment and its "thinnest" and "filler" sentence; one retrospective clause in the original candidate. PR #552's review record and reconciliation; the designer's evaluation files; the H1 candidate; the blind output; the adjudication. |
| Semantic consistency (R2) | `review/semantic-packet/` (manifest there) | The H1 rationale document; PR #552's reconciliation; the designer's evaluation files; the blind output; this record. The reviewer is told that the preserved list compares identifiers only. |
| Blind host (B) | The request file (48 KB) from canvas `blindtest` | Nothing from this construction. It received the PR #551 H1 + R-A instruction plus one explicit preserved-element paragraph, on the PR #551 original baseline. |

### 2.2 Results

- **R1 causal report:** verbatim in [`review/causal-report.md`](review/causal-report.md). Twenty findings, F1–F20, with a severity and a classification.
- **R2 semantic report:** verbatim in [`review/semantic-report.md`](review/semantic-report.md). Preserved elements checked one by one (the H1 review's preserved list: 29 nodes, 34 links, 1 phase, 6 emotion targets, 1 complex emotion, 3 genre contracts, 5 genre interactions), plus changed elements, missed propagation, internal consistency, and an own check.
- **B blind host:** the response was refused by the product (see §1). The raw response is in `evidence/blindtest/blind-host-response-raw.json`. A diagnostic reading is in §4.

## 3. Adjudication

Rule: a finding is **adopted** if the text it cites contradicts itself or the original, or if the mission requires it. It is **partly adopted** if the concern is real but the reviewer's classification or fix is wrong. It is **declined** with the reason. No finding is adopted only because a reviewer said so. The corrections were made in one round. They were not re-reviewed by a fresh reviewer, which is a limit recorded in §5.

### 3.1 Causal report (R1)

| id | Finding (short) | Decision | Where the decision lives |
|---|---|---|---|
| F1 | A dry-spring release cannot raise the high cistern's stored water | **Adopted.** Release draws the high cistern down: its channels dry; a lineage channel fails; the lower channels flush and then silt. | `01` §3 Consequence |
| F2 | The Brightwater cohort is "born into" a state that postdates their birth | **Adopted.** They came to adolescence after Book 20; Hesper was born about Book 13. | `01` §5 |
| F3 | C's "before the pulse is visible" contradicts the Book 23 prediction | **Adopted.** "Before the threshold is crossed." | `02` C; W2 `alt_c` |
| F4 | B binds the gift practice, which is the closed option (a) | **Adopted.** B binds the water at the Gate for every practice; it does not count the gift practice's labour. | `02` B "What binds" |
| F5 | "Since Book 6" implies hands once set draw | **Adopted.** "For the first time in the series." | `01` §2 |
| F6 | A's dependence is called "physics" but the schedule is the Table's | **Adopted.** The schedule follows a balance reading that anyone can check. | `02` A mechanism 1 |
| F7 | A's floor is funded by a body with no authority over shares | **Adopted.** Funded by the lineage's Right; administered by the Table. | `02` A mechanism 5 |
| F8 | B's rule says hands follow draw, while the text says hands set draw | **Adopted.** Hands are owed in proportion to draw; a shortfall is a deficit, not a cut. Arc IV's conversion is suspended for the window, not repealed. | `01` §6; `02` B; W2 `alt_b`, `l_alt_b_bounds` |
| F9 | C makes the Balance Stones binding, against "informs but does not bind" | **Adopted as a stated cost.** C changes a Book 23 function unless the valley ratifies it; the author must accept it. | `02` C costs |
| F10 | The record payoff weakened | **Adopted.** W2 restores "no single institution holds the record in Book 30", and adds that no body holds both the record and the schedule. | W2 `gn_political_institutional` |
| F11 | Provenance changed against the Fixed brief | **Declined.** The experience words (wonder, belonging, hope) are author-fixed in the intentions. The eliciting conditions and the emotion mapping are the agent's. The provenance field can record only one. The correction stays, and the limit is recorded as C4 in [05](05-consistency-record.md). | W2 emotion targets; `05` A5, C4 |
| F12 | Revocability stated as fact and reserved for the author | **Adopted.** Labelled a working design; open question 5 stays open. | W2 `inst_lineage_crews` |
| F13 | The Book 15 surfeit is caused by the Gate, which the original does not say | **Adopted as an assumption.** Labelled as the construction's reading, which the author may reject. | `01` §1 table; W2 `str_hollow_gate` |
| F14 | Genuine abundance in the high cistern has no mechanism | **Adopted.** The Table holds water back in dry spells, and lineage crews seal the high channels' leaks. | `01` §5 |
| F15 | "Nothing here is new" and "one correction" overstate | **Adopted.** Each row cites its source; the Gate is the one addition. W2 summary restated. | `01` §1; W2 summary |
| F16 | Open question on a measured ledger removed | **Adopted.** Restored (merged with the Compact question to keep the sixteen-question cap). | W2 open questions |
| F17 | Book 1 reading and custody wording changed | **Declined.** The Book 1 correction is required by the mission (§8) and by PR #552 finding 9. Custody must be explicit (mission §8, H1 finding 18). The reviewer's classification as "unnecessary" is not accepted. | `05` A1, A13 |
| F18 | Gate Table seat composition differs between the node and Alternative B | **Adopted.** B's Table is the Gate Table with its seats redrawn, all by lot, one cycle each. | `02` B |
| F19 | The Lowfen, the Special Right and the Gate lack antecedents | **Partly adopted.** The Lowfen derives from Book 1's lower channel; the Special Right from Books 6–11 (lineages) and Book 15 (the tally). The Gate is a construction addition, labelled, and the author may reject it. Not added to open questions because of the cap. | `01` §1; `05` A15 |
| F20 | B's capture risk stated two ways | **Adopted.** The comparison row now reads "risk ... limited by lot seats and sunset". | `02` comparison |

Optional repair notes: the Book 21 physics (F1), the belief's dating (F2) and the revocability marking (F12) are adopted. "Before the window opens" is replaced by "before the threshold is crossed" (F3), which fixes the same point with a checkable condition.

Declined issues the reviewer raised without a numbered finding are covered in §3.2.

### 3.2 Semantic report (R2)

Task 1 (preserved elements) produced conditional or stale verdicts for these. Each is handled as shown.

| Element | Verdict | Decision |
|---|---|---|
| `alt_a_reciprocal`, `inst_gate_table` ("voice at the Gate Table") | conditional | **Adopted.** The remnant stands outside the Table in H1; neither W2 nor the Table holds a seat for it. |
| `alt_b_allotted` (remnant's place under all-lot seats) | conditional | **Resolved** by the same change: the remnant is outside the Table, so B's seats do not need to account for it. |
| `inst_reading_hall` | stale: no custody, and founded "after" the Book 15 reading | **Adopted** in H1: founded at Book 15 and takes custody there. |
| `th_reading` / Book 12 reader | conditional | **Adopted** in H1: the Book 12 partial reading is made under the committee's custody. |
| `l_custody_grants_hall` | conditional: no time bound | **Adopted.** W2: "until Book 5". H1: "until Book 15". |
| `ph_5_unmeasured` (silent on the remnant) | conditional | **Declined.** The finale's open question records whether the Hall becomes a benevolent authority. Arc V needs no remnant role to be consistent. |
| `gn_epic_fantasy` ("public reading" trope) | conditional | **Declined.** The trope refers to the Book 15 reading of the Stones, not to access to the record. H1 separates the two in the political contract. |
| `gi_pastoral_mystery_reinforces` (lineages and custody) | conditional | **Declined.** The lineages hold the knowledge to read the script; custody is the physical record. The two are distinct in the text. |
| `l_ledger_opens_trade`, `inst_mill_compact` (sale rules omitted) | conditional | **Declined.** The sale rules are a phase-level detail (ph_1, ph_2); the link's text holds. |
| `l_reading_decides_binding` | conditional | **Declined.** The committee's reading does not bind before Book 15, and the link's text is general. |
| `gn_pastoral_belonging` (references changed elements) | conditional | **Accepted as consistent** after the changes above. |

Task 2 (changed elements) and task 3 (missed propagation):

| Item | Decision |
|---|---|
| Summary: "Books 1-15 are unchanged except for one correction" | **Adopted**, in W2 and H1 (inherited). |
| `ph_1` thinning motive is not stated anywhere | **Adopted** in H1: "a thinning its own falsified credit helped cause". |
| `ph_1` "tenders" undefined | **Declined.** Defined in the original's character list: "a tender of Quillmark terrace" (A §2, in the packet). |
| `ph_2` "scholars" | **Declined.** The original calls the Book 8 partial readings "scholarly" (C-revision-delta A5). |
| `ph_3` custody "plural" against "passes to the Reading Hall" | **Adopted** in H1: "one public keeper". |
| `ph_3` "founded" against custody | **Adopted** in H1. |
| `ph_4` remnant "voice" | **Adopted** in H1: "stands outside the Gate Table". |
| `ce_bittersweet_return` "given up custody" | **Adopted** in H1: "has lost custody of it". |
| Open question on H1 not its own entry | **Declined.** The list is capped at sixteen. H1's question is merged into the reform question. |
| Witness not named | **Declined.** The witness is a household, not a character, and the text states the household's evidence. |
| Loops not named as loops | **Declined.** The loops exist as link chains (L1: `l_ledger_draws_source`, `l_source_limits_ledger`; L2: `l_oldhand_redefines_share`; L3: `l_ledger_opens_trade`, `l_trade_draws_without_return`). The original does not name them either. |
| `R-A`, "the fixed brief", "Keeper Anselm Corrow" not in the file | **Declined.** R-A is an instruction label; the brief is recorded as intentions; the candidate uses "Keeper Corrow", as the original does. |
| `ph_1` reader experience | **Declined.** The reader experience line would reintroduce the mixed anger register that R-A created. |

Task 4 (internal consistency): the custody statements, the Reading Hall's founding and the remnant's place were all made consistent in H1 (see above). The H1 open question is consistent with the rest of the text.

Task 5 (own check): the trope "the compromise that feeds a new monopoly" and the Book 8 intermediate-state question are not changed. Both are describing dangers or open questions and are not contradicted by H1, so they stay as they are.

## 4. Blind host-agent test

**Question.** Can a fresh agent, correctly instructed and using Auteur's operations, detect and repair the stale preserved items that PR #552 found? The instruction is the PR #551 H1 + R-A instruction on the original baseline, plus one explicit paragraph requiring a semantic check of every preserved element.

**Result, in two parts.**

1. **Structural: refused.** The response failed `ArchitectureCandidate` validation on one enum: a genre contract with role `background`. The product refused it, so nothing was applied. The product's structural gate worked. It is a host error, not a semantic failure, and it stopped the run.

2. **Semantic: diagnostic reading.** A scratch copy with only that enum corrected (`background` to `tertiary`) validates, and was read for content. It was not submitted and is not an applied revision. Its handling of the items:
   - `et_grief_of_orders`: **repaired.** Rewritten as the Hall's loss of sole custody, with dignity for the Hall, and the Hall "survives reformed rather than dissolved".
   - `ce_bittersweet_return`: **repaired.** "after the institution that held sole custody has been reformed rather than destroyed".
   - `et_anger_at_hidden_credit`: **changed** to "outrage at credit falsified against the powerless, which the reform answers by ending sealed custody but does not by itself repay". This is a judgment, not a repair the packet required.
   - The remnant: **removed** by the simpler route. The Hall "stays continuous rather than splitting into a remnant".
   - "Seizure": **reintroduced.** ph_1 says the monopoly breaks "by reform rather than by outside seizure". The baseline error PR #552 found is back.
   - "Restored monopoly": **reintroduced** as an open question, "the vehicle for the Book 30 restored-monopoly option". The phrase the construction removes is back.
   - Custody: **resolved** only as "contested among the reformed committee and the institutions that later form". No Book 15 handover.
   - Links: 24, of which eight link IDs the original does not have.

**Reading.** One fresh run did detect and repair the two items PR #552 named, and did not preserve the stale ones. But: (a) the run was refused structurally; (b) it reintroduced two errors the review had removed; (c) the 551 instruction already named the grief target, so the improvement may come from the added preserved-check paragraph or from variance between runs. The test was one run, not a controlled comparison. So the honest answer to PR #552's question is **partly**. A correctly instructed agent can detect and repair the named semantic items, but it does not do so reliably in one pass, and the product does not check its semantics. No product machinery is recommended from this, because the test does not establish the reliability of the instruction. A repeated trial would.

## 5. Limits

- Two reviewers and one blind host were run once each. None is a population.
- The corrections in §3 were made in one round and were **not** re-reviewed by a fresh reviewer. Any defect the corrections introduced is unreviewed.
- The coordinator wrote the construction, chose the packets' withholdings, and adjudicated the findings. Those choices are documented judgments, not a neutral process.
- The reviewers knew that some passages were withheld, and may have directed their attention toward the gaps.
- Nothing was run in prose. No reader, no fresh-agent reconstruction of the narrative, and no test of how the Arc IV chains read on the page.
- The blind run was refused structurally, and its semantic reading is diagnostic only.
- One more Opus review of the final text could catch what this round did not; it was not run, because the mission asks for corrections, not an indefinite critique cycle.
