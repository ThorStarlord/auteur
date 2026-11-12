# Stage F3 report, round 3 (verbatim)

**Packet:** `review/stage-f3-packet/` (copied from the packet folder used for the reviewer). It verifies the round-3 candidates W5 and H1v4 against W4, and the round-3 errata. The packet's file 09 keeps the text of errata E7, which the round-2 cleanup had removed.

**Reviewer:** one fresh general-purpose subagent, model Opus, one invocation. The reviewer self-identified as Claude Opus 5.5. It had no access to the Stage A, Stage B, Stage F or Stage F2 reports, to the adjudication, or to earlier versions of these corrections, except the before and after texts in its own packet.

**Freeze:** recorded after round 3 had been verified. Nothing below the line has been edited. Under the mission's stopping rule, round 3 is the last round of candidate changes, and its residual defects are recorded as open in the adjudication, not corrected.

---

1. **Identity.** I am Claude Opus 5.5 (claude-opus-5-5), acting as the independent reviewer. I read every file in the stageF3-packet folder: 00-reviewer-instructions.md, 01-findings.md, 02-original-architecture.md, 03-causal-construction.md, 04-finale-alternatives.md, 05-candidate-W4.json, 06-candidate-W5.json, 07-candidate-H1v4.json, 08-round3-changes.md and 09-prose-errata.md. I compared 05 with 06 field by field to confirm that W5-1, W5-2 and W5-3 are the only differences. I opened no other path, modified nothing and did not use the network.

2. **Table of items**

| ID | Judgment | Supporting quotation |
|---|---|---|
| ND-1 | Fixed | 06 `str_measured_turn`: "The counted Turn matches return to draw, which keeps the high cistern from surfeit." 06 `ph_3_old_hand`: "the counted Turn matches return to draw, which keeps the high terraces from surfeit" (409 characters, as claimed). E8: "matches return to draw, which keeps the high cistern from surfeit." All three now agree with 02 §2, "Surfeit (too much return, or stored water with no draw)". Neither the candidate nor the prose still credits labour as such. H1's `ph_3` no longer mentions the Turn, and H1's `str_measured_turn` carries the W5-1 text. |
| F-5 | Fixed | 06 `ph_5_unmeasured`: "The original's outcome is closest to A; its share-plot settlement is committed there; open here." This matches 02 Book 30, local closure: "the Compact takes a share-plot in lieu of claims". There is some tension with other text in 02; see observation 1. |
| ND-2 | New defect (both stated parts fixed) | Paragraph, proposed: "Mechanism 2 turns the same information into dependence. Mechanism 1 adds no dependence of its own". Principle, proposed: "the tally shows who maintains them", which now matches mechanism 4. Both stated defects are removed. E1 replaces only mechanism 1's body, so its old heading survives and contradicts the new paragraph (section 3). |
| T-1 | Fixed | 07 `ph_2_the_turn` activation: "draw separates from return and the high cistern thins (Book 6)". No instance of "upper cistern" remains in 05, 06 or 07. |
| E7 | New defect (rule sound, locator wrong) | E7: "which uses it in Books 1 and 6 and in the Book 6 closed future". The rule itself holds: the candidates use "high cistern" throughout, and 03 and 04 contain no "upper cistern". The cited locations are inaccurate (section 3). |

3. **New defects**

- **ND-2: mechanism 1's heading now contradicts the new paragraph. Caused by E1.** E1's "Mechanism 1, current" text starts at "Each practice's release depends…". The bold heading in 04 is therefore not replaced.
  - Side 1 (04, unchanged): "1. **Gate dependence.**"
  - Side 2 (E1, proposed): "Mechanism 1 adds no dependence of its own: it is a fact about the shared channels."
  - The new mechanism 1 body also no longer mentions the Gate at all. The label is now both stale and contradicted.
  - This is minor. A reader could take "of its own" to mean that the physical dependence exists before A and is not added by it.

- **E7: the restated erratum misstates where the original uses "upper cistern".**
  - Side 1 (E7): "which uses it in Books 1 and 6 and in the Book 6 closed future."
  - Side 2 (02, Book 6, closed futures): "a return to pre-open secrecy; any valley returning to the Hall's custody." The term does not occur there.
  - The original's actual uses are:
    - Book 1, enabled futures: "the first recorded thinning of the upper cistern"
    - Book 6, conflict: "The upper cistern thins"
    - §3.2, Source engine: "Consequence: the upper cistern thins"
  - The §3.2 use, the source of the phrase H1 reintroduced, is omitted, and a nonexistent one is named.
  - E7 also cites W4-4, which is not in the packet. 05 already reads "high cistern thins (Book 6)", which is consistent with it.

4. **Other observations, not part of this verification**

1. **F-5: "committed" versus the original's own provisional labels.**
   - 02 §1 lists "the Mill Compact's fate" under "[Open to author choice]".
   - 02 §7 lists "the Compact's end state" as "Provisional".
   - 02 §7 also lists the "Book 30 functions" as "Committed (sparse)".
   - So the original is ambivalent, and W5-3's "committed there" picks one reading. This is defensible, and I do not count it as a defect.
   - In the same `ph_5` field, the earlier sentence "the Compact's settlement is a clause of B or C" sits awkwardly next to an A-closest outcome that includes the settlement. 04's A also treats "The lowland share-plot settlement" as a failure mode of A, not a clause of B or C.
2. **`ph_5_unmeasured.narrative_function` is exactly 1000 characters.** The clipped "committed there; open here." looks compressed to fit the cap. If the cap is strictly below 1000, this field fails it. 08 gives no length check for W5-3.
3. **08's description of E8 is slightly inaccurate.** It says the replaced phrase "asserted the same claim through labour". The prose's current text, "The counted Turn (high terraces) keeps the high cistern from surfeit.", does not mention labour. The erratum itself is correct.

5. **What I could not assess**
- W4-4 and PR #553's `04-h1-focused-delta.md` are not in the packet. I checked the effect of W4-4 only through 05's text.
- 02 refers to the Studio candidate JSON and to files 01, 05 and D of the original set, none of which are in the packet.
- I cannot confirm that the 1000-character cap is inclusive.
- I cannot see the earlier review rounds, so my reading of each defect relies only on 01's wording.

6. **Your context:** none.
