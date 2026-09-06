"""Fail loudly if a builder artifact reached the validator. FACTORY_RULES.md 9.

This should be impossible. The validator runs in its own worktree with its own context,
so the plan and the implementation report are simply not there.

It is checked anyway, because the failure it guards against is silent by construction.
If separation ever breaks -- a shared worktree, a stray copy, a `git add` that swept up
`.claude/plans/`, a future change to the workflow that reuses a directory -- the
validator keeps producing confident verdicts and every one of them is contaminated.
Nothing goes red. The verdicts just quietly start agreeing with the builder.

An independence property that nobody checks is an independence property nobody has.

    python factory/tripwire.py <validator-working-dir> [--base <ref> --ref <ref>]

With --base/--ref, only files the branch changed are checked: a plan document
committed long ago (a repo whose normal process writes design docs) cannot be
this lap's builder output, while anything the branch added is still caught.
Without refs it falls back to scanning the whole tree (conservative).
"""
from __future__ import annotations
import glob
import os
import subprocess
import sys

# Anything that reveals HOW the code was written rather than WHAT it does now.
FORBIDDEN = [
    ".claude/plans/**",
    ".claude/reports/**",
    ".factory/runs/*/priming.md",
    ".factory/runs/*/plan.md",
    ".factory/runs/*/report.md",
    "**/implementation-report*.md",
    "**/*-plan.md",
    ".claude/code-reviews/**",
]


def _changed_files(root: str, base: str, ref: str) -> list[str] | None:
    """Repo-relative paths changed between base and ref, or None if unknowable."""
    try:
        r = subprocess.run(
            ["git", "-C", root, "diff", "--name-only", "-z",
             f"{base}...{ref}"],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return [p for p in r.stdout.split("\0") if p]


def _matches_any(rel: str) -> bool:
    from pathlib import PurePath
    p = PurePath(rel.replace("\\", "/"))
    return any(p.match(pat) for pat in FORBIDDEN)


def main() -> int:
    positional = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts: dict[str, str] = {}
    rest = sys.argv[1:]
    for i, a in enumerate(rest):
        if a in ("--base", "--ref") and i + 1 < len(rest):
            opts[a[2:]] = rest[i + 1]
    if len(positional) < 1:
        print(__doc__)
        return 2
    root = os.path.abspath(positional[0])
    if not os.path.isdir(root):
        print(f"TRIPWIRE_ERROR: {root} is not a directory. Failing closed.")
        return 2

    print(f"TRIPWIRE_PATTERNS_CHECKED={len(FORBIDDEN)}")
    changed: list[str] | None = None
    if "base" in opts and "ref" in opts:
        changed = _changed_files(root, opts["base"], opts["ref"])
    if changed is None:
        # No refs (or git unusable): scan the whole tree. Conservative - a repo
        # whose normal process commits plan-like files will trip here, which is
        # why callers pass --base/--ref whenever the branch is known.
        found = []
        for pattern in FORBIDDEN:
            for hit in glob.glob(os.path.join(root, pattern.replace("/", os.sep)),
                                 recursive=True):
                if os.path.isfile(hit):
                    found.append(os.path.relpath(hit, root).replace("\\", "/"))
    else:
        print(f"TRIPWIRE_SCOPE=branch-diff {opts['base']}...{opts['ref']} "
              f"({len(changed)} changed files)")
        found = [p.replace("\\", "/") for p in changed if _matches_any(p)]

    print(f"TRIPWIRE_PATTERNS_CHECKED={len(FORBIDDEN)}")
    if found:
        print(f"TRIPWIRE_TRIPPED={len(found)}")
        for f in sorted(set(found)):
            print(f"  builder artifact in the validator's tree: {f}")
        print("The validator can see how the code was written. Its verdict is no longer "
              "independent evidence and must not be used to merge. This is a workflow "
              "bug, not a code bug (FACTORY_RULES.md 9).")
        return 1
    print("TRIPWIRE_CLEAR")
    return 0


if __name__ == "__main__":
    sys.exit(main())
