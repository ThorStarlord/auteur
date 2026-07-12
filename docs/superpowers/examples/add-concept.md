# How to Add a New Concept to the Narrative Ontology

This guide walks through the process of adding a new concept to Layer 0. As an example, we'll add a "Political Intrigue" concept to the base ontology.

---

## Step 1: Define the Concept in YAML

Edit `data/ontology/base_ontology.yaml` and add your concept to the `concepts` section. Here's the complete example:

```yaml
concepts:
  # ... existing concepts ...
  
  PoliticalIntrigue:
    name: PoliticalIntrigue
    definition: "A scheme or machination involving multiple characters competing for power, influence, or advantage through hidden agendas and strategic maneuvering. Political intrigues involve power dynamics, information control, and the manipulation of social or political systems."
    category: base
    parent_concepts: []
    relationships:
      - source_concept: PoliticalIntrigue
        target_concept: Character
        cardinality: many-to-many
        description: "Political intrigue involves multiple characters with different goals"
        required: true
      - source_concept: PoliticalIntrigue
        target_concept: Conflict
        cardinality: one-to-many
        description: "Political intrigue generates conflict through competing interests"
        required: false
      - source_concept: PoliticalIntrigue
        target_concept: Revelation
        cardinality: many-to-many
        description: "Political intrigues are often revealed through exposure of hidden agendas"
        required: false
      - source_concept: PoliticalIntrigue
        target_concept: Relationship
        cardinality: one-to-many
        description: "Political intrigue affects character relationships"
        required: false
    validation_rules:
      - rule_id: intrigue_involves_multiple_agents
        condition: "Political intrigue must involve at least two characters with conflicting interests"
        error_message: "Political intrigue requires multiple characters with incompatible goals"
        applies_to: [netorare, mystery, gentlefemdom]
      - rule_id: intrigue_has_hidden_agenda
        condition: "At least one character must have a hidden goal or agenda"
        error_message: "Political intrigue must involve concealed motivations"
        applies_to: [netorare, mystery, gentlefemdom]
      - rule_id: intrigue_affects_narrative_progression
        condition: "Political intrigue must influence the story's direction"
        error_message: "Political intrigue has no impact on narrative"
        applies_to: [netorare, mystery, gentlefemdom]
```

### Key Elements Explained

**name** (required): The concept identifier, used programmatically and in CLI.

**definition** (required): Clear, comprehensive description of what this concept means in narrative context. Should be 1-3 sentences.

**category**: Typically "base" for core ontology, "genre-specific" for genre extensions.

**parent_concepts**: List of concepts this extends (leave empty for new base concepts).

**relationships**: Array of how this concept connects to others.
- **source_concept**: Your new concept name
- **target_concept**: Name of related concept (must exist in ontology)
- **cardinality**: One-to-one, one-to-many, or many-to-many
- **description**: How the relationship works
- **required**: Whether this relationship is mandatory

**validation_rules**: Array of constraints that must hold for valid instances.
- **rule_id**: Unique identifier (kebab-case, descriptive)
- **condition**: Plain English statement of the constraint
- **error_message**: What to show if violated
- **applies_to**: List of genres where rule applies (empty or omit = all genres)

---

## Step 2: Add Pydantic Model Definition

Edit `src/auteur/narrative_ontology/core/narrative_concepts.py` and add validation rules and concept definition:

```python
# Add validation rules for Political Intrigue
POLITICAL_INTRIGUE_RULES = [
    ValidationRule(
        rule_id="intrigue_involves_multiple_agents",
        condition="Political intrigue must involve at least two characters with conflicting interests",
        error_message="Political intrigue requires multiple characters with incompatible goals",
        applies_to=["netorare", "mystery", "gentlefemdom"],
    ),
    ValidationRule(
        rule_id="intrigue_has_hidden_agenda",
        condition="At least one character must have a hidden goal or agenda",
        error_message="Political intrigue must involve concealed motivations",
        applies_to=["netorare", "mystery", "gentlefemdom"],
    ),
    ValidationRule(
        rule_id="intrigue_affects_narrative_progression",
        condition="Political intrigue must influence the story's direction",
        error_message="Political intrigue has no impact on narrative",
        applies_to=["netorare", "mystery", "gentlefemdom"],
    ),
]

# Create the Concept instance
POLITICAL_INTRIGUE = Concept(
    name="PoliticalIntrigue",
    definition="A scheme or machination involving multiple characters competing for power, influence, or advantage through hidden agendas and strategic maneuvering. Political intrigues involve power dynamics, information control, and the manipulation of social or political systems.",
    relationships=[
        Relationship(
            source_concept="PoliticalIntrigue",
            target_concept="Character",
            cardinality="many-to-many",
            description="Political intrigue involves multiple characters with different goals",
            required=True,
        ),
        Relationship(
            source_concept="PoliticalIntrigue",
            target_concept="Conflict",
            cardinality="one-to-many",
            description="Political intrigue generates conflict through competing interests",
            required=False,
        ),
        Relationship(
            source_concept="PoliticalIntrigue",
            target_concept="Revelation",
            cardinality="many-to-many",
            description="Political intrigues are often revealed through exposure of hidden agendas",
            required=False,
        ),
        Relationship(
            source_concept="PoliticalIntrigue",
            target_concept="Relationship",
            cardinality="one-to-many",
            description="Political intrigue affects character relationships",
            required=False,
        ),
    ],
    validation_rules=POLITICAL_INTRIGUE_RULES,
)

# Add to registry (at end of file where ALL_CONCEPTS is built)
ALL_CONCEPTS = {
    "Character": CHARACTER,
    "Arc": ARC,
    # ... existing ...
    "PoliticalIntrigue": POLITICAL_INTRIGUE,  # Add this
}
```

---

## Step 3: Update the Ontology Registry

Edit `src/auteur/narrative_ontology/core/__init__.py` to export the new concept:

```python
from auteur.narrative_ontology.core.narrative_concepts import (
    CHARACTER,
    ARC,
    # ... existing exports ...
    POLITICAL_INTRIGUE,  # Add this
    ALL_CONCEPTS,
    get_concept,
)

__all__ = [
    "CHARACTER",
    "ARC",
    # ... existing ...
    "POLITICAL_INTRIGUE",  # Add this
    "ALL_CONCEPTS",
    "get_concept",
]
```

---

## Step 4: Test the New Concept

Create a test file to verify the concept works correctly. Add tests to `tests/auteur/narrative_ontology/test_base_ontology.py`:

```python
class TestPoliticalIntrigueConcept:
    """Test the PoliticalIntrigue concept definition."""

    def test_political_intrigue_exists(self):
        """Test that PoliticalIntrigue concept is defined."""
        from auteur.narrative_ontology.core import POLITICAL_INTRIGUE
        assert POLITICAL_INTRIGUE is not None
        assert isinstance(POLITICAL_INTRIGUE, Concept)

    def test_political_intrigue_name(self):
        """Test PoliticalIntrigue concept has correct name."""
        from auteur.narrative_ontology.core import POLITICAL_INTRIGUE
        assert POLITICAL_INTRIGUE.name == "PoliticalIntrigue"

    def test_political_intrigue_definition(self):
        """Test PoliticalIntrigue concept has non-empty definition."""
        from auteur.narrative_ontology.core import POLITICAL_INTRIGUE
        assert POLITICAL_INTRIGUE.definition
        assert len(POLITICAL_INTRIGUE.definition) > 0
        assert "power" in POLITICAL_INTRIGUE.definition.lower() or "hidden" in POLITICAL_INTRIGUE.definition.lower()

    def test_political_intrigue_has_relationships(self):
        """Test PoliticalIntrigue has relationships defined."""
        from auteur.narrative_ontology.core import POLITICAL_INTRIGUE
        assert len(POLITICAL_INTRIGUE.relationships) > 0
        # Should have relationships to Character, Conflict, Revelation, Relationship
        target_names = [r.target_concept for r in POLITICAL_INTRIGUE.relationships]
        assert "Character" in target_names
        assert "Conflict" in target_names

    def test_political_intrigue_character_relationship_required(self):
        """Test PoliticalIntrigue requires Character relationship."""
        from auteur.narrative_ontology.core import POLITICAL_INTRIGUE
        char_rels = [r for r in POLITICAL_INTRIGUE.relationships if r.target_concept == "Character"]
        assert len(char_rels) > 0
        assert char_rels[0].required is True

    def test_political_intrigue_has_validation_rules(self):
        """Test PoliticalIntrigue has validation rules."""
        from auteur.narrative_ontology.core import POLITICAL_INTRIGUE
        assert len(POLITICAL_INTRIGUE.validation_rules) > 0
        rule_ids = [r.rule_id for r in POLITICAL_INTRIGUE.validation_rules]
        assert "intrigue_involves_multiple_agents" in rule_ids
        assert "intrigue_has_hidden_agenda" in rule_ids

    def test_political_intrigue_in_registry(self):
        """Test PoliticalIntrigue is registered in ALL_CONCEPTS."""
        from auteur.narrative_ontology.core import ALL_CONCEPTS
        assert "PoliticalIntrigue" in ALL_CONCEPTS
        assert ALL_CONCEPTS["PoliticalIntrigue"].name == "PoliticalIntrigue"

    def test_get_concept_retrieves_political_intrigue(self):
        """Test get_concept function retrieves PoliticalIntrigue."""
        from auteur.narrative_ontology.core import get_concept
        intrigue = get_concept("PoliticalIntrigue")
        assert intrigue.name == "PoliticalIntrigue"

    def test_political_intrigue_validation_rules_apply_to_genres(self):
        """Test PoliticalIntrigue validation rules specify genre applicability."""
        from auteur.narrative_ontology.core import POLITICAL_INTRIGUE
        for rule in POLITICAL_INTRIGUE.validation_rules:
            assert len(rule.applies_to) > 0
            for genre in rule.applies_to:
                assert genre in ["netorare", "mystery", "gentlefemdom"]
```

Run tests to verify:

```bash
pytest tests/auteur/narrative_ontology/test_base_ontology.py::TestPoliticalIntrigueConcept -v
```

---

## Step 5: Verify Integration with OntologyLoader

The OntologyLoader automatically picks up your new concept:

```python
from auteur.narrative_ontology.loader import OntologyLoader

loader = OntologyLoader()

# Your new concept is automatically available
intrigue = loader.get_concept("PoliticalIntrigue")
print(intrigue["definition"])

# Works with CLI inspection
# auteur ontology inspect PoliticalIntrigue
```

---

## Step 6: Update Validators (if applicable)

If you want validators to enforce your concept's rules, update the relevant validator:

```python
# In src/auteur/narrative_ontology/validator/ontology_validator.py
def validate_political_intrigue(self, intrigue: Dict, genre: str = None) -> List[str]:
    """Validate a political intrigue structure against ontology rules."""
    errors = []
    
    # Check required relationships
    if "characters" not in intrigue or len(intrigue["characters"]) < 2:
        errors.append("Political intrigue must involve at least 2 characters")
    
    if not any(char.get("hidden_agenda") for char in intrigue.get("characters", [])):
        errors.append("Political intrigue must have at least one hidden agenda")
    
    return errors
```

---

## Step 7: Commit Your Changes

```bash
git add data/ontology/base_ontology.yaml
git add src/auteur/narrative_ontology/core/narrative_concepts.py
git add src/auteur/narrative_ontology/core/__init__.py
git add tests/auteur/narrative_ontology/test_base_ontology.py

git commit -m "feat: add PoliticalIntrigue concept to base ontology

- Defines political intrigue as scheme involving multiple characters
- Includes relationships to Character, Conflict, Revelation, Relationship
- Adds 3 validation rules for narrative coherence
- Tests verify concept structure and registry integration"
```

---

## Checklist for Adding New Concepts

- [ ] Added concept to `base_ontology.yaml` with complete YAML structure
- [ ] Added validation rules list in `narrative_concepts.py`
- [ ] Added Concept instance in `narrative_concepts.py`
- [ ] Updated ALL_CONCEPTS registry in `narrative_concepts.py`
- [ ] Updated `__init__.py` exports
- [ ] Created comprehensive tests covering:
  - Concept exists and is accessible
  - Definition is non-empty
  - All relationships are present and correct
  - All validation rules are present
  - Genre applicability is specified
  - Registry includes the concept
  - get_concept() function works
- [ ] Ran tests: `pytest tests/auteur/narrative_ontology/ -v`
- [ ] Verified with OntologyLoader manually
- [ ] Committed with descriptive message

---

## Common Pitfalls

**Circular Relationships:** Avoid A→B and B→A unless semantically necessary. Use symmetric relationships instead.

**Too Many Rules:** Start with 2-3 essential rules. Add more only if they prevent genuine errors.

**Vague Definitions:** Definitions should be specific enough to distinguish from similar concepts. "A narrative element" is too vague; "A scheme involving hidden agendas and power competition" is better.

**Missing Genre Applicability:** Always specify `applies_to` in validation rules. If rule applies to all genres, list all three: `["netorare", "mystery", "gentlefemdom"]`.

**Forgetting the Registry:** New concepts must be added to ALL_CONCEPTS dict or they won't be discoverable via get_concept() or CLI.

---

**Last Updated:** 2026-07-12
