"""CLI orchestration for the mystery pipeline (howdunit, paranoia, cozy cores)."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

from auteur.netorare.browser.server import NetorareServer
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.netorare.session import SessionManager, SessionError
from auteur.mystery.validation import validate_choices

logger = logging.getLogger(__name__)


class MysteryError(Exception):
    """Base error for mystery CLI operations."""
    pass


class MysteryCommand:
    """Orchestrates the complete mystery pipeline.

    Identical to NetorareCommand but routes to mystery core IDs (howdunit, paranoia, cozy).
    Reuses all infrastructure from netorare (Session, Server, UI).
    """

    def __init__(
        self,
        project_path: Path,
        core_id: str = "howdunit",
        provider: str = "anthropic",
        port: int = 8766,
        timeout: float = 3600.0,
        debug: bool = False,
    ):
        """Initialize the mystery command.

        Args:
            project_path: Path to project root
            core_id: Core template ID (howdunit, paranoia, cozy)
            provider: LLM provider (anthropic, openai)
            port: Port for browser server
            timeout: Timeout in seconds for waiting for completion
            debug: Enable debug logging
        """
        self.project_path = Path(project_path)
        self.core_id = core_id
        self.provider = provider
        self.port = port
        self.timeout = timeout
        self.debug = debug

        if debug:
            logging.basicConfig(level=logging.DEBUG)

        self.mystery_dir = self.project_path / "mystery"
        self.session_file = self.mystery_dir / "session.json"
        self.identity_file = self.project_path / "story_identity.yaml"

        self.session_manager: Optional[SessionManager] = None
        self.server_process: Optional[subprocess.Popen] = None

    def run(self) -> int:
        """Execute the complete mystery pipeline. Returns exit code (0 for success)."""
        try:
            self._validate_project_path()
            self._create_project_structure()
            self._create_session()
            self._start_browser_server()
            self._open_browser()
            self._poll_for_completion()
            choices = self._read_and_validate_choices()
            identity = self._generate_identity(choices)
            self._save_identity(identity)
            self._cleanup()
            self._display_success()
            return 0
        except MysteryError as e:
            self._cleanup()
            print(f"Error: {e}", file=sys.stderr)
            logger.exception(f"Mystery pipeline failed: {e}")
            return 1
        except KeyboardInterrupt:
            self._cleanup()
            print("\nMystery pipeline interrupted", file=sys.stderr)
            return 130
        except Exception as e:
            self._cleanup()
            print(f"Unexpected error: {e}", file=sys.stderr)
            logger.exception(f"Unexpected error in mystery pipeline: {e}")
            return 1

    def _validate_project_path(self) -> None:
        """Validate project path is usable."""
        if not self.project_path.exists():
            self.project_path.mkdir(parents=True, exist_ok=True)
        if not self.project_path.is_dir():
            raise MysteryError(f"Project path must be a directory: {self.project_path}")

    def _create_project_structure(self) -> None:
        """Create project directory structure."""
        self.project_path.mkdir(parents=True, exist_ok=True)
        self.mystery_dir.mkdir(parents=True, exist_ok=True)
        (self.project_path / ".auteur").mkdir(parents=True, exist_ok=True)

    def _create_session(self) -> None:
        """Create a new mystery session."""
        if self.session_file.exists():
            raise MysteryError(f"Session already exists at {self.session_file}")
        try:
            self.session_manager = SessionManager.create_session(self.project_path, self.core_id)
        except SessionError as e:
            raise MysteryError(f"Failed to create session: {e}")

    def _start_browser_server(self) -> None:
        """Start the browser server in a subprocess (reuses netorare server)."""
        if not self.session_file.exists():
            raise MysteryError(f"Session file not found: {self.session_file}")

        server_code = self._get_server_runner_code()

        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "-c", server_code],
                env={
                    **subprocess.os.environ,
                    "NETORARE_SESSION_FILE": str(self.session_file),
                    "NETORARE_PORT": str(self.port),
                    "PYTHONUNBUFFERED": "1",
                },
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            time.sleep(1.0)
            if self.server_process.poll() is not None:
                _, stderr = self.server_process.communicate()
                raise MysteryError(f"Server failed to start: {stderr}")
            logger.info(f"Browser server started (PID {self.server_process.pid}) on port {self.port}")
        except Exception as e:
            raise MysteryError(f"Failed to start browser server: {e}")

    def _get_server_runner_code(self) -> str:
        """Get Python code to run the server in a subprocess."""
        return """
import sys
import os
from pathlib import Path
from auteur.netorare.browser.server import NetorareServer

session_file = Path(os.environ["NETORARE_SESSION_FILE"])
port = int(os.environ["NETORARE_PORT"])

try:
    server = NetorareServer(session_file=session_file, port=port)
    server.start()
except KeyboardInterrupt:
    sys.exit(0)
except Exception as e:
    print(f"Server error: {e}", file=sys.stderr)
    sys.exit(1)
"""

    def _open_browser(self) -> None:
        """Open browser to the mystery server."""
        url = f"http://localhost:{self.port}/?session={self.session_manager.get_state()['id']}"
        try:
            success = webbrowser.open(url)
            if success:
                logger.info(f"Opened browser: {url}")
            else:
                print(f"Please open this URL in your browser: {url}", file=sys.stderr)
        except Exception as e:
            logger.warning(f"Failed to open browser: {e}")
            print(f"Please open this URL in your browser: {url}", file=sys.stderr)

    def _poll_for_completion(self) -> None:
        """Poll session for completion with timeout."""
        if not self.session_manager:
            raise MysteryError("Session manager not initialized")

        start_time = time.time()
        poll_interval = 2.0
        logger.info(f"Polling for completion (timeout: {self.timeout}s)...")

        while time.time() - start_time < self.timeout:
            try:
                manager = SessionManager.load_session(self.session_file)
                if manager.is_complete():
                    self.session_manager = manager
                    return
            except SessionError as e:
                logger.debug(f"Error loading session: {e}")
            time.sleep(poll_interval)

        raise MysteryError(f"Session did not complete within {self.timeout}s")

    def _read_and_validate_choices(self) -> dict:
        """Read choices from completed session and validate."""
        if not self.session_manager:
            raise MysteryError("Session manager not initialized")

        choices = self.session_manager.get_choices()
        if not choices:
            raise MysteryError("No choices found in completed session")

        try:
            from auteur.mystery.core_templates import get_template
            template = get_template(self.core_id)
            is_valid, errors, warnings = validate_choices(template, choices)

            if warnings:
                print("\nWarnings during validation:", file=sys.stderr)
                for warning in warnings:
                    print(f"  - {warning}", file=sys.stderr)

            if not is_valid:
                error_msg = "; ".join(errors)
                raise MysteryError(f"Choices validation failed: {error_msg}")

            logger.info("Choices validated successfully")
            return choices
        except MysteryError:
            raise
        except Exception as e:
            raise MysteryError(f"Validation error: {e}")

    def _generate_identity(self, choices: dict) -> str:
        """Generate story_identity.yaml content from choices."""
        try:
            identity = IdentityGenerator.from_choices(self.core_id, choices)
            yaml_content = IdentityGenerator.to_yaml(identity)
            logger.info("Identity generated successfully")
            return yaml_content
        except ValueError as e:
            raise MysteryError(f"Failed to generate identity: {e}")
        except Exception as e:
            raise MysteryError(f"Unexpected error generating identity: {e}")

    def _save_identity(self, yaml_content: str) -> None:
        """Save generated identity to story_identity.yaml."""
        try:
            self.identity_file.write_text(yaml_content, encoding="utf-8")
            logger.info(f"Identity saved to {self.identity_file}")
        except Exception as e:
            raise MysteryError(f"Failed to save identity file: {e}")

    def _cleanup(self) -> None:
        """Clean up: stop server subprocess and close resources."""
        if self.server_process:
            try:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5.0)
                except (subprocess.TimeoutExpired, Exception) as e:
                    if isinstance(e, subprocess.TimeoutExpired):
                        self.server_process.kill()
                logger.info("Browser server stopped")
            except Exception as e:
                logger.warning(f"Error stopping server: {e}")

    def _display_success(self) -> None:
        """Display success message with next steps."""
        print("\n[OK] Mystery pipeline completed successfully!")
        print(f"\nGenerated files:")
        print(f"  - Session: {self.session_file}")
        print(f"  - Identity: {self.identity_file}")
        print(f"\nNext steps:")
        print(f"  1. Validate identity: auteur identity validate {self.identity_file}")
        print(f"  2. Compile blueprint: auteur identity compile {self.identity_file} --output {self.project_path / 'blueprint.yaml'}")


def handle_mystery_init(
    project_path: Path,
    core_id: str = "howdunit",
    provider: str = "anthropic",
    port: int = 8766,
    timeout: float = 3600.0,
    debug: bool = False,
) -> int:
    """Handle 'auteur mystery init' command.

    Args:
        project_path: Path to project directory
        core_id: Core template ID (howdunit, paranoia, cozy)
        provider: LLM provider
        port: Server port
        timeout: Completion timeout in seconds
        debug: Enable debug logging

    Returns:
        Exit code (0 for success)
    """
    command = MysteryCommand(
        project_path=project_path,
        core_id=core_id,
        provider=provider,
        port=port,
        timeout=timeout,
        debug=debug,
    )
    return command.run()
