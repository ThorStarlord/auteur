# ADR 012: Series Engine V1

## Status

Accepted

## Context

Auteur now has a Story Discovery and Story Identity layer for deciding what a
single story is before compiling it into a blueprint. Series work introduces a
higher-order problem: multiple independently compilable books must also form one
larger narrative system.

## Decision

Series Engine V1 adds `SeriesIdentity` as a canonical Narrative Engine artifact
above `StoryIdentity`.

`series_identity.yaml` stores author-declared whole-series intent only:

- title
- series type and book count rules
- core question and global arc
- book plans
- cross-book character, relationship, faction, and mystery arcs
- declared dependency edges

Generated analysis artifacts do not get written back into `series_identity.yaml`.
Compiled book identities, diagnostics, dependency graphs, and bibles are
derivative report artifacts.

The V1 compiler maps each `BookPlan` into a normal `StoryIdentity`. Existing
identity validation and blueprint compilation remain the downstream path.
Series Engine does not generate outlines, drafts, or prose.

Cross-book diagnostics, graph generation, and bible compilation are
deterministic. LLM-based series discovery is deferred until the deterministic
spine is stable.

## Consequences

- Auteur gains a layer above `StoryIdentity` without replacing the existing
  single-book pipeline.
- Book-level identity files remain independently valid and compilable.
- Series diagnostics can reason about escalation, payoff timing, character
  runway, and dependency effects across books.
- Future `series discover` can reuse the proposal-comparison-promotion pattern
  established by Story Discovery.
