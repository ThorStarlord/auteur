# Stage F2 report, round 2 (verbatim)

**Packet:** `review/stage-f2-packet/` (copied from the packet folder used for the reviewer, after its cleanup). It verifies the round-2 candidates W4 and H1v3 against W3 and the round-2 errata. The cleanup of its file 09 removed the text of errata E7 (the round-2 erratum for terminology). E7 was therefore not checked in this round, and round 3 restates it.

**Reviewer:** one fresh general-purpose subagent, model Opus, one invocation. The reviewer self-identified as Claude Opus 5.5. It had no access to the Stage A, Stage B or Stage F reports, to the adjudication, or to any earlier version of these corrections, except the before and after texts in its own packet.

**Freeze:** recorded after round 3 had been derived, and before round 3 was verified. Nothing below the line has been edited. Round 3 is not covered by this report.

---

1. **Identity.** I am Claude Opus 5.5 (model ID claude-opus-5-5). I read only the ten files in `stageF2-packet/`: 00-reviewer-instructions.md, 01-findings.md, 02-original-architecture.md, 03-causal-construction.md, 04-finale-alternatives.md, 05-candidate-W3.json, 06-candidate-W4.json, 07-candidate-H1v3.json, 08-round2-changes.md and 09-prose-errata.md. To compare the JSON candidates, I ran a read-only Python one-liner that diffed 05 against 06 field by field and searched 05, 06 and 07 for key terms. I wrote, changed and deleted nothing.

2. **Table of items**

| ID | Judgment | Supporting quotation |
|---|---|---|
| F-1 | Fixed | 06 `str_hollow_gate.summary`: "The Source responds to the balance between draw and return, and surfeit is too much return, or stored water with no draw. The construction assumes that the trial's uncounted return exceeded the draw the Turn counted … The original does not name this mechanism, and the author may reject it." The physical claim that the labour fed the high channels is gone. What replaces it uses the original's own definition and is labelled as an assumption. E5 §3(b), "The high cistern bears the drawdown", matches 03 §3's Consequence ("draws the high cistern down"). |
| F-3 | Fixed, but see new defect ND-1 | 06 `ph_3_old_hand.narrative_function`: "The stewardship tally records care, not debt, and the counted Turn's labour keeps the high terraces from surfeit." The record no longer holds water. This now matches `str_measured_turn`: "…it does not hold the water." That node does not differ between 05 and 06, so the round-before change was already in 05. |
| F-5 | Partly fixed | 06 `ph_5_unmeasured`: "The original's adopted outcome is closest to A; its share-plot settlement is an open choice." The sentence now names the share-plot. It still describes the settlement only as open, and does not say that the original's Book 30 closure adopts it (02 §5: "the Compact takes a share-plot in lieu of claims"). Some support for "open" exists: 02 §1 lists "the Mill Compact's fate" under Open, and §7 lists "the Compact's end state" as provisional. A clause noting both sides of the original would remove the defect. |
| F-7 | Fixed, but see new defect ND-2 | E1 Principle, proposed: "Participation holds because each household's water runs through shared channels that its neighbours maintain, and the balance reading shows who maintains them." The coupling to each household's release is gone. |
| F-9 | Fixed | E3: "For the window it also binds the gift practice's labour, because its shares are inside the Long Rota, so its labour is counted for that window. This is a cost of B. The author has not confirmed it." This replaces the contradicting "stays uncounted". The added cost (a deficit record kept by the Reading Hall) agrees with B's existing "A deficit owed to the rebuild re-admits the debt reading for one window." |
| F-12 | Fixed | 07 `gn_political_institutional` payoff 2: "…an H1 consequence that reopens the finale's plural-record commitment (for the author to confirm)…". The text "author-reserved" appears nowhere in 07. |
| F-13 | Fixed | 07 `summary`: "The original's Book 5 split is replaced by the remnant forming at Book 15." and "Book 12's reading is made under its custody". |
| T-1 | Partly fixed | W4 is fixed: 06 `ph_2_the_turn` reads "the high cistern thins (Book 6)". H1v3 is not: 07 `ph_2_the_turn` still reads "draw separates from return and the upper cistern thins (Book 6)". This is despite 08's "H1v3 is derived from W4 by the recorded script". E7 in file 09 is a heading with no text under it, so the erratum cannot be checked (see section 5). |

3. **New defects**

- **ND-1 (caused by W4-1 together with W4-2).** The two changes describe surfeit in tension with each other.
  - W4-1 makes surfeit an excess of return over draw: "surfeit is too much return, or stored water with no draw … the trial's uncounted return exceeded the draw the Turn counted, so the surplus showed in the high cistern."
  - W4-2 says return labour prevents surfeit: "the counted Turn's labour keeps the high terraces from surfeit." The same claim appears in `str_measured_turn` ("The counted Turn's labour holds the high cistern against surfeit") and in 03 §1 item 3.
  - In the original, return is the labour given back to the channels (02 §2). Under W4-1's rule, more labour pushes the balance toward surfeit, so labour as such cannot be what holds surfeit off. What W4-1 implies holds it off is the matching: labour bounded to the draw of the shares.
  - A charitable reading of "counted" as "matched to draw" removes the conflict, but the text does not say that. Rewording W4-2 as something like "the counted Turn matches return to draw, which keeps the high terraces from surfeit" would close it.
- **ND-2 (caused by E1).** A paragraph next to E1, which E1 left unchanged, still describes the old mechanism 1.
  - The unchanged paragraph in 04 A, "How it differs from the Balance Stones", says: "Mechanisms 1 and 2 turn the same information into dependence. A household's water now depends on a particular neighbour's labour."
  - The new mechanism 1 says: "A terrace that stops maintaining the shared channels can leave them unable to carry the water of every terrace that uses them. That is a physical consequence, not a penalty."
  - Mechanism 1 is now a physical fact that exists before A. It no longer turns information into dependence, and the dependence is on everyone who shares the channel, not on "a particular neighbour". The paragraph now fits mechanism 2 only.
  - A smaller slip in the E1 text itself: the Principle's "the balance reading shows who maintains them" credits the balance reading with a job that 04 mechanism 4 gives to the tally ("The public tally, the Balance Stones and the Gate schedule let everyone see the balance and each household's care").
  - The mechanism's title, "Gate dependence", and the 06 `alt_a_reciprocal` summary ("gate dependence") are kept, although the new mechanism 1 text no longer mentions the Gate.

4. **Other observations, not part of this verification**

- **W4-1 and E5 leave two details unexplained.** The trial took place in Lower Ammen, but the text does not say how its uncounted return shows up in the high cistern upstream. Also, "the draw the Turn counted" is slightly off: the Turn counts hands, and draw follows shares ("each share returns labour by rota, and draw still follows shares").
- **E3 may sit uneasily with an unchanged line of B.** B's "What does not bind. A household's internal practice." stands next to E3's counting of the gift practice's labour for the window. This is arguable rather than a contradiction, because the gift practice is communal rather than one household's, and E3 marks the point as unconfirmed.
- **E5 §1 would read redundantly.** E5 replaces one sentence of a table cell whose next, unchanged sentence is "That reading is an assumption the author may reject." The replacement already says "the author may reject it", so the cell would say so twice.

5. **What I could not assess, and why**

- **E7.** File 09 has the E7 heading but no current or proposed text, so I cannot check the erratum. 08's statement that it is "now true for the candidate" holds for W4 but not for H1v3. The original (02) still says "upper cistern" three times (§3.2, Book 1, Book 6), and the packet does not say whether E7 is meant to cover the original.
- **H1-1 and H1-2.** 08 has blank stretches where these entries would be, so I have no before text for them. I judged F-12 and F-13 from 07 alone.
- **Files the packet refers to but does not include.** These are review-w3-to-w4.json, review-w4-to-h1v3.json, 04-h1-focused-delta.md (where H-E1 would apply), 05-consistency-record.md, 01-concept-comparison.md and the D file.
- **Schema validation.** I did not re-run it, because I have no access to the product's schema.

6. **Your context.** The packet sits in the scratchpad of a session whose working directory is a repository named "auteur", a narrative engineering toolkit. The branch name refers to a "wandering-islands" research stage. That repository's project instructions were loaded into my context automatically, but they say nothing about this architecture. I opened no file outside the packet and know nothing else about this architecture or any earlier review of it.
