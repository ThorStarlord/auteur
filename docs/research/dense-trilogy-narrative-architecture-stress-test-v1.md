# Dense Trilogy Narrative Architecture Stress Test V1

## Status

**FROZEN V1 — OWNER AUTHORIZED FOR SYNTHETIC EXECUTION.**

This document defines a bounded architecture-only synthetic experiment. It is
separate from the dormant natural-use campaign posture
`PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION` and must never be cited as natural
reachability, human-author, or reader evidence.

Execution is authorized only within the scope frozen here. The run must not
change production code, add ontology, reopen extraction, authorize scale work,
create chapter outlines, or generate prose. Any material protocol change requires
a new specification revision and a new owner decision.

The exact commit containing this frozen revision is the protocol identity for the
run. Every execution session must record that commit before doing story work.

## 1. Purpose

The experiment asks whether Auteur can carry a **dense trilogy-scale narrative
architecture** across fresh worker contexts without relying on one coding agent's
conversation memory of the whole story.

The target is an original trilogy with:

- one protagonist;
- five other main characters;
- ten recurring supporting characters;
- multiple factions/institutions;
- multiple important locations;
- multiple persistent subplots;
- changing relationships;
- secrets or asymmetric knowledge;
- delayed consequences;
- at least some setup/payoff pressure;
- enough accumulated history that Book 3 materially depends on Books 1 and 2.

The experiment tests the long-horizon chain:

```text
Representation
→ Accepted / canonical memory
→ Current-state reconstruction
→ Projection / integration
→ Relevance selection
→ Reasoning
→ Explanation
```

It deliberately stops before chapter planning and prose.

## 2. Primary research question

> Can Auteur support the construction and later reconstruction of a dense
> trilogy-scale narrative architecture with sixteen recurring characters and
> interacting narrative threads, while preserving authority boundaries and
> avoiding broad manual reconstruction of earlier Books?

Secondary questions:

1. Are the important narrative meanings representable somewhere in current
   Auteur architecture?
2. When representation already exists, do later long-horizon surfaces actually
   consume and project it?
3. Does accepted history remain coherent as Book 1 changes the conditions
   inherited by Book 2 and Book 2 changes the conditions inherited by Book 3?
4. Can fresh-context workers recover the right earlier history for later
   decisions without hidden summaries?
5. Can information that was low-salience when introduced become relevant again
   later?
6. Can at least one relationship whose *path* matters be reconstructed rather
   than reduced to a current-state label?
7. Can at least one consequential knowledge asymmetry or delayed obligation be
   carried into later planning?
8. After the clean trilogy result is frozen, can one semantically important
   Book-1 revision propagate across accepted Books 2 and 3 without silent rewrite?
9. Does this density produce a concrete information-load problem?

## 3. Claim ceiling

The strongest permitted closure claim is:

> In one synthetic, architecture-only trilogy stress case, fresh-context coding
> agents using the tested Auteur surfaces could (or could not) preserve,
> reconstruct, and reason over important accepted narrative architecture across
> three Books under the specified density and long-range dependency pressures.

The experiment may support bounded findings about:

- representational sufficiency;
- persistence of accepted/canonical information;
- integration between existing Auteur representation planes;
- current-state reconstruction;
- identity continuity;
- relevance selection;
- reasoning from surfaced evidence;
- explanation adequacy;
- revision propagation;
- authority preservation;
- information-load pressure.

It does **not** establish:

- human author value;
- natural workflow reachability;
- beginner usability;
- reader emotional response;
- prose quality;
- chapter/scene pacing quality;
- marketability;
- independent artistic quality;
- generalized 50/100/300-Book scale;
- population-level robustness;
- necessity of any new ontology;
- production authorization for a discovered gap.

Closure classification:

```text
SYNTHETIC SYSTEM EVIDENCE: YES
HUMAN AUTHOR EVIDENCE: NO
NATURAL WORKFLOW EVIDENCE: NO
PROSE / READER-EXPERIENCE EVIDENCE: NO
ONTOLOGY AUTHORIZATION: NO
IMPLEMENTATION AUTHORIZATION: NO
EXTRACTION AUTHORIZATION: NO
SCALE AUTHORIZATION: NO
```

## 4. Baseline representation-plane audit

This audit is part of the frozen protocol because Auteur already has multiple
Series-related representation paths. A failure must not be called a missing
concept when the concept already exists in another authoritative plane.

At repository baseline `588fb1ef88184be9246d406fd1c90737b7c09cf6`, the
important observed planes are:

| Plane | Primary artifacts/models | Observed role |
| --- | --- | --- |
| Universe | `UniverseIdentity` | setting profile, locations, mythology, timeline, cross-story constraints |
| Canonical Series architecture | `SeriesIdentity` | trilogy shape, Book plans, character/relationship/faction arcs, mysteries, dependencies, thematic arcs, character states, relationship states, lore, timeline, setups/payoffs |
| Book identity | `StoryIdentity` / `BookPlan` compilation | Book-level genre, target experience, central engine and identity contract |
| Accepted-history Series direction | `SeriesDirection`, `DirectionCommitment`, accepted Book Directions | sparse accepted Series promise/pressure/open question and explicit commitments |
| Accepted lived outcomes | `AcceptedRealizationBundle`, `StateTransition` | revisioned accepted Book outcomes and state changes |
| Derived long-horizon projection | `CanonicalState`, Global Map, repeated planning context, Focus | rebuildable current-state/history/relevance projection |
| Author continuity review | `SeriesProductizationService.build_continuity_review()` | planning intent + Series Direction + commitments + projected current/history evidence + impact + supporting connections |

The current code inspection shows an important seam: the canonical
`SeriesIdentity` path and the newer accepted-history/continuity-review path are
both real, but the inspected `SeriesProductizationService` composes its review
through `SeriesVerticalSliceService`; it does not directly consume the rich
`SeriesIdentity` model.

That observation does **not** pre-judge the experiment as a failure. It creates a
required distinction:

```text
CONCEPT EXISTS IN AUTEUR
!=
CONCEPT IS AVAILABLE TO THIS LONG-HORIZON REVIEW PATH
```

### Representation-plane rule

Before classifying any narrative miss, the worker/evaluator must ask:

1. Was the meaning representable in an existing authoritative Auteur artifact?
2. Was it actually stored there?
3. Was that artifact part of the intended long-horizon input path?
4. If not, is the problem integration/projection rather than representation?
5. Did the worker store the information in an inappropriate plane?

Misusing an existing artifact is an experiment/workflow issue, not evidence that
Auteur lacks the concept.

## 5. Experimental unit

One original trilogy.

### Hard bounds

These are actual experiment requirements:

| Dimension | Required |
| --- | ---: |
| Books | 3 |
| Protagonist | 1 |
| Other main characters | 5 |
| Recurring supporting characters | 10 |
| Total recurring characters | 16 |

The trilogy must also have:

- more than one meaningful faction/institution;
- more than one important location;
- multiple persistent subplots;
- multiple significant character relationships;
- material cross-Book consequences;
- at least three Book-3 planning questions whose meaning depends on older
  accepted history, not only immediate Book-2 state.

### Coverage targets, not creative quotas

The story should naturally pressure several of the following:

- relationship evolution;
- character evolution;
- faction/institution change;
- location meaning/state change;
- delayed setup/payoff;
- asymmetric knowledge or belief;
- dormant then reactivated thread;
- low-salience supporting-character information becoming important later;
- cross-Book causal chain;
- unresolved obligation/commitment;
- old event acquiring a new interpretation because later history changed its
  significance.

Creative coherence outranks hitting arbitrary counts. Do **not** add another
secret, subplot, faction, or setup merely to satisfy a benchmark number.

The final evidence report records actual achieved density.

## 6. Narrative-architecture boundary

### In scope

- Series premise and intended experience;
- Series Direction / Series Identity where current product architecture requires
  them;
- directional Book scaffolding;
- major conflicts and pressures;
- major events sufficient to establish state/causal changes;
- character goals and state changes;
- meaningful relationship changes;
- faction/institution changes;
- important location-state changes;
- persistent subplot evolution;
- mysteries/secrets;
- relevant knowledge/belief asymmetry;
- delayed setups/payoffs or obligations where the story naturally creates them;
- unresolved questions;
- commitments;
- accepted Book outcomes;
- cross-Book consequences;
- derived current-state/relevance views.

### Out of scope

- chapter-by-chapter outlines;
- scene lists;
- scene choreography;
- prose;
- dialogue;
- literary-style evaluation;
- reader emotional-response validation;
- market evaluation;
- complete trilogy manuscript generation.

Major events may be stated at architecture level when necessary to establish
transitions. They must not be expanded into chapters or scenes merely to make the
fixture feel complete.

## 7. Future direction is allowed; future detailed realization is not

Auteur's canonical `SeriesIdentity` for a trilogy requires three `BookPlan`
entries. Therefore the experiment must not pretend that Books 2 and 3 can be
completely blank.

The allowed distinction is:

```text
FUTURE DIRECTIONAL SCAFFOLDING:
ALLOWED / EXPECTED

FUTURE DETAILED CAUSAL SOLUTION:
NOT PRE-AUTHORED
```

A future Book may already have a Series function, target experience, central
pressure/engine, broad core answer, or intended scope because the current schema
requires or benefits from that direction.

It must **not** pre-author every later:

- event chain;
- revelation;
- relationship outcome;
- supporting-character role;
- secret disclosure;
- subplot resolution;
- setup/payoff mechanism;
- causal bridge.

If current schema forces more future commitment than the worker believes is
creatively appropriate, record that as product evidence rather than bypassing the
schema.

## 8. Lived-history requirement

The three Books must not be three isolated plots sharing a cast.

```text
Book 1 changes the world
→ Book 2 inherits those changed conditions
→ Book 2 changes the world again
→ Book 3 inherits both layers of history
```

At least half of Book 3's major pressures should materially depend on accepted
consequences originating in Books 1 or 2.

Useful signs of lived history include:

- trust, resentment, obligation, dependency, intimacy, rivalry, or fracture
  accumulating rather than resetting;
- institutions changing legitimacy, leadership, policy, resources, or alliances;
- locations acquiring political/social/symbolic history;
- supporting characters changing importance;
- dormant threads re-entering later decisions;
- old actions producing delayed consequences;
- later events changing how an earlier event is interpreted.

## 9. Fresh-context isolation

Fresh worker contexts are a hard invariant for the primary trilogy result.

### Session A — Series seed + Book 1

The first worker:

1. performs the runtime/workspace gate;
2. verifies the frozen protocol and exact baseline;
3. refreshes the representation-plane audit against the exact checkout;
4. creates the Series seed and required directional scaffolding;
5. creates Book-1 architecture only;
6. stores/accepts information only through legitimate Auteur surfaces;
7. captures evidence;
8. freezes Session-A output;
9. stops.

The chat/context ends.

### Session B — Fresh Book 2 worker

A genuinely fresh worker receives the frozen protocol and repository state, not a
handwritten Book-1 summary from Session A.

Before designing Book 2, it records what normal Auteur surfaces provide and what
additional source inspection is required. It then develops and accepts Book-2
architecture, captures evidence, freezes output, and stops.

The chat/context ends.

### Session C — Fresh Book 3 worker

Another fresh worker reconstructs the accumulated Series through Auteur and
creates Book-3 architecture.

It must exercise at least three later-Book decisions that depend on older
accepted history. The exact creative content is not pre-scripted, but the set
should naturally include pressure from multiple categories such as relationship
history, an old obligation/setup, asymmetric knowledge, a revived subplot, or a
supporting character whose relevance increased.

After Book 3 is accepted, freeze the **primary normal-accumulation evidence**.
Only after that freeze may revision stress begin.

### Revision pass — after the clean trilogy baseline

Change exactly one semantically important Book-1 fact/transition.

The revision must change meaning, not merely wording. Inspect impact across the
already accepted Books 2 and 3.

The revision pass may occur after Session C's primary evidence is frozen. It must
not alter the already-recorded normal-accumulation result.

### Session D — Fresh independent adversarial evaluator

A fresh evaluator inspects the frozen protocol and evidence. It does not create
story content. Its job is to challenge attribution, contamination, and claim
ceiling before Owner Gate.

## 10. Manual reconstruction accounting

Every later worker must distinguish three access modes:

### A. Intended surfaced context

Information supplied through the normal author-facing/review/planning surface
being tested.

### B. Targeted authoritative lookup

A narrow inspection of a known authoritative artifact to resolve a specific
question.

### C. Broad manual reconstruction

Reading substantial earlier Book/Series artifacts because the intended Auteur
surface did not provide enough context to continue.

Broad reconstruction is not forbidden; hiding it is forbidden.

The primary product question is whether later workers can continue without
category C becoming necessary for the important decisions.

## 11. Naturalistic pressure families

The experiment must include enough narrative density to exercise the following
questions, but it must not script their exact creative answers in advance.

### Low-salience → high-salience

At least one supporting-character fact, relationship, or thread that is minor in
Book 1 should become materially relevant in Book 3.

Evaluate whether the information was:

- never represented;
- represented but not persisted;
- persisted but not projected/integrated;
- projected but not selected;
- selected but reasoned over incorrectly;
- available but explained poorly.

### Knowledge asymmetry

At least one consequential later decision should depend on characters possessing
incompatible knowledge/beliefs or on a meaningful difference between accepted
world-state truth and a character's belief.

Do not create an epistemic ontology in advance. Test current representations
first.

### Relationship path dependence

At least one Book-3 decision should depend on *how* a major relationship arrived
at its current state, not only the final label.

A generic explanation is not evidence by itself that a new `Trajectory` entity
is required.

### Delayed setup / obligation

At least one meaningful earlier setup, promise, mystery, commitment, or obligation
must remain relevant beyond the Book where it was introduced. At least one
important thread should still be open when a later planning decision encounters
it.

Again, test current Series setup/payoff, commitment, open-question, dependency,
and history representations before proposing new ontology.

## 12. Revision stress

The revision occurs **after** Book 3 and the normal-accumulation result are frozen.

Evaluate:

1. accepted/revisioned lineage preservation;
2. current-state reconstruction;
3. stale/suspect/contradictory impact where applicable;
4. preservation of already accepted Books 2 and 3 without silent rewrite;
5. false-positive impact on unrelated material;
6. whether later planning/review surfaces the revision consequence;
7. whether the system distinguishes affected-by-revision from requires-review-now.

The revision result is a separate evidence layer from the clean trilogy result.

## 13. Failure taxonomy

Every consequential failure receives one primary class before any architecture
response is proposed.

| Class | Definition |
| --- | --- |
| `REPRESENTATION` | Important meaning cannot be expressed adequately in existing authoritative Auteur concepts. |
| `PERSISTENCE` | Meaning can be represented but is lost/corrupted over time. |
| `INTEGRATION_PROJECTION` | Meaning exists in an authoritative/accepted Auteur plane, but the relevant downstream long-horizon surface does not consume/project/connect it. |
| `CURRENT_STATE` | History exists but current state is reconstructed incorrectly. |
| `IDENTITY` | Characters, factions, locations, threads, or artifacts are confused/duplicated. |
| `SELECTION` | Relevant projected history exists but is not surfaced for the decision. |
| `OVERLOAD` | Too much irrelevant history is surfaced and materially harms orientation. |
| `REASONING` | Correct evidence is surfaced but the derived connection/conclusion is wrong. |
| `EXPLANATION` | Evidence/reasoning may be sound but the author-facing explanation is materially inadequate. |
| `REVISION` | Upstream revision propagation/downstream preservation is incorrect. |
| `AUTHORITY` | Derived/interpretive output crosses accepted/canonical boundaries. |
| `WORKFLOW` | Capability exists but normal product operation makes it materially hard/impossible to use. |
| `EXPERIMENT` | Apparent failure comes from protocol, fixture misuse, context leakage, or evaluator contamination. |

Prohibited inference:

```text
OBSERVED MISS
→ NEW ONTOLOGY REQUIRED
```

Required sequence:

```text
OBSERVED MISS
→ LOCATE FAILURE CLASS
→ CHECK EXISTING REPRESENTATION
→ CHECK WHETHER IT WAS STORED IN THE CORRECT PLANE
→ CHECK INTEGRATION / PROJECTION
→ CHECK SELECTION / REASONING / EXPLANATION
→ CHECK RECURRENCE / MATERIALITY
→ OWNER GATE
→ ONLY THEN CONSIDER NEW WORK
```

## 14. Evidence capture

For every major phase record separately:

### System facts

- exact repository revision;
- frozen protocol revision;
- branch/worktree identity;
- commands/surfaces used;
- accepted/canonical artifacts produced;
- derived artifacts/reviews produced;
- validation/diagnostic results;
- provenance/rebuild results where applicable;
- runtime errors.

### Narrative facts

- achieved cast/faction/location/thread density;
- important accepted state transitions;
- significant relationships;
- unresolved commitments/questions;
- delayed setups/payoffs/obligations actually used;
- knowledge asymmetries actually used;
- cross-Book dependencies;
- revision lineage.

### Worker behavior

- intended surfaced context used;
- targeted authoritative lookups;
- broad manual reconstruction;
- mistaken identities;
- unsupported assumptions;
- omitted relevant history;
- irrelevant history surfaced.

### Interpretation

Keep researcher interpretation separate from observed system facts. A proposed
capability must never be written as though it were already a demonstrated
representation gap.

## 15. Descriptive measurements

Collect useful counts without producing a synthetic aggregate score.

Examples:

- accepted narrative elements by Book;
- significant relationships actually used;
- cross-Book dependencies;
- Book-3 probes supported correctly;
- relevant historical items surfaced;
- irrelevant items surfaced;
- targeted lookups;
- broad reconstruction events;
- identity confusions;
- representation failures;
- integration/projection failures;
- authority-boundary violations;
- review/context size by Book;
- rebuild-equivalence outcomes;
- revision-impact breadth.

No weighted `Auteur Score` or leaderboard is permitted.

## 16. Success criteria

A strong positive result in this one tested trilogy requires:

1. Book 3 is reached with materially accumulated narrative complexity;
2. the sixteen-character cast remains identifiable without systemic identity
   confusion;
3. important factions, locations, relationships, subplots, and accepted outcomes
   remain coherent;
4. fresh Book-2 and Book-3 workers can continue using Auteur without broad manual
   reconstruction becoming necessary for the important decisions;
5. at least three Book-3 decisions correctly recover older relevant history;
6. low-salience earlier information can become relevant again;
7. at least one path-dependent relationship is reconstructed usefully;
8. at least one knowledge asymmetry or delayed obligation/setup is handled or
   yields a clearly classifiable bounded failure;
9. no derived output silently becomes canonical;
10. no material information-load failure prevents orientation;
11. after the clean trilogy result is frozen, revision lineage/downstream
    preservation remain coherent or yield a clearly attributable revision
    failure.

A positive result does not establish larger-scale validation.

## 17. Valuable negative outcomes

Examples of useful failures:

- `SeriesIdentity` holds relationship evolution but continuity review cannot see
  it → `INTEGRATION_PROJECTION` candidate, not automatically `REPRESENTATION`;
- accepted history exists but an old relevant fact never reaches Book-3 review →
  `SELECTION` or projection candidate;
- current primitives genuinely cannot represent consequential belief asymmetry →
  possible `REPRESENTATION` candidate after ruling out misuse/integration;
- review grows until useful context is buried → `OVERLOAD` / scale-pressure
  candidate;
- later worker can proceed only after broad manual reading of Books 1–2 → tested
  reconstruction path failure;
- revision rewrites accepted downstream history or produces incoherent current
  state → `REVISION` defect candidate.

Every candidate waits for Owner Gate.

## 18. Invalidating conditions

Mark the affected claim `INVALID / CONTAMINATED` if materially influenced by:

- hidden Book-1/Book-2 summaries supplied outside the declared product path;
- continuation in the same conversational context across fresh-worker phases;
- production code/schema changes during the run;
- a fully pre-solved trilogy whose later phases merely retrieve a master plan;
- evaluator expected answers leaked to story workers;
- retrospective rewriting of the fixture to make the product look better;
- chapter/prose quality treated as architecture evidence;
- synthetic evidence reported as human/natural-use evidence;
- important information deliberately stored in the wrong Auteur plane and then
  cited as a product representation failure.

Minor deviations that cannot plausibly affect the central claim may be retained
if explicitly logged and justified.

## 19. Hard invariants

1. No chapter outlines or prose in V1.
2. No production code or schema changes during execution.
3. No new ontology merely to satisfy the fixture.
4. No extraction reopening.
5. No pre-authorized scale implementation.
6. No hidden whole-story summary for later fresh workers.
7. No silent acceptance outside existing authority boundaries.
8. Derived/rebuildable views remain non-canonical.
9. Affected-by-revision is not automatically requires-review-now.
10. Currentness is not relevance.
11. Relevance is not causal support.
12. Unknown/unvalidated is not failed without observed failure.
13. Synthetic success is not human usability evidence.
14. No automatic V2 or implementation follows from closure.
15. Existing canonical Series architecture and accepted-history architecture must
    be distinguished rather than conflated.

## 20. Independent adversarial review

Use **one fresh independent reviewer after all primary and revision evidence is
frozen**.

Its purpose is epistemic challenge, not parallel story construction.

The reviewer should assume the provisional conclusion may be wrong and inspect:

- hidden context leakage;
- manual reconstruction mislabeled as product support;
- information stored in the wrong plane;
- representation failures that are actually integration/projection failures;
- projection failures that are actually selection/reasoning failures;
- fixture constraints that manufactured the apparent need for a capability;
- plausible but unsupported narrative answers;
- overclaiming from one synthetic trilogy;
- authority leakage;
- density that exists on paper but never actually affects later decisions;
- researcher interpretation presented as system fact.

Do not use parallel sub-agents to design pieces of the trilogy. The story
architecture is tightly coupled and each Book phase should have one coherent
worker.

## 21. Owner Gate

No result automatically authorizes implementation.

Allowed primary dispositions:

### A. `ARCHITECTURE_SUFFICIENT_AT_TESTED_TRILOGY_DENSITY`

Current representations and reconstruction path are adequate for the tested
case. No architecture work is warranted from this evidence.

### B. `PARTIALLY_SUFFICIENT / BOUNDED_GAPS_IDENTIFIED`

The tested path works broadly but one or more material bounded gaps recur.

### C. `REPRESENTATION_GAP_DEMONSTRATED`

A material recurring meaning cannot be expressed adequately after ruling out
wrong-plane storage, integration/projection, selection, reasoning, and workflow
failure. This authorizes reassessment, not automatic schema work.

### D. `INTEGRATION_OR_PROJECTION_GAP_DEMONSTRATED`

Auteur already represents the meaning, but the tested long-horizon path does not
consume/project/connect it adequately.

### E. `REASONING_OR_SELECTION_GAP_DEMONSTRATED`

Representation and projection are adequate, but later relevance/reasoning is not.

### F. `INFORMATION_LOAD_PRESSURE_DEMONSTRATED`

Architecture remains coherent but density materially overwhelms selection or
presentation.

### G. `REVISION_GAP_DEMONSTRATED`

The clean trilogy path is separately classified, but the post-freeze upstream
revision exposes a material revision/impact defect.

### H. `INVALID_OR_INCONCLUSIVE`

Contamination, fixture weakness, insufficient pressure, or mixed evidence blocks
product conclusions.

Multiple bounded secondary findings may accompany one primary disposition.

## 22. Stopping rule

Stop and return to Owner Gate when:

- an invalidating contamination makes the remaining claim uninterpretable;
- a hard product boundary prevents continuation without code/schema change;
- the fixture can continue only by maintaining a parallel research database that
  bypasses Auteur;
- the primary Book-3 evidence and required naturalistic pressures are complete;
- the post-freeze revision evidence is complete;
- continuing would only add story volume rather than new architectural pressure.

Do not continue to chapter outlines or prose from momentum alone.

## 23. Relationship to later experiments

A successful architecture V1 may justify a separate owner decision about a
**Narrative Realization Pressure** experiment:

```text
accepted trilogy architecture
→ Book outline
→ chapter outline
→ selected scene beats
```

That would test whether the abstract architecture can become a plausible event
sequence.

Only after realization pressure is understood should a separate **Selective
Expression / Reader-Experience** experiment generate prose for high-value scenes.

Neither later experiment is authorized here.

## 24. Session-A entry contract

Session A may start only when it records:

```text
FROZEN SPECIFICATION:
<exact commit containing this revision>

AUTEUR BASELINE:
588fb1ef88184be9246d406fd1c90737b7c09cf6

EXPERIMENT:
DENSE TRILOGY NARRATIVE ARCHITECTURE STRESS TEST V1

EXECUTION AUTHORIZATION:
OWNER APPROVED

STORY FIXTURE BEFORE START:
NONE

CHAPTER OUTLINES:
NOT AUTHORIZED

PROSE:
NOT AUTHORIZED

PRODUCTION CODE / SCHEMA CHANGES:
NOT AUTHORIZED

PARALLEL STORY SUB-AGENTS:
NO

FRESH-CONTEXT BOOK 2 / BOOK 3:
REQUIRED
```

If the exact main baseline has moved before the local run starts, do not silently
substitute the new revision. Report the drift and ask the owner/controller to
re-freeze the runtime baseline or explicitly approve the newer baseline.

## 25. Session-A required exit packet

Session A must stop after Series seed + Book 1 and report:

```text
RUNTIME / WORKSPACE GATE:
PASS / FAIL

FROZEN SPEC REVISION:
<sha>

AUTEUR BASELINE USED:
<sha>

REPRESENTATION-PLANE AUDIT:
CONFIRMED / REVISED WITH EVIDENCE

SERIES SEED:
CREATED / FAILED

BOOK 1 ARCHITECTURE:
CREATED / FAILED

CAST:
1 protagonist + 5 other main + 10 supporting
<actual>

FUTURE BOOKS:
DIRECTIONAL SCAFFOLDING ONLY / VIOLATION

CHAPTER OUTLINES:
NONE

PROSE:
NONE

ACCEPTED / CANONICAL ARTIFACTS CREATED:
<list>

DERIVED ARTIFACTS CREATED:
<list>

MANUAL BROAD RECONSTRUCTION:
NOT APPLICABLE FOR SESSION A / <explain>

PRODUCTION CODE CHANGES:
NONE

ONTOLOGY / EXTRACTION / SCALE CHANGES:
NONE

SESSION-A EVIDENCE:
FROZEN AT <commit/path>

NEXT STEP:
END THIS CODING-AGENT CHAT; START FRESH SESSION B
```

Session A must not continue into Book 2.

## 26. Final execution record

Closure records:

```text
TRILOGY DENSITY ACHIEVED:
<actual>

FRESH-CONTEXT ISOLATION:
PASS / FAIL

BROAD MANUAL WHOLE-HISTORY RECONSTRUCTION:
<count + cases>

PRIMARY NORMAL-ACCUMULATION FAILURE CLASS:
<class or NONE>

PRIMARY NORMAL-ACCUMULATION DISPOSITION:
<A-F/H as applicable>

REVISION RESULT:
<PASS / bounded failure + class>

ADVERSARIAL REVIEW:
<APPROVE / REVISE / INVALIDATE + reasons>

OWNER GATE:
<A-H>

IMPLEMENTATION AUTHORIZATION:
NONE UNLESS SEPARATELY GRANTED
```

## 27. Frozen disposition

```text
SPECIFICATION:
FROZEN V1

OWNER REVIEW:
COMPLETE

SYNTHETIC EXECUTION:
AUTHORIZED

SESSION A:
NOT STARTED

STORY:
NOT CREATED

CHAPTER OUTLINES:
NOT AUTHORIZED

PROSE:
NOT AUTHORIZED

PRODUCTION IMPLEMENTATION:
NOT AUTHORIZED

ONTOLOGY:
NO ADMISSION

EXTRACTION:
GATE NOT CROSSED

SCALE IMPLEMENTATION:
NOT AUTHORIZED

NATURAL-EVIDENCE CAMPAIGN POSTURE:
UNCHANGED / SEPARATE
```
