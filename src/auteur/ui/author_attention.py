"""Read-only author-attention projection over existing Auteur decision artifacts."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from auteur.story_design_packs.models import source_fingerprint
from auteur.story_design_packs.session import TutorSession
from auteur.structure.proposal_models import StructureProposal
from auteur.structure.revision_service import StructuralRevisionPlan


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _session_is_current(root: Path, session: TutorSession) -> bool:
    if session.status == "stale":
        return False
    for key, expected in session.source_fingerprints.items():
        if "=" not in key:
            return False
        _name, raw = key.split("=", 1)
        path = (root / raw).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            return False
        if source_fingerprint(path.read_bytes()) != expected:
            return False
    return True


def _item(
    priority: int,
    *,
    kind: str,
    artifact_id: str,
    state: str,
    reason: str,
    authority: str,
    next_command: str | None,
) -> dict[str, Any]:
    return {
        "priority": priority,
        "kind": kind,
        "artifact_id": artifact_id,
        "state": state,
        "reason": reason,
        "authority_status": authority,
        "next_command": next_command,
    }


def _load_plans(root: Path) -> tuple[list[tuple[Path, StructuralRevisionPlan]], set[Path]]:
    plans: list[tuple[Path, StructuralRevisionPlan]] = []
    proposal_paths: set[Path] = set()
    directory = root / ".auteur" / "structure" / "revision-plans"
    if not directory.is_dir():
        return plans, proposal_paths
    for path in sorted(directory.glob("*.yaml")):
        try:
            plan = StructuralRevisionPlan.model_validate(
                yaml.safe_load(path.read_text(encoding="utf-8"))
            )
        except Exception:
            continue
        plans.append((path, plan))
        if plan.proposal_path:
            raw = Path(plan.proposal_path)
            proposal = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
            if proposal.is_relative_to(root):
                proposal_paths.add(proposal)
    return plans, proposal_paths


def build_author_attention(project_root: Path) -> list[dict[str, Any]]:
    """Return deterministic next-attention items without mutating any artifact."""
    root = project_root.resolve()
    attention: list[dict[str, Any]] = []

    sessions = root / ".auteur" / "tutor" / "sessions"
    if sessions.is_dir():
        for path in sorted(sessions.glob("*.json")):
            try:
                session = TutorSession.model_validate_json(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            current = _session_is_current(root, session)
            if not current:
                attention.append(
                    _item(
                        10,
                        kind="tutor_session",
                        artifact_id=session.session_id,
                        state="stale",
                        reason="Tutor advice is bound to a source snapshot that is no longer current.",
                        authority="LOCAL / NONCANONICAL",
                        next_command=f"auteur tutor show {session.session_id} --project .",
                    )
                )
            elif session.status == "active":
                attention.append(
                    _item(
                        20,
                        kind="tutor_session",
                        artifact_id=session.session_id,
                        state="active",
                        reason="An advisory author decision is still unresolved.",
                        authority="LOCAL / NONCANONICAL",
                        next_command=f"auteur tutor show {session.session_id} --project .",
                    )
                )

    plans, planned_proposals = _load_plans(root)
    proposals = root / ".auteur" / "structure" / "proposals"
    if proposals.is_dir():
        for path in sorted(proposals.glob("*.yaml")):
            try:
                proposal = StructureProposal.model_validate(
                    yaml.safe_load(path.read_text(encoding="utf-8"))
                )
            except Exception:
                continue
            relative = _relative(root, path)
            selected = proposal.selection.selected_option_id
            if not selected:
                attention.append(
                    _item(
                        30,
                        kind="structure_proposal",
                        artifact_id=proposal.proposal_id,
                        state="unselected",
                        reason="A concrete noncanonical proposal needs author review and explicit selection.",
                        authority="NONCANONICAL PROPOSAL / NOT APPLIED",
                        next_command=f"auteur structure proposal inspect {relative} --project .",
                    )
                )
            elif path.resolve() not in planned_proposals:
                attention.append(
                    _item(
                        40,
                        kind="structure_proposal",
                        artifact_id=proposal.proposal_id,
                        state="selected",
                        reason="The proposal is selected but has not entered the Structure revision plan lifecycle.",
                        authority="NONCANONICAL PROPOSAL / NOT APPLIED",
                        next_command=f"auteur structure revision plan --proposal {relative} --project .",
                    )
                )

    for _path, plan in plans:
        state = plan.state.value
        if state == "blocked":
            attention.append(
                _item(
                    50,
                    kind="structure_revision_plan",
                    artifact_id=plan.plan_id,
                    state=state,
                    reason="Revision preconditions are blocked; inspect the derived preview before replanning.",
                    authority="REVISION PLAN / NOT APPLIED",
                    next_command=f"auteur structure revision preview {plan.plan_id} --project .",
                )
            )
        elif state == "draft":
            attention.append(
                _item(
                    60,
                    kind="structure_revision_plan",
                    artifact_id=plan.plan_id,
                    state=state,
                    reason="A concrete revision plan exists but its currentness has not yet been validated.",
                    authority="REVISION PLAN / NOT APPLIED",
                    next_command=f"auteur structure revision validate {plan.plan_id} --project .",
                )
            )
        elif state == "ready":
            attention.append(
                _item(
                    70,
                    kind="structure_revision_plan",
                    artifact_id=plan.plan_id,
                    state=state,
                    reason="The plan is current and ready for consequence preview before explicit authority action.",
                    authority="REVISION PLAN / NOT APPLIED",
                    next_command=f"auteur structure revision preview {plan.plan_id} --project .",
                )
            )

    return sorted(
        attention,
        key=lambda entry: (entry["priority"], entry["kind"], entry["artifact_id"]),
    )
