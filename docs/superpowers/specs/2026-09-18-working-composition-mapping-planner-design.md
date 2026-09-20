# Working Composition and Mapping Planner Design

**Date:** 2026-09-18
**Status:** Approved design direction; implementation not authorized
**Scope:** Beginner Workspace architectural design only

## Context

The Beginner Workspace currently composes primarily Mystery guidance. That
supports investigation mechanics, but a story may also depend on materially
important emotional, relationship, thematic, aesthetic, setting, or world
dimensions. The current Mystery-only projection can therefore produce a
coherent Mystery foundation that does not feel like the foundation of the
author's complete story.

Auteur already contains relevant domain capabilities, including target
experience, Story Identity commitments, Story Design Packs, Genre Packs,
relationship concepts, and emotional guidance. The problem is how to compose
those sources without creating an arbitrary pack stack, a second canonical
model, or silent interpretation of author intent.

This design is grounded in the canonical narrative architecture and preserves
the existing authority boundary: canonical Identity and Structure remain owned
by existing domain services.

## Decision

The Beginner Workspace will use a durable, noncanonical `WorkingComposition`
inside the Beginner session layer. It records proposed and author-confirmed
creative dimensions, their provenance, their working lifecycle, unresolved
tensions, and the guidance sources used to explain them.

The composition is not a new semantic layer and is not a canonical lens
artifact. It is orchestration state used to produce contextual guidance and a
promotion proposal.

```text
premise
  ↓
dimension detection
  ↓
author confirmation
  ↓
WorkingComposition
  ↓
per-dimension mappings
  ↓
composition and collision resolution
  ↓
candidate StoryIdentity
  ↓
promotion preview
  ↓
existing authority service
```

The system should propose relevant dimensions, but the author must confirm,
reject, revise, or add them. Pack selection, dimension confirmation, mapping,
and guidance never mutate canonical state by themselves.

## Dimension model

Semantic category and provenance origin are separate axes.

### Semantic categories

```text
PRIMARY_ENGINE
GENRE_SUBGENRE
EMOTIONAL_AESTHETIC
RELATIONSHIP_THEMATIC
SETTING_WORLD
```

### Origins

```text
DETECTED_FROM_PACK
INFERRED_FROM_STORY
AUTHOR_DEFINED
AUTHOR_MODIFIED
```

Author confirmation is not an origin. It is independently represented through
the dimension lifecycle, confirmation record, rationale, and provenance.

### Lifecycle

```text
DETECTED
PROPOSED
CONFIRMED
REJECTED
SUPERSEDED
```

An author-defined relationship lens may therefore be:

```text
category: RELATIONSHIP_THEMATIC
origin: AUTHOR_DEFINED
status: CONFIRMED
label: "Author-provided relationship lens"
```

The author-facing label may be edited without renaming or mutating the
underlying pack referenced by related guidance.

## Working composition requirements

The composition envelope must preserve, at minimum:

- stable composition and workspace identifiers;
- envelope schema version;
- dimensions and their categories;
- origin and lifecycle status;
- author-facing labels;
- detection evidence;
- author confirmation, rejection, or override rationale;
- source pack identifiers, versions, and content hashes;
- guidance provenance;
- explicit tensions and their participating dimensions;
- acknowledgement state for productive tensions;
- unresolved interpretation or mapping items;
- revision-workspace identity when applicable;
- and links to accepted upstream milestones.

It must reference existing domain definitions rather than duplicate their
meaning. Custom lenses preserve the author's wording and intent even when no
current pack fully represents them.

## Guidance composition

Guidance is composed from confirmed working dimensions using deterministic,
curated rules. The composition layer must:

- preserve the primary engine;
- select only relevant supporting dimensions for each Decision Card;
- explain reinforcing relationships between dimensions;
- explain productive tensions without treating them as errors;
- identify hard conflicts using existing domain or pack validation;
- preserve all source provenance;
- and distinguish unsupported representation from irrelevance to the current
  milestone.

The first implementation must not use an LLM as the source of mapping or
canonical authority.

## Mapping Planner

The Mapping Planner is an application-layer proposal and explanation
component. It does not validate or mutate canonical artifacts.

```text
confirmed WorkingComposition
        ↓
per-dimension deterministic mapping
        ↓
MappingRecords
        ↓
collision and contribution composition
        ↓
candidate StoryIdentity
        ↓
domain validation
        ↓
Promotion Preview
        ↓
existing authority service
```

### Mapping record

Each mapping preserves:

```text
mapping_id
source_dimension_id
source_category
source_origin
source_provenance
destination_field?
proposed_value?
contribution?
mapping_strength
evidence_class
disposition
review_status
rationale
unmapped_remainder?
author_override?
```

`mapping_strength` describes the relationship to canon:

```text
DIRECT_DOMAIN_MAPPING
SUPPORTED_CONTRIBUTION
CONTEXTUAL_INFLUENCE
UNRESOLVED_INTERPRETATION
```

`evidence_class` describes what justifies the mapping:

```text
DOMAIN_CONTRACT
PACK_METADATA
CURATED_COMPOSITION_RULE
AUTHOR_CONFIRMED_DECISION
EXISTING_CANONICAL_STATE
```

`disposition` describes semantic treatment:

```text
MAPS_TO_CANON
CONTRIBUTES_TO_CANON
GUIDANCE_CONTEXT
PROVENANCE_ONLY
REQUIRES_AUTHOR_DECISION
NOT_REPRESENTABLE_BY_CURRENT_DOMAIN
NOT_RELEVANT_TO_THIS_MILESTONE
```

`review_status` describes the author's response:

```text
PROPOSED
ACCEPTED
REJECTED
DEFERRED
OVERRIDDEN
```

The distinction is intentional. A mapping may remain `MAPS_TO_CANON` with
`review_status: REJECTED`; rejection records the author's response without
changing the semantic meaning of the proposal.

Rejecting or deferring a mapping does not deactivate its source dimension. The
confirmed dimension remains active in `WorkingComposition` unless the author
separately rejects, revises, or supersedes that dimension.

## Deterministic resolution

The resolver operates in explicit stages:

```text
validate individual mappings
  ↓
group by canonical destination
  ↓
merge compatible contributions
  ↓
surface collisions
  ↓
build candidate StoryIdentity
  ↓
compute unmapped remainder
  ↓
derive semantic patch and diff
  ↓
run existing domain validation
```

Mapping semantics must not depend on incidental insertion order. Any precedence
must be supplied by an explicit curated rule.

Compatible contributions retain their source order for explanation and their
full provenance, but are not semantically determined by that order. Collisions
remain visible with all competing proposals and require author review when
they affect canonical coherence.

Author overrides may replace a proposed value only with a value already
permitted by the existing canonical vocabulary and validation rules. An
unsupported override produces the validation diagnostic
`INVALID_FOR_CURRENT_VOCABULARY`, is excluded from the candidate Identity, and
is returned for author revision. This diagnostic is not a mapping disposition
or review status. The planner does not make the final authority judgment; the
existing domain service performs final validation at acceptance.

An `author_override` payload preserves:

- the original proposed value;
- the replacement value;
- the author's rationale;
- affected source dimension IDs;
- and the preflight and final validation results.

## Promotion preview

The preview must show:

```text
current canonical Identity
proposed canonical Identity
semantic canonical diff
mapping explanations
unresolved items
downstream impact
```

Every proposed canonical change links to one or more Mapping Records.

The preview classifies composition information as:

```text
WILL BECOME CANONICAL
WILL GUIDE DOWNSTREAM WORK
WILL REMAIN CONTEXT / PROVENANCE
UNRESOLVED
```

The Mapping Planner may target only existing canonical fields and values
supported by the current `StoryIdentity` contract. Examples in this document
are illustrative and do not establish new canonical schema.

Promotion is lossy only when the author can see the loss. Information that
cannot be represented canonically must remain visible as contextual or
provenance information before acceptance.

## Canonical authority and staleness

The authority boundary remains:

```text
WorkingComposition
        ≠ canon

pack selection
        ≠ canon

mapping proposal
        ≠ canon

candidate StoryIdentity
        ≠ canon

author acceptance
+ domain validation
+ existing authority service
        ↓
canonical mutation
```

Acceptance atomically validates the mapping, writes the canonical Identity
change through the existing authority path, preserves mapping provenance, and
computes downstream staleness.

Failed acceptance must leave prior canon and working state unchanged.

Staleness is based only on semantic canonical changes. The following must not
stale downstream artifacts by themselves:

- changed labels;
- changed author wording;
- changed pack references;
- changed provenance text;
- or other working-composition metadata.

The Mapping Planner does not own final canonical validation or canonical
mutation. It may perform preflight vocabulary checks and delegate candidate
validation to existing domain services.

## Tensions and milestone blocking

A tension record preserves:

- participating dimension IDs;
- the explanation of the tension;
- the affected decision or canonical contract;
- whether the author acknowledged it;
- and whether it blocks acceptance.

Productive tension is nonblocking when acknowledged. Existing domain and pack
validation remains authoritative for hard conflicts.

Milestone blocking follows these rules:

- a confirmed `PRIMARY_ENGINE` must have a valid mapping to an existing
  canonical value before Story Identity acceptance;
- unresolved mappings block only when they are required for canonical
  coherence;
- `NOT_REPRESENTABLE_BY_CURRENT_DOMAIN` is nonblocking when its remainder is
  acknowledged and preserved, unless an existing domain rule requires that
  representation;
- and rejected or deferred mappings do not block merely because they were
  rejected or deferred, provided the resulting candidate remains coherent.

## Revision behavior

Revision workspaces receive their own composition overlay. They compare:

```text
current canonical Identity
previously accepted mapping provenance
proposed revised mapping
proposed revised canonical Identity
```

Exploration recomputes mappings, guidance, impact, and semantic diffs without
mutating canon or creating actual downstream staleness. Only explicit
acceptance of the revised milestone can replace canonical state and trigger
semantic downstream staleness.

## Worked acceptance case

The first acceptance case uses a sanitized hybrid Mystery premise containing:

```text
Primary engine:
Mystery investigation

Supporting world dimension:
Superhero public identity

Supporting relationship dimension:
Author-defined relationship-betrayal tension
```

The exact canonical destinations in this example remain conditional on
repository verification. No example mapping creates a new field or vocabulary.

Expected mapping classes:

1. **Direct mapping** — the Mystery dimension maps to an existing canonical
   engine or genre value supported by the current Identity contract.
2. **Compatible contribution** — the superhero dimension contributes to an
   existing supported Identity commitment, if one exists; otherwise it remains
   contextual guidance and provenance.
3. **Relationship contribution** — the author-defined relationship dimension
   contributes to supported emotional, thematic, conflict, or relationship
   commitments where the current domain permits it.
4. **Unmapped remainder** — erotic aesthetic framing or power-shift emphasis
   remains visible as guidance context and provenance if no canonical field
   supports it.
5. **Author override** — the author replaces one proposed canonical value with
   an alternative value already permitted by the existing destination
   contract. A conceptual example such as “analytical investigation” versus
   “subjective uncertainty” is valid only if repository verification confirms
   that destination and vocabulary.
6. **Semantic diff** — only resulting canonical Identity changes contribute to
   downstream staleness.

The worked case must prove:

- pack confirmation creates guidance context, not canon;
- no dimension disappears because the domain cannot fully represent it;
- no unsupported lens object is canonized;
- canonical mappings are visible before acceptance;
- author overrides remain within domain vocabulary;
- and promotion is atomic.

## Alternatives rejected

### Arbitrary pack stacking

Rejected because it provides no semantic roles, precedence, collision model, or
authority boundary.

### Silent automatic inference

Rejected because it hides interpretation and can misrepresent authorial intent.

### Manual selection of every pack

Rejected because it places excessive ontology and pack knowledge burden on
beginners.

### New canonical lens object

Rejected because existing Identity concepts may already represent the resulting
commitments, while unsupported nuance should remain contextual until the domain
explicitly supports it.

## Acceptance criteria for the design

Before implementation planning begins, the design review must confirm that:

- the composition is session-layer, durable, and noncanonical;
- semantic category, origin, lifecycle, disposition, review status, mapping
  strength, and evidence class remain distinct;
- mappings target only existing canonical vocabulary;
- collisions and unmapped remainder are visible;
- author overrides are validated and auditable;
- semantic canonical diff, not composition churn, drives staleness;
- revision overlays preserve current canon;
- promotion delegates validation and mutation to existing authority services;
- the hybrid Mystery acceptance case is sanitized and reproducible;
- and no implementation work begins before this design is reviewed.

## Repository grounding

This design is grounded in:

- `docs/narrative-architecture.md` — canonical semantic layers and authority
  boundaries;
- `docs/design/decision-oriented-tutor.md` — derived guidance and
  advice-not-canon contract;
- `docs/product/creative-writing-tutor.md` — learning-by-doing Tutor boundary;
- `src/auteur/identity.py` — current Story Identity commitments;
- `src/auteur/blueprint.py` — target experience and emotional contracts;
- `src/auteur/genre_packs/models.py` and built-in packs — existing genre/profile
  knowledge;
- `src/auteur/story_design_packs/models.py` and composition — reusable design
  pack concepts and provenance;
- `src/auteur/beginner/guidance.py` — current derived guidance and semantic
  consequence model;
- `src/auteur/beginner/mystery_adapter.py` — current Mystery-only qualification
  inventory and evidence boundary.

## Phase boundary

This document authorizes design review only.

Not authorized by this document:

- production schema changes;
- persistence changes;
- Mapping Planner implementation;
- Beginner adapter changes;
- browser/UI changes;
- test changes;
- implementation planning;
- or qualification runs.
