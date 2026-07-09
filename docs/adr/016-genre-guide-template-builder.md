# ADR 016: Genre Guide / Template Builder V1

## Status

Accepted.

## Context

Auteur's genre pipeline is contract-driven. A guide builder should not create
prompt templates that only influence generation text; it should create
machine-readable `GenreContract` artifacts that validation and diagnostics can
use.

## Decision

V1 adds a deterministic CLI builder for project-local custom genre contracts.
The builder compiles structured markdown briefs into custom contract YAML,
validates contract usability, explains the contract as a human-readable guide,
and installs valid contracts under `genres/custom/` inside a project.

The package-level built-in genre data remains unchanged. V1 does not migrate
core genre enum fields or use LLM calls.

## Consequences

Generated guides are derived from contracts. Installed custom contracts are
project-local overlays and do not mutate `src/auteur/genres/data/`. Future work
can wire project-local custom contracts into broader identity and blueprint
flows after the contract artifact is stable.
