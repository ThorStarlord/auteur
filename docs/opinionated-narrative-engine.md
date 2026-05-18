# Opinionated Narrative Engine

Auteur is an automated AI story architect for beginner-to-intermediate fiction
writers who need decisive narrative direction. It transforms raw creative input
into a recommended, validated story engine before any chapter outline or prose
draft is treated as the product.

## Product Contract

Auteur recommends strongly, but the author can override. The system may infer
the strongest story implied by a premise, explain why that direction is strongest,
and reject weaker directions, but it must preserve those choices in explicit
artifacts before compiling them into a blueprint.

The default recommendation basis is `genre_aligned`: the strongest engine is the
one that best fulfills the commercial and reader-facing promise of the selected
genre/subgenre. Structural coherence and fidelity to author input still constrain
the recommendation, while emotional power is used to sharpen ties and explain
the recommendation.

## Three Layers

1. **Narrative Engine**: The primary product scope. This layer locks the core
   answer, target experience, genre promise, protagonist want, resistance,
   conflict, stakes, change, ending shape, rejected directions, and rationale.
2. **Chapter Outline**: Optional downstream automation. This layer sequences the
   accepted story engine into chapters after the engine is locked.
3. **Prose**: Optional execution. This layer drafts words from the accepted
   structure and should not invent or silently rewrite the story engine.

## Modes

**Opinionated Mode** is the default. Auteur presents one recommended engine,
explains why it best serves the premise and genre promise, lists weaker rejected
directions, and asks the author to accept, modify, or switch modes.

**Open-Ended Mode** is optional. Auteur presents multiple viable engines for
advanced authors who want exploration before locking the identity artifact.

## Artifact Boundary

`story_identity.yaml` is the approval boundary. Recommendation rationale such as
`why_this_is_best`, `rejected_directions`, and `author_overrides` documents the
decision process, but only accepted identity fields compile into `blueprint.yaml`.

Deterministic structure diagnostics validate shape, completeness, and coherence.
They do not judge whether the story is good, and they must not call an LLM.
