# Artifact Compatibility Contract

Auteur project files are versioned independently from the Python package. Every
persisted artifact envelope must carry an integer `schema_version`; omitted
versions are interpreted as version 1 only for legacy artifacts whose current
loader already defines that default.

Loaders must reject versions newer than the loader supports. They must not
coerce a future artifact into the current model or silently discard unknown
fields. A migration is a deterministic, read-before-write transformation and
must preserve the original file until the author explicitly accepts the
migrated result.

The stable v1 boundary includes artifact identity, revision, lifecycle,
authority, content hash, dependencies, and provenance. Changes to these fields,
serialized enum values, or canonical paths require a migration entry and a
release note. Package version `1.0.0` does not itself migrate project data.

Cross-domain readers use the shared validity states `fresh`, `stale`, `unknown`,
`missing`, `malformed`, and `unavailable`. Every state other than `fresh` is
blocking for canonical promotion. Authority-bearing acceptance is wrapped by
the `.auteur/acceptance/journal.json` intent/completion journal; incomplete
operations remain recoverable and are never inferred to have succeeded.
