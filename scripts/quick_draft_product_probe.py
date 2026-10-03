#!/usr/bin/env python3
"""Product-ergonomics probe for the Quick Draft experiment.

This is intentionally outside CI. It can print the mechanical interaction
comparison without a provider, or run live Quick Draft dogfood when existing
provider credentials are available.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.quick_draft import run_quick_draft


@dataclass(frozen=True)
class Scenario:
    name: str
    premise: str
    first_scene: str


SCENARIOS = (
    Scenario(
        "mystery",
        "Detective Miller discovers that every witness remembers the same murder differently.",
        "Miller questions Suspect Vance, who describes Miller himself committing the murder.",
    ),
    Scenario(
        "character",
        "A burned-out chef inherits the tiny restaurant she swore she would never return to.",
        "On opening night, her estranged younger brother walks into the kitchen asking for work.",
    ),
    Scenario(
        "speculative",
        "A courier learns that the package she is delivering contains tomorrow's newspaper.",
        "She opens it and finds a photograph of herself being arrested before midnight.",
    ),
    Scenario(
        "intentionally-vague",
        "Someone wakes with a key that should not exist.",
        "They try it on the only locked door in the apartment.",
    ),
)


def mechanical_comparison() -> dict[str, Any]:
    return {
        "claim_type": "mechanical_interaction_design",
        "conditions": [
            {
                "condition": "A_pre_compression",
                "visible_interactions_to_prose": 22,
                "description": "Measured corrected Beginner baseline.",
            },
            {
                "condition": "B_compressed",
                "visible_interactions_to_prose": 8,
                "description": "Compressed recommended path.",
            },
            {
                "condition": "C_quick_draft",
                "visible_interactions_to_prose": 2,
                "description": "Premise + first-scene intent, then generation.",
                "explicit_pre_prose_acceptance": 0,
            },
        ],
        "warning": (
            "Lower interaction count does not establish preference, ownership, "
            "creative quality, or lower cognitive load."
        ),
    }


def _live_probe(project: Path) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        result = run_quick_draft(
            scenario.premise,
            scenario.first_scene,
            project_root=project,
        )
        scaffold = yaml.safe_load(result.scaffold_path.read_text(encoding="utf-8")) or {}
        draft = result.draft_path.read_text(encoding="utf-8")
        runs.append(
            {
                "scenario": scenario.name,
                "session_id": result.session_id,
                "elapsed_seconds": result.elapsed_seconds,
                "thirty_second_target_met": result.elapsed_seconds <= 30.0,
                "draft_characters": len(draft),
                "provider": result.provider,
                "status": scaffold.get("status"),
                "story_setup": (scaffold.get("authority") or {}).get("story_setup"),
                "structure": (scaffold.get("authority") or {}).get("structure"),
            }
        )
    return runs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run all four scenarios through the configured real provider.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mechanical_comparison": mechanical_comparison(),
        "scenarios": [asdict(item) for item in SCENARIOS],
        "live_runs": [],
    }
    if args.live:
        payload["live_runs"] = _live_probe(args.project)

    root = args.project.resolve()
    out_dir = root / ".auteur" / "product-probes"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = out_dir / f"quick-draft-{stamp}.json"
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("Beginner ergonomics mechanical comparison")
        for condition in payload["mechanical_comparison"]["conditions"]:
            print(
                f"- {condition['condition']}: "
                f"{condition['visible_interactions_to_prose']} visible interaction(s) to prose"
            )
        if args.live:
            print("\nLive Quick Draft dogfood")
            for run in payload["live_runs"]:
                marker = "PASS" if run["thirty_second_target_met"] else "OVER 30s"
                print(
                    f"- {run['scenario']}: {run['elapsed_seconds']:.1f}s "
                    f"({marker}), {run['draft_characters']} chars"
                )
        else:
            print("\nLive provider run not requested; no prose-quality claim is made.")
        print(f"\nEvidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
