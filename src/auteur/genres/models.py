from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field
from auteur.blueprint import (
    Genre,
    LengthClass,
    MechanicalLoad,
    NarrativeRunway,
    ScopeComplexity,
)

class PsychologyLevel(str, Enum):
    ARCHETYPAL = "archetypal"         # Myth, fairy tale, pulp adventure
    FUNCTIONAL = "functional"         # Thriller, mystery, action, horror
    CONFLICT_BEARING = "conflict_bearing" # Romance, tragedy, corruption arcs
    PSYCHOLOGICALLY_DEEP = "psychologically_deep" # Literary, psychological drama

class RequirementLevel(str, Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    ENCOURAGED = "encouraged"
    SECONDARY = "secondary"
    FORBIDDEN = "forbidden"

class PsychologyBudget(BaseModel):
    level: PsychologyLevel
    reason: str
    motivation_clarity: RequirementLevel = RequirementLevel.REQUIRED
    psychological_depth: RequirementLevel = RequirementLevel.OPTIONAL
    character_texture: RequirementLevel = RequirementLevel.ENCOURAGED


class ScopeProfile(BaseModel):
    natural_lengths: list[LengthClass] = Field(default_factory=list)
    minimum_viable_length: LengthClass
    default_length: LengthClass
    narrative_runway: NarrativeRunway
    recommended_complexity: ScopeComplexity
    mechanical_load: MechanicalLoad
    worldbuilding_load: MechanicalLoad
    cast_load: MechanicalLoad
    compression_strategies: list[str] = Field(default_factory=list)
    expansion_strategies: list[str] = Field(default_factory=list)
    scope_failure_modes: list[str] = Field(default_factory=list)

class SetupContract(BaseModel):
    emotional_runway: NarrativeRunway
    relationship_establishment: RequirementLevel = RequirementLevel.OPTIONAL
    baseline_world_establishment: RequirementLevel = RequirementLevel.OPTIONAL
    minimum_setup_beats: list[str] = Field(default_factory=list)
    forbidden_shortcuts: list[str] = Field(default_factory=list)
    compression_strategies: list[str] = Field(default_factory=list)

class GenreContract(BaseModel):
    genre_id: Genre = Field(..., description="Must map to an existing Genre enum value")
    display_name: str
    
    # Core thematic/audience identity
    core_truth: str = Field(..., description="The central philosophical assumption of the genre")
    audience_product: str = Field(..., description="The primary emotional/experiential product sold to the reader")
    primary_excitement_beats: list[str] = Field(default_factory=list, description="Load-bearing plot mechanics")
    
    # Trope constraints
    required_tropes: list[str] = Field(default_factory=list)
    optional_tropes: list[str] = Field(default_factory=list)
    forbidden_mismatches: list[str] = Field(default_factory=list, description="Elements that break the contract")
    common_failure_modes: list[str] = Field(default_factory=list, description="LLM/writer traps for this genre")
    
    # Psychology limits
    psychology_budget: PsychologyBudget
    scope_profile: ScopeProfile
    
    # Setup requirements
    setup_contract: SetupContract
    
    # Recommendations for narrative generation
    default_engine_biases: list[str] = Field(default_factory=list)
    recommended_subversions: list[str] = Field(default_factory=list)
