# Review: commit bcac8345 (narrative reference stewardship)

Read-only review. Nothing was run. All findings below were checked against the code. Result: **no blocking findings**, 2 important, several minor.

## Answers to the five questions

1. **Write without a reviewed Apply?** No. The write paths are:
   - `book_prepare` / `_prepare_revision` (working_book_architecture.py ~2305-2375) writes only `request.json` and `latest_request.json`.
   - `_complete_revision` writes only a review.
   - `book_apply_review` is the only writer of `current.json`.
   - Observations, leads and adoption views are recomputed and never stored.
   - The requested element is added to `target_set`, so it is in `allowed_ids`. A requested association therefore cannot sit outside scope. The reverse also holds: `_requested_associations` rejects unknown elements, decisions, duplicates, already-held associations and non-current identities.
   - Caveat (minor, see M5): dependents of a requested element are also in scope. The agent could add an unrequested association there. The review's existing `question_associations.added` lists it, so the author sees it, but the "requested" block does not flag it.
2. **Origin computation.** Correct for the normal case. Two gaps, F1 and M2 below. The legacy no-lineage case is fine: `book_apply_review` seeds a develop lineage entry on first revise, so a revised Book always has a chain.
3. **Half-written state?** No. Every `ValueError` in `_requested_associations` and the length checks is raised before `write_host_agent_request`. The freshness check (`BeginnerConcurrencyError`) also precedes the write.
4. **Association presented as a decision, or a positional name as a tied reference?** No. Packet items carry `basis` / `authority` labels (`book_element_association`, `owner_observation_not_reference`). `books` stays decision-only. One nuance is F1.
5. **JS stale closure over n or o?** No. `n`, `o` and `data` are bound per `forEach` / call. `sel.value` is read at click time. Duplicate-key and selection-reset problems are M1 and M3.

## Findings

### F1. Important, confidence medium: an incomplete origin is still used as the read version
- `working_book_architecture.py:1385` (`read_sha = origin["series_request_sha256"] if origin else book_version`), with `_prose_origin` (1336).
- When the walk stops at an unreadable earlier version, the origin is flagged `complete: False`. The reading still resolves at that later version's Series list, with `read_basis: "element_origin"`.
- Downstream, two consumers ignore `complete` and tie the name to a question by the identity recorded at that version:
  - `question_projection.py:281` (`matched_by: "recorded_identity"`)
  - `deliberation._positional_uncertainties` (deliberation.py:248)
- Scenario: Book v0 (unreadable, Series S0 where "open question 6" meant X) is followed by an unchanged-text v1 (S1 where position 6 is Y, identity Y). The prose is read at S1 and surfaces as an identity lead for Y.
- The Atelier card does say "an earlier writer may exist", but the lead and the deliberation packet do not.
- Suggested fix: when `origin.complete` is false, skip the identity tie in leads and deliberation, or count it as a named gap, the way identity-less names are counted.

### F2. Important, confidence medium: `deliberation_standing` rows have a new shape
- `deliberation.py` (the added `kind` / `element_id` rows, lines ~385-460).
- `deliberation_standing` now also returns `book_element_association` rows. They have no `decision_id` and carry standing values (`element_changed`, `association_gone`) outside the old set.
- One in-tree consumer is safe: `consequence.py:497` passes a packet with no `engagements`.
- `tests/test_architecture_deliberation.py:192` and `:219` index `row["decision_id"]` / assert a closed standing set over the full result. They pass only because the Spring Ledger fixture has no element associations. Whether it has none was not confirmed. If it has, those two tests fail with `KeyError`. They were not updated in this commit.
- Any future consumer breaks the same way.

### Minor
- **M1. Duplicate ids and keys (high).** `studio_atelier.js:2718` sets `sel.id='atl-observation-question-'+n+'-'+element_id`. Lines 2725 and 1874 build `observation-prepare:` and `question-lead:` keys from `n` and `element_id`. Observations and leads are per match, so one element with two phrases, or the same phrase in two fields, gets duplicate DOM ids and duplicate `data-key`s. The second label's `htmlFor` focuses the first select, and `focusKey` lands on the first card. Include the field and match index in the id and key.
- **M2. Fallback series for the current version (medium).** `_applied_chain` (1328-1330) falls back to the record's Book-wide `series_request_sha256` if the current request cannot be read. After a partial revision of a stale Book that value is the older baseline, but it is reported as `element_origin`. The unreadable current request should be marked like any other unreadable version.
- **M3. Select resets on re-render (medium).** `studio_atelier.js:2721`. `renderStewardship` rebuilds the select from `proposed_question_id` on every `renderFolio()`. Any background re-render (for example `readSeries`) between choosing and clicking Prepare silently reverts the choice, and the click uses the reverted value. The selection is not held in `S`.
- **M4. Choices still offer the held question (high).** After an association is applied to an identity-less observation, the state stays `identity_not_recorded_at_read_version` with `recordable: true`. The held question is still in `choices` (test line 176 asserts this state). Choosing it gives an owner refusal ("already records"). This is safe but confusing. Filter held ids out of `choices`.
- **M5. Dependents may gain unrequested associations (medium).** `_prepare_revision` adds dependents to `allowed_ids` and the instruction forbids other associations. Only the instruction enforces this. The "requested" block reports on requested pairs only, so an extra association appears only in the generic `added` list.
- **M6. Out-of-date Book becomes a whole-Book revision (low).** `prepareAssociation` sends `holistic: true` when `freshness !== 'ready'`, and the code comment says an out-of-date Book "takes only a whole-Book revision". The owner has an explicit partial-on-stale path (`partial_on_stale`, ~2597), so the comment appears wrong. A holistic revision rebases the whole Book, which can change what other positional names mean. The button text does not say the request covers the whole Book. Apply is still reviewed, so this is a disclosure issue.
- **M7. Wording lead can match by coincidence (low).** `question_projection.py` ties an identity-less observation to a current question by exact text equality. If two current questions share wording, both get a lead. This is labelled `unidentified_wording_match` and is a lead only.

## Tests
- `test_working_book_reference_stewardship.py:98`: `read_basis in ("element_origin", "book_recorded_version")` accepts both outcomes. The test name says "reads at its origin", so the assertion does not check it. Assert `element_origin`.
- `:209` (`unchanged by the stewardship view`) compares the view against the plain read minus `adoption`. It is meaningful.
- The review tests at 104-145 check the `established` flag on both the recorded and the not-recorded path. Good.
- No test covers `complete: False` (F1) or a partial revision of a stale Book followed by an origin read. This is the most consequential untested path.
- I did not read the browser or mjs tests in depth. I did not confirm that the browser test's "unedited committed answer" cannot pass vacuously.

## Document versus code
- The document matches the code on: the adoption table, the limits (8 / 6 / 4 / 6 split and per-question 4 and 2), `requested_question_associations`, the unchanged request identity without associations, and the renamed fields.
- Mismatches:
  - The document says an unreadable earlier version is "not claimed to be complete". That is true of the origin record. It is not true of the leads and deliberation consumers (F1).
  - Section C says the current version "falls back to the record only when the request cannot be read". The fallback is silent (M2).
  - The document says that after recording, an observation's state is `already_recorded`. That holds only when the read-version identity is known. Identity-less observations stay recordable (M4).

## Overall
Apply is not bypassed and the refusals are clean. The risks are an incomplete origin presented as a tied lead (F1) and the new standing row shape (F2).
