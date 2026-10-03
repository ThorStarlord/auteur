# Auteur Capability Frontier & Construction Roadmap

**Date:** 2026-10-03  
**Role:** high-order repository construction roadmap  
**Scope:** choose what Auteur should become capable of handling next by progressively increasing narrative stress  
**Relationship:** companion to `auteur-unified-author-experience-architecture.md`, `auteur-system-interaction-map.md`, and `auteur-ux-product-requirements.md`  
**Authority:** roadmap / selection framework. A frontier being named here does **not** authorize implementation.

## 1. Why this roadmap exists

A feature roadmap answers:

> What feature should we build next?

That is not sufficient for Auteur.

Auteur's core product claim is not that it contains many narrative subsystems. It
is that those systems can help an author create, revise, and complete increasingly
complex stories without losing coherence, control, or momentum.

Therefore the more useful construction question is:

> **What harder kind of story should Auteur be able to handle next?**

The roadmap should expand the **story stress envelope** that the complete author
workflow can survive.

This prevents two recurring failure modes:

```text
interesting subsystem idea
-> implement subsystem
-> search for product value later
```

and:

```text
local friction
-> local patch
-> next local friction
-> next local patch
```

The selected construction model is:

```text
controlled narrative frontier
-> run the complete author journey
-> find the first material systemic failure
-> classify the owning layer
-> build the smallest capability that expands the envelope
-> rerun the same frontier
-> increase stress only after the current frontier is coherent
```

---

# 2. Narrative Stress Envelope

Story scale is not one dimension.

Auteur should model capability pressure across six largely independent
dimensions.

## Dimension A — Interpretive Difficulty

How difficult is it to understand what story the author is trying to make?

Examples of increasing stress:

```text
clear genre premise
-> ambiguous premise
-> mixed signals
-> unusual structure
-> hybrid genre
-> conflicting implications
-> unreliable / intentionally incomplete framing
```

This stresses:

- Story Lenses;
- Story Discovery;
- inference quality;
- preservation of ambiguity;
- recommendation quality;
- author-intent interpretation.

## Dimension B — Input / Process Messiness

How cleanly does the author supply the story?

Examples:

```text
clean premise
-> rough notes
-> fragments
-> contradictions
-> incomplete characters
-> spontaneous discoveries
-> abandoned plans
-> prose that outruns the model
```

This stresses:

- provisional inference;
- Quick Draft;
- creative discovery;
- story-update workflows;
- uncertainty;
- stale evidence;
- resilience to incomplete state.

## Dimension C — Narrative Breadth

How many simultaneously relevant things must Auteur track?

Examples:

```text
2 characters
-> ensemble cast
-> multiple relationships
-> subplots
-> factions
-> many locations
-> simultaneous plotlines
-> multiple POVs
```

This stresses:

- context selection;
- character / relationship relevance;
- subplot tracking;
- attention;
- retrieval;
- prompt composition;
- noise control.

## Dimension D — Narrative Depth

How many layers of meaning and dependency exist beneath surface events?

Examples:

```text
direct motivation
-> conflicting motivation
-> hidden motive
-> secrets
-> false belief
-> dramatic irony
-> unreliable testimony
-> foreshadowing
-> nested causal dependencies
-> thematic / character mirrors
```

This stresses:

- causality;
- knowledge and belief state;
- revelation timing;
- epistemic distinctions;
- motive reasoning;
- thematic continuity;
- deep dependency analysis.

## Dimension E — Longitudinal Horizon

How far must accepted story history remain useful?

Examples:

```text
one scene
-> one Chapter
-> several Chapters
-> one Book
-> long Book
-> trilogy
-> long Series
```

This stresses:

- accepted prior outcomes;
- continuity composition;
- long-term state;
- relevance over time;
- Book reconciliation;
- Series continuity;
- historical retrieval.

## Dimension F — Change / Revision Pressure

How much does the author's intent evolve after work already exists?

Examples:

```text
stable plan
-> additive discovery
-> moved revelation
-> changed relationship
-> antagonist becomes ally
-> protagonist emphasis changes
-> earlier Chapter rewrite
-> repeated mid-book restructuring
```

This stresses:

- impact;
- change-my-mind behavior;
- reconciliation;
- proposal routing;
- selective invalidation;
- preservation of unaffected work;
- recovery of creative momentum.

---

# 3. Stress profile, not single complexity score

The roadmap MUST NOT collapse these dimensions into one numeric “story
complexity” score.

Two stories can have similar apparent size but stress Auteur differently.

Example:

```text
Story A
2 characters
1 location
30 Chapters
stable plan

=> low breadth
=> high horizon
```

versus:

```text
Story B
12 characters
5 factions
6 Chapters
stable plan

=> high breadth
=> moderate horizon
```

The correct representation is a **stress profile**, not a score.

Example:

```text
A: Difficulty        moderate
B: Messiness         high
C: Breadth           low
D: Depth             moderate
E: Horizon           medium
F: Change pressure   high
```

Frontier selection should deliberately increase one or two dimensions whenever
possible so failures remain attributable.

---

# 4. Construction law: do not maximize all dimensions at once

A maximal stress story is bad early evidence.

For example:

```text
40 important characters
+ 5 POVs
+ nonlinear chronology
+ nested mystery
+ 70 Chapters
+ repeated rewrites
+ political factions
+ unreliable knowledge
```

If the workflow fails, the repository learns little about why.

Possible causes include:

- retrieval;
- state representation;
- context composition;
- prompt size;
- Story Identity;
- Structure;
- Realization;
- revision propagation;
- UI;
- provider behavior;
- long-horizon continuity.

Therefore:

> **Increase the stress envelope one controlled frontier at a time.**

The purpose of a frontier is not to create an impressive benchmark.

The purpose is to produce **decision-changing failure evidence**.

---

# 5. Capability Frontier Ladder

## F0 — Coherent Scene

### Stress profile

```text
A Difficulty:      low
B Messiness:       low
C Breadth:         very low
D Depth:           low
E Horizon:         one scene / Chapter
F Change pressure: none
```

Typical story:

- 2 characters;
- 1 location;
- 1 immediate conflict;
- 1 Chapter;
- clear premise.

Example:

> Detective Miller questions Suspect Vance about a murder.

### Product question

> Can Auteur turn a clear story idea into useful working prose while preserving
> explicit author control?

### Primary systems exercised

- premise interpretation;
- Story Discovery;
- Story core;
- Story shape;
- Chapter launch;
- Expression.

### Current disposition

**Largely mechanically established.**

Do not continue polishing F0 indefinitely merely because small stories are easy
to test.

---

## F1 — Messy Discovery

### Stress profile

```text
A Difficulty:      low–moderate
B Messiness:       high
C Breadth:         low
D Depth:           low–moderate
E Horizon:         1–3 Chapters
F Change pressure: moderate
```

Typical pressures:

- vague/partial premise;
- missing POV/location;
- unplanned character;
- unplanned location;
- unexpected revelation;
- author changes one important decision.

Reference scenario:

```text
Miller questions Vance.

During drafting:
-> Sister Beatrice appears
-> abandoned convent appears

Then author says:
-> Vance is not actually guilty
```

### Product question

> Can writing teach Auteur something new without forcing the writer to stop and
> repair the machine?

### Primary systems exercised

- Quick Draft;
- provisional inference;
- exact-review freshness;
- creative discovery;
- story updates;
- intentional divergence;
- change-my-mind basics.

### Current disposition

**Mechanically strong candidate.**

Human/provider evidence remains:

- #305 — real-author ergonomics;
- #310 — real-provider Quick Draft.

#313 owns the high-order reconciliation after those evidence streams.

---

## F2 — Small-Book Longitudinal Coherence

### Stress profile

```text
A Difficulty:      moderate
B Messiness:       moderate
C Breadth:         moderate-low
D Depth:           moderate-low
E Horizon:         5–8 Chapters / one small Book
F Change pressure: moderate
```

Reference Book profile:

- 5–7 meaningful characters;
- 3–4 important locations;
- 2 plotlines;
- 1 protagonist;
- 1 antagonist;
- 1 supporting relationship arc;
- 6 Chapters;
- 1 character discovered during drafting;
- 1 meaningful mid-book change;
- 1 revelation moved earlier.

Reference journey:

```text
premise
-> shaping
-> Chapter 1
-> new discovery
-> Chapter 2
-> changed author intent
-> Chapters 3–4
-> Structure drift
-> Chapters 5–6
-> whole-Book review
```

### Product question

> **Does the story written in earlier Chapters remain usable truth for later
> Chapters without requiring the author to manually synchronize every internal
> model first?**

This is the first frontier where Auteur's long-form value proposition becomes
material.

### Primary systems exercised

- accepted Chapter outcomes;
- Realization/state;
- contextual Chapter N planning;
- Structure drift;
- story-update signals;
- continuity composition;
- whole-book orientation;
- change propagation.

### Likely failure classes

- Chapter N forgets Chapter N-2;
- old Structure overrides accepted prose;
- too much context reaches every prompt;
- pending updates block writing unnecessarily;
- story discoveries are lost between Chapters;
- Book reconciliation is technically correct but unusable.

### Current disposition

**RECOMMENDED NEXT MAJOR CONSTRUCTION FRONTIER, EVIDENCE-GATED.**

Do not automatically start F2 before:

```text
#305
+
#310
-> #313 reconciliation
```

unless an independently warranted product defect requires repair.

If #313 does not materially revise the product thesis/entry model, F2 should be
the preferred next construction frontier over another local Quick Draft feature
or another new narrative subsystem.

---

## F3 — Multi-Thread Book

### Stress profile

```text
A Difficulty:      moderate
B Messiness:       moderate
C Breadth:         high
D Depth:           moderate
E Horizon:         10–15 Chapters
F Change pressure: moderate
```

Reference profile:

- 8–12 meaningful characters;
- 3–4 subplots;
- multiple relationships;
- 5–8 important locations;
- 2–3 factions;
- one or more secondary POVs.

### Product question

> Can Auteur remember **the right things at the right moment** rather than merely
> remembering everything?

### Primary systems exercised

- contextual retrieval;
- relevance selection;
- subplot activation/dormancy;
- relationship relevance;
- character/faction context;
- prompt budget discipline;
- Author Attention.

### Expected capability transition

The dominant problem changes from:

> Can Auteur remember?

to:

> Can Auteur select relevant context without drowning the writer/model in noise?

### Admission rule

Do not build a generalized relevance/retrieval subsystem merely because F3 will
probably need one.

Admit it when F3 evidence shows that existing context composition fails
recurringly.

---

## F4 — Narrative Depth

### Stress profile

```text
A Difficulty:      high
B Messiness:       moderate
C Breadth:         moderate
D Depth:           high
E Horizon:         medium
F Change pressure: moderate
```

Reference pressures:

- hidden motives;
- secrets;
- false beliefs;
- unreliable testimony;
- dramatic irony;
- reader knowledge distinct from POV knowledge;
- nested cause/effect;
- revelation timing;
- thematic and character mirrors.

Example:

```text
Miller believes:
Vance killed Elena.

Vance knows:
Beatrice manipulated the evidence.

Beatrice believes:
Miller already knows.

Reader knows:
Elena is alive.
```

### Product question

> Can Auteur distinguish what is true from what each participant believes,
> knows, hides, or misunderstands?

### Likely domain pressure

This frontier may reveal genuine model gaps such as:

- world truth versus character belief;
- POV knowledge;
- reader knowledge;
- deception;
- uncertainty;
- revelation state.

### Admission rule

Do **not** add an epistemic ontology merely because these concepts are
interesting.

Add/extend the domain model only when recurring F4 stories prove the current
accepted/candidate/derived state cannot express the required distinction cleanly.

---

## F5 — Evolving Long Book

### Stress profile

```text
A Difficulty:      moderate-high
B Messiness:       high
C Breadth:         moderate-high
D Depth:           moderate-high
E Horizon:         20–30 Chapters
F Change pressure: high
```

Reference changes:

- major revision around Chapter 8;
- new protagonist emphasis around Chapter 12;
- antagonist becomes ally around Chapter 15;
- earlier Chapter rewritten around Chapter 18;
- final-act Structure substantially changes.

### Product question

> Can the author substantially change the story without restarting it or paying
> an intolerable reconciliation tax?

### Primary systems exercised

- impact;
- selective invalidation;
- change-my-mind;
- dependency traversal;
- Structure revision;
- Realization updates;
- Book reconciliation;
- preservation of unaffected work.

### Success shape

```text
change
-> consequences understood
-> minimum necessary state updated
-> unaffected material preserved
-> future plans refreshed
-> creative momentum resumes
```

---

## F6 — Complex Long Book

### Stress profile

```text
A Difficulty:      high
B Messiness:       high
C Breadth:         high
D Depth:           high
E Horizon:         long Book
F Change pressure: high
```

Reference profile:

- 15–20 important characters;
- 4–6 major plot threads;
- multiple POVs;
- 25–40 Chapters;
- secrets / foreshadowing;
- substantial mid-book changes;
- multiple consequential relationship arcs.

### Product question

> Does the complete Auteur system remain coherent when breadth, depth, horizon,
> and revision pressure interact rather than being tested separately?

F6 is a **combined-pressure qualification frontier**.

It should not be attempted early merely to prove ambition.

---

## F7 — Series

### Stress profile

```text
A Difficulty:      high
B Messiness:       moderate-high
C Breadth:         very high
D Depth:           high
E Horizon:         multiple Books
F Change pressure: high
```

Reference pressures:

- promises created several Books earlier;
- world-state evolution;
- long-term character transformation;
- mysteries spanning Books;
- recurring locations/factions;
- inherited consequences;
- Book-level versus Series-level Story Identity.

### Product question

> Can accepted history remain useful and selectively relevant across Books
> without creating a second canon or flattening Book-specific meaning?

### Primary systems exercised

- Series continuity;
- Universe/Series/Book scopes;
- long-horizon projection;
- historical retrieval;
- dormant promise resurfacing;
- Book-specific versus Series-level authority.

### Admission rule

Existing Series architecture is not itself proof of F7 product readiness.

F7 requires complete author-workflow stress qualification after single-Book
frontiers are reliable.

---

# 6. Frontier qualification loop

For every frontier:

## Step 1 — define the controlled story

Record:

- stress profile A–F;
- expected Chapter/Book length;
- main characters;
- plot threads;
- deliberate changes/discoveries;
- exact claims being tested.

## Step 2 — run the complete author journey

Do not test the subsystem alone when the claim concerns the product.

Example:

```text
premise
-> shaping
-> planning
-> drafting
-> acceptance
-> discovery
-> revision
-> future planning
-> Book orientation
```

## Step 3 — identify the first material failure

Stop interpreting once a material failure makes downstream evidence unreliable.

Examples:

- Chapter 4 forgets an accepted Chapter 2 fact;
- prompt context becomes unusably noisy;
- an unmodeled belief cannot be represented;
- one story change requires 17 visible approvals.

## Step 4 — classify the failure

Use the existing repository classification:

| Failure class | Meaning |
| --- | --- |
| **UX / presentation** | capability exists but is difficult to understand/use |
| **workflow** | existing capabilities fail to compose into one author action |
| **craft knowledge** | reusable narrative guidance is missing |
| **domain model** | current accepted/candidate/derived state cannot express a recurring need |
| **infrastructure** | reliability/performance/portability blocks the workflow |

## Step 5 — select the lowest correct intervention

Examples:

```text
forgotten accepted Chapter fact
-> context composition / continuity workflow

too much remembered context
-> relevance selection

Miller must not know something Vance knows
-> possible epistemic domain-model pressure

too many confirmations after one clear author change
-> workflow / UX compression
```

## Step 6 — rerun the same frontier

Do not declare the capability fixed because a unit test passes.

The frontier story is the product-level qualification.

## Step 7 — advance only when coherent

A frontier may advance when:

- the complete journey remains usable;
- failures are no longer materially attributable to the stress dimension under
  qualification;
- authority remains correct;
- no new workaround creates a worse systemic failure;
- claim-appropriate human/provider evidence exists where required.

---

# 7. Failure-driven repository construction

The roadmap answers “what should we build next?” using this rule:

> **Build the smallest capability that removes the first meaningful blocker to
> the next controlled narrative frontier.**

This means the roadmap does **not** prescribe:

- continuity subsystem next;
- relationship subsystem next;
- knowledge subsystem next;
- retrieval subsystem next.

Instead:

```text
frontier story
-> observed failure
-> owner/layer diagnosis
-> bounded capability
```

Capabilities are admitted because a real story requires them.

---

# 8. Relationship to the Experience Frontier Roadmap

Narrative capability and UX/UI capability must be qualified separately.

See:

- `auteur-experience-frontier-construction-roadmap.md`

A narrative frontier may pass while its paired experience frontier fails.

Example:

```text
F2 PASS
Chapter 5 remembers Chapter 1 correctly

X3 FAIL
author cannot understand the Book workspace or next action
```

Conversely:

```text
X3 PASS
Book workspace is clear

F2 FAIL
Chapter 5 forgets an accepted Chapter 1 event
```

Do not repair one layer for the other's failure.

If #313 reaffirms the current product model, qualify:

```text
F2 — Small-Book Longitudinal Coherence
+
X3 — Persistent Book Workspace
```

with the same reference Book and independent pass/fail claims.

# 9. Relationship to the Unified Author Experience Architecture

The capability frontier roadmap and experience architecture constrain each other.

A frontier expansion is not successful merely because the backend can represent
the story.

The complete product must still preserve:

- the Unified Author Mental Model;
- maximum author control over meaning;
- minimum author administration of machinery;
- story-language presentation;
- progressive disclosure;
- explicit authority;
- recoverable exploration;
- no duplicate authorship;
- no reconciliation tax;
- no long-form context reset.

Therefore:

```text
narrative capability expansion
without
author-experience coherence
=
frontier not qualified
```

---

# 10. Relationship to #305, #310, and #313

The current frontier is F1.

Its remaining evidence is:

```text
#305
real-author experience

#310
real-provider Quick Draft behavior
```

Issue #313 consumes those results together with the Unified Author Experience
Architecture.

After #313:

- if the current experience model is materially revised, reconcile the frontier
  roadmap before construction;
- if the model is reaffirmed, prefer **F2 — Small-Book Longitudinal Coherence**
  as the next major construction frontier.

This prevents F2 from becoming an automatic package merely because it appears
next in a table.

---

# 11. F2 reference qualification story

If F2 is selected after #313, use one controlled reference Book before designing
new subsystems.

## Suggested shape

Working title: **The Vance Case**

### Cast

- Detective Miller — protagonist;
- Suspect Vance — principal suspect;
- Sister Beatrice — discovered during writing;
- Elena — relationship/revelation anchor;
- Captain Rowe — institutional pressure.

### Locations

Initial:

- police precinct;
- Miller's apartment.

Discovered / later:

- abandoned seaside convent;
- harbor district.

### Plot threads

1. murder investigation;
2. Miller / Elena relationship and trust.

### Deliberate stress events

- Chapter 1 introduces Sister Beatrice unexpectedly;
- Chapter 2 accepts the convent as real story context;
- Chapter 3 moves a planned revelation earlier;
- Chapter 4 changes Vance from likely culprit to probable pawn;
- Chapter 5 tests whether old Structure and accepted reality diverge cleanly;
- Chapter 6 performs whole-Book orientation/review.

### Qualification questions

- Does Chapter 2 know Beatrice exists?
- Does Chapter 4 remember what Chapter 1 actually established?
- Does moving the revelation earlier refresh dependent planning without forcing
  unrelated decisions open?
- Does changing Vance's role preserve unaffected material?
- Can pending compatible updates coexist with continued drafting?
- Does Book orientation explain drift in story language?
- Does the author have to manually re-enter discoveries already accepted in
  prose?

This Book is a **controlled stress fixture**, not canonical Auteur sample fiction.

---

# 12. Current approximate frontier state

This is a qualitative product-readiness map, not a numeric score.

```text
F0 — Coherent Scene
mechanically established

F1 — Messy Discovery
mechanically strong candidate
human/provider evidence pending

F2 — Small-Book Longitudinal Coherence
backend pieces exist
complete product proof is the recommended next frontier

F3 — Multi-Thread Book
partial underlying capability
product-level relevance qualification immature

F4 — Narrative Depth
some reasoning/craft capability exists
deep epistemic-state pressure not qualified

F5 — Evolving Long Book
revision/reconciliation components exist
combined long-horizon change pressure not qualified

F6 — Complex Long Book
many component capabilities exist
complete combined-pressure product qualification not established

F7 — Series
substantial backend architecture exists
end-to-end product stress qualification remains immature
```

Important:

> **Capability existing somewhere in the repository is not the same as the
> complete author workflow surviving that capability frontier.**

---

# 13. Anti-roadmap patterns

## Feature accumulation

```text
character system
-> relationship system
-> knowledge system
-> retrieval system
```

without frontier evidence.

**Reject.**

## Benchmark maximalism

Jump directly to a giant complex story so many systems fail simultaneously.

**Reject.**

## UI-first response to every frontier failure

Treat every failure as another button/copy problem.

**Reject.**

## Ontology-first response

Create a new domain model whenever a difficult story concept appears.

**Reject.**

## Frontier theater

Declare a frontier “passed” because isolated tests are green while the complete
author journey fails.

**Reject.**

## Permanent F0 optimization

Continue polishing simple-scene UX forever because it is easy to measure.

**Reject.**

---

# 14. Construction roadmap summary

```text
F0  Coherent Scene
      ↓
F1  Messy Discovery
      ↓
     #305 + #310
      ↓
     #313 high-order reconciliation
      ↓
F2  Small-Book Longitudinal Coherence
      ↓
F3  Multi-Thread Book
      ↓
F4  Narrative Depth
      ↓
F5  Evolving Long Book
      ↓
F6  Complex Long Book
      ↓
F7  Series
```

The arrows indicate **preferred evidence order**, not automatic authorization.

At every step:

```text
qualify frontier
-> observe first material failure
-> build lowest correct capability
-> requalify same frontier
-> advance only when coherent
```

---

# 15. Compact roadmap law

> **Do not build the next interesting feature. Build the capability required for
> Auteur to survive the next deliberately harder kind of story.**

That is the repository construction principle this roadmap exists to preserve.
