# Layer 0: Narrative Ontology Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task without human pauses between tasks.

**Goal:** Implement the foundational semantic layer that defines what narrative concepts exist, their relationships, and validation rules. All higher layers (1-4) reference Layer 0 without redefining it.

**Architecture:** Layer 0 is a declarative ontology—a structured definition of narrative concepts. It answers: "What kinds of things exist in narrative?" Not "how do we build stories?" but "what vocabulary does story-building use?"

**Tech Stack:**
- YAML/JSON for ontology data (human-readable, inspectable)
- Pydantic for ontology validation
- Existing genre_pipeline infrastructure (no special-casing per genre)
- CLI for ontology inspection

## Global Constraints

- Ontology is genre-agnostic (concepts like "Character" exist for all genres)
- Genre-specific ontologies extend base ontology (netorara adds theme-sets, not new concept types)
- All Layer 1-2 validators MUST reference Layer 0 (no hardcoded rules in code)
- Backward compatible: existing Layer 1-2 functionality unchanged, only refactored
- No breaking changes to StoryIdentity, Blueprint, or genre pipelines
- Ontology must be inspectable via CLI (`auteur ontology inspect <concept>`)

---

## File Structure

### New Directory: `src/auteur/narrative_ontology/`

```
src/auteur/narrative_ontology/
├── __init__.py                          # Public API exports
├── schema/
│   ├── __init__.py
│   ├── ontology_types.py                # Pydantic models for ontology structure
│   ├── concept_definition.py            # Base Concept class
│   └── concept_relationships.py         # Relationship definitions
├── core/
│   ├── __init__.py
│   ├── base_ontology.py                 # Core narrative concepts (Character, Arc, Theme, etc.)
│   └── narrative_concepts.py            # Complete concept library
├── genre/
│   ├── __init__.py
│   ├── genre_ontologies.py              # Genre-specific ontology extensions
│   ├── netorara_ontology.py             # Netorara-specific concepts
│   ├── mystery_ontology.py              # Mystery-specific concepts
│   └── gentlefemdom_ontology.py         # Gentle femdom-specific concepts
├── loader/
│   ├── __init__.py
│   └── ontology_loader.py               # Load/validate ontology from YAML
├── validator/
│   ├── __init__.py
│   └── ontology_validator.py            # Validate against ontology definitions
└── cli_ontology.py                      # CLI: `auteur ontology inspect`

data/
└── ontology/
    ├── base_ontology.yaml               # Core narrative concepts
    ├── netorara_ontology.yaml           # Netorara extensions
    ├── mystery_ontology.yaml            # Mystery extensions
    └── gentlefemdom_ontology.yaml       # Gentle femdom extensions

tests/auteur/narrative_ontology/
├── test_ontology_types.py
├── test_concept_definition.py
├── test_base_ontology.py
├── test_genre_ontologies.py
├── test_ontology_loader.py
├── test_ontology_validator.py
├── test_cli_ontology.py
└── test_validation_integration.py       # Test Layer 1-2 validators use Layer 0
```

---

## Task Breakdown

### Phase 1: Ontology Foundation (4 tasks)

**Task 1: Ontology Type Definitions**
- Pydantic models for ontology structure
- `Concept`: name, definition, relationships, validation_rules
- `Relationship`: source, target, cardinality, description
- `ValidationRule`: rule_id, condition, error_message
- `Genre-Specific Extension`: inherits from Concept
- Tests: 12+ covering all type combinations

**Task 2: Base Narrative Concepts**
- Implement core concepts as Pydantic models:
  - `Character`: entity with agency, beliefs, goals, relationships
  - `Arc`: progression over time (character, story, theme arcs)
  - `Theme`: recurring abstract idea
  - `Goal`: desired outcome (character or story goal)
  - `Conflict`: opposition/challenge
  - `Payoff`: resolution of setup
  - `Symbol`: object/image with meaning
  - `Relationship`: connection between entities
  - `Beat`: discrete narrative moment
  - `Setup`: introduction of element requiring resolution
  - `Revelation`: disclosure of hidden information
  - `Reversal`: unexpected change in trajectory
- Tests: 15+ covering concepts and relationships

**Task 3: Genre-Specific Ontologies**
- Netorara extensions:
  - `Cuckoldry Arc`: specific to netorara
  - `Humiliation Progression`: emotional escalation
  - `Consent Boundary`: validation rule for safety
- Mystery extensions:
  - `Investigation Arc`: evidence gathering
  - `Clue`: discrete piece of information
  - `Red Herring`: misdirection element
- Gentle femdom extensions:
  - `Authority Arc`: power dynamic progression
  - `Surrender Beat`: character moment
  - `Trust Checkpoint`: validation milestone
- Tests: 18+ covering genre-specific concepts

**Task 4: Ontology Loader**
- Load base and genre ontologies from YAML
- Validate ontology structure on load
- Merge genre ontologies with base
- Cache for performance
- Tests: 10+ covering load/merge/validation

### Phase 2: Validation & Integration (3 tasks)

**Task 5: Ontology Validator**
- Validate narrative concepts against ontology definitions
- Check concept relationships (e.g., can Character appear in multiple Arcs?)
- Enforce validation rules (e.g., Arc must have start and end)
- Genre-aware validation (netorara has specific rules)
- Tests: 14+ covering validation scenarios

**Task 6: Refactor Layer 1-2 Validators to Use Ontology**
- Update `arc_validator.py` to reference ontology (not hardcoded GENRE_THEMES)
- Update `outline_validator.py` to use ontology relationships
- Ensure all validation rules come from Layer 0
- Tests: Existing tests still pass (no behavior change, only refactoring)

**Task 7: Ontology CLI**
- Command: `auteur ontology inspect <concept>` — show definition, relationships, rules
- Command: `auteur ontology validate <genre>` — validate genre ontology
- Command: `auteur ontology list` — list all concepts
- Tests: 8+ covering CLI commands

### Phase 3: Integration & Verification (2 tasks)

**Task 8: Integration Tests**
- Verify all Layer 1 validators use Layer 0
- Verify all Layer 2 validators use Layer 0
- Test that adding new concept to ontology automatically works in validators
- Prove genre extensibility (adding new genre ontology just extends Layer 0)
- Tests: 12+ integration scenarios

**Task 9: Documentation & Examples**
- Ontology browser/inspector (markdown documentation)
- Example: How to add a new concept
- Example: How to add a new genre
- Tests: 5+ documentation examples

---

## Key Design Decisions

### Ontology as Data, Not Code

Instead of:
```python
# Old (hardcoded in code)
GENRE_THEMES = {"netorara": ["humiliation", "cuckoldry"]}
```

Use:
```yaml
# New (Layer 0 ontology)
Genre:
  netorara:
    extends: base_genre
    themes:
      - humiliation
      - cuckoldry
```

Then reference it:
```python
ontology.genre["netorara"].themes
```

### Concepts Are Composable

```yaml
Character:
  definition: "An entity capable of agency within the narrative"
  relationships:
    - has: Beliefs (one-to-many)
    - has: Goals (one-to-many)
    - participates_in: Arc (many-to-many)
  validation_rules:
    - must_have_identity
    - may_appear_in_multiple_arcs
```

### Genre Ontologies Extend, Not Replace

```yaml
Netorara:
  extends: base_ontology
  new_concepts:
    - Cuckoldry Arc
    - Humiliation Progression
  theme_set: [humiliation, degradation, cuckoldry]
```

---

## Integration Points (No Breaking Changes)

**Layer 1 (StoryIdentity):**
- Already uses Genre, Theme, Emotional Core
- Just validates against Layer 0 definitions

**Layer 2 (Blueprint):**
- arc_validator refactored to reference Layer 0 GENRE_THEMES
- Container validator uses Layer 0 relationship definitions
- No functional change, only refactoring

**Future Layers (3-4):**
- Will automatically inherit Layer 0 validation
- Adding new concepts just extends ontology

---

## Testing Strategy

**Unit Tests (per task):**
- Concept definitions validate correctly
- Relationships encode properly
- Validation rules execute as expected
- Genre ontologies extend correctly

**Integration Tests (Task 8):**
- Layer 1 validators use Layer 0
- Layer 2 validators use Layer 0
- New concept in ontology → automatic validation everywhere
- Genre extension → automatic genre awareness

**Verification:**
- All existing tests (1090+) still pass
- No breaking changes to Layer 1-2 APIs
- Ontology is inspectable and human-readable

---

## Success Criteria

✅ Layer 0 fully defined and validated
✅ All core narrative concepts documented
✅ All 3 genre-specific ontologies implemented
✅ Layer 1-2 validators refactored to use Layer 0
✅ CLI ontology inspector working
✅ All tests passing (1100+)
✅ Zero breaking changes to existing functionality
✅ Documented: how to add new concept, how to add new genre

---

**Last Updated:** 2026-07-12  
**Status:** Ready for implementation  
**Estimated Scope:** 9 tasks, ~400-500 total test cases  
**Continuous Execution:** Yes (no human pauses between tasks)
