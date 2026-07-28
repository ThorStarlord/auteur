# Rejected-Outcome Representation Specification

## Status

Proposed / awaiting approval. This specification is intentionally uncommitted.

## Problem

Accepted Genre Profile resolution commitments contain `rejected_outcomes`,
but Blueprint compilation currently stores those values in
`AuthorAudienceContract.forbidden_tropes`. The field is operationally useful
but semantically overloaded: a forbidden narrative mechanism and a rejected
terminal story result are different author constraints.

## Proven current behavior

The current flow is:

```text
GenreProfileCommitment.accepted_resolution_contract.rejected_outcomes
  -> compile_to_blueprint()
  -> blueprint.contract.forbidden_tropes
  -> ProfileDerivation.obligations_applied:
       "forbidden_tropes: <value>"
  -> analyze_structure() D-RES-002
  -> genre diagnose human/JSON output
```

`GenreProfileCommitment.rejected_outcomes` is a validated list of strings.
Compilation initializes `forbidden_tropes`, appends each profile outcome once,
and records the destination in `ProfileDerivation`. D-RES-002 does not scan
all forbidden tropes as rejected outcomes; it scans provenance entries with
the `forbidden_tropes:` prefix and reports when that value appears in
`contract.expected_elements`. Its evidence also prints the complete
`forbidden_tropes` list.

`AuthorAudienceContract.forbidden_tropes` is documented as tropes that
auto-fail validation, with existing values such as `chosen_one_prophecy`,
`resurrected_hero`, `deus_ex_machina_rescue`, and
`happily ever after or happy for now`. Profile-derived values include
`superficial_happy_ending`, `permanent_separation`, and `redemptive_twist`.
Those categories are not guaranteed to be tropes; some are terminal outcomes
or resolution states.

The field can therefore contain both author-authored trope constraints and
profile-derived rejected outcomes. `ProfileDerivation` identifies the
profile-derived entries for compiled artifacts, but the list itself does not
carry per-entry source or meaning. Textual collisions are possible: the same
string can be an authored trope constraint and a profile rejected outcome.
Serialized Blueprint output exposes only the conflated list plus separate
provenance text. Downstream consumers cannot reliably infer meaning from the
list alone.

## Domain distinction

### Forbidden trope

A narrative pattern, convention, device, or recurring structural mechanism
that the author explicitly disallows, such as a deus-ex-machina rescue or a
chosen-one prophecy.

### Rejected outcome

A terminal state, resolution result, relationship state, moral result, or
story consequence disallowed by an accepted Genre Profile commitment, such as
a superficial happy ending or permanent separation.

Some strings can be ambiguous without domain metadata. They must not be
reclassified automatically. The current data gives clear examples of both
trope-like and outcome-like values, proving that one list is insufficient to
preserve meaning.

## Non-goals

- unified typed narrative-constraint framework;
- automated migration of ambiguous legacy values;
- new forbidden-trope diagnostic;
- broad CLI redesign;
- posture-policy changes;
- emotional-target, narrative-engine, or framing propagation;
- compilation blocking, acknowledgment workflows, version, or release work.

## Options considered

### Option A — Keep current field, improve metadata

This is maximally backward-compatible and low scope, but retains the semantic
collision, makes author UX misleading, and forces downstream consumers to
interpret provenance conventions. It is insufficient as a durable model.

### Option B — Add a dedicated rejected-outcomes field

An additive `AuthorAudienceContract.rejected_outcomes` field preserves the
existing trope field, makes the distinction explicit, and requires only
focused compiler, analyzer, and compatibility changes. This has the best
clarity-to-scope ratio.

### Option C — Add a unified typed constraint model

This would improve extensibility and per-entry provenance, but introduces a
large cross-layer migration and changes many downstream consumers for a
problem currently limited to one contract field.

### Option D — Keep Blueprint unchanged and use provenance only

This avoids schema changes but keeps author-facing Blueprint semantics
conflated and makes direct consumers depend on diagnostic provenance. It does
not solve the representation problem.

## Selected representation

Select **Option B**, with the field owned by `AuthorAudienceContract`, not as
an unrelated top-level `StoryBlueprint` field:

```python
rejected_outcomes: list[str] = Field(default_factory=list)
```

The contract already owns `expected_elements`, `mandatory_ending_tone`, and
`forbidden_tropes`; rejected outcomes belong beside those constraints. This
is an additive field and does not alter `StoryBlueprint`'s outer shape beyond
its existing contract model.

## Schema contract

- Type: `list[str]`.
- Default: empty list.
- Values: preserve authored/profile-provided strings; do not invent IDs.
- Normalization: none beyond existing string validation; comparison remains
  exact and case-sensitive for compatibility.
- Order: preserve input/derivation order for stable serialization.
- Duplicates: suppress duplicates within the field during compilation while
  preserving first occurrence order.
- Empty strings: reject or preserve according to the existing list contract;
  the first slice should not introduce a new normalization policy. If model
  validation is currently absent, reject only through the existing profile
  model's validation path rather than silently dropping values.
- Authored and profile-derived values may coexist in the field, but their
  origin is represented in provenance rather than inferred from text.
- Legacy Blueprints without the field load with `[]` through the additive
  Pydantic default.
- Unknown extra fields follow the existing Blueprint loader policy.
- No schema-version increment is required for an additive defaulted field.

## Ownership and authority

Rejected outcomes originate as Layer 1 Genre Profile commitments and are
compiled into the Layer 2 Blueprint contract as derived constraints. The
Blueprint field is author-visible and may be edited as an explicit working
artifact, but profile origin remains inspectable.

Profile-derived entries are not immutable against author action; an author may
remove or replace them in a Blueprint. Such divergence is diagnosed. No
operation mutates StoryIdentity silently. Explicit author values remain
visible and coexist with derived values rather than being overwritten.

Adherence posture changes only diagnostic severity. It never changes the
field, removes outcomes, or changes provenance.

## Compilation behavior

For new compilations:

1. write profile `rejected_outcomes` to `contract.rejected_outcomes`;
2. do not write those profile values to `contract.forbidden_tropes`;
3. preserve any independently authored trope constraints in
   `forbidden_tropes`;
4. record `rejected_outcomes: <value>` in `ProfileDerivation`;
5. suppress duplicate values within the dedicated field;
6. compile identically on repeated runs apart from existing timestamps.

Immediate cutover for new writes is preferred. Indefinite dual-write would
preserve the semantic duplication and make collisions harder to reason about.

## Migration policy

Use **read-old/write-new compatibility**, without automatic data movement.

- Legacy Blueprints with only `forbidden_tropes` load unchanged.
- Do not assume any legacy forbidden trope is a rejected outcome.
- For a legacy Blueprint with `ProfileDerivation` containing
  `forbidden_tropes: X`, D-RES-002 may use that explicit provenance as a
  diagnostic-only fallback until the artifact is explicitly recompiled. It
  must not copy X into the new field automatically.
- Blueprints without `ProfileDerivation` have no safe basis for separating
  meanings; preserve the list and do not migrate it.
- Existing YAML/JSON round-trips remain valid because the new field defaults
  to `[]`.
- Newly compiled artifacts use only the dedicated field for profile outcomes.
- No one-time loader migration, repair command, snapshot rewrite, or schema
  migration is required in the first slice.

This is the least destructive policy: it preserves old author data and
diagnostic behavior while making the new representation correct for new
artifacts.

## D-RES-002 semantics

D-RES-002 retains ID
`profile.resolution_contract.rejected_outcome_present` and means only
“accepted profile rejected outcome is present in the Blueprint's expected
resolution elements.”

For new Blueprints it reads `contract.rejected_outcomes` as the source of
profile-rejected outcomes and checks whether each appears in
`contract.expected_elements`. It does not scan `forbidden_tropes` and does not
diagnose ordinary trope constraints. For legacy artifacts it may use the
explicit `ProfileDerivation` fallback described above.

Evidence identifies the rejected outcome, source commitment path,
`contract.rejected_outcomes`, affected `contract.expected_elements`,
recommendation ID, and whether the value came from legacy provenance.

No separate forbidden-trope diagnostic is justified now; existing genre
contract checks already operate on `forbidden_tropes` where applicable.
D-RES-001 and D-RES-003 remain unchanged. The approved posture severity
matrix applies to D-RES-002 exactly as it does today: representation changes
do not alter posture policy.

## Override behavior

An explicit override targets a rejected outcome commitment using the existing
commitment target and stable exact value semantics. The first slice must keep
the current override contract and provenance behavior.

An override suppresses only the matching rejected-outcome D-RES-002
obligation. It does not remove or suppress an author-authored forbidden trope
with the same text, does not suppress other rejected outcomes, and does not
affect D-RES-001 or D-RES-003. If two sources produce the same text, source
and target identity remain separate; text equality is not authority equality.
Changing posture never re-enables a suppressed diagnostic.

## Provenance

`ProfileDerivation.obligations_applied` should record the dedicated
destination, for example `rejected_outcomes: superficial_happy_ending`,
while retaining source field and recommendation ID. This is sufficient for
the first slice to distinguish derived entries from authored field contents.

Per-entry structured provenance is deferred. If later requirements need stable
IDs, rationale, or multiple authority levels, that is a separate typed
constraint design rather than an implicit expansion of this field.

## Serialization

YAML and JSON should expose separate contract fields in repository field order:

```yaml
forbidden_tropes:
  - deus ex machina
rejected_outcomes:
  - restoration of the original hierarchy
```

Emit `rejected_outcomes: []` according to existing Pydantic serialization
conventions; do not introduce a special null/omission rule in this slice.
Legacy files without the field load as an empty list and retain their original
`forbidden_tropes` output when reserialized unless an explicit recompilation
creates a new artifact.

## Human and JSON behavior

The first implementation slice should preserve existing CLI output shape
unless D-RES-002 evidence needs the new path. JSON evidence should name
`contract.rejected_outcomes`; human diagnostics should call it a rejected
outcome, never a forbidden trope. Source profile, recommendation, posture,
effective severity, and affected field remain visible through existing
diagnostic metadata and rendering.

Separate Blueprint sections are sufficient UX for the first slice. A broader
authored-versus-derived display is deferred unless consumers demonstrate a
need.

## Backward compatibility

| Artifact type | Loads | Writes new field | Migrates | Behavior changes |
|---|---:|---:|---:|---|
| Legacy Blueprint without provenance | yes | only on explicit recompilation | no | none on load |
| Legacy Blueprint with provenance | yes | only on explicit recompilation | no automatic move | D-RES-002 may use provenance fallback |
| New Blueprint without profile | yes | `[]` | no | no profile diagnostics |
| New Blueprint with accepted profile | yes | yes | n/a | D-RES-002 uses dedicated field |
| Blueprint with authored forbidden tropes | yes | preserves tropes | no | tropes do not become outcomes |
| Blueprint with overrides | yes | dedicated derived values | no | targeted suppression remains narrow |

Potential serialized equality snapshots for newly compiled profile Blueprints
will change because the new field is populated and the old field no longer
receives those values. Legacy files remain loadable. API consumers should
read the new field for outcome semantics and retain `forbidden_tropes` for
trope semantics.

## Counterfactual acceptance tests

1. Authored trope remains only in `forbidden_tropes` and does not trigger
   D-RES-002.
2. Profile rejected outcome appears only in `rejected_outcomes`, has explicit
   provenance, and triggers D-RES-002 when present in `expected_elements`.
3. Same text in both fields remains distinguishable by field/source.
4. Legacy Blueprint with only `forbidden_tropes` loads without migration.
5. Proven legacy provenance preserves diagnostic fallback without moving data.
6. No-profile compilation has no derived rejected outcomes.
7. One override suppresses only its matching rejected outcome.
8. D-RES-002 retains the approved posture severity matrix.
9. Old and new Blueprint round trips preserve their respective fields.
10. Repeated compilation does not duplicate either field.
11. Human/JSON output has the same D-RES-002 ID, source, and severity.
12. D-RES-001 and D-RES-003 triggers and severities are unchanged.

## Implementation surface

| File | Expected change | First slice | Risk |
|---|---|---:|---|
| `src/auteur/blueprint.py` | Add `AuthorAudienceContract.rejected_outcomes` | yes | low |
| `src/auteur/identity.py` | Write profile outcomes to dedicated field and update provenance | yes | medium |
| `src/auteur/structure/analyzer.py` | Read dedicated field; retain provenance fallback; update D-RES-002 evidence | yes |
| `src/auteur/blueprint.py` loaders/serializers | Rely on additive default and existing serialization | yes | low |
| `tests/test_profile_propagation.py` | Update propagation and round-trip expectations | yes | medium |
| D-RES-002 tests | Add legacy/new field and collision cases | yes | low |
| CLI tests | Only if evidence rendering needs assertion changes | conditional | low |
| `ProfileDerivation` model | No shape change; destination strings update | no | low |

Remain untouched: Genre Profile schemas, recommendation/applicability and
acceptance logic, posture policy, `StoryIdentity` schema, CLI exit semantics,
other semantic layers, package version, and release files.

## Delivery sequence

1. Approve this representation and migration policy.
2. Add failing schema, compilation, legacy-loader, D-RES-002, and collision
   tests.
3. Add the additive contract field and write-new compilation behavior.
4. Update D-RES-002 with dedicated-field reads and provenance fallback.
5. Verify round trips, overrides, posture matrix, and public parity.
6. Qualify the new candidate from its exact SHA.

## Risks

- Newly compiled profile Blueprints change serialized shape and field values;
  consumers must distinguish fields explicitly.
- Existing tests asserting profile outcomes in `forbidden_tropes` require
  intentional reinterpretation, not silent compatibility aliases.
- Provenance fallback increases analyzer branching temporarily; keep it
  limited to explicit legacy `ProfileDerivation` entries.
- Ambiguous legacy values cannot be safely migrated without author action.

## Open decisions

1. Whether future profile commitments need per-entry stable outcome IDs rather
   than strings.
2. Whether explicit author editing of the dedicated field needs an author-vs-
   derived marker in a later schema.
3. Whether a future explicit migration command is warranted after observing
   legacy artifact usage.
4. Whether empty additive fields should be omitted in a future serialization
   cleanup; preserve current conventions for now.

## Recommendation

Adopt additive `AuthorAudienceContract.rejected_outcomes: list[str] = []`.
Use read-old/write-new compatibility, never auto-migrate ambiguous legacy
values, and preserve D-RES-002's stable ID with dedicated-field semantics plus
an explicit provenance fallback for old compiled artifacts. Do not dual-write
new profile outcomes indefinitely. This is the smallest durable design that
separates a forbidden narrative mechanism from a rejected story outcome while
preserving author data, provenance, posture severity, and CLI compatibility.
