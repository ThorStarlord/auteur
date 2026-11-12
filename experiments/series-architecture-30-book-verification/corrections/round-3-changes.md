# Round 3 corrections: W5 and H1v4

Status: **working / noncanonical.** Records the third and final set of candidate changes. It corrects what the second finding-specific verification found. W5 is `05-working-candidate-v5.json`, and H1v4 is `11-h1v4-from-w5.json`, both produced by [make_round3.py](../evidence/make_round3.py). W4 and H1v3 are kept as they were verified.

**Validation.** Both pass the product's schema. The product's review objects are [review-w4-to-w5.json](review-w4-to-w5.json) and [review-w5-to-h1v4.json](review-w5-to-h1v4.json). The changed components are the ones listed below and nothing else.

**Stopping rule.** Round 3 is the last round of candidate changes in this mission, by design. Each round has been verified once by a fresh reviewer, and each round has surfaced a defect in the previous round's wording. Items that a third verification would still be needed for are recorded as open in [06](../06-adjudication.md), not corrected further.

| Second-round finding | Verified state | Round 3 change |
|---|---|---|
| ND-1: W4-1 says surfeit is too much return; W4-2 and the Turn node say labour holds surfeit off | New defect | W5-1, W5-2 and errata E8 |
| F-5: the original's Compact commitment is named only as "open" | Partly fixed | W5-3 |
| ND-2: the A paragraph beside mechanism 1 still describes it as a dependence | New defect | Errata E1 (paragraph) |
| T-1: the H1 path reintroduces "upper cistern" | Partly fixed | H1-4 |
| E7 (terminology) was not checked, because the packet cleanup removed its text | Unverified | Errata E7 restated |

---

## W5-1. `str_measured_turn.summary`. The Turn matches return to draw

- **Before:** "The counted Turn's labour holds the high cistern against surfeit."
- **After:** "The counted Turn matches return to draw, which keeps the high cistern from surfeit."
- **Defect removed:** under the Source's balance rule, surfeit is too much return, so labour as such cannot hold surfeit off. What holds it off is returning no more than the draw.

## W5-2. `ph_3_old_hand.narrative_function`. The same claim in the Book 15 phase

- **Before:** "… and the counted Turn's labour keeps the high terraces from surfeit."
- **After:** "… and the counted Turn matches return to draw, which keeps the high terraces from surfeit."
- **Length:** 409 characters, under the 1000 cap.

## W5-3. `ph_5_unmeasured.narrative_function`. The Compact's Book 30 settlement

- **Before:** "The original's adopted outcome is closest to A; its share-plot settlement is an open choice."
- **After:** "The original's outcome is closest to A; its share-plot settlement is committed there; open here."
- **Defect removed:** the original commits a share-plot settlement in its Book 30 closure. The new wording names that commitment, and it says the settlement is open in this construction.
- **Length:** 1,000 characters, exactly at the cap. The first attempt at this round was 1,003 characters and was shortened before validation.

## H1-4. H1 activation, Book 6 phrase. Terminology reintroduced by the H1 script

- **Before (H1 script):** "… draw separates from return and the upper cistern thins (Book 6) …"
- **After:** "… draw separates from return and the high cistern thins (Book 6) …"

## Carried into the H1 path unchanged in round 3

- **H1-1, H1-2, H1-3** as in round 2. The H1 path is derived from W5, so it carries W5-1 to W5-3.

---

## Errata changed in round 3

- **E1 (02 Alternative A):** the Principle credits the tally, not the balance reading, with showing who maintains the channels. The paragraph after the mechanisms no longer calls mechanism 1 a dependence.
- **E7 (terminology):** restated, with the H1 change recorded as H1-4.
- **E8 (01 §1 item 3):** the counted Turn "matches return to draw". This replaces "keeps the high cistern from surfeit", which asserted the same claim through labour.

## Checks run on round 3

- Schema validation: W5 and H1v4 pass `ArchitectureCandidate`.
- W5 summary: 1,739 characters, unchanged. H1v4 summary: 2,908 characters.
- ph_3 narrative: 409 characters. ph_5 narrative: 1,000 characters.
- The traces (04) and the crisis (03) use none of the changed text.
