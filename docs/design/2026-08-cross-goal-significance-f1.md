# Implementation Design — Cross-Goal Significance (F1): decision-scoped authored significance

> Phase: implementation design (slice 1, revision 1 — semantic hardening). Human
> mechanism selection: **F1 — explicit qualitative goal significance, decision-scoped,
> non-ranking**, advanced via a zero-code human reaction test (judgment
> `DECISION_CONTEXT_IMPROVED`, not `DECISION_RESOLVED_BY_PRODUCT`; recorded @ 2dcf073 on
> `discovery/cross-goal-significance`). Revision per human design review (semantic
> hardening only — the F1 mechanism remains selected). Base SHA: f9124ffa (main, PR #67
> merged). Production source read-only until approved and construction begins. Evidence:
> solution discovery @ 84dbb38; F1 reaction test in `evidence-package.md` @ 2dcf073.

## 0. Design hypothesis (binding)

The post-S1 residual is a significance gap: the product composes the cross-goal tradeoff
deterministically but can neither receive nor surface the author's decision-local
significance. The smallest fix (F1) adds an **authored, decision-scoped, non-ranking
significance declaration** that is **surfaced, never used** — echoed beside the composed
consequences with provenance, never ranked, scored, or interpreted. The human reaction
test established the narrow claim this design must satisfy:

> **F1 author impact: `DECISION_CONTEXT_IMPROVED` — cognitive/context-reconstruction
> burden reduced and a decision-local value judgment preserved durably and legibly beside
> the composed consequences. NOT `DECISION_RESOLVED_BY_PRODUCT`.**

## 0.1 Semantic contract (binding, hardening revision)

The F1 mechanism has two distinct kinds of ordering that must never be conflated:

- **Author-authored relative significance** — the capability F1 preserves: the author
  explicitly declares which of this decision's conflicting goals has precedence.
- **Product-generated or product-applied ranking** — explicitly out of scope: Auteur must
  NEVER generate the ordering, infer a missing ordering from prose, extend a partial
  ordering, turn the ordering into scores, use it to rank alternatives, or derive a
  recommendation from it.

The three states are mutually distinct, and a fourth state is NOT representable by F1:

| State | Meaning |
|---|---|
| `goal_significance` absent (null) | no significance declaration supplied — status quo |
| `goal_significance.ordered` | author explicitly declares relative significance (exactly two goals, slice 1) |
| `goal_significance.unranked` | author explicitly declares INTENTIONAL non-precedence (see §1.2) |
| "I don't know which matters more" | NOT representable by F1 — that is the deferred F3 unsettled-author problem |

## 1. Field decision (binding): one optional decision-scoped field, closed shape

**`goal_significance` on the AuthorDecision** (decision-scoped by placement — never
canonical, never on the blueprint/identity):

```yaml
# explicit relative significance (most significant first) — slice 1: EXACTLY two refs:
goal_significance:
  ordered:
    - blueprint.contract.mandatory_ending_tone
    - blueprint.identity.pov_type
# or the explicit intentional non-precedence state:
goal_significance:
  unranked: true
# or absent (None) = no significance declaration -> status quo
```

### 1.1 `ordered` — slice-1 bound to EXACTLY two distinct goal refs (binding)

- **Exactly two distinct refs, most significant first.** The observed evidence is a
  two-goal tradeoff (ending tone ↔ POV contract); a general preference-ordering language
  has NOT been earned. Three-or-more-goal orderings are rejected in slice 1 and force the
  next semantic decision when a real case arrives.
- An omitted goal must NEVER ambiguously mean "less important" — because the shape is
  closed at exactly two refs, no goal can be silently omitted.
- **Refs use the existing exact goal/target reference grammar** (`identity.` /
  `blueprint.` / `decision.` explicit roots) and are resolved by the EXISTING
  `_resolve_entity_ref` machinery — no parallel reference interpretation.
- **Reference validity (fail closed):** each ref must (a) use the explicit-root grammar,
  (b) resolve successfully, (c) be unique within the pair, and (d) refer to a goal that
  **actually participates in this decision's represented cross-goal tradeoff** — i.e. the
  ref must appear among the `bears_on` refs of this decision's structural anchors.
  Stale, unknown, wrong-type, duplicate, or unrelated-story-fact refs are rejected.

### 1.2 `unranked` — pinned semantics (binding)

`unranked: true` means, exactly:

> **The author explicitly declares that no represented goal should have precedence for
> this decision; non-ranking is intentional.**

It does NOT mean: significance unknown; the author has not decided; missing information;
"ask me later." Those cases are `goal_significance: null/absent` and belong to the
deferred F3 unsettled-author interaction. The field contract for `unranked` includes the
intentionality explicitly; the renderer may therefore state it (see §2.2).

### 1.3 Schema shape (binding)

- Closed shape: exactly `{ordered: [ref, ref]}` or `{unranked: true}` — mutually
  exclusive; `extra="forbid"`; both present rejected.
- NO numeric weights (excluded by the reaction test); no prose; no derived values.
- `None` default — backward compatible; existing artifacts parse unchanged.

## 2. Consumer behavior (binding)

1. **Echo, never use.** The consumer renders the authored declaration as a
   provenance-labeled observation and NEVER ranks, scores, reorders, filters, or branches
   on it. **Central invariant: deterministic consequence content is byte-identical with
   or without `goal_significance`.** F1 adds only provenance-labeled authored decision
   context in the probe/view surface. No downstream consequence builder branches on
   significance in slice 1.
2. **Report observation (new probe `goal_significance`, info, common scope):**
   - `ordered`: `authored goal significance (this decision): <ref1> > <ref2>`
   - `unranked`: `authored goal significance (this decision): unranked — no goal has
     authored precedence; non-ranking is intentional`
   refs: `decision: goal_significance`.
3. **View surface:** the authored declaration is shown like the existing
   `combination_direction` line (`cli.py` view): `Goal significance (authored,
   decision-scoped): ...`.
4. **Provenance distinction preserved** in the report: authored goals (blueprint),
   authored decision-local significance (`goal_significance`), and deterministic
   consequences (composed) remain labeled separately.
5. **Anti-inference regressions:** significance is NEVER derived from question/criterion
   prose, labels, target values, or any other input — only the authored field renders;
   the ordering is never extended, completed, or used.

## 3. Controls and golden discriminators (binding for qualification)

Pin at least:

1. `ordered` A > B (ending-tone > POV-contract): observation echoes the authored order;
   composed consequences byte-identical to the same artifact without the field.
2. Reversed-context B > A (the SAME two goals, reversed order in a second decision
   artifact): both valid; each echoes its own decision-scoped order.
3. `unranked: true`: observation echoes intentional non-precedence; no hierarchy invented
   anywhere.
4. Absent field: status quo — no observation, no behavior change (existing fixtures
   byte-identical).
5. "I don't know which matters more" prose with NO structured declaration → no
   significance observation (the unsettled case stays out of F1).
6. Misleading prose ("the ending matters more ...") with the field ABSENT → no
   significance observation, no effect on consequences — prose never parsed.
7. Schema fail-closed: both `ordered` and `unranked` rejected; `ordered` with one ref or
   three+ refs rejected (slice-1 bound); duplicate refs rejected; stale/unknown refs
   rejected; ref to an unrelated goal (not in this decision's bears_on refs) rejected;
   numeric weights rejected; unknown fields rejected.
8. Provenance labels: the significance observation is distinguishable from authored-goal
   and deterministic-consequence content.
9. **Central invariant:** for every control, the consequence content (observations minus
   the `goal_significance` observation, alternatives, combinations) is byte-identical to
   the same artifact without the field.

Golden discriminators: new fixtures under `tests/fixtures/author_decisions/
case-goal-significance/` (ordered A>B, reversed B>A, unranked, absent, unsettled-prose,
misleading-prose) with expected-consequences.yaml; existing goldens (case-d, case-e,
case-one-of) byte-identical.

## 4. Out of scope (binding)

F3 elicitation (including the "I don't know" unsettled case); F4 provisional Auteur
tradeoff; numeric weights / preference machinery; product-generated or product-applied
ranking of alternatives; recommendation; canonical/global goal priority; three-or-more
goal ordering; S2 (second structural dimension); richer nature vocabulary; substitution
lifecycle.

## 5. Verification plan

- TDD: failing tests first for (a) schema parses ordered (exactly 2)/unranked and fails
  closed on every invalid shape in §3.7, (b) probe emits the two observation forms, (c)
  the byte-identical-consequences invariant (§3.9), (d) absent/unsettled/misleading
  controls, (e) view renders the authored line, (f) existing goldens unchanged.
- Golden fixtures: `case-goal-significance/` per the controls above.
- Full verification stack on the merge path: pytest (categories reported separately),
  ruff, `scripts/check.py` — per `docs/engineering/release-qualification.md`.

## 6. Stop point

This design stops at human design approval before construction. No schema or code changes
until approval. The shipped surface (merged main incl. PR #67) remains the product
boundary meanwhile.
