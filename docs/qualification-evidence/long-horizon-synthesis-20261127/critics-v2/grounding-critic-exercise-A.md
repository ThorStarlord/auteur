# Grounding critic, v2 Exercise A (verbatim report, read-only fresh subagent)

Scope: the v2 Exercise A synthesis (`exercise-A/run-3-grounded-quotes/`). Its criticisms became the input of the Exercise D v2 follow-up (`exercise-D-v2/criticism.txt`).

---

All 15 quotes are verbatim in their cited items, so the problems are in provenance labels, tense, and premises the quotes do not carry.

**Trajectory**
- **s1 (Book 24, "recorded"; E5, E7, E1):** Overreaching. E5 is `agent_proposed`, and E7 says the review point is "agent-proposed as P1". The changes field also says "Inferred", so basis and changes conflict.
- **s1 "since Book 20" (E1):** Supported. E1: "From Book 20 lineage crews carry channel repair".
- **s2 (E6, E4, "recorded"):** Supported, with minor overreach. E6: "has never seen the labour, because lineage crews perform it under the Right". E4 is `unknown_legacy`, so "recorded" is loose. "Never shown what it takes" paraphrases "never seen".
- **s3 (proposed; E3, E7):** Overreaching. E3 is an "agent inference" and the stage is stated unconditionally, which the proposed-basis rule forbids. "The record states that the Right is exposed" credits agent text.
- **s4 (proposed; E5, E3):** Supported as a proposal. "Which the record says Book 24 exports" rests on agent-proposed E5. "Per person" is not checkable, since E5 is truncated at "rather than who".
- **s5 (proposed; E8, E4):** Misread. E8 says the cohort "may claim standing" and is `hypothetical`, but the stage says it "claims standing". "No body is named" and "do not ask" are absences argued from 11 excerpts (E14: 182 elements read).

**Relations**
- **R1 prerequisite, s1 to s3 (E7):** Overreaching. E7 makes the Right conditional on training; nothing cited says the review must precede the test.
- **R2 complicates, d1 to s3 (E3):** Supported. The link to outside apprentices is inferred, as the reason says.
- **R3 preparation, s2 to s5, "causal" (E8, E4):** Overreaching on the dependence label. "Causal" is not stated, and the reason itself says necessity is not stated.
- **R4 reinforces, s4 to s3 (E5):** Overreaching. The quote covers separation from tally; E5 says nothing about "demonstrated training".
- **R5 enables, s4 to s5 (E8):** Unsupported. E8 never mentions a record; the quote concerns a missing granting body.

**Alternatives**
- **A1 keep crews under the Right (E6, E1):** Premise supported. "Viable" and "never enters a record" are judgements, not cited.
- **A2 standing before condition (E8, E3):** Overreaching. "As the record states" credits agent-proposed E3.
- **A3 record before condition (E5):** Supported. "Whether that is permitted is not stated" is correct absence wording.

**Opportunities**
- **O1 labour transferable (E1, E7):** Overreaching. The quote supports only the training condition, not "transferable".
- **O2 uncounted practice visible (E4, E5):** Overreaching. The quote supports separation from tally; the visibility step is inferred from truncated E5.

**Reader experience**
- **"Book 24 turns the labour into a question of who meets the Right's condition":** Overreaching. No cited words carry it; it rests on agent-proposed E5 and E7.
- **"Book 25 repeats Book 24's five elements word for word" (E14, E9 to E13):** Supported. Source hashes match E3 to E7 pairwise.
- **"Households with few hands" (E1):** Supported, verbatim.
- **"Everyday belonging (E2) needs that labour seen":** Unsupported as cited. E2's visible text names "everyday belonging" but nothing about labour, and it is truncated.

**Open decisions and uncertainty**
- Open decisions 1, 2 and 4, and uncertainty 1, 3 and 4: Supported (E14; E7 "the source gives a reversal"; truncation of E2 and E5; `culmination_requested` false).
- Open decision 3, "the record names none": Overreaching. E8 covers Book 24 only.
- Uncertainty 2 (E3, E5, E7 agent-proposed): Supported, and it contradicts s1's "recorded" label.
- Culmination null, empty `changes_from_prior` and empty `criticism_assessments`: Supported; the request has none of these.

**Criticisms**
1. Stage s1 is labelled "recorded" although E5 and E7 are agent-proposed and E7 calls its review point "agent-proposed as P1", so it should be labelled proposed or inferred (s1; E5, E7).
2. Stage s5 turns E8's "may claim standing" into a cohort that "claims standing" and treats eleven excerpts as proof that Books 24 and 25 "do not ask" the question, so it should stay conditional and state the absence as not stated in the cited items (s5; E8, E14).
3. Relation R5 says a capability record gives standing "something to rest on", but E8 never mentions a record, so the enables link has no cited premise (R5, s4 to s5; E8).
4. Relation R1 is a prerequisite on the Book 24 review point, yet E7 only makes the Right conditional on training, so the strongest relation type is used without the necessity it requires (R1, s1 to s3; E7).
