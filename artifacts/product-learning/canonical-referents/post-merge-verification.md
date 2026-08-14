# Post-Merge Verification — F2 canonical structural referents (PR #75)

> Recorded 2026-08-14 after PR #75 merged (merge commit `c968a747` on origin/main; exact
> PR head `8fb23f0`, F2 explicit anchor promotion). Selected under the standing
> delegated-authority envelope. Source-qualified at the PR head (4185 passed / 1 skipped /
> 27 xfailed; ruff + check.py green; independent review ship-as-is after 4 should-fix +
> 2 nits resolved).

## What shipped

- `StoryBlueprint.structural_referents: list[StructuralReferent]` — neutral durable
  referent (NOT a subplot ontology): `referent_id`, `kind` (validated closed value
  "subplot"), `participants`, `carrier_refs`, `provenance` (decision_id + anchor_id +
  promoted_at). `extra="forbid"` on both models.
- `decision promote <id> --anchor <id>` — explicit opt-in promotion; fail closed on
  unknown anchor, stale/unresolvable refs, and wrong-category refs (participant must be
  character, carrier must be thread). Idempotent.
- Promotion MAY create the durable referent; NEVER enacts the chosen outcome and NEVER
  promotes `bears_on`/`nature`/F1 significance. Backward compatible (empty default).

## Post-merge test evidence

```
tests\test_author_decisions_referents.py + outcome + core:
44 passed in ~40s (merged main, repo .venv)
```

## Controls verified

- promote creates stable referent; durable subset only (no bears_on/nature); unpromoted
  anchor stays local; duplicate promotion idempotent; no-enactment (story_engine +
  characters unchanged); significance not promoted; existing blueprints load unchanged;
  unknown-anchor fail-closed; stale-participant fail-closed; wrong-category participant
  fail-closed.
- Full suite 4185 passed / 0 failed at the PR head.

## Escalation check

No escalation condition encountered; merged scope matches the delegated initiative
(schema field + promote subcommand + tests + design doc). The durable referent reuses the
existing narrow `kind` vocabulary (validated closed), does not restructure
`story_engine.threads`, and does not introduce a generic subplot ontology.

## Accepted nit (carried forward, low likelihood)

`decision promote` writes the blueprint via `read_yaml`→`atomic_write_yaml` (full
`safe_load`/`safe_dump` round-trip), which could normalize timestamp-like scalars or drop
comments. Accepted as a nit — the frozen fixture has `profile_derivation: null`; a future
surgical-write refactor can address it if a real case shows re-serialization harm.

## Claim language

- **human-demonstrated:** accepted outcome needs a stable referent (downstream test).
- **agent-selected/validated:** F2 + qualification.
- **post-merge observed:** this record.

## Follow-on (parked, not resumed)

Accepted-Decision Downstream Validation and Decision Revision & Supersession remain
PARKED. Per the envelope, neither resumes automatically; the next natural experiment
(chosen outcome → durable referent → can the author now enact/carry it downstream) waits
for the human's go-ahead.
