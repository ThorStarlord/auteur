# Expression Composition

Expression Composition is a Layer 4 operation that assembles accepted Scene
Expressions into a derived Chapter Expression snapshot.

```text
Accepted Scene Expressions → deterministic Chapter Expression assembly
```

## Ownership

Scene Expression remains canonical at Scene scope. Chapter Expression is a
derived, provenance-rich assembly and is never a second silent source of truth.
Accepting an assembly approves its selected source revisions; it does not
change Scene Realization, Scene Expression, Structure, Story Identity, or the
Bible, and does not mean the Chapter is publication-ready.

## Stable markers

The internal manuscript uses stable, machine-readable markers:

```html
<!-- auteur:scene id=scene_07_01 expression_revision=3 -->
Scene prose.
<!-- auteur:end-scene id=scene_07_01 -->
```

Markers are stored in the internal manuscript and duplicated in the metadata
section map. Clean export may remove them. Missing, malformed, or duplicated
markers are invalid for future reconciliation. Character offsets are never the
sole mapping mechanism.

## Transition representation

V1 stores transitions inside the Chapter Expression manifest rather than
creating a general transition-artifact subsystem:

```yaml
transition_id: transition_scene_07_01_scene_07_02
before_scene: scene_07_01
after_scene: scene_07_02
revision: 1
lifecycle: accepted
text: "At dawn, the archive was already awake."
content_hash: sha256:...
```

Transition prose is Chapter-owned Expression. It may connect time, place, POV,
or tone, but may not introduce canonical events absent from Realization.
Automatic transition generation is outside this pilot.

## Transformation contract

```yaml
id: expression.compose_chapter
category: projection
family: knowledge_evaluation
version: 1
inputs:
  - accepted Chapter Structure
  - accepted Scene Expressions
  - optional accepted transition text
outputs:
  - Chapter Expression assembly
  - rendered Chapter manuscript
  - section map
  - validation findings
executor:
  epistemic_behavior: translational
  kind: deterministic
authority_change:
  from: canonical_sources
  to: derived_assembly
acceptance_required: true
lossiness: reversible_internally
reversibility: reversible_while_markers_and_manifest_exist
failure_policy:
  atomic: true
  partial_accepted_output: forbidden
```

The composer preserves Chapter order, Scene IDs, selected Expression and
Realization revisions, Scene prose, and transition ownership. It creates only
markers, separators, manifest metadata, and derived assembly output.

## Storage

```text
chapters/<chapter>/expression/
├── chapter_v001.md
├── chapter_v001.yaml
├── chapter_v002.md
├── chapter_v002.yaml
└── accepted.yaml
```

Every assembly receives a new version. Previous assemblies remain available.
Acceptance marks the prior accepted assembly `replaced` and never deletes it.
Existing `draft_vN.md` and `final.md` behavior is unchanged.

## Mixed revisions and staleness

Mixed revisions are valid:

```text
scene_01 → prose_v003
scene_02 → prose_v001
scene_03 → prose_v005
```

Each selected revision must be accepted, valid, fresh, or explicitly
acknowledged as divergent, and recorded in the assembly manifest.

An assembly becomes stale when its Chapter Structure, selected Scene
Expression, source Scene, transition, or transformation version changes.
Formatting-only equivalent changes follow canonical hashing behavior. Stale
assemblies remain preserved and are never regenerated automatically.

## Acceptance

Chapter acceptance records the selected assembly revision, author, and time.
It creates an accepted derived snapshot and marks the previous accepted
assembly replaced. Invalid, stale, or unresolved assemblies cannot be accepted
without the explicit review path. Acceptance never mutates upstream artifacts.

## External edits and round-trip boundary

The pilot only supports marker-preserving inspection and clean marker removal.
Markerless or ambiguously marked external edits become unresolved Chapter
divergence. They may be preserved, compared, or turned into proposals, but are
not heuristically split back into Scene Expressions.

Direct Chapter edits create a Chapter Expression candidate. They do not mutate
Scene prose. Section-aware editing, semantic merge, and full reconciliation
are future work.

External edits are handled by the separate `expression.reconcile_chapter`
inspection/proposal pilot. Inspection and proposal creation preserve the
derived assembly and canonical Scene artifacts; proposal application is not
part of that pilot.

The pilot provides read-only marked-manuscript inspection. It reports unchanged,
modified, moved, missing, duplicated, and unresolved sections without writing
back to Scene Expression. Markerless manuscripts receive an actionable
`unresolved_divergence` report and are never heuristically split.

Transition manifests are Chapter-owned dependencies. Their boundary, lifecycle,
revision, and content hash participate in Chapter freshness. Structured events
not found in adjacent Realization create review-required findings; likely prose
events remain advisory. Transition changes never mutate upstream artifacts.

The CLI supports concise inspection, technical JSON inspection, clean or
marker-preserving export, marked-manuscript inspection, and Chapter assembly
comparison:

```bash
auteur expression inspect-chapter chapter_07:expression_v001 --project PROJECT
auteur expression inspect-chapter chapter_07:expression_v001 --project PROJECT --json
auteur expression export-chapter chapter_07:expression_v001 --project PROJECT --output chapter_07.md --clean
auteur expression export-chapter chapter_07:expression_v001 --project PROJECT --output chapter_07-marked.md --with-markers
auteur expression inspect-manuscript edited.md --against chapter_07:expression_v001 --project PROJECT
auteur expression compare-chapters chapter_07:expression_v001 chapter_07:expression_v002 --project PROJECT
```

Clean export removes internal markers and is not round-trip-safe. Marked export
preserves the internal mapping. Neither export becomes canonical automatically.

## Progressive disclosure

- Simple mode: concatenate accepted Scene prose in Chapter order.
- Guided mode: show selected revisions, stale sections, and transitions.
- Advanced mode: Chapter-level editing and marker-aware reconciliation.

The pilot implements deterministic simple-mode assembly only.

## Non-goals

This pilot does not implement a generic composition runtime, automatic
transition generation, chapter-wide Bard drafting, semantic merge, publishing,
collaboration, Scene synchronization from Chapter edits, or full round-trip
reconciliation.
