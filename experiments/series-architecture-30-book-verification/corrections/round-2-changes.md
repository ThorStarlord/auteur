# Round 2 corrections: W4 and H1v3

Status: **working / noncanonical.** The first finding-specific verification (Stage F, round 1) found that some round-1 corrections were partly fixed and that one introduced a new contradiction. Round 2 corrects those. It does not change the round-1 files. W4 is `04-working-candidate-v4.json` and H1v3 is `10-h1v3-from-w4.json`, both produced by [make_round2.py](../evidence/make_round2.py). The round-1 candidate (`03-working-candidate-v3.json`) and H1v2 (`09-h1v2-from-w3.json`) are kept as they were verified.

**Validation.** Both pass the product's schema. The product's review objects are [review-w3-to-w4.json](review-w3-to-w4.json) and [review-w4-to-h1v3.json](review-w4-to-h1v3.json). The changed components are those listed below, and nothing else.

| Round-1 finding | Verified state | Round 2 change |
|---|---|---|
| F-1 (surfeit path unsupported) | Fixed, but its path was unsupported | W4-1 |
| F-3 (the tally holds the surfeit in ph_3) | Partly fixed (the node was fixed, the phase was not) | W4-2 |
| F-5 (Compact settlement not acknowledged) | Partly fixed | W4-3 |
| F-7 (A's Principle keeps the coupling) | Partly fixed | Errata E1 (Principle), not a candidate change |
| F-9 (gift-practice erratum contradicts B's text) | New defect | Errata E3, rewritten |
| F-13 (H1 summary omits remnant timing and Book 12) | Partly fixed | H1-2 extended |
| Terminology ("upper cistern" in ph_2) | Not in the findings; found by the verifier | W4-4 |
| F-12 ("author-reserved" label) | Overreach | H1-1 label: "for the author to confirm" |

---

## W4-1. `str_hollow_gate.summary` (round 1 F-1)

- **Round 1 (W3-1):** "In the Book 15 trial the high cistern showed surfeit, which the original defines as too much return, or stored water with no draw. The construction assumes that the trial's uncounted return labour fed the high channels beyond the Turn's count, so stored water rose with no draw to match it. Release draws the cistern down and cannot raise it."
- **Round 2 (W4-1):** "In the Book 15 trial the high cistern showed surfeit. The Source responds to the balance between draw and return, and surfeit is too much return, or stored water with no draw. The construction assumes that the trial's uncounted return exceeded the draw the Turn counted, so the surplus showed in the high cistern. The original does not name this mechanism, and the author may reject it. Release draws the cistern down and cannot raise it."
- **Defect removed:** the first version gave the surfeit a labour path (gift-practice labour fed the high channels) that the packet does not establish. The new version relies only on the Source's balance rule, which the original states, and labels the mechanism as the construction's assumption.

## W4-2. `ph_3_old_hand.narrative_function` (round 1 F-3)

- **Round 1 (unchanged text):** "The stewardship tally records care, not debt, so the high terraces are not surfeited."
- **Round 2 (W4-2):** "The stewardship tally records care, not debt, and the counted Turn's labour keeps the high terraces from surfeit."
- **Defect removed:** the phase repeated the claim that a record prevents surfeit, which round 1 had corrected only in the Turn node.

## W4-3. `ph_5_unmeasured.narrative_function` (round 1 F-5)

- **Round 1 (W3-4):** "The original's adopted outcome is closest to A; its Compact settlement stays open."
- **Round 2 (W4-3):** "The original's adopted outcome is closest to A; its share-plot settlement is an open choice."
- **Defect removed:** the original does commit a Compact share-plot settlement in its Book 30 closure, and the round-1 wording did not say so. The new wording names it as an open choice, which is what the original's own list does.
- **Length:** the phase narrative is now 996 characters, under the 1000 cap. The first draft of this round was 1,004 characters and was shortened before validation.

## W4-4. `ph_2_the_turn`, activation of Mill Compact (terminology)

- **Before:** "… draw separates from return and the upper cistern thins (Book 6) …"
- **After:** "… draw separates from return and the high cistern thins (Book 6) …"
- **Why:** the candidate used "high cistern" elsewhere. The one instance of "upper" in the candidate is now aligned.

---

## H1v3: the H1 path, corrected in round 2

H1v3 is derived from W4 by the recorded script, and then the H1 corrections are applied.

- **H1-1 (round 1 F-12), wording changed:** the finale payoff now says the Reading Hall is the single public keeper of the record, "an H1 consequence that reopens the finale's plural-record commitment (for the author to confirm)". The round-1 label "(author-reserved)" overstated the packet, because the plural-record commitment is not in the author-reserved list in 02.
- **H1-2 (round 1 F-13), extended:** the summary now also says that Book 12's reading is made under committee custody, and that "the original's Book 5 split is replaced by the remnant forming at Book 15". The Book 15 remnant and the Book 12 reading were H1 changes that the round-1 summary did not list.
- **H1-3 (round 1 F-15), unchanged in round 2.**

## Errata changed in round 2

- **E1 (02, Alternative A):** the Principle sentence that repeated the coupling is replaced. Mechanism 1's physical wording now says a terrace can leave the channels unable to carry the water of every terrace that uses them.
- **E3 (02, Alternative B):** the round-1 erratum contradicted B's own item 2. The new erratum amends item 2 explicitly and states that the author has not confirmed the gift practice's inclusion. It also adds the deficit keeper as a cost.
- **E4 (02, Alternative C):** a note keeps activation as an open author choice.
- **E5 (01 §1 and §3):** the Book 15 mechanism is restated as the Source's balance rule, with the assumption labelled.
- **E7 (terminology):** now true for the candidate, after W4-4.

## Checks run on round 2

- Schema validation: W4 and H1v3 pass `ArchitectureCandidate`.
- W4 summary: 1,739 characters, unchanged from round 1.
- H1v3 summary: 2,908 characters, under 3,000.
- ph_3 narrative: 388 characters. ph_5 narrative: 996 characters.
- The traces (04) and the crisis (03) use none of the changed text.
