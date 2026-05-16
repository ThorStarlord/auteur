from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_COMMANDS = (
    (sys.executable, "scripts/test-validators.py"),
    (sys.executable, "scripts/validate-repo.py"),
    (sys.executable, "-m", "pytest", "tests", "-q", "--tb=no"),
)


def run_checks() -> int:
    for command in CHECK_COMMANDS:
        print(f"$ {' '.join(command)}", flush=True)
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            return completed.returncode
    return 0


def main() -> int:
    return run_checks()


if __name__ == "__main__":
    raise SystemExit(main())
