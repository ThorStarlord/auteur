# Auteur V1 Authority-Bearing Artifact Matrix

This matrix defines what must be knowable for every artifact family that V1 permits to become narrative authority. `VERIFY` means the current implementation must be reconciled against the contract before release; it is not a claim that the capability is missing.

## Required invariant

For every `SUPPORTED` authority-bearing family, V1 must answer:

1. Who owns authority?
2. What revision/current pointer is authoritative?
3. What direct dependencies matter?
4. How is freshness/currentness determined?
5. What happens after an upstream accepted change?
6. What explicit action grants authority?
7. Does failure leave prior authority intact?
8. Can prior accepted revisions/decisions be inspected?

| Artifact family | Layer / scope | V1 | Authority owner | Revision/history | Dependency/freshness | Explicit acceptance | Failure atomicity | Release disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| StoryIdentity | Identity / Book | SUPPORTED | Story Discovery / Identity acceptance | implemented | implemented/verify coverage | implemented | implemented | VERIFY E2E |
| Blueprint / Structure | Structure / Book | SUPPORTED | Structure authority workflow | implemented | implemented | `revision apply --confirm` for supported revision route | implemented | VERIFY E2E |
| Chapter Structure / Outline | Structure / Chapter | SUPPORTED | Structure/outline workflow | implemented/verify | implemented/verify | explicit owning workflow | verify | VERIFY |
| Scene Realization | Realization / Scene | SUPPORTED | Realization lifecycle | ArtifactStore-backed | implemented/verify | explicit acceptance | verify | VERIFY |
| Scene Expression | Expression / Scene | SUPPORTED | ExpressionStore | candidate + accepted revision | source Scene revision/hash; stale/divergent review semantics | explicit `accept`, divergence requires explicit allowance | candidate writes use temp/replace; acceptance path must be qualified | VERIFY |
| Chapter Expression | Expression / Chapter | SUPPORTED | Chapter Expression lifecycle | implemented | accepted Scene/transition refs | explicit acceptance | implemented/verify | VERIFY |
| Book Expression / Manuscript | Expression / Book | SUPPORTED | Book reconciliation/acceptance | implemented | accepted Chapter/source refs | explicit acceptance | implemented/verify | VERIFY |
| Series Direction / accepted Series state | Identity/Structure / Series | BOUNDED | Series authority workflow | accepted-history/current-state machinery | currentness/continuity projections | explicit author action | verify bounded path | VERIFY BOUNDED |
| Universe contracts | Identity/Structure / Universe | BOUNDED | Universe owning workflow | verify | verify | explicit author action | verify | VERIFY BOUNDED |
| Tutor sessions | advisory | NONCANONICAL | none | local session history | source-byte fingerprints/currentness | never canonical | n/a | NOT AUTHORITY |
| Decision Cards / handoffs | derived | NONCANONICAL | none | derived/persisted where applicable | source evidence/currentness | never canonical | n/a | NOT AUTHORITY |
| Structure proposals / revision plans / previews | candidate/derived | NONCANONICAL UNTIL APPLY | Structure workflow | durable proposal/plan state | source/target hashes/preconditions | selection/planning are not acceptance | fail closed | NOT AUTHORITY UNTIL APPLY |
| Global Map / Focus / dashboards / reports | derived | NONCANONICAL | none | rebuildable/projection-specific | current accepted sources | never canonical | n/a | NOT AUTHORITY |

## Realization ↔ Expression boundary

`docs/expression-boundary.md` is the normative V1 boundary. Expression can create wording, dialogue, imagery, rhythm, sensory detail, interiority, paragraphing, and local pacing. It cannot silently change participants, event order, goal/opposition/turn/decision/outcome, knowledge state, emotional changes, location/action facts, or arc realizations owned upstream.

When prose evidence implies an upstream change:

```text
Expression evidence
→ derived validation/review finding
→ noncanonical Realization proposal
→ explicit owning-workflow decision
→ accepted Realization revision (if approved)
→ Expression revalidation
```

No parser/model output may silently rewrite Realization.

## Audit classification

During closure, every `VERIFY` cell is classified as exactly one of:

- `A — ALREADY_IMPLEMENTED`: current implementation satisfies the V1 invariant.
- `B — SEMANTICALLY_EQUIVALENT`: implementation differs in shape but satisfies the same invariant.
- `C — GENUINELY_MISSING`: implement before release or narrow V1 scope.
- `D — DERIVED_NOT_REQUIRED`: the artifact cannot grant narrative authority; full lifecycle parity is unnecessary.
- `E — OUT_OF_V1`: capability is deliberately outside the product contract.

The audit must not normalize every artifact into one storage engine merely for symmetry.
