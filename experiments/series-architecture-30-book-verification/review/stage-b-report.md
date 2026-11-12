# Stage B review report (verbatim)

**Packet:** `review/stage-b-packet/` (copied byte-for-byte from the frozen packet folder; manifest in `review/stage-b-manifest.json`). The H1 candidate is file 09, with hash prefix `face0464…`, the same as the recorded H1-from-W2.

**Reviewer:** one fresh general-purpose subagent, model Opus, one invocation. The reviewer reported its own identity as "Claude Opus 5.5 (model ID claude-opus-5-5)". It had no access to the Stage A report, to the construction's earlier reviews, to the coordinator's adjudication, or to `07-synthesis.md`. It read the eleven packet files and reported opening no other path.

**Known exposure, recorded for independence:** as in Stage A, the reviewer's automatically supplied session context included repository metadata: the auteur repository's name and a git status header naming an unrelated branch. It reported that it opened no repository file and that this metadata did not inform its findings. It did not see the Stage A report, or the Stage A packet's content beyond the Stage B packet itself.

**Freeze:** this report is recorded before the crisis was frozen and before any adjudication. Nothing below the line has been edited.

---

I am Claude Opus 5.5 (model ID claude-opus-5-5). I read all eleven files in the Stage B packet folder: 00-reviewer-instructions.md, 01-author-brief.md, 02-original-architecture.md, 03-causal-construction.md, 04-finale-alternatives.md, 05-candidate-W2.json, 06-source-identity.md, 07-h1-premise.md, 08-h1-focused-instruction.txt, 09-candidate-H1-from-W2.json and 10-h1-changes.md. I opened no other path, modified no file and did not use the network.

---

## 1. Overall assessment

H1 keeps two things apart and keeps them apart everywhere: public access to the records from Book 5, and the committee's physical custody of the Stones and the master record until Book 15. The three loops, the Arc II trade mechanism, the Book 15 gift reading, the Unmeasured Return and the Arc IV conflicts all survive. No new antagonist appears.

The revision falls short in four ways:

- **It changes things outside the premise.** It replaces a Book 30 commitment ("no single institution holds the record") with "one public keeper". Nothing in the premise requires this, and it contradicts the original.
- **It leaves old claims in place.** The summary still says Books 1–15 "keep the original's events". The original's Book 1 and Book 6 closed futures, which H1 now contradicts, are not revisited.
- **The handover has no mechanism.** Nothing says who makes the Book 15 full reading while the committee holds the Stones, or why custody then passes to the Reading Hall.
- **Book 1 agency is weakened.** Idrun becomes "a lower-terrace household". It is not said whether Dorran's Book 1 defection still happens.

The new open question is aimed at the wrong place. The finale alternatives were not re-checked against a Reading Hall that now holds both custody and the readings. H1 is coherent as a premise, but this revision only partly carries it through.

## 2. Findings (most consequential first)

**R1. Verified defect. The Book 30 end state changes beyond the premise.**
- **Location:** file 09, `gn_political_institutional` payoff_expectations[1]; `ph_3_old_hand.transition`.
- **Quotation:** H1 says "in Book 30 the record has one public keeper" and "so the record has one public keeper while the readings stay plural". File 02 §5, Book 30, says "no single institution holds the record". W2's payoff said "no single institution holds the record".
- **Explanation:** H1, in both file 07 and file 08, concerns Books 5–15. It does not touch the Book 30 end state, yet the revision rewrites a finale commitment. The file 09 summary still says it is "Built on the original … which it does not modify".
  - W2 already had a latent tension. `th_custody` called custody "plural", while `inst_reading_hall` said it "Keeps the public record". H1 settles that tension in the singular direction without flagging the choice.
  - The change also affects the finale alternatives, which were left unchanged. Under H1, the Reading Hall from Book 15 holds custody of the Stones and the master record, the readings, the gauge and the Balance Stones. That is close to the Hall's old pairing of custody and reading.
  - `alt_b_allotted` lists "the Hall's custody returning under another name" as a failure mode. `alt_c_ratified_trigger` lists "activation by the Reading Hall's reading may be unchecked". Under H1 the first is partly realised at Book 15, and the second becomes more dangerous.
- **What would settle it:** either restore plural custody at Book 30 and give it a mechanism, or mark "one public keeper" as a declared H1 consequence and re-check alt A, alt B, alt C and `ph_5` against it.

**R2. Verified defect. The summary contradicts the revision.**
- **Location:** file 09, top-level `summary`.
- **Quotation:** "Books 1-15 keep the original's events. The working construction corrects one thing in them."
- **Explanation:** H1 changes several Book 1–15 events:
  - Book 5 becomes a reform where the original had dissolution (W2: "the Hall dissolves in Book 5").
  - Dorran no longer defects.
  - Custody stays with the Hall until Book 15.
  - Book 8 is now "authored by the committee".
  - The committee sets the sale rules.

  The script prefixed an H1 paragraph to the summary but did not remove the W2 claims it falsifies.
- **What would settle it:** rewrite the summary so it lists the H1 changes to Books 1–15.

**R3. Verified defect. The original's closed futures are contradicted and were not revisited.**
- **Location:** file 02 §5, Book 1 and Book 6 "Closed futures", against file 09 `inst_stone_hall`, `th_custody` and `ph_2_the_turn`.
- **Quotation:** Book 1 says "the Hall's sole custody of the Stones is never restored". Book 6 closes off "any valley returning to the Hall's custody". H1 says "The reform committee keeps physical custody of the Stones and the master record … until Book 15".
- **Explanation:** under H1 the Hall's sole physical custody runs unbroken from Book 1 to Book 15. Valleys in Books 6–15 trade under "the committee's sale rules", which puts them under Hall custody and rules. Because file 09 claims Books 1–15 are kept (R2), these closed futures still apply, and they are false.
- **What would settle it:** restate both closed futures under H1, for example "sealed custody is never restored" for Book 1, or narrow them in some other way.

**R4. Unresolved question with a credible concern. Book 1 agency and Dorran's timeline.**
- **Location:** file 09 `ph_1_reckoned_water.narrative_function` and `th_witness`; file 02 §5 Book 1 and Book 6.
- **Quotation:** "Dorran carries the reform as messenger rather than defecting." The W2 sentence "Protagonist's agency comes from evidence and a coalition, not inheritance" is removed.
- **Explanation:**
  - In the original, Idrun and Dorran read the Stone, prove the false credit, restore the channel with a night of return labour, and the share is corrected. Dorran defects in Book 1.
  - H1 does not say when Dorran's non-defection happens. If he never defects, his Book 1 lamp-reading of a sealed Stone needs a reason: was it sanctioned or covert?
  - Book 6 in the original has Dorran argue that "the Hall hoarded unsold shares". As the Hall's messenger he would be indicting his own institution.
  - Idrun is no longer named in file 09. Her agency in Books 1–5 shrinks to supplying "evidence" that "forces the timing". Nothing in file 09 still records the Book 1 local closure (share corrected, flood stopped, uncounted return labour).
- **What would settle it:** state Dorran's status in Book 1 and in Book 5, and restore Idrun's Book 1 actions and closure in `ph_1`.

**R5. Unsupported claim. The custody transfer at Book 15 has no mechanism.**
- **Location:** file 09 `ph_3_old_hand`, `inst_reading_hall` and `l_custody_passes_reading_hall`.
- **Quotation:** "the committee's custody ends with it: custody passes to the Reading Hall". The Reading Hall is "Founded at Book 15 with the full reading". W2 said "Founded after the full reading".
- **Explanation:** the order of events is now circular. The Reading Hall is founded with the full reading and takes custody at the same moment. The committee holds the Stones until then and keeps the debt reading. Nothing says:
  - who performs the gift reading, or with whose access;
  - why a committee with an interest in the debt reading would allow it;
  - who founds the Reading Hall;
  - what compels the handover: a Council vote, the evidence, or Corrow's own split.

  The handover is asserted, not caused.
- **What would settle it:** name the actor, the access route and the force that ends the committee's custody.

**R6. Credible concern. Nothing is said about who has authority over shares in Books 5–15.**
- **Location:** file 09 `ph_1.transition` and `ph_2_the_turn`; file 02 Book 6 local closure.
- **Quotation:** "the reform committee, not the tenders, sets the first rules of sale". File 02 has "Compact purchases are capped at a fixed proportion".
- **Explanation:**
  - Between Book 6 and Book 15 the committee holds the master record and the sale rules, and the Council schedules the Turn. It is unclear who imposes the Book 6 cap, and whether the committee must consent to it.
  - No guard is stated against the custodian falsifying the master record again. Only "access" is public, and the Book 1 falsification happened inside the record.
- **What would settle it:** assign who sets the cap and who records shares, and say whether public copies can be checked against the master record.

**R7. Credible concern. The Book 8 and Book 12 readings are underspecified under committee custody.**
- **Location:** file 09 `ph_2_the_turn` and `ph_3_old_hand`; `th_reading` (unchanged).
- **Quotation:** Book 8 is "authored by the committee and contested by scholars". Book 12 is "made under the committee's custody".
- **Explanation:**
  - The two readings are treated unevenly. Book 8 has an author; Book 12 does not.
  - In file 02, Book 12 is the Compact's contract reading. It is unclear whether the committee grants the Compact access.
  - `th_reading` ("Who may read the oldest script") is unchanged, but under H1 the committee decides who may read. The thread is now incomplete.
  - The reading schedule still satisfies "no indefinitely postponed revelations". But a custodian with a debt interest controls access, which increases the stated risk in `gi_mystery_epic_enables` ("readings postponed into a withheld revelation"), and no motive for the committee's cooperation is given.
- **What would settle it:** say whether the Book 8 reading leans towards debt, who authors Book 12, and why the committee allows both readings.

**R8. Credible concern. The new open question is aimed at the wrong place.**
- **Location:** file 09 `open_questions[14]`.
- **Quotation:** "does the Hall become a benevolent authority that the finale must oppose?"
- **Explanation:** under H1 the Hall loses custody at Book 15 and is a remnant "outside the Gate Table" in Arc IV. By the finale it has no authority to oppose. The genuinely new questions H1 creates go unnamed:
  - what causes the Book 15 transfer (R5);
  - whether the Reading Hall, as the single keeper, becomes the new custodial authority (R1).

  The question also absorbs W2's reform-stance question, which file 06 lists as author-reserved. That merge is acceptable, but it moves the focus away from where the risk sits.
- **What would settle it:** rephrase the question around the transfer and around the Reading Hall's custody.

**R9. Unresolved question. Provenance of the custody-until-Book-15 structure.**
- **Location:** file 07 compared with file 08.
- **Quotation:** file 07 says "its committee keeps the debt reading", with no end date. File 08 adds "keeps PHYSICAL CUSTODY … until Book 15; at Book 15 custody passes to the Reading Hall".
- **Explanation:** the core structural change (custody until Book 15, then transfer) is in the instruction, not in the author-proposed premise. The same applies to the "Gate Table seat of the remnant". I cannot tell whether the author sanctioned these additions.
- **What would settle it:** author confirmation that the file 08 additions belong to H1.

**R10. Unresolved question. The referent of the bittersweet complex emotion.**
- **Location:** file 09 `ce_bittersweet_return`.
- **Quotation:** "a practice honoured after the institution that held it has lost custody of it".
- **Explanation:** custody applies to the record, not to a practice. The only institution that loses custody is the Hall, and its "practice" (the debt ledger) is not honoured by others; the remnant keeps it. The emotion belongs to the pastoral contract, whose practice (the Turn) is held by the Council, which never loses custody. The revision changed the wording but did not fix which practice is meant.
- **What would settle it:** name the practice and the institution.

**R11. Unsupported claim. The causal link between thinning and the reform.**
- **Location:** file 09 `ph_1.narrative_function`.
- **Quotation:** "protects the Hall's standing against a thinning its own falsified credit helped cause".
- **Explanation:** no mechanism shows how falsified credit causes thinning, or how opening the records counters it. Under loop L3, opening the records leads to trade, which thins the spring further. That irony would suit the brief ("conflicts from earlier successes") if it were stated. W2's transition clause "the spring shows its first recorded thinning" was dropped without a replacement.

**R12. Unresolved question. Book 5 timing and the description of the original path.**
- **Location:** file 09 `th_witness`.
- **Quotation:** "evidence forces the timing … (Book 5)" and "In the original path the same evidence, with a coalition from outside".
- **Explanation:** the falsification was proven in Book 1, so it is unclear what forces the timing four Books later. Calling the original coalition "from outside" is also inexact, because Dorran was a Stone Hall apprentice. That wording comes from the instruction (file 06 notes this).

**R13. Minor credible concern. Corrow's remnant in Arc IV.**
- **Location:** file 09 `ph_4_settled_water`.
- **Quotation:** "Corrow's remnant (the debt reading) stands outside the Gate Table and argues for counting."
- **Explanation:** this is consistent with `inst_gate_table`, which gives seats to practices, and a reading is not a practice. W2 had no remnant seat, so the instruction referred to a seat that did not exist, and the revision correctly declined to invent one.
  - However, the remnant's natural position is Conflict A option (a), "the debt reading returns through the tally". It is placed in Conflict B instead.
  - No link connects `inst_stone_hall` to any Arc IV node.
  - "Argues for counting" blurs the remnant's position with the counted Turn, which does have a seat.
  - `l_reform_keeps_debt` ("until Book 15") wrongly implies the debt reading stops at Book 15.

**R14. Deliberate author choice. The reform stance and finales A, B and C.**
- **Location:** file 06 author-reserved list; file 09 alternative nodes.
- **Explanation:** these remain open, which is correct. H1 changes what is at stake in them. Alternative B's "Readers will hear the Hall in it" (file 04) now echoes a reforming Hall rather than a fallen one, and the Gate Table as "model or warning" now has a precedent of internal reform. The revision does not note this.

## 3. Preserved-element table

| Element | Status under H1 | Reason |
|---|---|---|
| et_wonder | valid | Its triggers are unaffected by the custody change: "the first chamber beneath the spring (Book 1) and the First Stones read in full (Book 15)". Book 15 now also depends on R5. |
| et_belonging | valid | Return labour does not depend on who holds the record: "return work completed together by people who have few reasons to trust one another". |
| et_hope | valid | Arguably strengthened. Public access, begun by the Hall itself, outlasts the Hall's custody: "a shared practice can outlast the institution that began it". |
| et_grief_of_orders (changed) | valid | Moved coherently. The reformer-turned-loser keeps the dignity the target asks for: "the committee's loss of custody at Book 15 and Keeper Corrow's remnant's dissent". Arc I loses its grief beat. |
| et_anger_at_hidden_credit | valid | The trigger still holds: "the falsified lower-terrace share in Book 1". Its payoff is weaker, because the falsifying institution keeps custody until Book 15 (R3). |
| et_fear_of_wild_water | valid | Its events (Book 1, Book 21, the pulse) are untouched: "lower terraces running wild in Book 1, a household's declined share in Book 21". |
| et_cost_of_counting | valid | Arc IV Conflict A is preserved: "the hands-to-draw conversion adopted in Book 20". |
| ce_awe_of_source | valid | Physical wonder does not depend on custody: "wonder that turns into care rather than fear". |
| ce_bittersweet_return (changed) | unclear | The referent is mismatched (R10): "the institution that held it has lost custody of it", but custody belongs to a record, not a practice. |
| gn_epic_fantasy | valid | The trope "the keepers' authority reversed by public reading" now applies literally at Book 15, but the reversal has no mechanism (R5). |
| gn_pastoral_belonging | unclear | It bundles ce_bittersweet_return (unclear) and the relocated grief, a custody event that is institutional rather than pastoral: "complex_emotion_ids: ['ce_bittersweet_return']". |
| gn_political_institutional (changed) | unclear | The first payoff is valid: "monopoly of access ends in Book 5; its monopoly of custody ends in Book 15". The second, "the record has one public keeper", contradicts file 02 Book 30 (R1). The trope "compromise that feeds a new monopoly" now points nowhere specific. |
| gn_mystery_discovery | valid | The reframing still holds under H1: "the gift reading in Book 15 reframes the Book 1 debt". |

## 4. Justified strengths

- **Access and custody are kept apart consistently.** The split between public access (Book 5) and physical custody (Book 15) is the same in `th_custody`, `inst_stone_hall`, `eng_ledger`, `ph_1`, `ph_3`, `l_custody_grants_hall` and the first political payoff. This handles the premise's central ambiguity.
- **The preserved mechanisms are actually preserved.** Loops L1, L2 and L3, the Arc II trade mechanism, the Book 15 gift reading, the Unmeasured Return and both Arc IV conflicts survive in meaning, not just in identifier. The Arc II changes add authorship ("under the committee's sale rules") without altering the mechanism.
- **The reformer is also the loser.** Corrow is both the reformer and, at Book 15, the losing party. That fits the grief target's "reasons that are coherent from their side" and avoids creating a villain.
- **No seat was invented.** The revision did not create a Gate Table seat that W2 never had, which respects the Table's limit to practices.
- **The hypothetical status is labelled.** The summary marks the revision as hypothetical, and no new threat or postponed revelation is introduced.

## 5. What I could not assess

- **Withheld passages:** the designer's self-assessments, the advocacy paragraph and the nomination section.
- **Documents referred to but not in the packet:** 01-concept-comparison.md, D-product-capability-observations.md, 05-consistency-record.md, the "renewal test R2", the evidence revision-instruction.txt, make_h1_path.py, make_stage_b_packet.py, PR #551 and #553, A-studio-candidate-original.json, and the first review packet.
- **The "witness-led repair R-A":** file 07 names it but never defines it, so I could not check whether the revision implements it beyond `th_witness`.
- **Author sanction:** I could not tell whether the author approved the additions in file 08 that go beyond file 07 (R9).
- **Elements I did not tabulate:** I checked trope functions in phases and genre interactions only where they were affected. `gi_mystery_epic_enables` has a heightened risk (R7). The other genre interactions remain valid.

## 6. My context

I know nothing about this architecture's content from outside the folder. Session metadata I was given automatically indicates that this review runs inside a narrative-engineering toolkit repository ("auteur"). The current branch is named `research/wandering-islands-stage4j-targeted-literary-correction-20261110`. I did not open any repository file, and this knowledge did not inform the findings.
