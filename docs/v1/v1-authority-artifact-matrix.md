# Auteur V1 Authority-Bearing Artifact Matrix

This matrix reconciles the authority-bearing artifact families in the V1 Product Contract against current implementation. Implementation classification is separate from final release qualification.

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

| Artifact family | Layer / scope | V1 | Authority owner | Revision / dependency semantics | Explicit acceptance | Implementation classification | Release evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| StoryIdentity | Identity / Book | SUPPORTED | Story Discovery / Identity acceptance | revision/currentness semantics + source hashes | explicit Identity acceptance | `A — ALREADY_IMPLEMENTED` | exact V1 Golden Journey pending |
| Blueprint / Structure | Structure / Book | SUPPORTED | Structure authority workflow | current target hashes, preconditions, plans/history | `revision apply --confirm` for supported revision route | `A — ALREADY_IMPLEMENTED` | exact V1 Golden Journey pending |
| Chapter Structure / Outline | Structure / Chapter | SUPPORTED | Structure/outline workflow | accepted outline/provenance + structural impact semantics | explicit owning workflow | `B — SEMANTICALLY_EQUIVALENT` | qualification bundle pending |
| Scene Realization | Realization / Scene | SUPPORTED | Realization lifecycle | ArtifactStore accepted revisions, hashes, dependencies/currentness | explicit acceptance | `A — ALREADY_IMPLEMENTED` | 20-Chapter/60-Scene topology test pending exact-head result |
| Scene Expression | Expression / Scene | SUPPORTED | ExpressionStore | source Scene revision/hash, stale/divergent review semantics | explicit `accept`; divergence requires explicit allowance | `A — ALREADY_IMPLEMENTED` | Expression boundary death tests pending exact-head result |
| Chapter Expression | Expression / Chapter | SUPPORTED | Chapter Expression lifecycle | accepted Scene/transition dependencies | explicit acceptance | `B — SEMANTICALLY_EQUIVALENT` | qualification bundle pending |
| Book Expression / Manuscript | Expression / Book | SUPPORTED | Book reconciliation/acceptance | accepted Chapter/source refs and dedicated immutable lifecycle | explicit acceptance | `B — SEMANTICALLY_EQUIVALENT` | publish/reconciliation suite pending exact-head result |
| Series Direction / accepted Series state | Identity/Structure / Series | BOUNDED | Series authority workflow | accepted-history/current-state store delegates authority history to ArtifactStore; projections derived | explicit author action | `B — SEMANTICALLY_EQUIVALENT / BOUNDED` | bounded Series evidence already exists; final release integration pending |
| Universe contracts | Identity/Structure / Universe | EXPERIMENTAL | Universe tooling | no V1 provenance-normalized vertical claim | outside primary V1 authority-complete journey | `E — OUT_OF V1 AUTHORITY-COMPLETE CLAIM` | none required for 1.0 |
| Tutor sessions | advisory | NONCANONICAL | none | local session history + source-byte fingerprints/currentness | never canonical | `D — DERIVED_NOT_REQUIRED` | Workspace/Tutor integration tests |
| Decision Cards / handoffs | derived | NONCANONICAL | none | source evidence/currentness | never canonical | `D — DERIVED_NOT_REQUIRED` | Golden Journey |
| Structure proposals / revision plans / previews | candidate/derived | NONCANONICAL UNTIL APPLY | Structure workflow | durable proposal/plan state + source/target hashes/preconditions | selection/planning are not acceptance | `D — DERIVED_NOT_REQUIRED` | Golden Journey |
| Global Map / Focus / dashboards / reports | derived | NONCANONICAL | none | rebuildable/projection-specific | never canonical | `D — DERIVED_NOT_REQUIRED` | no universal lifecycle parity required |

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

- `A — ALREADY_IMPLEMENTED`: current implementation satisfies the V1 invariant.
- `B — SEMANTICALLY_EQUIVALENT`: implementation differs in shape but satisfies the same invariant.
- `C — GENUINELY_MISSING`: implement before release or narrow V1 scope.
- `D — DERIVED_NOT_REQUIRED`: the artifact cannot grant narrative authority; full lifecycle parity is unnecessary.
- `E — OUT_OF_V1`: capability is deliberately outside the product contract.

The closure audit found no category-C need for a new provenance subsystem. Exact-candidate qualification can still expose a concrete defect in an existing path; such a defect should be fixed at its owning boundary rather than by normalizing every artifact into one storage engine.
