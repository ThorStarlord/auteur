# Bounded Episode 1 Direction — Implemented Capability

Status: implemented bounded packages for issue #218. The normative
definition is the ratified Bounded Episode 1 Direction Capability Contract
(`feature/series-episode-one-direction@aa3aaf9`,
`docs/acceptance/series-episode-one-direction-capability-contract-v1.md`).
This note states what is implemented and what is excluded; it is not itself
a claim that the capability is qualified, released, or shipped.

## Capability

For a Series that the author has explicitly declared episodic, Auteur lets
the author propose a local Direction for Episode 1 that builds on the
accepted Series Direction and references the Series commitments the author
selects, explicitly accept it so that it becomes authoritative, and inspect
it distinctly from the Series Direction. Proposal is non-authoritative;
explicit acceptance is the only authority transition.

## Workflow (author-facing)

```text
declare the Series episodic
  -> propose an Episode 1 Direction
  -> explicitly accept the Episode 1 Direction
  -> inspect
```

There is no separate author-facing "begin Episode 1 planning" step.

## Authority (in order)

```text
accepted Series Direction        -> pre-existing Series-scope authority (unchanged)
accepted episodic entry-form     -> Series identity decision: this Series is episodic
accepted Episode 1 Direction     -> Episode-1 entry-unit Direction authority
```

Each accepted artifact is created only by explicit author action, persisted
atomically with rollback, carries provenance with a stable identity and a UTC
timestamp, and leaves prior state unchanged on failure. The accepted Series
Direction is never altered, re-versioned, or re-accepted by this capability.
Book and Episode entry work are mutually exclusive by active check.

## Placement

Episode 1 is a Series-scope, Identity-layer entry-unit Direction artifact for
explicitly episodic Series. It is not a sixth canonical scope; the five-scope,
five-layer model is unchanged. No generalized Episode scope, no Book/Episode
unification, and no Episode-to-Chapter nesting.

## Excluded

No Episode beyond Episode 1; no Episode realization, canonical-state
progression, outcomes, or next-episode planning; no generalized entry-unit or
Direction abstraction; no Direction inheritance or revision propagation; no
universal dependency inference; no generalized Author Decision system; no
changes to legacy full-Series or StoryBible workflows; no browser, TUI, or
editor surface; no change to `SeriesDirection` or the legacy Series type model
that would alter an existing accepted artifact hash; no entry-form conversion.

## Evidence boundary

Implementation and qualification status are tracked separately from this
definition. Human validation is still required for whether the four-step
workflow reads as the smallest coherent unit, whether the entry-form lock
timing matches author practice, whether the inspection view makes the
Series/Episode distinction obvious, and whether duplicate-reference rejection
matches author expectations.
