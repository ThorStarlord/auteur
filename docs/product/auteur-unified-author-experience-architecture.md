# Auteur Unified Author Experience Architecture

**Date:** 2026-10-03  
**Role:** high-order product / UX system architecture  
**Scope:** author-facing experience across premise, shaping, drafting, discovery, revision, continuity, and long-form completion  
**Source baseline:** integrated Beginner candidate in PR #309 plus existing semantic/authority contracts  
**Authority:** this document unifies product interaction rules. It does **not** create a sixth semantic layer, a parallel story authority, or a new acceptance system.

## Why this document exists

Auteur already has substantial internal capability:

- Story Discovery and Story Identity;
- whole-story Structure;
- Realization / story-state handling;
- Expression drafting and Chapter / Book acceptance;
- impact, review, convergence, planning, and provenance;
- Book reconciliation and long-horizon continuity;
- Beginner projections and author-facing orchestration.

Recent product work also added:

- a compressed shape-first Beginner flow;
- plain-language front-door vocabulary;
- a two-input Quick Draft path;
- post-draft creative-discovery reconciliation;
- exact-draft review freshness;
- explicit carry-forward from exploratory prose into story shaping.

Each of those changes is locally coherent. The next product risk is different:

> **locally correct flows can still form a systemically disjointed author experience.**

This document therefore defines the author-level system that should remain coherent from the first idea through Book completion.

It is intentionally a synthesis layer over existing authorities, not another authority.

---

# 1. Evidence and requirement status

Every consequential statement in this architecture should be understood through one of these statuses.

| Status | Meaning |
| --- | --- |
| **ESTABLISHED PRODUCT PRINCIPLE** | Repeatedly selected and already reflected in durable product/authority contracts. |
| **CURRENT SYSTEM CONTRACT** | Mechanically implemented or already required by an owning architecture/workflow. |
| **SELECTED EXPERIENCE DIRECTION** | Chosen high-order product direction for the next UX architecture, subject to evidence. |
| **WORKING UX HYPOTHESIS** | Plausible experience design that must not be mistaken for validated human preference. |
| **OPEN EVIDENCE QUESTION** | Requires real-provider or real-author evidence before stronger product commitment. |

The repository must not silently promote a working UX hypothesis into a canonical product requirement merely because it is coherent.

---

# 2. Unified author mental model

## 2.1 The mental model Auteur should teach

A beginner should be able to understand Auteur approximately like this:

```text
1. I can explore freely.
2. I decide what matters to my story.
3. Auteur remembers the decisions I actually keep.
4. Auteur can help shape those decisions into a coherent story.
5. Writing is allowed to discover things the plan did not know.
6. When that happens, Auteur asks what I want to keep or change.
7. I can change my mind deliberately without losing the story.
8. Auteur helps the long story remember itself.
```

This is the **author mental model**.

It is intentionally smaller than the machine model.

The author should not need to hold this internal model in working memory:

```text
Ontology
-> Identity
-> Structure
-> Realization
-> Expression
-> proposals
-> staleness
-> provenance
-> review lifecycle
-> reconciliation
-> convergence
-> Book ownership
-> Series projections
```

Those distinctions remain important internally. Product quality depends on **absorbing their complexity without erasing their semantic boundaries**.

## 2.2 The primary product promise

**ESTABLISHED PRODUCT PRINCIPLE**

```text
maximum author control over meaning
+
minimum author administration of machinery
```

A useful restatement is:

> **The author decides the story. Auteur manages the machinery required to realize, remember, and revise those decisions.**

## 2.3 The freedom / authority relationship

Creative freedom and strict authority are not opposites.

Auteur should separate:

```text
freedom to explore
from
authority to make exploration durable
```

Therefore:

```text
author can write something
!=
machine must already have modeled it

machine can infer something
!=
author has accepted it

prose can discover something
!=
all upstream layers must change

accepted story fact
!=
every previous plan was wrong
```

The author should experience this distinction as **freedom first, commitment when useful**, not as a sequence of governance forms.

---

# 3. Author-facing concepts versus internal machinery

The default Beginner product should primarily use concepts such as:

| Author concept | Meaning |
| --- | --- |
| **Story idea** | What the author is imagining now. |
| **What Auteur sees** | A working interpretation, not accepted truth. |
| **Direction** | One plausible way the story could develop. |
| **Story core** | The commitments that define what story this is becoming. |
| **Story shape** | The broad organization that helps the story work. |
| **First-scene intent** | What the author wants to happen now. |
| **Working draft** | Prose that can be edited freely. |
| **Accepted story** | Material the author has deliberately kept through the relevant owner. |
| **Story updates** | New material or changed intent that may need to be remembered elsewhere. |
| **Continuity** | What the story has already established and what future writing should know. |
| **Deep details** | Advanced diagnostics, evidence, provenance, and internal state when wanted. |

Internal names remain valid implementation vocabulary, but they should appear only when they materially help an advanced user understand or control the system.

---

# 4. Auteur is not one linear funnel

A fixed progression such as:

```text
Scratchpad -> Structural Guide -> Compiler
```

is too rigid as the author mental model.

Those are better understood as **capability depths** that can become foregrounded when useful.

A writer may move:

```text
deep story shaping
-> free drafting
-> continuity review
-> free rewriting
-> structural revision
-> drafting again
```

without violating the product model.

The selected architecture therefore uses four contextual capability modes.

## 4.1 Creative mode

**Purpose:** momentum, exploration, prose, rough intent.

Typical surfaces:

- Quick Draft;
- editable working prose;
- first-scene intent;
- free rewrite;
- lightweight “what did we discover?” reflection.

The system should minimize approval/admin activity here.

## 4.2 Guidance mode

**Purpose:** understand and shape what the story is becoming.

Typical surfaces:

- premise interpretation;
- Story Lenses;
- Direction;
- Story core;
- Story shape;
- recommended planning;
- explanation and trade-offs.

The system should offer strong defaults without silently deciding meaning.

## 4.3 Continuity mode

**Purpose:** help the story remember itself and make consequences visible.

Typical surfaces:

- accepted prior Chapter context;
- story updates;
- creative-divergence review;
- stale-review detection;
- change consequences;
- whole-book orientation;
- continuity warnings;
- unresolved story updates.

Continuity should feel like assistance with remembering and consequences, not database maintenance.

## 4.4 Deep-control mode

**Purpose:** advanced inspection and deliberate intervention.

Typical surfaces:

- raw artifacts;
- provenance;
- diagnostics;
- internal proposals;
- step-by-step planning;
- ownership / authority detail;
- advanced CLI;
- exact continuity evidence.

Deep control is always available, but Beginner flows should not require it by default.

---

# 5. Progressive-disclosure triggers

Modes should surface because of **author need**, not merely because the repository has a subsystem.

## 5.1 Creative-mode triggers

Foreground creative mode when:

- the author explicitly chooses **Start writing now**;
- the author has a concrete scene impulse stronger than a planning need;
- the author is rewriting existing prose;
- the author wants to explore an uncertain idea before committing.

## 5.2 Guidance-mode triggers

Foreground guidance when:

- the author chooses **Explore this story**;
- the premise is too ambiguous for a useful next commitment;
- the author asks what the story currently is;
- the author asks why a draft or plot is not working;
- the author asks for pacing, direction, or structural help;
- the author chooses **Shape this story** after Quick Draft.

## 5.3 Continuity-mode triggers

Foreground continuity when:

- accepted prose introduces material not represented elsewhere;
- the author changes an accepted premise or long-range intent;
- future planning would be materially affected by unresolved story updates;
- accepted Chapters begin to disagree with current Structure or state;
- whole-book or Series consistency matters to the next decision;
- review evidence has become stale.

## 5.4 Deep-control triggers

Expose deep control when:

- the author explicitly asks for more detail;
- a conflict cannot be explained adequately in story language alone;
- advanced users need artifact/provenance control;
- a recovery or debugging situation requires exact technical evidence.

## 5.5 Trigger law

**SELECTED EXPERIENCE DIRECTION**

> **Complexity should appear in response to a problem the author can already perceive.**

Avoid:

```text
subsystem exists
-> surface subsystem
```

Prefer:

```text
author encounters meaningful story need
-> surface the relevant capability
-> keep machinery behind progressive disclosure
```

---

# 6. Two entry tempos, one product

Auteur currently has two legitimate starting tempos.

## 6.1 Shape first

```text
story idea
-> Explore this story
-> what Auteur sees
-> Direction
-> Story core
-> Story shape
-> Chapter launch
-> draft
```

Use when the author wants understanding and shaping before prose.

## 6.2 Write first

```text
story idea
+ first-scene intent
-> Start writing now
-> inferred provisional setup
-> working scene
-> edit freely
-> What did we discover?
-> explicitly select anything worth carrying forward
-> Shape this story
```

Use when the author has enough scene-level intent to learn through writing.

## 6.3 Convergence rule

These must **converge**, not become separate products.

Both paths should eventually produce the same kind of durable story state:

```text
author intent
-> explicit meaningful commitments
-> accepted owners
-> reusable accepted context
-> drafting
-> discoveries / consequences
-> explicit story updates
-> future planning
```

Quick Draft must not create a shadow Story Identity or shadow canon.

Shape-first must not force every reversible planning seam to become a separate visible approval.

---

# 7. The recurring author loop

The high-order product loop is:

```text
IMAGINE
-> UNDERSTAND when useful
-> CHOOSE what matters
-> WRITE
-> DISCOVER
-> UPDATE the story when useful
-> CONTINUE
```

Internally, this may traverse many specialized systems.

The author should primarily experience:

```text
What am I trying to make?
What does Auteur understand?
What do I want to keep?
What happens next?
What changed while I was writing?
What does the story need to remember?
```

That recurring loop is more important than any individual page or command.

---

# 8. Author intent to machine state

## 8.1 Intent is not a schema-editing task

The author should normally state intent in story language:

- “Make her distrust him sooner.”
- “Sister Beatrice matters now.”
- “I want this to feel warmer.”
- “Move the revelation earlier.”
- “I changed my mind; the antagonist is actually an ally.”

Auteur is responsible for translating that into:

```text
affected story meaning
-> likely semantic owners
-> consequences
-> bounded proposals / revisions
-> explicit owner transitions where required
```

The author should not have to know which internal layer owns the consequence before stating the change.

## 8.2 Intent translation must remain inspectable

Machine translation of intent is still inference.

Therefore the product must preserve:

- what the author literally asked;
- what Auteur inferred would need to change;
- what has actually been accepted;
- what remains only proposed;
- what consequences are expected.

---

# 9. Creative discovery propagation

## 9.1 Core law

**ESTABLISHED PRODUCT PRINCIPLE**

> **Unexpected prose is evidence before it is an error.**

## 9.2 Lowest-sufficient-owner rule

A discovery should propagate only as far upward as required to preserve meaning and future coherence.

Examples:

```text
new side character
-> realized / continuity state
-> maybe Structure if structurally consequential
-> usually not Story core

new location
-> realized / continuity state
-> maybe Structure if it changes the chapter path

new relationship fact
-> realized / continuity state
-> maybe Story core if it changes the defining story promise

changed central premise
-> likely Story core / Identity consequence
```

Avoid:

```text
new thing appeared
-> reopen every layer
```

## 9.3 Accepted prose is usable context even before every model is synchronized

**SELECTED EXPERIENCE DIRECTION**

An accepted Chapter Expression is authoritative for that accepted prose.

Future planning should be able to consume accepted prior Chapter outcomes as context even while separate upstream/downstream synchronization proposals remain unresolved.

This prevents the product from forcing:

```text
write
-> discover
-> stop writing
-> finish all model maintenance
-> only then continue
```

Instead:

```text
accepted prose
-> future planning may know what actually happened
+
pending story updates remain visible
-> specialized owners can be reconciled explicitly
```

This rule must not silently mutate other owners.

It is a context-composition rule, not a new canon system.

---

# 10. The Sister Beatrice system test

A concrete creative event is more useful than reasoning about subsystems in isolation.

Assume the current plan contains:

- Detective Miller;
- Suspect Vance;
- a precinct interrogation.

The writer drafts:

> Sister Beatrice leads Miller to an abandoned seaside convent and reveals that Vance stayed there.

The intended systemic journey is:

```text
1. Working prose contains Sister Beatrice + convent
2. Exact draft bytes become the review subject
3. Auteur notices possible new material / divergence
4. Writer chooses:
   a. Keep draft & update story
   b. Keep as intentional divergence
   c. Revise to match plan
5. If kept, Chapter Expression crosses the existing Chapter acceptance owner
6. New material remains explicit evidence for lower owning systems
7. Suggested updates are routed to the lowest sufficient owner
8. Future Chapter planning can use the accepted Chapter outcome as context
9. Unresolved synchronization remains visible as story-update work, not hidden drift
10. Whole-book / long-horizon continuity reasons from accepted sources and explicit pending changes
```

The author-facing story is much simpler:

```text
You invented something new.
Do you want to keep it?
If yes, Auteur will remember where it matters.
```

---

# 11. Long-form evolution: Chapter 1 to Chapter N

## 11.1 Future planning should not reset context

Each new Chapter should receive composed context from:

- accepted Story core;
- accepted Story shape / Structure;
- accepted prior Chapter outcomes;
- accepted realized facts/state;
- relevant continuity context;
- unresolved but explicit story-update signals when they materially affect planning.

It should **not** treat the original premise as if nothing has happened since Chapter 1.

## 11.2 Accepted prose and planning may diverge

That divergence is not automatically failure.

Use this distinction:

| Situation | Product response |
| --- | --- |
| Prose adds compatible detail | preserve momentum; offer lightweight story update |
| Prose realizes plan differently but compatibly | show meaningful difference; author decides whether planning needs update |
| Prose contradicts accepted fact | require explicit story decision |
| Structure becomes obsolete because repeated prose evolves elsewhere | propose Structure change; do not force prose back into old plan |
| Draft is exploratory / rejected | do not contaminate accepted future context |

## 11.3 Long-form continuity principle

> **Future guidance should follow the accepted story that was actually written, not merely the plan that once predicted it.**

Planning remains valuable because it provides intention and constraints.

Accepted realization/expression remains valuable because it records what actually happened.

Auteur should reason over both rather than pretending they cannot diverge.

---

# 12. Change-my-mind architecture

Changing intent is a first-class author action, not an error condition.

## 12.1 User-facing flow

```text
author states new intent in story language
-> Auteur explains the meaningful consequences
-> unchanged commitments remain untouched
-> affected owners receive proposed changes
-> author confirms consequential changes
-> dependent planning is refreshed
-> writing resumes
```

## 12.2 Do not make the author reconstruct the dependency graph

Avoid:

```text
change Story Identity field
then Structure
then Chapter Plan
then Scene Plan
then Bible
...
```

Prefer:

> “Changing the antagonist into an ally affects the story core, three planned confrontations, and the next Chapter. Here is what Auteur proposes to update.”

The author chooses meaning; the system handles dependency traversal.

## 12.3 Change direction versus revise history

The product should distinguish:

- **change from here forward** — prior accepted events remain true, future meaning changes;
- **revise earlier story** — accepted earlier material itself changes.

Those have different consequences and should not be collapsed into one generic “reconcile” action.

---

# 13. Whole-book and long-horizon interaction

Book reconciliation, Series continuity, and global maps should function as **continuity intelligence**, not as a second authoring product.

The Beginner experience should surface them through questions such as:

- “Does the Book still match the story you are writing?”
- “What changed since the current Book plan?”
- “Which established facts matter to the next Chapter?”
- “Where are two accepted parts of the story now in tension?”

Avoid making the author manually traverse Book reconciliation state merely because the backend requires it.

The underlying Book/Series authorities remain unchanged.

---

# 14. Machine-complexity absorption rules

These rules apply across the product.

## 14.1 Lead with story consequence

Prefer:

> “This Chapter introduces a new place.”

before:

> “Realization reconciliation proposal available.”

## 14.2 Bundle reversible machinery

If several internal operations are reversible execution scaffolding and represent one coherent author intent, the product may bundle them behind one author-facing action.

## 14.3 Preserve meaningful commitments

Do not bundle distinct story-meaning choices merely to reduce click count.

## 14.4 Infer provisionally

If the machine needs a value that the author has not established, prefer:

```text
unknown / provisional
```

over invented commitment.

## 14.5 Do not ask twice for the same authorship

If prose already contains a discovery and the author explicitly selects it for shaping, do not force them to retype it into another model.

## 14.6 Route to the lowest sufficient owner

Do not reopen Story core merely because a lower layer can represent the new information.

## 14.7 Compose specialized systems

Beginner and other projections may synthesize many systems into one coherent surface while leaving their ownership intact.

## 14.8 Keep escape hatches

Defaults must not become prisons. Deep inspection and step-by-step control remain available.

## 14.9 Preserve recoverability

Exploratory work should survive refresh/reopen and should not disappear merely because it is provisional.

## 14.10 Make uncertainty visible without making it burdensome

The product may say:

> “Auteur is not sure yet.”

without forcing an immediate decision unless uncertainty blocks meaningful progress.

---

# 15. Systemic UX antipatterns

## 15.1 Machine-state leakage

Internal lifecycle language becomes required author vocabulary.

Example:

```text
"reconciliation required"
```

instead of:

```text
"Your draft introduced something new."
```

## 15.2 Approval laundering

Internal seams become multiple visible confirmations even though the author already expressed one coherent intent.

## 15.3 Premature commitment

The author is required to choose before enough creative evidence exists.

## 15.4 Hidden commitment

A machine inference becomes durable merely because an internal schema needed a field.

## 15.5 Duplicate authorship

The writer establishes something in prose, then has to manually enter it again in planning/state.

## 15.6 Layer echo

The same semantic decision is independently presented in Story core, Structure, Chapter Plan, Scene Plan, and continuity without explaining that these are consequences of one earlier choice.

## 15.7 State-machine-shaped UX

The user journey reflects backend transition topology rather than creative intent.

## 15.8 Reconciliation tax

Every exploratory change creates enough maintenance ceremony that the writer learns not to experiment.

## 15.9 Stale evidence masquerading as current evidence

A review or recommendation is presented as current after the underlying author material changed.

## 15.10 Inference leakage

Generic defaults introduced for scaffolding appear in prose or later planning as though the author established them.

## 15.11 Entry-path bifurcation

Shape-first and write-first evolve into two incompatible products that cannot rejoin one accepted story state.

## 15.12 Long-form context reset

Each new Chapter behaves as if the original premise and old plan matter more than accepted events that actually happened in prior Chapters.

---

# 16. Cross-system product contracts

## 16.1 Beginner is a projection/orchestration layer

It may compose:

- Discovery;
- Identity;
- Structure;
- Realization;
- Expression;
- review;
- impact;
- continuity;
- Book/Series orientation.

It never becomes a parallel authority.

## 16.2 Projection is not mutation

Showing a likely next action, likely consequence, or possible discovery does not execute or accept it.

## 16.3 Inference is not acceptance

All inferred planning, Quick Draft scaffolding, Story Lens analysis, and discovery detection remain provisional/derived until the relevant existing owner accepts a change.

## 16.4 Accepted Expression is not automatic upstream mutation

Accepted prose may provide downstream context and evidence while upstream synchronization remains explicit.

## 16.5 Context must preserve provenance

When one subsystem passes context to another, the recipient should be able to distinguish:

- author-explicit input;
- accepted story state;
- accepted prose/outcome;
- machine inference;
- author-selected discovery;
- pending proposal;
- stale evidence.

## 16.6 Future generation must not flatten epistemic status

A model prompt should not receive all context as equally authoritative text.

Accepted facts and provisional suggestions need distinguishable framing.

---

# 17. High-order tensions in the current product

## 17.1 Shape-first versus write-first

**Selected resolution:** maintain both as entry tempos and make them converge.

**Open evidence:** #305 must establish when each tempo creates more value.

## 17.2 Planning authority versus prose discovery

**Selected resolution:** accepted prose can teach Auteur something new; updates propagate explicitly.

**Open evidence:** whether the reconciliation surface feels supportive or administrative.

## 17.3 Strong governance versus creative momentum

**Selected resolution:** governance follows meaningful commitment, not every act of exploration.

## 17.4 Long-range coherence versus local freedom

**Selected resolution:** future planning composes accepted story outcomes and accepted plans; it does not force prose to retroactively match old plans.

## 17.5 Rich internal intelligence versus simple user vocabulary

**Selected resolution:** specialized internals remain; Beginner uses story language and progressive disclosure.

## 17.6 Opinionated guidance versus author ownership

**Selected resolution:** Auteur recommends strongly, explains why, and preserves easy disagreement/change.

**Open evidence:** whether authors experience recommendations as useful expertise or as the tool authoring the story for them.

---

# 18. Evidence-gated questions

## #310 — real-provider questions

Must establish:

- real time to first prose;
- whether Quick Draft is scene-sized and responsive;
- whether exact premise / scene intent survive provider generation;
- whether provisional generic scaffolding leaks into prose;
- whether intentionally vague inputs remain usefully open.

## #305 — real-author questions

Must establish:

- which entry tempo authors prefer in which situations;
- whether authors understand that provisional inference is reversible;
- whether **What did we discover?** feels useful;
- whether explicit carry-forward feels like control or bureaucracy;
- whether **Keep draft & update story** preserves momentum;
- when authors want structural guidance to appear;
- whether Auteur creates value over Markdown + a capable general-purpose LLM;
- whether long-form continuity value is understandable enough to justify additional machinery.

Until those questions return evidence, this architecture should not prescribe one universal default tempo for every author.

---

# 19. Experience success criteria

The unified experience is successful when:

1. a beginner can explain Auteur without naming internal semantic layers;
2. both shape-first and write-first lead to one coherent accepted story state;
3. writers can create unexpected material without validators functioning as plan-enforcement police;
4. important discoveries can become durable without silent promotion;
5. future Chapters know relevant accepted events from earlier Chapters;
6. changing intent does not require manually traversing internal dependency layers;
7. long-form continuity appears when it solves a visible author problem;
8. the primary surface normally asks for story decisions, not lifecycle administration;
9. advanced users can still inspect exact machinery;
10. real authors can identify value over an ordinary editor/chat workflow.

---

# 20. Non-goals

This architecture does **not**:

- create a new semantic layer;
- replace Story Identity, Structure, Realization, or Expression;
- create a new canon store;
- make all prose discoveries canonical;
- require Quick Draft as the default entry for every author;
- require a one-way Scratchpad -> Guide -> Compiler journey;
- eliminate explicit meaningful author acceptance;
- eliminate diagnostics or validation;
- prescribe a native desktop implementation;
- authorize new implementation merely because a coherent idea appears here;
- claim real-author preference before #305;
- claim provider quality/latency before #310.

---

# 21. Compact system law

The intended Auteur experience can be summarized as:

```text
create freely
-> understand when useful
-> commit meaning deliberately
-> let Auteur manage reversible machinery
-> write
-> let writing produce evidence
-> choose what the story should remember
-> carry accepted reality forward
-> expose deeper machinery only when the author needs it
```

Or in one sentence:

> **Auteur should make a complex story system feel like an intelligent writing partner that remembers, explains, and coordinates consequences without taking authorship away from the writer.**
