from __future__ import annotations

import json
from pathlib import Path

import yaml

from auteur.roundtrip.handlers import ExportData, ImportData


def write_export(data: ExportData) -> Path:
    data.output.parent.mkdir(parents=True, exist_ok=True)
    data.output.write_text(data.text, encoding="utf-8")
    return data.output


def write_import_artifacts(data: ImportData) -> Path:
    data.artifact_dir.mkdir(parents=True, exist_ok=True)
    (data.artifact_dir / "imported_draft.md").write_text(data.imported_text, encoding="utf-8")
    (data.artifact_dir / "import_manifest.json").write_text(
        json.dumps(data.manifest, indent=2),
        encoding="utf-8",
    )
    (data.artifact_dir / "diff_report.json").write_text(
        json.dumps(data.diff_report, indent=2),
        encoding="utf-8",
    )
    (data.artifact_dir / "drift_report.json").write_text(
        json.dumps(data.drift_report, indent=2),
        encoding="utf-8",
    )
    (data.artifact_dir / "canon_update_proposals.yaml").write_text(
        yaml.safe_dump(data.proposals, sort_keys=False),
        encoding="utf-8",
    )
    return data.artifact_dir


def mark_proposal_accepted(artifact_dir: Path, proposal_id: str) -> Path:
    proposals_path = artifact_dir / "canon_update_proposals.yaml"
    payload = yaml.safe_load(proposals_path.read_text(encoding="utf-8")) or {"proposals": []}
    for proposal in payload.get("proposals", []):
        if proposal.get("id") == proposal_id:
            proposal["status"] = "accepted"
            proposals_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            return proposals_path
    raise ValueError(f"proposal not found: {proposal_id}")


def write_promoted_draft(output: Path, text: str) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"draft already exists: {output}")
    output.write_text(text, encoding="utf-8")
    return output
