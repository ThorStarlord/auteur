from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from auteur.editing.models import EditReport, PatchProposal


@dataclass(frozen=True)
class ReviewArtifactPaths:
    report_path: Path
    patch_path: Path
    review_path: Path


def write_review_artifacts(report: EditReport, artifact_dir: Path) -> ReviewArtifactPaths:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    report_path = artifact_dir / "edit_report.json"
    patch_path = artifact_dir / "patch_proposals.yaml"
    review_path = artifact_dir / "review.md"

    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )
    write_patch_proposals(report.patches, patch_path)
    review_path.write_text(format_review_markdown(report), encoding="utf-8")
    return ReviewArtifactPaths(report_path=report_path, patch_path=patch_path, review_path=review_path)


def format_review_markdown(report: EditReport) -> str:
    lines = [
        "# Editing Review",
        "",
        f"Chapter: {report.chapter}",
        f"Source draft: {report.source_draft}",
        f"Passes: {', '.join(report.passes)}",
        "",
        "Findings and patch proposals are review artifacts. Deterministic suggestion text is safe but simple, not final prose quality.",
        "",
        "## Findings",
    ]
    if not report.findings:
        lines.append("- None.")
    for finding in report.findings:
        lines.append(
            f"- {finding.id} ({finding.severity.value}) line {finding.location.start_line}: {finding.evidence}"
        )
    lines.extend(["", "## Patch Proposals"])
    if not report.patches:
        lines.append("- None.")
    for patch in report.patches:
        lines.append(
            f"- {patch.id} for {patch.finding_id}: replace `{patch.original}` with `{patch.replacement}` ({patch.status.value})"
        )
    lines.extend([
        "",
        "## Next Steps",
        f"- Accept a patch: `auteur edit accept <project> {report.chapter} <patch-id> --draft {report.source_draft}`",
        f"- Reject a patch: `auteur edit reject <project> {report.chapter} <patch-id> --draft {report.source_draft}`",
        f"- Apply an accepted patch: `auteur edit apply <project> {report.chapter} --patch <patch-id> --draft {report.source_draft}`",
    ])
    return "\n".join(lines) + "\n"


def write_patch_proposals(patches: list[PatchProposal], patch_path: Path) -> Path:
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    patch_path.write_text(
        yaml.safe_dump({"patches": [patch.model_dump(mode="json") for patch in patches]}, sort_keys=False),
        encoding="utf-8",
    )
    return patch_path


def load_patch_proposals(patch_path: Path) -> list[PatchProposal]:
    payload = yaml.safe_load(patch_path.read_text(encoding="utf-8")) or {}
    return [PatchProposal.model_validate(item) for item in payload.get("patches", [])]


def write_revised_draft(text: str, artifact_dir: Path) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    output = artifact_dir / "revised_draft.md"
    output.write_text(text, encoding="utf-8")
    return output
