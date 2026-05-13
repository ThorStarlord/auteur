"""Proposal resolution — load, resolve, and write proposal artifacts to disk."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime, timezone

import yaml

from auteur.structure.proposal_models import (
    ProposalOption,
    ProposalType,
    StructureProposal,
)



def load_resolved_rules(project_path: Path) -> set[str]:
    """Scan structure/proposals/ for YAML files with a non-empty selected_option_id.
    Return the set of source_rule values that have been resolved."""
    import yaml as _yaml

    proposals_dir = project_path / "structure" / "proposals"
    if not proposals_dir.is_dir():
        return set()

    resolved: set[str] = set()
    for proposal_file in sorted(proposals_dir.glob("*.yaml")):
        try:
            data = _yaml.safe_load(proposal_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        selection = data.get("selection", {})
        if isinstance(selection, dict) and selection.get("selected_option_id"):
            source_rule = data.get("source_rule")
            if source_rule:
                resolved.add(source_rule)
    return resolved


def resolve_proposal(project_path: Path, proposal_id: str, option_id: str) -> int:
    """Load a proposal YAML, set the selected option, record a decision, and save."""
    import yaml as _yaml
    from datetime import datetime, timezone

    proposals_dir = project_path / "structure" / "proposals"
    proposal_path = proposals_dir / f"{proposal_id}.yaml"

    if not proposal_path.exists():
        print(f"Proposal not found: {proposal_path}", file=__import__("sys").stderr)
        return 1

    try:
        data = _yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Failed to parse {proposal_path}: {exc}", file=__import__("sys").stderr)
        return 1

    if not isinstance(data, dict):
        print(f"Invalid proposal format: {proposal_path}", file=__import__("sys").stderr)
        return 1

    options = data.get("options", [])
    option_ids = [o.get("id") for o in options if isinstance(o, dict)]
    if option_id not in option_ids:
        print(
            f"Option '{option_id}' not found in proposal. "
            f"Available: {option_ids}",
            file=__import__("sys").stderr,
        )
        return 1

    data["selection"] = {
        "selected_option_id": option_id,
        "custom_data": {},
    }
    data["decision"] = {
        "selected_option_id": option_id,
        "custom_data": {},
        "status": "accepted",
        "author": None,
        "references": [],
        "accepted_at": datetime.now(timezone.utc).isoformat(),
    }

    proposal_path.write_text(
        _yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Resolved {proposal_id} with option '{option_id}'.")
    return 0


def write_audit_repair_proposals(
    project_path: Path,
    diagnostics: list[object],
) -> None:
    """Serialize Bible audit diagnostics into StructureProposal YAML files.

    Proposal generation is delegated to
    ``auteur.structure.proposal_generation.propose_repairs_from_audit_diagnostics``.
    This function handles I/O only.
    """
    from auteur.structure.proposal_generation import propose_repairs_from_audit_diagnostics

    proposals_dir = project_path / "structure" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)

    existing_proposals = {p.stem for p in proposals_dir.glob("repair_*.yaml")}

    proposals = propose_repairs_from_audit_diagnostics(diagnostics)

    written = 0
    for proposal in proposals:
        if proposal.proposal_id in existing_proposals:
            continue
        proposal_path = proposals_dir / f"{proposal.proposal_id}.yaml"
        import yaml as _yaml
        proposal_path.write_text(
            _yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        written += 1

    print(f"Wrote {written} repair proposal(s) to {proposals_dir}")