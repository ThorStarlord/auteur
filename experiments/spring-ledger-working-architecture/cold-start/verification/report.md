# Verification of the Book 24 corrections (round 1, complete packet, verbatim)

**Packet:** `cold-start/verification/packet/` (seven files: instructions, the architecture as it stood at this round, the intentions, the round-1 corrected function, the round-1 corrected candidate, the source excerpt, and the change list).

**Reviewer:** one fresh general-purpose subagent, model Opus, one invocation. It self-identified as Claude Opus 5.5. It read all seven packet files and nothing else. Its automatically supplied session context included repository metadata, which it reported did not bear on its verdicts.

**Freeze:** recorded after round 1 and before round 2. Nothing below the line has been edited.

**Two notes on the process.**

1. **The first attempt was void.** A first verification was launched on a packet that contained only two of the seven files, because of an error in assembling the packet. Its report judged the corrections from the change list alone and could not check any of them against text. It is not counted. It is summarised here only so the record is complete: the reviewer reported that it could not verify any correction against the text.
2. **Round 2 was not separately verified by a fresh reviewer.** After this verification found one new defect (the gauge naming) and two partly fixed items, the second correction round was checked mechanically by the coordinating agent. The mechanical checks are in `cold-start/corrections.md`. A further independent round was not run, to respect the mission's bound on review cycles.

---

1. **Identity.** I am Claude Opus 5.5 (model ID `claude-opus-5-5`). I read all seven files in the packet folder and nothing else: `00-instructions.md`, `01-series-architecture.md`, `02-author-intentions.md`, `03-book-24-function-corrected.md`, `04-candidate-book24-corrected.json`, `05-source-excerpt.md` and `06-changes.md`. I did not modify, create or delete any file, and I did not use the network.

2. **Table of items.**

| ID | Verdict | Short quotation |
|---|---|---|
| F1 (function §7.2) | Fixed | "bears on the governing variable … It does not change who is counted for draw." |
| F1 (candidate `l_b24_mark_variable`) | Fixed | "bears on who can return labour; does not change who is counted for draw" |
| F2 | Fixed | "Whether it is independent of the author's preference remains the author's decision." |
| F3 (function §4) | Partly fixed | "declines … because the gauge does not resolve local return (P3)." But §7.4 still says "The Reading Hall has defined a limit on itself … will not attribute it to persons." |
| F3 (candidate link) | Fixed, with a concern | "declines to attribute gauge balance to named hands, which the gauge does not resolve" |
| F4 | Partly fixed | "This Book neither designates the Lowfen as the surge route nor excludes it." It sits beside the unchanged "Any channel except the Long Return's surge route would serve." |
| F5 | New defect | "The gauge is the Source's own state, and it does not depend on the Gate." |
| F6 (gift without skill) | Fixed | "a new physical assumption (P4), not a consequence of the caveat in 01 §2.3" |
| F6 (granddaughter) | Fixed | "sets evidence against an institution's record; here the evidence is a craft-mark on the water, not a share-mark" |
| K1 | Fixed: matches the source | "Her household is one of the hand-light houses the Turn burdens (original §5, Book 23)" |

Notes on each row:

- **F1.** **Credible architectural concern: none.** The capability record is now attached to the Ledger engine and only "bears on" the variable. Nothing else in 03 or 04 still describes a third term. The candidate's `str_b24_capability_mark` agrees: "not hours, debt or draw".

- **F2.** The motive is no longer declared independent of the author's preference. This matches 01 §4, where the Hesper row lists as unresolved "Whether her motive is independent of the author's preference for the Turn (open)". It also matches 01 §8.11 and candidate open question 10.
  - Minor point, which predates the correction: "open question 10" uses the candidate's numbering, but in 01 §8 item 10 is "Who carries the Turn when the maintenance lineages end." The text pairs it with "(01 §8.11)", which resolves the ambiguity, so this is not a defect.

- **F3.** The stated reason moved from an institutional principle to a limit of the instrument, and the sentence about B is now neutral. One part remains (see the next section).
  - **Credible architectural concern.** "the gauge does not resolve local return (P3)" reads as fact. P3 itself says "the gauge's resolution is not established", and §11 lists "Whether the gauge can resolve local return at all (P3)" as unknown. Because it cites P3, this is a labelled assumption, not a verified defect. Still, the refusal now stands or falls with P3. The candidate link states the same thing with no assumption marker at all.
  - P7 still says "refuses attribution". That is a wording difference, not a defect.

- **F4.** The unsupported claim "so it is avoided" is gone. One part remains: by P10's own first sentence, the Lowfen would not "serve" if the author later made it the surge route. So the Book's chosen work site quietly depends on an author-reserved choice going one way, and the text does not say so.
  - **Credible architectural concern**, not a strict contradiction.
  - It matters because the candidate's `str_lowfen_channel` says "Its lowest terrace is where a declined share runs wild". That makes the Lowfen a natural candidate for the surge route.

- **F5.** The cited link to the Gate Table is gone. But the new independence claim conflicts with the candidate (see the next section).

- **F6, gift without skill.** This accurately reflects 01 §2.3: "Gift without return thins the spring, and gift with unequal hands strands the poor." It is consistent with P4 and with §10's "without new physics beyond P3 and P4."

- **F6, the granddaughter.** The false "repeats her grandmother's act … against her grandmother's institution" is gone.
  - **Deliberate author choice.** "against" is loose. In Book 1 the evidence exposed falsification, while here the craft-mark is an alternative record that the Council accepts. That is a looser parallel, not a defect.

- **K1.** See section 4.

3. **New defects.**

**F5: the gauge's independence from the Gate (Verified defect: an inconsistency within the folder).**
- Corrected text (03 §2): "The gauge is the Source's own state, and it does not depend on the Gate."
- Candidate, `inst_reading_hall`: "Publishes the Gate gauge reading (Book 22) and the Balance Stones (Book 23)."
- Candidate, `inst_gate_table`: "set the Hollow Gate schedule from the gauge reading". Also `l_reading_separate_schedule`: "the Reading Hall publishes the gauge; the Table keeps no record".
- 01 §2.2 ("the balance is visible as a public gauge") supports reading the gauge as part of the Source engine. The candidate, however, names it the *Gate* gauge and dates it to Book 22, the Gate Table's year.
- The corrected sentence also runs together the balance (the Source's state) and the gauge (an instrument the Reading Hall publishes).
- Effect: 03 §2's claim that the function "holds whether or not the author keeps them [the Gate and Gate Table]" now depends on settling which description of the gauge is right.

**F3: a remainder, quoted on both sides. Not strictly caused by the correction, but exposed by it.**
- Corrected §4: "because the gauge does not resolve local return (P3). Whether the Hall should keep any person-level record is not settled here".
- Unchanged §7.4: "The Reading Hall has defined a limit on itself. It reads aggregate balance and will not attribute it to persons. This matters … to B's deficit record".
- §7.4 keeps the self-imposed, principled framing that the correction removed from §4. It also partly settles what §4 says is "not settled here". I count this as the remaining part under "Partly fixed", not as a new defect, because the corrected text does not cite §7.4.

4. **Hesper's household.**

- **It matches the source.** `05-source-excerpt.md`, line 128, reads: "the Turn burdens households with few hands, including Hesper's own." The restored row reads: "Her household is one of the hand-light houses the Turn burdens." "Few hands" and "hand-light" mean the same thing, and the fact is correctly filed under "Established".

- **Caveats on the source.**
  - In the original the statement is framed through Idrun ("Idrun … sees that the claim is partly right"), though the narrator states it as fact.
  - The excerpt has no section heading, so I can confirm the wording but not that it sits in "§5, Book 23". Line 119 is Book 15 material, so the placement is plausible.
  - The excerpt holds two lines, not one sentence, and line 119 is cut off.

- **It agrees with the rest of the architecture, with a few tensions.**
  - It is consistent with 01 §3.2 ("Hand-light houses have drawn less since Book 20") and with 03 §5, where the crew chooses "knowing that their own hand-light households stay cut".
  - **Unresolved question:** 03 §11 still lists "Whether the Sallow house is hand-light." That is expected, since K1 is "not a function change". But the excerpt speaks of "Hesper's own" household, which may or may not be Idrun's Sallow house, so §11's question is only partly answered.
  - **Credible architectural concern:** Hesper "Holds the cohort's belief that abundance needs no work", and the cohort belief is said to arise because it "has never seen the labour". A member of a burdened, draw-cut hand-light house sits awkwardly with that. It fits the original's young calling the Turn "a tax" better than "abundance needs no work". This is a motive to resolve, not a contradiction.

5. **What I could not assess, and why.**
- The original architecture, beyond the two excerpt lines. So I could not check the §5 section placement, whether Book 1's share-marks were "cut in stone", or the context of the Brightwater festival.
- The full text of 03 and 04 before the corrections. I had only the before snippets in 06, so I cannot tell whether other passages were also edited or should have been.
- Whether the gauge is physically or institutionally tied to the Gate in the author's intent. The packet's sources disagree, and the physics behind P3 and P4 is not established.
- Schema validity of the candidate JSON, which I did not test. There was also no stated defect for F6 beyond the before and after text, so I judged it against the folder's own facts.

6. **Your context.** I have no knowledge of "The Spring Ledger" from outside this folder. Two things in my session environment, which I did not open as files, may be related:
- The session runs in a repository for a narrative-engineering toolkit called "auteur".
- It is on a git branch named `research/wandering-islands-stage4j-targeted-literary-correction-20261110`. "Wandering Islands" also appears in 02's intention record ("do not reuse prior Wandering Islands answers").

None of this shaped my judgments, which rest on the folder's contents only.
