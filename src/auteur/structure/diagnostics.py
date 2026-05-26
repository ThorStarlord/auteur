from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class DiagnosticSeverity(str, Enum):
    INFO = "info"
    ERROR = "error"
    WARNING = "warning"


class DiagnosticLayer(str, Enum):
    TARGET_EXPERIENCE = "target_experience"
    CONSTRAINTS = "constraints"
    SCOPE = "scope"
    STRUCTURAL_FORCES = "structural_forces"
    THREADS = "threads"
    THEME = "theme"
    CARRIERS = "carriers"
    REPRESENTATION = "representation"
    MODULATION = "modulation"


class RepairOptions(BaseModel):
    preserve_intent: list[str] = Field(default_factory=list)
    challenge_intent: list[str] = Field(default_factory=list)


class StructureDiagnostic(BaseModel):
    severity: DiagnosticSeverity
    layer: DiagnosticLayer
    rule: str
    message: str
    evidence: list[str] = Field(default_factory=list)
    repair_options: RepairOptions = Field(default_factory=RepairOptions)
    genre_recommendation_flow: dict[str, object] | None = None

