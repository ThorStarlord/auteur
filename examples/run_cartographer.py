"""End-to-end demo: build a blueprint, slice it, render the Cartographer prompt.

Run from repo root:

    python -m examples.run_cartographer

Or, after `pip install -e .`:

    python examples/run_cartographer.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running the script directly without installing the package.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

from auteur import PlanningCall, render_cartographer_prompt
from sample_blueprint import build_shattered_crown


def main() -> None:
    blueprint = build_shattered_crown()

    chapter_to_plan = 27
    call = PlanningCall.for_chapter(blueprint, chapter_to_plan)

    system, user = render_cartographer_prompt(call)

    print("=" * 78)
    print(f"Auteur — Cartographer prompt for chapter {chapter_to_plan} of {blueprint.identity.title!r}")
    print("=" * 78)
    print("\n--- SYSTEM PROMPT ---\n")
    print(system)
    print("\n--- USER MESSAGE ---\n")
    print(user)
    print("\n" + "=" * 78)
    print(
        f"Length sanity check: estimated_chapters={blueprint.structure.estimated_chapters}, "
        f"max_pov={blueprint.structure.max_pov_characters}, "
        f"max_total_chars={blueprint.structure.max_characters_total} "
        f"(auto-filled from length_class={blueprint.identity.length_class.value})"
    )


if __name__ == "__main__":
    main()
