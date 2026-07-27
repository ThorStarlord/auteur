# Verification Report: Genre Profile Resolution-Contract Propagation

Date: 2026-07-27
Branch: `feat/genre-profile-resolution-propagation`
Base: `9044b45` (main)
Spec: `docs/superpowers/specs/2026-07-27-genre-profile-blueprint-propagation.md`

## Summary

Implements the first approved vertical slice of Genre Profile-to-Blueprint
propagation: `accepted_resolution_contract` → `expected_elements` /
`forbidden_tropes` → `ProfileDerivation` provenance → deterministic structural
diagnostics (D-RES-001, D-RES-002, D-RES-003). Includes override propagation.

## Files Changed

| File | Change | Lines |
|---|---|---|
| `src/auteur/blueprint.py` | Added `ProfileDerivation` model + `StoryBlueprint.profile_derivation` field | +33 |
| `src/auteur/identity.py` | Resolution-contract + override compilation in `compile_to_blueprint()` | +43 |
| `src/auteur/structure/analyzer.py` | Profile diagnostics D-RES-001/002/003 | +116 |
| `tests/test_profile_propagation.py` | 27 counterfactual + unit + regression tests | new file |

## What Was Verified

### Propagation Contract (identity → blueprint)

| Source | Target | Status |
|---|---|---|
| `genre_profile.accepted_resolution_contract.required_outcomes` | `contract.expected_elements` | ✅ |
| `genre_profile.accepted_resolution_contract.rejected_outcomes` | `contract.forbidden_tropes` | ✅ |
| `genre_profile.accepted_resolution_contract.pattern` | `profile_derivation.obligations_applied` | ✅ |
| `genre_profile.source_recommendation_id` | `profile_derivation.recommendation_id` | ✅ |
| `genre_profile.author_overrides[].replacement_value` | `contract.expected_elements` (replaces) | ✅ |

### Diagnostics

| Rule | Check | Status |
|---|---|---|
| D-RES-001 | Required outcome missing from expected_elements | ✅ |
| D-RES-002 | Rejected outcome found in expected_elements | ✅ |
| D-RES-003 | Resolution pattern implies tone conflicting with mandatory_ending_tone | ✅ |

### Non-Regression

- Without genre_profile → `profile_derivation` is None, all contract fields
  are default-empty, no profile diagnostics fire.
- Semantic equivalence with v0.37.1: same contract fields, same structure,
  same behavior. Serialized output differs only by additive
  `profile_derivation: null` key. Use `exclude_none=True` for byte-identity.
- No identity mutation during compilation.
- Round-trip through YAML serialization preserves ProfileDerivation.
- 9 broader test suites all pass.

## Repository Qualification

### Test Inventory

| Metric | Baseline (v0.37.1) | Candidate | Delta |
|---|---|---|---|
| Collected | 3729 | 3756 | +27 |
| Added test nodes | — | `test_profile_propagation.py: 27` | +27 |
| Removed test nodes | — | none | 0 |
| Marker changes | — | none | 0 |

### Focused Qualification

Profile propagation + directly affected suites:

| Category | Count |
|---|---|
| Collected | 48 |
| Passed | 48 |
| Skipped | 0 |
| Xfailed | 0 |
| Xpassed | 0 |
| Failed | 0 |
| Errors | 0 |

### Serial Qualification

```
python -m pytest tests -n 0 --tb=short -q
```

| Category | Count |
|---|---|
| Collected | 3756 |
| Passed | 3728 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 1 |
| Xfailed | 27 |
| Xpassed | 0 |
| Duration | 799.1s |

### Parallel Qualification

```
python -m pytest tests -n auto --tb=short -q
```

| Category | Count |
|---|---|
| Collected | 3756 |
| Passed | 3728 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 1 |
| Xfailed | 27 |
| Xpassed | 0 |
| Duration | 300.7s |

Serial and parallel counts reconcile exactly. The 27 xfailed tests are
pre-existing baseline markers, unrelated to this change.

## Behavior Verification

| Scenario | Status |
|---|---|
| No profile ⇒ no derivation, no diagnostics | ✅ |
| Required outcomes ⇒ expected_elements | ✅ |
| Rejected outcomes ⇒ forbidden_tropes | ✅ |
| Provenance identifies accepted commitment | ✅ |
| Identity unchanged after compilation | ✅ |
| Mode wins over profile pattern (no silent overwrite) | ✅ |
| Conflict visible through D-RES-003 | ✅ |
| Override replaces downstream obligation | ✅ |
| Override suppresses diagnostic for overridden outcome | ✅ |
| Override provenance tracked in obligations_applied | ✅ |
| Original recommendation value remains inspectable | ✅ |
| No duplicate obligations on repeated compile | ✅ |
| Stable ordering on repeated compile | ✅ |
| Semantically stable output (modulo timestamp) | ✅ |
| Three diagnostics reachable through analyze_structure() | ✅ |
| Diagnostic evidence includes provenance paths | ✅ |

## Known Gaps (Follow-up Slices)

1. **Adherence posture** — Diagnostic severity is always WARNING regardless
   of `adherence_posture`. Severity modulation is deferred.
2. **Emotional-target propagation** — `accepted_target_emotions` not
   propagated to `EmotionalBlueprint`. Separate slice.
3. **Narrative engine propagation** — `accepted_narrative_engine` not
   propagated. Separate slice.
4. **Framing propagation** — `accepted_framing` not propagated. Separate
   slice.

## Compatibility Claims

| Claim | Verdict |
|---|---|
| Byte-identical with v0.37.1 | **False** — new `profile_derivation: null` key in serialized output |
| Semantically identical | **True** — same structure, contract fields, behavior |
| Generated metadata differences | `profile_derivation: null` when no profile; ISO timestamp when profile present |

## Verdict

| Criterion | Status |
|---|---|
| Implementation matches approved slice | ✅ PASS |
| Resolution obligations propagate | ✅ PASS |
| Author authority preserved | ✅ PASS |
| Conflicts remain visible | ✅ PASS |
| Provenance sufficient | ✅ PASS |
| Diagnostics publicly reachable | ✅ PASS |
| Override criterion resolved | ✅ PASS (implemented) |
| Focused suite reconciled | ✅ PASS (48/48) |
| Serial suite reconciled | ✅ PASS (3756/3756) |
| Parallel suite reconciled | ✅ PASS (3756/3756) |
| Ready for review commit | ✅ YES |
| Ready for merge | ✅ YES |

## Candidate SHA

`9044b45` (base). Source changes are uncommitted in the working tree
of `feat/genre-profile-resolution-propagation`.
