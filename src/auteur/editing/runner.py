from __future__ import annotations

from pathlib import Path

from auteur.editing.models import EditFinding, EditReport, PatchProposal
from auteur.editing.passes.aiisms import run_aiism_pass


def run_edit_review(
    text: str,
    *,
    source_file: Path,
    chapter: int,
    source_draft: str,
    passes: list[str],
) -> EditReport:
    findings: list[EditFinding] = []
    patches: list[PatchProposal] = []

    for pass_name in passes:
        normalized = pass_name.strip().lower()
        if normalized != "aiisms":
            raise ValueError(f"unsupported edit pass: {pass_name}")
        pass_findings, pass_patches = run_aiism_pass(text, source_file=source_file)
        findings.extend(pass_findings)
        patches.extend(pass_patches)

    return EditReport(
        chapter=chapter,
        source_file=str(source_file).replace("\\", "/"),
        source_draft=source_draft,
        passes=passes,
        findings=findings,
        patches=patches,
    )

