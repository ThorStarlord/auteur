# Implementation Design — Canonical Structural Referents (F2): explicit anchor promotion

> Phase: implementation design only (no construction). Mechanism **F2 — explicit,
> author-controlled promotion of a decision-local structural anchor into a durable
> structural referent**, selected by the human 2026-08-14. Discovery @ `8f5a0b7` on
> `discovery/canonical-referents`. Base SHA: 156b73cb (origin/main, PR #74 merged). The
> evidence earned a stable structural referent; it did NOT earn a first-class canonical
> `Subplot` ontology.

## 0. Product intent (binding)

Some structural things first become explicit inside an AuthorDecision (a B4
`StructuralAnchor`, e.g. `signe_marriage`). When the author later needs an accepted
outcome concerning that thing to participate in downstream structural work, Auteur must
have an explicit, stable referent for it — not infer the target from prose. Promotion is
**opt-in and author-controlled**; decision-local anchors remain local unless explicitly
promoted.

## 1. Durable vs decision-contextual (the central modeling decision)

The B4 `StructuralAnchor` mixes two kinds of fact; promotion must separate them:

| Anchor field | Durability | Rationale |
|---|---|---|
| `anchor_id` | **durable** (becomes the referent's stable id) | identity |
| `kind` | **durable** | existing narrow `StructuralAnchorKind` (subplot); NOT a new ontology |
| `participants` | **durable** | explicit character refs — stable |
| `carrier_refs` | **durable** | explicit thread refs — stable |
| `bears_on` + `nature` | **decision-contextual (NOT promoted)** | describes how the thing mattered in ONE decision; can change when the ending/goals change |

The durable referent carries identity + participants + carriers + provenance. `bears_on`
and `nature` stay decision-local by default — promoting them would freeze decision
context into story truth.

## 2. Where the referent lives (binding)

New minimal field on `StoryBlueprint`:

```python
class StructuralReferent(BaseModel):
    referent_id: str            # stable id (== promoted anchor_id)
    kind: StructuralAnchorKind  # existing narrow enum, reused (subplot)
    participants: list[str]     # explicit entity refs (identity./blueprint./decision.)
    carrier_refs: list[str]
    provenance: ReferentProvenance

class ReferentProvenance(BaseModel):
    promoted_from_decision_id: str
    promoted_from_anchor_id: str
    promoted_at: str            # ISO-8601
```

`StoryBlueprint.structural_referents: list[StructuralReferent] = Field(default_factory=list)`.

The field name is deliberately neutral (`structural_referents`, not `subplots`) and reuses
the existing `StructuralAnchorKind` — it does NOT assert a general subplot ontology, does
NOT restructure `story_engine.threads`, and does NOT introduce arbitrary-object types.
This keeps F2 distinct from the F3 escalation path.

## 3. Promotion mechanics (binding)

- **Explicit author action** via `decision promote <decision_id> --anchor <anchor_id>`
  (new author-decisions subcommand), or equivalent authored YAML edit. No automatic
  promotion; no promotion merely because `chosen` exists.
- Promotion **copies the durable subset** (id, kind, participants, carrier_refs) into a
  new `StructuralReferent` and records provenance (decision_id + anchor_id + timestamp).
- `bears_on`/`nature` are **not copied** — they remain decision-local.
- **Idempotent on duplicate promotion:** promoting the same anchor twice is a no-op
  (referent already exists → unchanged, provenance preserved) or a clear "already
  promoted" result — never a second copy.
- **Already-canonical referent:** if the decision already concerns a canonical entity
  (e.g. a `characters[i]` or `blueprint.contract.*`), promotion is inert — no new
  representation is added (the control).
- **Stale/missing reference:** promoting an anchor whose `participants`/`carrier_refs`
  reference an unresolvable path fails closed via the existing `_resolve_entity_ref`
  (no partial promotion).

## 4. How a decision refers to the promoted entity (binding)

After promotion, the accepted outcome `chosen: [signe_marriage]` can address the durable
referent by id. The decision does NOT rewrite its own historical provenance: the anchor
keeps its decision-local `anchor_id`; the referent carries a provenance pointer back.
No name matching — the id is explicit.

## 5. Separation: promotion ≠ application (binding)
Promotion answers "what durable thing was the decision about?" **Promotion MAY mutate
canonical Blueprint by creating the durable structural_referents registry entry - that
is the purpose of F2.** It must NOT enact the AuthorDecision outcome: it does NOT
interpret chosen + combination_direction as an instruction to cut, keep, delete, add,
or restructure story content, and it does NOT promote F1 significance. Downstream
application remains the separate parked campaign. The promoted referent gives
downstream reasoning an addressable target; enactment semantics stay out of scope.
## 6. Binding invariants (verbatim from the brief)

- no name matching / prose parsing / fuzzy / semantic / LLM matching;
- no automatic promotion or automatic canonicalization of every anchor;
- no assumption that referents are universally "subplots";
- no automatic application of `chosen`;
- promotion may create the durable structural_referents entry, but never enacts the chosen outcome or otherwise adds/deletes/restructures story content;
- no global promotion of F1 significance;
- no ranking/recommendation;
- provenance explicit;
- existing decision-local anchors remain valid without promotion;
- existing Blueprints and AuthorDecisions remain backward compatible (the new field
  defaults to empty; `extra="forbid"` untouched).

## 7. Required controls (verbatim from the brief)

1. `signe_marriage` can be explicitly promoted and receives a stable durable referent.
2. The same outcome can subsequently address that referent without prose/name inference.
3. A decision-local anchor left unpromoted remains purely local.
4. A decision concerning an already-canonical entity does not require promotion or
   duplicate representation.
5. Promotion does not itself enact `cut`/`keep`.
6. Decision-local significance does not leak into global canon.
7. Existing artifacts continue to load unchanged.

## 8. Escalation gates (stop before construction if hit)

Escalate to the human if the smallest coherent solution requires: a general canonical
`Subplot` entity; broad restructuring of `story_engine.threads`; a generic ontology for
arbitrary structural-object types; automatic decision→Blueprint application; inference to
identify promotion targets; or material changes to creative-authority semantics.

**Assessment:** this design satisfies the brief with a minimal neutral field reusing the
existing narrow `StructuralAnchorKind`, explicit opt-in promotion, provenance, idempotency,
and a strict promotion≠application split. **No escalation gate is hit.**

## 9. Verification plan (for construction, deferred)

- TDD: controls 1–7 first (RED), then schema + `decision promote` + resolution + goldens.
- Full verification stack on the merge path: pytest (categories), ruff, `scripts/check.py`.
- Independent review; autonomous merge per the envelope when scope matches, CI passes,
  review clean, exact head merged.

## 10. Stop point

This is **design only**. Construction is deferred pending the human's go-ahead (the brief
scoped this turn to Implementation Design; no escalation condition appeared, so the design
is complete and ready for construction under the envelope).
