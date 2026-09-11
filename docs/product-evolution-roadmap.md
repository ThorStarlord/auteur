# Auteur Product Evolution Roadmap

**Role:** forward-looking product/repository evolution map.  
**Authority:** advisory except where a direction is explicitly selected as `NOW`; exact execution/status remains in [../STATUS.md](../STATUS.md).  
**V1 closure contract:** [v1/v1-product-contract.md](v1/v1-product-contract.md).  
**Product contract:** [PRD.md](PRD.md) and [../MISSION.md](../MISSION.md).  
**Canonical architecture:** [narrative-architecture.md](narrative-architecture.md).  
**Architecture roadmap:** [architecture-roadmap.md](architecture-roadmap.md).

## Purpose

This document keeps promising directions visible without turning brainstorming into implementation authority. Auteur now has substantial narrative architecture and an integrated guided decision loop. The currently selected work is **V1 product/release closure**, not another feature-expansion branch.

This file answers **“what direction is selected, and what other directions are worth preserving?”** `STATUS.md`, bounded plans, PRs, and qualification records answer **“what is actually implemented/qualified now?”**

## Strategic Thesis

Default to **product integration and contract closure before foundational architecture expansion**. The five semantic layers, authority/provenance, transformations, diagnostics/reasoning, StoryIdentity, Structure, Realization/state, Expression workflows, Series continuity, long-horizon projections, and bounded guided decision loop already exist in operational forms.

The integrated loop remains:

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

Admit a new architectural concept only when observed product friction cannot be solved cleanly by existing concepts, workflow, presentation, reusable craft knowledge, or a narrower product claim.

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

Avoid `interesting idea → new ontology/model/subsystem → search for product value later`.

Classify new friction as primarily:

- **UX / presentation** — capability exists but is hard to understand or operate;
- **workflow** — existing capabilities do not connect into a coherent author action;
- **craft knowledge** — reusable narrative-design guidance is missing;
- **domain model** — accepted/candidate/derived state cannot express a recurring need;
- **infrastructure** — reliability, portability, performance, packaging, or qualification blocks use.

Choose the smallest correct layer. Do not turn a UX or claim-boundary problem into ontology by default.

## Roadmap States

| State | Meaning |
| --- | --- |
| `NOW` | Explicitly selected/authorized bounded work; exact progress belongs in `STATUS.md`. |
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

## NOW — Auteur V1.0 Product Closure

**State:** `NOW`  
**Selection:** owner-authorized 2026-09-11.  
**Program record:** [v1/v1-closure-plan.md](v1/v1-closure-plan.md).  
**Support contract:** [v1/v1-product-contract.md](v1/v1-product-contract.md).

The current repository frontier is to close the existing architecture into a bounded, reproducibly qualified `1.0.0` contract. This does **not** authorize another narrative foundation.

Selected closure responsibilities are:

```text
explicit V1 support / claim contract
→ authority/provenance reconciliation for promised artifact families
→ bounded Realization ↔ Expression ownership closure
→ browser beginner control plane over existing authority services
→ provider failure and interruption/recovery hardening
→ realistic hermetic author-journey qualification
→ exact frozen-candidate release qualification
```

The program deliberately chooses scope reduction over speculative architecture where appropriate: Universe is optional/experimental rather than a provenance-normalized V1 vertical; generalized Episode progression and 50/100+ Book scale are outside the V1 claim.

### Stop condition

Stop V1 closure when every capability explicitly promised by the V1 Product Contract has a complete authority-safe path and the exact frozen release candidate satisfies the required qualification matrix. A historical audit item, open issue, research direction, or candidate below is not a V1 blocker unless the V1 Product Contract explicitly says it is.

### Frozen while this program is active

Do not start generalized Episode 2+, universal causal/relationship ontology, automatic story-instance extraction, generic graph database, adaptive writer-skill state, cloud/collaboration, generic workflow engines, speculative Story Design Pack breadth, or very-large-scale optimization merely to make the release appear more complete.

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

The post-M1 evidence sequence is integrated and qualified on its shipped baseline:

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

Delivered baseline capabilities include Decision-to-Authority Handoff, Tutor → Structure Proposal Bridge, explicit proposal review/selection, fail-closed revision continuation, Narrative Change Preview, Decision Reassessment, unified Author Attention, the hermetic Beginner Decision Loop, and the original loopback GET-only Workspace V1.

The selected V1 closure program may extend that Workspace presentation into a bounded Workspace V2 control plane **only by reusing existing application/authority services**. Such extension does not change the shipped authority principle or create a second acceptance system.

See [guides/guided-author-decision-loop.md](guides/guided-author-decision-loop.md).

## CANDIDATE — Unified Decision Inbox / Broader Attention Sources

**State:** `CANDIDATE`

Author Attention currently composes a bounded set of decision artifacts. A broader inbox may be useful if real use shows important decisions from other existing systems are missed.

Potential sources:

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

The underlying systems keep their semantics and authority. Do not create a parallel project-state database; extend the existing projection only when omitted sources produce concrete product friction.

## CANDIDATE — Current Author Intent

**State:** `CANDIDATE`; promote only if real Tutor/orientation use reveals relevance friction.

A small local/noncanonical statement of what the author is trying to decide could improve Decision Card relevance:

```text
Current Author Intent
+ accepted narrative state
+ diagnostics / craft knowledge
→ more relevant Decision Card / attention item
```

Guardrails: local/noncanonical by default; never silently promoted into accepted Direction; prefer plain-language input; do not build a universal intent ontology without recurring evidence.

## CANDIDATE — Episode / Serial Entry Progression

**State:** `CANDIDATE`, deliberately outside V1 closure.

Historical PR #167 is closed/superseded and must not be transplanted into contemporary `main`. Issue #218 preserves the ratified Episode 1 capability contract for future reconstruction when the serial lane is deliberately selected.

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

Story Design Packs are the preferred home for reusable craft knowledge that does not belong in story-instance canon or core ontology. Potential packs include Character Arc, Relationship Arc, Mystery Construction, Romance, Thriller Escalation, Tragedy, Setup & Payoff, Theme, Pacing, and Serial Progression.

**Admission rule:** add a pack when repeated real Decision Cards lack the craft knowledge needed to help the author—not merely because a concept can be represented.

## CANDIDATE — Existing-Manuscript Reverse Engineering

**State:** `CANDIDATE`

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

Book reconciliation exists, but richer Book-scale reasoning/editing remains plausible. Prefer bounded Book-level decisions over automatic manuscript rewrites. Reuse existing reasoning/Decision Card contracts where possible instead of creating a parallel advisory system.

## Post-V1 Candidate Evolution — Not an Approved Queue

```text
V1 CLOSURE / RELEASE EVIDENCE
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

Evidence may reorder, combine, defer, or reject these candidates. None becomes selected merely because it appears here.

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

Tutor depth can teach/explain/challenge without persistent writer-skill state. Do not infer proficiency or build adaptive curriculum until repeated educational use demonstrates a concrete persistence need.

## Engineering Hardening Lane

**State:** partly selected only where the V1 contract requires it.

The V1 closure program selects bounded reliability items that directly affect the release promise: provider failure normalization, interruption recovery, cross-platform semantic/hash/path invariants, exact installed-artifact qualification, and browser action safety. Other hardening—such as OS-enforced sandboxing for optional external reviewer execution—remains a candidate unless the V1 contract is expanded to promise that subsystem.

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

Periodically ask: **“Is helping authors make better long-horizon creative decisions still the strongest organizing product thesis for Auteur?”** Outcomes may reaffirm, revise, reinterpret, or retire the thesis. A thesis change must follow durable product governance and must not occur implicitly through a roadmap item.

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
docs/PRD.md                    product requirements
docs/v1/v1-product-contract.md selected 1.0 support / claim boundary
docs/v1/v1-closure-plan.md     selected closure work and evidence gates
docs/narrative-architecture.md canonical semantic model
docs/architecture-roadmap.md   architecture integrity / extension history
docs/product-evolution-roadmap.md selected direction + preserved candidates
STATUS.md                      current implementation / qualification frontier
issues + bounded plans         implementation contracts
qualification / releases       proof and release claims
```

Historical ADRs, research, experiments, handoffs, qualification records, and campaign documents remain evidence; do not rewrite them to make the current roadmap cleaner.

## Maintenance Rules

Update this roadmap when a repeated friction creates a candidate, a candidate becomes selected/deferred/rejected/shipped, evidence changes an admission condition, the V1 closure selection ends, or the product thesis changes materially. Do not update it for every commit or issue transition.

When the current V1 closure program finishes, return selection authority to observed product evidence before promoting any preserved candidate.
