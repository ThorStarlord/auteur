"""Pydantic models for narrative ontology structure."""

from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, Field, field_validator


class Relationship(BaseModel):
    """Represents a relationship between two concepts.
    
    Attributes:
        source_concept: Name of the source concept
        target_concept: Name of the target concept
        cardinality: Type of relationship cardinality
        description: Human-readable description of the relationship
        required: Whether this relationship is required
    """

    source_concept: str = Field(..., description="Name of the source concept")
    target_concept: str = Field(..., description="Name of the target concept")
    cardinality: Literal["one-to-one", "one-to-many", "many-to-many"] = Field(
        ..., description="Cardinality of the relationship"
    )
    description: str = Field(..., description="Description of the relationship")
    required: bool = Field(default=True, description="Whether relationship is required")


class ValidationRule(BaseModel):
    """Represents a validation rule for concepts.
    
    Attributes:
        rule_id: Unique identifier for the rule
        condition: String representation of the validation condition
        error_message: Error message to display if validation fails
        applies_to: List of genres this rule applies to
    """

    rule_id: str = Field(..., description="Unique identifier for the validation rule")
    condition: str = Field(
        ..., description="Validation condition as a string (evaluated later)"
    )
    error_message: str = Field(
        ..., description="Error message if validation fails"
    )
    applies_to: List[str] = Field(
        default_factory=list,
        description="List of genres this rule applies to",
    )

    @field_validator("applies_to")
    @classmethod
    def validate_applies_to(cls, v: List[str]) -> List[str]:
        """Validate that applies_to contains valid genre names."""
        valid_genres = {"netorare", "mystery", "gentlefemdom"}
        for genre in v:
            if genre not in valid_genres:
                raise ValueError(
                    f"Invalid genre '{genre}'. Must be one of: {valid_genres}"
                )
        return v


class Concept(BaseModel):
    """Represents a concept in the narrative ontology.
    
    Attributes:
        name: Name of the concept (must be unique within base or genre)
        definition: Human-readable definition
        relationships: List of relationships this concept has
        validation_rules: List of validation rules for this concept
    """

    name: str = Field(..., description="Name of the concept")
    definition: str = Field(..., description="Definition of the concept")
    relationships: List[Relationship] = Field(
        default_factory=list, description="Relationships for this concept"
    )
    validation_rules: List[ValidationRule] = Field(
        default_factory=list, description="Validation rules for this concept"
    )


class GenreOntologyExtension(BaseModel):
    """Represents a genre-specific extension of the base ontology.
    
    Attributes:
        genre: Genre identifier
        extends: Base ontology or another genre this extends
        new_concepts: List of new concept names introduced by this genre
        metadata: Additional metadata about the extension
    """

    genre: str = Field(..., description="Genre identifier")
    extends: str = Field(
        default="base", description="Base ontology or genre this extends from"
    )
    new_concepts: List[str] = Field(
        default_factory=list, description="New concepts introduced by this genre"
    )
    metadata: Dict = Field(
        default_factory=dict, description="Additional metadata about the extension"
    )
