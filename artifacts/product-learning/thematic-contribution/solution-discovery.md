# Solution Discovery — Referent-Level Thematic Contribution

> Cycle: `discovery/thematic-contribution` (worktree `H:/GithubRepositories/auteur-thematic-discovery`,
> base = canonical `origin/main @ c968a747`). Zero production change. Solution Discovery
> only — stop before Implementation Design. Narrowly scoped to the thematic/contribution
> slice; NOT reopening footprint, NOT redesigning StoryThread, NOT a generic contribution
> ontology.

## Demonstrated product opportunity (validated Case-4 result)

> **When a durable structural referent stops participating, Auteur's current thematic
> reasoning can continue counting thematic work that is no longer operative. In the
> validated case, explicitly removing that contribution materially changed the author's
> next structural action. However, `StructuralReferent` currently has no explicit
> representation of the contribution, so the product cannot make that reasoning change
> without inference.**

Both halves of the evidence are in place:

```
CAPABILITY GAP   referent-level thematic contribution not currently expressible    ✅
AUTHOR VALUE     excluding the contribution of a cut referent changes next action   ✅
                    ↓
BOUNDED R2 EARNED — thematic/contribution slice only
```

## Discovery question

> **What is the smallest explicit, author-controlled representation of a structural
> referent's thematic contribution that lets downstream reasoning distinguish declared
> thematic coverage from currently operative thematic contribution, without inferring
> contribution from prose or expanding into a general contribution ontology?**

## First falsification — can existing authored representation carry the validated nuance?

Tested against shipped source (`origin/main @ c968a747`):

| Existing representation | Can it express "pressures the ending AND supplies material that makes the ending credible"? |
|---|---|
| `bears_on` + `nature` (anchor) | **No.** `AnchorRelationshipNature` is closed to exactly `{sustains, pressures}` (N1, `models.py:138-145`). "Helps make the ending emotionally credible" is neither; collapsing it into `sustains`/`pressures` is exactly what the human explicitly forbade. |
| `StructuralReferent` | **No.** Deliberately carries NO `bears_on`/`nature` (durable subset = id/kind/participants/carriers/provenance; `extra="forbid"`). |
| `thematic_function` (thread) | **No.** Free-text prose on `StoryThread`, not the referent; the whole Case-4 problem is that this aggregation counts declared thread work, and it is prose Auteur must not parse. |
| F1 `goal_significance` | **No.** Decision-local ordering of goals (ending tone > POV) — not a referent-level contribution. |
| carrier relationships | **No.** `carrier_refs` link referent→thread; they say *where* a referent is realized, not *what it contributes*. |
| theme/contract references | **No.** `theme.thesis`/`central_question` are story-level; no per-referent contribution link. |

**Falsified:** no existing authored representation can carry the validated nuance faithfully.
The nuance is not decomposable into `sustains`/`pressures` (the human explicitly required
preserving both "pressures the ending" and "supplies material that makes the ending
credible" — a single subplot doing both).

## Mechanism families compared

### F1 — Reuse existing relationship semantics
**Falsified above** — closed `sustains`/`pressures` vocabulary cannot express the nuance;
collapsing is explicitly forbidden.

### F2 — Explicit contribution → existing thematic-target reference
The referent gains an authored reference to an existing thematic target (e.g. a theme
thesis term, a contract element) with the smallest additional semantics describing the
contribution. Requires deciding whether the "contribution" is a categorical, relational,
free-text-but-explicit, or structured form — deliberately NOT preselected here.

### F3 — Narrow referent-local thematic contribution declaration
A referent-local authored declaration (smallest shape, vocabulary open until design).
Most direct fit for the validated case; risk is it becomes a generic "note" field.

### F4 — Richer/general contribution model (upper bound)
A general structural-function/contribution model of which thematic is one example.
**Rejected for this slice** — the human explicitly said: validated thematic case → smallest
thematic mechanism → only repeated evidence earns general contribution semantics.

## End-to-end bar (binding)

The winning mechanism must support:

```
explicit authored contribution
→ durable structural referent
→ current participation known
→ non-participating contribution excluded
→ thematic reasoning changes meaningfully
→ author sees the validated thematic loss
```

A new field merely echoed in diagnostics does not qualify (the M2/echo trap).

## Controls (binding)

1. participating referent → contribution remains operative;
2. non-participating referent → contribution excluded;
3. referent with no declared contribution → no inference;
4. two referents contributing to the same thematic target;
5. one referent contributing differently to multiple targets, if the mechanism claims to
   support it;
6. the `pressures ending` + `helps make ending credible` nuance (both expressible);
7. thread still exists after referent stops participating;
8. F1 significance remains decision-local;
9. existing Blueprints/referents backward compatible;
10. no automatic application from `chosen`;
11. no prose/name/fuzzy/LLM inference.

## Permitted verdicts (this discovery returns one)

- **EXISTING SEMANTICS SUFFICIENT** — no new representation needed.
- **NARROW THEMATIC-CONTRIBUTION REPRESENTATION EARNED** — smallest surviving explicit
  mechanism identified.
- **GENERAL CONTRIBUTION SEMANTICS REQUIRED** — narrow mechanisms fail; broader ontology
  needed; stop for human selection.
- **CURRENT REASONING CANNOT USE IT MEANINGFULLY** — representation storable but the
  downstream value test cannot be reproduced without a larger reasoning-model change.

## Claim language

- **human-demonstrated:** excluding a cut referent's thematic contribution materially
  changes the next structural action (Case-4 zero-code test, T2).
- **agent-validated:** this discovery — existing semantics falsified; F3 narrowest;
  nuance-preservation is the binding control.
- **post-merge observed:** n/a (nothing built).
