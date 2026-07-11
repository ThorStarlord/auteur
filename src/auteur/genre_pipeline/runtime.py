from __future__ import annotations

import socket
import subprocess
import sys
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.error import URLError
from urllib.request import urlopen

import yaml

from auteur.blueprint import StoryMode
from auteur.genre_pipeline.identity import IdentityCompilationError, compile_story_identity
from auteur.genre_pipeline.models import GenrePipelineSpec, GenreSessionStatus
from auteur.genre_pipeline.session import GenreSessionError, GenreSessionStore


class GenrePipelineRuntimeError(RuntimeError):
    pass


@dataclass(frozen=True)
class GenrePipelineResult:
    genre: str
    core_id: str
    session_file: Path
    identity_file: Path
    warnings: tuple[str, ...]
    browser_opened: bool


class GenrePipelineRuntime:
    def __init__(
        self,
        project_path: Path,
        spec: GenrePipelineSpec,
        core_id: str,
        *,
        mode: StoryMode | str | None = None,
        port: int | None = None,
        timeout: float = 3600.0,
        debug: bool = False,
        process_factory: Callable[..., Any] = subprocess.Popen,
        browser_opener: Callable[[str], bool] = webbrowser.open,
        server_probe: Callable[[str], bool] | None = None,
        port_checker: Callable[[int], None] | None = None,
    ):
        self.project_path = Path(project_path)
        self.spec = spec
        self.core_id = core_id
        self.mode = mode
        self.port = spec.default_port if port is None else port
        self.timeout = timeout
        self.debug = debug
        self.process_factory = process_factory
        self.browser_opener = browser_opener
        self.server_probe = server_probe or self._probe_server
        self.port_checker = port_checker or self._check_port_available
        self.sleep: Callable[[float], None] = time.sleep
        self.monotonic: Callable[[], float] = time.monotonic
        self.store = GenreSessionStore.for_project(self.project_path, spec)
        self.identity_file = self.project_path / "story_identity.yaml"

    def run(self) -> GenrePipelineResult:
        self._validate_destination()
        process = None
        try:
            session = self.store.create(self.core_id, mode=self.mode)
            process = self._launch_server()
            base_url = f"http://127.0.0.1:{self.port}"
            self._wait_for_server(base_url, process)
            url = f"{base_url}/?session={session.id}"
            browser_opened = bool(self.browser_opener(url))
            completed = self._wait_for_completion(process)
            compilation = compile_story_identity(
                self.spec,
                completed.core_id,
                completed.choices,
                working_title=completed.working_title,
                mode=completed.mode,
                require_complete=True,
            )
            self._write_identity(compilation.identity)
            warnings = tuple(compilation.choice_warnings) + tuple(
                diagnostic.message for diagnostic in compilation.warning_diagnostics
            )
            return GenrePipelineResult(
                genre=self.spec.genre.value,
                core_id=self.core_id,
                session_file=self.store.session_file,
                identity_file=self.identity_file,
                warnings=warnings,
                browser_opened=browser_opened,
            )
        except (GenreSessionError, IdentityCompilationError, OSError, ValueError) as exc:
            raise GenrePipelineRuntimeError(str(exc)) from exc
        finally:
            if process is not None:
                self._stop_process(process)

    def _validate_destination(self) -> None:
        if self.project_path.exists() and not self.project_path.is_dir():
            raise GenrePipelineRuntimeError(f"Project path must be a directory: {self.project_path}")
        if self.identity_file.exists():
            raise GenrePipelineRuntimeError(f"Canonical identity already exists: {self.identity_file}")
        self.port_checker(self.port)
        self.project_path.mkdir(parents=True, exist_ok=True)

    def _check_port_available(self, port: int) -> None:
        try:
            s = socket.socket()
            s.bind(("127.0.0.1", port))
            s.close()
        except OSError:
            raise GenrePipelineRuntimeError(f"Port {port} is already in use")

    def _launch_server(self):
        command = [
            sys.executable,
            "-m",
            "auteur.genre_pipeline.server",
            "--project",
            str(self.project_path),
            "--genre",
            self.spec.genre.value,
            "--port",
            str(self.port),
        ]
        stream = None if self.debug else subprocess.DEVNULL
        return self.process_factory(command, stdout=stream, stderr=stream)

    def _wait_for_completion(self, process):
        deadline = self.monotonic() + self.timeout
        while self.monotonic() < deadline:
            session = self.store.load()
            if session.status == GenreSessionStatus.COMPLETE:
                return session
            return_code = process.poll()
            if return_code is not None:
                raise GenrePipelineRuntimeError(
                    f"Genre pipeline server exited before completion with code {return_code}"
                )
            self.sleep(0.2)
        raise GenrePipelineRuntimeError(
            f"Genre pipeline did not complete within {self.timeout:g} seconds"
        )

    def _wait_for_server(self, base_url: str, process) -> None:
        deadline = self.monotonic() + min(self.timeout, 10.0)
        while self.monotonic() < deadline:
            return_code = process.poll()
            if return_code is not None:
                raise GenrePipelineRuntimeError(
                    f"Genre pipeline server exited before completion with code {return_code}"
                )
            if self.server_probe(base_url):
                return
            self.sleep(0.05)
        raise GenrePipelineRuntimeError(
            f"Genre pipeline server was not ready within {min(self.timeout, 10.0):g} seconds"
        )

    @staticmethod
    def _probe_server(base_url: str) -> bool:
        try:
            with urlopen(f"{base_url}/session", timeout=0.2) as response:
                return response.status == 200
        except (OSError, URLError):
            return False

    def _write_identity(self, identity) -> None:
        if self.identity_file.exists():
            raise GenrePipelineRuntimeError(f"Canonical identity already exists: {self.identity_file}")
        temporary = self.identity_file.with_suffix(".tmp")
        payload = yaml.safe_dump(
            identity.model_dump(mode="json", exclude_none=True),
            sort_keys=False,
            allow_unicode=True,
            width=120,
        )
        try:
            temporary.write_text(payload, encoding="utf-8")
            temporary.replace(self.identity_file)
        finally:
            if temporary.exists():
                temporary.unlink()

    @staticmethod
    def _stop_process(process) -> None:
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
