# Adherence-Posture Diagnostic Severity Specification

## Status

Proposed / awaiting approval. This document is intentionally uncommitted.

## Problem

An accepted `GenreProfileCommitment` persists an `adherence_posture`, but the
profile resolution diagnostics currently emit fixed `WARNING` severity.
Posture therefore has no runtime effect even though the propagation
specification defines it as a diagnostic expectation.

The first implementation slice should define severity semantics without
changing compilation, schemas, CLI exit codes, or author authority.

## Proven evidence

- `AdherencePosture` is defined in `src/auteur/genre_packs/models.py`.
- Actual values are `conventional`, `flexible`, `revisionist`, `subversive`,
  and `deconstructive`.
- `GenreProfileCommitment.adherence_posture` defaults to
  `AdherencePosture.CONVENTIONAL`.
- Pydantic validates enum values and round-trips the string enum value.
- `identity.py` accepts and persists the commitment; compilation copies
  resolution obligations into the Blueprint but does not copy posture.
- `analyze_structure()` emits D-RES-001/002/003 with fixed `WARNING` severity.
- The public `genre diagnose` command renders analyzer results and does not
  decide severity.
- Existing tests construct and serialize posture values, but do not assert
  posture-dependent severity.
- The propagation specification says posture affects diagnostic severity and
  explanation language, never compiled structure; it defines conventional as
  `ERROR`, flexible/revisionist/subversive as `WARNING`, and deconstructive as
  `INFO`.
- The product review identifies the missing posture read as a deferred
  contract gap.

## Non-goals

This proposal does not add posture values, schema fields, acknowledgment
workflow, compilation blocking, profile editing UX, exit-code changes,
`rejected_outcomes` redesign, emotional-target propagation, narrative-engine
propagation, framing propagation, or another Genre Pack.

## Existing posture model

| Value | Schema location | Default | Current effect |
|---|---|---|---|
| `conventional` | `GenreProfileCommitment.adherence_posture` | yes | metadata only |
| `flexible` | same | no | metadata only |
| `revisionist` | same | no | metadata only |
| `subversive` | same | no | metadata only |
| `deconstructive` | same | no | metadata only |

All five values are validated by Pydantic, serialized as their lowercase
strings, preserved through identity serialization, and currently unused by
runtime consumers. A missing field deserializes to the conventional default.
Legacy Blueprints without `ProfileDerivation` have no profile diagnostics.

## Posture semantics

Posture describes the author's intended relationship to accepted profile
commitments, not the story's emotional tone:

- **CONVENTIONAL**: the author intends to satisfy the accepted commitments;
  deterministic violations are errors.
- **FLEXIBLE**: the commitments guide the work but may be departed from;
  violations remain visible warnings.
- **REVISIONIST**: the author intends to revise conventions while retaining
  the profile as a reference; violations remain visible warnings and should
  explain that revision is intentional.
- **SUBVERSIVE**: the author intends deliberate contradiction of conventions;
  violations remain visible warnings and should explain the subversive intent.
- **DECONSTRUCTIVE**: the author intends to expose or dismantle the
  convention; violations are informational observations.

These meanings are policy explanations, not unrestricted literary judgments.

## Severity matrix

| Posture | D-RES-001 | D-RES-002 | D-RES-003 | Compilation | CLI exit |
|---|---|---|---|---|---|
| conventional | ERROR | ERROR | WARNING | proceeds | unchanged |
| flexible | WARNING | WARNING | WARNING | proceeds | unchanged |
| revisionist | WARNING | WARNING | WARNING | proceeds | unchanged |
| subversive | WARNING | WARNING | WARNING | proceeds | unchanged |
| deconstructive | INFO | INFO | INFO | proceeds | unchanged |

D-RES-001 and D-RES-002 are deterministic contract violations, so a
conventional posture treats them as errors. D-RES-003 remains a warning even
for conventional posture because pattern/tone compatibility is a bounded
diagnostic policy and may represent intentional authorial divergence. All
three remain visible under every posture; no posture suppresses a finding.

## Selected policy

Select **Policy A — severity-only modulation**. It is the smallest policy
that makes posture operational while preserving compilation, artifact
generation, CLI exit compatibility, and author control. Policy B would make
existing scripts fail on a severity change. Policy C introduces a new
acknowledgment state and authority workflow. Policy D hides evidence and
would make intentional divergence harder to inspect.

The first slice should apply the matrix to D-RES-001/002/003 only. It should
retain the current diagnostic IDs, evidence, repair options, and ordering.

## Precedence and override rules

1. Explicit author-authored Blueprint values remain authoritative and are not
   silently replaced.
2. Accepted profile commitments provide defaults and diagnostic expectations.
3. A `GenreAuthorOverride` is explicit author action and suppresses the
   corresponding overridden obligation's diagnostic, as today; posture does
   not re-enable it or downgrade unrelated findings.
4. Posture changes only effective severity and explanation metadata. It does
   not alter derived obligations, provenance, StoryIdentity, or Blueprint
   content.
5. No acknowledgment or waiver concept currently exists. Do not invent one in
   this slice.
6. Posture is read from the accepted `StoryIdentity.genre_profile` while
   analyzing the corresponding Blueprint. It need not be copied into
   `ProfileDerivation` for the first slice; diagnostics should expose the
   effective posture as derived metadata.
7. A contradictory posture and override are resolved by the explicit override
   for that target, while conflicts outside the target remain visible under
   the posture matrix.

## Architecture ownership

Use a small central policy function in the diagnostic layer, for example a
mapping from `(diagnostic_kind, posture)` to `DiagnosticSeverity`. The
analyzer remains the owner of D-RES-001/002/003 detection and supplies the
diagnostic kind. The CLI only renders the result.

This is preferable to CLI-owned logic because it keeps human and JSON output
identical, and preferable to profile-schema policy because all five postures
have shared semantics and the first slice does not need per-pack variation.
The function should be deterministic, exhaustive for the enum, and have an
explicit conventional fallback for legacy data.

## Diagnostic metadata

Each profile diagnostic should retain its current stable ID, evidence,
originating commitment path, affected Blueprint path, recommendation ID, and
repair options. Additive metadata should expose:

- `adherence_posture`: the lowercase enum value or a human-readable label;
- `base_severity`: the diagnostic's posture-independent baseline, if needed;
- `effective_severity`: the emitted severity.

If the existing diagnostic model cannot add metadata without a schema change,
include posture and effective-severity explanation in the message/evidence
only after confirming the model boundary. Do not change unrelated diagnostic
serialization.

## Human and JSON behavior

Human output should state the stable ID, effective severity, source
commitment, affected field, and a short posture explanation, for example:

> This profile was accepted with a CONVENTIONAL adherence posture, so the
> missing required resolution outcome is treated as an error rather than a
> warning.

JSON must expose the same diagnostic IDs and effective severities as human
output, plus the source and posture metadata. Human formatting must not make
independent severity decisions.

## CLI exit-code behavior

Keep the existing `genre diagnose` exit behavior unchanged in the first
slice. Severity changes are informative and compilation remains permissive;
changing exit codes would be a breaking workflow change without an approved
acknowledgment contract.

## Backward compatibility

- No `genre_profile`: no profile diagnostics and no posture effect.
- Missing posture: Pydantic default is conventional; legacy accepted profile
  data therefore receives deterministic conventional semantics.
- Unknown posture: reject at schema validation rather than silently guessing.
- Legacy Blueprint without `ProfileDerivation`: unchanged, no profile checks.
- Existing accepted profile: analysis uses its persisted posture; compilation
  is unchanged.
- Explicit override: existing suppression and provenance remain intact.
- JSON consumers: diagnostic IDs remain stable; effective severity may change
  for profiles with conventional/deconstructive posture, so this is an
  intentional additive semantic change and must be documented.
- CLI scripts: exit codes remain unchanged.

## Counterfactual acceptance tests

1. Same conflict with each posture: same ID/evidence, matrix-derived severity,
   no structural mutation.
2. No profile: no profile diagnostics.
3. Missing posture: conventional default and deterministic severity.
4. Author override: overridden D-RES-001/002 remains suppressed; provenance
   remains inspectable; unrelated diagnostics retain posture severity.
5. Human/JSON parity: same IDs, effective severities, posture metadata.
6. CLI exit compatibility: same return code before and after severity policy.
7. Identity and Blueprint round trips preserve posture/provenance semantics.
8. Repeated analysis is byte-for-byte stable in IDs, ordering, and severity.
9. D-RES-003 remains posture-independent for the proven compatible and
   contradiction cases unless the approved matrix is later revised.
10. All five actual posture values are covered for D-RES-001 and one
    representative test covers each D-RES-002/003 category.

## Implementation surface

| File | Expected change | Required first slice | Risk |
|---|---|---:|---|
| `src/auteur/structure/analyzer.py` | Call posture policy for three profile diagnostics; add posture metadata | yes | medium |
| `src/auteur/structure/diagnostics.py` | Only if additive metadata requires model support | conditional | medium |
| `src/auteur/genre_packs/models.py` | No change; enum/default already sufficient | no | none |
| `src/auteur/genre_packs/cli.py` | No severity logic; only adjust rendering if metadata requires it | conditional | low |
| `tests/test_profile_propagation.py` | Unit counterfactual severity tests | yes | low |
| `tests/test_profile_diagnostic_visibility.py` | Public human/JSON and exit compatibility tests | yes | low |

Remain untouched: StoryBlueprint schema, ProfileDerivation schema,
recommendation/applicability/acceptance logic, interactive pipeline code,
version metadata, release files, and all unrelated semantic layers.

## Delivery sequence

1. Approve this specification and the severity matrix.
2. Add policy-focused failing tests without changing schemas.
3. Implement the central deterministic policy and analyzer integration.
4. Verify focused tests, public CLI parity, and no structural mutation.
5. Run the full qualification process from the new candidate SHA.

## Risks

- Conventional/deconstructive severity changes may affect JSON consumers that
  treat `WARNING` as stable; IDs and exit codes remain compatible.
- Adding diagnostic metadata may require a model change; keep it additive and
  narrowly scoped.
- If D-RES-003 is made posture-dependent later, it must retain its separate
  compatibility policy rather than inheriting contract-violation semantics.

## Open decisions

1. Whether `DiagnosticSeverity` metadata can be extended additively or should
   use existing evidence fields.
2. Whether the human-facing label should be the raw enum or a short display
   label; raw enum remains required in JSON.
3. Whether D-RES-003 should remain posture-independent permanently or receive
   a separately approved advisory matrix after usage evidence.

## Recommendation

Approve Policy A: severity-only modulation, with D-RES-001/002 mapped by the
posture matrix and D-RES-003 remaining a warning-level conflict advisory.
Compilation must never be blocked by posture in this slice, CLI exit codes
must remain unchanged, and explicit overrides must continue to suppress only
the obligations they target. This is ready for implementation only after the
matrix and metadata approach are approved.
