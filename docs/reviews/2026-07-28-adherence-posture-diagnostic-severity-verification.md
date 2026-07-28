# Adherence-Posture Diagnostic Severity Verification

## Repository

Baseline SHA: `9b535e9d2c8d82aeb2b06aa671aa08709b3275c7`

Branch: `main`

Implementation SHA: `1be070cad1dc4bf0618e3d10ab7d95ac40e5a23e`

Working tree: clean except for the intentionally uncommitted approved
specification `docs/superpowers/specs/2026-07-28-adherence-posture-diagnostic-severity.md`.

## Policy

Actual posture values: `conventional`, `flexible`, `revisionist`, `subversive`,
`deconstructive`.

Default posture: `conventional`.

Central policy location: `auteur.structure.profile_severity`.

| Posture | D-RES-001 | D-RES-002 | D-RES-003 |
|---|---|---|---|
| conventional | ERROR | ERROR | WARNING |
| flexible | WARNING | WARNING | WARNING |
| revisionist | WARNING | WARNING | WARNING |
| subversive | WARNING | WARNING | WARNING |
| deconstructive | INFO | INFO | INFO |

Flexible, revisionist, and subversive remain distinct author choices and
intentionally share severity behavior in this first slice.

## Diagnostics

D-RES-001, D-RES-002, and D-RES-003 retain their stable IDs, triggers,
evidence, source commitment, affected Blueprint paths, repair guidance, and
override behavior. Only effective severity and additive posture metadata
vary. The existing `genre_recommendation_flow` metadata carries posture and
effective severity; no diagnostic schema changed.

Posture is passed from the accepted identity by `run_genre_diagnostics()` to
the canonical analyzer. The CLI still only renders results. D-RES-003 remains
a warning-level conflict advisory for every posture except deconstructive,
which is informational.

## Compatibility

Compilation remains permissive: an ERROR diagnostic does not block Blueprint
creation or mutate StoryIdentity. CLI exit codes remain unchanged (`genre
diagnose` returns 0 in the tested conflict cases). No-profile projects emit no
profile diagnostics. Missing posture uses the conventional default; unknown
string values use the same deterministic safe fallback in the policy helper,
while the Pydantic schema continues to reject unknown persisted enum values.
Human and JSON outputs expose the same IDs, effective severities, posture, and
source evidence. No Blueprint, StoryIdentity, ProfileDerivation, version, or
release schema changed.

## Counterfactuals

CONVENTIONAL: D-RES-001/002 ERROR; D-RES-003 WARNING; compilation succeeds.

FLEXIBLE: all three WARNING.

REVISIONIST: all three WARNING.

SUBVERSIVE: all three WARNING.

DECONSTRUCTIVE: all three INFO.

Override: targeted required-outcome override remains suppressed; unrelated
resolution-pattern conflict remains visible.

No profile: no profile diagnostics.

Round trip: posture survives identity serialization.

Idempotence: existing analyzer determinism tests plus the focused matrix use
stable IDs and severities across repeated inputs.

## Tests

Baseline collected: 3,774.

Candidate collected: 3,792.

Delta: +18 tests, all in `tests/test_adherence_posture_severity.py`.

Added nodes: 18. Removed nodes: 0. Marker changes: 0.

Focused: 72 passed, 0 skipped, 0 xfailed, 0 xpassed, 0 failed, 0 errors.

Serial: 3,792 collected; 3,764 passed; 1 skipped; 27 xfailed; 0 xpassed;
0 failed; 0 errors.

Parallel: identical categories and arithmetic.

Arithmetic: `3,764 + 1 + 27 + 0 + 0 + 0 = 3,792`.

The full runs used Python 3.14.3, pytest 9.0.3, explicit `tests` paths, and
the repository source pinned through `PYTHONPATH`. JUnit artifacts and logs
were disposable qualification outputs and were not committed.

## Deferred work

- acknowledgment workflows;
- compilation blocking;
- distinct runtime behavior for flexible/revisionist/subversive;
- `rejected_outcomes` representation changes;
- emotional-target propagation;
- narrative-engine propagation;
- framing propagation.

## Verdict

Specification implemented: PASS

Severity policy centralized: PASS

D-RES-001 matrix correct: PASS

D-RES-002 matrix correct: PASS

D-RES-003 matrix correct: PASS

Compilation remains permissive: PASS

CLI exit codes unchanged: PASS

Override suppression remains targeted: PASS

Human/JSON parity preserved: PASS

No-profile behavior preserved: PASS

No schema change: PASS

Serial suite reconciled: PASS

Parallel suite reconciled: PASS

Ready for review: YES
