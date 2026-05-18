# ADR 007: Medium Contract As Layer 2 Delivery Grammar

## Status

Accepted

## Context

Auteur already treats genre, mode, medium, audience, and boundaries as Layer 2
constraints. That was too coarse for delivery forms: a novel, webnovel, visual
novel, and action game can share a genre while using different machinery to
deliver the promise.

Genre answers what promise is being made. Medium answers how the promise can be
delivered. Scope answers how much execution budget the story has.

## Decision

Add `MediumContract` under `ProjectIdentity` as `identity.medium_contract`.
Keep `identity.medium` as a backward-compatible shortcut for existing
blueprints.

The contract records:

- medium
- format
- release model
- interaction model
- unit of delivery
- representation units
- modulation biases
- medium failure modes

Add a medium registry parallel to the genre registry. During blueprint
validation, if `identity.medium_contract` is absent and `identity.medium` is
present, Auteur fills a default medium contract from the registry.

V1 diagnostics stay narrow:

- warn when no usable medium contract or shortcut exists
- error when `identity.medium` conflicts with `identity.medium_contract.medium`

## Consequences

Layer 2 is now best described conceptually as **Promise / Form Contract** while
existing diagnostic layer keys can continue to use `constraints`.

The schema remains backward compatible for existing blueprints. New blueprints
can be more explicit without requiring a migration.

The first analyzer rules validate contract presence and internal consistency.
They do not judge whether the story is good for the medium or infer medium
quality from narrative content.
