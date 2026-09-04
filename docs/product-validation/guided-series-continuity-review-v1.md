# Guided Series Continuity Review V1

Status: implementation candidate; owner review required.

## Mission

Compose existing Series history, current state, commitments, open question,
revision impact, and supporting evidence into one read-only author-facing review
for a later-Book planning intent.

## Baseline

The implementation is based on
`de250363d949bd23eb35f49476641c1f36814a45`.

## Product surface

```text
auteur series review PROJECT --book N [--detail]
```

The command requires an explicit existing `BookPlanningIntent`. It does not
infer a creative question or create a new decision object.

## Existing capability composition

- `SeriesDirection.promise`, `pressure`, and `open_question` are displayed
  directly from the accepted Series Direction.
- `DirectionCommitment` is split into active and explicitly resolved lists
  using existing `resolved_commitment_ids` evidence.
- Current context, relevant history, current-state evidence, causal support,
  Focus inputs, provenance, and freshness are derived from existing Series
  services.
- Revision impact reuses the existing impact report and preserves its
  distinction between affected artifacts and rewrite instructions.

## Authority and boundaries

The review is derived and read-only. It does not accept or revise canon,
resolve a Series open question, record review dispositions, change Focus or
pressure semantics, or integrate `AuthorDecision.UnresolvedChoice`.

No new canonical state, lifecycle, ontology, extraction path, or scale claim
is introduced.

## Required scenarios

Focused tests cover normal later-Book planning, active/resolved commitments,
explicit planning-intent failure, progressive provenance disclosure, rebuild
equivalence, and preservation of accepted artifacts.

## Claim ceiling

Mechanical composition and authority preservation may be qualified. No broad
independent long-horizon product-value claim is made. Owner review must assess
clarity, burden, provenance trust, and whether the composition reduces manual
reconstruction.

## Stopping rule

Stop and reopen the owner boundary if implementation requires a new canonical
concept, a new persisted review lifecycle, generic decision-workspace
integration, new pressure semantics, extraction, or scale work.
