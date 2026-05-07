"""Auteur CLI.

Subcommands:
  init    create a project directory from a blueprint
  plan    render the Cartographer prompt (debug, no LLM call)
  draft   plan -> draft -> critique -> iterate (writes artifacts)
  accept  promote the latest draft_v*.md to final.md and update bible
  retry   continue iterating past previous max-iterations cap
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from auteur.blueprint import StoryBlueprint
from auteur.llm import LLMClient
from auteur.pipeline import PipelineRunner
from auteur.project import Project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="auteur", description="Agentic narrative engineering toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new project directory.")
    p_init.add_argument("path", type=Path)
    p_init.add_argument("--from", dest="blueprint_path", type=Path, required=True)

    p_plan = sub.add_parser("plan", help="Render the Cartographer prompt for a chapter (no LLM call).")
    p_plan.add_argument("blueprint", type=Path)
    p_plan.add_argument("chapter", type=int)

    p_draft = sub.add_parser("draft", help="Plan, draft, validate, iterate one chapter.")
    p_draft.add_argument("project", type=Path)
    p_draft.add_argument("chapter", type=int)
    p_draft.add_argument("--max-iterations", type=int, default=3)
    p_draft.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p_draft.add_argument("--model", default=None)

    p_accept = sub.add_parser("accept", help="Promote the latest draft_v*.md to final.md.")
    p_accept.add_argument("project", type=Path)
    p_accept.add_argument("chapter", type=int)

    p_retry = sub.add_parser("retry", help="Continue iterating past previous max-iterations cap.")
    p_retry.add_argument("project", type=Path)
    p_retry.add_argument("chapter", type=int)
    p_retry.add_argument("--max-iterations", type=int, default=3)
    p_retry.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p_retry.add_argument("--model", default=None)

    args = parser.parse_args(argv)

    if args.command == "init":
        return _cmd_init(args.path, args.blueprint_path)
    if args.command == "plan":
        return _cmd_plan(args.blueprint, args.chapter)
    if args.command == "draft":
        return _cmd_draft(args.project, args.chapter, args.max_iterations, args.provider, args.model)
    if args.command == "accept":
        return _cmd_accept(args.project, args.chapter)
    if args.command == "retry":
        return _cmd_retry(args.project, args.chapter, args.max_iterations, args.provider, args.model)
    parser.print_help()
    return 2


def _cmd_init(path: Path, blueprint_path: Path) -> int:
    if path.exists():
        print(f"Error: project path already exists: {path}", file=sys.stderr)
        return 1
    if not blueprint_path.exists():
        print(f"Error: blueprint not found: {blueprint_path}", file=sys.stderr)
        return 1
    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    Project.init(path, blueprint)
    print(f"Initialized project at {path}")
    return 0


def _cmd_plan(blueprint_path: Path, chapter_index: int) -> int:
    if not blueprint_path.exists():
        print(f"Error: blueprint file not found: {blueprint_path}", file=sys.stderr)
        return 1
    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    result = PipelineRunner(blueprint).plan_chapter(chapter_index)
    print("--- SYSTEM PROMPT ---\n")
    print(result.system_prompt)
    print("\n--- USER MESSAGE ---\n")
    print(result.user_message)
    return 0


def _cmd_draft(
    project_path: Path,
    chapter_index: int,
    max_iterations: int,
    provider: str,
    model: str | None,
) -> int:
    project = Project.load(project_path)
    client = _build_client(provider, model)
    runner = PipelineRunner(project.blueprint, bible=project.bible)

    def _progress(i: int, report: Any) -> None:
        if report.passed:
            status = "PASSED"
        else:
            errors = sum(1 for f in report.findings if f.severity == "error")
            status = f"FAILED ({errors} errors)"
        print(f"  iteration {i}: {status}")

    result = runner.draft_chapter(
        chapter_index,
        llm=client,
        project=project,
        max_iterations=max_iterations,
        on_iteration=_progress,
    )

    if result.conflict_report is not None:
        print(f"CONFLICT: {result.conflict_report}", file=sys.stderr)
        print(f"  See {project.chapter_dir(chapter_index) / 'outline.yaml'} for details.", file=sys.stderr)
        return 3
    if result.accepted:
        print(f"ACCEPTED on iteration {result.iterations}.")
        print(f"  final.md: {result.final_path}")
        print(f"  tokens: {result.total_input_tokens} in / {result.total_output_tokens} out")
        return 0
    print(f"NOT ACCEPTED after {result.iterations} iterations.", file=sys.stderr)
    print(f"  Latest draft and validation kept on disk.", file=sys.stderr)
    print(f"  Edit manually then: auteur accept {project_path} {chapter_index}", file=sys.stderr)
    print(f"  Or:                  auteur retry {project_path} {chapter_index}", file=sys.stderr)
    return 2


def _cmd_accept(project_path: Path, chapter_index: int) -> int:
    project = Project.load(project_path)
    chapter_dir = project.chapter_dir(chapter_index)
    drafts = sorted(chapter_dir.glob("draft_v*.md"), key=lambda p: int(p.stem.removeprefix("draft_v")))
    if not drafts:
        print(f"No drafts found in {chapter_dir}", file=sys.stderr)
        return 1
    latest = drafts[-1]
    project.write_final(chapter_index, latest.read_text(encoding="utf-8"))

    outline_path = chapter_dir / "outline.yaml"
    summary = ""
    tension: int | None = None
    if outline_path.exists():
        outline = yaml.safe_load(outline_path.read_text(encoding="utf-8"))
        summary = outline.get("chapter_summary", "")
        t = outline.get("estimated_chapter_tension")
        if isinstance(t, int):
            tension = t

    project.bible.record_event(chapter_index=chapter_index, summary=summary, deltas={"manually_accepted": True})
    if tension is not None:
        project.bible.record_tension(chapter_index, tension)
    project.bible.save()
    print(f"Accepted {latest.name} as final.md for chapter {chapter_index}.")
    return 0


def _cmd_retry(
    project_path: Path,
    chapter_index: int,
    max_iterations: int,
    provider: str,
    model: str | None,
) -> int:
    return _cmd_draft(project_path, chapter_index, max_iterations, provider, model)


def _build_client(provider: str, model: str | None) -> LLMClient:
    """Construct the production client for the chosen provider.

    Patched in tests with a FakeClient.
    """
    if provider == "anthropic":
        from auteur.llm.anthropic import AnthropicClient
        return AnthropicClient(default_model=model or "claude-sonnet-4-6")
    if provider == "openai":
        from auteur.llm.openai import OpenAIClient
        return OpenAIClient(default_model=model or "gpt-4o")
    raise ValueError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    raise SystemExit(main())
