# Phase D — Story Discovery Synthetic Confidence Findings

## Status

**QUALIFIED, pending final-tree requalification.**

Phase D exercised controlled synthetic provider outputs through Auteur's real Story Discovery mechanics. Production Story Discovery code was not changed.

## Qualification evidence

Initial qualified head: `c573afbac410922238b687e3dc0ce6f6edf4a076`.

GitHub Actions Validation #237 (run `32175714995`) completed successfully across:

- wheel smoke;
- Python 3.11 full pytest + verification stack;
- Python 3.12 full pytest + verification stack;
- Python 3.13 full pytest + verification stack.

The verification stack kept repository validators, vendored-contract checks, and Ruff green.

This findings file changes the PR tree, so the resulting head must pass CI again before merge.

## Benchmark result

The deterministic harness passed all 12 naturalistic cases through the real Story Discovery path:

- 3 underdetermined premises;
- 3 constraint-heavy premises;
- 3 strong genre-promise premises;
- 3 author-boundary premises.

The suite also passed controls for:

- self-advocacy/provenance evidence isolation;
- candidate-order permutation;
- candidate-ID remapping;
- contract-fit non-dominance;
- exact-duplicate rejection;
- semantic-near-duplicate boundary honesty;
- explicit author-constraint visibility;
- malformed comparative judgment failing closed;
- recommendation without canonical promotion.

Inherited Phase A/B controls for one-survivor and zero-survivor honesty remained green in the full suite.

## Authority result

Recommendation remained advisory. No recommendation run created canonical `story_identity.yaml`; explicit author acceptance remains the authority boundary.

## Known limitation

Exact normalized central-engine force duplicates are rejected. Semantic near-duplicates that are not exact matches are not deterministically rejected. Phase D confirms this boundary; it does not claim semantic similarity detection is solved.

## Method lesson

An early fixture used an imagined story-mode value (`dramatic`). Real `StoryIdentity` parsing exposed that invalid assumption, and the fixture was corrected before qualification. This is why the gate keeps real schema and validation in the loop rather than simulating final artifacts directly.

## Supported claim

Subject to final-tree CI, Phase D supports this bounded conclusion:

> Story Discovery passed systematic synthetic product stress testing across naturalistic, adversarial, mutation, permutation, and authority-boundary scenarios under controlled provider outputs.

## Not established

Phase D does not establish live-provider generation quality, live-model winner quality, real-writer preference, real-world recommendation acceptance, or population-level artistic quality.

## Decision

No deterministic failure currently justifies a production Story Discovery semantic change. If final-tree CI stays green, merge this research gate and treat live-provider/founder dogfood as a separate later confidence layer.
