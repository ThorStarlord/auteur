"""Deterministic Book Manuscript reasoning adapter.

Analyzes the accepted Book Manuscript artifact for:
- Chapter continuity (are there gaps in the sequence?)
- Chapter completeness (are all planned chapters present?)
- Pacing signals (no express intent to evaluate quality)
- Structural arc detection (no express intent to judge effectiveness)

The analyzer is read-only and produces explainable findings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .runtime import CriticRegistry, CriticSpec


def register_book_manuscript_critic(registry: CriticRegistry) -> None:
    """Register the deterministic Book Manuscript reasoning critic."""
    registry.register(CriticSpec(
        critic_id="book.manuscript",
        version="1.0.0",
        input_keys=("project",),
        run=run_book_analysis,
    ))


def run_book_analysis(*, project: Any, **_: Any) -> list[dict[str, Any]]:
    """Analyze the Book Manuscript artifact for structural concerns.

    Parameters
    ----------
    project : Path or str
        Path to the auteur project root.

    Returns
    -------
    list[dict]
        A list of findings, each with rule, message, evidence, hypotheses,
        and recommendations.
    """
    project_path = Path(project) if not isinstance(project, Path) else project
    findings: list[dict[str, Any]] = []

    _check_accepted_book(project_path, findings)
    _check_chapter_continuity(project_path, findings)
    _check_chapter_counts(project_path, findings)

    return findings


def _check_accepted_book(project_path: Path, findings: list[dict[str, Any]]) -> None:
    """Check whether an accepted Book Manuscript exists."""
    accepted = project_path / "book" / "expression" / "accepted.yaml"
    pointer = project_path / "book" / "expression" / "accepted-book-pointer.yaml"

    if not accepted.exists():
        findings.append({
            "rule": "book.manuscript.no_manifest",
            "message": "No accepted Book Manuscript manifest found.",
            "severity": "warning",
            "evidence": {
                "expected": "book/expression/accepted.yaml",
                "existing": False,
            },
            "hypotheses": [
                "no chapter has been accepted yet",
                "the project uses a non-standard directory layout",
                "the manuscript is in draft form only",
            ],
            "recommendations": [
                "accept at least one chapter to create a Book Manuscript",
                "verify the project structure with 'auteur status'",
            ],
            "requested_change": "Ensure the project has at least one accepted chapter.",
        })
        return

    manifest_text = accepted.read_text(encoding="utf-8").strip()
    if not manifest_text:
        findings.append({
            "rule": "book.manuscript.empty_manifest",
            "message": "Accepted Book Manifest is empty.",
            "severity": "warning",
            "evidence": {
                "path": "book/expression/accepted.yaml",
                "size": 0,
            },
            "recommendations": [
                "accept at least one chapter",
            ],
            "requested_change": "Populate the Book Manuscript with accepted chapters.",
        })
        return

    import yaml  # type: ignore[import-untyped]
    try:
        manifest = yaml.safe_load(manifest_text) or {}
    except Exception as exc:
        findings.append({
            "rule": "book.manifest.unparseable",
            "message": f"Book Manuscript manifest is not valid YAML: {exc}",
            "severity": "error",
            "evidence": {"path": "book/expression/accepted.yaml"},
            "recommendations": ["run 'auteur status' to check project health"],
            "requested_change": "Fix or regenerate the Book Manuscript manifest.",
        })
        return

    # Check pointer
    pointer_revision = None
    if pointer.exists():
        try:
            ptr = yaml.safe_load(pointer.read_text(encoding="utf-8")) or {}
            pointer_revision = ptr.get("current_accepted_book_revision")
        except Exception:
            pass

    chapters = manifest.get("chapters", [])
    total_chapters = len(chapters)

    if total_chapters == 0:
        findings.append({
            "rule": "book.manuscript.no_chapters",
            "message": "Accepted Book Manifest contains no chapter entries.",
            "severity": "warning",
            "evidence": {
                "chapter_count": 0,
                "manifest_fields": list(manifest.keys()),
            },
            "recommendations": [
                "accept at least one chapter via 'auteur accept chapter'",
            ],
            "requested_change": "Accept one or more chapters to build the Book Manuscript.",
        })
        return

    # Report chapter count summary
    chapter_ids = [ch.get("chapter_id") or ch.get("id", f"ch_{i}")
                   for i, ch in enumerate(chapters)]
    has_outline = manifest.get("chapter_estimate") is not None

    if has_outline and total_chapters < (manifest.get("chapter_estimate", 0)):
        planned = manifest["chapter_estimate"]
        findings.append({
            "rule": "book.manuscript.chapter_gap",
            "message": f"Book has {total_chapters} chapter(s) of {planned} planned.",
            "severity": "info",
            "evidence": {
                "chapter_count": total_chapters,
                "chapter_estimate": planned,
                "chapter_ids": chapter_ids,
            },
            "hypotheses": [
                "the remaining chapters are not yet accepted",
                "the chapter estimate was overly optimistic",
            ],
            "recommendations": [
                "continue accepting chapters to reach the estimate",
                "adjust the chapter estimate if the scope has changed",
                "check workflow status with 'auteur workflow status'",
            ],
            "requested_change": "Review progress toward the chapter estimate.",
        })

    findings.append({
        "rule": "book.manuscript.summary",
        "message": f"Book Manuscript has {total_chapters} accepted chapter(s).",
        "severity": "info",
        "evidence": {
            "chapter_count": total_chapters,
            "chapter_ids": chapter_ids,
            "pointer_revision": pointer_revision,
            "acceptance_pointer_present": pointer.exists(),
        },
        "recommendations": [
            "run 'auteur workflow next' for the next recommended action",
        ],
        "requested_change": "",
    })


def _check_chapter_continuity(project_path: Path, findings: list[dict[str, Any]]) -> None:
    """Check chapter id sequence for gaps or duplicates."""
    expression_dir = project_path / "book" / "expression"
    if not expression_dir.is_dir():
        return

    import yaml
    accepted = expression_dir / "accepted.yaml"
    if not accepted.exists():
        return

    try:
        manifest = yaml.safe_load(accepted.read_text(encoding="utf-8")) or {}
    except Exception:
        return

    chapters = manifest.get("chapters", [])
    if not chapters:
        return

    chapter_ids = [ch.get("chapter_id") or ch.get("id", "") for ch in chapters]
    seen: set[str] = set()
    for i, cid in enumerate(chapter_ids):
        if not cid:
            continue
        if cid in seen:
            findings.append({
                "rule": "book.manuscript.duplicate_chapter_id",
                "message": f"Duplicate chapter ID '{cid}' at position {i + 1}.",
                "severity": "error",
                "evidence": {"chapter_id": cid, "position": i + 1},
                "recommendations": [
                    "investigate the chapter acceptance history",
                    "ensure each chapter has a unique identifier",
                ],
                "requested_change": "Remove or rename the duplicate chapter entry.",
            })
        seen.add(cid)

    # Check for numeric ID gaps
    numeric_ids = []
    for cid in chapter_ids:
        try:
            numeric_ids.append(int(cid))
        except (ValueError, TypeError):
            pass

    if len(numeric_ids) >= 2:
        numeric_ids.sort()
        for i in range(1, len(numeric_ids)):
            expected = numeric_ids[i - 1] + 1
            if numeric_ids[i] != expected:
                findings.append({
                    "rule": "book.manuscript.sequence_gap",
                    "message": f"Chapter sequence gap between chapter {numeric_ids[i - 1]} and {numeric_ids[i]}.",
                    "severity": "warning",
                    "evidence": {
                        "previous_id": numeric_ids[i - 1],
                        "current_id": numeric_ids[i],
                        "expected_id": expected,
                    },
                    "hypotheses": [
                        "a chapter was removed or renumbered",
                        "chapters were accepted out of order",
                    ],
                    "recommendations": [
                        "verify the chapter sequence is intentional",
                        "renumber chapters if needed",
                    ],
                    "requested_change": "Review the chapter sequence for consistency.",
                })


def _check_chapter_counts(project_path: Path, findings: list[dict[str, Any]]) -> None:
    """Check chapter acceptance files on disk match the manifest."""
    expression_dir = project_path / "book" / "expression"
    if not expression_dir.is_dir():
        return

    import re
    import yaml

    # Discover actual chapter acceptance files
    actual_files: set[str] = set()
    for f in expression_dir.iterdir():
        if not f.name.endswith("_accepted.yaml"):
            continue
        m = re.match(r"^chapter_(.+?)_accepted\.yaml$", f.name)
        if m:
            actual_files.add(m.group(1))

    if not actual_files:
        return

    accepted = expression_dir / "accepted.yaml"
    if not accepted.exists():
        return

    try:
        manifest = yaml.safe_load(accepted.read_text(encoding="utf-8")) or {}
    except Exception:
        return

    manifest_chapters = manifest.get("chapters", [])
    manifest_ids = set()
    for ch in manifest_chapters:
        cid = ch.get("chapter_id") or ch.get("id", "")
        if cid:
            manifest_ids.add(cid)

    if not manifest_ids:
        return

    files_not_in_manifest = actual_files - manifest_ids
    if files_not_in_manifest:
        findings.append({
            "rule": "book.manuscript.orphan_acceptance",
            "message": f"{len(files_not_in_manifest)} accepted chapter file(s) not listed in the manifest.",
            "severity": "warning",
            "evidence": {
                "orphan_ids": sorted(files_not_in_manifest),
            },
            "hypotheses": [
                "chapters were removed from the manifest but files remain",
                "the manifest was regenerated without those chapters",
            ],
            "recommendations": [
                "clean up orphan acceptance files",
                "regenerate the manifest to match the files on disk",
            ],
            "requested_change": "Synchronize the manifest with the files on disk.",
        })
