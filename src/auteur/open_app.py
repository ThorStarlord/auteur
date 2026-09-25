"""Canonical local Auteur application launcher."""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from auteur.llm.factory import build_client

from .beginner.architecture_analysis import (
    DeterministicArchitectureAnalyzer,
    ProviderArchitectureAnalyzer,
    ResilientArchitectureAnalyzer,
)
from .beginner.discovery import DeterministicDiscoveryRecommender, StoryDiscoveryRecommender
from .beginner.server import BeginnerRuntimeDependencies, BeginnerWorkspaceServer


def _app_url(port: int) -> str:
    return f"http://127.0.0.1:{port}/"


def _health_url(port: int) -> str:
    return f"http://127.0.0.1:{port}/api/beginner/health"


def is_auteur_running(port: int, *, opener=urlopen) -> bool:
    try:
        with opener(_health_url(port), timeout=0.35) as response:
            if response.status != 200:
                return False
            body = json.loads(response.read().decode("utf-8"))
            return body == {"app": "auteur", "surface": "beginner", "status": "ok"}
    except (OSError, ValueError, HTTPError, URLError):
        return False


def _dependencies(provider: str | None, model: str | None) -> BeginnerRuntimeDependencies:
    if provider is None:
        return BeginnerRuntimeDependencies(
            architecture_analyzer=DeterministicArchitectureAnalyzer(),
            discovery_recommender=DeterministicDiscoveryRecommender(),
        )
    client = build_client(provider, model)
    resolved_model = model or ("gpt-4o" if provider == "openai" else "claude-sonnet-4-6")
    return BeginnerRuntimeDependencies(
        architecture_analyzer=ResilientArchitectureAnalyzer(
            primary=ProviderArchitectureAnalyzer(
                client=client,
                analyzer_id="beginner-architecture",
                analyzer_version="1",
                model_id=resolved_model,
                provider_id=provider,
            ),
            fallback=DeterministicArchitectureAnalyzer(),
        ),
        discovery_recommender=StoryDiscoveryRecommender(client=client),
    )


def open_auteur(
    *,
    project: Path,
    port: int = 8791,
    provider: str | None = None,
    model: str | None = None,
    open_browser: bool = True,
    browser_open: Callable[[str], object] = webbrowser.open,
    running_probe: Callable[[int], bool] = is_auteur_running,
    server_factory=BeginnerWorkspaceServer,
) -> int:
    project = project.resolve()
    url = _app_url(port)

    if running_probe(port):
        if open_browser:
            browser_open(url)
        print(f"Auteur is already running: {url}")
        return 0

    try:
        server = server_factory(
            project,
            port=port,
            dependencies=_dependencies(provider, model),
        )
    except OSError as exc:
        print(
            f"Could not start Auteur on 127.0.0.1:{port}: {exc}. "
            "If another application uses this port, pass --port <number>.",
            file=sys.stderr,
        )
        return 1

    print(f"Auteur: {url}")
    print(f"Project: {project}")
    print("Press Ctrl+C to stop the local Auteur server.")

    thread = server.start_in_thread()
    try:
        if open_browser:
            browser_open(url)
        thread.join()
    except KeyboardInterrupt:
        server.stop()
        thread.join(timeout=2)
        return 130
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auteur open",
        description="Open the local Auteur application.",
    )
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--port", type=int, default=8791)
    parser.add_argument("--provider", choices=("openai", "anthropic"))
    parser.add_argument("--model")
    parser.add_argument("--no-browser", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return open_auteur(
        project=args.project,
        port=args.port,
        provider=args.provider,
        model=args.model,
        open_browser=not args.no_browser,
    )


if __name__ == "__main__":
    raise SystemExit(main())
