# Auteur Experience Frontier & UX/UI Construction Roadmap

**Date:** 2026-10-03  
**Role:** high-order UX/UI construction roadmap  
**Scope:** choose which harder author experience the interface must support next as Auteur's narrative capability grows  
**Relationship:** companion to `auteur-capability-frontier-construction-roadmap.md` and `auteur-unified-author-experience-architecture.md`  
**Authority:** roadmap / qualification framework. A frontier being named here does **not** authorize implementation.

## 1. Why this roadmap exists

The Narrative Capability Frontier asks:

> **How difficult a story can Auteur handle coherently?**

The Experience Frontier asks a different question:

> **How much product capability and accumulated story state can Auteur expose while still feeling understandable, focused, and usable to the author?**

These dimensions must remain separate.

A backend may correctly remember a six-Chapter story while the interface becomes
confusing and overloaded.

Conversely, the interface may be clear while the underlying story system forgets
important accepted history.

Therefore:

```text
narrative capability
!=
experience capability
```

The complete product advances only when both remain coherent.

---

# 2. Experience Stress Envelope

UX/UI complexity should not be collapsed into one generic “interface
complexity” score.

Auteur should qualify author experience across eight dimensions.

## UX-A — Decision Density

How many meaningful author decisions are simultaneously relevant?

Examples:

```text
one obvious action
-> one primary action + one optional choice
-> several meaningful story changes
-> multiple pending consequences
-> competing high-value next actions
```

This stresses:

- prioritization;
- author attention;
- primary-action projection;
- grouping;
- deferral;
- explanation of what matters now.

A common failure is:

```text
many valid actions
-> all shown with equal weight
-> author must become the workflow scheduler
```

## UX-B — Workflow Branching

How many reasonable things could the author do next?

Examples:

```text
continue
-> continue / revise
-> write / shape / review
-> write / revise / replan / inspect continuity / compare / change direction
```

This stresses:

- information architecture;
- navigation;
- contextual commands;
- secondary actions;
- progressive disclosure;
- mode transitions.

The product goal is not to remove capability.

It is to avoid turning capability breadth into a cockpit of equally prominent
controls.

## UX-C — State / Continuity Load

How much accumulated work must the interface make understandable?

Examples:

```text
one premise
-> one draft
-> several Chapters
-> accepted history
-> pending story updates
-> Structure drift
-> revisions
-> Book-level continuity
```

This stresses orientation:

- Where am I?
- What is current?
- What changed?
- What needs my decision?
- What can I ignore?
- What should I work on next?

This axis becomes increasingly important beginning at Narrative Frontier F2.

## UX-D — Interaction Horizon

How long does the author remain in the product and need useful continuity of
work?

Examples:

```text
one action
-> one session
-> several writing sessions
-> weeks / months
-> complete Book
-> multi-Book Series
```

This stresses:

- resume/re-entry;
- work history;
- recent changes;
- unresolved work;
- session orientation;
- why prior decisions were made;
- long-term navigation.

A first-session flow and a six-month Book workspace should not be assumed to
need the same interface architecture.

## UX-E — Mode Switching

How often must the author move between different kinds of creative work?

Auteur's contextual modes include:

```text
Creative
Guidance
Continuity
Deep control
```

Typical sequence:

```text
write
-> ask why scene is weak
-> guidance
-> edit prose
-> discover new character
-> story update
-> return to writing
```

This stresses whether Auteur feels like one coherent product rather than several
specialized tools joined by navigation seams.

## UX-F — Expertise Range

How broad is the range between the simplest and deepest useful interaction?

Beginner need:

> “What should I do next?”

Advanced need:

> “Show the exact source, dependency, provenance, and alternative.”

This stresses progressive disclosure.

Preferred depth:

```text
Level 0 — orientation + primary action
Level 1 — why this matters
Level 2 — evidence / alternatives / blockers
Level 3 — raw artifacts / advanced commands / provenance / diagnostics
```

The product SHOULD avoid compromising at an awkward middle level that is too
technical for beginners and too weak for advanced users.

## UI-G — Information Density

How much information must coexist on one surface?

Examples:

```text
premise form
-> draft + review
-> Chapter + story updates + progress
-> Book + characters + relationships + continuity + pending changes
```

This stresses:

- visual hierarchy;
- grouping;
- collapse/expand behavior;
- contextual side panels;
- persistent navigation;
- focus management;
- information filtering.

A single-column card flow that succeeds at X1 may fail at X4.

## UI-H — Visual / Spatial Complexity

How many distinct spatial relationships must the interface communicate?

Possible increasing needs:

```text
forms / cards / editor
-> persistent navigation
-> editor + contextual panel
-> Book overview
-> relationship/timeline views
-> comparison/diff surfaces
-> multi-pane professional workspace
```

The roadmap MUST NOT pre-authorize these patterns.

Spatial complexity should grow only when the current simpler interaction model
fails at a qualified frontier.

---

# 3. Experience stress profile, not one UX score

An experience should be represented as a profile.

Example:

```text
UX-A Decision Density       medium
UX-B Workflow Branching     low
UX-C State Load             high
UX-D Interaction Horizon    high
UX-E Mode Switching         medium
UX-F Expertise Range        high
UI-G Information Density    medium
UI-H Spatial Complexity     low
```

Two product states can stress the interface differently even when they operate
on stories of similar narrative complexity.

Do not create a numeric weighted total and treat it as a product-quality score.

---

# 4. Accessibility is a floor, not a late frontier

Accessibility MUST NOT be deferred until the interface becomes sophisticated.

Every frontier should preserve baseline accessibility including:

- semantic controls;
- keyboard operability;
- visible focus;
- meaningful labels;
- sufficient contrast;
- screen-reader semantics;
- understandable validation/error feedback;
- no color-only meaning;
- usable focus order.

Higher frontiers may introduce harder accessibility problems, especially with
dense workspaces, diagrams, timelines, and multi-pane layouts.

Those are additional frontier pressures.

Baseline accessibility is not optional frontier scope.

---

# 5. Visual polish is not experience scale

Visual maturity and UX capability are related but distinct.

Auteur may have:

- a beautiful X1;
- an ugly X6;
- a mechanically strong X3 with weak visual identity;
- a visually polished interface with poor information architecture.

Therefore:

```text
visual polish
!=
experience frontier qualification
```

A lightweight visual-design maturity track may coexist:

```text
V0 — coherent typography / spacing / controls
V1 — semantic component language
V2 — writing-focused visual identity
V3 — dense workspace patterns
V4 — visualization language
V5 — professional polish
```

But V0–V5 MUST NOT replace the X-frontier model.

---

# 6. Experience Frontier Ladder

## X0 — Single-Task Clarity

### Experience profile

```text
Decision density:        very low
Workflow branching:      very low
State load:              very low
Interaction horizon:     immediate
Mode switching:          none
Expertise range:         beginner
Information density:     low
Spatial complexity:      low
```

Typical tasks:

- enter a premise;
- enter a first-scene intent;
- choose one obvious next action.

### Product question

> Can the author immediately understand what to do?

### Current disposition

**Mechanically established.**

Do not indefinitely optimize X0 because it is easy to test.

---

## X1 — Guided First Session

### Experience profile

```text
Decision density:        low
Workflow branching:      low
State load:              low
Interaction horizon:     one session
Mode switching:          low
Expertise range:         beginner + optional detail
Information density:     low–moderate
Spatial complexity:      low
```

Typical journey:

```text
premise
-> what Auteur sees
-> Direction
-> Story core
-> Story shape
-> first prose
```

### Product question

> Can Auteur provide useful guidance without making the author supervise
> reversible machinery?

### Primary evidence

PR #304 / #307.

### Current disposition

**Mechanically strong candidate.**

Human evidence remains #305.

---

## X2 — Reversible Creative Exploration

### Experience profile

```text
Decision density:        moderate-low
Workflow branching:      moderate
State load:              low–moderate
Interaction horizon:     several sessions
Mode switching:          moderate
Expertise range:         beginner + optional deep control
Information density:     moderate
Spatial complexity:      low–moderate
```

Capabilities:

- Shape First;
- Write First;
- editable working drafts;
- provisional inference;
- What did we discover?;
- Keep draft & update story;
- intentional divergence;
- change-my-mind basics;
- resumable Quick Draft.

### Product question

> Can the writer move between exploration and commitment without becoming
> confused about what is actually part of the story?

### Current disposition

**Mechanically strong candidate in #309.**

Real-author/provider evidence remains #305 / #310.

---

## X3 — Persistent Book Workspace

### Experience profile

```text
Decision density:        moderate
Workflow branching:      moderate
State load:              high
Interaction horizon:     days / weeks
Mode switching:          moderate
Expertise range:         beginner to advanced
Information density:     moderate-high
Spatial complexity:      moderate
```

Reference pressures:

- ~6 Chapters;
- accepted history;
- current Chapter;
- Book progress;
- pending story updates;
- recent changes;
- next planned work;
- Structure drift;
- resume after several days away.

### Product question

> **Can the author reopen Auteur after several days and immediately understand
> the Book, what changed, what matters now, and what to do next?**

This is the experience-side companion to Narrative Frontier:

> **F2 — Small-Book Longitudinal Coherence**

### Likely needs, to be discovered rather than prebuilt

Possible pressures may warrant:

- Book home / orientation;
- Current work;
- Story so far;
- Needs attention;
- Chapter progression;
- Recent changes;
- Continue writing.

These are hypotheses, not pre-authorized components.

### Current disposition

**RECOMMENDED NEXT EXPERIENCE FRONTIER if #305/#310/#313 reaffirm the current product model.**

X3 should be qualified alongside F2 using the same controlled Book.

---

## X4 — Multi-Thread Workspace

### Experience profile

```text
Decision density:        high
Workflow branching:      moderate-high
State load:              high
Interaction horizon:     Book
Mode switching:          high
Expertise range:         broad
Information density:     high
Spatial complexity:      moderate-high
```

Reference pressures:

- 8–12 meaningful characters;
- 3–4 subplots;
- several relationships;
- multiple locations;
- 2–3 factions;
- several active story questions.

### Product question

> Can the author focus on one relevant thread without losing orientation to the
> whole Book?

### Likely failure classes

- every character visible everywhere;
- no distinction between active and dormant threads;
- excessive navigation;
- attention list becomes noise;
- relationship/plot context becomes visually flat.

Possible future responses may include filtering, focus views, better contextual
retrieval, or more structured navigation.

Do not build them before the frontier proves the need.

---

## X5 — Deep Narrative Workspace

### Experience profile

```text
Decision density:        high
Workflow branching:      high
State load:              very high
Interaction horizon:     Book
Mode switching:          high
Expertise range:         advanced needs increase
Information density:     high
Spatial complexity:      high
```

Reference pressures:

- secrets;
- false beliefs;
- revelation timing;
- foreshadowing;
- complex continuity;
- multiple interpretations;
- substantial revisions.

### Product question

> Can deep story information remain inspectable without turning Auteur into a
> database administration tool?

Potential future visualization pressure may include:

- knowledge differences;
- causal chains;
- relationship evolution;
- revelation timelines;
- alternative interpretations.

Again, visualizations are admitted only after the experience frontier exposes
the recurring need.

---

## X6 — Professional Long-Form Workspace

### Experience profile

```text
Decision density:        high
Workflow branching:      very high
State load:              very high
Interaction horizon:     months
Mode switching:          very high
Expertise range:         beginner escape hatches + professional depth
Information density:     very high
Spatial complexity:      high
```

Reference pressures:

- ~30 Chapters;
- ~15 important characters;
- multiple POVs;
- months of writing;
- large revision cycles;
- many accepted and pending changes.

### Product question

> Can Auteur become a durable professional creative environment without losing
> the simple mental model established at X0–X2?

A possible spatial model might eventually become:

```text
navigation rail
+ main editor/workspace
+ contextual side panel
+ optional inspector
```

This is not a requirement yet.

It is an example of the kind of spatial architecture X6 pressure may justify.

---

## X7 — Series Workspace

### Experience profile

```text
Decision density:        very high
Workflow branching:      very high
State load:              extreme
Interaction horizon:     multiple Books / years
Mode switching:          very high
Expertise range:         broad
Information density:     extreme
Spatial complexity:      very high
```

Questions include:

- Which Book am I currently working in?
- What is Series-level versus Book-level?
- Which old promise matters now?
- How did this character change between Books?
- Which facts belong to which historical stage?
- What is dormant versus active continuity?

### Product question

> Can the author reason about a Series without having to operate a continuity
> database manually?

Backend Series concepts existing is not proof of X7 product readiness.

---

# 7. Narrative × Experience Frontier Matrix

The two roadmaps coordinate but do not form a rigid one-to-one ladder.

| Narrative frontier | Typical experience pressure |
| --- | --- |
| **F0 — Coherent Scene** | **X0 — Single-Task Clarity** |
| **F1 — Messy Discovery** | **X1–X2 — Guided + Reversible Exploration** |
| **F2 — Small-Book Longitudinal Coherence** | **X3 — Persistent Book Workspace** |
| **F3 — Multi-Thread Book** | **X4 — Multi-Thread Workspace** |
| **F4 — Narrative Depth** | **X5 — Deep Narrative Workspace** |
| **F5 — Evolving Long Book** | **X5–X6 — Deep / Professional Workspace** |
| **F6 — Complex Long Book** | **X6 — Professional Long-Form Workspace** |
| **F7 — Series** | **X7 — Series Workspace** |

This matrix is diagnostic, not deterministic.

A narrative frontier and experience frontier may fail independently.

---

# 8. Independent pass/fail examples

## Example A — Narrative PASS / Experience FAIL

Six-Chapter Book:

- Chapter 5 correctly remembers Chapter 1;
- accepted history is accurate;
- continuity composition works.

But the author opens Auteur and sees:

- seven cards;
- four warnings;
- three pending story updates;
- Story core;
- Structure;
- Chapter progress;
- continuity diagnostics.

They cannot tell what to do.

Result:

```text
F2 narrative capability: PASS

X3 experience capability: FAIL
```

Correct response:

> improve Book orientation / information architecture / prioritization

Not:

> redesign the continuity model.

## Example B — Experience PASS / Narrative FAIL

The Book Home clearly presents:

> Continue Chapter 5

but Chapter 5 generation forgets that Sister Beatrice joined Miller in Chapter
1.

Result:

```text
X3 experience capability: PASS

F2 narrative capability: FAIL
```

Correct response:

> repair context composition / longitudinal continuity

Not:

> redesign the interface.

## Example C — Shared boundary failure

At 12 characters:

- backend remembers all 12;
- UI shows all 12 everywhere;
- prompt context includes all 12 even when irrelevant.

Diagnosis:

```text
Narrative memory:        PASS
Narrative relevance:     FAIL
UX information relevance: FAIL
UI density:              FAIL
```

Correct response may require both:

- better contextual relevance;
- filtered product projection.

Not merely “make the sidebar prettier.”

---

# 9. UX versus UI failure taxonomy

Before changing the product, classify the failure.

## UX failures

### UX-1 — Mental model

The author does not understand what Auteur is asking or what a concept means.

### UX-2 — Workflow

The author understands the goal but must perform excessive or awkward
intermediate actions.

### UX-3 — Information architecture

The right information/capability exists but is organized in the wrong conceptual
place.

### UX-4 — Navigation / orientation

The author cannot tell where they are, where something lives, or how to return
to their work.

### UX-5 — Interaction semantics

A control's meaning or consequence is unclear, surprising, or inconsistent.

### UX-6 — Progressive disclosure

The product exposes too much too early, or hides necessary depth too aggressively.

### UX-7 — Re-entry / continuity

The author returns after time away and cannot reconstruct the current state or
next useful action.

## UI failures

### UI-1 — Visual hierarchy

The most important information/action does not visually dominate.

### UI-2 — Information density

Too much competing information occupies the surface.

### UI-3 — Spatial layout

The arrangement does not support the task or relationships among information.

### UI-4 — State feedback

The author cannot tell whether something is saved, working, accepted, stale,
loading, blocked, or changed.

### UI-5 — Responsive behavior

The surface degrades materially across available viewport sizes.

### UI-6 — Accessibility

Controls, focus, semantics, contrast, labels, or assistive-technology behavior
are insufficient.

### UI-7 — Design-system consistency

Equivalent concepts/actions are presented inconsistently enough to increase
cognitive load or error risk.

---

# 10. Lowest-correct-layer UX/UI intervention

Example:

> “I don't understand why I need to decide this.”

Likely:

```text
UX-1 mental model
or
UX-2 workflow
```

Changing typography alone is unlikely to solve it.

Example:

> “I know I need Chapter 7, but I cannot find it.”

Likely:

```text
UX-3 information architecture
or
UX-4 navigation
or
UI-1 visual hierarchy
```

Do not invent a new narrative concept.

Example:

> “The interface is clear, but all characters appear in every context.”

Could be:

```text
narrative relevance
+
UX information architecture
+
UI information density
```

Diagnose before patching.

---

# 11. Experience frontier qualification loop

## Step 1 — select paired frontier

Record:

- narrative frontier F0–F7;
- experience frontier X0–X7;
- Narrative Stress profile;
- Experience Stress profile;
- exact user journey;
- exact product claims under test.

## Step 2 — run the complete author scenario

Do not test one isolated screen when the claim concerns re-entry, long-form
orientation, or cross-mode coherence.

## Step 3 — identify the first meaningful experience failure

Examples:

- author cannot determine the primary next action;
- reopening the Book gives no useful orientation;
- story-update choices overwhelm drafting;
- advanced controls obscure Beginner work;
- the author repeatedly navigates between distant surfaces;
- information density makes important warnings indistinguishable.

## Step 4 — classify

Classify as:

- narrative capability;
- UX mental model;
- UX workflow;
- UX information architecture;
- UX navigation/orientation;
- UX interaction semantics;
- UX progressive disclosure;
- UX re-entry/continuity;
- UI visual hierarchy;
- UI density;
- UI spatial layout;
- UI state feedback;
- UI responsive behavior;
- UI accessibility;
- UI design-system consistency.

Multiple classes may be involved.

## Step 5 — repair the lowest correct layer

Do not fix a UI problem by adding a domain subsystem.

Do not fix a narrative-context failure by rearranging cards.

## Step 6 — rerun the same paired frontier

The frontier scenario is the product qualification.

## Step 7 — advance only when both sides are coherent

A narrative frontier does not advance merely because its backend is correct if
the author experience is unusable.

An experience frontier does not advance merely because the UI looks coherent if
the underlying story behavior is wrong.

---

# 12. Recommended next paired frontier

Current state:

```text
Narrative:
F0 established
F1 mechanically strong; #305/#310 evidence pending

Experience:
X0 established
X1 mechanically strong
X2 mechanically strong; #305 evidence pending
```

After:

```text
#305
+
#310
-> #313 high-order reconciliation
```

if the current product model is reaffirmed, prefer the paired frontier:

```text
F2 — Small-Book Longitudinal Coherence
+
X3 — Persistent Book Workspace
```

Use the same controlled six-Chapter reference Book.

Ask independently:

```text
SYSTEM QUESTION
Does Auteur remember and reason over the Book correctly?

EXPERIENCE QUESTION
Can the author understand and operate that Book easily?
```

This paired qualification should determine whether the next build belongs to:

- narrative context composition;
- relevance;
- workflow;
- Book orientation;
- navigation;
- information architecture;
- visual density;
- another lower correct layer.

Do not preselect “Book Dashboard” as the implementation before observing the
failure.

---

# 13. Relationship to progressive disclosure

The Experience Frontier does not replace the existing four-depth product
compression contract.

It stress-tests whether that contract survives scale.

At higher frontiers, continue preferring:

```text
Level 0 — Where am I? What should I do?
Level 1 — Why does it matter?
Level 2 — Evidence / alternatives / blockers
Level 3 — Raw artifacts / provenance / diagnostics
```

If a higher frontier seems to require putting Level-2/3 detail permanently on
the primary surface, first ask whether:

- relevance selection is weak;
- orientation is weak;
- navigation is weak;
- contextual access would solve the need.

Do not abandon progressive disclosure merely because internal state grew.

---

# 14. Relationship to contextual modes

Experience frontiers must preserve the Unified Author Experience modes:

- Creative;
- Guidance;
- Continuity;
- Deep control.

Scale should improve transitions between these modes rather than create separate
products for each.

A Book-scale workspace should still let the author move:

```text
write
-> ask for guidance
-> inspect one continuity issue
-> make one story decision
-> return to writing
```

without unnecessary global navigation.

---

# 15. Experience anti-roadmap patterns

## UI feature accumulation

```text
sidebar
-> timeline
-> character graph
-> dashboard
-> command palette
```

without frontier evidence.

**Reject.**

## Backend-shaped navigation

Every backend subsystem receives its own top-level screen because it exists.

**Reject.**

## Dashboard reflex

A complex state appears, so immediately build a dashboard.

First ask whether contextual projection solves the problem.

## Visualization reflex

A relationship or timeline can be visualized, therefore it should be.

Visualization is admitted when a recurring author task cannot be served more
simply.

## Density as sophistication

Showing more information is treated as an advanced/professional experience.

**Reject.**

Professional UX should improve relevance and control, not maximize simultaneous
information.

## Beginner lock-in

The interface stays artificially simple even when advanced users need deeper
control.

**Reject.**

Use progressive disclosure.

## Accessibility deferral

Accessibility is postponed until visual architecture “stabilizes.”

**Reject.**

## Aesthetic-only repair

Confusion caused by mental model or workflow is treated as a styling problem.

**Reject.**

---

# 16. Coordinated construction law

The repository now has two high-order construction questions:

```text
NARRATIVE
What deliberately harder story should Auteur survive next?

EXPERIENCE
What deliberately harder author experience should the product carry next?
```

They combine as:

```text
Narrative frontier
+
Experience frontier
-> controlled author scenario
-> first meaningful failure
-> narrative / UX / UI diagnosis
-> lowest correct intervention
-> requalify same paired frontier
```

This is the default construction logic for UX/UI growth.

---

# 17. Compact roadmap

```text
X0 — Single-Task Clarity
        ↓
X1 — Guided First Session
        ↓
X2 — Reversible Creative Exploration
        ↓
      #305 + #310
        ↓
      #313 high-order reconciliation
        ↓
X3 — Persistent Book Workspace
        ↓
X4 — Multi-Thread Workspace
        ↓
X5 — Deep Narrative Workspace
        ↓
X6 — Professional Long-Form Workspace
        ↓
X7 — Series Workspace
```

The arrows represent preferred evidence order, not automatic implementation
authority.

---

# 18. Compact experience construction principle

> **Do not scale the interface because the backend grew. Scale the interface
> when the author experience proves the current interaction model can no longer
> carry the product's complexity.**

And together with the narrative roadmap:

> **Build the smallest narrative, UX, or UI capability required for Auteur to
> survive the next deliberately harder story and author experience.**
