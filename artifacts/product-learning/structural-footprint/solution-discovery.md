# Solution Discovery — Canonical Structural Footprint / Realization

> Cycle: `discovery/structural-footprint` (worktree `H:/GithubRepositories/auteur-footprint-discovery`,
> base = canonical `origin/main @ c968a747`). Zero production change. Solution Discovery
> only — stop before Implementation Design for human selection. Preceded by M2 falsified
> as standalone (@ 10f469a): participation alone cannot close the demonstrated downstream
> problem.

## Demonstrated limitation (earned by M2 falsification)

> **A durable structural referent can be explicitly identified (PR #75), but downstream
> structural reasoning cannot make meaningful use of an accepted operation because Auteur
> has no canonical representation of how that referent is realized in story structure.
> Participation alone is insufficient.**

The escalation is earned: chosen (PR #74) → referent (PR #75) → participation (M2
falsified, 10f469a) → footprint is now the question.

## Discovery question

> **What is the smallest explicit, author-controlled representation of a structural
> referent's canonical realization that lets genuine downstream reasoning respond
> meaningfully to its inclusion/exclusion, while supporting shared and multi-carrier
> structure and avoiding prose inference?**

## End-to-end proof bar (binding — same bar that caught M2)

A mechanism qualifies only if the FULL loop produces a **meaningful downstream conclusion
change**:

```
accepted chosen operation
→ durable referent
→ explicit canonical footprint
→ explicit author-controlled enactment
→ genuine downstream structural conclusion changes meaningfully
```

A new field plus a diagnostic echo does NOT qualify.

## What the analyzer actually concludes from (mapped from shipped source)

`analyze_structure` produces its structural conclusions from:

| Conclusion family | Input | Can footprint change it? |
|---|---|---|
| `threads.exceeds_subplot_budget` / `structure.subplot_budget.missing` | `thread_count` vs `subplot_budget` (counts) | Only if the analyzer redefines what "counts" — a reasoning-model change, not footprint |
| `thread.supports_main_by.lacks_escalation_or_pressure` | per-thread `supports_main_by` | No — thread's own field, independent of referents |
| `theme.thesis_unrepresented` / `theme.motifs_*` | aggregate `thread.thematic_function` over DECLARED threads | No — cutting a referent doesn't change a thread's thematic_function |
| `subgenre.*.scope_mismatch` | `subplot_budget` vs scope biases | No — budget is a count |
| `medium.genre_runway_mismatch.too_many_threads` | `thread_count` vs medium runway | No — count of declared threads |
| character/psychology/arc rules | per-character fields | No — referents not traversed |

**Decisive finding:** every thread-based conclusion aggregates over `story_engine.threads`
as **declared** structure (counts, support functions, thematic resonance). There is NO
"participating vs declared" axis anywhere in the reasoning model. A footprint that maps
referent→thread does not change any thread's own fields, so no existing conclusion
changes — unless the analyzer is redefined to count participating referents instead of
declared threads, which is a reasoning-model change, not a footprint addition.

## Mechanism families compared

### F1 — Explicit realization edges (referent→thread/carrier with precise semantics)
Mapping signe_marriage → Relationship Echo gives the analyzer a link, but the analyzer
doesn't consume referent→thread edges, and cutting A with shared thread X would need
"X still carries B" semantics. Even with edges, no existing conclusion changes without a
consumer that reasons over participation-weighted edges — i.e. a reasoning-model change.

### F2 — Contribution-level footprint (a referent's specific contribution to a carrier)
Handles shared carriers correctly (A contributes X-part, B contributes X-part; cutting A
does not remove X). This is the right *semantics* for shared/multi-carrier, but it still
requires the analyzer to reason over contributions to change a conclusion — the analyzer
today reasons over threads as wholes. Same bar: conclusion change requires a consumer
change.

### F3 — Referent-centered canonical structure (referents become reason-able units)
Makes referents first-class in analysis. Larger; begins approaching a real subplot model.
Would require the analyzer to add referent-level rules — the demonstrated need is "an
accepted operation changes structural reasoning," not "referents are analyzed as units."

### F4 — First-class subplot ontology (upper bound)
Largest switching + ontology cost. Must win convincingly; nothing so far shows the
analyzer needs a full subplot model rather than a participation-aware consumption path.

## Shared-carrier discriminator (central)

```
Referent A ─┐
            ├── Thread X
Referent B ─┘
```

Cutting A must not delete X (B still uses it). Any footprint treating referent→thread as
ownership → "cut = delete thread" is falsified immediately. F2's contribution semantics
survive this; F1 naive edges fail it.

## The three-way verdict

The discovery's central finding is that **every candidate footprint mechanism changes no
existing structural conclusion unless the downstream consumer is itself changed to reason
over participation/contribution-weighted structure**. The analyzer is built around generic
thread counts, support-function checks, and thematic resonance over declared threads.
There is no natural landing point where decision-centric footprint produces a different
conclusion without a broader reasoning-model change.

**Verdict: CURRENT DOWNSTREAM MODEL IS THE LIMIT.**

- Footprint *can* be represented (F1/F2 semantics are constructible; F2 is the right
  shared-carrier shape).
- But existing structural consumers cannot use it meaningfully — the analyzer has no
  "participating vs declared" axis, no referent/contribution consumption, and its
  conclusions are all derived from declared thread structure.
- The real opportunity is therefore **not another representation increment**: it is a
  **downstream structural-reasoning model problem** — making the analyzer
  participation/contribution-aware so an accepted operation can change a conclusion.

This is the third outcome the brief explicitly allowed, and it is the honest one: forcing
F1/F2/F3/F4 now would be growing ontology onto a consumer that structurally cannot use it.
The M2 falsification and this discovery together show the missing layer is in the *consumer
reasoning model*, not the *representation*.

## Escalation

This verdict points beyond representation into a **downstream structural-reasoning model
change** — a substantially larger conclusion than an ontology increment. It therefore
stops for human product selection. No mechanism is selected; no design; no construction.
Decision Revision & Supersession stays PARKED.

## Claim language

- **human-demonstrated:** accepted choice needs durable referent (PR #74/#75) and the
  application gap (Outcome C); participation alone insufficient (M2 falsified).
- **agent-validated:** this discovery — footprint representable but unusable without a
  consumer reasoning-model change; CURRENT DOWNSTREAM MODEL IS THE LIMIT.
- **post-merge observed:** n/a (nothing built).
