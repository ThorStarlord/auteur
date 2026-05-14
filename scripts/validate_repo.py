from __future__ import annotations

import sys
from pathlib import Path


STALE_README_FRAGMENT = (
    "does not yet have structure generation/diagnosis cli commands, proposal/report artifacts"
)

REQUIRED_REFERENCE_DOCS = (
    "docs/references/repo-analysis-template.md",
    "docs/references/weakness-types.md",
    "docs/references/evidence-rules.md",
)


def validate_repo(root: Path) -> list[str]:
    errors: list[str] = []

    readme_path = root / "README.md"
    if not readme_path.exists():
        errors.append("Missing README.md")
    else:
        readme_text = readme_path.read_text(encoding="utf-8").lower()
        if STALE_README_FRAGMENT in readme_text:
            errors.append(
                "README contains stale capability claim about missing structure CLI/proposal artifacts"
            )

    for relative_path in REQUIRED_REFERENCE_DOCS:
        full_path = root / relative_path
        if not full_path.exists():
            errors.append(f"Missing required reference doc: {relative_path}")

    return errors


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    root = Path(args[0]).resolve() if args else Path(__file__).resolve().parents[1]

    errors = validate_repo(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Repository contract checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
