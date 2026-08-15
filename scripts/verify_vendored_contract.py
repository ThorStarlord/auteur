"""Verify Auteur's curated vendored Sensemaking subset against skills/VENDORED.yaml.

Drift detection for the vendoring contract (owner decision 2026-08-14:
curated vendored subset is intentional). Enforces:

- every INCLUDED path still exists (a vendored file removed without updating
  the manifest is drift); and
- every EXCLUDED component stays absent (current-era Sensemaking machinery
  appearing without a contract change is drift).

Exit codes:
  0  contract holds (included present, excluded absent)
  1  drift detected (list printed)
  2  manifest missing or malformed
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "skills" / "VENDORED.yaml"


def load_manifest(path: Path = MANIFEST) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"vendoring manifest not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"malformed vendoring manifest: {path} ({exc})") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError(f"malformed vendoring manifest: {path}")
    return data


def _validate_path_value(path: str) -> None:
    """Manifest path values must be repo-relative; never absolute or escaping."""
    p = path.replace("\\", "/")
    if p.startswith("/") or ".." in p.split("/"):
        raise ValueError(f"manifest path must be repo-relative: {path!r}")


def _included_paths(manifest: dict) -> list[str]:
    included = manifest.get("included", {})
    paths: list[str] = []
    for name in included.get("skills", []):
        _validate_path_value(f"skills/{name}/SKILL.md")
        paths.append(f"skills/{name}/SKILL.md")
    for name in included.get("scripts", []):
        _validate_path_value(f"scripts/{name}")
        paths.append(f"scripts/{name}")
    for doc in included.get("framework_docs", []):
        _validate_path_value(doc)
        paths.append(doc)
    return paths


def check_drift(manifest: dict, root: Path = ROOT) -> list[str]:
    """Return a list of drift descriptions; empty means the contract holds."""
    problems: list[str] = []

    missing = [p for p in _included_paths(manifest) if not (root / p).exists()]
    for p in missing:
        problems.append(f"included path missing: {p}")

    for excluded in manifest.get("excluded", []):
        _validate_path_value(excluded)
        if (root / excluded).exists():
            problems.append(
                f"excluded component present: {excluded} "
                "(adding current-era machinery is an intentional contract "
                "change; record it in skills/VENDORED.yaml first)"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    try:
        manifest = load_manifest()
    except (FileNotFoundError, ValueError) as exc:
        print(f"VENDORED CONTRACT: MANIFEST ERROR: {exc}")
        return 2

    problems = check_drift(manifest)
    if problems:
        print("VENDORED CONTRACT: DRIFT DETECTED")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("VENDORED CONTRACT: OK (included present, excluded absent)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
