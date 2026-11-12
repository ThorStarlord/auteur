# Stage B — reviewer report (verbatim)

Same reviewer as Stage A (agent `a6f8f569bd1834f47`, resumed with its Stage A context intact, self-reported model Opus 5.5). Instructions: `stage-b/packet/00-stage-b-instructions.md`. Recorded verbatim from the subagent's final reply. No edits, no commentary inserted.

---

# Stage B report: revision H1 and repair R-A

## S0. Stage A modification

No change to Stage A judgments. The Stage A finale weakness still stands; S1 and F4 below explain why H1 makes it sharper. Both packet contradictions I raised in Stage A are still in the revised candidate: the Book 1 partial reading, and the finale described as "restored monopoly".

Paths opened in Stage B, in order: `stage-b-packet/00-stage-b-instructions.md`, `04-revision-delta.md`, `05-revised-candidate.json`, `06-review-evidence.json`. I opened nothing else and did not speculate about withheld text.

## S1. Changed premises

**P1. Who opens the records in Book 5: Keeper Corrow, under pressure from the evidence.**
- **Direct dependencies:**
  - The Ledger node now reads "opened by the Hall's own reform once evidence forces it (Book 5)".
  - The custody thread now passes custody to a reform committee.
  - The Arc I transition now says "the reform committee... sets the first rules of sale".
  - Arc II gains a named author of the sale rules.
- **Changed motivations:**
  - Corrow acts "to protect the Hall's standing against thinning". He is no longer a defeated dissenter.
  - Dorran becomes the messenger instead of a defector.
  - Quillmark and the Council now oppose rules a reformed institution approved, rather than a power vacuum.
- **This fits the original:** the original character list already calls Corrow "a reformer who later leads a dissenting remnant". H1 builds on an existing trait rather than inventing one.
- **Speculative:** the delta says the original's Arc I agency was "seizure". The original phase actually says "Protagonist's agency comes from evidence and a coalition, not inheritance", and Book 1 closes through proof. So assumption A1 overstates the change. Idrun's agency was already evidence-based. What H1 really changes is who acts in Book 5 and whether the Hall survives.

**P2. The Hall is reformed, not destroyed, and keeps the debt reading.**
- **Direct dependencies:**
  - New link `l_reform_keeps_debt`.
  - Book 15 becomes a choice the committee has to make (Arc III's narrative).
  - The "debt (Stone Hall)" side of the Old Hand engine continues without interruption.
- **Payoffs:**
  - "The Stone that would not read" is stronger. The Book 15 gift reading now directly threatens a living institution's legitimacy, not a defeated remnant's.
  - The Stone Hall's fall stops being an Arc I event. The grief payoff tied to it is weakened or moved; see S2.

**P3. Book 8's partial reading is authored by the committee and contested by scholars.**
- **Direct dependencies:** Arc II's narrative. This strengthens the Old Hand engine's legitimacy dispute before Book 15. It does not change the reading schedule, so the no-postponed-revelation rule still holds.

**P4. The emotional register of Arc I.**
- The anger target's intended effect changes to "unease that an institution must be forced into correcting itself, and that its correction still costs the wronged".
- Its emotion type is still `anger`, and the Arc I `reader_experience` still says "anger at falsified credit". That is defensible: Book 1's falsification still provokes anger, and Book 5's partial correction adds unease. But the field now describes two emotions under one label.

**P5. The Series' moral engine (claimed in delta §8).**
- The shift is from "liberation by seizure" to "legitimate reform by evidence". As noted under P1, the "from" side is overstated.
- The real new risk is the one the delta names: "benevolent-institution drift".
- **Effect on the finale:** this weakens the finale's distinctiveness. If an institution can correct itself as early as Book 5, then the finale's non-binding "shared accounting of care" has even less to set it apart. That is my Stage A weakness, made sharper.

**Genuinely unaffected:**
- Source physics; loops L1–L3; `l_trade_draws_without_return`; the Arc II thinning mechanism (A7 is correct).
- The Unmeasured Return and the stewardship tally; Brightwater; Arcs IV and V; Hesper; the Long Return.
- The Council, the Compact and the Reading Hall nodes.

## S2. Preserved meaning

**Checked and consistent:**
- `l_hall_custody_credit` ("sealed custody allowed credit to favoured houses"). Book 1's falsification still happens.
- `l_custody_grants_hall`; `eng_old_hand` "debt (Stone Hall)"; `rx_consequence`. Favoured houses still lose standing.
- `et_hope` ("outlast the institution that began it"); `th_core_question`.
- `gn_epic_fantasy` trope "the keepers' authority reversed by public reading". This still holds, and is now sharper, because the Book 15 public reading reverses the committee's debt reading.
- Arc III transition "no single institution holds the record", which matches the custody thread's "plural body (Book 15 onward)".
- The `gn_political_institutional` payoff "monopoly ends in Book 5". Records are public, so this is plausibly consistent; see the custody item below.
- Arc II's Dorran logic. In the original Book 6, Dorran argues selling is a freedom. That now fits a messenger of a reform that authored the sale rules.

**Stale, contradicted or unsupported:**
1. **`et_grief_of_orders`** (marked preserved) is contradicted. Its eliciting condition, "the Stone Hall's fall and Keeper Corrow's dissent", describes events H1 removes or moves. The Hall does not fall, and Corrow leads the reform. The review request explicitly asked to reconsider "the anger/grief emotion targets", yet only the anger target changed.
2. **`ce_bittersweet_return`** ("after the institution that held it has fallen") is stale or unsupported. It would only be valid if the reformed Hall falls later, perhaps at Book 15. The revision neither states nor rules that out.
3. **Arc III** contains an internal tension:
   - The `genre_activations` still say "the Stone Hall remnant holds it as debt".
   - The revised narrative says the committee "must now choose".
   - The node title is now "reform committee and remnant", but no field explains where a remnant comes from under H1.

   This is an unsupported inference left over from the original and implies an unstated split.
4. **Custody versus monopoly** is plausibly open but ambiguous. The custody thread keeps custody with the reform committee from Book 5 to Book 15, while the payoff says the monopoly ends in Book 5. The two fit only if "monopoly" means secrecy rather than custody. That should be said.
5. **Original architecture §5** is stale. That section is described as the "medium of record" for what the candidate cannot express, and it is "unchanged by this revision".
   - Book 1 still says "Dorran defects".
   - Book 15 still speaks of "Corrow's remnant".
   - The delta lists those Books as needing repair, but no revised Book functions exist. That is acceptable for a focused hypothetical, but the representation now leaves two sources that disagree.
6. **Minor:** delta §3 calls Book 12 a dispute "between two institutions". The Arc III narrative keeps three readings.
7. **Minor:** the `gn_political_institutional` trope "the falsified record" was dropped, though Book 1's falsification remains central. This is an unnecessary loss.

## S3. Repair level

| # | Finding | Owner |
|---|---|---|
| F1 | Grief target and bittersweet complex emotion stale | Multi-Book Structure (Arc I–III emotional design) |
| F2 | Arc III "remnant" versus committee choice | Multi-Book Structure |
| F3 | Custody/monopoly ambiguity | Multi-Book Structure |
| F4 | Finale risk named in delta ("Repair needed") but Arc V left unchanged; deferred to an open question; the "restored monopoly" phrase persists | Whole-Series Architecture |
| F5 | Premise A1 ("seizure") misdescribes the original | Agent creative-reasoning method |
| F6 | Medium-of-record Book functions not revised; two sources disagree | Representation or review capability in Auteur |
| F7 | Revision-status metadata inside design fields (summary prefix "HYPOTHETICAL REVISION"; `th_witness` "Added by revision R-A"); the review takes `proposed_rationale` from `candidate.summary` | Representation or review capability in Auteur |
| F8 | Review lists `et_grief_of_orders` and `ce_bittersweet_return` as "preserved" by ID with no semantic check, despite the request naming grief | Representation or review capability in Auteur |

F1–F3 sit in Series-level fields, but they concern Arc I–III causality, so Multi-Book Structure owns them. F4 sits in Arc V, but it concerns what the climax must show, which is a Whole-Series matter.

## S4. Evaluation of R-A

- **Preserves governing identity:** yes. The physical commons, loops, core question, reader promise, independent agencies, staged readings and Book 15 gift reading are all intact. No antagonist is added; no revelation is postponed. Corrow's motive is stated openly in Arc I, which meets R-A's own stated cost.
- **Changes all materially affected components:** mostly, not fully. It updates Ledger, Stone Hall, custody, the Arc I–III narratives, the anger target and the political contract. It misses the grief target, the bittersweet complex emotion, the Arc III genre activation, and the original architecture's Book functions (F1, F2, F6).
- **Avoids unnecessary changes:** yes, with one exception. Leaving Arcs IV–V alone is correct. Dropping "the falsified record" trope was not needed.
- **Preserves author authority:** yes. The new open question, whether reform "stay[s] credible under Books 15 and 30, or does the Hall become a benevolent authority that the finale must then oppose", leaves the stance with the author. The delta's §8 "Open to author choice" agrees.
- **New contradictions or consequences:**
  - The custody ambiguity (F3).
  - The anger target now carries a mixed register.
  - **The main one:** H1 shows institutional self-correction in Book 5, under evidence, at a cost. That pre-empts part of what the finale claims as its own earned achievement.
  - The delta sees this: "The reform must have a cost paid in Arc II/III by the people it failed". The candidate implements it only as a phrase in the emotion target ("still costs the wronged") and as the tenders' opposition in Arc II. No phase names who pays or how.
  - Interestingly, H1 gives the stale "restored monopoly" finale phrase a possible new meaning, a reformed Hall reasserting custody. But nothing in the revision adopts that reading, so it stays unsupported.
- **Coherent working alternative:** yes, plausibly. R-A is a coherent Arc I–III variant and is preferable to R-B and R-C for the reasons the delta gives. With F1–F3 cleaned up it would be internally consistent. It does not repair, and was not meant to repair, the finale weakness. It makes that weakness more urgent.

## S5. Alternative repair

I do not propose a different repair, only a minimal completion of R-A. I am not applying it.

1. Re-point `et_grief_of_orders` to the committee's loss of sole legitimacy at Book 15. Either state that the Hall falls there (which keeps `ce_bittersweet_return` valid) or rewrite the complex emotion.
2. In Arc III's activation, replace "remnant" with the committee's choice, or state that a split happens at Book 15.
3. Add one clause to the custody thread saying records are public from Book 5 while the committee keeps custody until Book 15.
4. Give Arc II one named cost of the reform's sale rules, borne by lower-terrace households.
5. Restore "the falsified record" trope.

The finale change I proposed in Stage A, one causal sentence distinguishing shared accounting from the Balance Stones, still belongs at Whole-Series level. H1 makes it more necessary.

## S6. Classification

- F1, F2: creative reasoning weakness (incomplete propagation).
- F3: creative architecture weakness (minor; plausibly open).
- F4: creative architecture weakness (inherited from the original; sharpened by H1).
- F5: creative reasoning weakness.
- F6: representation weakness. It could be classed as no demonstrated product defect if focused hypotheticals are meant to leave the original architecture's Book functions alone.
- F7: representation weakness.
- F8: review weakness.
- Delta §3's "two institutions" for Book 12: creative reasoning weakness (minor).
- Arcs IV–V and the Source/loop invariants: no demonstrated product defect.

## S7. Evidence that could change this assessment

- The withheld §7 review commentary, or the withheld Arc IV clause, if either shows that the grief or remnant staleness was deliberately deferred. That would downgrade F1 and F2.
- A statement of whether the reformed Hall falls at Book 15. That would settle whether F1 and `ce_bittersweet_return` are actually stale.
- Documentation that the review contract compares IDs only by design and that semantic checks belong elsewhere. That would change F8 from a review weakness to a scope limit.
- A rule on whether `02-original-architecture.md` must be revised alongside candidate revisions (F6).
- A drafted Arc II or Book 30 showing the reform's cost, or the finale's distinct mechanism. That would resolve F4.
