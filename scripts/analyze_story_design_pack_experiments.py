"""Summarize blind evaluation records for Tutor experiments."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from auteur.story_design_packs.experiments import summarize_evaluations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluations", type=Path, required=True, help="JSON array of evaluation records.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evaluations = json.loads(args.evaluations.read_text(encoding="utf-8"))
    summary = summarize_evaluations(evaluations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"EXPERIMENT_SUMMARY {len(summary['conditions'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
