from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class StateChange(BaseModel):
    character: str = Field(min_length=1)
    field: str = Field(min_length=1)
    before: str | None = None
    after: str | None = None


class ArcAdvancement(BaseModel):
    character: str = Field(min_length=1)
    milestone_touched: str | None = None
    delta_pct: int | None = None


class ContractComplianceItem(BaseModel):
    rule: str = Field(min_length=1)
    how_honored: str = Field(min_length=1)


class OutlineScene(BaseModel):
    scene_id: str = Field(min_length=1)
    pov_character: str | None = None
    location: str | None = None
    summary: str = Field(min_length=1)
    key_events: list[str] = Field(default_factory=list)
    character_state_changes: list[StateChange] = Field(default_factory=list)
    arc_advancements: list[ArcAdvancement] = Field(default_factory=list)
    estimated_tension: int | None = Field(default=None, ge=1, le=10)
    emotional_tone: str | None = None


class CartographerOutline(BaseModel):
    scope: str | None = None
    chapter_index: int | None = None
    chapter_summary: str | None = None
    scenes: list[OutlineScene] = Field(default_factory=list)
    arc_pushes: list[str] = Field(default_factory=list)
    contract_compliance: list[ContractComplianceItem] = Field(default_factory=list)
    expected_elements_touched: list[str] = Field(default_factory=list)
    forbidden_tropes_avoided: list[str] = Field(default_factory=list)
    estimated_chapter_tension: int | None = Field(default=None, ge=1, le=10)
    thematic_reinforcement: str | None = None
    conflict_report: str | None = None

    @model_validator(mode="after")
    def validate_scenes_and_summary(self) -> "CartographerOutline":
        """When there is no conflict_report, scenes must be non-empty and
        chapter_summary must be a non-empty string.  A conflict_report outline
        is allowed to have empty scenes and a null summary because the
        Cartographer intentionally did not plan."""
        if self.conflict_report is not None:
            return self
        errors: list[str] = []
        if not self.chapter_summary:
            errors.append("chapter_summary is required when there is no conflict_report")
        if not self.scenes:
            errors.append("scenes is required (at least 1) when there is no conflict_report")
        if errors:
            raise ValueError("; ".join(errors))
        return self
