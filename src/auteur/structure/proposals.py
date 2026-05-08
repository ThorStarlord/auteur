from __future__ import annotations

from enum import Enum
from typing import Any
from datetime import datetime
import os
from copy import deepcopy
import yaml

from pydantic import BaseModel, Field, model_validator
from auteur.blueprint import StoryBlueprint


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
            accepted_at=datetime.utcnow(),
        )


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = _deep_merge(base.get(k, {}), v)
        else:
            base[k] = v
    return base


def apply_proposal_to_blueprint(
    proposal: StructureProposal,
    blueprint: StoryBlueprint,
    *,
    output_dir: str | None = None,
    original_path: str | None = None,
    in_place: bool = False,
) -> tuple[StoryBlueprint, str]:
    """Materialize a proposal's selected option into a StoryBlueprint.

    Default behavior writes a new blueprint YAML file (and a small sidecar
    metadata file) into `output_dir` and returns (new_blueprint, path).
    In-place mutation requires `in_place=True` and an `original_path` to
    overwrite.
    """
    if not proposal.selection.selected_option_id:
        raise ValueError("No selected option to apply")

    # locate the selected option
    selected = None
    for opt in proposal.options:
        if opt.id == proposal.selection.selected_option_id:
            selected = opt
            break
    if selected is None:
        raise ValueError("Selected option not found in proposal options")

    # Prepare merged blueprint data
    base = deepcopy(blueprint.model_dump())
    patch = deepcopy(selected.data)
    merged = _deep_merge(base, patch)

    # validate the merged blueprint
    new_bp = StoryBlueprint.model_validate(merged)

    # determine output path
    out_dir = output_dir or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    if in_place:
        if not original_path:
            raise ValueError("in_place=True requires original_path to overwrite")
        target_path = original_path
    else:
        safe_title = (
            blueprint.identity.title.replace(" ", "_").replace("/", "-")
            if getattr(blueprint.identity, "title", None)
            else "blueprint"
        )
        fname = f"{safe_title}_applied_{proposal.proposal_id}.yaml"
        target_path = os.path.join(out_dir, fname)

    # write blueprint YAML
    with open(target_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(new_bp.model_dump(mode="json"), f, sort_keys=False)

    # write a sidecar provenance file rather than mutating the blueprint schema
    meta = {
        "applied_from_proposal": proposal.proposal_id,
        "applied_at": datetime.utcnow().isoformat(),
        "selected_option_id": proposal.selection.selected_option_id,
        "decision": proposal.decision.model_dump(mode="json") if proposal.decision else None,
    }
    meta_path = target_path + ".meta.yaml"
    with open(meta_path, "w", encoding="utf-8") as mf:
        yaml.safe_dump(meta, mf, sort_keys=False)

    return new_bp, target_path
