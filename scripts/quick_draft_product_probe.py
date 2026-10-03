#!/usr/bin/env python3
"""Product-ergonomics probe for the Quick Draft experiment.

This is intentionally outside CI. It can print the mechanical interaction
comparison without a provider, or run live Quick Draft dogfood when existing
provider credentials are available.

Live runs persist inspectable evidence, including exact prose and provisional
scaffolding, but leave subjective product judgments for a human reviewer.
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


def _manual_review_template() -> dict[str, Any]:
    return {
        "honors_first_scene_intent": None,
        "generic_defaults_leak_into_prose": None,
        "scene_sized": None,
        "unwanted_commitments": [],
        "useful_to_react_to": None,
        "notes": "",
    }


def _live_run_record(
    scenario: Scenario,
    *,
    session_id: str,
    elapsed_seconds: float,
    provider: str,
    scaffold: dict[str, Any],
    draft: str,
) -> dict[str, Any]:
    inferred = scaffold.get("inferred_scaffolding") or {}
    return {
        "scenario": scenario.name,
        "inputs": asdict(scenario),
        "session_id": session_id,
        "elapsed_seconds": elapsed_seconds,
        "thirty_second_target_met": elapsed_seconds <= 30.0,
        "draft_characters": len(draft),
        "draft_text": draft,
        "provider": provider,
        "status": scaffold.get("status"),
        "authority": scaffold.get("authority") or {},
        "inferred_provisional": {
            "lenses": inferred.get("lenses") or [],
            "identity_container": inferred.get("identity_container") or {},
            "scene_plan": inferred.get("scene_plan") or {},
        },
        "manual_review": _manual_review_template(),
    }


def _messy_writer_follow_up_template() -> dict[str, Any]:
    return {
        "reference_unplanned_character": "Sister Beatrice",
        "reference_unplanned_place": "abandoned seaside convent",
        "session_id": None,
        "discoveries_seen": [],
        "discoveries_selected_for_shaping": [],
        "handoff_selected_discoveries": [],
        "prose_preserved": None,
        "stale_review_detected": None,
        "only_selected_discoveries_carried_forward": None,
        "notes": "",
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
            _live_run_record(
                scenario,
                session_id=result.session_id,
                elapsed_seconds=result.elapsed_seconds,
                provider=result.provider,
                scaffold=scaffold,
                draft=draft,
            )
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
        "schema": "quick_draft_product_evidence_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mechanical_comparison": mechanical_comparison(),
        "scenarios": [asdict(item) for item in SCENARIOS],
        "live_runs": [],
        "messy_writer_follow_up": _messy_writer_follow_up_template(),
        "claim_boundary": {
            "mechanical": (
                "Interaction counts, authority state, stored prose, and provisional "
                "scaffolding may be established by this artifact."
            ),
            "provider": (
                "A live run may establish observed latency and inspectable generated output "
                "for the configured provider."
            ),
            "human": (
                "Preference, ownership, joy, confidence, cognitive load, and desire to "
                "continue require a real participant and are not inferred here."
            ),
        },
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
            print(
                "\nThe evidence JSON includes exact prose, inferred provisional "
                "scaffolding, and blank human-review fields for manual inspection."
            )
        else:
            print("\nLive provider run not requested; no prose-quality claim is made.")
        print(f"\nEvidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
