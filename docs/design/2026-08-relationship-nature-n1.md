# Implementation Design — N1: Closed Relationship-Nature Vocabulary on Anchor bears_on

> Phase: implementation design (slice 1). Human selection: **N1 — closed
> relationship-nature vocabulary**, with binding design constraints (structural_role NOT
> in this slice; N2 remains the next richness candidate). Base SHA: 2ed814e (main, PR #64).
> Production source is read-only until this design is approved and construction begins.
> Evidence: solution discovery at
> `auteur-relationship-nature-discovery/artifacts/solution-discovery/relationship-nature/report.md`
> (481b451); author judgment + selection at
> `auteur-anchors-learning/artifacts/product-learning/structural-anchors/synthesis.md`
> (2eeb8ea).

## 0. Design hypothesis (binding)

Extend an individual `bears_on` relationship with the smallest explicit author-owned
semantic describing **how that anchor relates to that particular target**. `nature`
belongs to the anchor→target relationship, NOT to the anchor globally:

```yaml
bears_on:
  - ref: blueprint.contract.mandatory_ending_tone
    relationship: bears_on
    nature: sustains
```

No `structural_role`, no function profiles, no canonical Blueprint entities in this
slice. N2 remains the next richness candidate IF N1 later proves insufficient.

## 1. Vocabulary decision (binding: the shipped invariant)

**First-slice enum: EXACTLY TWO values — `sustains` and `pressures`.**

Per the vocabulary invariant ("if Auteur accepts an authored semantic relationship, the
consumer knows what that relationship means"), every accepted value ships with pinned
author-facing meaning, deterministic consumer meaning, composed-cut consequence, and
difference-from-the-other. `complicates` and `resolves` are DEFERRED candidates, NOT
schema values: their author-facing distinctions are not yet crisp enough to pin
(complicates overlaps pressures; resolves implies a direction toward resolution that
borders on the creative verdict the consumer must not issue).

### 1.1 `sustains`

1. **Author-facing meaning:** the subplot keeps the target property alive or intact —
   e.g. Marta's pregnancy sustains the ending's ambiguity (hope left unresolved).
2. **Deterministic consumer meaning:** the relationship type is "sustaining" — the
   consumer reports the declared sustaining relationship with the resolved target value.
3. **Composed consequence with authored kept/cut:** for a cut alternative —
   `cut alternative <X> removes its declared sustaining relationship to <target> = <value>`;
   for a kept alternative — `kept alternative <X> preserves its declared sustaining
   relationship to <target> = <value>`. The consequence states WHAT the operation removes
   or preserves (the declared relationship type); it NEVER states whether that is
   creatively good or bad.
4. **Difference from `pressures`:** sustaining = declared preservation of the target;
   pressuring = declared tension exerted on the target. The composed consequences name
   different relationship types.

### 1.2 `pressures`

1. **Author-facing meaning:** the subplot exerts declared tension on the target — e.g.
   Anders' debt pressures the ending toward resolution.
2. **Deterministic consumer meaning:** the relationship type is "pressuring" — reported
   with the resolved target value.
3. **Composed consequence:** `cut alternative <X> removes its declared pressuring
   relationship to <target> = <value>` / `kept ... preserves ...`.
4. **Difference from `sustains`:** see 1.1.4.

**Minimal-pair rationale:** `sustains` + `pressures` is the smallest vocabulary that
breaks the Anders-vs-Marta tie (Marta sustains, Anders pressures — authored, never
inferred) and both values have crisp pinned semantics. No value ships without defined
consumer meaning.

## 2. Model change (design Q: where nature lives)

`AnchorBearsOn` gains one optional field:

```python
class AnchorRelationshipNature(str, enum.Enum):
    sustains = "sustains"
    pressures = "pressures"

class AnchorBearsOn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ref: str
    relationship: AnchorRelationshipKind = AnchorRelationshipKind.bears_on
    nature: AnchorRelationshipNature | None = None
```

- `nature` is per-relationship (anchor→target), matching the design hypothesis.
- `None` = "relationship nature not explicitly supplied"; the existing `bears_on`
  relevance relationship remains valid and unchanged.

## 3. Authority (binding)

`nature` is explicitly authored. NEVER inferred from: subplot names, Identity prose, the
decision question, `combination_direction`, target values, character roles, or existing
thread vocabulary. Absence of `nature` = "relationship nature not explicitly supplied" —
no nature-derived consequence. Nothing in the consumer scans prose/labels/names to
assign a nature.

## 4. Backward compatibility (binding)

- Existing B4 anchors with plain `bears_on` (no `nature`): behavior byte-for-byte —
  the shipped `anchor <X> bears on <ref> = <value>` info remains, no nature-derived
  consequence.
- Unanchored artifacts and Case D: unchanged (no-op control).
- Frozen golden expectations (expected-consequences.yaml for D/E): unchanged.

## 5. Consumer behavior (non-echo composition)

The consumer composes authored nature with already-known decision semantics
(kept/cut), so the feature is not a pure echo:

- **Per-alternative (relationship level):** when `nature` is authored, the bears_on
  finding becomes `anchor <X> bears on <ref> = <value> (nature: sustains)` — the nature
  label attaches to the resolved relationship.
- **Composed with direction (per combination, JSON + text):** for each member
  alternative with authored nature, when `combination_direction` is authored:
  - cut member → info `cut alternative <X> removes its declared <nature> relationship
    to <ref> = <value>`;
  - kept member → info `kept alternative <X> preserves its declared <nature>
    relationship to <ref> = <value>`.
  The consequence derives from (authored nature) + (authored direction) + (resolved
  target value). It states what the operation removes/preserves — non-ranking,
  non-verdict. When direction is absent, no composed consequence (nature echoes at
  relationship level only).
- Closing lines unchanged: no recommendation, no verdict.

## 6. Case E golden discriminator (binding)

Authored difference against the SAME target:
- anders_debt: `bears_on blueprint.contract.mandatory_ending_tone, nature: pressures`;
- marta_pregnancy: same ref, `nature: sustains`.

With direction=kept (k=2), the deterministic cut consequences differ:
- combo [anders_debt, marta_pregnancy]: both kept → `kept alternative anders_debt
  preserves its declared pressuring relationship ...` / `kept alternative
  marta_pregnancy preserves its declared sustaining relationship ...`;
- combo [anders_debt, signe_marriage]: cut marta → `cut alternative marta_pregnancy
  removes its declared sustaining relationship to blueprint.contract.mandatory_ending_tone
  = bittersweet`;
- combo [marta_pregnancy, signe_marriage]: cut anders → `cut alternative anders_debt
  removes its declared pressuring relationship ...`.

The Anders-vs-Marta consequences differ deterministically (sustaining vs pressuring).
The report still refuses: `therefore cut Anders` / `therefore cut Marta` (closing lines).

## 7. Case D control (binding)

No nature authored anywhere on Case D → byte-identical M1/B4 behavior (existing
no-op control tests cover).

## 8. Deferred (binding)

- `structural_role` (N2 dimension) — next richness candidate, only if N1 evidence
  demands it;
- full structural-function profiles;
- canonical Blueprint subplot entities;
- Candidate-A POV probe coverage;
- `complicates` / `resolves` vocabulary values;
- ranking/scoring/recommendations.

## 9. Test surface (for the construction cycle, pending approval)

- schema: nature parses; unknown nature value rejected; extra fields forbidden;
  absence → None;
- authority/back-compat: existing anchored fixture (no nature) byte-identical;
  unanchored Case D unchanged;
- consumer: nature-labeled bears_on finding; composed kept/cut consequences per
  combination (JSON + text); direction absent → no composition;
- golden: Case E with authored sustains/pressures → cut consequences differ
  deterministically; no verdict lines;
- fail-closed: bogus nature → load error.

## 10. Stop point

This design ends at the approval gate. Human design approval (or revision request) is
required before construction begins. Production source remains read-only until then.
