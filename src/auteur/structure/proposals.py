from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ProposalType(str, Enum):
    GENERATION = "generation"
    REPAIR = "repair"


class ProposalOption(BaseModel):
    id: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    tradeoffs: str = Field(min_length=1)
    data: dict[str, Any] = Field(
        description="A partial dictionary matching the StoryBlueprint structure."
    )


class ProposalSelection(BaseModel):
    selected_option_id: str = ""
    custom_data: dict[str, Any] = Field(default_factory=dict)


class StructureProposal(BaseModel):
    proposal_id: str = Field(min_length=1)
    type: ProposalType
    source_rule: str | None = None
    summary: str = Field(min_length=1)
    options: list[ProposalOption] = Field(min_length=1)
    selection: ProposalSelection = Field(default_factory=ProposalSelection)

    @model_validator(mode="after")
    def validate_selection(self) -> "StructureProposal":
        option_ids = [option.id for option in self.options]

        if len(option_ids) != len(set(option_ids)):
            raise ValueError("StructureProposal options must have unique IDs")

        selected_option_id = self.selection.selected_option_id
        if selected_option_id and selected_option_id not in option_ids:
            raise ValueError(
                f"selected_option_id {selected_option_id!r} does not match any option ID"
            )

        return self
