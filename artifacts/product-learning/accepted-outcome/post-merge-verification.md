# Post-Merge Verification — Accepted-Outcome: `chosen` field (PR #74)

> Recorded 2026-08-14 after PR #74 merged (merge commit `156b73cb` on origin/main; exact
> PR head `a5caa18`, accepted-outcome `chosen` membership field, mechanism M1). Selected
> under the standing delegated-authority envelope; human-demonstrated value (explicit
> outcome materially improves continuity). Source-qualified at the PR head (4174 passed /
> 1 skipped / 27 xfailed; ruff + check.py green; independent review ship-as-is after two
> should-fix items fixed in `a5caa18`).

## What shipped

Optional, author-controlled `chosen: list[alternative_id]` on AuthorDecision — the
explicit chosen outcome that the deliberation machinery had never persisted:

- `one_of` → exactly 1 member; `choose_k_of_n` → exactly `k` members; absent/None →
  open decision (backward compatible).
- fail-closed: members must be declared `alternative_ids`, distinct, cardinality matches
  the combination rule; `combination_direction` alone never implies membership.
- echo-only: surfaced in `decision view` (text + JSON) and recorded in the acceptance
  record (omitted when absent); never mutates canonical state, never drives propagation,
  never ranks, never inferred from prose.
- composed consequences byte-identical with/without `chosen`.

## Post-merge test evidence

```
tests\test_author_decisions_outcome.py + outcome_acceptance + core:
36 passed in ~40s (merged main, repo .venv)
```

## Controls verified

- Parse one_of (1 member) / choose_k_of_n (k members) / absent (None, backward compat).
- Fail-closed: unknown member, one_of=2, choose_k wrong count, duplicate members — all
  rejected.
- Direction≠membership; view surface; byte-identical consequences; acceptance provenance
  (chosen recorded; open-decision record omits the key).
- Full suite 4174 passed / 0 failed at the PR head.

## Escalation check

No escalation condition encountered; merged scope matches the delegated initiative
exactly (schema field + validation + view + acceptance-record + tests + design doc).
`chosen` is an explicit author-authored fact, not weights/ranking/LLM/ontology/prose
inference, and does not mutate canonical story state.

## Claim language

- **human-demonstrated:** explicit outcome materially improves continuity (one case).
- **agent-selected/validated:** M1 + qualification.
- **post-merge observed:** this record.

## Follow-on (parked, not started)

The two campaigns this unblocks — Accepted-Decision Downstream Validation and Decision
Revision & Supersession Validation — remain PARKED. Per the standing envelope, neither
is resumed automatically; they wait for the behavioral experiments already specified.
