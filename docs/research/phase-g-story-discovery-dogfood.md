# Phase G Story Discovery mechanical dogfood

## Purpose

This gate closes the thin Phase G product-integration question before any live-provider
semantic-quality claims are attempted.

Phase G asks whether a writer-facing path can carry an author from an unstructured idea to
an intent-aware Story Discovery decision without requiring manual YAML construction or
internal ontology vocabulary, while preserving the Phase F semantic and authority boundaries.

This is a **mechanical integration gate**, not a creative-quality evaluation.

## Evidence boundary

The executable evidence is `tests/test_phase_g_story_discovery_dogfood.py`.

The dogfood runs real product code for:

- guided Story Discovery brief capture;
- optional intent refinement and writer-facing architecture aliases;
- Story Discovery project-state classification;
- Identity-stage workflow routing;
- deterministic Story Discovery review;
- guided composition selection;
- the existing F5 composition engine;
- composition artifact persistence and hierarchy checks;
- writer-facing brief editing and stale-evidence invalidation;
- explicit `story-discovery accept`;
- accepted-Identity advancement to Structure.

Provider-backed semantic outputs are replaced with deterministic controlled responses. This
keeps the gate focused on Phase G integration and leaves live Anthropic/OpenAI behavior to
Phase H.

## Scenario A - successful writer journey

The test begins with an empty project and uses the public writer-facing commands.

```text
fresh project
  -> story-discovery start
  -> minimum adequate brief
  -> story-discovery start --refine
  -> richer optional declared intent
  -> workflow routes to intent-aware discovery
  -> controlled qualified F3/F4 evidence is persisted
  -> workflow routes to read-only review
  -> review explains the recommendation without canonical mutation
  -> story-discovery compose --project .
  -> author confirms the primary and names the mechanism to borrow
  -> unchanged F5 revalidates evidence and creates a candidate-only composition
  -> review reconstructs the composed direction
  -> explicit story-discovery accept
  -> canonical story_identity.yaml appears
  -> workflow advances to Structure
```

The assertions also prove that `story_identity.yaml` does not exist before explicit
acceptance.

The guided input deliberately uses writer-facing aliases such as `science fiction`,
`richly interconnected`, `several interacting causes`, and `one main engine with substantial
supporting layers`; the test verifies their existing canonical mappings rather than creating
new ontology values.

## Scenario B - non-adjudicable alternatives

The second scenario persists a causal result marked `not_adjudicable_near_duplicate` while
also carrying a contradictory historical recommendation ID.

Expected behavior:

```text
non-adjudicable F3 evidence
  -> classifier returns NON_ADJUDICABLE
  -> workflow routes to explanatory read-only review
  -> review says Auteur has no defensible recommendation
  -> no acceptance command is presented
  -> guided composition fails before provider construction
  -> no composed candidate or canonical identity is written
```

This specifically exercises the fail-closed precedence rule: F3 non-adjudicability outranks
a persisted winner field.

## Scenario C - changed author intent

The third scenario starts with a current qualified recommendation and a current composed
candidate, then changes the primary reader experience through the writer-facing `--edit`
flow.

Expected behavior:

```text
current recommendation + composition
  -> writer edits declared intent
  -> old run no longer matches the current brief
  -> classifier returns READY_TO_DISCOVER
  -> old recommendation is not current
  -> old composition is not current
  -> workflow routes back to intent-aware discovery
  -> review refuses to present stale evidence as current
  -> guided composition refuses stale artifacts before provider construction
  -> canonical identity remains absent
```

This proves that current declared author intent outranks historical discovery and composition
artifacts.

## Phase G invariants exercised by the gate

1. Canonical `StoryIdentity` changes only through explicit `story-discovery accept`.
2. The working `DiscoveryBrief` remains non-canonical declared-intent context.
3. Writer-facing aliases map to existing F1/F2 vocabulary rather than creating a parallel ontology.
4. Omitted/changed intent is not silently replaced by defaults.
5. F3 non-adjudicability remains fail-closed.
6. F4 compatibility gates what guided composition can borrow.
7. F5 remains the composition engine and still revalidates evidence before provider use.
8. Composition remains candidate-only until explicit acceptance.
9. Read/review paths do not require provider construction.
10. Accepted Identity still advances to the existing Structure stage.

## Qualification and closure rule

Thin Phase G may be closed only when this dogfood test passes together with the repository's
normal full qualification matrix:

- focused and full pytest coverage;
- Python 3.11, 3.12, and 3.13;
- repository validators/checks;
- Ruff;
- wheel smoke test;
- exact tested PR head;
- no unresolved blocking review feedback.

If that gate is green, the supported Phase G claim is narrow:

> A fresh writer can move from an unstructured premise to an intent-aware Story Discovery
> review and optional bounded composition through a guided, resumable, non-canonical workflow,
> while Phase F recommendation and authority semantics remain intact under controlled evidence.

## Explicit non-claims

This gate does **not** establish:

- live Anthropic/OpenAI creative quality;
- live causal-profile accuracy;
- live comparative-judge quality;
- experienced-writer persuasiveness;
- broad writer usability or preference;
- reliability of unconstrained free-form composition interpretation.

Those questions belong to the separate Phase H live-provider semantic-quality gate.
