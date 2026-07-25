"""Deterministic Scene realization reasoning adapter.

Analyzes scene realization artifacts for:
- Scene completeness (are required fields populated per status?)
- Character presence consistency (are POV characters in participants?)
- Tension marker detection (are dramatic elements present?)

The analyzer is read-only and produces explainable findings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .runtime import CriticRegistry, CriticSpec


def register_scene_critic(registry: CriticRegistry) -> None:
    """Register the deterministic Scene realization reasoning critic."""
    registry.register(CriticSpec(
        critic_id="scene.analysis",
        version="1.0.0",
        input_keys=("project",),
        run=run_scene_analysis,
    ))


def run_scene_analysis(*, project: Any, **_: Any) -> list[dict[str, Any]]:
    """Analyze scene realization artifacts for structural concerns.

    Parameters
    ----------
    project : Path or str
        Path to the auteur project root.

    Returns
    -------
    list[dict]
        A list of findings, each with rule, message, severity, evidence,
        and recommendations.
    """
    project_path = Path(project) if not isinstance(project, Path) else project
    findings: list[dict[str, Any]] = []

    scenes = _load_all_scenes(project_path)
    if not scenes:
        findings.append({
            "rule": "scene.completeness.no_scenes",
            "message": "No scene realization artifacts found.",
            "severity": "info",
            "evidence": {"scanned_path": str(project_path / ".auteur" / "scenes")},
            "recommendations": ["Seed scene artifacts with 'auteur realization seed'."],
        })
        return findings

    _check_scene_completeness(scenes, findings)
    _check_character_presence(scenes, findings)
    _check_tension_markers(scenes, findings)

    return findings


# ---------------------------------------------------------------------------
# Scene detection helpers
# ---------------------------------------------------------------------------


def _load_all_scenes(project_path: Path) -> list[dict[str, Any]]:
    """Load all scene YAML files from the project's .auteur/scenes/ directory."""
    scenes_dir = project_path / ".auteur" / "scenes"
    if not scenes_dir.is_dir():
        return []

    discovered: list[dict[str, Any]] = []
    for genre_dir in sorted(scenes_dir.iterdir()):
        if not genre_dir.is_dir():
            continue
        for yaml_file in sorted(genre_dir.rglob("*.yaml")):
            if yaml_file.name == "index.yaml":
                continue
            try:
                data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                if data and isinstance(data, dict):
                    data["_file"] = str(yaml_file.relative_to(project_path))
                    data["_genre"] = genre_dir.name
                    discovered.append(data)
            except Exception:
                continue
    return discovered


# ---------------------------------------------------------------------------
# Check: Scene completeness
# ---------------------------------------------------------------------------


def _check_scene_completeness(
    scenes: list[dict[str, Any]], findings: list[dict[str, Any]]
) -> None:
    """Check whether each scene has the fields required by its status.

    - draft: id, chapter_id
    - incomplete: + narrative_position, pov_character_id, participants, goal,
      opposition, outcome
    - ready: all incomplete fields + entry_state, exit_state, turn, decision
    """
    for scene in scenes:
        sid = scene.get("id", "?")
        status = scene.get("status", "draft")
        missing: list[str] = []

        # Always-required
        if not scene.get("id"):
            missing.append("id")
        if not scene.get("chapter_id"):
            missing.append("chapter_id")

        if status in ("incomplete", "ready"):
            if scene.get("narrative_position") is None:
                missing.append("narrative_position")
            if not scene.get("pov_character_id"):
                missing.append("pov_character_id")
            if not scene.get("participants"):
                missing.append("participants")
            if not scene.get("goal"):
                missing.append("goal")
            if not scene.get("opposition"):
                missing.append("opposition")
            if not scene.get("outcome"):
                missing.append("outcome")

        if status == "ready":
            if not scene.get("entry_state"):
                missing.append("entry_state")
            if not scene.get("exit_state"):
                missing.append("exit_state")
            if not scene.get("turn"):
                missing.append("turn")
            if not scene.get("decision"):
                missing.append("decision")

        if missing:
            severity = "error" if status == "ready" else "warning"
            findings.append({
                "rule": "scene.completeness.missing_fields",
                "message": f"Scene {sid} (status={status}) is missing required fields: {', '.join(missing)}",
                "severity": severity,
                "evidence": {
                    "scene_id": sid,
                    "status": status,
                    "missing_fields": missing,
                    "source": scene.get("_file", ""),
                },
                "recommendations": [f"Populate missing fields for scene {sid}."],
            })


# ---------------------------------------------------------------------------
# Check: Character presence
# ---------------------------------------------------------------------------


def _check_character_presence(
    scenes: list[dict[str, Any]], findings: list[dict[str, Any]]
) -> None:
    """Check whether POV characters are included in participants."""
    for scene in scenes:
        sid = scene.get("id", "?")
        status = scene.get("status", "draft")
        if status == "draft":
            continue  # participants may not be set yet

        pov = scene.get("pov_character_id")
        participants = scene.get("participants", [])
        if not pov:
            continue  # already flagged by completeness

        if pov not in participants:
            findings.append({
                "rule": "scene.character.pov_not_in_participants",
                "message": f"Scene {sid}: POV character '{pov}' is not listed in participants.",
                "severity": "warning",
                "evidence": {
                    "scene_id": sid,
                    "pov_character_id": pov,
                    "participants": participants,
                    "source": scene.get("_file", ""),
                },
                "recommendations": [f"Add '{pov}' to participants or change POV for scene {sid}."],
            })


# ---------------------------------------------------------------------------
# Check: Tension markers
# ---------------------------------------------------------------------------


def _check_tension_markers(
    scenes: list[dict[str, Any]], findings: list[dict[str, Any]]
) -> None:
    """Check whether scenes have dramatic tension elements present."""
    for scene in scenes:
        sid = scene.get("id", "?")
        status = scene.get("status", "draft")
        if status == "draft":
            continue

        tension_signals: list[str] = []

        # Opposition is a direct tension indicator
        if scene.get("opposition"):
            tension_signals.append("opposition")

        # Turn indicates dramatic change
        if scene.get("turn"):
            tension_signals.append("turn")

        # Decision is a choice point
        if scene.get("decision"):
            tension_signals.append("decision")

        # Outcome has consequences
        outcome = scene.get("outcome", {})
        if outcome and isinstance(outcome, dict):
            if outcome.get("knowledge_questioned"):
                tension_signals.append("knowledge_questioned")
            if outcome.get("consequences"):
                tension_signals.append("consequences")

        # Tags indicating tension
        tags = scene.get("tags", [])
        tension_tags = {"climax", "conflict", "tension", "turn", "revelation", "crisis"}
        matched_tags = [t for t in tags if t.lower() in tension_tags]
        if matched_tags:
            tension_signals.extend(f"tag:{t}" for t in matched_tags)

        if len(tension_signals) < 2:
            findings.append({
                "rule": "scene.tension.low_tension_signals",
                "message": (
                    f"Scene {sid} has only {len(tension_signals)} tension signal(s) "
                    f"({', '.join(tension_signals) if tension_signals else 'none'}). "
                    "Scenes benefit from at least 2 dramatic elements."
                ),
                "severity": "info",
                "evidence": {
                    "scene_id": sid,
                    "tension_signals_found": len(tension_signals),
                    "tension_signals": tension_signals,
                    "source": scene.get("_file", ""),
                },
                "recommendations": [
                    f"Add opposition, turn, decision, or consequences to scene {sid} "
                    "to increase dramatic tension."
                ],
            })
