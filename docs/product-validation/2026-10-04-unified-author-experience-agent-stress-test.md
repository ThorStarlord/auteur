# Unified Author Experience Coding-Agent Stress Test

**Date:** 2026-10-04  
**Status:** controlled coding-agent / product-mechanics evidence  
**Scope:** reduce the remaining uncertainty owned by #305, #310, and #313 without manufacturing human preference or live-provider evidence  
**Branch:** `docs/unified-author-experience-architecture`

## Purpose

The repository already contains substantial evidence about Beginner ergonomics,
Story Discovery, creative discovery, and Premise Fitness. This stress test asks:

> Which remaining Unified Author Experience questions can be answered or
> narrowed without another user study, and which claims still genuinely require
> a human author or real provider?

The goal is not to replace #305 or #310. It is to stop making those evidence
lanes re-prove mechanics that are already established.

## Existing evidence reused

This probe treats the following as prior evidence rather than rerunning it.

### Beginner-flow mechanics

The headless comparison already establishes:

```text
A — corrected pre-compression Beginner     ~22 visible interactions to prose
B — compressed Beginner                    ~8 visible interactions to prose
C — Quick Draft                             2 creative inputs to prose
```

It also establishes:

- Quick Draft performs zero explicit acceptance actions before prose;
- provisional scaffolding stays noncanonical;
- vague POV/location remain unset rather than being invented as schema facts;
- working prose can be edited and reloaded;
- `What did we discover?` is an explicit bridge rather than automatic canon;
- only author-selected discoveries enter shaping;
- exact-draft review freshness is tied to source bytes;
- post-draft choices preserve keep/update, intentional-divergence, and
  revise-to-plan paths.

### Founder / coding-agent Story Discovery evidence

Phase E already contains six founder creative-adjudication cases.

Those cases established useful human/owner evidence that:

- intent-aware Story Discovery can expose meaningful tradeoffs;
- alternatives must be causally distinct rather than rhetorically different;
- maximalism / mixed causation / engine hierarchy are useful author-intent axes;
- craft-teaching rationale matters;
- explicit acceptance preserves author authority.

Phase F then ran five controlled coding-agent regression cases and verified that
the implementation addressed those identified failure modes without claiming
fresh human preference.

### Premise Fitness evidence

The repository also already contains:

- ten Premise Fitness calibration cases;
- a repeated-use coding-agent stress test;
- explicit Story Opportunity Discovery / Premise Fitness / Story Discovery /
  MANA ownership boundaries.

Therefore this probe does **not** rerun premise-fit theory, causal-diversity
testing, or generic interaction-count comparison.

---

# 1. Stress case — author has no stable premise

Author state:

> I know the kinds of stories I like, but I do not yet know what story I want to
> make.

## Candidate product behavior

```text
preferences / influences / unresolved desire
-> optional Story Opportunity Discovery
-> working opportunities
-> optional Premise Fitness if fit tradeoffs matter
-> selected working premise / Discovery Brief
-> normal Auteur entry
```

## Finding

**Mechanically coherent.**

Sending this author directly to Story Discovery would confuse two different
questions:

- what story might be worth making;
- how a selected premise might be designed.

The merged Story Opportunity contract closes that gap without adding canon.

## Disposition

`KEEP` the optional upstream path.

Do not foreground Premise Fitness automatically.

---

# 2. Stress case — stable premise, author wants understanding before prose

Author state:

> I know the premise. Help me understand what kind of story this could become
> before I start writing.

## Candidate product behavior

Foreground:

> **Explore this story**

Then:

```text
interpretation
-> causally distinct Direction candidates
-> tradeoffs
-> Story core / shape
-> planning
-> prose
```

## Finding

**Shape-first is the mechanically correct foreground.**

The author explicitly asked for interpretation and design before prose. Sending
them into Quick Draft would answer a different question.

## Disposition

Foreground **Shape first** when the explicit user goal is understanding,
comparison, architecture, or long-range story shaping.

This is a product-routing decision grounded in expressed intent, not a claim
that authors generally prefer Shape first.

---

# 3. Stress case — stable premise plus strong first-scene impulse

Author state:

> I know the premise and I know the scene I want to write. I do not want to
> decide the whole structure yet.

## Candidate product behavior

Foreground:

> **Start writing now**

Inputs:

- exact premise;
- exact first-scene intent.

Unknowns remain provisional.

## Finding

**Write-first is the mechanically correct foreground.**

Forcing Direction / Story core / Story shape acceptance first would require
upstream commitments the author has explicitly said they are not ready to make.

The current Quick Draft architecture allows prose to produce additional evidence
without granting that prose or its inferred scaffold upstream authority.

## Disposition

Foreground **Write first** when the author has a concrete scene impulse stronger
than their current need for architecture.

Again, this is an intent-routing rule, not a population-level preference claim.

---

# 4. Stress case — intentionally vague premise

Input omits:

- named protagonist;
- genre;
- POV;
- setting.

The author supplies only a first-scene intention.

## Existing mechanical result

The headless implementation already discovered and repaired the schema-pressure
failure that tried to invent POV/location.

The product now permits unresolved fields to remain unresolved while exact author
inputs remain controlling evidence.

## What simulation can establish

The system boundary is correct:

```text
unknown author choice
-> provisional / unknown
-> no fake accepted commitment
```

## What simulation cannot establish

A real provider may still introduce details in ordinary prose.

That is not necessarily a product defect; fiction generation often requires
concrete local detail.

The remaining #310 question is narrower:

> Does the provider introduce details that materially distort the author's stated
> intent or masquerade as commitments forced by Auteur's scaffold?

## Disposition

System/authority question: **settled mechanically**.

Provider semantic-faithfulness question: **still #310**.

---

# 5. Stress case — `What did we discover?`

Draft introduces:

- Sister Beatrice;
- an abandoned seaside convent;
- a changed scene path.

## Existing mechanics

The current design:

- preserves the draft;
- refreshes evidence from the current bytes;
- surfaces heuristic observations;
- selects none by default;
- lets the author choose which observations enter shaping;
- records selected discoveries in a noncanonical handoff;
- skips an empty discovery-confirmation step when there are no discoveries.

## Agent stress question

Can the surface be useful in principle without becoming mandatory
administration?

## Finding

**Yes, structurally.**

The surface has value when it performs a delta function:

```text
what the plan / prior context expected
vs
what the current prose now contains
-> consequential differences only
```

The architecture already avoids the worst failure mode:

```text
heuristic detected X
-> X becomes story fact
```

Instead:

```text
heuristic detected X
-> author may carry X
-> otherwise X stays local to working prose
```

## Remaining uncertainty

Agent simulation cannot establish whether a writer experiences the observations
as insightful or noisy.

That is a #305 human-evidence claim.

## Provisional product rule

Keep the surface only when it has something consequence-bearing to say.

No discovered delta:

```text
-> no extra confirmation ceremony
```

Low-confidence or purely cosmetic observations should remain suppressed or
advanced-only rather than competing with creative momentum.

---

# 6. Stress case — Keep draft & update story

The draft is good, but it diverges from the old plan.

## Current mechanics

```text
Keep draft & update story
-> accept through existing Chapter Expression owner
-> preserve accepted prose
-> create derived / noncanonical update proposals
-> route proposals toward the lowest sufficient owners
```

It does not require all upstream systems to synchronize before the writer can
keep the prose.

## Finding

**Mechanical momentum preservation is supported.**

The operation avoids two high-cost alternatives:

1. discard useful prose merely because it surprised the plan;
2. silently rewrite Story Identity / Structure to match the prose.

## Remaining uncertainty

Whether this *feels* like creative momentum rather than data administration is a
human question.

## Disposition

Mechanical/product architecture: `KEEP`.

Subjective momentum claim: remains #305.

---

# 7. Stress case — when should continuity interrupt?

Assume Chapter 1 is accepted.

The prose introduced a new location and side character. Structure has not yet
been updated.

## Candidate A — always interrupt

```text
any unresolved update
-> block next writing step
```

### Failure

This converts continuity into synchronization bureaucracy.

Additive discoveries that do not make the next action false do not justify a
hard stop.

## Candidate B — never interrupt

```text
all divergence remains ambient forever
```

### Failure

Dependent generation can become actively misleading when accepted events and
the current plan contradict each other materially.

## Selected rule

Continuity should interrupt only when unresolved state would make the next
decision materially untrustworthy.

Examples:

### Ambient

- new compatible side character;
- new compatible location;
- added detail that future work can consume from accepted prose;
- pending update whose consequence does not affect the next action.

### Interrupt

- two accepted facts are mutually exclusive;
- the next planned scene depends on an event that accepted prose explicitly
  prevented;
- protagonist / governing engine / major relationship commitment changed and the
  next planning step would otherwise reason from the wrong story;
- an authority-bearing acceptance requires the contradiction to be resolved.

## Disposition

This question is **answerable structurally without new user evidence**.

Selected law:

> **Ambient by default; interrupt only at the first point where unresolved
> divergence would materially mislead a dependent decision or violate an
> existing authority/validation boundary.**

Human evidence may later refine presentation timing, but not this ownership law.

---

# 8. Stress case — can the author mental model hide internal layers?

The proposed author vocabulary is:

- Story idea;
- Story opportunity when needed;
- What Auteur sees;
- Direction;
- Story core;
- Story shape;
- working draft;
- accepted story;
- story updates;
- continuity;
- deep details.

The internal vocabulary remains:

```text
Ontology
Identity
Structure
Realization
Expression
proposals
staleness
provenance
reconciliation
...
```

## Agent inspection finding

The product projection is internally coherent without exposing the five-layer
model in the default path.

The same author concept can route to the correct internal owner while preserving
authority distinctions.

## What this establishes

It establishes **architectural feasibility** of the simplified mental model.

## What it does not establish

It does not prove that an unfamiliar writer understands those labels on first
contact.

That comprehension claim remains #305.

---

# 9. Stress case — Auteur versus Markdown + capable general-purpose LLM

A plain Markdown/chat workflow can plausibly reach prose with less ceremony than
Auteur.

That is a real competitive advantage of the baseline and should not be hidden.

## Capability differential Auteur can establish mechanically

Auteur adds explicit machinery for:

- accepted versus provisional story state;
- source-currentness and provenance;
- Story Discovery alternatives / tradeoffs;
- deterministic authority boundaries;
- stale-review detection tied to exact draft content;
- lowest-sufficient-owner update proposals;
- accepted-history reconstruction;
- continuity across Chapters / Books / Series;
- explicit intentional divergence;
- planned consequences versus realized events;
- deterministic state and validation contracts.

Markdown + a general conversational model may imitate some of these behaviors in
conversation, but does not inherently provide Auteur's durable typed authority
and continuity model.

## Finding

**Differential capability is established. Differential felt value is not.**

The unresolved question is not:

> Does Auteur do anything a plain chat does not do?

It clearly does.

The unresolved question is:

> Do authors value those capabilities enough to justify the additional product
> machinery and interaction cost?

Only real authors can answer that claim.

## Disposition

Do not use a coding-agent simulation to trigger product-thesis review.

Keep `PRODUCT_THESIS_REVIEW_SIGNAL` reserved for genuine human evidence that
the additional continuity/decision machinery produces insufficient felt value.

---

# 10. Provisional answers to #313 questions

| #313 question | Agent-stress disposition |
| --- | --- |
| Shape first vs write first: when foreground each? | **Provisionally answered.** Route from explicit current author intent: understanding/shaping -> Shape first; concrete scene impulse -> Write first. Keep both. |
| Does Quick Draft preserve intent with real providers? | **Not fully answerable.** Authority/scaffold boundary is mechanically sound; provider semantic fidelity and latency remain #310. |
| Does `What did we discover?` create value or administrative noise? | **Partially answered.** Architecturally useful as consequence-bearing delta with no auto-selection and no empty ceremony; experienced usefulness/noise remains #305. |
| Does `Keep draft & update story` preserve creative momentum? | **Mechanically yes.** It preserves prose and defers synchronization; experienced momentum remains #305. |
| When should continuity guidance interrupt vs remain ambient? | **Answered structurally.** Ambient by default; interrupt when unresolved divergence would materially mislead a dependent decision or cross an existing hard authority/validation boundary. |
| Can authors understand the unified mental model without learning layers? | **Architecturally feasible, human comprehension unproven.** #305 owns first-contact comprehension. |
| Does Auteur create enough value over Markdown + capable LLM? | **Capability differential yes; felt/value differential unknown.** Human comparative evidence remains required. |

---

# 11. What #305 still needs to test

The real-author comparison no longer needs to spend participant time proving
mechanics already covered by repository evidence.

Its irreducibly human questions are:

- Which entry path does the writer naturally want for a given creative state?
- Does the compressed flow feel like help or ceremony?
- Does Quick Draft preserve a sense of ownership?
- Is `What did we discover?` experienced as insight or noise?
- Does `Keep draft & update story` feel like creative help or bookkeeping?
- Are customization / deeper-control escape hatches discoverable when wanted?
- Are story-language labels understood without internal-layer explanation?
- Does continuity support create enough felt value over Markdown + a capable LLM?
- Would the writer continue in Auteur?

Those are the reasons #305 still exists.

Everything else should be pre-verified mechanically before the participant is
involved.

---

# 12. What #310 still needs to test

The live-provider dogfood can also be narrowed.

It does **not** need to re-prove:

- noncanonical Quick Draft authority;
- no pre-prose acceptance;
- provisional unknown handling in state;
- exact-input plumbing;
- discovery handoff authority;
- stale-review mechanics.

It does need to establish:

- actual provider/model latency;
- scene-sizedness;
- fidelity to the exact premise + first-scene intent;
- whether generic provisional defaults visibly leak into prose;
- whether ordinary model invention becomes unwanted commitment pressure;
- whether the prose is concrete/useful enough to react to;
- whether the messy-writer follow-up works with genuinely generated prose rather
  than only controlled text.

---

# 13. Provisional #313 disposition before human/provider evidence

The coding-agent stress test supports the following **provisional**, reversible
position:

```text
KEEP
- two authoring tempos
- unified story-language mental model
- progressive disclosure by perceived author need
- exact-author-input Quick Draft boundary
- explicit working vs accepted distinction
- creative-discovery bridge
- lowest-sufficient-owner routing
- continuity ambient-by-default / interrupt-on-material-dependency law

REVISE / CLARIFY
- route Shape first vs Write first from explicit current author intent
- treat What did we discover? as a consequential delta surface, not a mandatory
  post-draft checklist

DO NOT CLAIM YET
- writer preference
- lower cognitive load
- stronger ownership
- greater creative momentum
- first-contact comprehension
- provider prose quality
- provider intent fidelity
- differential felt value over Markdown + general LLM
```

Absent contrary #305/#310 evidence, the current architecture still makes
**F2 — Small-Book Longitudinal Coherence + X3 — Persistent Book Workspace** the
best provisional next frontier because the unresolved product value question has
shifted from first-screen mechanics toward whether Auteur's continuity machinery
actually pays off across a small Book.

This is a provisional planning implication, not authorization to skip #305,
#310, or #313.

---

# 14. Final evidence disposition

The repository has already done enough synthetic/founder/mechanical work that
another broad simulated-usability cycle would have low information value.

The useful evidence boundary is now:

```text
mechanics / authority / routing / failure behavior
-> substantially tested

founder product-judgment signal
-> substantially tested for Story Discovery

provider behavior
-> still needs #310 where the provider itself is the variable

subjective writer experience
-> still needs #305 where the human is the variable

high-order synthesis
-> #313 after claim-appropriate evidence
```

Therefore:

> **Use coding-agent simulation to narrow and pre-answer repository/product
> mechanics. Do not use it to manufacture the last human/provider claims that
> the existing protocols deliberately reserve.**
