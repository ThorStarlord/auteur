# Claim-basis verification and reflective follow-through: evaluation record (2026-11-27)

Branch `feat/claim-basis-verification`, from `main@752817c9` (after PR #653). Design: `docs/design/2026-11-27-long-horizon-creative-synthesis.md`, section 12. Machine summary: `summary.json`, built by `build_summary.py` from the owner records in this folder. Every answer, refusal and critic report named here is kept verbatim beside this file.

## 1. Starting and current state

- Starting canonical state: `main@752817c9`, the merge of PR #653 (reviewed head `4c8697b0`). The Spring Ledger study was re-seeded on a fresh study (`scripts/consequence_exercise.py seed`).
- Replay equivalence (`replay-equivalence/replay.json`): the recorded requests for Exercises A, B, C and D were re-prepared from their recorded inputs and reproduced exactly (same request identities). The recorded answers completed through the owner. The recorded refusal of Exercise D (attempt 1, extra field `book_check`) reproduced.
- Owner code is implemented and tested (section 3). Nothing has been committed to `main`.

## 2. What was decided and why (design section 12)

Responsibilities were separated: referential and textual grounding were already owned (admission, quote contract); semantic grounding gained one owner, `studio_architecture_verification.py`; relational and developmental grounding are judgements of the same owner about a relation or a stage; creative judgment is not verified, only reported as what remains open. Of the four approaches, only A (independent verification after synthesis) became an owner. C (reflective correction) became a carry of verifier judgements into a follow-up as criticism, with no new correction owner. B (interpretation before synthesis) was not built: the measured failures were in what quotes were attached to, not in missing interpretations. D (selective composition) became a record-derived "others depend on it" rule, with no score.

## 3. What was implemented

- `studio_architecture_verification.py` (new): claim inventory (stages, relations, alternative paths, opportunities, culmination conditions, by reference), dependents from the record's own references, `prepare`/`complete`/`project` for one claim, refusals kept beside their message, standing (current, superseded, stale). A verifier judgement is one of eleven values, with `evidence_register`, `affects`, `reasoning`, `quote`, `alternative_reading`, `would_settle` and a required `creative_room`. The owner refuses: unknown citations, a non-verbatim quote, a misreading with no alternative reading, an unevidenced interpretive judgement, a `supported` judgement on agent-proposed evidence, and `supported` for a claim the synthesis labelled `recorded` unless the evidence establishes it.
- `studio_architecture_synthesis.py`: `derived_changes(prior, current)` (owner-derived comparison of two stored answers, at read time), `synthesis_record` (read for verification), `verifications` input on prepare, which carries a completed verification of the prior synthesis as one criticism with its identity. Requests without verifications keep their identities (checked by the replay).
- Served: routes for the claim inventory, claim prepare and claim completion; the synthesis panel shows "Check a claim's basis" per claim, the verdict with what remains creatively open, an offer to carry a judgement into a follow-up, and the derived change list for a follow-up. Styles added.
- Tests: `tests/test_architecture_verification.py` (31 tests, including refusals, standing, follow-up identity, derived changes, the limits-in-instruction regression and a revised-stage regression); `tests/test_beginner_studio_synthesis_browser.py` gained one served test of the whole claim-check loop.
- Scripts: `scripts/claim_verification_exercise.py` (claims, prepare, complete); `scripts/synthesis_exercise.py` gained `--verification`.

## 4. Verification exercises on the preserved syntheses

Inventories were taken from each synthesis's stored answer. They cover the same claims the v2 grounding critics checked (A: 15 claims; B: 14; C: 22), except that the critics also checked open decisions, uncertainty and the culmination's standalone value, which the owner does not treat as claims. Each claim was judged by one fresh agent reading only its own request, writing its unedited answer; the owner completed each answer.

| Synthesis | Claims | Accepted first attempt | Verifier flags | Critic flags | Agreement |
|---|---|---|---|---|---|
| A (run 3) | 15 | 15 | 8 | 11 | 12/15 |
| B (v2) | 14 | 14 | 6 | 8 | 12/14 |
| C (v2) | 22 | 21 (one refused on length, then accepted on a corrected instruction) | 13 | 9 | 12/22 |
| F (follow-up, corrected) | 14 | 14 | 5 | 3 | 10/14 |

"Verifier flag" means a judgement in the misreading or unsupported family (overreaching, temporal, modal, attribution, standing, unsupported relation, contradicted). The "critic flag" is any verdict other than supported or acceptable proposal, from the v2 critics (A, B, C) and a fresh critic on the follow-up.

### 4.1 The refusal and the fix

C s1 was refused: `creative_room` ran to 401 characters against a 400-character bound. The verifier's instruction did not state the owner's limits. The project's own memory records this failure for inquiry prompts. The owner is unchanged; the instruction now states every limit, generated from the same constants as the schema, and a regression test checks it. The refused judgement is kept (`exercise-C-verification/owner/verification-s1-attempt-1-refused.json`). The same claim, prepared under the corrected instruction, was accepted on its first attempt (`exercise-C-verification/s1-corrected-instruction/`). All other verifications were prepared under the earlier instruction, which stated no limits and produced no other length refusal. This is a difference between requests and is recorded as one.

## 5. Adjudication of the 19 disagreements

Each disagreement was checked against the exact source text of the cited items (the request files). Counts: 6 verifier-right (one in part), 9 critic-right (two in part), 4 defensible either way.

Verifier right:
- C n2 (culmination necessary condition). Claim: "The author has chosen who gives return labour ... the record says this is not decided." It cites E2, which ends "Not decided." The critic accepted it. The claim contradicts itself, and the verifier's `contradicted` is correct.
- C n1. The cited E1 says the pulse "needs channel labour before its date"; the claim says the labour "is in place". A requirement is read as a state. The verifier is right; the critic did not flag it.
- C s4. The changes clause says the valley's routing "decides where that labour falls". E1 says the routing "decides which channel takes the surge". The verifier is right.
- C a1 (in part). The alternative conflates channel labour with the return labour E2 asks about; no cited item identifies them. The verifier is right on the identity gap; the critic accepted the alternative.
- F3 a3. The alternative's wording states an absence that the cited items do not carry. Verifier right.
- F3 r3. The relation's `causal` tag outruns both cited items, which are agent-proposed and do not order the review against the demonstration. The verifier's flag is right on the tag; the critic accepted the conditional.

Critic right:
- A s3 (proposed stage). Written as an unconditional event ("are trained ... is demonstrated"), where the synthesis contract requires a proposed stage to be conditional. The verifier said "not an error" because the stage is labelled proposed, yet its s5, which uses the same indicative pattern for a possibility, it flagged. The verifier is inconsistent here; this is a verifier miss.
- A o1 and A o2 (opportunities, in part). Both "could" statements are legitimate possibilities. Each also has an unsupported joint clause ("neither ... makes that possible alone"); the verifier noted the clause but classified the claim as creative speculation, so the unsupported part was not flagged. This is a verifier under-classification.
- B s3 (proposed stage). "Now practising" is taken from E11's hypothetical element. The verifier said `defensible_inference`. A verifier miss, the same pattern as A s3.
- B o1. The claim assigns hired labour the same channel repair; E24 does not give it. The verifier said creative speculation. A verifier miss.
- C n3. The claim's own text labels the recording of the giving as an inference and says how it is recorded is not stated. The verifier flagged it as `unsupported_relation`, ignoring the label. The verifier over-flagged a self-labelled inference.
- C a3. A hypothetical ordering (routing before the finale mechanism) offered as an alternative path. The verifier read the ordering as an asserted dependency; an alternative is a possibility. The verifier over-flagged a creative possibility.
- C r1. The verifier said `defensible_inference` while its own reasoning says the link to Book 24 is not stated. A prerequisite relation cannot be a defensible inference on an unstated link.
- F3 s2 (proposed stage). The stage identifies the generation of s1 with the refusing generation of E5, which no cited item does. The verifier passed it as agent-proposed creative speculation, so the identity link was not checked. The critic was right.

Either way:
- C s3. "once Book 24 has exported ... and Book 25 shows ..." is a conditional, but the export is agent-proposed and the verifier read "has exported" as achieved. Defensible in both directions.
- C e2 and C o2. Enrichment and opportunity claims whose unsupported clauses are inside a creative proposal. Creative speculation and overreach are both defensible classifications; the verifier's category absorbs the clause without naming it.
- F3 s1. "Has never seen the labour" is a derived element's absolute, carried by an inferred stage. The verifier's overreach and the critic's support are both defensible.

Findings from the disagreements:
1. The verifier misses unconditional wording in proposed stages (A s3, B s3, F3 s2), and it under-classifies unsupported clauses in opportunities by calling the claim creative speculation (A o1, A o2, B o1, C e2, C o2).
2. The verifier over-flags self-labelled inferences and hypothetical orderings (C n3, C a3).
3. The verifier is strong on contradiction, on a requirement read as a state (C n1), on identity conflation (C a1, F3 s2 by the critic's reading), and on causal tags (F3 r3).
4. Critic error: two critic quote complaints (F3 s5 and F3 a3) were wrong. Both quotes are verbatim: E8 reads "coordinates its channel work". The owner's quote check accepted them, and the critic had misread the source. These are excluded from the agreement counts above.

## 6. Load-bearing claims

The rule marks a claim load-bearing when a `prerequisite`, `enables` or `complicates` relation, or an opportunity, uses it. It is a record-derived rule, not a score.

- A: load-bearing claims are s1 to s5 (5). Verifier flags: 3 of 5 load-bearing, 5 of 10 others. Critic flags: 4 of 5 load-bearing, 7 of 10 others.
- B: no load-bearing claim. Its relations reference developments, not stages, so the rule selected nothing.
- C: load-bearing claims are s1 to s4 (4). Verifier flags: 3 of 4 load-bearing, 10 of 18 others. Critic flags: 1 of 4 load-bearing, 8 of 18 others.
- Totals: verifier flags 6 of 21 fall on load-bearing claims (load-bearing flag rate 6/9 = 67%, others 15/28 = 54%). Most flags, 15 of 21, lie outside the rule's selection, mostly in relations and alternatives.

So the rule concentrated the verifier's flags only mildly, did not concentrate the critic's, and would have missed most problems if used alone. Relations were the most error-prone kind for the verifier (8 of 15 flagged) and the critic (9 of 15). The design's selection assumption is not supported by these exercises; the recommendation is to check relations as a class, and to keep the load-bearing list as an orientation, not a filter.

## 7. Owner-derived changes from prior

For the follow-up F3 (prior: synthesis A run 3), the agent's `changes_from_prior` lists four items (all four criticisms accepted; two relations withdrawn; one renumbering). The owner's derived comparison (`derived_changes`) reports 55 mechanical items: stage evidence sets changed in three stages, the earned conditions changed in five stages, the judgements of what a stage changes changed in five, alternatives replaced, opportunities withdrawn and added, open decisions and uncertainty replaced, relations withdrawn (four) and added (two), and one placement change.

Two points for the record. First, several derived items are not in the agent's list (evidence sets, conditions, alternatives). The agent's account is therefore not the sole account, as the design requires. Second, in the earlier A-to-D comparison the matcher reported two corrected stages as removed and added, because their wording fell below the similarity threshold. That was a false material change. The positional `revised` rule fixed it, with a regression test. The derived list still cannot decide whether a revised stage is the same judgement; it states the slot, and the author decides.

## 8. Reflective correction, measured

The follow-up F3 carried four verifier judgements (s1, s5, r3, r5 of A) as criticism, each with its verification identity. The agent accepted all four, withdrew the two relations they targeted, and relabelled two stages.

Second verification pass on all 14 claims of F3: 5 flagged (s1 overreaching, a2 modal, a3 overreaching, r2 and r3 unsupported). A's first pass flagged 8 of 15. Against the fresh critic, F3 has 3 flags (s2, r2, a2). Of the 14 F3 claims, 4 stages are now labelled proposed and 1 inferred, and no stage is recorded. A's first pass had 2 recorded stages.

The apparent improvement is partly a relabelling effect. Two recorded stages were relabelled (one inferred, one proposed), and the verifier's flag set is narrower for proposed stages: a proposed stage is judged as creative speculation unless its wording misreads a premise, and the critic's one real flag on a proposed stage (F3 s2) was missed by the verifier. The corrected answer is better grounded on the critic's count, but the apparent gain is not clean evidence that reflective correction improved grounding. The record can not separate the two effects.

## 9. Controlled reasoning comparison (Experiment A of the mission)

One question, the same packet of evidence (the Exercise A request), two arms: the structured synthesis (A run 3) and an ordinary prose answer from a fresh agent under no contract (`compare/free-prose-A.txt`, 500 to 800 words). A blind critic compared them with arm labels removed (`compare/blind-critic.md`).

- Grounding: prose 0 misreadings and 4 overreaches; structured 2 misreadings and 6 overreaches. The critic checked the quotations and found them verbatim in both arms. The structured answer's two misreadings were a stage presented as recorded on an unknown-legacy element, and a claim that E5 is truncated before the record says who can repair, which E5 does contain.
- Creative substance: the structured answer offered the sharper dilemma (dilution against outside apprentices) and more alternatives; the prose answer offered a more developable arc in which the labour cost becomes the centre of a stage. The critic would give an author the prose answer, adding the structured answer's dilution tension.

Limits: one question, one sample per arm, one critic. The arms differ in format (JSON against prose), which the critic can see, and in reasoning budget, which was not controlled. Conclusion: in this sample, the structured reasoning did not produce a clear creative advantage over prose, and it produced more misreadings. This is inconclusive, not a finding that synthesis is worse.

## 10. Authentic workflow comparison (Experiment B of the mission)

Not run. The ordinary-inquiry comparison from the previous increment was confounded (inquiry received no Working Book excerpts), and a fair version needs the inquiry owner to accept the same excerpts. That change touches an owner outside this increment, so it is deferred rather than improvised here. The finding stands: the earlier comparison cannot be used to rank the two workflows.

## 11. Served journey and reconsideration handoff (Exercise F of the mission)

- Served: one new browser test drives a claim check end to end: prepare for claim s1 bound to the synthesis; paste the verifier's response for that exact request; the verdict shows with its creative room; the verdict is offered as criticism; the follow-up request carries it with its identity. The test uses a replayed verdict through the test fixture, so it proves the mechanics and the bindings, not an authentic judgement. All six served synthesis tests and all six served consequence tests pass (12 in the boundary run).
- Not run: the authentic served journey on the Exercise A study with recorded answers, with exact request equivalence checked in the served page. The served page was not driven against the replayed study in this increment.
- Not run: the reconsideration handoff in an authentic synthesis. PR #653 implemented the handoff picker; this increment did not exercise it with a real accepted reconsideration.

## 12. Limits and what remains uncertain

- The verifier is a fresh agent, not a human judgement, and agreement with the critics is not proof either way. The verifier was right and the critic was right on about equal numbers of disputed claims. Neither is a ground truth.
- The verification vocabulary is bounded and was not expanded after the exercises. The verifier's `creative_speculation` category absorbed unsupported clauses inside creative proposals (section 5), which suggests a later increment should require the verifier to name any unsupported clause, not only the category.
- Proposed labels changed the verifier's flag set (section 8). Until basis relabelling is itself checked, a lower flag rate after correction is not evidence of better grounding.
- The load-bearing rule did not select most problems (section 6).
- Natural-language development selection is deferred with findings (design section 12.8).
- Human author evaluation is not claimed.
- The synthesis contract's own prompt still states no field limits. It was not changed in this increment (it would change every future synthesis request identity). The first verification run showed this class of failure; the synthesis prompt is the next candidate for the same correction.

## 13. Implementation review and fixes

An independent implementation reviewer (a fresh agent with the commit's source diff, no earlier context) reported seven findings on commit `8f90cde8`; the report is kept as `review-8f90cde8.md`. Each was checked against the code and fixed in a follow-up commit:

1. Carried criticism used identifiers from the earlier synthesis's packet in a follow-up that numbers its evidence afresh (a culmination absent from the follow-up shifts later identifiers). Fixed: the criticism names the claim by its wording and says the identifiers are not carried.
2. Stale verifications could be carried: the panel disabled the box, but the carried list and the owner did not check standing. Fixed: the owner refuses a carry whose evidence has changed, and the page drops a stale check from its carried list when it reloads.
3. A quote with no cited evidence was not checked against anything. Fixed: a verification's quote must come from an item it cites.
4. The `superseded` standing could not occur: a claim has one request for a given synthesis, since the request identity is its inputs. Fixed: the standing is `current` or `stale`, the pointer is removed, and the design no longer names a superseded verification.
5. The positional revision rule measured Jaccard, not the documented share of the prior item's words that remain, so a lengthened correction was reported as removed and added. Fixed: containment, as documented. The Exercise F comparison is unchanged under the new rule (55 items).
6. Response and result were written in an order where a crash could leave a response that blocked a retry. Fixed: result first, then response, in both the verification and the synthesis owners.
7. The served panel's drafts were keyed by claim name, so a pasted response could appear under another synthesis's claim of the same name, and a late failed load could blank a newer panel. Fixed: drafts are keyed by request identity; a load only clears the state it owns.

Checked and clear by the reviewer: no narrative or Architecture write; refused judgements never reach `result.json`; no null dereference on an absent projection.

## 14. Validation

- Focused (L1) on the final code: `tests/test_architecture_verification.py` (33), `tests/test_architecture_synthesis.py` (24), `tests/test_architecture_reconsideration_repairs.py` (8), `tests/test_architecture_reconsideration.py` (13): 78 passed.
- Named boundary (L2), served: `tests/test_beginner_studio_consequence_browser.py` and `tests/test_beginner_studio_synthesis_browser.py`: 12 passed. These cover the consequence and reconsideration owners' served page, since the synthesis panel mounts beside them.
- Lint: ruff is clean on the changed source and scripts and on the new test module. The served test module keeps the fixture-import pattern that `main`'s synthesis tests already use.
- Not run: L3 full regression (no checkpoint trigger). No release qualification.
