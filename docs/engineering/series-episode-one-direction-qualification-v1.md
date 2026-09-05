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

## Relationship to the historical frozen qualification record

An earlier, now-frozen qualification effort for this same Bounded Episode 1
Direction capability was performed on a different (pre-current-main)
baseline and is preserved as its own historical evidence. That record is not
reused, extended, or re-asserted by this document. This record's every claim
is grounded exclusively in evidence produced against the exact I1 candidate
identified above.
