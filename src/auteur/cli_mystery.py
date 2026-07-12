"""Compatibility adapter for ``auteur mystery init``."""

from pathlib import Path

from auteur.blueprint import Genre, StoryMode
from auteur.genre_pipeline.cli import GenrePipelineCommand
from auteur.genre_pipeline.registry import get_genre_pipeline
from auteur.genre_pipeline.runtime import GenrePipelineRuntimeError


class MysteryError(GenrePipelineRuntimeError):
    pass


class MysteryCommand(GenrePipelineCommand):
    def __init__(
        self,
        project_path: Path,
        core_id: str = "howdunit",
        provider: str | None = None,
        port: int | None = None,
        timeout: float = 3600.0,
        debug: bool = False,
        mode: StoryMode | str | None = None,
    ):
        super().__init__(
            project_path=project_path,
            spec=get_genre_pipeline(Genre.MYSTERY),
            core_id=core_id,
            provider=provider,
            port=port,
            timeout=timeout,
            debug=debug,
            mode=mode,
        )


def handle_mystery_init(
    project_path: Path,
    core_id: str = "howdunit",
    provider: str | None = None,
    port: int | None = None,
    timeout: float = 3600.0,
    debug: bool = False,
    mode: StoryMode | str | None = None,
) -> int:
    return GenrePipelineCommand(
        project_path=project_path,
        spec=get_genre_pipeline(Genre.MYSTERY),
        core_id=core_id,
        provider=provider,
        port=port,
        timeout=timeout,
        debug=debug,
        mode=mode,
    ).run()

def handle_mystery_resume(project_path: Path, port: int | None = None, timeout: float = 3600.0, debug: bool = False, no_browser: bool = False) -> int:
    return GenrePipelineCommand(project_path=project_path, spec=get_genre_pipeline(Genre.MYSTERY), core_id="howdunit", port=port, timeout=timeout, debug=debug, resume=True, no_browser=no_browser).run()
