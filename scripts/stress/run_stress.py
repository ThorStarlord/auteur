"""Standalone offline stress runner for Auteur (scenarios A-D).

Executes every stress scenario in-process at the chosen scale and writes a
JSON + Markdown report under ``artifacts/stress/`` in the worktree:

    .venv\\Scripts\\python.exe scripts/stress/run_stress.py --scale smoke

Fully offline and deterministic: LLM traffic is scripted through FakeClient,
randomness is seeded, and no API keys or network access are used.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
STRESS_DIR = REPO_ROOT / "stress"
for _path in (str(REPO_ROOT), str(STRESS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import _stress_common as common  # noqa: E402  (path bootstrap must run first)


def _scenario_summary(result: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    failed = {k: v for k, v in result.get("checks", {}).items() if not v}
    status = "passed" if not failed else "failed"
    return status, failed


def _write_markdown_report(
    path: Path, report: dict[str, Any], overall_status: str
) -> None:
    lines: list[str] = []
    lines.append("# Auteur Stress Report")
    lines.append("")
    lines.append(f"- Overall: **{overall_status}**")
    lines.append(f"- Scale: `{report['scale']}`")
    lines.append(f"- Generated (UTC): {report['generated_at_utc']}")
    machine = report["machine"]
    lines.append(f"- Python: `{machine['python_version'].split()[0]}`")
    lines.append(f"- Platform: `{machine['platform']}`")
    lines.append(f"- CPUs: {machine['cpu_count']}")
    lines.append("")
    for entry in report["scenarios"]:
        lines.append(
            f"## Scenario {entry['scenario']} - {entry.get('name', '?')}: "
            f"**{entry['status']}**"
        )
        lines.append("")
        if entry["status"] == "error":
            lines.append(f"- Error: `{entry.get('error', 'unknown')}`")
            lines.append("")
            continue
        metrics = entry.get("metrics", {})
        if metrics:
            lines.append("### Metrics")
            lines.append("")
            for key, value in metrics.items():
                if key == "per_chapter":
                    lines.append("| chapter | wall_s | iterations | accepted | "
                                 "input_tokens | output_tokens |")
                    lines.append("|---|---|---|---|---|---|")
                    for row in value:
                        lines.append(
                            f"| {row['chapter']} | {row['wall_s']} "
                            f"| {row['iterations']} | {row['accepted']} "
                            f"| {row['input_tokens']} | {row['output_tokens']} |"
                        )
                else:
                    lines.append(f"- {key}: `{value}`")
            lines.append("")
        checks = entry.get("checks", {})
        if checks:
            lines.append("### Checks")
            lines.append("")
            for key, value in checks.items():
                lines.append(f"- {'[x]' if value else '[ ]'} {key}")
            lines.append("")
        timings = entry.get("timings", {})
        if timings:
            lines.append("### Timings (wall_s / peak traced bytes)")
            lines.append("")
            for label, data in timings.items():
                peak = data.get("peak_traced_bytes", "n/a (subprocess)")
                lines.append(f"- {label}: {data.get('wall_s', '?')}s / {peak}B")
            lines.append("")
        if entry.get("failed_checks"):
            lines.append(f"### Failed checks: {entry['failed_checks']}")
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the offline Auteur stress scenarios (A-D) and write a report."
    )
    parser.add_argument(
        "--scale",
        choices=common.SCALES,
        default=None,
        help="Stress scale (default: AUTEUR_STRESS_SCALE env var, else 'full').",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=None,
        help="Report output directory (default: <repo>/artifacts/stress).",
    )
    args = parser.parse_args(argv)
    scale = common.resolve_scale(args.scale)

    stamp = datetime.now(timezone.utc)
    artifacts_dir = args.artifacts_dir or (REPO_ROOT / "artifacts" / "stress")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    run_dir = artifacts_dir / f"{stamp.strftime('%Y%m%dT%H%M%SZ')}-stress-run"
    run_dir.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "schema": "auteur-stress-report/1",
        "generated_at_utc": stamp.isoformat(),
        "scale": scale,
        "machine": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
        },
        "scenarios": [],
    }

    overall_ok = True
    for key in "ABCD":
        entry: dict[str, Any] = {"scenario": key}
        try:
            result = common.SCENARIO_RUNNERS[key](run_dir, scale)
            status, failed = _scenario_summary(result)
            entry.update(result)
            entry["status"] = status
            if failed:
                entry["failed_checks"] = failed
                overall_ok = False
        except Exception as exc:  # noqa: BLE001 - report must capture any failure
            entry["status"] = "error"
            entry["error"] = f"{type(exc).__name__}: {exc}"
            entry["traceback"] = traceback.format_exc()
            overall_ok = False
        report["scenarios"].append(entry)

    overall_status = "passed" if overall_ok else "failed"
    json_path = artifacts_dir / f"{stamp.strftime('%Y%m%dT%H%M%SZ')}-stress-report.json"
    md_path = artifacts_dir / f"{stamp.strftime('%Y%m%dT%H%M%SZ')}-stress-report.md"
    json_path.write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    _write_markdown_report(md_path, report, overall_status)

    print(f"\nStress run scale={scale}: {overall_status}")
    for entry in report["scenarios"]:
        line = f"  Scenario {entry['scenario']} ({entry.get('name', '?')}): {entry['status']}"
        if entry["status"] == "error":
            line += f" - {entry.get('error', '')}"
        elif entry.get("failed_checks"):
            line += f" - failed checks: {sorted(entry['failed_checks'])}"
        print(line)
    print(f"  Report: {json_path}")
    print(f"  Report: {md_path}")
    print(f"  Run artifacts: {run_dir}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
