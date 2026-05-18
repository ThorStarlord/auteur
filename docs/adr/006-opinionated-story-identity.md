# ADR 006: Opinionated Story Identity Recommendation Metadata

## Status

Accepted

## Context

ADR 004 introduced `StoryIdentity` as the creative contract before
`StoryBlueprint`. Auteur's product direction now emphasizes a stronger posture:
it should infer and recommend the strongest story engine implied by raw input,
especially for beginner-to-intermediate writers who need decisive narrative
direction.

The risk is over-authoring. If recommendation rationale is hidden or compiled
directly into the blueprint, users may lose clear ownership of the story spine.

## Decision

`StoryIdentity` may carry recommendation metadata:

- `recommendation_mode`
- `best_basis`
- `why_this_is_best`
- `rejected_directions`
- `author_overrides`

The default mode is `opinionated`, and the default basis is `genre_aligned`.
The recommendation metadata documents why Auteur chose a direction and which
directions it rejected, but it is not a separate source of blueprint truth.

Only accepted or edited identity fields, such as `core_answer`, `story_type`,
`target_experience`, and `central_engine`, compile into `StoryBlueprint`
structure.

## Consequences

- Auteur can be decisive without silently mutating authorial intent.
- The recommendation process is versionable and reviewable in
  `story_identity.yaml`.
- Existing minimal identity files remain valid through schema defaults.
- Deterministic diagnostics continue to validate coherence and completeness,
  not story quality.
