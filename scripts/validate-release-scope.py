"""Validate the repository's machine-readable 1.0 support scope."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "docs" / "1.0-scope.md"
REQUIRED_MARKERS = (
    "# Auteur 1.0 Support Scope",
    "## Supported release path",
    "## Capability classification",
    "## Non-negotiable invariants",
    "## Release interpretation",
)


def validate_scope(path: Path = SCOPE) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing release scope: {path}"]
    text = path.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"scope missing required section: {marker}")
    if "Permanently out of scope" not in text:
        errors.append("scope must state permanently out-of-scope capabilities")
    if "Book-level reasoning/editing" not in text:
        errors.append("scope must classify Book-level reasoning/editing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the repository's 1.0 support scope.")
    parser.add_argument("--repo-root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args()
    errors = validate_scope(args.repo_root / "docs" / "1.0-scope.md")
    if errors:
        print("Release scope validation errors:")
        for error in errors:
            print(f" - {error}")
        return 1
    print("Release scope validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
