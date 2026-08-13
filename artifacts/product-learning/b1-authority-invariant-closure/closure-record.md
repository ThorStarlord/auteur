# B1 Closure Record — CLOSED / SUPERSEDED

> Cycle: `discovery/b1-authority-invariant-closure` — evidence-only closure of the
> recorded post-PR#58 authority-invariant binding obligation. Base: canonical
> `origin/main @ d9926b1` (PR #73 merged). Read-only discovery + this single
> documentation mutation. No production source change, no schema change, no test
> change, no bundled housekeeping, no successor opportunity invented.

## Verdict

**B1 — CLOSED / SUPERSEDED.**

The original post-PR#58 limitation — *accepted alternatives cannot explicitly bind to
the story entities or structural elements they concern without prohibited inference* —
is no longer true of the shipped product.

## The original obligation (recorded @ dc48287, post-PR#58 learning cycle)

> Accepted author-decision alternatives cannot explicitly bind themselves to the story
> entities or structural elements they concern. Downstream consequence reasoning either
> remains common to all alternatives, repeats authored declarations, or would have to
> infer relationships that the product explicitly forbids.

Authority invariant (binding): no name matching, label parsing, prose extraction, fuzzy
matching, semantic similarity, or LLM inference may silently create an accepted
relationship. Link authoring must be explicit.

## Present-day mechanisms that supersede it (verified against shipped source)

| Obligation requirement | Shipped mechanism | Evidence (origin/main @ d9926b1) |
|---|---|---|
| Alternatives bind to entities | **M1 `AlternativeBinding`** — `alternative_id` → `EntityReference` with explicit `entity_ref` + closed `EntityReferenceKind` (`concerns` / `conflicts_with`) | `author_decisions/models.py` (AlternativeBinding / EntityReference) |
| Alternatives bind to structural elements | **B4 `StructuralAnchor`** — decision-local `participants`/`carrier_refs`/`bears_on`, never promoted to canonical state | `author_decisions/models.py` (StructuralAnchor / AnchorBearsOn) |
| Authority invariant — explicit link authoring, fail-closed | `_validate_bindings` rejects unknown `alternative_id`, duplicate blocks, duplicate/conflicting references; `_resolve_entity_ref` requires an explicit `identity.`/`blueprint.`/`decision.` root and raises on malformed/unresolvable/unknown refs | `author_decisions/models.py` `_validate_bindings`; `author_decisions/context.py` `_resolve_entity_ref` |
| No silent inference | closed relationship vocabularies reject inert semantics (`concerns`/`conflicts_with`; `sustains`/`pressures`; `bears_on`); resolution is pure field-path — no name/fuzzy/LLM code in the binding/anchor/significance machinery | source inspection across `models.py`/`context.py`/`consequences.py` |

The original Case D / Case E discriminators are now expressible without inference:
- Case D (what `nine_parallel_arcs` / `one_structural_spine` refer to) → structural
  anchors with participants.
- Case E (Anders' debt ↔ Anders, etc.) → `alternative_bindings` with `entity_ref` →
  `identity.characters[...]`.

## The historical mechanism-family comparison is no longer outstanding

The 2–4 family comparison was a means to an end: select how to make alternative↔entity
binding explicit. M1 (authored-on-alternative) shipped as the selected mechanism; B4
(separate relationship declarations) shipped as well; the shared exact-root reference
model is in use. Because the *problem* the comparison was meant to solve has already
been solved and shipped, the comparison itself is no longer a product obligation.

## BUG #59 — not part of this closure

BUG #59 (the `choose_k_of_n` per-alternative-finding TypeError) was a separate
engineering defect, tracked and resolved separately from this product opportunity. It
is not part of the B1 closure claim; its exact historical fix provenance is not
reconstructed here.

## Evidence language (what this closure proves and does not prove)

**Proves:** the recorded B1 limitation is no longer present in the current shipped
product; the authority-invariant binding obligation is answered by M1 + B4 with the
invariant enforced fail-closed.

**Does not prove:** every possible future binding need is solved; the current ontology
is complete; no future authority-related binding failure can occur.

## Close-out

This is the complete B1 closure record. No successor opportunity is manufactured; no
follow-on initiative is started. Campaign record marks B1 CLOSED / SUPERSEDED.
