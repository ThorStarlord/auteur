# Creative portfolio and culmination construction: evaluation record (2026-11-28)

Branch `feat/creative-portfolio-culmination` from `main@8b707652` (PR #655 merged). Owner-level changes are in commit `657a34f9`. Evidence: this folder. Every answer, refusal, verification, critique, paste and served state named here is kept beside this file, unedited. Nothing here is a human author's evaluation. The narrative material is an author-supplied premise that no human author has judged; every critic is a fresh agent, not a reader.

## 1. Claim ceiling (implemented, demonstrated, creative value, qualification)

- **Implemented:** parallel culmination configurations (standing per configuration); two instruction repairs at their owners (consequence v3 counterevidence rule; architecture `affects` node-only rule); the served page and owners unchanged otherwise.
- **Demonstrated (owner level):** a portfolio of three developments of mixed kinds (a mechanism, a mechanism layer, an author question) was synthesised into relations, sequences, culminations and opportunities; two culminations were held as parallel investigations; a reflective follow-up carrying criticism and two verifications changed the judgement in the ways the criticism asked; a second follow-up carried a further criticism and withdrew a clue reading that a grounding critic had shown to contradict the Story Vision.
- **Demonstrated (served):** the page prepared exactly the requests the owner prepares (four exact sha equivalences); accepted the recorded authentic answers for those requests, verified by stored content; ticked a reconsideration handoff through the picker, and the synthesis request carried it as evidence E5; the fresh answer to that handoff request was stored unedited.
- **Creative value (judged by fresh critics only):** the portfolio contains interactions that a single development does not give (section 5). Critics judged the reflected version more valuable than the plain one, and the native inquiry more useful for one decision. These are one critic and one packet per comparison.
- **Not demonstrated:** that the portfolio is creatively right for any author; that synthesis is better than ordinary inquiry in general; any Series-scale placement (no Book exists; every stage is a proposed placement without a number); that the verifier's judgements agree with a human.

## 2. Narrative material and selection

The Wandering Islands premise (`SETUP-NOT-RUN.md`, section 2) was frozen as the Story Vision (`wandering-islands/story-vision.txt`). It is an author-supplied twelve-Book fantasy with a non-character causal system (the migrations), a mystery (the island that does not return), a warm everyday register and an explicit earned-hope constraint. Its earlier worker run was never executed, so no Books or Working Book elements exist for it. The Spring Ledger study was kept for the reconsideration handoff (section 8), because its chain can be rebuilt with fresh answers.

Architecture (accepted, `wandering-islands/architecture/`): 27 nodes, 7 phases, 4 interpretations (one marked for author decision), 5 persistent questions, all continuing.

## 3. Architecture: one refusal, one repair, one acceptance

- Attempt 1 (request `54ed0cbf…`): refused whole by the owner: `interpretation 'int-discoverable-cause' affects unknown nodes: ph-reframing`. The fresh agent named phase identifiers in `affects`. The owner enforced the node-only rule but the instruction did not state it. Kept in `wandering-islands/architecture/refused/`.
- Repair: the instruction now states the node-only rule (`studio_architecture.py`; test `tests/test_architecture_interpretation_affects.py`).
- Attempt 2 (request `ec7f3d81…`, repaired instruction): accepted on its first completion.

## 4. Portfolio: developments, configurations, reflections

Developments, identical in every run: `en-unreturned-island` (mechanism: the broken pattern), `en-bond-maintenance` (mechanism: sustaining bonds across distance), `q-migration-explicability` (persistent question: how far the migrations are explained by the end). Question text, identical in every run: the portfolio question, which asks for each development's contribution, interactions, and two sequences (explicability first, bonds first).

| Run | Inputs | Request (prefix) | Owner | Outcome |
|---|---|---|---|---|
| S1 plain | question only | `341b276e…` | accepted, first completion | 6 stages (all proposed placements), 5 relations, 3 alternatives (explicability-first weakened; bonds-first viable; interleaved viable), 3 opportunities; agent offered no culmination |
| S2 culmination A | + "the island returns, altered" (working configuration) | `6bbce9e4…` | accepted | culmination with necessary conditions, enrichment, standalone value |
| S3 culmination B | + "the island is not restored; bonds re-formed" | `23e81a1d…` | accepted | culmination grown by earlier stages; standalone value per Book |
| S4 reflection of S1 | follow-up; criticisms c1 (grounding critic), c2 (creative critic); verifications r2 and o3 carried | `a7d9d69a…` | accepted, first completion | section 4.1 |
| S5 reflection of S2 | follow-up; criticism on culmination A (creative critic) | `54f6db81…` | accepted | culmination reconsidered as the return that tests what was kept, at a cost; "no return" alternative added |
| S6 reflection of S4 | follow-up; criticisms from the grounding critic on S4 and the creative critic's suggestion | `8cb56f08…` | accepted | section 4.2 |

Configurations. S2 and S3 are two culminations of the same developments, so they are separate configurations. Before this increment the owner keyed standing by developments alone: preparing S3 would have marked S2 superseded and hidden its unanswered request from the page. Test first (red: two new tests in `tests/test_architecture_synthesis.py`), then the repair (green). Requests without a culmination keep their identities and standing.

### 4.1 S1 to S4

The owner's comparison of S4 with S1 (derived from the stored answers, 53 items): 2 alternatives added and 2 removed; 4 relations added; 2 opportunities withdrawn; 4 open decisions added and 4 removed; 6 stage judgements changed; 4 stages revised; 2 stages reworded.

What the criticism changed:
- The author's design question (d3: how much the Series discloses by its end) is separated from the characters' in-world attempts to explain (grounding c1). S1 had treated it as in-world curiosity.
- The d3 to d1 relation is restated from causal to a bounded thematic tendency about the final Books (c1, and verifier r2, whose causal clause was marked conditional). S1 had said d3's answer "constrains how long d1 can run".
- d2 and d3 are independent unless the author adopts a clue proposal; S1 had called them independent and also coupled (c1, c3).
- The clue reading (the practices may carry traces of the migrations' order) enters as a proposed stage, path and opportunity, with its planting obligation (creative c2; the answer labels it a proposal).
- The interleaved order is dropped and the explicability-first order is no longer marked weakened (c2): both orders share the in-world inquiry and differ in when the reader learns how much the world can be known.

### 4.2 S4 to S6

The grounding critic on S4 (fresh agent, `critics/critic-grounding-s4.md`) found the reflection mostly repaired, with four residual overreaches of labelling and inference: the explicability-first path brought back the in-world/disclosure confusion; the first-to-sixth relation labelled causal while its reason calls it a craft condition; a "complicates" relation whose reason says no constraint is recorded; and an opportunity that reads repeated action families as rival stances. It also noted that the clue proposal ignored the Vision's "unpredictable" and that the changes list did not report a removed stage.

S6 accepted the grounding critic's points (c1, accepted) and partly accepted the creative critic's suggestion (c2): the clue reading, which the Vision's "unpredictable" weakens, was demoted to a weakened alternative, and the creative critic's suggestion entered as the proposed sixth stage: a homecoming practice held for an absence. It also dropped the rival-readings opportunity and re-labelled the first-to-sixth relation as thematic preparation.

Trade-off, kept visible: the most creatively alive idea (the double-coded practices) was weakened by the grounding critic's correct point about "unpredictable". The author decides whether the Vision allows an order encoded in custom at all. This is recorded as an open decision in S6.

### 4.3 Emergent possibilities (the required creative achievement)

The clearest interaction that no single development gives alone, as it stands in S6: a practice keyed to the expected return (a homecoming held for an absence) joins the broken pattern and the bonds in one image, and the tradition built to welcome an island home must decide what it is for (opportunity over d1 and d2, proposed). The earlier clue reading, which joined d2 and d3, is kept only as a weakened alternative, because the Vision's "unpredictable" contradicts it. Both possibilities are proposals; neither is record.

## 5. Claim verification

Four claims were checked against the exact evidence that S1 read: r1 (enables), r2 (complicates), o3 (the three-way opportunity), s5 (a conditional stage). All four are `defensible_inference`, with `relation_survives_correction: yes`. Each claim's clauses were judged supported, inferential or proposed; none was a misreading. The verifier passed r2, which the grounding critic on S1 called overreaching: that disagreement is recorded, not resolved. r2 and o3 were carried into S4.

## 6. Independent critics

- **Grounding, S1** (`critics/critic-grounding-s1.md`): 33 claims; supported 14, defensible inference 13, overreaching 5, misread 1, unsupported 0. Findings carried into S4 as c1 and c3, all accepted or partly accepted.
- **Grounding, S4** (`critics/critic-grounding-s4.md`): 41 claims; supported 19, defensible inference 18, overreaching 4, misread 0, unsupported 0. Findings carried into S6.
- **Creative, blinded four-way** (`critics/critic-creative-blind.md`; key `critics/blind-key.json`): W1 = culmination A, W2 = culmination B, W3 = plain S1, W4 = native inquiry. Judgement: the inquiry gave the most generative ideas and the clearest craft obligation (clues planted in domestic texture from the first Book), and it would be the most useful for the author's next decision; culmination B was the most earned ending; culmination A was announced, and its "map believed fixed" premise conflicts with the Vision; the plain synthesis was careful but null on the culmination question.
- **Creative, blinded two-way** (`critics/critic-creative-reflection.md`; key `critics/blind-key-reflection.json`): V1 = plain S1, V2 = reflected S4. The reflected version was judged more valuable and more faithful to the Vision, with the clue reading its most alive interaction (conditionally earned). Costs named: the clue proposal couples two developments meant to stay independent; the planting burden falls on the first Book; it risks making belonging instrumental. Its single suggestion (tie the inherited code to the missing island, a homecoming held for an absence) became S6's proposed stage.

## 7. Native inquiry versus synthesis, one objective

Both were run on the same developments and the same question through their owners: the inquiry as a `compare` operation over the same three anchors with the same author text (`inquiry/`); the synthesis as S1.

- Evidence access was not equalised, as the mission asks: the inquiry request was 65.8 KB against 32.6 KB for the synthesis (the inquiry is given the whole working candidate). Answers: 8.3 KB (inquiry), 11.1 KB (synthesis).
- Narrative understanding and opportunities: the inquiry gave two alternative readings with a stated divergence axis and the clearest uncertainties; the blinded critic ranked it first for the author's next decision.
- Developmental causation and relations: the synthesis gave the staged causation (each stage's `becomes_available` and `changes`) and dependence-typed relations, which the inquiry does not.
- Evidence recovery, intellectual continuity and author effort: one fresh agent each, one completion each, no refusal on the first attempt in either.
- Not shown: superiority of either. One critic, one packet, one sample per arm. The complementary reading: the inquiry supplies ideas and the synthesis an ordered causal structure that can be checked stage by stage.

## 8. Served journey and the reconsideration picker

### 8.1 Served journey (Wandering Islands), exact request equivalence

| Step | Page action | Request (prefix) | Equivalence | Answer |
|---|---|---|---|---|
| 1 | three developments; question; "Prepare synthesis" | `341b276e…` | equals S1 | recorded S1 response object; stored text equals `answer-s1.json` |
| 2 | "Check this claim" r2 | `ccf361ff…` | equals r2 verification | recorded verifier response; equals `answer-v-r2.json` |
| 3 | "Check this claim" o3 | `9d1cbf67…` | equals o3 verification | recorded verifier response; equals `answer-v-o3.json` |
| 4 | carry r2 and o3; "Criticise or continue"; question and two criticism lines; "Prepare follow-up" | `a7d9d69a…` | equals S4 | recorded S4 response; equals `answer-s4.json` |

Mechanics: no horizontal overflow at 1024 px; no page error. The one 404 in the console came from a URL I guessed while probing the page, not from the page. Browser-pane limits: clipboard paste did not reach the page, so the responses were typed; one form tool stored a JSON-shaped value as `[object Object]`, which was caught and corrected by typing. The step-4 request equals the recorded one only because the typed criticism lines and the carried verifications were in the same order as the recorded spec. The screenshot is `served/served-follow-up-trajectory-1024px.jpg`.

### 8.2 Spring Ledger: fresh chain, then the picker

The PR #655 chain cannot be replayed exactly from a fresh seed: the architecture instruction repair (section 3) changed the identity of every new architecture request, including the Spring Ledger seed. The mission's rule for this case is fresh requests with fresh answers, so a new chain was run (`spring-ledger-handoff/chain/`; the replay-driver is `scratchpad/sl/chain_replay.py`, which is the PR #655 driver with a new root):

- Discovery: fresh answer, accepted; four possibilities; the chain's selected possibility p3 (as in PR #655).
- Inquiry on p3: fresh answer, accepted.
- Revision with the reworded instruction (`instruction-h2-reword.txt`, the one PR #655 accepted): fresh answer, completed through its owner.
- Consequence analysis of the pending revision: fresh answer, accepted on its first completion (status `ready`, four concerns, four alternatives). Under PR #655 the first attempt had been refused for the counterevidence rule. This is one sample under the repaired version 3 instruction, not a rate. Caveat: this agent reported 25 tool uses, more than the packet-only protocol allows, and I did not inspect its transcript; the owner's acceptance is the only check on its content.
- Reconsideration of the reach claim (`conditional_inheritance`) with the recorded instruction and criticism: fresh answer; accepted; disposition `qualified`; criticism c1 partly accepted; zero refused attempts.

Served picker (Spring Ledger, served from the replayed study on port 8797): the synthesis section offered the accepted reconsideration (`fb46abf6…`, status ready, standing current) as a handoff checkbox. I ticked it through the page with the developments `q-right-revocable` and `q-compact-settlement` (the two questions PR #655's handoff synthesis used). The page prepared the synthesis (request `bb0ec2a4…`). The request's evidence carried the handoff as E5 (kind `handoff`, owner `reconsideration owner: accepted judgement, advisory`). A fresh agent answered that request; the answer was pasted (typed), stored and equals `answer-handoff-synthesis.json`. The answer cites E5 in its trajectory, relations, alternative paths and opportunity; it names the reconsideration's point about the training condition's hinge and its unestablished presence in Book 24 (uncertainty item 1).

Caveat on the handoff's use: the answer cites E5, but whether it reads E5 correctly is for a grounding critic, which I have not run on this answer. It is recorded as unverified.

## 9. Product decisions and gaps

Repaired in this increment:
1. Standing per developments hid parallel culmination configurations. Repaired (section 4).
2. Two instruction omissions at the owners that enforce the rules: consequence v3 counterevidence; architecture `affects` node-only. Repaired (sections 3 and 8.2). Both change the identity of new requests; stored requests are untouched.

Open, not repaired here:
3. Proposed stages cannot carry a Book number. The owner refuses a Book number on a proposed stage by design (`test_a_stage_that_names_no_book_that_exists_or_that_is_proposed_with_a_book_is_refused`), so a twelve-Book placement can only be stated in prose. This is a Series-scale semantics decision (owner-reserved): a placement field for proposals would have to say that it is a proposal. Recommendation: decide the semantics before any change.
4. Culmination provenance. The owner's `culmination` field is documented as the author's named culmination. Working configurations proposed by the exercise (A, B) are indistinguishable to the owner from author-named ones; this record labels them only in the text. Recommendation: a provenance label on the culmination, decided by the author-side owner.
5. The author-question versus in-world confusion appeared in S1 and was repaired by reflection in S4, but the synthesis instruction does not prevent it. An instruction sentence would change every synthesis identity, including the served answers recorded here, so it was not added. Recommendation: add it with the next instruction revision, and re-run the served journey with fresh answers.
6. Agent-proposed culminations are part of the contract (`culmination: an object, or null when the author named none and you offer none`), and S1 offered none. The reflections proposed no new culmination object either. Not investigated further.
7. The verifier and the grounding critic disagreed on r2 (defensible inference against overreaching). No ground truth exists here; the disagreement is kept.
8. The grounding critic's residual overreaches on S4 were repaired in S6 (section 4.2), but S6's own grounding has not been checked by a critic.

## 10. Validation

- L1, focused (after all code changes): `tests/test_architecture_synthesis.py`, `tests/test_architecture_verification.py`, `tests/test_contract_limit_instructions.py`, `tests/test_architecture_consequence_v3.py`, `tests/test_architecture_interpretation_affects.py`, `tests/test_beginner_studio_architecture.py`, `tests/test_architecture_consequence.py`, `tests/test_architecture_consequence_mechanisms.py`, `tests/test_architecture_question_projection.py`: 222 passed.
- L2, named boundary (served synthesis and consequence browser suites, Chromium via the system Python 3.14): `tests/test_beginner_studio_synthesis_browser.py`, `tests/test_beginner_studio_consequence_browser.py`: 12 passed.
- L3: not run (no checkpoint trigger). No release qualification.
- Independent implementation review of the owner diff: fresh reviewer, `scratchpad/wi/review-diff.md` (its verdict is in section 11).

## 11. Independent review of the owner diff

Verdict: APPROVE, no blocking defects (`review-diff.md`, copied to the evidence folder). The reviewer checked that requests prepared before the change keep their standing, that requests without a culmination keep their identities, and that both instruction sentences match the owners' validators; it also judged that the new tests fail on the pre-change code.

Non-blocking findings and what was done: (1) an identical culmination request re-prepared after the change has a new identity (stated in the design document, section 13.1 identity note); (2) a follow-up that adds or changes a culmination does not supersede its prior, which is the parallel-configuration meaning; the `_standing` docstring still said 'the same developments', and was corrected to 'the same configuration'; (3) an optional simplification (derive the key from `culmination_sha256`) was not taken, because the stored field keeps the key readable in the request.

## 12. What the increment does not establish

- No human author evaluation. No Series-scale qualification (no Book is written; no placements are numbered).
- Small samples throughout: one portfolio per configuration, one chain, one composition, one blinded comparison per question.
- Critics and verifiers are fresh agents of the same model family as the answering agents; their agreement is not proof.
- The served journey and the picker were exercised through the page with recorded or fresh answers; no author typed a creative judgement.
