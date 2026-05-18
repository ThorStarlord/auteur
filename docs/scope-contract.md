# Scope Contract

Auteur treats length as capacity, not quality. A short story can be artistically
rich, and a long novel can be shallow, but each container has a limited ability
to carry narrative machinery.

The Scope Contract is the Layer 3 execution budget for that machinery. It sits
after genre identification and before detailed story-engine expansion.

```text
raw idea
  -> genre contract
  -> scope contract
  -> recommended story engine
  -> blueprint seed
  -> structure diagnostics
```

## Scope Profile vs Scope Contract

`GenreContract.scope_profile` stores genre-level affordances: natural lengths,
minimum viable length, default length, narrative runway, mechanical load,
worldbuilding load, cast load, compression strategies, expansion strategies, and
common scope failure modes.

`StructuralConstants.scope_contract` stores the accepted project-level execution
budget. It can differ from the genre default because the user's premise may be
larger or smaller than the genre's usual shape.

## Mechanical Load

Use mechanical load instead of "simple genre." Mechanical load describes how
many moving parts the story must operate: clue chains, suspects, factions,
relationship beats, world rules, multiple POVs, political arenas, or escalation
cycles.

This keeps the distinction clear: a genre can have lower default mechanical load
while still being emotionally, formally, or artistically demanding.

## Scope Fit Recommendations

Future recommendation behavior should be bidirectional:

- Fit the premise to the selected container by reducing machinery.
- Fit the full premise by expanding length, scale, or series shape.
- Offer a middle path only when it is concrete enough to build.

Auteur should not tell the user they cannot write the story they want. It should
make the execution tradeoff explicit: this container needs a narrower build, or
this premise needs a larger container.

Auteur does not model writer skill level for this decision. Scope evaluation is
about the story plan, genre machinery, and selected container.
