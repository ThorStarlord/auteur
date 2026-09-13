# How to Add a Narrative Ontology Concept

> Current for Narrative Ontology V2. The canonical specification source is `src/auteur/data/ontology/`; do not duplicate a concept definition in Python.

## 1. Decide whether the idea belongs in Ontology

Add a Layer-0 concept only when the term is reusable semantic vocabulary needed across narrative artifacts. Do **not** add project-specific facts, authorial commitments, workflow state, Global Map entries, or subjective craft judgments as concepts.

Use these owners instead when appropriate:

- Identity: authorial commitments;
- Structure: concrete plans;
- Realization: accepted story-instance events/facts/state transitions;
- Expression: prose/language;
- Reasoning/Critics: interpretive craft judgment;
- Provenance/workflow: revision, source, acceptance, and orchestration metadata.

See `docs/architecture/narrative-ontology-v2.md` and `docs/architecture/narrative-ontology-reconciliation-v2.md`.

## 2. Add the declaration to the packaged specification

For a generally reusable concept, edit either the historical compatibility core only when that contract genuinely needs amendment, or preferably the V2 supplemental vocabulary:

```text
src/auteur/data/ontology/semantic_vocabulary.yaml
```

Example:

```yaml
concepts:
  PoliticalIntrigue:
    name: PoliticalIntrigue
    definition: A reusable narrative pattern of competing power interests, hidden agendas, and strategic information control.
    category: semantic
    parent_concepts: []
    relationships:
      - source_concept: PoliticalIntrigue
        target_concept: Character
        relation_type: participates_in
        cardinality: many-to-many
        description: Political intrigue may involve multiple characters.
        required: true
    validation_rules:
      - rule_id: political_intrigue_effectiveness
        kind: interpretive_criterion
        condition: The intrigue should materially affect narrative understanding or pressure.
        error_message: Political intrigue may be narratively inert.
        applies_to: []
```

Relationship targets and parent concepts must resolve. If `relation_type` is supplied, the id must exist in `src/auteur/data/ontology/relation_types.yaml`.

Supported cardinalities are:

- `one-to-one`
- `one-to-many`
- `many-to-one`
- `many-to-many`

## 3. Classify rules correctly

Every rule belongs to one of four categories:

- `schema_constraint` — objective data-shape/reference requirement;
- `semantic_invariant` — deterministic semantic requirement;
- `craft_heuristic` — advisory craft guidance;
- `interpretive_criterion` — subjective or model/human judgment.

Only schema constraints and semantic invariants execute inside `OntologyValidator`, and they must reference a **named executor** plus structured parameters. Free-text `condition` is documentation only and is never evaluated as code.

Example deterministic rule:

```yaml
- rule_id: example_requires_owner
  kind: semantic_invariant
  executor: required_fields
  parameters:
    fields: [owner_id]
  condition: The instance requires an owner.
  error_message: Missing owner.
  applies_to: []
```

Do not add arbitrary Python expressions to YAML.

## 4. Add a genre extension only for real semantic vocabulary

Genre extension files use:

```text
src/auteur/data/ontology/<genre>_ontology.yaml
```

A genre that has no ontology extension still inherits the core ontology. Do not create an extension merely to store pacing advice, reader expectations, or other craft recommendations; those belong in genre craft/guide systems.

Compatibility aliases for historical public names belong in:

```text
src/auteur/data/ontology/compatibility.yaml
```

## 5. No parallel Python registry edit

Do **not** add the concept to `src/auteur/narrative_ontology/core/narrative_concepts.py`.

That module is a legacy compatibility facade for the historical twelve concepts. `OntologyRegistry` discovers current semantics from packaged YAML.

Use:

```python
from auteur.narrative_ontology import OntologyRegistry

registry = OntologyRegistry()
concept = registry.get_concept("PoliticalIntrigue", "literary")
assert concept is not None
registry.assert_valid()
```

## 6. Add deterministic qualification

At minimum test:

1. the concept loads through `OntologyRegistry`;
2. all parent and relationship references resolve;
3. all referenced relation-type ids resolve;
4. executable rules have known executors;
5. the concept works for a core-only product genre when it is general vocabulary;
6. invalid declarations fail closed;
7. no ontology API acquires or mutates canonical story authority.

Run the narrative-ontology suite and then the repository's normal qualification commands.

## Checklist

- [ ] Confirmed the term belongs in Layer 0.
- [ ] Added exactly one canonical YAML definition under `src/auteur/data/ontology/`.
- [ ] Used a registered relation type where appropriate.
- [ ] Classified each rule as schema, semantic invariant, craft heuristic, or interpretive criterion.
- [ ] Used a named executor for every executable rule.
- [ ] Added no executable free-text expressions.
- [ ] Added/updated compatibility alias only when needed.
- [ ] Added positive and rejection tests.
- [ ] `OntologyRegistry.assert_valid()` passes.
- [ ] No duplicate Python ontology definition was added.

**Last updated:** 2026-09-11
