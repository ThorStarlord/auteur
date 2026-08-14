# Reconciliation — release-qualification evidence producer (2026-08-14)

## Work claim

```text
implemented:
  - scripts/release_evidence.py — canonical durable release-qualification
    evidence producer (candidate provenance guard, structured-pytest suite
    accounting, baseline failure-set deltas, wheel result consumption)
  - scripts/check.py --qualify — qualification invocation replaces the plain
    pytest entry (single suite execution, explicit flag)
  - scripts/verify_wheel.py — narrow repair: expected version derived from
    canonical pyproject metadata (tomllib) instead of hardcoded 0.37.0
  - tests/test_release_evidence.py — 16 focused tests (terminal-outcome
    collapsing, reconciliation, provenance guard, baseline deltas)

mechanically derived:
  - suite accounting: collected 4252 = passed 4224 + skipped 1 + xfailed 27
    + xpassed 0 + failed 0 + errors 0 (reconciles: true), from a real
    execution via structured pytest reports, not terminal prose
  - candidate sha: git rev-parse HEAD at qualification time
  - wheel result: consumed from the existing scripts/verify_wheel.py
    (exit code, banner, sha256), environment-sanitized

still requires human/owner judgment:
  - baseline/release disposition: the producer emits observations and
    failure-set deltas only; whether a known baseline failure is permitted
    for a release remains the release authority's decision

deliberately unchanged:
  - CHANGELOG.md currency drift (separate finding, not causally linked)
  - product behavior, routing, Skills, workflows, contracts
  - Sensemaking Skills repository
  - historical acceptance records (v0.35 and earlier hand-maintained tables
    are preserved as history, not rewritten)

validation performed:
  - focused tests: 16/16 passed (tests/test_release_evidence.py)
  - qualification run on candidate 309a473: suite 4252 collected, 0 failed,
    0 errors, 0 xpassed; wheel qualification 10/10 PASS; exit 0
  - fail-closed demonstrated: candidate 27c5282 run recorded collection
    errors (stale-environment) and the gate exited nonzero with the failure
    recorded; a subsequent wheel-only failure was recorded before the
    PYTHONPATH-leak fix

unresolved:
  - first run establishes no baseline reference yet; a future run with
    --reference <sha> will compute added/removed/unchanged failure sets
  - future acceptance/release records should cite
    docs/qualification-evidence/<candidate-sha>.json instead of reproducing
    counts (convention applies from the next release record onward)
```

## Claim-by-claim reconciliation

| Claim | Classification | Evidence |
|---|---|---|
| Producer exists and is durable/candidate-addressed | **VERIFIED** | `docs/qualification-evidence/309a4731212502edc12080aab251d9c954702df0.json` (candidate `sha` = 309a473; created by `scripts/release_evidence.py`) |
| Suite accounting is mechanically derived and reconciles | **VERIFIED** | Artifact `suite`: 4252 = 4224+1+27+0+0+0, `reconciles: true`, `collection_errors: []`, `session_errors: []`; derived from structured pytest reports (one terminal outcome per node) |
| Candidate SHA identifies the tested bytes | **VERIFIED** | Provenance guard recorded `clean_for_candidate: true` and the permitted non-candidate changes; the pre-fix candidate 27c5282 artifact documents the fail-closed gate behaving correctly |
| Wheel evidence comes from the existing verifier, not a reimplementation | **VERIFIED** | Artifact `wheel`: `source: scripts/verify_wheel.py`, `status: PASS`, `exit_code: 0`, banner + sha256 captured; the verifier's 10 checks were not duplicated |
| No hand-transcribed accounting in the new path | **VERIFIED** | Every value in the artifact derives from execution or git; no prose was scraped (`-rA` parsing not used) |
| Historical records preserved, not rewritten | **VERIFIED** | v0.35/v0.37 hand-maintained tables untouched; the two failed-attempt artifacts (27c5282) remain candidate-addressed |
| Changelog drift fixed by this task | **DISPUTED** (claim not made) | Out of scope by design; recorded as a separate finding |

**Omitted:** none material. One nuance recorded rather than hidden: the first qualification run failed (stale environment collection errors) and the second failed on wheel (PYTHONPATH leak); both are preserved as the candidate-addressed 27c5282 artifact, and the leak was fixed in 309a473.

## Repair verification (finding-specific)

Original finding (evidence-0021 lineage, re-derived for Auteur at 30529b99):
"the release-qualification policy requires reconciled evidence, but the
complete-suite evidence has no canonical durable producer; acceptance
records transcribe mechanically observable results by hand."

Closure question: can a fresh reviewer trace **candidate X -> actual
qualification execution -> mechanically reconciled evidence artifact ->
acceptance record** without relying on copied terminal prose?

```text
acquisition_status: SUCCEEDED
  (suite executed in full; wheel qualification executed in full)

observation (finding-specific):
  candidate 309a473 -> `python scripts/release_evidence.py`
    -> docs/qualification-evidence/309a473....json
       (reconciles true; wheel PASS; provenance guard clean)
    -> this record cites the artifact by sha address

disposition: closed
  (the suite-evidence provenance path is mechanically closed; the
   acceptance-record citation convention applies to future release records;
   changelog drift remains a separate, unclosed finding)
```

Generic-green note: "all 4252 tests green" alone is not the closure proof —
the closure proof is the existence and content of the candidate-addressed,
mechanically reconciled artifact that this record cites.
