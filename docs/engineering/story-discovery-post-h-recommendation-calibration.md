# Story Discovery post-H recommendation calibration

## Scope

This qualification record closes the implementation boundary tracked by #125 after Phase H.

Baseline under qualification: `fd62d29dfa4424ce4aaa66c6093dd3dd8008e802` plus this record.

The production contract now distinguishes:

- `explicit_intent_fit`: a declared author preference or hard constraint actually distinguishes the selected direction;
- `advisory_artistic_preference`: several directions remain compatible with declared intent and Auteur states its own bounded craft preference honestly;
- `not_adjudicable`: the directions are causally distinct but even a bounded advisory preference would require inventing an unsupported deciding criterion.

No numeric creative score is introduced. Recommendation remains advisory and canonical StoryIdentity still changes only through explicit `story-discovery accept`.

## Persistence and compatibility

New recommendation artifacts record `recommendation_status`, `recommendation_basis`, `candidate_tradeoffs`, `recommendation_rationale`, and a winner only when one exists. `rejected_candidate_reasons` remains as a compatibility field for recommended outcomes.

Legacy recommendation artifacts with a valid winner remain readable without retroactively assigning a new evidence basis. A qualified legacy artifact with no winner and no explicit `not_adjudicable` judgment remains invalid rather than being guessed into the new state.

## Derived state and review

A qualified causal set with a comparative `not_adjudicable` result is a valid `NON_ADJUDICABLE` project state rather than corrupt evidence. Its deterministic review can show the viable alternatives and explicit author acceptance commands without selecting a hidden primary or enabling primary-relative composition.

Intent-fit recommendations, advisory preferences, and legacy recommendations render with different epistemic language. Raw-premise exploratory comparison cannot claim `explicit_intent_fit`.

## Qualification controls

The repository test suite includes focused controls for:

- explicit-intent recommendation basis;
- advisory close calls;
- comparative non-adjudicability;
- exploratory rejection of false intent-fit claims;
- malformed basis/winner combinations;
- legacy judge compatibility;
- derived project state and writer-facing review;
- explicit non-canonical authority.

Full repository CI on the exact PR head is the release gate for this record.

## Publication anomaly

During construction, the production/test changes reached `main` before the intended PR qualification boundary. History is not rewritten. This follow-up PR qualifies the exact resulting repository state plus this record; any CI failure must be repaired on this branch before #125 is closed.
