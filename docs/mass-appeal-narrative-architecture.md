# Mass-Appeal Narrative Architecture (MANA)

**Status:** experimental cross-cutting analytical contract  
**Scope:** audience-effect analysis across Auteur's existing narrative architecture  
**Authority:** derived / noncanonical; does not add a semantic layer, validator, score, or acceptance path

## Purpose

Mass-Appeal Narrative Architecture (MANA) is Auteur's optional audience-side view
of an existing story.

Auteur's canonical semantic architecture answers:

```text
Identity -> Structure -> Realization -> Expression
what it is -> how it is planned -> what happens -> how it is rendered
```

MANA asks a different question:

> Given the narrative evidence that currently exists, what audience-facing
> effects are structurally supported, where is there a meaningful tension or
> gap, and which claims are still too early to assess?

MANA is intentionally probabilistic and diagnostic in spirit. It does **not**
claim that satisfying a set of conditions causes bestseller status, predicts
sales, proves artistic quality, or establishes that real readers will respond in
a particular way.

## Architectural placement

MANA is **not** Layer 5.

It is a cross-cutting projection comparable in placement to diagnostics,
editing, provenance, and orchestration:

```text
                         MANA
                           |
                           | observes
                           v
Ontology -> Identity -> Structure -> Realization -> Expression
             |            |             |             |
          promise       planning      events/state    language
```

Canonical narrative state remains owned by the existing five semantic layers.
A MANA report never silently mutates StoryIdentity, Structure, Realization,
Expression, or accepted author decisions.

## Audience-effect dimensions

The initial vocabulary is:

1. **Narrative legibility** — can the intended audience form a usable model of
   the story's central situation, governing engine, and relevant expectations?
2. **Motivational attachment** — is the value being pursued, protected,
   threatened, lost, or transformed structurally legible?
3. **Predictive engagement** — does the design give the audience enough
   information to form expectations while preserving meaningful uncertainty?
4. **Consequential progression** — do major attempts and outcomes change later
   options, beliefs, costs, or pressures rather than merely repeat obstacles?
5. **Grounded credibility** — do realized events and character responses remain
   causally, psychologically, and world-rule coherent?
6. **Emotional legibility** — is the intended reader-facing emotional
   significance structurally explicit enough to be followed?
7. **Affective commitment** — does Expression grant intended important emotions
   sufficient dignity, or does the rendering unintentionally deflate them?
8. **Payoff architecture** — are major promises, expectations, revelations, or
   transformations designed to discharge in inspectable ways?
9. **Memorability** — what completed-work elements function as likely retrieval
   anchors after consumption?
10. **Transmission** — what completed-work elements can be compressed into
    compelling, accurate social descriptions without flattening the work?

These dimensions are analytical vocabulary, not required story ingredients.
Different genres, modes, audiences, and authorial goals may deliberately use
very different settings on each dimension.

## Audience causal model

MANA's organizing hypothesis is:

```text
comprehension
-> motivational relevance
-> prediction / uncertainty
-> consequential change
-> emotional experience
-> payoff
-> memory
-> transmission
```

This is a **theoretical engineering model**, not an experimentally established
universal law. It exists to connect otherwise separate Auteur concepts from the
audience side.

In particular:

- genre promise is not the same thing as mass appeal;
- tension is not the same thing as predictive engagement;
- setup/payoff tracking is not proof that an audience noticed the setup;
- emotional design is not proof that realized prose produces the intended
  emotion;
- conceptual compressibility is not a guarantee of social sharing.

## Relationship to existing Auteur concepts

MANA consumes existing narrative evidence rather than duplicating it.

### Story Opportunity Discovery and Premise Fitness

MANA is downstream from the upstream creative-search and premise-fit contracts.

```text
Story Opportunity Discovery
-> working premise / Discovery Brief
-> optional Premise Fitness
-> Story Discovery
-> selected narrative architecture
-> optional MANA audience-effect analysis
```

The responsibilities are different:

- **Premise Fitness** asks whether a working premise is capable, sustainable, and
  economical for its intended genre, experience, scope, complexity, and posture.
- **MANA** asks what audience-facing effects are currently supported by the
  narrative evidence that actually exists.

Therefore MANA must not:

- turn Premise Fitness into a popularity score;
- infer current market demand from premise fit;
- re-rank Story Discovery candidates automatically;
- duplicate Premise Fitness runway / scope-fit diagnostics;
- treat a strong audience-effect hypothesis as evidence that a premise is
  commercially viable.

When a Post-Discovery Fitness Delta exists, MANA may consume the selected
architecture that produced it, but it owns a different question:

```text
fitness delta
= what the architecture changed about premise fit

MANA
= what audience effects the current architecture supports / leaves uncertain
```

Both remain derived and noncanonical.


| MANA concern | Existing Auteur evidence |
| --- | --- |
| Narrative legibility | genre, audience, author intent, governing engine |
| Motivational attachment | want, stakes, target experience |
| Predictive engagement | resistance, conflict, pressure/tension planning, revelation structure |
| Consequential progression | structural change, reversals, event causality |
| Grounded credibility | Realization state, continuity, causal/state diagnostics |
| Emotional legibility | Target Experience, emotional trajectory, aesthetic framing |
| Affective commitment | Expression choices: voice, diction, dialogue, pacing, tonal deflation |
| Payoff architecture | setup/payoff intentions, climax mechanics, accepted genre promises |
| Memorability | completed realized moments, motifs, transformations, images, revelations |
| Transmission | completed-work concept compression and retellable hooks |

### Story Lens

MANA does not create a sixth default Beginner Story Lens.

The existing **Reader Experience** lens may later surface selected MANA insights
when they are helpful and supported by the current evidence. The Story Lens
first-screen contract remains a beginner orientation surface rather than a
commercial-quality dashboard.

### Commercial clarity

Auteur's existing `commercial_clarity` Story Discovery lens asks for the
clearest market and genre promise. MANA is broader.

```text
commercial_clarity
~= recognizable market / genre promise

MANA
= cross-layer audience-effect analysis
```

Neither should replace the other.

## Epistemic classification

MANA must distinguish four bases:

- **E — Empirical:** supported reasonably directly by empirical research.
- **T — Theoretical:** a serious explanatory model consistent with evidence but
  not established as a universal causal law.
- **H — Heuristic:** craft knowledge useful for design or diagnosis.
- **P — Project evidence:** concrete evidence from the current story/project.

The current deterministic implementation primarily emits **P + H** findings.
It does not attach "empirical" to a rule merely because a related research
literature exists.

A future research-backed knowledge pack may attach E/T references, but the
runtime must preserve the distinction between evidence about humans in general
and evidence about this particular story.

## Stage-sensitive evidence

MANA must not judge dimensions before the owning narrative evidence exists.

| Available evidence | Reasonable MANA claims |
| --- | --- |
| **Identity** | concept/genre/audience legibility, early motivational framing, reader promise |
| **Structure** | predictive architecture, pressure/escalation planning, planned payoff, emotional progression |
| **Realization** | event-level causality, consequence, behavioral/world-rule credibility |
| **Expression** | prose-level clarity, affective commitment, tonal deflation, sensory grounding |
| **Completed work** | payoff completion, memory anchors, conceptual compression, transmission potential |

The current implementation accepts a `StoryBlueprint`. Therefore it can infer
only **Identity** or **Structure** evidence. Later-stage dimensions are returned
as `not_yet_assessable` instead of being guessed.

```text
missing evidence
!= negative verdict

later-stage question
!= permission to infer from earlier-stage proxies
```

## Diagnostic states

MANA uses qualitative finding states:

- `supported` — current project evidence structurally supports the dimension;
- `tension` — useful evidence exists but there is a material unresolved
  audience-effect tension;
- `unestablished` — the current owning stage is available but the dimension is
  not established there;
- `not_yet_assessable` — the required later-stage evidence does not yet exist.

These are **not quality grades**.

## No aggregate score

MANA must never produce:

- a mass-appeal percentage;
- a bestseller probability;
- a weighted quality score;
- a commercial grade;
- an automatic candidate leaderboard;
- an automatic Story Discovery winner.

The earlier conceptual shorthand

```text
legibility x care x tension x emotion x payoff x memory x transmission
```

is a mental model for bottlenecks, not an executable scoring equation.

Auteur's existing rule remains controlling:

> deterministic contract fit is compliance evidence, not artistic-quality
> ranking.

## Theory, Diagnostic, Guidance

MANA has three responsibilities.

### 1. MANA Theory

Defines audience-effect vocabulary, epistemic boundaries, and relationships to
Auteur's existing semantic concepts.

Theory does not mutate projects.

### 2. MANA Diagnostic

Reads current evidence and produces a typed, derived report.

Current implementation:

```python
from auteur.audience_effects import analyze_audience_effects

report = analyze_audience_effects(blueprint)
```

Author-facing read-only CLI:

```text
auteur reasoning audience blueprint.yaml
auteur reasoning audience blueprint.yaml --json
```

The command prints a derived report only. It writes no narrative artifact and
crosses no acceptance boundary.

The report contains:

- available evidence stage;
- one finding per audience-effect dimension;
- concrete project evidence;
- limitations / claim ceiling;
- epistemic basis;
- noncanonical guidance for currently assessable gaps.

### 3. MANA Guidance

Guidance suggests bounded ways to strengthen an identified audience-effect
tension while preserving authorial intent.

Guidance is:

```text
DERIVED / NOT CANON
```

It cannot edit the Blueprint, accept a proposal, change StoryIdentity, or become
an automatic recommendation winner.

## Initial implementation boundary

The first implementation slice deliberately does **not**:

- parse manuscripts to estimate memorability;
- classify sincerity from prose;
- claim reader transportation;
- infer social sharing probability;
- call an LLM;
- add a new canonical artifact;
- add a new semantic layer;
- add a MANA validator;
- add a Beginner dashboard score;
- modify Story Discovery winner selection.

Those are future possibilities only if later evidence justifies a bounded
extension.

## Design principle

MANA should be used to ask:

> What audience-facing effect is this existing narrative architecture trying to
> produce, what current evidence supports that effect, and what can we not yet
> know?

It should not be used to ask:

> How can Auteur mathematically prove this story will be popular?
