# How to Add a New Genre to the Narrative Ontology

This guide walks through the process of adding a new genre and its associated ontology extensions. As an example, we'll add "Psychological Thriller" genre with its unique concepts.

---

## Understanding Genre Extension Architecture

A genre extension:
1. **Inherits all base concepts** (Character, Arc, Theme, etc. remain unchanged)
2. **Adds genre-specific concepts** (concepts that only apply to that genre)
3. **Uses genre-specific validation rules** (constraints unique to the genre's narrative needs)
4. **Extends without replacing** (base ontology is pristine, genre concepts coexist)

---

## Step 1: Define the Genre Ontology in YAML

Create a new file `data/ontology/psychological_thriller_ontology.yaml`:

```yaml
# Psychological Thriller Genre Ontology
# Genre-specific concepts for psychological thriller narratives
# Extends base ontology with concepts for mental manipulation, unreliable narration, and psychological tension

extends: base

concepts:
  UnreliableNarrator:
    name: UnreliableNarrator
    definition: "A character whose perspective or account of events cannot be fully trusted. Unreliable narrators distort reality through mental illness, dishonesty, or limited perception, creating doubt about what actually happened."
    category: genre-specific
    parent_concepts:
      - Character
    relationships:
      - source_concept: UnreliableNarrator
        target_concept: Revelation
        cardinality: many-to-many
        description: "Unreliable narrator's distortions are often revealed later"
        required: false
      - source_concept: UnreliableNarrator
        target_concept: Arc
        cardinality: many-to-many
        description: "Unreliable narrator appears in psychological arcs"
        required: false
      - source_concept: UnreliableNarrator
        target_concept: Beat
        cardinality: many-to-many
        description: "Unreliable narrator's perspective distorts individual beats"
        required: false
    validation_rules:
      - rule_id: unreliable_narrator_has_distortion_motive
        condition: "Unreliable narrator's distortions must stem from psychological cause (trauma, mental illness, dishonesty)"
        error_message: "Unreliable narrator lacks motivation for distortion"
        applies_to: [psychological_thriller]
      - rule_id: unreliable_narrator_creates_doubt
        condition: "Unreliable narrator must create genuine uncertainty for audience"
        error_message: "Unreliable narrator's presence creates no narrative doubt"
        applies_to: [psychological_thriller]

  MentalRealm:
    name: MentalRealm
    definition: "Internal psychological space—memories, fantasies, delusions, or subconscious manifestations. Mental realms exist parallel to external events and reveal character psychology."
    category: genre-specific
    parent_concepts:
      - Arc
    relationships:
      - source_concept: MentalRealm
        target_concept: Character
        cardinality: many-to-many
        description: "Mental realm represents character's internal state"
        required: true
      - source_concept: MentalRealm
        target_concept: Symbol
        cardinality: many-to-many
        description: "Mental realm manifests through surreal symbols"
        required: false
      - source_concept: MentalRealm
        target_concept: Reversal
        cardinality: many-to-many
        description: "Mental realm can shift reality through psychological reversal"
        required: false
    validation_rules:
      - rule_id: mental_realm_reflects_psychology
        condition: "Mental realm must reflect character's emotional or psychological state"
        error_message: "Mental realm is disconnected from character psychology"
        applies_to: [psychological_thriller]
      - rule_id: mental_realm_affects_external_events
        condition: "Mental realm perceptions must influence character's external actions"
        error_message: "Mental realm has no impact on narrative progression"
        applies_to: [psychological_thriller]

  ParanoiaEscalation:
    name: ParanoiaEscalation
    definition: "Progressive intensification of character suspicion, fear, or mistrust. Paranoia escalation tracks how uncertainty and threat perception grow, whether justified or imagined."
    category: genre-specific
    parent_concepts:
      - Conflict
    relationships:
      - source_concept: ParanoiaEscalation
        target_concept: Character
        cardinality: many-to-many
        description: "Paranoia escalation affects character perception and behavior"
        required: true
      - source_concept: ParanoiaEscalation
        target_concept: Revelation
        cardinality: many-to-many
        description: "Paranoia escalation is often resolved or recontextualized by revelation"
        required: false
      - source_concept: ParanoiaEscalation
        target_concept: Relationship
        cardinality: many-to-many
        description: "Paranoia escalation damages or transforms relationships"
        required: false
    validation_rules:
      - rule_id: paranoia_has_justification_or_delusion
        condition: "Paranoia must be either justified (real threat) or rooted in delusion"
        error_message: "Paranoia escalation lacks narrative foundation"
        applies_to: [psychological_thriller]
      - rule_id: paranoia_shows_progression
        condition: "Paranoia must visibly intensify through narrative"
        error_message: "Paranoia escalation shows no meaningful progression"
        applies_to: [psychological_thriller]

  TruthAmbiguity:
    name: TruthAmbiguity
    definition: "A situation or revelation where the actual truth remains deliberately unclear or multiple contradictory truths are possible. Truth ambiguity sustains psychological uncertainty."
    category: genre-specific
    parent_concepts:
      - Setup
    relationships:
      - source_concept: TruthAmbiguity
        target_concept: Revelation
        cardinality: many-to-many
        description: "Truth ambiguity may or may not be resolved by revelation"
        required: false
      - source_concept: TruthAmbiguity
        target_concept: UnreliableNarrator
        cardinality: many-to-many
        description: "Truth ambiguity often stems from unreliable narrator"
        required: false
      - source_concept: TruthAmbiguity
        target_concept: Theme
        cardinality: many-to-many
        description: "Truth ambiguity often embodies theme about perception vs. reality"
        required: false
    validation_rules:
      - rule_id: truth_ambiguity_creates_interpretation_space
        condition: "Truth ambiguity must allow multiple valid interpretations"
        error_message: "Truth ambiguity allows only one obvious interpretation"
        applies_to: [psychological_thriller]
      - rule_id: truth_ambiguity_affects_character_decisions
        condition: "Truth ambiguity must influence how characters act"
        error_message: "Truth ambiguity has no bearing on narrative"
        applies_to: [psychological_thriller]

metadata:
  version: "1.0"
  last_updated: "2026-07-12"
  description: "Genre-specific concepts for psychological thriller narratives"
  genre: psychological_thriller
  extends: base
  new_concepts_count: 4
  new_concepts:
    - UnreliableNarrator
    - MentalRealm
    - ParanoiaEscalation
    - TruthAmbiguity
```

### Key Elements Explained

**extends**: Must reference "base" to inherit all core concepts.

**concepts**: Dictionary of new genre-specific concepts (don't redefine base concepts here).

**parent_concepts**: List which base concept(s) this extends. `UnreliableNarrator` extends `Character` because unreliable narrators are a special kind of character.

**validation_rules -> applies_to**: Use the new genre's identifier: `["psychological_thriller"]`.

**metadata -> new_concepts**: List of concept names added (for documentation).

---

## Step 2: Register Genre in Python

Edit `src/auteur/narrative_ontology/genre/genre_ontologies.py` to add genre metadata:

```python
"""Genre ontology definitions and registry."""

from typing import Dict, List

# Supported genres
SUPPORTED_GENRES = {
    "netorare",
    "mystery",
    "gentlefemdom",
    "psychological_thriller",  # Add this
}

# Genre metadata (description, port, concept count, etc.)
GENRE_METADATA = {
    "netorare": {
        "description": "Cuckoldry and humiliation narratives",
        "port": 8765,
        "new_concepts": 4,
        "emotional_cores": ["Classic Humiliation", "Horror", "Mystery"],
    },
    "mystery": {
        "description": "Detective and investigation narratives",
        "port": 8766,
        "new_concepts": 4,
        "emotional_cores": ["Howdunit", "Paranoia", "Cozy"],
    },
    "gentlefemdom": {
        "description": "Power dynamic and intimate dominance narratives",
        "port": 8767,
        "new_concepts": 4,
        "emotional_cores": ["Sensual Dominance", "Tender Surrender", "Romantic Authority"],
    },
    "psychological_thriller": {  # Add this
        "description": "Psychological manipulation and unreliable perception narratives",
        "port": 8768,
        "new_concepts": 4,
        "emotional_cores": ["Paranoid Descent", "Reality Fracture", "Trust Shattered"],
    },
}

def get_genre_port(genre: str) -> int:
    """Get the CLI server port for a genre."""
    metadata = GENRE_METADATA.get(genre)
    if not metadata:
        raise ValueError(f"Unknown genre: {genre}")
    return metadata["port"]

def get_supported_genres() -> List[str]:
    """Return list of supported genres."""
    return sorted(list(SUPPORTED_GENRES))

def get_genre_metadata(genre: str) -> Dict:
    """Get metadata for a genre."""
    if genre not in GENRE_METADATA:
        raise ValueError(f"Unknown genre: {genre}")
    return GENRE_METADATA[genre]
```

---

## Step 3: Create Genre-Specific Python Module

Create `src/auteur/narrative_ontology/genre/psychological_thriller_ontology.py`:

```python
"""Psychological Thriller Genre Ontology Extensions

Layer 0 Task 3: Genre-specific concepts for psychological thriller narratives.
Defines concepts specific to narratives involving mental manipulation, unreliable
perception, psychological tension, and truth ambiguity.
"""

from auteur.narrative_ontology.schema.ontology_types import (
    Concept,
    Relationship,
    ValidationRule,
)

# ============================================================================
# VALIDATION RULES FOR PSYCHOLOGICAL THRILLER CONCEPTS
# ============================================================================

UNRELIABLE_NARRATOR_RULES = [
    ValidationRule(
        rule_id="unreliable_narrator_has_distortion_motive",
        condition="Unreliable narrator's distortions must stem from psychological cause",
        error_message="Unreliable narrator lacks motivation for distortion",
        applies_to=["psychological_thriller"],
    ),
    ValidationRule(
        rule_id="unreliable_narrator_creates_doubt",
        condition="Unreliable narrator must create genuine uncertainty for audience",
        error_message="Unreliable narrator's presence creates no narrative doubt",
        applies_to=["psychological_thriller"],
    ),
]

MENTAL_REALM_RULES = [
    ValidationRule(
        rule_id="mental_realm_reflects_psychology",
        condition="Mental realm must reflect character's emotional or psychological state",
        error_message="Mental realm is disconnected from character psychology",
        applies_to=["psychological_thriller"],
    ),
    ValidationRule(
        rule_id="mental_realm_affects_external_events",
        condition="Mental realm perceptions must influence character's external actions",
        error_message="Mental realm has no impact on narrative progression",
        applies_to=["psychological_thriller"],
    ),
]

PARANOIA_ESCALATION_RULES = [
    ValidationRule(
        rule_id="paranoia_has_justification_or_delusion",
        condition="Paranoia must be either justified (real threat) or rooted in delusion",
        error_message="Paranoia escalation lacks narrative foundation",
        applies_to=["psychological_thriller"],
    ),
    ValidationRule(
        rule_id="paranoia_shows_progression",
        condition="Paranoia must visibly intensify through narrative",
        error_message="Paranoia escalation shows no meaningful progression",
        applies_to=["psychological_thriller"],
    ),
]

TRUTH_AMBIGUITY_RULES = [
    ValidationRule(
        rule_id="truth_ambiguity_creates_interpretation_space",
        condition="Truth ambiguity must allow multiple valid interpretations",
        error_message="Truth ambiguity allows only one obvious interpretation",
        applies_to=["psychological_thriller"],
    ),
    ValidationRule(
        rule_id="truth_ambiguity_affects_character_decisions",
        condition="Truth ambiguity must influence how characters act",
        error_message="Truth ambiguity has no bearing on narrative",
        applies_to=["psychological_thriller"],
    ),
]

# ============================================================================
# PSYCHOLOGICAL THRILLER CONCEPTS
# ============================================================================

UNRELIABLE_NARRATOR = Concept(
    name="UnreliableNarrator",
    definition="A character whose perspective or account of events cannot be fully trusted. Unreliable narrators distort reality through mental illness, dishonesty, or limited perception.",
    relationships=[
        Relationship(
            source_concept="UnreliableNarrator",
            target_concept="Revelation",
            cardinality="many-to-many",
            description="Unreliable narrator's distortions are often revealed later",
            required=False,
        ),
        Relationship(
            source_concept="UnreliableNarrator",
            target_concept="Arc",
            cardinality="many-to-many",
            description="Unreliable narrator appears in psychological arcs",
            required=False,
        ),
        Relationship(
            source_concept="UnreliableNarrator",
            target_concept="Beat",
            cardinality="many-to-many",
            description="Unreliable narrator's perspective distorts individual beats",
            required=False,
        ),
    ],
    validation_rules=UNRELIABLE_NARRATOR_RULES,
)

MENTAL_REALM = Concept(
    name="MentalRealm",
    definition="Internal psychological space—memories, fantasies, delusions, or subconscious manifestations. Mental realms exist parallel to external events.",
    relationships=[
        Relationship(
            source_concept="MentalRealm",
            target_concept="Character",
            cardinality="many-to-many",
            description="Mental realm represents character's internal state",
            required=True,
        ),
        Relationship(
            source_concept="MentalRealm",
            target_concept="Symbol",
            cardinality="many-to-many",
            description="Mental realm manifests through surreal symbols",
            required=False,
        ),
        Relationship(
            source_concept="MentalRealm",
            target_concept="Reversal",
            cardinality="many-to-many",
            description="Mental realm can shift reality through psychological reversal",
            required=False,
        ),
    ],
    validation_rules=MENTAL_REALM_RULES,
)

PARANOIA_ESCALATION = Concept(
    name="ParanoiaEscalation",
    definition="Progressive intensification of character suspicion, fear, or mistrust. Paranoia escalation tracks how uncertainty and threat perception grow.",
    relationships=[
        Relationship(
            source_concept="ParanoiaEscalation",
            target_concept="Character",
            cardinality="many-to-many",
            description="Paranoia escalation affects character perception and behavior",
            required=True,
        ),
        Relationship(
            source_concept="ParanoiaEscalation",
            target_concept="Revelation",
            cardinality="many-to-many",
            description="Paranoia escalation is often resolved by revelation",
            required=False,
        ),
        Relationship(
            source_concept="ParanoiaEscalation",
            target_concept="Relationship",
            cardinality="many-to-many",
            description="Paranoia escalation damages or transforms relationships",
            required=False,
        ),
    ],
    validation_rules=PARANOIA_ESCALATION_RULES,
)

TRUTH_AMBIGUITY = Concept(
    name="TruthAmbiguity",
    definition="A situation where the actual truth remains deliberately unclear or multiple contradictory truths are possible. Truth ambiguity sustains psychological uncertainty.",
    relationships=[
        Relationship(
            source_concept="TruthAmbiguity",
            target_concept="Revelation",
            cardinality="many-to-many",
            description="Truth ambiguity may or may not be resolved by revelation",
            required=False,
        ),
        Relationship(
            source_concept="TruthAmbiguity",
            target_concept="UnreliableNarrator",
            cardinality="many-to-many",
            description="Truth ambiguity often stems from unreliable narrator",
            required=False,
        ),
        Relationship(
            source_concept="TruthAmbiguity",
            target_concept="Theme",
            cardinality="many-to-many",
            description="Truth ambiguity often embodies theme about perception vs. reality",
            required=False,
        ),
    ],
    validation_rules=TRUTH_AMBIGUITY_RULES,
)

# Registry for genre-specific concepts
PSYCHOLOGICAL_THRILLER_CONCEPTS = {
    "UnreliableNarrator": UNRELIABLE_NARRATOR,
    "MentalRealm": MENTAL_REALM,
    "ParanoiaEscalation": PARANOIA_ESCALATION,
    "TruthAmbiguity": TRUTH_AMBIGUITY,
}
```

---

## Step 4: Update OntologyLoader

Edit `src/auteur/narrative_ontology/loader/ontology_loader.py` to recognize the new genre:

```python
def load_genre_ontology(self, genre: str) -> Dict[str, Any]:
    """Load genre-specific ontology from YAML file.

    Loads genre extensions for netorare, mystery, gentlefemdom, or psychological_thriller.
    Each genre file contains genre-specific concepts that extend the base ontology.
    """
    # Update valid_genres set
    valid_genres = {"netorare", "mystery", "gentlefemdom", "psychological_thriller"}
    if genre not in valid_genres:
        raise ValueError(
            f"Invalid genre: {genre}. Must be one of: {valid_genres}"
        )
    # ... rest of function unchanged ...
```

Also update `get_concept()` method:

```python
def get_concept(self, name: str, genre: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve a concept by name, optionally with genre context."""
    if genre is None:
        # ... existing code ...
        pass
    else:
        valid_genres = {"netorare", "mystery", "gentlefemdom", "psychological_thriller"}
        if genre not in valid_genres:
            raise ValueError(
                f"Invalid genre: {genre}. Must be one of: {valid_genres}"
            )
        # ... rest of function unchanged ...
```

---

## Step 5: Test the New Genre

Create test file `tests/auteur/narrative_ontology/test_psychological_thriller_ontology.py`:

```python
"""Tests for psychological thriller genre ontology (Task 3).

Tests that psychological thriller concepts are properly defined with:
- Correct definitions
- Relationships to base and other genre concepts
- Validation rules
- Genre-specific validation
"""

import pytest
from auteur.narrative_ontology.loader import OntologyLoader
from auteur.narrative_ontology.schema.ontology_types import Concept


class TestPsychologicalThrillerGenre:
    """Test psychological thriller ontology."""

    def test_genre_ontology_loads(self):
        """Test that psychological thriller ontology can be loaded."""
        loader = OntologyLoader()
        concepts = loader.load_genre_ontology("psychological_thriller")
        assert concepts is not None
        assert len(concepts) == 4

    def test_genre_concepts_exist(self):
        """Test all psychological thriller concepts exist."""
        loader = OntologyLoader()
        concepts = loader.load_genre_ontology("psychological_thriller")
        expected = {"UnreliableNarrator", "MentalRealm", "ParanoiaEscalation", "TruthAmbiguity"}
        assert set(concepts.keys()) == expected

    def test_unreliable_narrator_concept(self):
        """Test UnreliableNarrator concept is properly defined."""
        loader = OntologyLoader()
        narrator = loader.get_concept("UnreliableNarrator", genre="psychological_thriller")
        assert narrator["name"] == "UnreliableNarrator"
        assert "distort" in narrator["definition"].lower()
        assert len(narrator["relationships"]) > 0

    def test_mental_realm_requires_character(self):
        """Test MentalRealm has required relationship to Character."""
        loader = OntologyLoader()
        realm = loader.get_concept("MentalRealm", genre="psychological_thriller")
        char_rels = [r for r in realm["relationships"] if r["target_concept"] == "Character"]
        assert len(char_rels) > 0
        assert char_rels[0]["required"] is True

    def test_paranoia_escalation_has_rules(self):
        """Test ParanoiaEscalation has validation rules."""
        loader = OntologyLoader()
        paranoia = loader.get_concept("ParanoiaEscalation", genre="psychological_thriller")
        assert len(paranoia["validation_rules"]) > 0
        rule_ids = [r["rule_id"] for r in paranoia["validation_rules"]]
        assert "paranoia_has_justification_or_delusion" in rule_ids

    def test_genre_concepts_apply_to_psychological_thriller(self):
        """Test all validation rules specify psychological_thriller applicability."""
        loader = OntologyLoader()
        concepts = loader.load_genre_ontology("psychological_thriller")
        for concept_name, concept in concepts.items():
            for rule in concept.get("validation_rules", []):
                assert "psychological_thriller" in rule["applies_to"]

    def test_merged_ontology_contains_base_and_genre(self):
        """Test merged ontology has both base and genre concepts."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        genre = loader.load_genre_ontology("psychological_thriller")
        merged = loader.merge_ontologies(base, genre)
        
        # Should have base concepts
        assert "Character" in merged
        assert "Arc" in merged
        
        # Should have genre concepts
        assert "UnreliableNarrator" in merged
        assert "MentalRealm" in merged

    def test_get_concept_names_includes_genre(self):
        """Test get_concept_names returns both base and genre concepts."""
        loader = OntologyLoader()
        concepts = loader.get_concept_names(genre="psychological_thriller")
        
        # Base concepts
        assert "Character" in concepts
        assert "Arc" in concepts
        
        # Genre concepts
        assert "UnreliableNarrator" in concepts
        assert "MentalRealm" in concepts

    def test_get_genre_extensions_psychological_thriller(self):
        """Test get_genre_extensions returns only genre-specific concepts."""
        loader = OntologyLoader()
        extensions = loader.get_genre_extensions("psychological_thriller")
        
        # Should include genre concepts
        assert "UnreliableNarrator" in extensions
        assert "MentalRealm" in extensions
        
        # Should NOT include base concepts
        assert "Character" not in extensions
        assert "Arc" not in extensions
```

Run tests:

```bash
pytest tests/auteur/narrative_ontology/test_psychological_thriller_ontology.py -v
```

---

## Step 6: Update Validation Rules (if applicable)

If genres have special validation, update `ontology_validator.py`:

```python
# In src/auteur/narrative_ontology/validator/ontology_validator.py

def validate_genre_concepts_exist(self, genre: str) -> List[str]:
    """Validate that a genre has all required concepts."""
    errors = []
    required_by_genre = {
        "netorare": ["Character", "CuckoldryArc"],
        "mystery": ["Character", "InvestigationArc"],
        "gentlefemdom": ["Character", "AuthorityArc"],
        "psychological_thriller": ["Character", "UnreliableNarrator", "MentalRealm"],
    }
    
    loader = OntologyLoader()
    concepts = loader.get_concept_names(genre=genre)
    concept_set = set(concepts)
    
    for required in required_by_genre.get(genre, []):
        if required not in concept_set:
            errors.append(f"{genre} ontology missing required concept: {required}")
    
    return errors
```

---

## Step 7: Commit Your Changes

```bash
git add data/ontology/psychological_thriller_ontology.yaml
git add src/auteur/narrative_ontology/genre/genre_ontologies.py
git add src/auteur/narrative_ontology/genre/psychological_thriller_ontology.py
git add src/auteur/narrative_ontology/loader/ontology_loader.py
git add src/auteur/narrative_ontology/validator/ontology_validator.py
git add tests/auteur/narrative_ontology/test_psychological_thriller_ontology.py

git commit -m "feat: add psychological_thriller genre to ontology

- Defines 4 genre-specific concepts:
  - UnreliableNarrator: perspective cannot be fully trusted
  - MentalRealm: internal psychological space
  - ParanoiaEscalation: progressive threat perception
  - TruthAmbiguity: deliberately unclear truth
- Registers genre in loader and validator
- All concepts inherit from base ontology
- Genre validation rules specify psychological_thriller applicability
- Comprehensive tests verify genre structure and integration"
```

---

## Step 8: Verify Genre Works End-to-End

```python
from auteur.narrative_ontology.loader import OntologyLoader

loader = OntologyLoader()

# Verify genre loads correctly
base = loader.load_base_ontology()
genre = loader.load_genre_ontology("psychological_thriller")
merged = loader.merge_ontologies(base, genre)

print(f"Base concepts: {len(base)}")  # 12
print(f"Genre concepts: {len(genre)}")  # 4
print(f"Total (merged): {len(merged)}")  # 16

# Verify specific concepts
unreliable = loader.get_concept("UnreliableNarrator", genre="psychological_thriller")
print(f"UnreliableNarrator definition: {unreliable['definition'][:50]}...")

# Verify extensions
extensions = loader.get_genre_extensions("psychological_thriller")
print(f"Genre-specific concepts: {extensions}")
```

---

## Checklist for Adding New Genres

- [ ] Created YAML file at `data/ontology/{genre}_ontology.yaml`
- [ ] YAML includes `extends: base` at top
- [ ] All concepts have complete structure (name, definition, relationships, rules)
- [ ] All validation rules have `applies_to: [{genre}]`
- [ ] Created Python module at `src/auteur/narrative_ontology/genre/{genre}_ontology.py`
- [ ] Registered genre in `genre_ontologies.py` with metadata
- [ ] Updated `OntologyLoader.load_genre_ontology()` to include new genre
- [ ] Updated `OntologyLoader.get_concept()` to include new genre
- [ ] Created comprehensive test file
- [ ] All tests passing: `pytest tests/auteur/narrative_ontology/ -v`
- [ ] Verified end-to-end with manual OntologyLoader test
- [ ] Committed with descriptive message

---

## Common Pitfalls

**Forgetting `extends: base`:** Genre YAML must extend base ontology or relationships to base concepts won't work.

**Hardcoding Genre Validation:** Use the loader/validator infrastructure rather than hardcoding genre checks.

**Duplicate Base Concepts:** Never redefine base concepts in genre YAML. Only add new concepts.

**Missing Port Allocation:** Each genre needs a unique port for CLI server. Check `GENRE_METADATA` in `genre_ontologies.py`.

**Incomplete Validation Rules:** Every genre concept needs at least 1-2 validation rules to be meaningful.

---

**Last Updated:** 2026-07-12
