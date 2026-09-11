# Auteur Product Evolution Roadmap

**Role:** forward-looking product/repository evolution map.  
**Authority:** advisory planning document; entries here do not authorize implementation.  
**Operational status:** [../STATUS.md](../STATUS.md).  
**Durable product contract:** [PRD.md](PRD.md) and [../MISSION.md](../MISSION.md).  
**Canonical domain architecture:** [narrative-architecture.md](narrative-architecture.md).  
**Architecture-specific roadmap:** [architecture-roadmap.md](architecture-roadmap.md).

## Purpose

This document keeps promising directions for evolving Auteur in one place without
turning brainstorming into implementation authority.

It exists because Auteur now has substantial narrative architecture and many
capability families, while the largest remaining opportunity is increasingly
product integration: helping an author move from uncertainty to one useful
creative decision, understand the recommendation, make a choice, and cross an
explicit authority boundary when the story should actually change.

This file answers:

> What product/repository directions are worth considering after or alongside the
> currently authorized work?

It does **not** answer:

> What is being implemented right now?

Use `STATUS.md`, approved issues, bounded implementation plans, and qualification
records for that.

## Strategic Thesis

Auteur should default to **product integration before foundational architecture
expansion**.

The system definition is already substantial: five semantic layers, explicit
artifact authority, provenance, transformations, diagnostics/reasoning,
StoryIdentity, Structure, Realization/state, Expression workflows, Series
continuity machinery, and long-horizon projections all exist in bounded forms.

The next maturation step is to make those capabilities feel like one product:

```text
accepted narrative authority
        ↓
derived context / diagnostics / craft knowledge
        ↓
one bounded author decision
        ↓
recommendation + explanation + trade-offs
        ↓
author response
        ↓
explicit existing story-authority workflow when canon should change
        ↓
accepted narrative authority
```

A new architectural concept should be admitted only when observed product
friction cannot be solved cleanly by existing concepts, workflow, presentation,
or reusable craft knowledge.

## Development Rule

Prefer this loop:

```text
real author workflow
        ↓
observed friction
        ↓
bounded product gap
        ↓
classify the owning layer
        ↓
implement the smallest useful intervention
        ↓
verify in the workflow
```

Avoid this default:

```text
interesting representable idea
        ↓
new ontology / model / subsystem
        ↓
search for a product use later
```

### Owning-layer classification

Before authorizing a roadmap candidate, decide whether the problem is primarily:

- **UX / presentation** — the capability exists but the author cannot understand or operate it;
- **workflow** — existing capabilities do not connect into a coherent author action;
- **craft knowledge** — the system lacks reusable narrative-design guidance;
- **domain model** — accepted/candidate/derived narrative state cannot express a repeatedly observed need;
- **infrastructure** — reliability, portability, performance, packaging, or qualification blocks use.

Choose the smallest correct layer. Do not promote a UX problem into ontology by
default.

## Roadmap State Vocabulary

Every item in this document should use one of these states:

| State | Meaning |
| --- | --- |
| `NOW` | Currently selected/authorized work. Exact progress belongs in `STATUS.md`. |
| `NEXT` | Strong candidate for selection immediately after the current milestone, but not automatically authorized. |
| `CANDIDATE` | Plausible direction worth preserving and evaluating. |
| `EVIDENCE-GATED` | Do not implement until the named evidence/trigger exists. |
| `DEFERRED` | Intentionally postponed; not a current priority. |
| `REJECTED` | Considered and deliberately declined unless the underlying evidence changes. |
| `SHIPPED` | Implemented and merged; use `STATUS.md`/release records for exact production state. |

These states are not release states.

```text
idea exists ≠ authorized
selected ≠ implemented
implemented ≠ qualified
qualified ≠ released
```

## NOW — Decision-Oriented Tutor M1

**State:** `NOW`

The current selected frontier is the bounded Decision-Oriented Tutor M1. The
exact issue state and current `main` boundary belong in `STATUS.md`.

Current dependency sequence:

```text
0006 safe advisory sessions
  → 0007 root Tutor workflow
  → 0008 authority/staleness boundary tests
  → 0009 production Tutor documentation
```

The M1 invariant is non-negotiable:

- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- A Tutor response does not itself accept StoryIdentity, rewrite canon, update a
  blueprint, or apply a Structure repair.
- Canonical change continues through existing explicit story-authority paths.

Do not expand M1 with speculative learning models, Series reasoning, causal
ontology, or automatic repair.

## NEXT — Beginner Decision Golden Path

**State:** `NEXT`

After M1 is complete and qualified, exercise one real beginner-style project
through the integrated product loop:

```text
raw premise
→ Story Discovery
→ explicit StoryIdentity acceptance
→ lightweight Structure
→ diagnostic / craft question
→ Tutor Decision Card
→ explanation / alternatives
→ author response
→ explicit authority-bearing story change where appropriate
→ derive the next useful decision
```

### Why

Individual subsystems can be correct while the overall experience remains
fragmented. This golden path should test whether Auteur now feels like one
coherent product.

### Evidence to collect

Record concrete friction such as:

- author does not know what to do after `tutor choose`;
- the next decision is technically valid but irrelevant to current intent;
- terminology exposes too much internal machinery;
- multiple subsystems compete for attention;
- the author cannot tell advice from authority;
- the author must manually reconstruct information Auteur already stores.

Select the next bounded product change from observed friction rather than from
this roadmap's candidate order alone.

## NEXT — Decision-to-Authority Handoff

**State:** `NEXT` after evidence from the Beginner Decision Golden Path.

Likely product question:

> I chose the Tutor recommendation. What do I do to actually change the story?

A bounded handoff could translate an advisory Tutor response into an explanation
of the affected authoritative artifacts and the **existing** workflow required
to change them.

Conceptual shape:

```text
Tutor response
        ↓
derived Decision Handoff
        ↓
which accepted commitments/plans would be affected?
        ↓
which existing authority workflow owns the change?
        ↓
explicit author confirmation there
```

### Guardrails

- The handoff is derived/noncanonical.
- It must not become a second acceptance system.
- It may recommend an existing Identity/Structure/Realization revision path but
  must not silently execute authority-bearing changes.
- If no existing authoritative workflow can express the desired change, record
  that as product evidence before inventing a new one.

## CANDIDATE — Unified Decision Inbox

**State:** `CANDIDATE`

Make Decision Cards a common **author-facing integration protocol**, not a new
canonical domain model.

Potential producers include:

```text
Story Discovery ─────────┐
Structure diagnostics ───┤
Story Design Packs ───────┤
Series continuity ────────┤
Impact / reconciliation ──┼→ Decision Cards → Tutor
Planning ─────────────────┤
Simulation / portfolio ───┘
```

The underlying subsystems keep their own semantics and authority. The inbox
simply gives the author one place to answer:

> What important decision needs my attention now?

### Required qualities

- deterministic/stable ordering where possible;
- no opaque "creative quality" score;
- clear blocker/importance/advisory distinctions;
- `why this?`, `why now?`, evidence, consequences, and authority visible;
- no subsystem gains story authority by emitting a Decision Card.

## CANDIDATE — Current Author Intent

**State:** `CANDIDATE`, promote only if real Tutor use demonstrates relevance
friction.

Add a small local/noncanonical expression of what the author is trying to decide
right now, for example:

> Should the revelation happen in Book 2 or wait until Book 3?

Potential role:

```text
Current Author Intent
        +
accepted narrative state
        +
derived diagnostics / craft knowledge
        ↓
more relevant Decision Card
```

### Guardrails

- local/noncanonical by default;
- never silently promoted into story intent or accepted Direction;
- no universal intent ontology unless repeated evidence demands one;
- prefer plain-language author input over elaborate schema expansion.

## CANDIDATE — Guided Author Workspace

**State:** `CANDIDATE`; consider after root Tutor semantics are stable.

The primary creative-beginner experience should eventually hide CLI/YAML/Pydantic
machinery until it is useful. A small local browser surface is a plausible next
presentation layer because Auteur already contains browser/session infrastructure
for interactive genre workflows.

A minimal workspace could emphasize:

```text
YOUR STORY
current accepted direction

NEXT DECISION
why it matters
recommendation
alternatives / trade-offs
[Explain] [Teach me] [Choose]
```

Advanced disclosure can reveal evidence, provenance, canonical artifacts,
diagnostics, and CLI equivalents.

Do not begin with a broad desktop application, cloud collaboration platform, or
new GUI architecture. First prove the bounded decision interaction.

## CANDIDATE — Episode / Serial Entry Progression

**State:** `CANDIDATE`

There is already bounded Episode 1 Direction work in an open PR. After the
current Tutor milestone, reconcile that work against contemporary `main`,
requalify it, and decide whether it remains the smallest useful step toward
serial fiction.

Prefer:

```text
bounded Episode 1 support
→ real serial use
→ observe need for Episode 2+
→ generalize only from recurring evidence
```

Avoid prematurely inventing a universal `Entry<T>`, Season graph, or sixth
semantic scope. Episode remains an entry form inside the existing architecture
unless evidence proves otherwise.

## CANDIDATE — Story Design Pack Growth

**State:** `CANDIDATE`, evidence-driven admission.

Story Design Packs are a preferred place for reusable craft knowledge that does
not belong in story-instance canon or the core ontology.

Potential packs include:

- Character Arc;
- Relationship Arc;
- Mystery Construction;
- Romance;
- Thriller Escalation;
- Tragedy;
- Setup & Payoff;
- Theme;
- Pacing;
- Serial Progression.

### Admission rule

Add a new Story Design Pack when repeated real Decision Cards lack the craft
knowledge required to help the author—not merely because a writing concept can
be represented.

Prefer one small pack with observed demand over a broad speculative taxonomy.

## CANDIDATE — Existing-Manuscript Reverse Engineering

**State:** `CANDIDATE`, strategically important but not before the guided
Decision loop is coherent.

Potential second entry path:

```text
existing manuscript
        ↓
derived / candidate analysis
        ↓
Candidate StoryIdentity
Candidate Structure
observed Realization/state
unresolved questions / diagnostics
        ↓
author correction and review
        ↓
explicit acceptance
        ↓
normal Auteur project
```

Core rule:

```text
extraction ≠ canon
```

Inferred information remains derived/candidate until explicitly accepted through
the owning authority workflow.

## CANDIDATE — Book-Level Reasoning and Editing

**State:** `CANDIDATE`

Book reconciliation exists, but richer Book-scale reasoning/editing remains a
plausible maturity step. The preferred author-facing output should be bounded
Book-level decisions rather than automatic manuscript rewrites.

Candidate questions include:

- Are multiple chapters performing the same structural function?
- Has a character trajectory stalled across the Book?
- Are setups/payoffs missing or mistimed?
- Is thematic progression coherent?
- Does a late revision invalidate earlier assumptions?

Where possible, express findings through existing reasoning/Decision Card
contracts rather than creating a parallel Book advisory system.

## EVIDENCE-GATED — Long-Horizon Expansion

**State:** `EVIDENCE-GATED`

The long-horizon campaign currently uses prospective native evidence incubation.
Do not manufacture another experiment or promote speculative architecture from
this roadmap.

Do not start these merely because they are plausible:

- universal causal graph;
- automatic narrative relationship extraction;
- generalized relationship/trajectory ontology;
- Guided Series Continuity Review V2;
- 50/100+ entry scale architecture;
- universal setup/payoff ontology;
- generalized epistemic-state system;
- generic graph database.

Re-enter this area only when the campaign's documented natural evidence trigger
is met, then select the smallest capability that addresses the observed failure.

## DEFERRED — Adaptive Learning / Writer Skill Model

**State:** `DEFERRED`

Tutor depth can teach, explain, challenge, or quiz without creating a persistent
writer-skill model. Do not infer learning progression, proficiency, or adaptive
curriculum until the basic Tutor proves repeated educational value and a
specific product need requires persistence.

Educational scaffolding and story authority must remain separate even if this is
revisited later.

## Engineering Hardening Lane

**State:** `CANDIDATE` maintenance lane; schedule independently from product
feature selection when risk/cost justify it.

Promising work includes:

- reconcile the open full-suite Windows CI leg;
- cross-platform deterministic qualification;
- path/line-ending/locale/timezone isolation;
- stronger freeze/completeness qualification integrity;
- sandboxing where external reviewer execution justifies the cost.

Engineering hardening should protect product work without becoming a reason to
open unrelated infrastructure programs during a bounded product milestone.

## Product Evolution Loop

Auteur should maintain four nested loops.

### Level 1 — Author Decision Loop

```text
story state
→ important decision
→ guidance
→ author choice
→ explicit safe story change
→ updated story state
```

### Level 2 — Product Improvement Loop

```text
run real Author Decision Loop
→ observe friction
→ select one bounded product gap
→ implement
→ verify
```

### Level 3 — Repository Evolution Loop

```text
repeated product gaps
→ classify: UX / workflow / craft knowledge / domain / infrastructure
→ choose smallest correct layer
→ define bounded milestone
→ qualify
```

### Level 4 — Product Thesis Loop

Periodically reassess:

> Is helping authors make better long-horizon creative decisions still the
> strongest organizing product thesis for Auteur?

Possible outcomes are **reaffirm**, **revise**, **reinterpret**, or **retire** a
product thesis. A thesis change should update the durable product documents
through their own governance path; it should not happen implicitly through a
roadmap candidate.

## Candidate Selection Criteria

When selecting the next roadmap item, prefer candidates that score well on these
qualitative questions:

1. Does it solve friction observed in a real author workflow?
2. Does it strengthen the core author-decision loop?
3. Can existing architecture express it without a new foundational subsystem?
4. Is the authority boundary clear?
5. Can it be implemented and qualified as one bounded slice?
6. Does it reduce beginner cognitive load?
7. Does it improve long-horizon coherence or decision relevance?
8. Is the evidence stronger than the competing candidates' evidence?

Do not turn this into a false-precision numerical ranking system unless a future
workflow specifically requires one.

## Relationship to Other Documents

Use repository documents for distinct purposes:

```text
MISSION.md
  why Auteur exists; durable invariants

PRD.md
  product contract and primary-user requirements

narrative-architecture.md
  canonical semantic architecture

architecture-roadmap.md
  architecture integrity and architecture-specific extension history

product-evolution-roadmap.md
  candidate product/repository directions

STATUS.md
  what is actually current / selected / pending now

issues + bounded plans
  exact implementation contract

qualification / release records
  what was proven and shipped
```

Historical ADRs, research, experiments, handoffs, qualification records, and
campaign documents remain evidence. Do not rewrite them to make the current
roadmap cleaner.

## Maintenance Rules

Update this roadmap when:

- a repeated product friction suggests a new candidate;
- a candidate is selected, deferred, rejected, or shipped;
- evidence changes a candidate's priority or admission condition;
- the product thesis changes materially.

Do **not** update it for every commit or issue status transition. Those belong in
`STATUS.md` and GitHub.

When a candidate becomes active work:

1. record selection/authorization in the appropriate current-status or planning
   surface;
2. create bounded issues/specification with explicit in-scope/out-of-scope and
   authority rules;
3. change this roadmap state to `NOW` only when that selection is real;
4. after merge/qualification, move it to `SHIPPED` or replace it with the next
   evidence-driven question.

This keeps Auteur's future visible without allowing future ideas to silently
become production scope.