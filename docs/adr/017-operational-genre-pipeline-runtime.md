# ADR 017: Operational Genre Pipeline Runtime

## Status

Accepted.

## Context

Auteur has three interactive genre pipelines, but their command, session, server,
browser, and identity paths are coupled to the netorare implementation. The
built-in `GenrePipelineSpec` registry describes genre variation without governing
runtime execution, and browser sessions can therefore bypass the registered
template and validator.

## Decision

`auteur.genre_pipeline` is the sole production runtime for built-in interactive
genre authoring. The runtime resolves a built-in pipeline specification, stores
non-canonical session state under `.auteur/genre_sessions/`, normalizes template
data for one browser protocol, and writes canonical `story_identity.yaml` only
after author completion and deterministic identity validation.

The registry is a closed catalog of built-in pipelines, not a third-party plugin
system. Legacy `netorare/session.json` state is detected and reported but is not
silently migrated or promoted.

## Alternatives Considered

- Retrofitting the three existing command classes would preserve their duplicate
  orchestration and keep netorare names in the shared runtime.
- Separate servers and compilers per genre would isolate behavior but multiply
  infrastructure and make cross-genre fixes inconsistent.
- External plugin discovery is deferred until the built-in runtime contract has
  proven stable.

## Consequences

Genre variation is supplied through one operational specification while session,
server, browser, and compilation behavior remain shared. Existing public genre
commands become thin adapters. Session paths change, and completed or legacy
sessions require explicit author cleanup rather than automatic migration.
