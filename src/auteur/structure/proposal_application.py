"""Proposal application — apply a selected proposal to a blueprint."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

import yaml
import os

from auteur.blueprint import StoryBlueprint
from auteur.structure.proposal_models import (
    ProposalOption,
    ProposalSelection,
    ProposalType,
    StructureProposal,
)


def _proposal_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


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
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "selected_option_id": proposal.selection.selected_option_id,
        "decision": proposal.decision.model_dump(mode="json") if proposal.decision else None,
    }
    meta_path = target_path + ".meta.yaml"
    with open(meta_path, "w", encoding="utf-8") as mf:
        yaml.safe_dump(meta, mf, sort_keys=False)

    return new_bp, target_path