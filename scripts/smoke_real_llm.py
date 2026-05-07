"""Real-LLM smoke test for Engine v1.

Run manually before a release:

    ANTHROPIC_API_KEY=sk-... python scripts/smoke_real_llm.py

Drafts chapter 1 of the sample blueprint against the real Anthropic API
and prints the cost. NOT a pytest target — uses real tokens.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from auteur.blueprint import StoryBlueprint
from auteur.llm.anthropic import AnthropicClient
from auteur.pipeline import PipelineRunner
from auteur.project import Project


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set; aborting.", file=sys.stderr)
        return 1

    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)
    with tempfile.TemporaryDirectory() as tmp:
        project_path = Path(tmp) / "smoke_novel"
        project = Project.init(project_path, blueprint)
        runner = PipelineRunner(blueprint, bible=project.bible)
        client = AnthropicClient()

        def progress(i, report):
            errs = sum(1 for f in report.findings if f.severity == "error")
            warns = sum(1 for f in report.findings if f.severity == "warning")
            print(f"iteration {i}: passed={report.passed} errors={errs} warnings={warns}")

        print("Drafting chapter 1 against the real API...")
        result = runner.draft_chapter(
            1,
            llm=client,
            project=project,
            max_iterations=3,
            on_iteration=progress,
        )

        print()
        print(f"accepted: {result.accepted}")
        print(f"iterations: {result.iterations}")
        print(f"input tokens: {result.total_input_tokens}")
        print(f"output tokens: {result.total_output_tokens}")
        if result.final_path:
            print("final.md preview (first 500 chars):")
            print(result.final_path.read_text(encoding="utf-8")[:500])
        if result.conflict_report:
            print(f"CONFLICT: {result.conflict_report}")
            return 3
        return 0 if result.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
