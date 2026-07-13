# Revision and Staleness Semantics

This document defines the Minimal V1 provenance pilot for:

```text
StoryIdentity → Blueprint → Chapter Outline → Scene Realization
```

It does not define provenance for Universe, Series, Draft/Expression,
Editing, Round-trip Import, Relations, graphs, or reports.

## Status dimensions

Metadata keeps independent dimensions:

- `authority`: `canonical` or `derived`;
- `lifecycle`: `draft`, `accepted`, `replaced`, `rejected`, or `archived`;
- `review_state`: `none`, `review_required`, or `acknowledged_divergence`;
- `provenance_state`: `tracked` or `unknown`.

Health and freshness are computed:

- `valid` when schema and dependency invariants hold;
- `invalid` when an objective invariant fails;
- `fresh` when recorded direct dependency revisions and hashes match;
- `stale` when a dependency changed but the artifact remains structurally valid.

Stale is not invalid. Accepted author work is never silently overwritten.

## Authority

Accepted author contracts and plans are canonical. Generated candidates are
drafts until explicitly accepted. Dependency manifests, graphs, and reports
are derived. Authority changes only through explicit adoption or acceptance.

## Sidecars

Pilot metadata lives beside the project under:

```text
.auteur/state/artifacts/<artifact_id>.yaml
```

The source YAML remains unchanged. Missing sidecars mean provenance is unknown;
legacy artifacts remain loadable and valid when their own schemas pass.

## Direct dependencies

The pilot records direct edges only:

```text
StoryIdentity ──semantic────▶ Blueprint
StoryIdentity ──semantic────▶ Chapter Outline
Blueprint ──────structural──▶ Chapter Outline
Chapter Outline ─structural──▶ Scene Realization
Blueprint ──────semantic────▶ Scene Realization
Scene A ────────state/order─▶ Scene B
```

Edges are marked `declared`, `inferred`, `generated`, or `suggested`.
Suggested model edges never become canonical automatically. Transitive impact
is computed at runtime.

## Hash policy

YAML and JSON are parsed, Unicode-normalized to NFC, serialized with sorted
keys and stable enum values, then hashed with SHA-256. Operational metadata and
dependency manifests are excluded; semantic extension fields are included.

Formatting-only YAML changes do not change the semantic hash. Markdown hashing
is outside this pilot.

## Acceptance

Initial acceptance creates revision 1 with the current content hash and direct
dependency evidence. Revalidation creates a new revision, refreshes dependency
evidence, and computes `fresh`.

Intentional divergence also creates a new revision, retains stale dependency
evidence, and sets `review_state: acknowledged_divergence`. It remains stale.
Unreviewed stale artifacts remain unchanged and require review.

## Archival

Accepted artifacts are archived rather than hard-deleted. IDs are never reused.
Archive metadata records who, when, why, and an optional replacement. Active
references to archived artifacts are invalid; historical references must name an
explicit revision and historical relation.

## Legacy adoption

Artifacts without sidecars remain usable and are reported with
`provenance_state: unknown` and freshness `unknown`. Explicit adoption creates
a baseline sidecar without rewriting the source artifact. Repository-wide
migration is not required.

## Pilot limitations

This pilot does not implement collaboration, merge engines, branch
reconciliation, automatic semantic rewriting, model-inferred canonical edges,
database storage, or global migration.
