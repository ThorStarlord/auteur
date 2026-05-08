from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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
