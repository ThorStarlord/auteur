# Revision and Staleness Contract

This document defines the minimum freshness behavior guaranteed by Auteur 1.0.
It supplements the authority rules in
[the Architecture Constitution](architecture-constitution.md).

## Vocabulary

- **Fresh**: every recorded source dependency still matches the revision and
  content hash captured when the derived artifact was created.
- **Stale**: at least one recorded source dependency has changed, disappeared,
  or cannot be verified.
- **Unknown**: the artifact does not contain enough dependency evidence to
  determine freshness. Unknown is not treated as fresh for promotion.

## Required behavior

| Upstream change | Directly affected outputs | Required behavior |
|---|---|---|
| Story Identity | Blueprint, Structure, downstream plans, diagnostics | Mark dependent outputs stale or require regeneration; never substitute silently |
| Blueprint identity/structure fields | Structure reports, proposals, Cartographer plans | Reject stale promotion and regenerate reports/plans |
| Structure | Chapter Structure, Realization plans, impact reports | Preserve unaffected artifacts only when their explicit dependencies remain fresh |
| Chapter/Scene Realization | Scene/Chapter Expression, Book composition | Mark dependent expression or composition stale; retain prior accepted revision |
| Expression candidate/publication | Reasoning and reconciliation reports | Reports referencing the old candidate remain historical; do not reinterpret them |
| Genre Pack or contract version | Recommendations, diagnostics, tutor cards | Require a new evaluation with the new pack/contract hash |
| Universe/Series constraint | Dependent Series/Book projections | Emit deterministic blocking diagnostics for violated structured constraints |

## Promotion gate

An operation that changes authority must verify all declared dependencies before
writing the new accepted pointer. If any dependency is stale or unknown:

1. no canonical file is changed;
2. no accepted pointer is moved;
3. a structured stale diagnostic identifies the dependency and captured source;
4. the caller may regenerate or explicitly start a new proposal from current
   sources.

Publication of a candidate is allowed when its publication contract permits it,
but publication never makes the candidate canonical.

## Preservation rule

An unaffected artifact may be reused only when its dependency set is explicit
and every dependency is fresh. Absence of an observed dependency does not prove
independence. Free-form semantic inference is advisory and cannot authorize
reuse or acceptance.

## Scope limits for 1.0

The first release guarantees freshness for explicit artifact references,
revision identifiers, content hashes, and existing proposal/acceptance
manifests. It does not claim complete semantic inference from prose, automatic
causal extraction, or safe markerless external-edit mapping.

