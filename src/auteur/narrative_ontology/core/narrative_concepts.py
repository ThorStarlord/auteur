"""Task 2: Base Narrative Concepts

Implements all core narrative concepts as Pydantic model instances.
These concepts form the foundation of the narrative ontology layer.
"""

from auteur.narrative_ontology.schema.ontology_types import (
    Concept,
    Relationship,
    ValidationRule,
)

# ============================================================================
# VALIDATION RULES FOR EACH CONCEPT
# ============================================================================

# Character validation rules
CHARACTER_RULES = [
    ValidationRule(
        rule_id="character_must_have_identity",
        condition="Character must have a name or identifier",
        error_message="Character cannot be defined without an identity",
    ),
    ValidationRule(
        rule_id="character_may_have_goals",
        condition="Character may have zero or more goals",
        error_message="Character goal cardinality violated",
    ),
    ValidationRule(
        rule_id="character_may_appear_in_multiple_arcs",
        condition="Same character can appear in multiple arcs",
        error_message="Character cannot be restricted to single arc",
    ),
    ValidationRule(
        rule_id="character_beliefs_must_be_consistent",
        condition="Character beliefs should form coherent worldview",
        error_message="Character beliefs are contradictory within same arc",
    ),
]

# Arc validation rules
ARC_RULES = [
    ValidationRule(
        rule_id="arc_must_have_start",
        condition="Arc must have a defined starting point",
        error_message="Arc cannot begin without clear starting state",
    ),
    ValidationRule(
        rule_id="arc_must_have_end",
        condition="Arc must have a defined ending point",
        error_message="Arc cannot conclude without clear ending state",
    ),
    ValidationRule(
        rule_id="arc_must_contain_beats",
        condition="Arc must contain one or more beats",
        error_message="Arc cannot exist without narrative moments",
    ),
    ValidationRule(
        rule_id="arc_progression_is_monotonic",
        condition="Progression from start to end should show change",
        error_message="Arc shows no meaningful progression",
    ),
]

# Theme validation rules
THEME_RULES = [
    ValidationRule(
        rule_id="theme_is_abstract_concept",
        condition="Theme is abstract and may not have concrete state",
        error_message="Theme cannot be treated as concrete entity",
    ),
    ValidationRule(
        rule_id="theme_may_not_require_resolution",
        condition="Theme may exist unresolved throughout narrative",
        error_message="Theme must resolve (themes can exist unresolved)",
    ),
    ValidationRule(
        rule_id="theme_influences_multiple_arcs",
        condition="Single theme can influence many arcs",
        error_message="Theme scope violated",
    ),
]

# Goal validation rules
GOAL_RULES = [
    ValidationRule(
        rule_id="goal_must_be_desired_outcome",
        condition="Goal must represent something an entity wants to achieve",
        error_message="Goal is not a desired outcome",
    ),
    ValidationRule(
        rule_id="goal_may_be_achieved_or_abandoned",
        condition="Goal can be pursued, achieved, or abandoned",
        error_message="Goal state is invalid",
    ),
    ValidationRule(
        rule_id="goal_must_have_owner",
        condition="Goal must belong to a Character or Story entity",
        error_message="Goal has no owner",
    ),
]

# Conflict validation rules
CONFLICT_RULES = [
    ValidationRule(
        rule_id="conflict_must_involve_opposition",
        condition="Conflict must involve at least two opposing forces",
        error_message="Conflict lacks opposition",
    ),
    ValidationRule(
        rule_id="conflict_creates_narrative_tension",
        condition="Conflict should create forward momentum in narrative",
        error_message="Conflict does not generate tension",
    ),
    ValidationRule(
        rule_id="conflict_must_have_stakes",
        condition="Conflict must have something at stake",
        error_message="Conflict has no stakes",
    ),
]

# Payoff validation rules
PAYOFF_RULES = [
    ValidationRule(
        rule_id="payoff_resolves_setup",
        condition="Payoff must resolve a corresponding Setup",
        error_message="Payoff exists without matching setup",
    ),
    ValidationRule(
        rule_id="payoff_must_occur_after_setup",
        condition="Payoff must come after its setup in narrative sequence",
        error_message="Payoff precedes setup in narrative",
    ),
]

# Symbol validation rules
SYMBOL_RULES = [
    ValidationRule(
        rule_id="symbol_has_multiple_meanings",
        condition="Symbol can represent multiple concepts simultaneously",
        error_message="Symbol reduced to single meaning",
    ),
    ValidationRule(
        rule_id="symbol_meaning_evolves",
        condition="Symbol meaning can evolve throughout narrative",
        error_message="Symbol meaning is static",
    ),
]

# Relationship validation rules
RELATIONSHIP_RULES = [
    ValidationRule(
        rule_id="relationship_connects_entities",
        condition="Relationship must connect two narrative entities",
        error_message="Relationship has no clear connection",
    ),
    ValidationRule(
        rule_id="relationship_affects_narrative",
        condition="Relationship must influence narrative progression",
        error_message="Relationship is narratively inert",
    ),
]

# Beat validation rules
BEAT_RULES = [
    ValidationRule(
        rule_id="beat_is_discrete_moment",
        condition="Beat is a single, identifiable narrative moment",
        error_message="Beat spans multiple discrete moments",
    ),
    ValidationRule(
        rule_id="beat_must_have_content",
        condition="Beat must have action, dialogue, or revelation",
        error_message="Beat is empty of narrative content",
    ),
    ValidationRule(
        rule_id="beat_belongs_in_arc",
        condition="Beat must belong to at least one arc",
        error_message="Beat is orphaned from arc structure",
    ),
]

# Setup validation rules
SETUP_RULES = [
    ValidationRule(
        rule_id="setup_introduces_element",
        condition="Setup must introduce an element requiring later resolution",
        error_message="Setup introduces nothing requiring resolution",
    ),
    ValidationRule(
        rule_id="setup_must_be_resolved",
        condition="Setup must have corresponding payoff",
        error_message="Setup exists without resolution",
    ),
]

# Revelation validation rules
REVELATION_RULES = [
    ValidationRule(
        rule_id="revelation_discloses_hidden_info",
        condition="Revelation must disclose information previously unknown to audience/character",
        error_message="Revelation reveals nothing new",
    ),
    ValidationRule(
        rule_id="revelation_changes_understanding",
        condition="Revelation must alter how narrative is understood",
        error_message="Revelation does not change understanding",
    ),
]

# Reversal validation rules
REVERSAL_RULES = [
    ValidationRule(
        rule_id="reversal_inverts_trajectory",
        condition="Reversal must invert the expected direction of arc",
        error_message="Reversal does not change direction",
    ),
    ValidationRule(
        rule_id="reversal_must_be_unexpected",
        condition="Reversal should violate established expectations",
        error_message="Reversal is predictable or expected",
    ),
]

# ============================================================================
# RELATIONSHIPS BETWEEN CONCEPTS
# ============================================================================

# Character relationships
CHARACTER_RELATIONSHIPS = [
    Relationship(
        source="Character",
        target="Beliefs",
        cardinality="one-to-many",
        relationship_type="has",
        description="Character holds one or more beliefs about the world",
        required=False,
    ),
    Relationship(
        source="Character",
        target="Goal",
        cardinality="one-to-many",
        relationship_type="pursues",
        description="Character pursues one or more goals",
        required=False,
    ),
    Relationship(
        source="Character",
        target="Arc",
        cardinality="many-to-many",
        relationship_type="participates_in",
        description="Character can appear in multiple arcs",
        required=False,
    ),
    Relationship(
        source="Character",
        target="Relationship",
        cardinality="one-to-many",
        relationship_type="engages_in",
        description="Character engages in relationships with other entities",
        required=False,
    ),
]

# Arc relationships
ARC_RELATIONSHIPS = [
    Relationship(
        source="Arc",
        target="Beat",
        cardinality="one-to-many",
        relationship_type="contains",
        description="Arc contains one or more beats",
        required=True,
    ),
    Relationship(
        source="Arc",
        target="Character",
        cardinality="many-to-many",
        relationship_type="involves",
        description="Arc involves one or more characters",
        required=False,
    ),
    Relationship(
        source="Arc",
        target="Theme",
        cardinality="many-to-many",
        relationship_type="explores",
        description="Arc explores one or more themes",
        required=False,
    ),
    Relationship(
        source="Arc",
        target="Conflict",
        cardinality="one-to-many",
        relationship_type="contains",
        description="Arc contains one or more conflicts",
        required=False,
    ),
]

# Theme relationships
THEME_RELATIONSHIPS = [
    Relationship(
        source="Theme",
        target="Arc",
        cardinality="many-to-many",
        relationship_type="influences",
        description="Theme influences multiple arcs",
        required=False,
    ),
    Relationship(
        source="Theme",
        target="Symbol",
        cardinality="many-to-many",
        relationship_type="manifests_as",
        description="Theme manifests through symbols",
        required=False,
    ),
]

# Goal relationships
GOAL_RELATIONSHIPS = [
    Relationship(
        source="Goal",
        target="Character",
        cardinality="many-to-one",
        relationship_type="owned_by",
        description="Goal is owned by a character",
        required=True,
    ),
    Relationship(
        source="Goal",
        target="Conflict",
        cardinality="many-to-one",
        relationship_type="creates",
        description="Goal pursuit creates conflict",
        required=False,
    ),
]

# Conflict relationships
CONFLICT_RELATIONSHIPS = [
    Relationship(
        source="Conflict",
        target="Arc",
        cardinality="many-to-one",
        relationship_type="occurs_in",
        description="Conflict occurs within an arc",
        required=False,
    ),
    Relationship(
        source="Conflict",
        target="Payoff",
        cardinality="one-to-one",
        relationship_type="resolves_to",
        description="Conflict resolves in payoff",
        required=False,
    ),
]

# Payoff relationships
PAYOFF_RELATIONSHIPS = [
    Relationship(
        source="Payoff",
        target="Setup",
        cardinality="many-to-one",
        relationship_type="resolves",
        description="Payoff resolves a setup",
        required=True,
    ),
]

# Symbol relationships
SYMBOL_RELATIONSHIPS = [
    Relationship(
        source="Symbol",
        target="Theme",
        cardinality="many-to-many",
        relationship_type="represents",
        description="Symbol represents themes",
        required=False,
    ),
]

# Relationship concept relationships (meta!)
RELATIONSHIP_CONCEPT_RELATIONSHIPS = [
    Relationship(
        source="Relationship",
        target="Character",
        cardinality="many-to-many",
        relationship_type="connects",
        description="Relationship connects characters",
        required=True,
    ),
]

# Beat relationships
BEAT_RELATIONSHIPS = [
    Relationship(
        source="Beat",
        target="Arc",
        cardinality="many-to-one",
        relationship_type="belongs_to",
        description="Beat belongs to an arc",
        required=True,
    ),
]

# Setup relationships
SETUP_RELATIONSHIPS = [
    Relationship(
        source="Setup",
        target="Payoff",
        cardinality="one-to-one",
        relationship_type="requires",
        description="Setup requires corresponding payoff",
        required=True,
    ),
]

# Revelation relationships
REVELATION_RELATIONSHIPS = [
    Relationship(
        source="Revelation",
        target="Beat",
        cardinality="many-to-one",
        relationship_type="occurs_as",
        description="Revelation occurs as a beat",
        required=False,
    ),
]

# Reversal relationships
REVERSAL_RELATIONSHIPS = [
    Relationship(
        source="Reversal",
        target="Arc",
        cardinality="many-to-one",
        relationship_type="affects",
        description="Reversal affects an arc's trajectory",
        required=False,
    ),
]

# ============================================================================
# CORE NARRATIVE CONCEPTS (11 required + 1 bonus)
# ============================================================================

CHARACTER = Concept(
    name="Character",
    definition="An entity capable of agency within the narrative. Characters have identities, beliefs, goals, and can participate in relationships and arcs.",
    relationships=CHARACTER_RELATIONSHIPS,
    validation_rules=CHARACTER_RULES,
    category="entity",
    metadata={
        "examples": ["protagonist", "antagonist", "supporting character"],
        "properties": ["identity", "beliefs", "goals", "relationships"],
    },
)

ARC = Concept(
    name="Arc",
    definition="A progression over time from a starting state to an ending state. Arcs can track character development, story progression, or thematic exploration.",
    relationships=ARC_RELATIONSHIPS,
    validation_rules=ARC_RULES,
    category="progression",
    metadata={
        "examples": ["character arc", "plot arc", "thematic arc"],
        "properties": ["start_state", "end_state", "beats", "progression"],
        "arc_types": ["character", "plot", "theme"],
    },
)

THEME = Concept(
    name="Theme",
    definition="A recurring abstract idea or concept explored throughout the narrative. Themes are not concrete entities but intellectual or emotional explorations.",
    relationships=THEME_RELATIONSHIPS,
    validation_rules=THEME_RULES,
    category="abstract",
    metadata={
        "examples": ["power", "redemption", "identity", "betrayal"],
        "properties": ["name", "description"],
        "characteristics": ["abstract", "may_not_resolve", "influences_multiple_arcs"],
    },
)

GOAL = Concept(
    name="Goal",
    definition="A desired outcome that an entity (typically a character) wants to achieve. Goals create motivation and can generate conflicts.",
    relationships=GOAL_RELATIONSHIPS,
    validation_rules=GOAL_RULES,
    category="entity",
    metadata={
        "examples": ["win the competition", "escape the building", "gain trust"],
        "properties": ["owner", "target", "difficulty"],
        "goal_types": ["immediate", "intermediate", "ultimate"],
    },
)

CONFLICT = Concept(
    name="Conflict",
    definition="Opposition or challenge involving at least two forces with incompatible goals. Conflict creates narrative tension and drives progression.",
    relationships=CONFLICT_RELATIONSHIPS,
    validation_rules=CONFLICT_RULES,
    category="progression",
    metadata={
        "examples": ["man vs. self", "man vs. man", "man vs. environment"],
        "properties": ["opposing_forces", "stakes", "resolution"],
        "conflict_types": ["internal", "external", "environmental"],
    },
)

PAYOFF = Concept(
    name="Payoff",
    definition="The resolution or delivery of something set up earlier in the narrative. Payoffs satisfy expectations created by setups.",
    relationships=PAYOFF_RELATIONSHIPS,
    validation_rules=PAYOFF_RULES,
    category="resolution",
    metadata={
        "examples": ["fulfillment of promise", "reveal of mystery", "consequence"],
        "properties": ["setup_reference", "timing", "satisfaction_level"],
    },
)

SYMBOL = Concept(
    name="Symbol",
    definition="An object, image, or action that carries meaning beyond its literal interpretation. Symbols represent abstract concepts through concrete forms.",
    relationships=SYMBOL_RELATIONSHIPS,
    validation_rules=SYMBOL_RULES,
    category="abstract",
    metadata={
        "examples": ["ring of power", "white whale", "red door"],
        "properties": ["physical_form", "meanings", "evolution"],
        "characteristics": ["multi_valued", "evolving", "thematic"],
    },
)

RELATIONSHIP_CONCEPT = Concept(
    name="Relationship",
    definition="A connection between narrative entities (typically characters) that affects how they interact. Relationships have dynamics, stakes, and evolution.",
    relationships=RELATIONSHIP_CONCEPT_RELATIONSHIPS,
    validation_rules=RELATIONSHIP_RULES,
    category="entity",
    metadata={
        "examples": ["friendship", "romance", "rivalry", "alliance"],
        "properties": ["participants", "dynamics", "stakes", "evolution"],
        "relationship_types": ["romantic", "familial", "professional", "adversarial"],
    },
)

BEAT = Concept(
    name="Beat",
    definition="A discrete, identifiable moment in the narrative. Beats are atomic narrative units that combine to form scenes and arcs.",
    relationships=BEAT_RELATIONSHIPS,
    validation_rules=BEAT_RULES,
    category="narrative_moment",
    metadata={
        "examples": ["character makes decision", "two characters argue", "revelation occurs"],
        "properties": ["content", "timing", "arc_position"],
        "beat_types": ["action", "dialogue", "revelation", "reaction"],
    },
)

SETUP = Concept(
    name="Setup",
    definition="The introduction of an element, promise, or mystery that requires later resolution. Setups create expectations that drive narrative forward.",
    relationships=SETUP_RELATIONSHIPS,
    validation_rules=SETUP_RULES,
    category="narrative_moment",
    metadata={
        "examples": ["introduce plot device", "make promise", "pose mystery"],
        "properties": ["element", "expectation", "payoff_reference"],
        "characteristics": ["creates_debt", "forward_looking", "mandatory_resolution"],
    },
)

REVELATION = Concept(
    name="Revelation",
    definition="The disclosure of information previously unknown to the audience or characters. Revelations change understanding and can reframe entire narratives.",
    relationships=REVELATION_RELATIONSHIPS,
    validation_rules=REVELATION_RULES,
    category="narrative_moment",
    metadata={
        "examples": ["character's true identity", "hidden relationship", "secret motivation"],
        "properties": ["hidden_information", "impact", "timing"],
        "characteristics": ["transformative", "changes_context", "affects_understanding"],
    },
)

REVERSAL = Concept(
    name="Reversal",
    definition="An unexpected change that inverts the direction or expected outcome of an arc. Reversals violate established patterns and create surprise.",
    relationships=REVERSAL_RELATIONSHIPS,
    validation_rules=REVERSAL_RULES,
    category="progression",
    metadata={
        "examples": ["heel turn", "betrayal", "unexpected success from defeat"],
        "properties": ["previous_direction", "new_direction", "surprise_factor"],
        "characteristics": ["unexpected", "trajectory_inverting", "pattern_breaking"],
    },
)

# ============================================================================
# CONCEPT REGISTRY - All concepts accessible by name
# ============================================================================

ALL_CONCEPTS = {
    "Character": CHARACTER,
    "Arc": ARC,
    "Theme": THEME,
    "Goal": GOAL,
    "Conflict": CONFLICT,
    "Payoff": PAYOFF,
    "Symbol": SYMBOL,
    "Relationship": RELATIONSHIP_CONCEPT,
    "Beat": BEAT,
    "Setup": SETUP,
    "Revelation": REVELATION,
    "Reversal": REVERSAL,
}


def get_concept(name: str) -> Concept:
    """Retrieve a concept by name."""
    if name not in ALL_CONCEPTS:
        raise ValueError(f"Unknown concept: {name}")
    return ALL_CONCEPTS[name]


def get_all_concepts() -> dict:
    """Get all defined concepts."""
    return dict(ALL_CONCEPTS)
