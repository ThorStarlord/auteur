# Auteur Product Evolution Roadmap

**Role:** forward-looking product/repository evolution map.  
**Authority:** advisory; listing an idea here does not authorize implementation.  
**Operational status:** [../STATUS.md](../STATUS.md).  
**Product contract:** [PRD.md](PRD.md) and [../MISSION.md](../MISSION.md).  
**Canonical architecture:** [narrative-architecture.md](narrative-architecture.md).  
**Architecture roadmap:** [architecture-roadmap.md](architecture-roadmap.md).

## Purpose
This document keeps promising directions for evolving Auteur in one place without turning brainstorming into implementation authority. Auteur now has substantial narrative architecture and many capability families; the largest remaining opportunity is increasingly product integration: help an author move from uncertainty to one useful creative decision, understand the recommendation, make a choice, and cross an explicit authority boundary when the story should actually change.

This file answers **“what directions are worth considering?”** `STATUS.md`, approved issues, bounded plans, and qualification records answer **“what are we actually building now?”**

## Strategic Thesis
Default to **product integration before foundational architecture expansion**. The five semantic layers, authority/provenance, transformations, diagnostics/reasoning, StoryIdentity, Structure, Realization/state, Expression workflows, Series continuity, and long-horizon projections already exist in bounded forms.

The next maturation step is to make those capabilities feel like one product:

```text
accepted narrative authority
→ derived context / diagnostics / craft knowledge
→ one bounded author decision
→ recommendation + explanation + trade-offs
→ author response
→ explicit existing story-authority workflow when canon should change
→ accepted narrative authority
```

Admit a new architectural concept only when observed product friction cannot be solved cleanly by existing concepts, workflow, presentation, or reusable craft knowledge.

## Development Rule
Prefer:

```text
real author workflow
→ observed friction
→ bounded product gap
→ classify the owning layer
→ smallest useful intervention
→ verify in the workflow
```

Avoid the default `interesting idea → new ontology/model/subsystem → search for product value later`.

Before authorization, classify the problem as primarily:
- **UX / presentation** — capability exists but is hard to understand or operate;
- **workflow** — existing capabilities do not connect into a coherent author action;
- **craft knowledge** — reusable narrative-design guidance is missing;
- **domain model** — accepted/candidate/derived state cannot express a recurring need;
- **infrastructure** — reliability, portability, performance, packaging, or qualification blocks use.

Choose the smallest correct layer. Do not turn a UX problem into ontology by default.

## Roadmap States
| State | Meaning |
| --- | --- |
| `NOW` | Selected/authorized work; exact progress belongs in `STATUS.md`. |
| `NEXT` | Strong post-milestone candidate, not automatically authorized. |
| `CANDIDATE` | Worth preserving and evaluating. |
| `EVIDENCE-GATED` | Do not implement until the named trigger exists. |
| `DEFERRED` | Intentionally postponed. |
| `REJECTED` | Deliberately declined unless evidence changes. |
| `SHIPPED` | Implemented/merged; exact production state belongs elsewhere. |

These are not release states:

```text
idea exists ≠ authorized
selected ≠ implemented
implemented ≠ qualified
qualified ≠ released
```

## NOW — Decision-Oriented Tutor M1
**State:** `NOW`

The current selected frontier is the bounded Decision-Oriented Tutor M1. Exact issue state belongs in `STATUS.md`.

```text
0006 safe advisory sessions
→ 0007 root Tutor workflow
→ 0008 authority/staleness boundary tests
→ 0009 production Tutor documentation
```

Non-negotiable M1 contract:
- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- Tutor responses do not themselves accept StoryIdentity, rewrite canon, update a blueprint, or apply Structure repair.
- Canonical changes continue through existing explicit author-authority paths.

Do not expand M1 with speculative learning models, Series reasoning, causal ontology, or automatic repair.

## NEXT — Beginner Decision Golden Path
**State:** `NEXT`

After M1 is complete and qualified, run one real beginner-style project through:

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
→ next useful decision
```

Capture friction such as: unclear action after `tutor choose`; irrelevant next decision; excessive internal terminology; competing subsystem priorities; confusion between advice and authority; or manual reconstruction of information Auteur already stores. Select the next bounded change from observed friction, not from roadmap order alone.

## NEXT — Decision-to-Authority Handoff
**State:** `NEXT` after Golden Path evidence.

Likely question: **“I chose the Tutor recommendation. What do I do to actually change the story?”**

A bounded handoff could explain which authoritative artifacts are affected and which **existing** workflow owns the change:

```text
Tutor response
→ derived Decision Handoff
→ affected accepted commitments/plans
→ existing authority workflow
→ explicit author confirmation there
```

Guardrails: the handoff is derived/noncanonical; it is not a second acceptance system; it may recommend an Identity/Structure/Realization revision path but must not silently execute it. If existing authority workflows cannot express the change, record that as product evidence before inventing a new one.

## CANDIDATE — Narrative Change Preview
**State:** `CANDIDATE`; promote only after real handoff use shows authors need impact visibility before changing authority-bearing state.

Before an author performs an authoritative revision, Auteur could produce a derived preview of likely consequences using existing provenance, dependency, impact, continuity, and planning machinery.

```text
proposed authoritative change
→ derived change preview
→ affected commitments / plans / realized state
→ downstream artifacts that may become stale, suspect, or contradictory
→ continuity / setup-payoff / planning consequences already evidenced by current systems
→ author decides whether to proceed through the existing authority workflow
```

This is conceptually a narrative `git diff --dry-run`.

Guardrails:
- preview ≠ modification;
- preview output is derived/noncanonical;
- do not create a second mutation path;
- do not claim causal downstream effects where only dependency/impact evidence exists;
- reuse existing impact/provenance contracts before inventing new graph or ontology foundations;
- if existing dependency information is insufficient, record the specific blind spot as evidence rather than silently inferring certainty.

## CANDIDATE — Decision Reassessment / Closed Decision Loop
**State:** `CANDIDATE`; promote only after Decision-to-Authority Handoff exists or equivalent real product evidence appears.

A resolved Tutor interaction should eventually be traceable through the authoritative story change that followed it and then be reassessed against the original decision context:

```text
problem / question
→ Decision Card
→ author response
→ Decision Handoff
→ explicit authoritative revision
→ deterministic / bounded reassessment
→ resolved / still relevant / transformed / new downstream decision
```

The goal is to answer **“Did the story change that followed this decision actually address the reason the decision was surfaced?”** without inventing an opaque creative-quality score.

Guardrails:
- reassessment is not automatic artistic approval;
- a Tutor response does not itself prove the issue was resolved;
- canonical revision history remains owned by existing authority-bearing workflows;
- preserve links from the original card/session to the later accepted revision without turning Tutor sessions into canonical story history;
- represent unresolved or ambiguous outcomes explicitly.

## CANDIDATE — Unified Project Orientation
**State:** `CANDIDATE`; likely after the root Tutor loop and before a broader workspace UI.

Auteur already knows substantial accepted and derived project state. A bounded orientation projection could compose that information into one answer to **“Where am I, what matters now, and what should I decide next?”**

```text
PROJECT NOW

accepted StoryIdentity / Direction
+ current Series / Book / Chapter / Scene scope where known
+ current structural horizon
+ Current Author Intent when present
+ active diagnostics / continuity concerns
+ stale or unresolved decisions
+ planning blockers / impact evidence
+ active Tutor session
→ one prioritized Decision Card or one explicit no-action-needed result
```

Start as a CLI/API projection before designing a broad dashboard. Reuse Global Map/Focus, planning, diagnostics, Decision Cards, and provenance rather than creating a parallel project-state database.

Guardrails:
- orientation is derived/rebuildable, not second canon;
- no opaque global “story health” score;
- show `why this?`, `why now?`, source evidence, currentness, and authority;
- allow “no warranted decision” rather than forcing perpetual intervention;
- expose underlying artifacts progressively for advanced users.

## CANDIDATE — Unified Decision Inbox
**State:** `CANDIDATE`

Use Decision Cards as a common **author-facing integration protocol**, not a new canonical domain model:

```text
Story Discovery ────────┐
Structure diagnostics ──┤
Story Design Packs ──────┤
Series continuity ───────┤
Impact / reconciliation ─┼→ Decision Cards → Tutor
Planning ────────────────┤
Simulation / portfolio ──┘
```

The underlying systems keep their semantics and authority. The inbox answers **“what important decision needs my attention now?”** Required qualities: stable ordering where possible, no opaque creative-quality score, clear blocker/advisory distinctions, visible `why this?`, `why now?`, evidence, consequences, and authority.

Unified Project Orientation may consume this inbox or select from it, but neither concept should become a new canonical narrative layer.

## CANDIDATE — Current Author Intent
**State:** `CANDIDATE`; promote only if real Tutor use reveals relevance friction.

Add a small local/noncanonical statement of what the author is trying to decide now, e.g. “Should the revelation happen in Book 2 or Book 3?”

```text
Current Author Intent
+ accepted narrative state
+ diagnostics / craft knowledge
→ more relevant Decision Card
```

Guardrails: local/noncanonical by default; never silently promoted into accepted Direction; prefer plain-language author input; do not build a universal intent ontology without recurring evidence.

## CANDIDATE — Guided Author Workspace
**State:** `CANDIDATE`; consider after root Tutor semantics and the core decision loop stabilize.

The beginner experience should progressively hide CLI/YAML/Pydantic machinery. A small local browser surface is plausible because Auteur already has browser/session infrastructure.

Minimal shape:

```text
YOUR STORY
current accepted direction

NEXT DECISION
why it matters
recommendation
alternatives / trade-offs
[Explain] [Teach me] [Choose]
```

If Decision-to-Authority Handoff and Change Preview are later qualified, the workspace should project those existing semantics rather than create UI-only mutation behavior.

Advanced disclosure can reveal evidence, provenance, artifacts, diagnostics, and CLI equivalents. Do not start with a broad desktop app, cloud collaboration platform, or new GUI architecture; prove the bounded decision interaction first.

## CANDIDATE — Episode / Serial Entry Progression
**State:** `CANDIDATE`

Bounded Episode 1 Direction work already exists in an open PR. After the Tutor milestone, reconcile it against contemporary `main`, requalify it, and decide whether it remains the smallest useful serial-fiction step.

```text
bounded Episode 1 support
→ real serial use
→ observe need for Episode 2+
→ generalize only from recurring evidence
```

Avoid prematurely inventing a universal `Entry<T>`, Season graph, or sixth semantic scope. Episode remains an entry form inside the existing architecture unless evidence proves otherwise.

## CANDIDATE — Story Design Pack Growth
**State:** `CANDIDATE`, evidence-driven admission.

Story Design Packs are a preferred home for reusable craft knowledge that does not belong in story-instance canon or core ontology. Potential packs: Character Arc, Relationship Arc, Mystery Construction, Romance, Thriller Escalation, Tragedy, Setup & Payoff, Theme, Pacing, Serial Progression.

**Admission rule:** add a pack when repeated real Decision Cards lack the craft knowledge needed to help the author—not merely because a concept can be represented. Prefer one small pack with observed demand over a broad speculative taxonomy.

## CANDIDATE — Existing-Manuscript Reverse Engineering
**State:** `CANDIDATE`; strategically important, but after the guided Decision loop is coherent.

Potential second entry path:

```text
existing manuscript
→ derived/candidate analysis
→ Candidate StoryIdentity + Candidate Structure + observed Realization/state
→ author correction/review
→ explicit acceptance
→ normal Auteur project
```

Core rule: **extraction ≠ canon**. Inferred information remains derived/candidate until explicitly accepted through the owning authority workflow.

## CANDIDATE — Book-Level Reasoning and Editing
**State:** `CANDIDATE`

Book reconciliation exists, but richer Book-scale reasoning/editing remains plausible. Prefer bounded Book-level decisions over automatic manuscript rewrites. Useful questions include duplicate chapter function, stalled character trajectory, mistimed setup/payoff, thematic drift, and consequences of late revision. Reuse existing reasoning/Decision Card contracts where possible instead of creating a parallel advisory system.

## Candidate Evolution Sequence — Not an Approved Queue
This sequence captures the current strongest product-evolution hypothesis if evidence continues to support the guided-decision thesis. It is **not** a dependency guarantee, milestone authorization, or instruction to skip observed evidence.

```text
Decision-Oriented Tutor M1
        ↓
Beginner Decision Golden Path
        ↓
Decision-to-Authority Handoff
        ↓
Narrative Change Preview
        ↓
Decision Reassessment
        ↓
Unified Project Orientation
        ↓
Guided Author Workspace
        ↓
Serial / Episode expansion
```

Interpretation rules:
- each transition still requires real selection/authorization;
- Golden Path evidence may reorder, combine, defer, or reject later candidates;
- Unified Decision Inbox and Current Author Intent are supporting candidates that may be pulled earlier if real relevance/orientation friction warrants them;
- Story Design Pack growth remains demand-driven and can happen opportunistically when a real Decision Card lacks needed craft knowledge;
- engineering hardening runs independently when risk justifies it;
- long-horizon expansion remains subject to its separate campaign evidence gate regardless of this sequence.

## EVIDENCE-GATED — Long-Horizon Expansion
**State:** `EVIDENCE-GATED`

The long-horizon campaign is in prospective native evidence incubation. Do not manufacture another experiment or start these merely because they are plausible:
- universal causal graph;
- automatic narrative relationship extraction;
- generalized relationship/trajectory ontology;
- Guided Series Continuity Review V2;
- 50/100+ entry scale architecture;
- universal setup/payoff ontology;
- generalized epistemic-state system;
- generic graph database.

Re-enter only when the campaign's documented natural evidence trigger is met, then select the smallest capability addressing the observed failure.

## DEFERRED — Adaptive Learning / Writer Skill Model
**State:** `DEFERRED`

Tutor depth can teach, explain, challenge, or quiz without persistent writer-skill state. Do not infer proficiency, learning progression, or adaptive curriculum until the basic Tutor proves repeated educational value and a specific need requires persistence. Educational scaffolding and story authority remain separate.

## Engineering Hardening Lane
**State:** `CANDIDATE` maintenance lane; schedule independently when risk/cost justify it.

Promising work: reconcile the open Windows full-suite CI leg; cross-platform deterministic qualification; path/line-ending/locale/timezone isolation; stronger freeze/completeness integrity; sandboxing where external reviewer execution justifies the cost. Hardening should protect product work without opening unrelated infrastructure programs during a bounded milestone.

## Product Evolution Loop
### Level 1 — Author Decision Loop
```text
story state → important decision → guidance → author choice
→ explicit safe story change → updated story state
```

### Level 2 — Product Improvement Loop
```text
run real Author Decision Loop → observe friction
→ select one bounded gap → implement → verify
```

### Level 3 — Repository Evolution Loop
```text
repeated product gaps
→ classify UX / workflow / craft knowledge / domain / infrastructure
→ smallest correct layer → bounded milestone → qualify
```

### Level 4 — Product Thesis Loop
Periodically ask: **“Is helping authors make better long-horizon creative decisions still the strongest organizing product thesis for Auteur?”** Outcomes may be reaffirm, revise, reinterpret, or retire. A thesis change must follow the governance path of durable product documents; it must not occur implicitly through a roadmap item.

## Candidate Selection Criteria
Prefer candidates that answer yes to most of these questions:
1. Does it solve friction observed in a real author workflow?
2. Does it strengthen the author-decision loop?
3. Can existing architecture express it without a new foundation?
4. Is the authority boundary clear?
5. Can it be implemented and qualified as one bounded slice?
6. Does it reduce beginner cognitive load?
7. Does it improve long-horizon coherence or decision relevance?
8. Is its evidence stronger than competing candidates' evidence?

Do not convert this into a false-precision numerical ranking without a concrete future need.

## Document Responsibilities
```text
MISSION.md                     durable purpose / invariants
docs/PRD.md                    product contract
docs/narrative-architecture.md canonical semantic model
docs/architecture-roadmap.md   architecture integrity / extension history
docs/product-evolution-roadmap.md candidate future directions
STATUS.md                      current selected/pending work
issues + bounded plans         implementation contracts
qualification / releases       proof and release claims
```

Historical ADRs, research, experiments, handoffs, qualification records, and campaign documents remain evidence; do not rewrite them to make the current roadmap cleaner.

## Maintenance Rules
Update this roadmap when a repeated friction creates a new candidate, a candidate is selected/deferred/rejected/shipped, evidence changes an admission condition, or the product thesis changes materially. Do **not** update it for every commit or issue transition; those belong in `STATUS.md` and GitHub.

When a candidate becomes active work:
1. record real selection/authorization in the appropriate current-status/planning surface;
2. create bounded issues/specs with explicit scope and authority rules;
3. change roadmap state to `NOW` only when selection is real;
4. after merge/qualification, mark it `SHIPPED` or replace it with the next evidence-driven question.

This keeps Auteur's future visible without allowing future ideas to silently become production scope.
