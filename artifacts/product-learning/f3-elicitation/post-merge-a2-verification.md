# Post-Merge Verification — A2 (PR #73): F3 elicitation surfaced in `decision view`

> Recorded 2026-08-13 after PR #73 merged (merge commit `d9926b1` on origin/main; exact
> PR head `357b640`, A2 — decision view elicitation-availability, mechanism M1).
> Direction A2 selected by the human under the standing delegated-authority envelope;
> reuse/extension of shipped F3 behavior, no escalation triggers. Source-qualified at the
> PR head before merge (4164 passed / 1 skipped / 27 xfailed; ruff + check.py green;
> independent review ship-as-is after one nit fixed in `357b640`).

## What shipped

`decision view` surfaces F3 elicitation availability deterministically (3 states):

- **unsettled** (no `goal_significance` + composed combinations): text hint with the
  exact `decision elicit` invocation; JSON `state: unsettled` + `command`;
- **no_composed_consequences**: honest "not applicable" note; JSON state only;
- **declared**: no hint (F1 is the destination); JSON `state: declared`.

Plus a pre-existing defect repair in the same handler: `view --json` failed with
"cannot represent an object" for any decision with alternative_bindings
(`EntityReferenceKind` not YAML-serializable) — `relationship` now serialized via
`.value`, matching the resolved block.

## Post-merge test evidence

```
tests\test_author_decisions_view_elicitation.py + cli + elicit:
44 passed in ~40s (merged main, repo .venv)
```

## Controls verified

- 3-state matrix (unsettled/declared×2/no_composed_consequences), invocation text,
  JSON state+command closed set, directionless honesty, no-resolution regression,
  anti-inference (unsettled prose vs absent — identical hints modulo decision_id),
  authored-lines regression.
- Existing view/evaluate/elicit tests unchanged; full suite 4164 passed / 0 failed at
  the PR head.
- Backward compatible: no identity/blueprint → no elicitation section; declared → no
  hint.

## Post-merge observations (recorded; non-blocking)

1. Hint paths are unquoted (consistent with the rest of the CLI; a path with spaces
   would break copy-paste — cosmetic, out of stated scope).
2. JSON always carries `authored.elicitation` (null without resolution); control 5 pins
   only the text path — a one-line JSON regression assert could harden this later.

## Escalation check

No escalation condition encountered; merged scope matches the delegated initiative
exactly (one CLI handler + tests + design doc; the `view --json` enum fix is a same-handler
defect repair, not scope creep).

## Claim language

- **agent-validated:** A2 surfacing of shipped F3 behavior.
- **post-merge observed:** this record.
- No claim of human approval for intermediate choices; the human selected direction A2.
