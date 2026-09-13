"""Read-only post-application reassessment for Structure revisions."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from auteur.blueprint import StoryBlueprint
from auteur.structure.analyzer import analyze_structure
from auteur.structure.proposal_models import StructureProposal
from auteur.structure.revision_models import RevisionApplication
from auteur.structure.revision_service import StructuralRevisionPlan


def _read_model(path: Path, model, label: str):
    if not path.is_file():
        raise ValueError(f"{label} not found: {path.stem}")
    try:
        return model.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    except Exception as exc:
        raise ValueError(f"Invalid {label.lower()} {path.stem}: {exc}") from exc


def _proposal_for_plan(root: Path, plan: StructuralRevisionPlan) -> StructureProposal | None:
    if not plan.proposal_path:
        return None
    raw = Path(plan.proposal_path)
    path = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return None
    try:
        return StructureProposal.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    except Exception:
        return None


def build_revision_reassessment(project_root: Path, application_id: str) -> dict[str, Any]:
    """Re-run exact diagnostic evidence when the applied revision has such a source."""
    root = project_root.resolve()
    base = root / ".auteur" / "structure"
    application = _read_model(
        base / "revision-applications" / f"{application_id}.yaml",
        RevisionApplication,
        "Revision application",
    )
    if application.state != "applied":
        raise ValueError(
            f"Revision application {application_id} is not fully applied (state={application.state})"
        )
    plan = _read_model(
        base / "revision-plans" / f"{application.plan_id}.yaml",
        StructuralRevisionPlan,
        "Revision plan",
    )
    proposal = _proposal_for_plan(root, plan)

    base_payload: dict[str, Any] = {
        "application_id": application.application_id,
        "plan_id": plan.plan_id,
        "authority_status": "DERIVED REASSESSMENT / READ ONLY",
        "mutates_story": False,
        "quality_score": None,
    }
    if proposal is None or proposal.source_domain != "structure" or not proposal.source_rule:
        return {
            **base_payload,
            "assessment_status": "not_assessable",
            "source_rule": proposal.source_rule if proposal else None,
            "matching_diagnostics": [],
            "reason": (
                "No exact originating Structure diagnostic rule is available; "
                "Auteur will not infer that this craft decision was resolved."
            ),
            "claim_scope": "No deterministic resolution claim is made.",
        }

    blueprint_path = root / "blueprint.yaml"
    if not blueprint_path.is_file():
        raise ValueError("Current blueprint.yaml is required for deterministic reassessment")
    diagnostics = analyze_structure(StoryBlueprint.from_yaml(blueprint_path))
    matching = [diagnostic for diagnostic in diagnostics if diagnostic.rule == proposal.source_rule]
    status = "remaining" if matching else "resolved"
    return {
        **base_payload,
        "assessment_status": status,
        "source_rule": proposal.source_rule,
        "matching_diagnostics": [diagnostic.model_dump(mode="json") for diagnostic in matching],
        "reason": (
            f"Canonical Structure analyzer still emits {proposal.source_rule!r}."
            if matching
            else f"Canonical Structure analyzer no longer emits {proposal.source_rule!r}."
        ),
        "claim_scope": (
            "This is only an exact diagnostic-rule reassessment; it is not a story-quality "
            "score and does not prove that the revision caused the result."
        ),
    }
