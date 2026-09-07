"""Mechanical qualification and runtime gate for Pack Effect v1.

This script intentionally does not contain a fake model and does not produce
product-value evidence. `--mechanical` checks condition construction and
serialization only. `--check-runtime` reports whether an operator-configured
real runtime is present without printing secrets.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from auteur.story_design_packs.integration import build_discovery_tutor_guidance
from auteur.story_design_packs.loader import load_builtin_pack

ROOT = Path(__file__).parent


def load_cases() -> list[dict[str, str]]:
    return json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))["cases"]


def condition(case: dict[str, str], pack_ids: list[str]) -> dict[str, Any]:
    guidance = build_discovery_tutor_guidance(
        pack_ids or None, premise=case["premise"], decision=case["decision"]
    )
    return {"case_id": case["case_id"], "pack_ids": pack_ids, "premise": case["premise"], "decision": case["decision"], "guidance": guidance}


def mechanical() -> None:
    pack, digest = load_builtin_pack("superhero", "0.1.0")
    assert pack.pack_id == "superhero" and pack.version == "0.1.0"
    cases = load_cases()
    assert len(cases) == 6 and len({c["case_id"] for c in cases}) == 6
    control = [condition(c, []) for c in cases]
    treatment = [condition(c, ["superhero"]) for c in cases]
    assert all(row["guidance"] is None for row in control)
    assert all(row["guidance"] and row["guidance"]["pack_sources"] for row in treatment)
    assert all(row["pack_ids"] == [] for row in control)
    assert all(row["pack_ids"] == ["superhero"] for row in treatment)
    payload = {"pack_id": pack.pack_id, "version": pack.version, "content_hash": digest, "control": control, "treatment": treatment}
    json.dumps(payload, ensure_ascii=False, sort_keys=True)
    print(json.dumps({"status": "PASS", "case_count": len(cases), "treatment_pack": "superhero@0.1.0", "pack_hash": digest}, sort_keys=True))


def runtime_status() -> None:
    provider = os.getenv("AUTEUR_LLM_PROVIDER")
    model = os.getenv("AUTEUR_LLM_MODEL")
    key_present = bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))
    if provider and model and key_present:
        print(json.dumps({"status": "CONFIGURED_RUNTIME_PRESENT", "provider": provider, "model": model}))
    else:
        print(json.dumps({"status": "EXPERIMENT_RUNTIME_UNAVAILABLE", "reason": "No complete approved provider/model/key configuration was present."}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mechanical", action="store_true")
    parser.add_argument("--check-runtime", action="store_true")
    args = parser.parse_args()
    if args.mechanical:
        mechanical()
    elif args.check_runtime:
        runtime_status()
    else:
        parser.error("Choose --mechanical or --check-runtime")
