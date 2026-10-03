# Auteur System Interaction Map

**Date:** 2026-10-03  
**Role:** cross-system interaction companion to `auteur-unified-author-experience-architecture.md`  
**Scope:** author action -> product projection -> semantic owner -> authority transition -> downstream context  
**Authority:** descriptive / product-contract mapping. Existing domain owners remain authoritative.

## 1. Purpose

Auteur contains specialized systems that must remain semantically distinct while feeling coherent to the writer.

This map answers:

> **When the author does something meaningful, which systems become involved, what do they know, what may they change, and what should the author actually see?**

The map is deliberately organized by **author event**, not by package/module.

---

# 2. System families

| Product responsibility | Primary internal owner(s) | Can create accepted story authority directly? | Default Beginner presentation |
| --- | --- | ---: | --- |
| Premise interpretation | Beginner analysis / Story Lenses | No | What Auteur sees |
| Story possibilities | Story Discovery | No until existing Direction / Identity acceptance path | Direction |
| Defining story commitments | Identity | Yes, through existing acceptance | Story core |
| Whole-story organization | Structure / Blueprint | Yes, through existing Structure workflow | Story shape |
| Scene/Chapter planning | Cartographer / planning workflows | Existing planning authorities | Chapter launch |
| Story facts/events/state | Realization / Bible/state | Through owning state workflow | Usually hidden; continuity/story updates |
| Prose | Expression / Bard | Yes, through Chapter/Book acceptance | Working draft / accepted draft |
| Review / critique | Critics / Review | No | Review details |
| Change consequence analysis | Impact / related derived systems | No | “What would change?” |
| Candidate reconciliation | Convergence / proposal flows | No by itself | Story updates / choices |
| Whole-book synchronization | Book reconciliation | Book owner only | Whole-book continuity |
| Long-horizon continuity | Series / Universe projections | Existing Series/Book authorities | Relevant continuity when needed |
| Product orchestration | Beginner | **Never** parallel authority | One coherent next action |

---

# 3. End-to-end baseline flow

## 3.1 Shape-first

```text
AUTHOR
enters premise
    |
    v
BEGINNER INTERPRETATION
derived "what Auteur sees"
    |
    v
STORY DISCOVERY
plausible directions
    |
    | author chooses
    v
IDENTITY OWNER
accepted story core
    |
    v
STRUCTURE
recommended / customized story shape
    |
    | author accepts
    v
PLANNING
outline -> Chapter plan -> scene plans -> draft handoff
    |
    v
EXPRESSION
working Chapter prose
    |
    | author keeps
    v
CHAPTER EXPRESSION OWNER
accepted Chapter
    |
    v
CONTINUITY COMPOSITION
accepted prior outcome informs next planning
```

The Beginner layer projects this as a small number of coherent author actions.

## 3.2 Write-first

```text
AUTHOR
premise + first-scene intent
    |
    v
QUICK DRAFT FACADE
provisional inferred scaffold only
    |
    v
EXPRESSION GENERATION
editable working scene
    |
    v
DISCOVERY PROJECTION
possible new material
    |
    | author explicitly selects what to carry
    v
NORMAL BEGINNER SHAPING
selected discoveries + premise + scene intent
    |
    v
DISCOVERY / IDENTITY / STRUCTURE
normal existing owners
```

Quick Draft does not become a Story Identity owner.

---

# 4. Context classes

Cross-system context must preserve what kind of evidence it is.

| Context class | Example | May be treated as accepted fact? |
| --- | --- | ---: |
| Author-explicit current intent | “Make the antagonist an ally.” | Intent, not yet all resulting state |
| Accepted Story core | protagonist central desire | Yes within Identity authority |
| Accepted Structure | chosen story shape | Yes within Structure authority |
| Accepted Chapter prose | Sister Beatrice appears in Chapter 1 | Yes as accepted Expression |
| Accepted realized state | character/location/event formally retained by state owner | Yes within Realization/state authority |
| Machine inference | “this may be noir” | No |
| Quick Draft provisional scaffold | generic tension progression | No |
| Heuristic discovery | “possible new place: convent” | No |
| Author-selected discovery | “carry Sister Beatrice into shaping” | Explicit shaping input, not automatically accepted fact |
| Proposed update | change Structure to include convent sequence | No |
| Stale review | critic report over old draft bytes | No current evidentiary authority |

The prompt/context composer must not flatten these classes into one undifferentiated text blob.

---

# 5. Sister Beatrice lifecycle

This is the canonical high-order interaction test.

## Step 0 — current accepted/planned context

```text
Accepted / planned:
- Detective Miller
- Suspect Vance
- precinct interrogation
```

No Sister Beatrice or convent exists in current modeled context.

## Step 1 — writer invents new material

Working draft:

```text
Miller follows Vance to an abandoned seaside convent.
Sister Beatrice reveals that Vance has been hiding there.
```

### System state

| System | What it knows |
| --- | --- |
| Expression | Working prose contains Beatrice + convent |
| Structure | Still contains precinct-centered plan |
| Identity | Unchanged |
| Realization/Bible | May not yet contain Beatrice/convent |
| Beginner | May derive possible discoveries |
| Critics | May evaluate exact current draft |
| Book/Series | Must not treat working draft as accepted history |

### Author experience

> “You wrote something new.”

Not:

> “Schema mismatch in Realization State.”

---

# 6. Exact-review freshness

Review evidence is tied to exact draft content.

```text
draft bytes D1
-> hash H1
-> critics review H1

author edits
-> draft bytes D2
-> hash H2

H2 != H1
-> prior review is stale
```

The product must say:

> “This draft changed after its previous review.”

It must not display old findings as though they describe D2.

---

# 7. Post-draft author decision

The Beginner surface offers:

```text
Keep draft & update story
Keep as intentional divergence
Revise to match plan
```

These map to different system consequences.

## 7.1 Keep draft & update story

```text
author choice
-> existing Chapter Expression acceptance owner
-> accepted prose
-> derived noncanonical update proposals
-> proposals routed to lowest sufficient owners
```

Important:

```text
Chapter acceptance
!=
automatic Structure mutation

Chapter acceptance
!=
automatic Identity mutation

Chapter acceptance
!=
automatic Bible mutation
```

## 7.2 Keep as intentional divergence

```text
author choice
-> existing Chapter Expression acceptance
-> divergence acknowledgement retained
-> current upstream plan remains unchanged
```

The product may later surface the divergence when it becomes relevant.

## 7.3 Revise to match plan

```text
author choice
-> existing noncanonical revision path
-> current working prose preserved in history
-> no Chapter acceptance
```

---

# 8. Lowest-sufficient-owner routing

After **Keep draft & update story**, possible routing is:

| New evidence | First likely owner | Escalate when |
| --- | --- | --- |
| Sister Beatrice exists | Realization / continuity state | her role changes defining story commitments |
| Convent exists | Realization / location state | location fundamentally changes story architecture |
| Beatrice hid Vance there | Realized event/fact | the event invalidates planned Structure |
| Chapter leaves precinct path | Realization / Structure | downstream beats/planning depend on old path |
| Vance is secretly protagonist | Identity | immediately; defining story meaning changed |
| Story changes from mystery to family reconciliation | Identity + Structure | defining experience/engine changed |

Routing must not use:

```text
new detail
-> reopen all owners
```

---

# 9. Future Chapter planning with pending story updates

This is the most important cross-system rule for long-form coherence.

Assume Chapter 1 containing Beatrice has been accepted, but Realization/Structure update proposals are still pending.

Future planning should compose:

```text
accepted Story core
+
accepted Structure
+
accepted Chapter 1 outcome
+
accepted realized facts
+
material pending story-update signals
```

It should not simply use:

```text
old Structure alone
```

and it should not silently mutate Structure.

## Product behavior

Chapter 2 planning may know:

> “Sister Beatrice appeared in the accepted Chapter 1 and Vance stayed at the convent.”

while also knowing:

> “The current Structure has not yet been updated to reflect this detour.”

This lets the system preserve momentum without hiding model drift.

---

# 10. Quick Draft -> shaping handoff

## 10.1 Current product sequence

```text
premise
+ first-scene intent
-> provisional Quick Draft scaffold
-> scene prose
-> author edits
-> What did we discover?
-> heuristic observations
-> explicit author checkboxes
-> Shape this story
```

## 10.2 Handoff data

The handoff should preserve:

- exact premise;
- exact first-scene intent;
- exact source-draft hash;
- selected discoveries;
- destination workspace;
- provisional source identity.

Unselected heuristic findings remain behind.

## 10.3 Authority

```text
author-selected discovery
= explicit shaping evidence

author-selected discovery
!= accepted Story Identity

author-selected discovery
!= accepted Structure
```

The normal shaping path still owns acceptance.

---

# 11. Change-my-mind interaction map

Example author intent:

> “Marcus is not the antagonist anymore. He becomes an ally.”

## Desired interaction

```text
AUTHOR INTENT
free-form change statement
    |
    v
INTENT INTERPRETATION
identify affected meaning
    |
    v
IMPACT
derive affected accepted/planned artifacts
    |
    v
AUTHOR-FACING CONSEQUENCES
"this changes X, Y, and Z"
    |
    v
PROPOSALS / REVISION PLANS
existing owners
    |
    | explicit consequential decisions
    v
ACCEPTED UPDATED STATE
    |
    v
REPLAN DEPENDENTS
    |
    v
RESUME WRITING
```

The author should not manually visit every layer.

## Two distinct change classes

### Change from here forward

Past accepted events remain true.

Example:

> “From now on, she chooses to trust him.”

### Revise earlier story

Earlier accepted material itself becomes obsolete.

Example:

> “The Chapter 2 reveal never happened.”

These must have different consequences and should not be collapsed into one generic state transition.

---

# 12. Whole-book reconciliation map

The author-level purpose of Book reconciliation is:

> “Make sure the Book you now have matches the story you actually wrote.”

Internally:

```text
accepted Chapters
+
accepted Book-owned sources
+
current Structure
+
accepted state
-> inspect differences
-> propose updates
-> explicit decisions
-> recompose
-> explicit Book acceptance
```

The Beginner product should generally surface:

- meaningful differences;
- consequences;
- unresolved updates;
- one next action.

It should not require the author to operate the raw reconciliation transaction lifecycle unless they choose deep control.

---

# 13. Series / long-horizon context

Long-horizon support should answer author questions such as:

- What does this Book establish that later Books must remember?
- Which characters/relationships are still active?
- Which promises remain unresolved?
- What changed from the original Series plan?
- What previous event now matters to the next decision?

Derived global maps remain orientation tools.

They do not become a second canon.

---

# 14. System handoff contract

Every cross-system handoff should be able to answer:

1. **What did the author actually say or do?**
2. **What source state was current?**
3. **What is accepted?**
4. **What is inferred?**
5. **What is proposed?**
6. **What is stale?**
7. **Which owner must accept any consequential change?**
8. **What should the author see now?**

If a handoff cannot answer those questions, it is likely to create either hidden commitment or user-facing machinery leakage.

---

# 15. Product projection rules by internal condition

| Internal condition | Beginner-facing interpretation |
| --- | --- |
| provisional inference exists | “Here’s what Auteur currently sees.” |
| multiple plausible directions | “Here are a few ways this could develop.” |
| accepted Story core exists | “This is the story you’re building.” |
| Structure proposal exists | “Here’s a recommended story shape.” |
| draft exists, not accepted | “Working draft.” |
| review stale | “The draft changed after this review.” |
| additive discovery | “Auteur noticed something new.” |
| plan divergence | “This Chapter moved away from the plan.” |
| hard contradiction | “This conflicts with something you established earlier.” |
| pending update proposals | “There are story updates to review.” |
| accepted past outcome affects future | silently include as context; surface only when relevant |
| Book-level mismatch | “The Book plan and written story have drifted apart here.” |
| advanced provenance requested | show exact owner/source/hash/command detail |

---

# 16. Failure modes this map is designed to prevent

## Duplicate state authority

Beginner stores its own accepted version of something already owned elsewhere.

**Forbidden.**

## Context amnesia

Chapter N planning ignores accepted events from Chapter N-1 because they were not manually backfilled into every upstream model.

**Systemic product defect.**

## Context contamination

A rejected or provisional Quick Draft detail becomes future accepted context merely because it appeared in a prompt.

**Forbidden.**

## Silent drift

Accepted prose contradicts planning/state and future generation proceeds as though the mismatch does not exist.

**Defect.**

## Maintenance blockade

The writer cannot proceed until every additive discovery has been fully synchronized.

**Avoid unless a genuine contradiction makes continuation unsafe or misleading.**

## Shadow product fork

Quick Draft and shape-first produce different incompatible forms of story truth.

**Forbidden.**

---

# 17. Current implementation versus selected high-order target

| Concern | Current integrated candidate | High-order target |
| --- | --- | --- |
| Shape-first compression | implemented in #304 | retain, validate human value |
| Plain vocabulary | implemented in #307 | extend consistently to deeper continuity surfaces |
| Quick Draft | implemented in #309 | retain as optional tempo if #305/#310 support it |
| Quick Draft persistence | implemented | preserve |
| Explicit discovery carry-forward | implemented | preserve |
| Exact-draft review freshness | implemented | preserve across all review surfaces |
| Creative divergence choices | implemented | validate human comprehension |
| Lowest-owner proposal principle | selected / bounded implementation | generalize across long-form updates |
| Accepted prose informing future planning | partially represented by continuation/outcome flows | make an explicit cross-system composition invariant |
| Change-my-mind natural-language routing | existing components exist, unified UX incomplete | future evidence-gated design responsibility |
| Whole-book continuity UX | advanced/read-only orientation exists | project story consequences before transaction machinery |
| Series continuity UX | backend capability exists | contextual progressive disclosure |
| Unified cross-system author model | fragmented across docs | defined by this architecture package |

---

# 18. Validation traces

The following concrete traces should remain standard high-order regression scenarios.

## Trace A — Shape-first beginner

```text
premise
-> interpretation
-> direction
-> story core
-> story shape
-> Chapter plan
-> prose
```

Question: did the author decide meaning without supervising reversible machinery?

## Trace B — Write-first beginner

```text
premise + scene intent
-> prose
-> discoveries
-> explicit carry-forward
-> shaping
```

Question: did exploration remain provisional until the author selected meaning?

## Trace C — Sister Beatrice

```text
planned precinct scene
-> unplanned Beatrice + convent
-> accepted prose
-> update story
-> Chapter 2
```

Question: does Chapter 2 know the accepted reality without silent Structure mutation?

## Trace D — Change my mind

```text
accepted antagonist
-> author says "make him an ally"
-> consequences
-> explicit updates
-> revised future planning
```

Question: can the author change intent without navigating internal layers?

## Trace E — Long-form drift

```text
original Book plan
-> repeated accepted Chapter deviations
-> whole-book continuity review
-> explicit Book update
```

Question: does Auteur follow the story actually written while preserving deliberate authority?

---

# 19. Relationship to capability frontier qualification

The interaction traces in this document become **frontier qualification
journeys** under:

- `auteur-capability-frontier-construction-roadmap.md`

Examples:

```text
F1 — Messy Discovery
-> Trace B / Sister Beatrice

F2 — Small-Book Longitudinal Coherence
-> Trace C extended through Chapter 6 + whole-Book orientation

F5 — Evolving Long Book
-> Trace D repeated under long-horizon revision pressure

F7 — Series
-> long-horizon context + Book/Series authority traces
```

When a frontier fails, diagnose the **first material interaction break** in this
map before choosing a new subsystem.

The purpose is not merely to ask whether data exists somewhere in the
repository. The question is:

> Which author action stopped composing cleanly across the existing systems?

This preserves a direct connection between capability growth and the unified
author experience.

# 20. One-system test

A product state is systemically coherent when the author can move through:

```text
explore
-> shape
-> write
-> discover
-> change
-> reconcile
-> continue
```

without needing to understand why those actions internally belong to different packages.

The systems may remain specialized.

The experience must not.
