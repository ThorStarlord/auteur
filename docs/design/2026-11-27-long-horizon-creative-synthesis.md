# Long-horizon creative synthesis: trajectories, relations and culminations (design, 2026-11-27)

Status: design for the initial construction increment on `feat/long-horizon-synthesis`, from `main@077edc09` (after PR #652).
Advisory. A synthesis changes no Working Architecture, no Working Book, no Identity, Structure, Realization or Expression record,
applies nothing, and is not canon. It invokes no agent and no critic by itself.

Governing sources: `MISSION.md` (hard invariants, author authority), `docs/design/2026-10-09-living-story-studio.md` (agent-first
contract, noncanonical working material, explicit owner actions), `docs/design/2026-11-27-evidence-grounded-reconsideration.md`
(the consequence lineage this builds on).

## 1. The responsibility

An author selects one to three existing creative developments (persistent questions, or Architecture mechanisms: a node or a link),
writes what they want to understand in ordinary language, and may name a possible culmination. Auteur prepares one bounded request
built from the owners of each source. A fresh agent returns one structured synthesis. The owner validates it and stores it beside
the request. The synthesis reads as a trajectory first: stages across Books, how each becomes available, how it changes what came
before, and what remains open. Portfolio relations (reinforcing, independent, complicating, incompatible, necessary or helpful
preparation) and culmination conditions (necessary preparation versus optional enrichment, and what earlier Books keep as their own
experience) appear inside the same judgement. They are not three engines.

## 2. Ownership: what each component owns

| Responsibility | Owner (existing or new) | Decision |
|---|---|---|
| Source evidence: Working Architecture (nodes, links, phases) | `studio_architecture.py` (`_candidate`, `project_architecture`) | Reuse. Read now; the candidate fingerprint is recorded. |
| Narrative identity of a question | `studio_architecture_question_projection.py` (`project_architecture_questions`) | Reuse. Questions are identities; standing is read there. |
| Cross-Book evidence | `series/working_book_architecture.py` (`book_numbers`, `book_elements`) | Reuse. Elements cite nodes (`series_refs`) and questions (`question_refs`); coverage counts are exact and read now. |
| Selected creative alternative and its instruction | Revision request provenance (`studio_architecture.py`, `requests/<sha>/request.json`) | Reuse. The request keeps the full record; the consequence packet only clipped it. Recovery is validated by lineage (section 6). |
| Accepted or qualified judgements about a consequence claim | `studio_architecture_reconsideration.py` | Reuse as handoff source (section 7). It stays the owner of reconsiderations. |
| Proposed developmental judgement (trajectory, relations, culmination) | **`studio_architecture_synthesis.py` (new)** | New owner of one judgement type. It has request, response, result and refusal records, a latest pointer, and standing, all in the consequence lineage. |
| Standing (current, superseded, stale) | Synthesis owner, from a recomputed evidence fingerprint | New, in the same pattern as consequence standing. |
| Authorial acceptance | None in this increment | A synthesis is never applied. Any later change to the Architecture goes through the existing revision and apply owners. |
| Narrative canon and commitments | Existing owners only | Not touched. |

## 3. Options considered

- **(a) Extend the existing inquiry owner.** Rejected for the first increment. Inquiry anchors name Architecture nodes, links, questions or one Book element. It has no trajectory contract, no stage or relation vocabulary, and its prior exchanges carry text without binding to evidence. Widening it would blur an answer-to-a-question with a judgement over time.
- **(b) Compose consequence analysis and reconsideration.** Rejected. Both examine a pending revision's change. A synthesis looks forward from developments that already exist, with no pending revision.
- **(c) A bounded synthesis owner that consumes the owners above.** Selected. It reuses the consequence lineage for storage, refusal, freshness and the host-agent contract. It adds one judgement type and nothing else.
- **(d) A derived projection over existing records.** Rejected. A trajectory is an agent judgement. Presenting it as a projection would present a judgement as a record.
- **(e) A dedicated persistent trajectory store.** Rejected. The request, response and result already persist beside the owner's lineage. A second store would duplicate lifecycle and standing.
- **(f) Three engines (trajectory, portfolio, culmination).** Rejected by the mission. One contract carries all three, and the trajectory is its spine.

## 4. Developments and admission

The author selects one to three developments from the current Architecture: a persistent question, a mechanism node, a mechanism
link, or the selected creative alternative of a pending revision. Each selection is read by the owner, which records its identity
and text. A development that no longer exists in the current Architecture is refused by name.

Admission is explicit. The request carries four evidence sets, which are kept distinct:

- **historically available:** evidence the owner read for this request, identified but not necessarily shown;
- **supplied:** evidence whose content is in this request (a development's own text, its Working Book element excerpts, its
  coverage record, the links among the selected developments, the author's vision and accepted constraints, and any handoffs);
- **recovered:** exact source wording recovered by an owner-qualified path (the full selected alternative, the full revision
  instruction, the full mechanism record);
- **cited by the agent:** what the answer names. A citation resolves only to supplied or recovered evidence. A citation to
  something that existed but was not supplied is refused with that reason.

An identifier's existence is not proof that its content was available. The reconsideration owner had admitted every packet
identifier, not the claim's supplied identifiers, and section 6 repairs that.

The coverage record also states, for each cited element, whether its identical text appears in another Book (an exact text
comparison, not a judgement). The Spring Ledger study holds such repeats (Book 25 carries Book 24's elements word for word), and the
owner states the fact so a reading does not mistake a repeated record for a new development.

Bounds: at most three developments; at most twelve Working Book element excerpts per development, each excerpt at most 400
characters and labelled when truncated; exact counts of readable elements, considered elements and citing elements regardless of
listing bounds; at most two handoffs; at most four criticisms. Recovered records are capped at 8,000 characters and labelled when
longer, so a full selected alternative is not truncated in practice.

## 5. The synthesis contract (`SynthesisAnswer`, schema version 1)

- `trajectory`: two to six stages. Each stage has `book` (an existing Book number, or null), `horizon` (`existing_book` or
  `proposed_book`), `development` (what happens, conditional when proposed), `becomes_available` (the earlier condition that makes
  it possible, cited), `changes` (what it changes in what earlier developments mean or make possible), `basis` (`recorded`,
  `inferred` or `proposed`) and `evidence`. Stages are ordered by developmental dependency. A stage's book number is a placement,
  not a claim of chronology, unless the record states it.
- `relations`: zero to eight. Each has `kind` (`prerequisite` (necessary), `preparation` (helpful), `enables`, `complicates`,
  `reinforces`, `independent`, `incompatible`), `between` (developments `d1` to `d3` or stages `s1` to `s6`), `dependence`
  (`causal`, `thematic`, `sequential_only` or `none`), `reason` and `evidence`.
- `culmination`: present when the author named a culmination; optional otherwise. Holds `statement`, `necessary` (preconditions),
  `enrichment` (optional strengthening), and `standalone_value` (what the earlier Books keep as their own experience if the
  culmination never arrives).
- `alternative_paths`: one to three. Each has `ordering` (what occurs earlier, later or differently), `effect` (what changes for the
  reader and the developments), `viability` (`viable`, `weakened`, `closed` or `unresolved`) and `evidence`.
- `opportunities`: zero to three. Each names two or three developments whose interaction yields something neither gives alone.
- `reader_experience`: what makes the trajectory compelling as an experience.
- `open_decisions` and `uncertainty`: what should remain open, and what the record does not establish.
- `criticism_assessments`: zero to four, each assessing a criticism the request supplied by its owner identifier (verdict and reason),
  as in reconsideration.
- `changes_from_prior`: zero to four. Used only by a follow-up request; it states what changed in the judgement and why.

The owner validates cited identifiers, stage and development references, the requirement of evidence for `recorded`, `inferred`
and for the necessary relations, the existence of each Book number, criticism identities, and the presence of a culmination when
the author named one. A refused answer is kept beside its refusal and never becomes the synthesis.

The distinctions in the mission (necessary preparation versus helpful preparation, causal dependence versus thematic resonance,
developmental sequence versus chronological adjacency, emergence versus repetition, earned culmination versus predetermined
fulfilment, productive tension versus destructive interference, possibility versus commitment) are represented only where a field
carries them: `kind` (necessary and helpful, and tension and interference), `dependence` (causal and thematic), `basis` (recorded,
inferred, proposed), `viability`, and `standalone_value` (possibility that does not depend on culmination). Whether those fields
improve the reasoning is tested by the exercises (section 10), not assumed.

## 6. Repairs to the reconsideration owner (`studio_architecture_reconsideration.py`)

**6.1 Provenance-bound recovery of the selected creative alternative and its instruction.** The consequence packet clips the
selected alternative to 600 characters and the revision instruction to 1,200. A reconsideration of a reach claim recovers both in
full from the revision request the analysis names (`review_request_sha256`). Lineage is validated before a record is recovered:
the revision request must exist and have the revision role; its `selected_creative_alternative` must carry the same
`inquiry_request_sha256` and `hypothesis_id` that the packet item carries; the full text must begin with the packet's clipped text
(ignoring its ellipsis); and the instruction's full text must match the packet item's `sha256`. Recovery that fails any check is not
admitted and the reconsideration names the failure. The recovered record keeps the author's question, the description (what changes,
how it operates, who faces the choice, what it costs, what the reader must weigh) and the considered mechanisms, so the creative
significance is available to the agent.

**6.2 Evidence admission.** `allowed_evidence` previously included every packet identifier. It now equals the identifiers whose
content this request supplies (the claim's own evidence) plus the recovered records. Packet identifiers outside the claim are listed
as `historically_available`, with no content. A citation to one is refused with the reason "its content is not supplied to this
reconsideration". A citation to an identifier the request never named keeps the existing refusal.

**6.3 Standing.** `_row` called `_standing(..., latest=True)` unconditionally. An analysis that is no longer the latest, while the
same proposal is still live, therefore read as current. A shared helper `analysis_standing(store, request_sha)` in the consequence
owner now derives latestness from `latest_request.json`, the same way its history rows do. The reconsideration reads that helper.
Historical reconsiderations keep their provenance: their standing is `historical`, with the analysis's own standing carried.

**6.4 Handoff.** `reconsideration_handoff(store, reconsideration_request_sha256)` returns a read-only bundle for a `ready`
reconsideration: analysis identity and result bytes sha, claim identity and sha, reconsideration request identity, disposition,
revised judgement, evidence with each record's owner, version and freshness, remaining uncertainty, downstream items, criticism
verdicts, current or historical standing, and refused-attempt count. The bundle is advisory and cannot be used as canon.

## 7. The lifecycle of a synthesis

- **Prepare** (`prepare_architecture_synthesis(store, question, developments, culmination?, handoffs?, criticism?, prior?)`): explicit
  only; reads owners, writes the request (`architecture/synthesis/requests/<sha>/request.json`) and updates the latest pointer; no
  record changes. The request sha is deterministic (no nonce), so an exact replay is possible.
- **Complete** (`complete_architecture_synthesis(store, payload)`): refuses when the request is absent, the role is wrong, or the
  stored response differs. Refused answers are kept under `refused/` with the owner's refusal. A valid answer is stored as
  `response.json` and `result.json`.
- **Project** (`project_architecture_synthesis(store)`): the latest synthesis with its standing, and the earlier syntheses.
  Standing is `current` when it is the latest synthesis of the same developments and the evidence fingerprint recomputed now equals
  the stored one. `superseded` means a later synthesis of the same developments exists; a synthesis of other developments does not
  supersede it. `stale` means the evidence has changed since preparation, or a development is gone. The fingerprint covers the whole
  source each record was read from, not only the excerpt the packet supplies: a change beyond an excerpt still makes the standing
  stale. A stale or superseded synthesis remains readable with its provenance.
- **Follow-up.** A follow-up request names the prior synthesis, may add criticism and handoffs, and carries the prior judgement as
  text only ("earlier judgement, not evidence; cite nothing from it"). Its answer states `changes_from_prior`. The follow-up is the
  continued creative investigation; it is the only route by which criticism changes a judgement.

## 8. Served journey

In the Architecture surface, beneath the consequence panel, a "Synthesis" section. Progressive disclosure, with the same control
vocabulary as consequence and reconsideration:

1. Choose up to three developments from the current questions and mechanisms, and write the question in ordinary language.
2. Optionally name a culmination, and optionally use an accepted reconsideration as a handoff.
3. "Prepare synthesis" shows the request as awaiting a coding agent, with the fingerprint.
4. The completed synthesis reads as a trajectory first (stage cards with book, horizon and basis), then relations, culmination,
   alternatives, opportunities, open decisions and uncertainty. Evidence sits in disclosure with identifiers, freshness and owner.
5. Criticism is entered beneath a synthesis, and "Continue from this" prepares a follow-up. Its result states what changed.

No step applies anything. The page never presents a judgement as a record.

## 9. Verification plan

- Owner tests: the repairs (6.1 to 6.4), each with a regression test; synthesis prepare and complete round trip; deterministic
  request; refusals for unknown developments, unsupplied citations, unsupported `recorded` stages, unknown Book numbers and
  criticism identities; a refused answer kept beside its refusal; the result bytes unchanged; standing current, superseded and stale.
- Served: the section appears; preparation shows the awaiting state; a completed synthesis renders stage cards at 1440 px and
  390 px with no overflow and no page error; unsent text survives a re-render.
- Named boundaries for L2: the consequence and reconsideration owners (their repairs change standing and admission), and the
  served Architecture page.

## 10. Exercises and evaluation

Exercises use the seeded Spring Ledger study (`scripts/consequence_exercise.py seed`), which holds Books 24 and 25 with 182 Working
Book elements, persistent questions, and a candidate Architecture. Each exercise prepares through the owner, and a fresh agent's
unedited answer is completed through the owner. Nothing is applied.

- **A, developmental trajectory:** the Special Draw Right and the lineage crews (`th_maintenance` with `inst_lineage_crews`), across
  Books 24 and 25 and a proposed next Book.
- **B, interdependent developments:** two questions (`q-right-revocable` and `q-compact-settlement`), with at least one interference and one new opportunity.
- **C, earned culmination:** the finale choice (`q-finale-mechanism`), with the author's named culmination, distinguishing
  necessary from enriching preparation.
- **D, reflective synthesis:** a follow-up of Exercise A, with an author criticism and an accepted reconsideration from PR #652 as a handoff.
- **E, integrated journey:** the served page, with the authentic answers pasted for their exact request fingerprints.

An ordinary-inquiry comparison (the existing inquiry owner, same developments) accompanies Exercise A. Independent critics
evaluate creative substance, not contract compliance. The evaluation records originals, failures, criticisms and revisions.

## 11. Limits accepted for this increment

- The author chooses developments explicitly from the current Architecture. Choosing them from natural language is not built here.
- Stages beyond the existing Books are proposals. The Working Book holds two Books in the seeded study; the synthesis does not
  invent Book content.
- One synthesis judgement type; no persistent trajectory graph; no applied or accepted trajectory.
- Human author evaluation is not claimed. Agent answers are a small sample; their quality is evaluated, not generalised.

## 12. Increment 2: claim-basis verification and reflective follow-through (2026-11-27)

Status: decision recorded before the contracts in this section are implemented on `feat/claim-basis-verification` from `main@752817c9` (after PR #653). Advisory, as sections 1 to 11.

### 12.1 The problem it addresses

The v2 quotation contract established textual grounding: a quote is verbatim in the cited item. The v2 critics still found, in about a third of
the Exercise B and C claims, that the quoted words did not carry the interpretation attached to them: present tense read as
achieved, a conditional read as an event, agent-proposed text labelled as record, and a relation that outran its premise. Textual
grounding is therefore necessary and insufficient. The responsibilities are distinguished as follows.

| Responsibility | Governing question | Owner after this increment |
|---|---|---|
| Referential grounding | Does the referenced evidence exist, and was it supplied? | Synthesis and reconsideration admission (sections 4 and 6.2). Unchanged. |
| Textual grounding | Do the quoted words appear in the cited evidence? | `_grounded` in the synthesis owner. Unchanged. |
| Semantic grounding | Does the cited evidence support the interpretation? | **New: claim-basis verification** (this section). |
| Relational grounding | Does the evidence warrant the relation between two claims? | The same verification, for a relation claim. |
| Developmental grounding | Does the evidence warrant a dependency between stages? | The same verification, for a stage or a necessary condition. Dependents are derived by the owner (12.5). |
| Creative judgment | Is the possibility worthwhile? | Not verified. The verifier reports what remains creatively open (`creative_room`) and never ranks creative value. |

These are intellectual distinctions. Only semantic grounding earns a new owner; the others are already served by an existing owner or
are deliberately left to the author and to creative critics.

### 12.2 Approaches considered

- **A. Independent verification after synthesis.** Selected as the core. A fresh agent judges one claim against the exact evidence the
  original agent was given. It is a judgement about a judgement, so it is a new owner, `studio_architecture_verification.py`.
- **B. Evidence interpretation before synthesis.** Investigated, not built. It would store an interpretation of each source before the
  synthesis reads it. That is a new persistence subsystem and it would fix a reading before the author's question is in view. The
  measured failures did not come from missing interpretations: quotes were present and the misreadings were in what the quotes were
  attached to. Revisit only if Exercise A shows the verifier cannot judge meaning from the packet alone.
- **C. Reflective correction after criticism.** Selected as follow-through, with no new correction owner. A verification judgement may
  enter a follow-up synthesis as one criticism, carrying the verification's identity. The follow-up's existing criticism assessment and
  `changes_from_prior` perform the correction, and the prior synthesis is kept.
- **D. Selective or adaptive composition.** Partly adopted. Verification is requested per claim, and the owner names the claims others
  depend on (12.5), by a rule over the record's own references. No importance score, no adaptive engine, no ranking of claims.

### 12.3 Ownership and storage

`studio_architecture_verification.py` (new) owns the claim verification lifecycle: prepare, complete, project. It reads one completed
synthesis by its request identity and its stored result. It writes only under `architecture/synthesis/verifications/`. It never writes
the synthesis request, response, result or pointer, and it never applies anything.

Request, response, result and refused records follow the consequence lineage (`requests/<sha>/`, `refused/`, a latest pointer per
claim). Standing is computed, not stored: `current` when the evidence
fingerprint recomputed now equals the one at preparation; `stale` when the evidence the synthesis read has changed. A claim has one
request for a given synthesis: its identity is its inputs, with no sequence, so a claim is checked once for that synthesis. A changed
synthesis is re-synthesized, and its checks are read as stale. (An earlier draft of this section named a `superseded` standing for
verifications; it was unreachable and is removed.) A verification's standing is therefore `current` or `stale`: `stale` applies
when the evidence the synthesis read has changed.

### 12.4 The verification contract (`ClaimVerification`, schema version 1)

The claim is named by reference: `s1` to `s6` (a stage), `r1` to `r8` (a relation), `a1` to `a3` (an alternative path), `o1` to `o3`
(an opportunity), `n1` to `n4` (a necessary culmination condition), `e1` to `e4` (an enrichment condition).

The verifier receives the complete evidence the original synthesis was given, with the exact stored text of each item, its owner,
freshness and epistemic status or attribution where the record has one. It receives the claim's wording and the basis the synthesis
gave it. It returns:

- `evidence_register`: what the cited evidence actually establishes about the premise: `established`, `inferred_from_established`,
  `agent_proposed`, `author_stated`, `not_established` or `mixed`.
- `judgment`, one of eleven values: `supported`, `defensible_inference`, `creative_speculation`, `overreaching`,
  `temporal_misreading`, `modal_misreading`, `attribution_error`, `standing_confusion`, `unsupported_relation`, `contradicted`,
  `insufficient_evidence`. The set is bounded for this increment; exercises decide whether it needs another value.
- `affects`: `creative_possibility`, `asserted_condition` or `load_bearing_premise`.
- `reasoning` (at most 600 characters), `evidence` (identifiers from the packet), and `quote` (verbatim words from a cited item).
- `alternative_reading` (what the evidence does support, when the judgement is not `supported`) and `would_settle` (what evidence would
  settle an `insufficient_evidence` judgement).
- `creative_room`: what remains creatively possible and which parts must be treated as proposals rather than record. It is always
  required. A verification that narrows possibility without saying so is a defect of the verifier.

The verifier does not receive the synthesis's reasoning, reader experience or other judgements: only the question, the claim's wording,
the claims that use it, the developments, and the evidence the synthesis read. This keeps the verifier from defending the synthesis.

The instruction states every owner-enforced limit, generated from the same constants as the schema. The first authentic run showed why:
one answer (Exercise C, claim s1) was refused because `creative_room` ran to 401 characters against a 400-character bound that the
instruction did not state. The refusal is kept; the instruction was corrected; the same claim was re-prepared under the corrected
instruction and accepted on its first attempt. Every other verification in this increment was prepared under the earlier instruction,
which stated no limits and produced no other length refusal. This is recorded as a difference between requests, not hidden.

Owner checks: the claim exists in the synthesis; every cited identifier was in the packet; a quote comes from a cited item and is
verbatim in it; an
interpretive judgement cites evidence; a misreading, overreach, contradiction, unsupported relation or standing confusion gives an
alternative reading; `insufficient_evidence` names what would settle it; a stage the synthesis labelled `recorded` cannot be judged
`supported` on evidence the verifier itself marks `agent_proposed` or `not_established`. The last rule checks the verifier's
consistency, not its meaning. A refused verification is kept beside its refusal and does not become the verification.

### 12.5 Load-bearing claims, derived from the record's own references

A claim is load-bearing when another claim uses it: it is the `between` reference of a relation of kind `prerequisite`, `enables` or
`complicates`, or of an opportunity. The owner lists those dependents by reference. It reports a count of dependents, not a score, and
it does not rank claims by importance. The served page offers "Check this claim" on every claim and marks the load-bearing ones
"others depend on it". The exercises test whether selective checking of these claims finds more problems per verification than checking
an arbitrary subset.

### 12.6 Owner-derived changes from prior

A follow-up's `changes_from_prior` is the agent's account and is not the sole account. The owner derives a comparison between the
prior and the follow-up answers, at read time, from the stored results:

- Stages are matched one to one by the similarity of their development text. A pair with identical text is unchanged; a pair with
  similar but different text is `reworded`. An item in the same slot of the other answer that keeps at least 30 percent of its words
  is matched as `revised`: the owner reports the slot, and does not decide whether it is the same judgement. Without this rule, a
  corrected stage (Exercise F: two stages) was reported as an unrelated removal and an addition, which overstated the change. An
  unmatched prior stage is `removed` and an unmatched new stage is `added`. Matched pairs
  are compared for placement (book, horizon), basis, the evidence set, `becomes_available` and `changes`.
- Relations are compared after mapping each stage reference to the matched stage, by kind, dependence and the mapped pair. A relation
  whose stage was removed is reported as withdrawn with that stage.
- Alternative paths are matched by ordering text and compared for viability. Opportunities are matched by text. The culmination is
  compared by statement and its conditions. Open decisions and uncertainty are compared as exact strings.

What the comparison cannot establish is stated, not hidden: a `reworded` stage may be the same judgement in different words or a
changed judgement; the owner reports the similarity pair, and the author decides. The agent's list is shown beside the derived list,
with both counts. Immaterial wording changes are listed as `reworded` without an explanation being required of the agent.

### 12.7 Follow-through into a synthesis

A follow-up synthesis may name completed verifications of claims in the prior synthesis (`verifications`). Each becomes one criticism.
The text names the claim by its own wording, states the verifier's judgement and reasoning, and is labelled as a verifier's judgement,
not as evidence. It does not carry the verifier's evidence identifiers: a follow-up numbers its evidence afresh (a culmination absent
from the follow-up shifts every later identifier), so an earlier identifier could point at a different item. A verification is carried
only while the evidence it judged is unchanged; a stale check is refused by the owner and dropped from the page's carried list. The
owner records the verification identity beside the criticism, so the follow-up's criticism assessment can be traced to its source. The
total criticism bound of four still applies.

### 12.8 Limits accepted for this increment

- The verifier is a fresh agent; it is not an independent human judgement, and agreement with critics is not proof of correctness.
- The verification vocabulary is bounded and was chosen before exercises. Its adequacy is tested, not assumed.
- Natural-language development selection is not built. It is deferred. The findings are: the author's developments are selectable from
  the current questions and mechanisms, but a sentence such as "how might the revocable-rights conflict interact with the Mill Compact"
  needs a retrieval step that maps words to developments and reports its ambiguity. That step would be an agent judgement, and a
  reversible author selection would be needed before anything is prepared. It is a separate responsibility and is recorded for later.
- The load-bearing rule is a record-derived rule, not a score. On the three exercised syntheses it did not concentrate problems:
  Exercise B had no load-bearing claim at all, because its relations reference developments rather than stages; in Exercises A and C most
  problems were in relations and alternatives, which the rule does not select (evaluation record, sections 4 and 6).
- No author disagreement is recorded as a structured judgement. An author's disagreement enters as criticism of a follow-up, and that is
  the only route by which it changes a later judgement.
