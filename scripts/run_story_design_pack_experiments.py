"""Build reproducible matched packets for Story Design Pack experiments."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from auteur.story_design_packs.experiments import ExperimentCase, build_experiment_packets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True, help="JSON array of experiment cases.")
    parser.add_argument("--pack", action="append", required=True, dest="pack_ids")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = [ExperimentCase.model_validate(item) for item in json.loads(args.cases.read_text(encoding="utf-8"))]
    packets = build_experiment_packets(cases, pack_ids=args.pack_ids)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps([packet.model_dump(mode="json") for packet in packets], indent=2) + "\n", encoding="utf-8")
    print(f"EXPERIMENT_PACKETS {len(packets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
