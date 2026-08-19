"""Author-facing rendering for grounded Story Discovery craft analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from auteur.story_discovery_causality import CausalProfileRecord
from auteur.story_discovery_craft import CraftAnalysis, CraftImpactRecord


def _candidate_by_id(candidate_outputs: list[Any], candidate_id: str) -> Any:
    matches = [item for item in candidate_outputs if item.candidate_id == candidate_id]
    if len(matches) != 1:
        raise ValueError(
            f"craft surface expected one candidate for {candidate_id!r}; found {len(matches)}"
        )
    return matches[0]


def _reader_contract(identity: Any) -> tuple[str, list[str], str | None]:
    target = identity.target_experience.model_dump(mode="json")
    primary = target.get("primary_emotional_promise") or target.get("primary") or ""
    secondary = target.get("secondary_palette") or target.get("secondary") or []
    trajectory = target.get("emotional_trajectory")
    if isinstance(trajectory, dict):
        trajectory_text = trajectory.get("pattern")
    else:
        trajectory_text = target.get("progression") or None
    if trajectory_text == "static" and not target.get("emotional_trajectory"):
        trajectory_text = None
    return primary, list(secondary), trajectory_text


def compact_craft_lines(
    analysis: CraftAnalysis,
    profiles: dict[str, CausalProfileRecord],
    candidate_outputs: list[Any],
) -> list[str]:
    """Render the CLI-sized craft explanation for an adjudicated recommendation."""

    winner = analysis.primary_candidate_id
    winner_output = _candidate_by_id(candidate_outputs, winner)
    profile = profiles[winner]
    primary, secondary, trajectory = _reader_contract(winner_output.identity)

    lines = [
        "Primary narrative engine",
        f"- Causal strategy: {profile.primary_strategy or 'not fully specified'}",
        f"- Causal owner: {profile.causal_owner or 'not fully specified'}",
    ]
    if primary:
        lines.append(f"- Governing reader promise: {primary}")
    if secondary:
        lines.append(f"- Supporting emotional palette: {', '.join(secondary)}")
    if trajectory:
        lines.append(f"- Emotional trajectory: {trajectory}")

    lines.extend(["", "Craft tradeoffs"])
    for candidate_output in candidate_outputs:
        if candidate_output.candidate_id == winner:
            continue
        impact = analysis.impacts[candidate_output.candidate_id]
        action = ", ".join(impact.external_action_shift.add_or_emphasize) or "no grounded action shift"
        layers = ", ".join(impact.craft_layers_changed) or "no grounded layer shift"
        reader = impact.reader_experience_shift.primary_promise_effect.replace("_", " ")
        lines.extend(
            [
                f"- {candidate_output.identity.title} (`{candidate_output.candidate_id}`)",
                f"  Changes: {layers}",
                f"  You would write more: {action}",
                f"  Primary reader-promise effect: {reader}",
                f"  Gain: {impact.gain or 'not established'}",
                f"  Give up / reweight: {impact.give_up or 'not established'}",
                f"  Composability: {impact.composability.replace('_', ' ')}",
                f"  Risk: {impact.primary_risk or 'not established'}",
            ]
        )
    return lines


def replace_generic_alternatives_with_craft(
    base_lines: list[str],
    craft_lines: list[str],
) -> list[str]:
    """Replace the generic alternative list while preserving authority/next commands."""

    try:
        start = base_lines.index("Alternatives")
        end = base_lines.index("Nothing has been accepted yet.", start)
    except ValueError:
        return [*base_lines, "", *craft_lines]
    prefix = base_lines[:start]
    suffix = base_lines[end:]
    return [*prefix, *craft_lines, "", *suffix]


def _detail_lines(
    title: str,
    candidate_id: str,
    impact: CraftImpactRecord,
) -> list[str]:
    action_add = ", ".join(impact.external_action_shift.add_or_emphasize) or "none established"
    action_less = ", ".join(impact.external_action_shift.de_emphasize) or "none established"
    scenes = ", ".join(impact.scene_family_shift) or "none established"
    palette = ", ".join(impact.reader_experience_shift.secondary_palette_effect) or "none established"
    layers = ", ".join(impact.craft_layers_changed) or "none established"
    lines = [
        f"### {title} (`{candidate_id}`)",
        "",
        f"**WHAT CHANGES** — {layers}",
        "",
        f"**CAUSAL EFFECT** — {impact.causal_ownership_shift or 'Not established from bounded evidence.'}",
        "",
        f"**WHAT YOU WILL WRITE MORE OF** — {action_add}",
        f"**WHAT MOVES OUT OF EMPHASIS** — {action_less}",
        "",
        f"**SCENE-FAMILY SHIFT** — {scenes}",
        "",
        f"**PRESSURE / STORY TEXTURE** — {impact.pressure_texture_shift or 'Not established from bounded evidence.'}",
        "",
        (
            "**READER-EXPERIENCE SHIFT** — primary promise: "
            f"{impact.reader_experience_shift.primary_promise_effect.replace('_', ' ')}; "
            f"secondary palette: {palette}; trajectory: "
            f"{impact.reader_experience_shift.trajectory_effect or 'no grounded change established'}"
        ),
        "",
        f"**THEMATIC EFFECT** — {impact.thematic_effect or 'Not established from bounded evidence.'}",
        "",
        f"**WHAT YOU GAIN** — {impact.gain or 'Not established from bounded evidence.'}",
        "",
        f"**WHAT YOU GIVE UP / REWEIGHT** — {impact.give_up or 'Not established from bounded evidence.'}",
        "",
        f"**COMPOSABILITY** — {impact.composability.replace('_', ' ')}",
    ]
    if impact.composition_note:
        lines.extend(["", f"Composition note: {impact.composition_note}"])
    lines.extend(
        [
            "",
            f"**PRIMARY RISK** — {impact.primary_risk or 'Not established from bounded evidence.'}",
        ]
    )
    if impact.evidence_gaps:
        lines.extend(["", "Evidence gaps: " + "; ".join(impact.evidence_gaps)])
    lines.append("")
    return lines


def append_craft_comparison(
    output_dir: Path,
    analysis: CraftAnalysis,
    profiles: dict[str, CausalProfileRecord],
    candidate_outputs: list[Any],
) -> None:
    """Append the full teaching explanation to comparison.md."""

    winner = analysis.primary_candidate_id
    winner_output = _candidate_by_id(candidate_outputs, winner)
    profile = profiles[winner]
    primary, secondary, trajectory = _reader_contract(winner_output.identity)
    lines = [
        "",
        "## Craft Consequences of This Choice",
        "",
        f"### Recommended primary engine — {winner_output.identity.title} (`{winner}`)",
        "",
        f"- Primary causal strategy: {profile.primary_strategy or 'not fully specified'}",
        f"- Causal owner: {profile.causal_owner or 'not fully specified'}",
        f"- Governing reader promise: {primary or 'not established'}",
    ]
    if secondary:
        lines.append(f"- Supporting emotional palette: {', '.join(secondary)}")
    if trajectory:
        lines.append(f"- Emotional trajectory: {trajectory}")
    lines.extend(
        [
            "",
            "The alternatives below describe **narrative-weight movement**, not a universal quality ranking.",
            "",
        ]
    )
    for candidate_output in candidate_outputs:
        if candidate_output.candidate_id == winner:
            continue
        lines.extend(
            _detail_lines(
                candidate_output.identity.title,
                candidate_output.candidate_id,
                analysis.impacts[candidate_output.candidate_id],
            )
        )
    path = output_dir / "comparison.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n".join(lines), encoding="utf-8")
