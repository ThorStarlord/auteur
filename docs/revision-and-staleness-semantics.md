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

Each dependency stores a versioned projection contract:

```yaml
projection:
  id: story_identity.structural
  version: 1
  fields: [genre, emotional_core, target_experience, central_engine]
projected_hash: sha256:...
full_content_hash: sha256:...
revision: 3
```

The projected hash controls semantic freshness. A revision change with the
same projected hash is visible for audit but does not create false staleness.
Projection versions require revalidation and are reported explicitly.
Blueprint chapter dependencies use chapter-specific projections; scenes use
their chapter projection unless they explicitly declare Blueprint fields.

## Hash policy

YAML and JSON are parsed, Unicode-normalized to NFC, serialized with sorted
keys and stable enum values, then hashed with SHA-256. Operational metadata and
dependency manifests are excluded; semantic extension fields are included.

Formatting-only YAML changes do not change the semantic hash. Markdown hashing
is outside this pilot.

## Acceptance

Initial acceptance creates revision 1 with the current content hash and direct
dependency evidence. Revalidation creates a new revision, refreshes dependency
evidence, and computes `fresh`. The current metadata remains in
`.auteur/state/artifacts/<artifact_id>.yaml`; immutable snapshots are stored in
`.auteur/state/artifacts/revisions/<artifact_id>/000001.yaml` and subsequent
numbered files. `list_revisions`, `current`, and `get_revision` expose this
history.

Intentional divergence also creates a new revision, records the reviewed
dependency snapshot and rationale, and sets
`review_state: acknowledged_divergence`. The mismatch remains visible without
re-entering unattended review. Any later dependency revision, projected hash,
or projection-version change reopens `review_required`.

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

## Author-facing impact and explanations

The CLI provides:

```text
auteur state affected-by <artifact>
auteur state affected-by <artifact> --json
```

Output identifies direct versus transitive impact, current health/freshness,
review state, and the dependency path. `state explain` retains structured
reason codes and hashes while adding summaries and recommended next actions.

## Provenance and knowledge validation

Provenance determines dependency freshness and artifact health; it does not
own narrative knowledge semantics. Scene status invokes the existing Layer 3
`KnowledgeValidator` boundary. When a state/order predecessor no longer
supports an entry knowledge fact declared from chapter position, the Scene is
invalid with an `impossible_knowledge` explanation while the dependency itself
remains separately marked stale.

This pilot does not implement collaboration, merge engines, branch
reconciliation, automatic semantic rewriting, model-inferred canonical edges,
database storage, or global migration.
