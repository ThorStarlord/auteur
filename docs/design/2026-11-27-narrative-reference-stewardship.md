# Narrative reference stewardship and integrated cross-Book deliberation (2026-11-27)

Status: implemented on `feat/narrative-reference-stewardship`. This records the contract as built. It extends
[question-linked narrative inheritance](2026-11-27-question-linked-narrative-inheritance.md), whose reference extension the owner
approved. The owner's implementation defaults are kept as stated: reserved evidence shares 8 / 6 / 4 / 6 (within the cap of 24),
the existing standing vocabulary, and the one-based reading of positional prose. None of them is an architectural invariant.
Evidence: [EVALUATION.md](../qualification-evidence/narrative-reference-stewardship-20261127/EVALUATION.md).

## A. Starting capability

PR #648 let a Working Book element reference a persistent Series question by identity, and let Narrative Question
Workspace read those associations as engagement. What it did not do:

- A positional name in Book prose ("open question 6") was read only from the Book-wide version it was recorded against. A
  Book revision that rewrote the prose later could make that version the wrong reader.
- An author could see a positional name only in a Book's development panel, which the question reading did not reach.
- Deliberation and discovery read a Book's question evidence as decisions only. Element associations never reached them.
- Deliberation packets gave no element-level structure: no engagements, no element co-reference, no typed dependencies.

## B. Selected architecture

Every change extends an existing owner. No store, relationship table, graph or retrieval mechanism was added.

| Concern | Owner | What changed |
|---|---|---|
| Where prose was written | `auteur.series.working_book_architecture` | Applied versions are read from the lineage; the version a prose field first read in is its origin |
| Positional observations | same | Read at the origin version; the Book-wide version is still reported; each observation carries an adoption view |
| Requesting an association | same, through `book_prepare` | Optional `associations`; the owner checks each one, adds its element to scope, and states the request in the packet |
| Whether a response recorded it | same, in `_complete_revision` | `requested_question_associations` in the review, with the question's wording and an `established` flag |
| Deliberation evidence | `studio_architecture_deliberation` | Per-question `engagements` (spread across Books), recorded element co-references, positional names tied by identity |
| Discovery evidence | `studio_architecture_discovery` | `book_element` evidence, accepted only for a question the element engages in that request |
| Question reading leads | `studio_architecture_question_projection` | Per-question `positional_leads`, labelled by how they match |
| Atelier | `studio_atelier.js` and the creative panel | Observation cards with the owner's choices, a review line for requested associations, and labelled evidence lines |

The `books` field of each question stays decision-only. Element associations are in `engagements`, which deliberation and
discovery read explicitly.

## C. Reference recovery

**Where the prose was written.** `_applied_chain` lists each applied version of a Book, oldest first. The current version reads
its series from its own request, because a partial revision of an out-of-date Book keeps the Book-wide baseline on the record.
If that request cannot be read, the record's Book-wide version stands in, and the origin is marked not established.
`_prose_origin` walks back from the current version and compares each prose field exactly. The origin is the oldest version
whose text equals the current text, and the walk stops at the first version that read differently (`written_in_this_version`)
or cannot be read (`earlier_version_unreadable`, which is not claimed to be complete). Similar wording is never matched.

**Reading.** A positional name is read at its origin's series version when that is known, and at the Book-wide version otherwise
(`read_basis`). The referent, the identity recorded there, and the other numbering are reported. Nothing is written.

**Adoption states** (`book_observation_stewardship`, one per observation, from the owner's records):

| State | Meaning | Author can |
|---|---|---|
| `recordable` | The version named an identity for that position and it is still open | Confirm it, or choose another current question |
| `identity_not_recorded_at_read_version` | The version recorded no identity for that position | Choose the current question; the owner records the choice and the historical wording remains a reading |
| `question_no_longer_open` | The identity recorded then is no longer open | Choose a current question, knowing the old reference is not carried across |
| `already_recorded` | The element already records that association | Nothing (shown) |
| `origin_not_established` | An earlier version the record cannot read may have written this prose | Choose the current question; the recorded identity is not offered |
| `no_current_identities` | The working Architecture has no identities yet | Give identities first, through an Architecture revision |
| `not_recordable` | A typed-edge function, a decision, or a missing element | Nothing; the reason is stated |

A positional name in a typed edge's function is never offered an association: edges cannot carry question references, and the
owner does not attach one to another element on its behalf.

**Requesting an association.** `book_prepare(..., associations=[{element_id, question_id}])` requires a current identity, refuses a
decision, an unknown element, a repeated or already-recorded association, and more than six requests. The element joins the
revision's scope. The owner's instruction states that the element's own prose must engage the question, that the response should
add the reference only if it does, and that a changed element uses the explicit form. The packet carries the requested
associations with the question's current wording and the historical positional readings of that element, so the agent can compare
them. Requests without associations produce the same request identity as before.

**Reviewing.** `requested_question_associations` in the review says, for each request, whether the response recorded it, and gives
the question's wording. `unrequested_question_associations` names any association the response added that was not asked for, and
the Atelier names those before Apply. "Not recorded" is reported and does not block the rest of the revision. Apply stays the author's explicit
choice; the review lists exactly what Apply will change.

**Lead from the question.** A question's `positional_leads` lists Book prose that names it by position. A name whose origin is
not established is not a lead, and is counted as untied in deliberation. A lead matched by identity
is one whose version recorded that identity at that position. A lead matched by wording is one whose version recorded no
identity and whose named wording equals the question's current wording exactly; it is labelled as a lead, not an identity. An
element that already records the association is an engagement, not a lead.

## D. Cross-Book reasoning

Deliberation (the inquiry's "compare" or "connect" with two or three continuing questions) receives, per question:

- `engagements`: the Book elements that record an association with the question, with the element's own attribution, epistemic
  status and commitment authority, its standing (current wording, moved and so on), its recorded position, its element text, and
  up to two typed dependencies the Book records for it. Up to four are shown, spread one Book at a time so that no Book takes the
  whole allowance. Omitted counts are reported.
- `co_references`: a recorded decision co-reference (as before), and a recorded element co-reference for one element that records
  associations with two selected questions. The second is labelled as a fact about one element's record, not a relation between
  the questions.
- `positional_observations`: positional names tied to a selected question by identity at the version they were written against.
  A name whose version recorded no identity is not tied to any question; the packet counts such names as a named gap.

Each element's standing is re-read at completion: `current`, `book_revised`, `element_changed` or `association_gone`. The inquiry
guidance says that an association is engagement, not significance; that a shared association does not relate two questions; that
several Books engaging one question may repeat it, develop different dimensions of it, complement or contradict one another, or be
better understood apart; and that a positional observation may be cited only as an uncertainty about its Book. The answer may
conclude that the questions should stay independent.

## E. Opportunity discovery

The discovery packet gives each continuing question up to two `book_element_associations` (spread across Books) with the element's
text and its own status. A possibility may cite one as `ref_kind: book_element`, which requires `book_number`. The owner accepts
the citation only if the element engages one of that possibility's questions in the request. The prompt says an association is
evidence of engagement, not of significance, and that a possibility resting only on associations or shared references is
speculative. An answer with no possibility remains legitimate. Discovery's grounded label still requires a recorded mechanism.

Discovery does not add a new engine: the same request, answer, transferability and deliberation pathway applies.

## F. Semantic criticism

See the evaluation (Exercise D). No production critic was added in this increment: the mission asked whether focused criticism
improves decisions, and the exercise is the place to find out. A standing critic pass would be a new mandatory step, which this
mission rules out.

## G. Authentic exercises

Summarised in the evaluation: Exercise A (Book 25 association through the owner and a fresh agent), Exercise B (cross-Book
deliberation), Exercise C (opportunity discovery), Exercise D (focused critique of a consequential reading). Each stage writes its
unedited agent output and the owner's result; nothing is edited after it is written.

## H. Served journey

`tests/test_beginner_studio_reference_stewardship_browser.py` drives the Atelier through the real controls: the question reading and
its lead, Book 25's development panel and observation choice, the prepare control, the owner's review (which the test completes with
the committed unedited answer), the served Apply control, and the question reading afterwards. It also covers the no-change path
(a lead is left alone and nothing on disk changes) and a 390 px width without horizontal overflow.

## I. Integrity

- **Versions.** Stored records and PR #648's evidence are unchanged. Observations are recomputed, never stored, so their read
  version can move without rewriting anything. Where the origin equals the Book-wide version, the reading is the same as before.
- **Renamed read fields.** `resolved_at_recorded_version` is now `resolved`, and `identity_at_recorded_version` is now
  `identity_at_read_version`. Only live reads used them, and the PR #648 reproduce script that prints them is historical.
- **Deliberation and discovery packets** gain keys and two RefKinds. Their schema labels are unchanged, because consumers read
  keys by name and the additions do not reinterpret an existing key. Stored answers keep the packet they were asked with.
- **Authority.** Nothing is applied, accepted, settled or inferred. A lead or an observation never writes. An engagement says the
  element engages a question and nothing about its story role. The owner records an identity only from the author's choice or from
  a version's own record.
- **Compatibility.** See the correction in
  [question-linked narrative inheritance, section K](2026-11-27-question-linked-narrative-inheritance.md#k-compatibility-and-rollback-correction-2026-11-27).
  This increment adds no new record kind. It adds a request setting and a review key, both of which the pre-#648 code treats as
  opaque, so the compatibility boundary is still the first applied `series_question` reference.

## J. Limits

- The owner checks identity, binding, placement, scope and authority. It does not check that an element is about a question.
  Semantic checks remain the reasoning agent's and the author's.
- Wording matches for leads are exact string equality, and only where the version recorded no identity. They are labelled, not
  promoted.
- Typed-edge observations and decision text are not adoptable, by design.
- An out-of-date Book takes a whole-Book request from the Atelier, because the adapter prepares against the current working
  Architecture only. The card says so, and the review shows each change.
- Deliberation and discovery see at most four and two element associations per question. Omitted counts are reported.
- The evidence is one specimen, one author model run per arm, with identities assigned by the study's helper. It shows the
  mechanism works and where the reasoning is fallible; it does not establish general reasoning quality.
