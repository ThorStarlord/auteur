# Question-linked narrative inheritance and cross-Book reasoning (2026-11-27)

Status: implemented on `feat/question-linked-narrative-inheritance`. This document records the contract as built. The owner
approved the reference extension (mission section 1). The share split, the order of the question-linked class, and the standing
wording are implementation choices made within that approval, recorded here for the owner to confirm. It extends, and does not reopen, the mechanism-grounded consequence responsibility
([2026-11-26-mechanism-grounded-prospective-reasoning.md](2026-11-26-mechanism-grounded-prospective-reasoning.md)).

## A. Starting capability

- A Working Book's decisions (`open_author_decisions`) already bind to a Series open question: index, text digest, stable
  identity (`series_question_id`, when the Series version records one) and the Series version (`series_question_version`).
  Those bindings are validated by `_check_references`, never restamped, and read by `_decision_question_reference`.
- Ordinary Book elements could cite only Series nodes (`series_node`), Book elements and visible source items. Their
  prose could name a question only by position ("open question 6"). Positional names become fragile when questions move,
  and nothing lets the owner follow them.
- The question projection already joins Book references to questions, but only through decisions.

## B. Verified motivating referent (correction to PR #647)

PR #647 treated Book 24's "open question 6" as the Mill Compact question. Verified through the owners on a freshly seeded
Spring Ledger study (`scripts/seed_book_discovery_study.py`):

- Book 24's record is written against Series version `dd0448f7…` (16 open questions, no identities).
- 1-based position 6 (index 5) is: "Is the Book 20 hands-to-draw conversion a lasting settlement, or a stage the finale must
  revisit?" Index 6, the Compact question, is 1-based position 7.
- Book 24's own engine element `eng-ledger-source` says "Whether the conversion is a lasting settlement (open question 6)",
  using the same numeral for the same question. The 0-based reading, which PR #647 used, is not what the Book means.

So the historically recoverable referent is the conversion settlement question. It is not the Compact question. The earlier
critic finding ("the analysis does not connect the blind spot to the Compact") was itself based on that misreading. This
correction is a finding about evidence, not a change to the completed consequence contract.

Because the version has no identities, nothing can bind a typed reference to it. A typed association must name a
question identity that the owner validates against an identity-bearing Series version.

## C. Selected architecture

The extension is additive to the existing Working Book reference machinery:

- `Ref` gains kind `series_question`. Its `id` is the question's stable identity (`q-…`). It is the only field an agent
  supplies.
- The owner records the binding: `series_question_index`, `series_question_sha256` and `series_question_version`, the three
  owner fields mirrored from `DecisionElement`. They are omitted from the stored JSON when unset, so legacy records keep their
  canonical serialization and content digests (see §F).
- No new store, owner or taxonomy. References live in each element's `refs`. Standing reuses `relate_to_current` and the
  decision reference states.

### Reference boundary

A `series_question` reference may appear in `refs` of any element collection except `open_author_decisions`. A decision's
binding is already its question; a second one would be a second owner. It may not appear as a typed-edge target or as an
agent's `name_source`. An edge expresses a dependency, and a question is not a dependency. A name source must be a visible
source.

Candidate consumers (`inherited`, `engines`, `agents`, `choice` parts, `local_resolution`, `series_consequences`,
`later_possibilities`, `assumptions`, `alternatives`, `unresolved`, the function block) are all allowed. The owner does not
require any collection to carry a reference, and it does not prefer coverage.

### Establishment and validation

- An agent names a question by its identity. The identity must be one of the `open_question_ids` of the Series version the
  request was built on. Identities are never inferred from wording or position.
- For a new association (an element gains a `series_question` ref it did not hold), the owner records index and digest from
  that identity's position in that version, and the version is the request's Series version. The question must exist there.
- If a response supplies an index, digest or version for a reference, the owner accepts it only when it equals the value the
  owner would record. Otherwise the response is refused, with the reason: binding fields are owner-recorded.
- A retained association (same element, same identity, held by the Book before the revision) keeps the binding it was
  recorded with. It is never restamped to the latest Series version, even by a whole-Book revision, and it is not
  refused when its question has moved, been reworded or been removed. A changed question is reported, not enforced.

### Authority

A reference records association only. It does not establish that the element answers, settles, develops or inherits from
the question, nor that it is an accepted intention. Element attribution, epistemic status and commitment authority are
unchanged, and they are the only authority the element projects. An element that is a hypothetical alternative keeps
`not_adopted`, so its reference is distinguishable from one on an accepted commitment. Decisions keep `author_reserved`.

## D. Standing vocabulary

Reused, not new. For a reference, the states are `current_wording`, `moved`, `reworded`, `moved_and_reworded` and `removed`
(read as "no longer open"), from `relate_to_current`. Two further states apply to the binding itself: `version_unavailable`
(the recorded version cannot be read) and `binding_mismatch` (the recorded index or digest does not match that version).
Identity is always established for a reference, so `identity_not_established` does not arise for one.

## E. Historical compatibility and bindings

- Serialization: the new `Ref` fields are dropped when unset, so an unbound reference serializes exactly as before. A test
  checks that a stored record round-trips unchanged through the owner's model.
- No migration and no rewrite of stored records. Legacy records are read as before.
- Retained bindings survive later changes: reorders, rewords and removals of the referenced question leave the stored binding
  as recorded, and the standing says what changed.
- A retained association is not restamped by a holistic revision. A new association is bound to the version it was validated
  against. This is the same principle as `_stamp_decision_versions`, applied more strictly: nothing is restamped silently.
- Fingerprint, freshness and impact behaviour are unchanged. A question change does not make a Book stale. It is reported.
- Inherited-claim provenance ignores question references. A claim whose only reference is a question has no basis, and
  `_inherited_provenance` says so.
- Packet versions: the consequence packet becomes version 3 (see §H). Version 2 analyses stay readable and are not
  reinterpreted.

## F. Positional prose observations (read-only)

An element whose prose names "open question N" (1-based, as Book 24 does) is reported as a qualified observation. The
owner resolves position N in the Series version the Book record was written against:

- the referent text at index N-1 in that version;
- the identity recorded at that version for that position, or none when the version has no identities;
- an explicit state: `resolved_at_recorded_version`, `historical_version_unavailable` or `position_out_of_range`.

It is not a binding and never writes. An author or agent attaches the reference through a reviewed revision by naming
the current identity. The owner does not infer that identity from the referent's wording or from the position. The
observation shows the reading and the numbering convention it assumes, so the author can judge.

## G. Authoring, review and Apply

- The Working Book prompts (`_BOOK_SYSTEM`, `_BOOK_REVISION_SYSTEM`) state the kind, the identities allowed (the develop and
  revision packets list each question's `id`), the placement rule, the authority rule, and that the owner records the
  binding. The develop packet gains each question's `id`, so the develop path can offer the same identities as a revision.
- `_build_review` adds a `question_associations` section: added, removed and retained associations, each with its element,
  the question's recorded and current standing, and the authority the element projects. Consequential changes are shown
  before Apply.
- Apply is unchanged. The reviewed candidate, including its references, is what it stores. `applied_review` records the
  association changes. `book_resume` does not show them separately; they appear in the Book's artifact and its element rows.

## H. Projection and evidence selection

- `book_series_references` returns `element_question_references`: one row per (element, identity) with the element's
  collection, text, commitment authority, the question's standing and its recorded formulation. `question_references`
  keeps its meaning (decisions only).
- `project_architecture_questions` keeps each question's `books` list decision-only, because the deliberation, discovery and
  consequence consumers read it as decisions. Element associations are listed separately, in each question's `engagements` list,
  with the Book's own collection name for the element. A question-centred reading shows both, not a new taxonomy.
- Consequence evidence: `book_element_candidates` gains a `question_linked` class for elements that reference a question the
  proposal examines. Shares within the unchanged cap of 24: inherited 8, forward 6, other 4, question-linked 6. The class is
  listed last, so a share left unused goes to inherited and forward evidence first and a question association never takes
  slots they leave. Packet version 3 records the change. Question-linked rows carry the question identities they reference and
  the examined ones, and are not presented as causal inheritance.
- Deliberation and discovery are not changed in this increment. The consequence analysis is the vertical that exercises the
  new evidence; the others already receive Book evidence through `book_element_evidence`, which now also reports question
  references. Extending them is a follow-up with its own evidence.

## I. Served Atelier

- The question reading lists each Book engagement under its element's collection name, with its recorded formulation,
  current standing, authority and the limits of what the association establishes.
- The Book element view shows its question references and their standing, and links to the question.
- The review of a revision shows question association changes before Apply.
- The consequence panel marks question-linked Book evidence and says that it records an association only.

## J. Limits

- One Series version, one Book record, and the positional numbering convention (1-based in prose) are the only sources of
  historical referents. Other numbering is not interpreted.
- A retained binding cannot be re-bound. To re-attach a question, remove the reference in one revision and add it in a later
  one; the new association then binds to the version it is validated against.
- The owner checks that an identity exists in the authorized version and that the binding matches it. It does not check that
  the element is about the question, and it does not check the reading of a cited item. Semantic reasoning limits remain
  where the exercises record them.
- No backfill. Prose mentions are not converted to references. Each association is a reviewed, explicit revision.
