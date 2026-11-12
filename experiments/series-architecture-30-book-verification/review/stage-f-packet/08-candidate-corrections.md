# Corrections to the final candidate (W3) and to the H1 path (H1v2)

Status: **working / noncanonical.** Records each change to W2 and to H1-from-W2, with the defect it removes and the finding that identified it. W2 (`03-working-candidate-v2.json`, PR #553) and H1-from-W2 are unchanged. The corrected candidates are new files in this folder, and both were produced by [make_w3_and_h1v2.py](../evidence/make_w3_and_h1v2.py).

**Validation.** Both corrected candidates pass the product's schema (`ArchitectureCandidate`, schema v2). The product's own review objects are in [review-w2-to-w3.json](review-w2-to-w3.json) and [review-w3-to-h1v2.json](review-w3-to-h1v2.json). The changed components are the ones listed below and nothing else.

**One failed draft, recorded.** The first draft of W3-4 appended a longer sentence to the Book 30 phase narrative. The schema caps that narrative at 1000 characters, and the draft ran to 1,176 characters, so validation failed. The sentence was shortened to 986 characters. The cap was not loosened.

---

## W3: the final candidate, corrected

### W3-1. `str_hollow_gate.summary`. Book 15 surfeit

- **Before:** "In the Book 15 trial the schedule carried release to the lower channels, and the high cistern showed surfeit. The construction reads the surfeit as that release's effect, which the original does not name."
- **After:** "In the Book 15 trial the high cistern showed surfeit, which the original defines as too much return, or stored water with no draw. The construction assumes that the trial's uncounted return labour fed the high channels beyond the Turn's count, so stored water rose with no draw to match it. Release draws the cistern down and cannot raise it."

### W3-2. `str_measured_turn.summary`. Labour, shares and the tally

- **Before:** "Draw matched to labour in the high terraces … The stewardship tally, from Book 15, is kept as a record of care for this practice. It holds the high cistern against surfeit."
- **After:** "Labour matched to shares in the high terraces … each share returns labour by rota, and draw still follows shares. The counted Turn's labour holds the high cistern against surfeit. The stewardship tally … records that labour … it does not hold the water."

### W3-2b. `ph_4_settled_water.narrative_function`. "First time"

- **Before:** "It makes hands set part of draw for the first time since Book 6, and it gives lineage crews a claim on draw."
- **After:** "It makes hands set part of draw for the first time in the series, and it gives lineage crews a claim on draw."

### W3-3. `inst_stone_hall.summary`. "Splits"

- **Before:** "Under this working path the Hall dissolves in Book 5, and a remnant under Keeper Corrow continues …"
- **After:** "Under this working path the Hall splits in Book 5, as the original has it, and a remnant under Keeper Corrow continues …"

### W3-4. `ph_5_unmeasured.narrative_function`. The original's adopted outcome

- **Before:** "… the Compact's settlement is a clause of B or C."
- **After:** "… the Compact's settlement is a clause of B or C. The original's adopted outcome is closest to A; its Compact settlement stays open."
- **Failed first draft.** The first draft added a longer sentence. The narrative ran to 1,176 characters, which failed the schema's 1000-character cap. The shorter wording above, at 986 characters, is the one recorded here.

### W3-5. `summary`. Recording what is not decided

- **Before:** "… the stance toward reform are not decided here."
- **After:** "… the stance toward reform are not decided here. Also not decided: whether the Hollow Gate and the Gate Table are accepted parts of the world, and which body ratifies the instrument that Alternative C depends on."


---

## H1v2: the H1 path, corrected

H1v2 is derived from W3 by the recorded script `make_h1_path.py`, and then the three H1 corrections are applied. Each correction asserts the exact text it replaces.

### H1-1. `gn_political_institutional` payoff 2. The finale consequence is declared

- **Before (H1 script):** "in Book 30 the record has one public keeper, and no single body holds both the record and the Gate schedule"
- **After:** "in Book 30 the Reading Hall is the single public keeper of the record, an H1 consequence that reopens the finale's plural-record commitment (author-reserved), and no single body holds both the record and the Gate schedule"

### H1-2. `summary`. Books 1–15 changes listed, and the sanction declared

- **Before:** the H1 prefix followed by the W3 summary, which still said "Books 1-15 keep the original's events."
- **After:** the H1 prefix now lists the changes to Books 1–15. It says that Dorran's Book 1 status is not yet specified, that the transfer's cause is not yet specified, and that the custody-until-Book-15 structure comes from the revision instruction and is not sanctioned by the premise. The W3 sentence is replaced with "Under H1, Books 1-15 change as stated above."

### H1-3. `open_questions[14]`. The question is about the transfer

- **Before:** "Under H1: does reform from within stay credible under Books 15 and 30, or does the Hall become a benevolent authority that the finale must oppose?"
- **After:** "Under H1: what causes the custody transfer at Book 15, and does the Reading Hall, as the single public keeper of the record, become the custodial authority the finale must check?"

---
