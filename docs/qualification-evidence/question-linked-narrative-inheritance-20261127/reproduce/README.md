# Reproduction context for PR #648's recorded evidence

These scripts and the files under `exercise-a/` are PR #648's historical evidence. They were produced under PR #648's contract
(merge commit `77c5848a`, `feat/question-linked-narrative-inheritance`). They are kept unchanged. This note records how they
relate to the current code, so that nobody reads the recorded names as current ones.

## Renamed fields

PR #649 (merge commit `55cd1da9`) renamed two live-read fields of the Working Book owner. The recorded evidence keeps PR #648's names.

| PR #648 name (recorded in this evidence) | Current name (PR #649 and later) |
| --- | --- |
| `resolved_at_recorded_version` | `resolved` |
| `identity_at_recorded_version` | `identity_at_read_version` |

Only live reads used the old names, so no stored record carries them. The recorded file `exercise-a/referent-recovered.json` keeps
PR #648's names and is not rewritten. Whether its values match what the current code gives for the same read was not checked in
this PR.

## Execution context

- To reproduce the recorded files exactly, check out `77c5848a` in a separate worktree and run the stages there, with
  `PYTHONPATH=src` pointing at that worktree's `src`.
- On the current code the same stages write the current field names. Compare by the table above, not by string match.
- These scripts were not run against `main` in the PR that carries this note. Nothing in this folder was edited to make it run.
