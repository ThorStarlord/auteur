# Stage C — reveal, reconciliation, and next responsibility

Status: **working / noncanonical review record.** Nothing here changes the original experiment (PR #551), the fixed brief, any accepted artifact, or the narrative ontology. The original experiment directory is byte-identical to PR #551's head `3168963b`, checked with `git diff --stat 3168963b -- experiments/series-architecture-30-book-v1`, which is empty.

Frozen inputs: Stage A at `e25250ca`; Stage B at `e097468f`. Both reviewer reports are verbatim in `stage-a/reviewer-report.md` and `stage-b/reviewer-report.md`.

## 0. Reveal protocol and exposure

- The original designer's evaluation files were read only after Stage B was frozen: `E-synthesis-and-evaluation.md`, `04-renewal-test.md`, `05-local-global-judgment.md`, `D-product-capability-observations.md`, and `01-concept-comparison.md`.
- **Coordinator exposure.** The coordinator wrote the original architecture and its evaluation in an earlier session. It had read `E-synthesis-and-evaluation.md` before this review, so it is not blind to the designer's conclusions. The coordinator also prepared the withholdings and read `C-revision-delta.md` while preparing the Stage B packet, before Stage B ran. The critic did not receive any of these files.
- The reviewer knew that one paragraph of `C-revision-delta.md` §7 had been withheld (the Stage B markers said so), and in Stage A it knew that section 8 of the original architecture and one Arc IV clause had been withheld. The §7 notice may have directed its attention toward omissions, so its Stage B agreement on the grief target is somewhat less independent than an unprompted finding would be.

## 1. Verification of the claims in this record

| Claim checked | Source checked | Result |
|---|---|---|
| `et_grief_of_orders` is unchanged and names "the Stone Hall's fall" | `C-studio-candidate-revised.json` vs original | Confirmed: unchanged. `inst_stone_hall` now reads "reformed, not destroyed". |
| `ce_bittersweet_return` is unchanged and reads "after the institution that held it has fallen" | same | Confirmed: unchanged. |
| Arc III genre activation still says "the Stone Hall remnant holds it as debt" | revised `ph_3_old_hand` | Confirmed, although the delta lists `ph_3` as changed. |
| The summary of `th_witness` says "Added by revision R-A" and the review's rationale is copied from `candidate.summary` | revised JSON; `07-complete-revision.json` review | Confirmed. |
| Book 1 gives the first partial reading | original `ph_1` narrative; `th_reading` summary says "Books 1, 8 and 12" | Confirmed in JSON. `A-original-architecture.md` §3.3 and §6 say Books 8 and 12; `01-concept-comparison.md` says "Book 1 open". The artifacts disagree. |
| Finale choice is "restored monopoly" vs shared accounting | original `ph_5` | Confirmed in JSON. `A-original-architecture.md` Book 30 names three options, not a monopoly. |
| "Seizure" is the original's Arc I agency | `A-original-architecture.md` (zero matches); `ph_1` says "agency comes from evidence and a coalition, not inheritance" | **Not in the original.** The word appears only in `C-revision-delta.md` (A1, and §8). The counterfactual's baseline is misdescribed. |
| The "civilizational" scope claim is weak | `A-original-architecture.md` §1 and (withheld) §8.4 | Confirmed in the original's own withheld text. |
| Books 27–29 have functions | `A-original-architecture.md` §5 Book 23 and §6 table | **Overstated.** They appear only as the Compact's named bid ("Books 27–29", "Book 27 (planned)"). |
| Abundance in Book 23 has no source ("never draws it") | `A-original-architecture.md` §5 Book 15 ("cost falls on the high cistern, which shows surfeit and fever") and Book 23 ("drawing glowing high-cistern water"); `ph_3` ("causes surfeit in the high terraces") and `ph_5` ("overdraws the upper cistern") | **Contradicted.** The chain is drawn across Books 15 and 23. Its explicitness is a fair question. |
| The revision instruction named the grief target | `evidence/revision-instruction.txt` | Confirmed: "the anger/grief emotion targets". |

## 2. Reconciliation of consequential findings

Classifications: **Agreement** (independent, with the designer's finding), **Disagreement**, **New** (not in the designer's report), **Unsupported** (the critic's claim fails the check), **Unresolved** (the evidence cannot decide).

| # | Finding | Designer's position | Independent reviewer | Classification |
|---|---|---|---|---|
| 1 | Causal renewal Books 1–15 is real and different in kind (custody → market → labour → legitimacy) | R1–R4 supported (`04`, `E §2`) | Strong; same chain described (`A` §3–§5) | **Agreement** |
| 2 | Engines interact causally (L1–L3), not coexistence | Coherent on paper; "held only in prose" risk (`E §2`, `01`) | Strong; Book 15 combined effect | **Agreement.** The fragmentation risk is not reproduced. |
| 3 | Finale care-without-debt is asserted, not derived | Strongest weakness (`E §3`) | Shared accounting "informs but binds no one", so the governing variable is not shown to change at the climax | **Agreement on location and claim. New on mechanism:** the cure is less binding than the regime that caused the unevenness. |
| 4 | Arc IV is the thinnest and must export the state the finale needs | Derive ≥2 Arc IV conflicts (`E §7`, `04 §5`) | Arc IV's "uneven hands" and "abundance" are required exports, but provisional (`A §7`) | **Agreement on location.** The critic frames the fix as an exported state, not as conflicts. |
| 5 | Old Hand's state does not change between Books 8 and 15 (ladder unstaged) | Real gap; Multi-Book owner (`05`) | Reads the readings as "staged (Books 8, 12, 15)" and does not test state change | **Disagreement, favoring the designer.** `A §3.3` gives a changed state only at Book 15. Books 8 and 12 are described as readings and claims. Whether Books 9–11 and 13–14 need functions at all is **Unresolved** under the brief's ban on per-Book outlines. |
| 6 | Arc V's middle (Books 24–29) is underspecified | Not identified | Books 24–26 risk a countdown; 27–29 are only a named bid | **New.** Partly overstated (see 9). |
| 7 | Book 23 abundance has no derivation | R5 supported by generational inheritance (`04`) | "Nothing yet sets up that abundance... never draws it" | **Unsupported as stated.** Book 15 surfeit → Book 23 festival is drawn. The designer's R5 is better supported here. The narrower question of explicitness remains. |
| 8 | Finale options contradict between JSON and prose ("restored monopoly" vs three options) | Not identified | Identified | **New, confirmed.** |
| 9 | Book 1 partial reading contradicts Books 8 and 12 across artifacts | Not identified; the designer's own `01` says "Book 1 open" and `05` says Books 8 and 12 | Identified | **New, confirmed.** The artifacts disagree among themselves. |
| 10 | Civilizational scope is unsupported at the finale | Withheld from the critic (`A §8.4`) | Identified independently | **Agreement.** The critic could not see the designer's statement. |
| 11 | Hesper's generational motive is authored, not derived | Authored-motive risk (`04 §5.5`, `E §5`, `A §8.3`) | Credits generational transformation as demonstrated (`§1F`) | **Disagreement, unresolved.** The packet gives her motive only as upbringing under open records and unmeasured return. |
| 12 | Reform-from-within biases the series toward institutional repair | Named risk (`E §4`, `C §8`) | "Benevolent-institution drift"; it weakens the finale's distinctiveness | **Agreement.** The critic adds the link to finale distinctiveness. |
| 13 | Alternative product: layered "Debt of Hands" may be better for an author | Counterargument (`E §4`, `01`) | Not assessed | **Unresolved.** The alternative is not in the packet. |
| 14 | Counterargument that the crisis itself does the binding | Not raised | Raised by the critic (`§3`) | **Unresolved.** It needs a drafted Book 30 to test. |
| 15 | H1's "preserved" grief target is stale | Known omission (`C §7`, withheld from the critic); `D §4.5` | Stage B F1, F8 | **Agreement,** with the qualification in §0. |
| 16 | Bittersweet complex emotion is also stale or conditional under H1 | Listed as unchanged (`C §7`) | Stage B S-B2 | **New, conditional.** It is valid only if the Hall later falls, which the revision neither says nor rules out. |
| 17 | Arc III remnant contradicts the committee's choice | Delta lists `ph_3` as changed but misses this phrase | Stage B F2 | **New, confirmed.** |
| 18 | Custody and monopoly are ambiguous under H1 | Not raised | Stage B F3 | **New, minor.** |
| 19 | The counterfactual's baseline misdescribes the original as "seizure" | `C §2` A1; `C §8` moral engine | Stage B F5 | **New, confirmed, significant.** The designer's claim that H1 changes a seizure-based engine rests on a baseline the original does not contain. The original's own Book 1 is evidence-driven. |
| 20 | The medium-of-record is not revised | Deliberate: "unchanged by this revision" (`C §9`) | Stage B F6 | **Unresolved.** It is a stated choice, not a defect, unless the packet must stay consistent with candidate revisions. |
| 21 | Revision status is stored in design fields and copied into rationale | `D §3` notes authority lives in summary text | Stage B F7 | **New, partly anticipated** by `D §3`. |
| 22 | Preserved-by-ID review does no semantic check; revision obligations are only in the prompt | `D §4.5`, `D §4.12` | Stage B F8 | **Agreement.** The instruction named the grief target, so the failure is in carrying out the obligation, not in its absence. |
| 23 | Finale risk named in the delta is not implemented | `C §3` ("most exposed payoff"; "reform must have a cost paid") | Stage B F4 | **Agreement.** |
| 24 | Dropped trope "the falsified record"; Book 12 "two institutions" | Not raised | Stage B minor | **New, minor.** |
| 25 | R-A is a coherent working alternative but incomplete | Preferred (`C §6`) | Coherent; needs F1–F3 cleaned up | **Agreement.** |

## 3. Product-capability implications

**Creative design.** The critic and the designer agree the finale and the late series are where the work lies. Findings 3, 4, 6, 10, and 23 concern the Whole-Series and Multi-Book owners. Findings 5 and 11 are unresolved and need the Arc II–III ladder and Hesper's motives drafted. Nothing here calls for a new engine or a redesign.

**Reasoning method.** Several failures are in how the agent reasons, not in what the product holds:
- It did not carry out an explicit instruction to reconsider the grief target (findings 15, 22).
- It built a counterfactual on a baseline the original does not contain (finding 19).
- It did not check whether a phase it marked as changed still carried a stale phrase (finding 17).
- The critic overstated absence in two places (findings 6 and 7). A review method should quote the text it relies on before claiming something is missing.

**Context delivery.** No main finding failed for lack of context. The packet withheld the designer's §7 and §8 material, which may have limited the critic's view of Arc III and Hesper. That is a deliberate protocol effect and is recorded as a limitation, not a product defect.

**Representation.** Findings 8 and 9 show that the JSON and the prose disagree and nothing checks them against each other. Finding 21 shows that revision status lives in a design field. Every finding in §2 was identifiable by reading existing artifacts, and none required a new typed relation. So no representation change is warranted now. Cross-artifact consistency is a review concern, not an ontology concern.

**Review capability.** Finding 22 is the one real review weakness: the review compares IDs and does not test the meaning of preserved items against changed context. Mission §7 asks that a reasoning-based check using existing operations be tried before any new ontology.

## 4. Answer to the central question

Does the architecture contain enough generative causal structure to support its intended transformations and distant payoffs?

- **Established:** the development from Book 1 to Book 15. Each victory changes a named variable, and the next pressure comes from a different engine. Both reviewers accept this (findings 1–2).
- **Not established:** the finale's care-without-debt payoff. The reviewers agree the endpoint is described rather than derived. Its missing link is the exported state of Arc IV and a binding mechanism at Book 30 (findings 3, 4, 23).
- **Unresolved:** whether the Old Hand's state needs intermediate Books (finding 5), and whether Hesper's motive is independent (finding 11).

So the answer is mixed. The architecture derives its middle and its opening, and describes its end without deriving it. The gap is localised. It is not a missing engine.

## 5. Next construction recommendation

**Recommended next responsibility (not started):** a bounded working construction, owned at the **Multi-Book Structure** and **Whole-Series** levels, with these components:

1. **Derive Arc IV's exported state** from Books 15–18 and the Arc IV history: the uneven-hands and abundance state that Books 23 and 30 need. Derive at least two Arc IV conflicts from that state, each traced to a changed relationship and not to a new antagonist.
2. **State the Book 30 binding mechanism:** how shared accounting changes who returns labour, as distinct from the Balance Stones' "informs but does not bind". Offer two alternatives. Whether it binds is an author choice, so the construction must not decide it.
3. **Make the consistency corrections** the review found, in a new working candidate and not in PR #551's files: the Book 1 partial reading (finding 9), the "restored monopoly" wording (finding 8), the Arc III remnant (finding 17), the grief and bittersweet targets (findings 15–16), and the seizure baseline (finding 19).
4. **Validate with a fresh-context reviewer**, using the same withholding discipline, on the new working delta. Include a cheap test: an explicit preserved-ID semantic pass in the existing revision flow, to see whether it catches the grief and bittersweet items.

**Stop conditions for that responsibility:** no prose; no Book outlines beyond the focal Books and the exported Arc IV state; no accepted artifact; no product or schema change; the finale stance stays an author decision.

**Strongest viable alternative: semantic review capability (C).** It is not warranted yet. The one tested instance (finding 15) was caught by reasoning when the agent was explicitly asked. The other review-level finding (finding 9) is cross-artifact consistency, which a reader can check. A product change would add machinery before the reasoning test has been tried. If the explicit preserved-ID pass in step 4 does not catch the grief item, C becomes the next candidate.

**Other alternatives considered:**
- *Whole-Series redesign (B):* not warranted. Both reviewers accept the three engines and the Book 1–15 chain.
- *Method improvement (D):* partly. The concrete failures are tested by step 4. A general method change is a larger program the mission rules out.
- *No new work (E):* not warranted. The finale gap is decision-changing, and both reviewers found it.
- *CLI bridge parity* (`apply` in the bridge, UTF-8 output): a convenience. It does not change the narrative question and should not displace the construction. It remains a separate, owner-chosen item.

**Cheaper reversible test:** a 2–3 page working delta covering only components 1 and 2, reviewed by a fresh reviewer, without changing the candidate. If the review finds the finale earned, edit the candidate. If not, the cost is small.

**Author-reserved decisions** (needed before acceptance, not before the construction starts): whether the finale's shared accounting binds; flood casualties; the Compact's end state; whether reform from within is the series' stance; and whether the Old Hand needs intermediate Books at all.

**What would change this recommendation:**
- Evidence that Arc IV's exported state is already derivable from existing text. The construction would then be smaller.
- A drafted Book 30 that makes shared accounting visibly change the labour distribution. That would reduce the finale finding to a matter of detail.
- An author ruling that a non-binding finale is intended. The critic's central weakness would then become a matter of emphasis.

## 6. Stop-condition status

1. Stage A is preserved (`e25250ca`). ✔
2. Stage B is preserved (`e097468f`). ✔
3. Findings are reconciled with the designer's evaluation (§2). ✔
4. The next warranted responsibility is identified (§5), and nothing has been executed. ✔

**Limitations:** one reviewer per stage; the reviewer used a different model from the designer; no reader response; no prose; no fresh-context reconstruction test; the withholdings were chosen by the coordinator.
