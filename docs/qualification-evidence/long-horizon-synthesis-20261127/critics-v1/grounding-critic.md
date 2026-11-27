# Adversarial grounding critic, v1 (verbatim report, read-only fresh subagent)

Scope: the four v1 syntheses, Exercise A run 2, Exercise B, Exercise C, Exercise D. Each claim was checked against the evidence text in its own request. The report is preserved as produced.

---

**Most serious problems**

1. **A and D misread "now practising both" as something stage 3 must produce.** E8 says "The cohort, now practising both counted and uncounted return," and E4 says the split is already recorded. A's relation s3→s5 is a prerequisite because "only s3 brings that practice about," and its s5 stage says "The cohort has practised both only if s3 happens," while A's own s5 development says "now practises both." D repeats this as prerequisite s2→s4 ("Stage 2 is the proposed route into that practice, and no other route is recorded"). D's alternative path 3 then calls standing without stage 2 "closed on the current record" and calls stage 2 "the only recorded route." No cited identifier says that. D's changes_from_prior keeps the standing stage "conditional on the apprentice stage." Verdict: misread (A twice, D twice).

2. **A keeps the public-record claim that criticism c2 contests.** A's s4 changes say the record "may let the uncounted cohort give back without first being counted (inferred from E5)," and A's opportunity 2 repeats it. E5's visible text ends "says who can repair rather than who" and says nothing about the count. A also completes the cut-off phrase as "who owes." Verdict: unsupported (twice). D's c2 reason identifies the same gap.

3. **C turns a conditional into an "accepted gap."** C's E5 (repeated as E14) reads: "Accepting her granddaughter's crew means accepting a gap in the tally she keeps." C calls it "the steward's accepted gap" in s2, enrichment 2, opportunity 2, an open decision, the standalone value and the reader experience. No cited identifier says the steward or the crew has accepted anything. Verdict: misread.

4. **C treats duplicated Book 25 text as a persisting condition.** E17 lists nine Book 25 elements with the same text as Book 24. C's s2 (labelled inferred) reads that as "a shortfall that stays visible across two Books is a standing condition" (E16, E17). Its changes then say the finale must answer "a labour gap already recorded as persisting." Its own uncertainty says Book 25's "own contribution is unknown," yet its standalone value says Books 24 and 25 keep the labour "as their own experience." Verdict: misread, and a chronology claim under (d). A's s2 is inconsistent in another way: it keeps Book 25 as a stage while saying it "needs its own development before it can be a stage." D drops Book 25 under c1, which E14 supports.

5. **A states the review point as recorded and drops the reversal.** E7 says: "Its review point falls in Book 24 (agent-proposed as P1; the source gives a reversal for it)." A's s1 is labelled recorded, and A's uncertainty never mentions the reversal. A's reader experience says Book 24 keeps "the review point held." B's reader experience ("stands on its own as the review") repeats the claim. B's uncertainty and D's open decisions do flag the reversal. Verdict: overreaching.

6. **B drops the condition on its strongest opportunity.** E24 says "under B, purchased draw owes grain-labour to the rebuild," and B's own relation says "Condition B is not defined in the supplied record." B's opportunity 2, labelled "Inferred," says crediting Compact labour "would bring the purchased draw under the rebuild" with no condition. Verdict: overreaching.

7. **Other overreach, each checked against the cited text:**
   - B, relation 2: hired labour's bearing on the Right's condition "is contested." Nothing cited says so; E4 says only that the lineage fears dilution.
   - B, s3: the valley's hands must be "tested under the Right" and the credit question answered first. E12 says only that the valley has "some hands of its own."
   - C, opportunity 1: "the surge is routed by the people who will give the labour." E1 says the choice "belongs to the valley."
   - C, opportunity 2: the steward's gap and the refusing generation's return are "the same cost seen from two sides." Neither cited identifier says so.
   - C, enrichment 1: trained hands "show who can repair." E8 says only that they "set up the Long Return's labour."
   - C, relation 1: training must "start in Book 24." E7 says training "has begun," with no start date.
   - C, uncertainty: "Books 26 to 29 are not in the record (E13)." E13 concerns training years, and E11 names "Books 27 to 29."
   - A, relation 3: a record without trained outsiders "would list only lineage members." E5 says nothing about membership.
   - A, relation 4: standing "not on evidence." E8 says nothing about evidence.
   - A, alternative 2: standing "lacks the training the Right requires." E7 ties the training condition to the Right, not to standing.
   - D, alternative 2: the uncounted generation "would not yet appear" in the record. E6 says nothing about records.

**Checks (a) to (d)**

- **(a) Citations:** Every identifier cited in the four answers is in its request's allowed_evidence. A and D say "matching source hashes" and cite E14, which records same text, not hashes. The hashes appear in the source_sha256 fields of E3 to E13.
- **(b) Basis labels:** Five stages labelled "recorded" rest on Working Book text the record marks agent_proposed, unknown_legacy or null-attributed: A s1, B s1, B s2, C s1 and D s1. A s1 and B s2 do not flag this in the stage text. No recorded stage rests only on an explicitly marked agent inference.
- **(c) Proposed stages:** None of the ten proposed-horizon stages names people, places or factions the record does not supply.
- **(d) Book numbers and chronology:** Book references (20, 23, 24, 25, 27 to 29, 30) match the record. The exceptions are item 4, A's "only if s3 happens" (item 1), and C's Books 26 to 29 claim (item 7).

**Per-answer summary**

- **A (evA2):** 30 claims checked. 17 supported, 5 overreaching, 2 misread, 5 unsupported, 1 not checkable.
- **B (evB):** 26 claims checked. 21 supported, 4 overreaching, 0 misread, 0 unsupported, 1 not checkable.
- **C (evC):** 46 claims checked. 35 supported, 4 overreaching, 4 misread, 1 unsupported, 2 not checkable.
- **D (evD):** 40 claims checked. 34 supported, 1 overreaching, 2 misread, 0 unsupported, 3 not checkable. D's c1 and c2 verdicts match the visible E14 and E5 text.

Counting unit: one record-testable assertion, meaning a stage's factual premise, a stated dependence, an alternative's premise, an opportunity, a culmination condition, a criticism reason, or an uncertainty or open-decision fact. Proposals are counted through their premises only. Supported claims are counted but not listed. Unlisted non-supported items are of the same kinds as those above.
