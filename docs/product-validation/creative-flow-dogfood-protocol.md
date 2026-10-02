# Creative Flow Dogfood Protocol

**Status:** SELECTED PRODUCT-EVIDENCE RESPONSIBILITY  
**Tracking issue:** [#299](https://github.com/ThorStarlord/auteur/issues/299)  
**Primary evidence type:** real-author observation  
**Secondary evidence type:** repository/scripted mechanical verification  
**Product scope:** Beginner author journey and revision/recovery experience  
**Authority impact:** none; this protocol does not alter story authority

## Purpose

Determine whether Auteur's current Beginner experience preserves creative
momentum while retaining the existing explicit authority, provenance, staleness,
and revision guarantees.

The governing product hypothesis is **Freedom Before Commitment**:

> Maximize creative freedom while material is exploratory; maximize rigor once
> the author chooses to make it authoritative.

This protocol tests the experience before selecting another feature package.

It does **not** assume that Creative Scratch / Riff, a second authoring mode, a
new semantic layer, or a changed product thesis is necessary.

## Evidence boundary

Repository tests can establish:

- whether a workflow is reachable;
- whether a transition executes;
- whether accepted state remains intact;
- whether downstream artifacts stale or recover correctly;
- whether an exploratory or divergent artifact is preserved;
- whether the author has an executable recovery path.

Repository tests cannot establish:

- joy;
- cognitive burden;
- creative momentum;
- confidence;
- preference;
- whether a confirmation feels bureaucratic;
- whether advice feels inspiring;
- whether a real beginner wants to continue using the product.

Do not synthesize those subjective results from code inspection or scripted
personas.

## Governing comparison

Use the same author and the same or equivalent premise wherever possible.

```text
A — Markdown + capable general-purpose LLM
B — current Auteur
C — low-friction Auteur prototype only if A/B evidence warrants one
```

Condition C is not authorized by this protocol alone. It becomes eligible only
after A/B or direct dogfood evidence identifies concrete friction that a bounded
prototype can test more cheaply than a production change.

## Observation model

Classify every meaningful interaction:

### CREATIVE

The author creates, invents, explores, or discovers story material.

Examples:

- writes prose;
- invents a character;
- changes a relationship;
- proposes a twist;
- discovers a better motive while drafting.

### INSIGHT

Auteur materially improves the author's understanding of the story or craft.

Examples:

- reveals a consequence the author had not noticed;
- clarifies why a direction creates a stronger tension;
- helps the author see a continuity problem;
- makes an implicit story engine legible.

### NAVIGATION

The author moves to a useful surface or task without itself producing creative
or insight value.

Examples:

- opens a story;
- moves from review to drafting;
- opens optional supporting detail.

### ADMINISTRATIVE

The author manages or confirms system state without a distinct creative or
insight payoff.

Examples:

- confirms a recommendation solely so the workflow can continue;
- repeats acceptance for an already-understood commitment;
- resolves lifecycle/state terminology;
- performs bookkeeping required by the product rather than by the creative
  decision.

Do not treat ADMINISTRATIVE as automatically bad. Some explicit authority is
necessary. The question is whether its frequency and placement are
proportionate to the value it protects.

## Primary signals

Primary friction signal:

> **administrative interactions between CREATIVE or INSIGHT events**

Also record:

- time to first useful INSIGHT;
- time to first meaningful prose;
- longest run of ADMINISTRATIVE/NAVIGATION actions without creative payoff;
- hesitation moments;
- explicit requests to skip;
- "why do I need to decide this?" moments;
- terminology that requires explanation;
- author ideas with no natural place to go;
- product interruptions to a creative train of thought;
- recovery cost after changing accepted assumptions;
- moments where Auteur makes the author feel more capable or inspired;
- whether the author wants to continue the session voluntarily.

Raw click count is secondary. One high-value deliberate decision may be worth
many low-cost interactions; one unnecessary confirmation may be more harmful
than several useful choices.

## Run A — Naive Author

### Goal

Exercise current Auteur as a writer, not as a developer.

### Setup

1. Use the normal standalone/local author-facing entry.
2. Do not open the IDE, source files, tests, or internal artifacts during the
   creative session.
3. Start from a raw, imperfect premise that has not been pre-structured for
   Auteur.
4. Use the product's normal recommended path unless the author naturally wants
   to deviate.

### Endpoint

Attempt to reach a meaningful Chapter 1 prose candidate. A target near 1,500
words is useful for comparability but is not a product requirement.

### Observe

- when the first interesting story insight appears;
- when the author first wants to write prose;
- whether the product supports or delays that impulse;
- every authority confirmation and whether the author understands why it exists;
- whether recommendations feel specific to the story or generic;
- whether the author experiences Story Lenses/Direction/Structure as useful
  compression or as setup work.

### Result

Do not infer that slow time-to-prose is a defect by itself. Determine whether
the preceding work generated enough author-perceived value to justify the delay.

## Run B — Messy Writer

### Goal

Test story discovery that occurs through writing rather than before writing.

Use at least two of these disturbances:

1. **Spontaneous important character** — introduce a consequential character
   that was not represented in accepted planning.
2. **Discovered revelation** — reveal that an existing assumption about identity,
   motive, relationship, or antagonism is wrong.
3. **Contradictory exploratory scene** — deliberately write a promising scene
   that conflicts with accepted Structure or Direction.
4. **Orphan fragment** — create a line of dialogue, image, idea, or scene fragment
   with no known structural placement.

### Observe mechanically

- Is the material preserved?
- Is it rejected, blocked, or allowed to remain provisional?
- Does Auteur distinguish exploration from authority?
- Can consequences be inspected before any canonical change?
- Can the author continue without resolving everything immediately?
- What exact accepted dependencies become stale if the author later promotes
  the discovery?

### Observe experientially

- Does the author feel punished for improvising?
- Does the product demand classification before the author knows what the idea
  means?
- Does the recovery language lead with story consequences or with internal
  lifecycle terminology?
- Does the writer want to leave Auteur for a blank editor?

## Run C — Change My Mind

### Goal

Test whether correct revision mechanics also produce acceptable subjective
recovery cost.

After accepted upstream work and at least one downstream artifact exist, make a
material change such as:

- dark mystery -> black comedy;
- protagonist's primary desire changes;
- presumed antagonist becomes an ally or family member;
- relationship premise changes;
- key revelation moves earlier/later and invalidates prior Structure.

### Observe mechanically

Record:

- which artifacts stale;
- which remain reusable;
- which proposals/reviews are required;
- whether prior work is preserved;
- whether any silent canonical rewrite occurs;
- whether the current product provides an executable recovery path.

### Observe experientially

Record:

- number of author decisions required to regain momentum;
- whether the author can understand the consequences before committing;
- whether the product suggests repair without acting as an overbearing editor;
- whether recovery feels proportional to the magnitude of the change;
- whether the author would have found it easier to abandon the project state and
  return to a plain document.

## Run D — Competitive baseline

### Goal

Determine whether Auteur's additional structure produces writer-visible value
over the practical substitute: a plain document plus a capable general-purpose
LLM.

### Conditions

Use a comparable creative objective in both conditions.

#### A — Markdown + general-purpose LLM

Provide normal story/context material and the current creative question. Do not
recreate Auteur's internal state machine manually.

#### B — Current Auteur

Use the normal product path and existing accepted-history/continuity machinery.

### Compare

Do not select a winner by a numeric score. Compare concrete evidence:

- ability to recover consequential prior decisions;
- continuity across the session;
- awareness of setups/payoffs and downstream consequences;
- relevance of advice;
- revision safety;
- preservation of author ownership;
- administrative burden;
- ability to carry uncertainty;
- number and quality of useful novel connections;
- desire to continue.

The comparison is evidence about the product, not proof that immediate prose
generation should replace the current product thesis.

## Friction classification

For the **first material experiential friction**, classify the owning layer
before proposing a fix:

- **UX / presentation** — the capability exists but is confusing, overexposed,
  poorly sequenced, or too ceremony-heavy;
- **workflow** — existing capabilities cannot be traversed naturally from the
  author's current creative action;
- **craft knowledge** — guidance is too generic or thin to create useful insight;
- **domain model** — recurring exploratory state cannot be represented safely
  without forcing a false canonical choice;
- **infrastructure** — provider, packaging, latency, portability, or reliability
  blocks the experience.

Prefer the earliest sufficient layer.

```text
presentation
-> workflow connection
-> reusable craft knowledge
-> existing domain model
-> new domain concept only if earlier layers cannot express the need
```

## Intervention gate

After evidence returns, choose exactly one:

### CURRENT_FLOW_ACCEPTABLE

No material experiential friction warrants repository change.

Do not invent a feature to keep the roadmap moving.

### BOUNDED_INTERVENTION_SELECTED

Select the smallest change that directly addresses observed friction.

Examples may include copy, sequencing, progressive disclosure, deferred
confirmation, a provisional-input affordance, or a bounded exploratory surface.

### CREATIVE_SCRATCH_SPIKE_WARRANTED

Use only when evidence shows that:

1. the author needs to create material before knowing its canonical role;
2. the current surface imposes recurring friction;
3. presentation/workflow repair without an exploratory surface is insufficient;
4. the spike can remain noncanonical and reversible;
5. no new semantic layer is required to learn from it.

A possible spike shape is:

```text
raw thought / dialogue / prose / scene / contradiction
-> preserved as provisional exploration
-> no canonical implication
-> Auteur may later surface consequential discoveries
-> author explicitly chooses whether to incorporate any of them
```

This is an experiment shape, not a preselected production architecture.

### THESIS_REVIEW_REQUIRED

Use only if repeated evidence challenges the current organizing premise that
premise-to-direction guidance should precede or dominate the first-value
experience.

Do not revise MISSION/PRD implicitly from one frustrating session.

### EXTERNAL_OR_HUMAN_EVIDENCE_BLOCKED

Use when the required subjective evidence cannot currently be obtained.

Do not substitute agent simulation and call the question answered.

## Evidence record template

For each run record:

```text
repository_sha:
participant:
condition:
premise:
start_time:
endpoint:
time_to_first_insight:
time_to_first_prose:

interaction_sequence:
  - class: CREATIVE | INSIGHT | NAVIGATION | ADMINISTRATIVE
    surface:
    action:
    author_observation:
    system_fact:

first_material_friction:
classification:
mechanical_recovery:
subjective_recovery_cost:
authority_preserved:
data_loss:
author_wants_to_continue:
claims_established:
claims_not_established:
```

Keep system facts, observed author statements/behavior, researcher
interpretation, and proposed changes separate.

## Relationship to existing qualification work

This product-evidence lane runs independently from:

- #295 formal L3 requalification;
- #218 Episode 1 Direction cross-platform/verification/wheel qualification and
  its own bounded human-validation questions;
- #272 branch-protection administration.

It does not close, weaken, or bypass those responsibilities.

Likewise, a green L3 or Release Qualification run does not establish the human
experience claims in this protocol.

## Stop rule

Stop the product-evidence episode when:

- the first material friction has enough evidence to select a bounded
  intervention;
- current flow is acceptable at the tested claim level;
- Level-4 thesis review is genuinely warranted; or
- the required human evidence is unavailable.

Do not continue brainstorming additional features after one bounded
responsibility is selected.
