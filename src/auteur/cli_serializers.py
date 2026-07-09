"""Serializers for CLI command results — write artifact files from HandlerResult data.

Each serializer takes a HandlerResult and output path(s), writes the artifact file(s),
and returns the written Path (or None on failure/no data).  They do NOT print anything.
Parent directories are created automatically.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from auteur.cli_handlers import (
    CompileBlueprintData,
    HandlerResult,
    IdentityValidateData,
    RecommendOpenEndedData,
    RecommendOpinionatedData,
)

if TYPE_CHECKING:
    from auteur.blueprint import StoryBlueprint
    from auteur.identity import StoryIdentity

# ---------------------------------------------------------------------------
# Structure command serializers
# ---------------------------------------------------------------------------


def serialize_structure_diagnose(result: HandlerResult, output_path: Path) -> Path | None:
    """Write ``structure_report.json`` from a structure-diagnose result.

    Returns the written *Path* or *None* when *result* indicates failure.
    """
    if not result.is_success or result.data is None:
        return None
    data: dict[str, Any] = result.data
    report = {"diagnostics": data["diagnostics"]}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"{json.dumps(report, indent=2)}\n", encoding="utf-8")
    return output_path


def serialize_structure_propose_repairs(
    result: HandlerResult,
    diagnostics_dir: Path,
    proposals_dir: Path,
) -> Path | None:
    """Write ``structure_report.json`` and per-proposal YAML files.

    Returns the diagnostics-report *Path* (the primary artifact).  Also injects
    ``report_path`` and ``proposal_paths`` into ``result.data`` for the formatter.
    Returns *None* when *result* indicates failure.
    """
    if not result.is_success or result.data is None:
        return None
    data: dict[str, Any] = result.data
    report = {"diagnostics": data["diagnostics"]}
    proposals: list[Any] = data["proposals"]

    # --- diagnostics report ---
    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    report_path = diagnostics_dir / "structure_report.json"
    report_path.write_text(
        f"{json.dumps(report, indent=2, ensure_ascii=False)}\n",
        encoding="utf-8",
    )

    # --- per-proposal YAML files ---
    proposals_dir.mkdir(parents=True, exist_ok=True)
    proposal_paths: list[Path] = []
    for proposal in proposals:
        proposal_path = proposals_dir / f"{proposal.proposal_id}.yaml"
        proposal_path.write_text(
            yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        proposal_paths.append(proposal_path)

    # Inject paths for the formatter's consumption
    data["report_path"] = str(report_path)
    data["proposal_paths"] = proposal_paths
    result.data = data

    return report_path


def serialize_structure_generate_text(text: str, output_path: Path) -> Path:
    """Write plain generated text to *output_path*.

    Used by the structure-generate command when the user provides ``--output``.
    Returns the written *Path*.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text + "\n", encoding="utf-8")
    return output_path


# ---------------------------------------------------------------------------
# Identity command serializers
# ---------------------------------------------------------------------------


def serialize_identity_validate(result: HandlerResult, output_dir: Path) -> Path | None:
    """Write ``validation_report.json`` from an identity-validate result.

    Returns the written *Path* or *None* when *result* indicates failure.
    """
    if not result.is_success or result.data is None:
        return None
    data: IdentityValidateData = result.data
    path = output_dir / "validation_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(data.report, indent=2)}\n", encoding="utf-8")
    return path


def serialize_identity_opinionated(
    data: RecommendOpinionatedData,
    output_path: Path,
    *,
    debug: bool = False,
    timestamp: str = "",
) -> Path:
    """Write a single opinionated-identity YAML (and optional debug logs).

    Returns the identity YAML *Path*.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.identity.to_yaml(output_path)
    if debug and data.debug_logs and timestamp:
        debug_dir = Path(".auteur/runs") / timestamp
        debug_dir.mkdir(parents=True, exist_ok=True)
        for entry in data.debug_logs:
            attempt = entry.get("attempt", "unknown")
            basis = entry.get("basis", "unknown")
            log_path = debug_dir / f"attempt_{attempt}_{basis}.txt"
            log_path.write_text(entry.get("content", str(entry)), encoding="utf-8")
    return output_path


def serialize_identity_openended(
    data: RecommendOpenEndedData,
    output_path: Path,
    premise: str,
) -> list[Path]:
    """Write candidate YAMLs, ``recommendation_set.yaml``, and ``comparison.md``.

    Returns a list of every *Path* written.
    """
    candidate_dir = output_path.parent / "story_identity_candidates"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    # --- candidate YAMLs ---
    for co in data.candidates:
        candidate_path = candidate_dir / f"{co.candidate_id}.yaml"
        candidate_path.write_text(co.yaml_content, encoding="utf-8")
        co.candidate.path = str(candidate_path)
        written.append(candidate_path)

    # --- recommendation_set.yaml ---
    data.rec_set.source_input_path = premise
    for c, co in zip(data.rec_set.candidates, data.candidates):
        c.path = co.candidate.path
    rec_set_path = candidate_dir / "recommendation_set.yaml"
    rec_set_path.write_text(
        yaml.safe_dump(data.rec_set.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    written.append(rec_set_path)

    # --- comparison.md ---
    lines = list(data.comparison_lines)
    if lines:
        lines[0] = "# Story Identity Candidate Comparison"
    if len(lines) >= 2:
        lines[1] = f"\nSource Premise File/Text: `{premise}`"
    comparison_path = candidate_dir / "comparison.md"
    comparison_path.write_text("\n".join(lines), encoding="utf-8")
    written.append(comparison_path)

    return written


def _discovery_report(data: RecommendOpenEndedData, premise: str) -> dict[str, Any]:
    comparison: list[dict[str, Any]] = []
    for co in data.candidates:
        candidate = co.candidate
        identity = co.identity
        comparison.append(
            {
                "candidate_id": getattr(candidate, "candidate_id", co.candidate_id),
                "lens": getattr(candidate, "lens", ""),
                "genre": identity.story_type.genre.value,
                "emotional_promise": identity.target_experience.primary,
                "primary_engine": identity.central_engine.conflict,
                "contract_fit": getattr(candidate, "contract_fit", 0),
                "contract_fit_status": getattr(candidate, "contract_fit_status", "weak"),
                "risks": getattr(candidate, "risks", []),
            }
        )

    return {
        "premise_summary": premise,
        "candidate_count": len(data.candidates),
        "search_strategy": getattr(data.rec_set, "search_strategy", "Narrative Search"),
        "design_lenses": getattr(data.rec_set, "design_lenses", []),
        "comparison": comparison,
        "chosen_candidate": None,
        "timestamp": data.rec_set.generated_at if hasattr(data.rec_set, "generated_at") else "",
    }


def serialize_story_discovery(
    data: RecommendOpenEndedData,
    output_dir: Path,
    premise: str,
) -> list[Path]:
    """Write Story Discovery candidates, index, report, and comparison artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for co in data.candidates:
        candidate_path = output_dir / f"{co.candidate_id}.yaml"
        candidate_path.write_text(co.yaml_content, encoding="utf-8")
        co.candidate.path = str(candidate_path)
        written.append(candidate_path)

    data.rec_set.source_input_path = premise
    for c, co in zip(data.rec_set.candidates, data.candidates):
        c.path = co.candidate.path

    discovery_set_path = output_dir / "discovery_set.yaml"
    discovery_set_path.write_text(
        yaml.safe_dump(data.rec_set.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    written.append(discovery_set_path)

    report_path = output_dir / "discovery_report.yaml"
    report_path.write_text(
        yaml.safe_dump(_discovery_report(data, premise), sort_keys=False),
        encoding="utf-8",
    )
    written.append(report_path)

    lines = data.comparison_lines
    if len(lines) >= 2:
        lines[1] = f"\nSource Premise File/Text: `{premise}`"
    comparison_path = output_dir / "comparison.md"
    comparison_path.write_text("\n".join(lines), encoding="utf-8")
    written.append(comparison_path)

    return written


def serialize_identity_promote(identity: StoryIdentity, output_path: Path) -> Path:
    """Write a promoted identity YAML at *output_path*.

    Returns the written *Path*.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    identity.to_yaml(output_path)
    return output_path


# ---------------------------------------------------------------------------
# Blueprint serializers
# ---------------------------------------------------------------------------


def serialize_compile_blueprint(result: HandlerResult, output_path: Path) -> Path | None:
    """Write blueprint YAML from a compile-to-blueprint result.

    Returns the written *Path* or *None* when *result* indicates failure.
    """
    if not result.is_success or result.data is None:
        return None
    data: CompileBlueprintData = result.data
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(data.blueprint.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    return output_path


# ---------------------------------------------------------------------------
# Audit serializers
# ---------------------------------------------------------------------------


def serialize_audit(result: HandlerResult, output_dir: Path) -> Path | None:
    """Write ``audit_report.json`` from an audit result.

    Returns the written *Path* or *None* when *result* indicates failure.
    """
    if result.data is None:
        return None
    data = result.data
    path = output_dir / "audit_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"{json.dumps({'diagnostics': [d.model_dump(mode='json') for d in data.diagnostics]}, indent=2)}\n",
        encoding="utf-8",
    )
    return path
