# Review: question-linked narrative inheritance

Scope: current design file, change.diff, the owner module, the consequence, projection and mechanisms modules, the Atelier JS, the new tests and the reproduce scripts. No repository file was changed.

**No blocking defect found.** Guarantees 1 to 9 hold on the paths I read. Guarantee 10 is implemented, but its test does not prove it. Four important items and several minor ones follow.

## Findings

### 1. Important: element associations with unreadable or mismatched bindings lose their question
- `src/auteur/series/working_book_architecture.py:935` and `:938`: `_question_standing` returns `version_unavailable` and `binding_mismatch` without `question_id`, although the element's identity is `ref.id`.
- `src/auteur/beginner/studio_architecture_question_projection.py:255-256`: element rows without `question_id` go to `unattributed_references`.
- `src/auteur/beginner/browser/studio_atelier.js:1852-1853`: that bucket is described to the author as "decisions ... none can be attached to a question here".
- Scenario: Book 24's association to the conversion question is recorded at a version whose record can no longer be read. The question's engagement list drops it, and the folio counts it as an unattributed decision.
- Design §D (line 82) and §H (line 125) require the identity on each reference row. No test covers an element association with a missing or mismatched binding.

### 2. Important: review rows omit standing and element authority
- `working_book_architecture.py:1788-1793` (`_question_associations.row`) carries only element id, collection, question id, recorded index, version and question text.
- Design §G (lines 116-117) requires the recorded and current standing, and the authority the element projects.
- `studio_atelier_book.js:101-106` renders only the verb, the element label and the question text.
- Evidence: `reproduce/exercise-a/review-book24.json`, `question_associations.added`, has the same six keys.
- Scenario: a revision adds an association to a question that has since been removed, or to a hypothetical alternative. The review says "now engages" with no standing and no authority line before Apply.

### 3. Important: the test for guarantee 10 is weaker than its name
- `tests/test_architecture_consequence_mechanisms.py:129-140` asserts `len(linked) >= 6` with 12 inherited and 10 question-linked candidates. Only 22 candidates exist, so the leftover pass fills the cap with or without a reserved share.
- I ran `book_element_candidates` with the question-linked share set to 0. The result is identical: 10 linked rows.
- With 30 inherited and 10 linked, a share of 6 gives 6 linked rows and a share of 0 gives 0. No test covers that competitive case.

### 4. Important: the share split changed after the reviewed snapshot
- The snapshot in change.diff (written 01:11:48) says inherited 8, forward 8, other 2, question-linked 6. The design file on disk (modified 01:12:50) now says 8, 6, 4, 6.
- Code (`studio_architecture_mechanisms.py:53-57`) and the test (`test_architecture_consequence_mechanisms.py:120`) were already 8, 6, 4, 6 in the diff.
- The design header says it records decisions the owner approved. The repository does not show whether 8, 6, 4, 6 was approved. The owner should confirm. The same edit made §H's books list decision-only, which matches guarantee 9.

### 5. Minor: test gaps against design claims
- Design §E (line 87) says a test pins a legacy record's content digest. None does. `tests/test_working_book_question_references.py:103-108` compares new output with the same code's output. Its `Ref` shape assertion is meaningful.
- Guarantee 7 (`working_book_architecture.py:469-475`) has no test.
- Guarantee 2 for a retained association with a changed binding (`_stamp_question_references`, lines 621-654) has no test.

### 6. Minor: duplicate question references on one element are not rejected
- `_check_references` (lines 495-530) has no uniqueness check on refs. `book_series_references` emits one row per ref (lines 1218-1235), so the folio would show two engagement cards for one element. Inferred from the code; not run.

### 7. Minor: the design's Book-view link is missing
- Design §I (line 144) says the Book view "links to the question". `renderBookQuestionLinks` (`studio_atelier.js:2653`) has no link or action.

### 8. Minor: positional observations skip typed-edge prose
- `_labelled_elements` (lines 295-328) excludes typed edges, and `_PROSE_FIELDS` (line 1260) has no edge field. An edge `function` such as "open question 6" is not observed. Inferred; not run.

## Checked and correct
- `Ref._omit_unset_binding` (lines 84-90) drops unset binding keys. A `series_node` ref dumps as `{kind, id}`.
- Legacy digests: the recorded `content_sha256` equals `_digest` of the raw stored JSON (checked on `working-book-revision-20261112/clean-run/22-resume-final.json`). A fresh dump differs only by defaults already on origin/main (`responsibility`, null `attribution`). This change does not cause it.
- Refusal messages match their checks: `_question_association_problems`, `_stamp_question_references`, and the typed-edge and name-source checks at `_check_references` 521-526.
- Decision refusal (`_check_semantics` 403-406) runs on every write path: `book_complete` 881, `_complete_revision` 2146, `book_withdraw` 2233.
- A retained binding survives a reorder and a holistic revision. The version is unchanged and the state reads `moved` (test at line 183).
- Inherited provenance ignores question refs (line 469).
- The books list is decision-only. Deliberation and discovery read `books` as decisions (`studio_architecture_deliberation.py:206, 224, 281-295`; `studio_architecture_discovery.py:200`).
- Positional observations are read-only.
- Packet version 3 gates no reader. Stored packets are not rebuilt, because `complete_architecture_consequence` checks against the submitted packet.
- The unedited Book 24 answer and the recorded Book 24 record parse with the owner model and round-trip unchanged. The answer carries no owner-set binding fields.
- I ran `tests/test_working_book_question_references.py` and `tests/test_architecture_consequence_mechanisms.py` with the project venv, `PYTHONPATH=src` and no cache writes: 38 passed. The browser and `.mjs` tests were not run.
