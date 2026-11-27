# Critic report D

Scope: Answer A is the deliberation answer (exercise-b, `answer-B-unedited.json`). Answer B is the discovery answer (exercise-c, `answer-C-unedited.json`). I checked claims only against each request's packet and Architecture. Nothing was changed.

## Summary

Answer A is careful. It keeps recorded, interpreted and undecided material apart, and it does not treat the Book 25 co-reference as a story relation. Its weaknesses are a few overreaching phrases and some unused evidence, and none is a confirmed error. Answer B is more exposed. One coverage-note claim is contradicted by the Architecture. Several possibilities are labelled "grounded" while resting on unaccepted construction additions or on assumptions the answer itself lists. Possibility 4 is correctly labelled speculative.

## Answer A (deliberation: q-conversion-settlement vs q-compact-settlement)

1. Claim: "any connection between them would run only through the hands-and-draw thread" (hypothesis 3), and "both questions sit near the thread th_hands_and_draw".
   - Evidence checked: `l_compact_hands_in_kind` runs inst_mill_compact to th_maintenance, not to th_hands_and_draw. `l_ledger_opens_trade` runs eng_ledger to inst_mill_compact. `l_trade_draws_without_return` runs inst_mill_compact to eng_source. `l_conversion_sets_draw` runs th_hands_and_draw to eng_ledger.
   - Classification: UNSUPPORTED.
   - Reasoning: The Architecture records other paths between the two questions' neighbourhoods (via eng_ledger and th_maintenance). The "only" is not supported, and the answer's own observation 6 shows the Compact link going to th_maintenance.

2. Claim: the compact question's link to th_hands_and_draw is offered as "one distributional problem, two stakeholder fronts" (hypothesis 1).
   - Evidence checked: the answer says "interpretation only: no record relates the questions". `between.status` is `no_recorded_relation`.
   - Classification: LEGITIMATE_SPECULATION.
   - Reasoning: It is explicitly labelled as interpretation and not recorded.

3. Claim: the records give no basis for "one problem", so the questions may stay independent.
   - Evidence checked: the ph_5 narrative_function says "the Compact's settlement is a clause of B or C". Alt B lists "grain-labour from the Compact". `th_hands_and_draw` says "Each finale mechanism answers the question differently". The conversion question says "a stage the finale must revisit".
   - Classification: ALTERNATIVE_READING (relevant evidence available but unused).
   - Reasoning: Both questions have a recorded tie to the finale alternatives, which supports a "shared finale dependency" reading. The answer's independence reading is still defensible, because nothing recorded relates the questions directly. The answer never mentions this evidence, though.

4. Claim: the element text's "open question 6" cannot be tied to either question.
   - Evidence checked: the element is recorded as engaging q-conversion-settlement (index 5). Its text says "open question 6" and "makes open question 6 concrete". The Architecture's lineage node uses one-based numbering ("open question 5" for the Special Draw Right, which is index 4).
   - Classification: PLAUSIBLE_UNCERTAIN.
   - Reasoning: The answer's caution follows the packet rule that positional names are not references. The packet's own one-based usage and the recorded association are consistent, but they do not prove the tie.

5. Claim: "records say nothing about how any Book treats [the compact question] in prose".
   - Evidence checked: dec-compact-settlement says "Oona's offer is neither accepted nor refused".
   - Classification: ALTERNATIVE_READING.
   - Reasoning: The decision text records some Book treatment (an offer made and left open), so "nothing" is slightly too strong. The narrower claim "no element engagements" is correct.

6. Claim: Books 24 and 25 repeat one element, and the records do not show different dimensions developed.
   - Evidence checked: both engagements carry element_id `cons-conversion-blind-spot`, text hash `de35e2d6...`, status unresolved, commitment undecided.
   - Classification: ALTERNATIVE_READING.
   - Reasoning: This is supported. The answer could also have said that the Book 25 decision text ("Book 24 makes it concrete without answering it") records Book 25 describing Book 24's work. It gives the sibling reading only through the engagement records.

## Answer B (discovery)

1. Claim (coverage_note): questions with "no recorded mechanism tying them to others (lowland towns, Compact settlement, plurality, Brightwater share count); they stay independent".
   - Evidence checked: `l_compact_hands_in_kind`, `l_trade_draws_without_return`, ph_5 ("the Compact's settlement is a clause of B or C"), alt_b ("grain-labour from the Compact"), and q-compact-settlement's own mention of the Gate Table.
   - Classification: CONFIRMED_ERROR (for the Compact settlement item).
   - Reasoning: The Architecture records mechanisms tying the Compact question to B/C, to th_maintenance and to the Gate Table question. The other three set-aside items I did not find contradicted.

2. Claim (possibility 1): "Alternatives B and C are recorded as depending on cistern storage, yet the surge route and finale mechanism are posed as independent choices".
   - Evidence checked: q-other-15 says "Alternatives B and C depend on it". q-finale-mechanism's wording names "A, B, C or a third".
   - Classification: UNSUPPORTED.
   - Reasoning: The finale-mechanism question already contains B and C, so its dependency on storage is recorded, not hidden. Only the surge route's tie to storage is new, and that is interpretation.

3. Claim (possibility 1): basis "grounded"; counterevidence lists only "valley's choice" and "no cistern value".
   - Evidence checked: str_hollow_gate says the surfeit mechanism "is an assumption the author may reject". q-gate-table says the Hollow Gate is "not decided; both are construction additions".
   - Classification: PLAUSIBLE_UNCERTAIN.
   - Reasoning: The possibility's core node is an unaccepted construction addition, and the counterevidence does not say so. Possibility 4 does cite the same question.

4. Claim (possibility 1): "Recorded: Gate release draws the high cistern down and cannot raise it... the Long Return pulse must be routed through the Gate".
   - Evidence checked: the str_hollow_gate summary and `l_longreturn_needs_gate`.
   - Classification: supported (see list below). The "Interpretation:" label correctly fences the cistern-limit inference.

5. Claim (possibility 2, significance): the hours record "links the conversion, the binding force of shared accounting and the lineage right through one recorded mechanism".
   - Evidence checked: eng_ledger records hours beside the mark. `l_lineage_right_on_draw` records a skill claim on draw. The tally is recorded in str_measured_turn and alt_a.
   - Classification: UNSUPPORTED.
   - Reasoning: Only the hours record is recorded. Its bearing on q-other-3 (care accounting) rests on the listed assumption "care counted under A uses the same record". Its bearing on q-right-revocable is not recorded, and the answer's own counterevidence says that question turns on who carries the Turn.

6. Claim (possibility 2): the hours record "could expose the conversion's blind spot".
   - Evidence checked: eng_ledger says the count "of the draw can be read straight from it". The element text names uncounted labour by hand-light households. The element association is engagement only.
   - Classification: LEGITIMATE_SPECULATION.
   - Reasoning: It is labelled "Interpretation", with a stated assumption and a counterevidence note that the association shows engagement only. The "grounded" label is generous, but the answer's own caveats keep the reading honest.

7. Claim (possibility 3): "A reading that activates Alternative C would be the Old Hand engine acting on the spring".
   - Evidence checked: eng_old_hand covers "Readings of the First Stones". Balance Stones are published by inst_reading_hall (Book 23). alt_c names "the Reading Hall's reading" and "published Balance Stones threshold". q-other-8 leaves open "who reads it".
   - Classification: UNSUPPORTED.
   - Reasoning: Nothing recorded says a Balance Stones threshold reading is an Old Hand (First Stones) reading. The answer lists "the threshold reading resembles earlier readings" as an assumption, but the title states it flatly. The question leaves the reader of the threshold open.

8. Claim (possibility 3): intermediate readings "between Books 8 and 15" could set a precedent, and the next step is "sketch one intermediate reading in Books 9-14".
   - Evidence checked: th_reading says "Partial readings of the script are Books 8 and 12, and the full reading is Book 15".
   - Classification: UNSUPPORTED.
   - Reasoning: The Architecture already records a Book 12 partial reading. The answer does not use it or say how it bears on q-other-10.

9. Claim (possibility 3): the spring and intent question "can stay open" through readings steering what is recorded.
   - Evidence checked: eng_source says it "responds to balance rather than to any character's intention". q-other-0 says Book 15 gives a partial answer.
   - Classification: PLAUSIBLE_UNCERTAIN.
   - Reasoning: eng_source's recorded statement bears directly on q-other-0 and is not cited. The conclusion stands as interpretation, but the evidence is relevant and omitted.

10. Claim (possibility 4): Hesper at a lot-drawn Gate Table seat as a test of motive. The significance line says "three open questions are about authorial stance made visible in a character".
    - Evidence checked: dec-hesper-motive, dec-reform-stance, dec-gate-table, alt_b (lot-drawn seats). The answer marks the possibility "Imaginative step, not recorded" and basis "speculative".
    - Classification: LEGITIMATE_SPECULATION.
    - Reasoning: Labelled correctly, with counterevidence that lot seats exist only under unchosen B. q-gate-table is about acceptance of the Gate, not authorial stance, so "three questions about authorial stance" is slightly loose.

## Claims checked and found supported

Answer A:
- `between.status` is `no_recorded_relation` and the relations list is empty.
- Book 25's decisions dec-compact-settlement and dec-conversion-settlement are both `resolved_by_owner_from_recorded_version`.
- The co-reference is "a recorded reference, not a relationship in the story".
- cons-conversion-blind-spot appears in Books 24 and 25 with an identical text hash, and is unattributed, unresolved and undecided.
- q-compact-settlement has no element engagements.
- Both questions were introduced at revision 3, with two earlier versions recorded as a named gap.
- Six untied positional names are recorded as a named gap.
- Link and node descriptions (`l_conversion_sets_draw`, `l_compact_hands_in_kind`, th_hands_and_draw) match the packet.

Answer B:
- Only one element association is supplied, and no question has history beyond introduction at revision 3.
- The text of the cited evidence matches the packet: str_hollow_gate (release draws down, cannot raise), `l_longreturn_needs_gate`, `l_declined_goes_wild`, q-other-15, dec-surge-route, `l_lineage_right_on_draw`, alt_a's surveillance failure mode, eng_old_hand, inst_reading_hall (no schedule authority), alt_c's failure modes, dec-hesper-motive, dec-reform-stance and dec-gate-table.
- eng_ledger does record hours beside the mark.
- The note that the element association shows engagement only is accurate.
- Alternatives A, B and C are described as "not chosen", and no possibility is stated as accepted.
