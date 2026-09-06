# Bounded Episode 1 Direction Qualification (I1 Current-Main Integration)

Status: qualification evidence complete. This status is narrow: the
implementation, test, and independent-reviewer evidence required by this
qualification record is complete for the exact I1 current-main integration
candidate identified below. This record does not assert, and must not be read
as asserting, that a final post-documentation Validator has run, that a human
has approved the candidate, or that the candidate has been committed, pushed,
opened as a pull request, merged, released, or shipped. Those remain separate,
later gates.

This record qualifies the bounded Episode 1 Direction capability defined in
the
[Bounded Episode 1 Direction Capability Contract](../acceptance/series-episode-one-direction-capability-contract-v1.md)
and the
[Bounded Episode 1 Direction Implementation Boundary](../design/series-episode-one-direction-implementation-boundary-v1.md),
as integrated onto contemporary `main`. It is a distinct qualification record
from, and does not reuse or imply, the evidence in the historical
[Series Vertical Slice V1 Qualification](series-vertical-slice-qualification-v1.md).
That capability contract explicitly reverses, for Episode 1 Direction only,
the "episode support or Book/Episode unification" deferral recorded there; this
document is the qualification evidence for that narrow reversal, produced
separately rather than by amending the historical record.

## Candidate identity

```text
capability:     Bounded Episode 1 Direction (Series-scope, Identity-layer entry-unit)
I1 baseline SHA: 588fb1ef88184be9246d406fd1c90737b7c09cf6
repository:     H:/GithubRepositories/auteur-episode-one-direction-integration
branch:         feature/series-episode-one-direction
worktree root:  H:/GithubRepositories/auteur-episode-one-direction-integration
```

The pre-documentation candidate consisted of exactly 19 staged paths against
the I1 baseline: 6 production files, 9 test/fixture files, and 4
documentation files. This qualification record and the accompanying forward
reference in the Series Vertical Slice qualification record are the two
documentation-only additions that complete the candidate at 21 total staged
paths. Adding this record and the forward reference does not modify any of
the original 19 paths.

## Compatibility and integration provenance

This candidate was constructed by transplanting the previously frozen,
independently reviewed Bounded Episode 1 Direction implementation onto a
fresh baseline drawn from contemporary `main` at I1
(`588fb1ef88184be9246d406fd1c90737b7c09cf6`), rather than by re-implementing
the capability. Construction used a no-commit cherry-pick of the normative
documentation paths and the CHECKPOINT-3-validated feature paths, followed by
a full semantic integration audit. One purely textual (non-semantic) merge
conflict occurred, in `src/auteur/series/vertical_slice_formatters.py`, where
two independently added function blocks both ended in the identical line
`return "\n".join(lines)`. It was resolved by reconstructing each function's
own `return` statement and concatenating both blocks, with no logic change.
The frozen historical qualification record for the prior (pre-current-main)
compatibility candidate is deliberately excluded from this record's evidence;
it qualified a different candidate on a different baseline and is not
re-asserted here.

## AC1-AC19 status

All 19 capability-level acceptance criteria in
`tests/test_series_episode_one_direction.py` pass against this exact
candidate. Each criterion was independently traced by the pre-documentation
Validator (see below) to concrete service and store logic, including
propose/accept non-authoritativeness, structural commitment-reference
validation, all-or-nothing acceptance, idempotent re-declaration and
re-acceptance, two-way Book/Episode exclusivity via active checks, distinct
inspection labelling, and unchanged Book-oriented coexistence. AC19 verifies
only durable normative-content markers in the three documentation paths; it
does not inspect either qualification-record document or any transient
"Status:" wording, and is therefore unaffected by this documentation phase.

Result: **PASS** (19/19).

## Compile evidence

`python -m compileall -q src` against the full candidate.

Result: **PASS**.

## Touched-unit evidence

The focused unit group covering the six modified/added production files and
their direct test counterparts.

Result: **183 passed, 0 failed**.

## Acceptance evidence

`tests/test_series_episode_one_direction.py`, the capability-level AC1-AC19
suite, run in isolation.

Result: **34 passed, 0 failed**.

## Contemporary-main coexistence evidence

A regression group exercising Global Map, repeated continuity, realization,
and Next-Decision machinery already present on contemporary `main`, to
confirm this candidate's additive changes do not disturb pre-existing
current-main behavior.

Result: **109 passed, 0 failed**.

## Full normal repository suite

`python -m pytest -q --tb=short` against the complete candidate, using the
project's normal `testpaths = ["tests"]` collection scope.

Result: **4,772 passed, 1 skipped, 27 xfailed, 0 failed**.

These four evidence groups (touched-unit, acceptance, coexistence, full
suite) are reported as distinct counts; none is a subset total added into
another, and none was summed to produce an aggregate figure.

## Lint and format evidence

`ruff check` against the six candidate production files: **PASS**.

`ruff format --check` against the same six files: the one newly added file,
`src/auteur/series/episode_direction.py`, is compliant. The five modified
pre-existing files remain non-compliant. This non-compliance was confirmed to
be pre-existing baseline debt, not something introduced by this candidate: a
read-only comparison of each file's I1-baseline blob
(`git show 588fb1ef88184be9246d406fd1c90737b7c09cf6:<path> | ruff format
--check --stdin-filename=<name> -`) against the candidate's working content
showed the same non-compliance already present at baseline, for the same five
files, before this candidate's changes were applied.

## Security review (independent, I1 candidate)

Critical: **0**. Important: **0**. Minor: **1**.

`src/auteur/series/vertical_slice_models.py` — the Episode identifier-like
fields (`candidate_id`, `proposal_id`, and `bundle_id`-derived identifiers
such as `AcceptedRealizationBundle.artifact_id`/`bundle_id`) are typed as
unconstrained `str` at the Pydantic model layer. This is a newly surfaced
observation on this I1 candidate; the earlier frozen (pre-current-main)
Security review of this capability did not raise it. Path safety for every
current call site is correctly enforced downstream, in
`vertical_slice_store.py`'s validated path-builders (`_PATH_SAFE_IDENTIFIER`
regex and `Path(x).name != x` checks), so there is no demonstrated exploit
path today. It is recorded as a new low-severity defense-in-depth
observation: adding a model-level regex/validator on these fields would guard
against a future call site that builds a path directly from one of them
without going through the existing store methods. This Minor is **not fixed
in this candidate** and **has not been promoted** to Important or Critical.

## Performance review (independent, I1 candidate)

Critical: **0**. Important: **0**. Minor: **1**.

`src/auteur/series/vertical_slice_models.py:120-133` —
`EpisodeDirection._validate_episode_direction` detects duplicate
Series-commitment references using `.count()` inside a set comprehension,
which is O(n^2) in the number of referenced commitments. This is an
independent I1 rediscovery of the same observation raised against the
earlier frozen candidate; the input is a small, human-authored reference
list, and the reviewer classified it Minor and non-blocking. This Minor is
**not fixed in this candidate** and **has not been promoted** to Important or
Critical.

## Pre-documentation Validator (independent, I1 candidate)

Critical: **0**. Important: **0**. Minor: **0**.

The Validator traced all 19 acceptance criteria to concrete code, confirmed
out-of-scope boundaries (no Episode beyond Episode 1, no realization or
canonical-state work, no generalized entry-unit abstraction, no changes to
the five-scope/five-layer model beyond one additive clarifying sentence),
and confirmed full coexistence with pre-existing contemporary-main Series
machinery.

The Validator disclosed one methodological limitation: its available tools
in that review session were read-only (Read/Grep/Glob) with no shell or Git
access, so it could not itself mechanically run
`git diff --cached --name-only` to confirm the exact candidate path
boundary. It instead verified the boundary by reading all candidate files in
full and checking for scope leakage, which it noted as a reasonable
substitute but not identical to a diff, and recommended a mechanical
confirmation before merge.

## Coordinator closure of the Validator's limitation

The reviewing coordinator subsequently closed this limitation directly, with
Git access, after the Validator's review completed: `git diff --cached
--name-only` was run against the candidate and confirmed the exact 19-path
staged boundary with no scope leakage, `git status --porcelain=v1
--untracked-files=all` confirmed zero unstaged drift and no unexpected
untracked files, and `git diff --cached --check` was confirmed clean. This
closure is recorded as the coordinator's own action, separate from and in
addition to the Validator's own report; it is not presented as something the
Validator itself performed.

## Unresolved findings summary

Two Minor findings remain open against this candidate: the Security
defense-in-depth observation on unconstrained identifier strings, and the
Performance O(n^2) duplicate-commitment check. Neither has been fixed in
this candidate. Neither has been promoted to Important or Critical. Both are
judged non-blocking for qualification-evidence completeness by the
respective independent reviewers.

## Scope and non-claims

This record does not assert:

- that a final post-documentation Validator has reviewed the complete
  21-path candidate (this record and the Series qualification forward
  reference included);
- human review or approval of the candidate;
- that the candidate has been committed, pushed, opened as a pull request,
  merged, released, or shipped;
- that either open Minor finding has been resolved;
- that any capability beyond the exact 19-path implementation/test/normative
  candidate described here has been qualified.

## PR #167 review remediation and requalification

Everything above this section records the qualification of the pre-commit
21-path candidate, which was then committed unchanged as
`1d9b09626e9c4a6fb0e9d4fa7827684f2a7f7b11` and published as pull request
[#167](https://github.com/ThorStarlord/auteur/pull/167). That evidence stands
as written; this section adds — it does not replace — the record of a bounded
review-remediation pass performed afterwards in response to the PR review.

### Provenance

An automated PR review (GitHub Copilot) on #167 raised six threads. Two were
accepted as low-severity, deliberately-unfixed findings (see "the two
deliberately unresolved accepted Minors" below). The other four were accepted
as correct and remediated. Commit `1d9b096` was treated as immutable; the
remediation was applied as working-tree changes on top of it, to be captured
in a single follow-up commit after this record and a final Validator pass.

### Exact revised candidate state

Base: `1d9b09626e9c4a6fb0e9d4fa7827684f2a7f7b11` (unchanged; HEAD is still this
commit — no new commit was created during remediation).

Working-tree modifications relative to `1d9b096`, exactly six substantive
paths plus this record:

```text
src/auteur/series/vertical_slice_service.py                         (guard-order fix)
docs/narrative-architecture.md                                      (terminology)
docs/design/series-episode-one-direction-implementation-boundary-v1.md  (terminology)
tests/test_series_episode_one_direction.py                          (assertions + 2 regression tests)
tests/test_series_vertical_slice_cli.py                             (assertions)
tests/test_series_vertical_slice_e2e.py                             (assertions)
docs/engineering/series-episode-one-direction-qualification-v1.md    (this record)
```

No other tracked file differs from `1d9b096`; in particular
`vertical_slice_models.py`, `vertical_slice_store.py`,
`vertical_slice_formatters.py`, `cli.py`, `episode_direction.py`,
`CHANGELOG.md`, the capability contract, and the Series Vertical Slice
qualification record are byte-unchanged. No untracked files were created.

### Guard-order issue — resolved

`SeriesVerticalSliceService.accept_episode_direction` previously loaded the
proposal file before checking Series eligibility, so a caller on a
Book-oriented or undeclared Series received a `FileNotFoundError` (and a weak
proposal-id existence/format oracle) instead of the domain eligibility
`ValueError`, and the ordering was inconsistent with `accept_book_direction`.
The explicit-episodic eligibility guard is now evaluated before the proposal
lookup, matching `accept_book_direction`. The valid episodic acceptance path
is unchanged, and AC10 ordering is preserved: the exact-match idempotency
check still runs before commitment validation and before the stale-source
check. A symmetrical regression test
(`test_edge_book_oriented_series_rejects_accept_episode_before_proposal_lookup`)
locks the new ordering.

### Narrative-architecture terminology — corrected

`docs/narrative-architecture.md` previously said an episodic Series uses an
Episode entry-unit Direction "in place of a Book Identity", which read as if
episodic Series lose the Book Identity concept. It now says the Episode
entry-unit Direction is used in place of the Book 1 Direction entry-unit
path, and states explicitly that the canonical Book Identity concept and the
five canonical scopes are unchanged. The five-scope and five-layer models are
untouched.

### Over-broad inspection contract and tests — corrected

The implementation-boundary document previously required the formatter/tests
to "never emit the token 'Book'". This overstated the product requirement,
which is that Episode 1 must never be labelled or surfaced as "Book 1" /
"Book Direction" — not that legitimate author-supplied text can never contain
the word "Book". The two over-broad phrases in the boundary document are
narrowed to the label requirement. The high-level capability contract was
already correctly label-focused and is unchanged. The corresponding broad
`assert "Book" not in <output>` assertions in
`tests/test_series_episode_one_direction.py`,
`tests/test_series_vertical_slice_cli.py`, and
`tests/test_series_vertical_slice_e2e.py` are replaced with assertions that
the Episode label ("Accepted Episode 1 Direction") is present and that
"Book 1" / "Book Direction" are absent. A new focused regression test
(`test_legitimate_author_text_may_contain_word_book_without_mislabelling`)
sets both the Series promise and the Episode title to legitimately contain
the word "Book" and demonstrates that the author text survives inspection
verbatim while the Episode label stays correct and no Episode-as-Book-1
mislabelling occurs.

### Fresh execution evidence (revised candidate)

Run with `PYTHONPATH=src`; counts are freshly measured against the revised
candidate, not carried over from the pre-commit evidence above.

- compile (`python -m compileall -q src`): **PASS**
- touched-unit group
  (`test_series_episode_one_direction`, `test_series_episode_direction`,
  `test_series_vertical_slice_service`, `test_series_vertical_slice_models`,
  `test_series_vertical_slice_store`, `test_series_vertical_slice_cli`):
  **217 passed, 0 failed**
- Episode acceptance suite (`tests/test_series_episode_one_direction.py`):
  **34 passed, 0 failed** — 32 tests as committed at `1d9b096` (verified by
  `git show 1d9b096:tests/test_series_episode_one_direction.py` collecting 32
  tests) plus the 2 new regression tests added by this remediation. Note: the
  pre-commit "Acceptance evidence" section above records "34 passed" for this
  file run in isolation; that figure was a stale carry-over from the earlier
  frozen pre-current-main candidate (whose copy of the file held 34 tests).
  The accurate isolated count for `1d9b096` is 32; the revised candidate is
  34 (32 + 2). No pre-existing test was removed by this remediation.
- Episode acceptance + vertical-slice e2e: **36 passed, 0 failed**
- contemporary-main coexistence group
  (`test_series_vertical_slice_global_map`, `test_series_repeated_map_focus`,
  `test_series_cli_continuity_integration`, `test_author_decisions_outcome`,
  `test_author_decisions_outcome_acceptance`): **103 passed, 0 failed**
- full normal repository suite (`python -m pytest -q`):
  **4,774 passed, 1 skipped, 27 xfailed, 0 failed**
- `ruff check` on the six candidate production files: **PASS**
- `ruff format --check`: unchanged from the pre-commit candidate — the same
  five pre-existing modified modules remain non-compliant (this debt exists
  at `1d9b096` and at the I1 baseline; the reorder and test edits follow each
  file's existing style and introduce no new non-compliance), and
  `episode_direction.py` remains compliant
- `git diff --check`: clean

These groups are reported as distinct counts and are not summed.

### Fresh independent review (revised candidate)

Each reviewer inspected the revised working-tree content and was instructed
not to anchor to the pre-commit reviews.

- Security: **0 Critical, 0 Important, 1 Minor**. The one Minor is the
  previously known, accepted, unconstrained-identifier-string
  defense-in-depth observation, unchanged by this remediation. The reviewer
  independently assessed the guard-order change as a net security
  improvement (it removes a proposal-id existence/format oracle on
  ineligible Series) with no downside.
- Performance: **0 Critical, 0 Important, 1 Minor**. The one Minor is the
  previously known, accepted O(n^2) duplicate-commitment check, unchanged by
  this remediation. The statement reorder adds no filesystem work on the
  common path and removes one read on the ineligible-Series error path.
- Pre-commit-follow-up Validator: **0 Critical, 0 Important, 0 Minor**, with
  one methodological "could not verify" item — the read-only Validator
  session had no shell/git access to confirm the exact file-scope boundary.
  The coordinator closed this directly with Git: exactly the six substantive
  paths above (plus this record) differ from `1d9b096`;
  `vertical_slice_models.py`, `vertical_slice_store.py`,
  `vertical_slice_formatters.py`, `cli.py`, `episode_direction.py`,
  `CHANGELOG.md`, the capability contract, and the Series qualification
  record are byte-unchanged; there are no untracked files; `git diff
  --check` is clean.

### The two deliberately unresolved accepted Minors

Both Minors from the pre-commit reviews remain open and were **not** fixed in
this remediation, by explicit decision:

1. Episode identifier-like model fields (`candidate_id`, `proposal_id`,
   `bundle_id`-derived) are unconstrained `str` at the Pydantic layer. Path
   safety is enforced downstream in every `vertical_slice_store.py`
   path-builder at all traced call sites, so there is no exploit path;
   model-level validation would be defense-in-depth only.
2. Duplicate commitment-reference detection in
   `EpisodeDirection._validate_episode_direction` is O(n^2) via `.count()` in
   a comprehension. The input is a small, human-authored list; assessed
   non-blocking.

Neither has been promoted to Important or Critical. Both were re-confirmed
present and unchanged by the fresh reviewers.

### Non-claims for this remediation

This section does not assert that a final post-documentation Validator has
reviewed the complete revised candidate (that pass is run after this record
is written), nor human approval, nor that the remediation has been committed,
pushed, merged, released, or shipped. The follow-up commit and push are
withheld pending the final Validator and an explicit human decision.

## Relationship to the historical frozen qualification record

An earlier, now-frozen qualification effort for this same Bounded Episode 1
Direction capability was performed on a different (pre-current-main)
baseline and is preserved as its own historical evidence. That record is not
reused, extended, or re-asserted by this document. This record's every claim
is grounded exclusively in evidence produced against the exact I1 candidate
identified above and, in the section immediately above, its bounded
review-remediation revision.
