# Auteur 1.0 public contract

This document defines the compatibility surface for the `1.x` release line.

## Python interface

The names listed in `auteur.__all__` are the supported package-root imports for
1.x. Their import paths, names, constructor fields, enum values, serialized
field names, and documented error behavior are stable under SemVer:

- additive optional fields and new enum values require compatibility review;
- removing, renaming, or changing the meaning of a listed name requires a
  major version;
- internal modules and names not listed in `auteur.__all__` are not stable
  package-root imports;
- deprecated names remain available for the documented 1.x deprecation window
  and must emit a targeted deprecation notice before removal.

The authoritative export manifest is the `__all__` declaration in
`src/auteur/__init__.py`; `tests/test_public_api_contract.py` prevents
accidental drift.

## CLI interface

The `auteur` console script is a supported interface. Stable commands,
options, exit codes, and `--json` object keys are documented by the command's
own help and [the 1.0 CLI contract](cli-contract.md). A command that is not
documented as supported is experimental and must not be used as an automation
dependency.

## Persisted artifacts

Project files and sidecar artifacts are user data. Compatibility is governed by
`docs/engineering/artifact-compatibility.md`: loaders reject unsupported future
versions, migrations are deterministic, and a write never silently reinterprets
ambiguous legacy data.

Changes to `.auteur` paths, schema versions, field names, enum values, pointer
formats, decision snapshots, or acceptance journals require a migration note,
fixture coverage, and release-note entry before merge.

Acceptance journaling is a write-ahead operational record, not a replay log.
`AcceptanceJournal.recovery_report()` reports interrupted operations and always
sets `replay_allowed` to false until the owning artifact workflow has performed
an explicit, owner-specific recovery action.

## Release rule

`1.0.0` is not evidence that this contract has been qualified. A release may be
called qualified only when the exact candidate SHA, source checks, built wheel,
installed smoke tests, and release record agree as required by
`docs/engineering/release-qualification.md`.
