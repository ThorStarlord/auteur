from __future__ import annotations

from enum import Enum
from typing import Any, Mapping
from datetime import datetime, timezone
import os
import re
from copy import deepcopy
import yaml

from pydantic import BaseModel, Field, model_validator
from auteur.blueprint import StoryBlueprint, CharacterRole
from auteur.structure.diagnostics import StructureDiagnostic




import re


def _proposal_slug(text: str) -> str:
    return re.sub(r'[^a-z0-9_]', '_', text.lower().replace(' ', '_'))


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


class ProposalDecision(BaseModel):
    selected_option_id: str = Field(min_length=1)
    custom_data: dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="accepted")
    author: str | None = None
    references: list[str] = Field(default_factory=list)
    accepted_at: datetime | None = None


class StructureProposal(BaseModel):
    proposal_id: str = Field(min_length=1)
    type: ProposalType
    source_rule: str | None = None
    source_domain: str | None = None
    summary: str = Field(min_length=1)
    options: list[ProposalOption] = Field(min_length=1)
    selection: ProposalSelection = Field(default_factory=ProposalSelection)
    decision: ProposalDecision | None = None

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

    def accept(
        self,
        selected_option_id: str,
        custom_data: dict[str, Any] | None = None,
        *,
        status: str = "accepted",
        author: str | None = None,
        references: list[str] | None = None,
    ) -> None:
        """Record an author's decision on this proposal.

        This updates the in-memory proposal artifact: selection and a decision
        metadata record. This should not itself mutate any blueprints.
        """
        option_ids = [o.id for o in self.options]
        if selected_option_id and selected_option_id not in option_ids:
            raise ValueError(f"selected_option_id {selected_option_id!r} does not match any option ID")

        self.selection.selected_option_id = selected_option_id
        self.selection.custom_data = custom_data or {}
        self.decision = ProposalDecision(
            selected_option_id=selected_option_id,
            custom_data=self.selection.custom_data,
            status=status,
            author=author,
            references=references or [],
            accepted_at=datetime.now(timezone.utc),
        )


