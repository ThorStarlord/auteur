# Auteur Product Design Research

Status: active research. This document records open product-design questions;
it does not redefine Auteur's semantic architecture or runtime ownership.

## Settled product definition

The primary persona is a **creative beginner**: someone inexperienced in
long-form narrative craft, regardless of technical ability. Technical expertise
is not the defining audience.

Auteur's first valuable outcome is helping that author turn a premise, idea,
character impulse, or desired reader experience into a clear, accepted
whole-story direction. The default product posture is guided and opinionated:
one recommended direction, rationale, rejected alternatives, and explicit
author ratification.

The current CLI, YAML, JSON, and Markdown artifacts remain transparent advanced
surfaces. The default experience should progressively disclose the system and
translate canonical terms into plain-language explanations without renaming the
canonical model.

See [Opinionated Narrative Engine](../opinionated-narrative-engine.md) for the
current product-definition contract and [Narrative Architecture](../narrative-architecture.md)
for the canonical semantic model.

## Research boundary

This is product-design research, not a request to expand the narrative engine.
It should not introduce new semantic layers, make prose generation primary, or
silently change author authority rules.

The technical-expert persona is not an alternative product target. Research may
include technically experienced participants, but the question is whether the
creative-beginner experience works for them—not whether Auteur should be
positioned as a technical-author tool.

## Research tracks

### 1. Persona and job-to-be-done validation

Question: Does the settled creative-beginner persona have a clear, valuable job
for Auteur to perform?

Primary job-to-be-done: When I have a premise, character impulse, or desired
reader experience but not a coherent long-form plan, I want Auteur to guide me
to an accepted story direction and the next useful creative decision, so I can
move forward without learning narrative-engineering machinery first.

Hypothesis: This job is more valuable and more differentiating than immediate
prose generation or unrestricted brainstorming.

Evidence: the author's stated problem before the task, the outcome they seek,
whether the accepted direction changes their ability to continue, and whether
they can identify the next decision afterward.

Stop condition: do not broaden the primary job until repeated sessions show
that premise-to-direction work is insufficient to create meaningful value.

### 2. Premise-to-Identity onboarding

Question: Can a creative beginner move from a raw premise to an accepted Story
Identity without learning YAML, Pydantic, or Auteur's internal vocabulary?

Hypothesis: Guided questions, plain-language explanations, and one strong
recommendation will produce a clearer first session than direct artifact
editing.

Evidence: task completion, time to accepted identity, abandonment points, help
requests, and the author's ability to explain the accepted direction.

Stop condition: do not call onboarding validated until participants can explain
the main commitments and identify the next creative decision without reading
implementation details.

### 3. Progressive disclosure

Question: When should Identity, Structure, Realization, and Expression become
visible to the author?

Hypothesis: Identity and lightweight Structure should be sufficient for the
first session; Realization and Expression should appear when the author moves
toward scenes and prose.

Evidence: comprehension, unnecessary terminology exposure, task switching,
completion, and requests to bypass or skip sections.

Stop condition: retain only the minimum concepts needed for the current author
decision; defer concepts that do not change that decision.

Reconciliation: progressive disclosure constrains what the author must operate
during a local decision. It does not imply that Auteur's persistent
whole-story representation must itself remain minimal. The whole-story
representation (explicit narrative architecture / Global Map) may be richer than
the current UI projection (Decision Map / Focus). Showing the minimum for the
current decision is a presentation principle, not a cap on maintained
architecture.

### 4. Author-facing vocabulary

Question: Which plain-language explanations let authors understand canonical
terms such as Story Identity, Structure, proposal, diagnosis, and ratification?

Hypothesis: Showing a plain-language meaning beside the canonical term preserves
precision better than either raw technical vocabulary or replacing the domain
terms entirely.

Evidence: comprehension checks, paraphrase accuracy, misinterpretation rate,
and whether authors can distinguish a recommendation from a canonized decision.

Stop condition: no term is considered author-facing until a creative beginner can
explain what it controls and what it does not control.

### 5. Diagnostic comprehension and repair

Question: Can an author understand a structural diagnostic, its consequence, and
the available repair choices without reading validator output or source code?

Hypothesis: “What seems wrong / why it matters / choices available” is a useful
default presentation, provided the exact finding, severity, provenance, and
proposal lifecycle remain inspectable.

Evidence: correct explanation of the finding, choice quality, time to decision,
unnecessary overrides, and whether the author understands why a blocker stops
downstream prose.

Stop condition: do not simplify a diagnostic further if simplification causes
the author to lose the authority boundary or the reason for the finding.

### 6. Guided-surface choice

Question: Which guided surface best supports the settled product promise:
browser workflow, TUI, editor integration, or another interface?

Hypothesis: The best first surface is the one that minimizes cognitive load for
the premise-to-Identity task while keeping canonical artifacts inspectable.

Evidence: completion, comprehension, recovery from mistakes, author confidence,
artifact inspection, and continued use after the first session.

Stop condition: do not choose a surface from analogy or implementation
convenience alone; choose it after comparing the same task across candidate
surfaces.

### 7. Time-to-first-value

Question: How quickly can a creative beginner reach a meaningful outcome?

Primary measure: time from the first premise or creative impulse to an accepted
`StoryIdentity` and a clear next creative decision.

Secondary measure: time from an existing manuscript or scene to a useful
structural diagnosis. This is a later workflow and must not displace the
primary premise-to-Identity path.

Evidence: elapsed task time, abandoned steps, repeated questions, comprehension
at the end of the task, and whether the author continues independently.

Stop condition: do not claim product value from artifact creation alone; the
author must understand what was accepted and what to do next.

### 8. Architecture value and Global Map

Central question: What explicit narrative architecture does Auteur need in order
to make materially better long-horizon creative decisions than a
prompt/context-only system, while remaining understandable and maintainable for
the author?

Working hypothesis: Auteur may benefit from maintaining richer narrative
structure than must be shown during an individual local decision. A persistent
whole-story projection (Global Map) exposes that structure when useful, while a
relevance-selected projection (Decision Map) and bounded Focus progressively
disclose only the subset relevant to the current decision.

This track distinguishes internal representational value from author-facing
usability:

- **Internal representational value** — Does explicit architecture materially
  improve Auteur's reasoning?
- **Author-facing usability** — Can the author understand, inspect, correct, and
  benefit from the architecture?

Intended comparative experiment (same narrative state and same creative
decision wherever possible):

- **A. Prompt/context-only baseline** — a capable model receives ordinary
  story and context material and the current creative question without Auteur's
  explicit architectural substrate.
- **B. Current Auteur** — current accepted-history plus Repeated Map/Focus
  behavior.
- **C. Architecture-rich Auteur** — a richer experimental narrative architecture
  is available, from which Auteur derives Global Map → Decision Map → Focus.

Evidence dimensions to compare include: long-range setup/payoff awareness,
character-trajectory consistency, relationship continuity, causal consequences,
preservation of accepted direction, detection of obsolete or contradictory
conditions, relevance selection, recommendation quality, explanation quality,
useful novel connections, author orientation, maintenance burden, stale
architectural information, duplicate information, false precision, and
cognitive overload.

Complexity rule: do not optimize for minimal architecture or maximal
architecture. Seek the smallest architecture that produces materially better
long-horizon reasoning and author control.

For each candidate architectural concept, ask:

VALUE

- Did it change a recommendation?
- Did it detect a consequential problem?
- Did it improve an explanation?
- Did it help the author orient?
- Did it preserve an important long-range relationship?

COST

- Did the author or system have to maintain it?
- Did it become stale?
- Did it duplicate another representation?
- Did it create false precision?
- Did it make reasoning or presentation harder?

Suggested disposition:

- high value / low cost → strong production candidate
- high value / high cost → redesign or automate
- low value / low cost → probably unnecessary
- low value / high cost → remove or defer

Global Map and Decision Map in this track are product-facing projections and
interaction concepts, not new semantic layers, unless later evidence proves a
canonical architecture change is necessary. Experiment before
productionization: do not promote concepts to production architecture or UI
until the comparative experiment shows they earn their complexity. The
experiment must be rich enough for architectural information to actually affect
reasoning; a purely visual mockup test is insufficient.

Intended sequence after this thesis clarification: clarify product thesis →
define Architecture Value Experiment → create one experimental rich narrative
representation → create a disposable but functionally meaningful Global Map
prototype → compare A/B/C → identify which concepts earn their complexity →
promote only supported concepts into production architecture → implement
production Global Map → run author-facing comprehension and usability
validation.

## Shared experiment protocol

Use the same task sequence for each candidate experience:

1. provide a short premise or creative impulse;
2. guide the author to a recommended story direction;
3. ask the author to explain and ratify the commitments;
4. show one structural finding in plain language;
5. ask the author to choose a repair, preserve the intent, or explicitly
   override the blocker;
6. ask what the next useful creative decision is.

Record separately:

- system facts and task outcomes;
- author explanations and choices;
- observed confusion or friction;
- researcher interpretation;
- proposed product changes.

Do not treat a successful artifact write as proof of product usability. A
successful session requires both a valid artifact and author comprehension of
what was accepted, what remains provisional, and what happens next.

## Relationship to other research

Authority boundaries, evidence presentation, and human handoff are shared
themes with Sensemaking research. Sensemaking-specific questions—such as
repository uncertainty detection, coding-agent responsibility selection, and
repository memory—do not belong in this Auteur research document.
