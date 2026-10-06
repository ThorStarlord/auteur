# Auteur UX / Product Requirements — Provisional High-Order Contract

**Date:** 2026-10-03  
**Status:** **PROVISIONAL / EVIDENCE-GATED**  
**Derived from:** `auteur-unified-author-experience-architecture.md` and `auteur-system-interaction-map.md`  
**Purpose:** translate the unified author experience into testable product requirements without pretending unresolved human/provider questions are settled.

## 1. Requirement status

Each requirement uses one of:

- **ESTABLISHED** — already a durable product/authority principle.
- **CURRENT** — mechanically implemented in the current integrated candidate.
- **SELECTED** — chosen high-order direction, not yet fully implemented/validated.
- **EVIDENCE-GATED** — must wait for #305 and/or #310 before stronger commitment.

A requirement may be both mechanically implemented and still human-evidence-gated for claims about usefulness.

---

# 2. Unified author mental model

### UA-01 — Story-language mental model
**Status:** ESTABLISHED

The default Beginner product MUST be understandable through story-language concepts such as:

- Story idea;
- what Auteur sees;
- Direction;
- Story core;
- Story shape;
- working draft;
- accepted story;
- story updates;
- continuity.

A beginner MUST NOT need to understand the five semantic layers to use the normal product path.

### UA-02 — Working versus accepted state
**Status:** ESTABLISHED

The author MUST be able to distinguish:

- exploratory / working material;
- machine inference;
- author-selected shaping input;
- accepted story state.

The distinction MAY be conveyed through plain language rather than lifecycle jargon.

### UA-03 — Author meaning / machine machinery split
**Status:** ESTABLISHED

Auteur SHOULD ask the writer to decide story meaning.

Auteur SHOULD absorb reversible planning, state propagation, dependency traversal, and other execution machinery when doing so does not collapse distinct creative decisions.

### UA-04 — No duplicate authorship
**Status:** SELECTED

If the author has already established an idea in prose and explicitly selected it for shaping/updating, the product SHOULD NOT require them to manually re-enter the same meaning into another internal model.

---

# 3. Entry and authoring tempo

### ENTRY-00A — Optional pre-premise discovery
**Status:** ESTABLISHED

When an author does not yet have a stable premise, Auteur MAY support the
documentation-defined Story Opportunity Discovery workflow before normal
authoring entry.

The normal product MUST NOT require this workflow when the author already has a
working premise.

Story Opportunity outputs MUST remain working / nonaccepted until existing
Identity authority is crossed explicitly later.

### ENTRY-00B — Premise Fitness is decision-triggered
**Status:** ESTABLISHED

Premise Fitness MUST NOT become a mandatory gate, score, validator, or approval
step before Story Discovery.

It MAY be surfaced when genre promise, narrative horizon, complexity, runway,
renewability, expansion, or multi-engine fit creates a material decision
tradeoff.

Its output MUST remain derived / noncanonical and MUST NOT automatically choose
a Story Discovery direction.

### ENTRY-01 — Shape-first entry
**Status:** CURRENT

The Beginner Home MUST support a shape-first path beginning from a premise and leading through interpretation, Direction, Story core, Story shape, planning, and prose.

### ENTRY-02 — Write-first entry
**Status:** CURRENT / EVIDENCE-GATED

The Beginner Home MUST support an optional write-first path accepting:

1. premise;
2. first-scene intent.

It MUST be capable of reaching working prose without Story core / Story shape acceptance beforehand.

Whether write-first becomes the default or remains secondary is **EVIDENCE-GATED by #305**.

### ENTRY-03 — One product after entry
**Status:** SELECTED

Shape-first and write-first MUST converge on the same existing story authorities.

Neither path may create a shadow canon or path-specific Story Identity.

### ENTRY-04 — Preserve entry choice
**Status:** SELECTED

The product SHOULD allow an author to move between writing and shaping without treating the earlier choice as irreversible.

### ENTRY-05 — Foreground from explicit current intent
**Status:** SELECTED

Auteur SHOULD foreground **Shape first** when the author's explicit current goal
is understanding, comparison, architecture, or long-range shaping.

Auteur SHOULD foreground **Write first** when the author has a concrete scene
impulse stronger than the current need for architecture.

When the current goal is ambiguous, the product SHOULD preserve both entry
options rather than infer a population-level preference from genre or author
stereotype.

This requirement does not establish which path writers generally prefer.

---

# 4. Progressive disclosure

### PD-01 — One primary action
**Status:** CURRENT

A Beginner surface SHOULD normally expose one primary forward action even when many technical actions are valid.

### PD-02 — Contextual capability depth
**Status:** SELECTED

Creative, Guidance, Continuity, and Deep-control capabilities SHOULD be foregrounded based on author need rather than a fixed one-way stage progression.

### PD-03 — Story-visible trigger
**Status:** SELECTED

Deeper capability SHOULD appear when a problem meaningful to the author becomes visible.

Examples:

- ambiguity -> guidance;
- new discovery -> story update;
- contradiction -> continuity decision;
- “why?” -> deeper evidence.

### PD-04 — Advanced access
**Status:** ESTABLISHED

Progressive disclosure MUST NOT remove advanced inspection or step-by-step control.

### PD-05 — Material post-Discovery fit change
**Status:** SELECTED

If a decision-relevant Story Discovery architecture materially changes an
earlier Premise Fitness assumption, Auteur MAY surface a plain-language summary
such as **What this story direction changes**.

If no material fit assumption changes, the product SHOULD remain silent rather
than adding another confirmation surface.

This projection is advisory only and MUST NOT become an acceptance gate.

---

# 5. Inference and provisional state

### INF-01 — Inference never equals acceptance
**Status:** ESTABLISHED

Model inference, deterministic heuristics, Story Lens interpretation, Quick Draft scaffold defaults, and discovery detection MUST remain nonauthoritative until the relevant existing owner accepts a consequence.

### INF-02 — Preserve unknowns
**Status:** CURRENT

If POV, location, genre, tone, or another value is not established and does not need to be fixed to proceed, Auteur SHOULD preserve it as unknown/provisional instead of inventing a durable commitment.

### INF-03 — Epistemic framing in generation context
**Status:** SELECTED

Cross-system context supplied to generation/reasoning SHOULD distinguish:

- accepted facts;
- author-explicit current intent;
- provisional inference;
- pending proposal;
- stale evidence.

It SHOULD NOT flatten all context into equally authoritative prompt text.

### INF-04 — Exact author input
**Status:** CURRENT

Quick Draft MUST pass the exact author premise and exact first-scene intent to the prose model as controlling creative evidence.

---

# 6. Drafting and working prose

### DRAFT-01 — Working prose before acceptance
**Status:** CURRENT

Working prose MUST remain editable and nonaccepted until the relevant existing Expression owner accepts it.

### DRAFT-02 — Recoverable exploratory work
**Status:** CURRENT

Quick Draft sessions MUST survive normal refresh/reopen without being silently promoted.

### DRAFT-03 — Revision history
**Status:** CURRENT

Saving Quick Draft edits SHOULD preserve prior working versions rather than destructively overwriting the only copy.

### DRAFT-04 — Scene-sized write-first output
**Status:** EVIDENCE-GATED

Quick Draft SHOULD produce useful first-scene-scale prose rather than compressing an entire story/chapter into the initial response.

Real provider evidence is required through #310.

---

# 7. Review freshness

### REVIEW-01 — Exact-content review binding
**Status:** CURRENT

Review evidence MUST identify the exact draft content it evaluated.

### REVIEW-02 — Stale review truthfulness
**Status:** CURRENT

If draft bytes change after review, the prior findings MUST NOT be displayed as current findings.

### REVIEW-03 — Stale does not mean invalid
**Status:** ESTABLISHED

A stale review means “this evidence no longer describes the current draft,” not “the new draft is invalid.”

---

# 8. Creative discovery and story updates

### DISC-01 — Unexpected prose is evidence first
**Status:** ESTABLISHED

Unexpected creative material MUST be treated as evidence before it is treated as error.

### DISC-02 — Discovery classes
**Status:** CURRENT / SELECTED

The system SHOULD distinguish at least:

- additive discovery;
- plan divergence;
- hard conflict requiring author decision.

### DISC-03 — Explicit author choice
**Status:** CURRENT

When meaningful divergence exists, the Beginner surface MUST offer story-language choices equivalent to:

- Keep draft & update story;
- Keep as intentional divergence;
- Revise to match plan.

### DISC-04 — Lowest-sufficient-owner routing
**Status:** SELECTED

Story updates SHOULD route to the lowest owner capable of representing the meaning.

Ordinary new character/location details SHOULD NOT reopen Story core automatically.

### DISC-05 — Heuristic discovery is not commitment
**Status:** CURRENT

Quick Draft discovery checkboxes MUST be unselected by default.

Only explicitly selected observations may enter story shaping as author-selected evidence.

### DISC-06 — Human usefulness
**Status:** EVIDENCE-GATED

The discovery surface SHOULD feel like help incorporating creative discoveries rather than correction/data maintenance.

This claim requires #305.

### DISC-07 — Consequential-delta surface
**Status:** SELECTED

`What did we discover?` SHOULD prefer consequence-bearing differences between
prior context/plans and current prose over exhaustive extraction.

When no material discovery exists, the product SHOULD skip an empty
confirmation/checklist step.

Heuristic observations MUST remain unselected / nonauthoritative until the
author explicitly carries them forward.

---

# 9. Accepted prose and downstream context

### CONTEXT-01 — Accepted prose matters
**Status:** SELECTED

Future planning MUST be able to use relevant outcomes from accepted prior Chapter prose.

### CONTEXT-02 — Plan is not the only truth about what happened
**Status:** SELECTED

When accepted prose realizes the story differently from an older plan, downstream guidance SHOULD reason from both:

- accepted intended structure;
- accepted events that actually occurred.

### CONTEXT-03 — Pending updates remain explicit
**Status:** SELECTED

Using accepted Chapter outcomes downstream MUST NOT silently mutate Structure, Identity, or state owners.

Any unresolved synchronization SHOULD remain explicit.

### CONTEXT-04 — Additive updates should not automatically block writing
**Status:** SELECTED

Pending compatible story updates SHOULD NOT prevent the author from continuing merely because every internal model has not yet been synchronized.

A genuine hard contradiction MAY require resolution before dependent generation if proceeding would materially mislead the author.

### CONTEXT-05 — Ambient-by-default continuity
**Status:** SELECTED

Continuity guidance SHOULD remain ambient while unresolved updates are compatible
with the next author action.

It SHOULD interrupt only when unresolved divergence would materially mislead a
dependent decision or when an existing hard authority / validation boundary
requires explicit resolution.

The product MUST NOT implement `any pending update -> block` as a generic
continuity rule.

---

# 10. Change-my-mind behavior

### CHANGE-01 — Story-language change intent
**Status:** SELECTED

The author SHOULD be able to state a meaningful change in natural story language without first identifying the owning semantic layer.

### CHANGE-02 — Consequence projection
**Status:** SELECTED

Auteur SHOULD translate the change into:

- affected story meaning;
- affected accepted/planned artifacts;
- proposed updates;
- meaningful consequences.

### CHANGE-03 — Preserve unaffected commitments
**Status:** SELECTED

A change SHOULD NOT cause unrelated accepted decisions to be reopened.

### CHANGE-04 — Distinguish future change from historical revision
**Status:** SELECTED

The product SHOULD distinguish:

- change from here forward;
- revise earlier accepted story.

### CHANGE-05 — Resume momentum
**Status:** EVIDENCE-GATED

After a change, the product SHOULD return the writer to useful creative work without excessive approval/admin ceremony.

Human evidence is required through #305.

---

# 11. Long-form continuity

### LONG-01 — Chapter N receives evolved context
**Status:** SELECTED

Chapter N planning SHOULD compose relevant context from:

- accepted Story core;
- accepted Structure;
- accepted prior Chapter outcomes;
- accepted realized facts;
- material unresolved story-update signals.

### LONG-02 — No premise reset
**Status:** SELECTED

Long-form generation MUST NOT behave as though the original premise is more current than accepted events that happened in later Chapters.

### LONG-03 — Whole-book story consequence first
**Status:** SELECTED

Whole-book continuity surfaces SHOULD explain meaningful story drift before exposing reconciliation transaction machinery.

### LONG-04 — Series maps remain derived
**Status:** ESTABLISHED

Long-horizon maps/projections MUST NOT become a second canon.

### LONG-05 — Continuity value must be perceptible
**Status:** EVIDENCE-GATED

Auteur’s additional long-form machinery is justified only if authors can identify useful continuity/decision value beyond a general-purpose editor/LLM.

Human evidence: #305.

---

# 12. Vocabulary and presentation

### LANG-01 — Story language first
**Status:** CURRENT

Beginner-facing copy SHOULD prefer:

- accepted story;
- working draft;
- story update;
- story shape;
- source history;

over internal lifecycle terms such as:

- canonical/noncanonical;
- candidate;
- reconciliation;
- provenance;
- ontology.

### LANG-02 — Technical detail on demand
**Status:** ESTABLISHED

Internal vocabulary MAY be exposed under advanced/deep-control surfaces when it improves precision.

### LANG-03 — Explain story consequence before system state
**Status:** SELECTED

When a technical condition affects the author, the product SHOULD first explain the story consequence.

---

# 13. Authority and ownership

### AUTH-01 — No parallel Beginner authority
**Status:** ESTABLISHED

The Beginner system MUST route meaningful acceptance to existing owners.

### AUTH-02 — No silent recommendation promotion
**Status:** ESTABLISHED

Recommendation/proposal/inference MUST NOT become accepted story state merely because it is convenient for the workflow.

### AUTH-03 — Accepted Expression does not mutate upstream automatically
**Status:** ESTABLISHED

Accepting Chapter prose MUST NOT silently rewrite Story core or Structure.

### AUTH-04 — Accepted Expression may provide context
**Status:** SELECTED

Accepted Expression MAY be composed as downstream context while explicit synchronization with other owners remains pending.

### AUTH-05 — Product projections may compose systems
**Status:** ESTABLISHED

A product projection MAY synthesize status from multiple subsystems without taking ownership of their authority-bearing state.

---

# 14. Reliability and recoverability

### REL-01 — Working context survives normal navigation
**Status:** CURRENT

Provisional Quick Draft work MUST survive ordinary refresh/reopen.

### REL-02 — Accepted state survives product projections
**Status:** ESTABLISHED

Re-rendering, orientation, diagnostics, or navigation MUST NOT mutate accepted story state.

### REL-03 — Failure should preserve author work
**Status:** ESTABLISHED

Provider/review/reconciliation failure SHOULD preserve the author’s latest working prose and accepted prior state.

### REL-04 — No stale-home resurrection
**Status:** CURRENT

After Quick Draft transitions into a normal workspace, returning Home without the provisional Quick Draft URL context MUST NOT present the old Quick Draft as the active story surface.

---

# 15. System UX anti-requirements

The product MUST NOT intentionally create these experience patterns:

### ANTI-01 — State-machine-shaped UX

Do not expose every backend transition as a user step.

### ANTI-02 — Approval laundering

Do not ask multiple times for one already-expressed creative commitment merely because internal owners have multiple transitions.

### ANTI-03 — Hidden commitment

Do not make provisional inference durable merely to fill internal fields.

### ANTI-04 — Reconciliation tax

Do not make experimentation prohibitively expensive through mandatory maintenance ceremony.

### ANTI-05 — Duplicate authorship

Do not make the author restate discoveries already explicitly selected from their prose.

### ANTI-06 — Long-form context amnesia

Do not plan future Chapters as if accepted previous events never happened.

---

# 16. Capability frontier and construction requirements

### SCALE-01 — Narrative stress profile
**Status:** SELECTED

Repository-level story qualification SHOULD describe the intended stress profile
across:

- Interpretive Difficulty;
- Input / Process Messiness;
- Narrative Breadth;
- Narrative Depth;
- Longitudinal Horizon;
- Change / Revision Pressure.

The product MUST NOT rely on one aggregate narrative-complexity score.

### SCALE-02 — Controlled frontier progression
**Status:** SELECTED

Major construction SHOULD increase one or two stress dimensions at a time when
practical so failures remain attributable.

### SCALE-03 — Failure-driven capability admission
**Status:** SELECTED

A new narrative subsystem or major capability SHOULD normally be admitted only
after the next controlled frontier exposes a recurring material limitation that
cannot be cleanly solved by existing workflow, presentation, craft knowledge, or
model concepts.

### SCALE-04 — Complete-workflow qualification
**Status:** SELECTED

A capability frontier MUST NOT be considered qualified solely because isolated
components or unit tests pass.

Qualification SHOULD exercise the complete relevant author journey.

### SCALE-05 — Lowest-correct-layer repair
**Status:** ESTABLISHED / SELECTED

Frontier failures SHOULD be classified before intervention as primarily:

- UX / presentation;
- workflow;
- craft knowledge;
- domain model;
- infrastructure.

The repository SHOULD modify the lowest correct layer.

### SCALE-06 — F2 preferred next frontier
**Status:** EVIDENCE-GATED

If #305/#310 and #313 reaffirm the current unified author experience, the next
major construction frontier SHOULD be:

> **F2 — Small-Book Longitudinal Coherence**

The reference stress should use a controlled ~6-Chapter Book with:

- 5–7 meaningful characters;
- two plot threads;
- one drafting discovery;
- one meaningful mid-book change;
- one revelation moved earlier;
- whole-Book orientation at the end.

F2 being documented does not authorize implementation before #313.

### SCALE-07 — No permanent simple-story optimization
**Status:** SELECTED

The repository SHOULD NOT indefinitely optimize F0/F1 interactions merely
because simple stories are easier to test.

Once the current frontier is coherent, product work SHOULD move toward the next
warranted stress frontier.

# 17. Experience frontier and UX/UI construction requirements

### X-SCALE-01 — Experience stress profile
**Status:** SELECTED

UX/UI qualification SHOULD describe pressure across:

- Decision Density;
- Workflow Branching;
- State / Continuity Load;
- Interaction Horizon;
- Mode Switching;
- Expertise Range;
- Information Density;
- Visual / Spatial Complexity.

The product MUST NOT reduce these to one aggregate “UX complexity” score.

### X-SCALE-02 — Independent narrative / experience qualification
**Status:** SELECTED

Narrative and experience frontiers MUST be allowed to pass/fail independently.

A narrative failure SHOULD NOT be disguised as a UI repair.

A UX/UI failure SHOULD NOT trigger a new narrative subsystem unless the underlying story capability is actually insufficient.

### X-SCALE-03 — Paired frontier selection
**Status:** SELECTED

Major construction SHOULD select both a narrative frontier F0–F7 and an experience frontier X0–X7.

### X-SCALE-04 — UX/UI failure classification
**Status:** SELECTED

Classify failures before implementation as primarily:

- UX mental model;
- UX workflow;
- UX information architecture;
- UX navigation/orientation;
- UX interaction semantics;
- UX progressive disclosure;
- UX re-entry/continuity;
- UI visual hierarchy;
- UI information density;
- UI spatial layout;
- UI state feedback;
- UI responsive behavior;
- UI accessibility;
- UI design-system consistency.

Repair the lowest correct layer.

### X-SCALE-05 — Accessibility floor
**Status:** ESTABLISHED / SELECTED

Baseline accessibility MUST be preserved at every experience frontier.

### X-SCALE-06 — Visual polish is separate from frontier scale
**Status:** SELECTED

Aesthetic maturity SHOULD improve continuously but MUST NOT be used as evidence that an experience frontier is qualified.

### X-SCALE-07 — X3 preferred next experience frontier
**Status:** EVIDENCE-GATED

If #305/#310/#313 reaffirm the current unified author experience, the next experience frontier SHOULD be:

> **X3 — Persistent Book Workspace**

paired with:

> **F2 — Small-Book Longitudinal Coherence**

using the same controlled six-Chapter reference Book.

X3 being documented does not authorize a Book Dashboard, sidebar, timeline, graph, or multi-pane workspace before frontier evidence identifies the first material experience failure.

### X-SCALE-08 — Do not scale UI merely because backend complexity grew
**Status:** SELECTED

The interface SHOULD gain additional persistent structure only when author-experience evidence shows that the current simpler interaction model can no longer carry the product's complexity.

### X-SCALE-09 — Contextual modes remain one product
**Status:** SELECTED

Creative, Guidance, Continuity, and Deep-control modes SHOULD remain coherently reachable within higher experience frontiers rather than becoming separate applications.

# 18. Validation requirements

### VAL-01 — Mechanical evidence scope
**Status:** ESTABLISHED

Repository/static tests may establish:

- action availability;
- designed interaction count;
- authority boundaries;
- persistence/recoverability;
- exact-review freshness;
- explicit carry-forward;
- routing mechanics.

### VAL-02 — Provider evidence
**Status:** CURRENT RESPONSIBILITY #310

Real provider evidence MUST be used for claims about:

- observed latency;
- actual generated prose;
- prompt/inference leakage;
- scene-sized output.

### VAL-03 — Human evidence
**Status:** CURRENT RESPONSIBILITY #305

Real participant evidence MUST be used for claims about:

- experienced cognitive load;
- bureaucracy;
- ownership;
- creative momentum;
- confidence;
- preference;
- desire to continue;
- perceived continuity value.

### VAL-04 — No synthetic promotion
**Status:** ESTABLISHED

A coherent architecture, passing test, or agent simulation MUST NOT be presented as proof of real-author preference.

---

# 19. Evidence-gated product decisions

Coding-agent stress testing has narrowed this list. The following decisions still
require #305 and/or #310 evidence:

1. Which entry path do writers actually prefer in comparable situations, after
   routing from explicit current intent?
2. Is the Quick Draft first scene reliably useful and intent-faithful with real
   providers?
3. Is **What did we discover?** experienced as useful enough to retain, or as
   noisy/administrative, when it is limited to consequence-bearing deltas?
4. Does **Keep draft & update story** feel like creative help rather than
   bookkeeping?
5. How much inferred scaffolding can remain hidden before authors feel loss of
   control?
6. Can unfamiliar authors understand the unified story-language mental model
   without learning internal semantic layers?
7. Does Auteur's continuity / decision machinery create enough **felt** value
   over Markdown + a capable general-purpose LLM to justify its additional
   interaction cost?

The structural interruption rule is no longer evidence-gated:

> continuity remains ambient by default and interrupts only when unresolved
> divergence would materially mislead a dependent decision or cross an existing
> hard authority / validation boundary.

The exact human-facing timing/copy of that interruption may still be refined by
#305.

No implementation should manufacture the remaining human/provider claims from
agent simulation.

---

# 20. Post-evidence reconciliation

After #305 and #310 return:

```text
provider evidence
+
human evidence
+
this provisional architecture
-> reconcile requirements
-> mark requirements KEEP / REVISE / REJECT / NEW
-> identify bounded next implementation wave
```

The reconciliation SHOULD prefer the smallest high-order correction that restores one coherent author mental model.

It SHOULD NOT return to an endless sequence of unrelated local UI patches.

---

# 21. Product-level acceptance

The high-order UX architecture is ready for stronger implementation authority when:

- #310 has produced real-provider evidence for the Quick Draft path;
- #305 has produced at least one serious real-author comparison;
- the evidence does not require a Level-4 product-thesis review;
- the provisional requirements have been reconciled against that evidence.

Until then, this document is a **product requirements scaffold**, not proof that every selected interaction is the ideal final experience.
