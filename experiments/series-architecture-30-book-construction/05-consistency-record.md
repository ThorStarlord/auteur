# 05 — Semantic consistency record

Status: **working / noncanonical.** Records which contradictions the working construction corrects, which it tests, and which it deliberately leaves open. The original experiment (PR #551) is not modified. Where a correction applies only to the working construction, the original files still contain the uncorrected text, and this record says so.

Status values: **corrected** (fixed in W1 or H1, with the field named), **explicit** (was implicit, now stated), **open** (deliberately not decided), **pending review** (the independent review must test it), **product** (a limit of Auteur's representation, not of the fiction).

---

## A. Original path (working candidate W1)

| # | Issue | Where it appears | Origin | Status | What W1 does |
|---|---|---|---|---|---|
| A1 | Book 1 partial reading: the JSON says Book 1 gives the first partial reading; the prose says Books 8 and 12; the concept note says "Book 1 open" | `ph_1` (original); `th_reading` summary; `A-original-architecture.md` §3.3, §6; `01-concept-comparison.md` | PR #552 finding 9 | **corrected** | Book 1 reads the share-marks as evidence and does not read the script. The first partial reading of the script is Book 8 (`th_reading`, `ph_1`). |
| A2 | The Book 30 alternatives in the JSON ("restored monopoly" against shared accounting) do not match the prose's three options | `ph_5` (original) | PR #552 finding 8 | **corrected** | `ph_5` names the three options (A, B, C), which map onto the prose's three. |
| A3 | "Restored monopoly" implies the Stone Hall returns | `ph_5` genre activation (original) | Mission §8 | **corrected** | `ph_5` narrative: "No option restores the Stone Hall's sole custody." |
| A4 | A retrospective clause ("the most likely place for filler") sits in a design field | `ph_4` narrative (original) | Stage A packet withholding | **corrected** | Removed. Retrospective commentary belongs in the record, not the candidate. The original file keeps it. |
| A5 | Three emotion targets are labelled `author_declared`, but their intended effects and eliciting conditions are the agent's mapping of the brief. The brief's experience words are author-fixed; the mapping is not | `emotion_targets` (original); `D §4.6` | PR #551 observation 6 | **corrected** | Set to `agent_proposed`. The experience words remain author-fixed intentions in the Studio record. |
| A6 | Book 23's abundance: the critic claimed nothing sets it up. Checked: Book 15 creates the surfeit and Book 23 draws the water | `A-original-architecture.md` §5 (Books 15 and 23); `ph_3`, `ph_5` | PR #552 finding 7 (rejected as stated) | **explicit** | The chain is written out as Surfeit (15) → gate schedule (21) → surplus (22–23) → festival draw (23) (`01` §5; `ph_4`). |
| A7 | Books 27–29 have no function (critic); the original names only the Compact's bid | `A-original-architecture.md` §5, §6 | PR #552 finding 6 (partly overstated) | **explicit** | Books 27–29 now carry the Compact's bid and, under C, the ratification window. Books 24–26 still have no function, which is deliberate. |
| A8 | Civilizational scope is unsupported | `A-original-architecture.md` §8.4 | PR #552 finding 10 | **open** (partly addressed) | Lowland draw enters through the Compact's grain-labour (B) and the lowland gate (`open_questions` 2 and 16). The lowland towns have no arc, and that stays open. |
| A9 | Arc IV is the thinnest arc and exports nothing | `ph_4`; `A-original-architecture.md` §4, §8.1 | PR #552 finding 4 | **corrected** | Two conflicts with exports (`01` §2–§4; `ph_4`). Tested in [06](06-validation-and-review.md), not in prose. |
| A10 | Finale "care without debt" is asserted, not derived | `ph_5`; `A-original-architecture.md` §5 Book 30 | PR #552 finding 3 | **corrected**, mechanism only | Three mechanisms with failure modes (`02`). Whether shared accounting binds, and which mechanism is chosen, stays with the author. |
| A11 | The Old Hand's state between Books 8 and 15 is not changed by any Book | `A-original-architecture.md` §8.2 | PR #552 finding 5 | **open** | Not added: the brief forbids per-Book outlines, and no Arc IV conflict requires it. Open question 11. |
| A12 | Hesper's motive may be authored rather than derived | `A-original-architecture.md` §8.3 | PR #552 finding 11 | **open** | Kept as authored. Open question 10. Her apprenticeship is the only function given. |
| A13 | Custody and access are conflated in Book 5. The original says custody is "contested afterwards" but does not say who holds the physical record | `th_custody` (original); `ph_1` | **Found in construction**; the same ambiguity PR #552 finding 18 found under H1 | **explicit** | Public access to the credit record from Book 5. Physical custody contested until Book 15. |
| A14 | The Council is said to hold the gift reading (Book 15) and also to run the counted Turn, which counts labour against draw | `inst_terrace_council`; `str_measured_turn` | **Found in construction**; the original already has both | **open** | W1 keeps both and says the Council reads gift while running the count. The causal reviewer was asked to test it and did not raise it, so it is recorded as open, not as tested. |
| A15 | The Hollow Gate: the original names the lower gate only at Harrow Lowe | `A-original-architecture.md` §2 | **Found in construction** | **explicit** | The Hollow Gate is added as the valley's internal sluice (`01` §1). It is marked as a construction addition. |

## B. Hypothetical path (H1, [04](04-h1-focused-delta.md))

| # | Issue | Where | Origin | Status | What H1 does |
|---|---|---|---|---|---|
| B1 | The counterfactual's baseline is "seizure"; the original has evidence and coalition | `C-revision-delta.md` §2 A1, §8 | PR #552 finding 19 | **corrected** | The baseline is restated in `04` §2. The word does not appear in W1 or H1. |
| B2 | `et_grief_of_orders` names "the Stone Hall's fall", which H1 removes | `et_grief_of_orders` | PR #552 finding 15 | **corrected** | Re-pointed to the committee's loss of custody at Book 15 and the remnant's dissent. |
| B3 | `ce_bittersweet_return` depends on the institution having fallen | `ce_bittersweet_return` | PR #552 finding 16 | **corrected** | Context anchored to giving up custody. Whether this is still bittersweet is for review. |
| B4 | Arc III names "the Stone Hall remnant" but nothing forms the remnant under H1 | `ph_3` genre activation | PR #552 finding 17 | **corrected** | The remnant forms at Book 15, when custody passes to the Reading Hall. |
| B5 | Custody and monopoly are ambiguous | `inst_stone_hall`; `gn_political_institutional` payoff | PR #552 finding 18 | **corrected** | Access monopoly ends in Book 5. Custody monopoly ends in Book 15. |
| B6 | The R-A anger target carries two emotions under one label ("unease"), so it has a mixed register | `et_anger_at_hidden_credit` (R-A) | Stage B P4 | **corrected** | H1 restores the Book 1 anger. The cost of reform is carried by the grief target and the consequential-loss reader experience. A reviewer may challenge this. |
| B7 | "The falsified record" trope was dropped under R-A | `gn_political_institutional` | PR #552 finding 24 | **corrected** | Kept. |
| B8 | "Corrow's dissenting remnant" in Book 15 is consistent with the original, but not with H1 unless the remnant forms in Book 15 | `A-original-architecture.md` §5 Book 15 | PR #552 finding 17 | **corrected** | Consistent with H1: the remnant forms at Book 15. |
| B9 | Revision status is stored in design fields, and the review copies the summary into `proposed_rationale` | `th_witness` summary; candidate summary | PR #552 finding 21 | **partly corrected**, **product** | The `th_witness` summary no longer says "Added by revision R-A". The H1 summary still carries a hypothetical label, because the product takes the rationale from it. Logged as a product limit in [06](06-validation-and-review.md). |
| B10 | Preserved-by-ID review does no semantic check | Product review (`preserved`) | PR #552 finding 22 | **tested** | A blind host run and a semantic reviewer, in [06](06-validation-and-review.md). |
| B11 | The medium of record is not revised for H1 | `A-original-architecture.md` (PR #551) | PR #552 finding 20 | **open** | Deliberately unchanged. [04](04-h1-focused-delta.md) §6 names the disagreements that remain in the original files. |
| B12 | Book 12 described as a dispute "between two institutions" | `C-revision-delta.md` §3 | PR #552 finding 24 (minor) | **corrected** | `ph_3` transition: "Legitimacy is contested among three readings." |

## C. Product limits recorded here (not fixed in the fiction)

| # | Limit | Evidence |
|---|---|---|
| C1 | `apply` is not in the CLI bridge. The working revision was applied with the Python entry point. | `evidence/apply_review.py`; `evidence/run_canvas.sh` |
| C2 | The review's `preserved` object compares IDs. It does not check meaning. | [06](06-validation-and-review.md) §3 |
| C3 | The product's `proposed_rationale` is copied from the candidate summary. Revision status can therefore enter the rationale. | B9 above |
| C4 | Authority provenance (`author_declared`) is accepted from the host agent. The product does not check that an author declared it. | A5 above; PR #551 observation 6 |
| C5 | Link `function` is limited to 120 characters, so causal chains are written as short labels and their detail sits in node summaries. | `03-working-candidate.json`, all links |
| C6 | The schema has no phase or Book node. Book functions are free text in `scope` and in phase narratives. | `03-working-candidate.json` `phases` |
| C7 | `open_questions` is capped at sixteen. H1 has to replace one question to add its own. | `evidence/make_h1_path.py` |

## D. Summary of what changed in the reading, and what did not

- **Corrected in the working construction:** A1–A5. Their correction is recorded here and not in the original files.
- **Explicit:** A6, A7, A13, A15.
- **Open, on purpose:** A8, A11, A12, B11. The fiction's author-reserved choices are in [02](02-finale-alternatives.md) and are not counted as corrections.
- **Open, not tested:** A14. The causal reviewer was asked about it and did not raise it.
- **Product limits:** B9, C1–C7. None of these is fixed by changing the fiction.

## E. Corrections made after independent review (W2 and H1 final)

The two reviews and the blind run produced the findings adjudicated in [06](06-validation-and-review.md) §3. The corrections that changed text, by file:

| Where | Correction | Source |
|---|---|---|
| `01` §1, §3, §5, §6 | Each row cites its source. Book 21: release in a dry spring draws the high cistern down, and does not raise its surplus. Brightwater's cohort came to adolescence after Book 20. Genuine abundance has a mechanism (held water, sealed leaks). B's rule: hands are owed in proportion to draw; a shortfall is a deficit. | Causal F1, F2, F8, F14, F15 |
| `02` A, B, C | The schedule follows a balance reading. The floor is administered by the Table, funded by the Right. B binds water, not labour, and its Table's seats are redrawn by lot. C's trigger is "before the threshold is crossed". C's costs include the Stones' changed function and an unchecked reading-activation. The comparison's B risk is stated once. | Causal F3–F9, F18, F20 |
| W2 `summary` | "Books 1-15 keep the original's events" and one correction, with the Gate and the tally made explicit. | Semantic task 2 |
| W2 `str_hollow_gate`, `inst_lineage_crews`, `alt_b`, `alt_c`, links `l_alt_b_bounds`, `l_custody_grants_hall` | The Book 15 surfeit's mechanism is an assumption. The Special Right is a working design, revocable, open. B's deficit, C's threshold and activation, and a custody bound of "until Book 5". | Causal F8, F12, F13, F3; semantic (custody) |
| W2 `gn_political_institutional` | "no single institution holds the record in Book 30" restored, with the schedule separate. | Causal F10 |
| W2 open questions | Merged the lowland question with the Gate Table's reach; restored the measured-ledger question. | Causal F16 |
| H1 `inst_reading_hall`, `l_custody_grants_hall`, `ph_1`, `ph_3`, `ph_4`, `ce_bittersweet_return`, `gn_political_institutional` | Custody at Book 15 by the Reading Hall; the custody bound is "until Book 15"; the thinning motive; one public keeper, not plural; the remnant outside the Table; the Book 12 reader; "has lost custody of it"; the Book 30 payoff. | Semantic tasks 1–4 |

Not changed, with reasons in [06](06-validation-and-review.md) §3: the provenance of the three emotion targets (F11, a representation limit recorded as C4), the Book 1 correction (F17, required by the mission), and the items the semantic review raised that are judgments rather than contradictions.
