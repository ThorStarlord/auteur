# Opinionated Narrative Engine

Auteur is an automated AI story architect for creative beginners who need
decisive narrative direction. It transforms raw creative input into a
recommended, validated story engine before any chapter outline or prose draft
is treated as the product.

## Product Persona

Auteur's primary persona is a **creative beginner**: someone inexperienced in
long-form narrative craft, regardless of technical ability. Technical expertise
is not a requirement of the product and is not its defining audience.

Product design should progressively hide internal machinery such as CLI
commands, YAML, Pydantic, and Auteur's specialist vocabulary from users who do
not need to understand it. This is a product-design hypothesis, not a semantic
layer or runtime-architecture decision.

## System Definition vs Product Design

Auteur's **system definition** is the settled technical and domain contract:
the narrative compiler, five semantic layers, canonical author commitments,
deterministic diagnostics, bounded generation, and explicit authority
boundaries.

Auteur's **product design** is how a creative beginner discovers, understands,
and operates that contract: onboarding, progressive disclosure, vocabulary,
diagnostic presentation, repair decisions, and the default interaction surface.
The system definition is substantially established; product design remains an
active design and research area. This distinction does not introduce another
semantic layer.

## First Value (Working Product Promise)

Auteur's first valuable outcome is helping a creative beginner turn a raw idea
into a clear, accepted whole-story direction: a `StoryIdentity` plus enough
Structure to understand what the story is and where its risks are. Immediate
prose generation is not the primary first-value promise.

## Default Interaction Surface (Working Product Hypothesis)

The default creative-beginner path should be guided authoring. Users should not
need to edit YAML, understand Pydantic, or operate the CLI directly to reach
the first valuable outcome. Canonical artifacts, provenance, and advanced CLI
surfaces remain inspectable and available for users who want them. The specific
guided surface—browser, TUI, editor integration, or another form—remains open.

## Recommendation Posture (Working Product Promise)

The default experience should present one strongest recommended story direction,
explain why it fits, and show meaningful rejected alternatives. The author can
accept, modify, or override the recommendation. Auteur reduces uncertainty; it
does not remove authorial control.

## Explicit Ratification (Working Product Promise)

Identity-level recommendations require explicit author ratification before
Auteur compiles Structure from them. The guided interface may make acceptance
simple and plain-language, but recommendation must never silently become canon.

## Primary Entry Path (Working Product Promise)

The primary path begins with a premise, idea, character impulse, or desired
reader experience and guides the author toward `StoryIdentity`. Existing scenes
or manuscripts may become a later reverse-engineering or diagnostic workflow,
but they are not part of the primary entry promise.

## Product Success (Working Product Promise)

Auteur succeeds when the author understands and accepts a coherent story
direction, can explain the main commitments in ordinary language, and knows the
next useful creative decision. Artifact production and prose volume are not
sufficient measures of product success.

## Author-Facing Vocabulary (Working Product Promise)

The guided experience should present plain-language meanings first while keeping
canonical Auteur terms visible alongside them. For example: “Story Identity —
the commitments that define what this story is.” The product should translate
the domain model for beginners, not replace or rename the canonical model.

In the default flow, “story direction” or “story shape” may be used as the
plain-language explanation for the canonical narrative engine. “Narrative
engine” remains the canonical term in artifacts and advanced views.

The five-layer architecture remains canonical, but the beginner-facing flow
should disclose it progressively: Identity and lightweight Structure first,
followed by Realization and Expression when the author moves toward scenes and
prose.

## Diagnostic Presentation (Working Product Promise)

Structural diagnostics should be presented to creative beginners as plain-
language editorial guidance: what seems wrong, why it matters, and what repair
choices are available. The exact deterministic finding, severity, provenance,
and proposal lifecycle remain available for inspection. Guidance must not become
silent mutation or an unbounded judgment that the story is “good” or “bad.”

Unresolved structural errors block downstream prose generation by default;
warnings remain advisory and may be acknowledged. A deliberate author decision
to continue past a blocker must remain explicit and auditable.

AI may diagnose a structural issue and propose repair options, but it must not
apply a repair or rewrite an accepted story commitment without an explicit
author selection.

The repair lifecycle remains visible to the author: diagnose, propose, select,
apply, and ratify. The guided experience may simplify the presentation, but it
must not collapse these authority boundaries.

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

## Three Product Stages

1. **Narrative Engine**: The primary product scope. This stage locks the core
   answer, target experience, genre promise, protagonist want, resistance,
   conflict, stakes, change, ending shape, rejected directions, and rationale.
2. **Chapter Outline**: Optional downstream automation. This stage sequences the
   accepted story engine into chapters after the engine is locked.
3. **Prose**: Optional execution. This stage drafts words from the accepted
   structure and should not invent or silently rewrite the story engine.

## Modes

**Opinionated Mode** is the default. Auteur presents one recommended engine,
explains why it best serves the premise and genre promise, lists weaker rejected
directions, and asks the author to accept, modify, or switch modes.

**Experimental: Open-Ended Mode** is available for advanced authors who want to
explore multiple viable engines before locking the identity artifact. It is not
part of the standard MVP workflow and is hidden from default help output.

## Artifact Boundary

`story_identity.yaml` is the approval boundary. Recommendation rationale such as
`why_this_is_best`, `rejected_directions`, and `author_overrides` documents the
decision process, but only accepted identity fields compile into `blueprint.yaml`.

Deterministic structure diagnostics validate shape, completeness, and coherence.
They do not judge whether the story is good, and they must not call an LLM.

## Long-horizon product thesis

Auteur should build and maintain an explicit narrative architecture from
author intent, accepted direction, and accepted story history. That
architecture exists to externalize long-horizon narrative cognition: it helps
Auteur and the author understand the story beyond what either can reliably
hold in local working context.

The architecture may represent, where useful, narrative direction, characters
and trajectories, relationships, threads and arcs, commitments, setups and
payoffs, causal consequences, accepted current state, unresolved questions,
future intended direction, and other concepts that later prove useful. These
are examples of potentially useful architectural information. They do not imply
that every concept must become a new production domain object.

### Global Map

The Global Map is the author-inspectable whole-narrative projection of
relevant explicit narrative architecture. It answers questions such as:

- What is this story?
- Where is it going?
- What important trajectories exist?
- What has been established?
- What remains unresolved?
- What important relationships and consequences connect the story?

### Decision Map

The Decision Map is a relevance-selected projection of the Global Map for one
current creative decision. It does not expose the entire architecture by
default.

### Focus

Focus uses the Decision Map to help the author make one bounded current
creative decision.

Together:

```text
Explicit Narrative Architecture → Global Map → relevance projection → Decision Map → Focus → author decision → accepted architecture/state updated through existing authority boundaries
```

`Global Map` and `Decision Map` are product-facing projections and interaction
concepts. They are not new semantic layers and do not change the canonical
five-layer architecture (Ontology → Identity → Structure → Realization →
Expression) or its scope containers.

### Author authority

Generated architectural proposals, interpretations, and recommendations are not
authoritative merely because Auteur generated them. Author-declared
commitments and accepted narrative state become authoritative only through
existing explicit acceptance and ratification boundaries. This includes the
`story_identity.yaml` approval boundary, artifact-scoped acceptance operations
defined in the architecture constitution, and the canonical/derived/candidate
authority distinctions. Recommendation does not imply acceptance.

### Architectural-use principle

An architectural concept earns its place only by materially improving one or
more of: long-horizon reasoning, continuity, recommendation quality,
explanation, author orientation, decision-making, or narrative control. Do not
add architectural concepts merely because they are representable.
