# Progressive Commitment and Story-State Semantics v0

**Status:** evidence-gated product-model research candidate  
**Date:** 2026-10-03  
**Authority:** noncanonical; subordinate to MISSION.md, docs/PRD.md, docs/narrative-architecture.md, existing author-authority/acceptance workflows, and current schemas  
**Implementation status:** no new state enum, storage schema, authority path, or runtime behavior is authorized by this document

## 1. Question

Auteur intentionally lets an author move from a vague premise toward increasingly
specific narrative commitments. Existing architecture already distinguishes
derived/advisory material from explicit author acceptance, but a deeper product
question appears when incomplete or AI-inferred story information must survive
across later planning, drafting, and reconciliation:

> **Does Auteur need an explicit way to preserve not only a story value, but also
> how committed that value currently is?**

This document records that question and a candidate product principle:
**progressive commitment**.

It does not claim that the current repository has a Quick Draft defect or that a
global commitment-state machine is required.

## 2. Motivating systems problem

A local persistence problem can look simple:

~~~text
author enters partial story state
-> refresh
-> state disappears
-> persist state
~~~

Persistence alone answers only:

> Did the value survive?

Long-form authoring can require a different question:

> What did the value mean when it survived?

For example, an absent character attribute could mean:

- the author has not considered it;
- the author deliberately wants to decide later;
- Auteur temporarily inferred a value to support downstream reasoning;
- the author explicitly accepted the value;
- a later accepted choice conflicts with an earlier assumption.

If these meanings collapse into the same representation, downstream planning,
generation, continuity, and reconciliation may behave coherently at the storage
level while becoming incoherent at the product level.

## 3. Candidate product principle — progressive commitment

The candidate principle is:

> **Auteur should permit creative incompleteness while preserving enough
> epistemic and authority context for later systems to know what is unknown,
> tentative, accepted, or in conflict.**

A useful conceptual progression is:

~~~text
UNKNOWN
   |
   v
DEFERRED
   |
   v
PROVISIONAL
   |
   v
COMMITTED
~~~

with possible non-linear outcomes such as:

~~~text
PROVISIONAL -> REJECTED
COMMITTED   -> REVISED
PROVISIONAL / COMMITTED -> CONTRADICTED
~~~

These labels are explanatory vocabulary only. They are **not** a canonical enum.

## 4. Distinctions the product must not collapse

### 4.1 Epistemic status

What does Auteur currently know about the story proposition?

Examples:

~~~text
not established
tentative
supported
conflicting
~~~

### 4.2 Narrative authority

Who has authority to make the proposition canonical?

Examples:

~~~text
derived suggestion
author-adjusted interpretation
accepted StoryIdentity
accepted Structure change
accepted Realization / chapter outcome
~~~

Existing Auteur authority boundaries remain controlling.

### 4.3 Provenance

Where did the proposition come from?

Examples:

~~~text
author premise
provider inference
deterministic projection
Story Discovery candidate
Tutor recommendation
accepted artifact
draft prose inference
~~~

### 4.4 Freshness / staleness

Is the proposition still current relative to the sources it depended on?

This remains owned by existing source-binding/currentness and
revision/staleness contracts.

### 4.5 Contradiction

Do two relevant propositions conflict?

Contradiction is not identical to uncertainty, provisionality, or staleness.

~~~text
PROVISIONAL
!= STALE

DEFERRED
!= UNKNOWN

CONTRADICTED
!= REJECTED

COMMITTED
!= immutable forever
~~~

A future implementation, if warranted, must preserve these distinctions rather
than compressing all of them into one overloaded status field.

## 5. Why this matters over long horizons

Consider a hypothetical authoring flow.

~~~text
Chapter 1
author leaves protagonist occupation undecided
        |
        v
Chapter 2
Auteur needs an occupation for local reasoning
and tentatively uses "doctor"
        |
        v
Chapter 3
that assumption influences knowledge, scene outcome,
and a relationship
        |
        v
Chapter 5
author explicitly chooses "journalist"
~~~

The later change may affect:

~~~text
occupation
-> knowledge assumptions
-> scene causality
-> relationship consequence
-> later plot information
~~~

If "doctor" was only temporary scaffolding, reconciliation should not present the
same product meaning as changing an author-accepted commitment.

The important product requirement is therefore not necessarily "track every
dependency." It is:

> **Do not make downstream systems forget the difference between temporary
> scaffolding and accepted narrative authority when that difference changes the
> author's decision.**

## 6. Relationship to Auteur's five semantic layers

Progressive commitment does **not** create a sixth semantic layer.

The five-layer architecture remains:

~~~text
Ontology -> Identity -> Structure -> Realization -> Expression
~~~

Commitment status, provenance, currentness, and authority are cross-cutting
properties of how information moves through those layers.

Examples:

- **Identity:** a Story Discovery direction may be derived until explicit
  acceptance creates authoritative StoryIdentity.
- **Structure:** a proposal remains noncanonical until the existing explicit
  selection/revision/apply path changes accepted Structure.
- **Realization:** draft/inferred event-state information must not silently
  outrank accepted realized state.
- **Expression:** prose may explore wording freely while remaining constrained by
  accepted narrative facts.

The research question is whether current per-workflow distinctions are sufficient
or whether recurring authoring friction reveals a need for a more explicit,
shared progressive-commitment representation.

## 7. Relationship to Story Lenses

Story Lenses already preserve an important distinction:

~~~text
derived interpretation
!= accepted Story Direction / StoryIdentity
~~~

Missing lenses also remain explicitly unestablished rather than being filled with
invented certainty.

That is compatible with progressive commitment, but it does not prove that
fact-level or downstream long-horizon commitment semantics are needed.

Do not turn the Story Lens model into a universal commitment system by analogy
alone.

## 8. Relationship to reconciliation

Book/Structure/long-horizon reconciliation should remain owned by existing
systems.

Progressive commitment may eventually improve the **meaning** of reconciliation
when evidence shows that current systems cannot distinguish, for example:

~~~text
author changed an accepted commitment
vs.
AI temporary assumption was replaced
vs.
previous source became stale
vs.
two accepted facts actually conflict
~~~

A future implementation should prefer using existing reconciliation and
provenance surfaces rather than creating a second reconciliation engine.

## 9. Potential product behavior if later warranted

If real workflow evidence establishes the need, candidate behavior could include:

- displaying "not decided yet" distinctly from missing/error state;
- allowing an author to explicitly defer a decision without blocking progress;
- labeling AI-generated assumptions as tentative when shown to the author;
- preventing tentative assumptions from masquerading as accepted canon;
- carrying provenance/currentness into downstream prompts when it changes
  interpretation;
- reducing reconciliation severity when a provisional assumption is replaced;
- increasing reconciliation significance when an accepted commitment is changed;
- showing which later decisions depended materially on a replaced assumption.

These are candidate behaviors, not current requirements.

## 10. A possible story-assertion model

A future design investigation might discover that some story assertions need more
than a bare value:

~~~text
story assertion
=
value
+ authority status
+ epistemic/commitment status
+ provenance
+ currentness
+ dependency/revision evidence when material
~~~

Do not implement this shape directly from this document.

Auteur already has different artifact types and authority paths with different
semantics. A universal wrapper may be unnecessary or harmful. The correct
implementation could instead be a smaller refinement to one existing workflow.

## 11. Evidence gate

Promote this candidate only when observed workflow evidence demonstrates a
recurring problem that existing authority/provenance/staleness concepts cannot
cleanly express.

Useful triggers include:

1. an author intentionally leaves information open, but downstream systems treat
   it as accidental missing data;
2. AI-generated scaffolding is repeatedly mistaken for author-accepted canon;
3. replacing a tentative assumption creates the same warnings/repair burden as
   contradicting an accepted commitment;
4. later planning cannot reconstruct whether a consequential fact was author
   choice, derived inference, or temporary working assumption;
5. multiple local fixes add flags/special cases around the same missing
   distinction;
6. the Beginner workflow becomes more coercive because the system requires
   premature decisions merely to keep later stages functioning.

One synthetic example is enough to nominate investigation, not to establish a
new domain model.

## 12. Evidence that would argue against promotion

Do not add new architecture when existing surfaces already solve the observed
problem through:

- explicit accepted-vs-derived artifact ownership;
- source provenance;
- currentness/staleness;
- existing candidate/proposal lifecycle;
- clearer UX copy/presentation;
- one bounded workflow-specific field;
- ordinary reconciliation.

If a small presentation/workflow fix preserves the relevant distinction, prefer
it over a universal story-state ontology.

## 13. Design laws

~~~text
creative incompleteness
!= invalid state automatically

missing value
!= deferred decision automatically

AI inference
!= accepted canon

provisional wording
!= user understands provisionality

accepted
!= immutable forever

replacement of a tentative assumption
!= contradiction of accepted canon automatically

progressive commitment
!= mandatory questionnaire

shared concept
!= global schema automatically
~~~

## 14. Product implication

If evidence eventually supports the principle, Quick/low-friction authoring and
deep long-horizon coherence should not be opposing product modes.

They can be reconciled by allowing early low commitment while preserving enough
semantic context for later refinement:

~~~text
vague intent
-> exploration
-> tentative scaffolding where useful
-> explicit author acceptance where required
-> revision / reconciliation
-> increasingly coherent long-form state
~~~

This suggests a broader product framing:

> Auteur may be understood not only as a narrative compiler, but as a system for
> progressively transforming uncertain creative intent into explicit,
> inspectable, revisable narrative commitments.

That framing is a research interpretation, not a replacement for the current
product thesis.

## 15. Current disposition

~~~text
PROGRESSIVE_COMMITMENT_PRINCIPLE
= RESEARCH CANDIDATE / EVIDENCE_GATED

UNKNOWN / DEFERRED / PROVISIONAL / COMMITTED / CONTRADICTED
= EXPLANATORY VOCABULARY ONLY

NEW GLOBAL STORY-STATE ENUM
= NOT AUTHORIZED

NEW PERSISTENCE SCHEMA
= NOT AUTHORIZED

NEW RECONCILIATION ENGINE
= NOT WARRANTED

EXISTING AUTHOR AUTHORITY
= UNCHANGED
~~~

## 16. Governing rule

> **Preserve creative freedom early without allowing temporary uncertainty,
> derived inference, and explicit author commitment to become semantically
> indistinguishable when later decisions depend on the difference.**
