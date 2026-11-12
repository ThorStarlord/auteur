# Stage F report, round 1 (verbatim)

**Packet:** `review/stage-f-packet/` (copied byte-for-byte from the packet folder used for the reviewer; it was built with the sources as they stood before round 2). The candidates it verifies are W2 (baseline), W3 (round 1) and H1v2 (round 1). The packet's file 08 lists the round-1 changes, and its file 09 the round-1 errata.

**Reviewer:** one fresh general-purpose subagent, model Opus, one invocation. The reviewer self-identified as Claude Opus 5.5. It had no access to the Stage A or Stage B reports, to the adjudication, or to any earlier version of these corrections. It read the ten packet files and reported opening no other path. Its automatically supplied session context included the repository's metadata, which it reported did not bear on the architecture.

**Freeze:** this report was recorded after round 2 had been derived in the corrections folder, and before round 2 was verified. Nothing below the line has been edited. Round 2 is not covered by this report.

---

**1. Identity.** I am Claude Opus 5.5 (claude-opus-5-5), working as an independent reviewer. I read only the ten files in `stageF-packet/`: 00-reviewer-instructions.md, 01-findings.md, 02-original-architecture.md, 03-causal-construction.md, 04-finale-alternatives.md, 05-candidate-W2.json, 06-candidate-W3.json, 07-candidate-H1v2.json, 08-candidate-corrections.md and 09-prose-errata.md. I modified, created and deleted nothing and did not use the network. I ran one read-only script over the JSON files to count characters and list the open questions.

Numbering note: file 09 refers to the prose files by their PR names. Its "01" is packet file 03, its "02" is packet file 04, and its "04" is the H1 path document, which is not in this packet.

**2. Table of findings**

| ID | Judgment | Supporting quotation |
|---|---|---|
| F-1 | Fixed | W3 `str_hollow_gate`: "the trial's uncounted return labour fed the high channels beyond the Turn's count, so stored water rose with no draw… Release draws the cistern down and cannot raise it." E5 §3(b), "The high cistern bears the drawdown", now agrees with 03 §3's Consequence: "Release at need in a dry spring draws the high cistern down." The current texts of both E5 items match 03 word for word. (See Other observation 1.) |
| F-2 | Fixed | W3-2: "each share returns labour by rota, and draw still follows shares." W3-2b: "for the first time in the series." Both agree with `th_hands_and_draw` ("Until Book 19 draw follows shares alone") and with 03 §2 ("For the first time in the series"). |
| F-3 | Partly fixed | The node is fixed: "The counted Turn's labour holds the high cistern against surfeit. The stewardship tally… records that labour…; it does not hold the water." The same defect remains in W3 `ph_3_old_hand.narrative_function`: "The stewardship tally records care, not debt, so the high terraces are not surfeited." H1v2's version of that phase drops the "so…" clause, but W3 keeps it. |
| F-4 | Fixed | "the Hall splits in Book 5, as the original has it." This matches 02 §4 Arc I (Books 1–5), whose exported state is "Hall split". |
| F-5 | Partly fixed | The omitted outcome is now named: "The original's adopted outcome is closest to A." The second half of the defect is not resolved. "its Compact settlement stays open" does not acknowledge that the original commits one ("the Compact takes a share-plot in lieu of claims", 02 §5 Book 30). It also sits awkwardly beside the preceding clause, "the Compact's settlement is a clause of B or C", while 04 A treats "The lowland share-plot settlement" as part of A's context. |
| F-6 | Fixed | W3 summary: "Also not decided: whether the Hollow Gate and the Gate Table are accepted parts of the world, and which body ratifies the instrument that Alternative C depends on." |
| F-7 | Partly fixed | The mechanism is fixed. E1's current text matches 04 exactly, and its proposed text removes both the dependence on the other practice's agreement and the penalty contradiction: "That is a physical consequence, not a penalty… A does not include that rule." The same coupling survives in A's Principle: "the schedule that follows the balance makes that dependence visible in each household's own release." The mechanism also keeps the heading "Gate dependence" but no longer mentions the Gate. |
| F-8 | Fixed | E2: "its authority over shares is the Right's holders' consent, not the Table's. A does not say who holds that authority if the lineage withholds consent." This agrees with the retained sentence "The Table has no authority over shares or the record." |
| F-9 | New defect (and partly fixed) | E3 answers whether gift shares are in the rota and names the keeper of the deficit record. It introduces two contradictions, set out in section 3. |
| F-10 | Fixed | E4: "The Reading Hall's published reading decides whether the rule applies." This matches C mechanism 2, "The Reading Hall reads it." (See Other observation 3.) |
| F-11 | Fixed | E6 removes the Book 20 leak claim: "a real surplus sits in the high cistern. The Table holds water back in dry spells instead of releasing it." The current text matches 03 §5 exactly. |
| F-12 | Fixed | H1v2 payoff 2: "the Reading Hall is the single public keeper of the record, an H1 consequence that reopens the finale's plural-record commitment (author-reserved)." The change is now declared. (See Other observation 4 on the "author-reserved" label.) |
| F-13 | Partly fixed | The sanction is declared: "The custody-until-Book-15 structure comes from the revision instruction, not from the author-proposed premise; its sanction is not recorded." The list of changes leaves out two that H1v2 itself makes. The Hall's split moves from Book 5 (the original's "Hall split" at the end of Arc I) to Book 15 ("At Book 15… the debt-keeping members become Corrow's remnant. The Hall is reformed, not destroyed"). Book 12's reading also changes ("The Book 12 partial reading is made under the committee's custody"). |
| F-14 | Fixed (content only) | H-E1: "Book 1's 'the Hall's sole custody of the Stones is never restored', and Book 6's 'any valley returning to the Hall's custody', both describe a state the committee holds in that window. These are H1 consequences. They are declared here." I could not check its placement (see section 5). The H1v2 candidate summary declares only the Book 1 closed future, not the Book 6 one. |
| F-15 | Fixed | H1v2 `open_questions[14]` (index checked): "what causes the custody transfer at Book 15, and does the Reading Hall, as the single public keeper of the record, become the custodial authority the finale must check?" Note that file 07 also appends "Does the Gate Table model reform from within or warn against it? Not decided." That sentence is not in 08's recorded "After" text. It is a record mismatch, not a defect. |

**3. New defects**

Both come from E3, the erratum for F-9.

- **E3 against B's Gate-schedule clause.** E3 adds: "The gift practice's shares are inside the window's rota." In the Long Rota, "hands are allocated per share by a published formula". Yet 04 B, "What binds" item 2, still says: "It binds the water, not the labour: the gift practice's labour stays uncounted." It also says, under "What does not bind": "A household's internal practice." If gift shares are inside the rota, their labour is allocated and counted, so these two statements now contradict each other.
- **E3 against the packet's author status.** E3 says: "The author confirms it." 04's header says: "None is the author's choice. The author decides…" 03's header says "no author has approved it." Read as written, E3 records an author decision that the packet says has not been made. If it means "the author must confirm it", the wording needs to say so.
- **Minor.** E3's heading names "What binds" and "What prevents capture", but it gives text only for "What binds".

**4. Other observations, not part of this verification**

1. **F-1 geography.** The new surfeit mechanism has Lower Ammen's trial labour feeding "the high channels". 03 §1 and W3 `str_unmeasured_return` place the gift practice on the lower channels. How labour in the lower valley raises the high cistern is not stated.
2. **E7's "throughout" claim.** E7 says "The construction uses 'high cistern' throughout." W3 `ph_2_the_turn` still reads "the upper cistern thins (Book 6)". The prose and the candidate also mix "upper channels" and "high channels".
3. **E4 and an author-reserved choice.** E4's "decides whether the rule applies" reads as automatic activation. 04 C's failure modes keep that open: "Whether activation is automatic or confirmed by the Table is an author choice." W3's open question 9 also leaves "who reads it" open. This is a small overreach and may be deliberate.
4. **H1-1's "(author-reserved)" label.** The plural-record outcome does not appear in 04's list of author-reserved decisions. 02 §7 lists the focal Book functions as "Committed". The label is reasonable, but nothing in the packet supports it.
5. **E1's physical consequence.** "cannot carry its own water" assumes that neglecting a shared channel harms only the household that neglected it. A shared channel usually harms all its users.

**5. What I could not assess**

- **Missing files.** 08 refers to `03-working-candidate-v2.json`, `w3-changes.md`, `make_w3_and_h1v2.py`, `make_h1_path.py`, `review-w2-to-w3.json`, `review-w3-to-h1v2.json` and H1-from-W2. None is in the packet. I could not verify the schema-validation claim, the claim that only the listed components changed, or the H1 "Before" texts. The H1v2 question that F-15 changes is not present in W2.
- **H-E1's placement.** It targets "04 §2 or §3" of the H1 path document, which is not in the packet. Packet file 04 is the finale alternatives.
- **What I could confirm.** The 986-character length of W3-4's narrative is correct (W2's was 903). The current texts of E1, E2, E4, E5 and E6 match packet files 03 and 04 exactly.

**6. Your context**

None. Apart from the agent-memory and project-instruction notes the host loaded into my context, which describe the toolkit (Auteur) and nothing about this series, I know nothing about this architecture from outside this folder.
