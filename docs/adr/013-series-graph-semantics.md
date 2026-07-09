# ADR 013: Series Dependency Graph Semantics

## Status

Accepted

## Context

Series Engine V1 introduced `dependency_graph.yaml` as a deterministic artifact
for reasoning about cross-book dependencies. The first graph shape contained
useful nodes and edges, but the meaning of edge direction needed to be explicit
before future impact analysis can rely on it.

## Decision

Series dependency graph edges use this rule:

```text
source --type--> target means source affects target
```

The graph's derived impact metadata follows from that rule:

- `dependents` are nodes affected by this node.
- `dependencies` are nodes this node relies on or is affected by.

For example, if Book 1 sets up a mystery:

```text
book_1 --sets_up--> emperor_identity
```

Then `emperor_identity` lists `book_1` as a dependency, and `book_1` lists
`emperor_identity` as a dependent.

Generated impact metadata remains artifact-only. It must not be written back
into `series_identity.yaml`.

## Consequences

- Future impact analysis can ask what a moved reveal/payoff affects without
  guessing edge direction.
- Declared edges and automatically derived setup/payoff edges use the same
  semantics.
- The graph remains deterministic and report-oriented.
