# Grounded creative synthesis: evaluation record (2026-11-28)

Branch `feat/grounded-creative-synthesis`, from `main@b3e4bfb9` (PR #654 merged). Commits `e61acb07` (checkpoint) and `ec665547` (review repairs). Evidence folder: this directory. Every answer, refusal, refusal message and critic report named here is kept beside this file. Nothing here is a human author evaluation, and no conclusion below is a claim of general reasoning reliability.

## 1. Starting and current state

- Start: `main@b3e4bfb9`, PR #654 merged. PR #540 (an unrelated research branch) was not touched.
- Current: this branch, 2 commits on top of `main@b3e4bfb9`. PR status is given in section 12.

## 2. Integration responsibilities completed (Lane A)

- **Authentic reconsideration handoff (owner-level, authentic reasoning).** A fresh chain was run on a new Spring Ledger study: discovery, inquiry, revision, consequence analysis, reconsideration, synthesis. Every stage was prepared through its owner, answered by a fresh agent, and completed through its owner. Nothing was replayed. The earlier PR #645 chain did not reproduce from the current seed (the discovery request differed), so it was not used: replaying it would have re-bound historical answers to new requests.
- Result: an accepted reconsideration of the analysis's reach claim (`conditional_inheritance`), disposition `unresolved`, standing `current`. The synthesis that received it cites the handoff's evidence (E5), carries the route as an unresolved hypothesis, keeps its basis `proposed`, and reports the handoff's own uncertainty. This was exercised through the owner, not through the served picker (section 9).
- Refusals kept: revision attempts 1 and 2 (an interpretation's `affects` named question identifiers, which the owner accepts only for nodes); a third attempt the agent declined to write because the candidate already held the maximum of 16 open questions and "change nothing else" forbade retiring one; the author-equivalent resolution was to reword the existing question `q-right-revocable` keeping its identity, which the accepted revision does (one question changed, none removed). Consequence attempt 1 (counterevidence must cite material other than the mechanism it challenges) was refused; attempt 2 was accepted.
- Not done in Lane A: the authentic served journey (the synthesis, the claim check, the carry and the follow-up were not driven through the served page with authentic answers), and the native inquiry-versus-synthesis comparison on comparable objectives (section 6).

## 3. Synthesis contract reliability (Lane B12)

- Every owner-enforced bound on the synthesis answer and the verification is now generated from the same JSON Schema the output contract carries (`contract_limit_lines`, `limits_instruction`), so an instruction cannot omit a bound. The bounds include the minimum of one character or item and the correct pluralisation.
- The synthesis instruction now states its bounds. New synthesis requests therefore have new identities; historical requests, responses and results keep theirs (the replay of the PR #653 requests is not re-run here).
- Regression tests: `tests/test_contract_limit_instructions.py` (4 tests) and the verifier instruction test.
- Known and not yet repaired: the consequence analysis's instruction does not state its counterevidence rule (the refusal in section 2 is the evidence). This is the same class of omission and is recorded as the next candidate.

## 4. Semantic verification improvements (Lane B9)

- Clause-level judgement (contract version 2). A verifier names the parts of a claim it judges (clauses), each copied from the claim's own words. The owner checks identity and consistency only: a clause must be words the claim contains and at least 12 characters; a judgement must name at least one clause; a supported judgement cannot carry a clause the verifier marks proposed, unsupported or contradicted; a claim with an unsupported clause cannot be judged supported, a defensible inference or creative speculation, and must name the defensible creative possibility.
- Limits of this: the owner cannot detect a part the verifier leaves out, and cannot judge meaning. A part the verifier omits is an instruction to the verifier, not a check. The independent review found the first version of these rules could be satisfied by omission or trivial substrings; both were repaired (section 8).
- Version-1 requests still complete under version 1 (the test covers this).

## 5. Epistemic-label sensitivity (Lane B10)

Paired cases on one fixed evidence packet (the Exercise A packet), changing one controlled feature each. Ten pairs (P1 label, P2 wording, P3 unsupported premise against none, P4 labelled inference against recorded label, P5 hypothetical ordering against asserted necessity). Each claim was judged by a fresh verifier.

Round v1 (filler text in the stage's `becomes_available`/`changes` fields and an asserted "already shown" effect in P5, both confounds of my own design):
- P2a (unconditional proposal) was judged `creative_speculation`: a miss.
- P3b (no unsupported premise) and P5a (hypothetical ordering) were flagged, partly because of the filler and the effect text.
- P1a/P1b (recorded against proposed, same wording) were both flagged, with different categories: the label changed the category, not the flag.

Round v2 (neutral filler, same instruction): P2a still a miss; P3b no longer flagged; P5a refused by the owner's clause rule (the verifier had found a sub-clause unsupported but judged the claim creative speculation): the refusal is the rule working as designed, and the refused answer is kept.

Correction and round v3: the instruction now says a proposal is stated conditionally, and a label does not license its tense (proposed claims only). Results: P2a flagged as a modal misreading (fixed). P2b (a conditional claim) refused in one of three runs, because the verifier marked a conditional consequence as unsupported; P3b flagged as a modal misreading because my neutral filler ("The stage asks what…") reads as an indicative proposal. Replicates: v3 P2a flagged in both runs; v3 P2b clean in two of three runs; v2 P2a flagged in one of three runs (one refused, one a miss).

Verdict on the correction: keep it, with the trade-off disclosed. It fixes the target miss consistently in v3 and over-flags conditionals in roughly one of three runs. Samples are one to three per condition: none of this establishes the rate.

Labels: the sensitivity results do not show superficial relabelling suppressing flags in this set (P1b was still flagged), but they show that the label moves the verifier's category and that unconditional wording under a proposed label escaped examination in every v1 and v2 run.

The v1 "requests" folder was regenerated after the first round and no longer matches the first round's instruction; the first round's requests are the preserved `requests_opaque` files, which the answers were given against.

## 6. Reasoning composition (Lane B13) and workflow comparison (Lane A, partial)

Composition: one packet (the handoff synthesis's question, developments, evidence and handoff), three arms: (A) the structured synthesis (accepted, owner-checked); (B) free-form prose, no contract; (C) an exploratory working note, then a structured expression through the same contract (the expression was checked by the owner's answer checks in memory, not stored, because its request had already been completed in the copied study).

Blind critic (one critic; labels hidden; it reports grounding and creative substance separately): grounding flags, A 1, B 1, C 4. Creative: C produced the richest ideas; B gave the clearest next choices for an author; the critic would give an author B, with C's ideas as material to check.

Interpretation: exploring first increased the number of possibilities and the number of grounding overreaches in this sample; expressing the exploration in the contract did not remove them. One critic, one packet, one sample per arm: this is evidence about this packet, not about the composition approaches in general. The mission's Approach C concern (whether structured expression loses or adds claims) is answered only for this packet: it added four overreaches.

Workflow comparison: not run in comparable form. The chain's inquiry (anchored on possibility p3) and the handoff synthesis (anchored on two questions) have related but not equivalent objectives, and the inquiry is a native product workflow that was run with its own packet. A comparison on equivalent author situations needs the inquiry and synthesis run on one shared objective, and the critic on both; that was not done.

## 7. Portfolio-centred and culmination-centred work (Lane C)

Not done. The handoff synthesis is a two-development question, which is a first step toward portfolio reasoning, but no portfolio exercise over three or more independently valuable developments, and no culmination exercise with alternative payoffs, was run in this increment. The synthesis owner's bounds (three developments, six stages) were not raised.

## 8. Independent review and repairs

An independent reviewer (fresh agent, source diff only) reported six defects in the increment; all six are repaired in `ec665547` and tested:
1. The clause check could be satisfied by omission or a one-character substring. Repaired: a judgement must name clauses; a clause must be at least 12 characters of the claim's own words.
2. A supported judgement could carry a proposed clause. Repaired: refused.
3. The instruction contradicted the contract (version 1 in the key list, omitted keys). Repaired: version 2 and every key.
4. The generated instruction omitted conditional requirements and the minimum of one. Repaired: the conditional requirements are stated in the instruction; the generator states the minimum.
5. The tense rule reached inferences as well as proposals. Repaired: proposed claims only.
6. Requests prepared under version 1 could not complete. Repaired: they complete under the version-1 model they were prepared with.

## 9. Served journey and served picker

- Browser mechanics: the served boundary (synthesis and consequence browser suites, 12 tests) passes on the repaired code. The served synthesis tests drive the claim check with replayed verdicts through the test fixture; that proves the mechanics and the bindings, not an authentic judgement.
- Not run: the authentic served journey (the served page driven with authentic answers from the chain, with exact request equivalence checked in the served page), and the served handoff picker on the chain's accepted reconsideration. The handoff was exercised at owner level only.

## 10. Architectural decisions

- Instruction bounds are generated from the contract, not hand-written (rejected: maintaining hand-written limits, which drifted in the first authentic run).
- Verifier judgement is clause-level and mechanically checked for identity and consistency only (rejected: a semantic check by the owner, which the owner cannot perform; and a permanent ontology of claim parts, which the design rejects).
- Version-1 requests keep their contract (rejected: rebinding pending requests to version 2, which would silently change what the author was asked to judge).
- Contract conflicts are resolved by an authorial-equivalent rewording of an existing question with its identity kept (rejected: retiring a question, which removes author work).

## 11. Limitations

- Every sample here is small: sensitivity pairs are one to three runs per condition; the composition comparison is one critic on one packet; the chain is one chain.
- The verifier's clause judgements are not validated against author judgements.
- The consequence analysis's counterevidence rule is not stated in its instruction (section 2).
- The served authentic journey and the served picker are not exercised.
- Natural-language development selection, relation-centred examination and the portfolio and culmination work (Lane C) are not done.

## 12. Validation

- L1 focused (after repairs): 91 passed (`tests/test_architecture_verification.py`, `tests/test_contract_limit_instructions.py`, `tests/test_architecture_synthesis.py`, `tests/test_architecture_reconsideration_repairs.py`, `tests/test_architecture_reconsideration.py`).
- L2 served boundary (after repairs): 12 passed (`tests/test_beginner_studio_synthesis_browser.py`, `tests/test_beginner_studio_consequence_browser.py`).
- L3 not run (no checkpoint trigger). No release qualification.
