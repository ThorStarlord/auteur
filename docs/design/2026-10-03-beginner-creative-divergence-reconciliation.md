# Beginner Creative Divergence Reconciliation

**Date:** 2026-10-03  
**Tracking:** #306  
**Scope:** Beginner post-draft human-facing workflow  
**Evidence source:** chaotic-writer simulation with an unplanned character and setting  
**Status:** Product contract selected; implementation pending

## Problem

Writers frequently discover story material while drafting that was not represented
in the accepted planning model.

The Beginner flow must distinguish:

~~~
unexpected idea
!= malformed data
!= hard canon contradiction
~~~

The plan is evidence about expected story movement. It is not a cage around what
the writer is allowed to discover.

> **Unexpected prose is evidence before it is an error.**

## Chaotic-writer evidence

The simulation began from a simple modeled story:

~~~
Detective Miller investigates Suspect Vance.

Planned Chapter 1:
Miller questions Vance at the police precinct.
~~~

During drafting the human introduced:

- **Sister Beatrice**, a character not present in the modeled story;
- **an abandoned seaside convent**, a setting not present in Identity or Structure;
- a material path change in which Miller leaves the precinct-focused plan.

Example divergent prose:

~~~
# Scene 1
Detective Miller followed Suspect Vance out of the precinct.

# Scene 2
At the abandoned seaside convent, Sister Beatrice unlocked a salt-stained
chapel door and told Miller she had hidden Vance there for three nights.
~~~

## Current behavior observed

### Case A — divergence is not detected

If prose is edited after its matching validation artifact is written, the current
post-draft projection can continue to associate the old validation with the
changed draft by version number.

~~~
draft_v1.md changed
+
validation_v1.json unchanged
-> old review still appears current
~~~

The new prose survives and can be accepted, while realized state/Bible may remain
unaware of Sister Beatrice, the convent, or the changed chapter event.

This is **semantic model drift**, not author-data loss.

### Case B — critic reports divergence as an error

A blocking finding changes the projection to revision-required. The projection
already includes both revise and accept-deliberate-divergence as revision
options, but the current Beginner Browser hides **Keep this draft** when blocking
findings exist and does not surface deliberate divergence.

Visible experience:

~~~
unexpected idea
-> ERROR
-> revise
~~~

### Case C — lower-level acceptance

The underlying Chapter acceptance owner can promote the latest candidate without
consulting the matching validation report.

This creates a product inconsistency:

~~~
Browser policy:
blocking review -> Keep unavailable

underlying acceptance:
latest draft -> may still be promoted
~~~

The Browser and authority workflow must converge on one explicit reconciliation
contract.

## Creative divergence classification

### 1. Additive Discovery

New material that does not negate accepted narrative meaning.

Examples:

- new side character;
- new location;
- new relationship detail;
- new incidental world fact;
- new object;
- compatible backstory.

Default treatment:

~~~
nonblocking discovery
-> preserve prose
-> offer reconciliation
~~~

### 2. Plan Divergence

The prose materially changes how an accepted plan is realized without necessarily
contradicting canon.

Examples:

- planned interrogation becomes a pursuit;
- scene moves to an unplanned location;
- a different participant drives the turn;
- compatible outcome reached through a different route.

Default treatment:

~~~
review recommended
-> author chooses how to reconcile
~~~

### 3. Hard Canon Contradiction

The prose asserts something incompatible with an accepted fact or commitment.

Example:

~~~
accepted fact:
Vance's sister died ten years ago

draft:
Sister Beatrice is Vance's living biological sister
~~~

Default treatment:

~~~
explicit author decision required
~~~

Even here, the UI should lead with the story conflict rather than technical
validation jargon.

## Beginner workflow: Reconcile New Elements

When meaningful discovery or divergence is detected, the primary surface should
say something like:

### Auteur noticed the story changed while you were writing

That's okay. Writing often discovers things the plan did not know yet.

**New character**  
Sister Beatrice

**New place**  
Abandoned seaside convent

**Story change**  
Miller leaves the planned precinct interrogation and follows Vance elsewhere.

Primary actions:

~~~
[Keep draft & reconcile]
[Keep as intentional divergence]
[Revise to match plan]

[Review details]
~~~

This is a story-development surface, not a schema-error surface.

## Action semantics

### Keep draft & reconcile

Meaning:

~~~
preserve current prose
-> cross existing Chapter Expression acceptance explicitly
-> create noncanonical reconciliation proposals
-> route proposals to the lowest appropriate owners
-> never silently rewrite upstream authority
~~~

Plausible routing for the simulation:

| Discovery | Likely target |
|---|---|
| Sister Beatrice exists | realized/state carrier proposal |
| abandoned seaside convent exists | realized/state location proposal |
| Beatrice hid Vance there for three nights | realized fact/event proposal |
| Chapter 1 leaves the precinct plan | Realization/Structure proposal if consequential downstream |

Story Identity remains untouched unless the discovery genuinely changes what the
story fundamentally is.

### Keep as intentional divergence

Meaning:

~~~
accept/preserve Expression
+
record explicit author acknowledgement
+
retain visible divergence from current planning
~~~

This is the Beginner product form of the existing deliberate-divergence concept.
It does not imply that upstream models were updated.

### Revise to match plan

Meaning:

~~~
preserve current authority
-> keep candidate/history
-> use existing revision/retry route
~~~

This remains appropriate when the author decides the discovery was accidental or
less useful than the plan.

## Candidate editing contract

The Browser currently displays prose but does not provide a first-class manual
prose-editing surface.

A forgiving writing product should support author edits as a new candidate state
rather than mutating a previously validated candidate in place.

Preferred lifecycle:

~~~
draft_v1
+ validation bound to draft_v1 hash

author edits
-> draft_v2 or equivalent new candidate state
-> unvalidated / reconciliation pending
-> fresh validation/reconciliation
~~~

Do not allow:

~~~
draft_v1 bytes changed
+
validation_v1 still treated as current
~~~

## Validation freshness contract

Every review artifact must identify the exact candidate content it reviewed.

Minimum binding:

~~~yaml
candidate:
  path: draft_v2.md
  sha256: <candidate-content-hash>
~~~

Review projection compares that hash with the current candidate before presenting
findings as current.

Mismatch means **review stale**, not **candidate invalid**.

## Authority contract

Reconciliation preserves the existing authority architecture.

~~~
Expression evidence
!= automatic upstream mutation

Expression acceptance
!= Identity acceptance

Expression acceptance
!= Structure acceptance
~~~

Selected flow:

~~~
prose discovery
-> classify
-> preserve candidate
-> author chooses
-> generate proposals
-> each proposal crosses its own owning authority explicitly
~~~

The Beginner layer orchestrates the workflow but does not become a new authority
owner.

## Lowest-owner rule

Route discoveries to the lowest semantic owner capable of representing them.

~~~
new character/location/state
-> realized/state owner first

changed scene execution
-> Realization / Structure only if consequential

changed core story meaning
-> Identity only when genuinely necessary
~~~

Do not reopen Story Identity merely because prose contains something new.

## UX language

Prefer:

- "Auteur noticed something new."
- "This chapter moved away from the plan."
- "This conflicts with something you established earlier."
- "Keep the idea and update the story?"
- "Keep this as an intentional divergence?"
- "Revise toward the existing plan?"

Avoid making ordinary creative discovery sound like schema failure, invalid data,
malformed state, or an illegal character/location.

Technical evidence remains available under progressive disclosure.

## Mechanical acceptance criteria

The bounded implementation is mechanically adequate when:

1. a manually changed candidate cannot inherit stale validation silently;
2. additive discovery does not become a blocking error by default;
3. plan divergence exposes an explicit author choice;
4. accept-deliberate-divergence is reachable from the Beginner surface;
5. **Keep draft & reconcile** preserves prose and produces only noncanonical proposals until target owners accept them;
6. the Sister Beatrice + convent scenario never crashes or silently discards prose;
7. accepted prose cannot silently leave the product claiming that no model divergence exists;
8. hard contradiction is explained in story language before technical detail;
9. the author can always choose revision toward the plan;
10. no reconciliation action silently mutates Identity, Structure, Realization, or Bible authority.

## Human-validation questions

After implementation, test:

- Does **Auteur noticed something new** feel like help rather than correction?
- Can the author keep an unexpected idea without feeling punished?
- Is the distinction between reconcile, intentional divergence, and revise understandable?
- Does reconciliation preserve creative momentum rather than feel like data maintenance?
- Does the author understand when a genuine contradiction requires a more consequential decision?

## Non-goals

This contract does not:

- make every prose invention canonical automatically;
- allow Expression to silently rewrite planning;
- require reopening Identity for ordinary discoveries;
- eliminate validation;
- eliminate hard contradiction review;
- implement Creative Scratch/Riff;
- define a new semantic layer;
- change CI/CD, branch protection, formal L3 qualification, STATUS, or strategic reconciliation.

## Product principle

~~~
the validator protects author intent from accidental contradiction
!=
the validator protects the plan from the author
~~~

Planning is scaffolding.

Prose is allowed to teach Auteur something new.
