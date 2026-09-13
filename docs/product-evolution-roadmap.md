# Auteur Product Evolution Roadmap

**Role:** forward-looking product/repository evolution map.  
**Authority:** advisory; listing an idea here does not authorize implementation.  
**Operational status:** [../STATUS.md](../STATUS.md).  
**Product contract:** [PRD.md](PRD.md) and [../MISSION.md](../MISSION.md).  
**Canonical architecture:** [narrative-architecture.md](narrative-architecture.md).  
**Architecture roadmap:** [architecture-roadmap.md](architecture-roadmap.md).

## Purpose
This document keeps promising directions for evolving Auteur in one place without turning brainstorming into implementation authority. Auteur now has substantial narrative architecture and an integrated guided decision loop; future work should be selected from observed author friction rather than continuing the previous sequence automatically.

This file answers **“what directions are worth considering?”** `STATUS.md`, approved issues, bounded plans, and qualification records answer **“what are we actually building now?”**

## Strategic Thesis
Default to **product integration before foundational architecture expansion**. The five semantic layers, authority/provenance, transformations, diagnostics/reasoning, StoryIdentity, Structure, Realization/state, Expression workflows, Series continuity, long-horizon projections, and a bounded guided decision loop already exist in operational forms.

The integrated product loop is now:

```text
accepted narrative authority
→ derived context / diagnostics / craft knowledge
→ one bounded author decision
→ recommendation + explanation + trade-offs
→ author response
→ derived authority handoff
→ concrete noncanonical proposal when supported
→ explicit selection + revision planning + preview
→ explicit existing story-authority workflow
→ bounded reassessment + project orientation
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

## SHIPPED — Decision-Oriented Tutor M1
**State:** `SHIPPED`

The bounded Decision-Oriented Tutor M1 is complete on `main` through PRs #187, #191, #192, and #193.

```text
safe advisory sessions
→ root Tutor workflow
→ authority/staleness boundary tests
→ production Tutor documentation
```

Non-negotiable M1 contract remains:
- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- Tutor responses do not themselves accept StoryIdentity, rewrite canon, update a blueprint, or apply Structure repair.
- Canonical changes continue through existing explicit author-authority paths.

## SHIPPED — Guided Author Decision Loop
**State:** `SHIPPED`

The post-M1 evidence sequence is now integrated and qualified. It began with the Beginner Decision Golden Path, which exposed the missing post-choice authority route, then closed that gap without creating a second acceptance system.

```text
raw premise
→ Story Discovery
→ explicit StoryIdentity acceptance
→ blueprint / Structure
→ Tutor Decision Card
→ explanation + advisory choice
→ derived Decision Handoff
→ Tutor-generated noncanonical Structure proposal
→ explicit proposal inspection / selection
→ revision plan + validation
→ derived Narrative Change Preview
→ explicit Structure revision apply --confirm
→ deterministic / bounded Decision Reassessment
→ dashboard Author Attention
→ Guided Author Workspace V1
```

Delivered capabilities include:
- **Decision-to-Authority Handoff** — routes supported resolved Tutor choices to an existing authority workflow without executing it.
- **Tutor → Structure Proposal Bridge** — creates one schema-valid, unselected, noncanonical concrete proposal while deterministic code owns currentness, IDs, paths, allowed fields, and persistence.
- **Proposal review / selection** — records explicit proposal choice without changing the blueprint.
- **Revision correctness hardening** — proposal-backed planning fails closed on unselected/empty proposals and invalid blueprint replacement cannot fall back to destructive direct YAML write.
- **Narrative Change Preview** — read-only projection over an existing revision plan and existing dependency evidence; no second impact engine.
- **Decision Reassessment** — exact native Structure diagnostic rules can be re-run; Tutor/craft changes return `not_assessable` rather than an invented quality verdict.
- **Unified Project Orientation** — the existing dashboard gains deterministic Author Attention over Tutor sessions, proposals, and revision plans.
- **Full Beginner Decision Loop** — hermetic proof that StoryIdentity remains byte-identical and the blueprint changes only at explicit confirmed Structure application.
- **Guided Author Workspace V1** — local `127.0.0.1`, GET-only browser presentation over dashboard/attention state with no mutation endpoints.

The beginner-facing walkthrough is [guides/guided-author-decision-loop.md](guides/guided-author-decision-loop.md).

### Post-milestone selection rule

Completing this sequence does **not** authorize another package automatically. Run/use the integrated loop and select the next bounded change from concrete friction. If the next problem is discoverability, solve discoverability; if relevance is weak, consider intent/decision-source coverage; if craft guidance is thin, admit a demand-driven Story Design Pack. Do not invent a new semantic layer because the roadmap needs another item.

## CANDIDATE — Unified Decision Inbox / Broader Attention Sources
**State:** `CANDIDATE`

Author Attention currently composes a bounded set of decision artifacts. A broader inbox may be useful if real use shows important decisions from other existing systems are being missed.

Potential sources include:

```text
Story Discovery
Structure diagnostics
Story Design Packs / Tutor
Series continuity
Impact / reconciliation
Planning
Simulation / portfolio
→ Decision Cards / attention projection
```

The underlying systems keep their semantics and authority. The inbox should answer **“what important decision needs my attention now?”** with stable ordering where possible, clear blocker/advisory distinctions, visible evidence/currentness, and no opaque creative-quality score.

Do not create a parallel project-state database; extend the existing projection only when omitted sources produce concrete product friction.

## CANDIDATE — Current Author Intent
**State:** `CANDIDATE`; promote only if real Tutor/orientation use reveals relevance friction.

Add a small local/noncanonical statement of what the author is trying to decide now, e.g. “Should the revelation happen in Book 2 or Book 3?”

```text
Current Author Intent
+ accepted narrative state
+ diagnostics / craft knowledge
→ more relevant Decision Card / attention item
```

Guardrails: local/noncanonical by default; never silently promoted into accepted Direction; prefer plain-language author input; do not build a universal intent ontology without recurring evidence.

## CANDIDATE — Episode / Serial Entry Progression
**State:** `CANDIDATE`, bounded and deliberately separate from general long-horizon expansion.

Historical PR #167 is closed/superseded and must not be transplanted into current `main`. Fresh issue #218 preserves the ratified Episode 1 capability contract for contemporary reconstruction when the serial lane is deliberately selected.

```text
reconcile Episode 1 contract with current Series architecture
→ smallest bounded Episode 1 Direction package
→ qualify on contemporary main
→ real serial use
→ observe whether Episode 2+ is actually needed
```

Non-negotiable boundary:
- Episode 1 is not a sixth canonical scope.
- Canonical scope remains Universe → Series → Book → Chapter → Scene.
- Episode 1 Direction remains a Series-scope, Identity-layer entry-unit Direction artifact for explicitly episodic Series.
- No general Episode 2+, season roadmap, Episode realization, or generalized Book/Episode abstraction follows automatically.

## CANDIDATE — Story Design Pack Growth
**State:** `CANDIDATE`, evidence-driven admission.

Story Design Packs are a preferred home for reusable craft knowledge that does not belong in story-instance canon or core ontology. Potential packs: Character Arc, Relationship Arc, Mystery Construction, Romance, Thriller Escalation, Tragedy, Setup & Payoff, Theme, Pacing, Serial Progression.

**Admission rule:** add a pack when repeated real Decision Cards lack the craft knowledge needed to help the author—not merely because a concept can be represented. Prefer one small pack with observed demand over a broad speculative taxonomy.

## CANDIDATE — Existing-Manuscript Reverse Engineering
**State:** `CANDIDATE`; strategically important now that the guided decision loop is coherent.

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
The previously hypothesized guided-decision sequence through Workspace V1 is now complete. The next shape is intentionally branching rather than linear:

```text
SHIPPED GUIDED DECISION LOOP
        ↓
observe real author friction
        ├─ discoverability / orientation UX
        ├─ broader decision-source coverage
        ├─ Current Author Intent
        ├─ demand-driven Story Design Packs
        ├─ Existing-Manuscript Reverse Engineering
        ├─ Book-Level Reasoning / Editing
        └─ bounded Episode 1 reconstruction when deliberately selected
```

Interpretation rules:
- evidence may reorder, combine, defer, or reject candidates;
- no branch becomes `NOW` merely because it appears here;
- engineering hardening runs independently when risk justifies it;
- broader long-horizon expansion remains subject to its separate campaign evidence gate regardless of this map.

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

The full Windows Python 3.13 test leg is now integrated alongside Linux 3.11/3.12/3.13 validation and wheel smoke. Remaining hardening candidates include path/line-ending/locale/timezone isolation, stronger freeze/completeness integrity, and sandboxing where external reviewer execution justifies the cost. Hardening should protect product work without opening unrelated infrastructure programs during a bounded milestone.

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
