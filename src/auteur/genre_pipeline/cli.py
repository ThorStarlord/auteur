from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Callable

from auteur.blueprint import StoryMode
from auteur.genre_pipeline.models import GenrePipelineSpec
from auteur.genre_pipeline.registry import get_all_genres
from auteur.genre_pipeline.runtime import (
    GenrePipelineResult,
    GenrePipelineRuntime,
    GenrePipelineRuntimeError,
)


def register_genre_pipeline_subcommands(subparsers: Any) -> None:
    for spec in get_all_genres():
        parser = subparsers.add_parser(
            spec.slug,
            help=f"Interactive browser-based {spec.slug} story identity authoring.",
        )
        commands = parser.add_subparsers(
            dest=f"{spec.slug}_command",
            required=True,
        )
        init = commands.add_parser(
            "init",
            help=f"Create a {spec.slug} story identity authoring session.",
        )
        init.add_argument("project", type=Path, help="Project directory path.")
        init.add_argument(
            "--core",
            choices=list(spec.core_ids),
            default=spec.default_core_id,
            help=f"Built-in emotional core (default: {spec.default_core_id}).",
        )
        init.add_argument(
            "--mode",
            choices=[mode.value for mode in StoryMode],
            default=None,
            help="Override the core's visible default story mode.",
        )
        init.add_argument(
            "--provider",
            choices=["anthropic", "openai"],
            default=None,
            help="Deprecated compatibility option; this workflow makes no LLM call.",
        )
        init.add_argument(
            "--port",
            type=int,
            default=spec.default_port,
            help=f"Browser server port (default: {spec.default_port}).",
        )
        init.add_argument(
            "--timeout",
            type=float,
            default=3600.0,
            help="Session timeout in seconds (default: 3600).",
        )
        init.add_argument("--debug", action="store_true", help="Enable server output.")
        init.add_argument("--no-browser", action="store_true", help="Do not open a browser automatically.")
        resume = commands.add_parser("resume", help=f"Resume an incomplete {spec.slug} session.")
        resume.add_argument("project", type=Path, help="Project directory path.")
        resume.add_argument("--port", type=int, default=spec.default_port)
        resume.add_argument("--timeout", type=float, default=3600.0)
        resume.add_argument("--debug", action="store_true")
        resume.add_argument("--no-browser", action="store_true")

        # Blueprint subcommands
        blueprint = commands.add_parser(
            "blueprint",
            help=f"Manage narrative outlines for {spec.slug} stories.",
        )
        blueprint_cmds = blueprint.add_subparsers(
            dest=f"{spec.slug}_blueprint_command",
            required=True,
        )
        blueprint_init = blueprint_cmds.add_parser(
            "init",
            help="Create an empty book outline.",
        )
        blueprint_init.add_argument("project", type=Path, help="Project directory path.")
        blueprint_init.add_argument(
            "--title",
            type=str,
            default="Untitled Story",
            help="Working title for the book (default: Untitled Story).",
        )
        blueprint_list = blueprint_cmds.add_parser(
            "list",
            help="List outline artifacts.",
        )
        blueprint_list.add_argument("project", type=Path, help="Project directory path.")

        # Orchestration commands (seed, validate, graph, status)
        blueprint_seed = blueprint_cmds.add_parser(
            "seed",
            help="Seed template outlines from story_identity.yaml.",
        )
        blueprint_seed.add_argument("project", type=Path, help="Project directory path.")
        blueprint_seed.add_argument(
            "identity",
            type=Path,
            nargs="?",
            default=None,
            help="Path to story_identity.yaml (default: project/story_identity.yaml).",
        )
        blueprint_seed.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing outlines.",
        )

        blueprint_validate = blueprint_cmds.add_parser(
            "validate",
            help="Validate all outlines against reference, chronological, and contradiction validators.",
        )
        blueprint_validate.add_argument("project", type=Path, help="Project directory path.")

        blueprint_graph = blueprint_cmds.add_parser(
            "graph",
            help="Display outline structure visualization.",
        )
        blueprint_graph.add_argument("project", type=Path, help="Project directory path.")
        blueprint_graph.add_argument(
            "--format",
            choices=["text", "dot"],
            default="text",
            help="Output format (default: text for ASCII art).",
        )

        blueprint_status = blueprint_cmds.add_parser(
            "status",
            help="Display comprehensive outline status report.",
        )
        blueprint_status.add_argument("project", type=Path, help="Project directory path.")

        # Realization subcommands (Layer 3)
        realization = commands.add_parser(
            "realization",
            help=f"Manage scene realization for {spec.slug} stories.",
        )
        realization_cmds = realization.add_subparsers(
            dest=f"{spec.slug}_realization_command",
            required=True,
        )

        realization_seed = realization_cmds.add_parser(
            "seed",
            help="Seed template scenes from chapter outlines.",
        )
        realization_seed.add_argument("project", type=Path, help="Project directory path.")
        realization_seed.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing scenes.",
        )

        realization_validate = realization_cmds.add_parser(
            "validate",
            help="Validate all scenes against knowledge, temporal, and reference validators.",
        )
        realization_validate.add_argument("project", type=Path, help="Project directory path.")

        realization_inspect = realization_cmds.add_parser(
            "inspect",
            help="Display scene structure, coverage, and status.",
        )
        realization_inspect.add_argument("project", type=Path, help="Project directory path.")

        realization_graph = realization_cmds.add_parser(
            "graph",
            help="Display scene sequence visualization.",
        )
        realization_graph.add_argument("project", type=Path, help="Project directory path.")
        realization_graph.add_argument(
            "--format",
            choices=["text", "dot"],
            default="text",
            help="Output format (default: text for ASCII art).",
        )


class GenrePipelineCommand:
    def __init__(
        self,
        project_path: Path,
        spec: GenrePipelineSpec,
        core_id: str,
        *,
        mode: StoryMode | str | None = None,
        provider: str | None = None,
        port: int | None = None,
        timeout: float = 3600.0,
        debug: bool = False,
        resume: bool = False,
        no_browser: bool = False,
        runtime_factory: Callable[..., GenrePipelineRuntime] = GenrePipelineRuntime,
    ):
        self.project_path = Path(project_path)
        self.spec = spec
        self.core_id = core_id
        self.mode = mode
        self.provider = provider
        self.port = spec.default_port if port is None else port
        if not 1 <= self.port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        self.timeout = timeout
        self.debug = debug
        self.resume = resume
        self.no_browser = no_browser
        self.runtime_factory = runtime_factory
        self.session_file = (
            self.project_path
            / ".auteur"
            / "genre_sessions"
            / spec.slug
            / "session.json"
        )
        self.identity_file = self.project_path / "story_identity.yaml"

    def run(self) -> int:
        if self.provider is not None:
            print(
                "Warning: --provider is deprecated; this deterministic workflow makes no LLM call.",
                file=sys.stderr,
            )
        try:
            runtime = self.runtime_factory(
                project_path=self.project_path,
                spec=self.spec,
                core_id=self.core_id,
                mode=self.mode,
                port=self.port,
                timeout=self.timeout,
                debug=self.debug,
                resume=self.resume,
                no_browser=self.no_browser,
            )
            result = runtime.run()
        except GenrePipelineRuntimeError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            print("\nGenre pipeline interrupted", file=sys.stderr)
            return 130

        self._display_result(result)
        return 0

    @staticmethod
    def _display_result(result: GenrePipelineResult) -> None:
        print(f"[OK] {result.genre} identity authoring completed.")
        print(f"Session: {result.session_file}")
        print(f"Identity: {result.identity_file}")
        print(f"Validate: auteur identity validate {result.identity_file}")
        if result.url and not result.browser_opened:
            print(f"Open: {result.url}")
        for warning in result.warnings:
            print(f"Warning: {warning}", file=sys.stderr)

