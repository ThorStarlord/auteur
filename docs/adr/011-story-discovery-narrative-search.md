# ADR 011: Story Discovery as Narrative Search

## Status

Accepted

## Context

Auteur's `StoryIdentity` workflow can already recommend and validate a single
high-level story contract before blueprint compilation. That solves cold-start
identity generation, but it still frames raw notes as if they imply one best
story.

The stronger Narrative Engine workflow is to treat a premise as a design space:
the same brain dump may support several structurally valid interpretations with
different emotional promises, genre contracts, risks, and reader expectations.

## Decision

Story Discovery is a first-class Narrative Engine workflow:

```text
brain dump -> narrative search -> StoryIdentity candidates -> architectural comparison -> author decision -> canonical StoryIdentity
```

Story Discovery produces proposal and report artifacts. Candidate YAML files are
not canonical state. The author promotes one candidate only after validation, and
that promoted file becomes the canonical `story_identity.yaml`.

Candidate generation explores intentional design lenses such as emotional
payoff, commercial clarity, and thematic coherence. These lenses exist to search
different regions of the premise's narrative space, not to produce random
variants.

Contract fit is deterministic compliance analysis. It measures how well a
candidate satisfies its declared `GenreContract` and structural diagnostics. It
does not measure story quality and must not be treated as an automatic winner
ranking.

## Consequences

- Story Discovery remains inside the Narrative Engine layer and does not create
  chapter outlines or prose artifacts.
- Auteur keeps the compiler-style path of proposals, validation, promotion, and
  canonical state.
- LLM generation may propose candidate identities, but contract-fit analysis is
  deterministic and explainable.
- Future Blueprint Discovery and Outline Discovery can reuse the same
  proposal-comparison-promotion pattern without changing this workflow's scope.
