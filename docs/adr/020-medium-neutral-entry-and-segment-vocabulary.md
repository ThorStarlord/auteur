# ADR 020: Medium-neutral Entry and Segment Vocabulary

Status: **Accepted**

## Context

Auteur's canonical scope vocabulary historically uses `Universe -> Series -> Book -> Chapter -> Scene`, while the product already supports media and delivery units such as novels, short stories, film, television, visual novels, games, books, episodes, missions, levels, scene nodes, and choice nodes.

Treating Episode as a new sixth canonical scope would couple semantic scope to one medium. Treating an Episode Direction as Series scope obscures the entry-level boundary. PR #167 explored the latter as a bounded vertical slice but was closed without merge and is not current-main authority.

## Decision

Adopt a medium-neutral semantic vocabulary:

`Universe -> Series/Collection -> Entry -> Segment -> Scene`

where:

- **Entry** is one independently addressable work/installment inside a collection or series. Presentation aliases include Book, Episode, Film, Story, Route, and Mission.
- **Segment** is a major structural subdivision of an Entry. Presentation aliases include Chapter, Act, Sequence, Section, and (where the medium warrants it) Mission.

This ADR defines semantic vocabulary and compatibility mappings. It does **not** mass-migrate existing persisted Book/Chapter paths, Series models, provenance records, or CLI contracts.

## Compatibility rule

Existing `Book` and `Chapter` runtime/serialized meanings remain valid and authoritative. New code may use Entry/Segment at generic boundaries while adapters expose Book/Chapter as medium-specific aliases.

No existing artifact is rewritten merely because this ADR exists.

## Consequences

1. Episode support should prefer an Entry abstraction rather than a sixth scope or a Series-scoped Episode workaround.
2. Generic architecture documentation may use Entry/Segment while explicitly documenting Book/Chapter compatibility.
3. A future persistence migration requires its own contract, provenance plan, compatibility tests, and acceptance boundary.
4. Direction, Structure, Realization, and Expression remain semantic layers independent of Entry/Segment scope.
5. Unit-of-delivery remains a presentation/delivery concern and does not automatically create a new canonical scope.

## Non-goals

- no Episode realization implementation;
- no migration of existing BookDirection or book-number storage;
- no rewriting of historical accepted artifacts;
- no introduction of Season as a mandatory scope;
- no inference that every medium uses all five semantic scope positions.

## Rejected alternatives

### Add Episode as a sixth canonical scope

Rejected because it makes the scope lattice medium-specific and invites additional scope proliferation for Film, Route, Mission, and other units.

### Represent Episode permanently as Series scope

Rejected as the long-term semantic model because an installment has its own identity/structure/realization boundary even when stored beneath a Series container.

### Rename every Book/Chapter model immediately

Rejected because it creates a high-risk compatibility migration without product evidence that the storage rewrite is currently necessary.

## Follow-up

The implementation accompanying this ADR introduces a small `EntryKind` / `SegmentKind` vocabulary and compatibility mapping only. Broad persistence migration remains separately gated.