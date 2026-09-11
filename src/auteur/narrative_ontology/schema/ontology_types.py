"""Typed models for the Narrative Ontology V2 specification.

The schema is intentionally descriptive. YAML never contains executable Python
expressions: deterministic semantic rules refer to named executors registered by
runtime code, while craft heuristics and interpretive criteria remain advisory.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field


Cardinality = Literal["one-to-one", "one-to-many", "many-to-one", "many-to-many"]


class ValidationRuleKind(str, Enum):
    """Authority-safe categories for ontology validation guidance."""

    SCHEMA_CONSTRAINT = "schema_constraint"
    SEMANTIC_INVARIANT = "semantic_invariant"
    CRAFT_HEURISTIC = "craft_heuristic"
    INTERPRETIVE_CRITERION = "interpretive_criterion"


class Relationship(BaseModel):
    """A typed relationship declaration between ontology concepts.

    This describes vocabulary/schema relationships only. It is not a concrete
    story-instance relation and therefore carries no story authority.
    """

    source_concept: str = Field(..., description="Name of the source concept")
    target_concept: str = Field(..., description="Name of the target concept")
    cardinality: Cardinality = Field(..., description="Cardinality of the relationship")
    description: str = Field(..., description="Description of the relationship")
    required: bool = Field(default=True, description="Whether the relation is required by the vocabulary")
    relation_type: str | None = Field(
        default=None,
        description="Optional reusable RelationType id describing the relation semantics",
    )


class ValidationRule(BaseModel):
    """A classified ontology rule.

    `condition` is compatibility/documentation text only and is never evaluated.
    Deterministic rules use `executor` plus structured `parameters`.
    """

    rule_id: str = Field(..., description="Unique identifier for the rule")
    kind: ValidationRuleKind = Field(
        default=ValidationRuleKind.INTERPRETIVE_CRITERION,
        description="Rule authority/evaluation category",
    )
    executor: str | None = Field(
        default=None,
        description="Named deterministic executor; never arbitrary code",
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured parameters supplied to a named executor",
    )
    condition: str | None = Field(
        default=None,
        description="Human-readable compatibility text; never executed",
    )
    error_message: str = Field(..., description="Diagnostic emitted if an executable rule fails")
    applies_to: List[str] = Field(
        default_factory=list,
        description="Genres or concepts for which the rule is relevant",
    )


class Concept(BaseModel):
    """A reusable concept in the narrative ontology."""

    name: str = Field(..., description="Canonical concept name")
    definition: str = Field(..., description="Human-readable semantic definition")
    category: str = Field(default="base", description="Concept category")
    parent_concepts: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    validation_rules: List[ValidationRule] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RelationType(BaseModel):
    """Reusable semantics for a possible relation, not a story assertion."""

    id: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenreOntologyExtension(BaseModel):
    """Metadata describing a genre-specific vocabulary extension."""

    genre: str = Field(..., description="Genre identifier")
    extends: str = Field(default="base")
    new_concepts: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
