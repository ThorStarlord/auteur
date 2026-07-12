# Layer 0: The Narrative Ontology

## What is Layer 0?

Layer 0 is the foundational semantic layer of the Auteur narrative engineering toolkit. It defines **what kinds of things exist in narrative**, not how to build stories with them. Think of it as a dictionary of narrative concepts—a formal ontology that answers the question: "What vocabulary does storytelling use?"

Unlike operational layers (Layers 1-7) that describe processes and workflows, Layer 0 is a **declarative ontology**:

- **Concept definitions**: Abstract ideas that appear in all narratives
- **Relationship types**: How concepts connect to each other
- **Validation rules**: Constraints that ensure narrative coherence
- **Genre extensions**: Additional concepts for specific narrative genres

This separation of concerns means:

1. **All higher layers reference Layer 0** without redefining concepts
2. **New genres extend, not replace** the base ontology
3. **Validation rules come from the ontology**, not hardcoded in code
4. **Adding new concepts automatically propagates** to all validators

---

## Core Narrative Concepts (12 Base Concepts)

The Layer 0 base ontology defines 12 core concepts that appear in every narrative, regardless of genre:

### 1. Character

**Definition:** An entity capable of agency within the narrative. Characters have identities, beliefs, goals, and can participate in relationships and arcs.

**Key Relationships:**
- Pursues one or more **Goals** (one-to-many)
- Appears in multiple **Arcs** (many-to-many)
- Engages in **Relationships** with other entities (one-to-many)

**Validation Rules:**
- Must have an identity (name or identifier)
- May have zero or more goals
- May appear in multiple arcs
- Beliefs must form coherent worldview within same arc

**Example:** In a netorare narrative, the protagonist is a Character with goals (maintain relationship) and beliefs (spouse is faithful). The supporting character (other lover) is another Character with conflicting goals.

---

### 2. Arc

**Definition:** A progression over time from a starting state to an ending state. Arcs can track character development, story progression, or thematic exploration.

**Key Relationships:**
- Contains one or more **Beats** (one-to-many, required)
- Involves one or more **Characters** (many-to-many)
- Explores one or more **Themes** (many-to-many)
- Contains one or more **Conflicts** (one-to-many)

**Validation Rules:**
- Must have a defined starting point
- Must have a defined ending point
- Must contain one or more beats
- Progression from start to end should show change

**Example:** A character arc in mystery shows the detective's journey from "suspect is innocent" to "suspect is guilty"; a theme arc explores how justice evolves from retribution to rehabilitation.

---

### 3. Theme

**Definition:** A recurring abstract idea or concept explored throughout the narrative. Themes are not concrete entities but intellectual or emotional explorations.

**Key Relationships:**
- Influences multiple **Arcs** (many-to-many)
- Manifests through **Symbols** (many-to-many)

**Validation Rules:**
- Is abstract and may not have concrete state
- May exist unresolved throughout narrative
- May influence multiple arcs

**Example:** "Trust is fragile" is a theme that might appear in both the main romance arc and a subplot about friendship betrayal.

---

### 4. Goal

**Definition:** A desired outcome that an entity (typically a character) wants to achieve. Goals create motivation and can generate conflicts.

**Key Relationships:**
- Owned by a **Character** (many-to-many, required)
- Pursuit may create **Conflict** (many-to-many)

**Validation Rules:**
- Must represent something an entity wants to achieve
- Can be pursued, achieved, or abandoned
- Must belong to a Character or Story entity

**Example:** "Uncover the killer's identity" is a goal in mystery; "preserve the secret affair" is a goal in netorare.

---

### 5. Conflict

**Definition:** Opposition or challenge involving at least two forces with incompatible goals. Conflict creates narrative tension and drives progression.

**Key Relationships:**
- Occurs within an **Arc** (many-to-many)
- Resolves in a **Payoff** (one-to-one)

**Validation Rules:**
- Must involve at least two opposing forces
- Should create forward momentum in narrative
- Must have something at stake

**Example:** Detective vs. killer, protagonist vs. protagonist's own denial, character vs. society's judgment.

---

### 6. Payoff

**Definition:** The resolution or delivery of something set up earlier in the narrative. Payoffs satisfy expectations created by setups.

**Key Relationships:**
- Resolves a **Setup** (many-to-many, required)

**Validation Rules:**
- Must resolve a corresponding Setup
- Must come after its setup in narrative sequence

**Example:** A mysterious letter is setup in Act 1; revelation of its sender is payoff in Act 3.

---

### 7. Symbol

**Definition:** An object, image, or action that carries meaning beyond its literal interpretation. Symbols represent abstract concepts through concrete forms.

**Key Relationships:**
- Represents one or more **Themes** (many-to-many)

**Validation Rules:**
- Can represent multiple concepts simultaneously
- Meaning can evolve throughout narrative

**Example:** A wedding ring symbolizes commitment, fidelity, or obligation—and its meaning shifts as story progresses.

---

### 8. Relationship

**Definition:** A connection between narrative entities (typically characters) that affects how they interact. Relationships have dynamics, stakes, and evolution.

**Key Relationships:**
- Connects two **Characters** (many-to-many, required)

**Validation Rules:**
- Must connect two narrative entities
- Must influence narrative progression

**Example:** Romantic relationship (main couple), professional relationship (rivals), family relationship (sibling trust).

---

### 9. Beat

**Definition:** A discrete, identifiable moment in the narrative. Beats are atomic narrative units that combine to form scenes and arcs.

**Key Relationships:**
- Belongs to one or more **Arcs** (many-to-many, required)

**Validation Rules:**
- Is a single, identifiable narrative moment
- Must have action, dialogue, or revelation
- Must belong to at least one arc

**Example:** "The protagonist discovers the affair" is a beat; "the confrontation scene" is a beat; "the reconciliation handshake" is a beat.

---

### 10. Setup

**Definition:** The introduction of an element, promise, or mystery that requires later resolution. Setups create expectations that drive narrative forward.

**Key Relationships:**
- Requires corresponding **Payoff** (one-to-one, required)

**Validation Rules:**
- Must introduce an element requiring later resolution
- Must have corresponding payoff

**Example:** "Why does the suspect have the victim's phone?" (setup) requires explanation (payoff).

---

### 11. Revelation

**Definition:** The disclosure of information previously unknown to the audience or characters. Revelations change understanding and can reframe entire narratives.

**Key Relationships:**
- Occurs as a **Beat** (many-to-many)

**Validation Rules:**
- Must disclose information previously unknown to audience/character
- Must alter how narrative is understood

**Example:** "The witness was lying the whole time" reframes entire investigation; "the spouse knew all along" recontextualizes entire affair narrative.

---

### 12. Reversal

**Definition:** An unexpected change that inverts the direction or expected outcome of an arc. Reversals violate established patterns and create surprise.

**Key Relationships:**
- Affects one or more **Arcs'** trajectory (many-to-many)

**Validation Rules:**
- Must invert the expected direction of arc
- Should violate established expectations

**Example:** Detective convinced of guilt discovers suspect's innocence; character convinced spouse is cheating discovers spouse was actually protecting them.

---

## Genre-Specific Extensions

Each supported narrative genre extends the base ontology with additional concepts relevant to its emotional and thematic domain. These extensions **do not replace base concepts**—they add new ones that coexist with the 12 core concepts.

### Netorare Extensions (4 Concepts)

**New Concepts:**
- `CuckoldryArc`: Progression through emotional stages (revelation → humiliation → acceptance/resolution)
- `HumiliationProgression`: Escalation or modulation of humiliation elements
- `ConsentBoundary`: Defined limits on interactions and contact
- `DesireManipulation`: Psychological manipulation of character desires

**Example:** In a netorare narrative, a CuckoldryArc spans the protagonist's journey from ignorance through humiliation to some form of acceptance, while ConsentBoundary tracks what interactions the characters have agreed to allow.

---

### Mystery Extensions (4 Concepts)

**New Concepts:**
- `InvestigationArc`: Evidence gathering and hypothesis testing
- `Clue`: Discrete piece of information (evidence, testimony, observation)
- `RedHerring`: Misdirection element that delays truth-finding
- `DeductiveChain`: Sequence of logical conclusions building toward solution

**Example:** A Clue might be "the killer wore size 10 shoes"; a RedHerring might be "the suspect was seen at the scene"—they're both Beats, but have different relationships to the Investigation Arc.

---

### Gentle Femdom Extensions (4 Concepts)

**New Concepts:**
- `AuthorityArc`: Progression of power dynamics and authority establishment
- `SurrenderBeat`: Moment where character chooses submission/trust
- `TrustCheckpoint`: Validation milestone where trust deepens or fractures
- `IntimacyBoundary`: Negotiated limits on physical/emotional vulnerability

**Example:** An AuthorityArc shows how a dominant character establishes authority; TrustCheckpoints mark moments where the submissive character chooses deeper vulnerability.

---

## Layer 0 Architecture

### Directory Structure

```
data/ontology/
├── base_ontology.yaml           # Core narrative concepts (12)
├── netorare_ontology.yaml       # Netorare extensions (4)
├── mystery_ontology.yaml        # Mystery extensions (4)
└── gentlefemdom_ontology.yaml   # Gentle femdom extensions (4)

src/auteur/narrative_ontology/
├── schema/
│   └── ontology_types.py        # Pydantic models (Concept, Relationship, ValidationRule)
├── core/
│   └── narrative_concepts.py    # Concept registry and definitions
├── loader/
│   └── ontology_loader.py       # Load/cache/merge ontologies
└── validator/
    └── ontology_validator.py    # Validate against ontology
```

### Key Classes

**Concept** (Pydantic model)
```python
class Concept(BaseModel):
    name: str                              # Concept name
    definition: str                        # Human-readable definition
    relationships: List[Relationship]      # How concept connects to others
    validation_rules: List[ValidationRule] # Constraints on this concept
```

**Relationship** (Pydantic model)
```python
class Relationship(BaseModel):
    source_concept: str                           # Origin concept
    target_concept: str                           # Related concept
    cardinality: Literal["one-to-one", "one-to-many", "many-to-many"]
    description: str                              # Relationship meaning
    required: bool                                # Whether relationship is mandatory
```

**ValidationRule** (Pydantic model)
```python
class ValidationRule(BaseModel):
    rule_id: str                    # Unique identifier
    condition: str                  # Rule description
    error_message: str              # Error if violated
    applies_to: List[str]           # Genres this applies to
```

---

## Using Layer 0

### Inspecting Concepts

```python
from auteur.narrative_ontology.loader import OntologyLoader

loader = OntologyLoader()

# Get a concept
character_concept = loader.get_concept("Character")
print(character_concept["definition"])

# Get genre-specific concept
cuckoldry_arc = loader.get_concept("CuckoldryArc", genre="netorare")

# List all concepts
base_concepts = loader.get_concept_names()
netorare_concepts = loader.get_concept_names(genre="netorare")

# Get genre extensions (non-base concepts)
netorare_only = loader.get_genre_extensions("netorare")  # ["CuckoldryArc", ...]
```

### Validating Against Ontology

```python
from auteur.narrative_ontology.validator import OntologyValidator

validator = OntologyValidator()

# Check if concept exists
validator.concept_exists("Character")  # True
validator.concept_exists("UnknownConcept")  # False

# Check concept relationships
validator.has_relationship("Character", "Goal", genre="netorare")  # True

# Validate a narrative structure against ontology
errors = validator.validate_narrative_structure({
    "characters": [{"name": "Alice"}],
    "arcs": [{"name": "Main Arc", "beats": [...]}]
}, genre="netorare")

if errors:
    print("Validation errors:", errors)
```

### CLI Inspection

```bash
# List all concepts
auteur ontology list

# Inspect a specific concept
auteur ontology inspect Character
auteur ontology inspect CuckoldryArc --genre netorare

# Validate a genre's ontology
auteur ontology validate netorare

# Show genre extensions
auteur ontology extensions netorare
```

---

## Relationship Cardinality

Understanding cardinality is essential for modeling narratives:

### One-to-One (1:1)
A Setup requires exactly one Payoff; a Payoff resolves exactly one Setup.

```yaml
Setup:
  relationships:
    - target_concept: Payoff
      cardinality: one-to-one
      required: true
```

**Example:** "The letter is found" (Setup) has exactly one moment when its identity is revealed (Payoff).

### One-to-Many (1:M)
A Character can have multiple Goals; each Goal belongs to one Character.

```yaml
Character:
  relationships:
    - target_concept: Goal
      cardinality: one-to-many
      required: false
```

**Example:** Protagonist wants to find killer (Goal 1), protect family (Goal 2), and maintain sanity (Goal 3).

### Many-to-Many (M:M)
A Character appears in multiple Arcs; an Arc involves multiple Characters.

```yaml
Character:
  relationships:
    - target_concept: Arc
      cardinality: many-to-many
      required: false
```

**Example:** Same detective appears in murder arc and parallel corruption arc; same protagonist's guilt arc involves both main love interest and rival.

---

## Validation Rules Structure

Every concept has validation rules that define constraints. Rules are genre-aware:

```yaml
Character:
  validation_rules:
    - rule_id: character_must_have_identity
      condition: "Character must have a name or identifier"
      error_message: "Character cannot be defined without an identity"
      applies_to: [netorare, mystery, gentlefemdom]
    
    - rule_id: character_beliefs_must_be_consistent
      condition: "Character beliefs should form coherent worldview"
      error_message: "Character beliefs are contradictory within same arc"
      applies_to: [netorare, mystery, gentlefemdom]
```

Rules apply across all genres (in `applies_to`), ensuring:
- **Consistency**: A character's beliefs don't contradict within same arc
- **Completeness**: Characters must have identifiable presence
- **Genre specificity**: Genre-only rules (like `consent_boundary_consistent` for netorare)

---

## Integration with Other Layers

### Layer 1-2 Validators

All higher-layer validators (StoryIdentity, Blueprint) reference Layer 0:

```python
# OLD (hardcoded):
GENRE_THEMES = {"netorare": ["humiliation", "cuckoldry", "..."], ...}

# NEW (Layer 0):
loader = OntologyLoader()
netorare_concepts = loader.get_concept_names(genre="netorare")
# ["Character", "Arc", ..., "CuckoldryArc", "HumiliationProgression", ...]
```

This ensures validation rules are:
- **Centralized** in Layer 0
- **Maintainable** (one source of truth)
- **Extensible** (new concepts auto-propagate)

### No Breaking Changes

Layer 0 refactoring preserves all Layer 1-2 APIs and behaviors:
- StoryIdentity validation unchanged
- Blueprint validation unchanged
- All existing tests pass (1090+)

---

## Best Practices

### When Adding Concepts

1. **Is it a narrative concept?** (Applies to storytelling universally, not just one genre)
2. **Does it have relationships?** (How does it connect to other concepts?)
3. **Does it have validation rules?** (What constraints ensure coherence?)

If yes to all three, it belongs in Layer 0.

### Concept Naming

- **PascalCase** for concept names (Character, HumiliationProgression)
- **Meaningful names** that reflect narrative role
- **Consistent across documentation** (YAML, Pydantic, CLI)

### Validation Rules

- **rule_id**: kebab-case, descriptive (character_must_have_identity)
- **condition**: Plain English description of the constraint
- **error_message**: What went wrong and how to fix it
- **applies_to**: List of genres (empty = all genres)

---

## See Also

- [How to Add a New Concept](examples/add-concept.md)
- [How to Add a New Genre](examples/add-genre.md)
- [Ontology Validator Reference](../validator/ontology_validator.py)
- [Ontology Loader Reference](../loader/ontology_loader.py)

---

**Last Updated:** 2026-07-12  
**Status:** Complete and documented  
**Version:** 1.0
