# Stage A review report (verbatim)

**Packet:** `review/stage-a-packet/` (copied byte-for-byte from the frozen packet folder; manifest in `review/stage-a-manifest.json`).

**Reviewer:** one fresh general-purpose subagent, model Opus, one invocation. The reviewer reported its own identity as "Claude Opus 5.5 (model ID claude-opus-5-5)". It had no access to the construction's earlier reviews, to the coordinator's adjudication, or to `07-synthesis.md`. It read the seven packet files and reported opening no other path.

**Known exposure, recorded for independence:** the reviewer's automatically supplied session context included the repository's `CLAUDE.md`, the user's memory index and a git status header naming an unrelated branch. The reviewer reported that none of these concerns this architecture and that it opened none of those files. It did not see the construction files, the earlier reviews, or the earlier candidate.

**Freeze:** this report is recorded before the Stage B reviewer was launched and before any adjudication. Nothing below the line has been edited.

---

I am Claude Opus 5.5 (model ID claude-opus-5-5). I read only the seven files in the packet folder: 00-reviewer-instructions.md, 01-author-brief.md, 02-original-architecture.md, 03-causal-construction.md, 04-finale-alternatives.md, 05-candidate-W2.json and 06-source-identity.md. I opened no other path, changed no file and did not use the network.

## 1. Overall assessment

The construction's overall shape holds up. Arc IV's two conflicts come from Books 6 and 15. They create different pressures: labour on one side, coordination at the Gate on the other. They map cleanly onto the two physical needs of Book 30.

The problems sit one level down, in how the parts work together. Five are the most consequential:

- **Alternative A** brings back, through the Gate, the hands-to-water link it says it removes. Its care floor has no body with the instrument or the authority to run it.
- **Alternative B** applies a per-share binding rota while saying the gift practice's labour stays uncounted. "Binding" means at least three different things in it.
- **Alternative C** names two different readers of the gauge. It has no way to challenge a reading, and both of its activation options break the separation between schedule and record.
- **The physics of the Hollow Gate** is stated in opposite directions in different places.
- **Cross-artifact drift:** at least four statements disagree between files, and none of these changes is declared.

The Hollow Gate addition is modest in physical terms. But everything in Arc IV and Book 30 depends on it, and its acceptance as part of the world is still reserved to the author. Most findings can be fixed by stating a rule more precisely. None requires abandoning the architecture.

## 2. Findings

**R1. Area B. Verified defect.**
- **Location:** file 04, Alternative A, mechanisms 1 and 5 and "Effect on the governing variable"; file 05, `alt_a_reciprocal`.
- **Quotes:**
  - "Draw no longer depends on hands."
  - "A terrace that stops returning labour to the shared channels loses its own release at the next thaw. Nobody issues a penalty."
  - "Each practice's release depends on the Gate schedule the other practice agrees to."
- **Explanation:** Mechanism 1 mixes three different causes:
  - A physical consequence: an unmaintained channel cannot carry its water. This is not a penalty, and it fits with the floor.
  - Institutional scheduling: "the schedule follows the balance reading". The gauge reads the whole spring's balance at the Gate, so it cannot single out one terrace's labour. A terrace's release falls only if the Table applies a rule linking that terrace's labour to its release. That rule would be a penalty.
  - Deliberate withholding: release that depends on what "the other practice agrees to" is a sanction one party can choose to impose.

  Only the first cause is "no penalty". The second and third bring back the hands-to-draw link at terrace level. That contradicts the floor too: a terrace made up of hand-light households loses water for lacking labour. The gauge cannot tell inability from refusal, and under the correlated shock A already names, inability is exactly what it would see.
- **What would settle it:** Restrict mechanism 1 to the physical consequence. Alternatively, admit a scheduling rule and list it as a soft sanction among A's costs.

**R2. Area B. Credible architectural concern.**
- **Location:** file 04, Alternative A, mechanisms 3 and 5; file 03 §2 (the Right is "revocable by the Council").
- **Quote:** "The floor is funded by the lineage's Right, and the Gate Table administers it. The Table has no authority over shares or the record."
- **Explanation:** A floor on draw needs three things:
  - Knowing which households lack hands. That is the tally, which belongs to the Council and the Reading Hall.
  - Moving draw from the holders of the Right to households under the floor. That reallocates honoured claims, which is authority over draw. The Right is also revocable by the Council, not by the Table.
  - Delivering water to individual households. The Gate only splits the release between upper and lower channels, so it cannot reach a household.

  The Table has none of the three. Using the Right to fund the floor also cuts against mechanism 3, which uses the same Right as the incentive for training apprentices. It also feeds the "craft withdrawal" failure that A already lists.
- **What would settle it:** Name the body that holds the floor (probably the Council or a ratified instrument), its source of water, and how the water is delivered. Alternatively, accept that the Table gains a narrow authority over draw, and say so.

**R3. Area C. Verified defect: an unacknowledged change to the gift practice.**
- **Location:** file 04, Alternative B, "What binds" items 1 and 2, and "What does not bind".
- **Quotes:**
  - "hands are allocated per share by a published formula"
  - "the gift practice's labour stays uncounted"
  - "What does not bind. A household's internal practice."
- **Explanation:** Lower Ammen households hold shares, and the Lowfen is their channel and the main rebuild target. Two outcomes are possible, and both are problems:
  - If the Long Rota covers them, their labour is allocated, measured and carried as a deficit. That is counting, and B denies it.
  - If the Long Rota does not cover them, the households served by the main rebuild channel are exempt from the rebuild. The text never says so.

  Either way, B changes the gift practice without saying it does.
- **What would settle it:** State whether gift-practice shares are inside the Long Rota. If they are, list "the gift practice is counted for one window" as a cost of B.

**R4. Area C. Credible architectural concern: several incompatible meanings of "binding".**
- **Location:** file 04, Alternative B, the "Principle" and "Freedom" paragraphs, the Compact clause, and the effect statement.
- **Quotes:**
  - "Binding is confined to the rebuild window"
  - "a shortfall becomes a deficit to be repaid"
  - "Its allocation expires at the end of the cycle"
  - "The Compact may refuse grain-labour, and then its fate is open."
- **Explanation:** Binding works differently for each party:
  - **Households:** binding means refusal costs the window's draw.
  - **The gift practice:** the schedule binds its water but not its labour.
  - **The Compact:** its contribution is listed under "What binds", yet the Compact can refuse at no defined cost and has no seat. In practice its contribution is a negotiated contract, which is exactly the Compact's own reading of the Stones.
  - **Deficits:** a deficit "to be repaid" must either outlast the window and the sunset, or lapse at it. If it outlasts them, binding is not confined to the window, and someone keeps a debt record. Only the Reading Hall keeps records, and that would bring back the Hall's debt ledger. If it lapses, it is not a binding obligation.
- **What would settle it:** Define where repayment of a deficit ends and who records it. Move the Compact clause from "binds" to "negotiated".

**R5. Area C. Credible architectural concern.**
- **Location:** file 04, Alternative B, "Freedom" and "Fairness".
- **Quotes:**
  - "a household forfeits the window's draw, not its share"
  - "a shortfall becomes a deficit to be repaid, not a cut in water"
- **Explanation:** The two rules are coherent as rules about different causes: a shortfall from inability, and refusal. But no body is given the job of deciding which case a household is in. The outcomes are very different: a deficit in one case, losing the whole window's water in the other. The losing outcome is harsher than Arc IV's proportional conversion, which B claims only to suspend.
- **What would settle it:** Assign who decides "short" versus "refusing", and give a way to appeal.

**R6. Area D. Verified inconsistency plus a credible concern.**
- **Location:** file 04, Alternative C, mechanism 2, the Costs, and the Failure modes; Alternative A, mechanism 6.
- **Quotes:**
  - "The Reading Hall reads it."
  - "The surveyor's reading decides whether the rule applies."
  - "Disputes about meaning go to the Reading Hall."
- **Explanation:** In file 02, the surveyor is a Council role: Tarn "becomes a Council surveyor". So C names two different readers. Taking the questions in turn:
  - **Who decides whether the threshold has been crossed:** this is not stated.
  - **Who activates the rule:** the text leaves it as an author choice between automatic activation and confirmation by the Table.
  - **Who can challenge a mistaken reading:** nobody independent. Disputes go back to the Reading Hall, so the reader would judge challenges to its own reading.
  - **Whether the separation survives activation:** it does not, under either option.
    - With automatic activation, reading and binding join. The text acknowledges this.
    - With confirmation, the Table rules on what the gauge means. That takes reading authority into the scheduling body, the reverse breach, which the text does not notice.

  There is also a transition problem. In normal seasons the Table has A's composition, while activation requires B's "lot seats". Someone has to redraw the seats at the moment of crisis, and the text does not say who.
- **What would settle it:**
  - Name one reader.
  - Give confirmation to a third party, such as a joint panel or a challenge window with a default.
  - Specify how the Table is reconstituted at activation.

**R7. Area D. Credible architectural concern.**
- **Location:** file 04, Alternative C, the Costs; file 03 §6.
- **Quotes:**
  - "Few people attend to a rule for a pulse that has not come yet."
  - "The rule may be stale by the time the cycle arrives."
  - "The Balance Stones … show that its date is approaching."
- **Explanation:** The pulse is dated and has been predicted since Book 23. Ratification happens in Books 27–29, roughly 1.5 to 4.5 years before it. That undercuts the "calm years" and "stale rule" costs. It also leaves the trigger without an obvious purpose. A threshold earns its place only if the pulse's size or timing is uncertain, and the text never establishes that uncertainty.
- **What would settle it:** Make the pulse's magnitude uncertain, for example a known date but an unknown volume. Alternatively, restate C's costs.

**R8. Areas A and E. Verified defect: the physics runs in opposite directions.**
- **Location:** file 03 §1 (the Hollow Gate row) and §3; file 05, `str_hollow_gate`.
- **Quotes:**
  - Book 15: "reads the surfeit as an effect of the release the trial's schedule carried to the lower channels"
  - Book 21: release at need "draws the high cistern down. Its high channels dry"
  - Option (b): "The high terraces absorb the surplus."
- **Explanation:** File 02 defines surfeit as "too much return, or stored water with no draw". Releasing water out of the high cistern is draw, so it would lower the risk of surfeit, not cause it. Release to the lower channels is said to produce surfeit upstream in Book 15 and to drain the cistern in Book 21. No seasonal difference is stated to reconcile the two.

  Option (b) also refers to a "surplus" in a dry spring whose stated consequence is a shortfall. The text does flag the Book 15 reading as an assumption, but that assumption contradicts the defined physics.
- **What would settle it:** Reattribute the Book 15 surfeit to excess uncounted return, which the original definition allows. Change "surplus" in option (b) to "shortfall".

**R9. Area A. Credible architectural concern plus a deliberate author choice.**
- **Location:** file 03 §1 and §6; file 05, `str_hollow_gate`, `str_long_return` and `open_questions`; file 06, the author-reserved list.
- **Quotes:**
  - "the sluice that divides the high cistern's release between the upper and lower channels"
  - "The Gate must split the pulse between the high cistern and the lower channels."
- **Explanation:** These two descriptions place the Gate differently. In the first it sits below the cistern. In the second it sits between the cistern and the channels and can send the pulse into the cistern. Physically the addition is modest: the original already has an upper and a lower system that can thin or flood independently. Retroactively making the Council the Gate's operator also widens the Council's Book 6 mandate, which was "to schedule the Turn".

  The larger issue is dependence. Conflict B, the Gate Table, the Book 23 surplus, Book 30's routing need, and all three alternatives rest on the Gate. File 06 reserves "whether the Hollow Gate and the Gate Table are accepted" to the author. File 05's 16 open questions, which are at the schema cap, do not record it.
- **What would settle it:** Fix the topology: deep store, then cistern, then Gate, then channels. State who ran the Gate before Book 6. Carry the acceptance question in file 05.

**R10. Areas A and E. Verified defect.**
- **Location:** file 03 §5 against file 03 §2.
- **Quotes:**
  - "lineage crews have sealed the leaks in the high channels that used to feed wild water (Book 20)"
  - "Lineage crews repair the Lowfen."
- **Explanation:** The Book 20 repair was to the Lowfen, a lower channel. One of the two causes given for the Book 23 surplus cites work that Arc IV never contains.
- **What would settle it:** Add high-channel sealing to Book 20, or remove that cause from §5.

**R11. Area E. Verified defect: three incompatible statements about when hands first set draw.**
- **Location:** file 03 §2; file 05, `th_hands_and_draw`, `str_measured_turn` and `ph_4_settled_water`.
- **Quotes:**
  - "For the first time in the series, a household's hands set part of its draw."
  - "Until Book 19 draw follows shares alone."
  - "Draw matched to labour in the high terraces, run by the Council since the Turn in Book 6."
  - "hands set part of draw for the first time since Book 6"
- **Explanation:** The same governing variable gets three different histories. If draw has matched labour since Book 6, the Arc IV conversion is not a first, and A's "reversal" would reverse Book 6 as well.
- **What would settle it:** Decide whether the counted Turn ties draw to labour or only ties labour to shares, then align all four places.

**R12. Area E. Verified cross-artifact inconsistency.**
- **Location:** file 05, `inst_stone_hall`, against file 02 §3.1, §4 and Book 6.
- **Quote:** "Under this working path the Hall dissolves in Book 5".
- **Explanation:** The original says "Hall split". Its Book 6 closed futures include "any valley returning to the Hall's custody", which implies the Hall still has custody somewhere after Book 5. File 05's summary declares only one correction (Book 1 and Book 8) and two clarifications (the Gate and the tally). The dissolution is not among them.
- **What would settle it:** Declare it as a correction or revert it.

**R13. Area A. Credible architectural concern.**
- **Location:** file 03 §2 and §4.
- **Quotes:**
  - Conflict A trigger: "the Lowfen channel, which carries Lower Ammen's wells"
  - Outcome: "Hand-light share-holders have their draw converted in proportion to their deficit."
  - Conflict B option (a): "counts the lower valley's water, which repeats the Hall's pattern"
- **Explanation:** There are two gaps:
  - If the conversion applies to Lower Ammen households, the Council counts gift-practice labour in Book 20. That is a step Book 21 then treats as unacceptable, and the Council's remit is "the counted Turn in the high terraces".
  - The conversion applies the principle "hands set draw" to poor households but not to the Compact's draw, which carries no hands at all. The text notes "The Compact's unhanded draw continues", but gives no reason for the exemption, such as contract protection or the Book 6 cap.
- **What would settle it:** State the conversion's jurisdiction and the reason the Compact is exempt.

**R14. Area A. Credible architectural concern, partly acknowledged.**
- **Location:** file 03 §5; file 02 Book 23; file 05, open question 10.
- **Quotes:**
  - "the Turn burdens households with few hands, including Hesper's own"
  - "Hand-light houses have drawn less since Book 20"
  - Her cohort holds "a belief that abundance needs no work"
- **Explanation:** Hesper's household had its water cut for lacking hands when she was about seven. That makes her an unlikely holder of the belief that abundance needs no work. She also leads a festival that displays high-cistern water "drawn by the hands that already had it". Her access to that water is not explained.
- **What would settle it:** Give a route by which she reaches the water, and show how her belief survives her own household's cut.

**R15. Area E. Credible architectural concern and deliberate author choice.**
- **Location:** file 02 Book 30 and §7 ("Committed: … Books 1, 6, 15, 23, 30 functions"), against file 04's "Author-reserved decisions".
- **Quotes:**
  - Original: "shared accounting of care, which informs but binds no one"; "The Turn persists, changed: no longer mandatory."
  - File 04: "Whether the shared accounting of care binds at all, and in what form." Under B and C, the Turn is mandatory for the window.
- **Explanation:** Reopening the finale is legitimate. But it changes a committed function of the original, and the construction does not declare that it does. File 05 maps the original's measured-Turn option and the Compact's settlement onto the new alternatives, but not the option the original actually adopted, which is approximately A. The original also contradicts itself here, because it commits the Compact's share-plot outcome while listing the Compact's fate as Open.
- **What would settle it:** Record this as an explicit correction.

**R16. Areas C and D. Unsupported claim.**
- **Location:** file 04, Alternative B ("unless the terraces ratify a renewal") and Alternative C ("the valley ratifies one instrument").
- **Explanation:** No body in the architecture can ratify for the whole valley. The Council governs the counted Turn, the Table governs only the schedule, and the Reading Hall governs only the record. Both B's sunset and all of C depend on a procedure that does not exist.
- **What would settle it:** Name the ratifying assembly and its quorum across both practices.

**R17. Unsupported claims about the physics.**
- **Location:** file 03 §6; file 02 Book 15; file 05, `ph_3_old_hand`.
- **Explanation:** Three causal claims have no mechanism behind them:
  - A balance gauge, which measures the gap between draw and return, "predicts" the date of a deep-store pulse.
  - A record of care keeps "the high terraces [from] surfeit", or "forces" a tally. Recording something is not a physical intervention. This one is inherited from the original and not fixed.
  - The Long Return's earlier occurrences are never seeded. A First Stones record of them, for instance, would answer the brief's ban on "arbitrary new threats".

**R18. Unresolved questions.**
- **Fate of the forfeited share (Book 21):** who holds it, and could the Compact buy it? It is still running wild at Book 30, and it is listed among Arc IV's exports.
- **Reach of the Gate:** file 02 has the Turn sworn "in Quillmark and two neighbouring valleys". It is unclear whether one Hollow Gate serves all three.
- **Two cistern names:** file 02 uses both "upper cistern" (Books 1 and 6) and "high cistern" (Books 15 and 23). The construction assumes they are the same structure.

## 3. Justified strengths

- **Arc IV comes from existing history.** Conflict A is built from Book 6 (shares that owe hands, purchased draw that carries none) and Book 15 (the tally and the trial's unequal cost). Neither conflict needs a villain.
- **Arc IV feeds Book 30 directly.** The two conflicts create distinct pressures: who carries the labour, and who controls the Gate. These map one-to-one onto Book 30's two physical needs, labour and routing, so Arc IV causally loads the finale.
- **The declined share is a good mechanism.** It shows a cost with no villain, the cost lands on a neighbour, and it fits the physics: unrecorded water is wild.
- **Book 23's abundance is well analysed.** Splitting it into real but seasonal abundance, uneven distribution, and a false belief is sound, and it keeps the original's events.
- **The Gate Table is a sound institution in Arc IV.** It separates schedule from record and reading, and it comes from a failed one-season trial rather than from fiat. These are well designed as of Book 22.
- **B's Compact clause targets the right gap.** The text correctly identifies grain-labour as the only lever on the lowland's unhanded draw. A's "lowland gap" failure mode is honest for the same reason.
- **The failure lists are mostly candid.** They admit C's change to the Balance Stones' Book 23 role, and B's partial return of the debt reading.
- **The Book 1 correction fits the original.** Share-marks read as evidence, with the first partial reading of the script in Book 8, agrees with the original's promise ledger.

## 4. What I could not assess

- **Documents I cannot see.** The text refers to several documents outside the packet:
  - `05-consistency-record.md`
  - `01-concept-comparison.md`
  - `D-product-capability-observations.md`
  - `A-studio-candidate-original.json`
  - "renewal test R2"
  - "the mission"
  - PRs #551 and #553
  - the evidence intention records

  Without these I cannot check the declared list of corrections, or whether the original Studio candidate already contains the Gate or the dissolution of the Hall.
- **Withheld passages.** I could not see the designer's self-assessments, advocacy or nomination, which are withheld by design.
- **Mislabelled cross-references.** Files 03 and 04 refer to each other as "01" and "02". I read those references as pointing to each other, on that assumption.
- **Schema validity of file 05.** I checked only roughly: there are 16 open questions, the link functions look under 120 characters, and the summary looks under 3000 characters. I did not validate it by machine.

## 5. Your context

I have no knowledge of *The Spring Ledger* from outside this folder. My session context was supplied automatically. It included the auteur repository's CLAUDE.md, which describes a narrative-engineering toolkit and its genre pipelines, a user-memory index, and a git status showing a branch named for "Wandering Islands" Stage 4j research. None of that touches this architecture's content, and I opened none of those files.
